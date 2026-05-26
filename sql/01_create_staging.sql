CREATE TABLE IF NOT EXISTS stg_oferty (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(150) NOT NULL,
    price_in_pln NUMERIC(12,2),
    exchange_rate_eur NUMERIC(10,4),
    exchange_rate_usd NUMERIC(10,4),
    price_in_eur NUMERIC(12,2),
    price_in_usd NUMERIC(12,2),
    mileage INT,
    gearbox VARCHAR(50),
    engine_capacity INT,
    fuel_type VARCHAR(50),
    city VARCHAR(100),
    voivodeship VARCHAR(100),
    year INT,
    source VARCHAR(50) NOT NULL DEFAULT 'csv',
    extracted_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stg_cepik (
    id SERIAL PRIMARY KEY,
    marka VARCHAR(100) NOT NULL,
    model VARCHAR(150) NOT NULL,
    rok_produkcji INT,
    rodzaj_paliwa VARCHAR(50),
    pojemnosc_silnika INT,
    wojewodztwo VARCHAR(100),
    data_pierwszej_rejestracji DATE,
    source VARCHAR(50) NOT NULL DEFAULT 'cepik_api',
    extracted_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stg_oferty_lookup
    ON stg_oferty (brand, model, year, fuel_type, voivodeship);

CREATE INDEX IF NOT EXISTS idx_stg_cepik_lookup
    ON stg_cepik (marka, model, rok_produkcji, rodzaj_paliwa, wojewodztwo);
