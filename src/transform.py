from __future__ import annotations

import re
from datetime import date

import pandas as pd

POLISH_MOJIBAKE_HINTS = ("Ĺ", "Ă", "Å", "â")


def _fix_mojibake(value: str) -> str:
    if not isinstance(value, str):
        return value
    if not any(hint in value for hint in POLISH_MOJIBAKE_HINTS):
        return value
    try:
        return value.encode("latin1").decode("utf-8")
    except UnicodeError:
        return value


def _normalize_text(value: object, keep_case: bool = False) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    text = _fix_mojibake(str(value)).strip()
    if not text:
        return None

    text = re.sub(r"\s+", " ", text)
    if keep_case:
        return text
    return text.title()


def _parse_int(value: object) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    digits = re.sub(r"[^\d]", "", str(value))
    if not digits:
        return None
    return int(digits)


def _parse_price(value: object) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    cleaned = re.sub(r"[^\d,\.]", "", str(value)).replace(",", ".")
    if cleaned.count(".") > 1:
        first, *rest = cleaned.split(".")
        cleaned = first + "." + "".join(rest)
    try:
        return round(float(cleaned), 2)
    except ValueError:
        return None


def transform_offers(df: pd.DataFrame) -> pd.DataFrame:
    offers = df.copy()
    offers["brand"] = offers["brand"].map(lambda x: _normalize_text(x)).str.replace("-", " ", regex=False)
    offers["model"] = offers["model"].map(lambda x: _normalize_text(x, keep_case=True))
    offers["price_in_pln"] = offers["price_in_pln"].map(_parse_price)
    offers["mileage"] = offers["mileage"].map(_parse_int)
    offers["gearbox"] = offers["gearbox"].map(lambda x: _normalize_text(x))
    offers["engine_capacity"] = offers["engine_capacity"].map(_parse_int)
    offers["fuel_type"] = offers["fuel_type"].map(lambda x: _normalize_text(x))
    offers["city"] = offers["city"].map(lambda x: _normalize_text(x, keep_case=True))
    offers["voivodeship"] = offers["voivodeship"].map(lambda x: _normalize_text(x))
    offers["year"] = offers["year"].map(_parse_int)
    offers["source"] = offers.get("source", "csv_offers").fillna("csv_offers")

    offers = offers.dropna(subset=["brand", "model", "year", "fuel_type", "voivodeship"])
    offers = offers[offers["price_in_pln"].notna() & (offers["price_in_pln"] > 0)]
    offers = offers[offers["year"].between(1950, date.today().year)]

    return offers.reset_index(drop=True)


def transform_cepik(df: pd.DataFrame) -> pd.DataFrame:
    cepik = df.copy()

    if cepik.empty:
        return pd.DataFrame(
            columns=[
                "marka",
                "model",
                "rok_produkcji",
                "rodzaj_paliwa",
                "pojemnosc_silnika",
                "wojewodztwo",
                "data_pierwszej_rejestracji",
                "source",
            ]
        )

    cepik["marka"] = cepik["marka"].map(lambda x: _normalize_text(x)).str.replace("-", " ", regex=False)
    cepik["model"] = cepik["model"].map(lambda x: _normalize_text(x, keep_case=True))
    cepik["rok_produkcji"] = cepik["rok_produkcji"].map(_parse_int)
    cepik["rodzaj_paliwa"] = cepik["rodzaj_paliwa"].map(lambda x: _normalize_text(x))
    cepik["pojemnosc_silnika"] = cepik["pojemnosc_silnika"].map(_parse_int)
    cepik["wojewodztwo"] = cepik["wojewodztwo"].map(lambda x: _normalize_text(x))
    cepik["data_pierwszej_rejestracji"] = pd.to_datetime(
        cepik["data_pierwszej_rejestracji"], errors="coerce"
    ).dt.date
    cepik["source"] = cepik.get("source", "cepik_api").fillna("cepik_api")

    cepik = cepik.dropna(subset=["marka", "model", "rok_produkcji", "rodzaj_paliwa", "wojewodztwo"])
    cepik = cepik[cepik["rok_produkcji"].between(1950, date.today().year)]

    return cepik.reset_index(drop=True)
