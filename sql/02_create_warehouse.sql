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
