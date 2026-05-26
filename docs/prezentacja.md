# Plan prezentacji koncowej

## Slajd 1 - Problem biznesowy
- Cel: analiza rynku aut uzywanych we Wroclawiu.
- Potrzeba: porownanie ofert rynkowych i rejestracji CEPiK.

## Slajd 2 - Zrodla danych
- CSV ofert samochodow.
- API CEPiK.
- API NBP (kursy EUR/USD).

## Slajd 3 - Architektura
- CSV + CEPiK + NBP -> ETL Python -> PostgreSQL -> FastAPI -> dashboard.
- Narzedzia: Docker, Metabase, Trello, GitHub.

## Slajd 4 - Model hurtowni
- Star schema.
- Wymiary: czas, lokalizacja, pojazd, paliwo, skrzynia.
- Fakty: oferty i rejestracje.

## Slajd 5 - ETL
- Ekstrakcja, czyszczenie, standaryzacja.
- Ladowanie staging i warehouse.
- Wzbogacenie cen o EUR/USD.

## Slajd 6 - Integracja CEPiK
- Test strict API.
- Obsluga problemu SSL `DH_KEY_TOO_SMALL`.
- Agregacyjne laczenie danych.

## Slajd 7 - API raportowe
- `/health`
- `/offers`
- `/reports/kpi`
- `/reports/top-brands`
- `/reports/avg-price-by-brand`
- `/reports/fuel-share`
- `/reports/price-by-year`

## Slajd 8 - Dashboard i raporty
- KPI cards.
- Top marki.
- Udzial paliw.
- Cena wg rocznika.
- Oferty vs rejestracje.

## Slajd 9 - Wyniki i obserwacje
- Najpopularniejsza marka.
- Dominujace paliwo.
- Trend cen wg rocznikow.
- Roznice miedzy oferta rynku a rejestracjami.

## Slajd 10 - Ryzyka i jak je obsluzono
- Jakosc danych wejsciowych.
- Ograniczenia CEPiK.
- Bezpieczenstwo sekretow i srodowiska.

## Slajd 11 - Podzial pracy zespolu
- Dawid: architektura, ETL integracyjny, backend, DevOps.
- Kuba: waluty i ETL.
- Mateusz: SQL/BI/dashboard.

## Slajd 12 - Podsumowanie
- Co dziala end-to-end.
- Co jest gotowe pod dalszy rozwoj.
- Wnioski koncowe.
