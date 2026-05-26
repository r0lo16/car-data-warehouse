# Dashboard w Metabase

## Cel
Przygotowac dashboard BI zgodny z zakresem projektu:
- KPI cards
- top 10 marek
- udzial paliw
- cena wedlug rocznika
- filtry (marka, paliwo, rok, miasto)

## Uruchomienie lokalne (Docker Compose)
1. Skopiuj konfiguracje:
   - `cp .env.example .env`
2. Uruchom uslugi:
   - `docker compose up -d postgres api metabase`
3. Sprawdz:
   - API: `http://localhost:8000/health`
   - Metabase: `http://localhost:3000`

Jesli porty sa zajete, zmien w `.env`:
- `API_PORT=8001`
- `METABASE_PORT=3001`
- `POSTGRES_PORT=5433`

## Podlaczenie PostgreSQL w Metabase
W kreatorze Metabase:
1. Add database -> PostgreSQL
2. Ustaw:
   - Host: `postgres`
   - Port: `5432`
   - Database name: `car_warehouse`
   - Username: `car_user`
   - Password: `change_this_password`
3. Save

## Raporty SQL (Metabase Questions)
### 1) KPI
```sql
SELECT
  SUM(f.liczba_ofert) AS total_offers,
  ROUND((SUM(f.cena * f.liczba_ofert)::numeric / NULLIF(SUM(f.liczba_ofert), 0)), 2) AS avg_price,
  ROUND((SUM(f.przebieg * f.liczba_ofert)::numeric / NULLIF(SUM(f.liczba_ofert), 0)), 2) AS avg_mileage
FROM fact_oferty f;
```

### 2) Top 10 marek
```sql
SELECT p.brand, SUM(f.liczba_ofert) AS offers_count
FROM fact_oferty f
JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
GROUP BY p.brand
ORDER BY offers_count DESC
LIMIT 10;
```

### 3) Udzial paliw
```sql
SELECT
  pf.fuel_type,
  SUM(f.liczba_ofert) AS offers_count,
  ROUND(100.0 * SUM(f.liczba_ofert)::numeric / NULLIF(SUM(SUM(f.liczba_ofert)) OVER (), 0), 2) AS share_pct
FROM fact_oferty f
JOIN dim_paliwo pf ON pf.id_paliwo = f.id_paliwo
GROUP BY pf.fuel_type
ORDER BY offers_count DESC;
```

### 4) Cena wedlug rocznika
```sql
SELECT
  p.year,
  ROUND((SUM(f.cena * f.liczba_ofert)::numeric / NULLIF(SUM(f.liczba_ofert), 0)), 2) AS avg_price
FROM fact_oferty f
JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
GROUP BY p.year
ORDER BY p.year;
```

### 5) Oferty vs rejestracje
```sql
SELECT
  p.brand,
  SUM(fo.liczba_ofert) AS offers_count,
  COALESCE(SUM(fr.liczba_rejestracji), 0) AS registrations_count
FROM fact_oferty fo
JOIN dim_pojazd p ON p.id_pojazd = fo.id_pojazd
LEFT JOIN fact_rejestracje fr
  ON fr.id_pojazd = fo.id_pojazd
 AND fr.id_paliwo = fo.id_paliwo
GROUP BY p.brand
ORDER BY offers_count DESC
LIMIT 15;
```

## Uklad dashboardu
- KPI cards: `total_offers`, `avg_price`, `avg_mileage`
- Bar chart: `top 10 marek`
- Pie/Donut: `udzial paliw`
- Line chart: `cena wedlug rocznika`
- Table/Bar: `oferty vs rejestracje`

## Kontrola jakosci
- odswiezanie danych po ETL: `python src/load_warehouse.py`
- sprawdzenie API: `GET /reports/*`
- zgodnosc liczb miedzy API i Metabase
