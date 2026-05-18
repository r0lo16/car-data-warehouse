# Integracja z API CEPiK

## Cel

API CEPiK zostało wykorzystane jako dodatkowe źródło danych rejestracyjnych pojazdów.

## Zakres danych

Pobierane są dane dla:
- województwa dolnośląskiego,
- roku 2023,
- pojazdów zarejestrowanych.

## Pola

- marka,
- model,
- rok produkcji,
- rodzaj paliwa,
- pojemność silnika,
- data pierwszej rejestracji,
- województwo.

## Sposób połączenia z CSV

Dane z CEPiK nie są łączone z ofertami po pojedynczym pojeździe, ponieważ CSV nie zawiera numeru VIN ani numeru rejestracyjnego.

Integracja odbywa się agregacyjnie po:
- marce,
- modelu,
- roku produkcji,
- rodzaju paliwa,
- województwie.


## Problem SSL

Podczas połączenia z API CEPiK na nowszej wersji OpenSSL wystąpił błąd `DH_KEY_TOO_SMALL`. W skrypcie zastosowano własny adapter SSL dla biblioteki requests, który obniża poziom bezpieczeństwa SSL tylko dla połączenia z API CEPiK.

## Wynik testu

Skrypt `src/extract_cepik.py` został uruchomiony poprawnie i pobrał 100 rekordów z API CEPiK. Wynik zapisano do pliku:

`data/raw/cepik_dolnoslaskie_2023.csv`
