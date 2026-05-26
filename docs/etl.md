# ETL - Sprint 2 (US-11 .. US-15) + rozszerzenie walutowe

## Cel
Proces ETL laduje dane z CSV oraz CEPiK do PostgreSQL i przygotowuje rozszerzenie cen o kursy NBP:
1. Ekstrakcja danych ofertowych (`data/raw/data_wroclaw_2023.csv`)
2. Ekstrakcja danych CEPiK (API lub fallback danych syntetycznych)
3. Ekstrakcja kursow walut NBP (EUR, USD)
4. Czyszczenie i normalizacja
5. Zaladowanie do tabel staging
6. Zaladowanie wymiarow i faktow modelu gwiazdy

## Wejscie
- CSV: `data/raw/data_wroclaw_2023.csv`
- CEPiK: API konfigurowane przez zmienne `CEPIK_*`
- NBP: `https://api.nbp.pl/api/exchangerates/rates/a/{code}/?format=json`

## Wyjscie
- `stg_oferty`, `stg_cepik`
- `dim_*`, `fact_oferty`, `fact_rejestracje`
- pliki pomocnicze:
  - `data/processed/offers_clean.csv`
  - `data/processed/cepik_clean.csv`
  - waluty (skrypt pomocniczy): `exchange_rate_eur`, `exchange_rate_usd`, `price_in_eur`, `price_in_usd`

## Uruchomienie
```bash
pip install -r requirements.txt
python src/load_warehouse.py
```

Uruchomienie samego skryptu walutowego:
```bash
python src/extract_currency.py
```

## Uwagi
- Jezeli API CEPiK nie jest dostepne lub brak klucza, pipeline automatycznie uzywa fallbacku (`source = cepik_fallback`), zeby nie blokowac demonstracji.
- Integracja walutowa jest podlaczona do glownego ETL (`src/load_warehouse.py`). Przy braku dostepu do NBP kolumny walutowe pozostaja puste.
- Klucze i hasla trzymamy poza repozytorium w `.env`.

## Ostatnie testy lokalne
### Test ETL + waluty (2026-05-26)
- wejscie po czyszczeniu CSV: `offers_clean=88127`
- NBP online:
  - `EUR=4.2434`
  - `USD=3.6451`
- zweryfikowane kolumny:
  - `exchange_rate_eur`
  - `exchange_rate_usd`
  - `price_in_eur`
  - `price_in_usd`

### Test CEPiK strict API (2026-05-26)
- tryb:
  - `CEPIK_FALLBACK_ONLY=false`
  - `CEPIK_STRICT_API=true`
  - `CEPIK_LIMIT=100`
  - `CEPIK_MAX_PAGES=1`
- wynik:
  - `raw=100` (source: `cepik_api`)
  - `clean=94` po transformacji i filtrach jakosci
