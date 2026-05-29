from __future__ import annotations

from pathlib import Path

from extract_currency import enrich_prices_with_currency, enrich_prices_with_empty_currency, try_get_currency_rates
from extract_cepik import extract_cepik_data
from extract_csv import extract_offers_csv
from load_staging import execute_sql_file, get_engine, load_staging_tables
from sqlalchemy import text
from transform import transform_cepik, transform_offers

from config import DATA_PROCESSED_DIR, SQL_DIR
from config import SETTINGS


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


def _start_etl_run(engine) -> int:
    with engine.begin() as connection:
        row = connection.execute(
            text(
                """
                INSERT INTO etl_run_log (status, started_at)
                VALUES ('RUNNING', NOW())
                RETURNING run_id
                """
            )
        ).mappings().first()
    return int(row["run_id"])


def _finish_etl_run(engine, run_id: int, status: str, metrics: dict[str, int], notes: str = "") -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE etl_run_log
                SET
                    finished_at = NOW(),
                    status = :status,
                    csv_rows_raw = :csv_rows_raw,
                    csv_rows_clean = :csv_rows_clean,
                    cepik_rows_raw = :cepik_rows_raw,
                    cepik_rows_clean = :cepik_rows_clean,
                    cepik_api_rows_raw = :cepik_api_rows_raw,
                    fact_oferty_rows = :fact_oferty_rows,
                    fact_rejestracje_rows = :fact_rejestracje_rows,
                    notes = :notes
                WHERE run_id = :run_id
                """
            ),
            {
                "run_id": run_id,
                "status": status,
                "csv_rows_raw": metrics.get("csv_rows_raw", 0),
                "csv_rows_clean": metrics.get("csv_rows_clean", 0),
                "cepik_rows_raw": metrics.get("cepik_rows_raw", 0),
                "cepik_rows_clean": metrics.get("cepik_rows_clean", 0),
                "cepik_api_rows_raw": metrics.get("cepik_api_rows_raw", 0),
                "fact_oferty_rows": metrics.get("fact_oferty_rows", 0),
                "fact_rejestracje_rows": metrics.get("fact_rejestracje_rows", 0),
                "notes": notes,
            },
        )


def _warehouse_counts(engine) -> dict[str, int]:
    with engine.connect() as connection:
        row = connection.execute(
            text(
                """
                SELECT
                    (SELECT COUNT(*)::INT FROM fact_oferty) AS fact_oferty_rows,
                    (SELECT COUNT(*)::INT FROM fact_rejestracje) AS fact_rejestracje_rows
                """
            )
        ).mappings().first()
    return dict(row) if row else {"fact_oferty_rows": 0, "fact_rejestracje_rows": 0}


def run_pipeline() -> None:
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    engine = get_engine()
    run_id = 0
    metrics: dict[str, int] = {}

    try:
        setup_sql = [
            SQL_DIR / "01_create_staging.sql",
            SQL_DIR / "02_create_warehouse.sql",
        ]
        _run_sql_sequence(engine, setup_sql)
        run_id = _start_etl_run(engine)

        offers_raw = extract_offers_csv()
        offers_clean = transform_offers(offers_raw)
        metrics["csv_rows_raw"] = int(len(offers_raw))
        metrics["csv_rows_clean"] = int(len(offers_clean))

        rates = try_get_currency_rates()
        if rates is None:
            offers_enriched = enrich_prices_with_empty_currency(offers_clean)
            print("NBP API unavailable. Currency columns were left empty.")
        else:
            offers_enriched = enrich_prices_with_currency(offers_clean, rates)
            print(f"NBP rates loaded: EUR={rates.eur}, USD={rates.usd}")

        cepik_raw = extract_cepik_data(offers_clean)
        cepik_clean = transform_cepik(cepik_raw)
        metrics["cepik_rows_raw"] = int(len(cepik_raw))
        metrics["cepik_rows_clean"] = int(len(cepik_clean))

        source_counts = cepik_raw["source"].value_counts(dropna=False).to_dict() if not cepik_raw.empty else {}
        api_rows = int(source_counts.get("cepik_api", 0))
        metrics["cepik_api_rows_raw"] = api_rows
        if SETTINGS.cepik_require_api_source and api_rows == 0:
            raise RuntimeError(
                "CEPiK API rows are required but not found in extraction result. "
                "Disable CEPIK_REQUIRE_API_SOURCE only if fallback is intentionally allowed."
            )

        offers_enriched.to_csv(DATA_PROCESSED_DIR / "offers_clean.csv", index=False)
        cepik_clean.to_csv(DATA_PROCESSED_DIR / "cepik_clean.csv", index=False)

        load_staging_tables(engine, offers_enriched, cepik_clean)
        _truncate_warehouse_tables(engine)

        warehouse_sql = [
            SQL_DIR / "03_load_dimensions.sql",
            SQL_DIR / "04_load_facts.sql",
        ]
        _run_sql_sequence(engine, warehouse_sql)
        metrics.update(_warehouse_counts(engine))

        _finish_etl_run(engine, run_id, "SUCCESS", metrics, notes=f"source_counts={source_counts}")
        print("Sprint 2 pipeline finished successfully.")
        print(f"Offers loaded: {len(offers_enriched)}")
        print(f"CEPiK rows loaded: {len(cepik_clean)}")
        print(f"CEPiK raw source distribution: {source_counts}")
    except Exception as exc:
        if run_id:
            _finish_etl_run(engine, run_id, "FAILED", metrics, notes=str(exc))
        raise


if __name__ == "__main__":
    run_pipeline()
