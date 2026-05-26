from fastapi import APIRouter, Query

from backend.app.database import fetch_all

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("")
def get_offers(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    query = """
        SELECT
            p.brand,
            p.model,
            p.year,
            pf.fuel_type,
            s.gearbox,
            l.city,
            l.voivodeship,
            f.cena AS avg_price_pln,
            f.przebieg AS avg_mileage,
            f.pojemnosc_silnika AS engine_capacity,
            f.liczba_ofert AS offers_count
        FROM fact_oferty f
        JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
        JOIN dim_paliwo pf ON pf.id_paliwo = f.id_paliwo
        JOIN dim_skrzynia s ON s.id_skrzynia = f.id_skrzynia
        JOIN dim_lokalizacja l ON l.id_lokalizacja = f.id_lokalizacja
        ORDER BY f.liczba_ofert DESC, p.brand, p.model
        LIMIT :limit
        OFFSET :offset
    """
    return fetch_all(query, {"limit": limit, "offset": offset})
