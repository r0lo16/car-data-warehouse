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

## Wynik

Skrypt `src/extract_cepik.py` zapisuje dane do:

`data/raw/cepik_dolnoslaskie_2023.csv`
