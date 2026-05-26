from __future__ import annotations

from pathlib import Path

from extract_currency import enrich_prices_with_currency, enrich_prices_with_empty_currency, try_get_currency_rates
from extract_cepik import extract_cepik_data
from extract_csv import extract_offers_csv
from load_staging import execute_sql_file, get_engine, load_staging_tables
from sqlalchemy import text
from transform import transform_cepik, transform_offers

from config import DATA_PROCESSED_DIR, SQL_DIR


def _run_sql_sequence(engine, sql_files: list[Path]) -> None:
    for sql_file in sql_files:
        execute_sql_file(engine, sql_file)


def _truncate_warehouse_tables(engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    fact_oferty,
                    fact_rejestracje,
                    dim_skrzynia,
                    dim_paliwo,
                    dim_pojazd,
                    dim_lokalizacja,
                    dim_czas
                RESTART IDENTITY CASCADE;
                """
            )
        )


def run_pipeline() -> None:
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    engine = get_engine()

    setup_sql = [
        SQL_DIR / "01_create_staging.sql",
        SQL_DIR / "02_create_warehouse.sql",
    ]
    _run_sql_sequence(engine, setup_sql)

    offers_raw = extract_offers_csv()
    offers_clean = transform_offers(offers_raw)
    rates = try_get_currency_rates()
    if rates is None:
        offers_enriched = enrich_prices_with_empty_currency(offers_clean)
        print("NBP API unavailable. Currency columns were left empty.")
    else:
        offers_enriched = enrich_prices_with_currency(offers_clean, rates)
        print(f"NBP rates loaded: EUR={rates.eur}, USD={rates.usd}")

    cepik_raw = extract_cepik_data(offers_clean)
    cepik_clean = transform_cepik(cepik_raw)

    offers_enriched.to_csv(DATA_PROCESSED_DIR / "offers_clean.csv", index=False)
    cepik_clean.to_csv(DATA_PROCESSED_DIR / "cepik_clean.csv", index=False)

    load_staging_tables(engine, offers_enriched, cepik_clean)
    _truncate_warehouse_tables(engine)

    warehouse_sql = [
        SQL_DIR / "03_load_dimensions.sql",
        SQL_DIR / "04_load_facts.sql",
    ]
    _run_sql_sequence(engine, warehouse_sql)

    print("Sprint 2 pipeline finished successfully.")
    print(f"Offers loaded: {len(offers_enriched)}")
    print(f"CEPiK rows loaded: {len(cepik_clean)}")


if __name__ == "__main__":
    run_pipeline()
