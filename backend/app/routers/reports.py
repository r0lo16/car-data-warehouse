from __future__ import annotations

from datetime import datetime, timezone
import re

import requests
from fastapi import APIRouter, Query

from backend.app.database import fetch_all, fetch_one
from backend.app.schemas.reports import (
    BrandAvgPriceResponse,
    BrandComparisonResponse,
    BrandCountResponse,
    ExchangeRatesResponse,
    FuelShareResponse,
    KpiResponse,
    YearPriceResponse,
)

router = APIRouter(prefix="/reports", tags=["reports"])
_nbp_rates_cache: dict[str, object] = {}
_nbp_url_template = "https://api.nbp.pl/api/exchangerates/rates/a/{code}/?format=json"
_supported_default_codes = ["EUR", "USD", "GBP", "CHF", "CZK", "NOK", "SEK"]


def _fetch_nbp_rate(code: str) -> tuple[float, str | None]:
    response = requests.get(_nbp_url_template.format(code=code.lower()), timeout=20)
    response.raise_for_status()
    payload = response.json()
    rate = float(payload["rates"][0]["mid"])
    effective_date = payload["rates"][0].get("effectiveDate")
    return rate, effective_date


def _normalize_codes(codes: str | None) -> list[str]:
    if not codes:
        return _supported_default_codes
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in codes.split(","):
        code = raw.strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", code):
            continue
        if code in seen:
            continue
        seen.add(code)
        normalized.append(code)
    return normalized or _supported_default_codes


def _get_rates_from_staging() -> dict[str, float]:
    row = fetch_one(
        """
        SELECT
            ROUND(AVG(exchange_rate_eur), 4)::float AS eur,
            ROUND(AVG(exchange_rate_usd), 4)::float AS usd,
            MAX(extracted_at)::TEXT AS extracted_at
        FROM stg_oferty
        WHERE exchange_rate_eur IS NOT NULL
          AND exchange_rate_usd IS NOT NULL
        """
    )
    if not row:
        return {}
    rates: dict[str, float] = {}
    if row["eur"] is not None:
        rates["EUR"] = float(row["eur"])
    if row["usd"] is not None:
        rates["USD"] = float(row["usd"])
    return rates


def _get_exchange_rates_cached(codes: list[str], ttl_seconds: int = 3600) -> ExchangeRatesResponse:
    cache_key = ",".join(codes)
    now_ts = datetime.now(tz=timezone.utc).timestamp()
    cached_bucket = _nbp_rates_cache.get(cache_key)
    if isinstance(cached_bucket, dict):
        cached_payload = cached_bucket.get("payload")
        cached_expires = float(cached_bucket.get("expires_at_ts", 0.0))
        if cached_payload is not None and now_ts < cached_expires:
            return cached_payload  # type: ignore[return-value]

    rates: dict[str, float] = {}
    effective_dates: dict[str, str | None] = {}
    had_nbp_error = False
    for code in codes:
        try:
            rate, effective_date = _fetch_nbp_rate(code)
            rates[code] = rate
            effective_dates[code] = effective_date
        except requests.RequestException:
            had_nbp_error = True

    staging_rates = _get_rates_from_staging()
    fallback_used = False
    for code in codes:
        if code not in rates and code in staging_rates:
            rates[code] = staging_rates[code]
            effective_dates[code] = None
            fallback_used = True

    if not rates:
        rates = {"EUR": 1.0, "USD": 1.0}
        effective_dates = {"EUR": None, "USD": None}
        source = "default_fallback"
    elif fallback_used and had_nbp_error:
        source = "nbp_api_with_staging_fallback"
    elif fallback_used:
        source = "staging_fallback"
    else:
        source = "nbp_api"

    payload = ExchangeRatesResponse(
        base_currency="PLN",
        rates=rates,
        effective_dates=effective_dates,
        source=source,
    )
    _nbp_rates_cache[cache_key] = {"payload": payload, "expires_at_ts": now_ts + ttl_seconds}
    return payload


@router.get("/kpi", response_model=KpiResponse)
def get_kpi() -> KpiResponse:
    metrics_query = """
        SELECT
            COALESCE(SUM(f.liczba_ofert), 0)::INT AS total_offers,
            COALESCE(ROUND((SUM(f.cena * f.liczba_ofert)::numeric / NULLIF(SUM(f.liczba_ofert), 0)), 2), 0)::float AS avg_price,
            COALESCE(ROUND((SUM(f.przebieg * f.liczba_ofert)::numeric / NULLIF(SUM(f.liczba_ofert), 0)), 2), 0)::float AS avg_mileage
        FROM fact_oferty f
    """
    top_brand_query = """
        SELECT p.brand
        FROM fact_oferty f
        JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
        GROUP BY p.brand
        ORDER BY SUM(f.liczba_ofert) DESC
        LIMIT 1
    """
    top_fuel_query = """
        SELECT pf.fuel_type
        FROM fact_oferty f
        JOIN dim_paliwo pf ON pf.id_paliwo = f.id_paliwo
        GROUP BY pf.fuel_type
        ORDER BY SUM(f.liczba_ofert) DESC
        LIMIT 1
    """
    registrations_query = """
        SELECT COALESCE(SUM(liczba_rejestracji), 0)::INT AS total_registrations
        FROM fact_rejestracje
    """

    metrics = fetch_one(metrics_query) or {"total_offers": 0, "avg_price": 0.0, "avg_mileage": 0.0}
    registrations = fetch_one(registrations_query) or {"total_registrations": 0}
    top_brand = fetch_one(top_brand_query)
    top_fuel = fetch_one(top_fuel_query)
    ratio = round(
        (metrics["total_offers"] / registrations["total_registrations"]) if registrations["total_registrations"] else 0.0,
        2,
    )

    return KpiResponse(
        total_offers=metrics["total_offers"],
        total_registrations=registrations["total_registrations"],
        offers_to_registrations_ratio=ratio,
        avg_price=metrics["avg_price"],
        avg_mileage=metrics["avg_mileage"],
        top_brand=(top_brand["brand"] if top_brand else "N/A"),
        top_fuel=(top_fuel["fuel_type"] if top_fuel else "N/A"),
    )


@router.get("/exchange-rates", response_model=ExchangeRatesResponse)
def get_exchange_rates(codes: str | None = Query(default=None)) -> ExchangeRatesResponse:
    normalized_codes = _normalize_codes(codes)
    return _get_exchange_rates_cached(normalized_codes)


@router.get("/top-brands", response_model=list[BrandCountResponse])
def top_brands() -> list[BrandCountResponse]:
    query = """
        SELECT
            p.brand,
            SUM(f.liczba_ofert)::INT AS offers_count
        FROM fact_oferty f
        JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
        GROUP BY p.brand
        ORDER BY offers_count DESC
        LIMIT 10
    """
    return [BrandCountResponse(**row) for row in fetch_all(query)]


@router.get("/avg-price-by-brand", response_model=list[BrandAvgPriceResponse])
def avg_price_by_brand() -> list[BrandAvgPriceResponse]:
    query = """
        SELECT
            p.brand,
            ROUND((SUM(f.cena * f.liczba_ofert)::numeric / NULLIF(SUM(f.liczba_ofert), 0)), 2)::float AS avg_price
        FROM fact_oferty f
        JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
        GROUP BY p.brand
        ORDER BY avg_price DESC
        LIMIT 20
    """
    return [BrandAvgPriceResponse(**row) for row in fetch_all(query)]


@router.get("/fuel-share", response_model=list[FuelShareResponse])
def fuel_share() -> list[FuelShareResponse]:
    query = """
        SELECT
            pf.fuel_type,
            SUM(f.liczba_ofert)::INT AS offers_count,
            ROUND(
                100.0 * SUM(f.liczba_ofert)::numeric / NULLIF(SUM(SUM(f.liczba_ofert)) OVER (), 0),
                2
            )::float AS share_pct
        FROM fact_oferty f
        JOIN dim_paliwo pf ON pf.id_paliwo = f.id_paliwo
        GROUP BY pf.fuel_type
        ORDER BY offers_count DESC
    """
    return [FuelShareResponse(**row) for row in fetch_all(query)]


@router.get("/price-by-year", response_model=list[YearPriceResponse])
def price_by_year() -> list[YearPriceResponse]:
    query = """
        SELECT
            p.year,
            ROUND((SUM(f.cena * f.liczba_ofert)::numeric / NULLIF(SUM(f.liczba_ofert), 0)), 2)::float AS avg_price
        FROM fact_oferty f
        JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
        GROUP BY p.year
        ORDER BY p.year
    """
    return [YearPriceResponse(**row) for row in fetch_all(query)]


@router.get("/offers-vs-registrations", response_model=list[BrandComparisonResponse])
def offers_vs_registrations() -> list[BrandComparisonResponse]:
    query = """
        WITH offers AS (
            SELECT p.brand, SUM(f.liczba_ofert)::INT AS offers_count
            FROM fact_oferty f
            JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
            GROUP BY p.brand
        ),
        regs AS (
            SELECT p.brand, SUM(fr.liczba_rejestracji)::INT AS registrations_count
            FROM fact_rejestracje fr
            JOIN dim_pojazd p ON p.id_pojazd = fr.id_pojazd
            GROUP BY p.brand
        ),
        joined AS (
            SELECT
                o.brand,
                o.offers_count,
                COALESCE(r.registrations_count, 0)::INT AS registrations_count
            FROM offers o
            LEFT JOIN regs r ON r.brand = o.brand
        )
        SELECT
            brand,
            offers_count,
            registrations_count,
            ROUND(
                100.0 * offers_count::numeric / NULLIF(SUM(offers_count) OVER (), 0),
                2
            )::float AS offers_share_pct,
            ROUND(
                100.0 * registrations_count::numeric / NULLIF(SUM(registrations_count) OVER (), 0),
                2
            )::float AS registrations_share_pct,
            ROUND(
                1000.0 * registrations_count::numeric / NULLIF(offers_count, 0),
                2
            )::float AS registrations_per_1000_offers
        FROM joined
        ORDER BY offers_count DESC
        LIMIT 15
    """
    return [BrandComparisonResponse(**row) for row in fetch_all(query)]
