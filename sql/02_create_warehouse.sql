CREATE TABLE IF NOT EXISTS dim_czas (
    id_czas SERIAL PRIMARY KEY,
    rok INT NOT NULL,
    miesiac INT NOT NULL,
    kwartal INT NOT NULL,
    CONSTRAINT uq_dim_czas UNIQUE (rok, miesiac, kwartal)
);

CREATE TABLE IF NOT EXISTS dim_lokalizacja (
    id_lokalizacja SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL DEFAULT '',
    voivodeship VARCHAR(100) NOT NULL,
    CONSTRAINT uq_dim_lokalizacja UNIQUE (city, voivodeship)
);

CREATE TABLE IF NOT EXISTS dim_pojazd (
    id_pojazd SERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(150) NOT NULL,
    year INT NOT NULL,
    engine_capacity INT,
    CONSTRAINT uq_dim_pojazd UNIQUE (brand, model, year, engine_capacity)
);

CREATE TABLE IF NOT EXISTS dim_paliwo (
    id_paliwo SERIAL PRIMARY KEY,
    fuel_type VARCHAR(50) NOT NULL,
    CONSTRAINT uq_dim_paliwo UNIQUE (fuel_type)
);

CREATE TABLE IF NOT EXISTS dim_skrzynia (
    id_skrzynia SERIAL PRIMARY KEY,
    gearbox VARCHAR(50) NOT NULL,
    CONSTRAINT uq_dim_skrzynia UNIQUE (gearbox)
);

CREATE TABLE IF NOT EXISTS fact_oferty (
    id_oferty SERIAL PRIMARY KEY,
    id_czas INT NOT NULL REFERENCES dim_czas(id_czas),
    id_lokalizacja INT NOT NULL REFERENCES dim_lokalizacja(id_lokalizacja),
    id_pojazd INT NOT NULL REFERENCES dim_pojazd(id_pojazd),
    id_paliwo INT NOT NULL REFERENCES dim_paliwo(id_paliwo),
    id_skrzynia INT NOT NULL REFERENCES dim_skrzynia(id_skrzynia),
    cena NUMERIC(12,2),
    przebieg INT,
    pojemnosc_silnika INT,
    liczba_ofert INT NOT NULL,
    CONSTRAINT uq_fact_oferty UNIQUE (id_czas, id_lokalizacja, id_pojazd, id_paliwo, id_skrzynia)
);

CREATE TABLE IF NOT EXISTS fact_rejestracje (
    id_rejestracji SERIAL PRIMARY KEY,
    id_czas INT NOT NULL REFERENCES dim_czas(id_czas),
    id_lokalizacja INT NOT NULL REFERENCES dim_lokalizacja(id_lokalizacja),
    id_pojazd INT NOT NULL REFERENCES dim_pojazd(id_pojazd),
    id_paliwo INT NOT NULL REFERENCES dim_paliwo(id_paliwo),
    liczba_rejestracji INT NOT NULL,
    CONSTRAINT uq_fact_rejestracje UNIQUE (id_czas, id_lokalizacja, id_pojazd, id_paliwo)
);

CREATE TABLE IF NOT EXISTS etl_run_log (
    run_id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    csv_rows_raw INT NOT NULL DEFAULT 0,
    csv_rows_clean INT NOT NULL DEFAULT 0,
    cepik_rows_raw INT NOT NULL DEFAULT 0,
    cepik_rows_clean INT NOT NULL DEFAULT 0,
    cepik_api_rows_raw INT NOT NULL DEFAULT 0,
    fact_oferty_rows INT NOT NULL DEFAULT 0,
    fact_rejestracje_rows INT NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE OR REPLACE VIEW vw_oferty_vs_rejestracje AS
WITH offers_agg AS (
    SELECT
        dc.rok,
        dl.voivodeship,
        dp.brand,
        dp.model,
        dpf.fuel_type,
        SUM(fo.liczba_ofert)::INT AS liczba_ofert
    FROM fact_oferty fo
    JOIN dim_czas dc ON dc.id_czas = fo.id_czas
    JOIN dim_lokalizacja dl ON dl.id_lokalizacja = fo.id_lokalizacja
    JOIN dim_pojazd dp ON dp.id_pojazd = fo.id_pojazd
    JOIN dim_paliwo dpf ON dpf.id_paliwo = fo.id_paliwo
    GROUP BY dc.rok, dl.voivodeship, dp.brand, dp.model, dpf.fuel_type
),
regs_agg AS (
    SELECT
        dc.rok,
        dl.voivodeship,
        dp.brand,
        dp.model,
        dpf.fuel_type,
        SUM(fr.liczba_rejestracji)::INT AS liczba_rejestracji
    FROM fact_rejestracje fr
    JOIN dim_czas dc ON dc.id_czas = fr.id_czas
    JOIN dim_lokalizacja dl ON dl.id_lokalizacja = fr.id_lokalizacja
    JOIN dim_pojazd dp ON dp.id_pojazd = fr.id_pojazd
    JOIN dim_paliwo dpf ON dpf.id_paliwo = fr.id_paliwo
    GROUP BY dc.rok, dl.voivodeship, dp.brand, dp.model, dpf.fuel_type
)
SELECT
    COALESCE(o.rok, r.rok) AS rok,
    COALESCE(o.voivodeship, r.voivodeship) AS voivodeship,
    COALESCE(o.brand, r.brand) AS brand,
    COALESCE(o.model, r.model) AS model,
    COALESCE(o.fuel_type, r.fuel_type) AS fuel_type,
    COALESCE(o.liczba_ofert, 0) AS liczba_ofert,
    COALESCE(r.liczba_rejestracji, 0) AS liczba_rejestracji,
    CASE
        WHEN COALESCE(r.liczba_rejestracji, 0) = 0 THEN NULL
        ELSE ROUND((COALESCE(o.liczba_ofert, 0)::numeric / r.liczba_rejestracji::numeric), 2)
    END AS wskaznik_oferty_do_rejestracji
FROM offers_agg o
FULL OUTER JOIN regs_agg r
    ON o.rok = r.rok
   AND o.voivodeship = r.voivodeship
   AND o.brand = r.brand
   AND o.model = r.model
   AND o.fuel_type = r.fuel_type;
