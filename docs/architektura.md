# Architektura rozwiazania

## Cel
Hurtownia danych do analizy rynku samochodow uzywanych we Wroclawiu.

## Zrodla danych
1. CSV z ofertami samochodow
2. API CEPiK (dane rejestracyjne)
3. API NBP (kursy EUR/USD)

## Przeplyw danych
CSV + CEPiK + NBP
-> Python ETL
-> PostgreSQL staging
-> PostgreSQL warehouse (star schema)
-> FastAPI endpoints
-> Metabase dashboard

## Infrastruktura
- VPS OVH
- Docker
- Docker Compose
- PostgreSQL
- FastAPI
- Metabase
- DuckDNS
- Nginx Proxy Manager

## Model hurtowni
Star schema with dimensions:
- `dim_czas`
- `dim_lokalizacja`
- `dim_pojazd`
- `dim_paliwo`
- `dim_skrzynia`

Facts:
- `fact_oferty`
- `fact_rejestracje`
