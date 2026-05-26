# Model danych hurtowni

## Typ modelu
Model gwiazdy z dwiema tabelami faktow:
- `fact_oferty`
- `fact_rejestracje`

Wspoldzielone wymiary:
- `dim_czas`
- `dim_lokalizacja`
- `dim_pojazd`
- `dim_paliwo`
- `dim_skrzynia` (tylko dla ofert)

## Ziarno tabel faktow
### `fact_oferty`
Jeden rekord opisuje agregat ofert dla kombinacji:
- czasu (`id_czas`)
- lokalizacji (`id_lokalizacja`)
- pojazdu (`id_pojazd`)
- paliwa (`id_paliwo`)
- skrzyni (`id_skrzynia`)

Miary:
- `cena` (srednia cena PLN)
- `przebieg` (sredni przebieg)
- `pojemnosc_silnika` (srednia pojemnosc)
- `liczba_ofert`

### `fact_rejestracje`
Jeden rekord opisuje agregat rejestracji CEPiK dla kombinacji:
- czasu (`id_czas`)
- lokalizacji (`id_lokalizacja`)
- pojazdu (`id_pojazd`)
- paliwa (`id_paliwo`)

Miara:
- `liczba_rejestracji`

## Klucze i ograniczenia
- wszystkie `dim_*` maja klucze surrogate (`SERIAL`)
- `fact_*` maja klucze surrogate + klucze naturalne wymuszone przez `UNIQUE`
- relacje fact -> dimension sa wymuszone przez FK

Najwazniejsze unikalnosci:
- `dim_czas`: `(rok, miesiac, kwartal)`
- `dim_lokalizacja`: `(city, voivodeship)`
- `dim_pojazd`: `(brand, model, year, engine_capacity)`
- `fact_oferty`: `(id_czas, id_lokalizacja, id_pojazd, id_paliwo, id_skrzynia)`
- `fact_rejestracje`: `(id_czas, id_lokalizacja, id_pojazd, id_paliwo)`

## Mapowanie zrodel do modelu
### CSV -> staging -> warehouse
`stg_oferty`:
- `brand`, `model`, `year`, `fuel_type`, `gearbox`, `city`, `voivodeship`
- `price_in_pln`, `mileage`, `engine_capacity`
- rozszerzenie NBP: `exchange_rate_eur`, `exchange_rate_usd`, `price_in_eur`, `price_in_usd`

### CEPiK API -> staging -> warehouse
`stg_cepik`:
- `marka`, `model`, `rok_produkcji`, `rodzaj_paliwa`
- `pojemnosc_silnika`, `wojewodztwo`, `data_pierwszej_rejestracji`

## Logika ladowania
1. ETL zapisuje dane do `stg_oferty` i `stg_cepik`.
2. Ladowane sa wymiary `dim_*` z deduplikacja (`ON CONFLICT DO NOTHING`).
3. Ladowane sa fakty z agregacja i upsertem (`ON CONFLICT DO UPDATE`).

## Uwagi projektowe
- Laczenie ofert i rejestracji jest agregacyjne (nie po VIN).
- Dla rejestracji lokalizacja korzysta z poziomu wojewodztwa (miasto = pusty string).
- Pipeline wspiera fallback CEPiK, ale posiada tez tryb strict (`CEPIK_STRICT_API=true`) do walidacji realnego API.
