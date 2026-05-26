INSERT INTO dim_czas (rok, miesiac, kwartal)
SELECT DISTINCT
    o.year AS rok,
    1 AS miesiac,
    1 AS kwartal
FROM stg_oferty o
WHERE o.year IS NOT NULL
ON CONFLICT (rok, miesiac, kwartal) DO NOTHING;

INSERT INTO dim_czas (rok, miesiac, kwartal)
SELECT DISTINCT
    EXTRACT(YEAR FROM COALESCE(c.data_pierwszej_rejestracji, MAKE_DATE(c.rok_produkcji, 1, 1)))::INT AS rok,
    EXTRACT(MONTH FROM COALESCE(c.data_pierwszej_rejestracji, MAKE_DATE(c.rok_produkcji, 1, 1)))::INT AS miesiac,
    EXTRACT(QUARTER FROM COALESCE(c.data_pierwszej_rejestracji, MAKE_DATE(c.rok_produkcji, 1, 1)))::INT AS kwartal
FROM stg_cepik c
WHERE c.rok_produkcji IS NOT NULL OR c.data_pierwszej_rejestracji IS NOT NULL
ON CONFLICT (rok, miesiac, kwartal) DO NOTHING;

INSERT INTO dim_lokalizacja (city, voivodeship)
SELECT DISTINCT
    COALESCE(NULLIF(TRIM(o.city), ''), '') AS city,
    TRIM(o.voivodeship)
FROM stg_oferty o
WHERE o.voivodeship IS NOT NULL AND TRIM(o.voivodeship) <> ''
ON CONFLICT (city, voivodeship) DO NOTHING;

INSERT INTO dim_lokalizacja (city, voivodeship)
SELECT DISTINCT
    ''::VARCHAR(100) AS city,
    TRIM(c.wojewodztwo) AS voivodeship
FROM stg_cepik c
WHERE c.wojewodztwo IS NOT NULL AND TRIM(c.wojewodztwo) <> ''
ON CONFLICT (city, voivodeship) DO NOTHING;

INSERT INTO dim_paliwo (fuel_type)
SELECT DISTINCT TRIM(o.fuel_type)
FROM stg_oferty o
WHERE o.fuel_type IS NOT NULL AND TRIM(o.fuel_type) <> ''
ON CONFLICT (fuel_type) DO NOTHING;

INSERT INTO dim_paliwo (fuel_type)
SELECT DISTINCT TRIM(c.rodzaj_paliwa)
FROM stg_cepik c
WHERE c.rodzaj_paliwa IS NOT NULL AND TRIM(c.rodzaj_paliwa) <> ''
ON CONFLICT (fuel_type) DO NOTHING;

INSERT INTO dim_skrzynia (gearbox)
SELECT DISTINCT TRIM(o.gearbox)
FROM stg_oferty o
WHERE o.gearbox IS NOT NULL AND TRIM(o.gearbox) <> ''
ON CONFLICT (gearbox) DO NOTHING;

INSERT INTO dim_pojazd (brand, model, year, engine_capacity)
SELECT DISTINCT
    TRIM(o.brand),
    TRIM(o.model),
    o.year,
    o.engine_capacity
FROM stg_oferty o
WHERE o.brand IS NOT NULL
  AND o.model IS NOT NULL
  AND o.year IS NOT NULL
ON CONFLICT (brand, model, year, engine_capacity) DO NOTHING;

INSERT INTO dim_pojazd (brand, model, year, engine_capacity)
SELECT DISTINCT
    TRIM(c.marka) AS brand,
    TRIM(c.model) AS model,
    c.rok_produkcji AS year,
    c.pojemnosc_silnika AS engine_capacity
FROM stg_cepik c
WHERE c.marka IS NOT NULL
  AND c.model IS NOT NULL
  AND c.rok_produkcji IS NOT NULL
ON CONFLICT (brand, model, year, engine_capacity) DO NOTHING;
