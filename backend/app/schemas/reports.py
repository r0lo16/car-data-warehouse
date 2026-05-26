from pydantic import BaseModel


class KpiResponse(BaseModel):
    total_offers: int
    avg_price: float
    avg_mileage: float
    top_brand: str
    top_fuel: str


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
