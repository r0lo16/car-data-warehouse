-- KPI
SELECT
    SUM(f.liczba_ofert) AS total_offers,
    ROUND(AVG(f.cena), 2) AS avg_price,
    ROUND(AVG(f.przebieg), 0) AS avg_mileage
FROM fact_oferty f;

-- Top 10 marek wedlug liczby ofert
SELECT
    p.brand,
    SUM(f.liczba_ofert) AS offers_count
FROM fact_oferty f
JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
GROUP BY p.brand
ORDER BY offers_count DESC
LIMIT 10;

-- Srednia cena wg marki
SELECT
    p.brand,
    ROUND(AVG(f.cena), 2) AS avg_price
FROM fact_oferty f
JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
GROUP BY p.brand
ORDER BY avg_price DESC;

-- Udzial paliw
SELECT
    pf.fuel_type,
    SUM(f.liczba_ofert) AS offers_count,
    ROUND(100.0 * SUM(f.liczba_ofert) / SUM(SUM(f.liczba_ofert)) OVER (), 2) AS share_pct
FROM fact_oferty f
JOIN dim_paliwo pf ON pf.id_paliwo = f.id_paliwo
GROUP BY pf.fuel_type
ORDER BY offers_count DESC;

-- Cena wg rocznika
SELECT
    p.year,
    ROUND(AVG(f.cena), 2) AS avg_price
FROM fact_oferty f
JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
GROUP BY p.year
ORDER BY p.year;

-- Sredni przebieg wg marki
SELECT
    p.brand,
    ROUND(AVG(f.przebieg), 0) AS avg_mileage
FROM fact_oferty f
JOIN dim_pojazd p ON p.id_pojazd = f.id_pojazd
GROUP BY p.brand
ORDER BY avg_mileage DESC;

-- Liczba ofert wg miasta
SELECT
    l.city,
    SUM(f.liczba_ofert) AS offers_count
FROM fact_oferty f
JOIN dim_lokalizacja l ON l.id_lokalizacja = f.id_lokalizacja
WHERE l.city IS NOT NULL
GROUP BY l.city
ORDER BY offers_count DESC;
