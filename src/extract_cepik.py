from __future__ import annotations

import random
import ssl
from datetime import date
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

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

VOIVODESHIP_BY_CODE = {
    "02": "Dolnośląskie",
    "04": "Kujawsko-pomorskie",
    "06": "Lubelskie",
    "08": "Lubuskie",
    "10": "Łódzkie",
    "12": "Małopolskie",
    "14": "Mazowieckie",
    "16": "Opolskie",
    "18": "Podkarpackie",
    "20": "Podlaskie",
    "22": "Pomorskie",
    "24": "Śląskie",
    "26": "Świętokrzyskie",
    "28": "Warmińsko-mazurskie",
    "30": "Wielkopolskie",
    "32": "Zachodniopomorskie",
}


class CepikSSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx,
            **pool_kwargs,
        )


def _pick(dct: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in dct and dct[key] not in (None, ""):
            return dct[key]
    return None


def _default_wojewodztwo() -> str | None:
    return VOIVODESHIP_BY_CODE.get(str(SETTINGS.cepik_wojewodztwo).zfill(2))


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
        if not rows[-1]["wojewodztwo"]:
            rows[-1]["wojewodztwo"] = _default_wojewodztwo()
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
        "typ-daty": 1,
        "limit": SETTINGS.cepik_limit,
        "page": 1,
    }

    rows: list[dict[str, Any]] = []
    next_url: str | None = url
    page = 0
    session = requests.Session()
    session.mount("https://api.cepik.gov.pl", CepikSSLAdapter())

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
        if SETTINGS.cepik_strict_api:
            raise RuntimeError("CEPiK API returned empty payload in strict mode.")
    except requests.RequestException:
        if SETTINGS.cepik_strict_api:
            raise

    return _build_fallback_from_offers(offers_df if offers_df is not None else pd.DataFrame())


if __name__ == "__main__":
    df = extract_cepik_data()
    print(f"Extracted {len(df)} rows from CEPiK source.")
