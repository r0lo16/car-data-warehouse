CREATE TABLE IF NOT EXISTS stg_oferty (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(100),
    model VARCHAR(100),
    price_in_pln NUMERIC(12,2),
    mileage INT,
    gearbox VARCHAR(50),
    engine_capacity INT,
    fuel_type VARCHAR(50),
    city VARCHAR(100),
    voivodeship VARCHAR(100),
    year INT,
    source VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS stg_cepik (
    id SERIAL PRIMARY KEY,
    marka VARCHAR(100),
    model VARCHAR(100),
    rok_produkcji INT,
    rodzaj_paliwa VARCHAR(50),
    pojemnosc_silnika INT,
    wojewodztwo VARCHAR(100),
    data_pierwszej_rejestracji DATE,
    source VARCHAR(50)
);
