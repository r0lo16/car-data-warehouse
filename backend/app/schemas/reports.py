from pydantic import BaseModel


class KpiResponse(BaseModel):
    total_offers: int
    total_registrations: int
    offers_to_registrations_ratio: float
    avg_price: float
    avg_mileage: float
    top_brand: str
    top_fuel: str


class ExchangeRatesResponse(BaseModel):
    base_currency: str
    rates: dict[str, float]
    effective_dates: dict[str, str | None]
    source: str


class BrandCountResponse(BaseModel):
    brand: str
    offers_count: int


class BrandAvgPriceResponse(BaseModel):
    brand: str
    avg_price: float


class FuelShareResponse(BaseModel):
    fuel_type: str
    offers_count: int
    share_pct: float


class YearPriceResponse(BaseModel):
    year: int
    avg_price: float


class BrandComparisonResponse(BaseModel):
    brand: str
    offers_count: int
    registrations_count: int
    offers_share_pct: float
    registrations_share_pct: float
    registrations_per_1000_offers: float
