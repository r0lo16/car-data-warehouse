# car-data-warehouse

Data warehouse project for used car market analysis in Wroclaw.

## Project scope
The project integrates:
- CSV offers data
- CEPiK API registration data
- NBP currency API rates (EUR, USD)

Stack:
- Python ETL
- PostgreSQL
- FastAPI
- Docker / Docker Compose
- Metabase
- DuckDNS
- Trello

## Goal
Build a data warehouse for analysis of:
- number of offers
- average prices and mileage
- brands, models, fuel types, years
- prices in PLN, EUR, USD
- offers vs CEPiK registrations comparison

## Architecture
CSV + CEPiK + NBP
-> Python ETL
-> PostgreSQL staging
-> PostgreSQL warehouse
-> FastAPI reporting API
-> Metabase dashboard

## Current status (2026-05-18)
Completed:
- repository and branch/PR workflow
- protected `main` branch
- VPS OVH setup
- Docker and Docker Compose setup
- PostgreSQL container running
- FastAPI container running
- FastAPI exposed by DuckDNS + Nginx Proxy Manager
- `GET /health` endpoint working

In progress:
- CEPiK extraction and integration
- NBP currency extraction and price conversion
- ETL transformations and full warehouse load

## Team workflow
- No direct push to `main`.
- Every contributor works on own branch.
- Merge to `main` only through Pull Request review.

Flow:
1. `git checkout main`
2. `git pull origin main`
3. `git checkout -b <branch-name>`
4. code + local test
5. `git add ... && git commit -m "..."`
6. `git push -u origin <branch-name>`
7. open PR `<branch-name> -> main`

## Local work
Typical local setup:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

Run ETL:
```bash
python src/load_warehouse.py
```

Run API:
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Security rules
Never commit:
- `.env`
- passwords, tokens, private keys
- cache/temp artifacts

Never use:
- `git push origin main`
- `git push --force`
