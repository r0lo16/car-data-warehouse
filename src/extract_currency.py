from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import requests

NBP_API_URL = "https://api.nbp.pl/api/exchangerates/rates/a/{code}/?format=json"


@dataclass(frozen=True)
class CurrencyRates:
    eur: float
    usd: float


def get_exchange_rate(currency_code: str, timeout: int = 30) -> float:
    code = currency_code.lower().strip()
    response = requests.get(NBP_API_URL.format(code=code), timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return float(data["rates"][0]["mid"])


def get_currency_rates() -> CurrencyRates:
    return CurrencyRates(
        eur=get_exchange_rate("eur"),
        usd=get_exchange_rate("usd"),
    )


def try_get_currency_rates() -> Optional[CurrencyRates]:
    try:
        return get_currency_rates()
    except requests.RequestException:
        return None


def convert_pln_to_currency(price_pln: float, rate: float) -> float:
    return round(float(price_pln) / rate, 2)


def enrich_prices_with_currency(df: pd.DataFrame, rates: CurrencyRates) -> pd.DataFrame:
    required_column = "price_in_pln"
    if required_column not in df.columns:
        raise ValueError(f"Missing required column: {required_column}")

    enriched = df.copy()
    enriched["exchange_rate_eur"] = rates.eur
    enriched["exchange_rate_usd"] = rates.usd
    enriched["price_in_eur"] = enriched["price_in_pln"].astype(float).map(
        lambda price: convert_pln_to_currency(price, rates.eur)
    )
    enriched["price_in_usd"] = enriched["price_in_pln"].astype(float).map(
        lambda price: convert_pln_to_currency(price, rates.usd)
    )
    return enriched


def enrich_prices_with_empty_currency(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["exchange_rate_eur"] = pd.NA
    enriched["exchange_rate_usd"] = pd.NA
    enriched["price_in_eur"] = pd.NA
    enriched["price_in_usd"] = pd.NA
    return enriched


if __name__ == "__main__":
    rates = get_currency_rates()
    test_price = 100000

    print(f"EUR rate: {rates.eur}")
    print(f"USD rate: {rates.usd}")
    print(f"{test_price} PLN -> EUR: {convert_pln_to_currency(test_price, rates.eur)}")
    print(f"{test_price} PLN -> USD: {convert_pln_to_currency(test_price, rates.usd)}")
