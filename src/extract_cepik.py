from __future__ import annotations

import random
from datetime import date
from typing import Any

import pandas as pd
import requests

from config import SETTINGS

CEPIK_COLUMNS = [
    "marka",
    "model",
    "rok_produkcji",
    "rodzaj_paliwa",
    "pojemnosc_silnika",
    "wojewodztwo",
    "data_pierwszej_rejestracji",
    "source",
]


def _pick(dct: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in dct and dct[key] not in (None, ""):
            return dct[key]
    return None


def _extract_rows_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data", [])
    rows: list[dict[str, Any]] = []

    for item in data:
        attributes = item.get("attributes", {}) if isinstance(item, dict) else {}
        rows.append(
            {
                "marka": _pick(attributes, "marka", "brand"),
                "model": _pick(attributes, "model"),
                "rok_produkcji": _pick(attributes, "rok-produkcji", "rok_produkcji", "year"),
                "rodzaj_paliwa": _pick(attributes, "rodzaj-paliwa", "rodzaj_paliwa", "fuel_type"),
                "pojemnosc_silnika": _pick(
                    attributes,
                    "pojemnosc-silnika",
                    "pojemnosc_silnika",
                    "engine_capacity",
                ),
                "wojewodztwo": _pick(attributes, "wojewodztwo", "voivodeship"),
                "data_pierwszej_rejestracji": _pick(
                    attributes,
                    "data-pierwszej-rejestracji-w-kraju",
                    "data-pierwszej-rejestracji",
                    "data_pierwszej_rejestracji",
                    "first_registration_date",
                ),
                "source": "cepik_api",
            }
        )
    return rows


def _fetch_cepik_api() -> pd.DataFrame:
    url = f"{SETTINGS.cepik_base_url.rstrip('/')}/{SETTINGS.cepik_resource.lstrip('/')}"
    headers = {"Accept": "application/json"}
    if SETTINGS.cepik_api_key:
        headers["X-API-Key"] = SETTINGS.cepik_api_key

    params = {
        "wojewodztwo": SETTINGS.cepik_wojewodztwo,
        "data-od": SETTINGS.cepik_data_od,
        "data-do": SETTINGS.cepik_data_do,
        "limit": SETTINGS.cepik_limit,
    }

    rows: list[dict[str, Any]] = []
    next_url: str | None = url
    page = 0
    session = requests.Session()

    while next_url and page < SETTINGS.cepik_max_pages:
        response = session.get(next_url, headers=headers, params=params if page == 0 else None, timeout=30)
        response.raise_for_status()
        payload = response.json()
        rows.extend(_extract_rows_from_payload(payload))
        next_url = payload.get("links", {}).get("next")
        page += 1

    return pd.DataFrame(rows, columns=CEPIK_COLUMNS)


def _build_fallback_from_offers(offers_df: pd.DataFrame) -> pd.DataFrame:
    if offers_df.empty:
        return pd.DataFrame(columns=CEPIK_COLUMNS)

    grouped = (
        offers_df.groupby(["brand", "model", "year", "fuel_type", "voivodeship", "engine_capacity"], dropna=False)
        .size()
        .reset_index(name="liczba_ofert")
    )

    rnd = random.Random(42)
    rows = []
    for _, row in grouped.iterrows():
        registrations = max(1, int(row["liczba_ofert"] * rnd.uniform(0.6, 1.8)))
        max_repeat = min(registrations, 30)
        for _ in range(max_repeat):
            month = rnd.randint(1, 12)
            day = rnd.randint(1, 28)
            rows.append(
                {
                    "marka": row["brand"],
                    "model": row["model"],
                    "rok_produkcji": int(row["year"]),
                    "rodzaj_paliwa": row["fuel_type"],
                    "pojemnosc_silnika": row["engine_capacity"],
                    "wojewodztwo": row["voivodeship"],
                    "data_pierwszej_rejestracji": date(int(row["year"]), month, day),
                    "source": "cepik_fallback",
                }
            )

    return pd.DataFrame(rows, columns=CEPIK_COLUMNS)


def extract_cepik_data(offers_df: pd.DataFrame | None = None) -> pd.DataFrame:
    if SETTINGS.cepik_fallback_only:
        return _build_fallback_from_offers(offers_df if offers_df is not None else pd.DataFrame())

    try:
        api_df = _fetch_cepik_api()
        if not api_df.empty:
            return api_df
    except requests.RequestException:
        pass

    return _build_fallback_from_offers(offers_df if offers_df is not None else pd.DataFrame())


if __name__ == "__main__":
    df = extract_cepik_data()
    print(f"Extracted {len(df)} rows from CEPiK source.")
