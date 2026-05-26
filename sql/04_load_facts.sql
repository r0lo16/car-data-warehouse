INSERT INTO fact_oferty (
    id_czas,
    id_lokalizacja,
    id_pojazd,
    id_paliwo,
    id_skrzynia,
    cena,
    przebieg,
    pojemnosc_silnika,
    liczba_ofert
)
SELECT
    dc.id_czas,
    dl.id_lokalizacja,
    dp.id_pojazd,
    dpf.id_paliwo,
    ds.id_skrzynia,
    ROUND(AVG(o.price_in_pln), 2) AS cena,
    ROUND(AVG(o.mileage))::INT AS przebieg,
    ROUND(AVG(o.engine_capacity))::INT AS pojemnosc_silnika,
    COUNT(*)::INT AS liczba_ofert
FROM stg_oferty o
JOIN dim_czas dc
    ON dc.rok = o.year
   AND dc.miesiac = 1
   AND dc.kwartal = 1
JOIN dim_lokalizacja dl
    ON dl.city = COALESCE(o.city, '')
   AND dl.voivodeship = o.voivodeship
JOIN dim_pojazd dp
    ON dp.brand = o.brand
   AND dp.model = o.model
   AND dp.year = o.year
   AND dp.engine_capacity IS NOT DISTINCT FROM o.engine_capacity
JOIN dim_paliwo dpf
    ON dpf.fuel_type = o.fuel_type
JOIN dim_skrzynia ds
    ON ds.gearbox = o.gearbox
GROUP BY
    dc.id_czas,
    dl.id_lokalizacja,
    dp.id_pojazd,
    dpf.id_paliwo,
    ds.id_skrzynia
ON CONFLICT (id_czas, id_lokalizacja, id_pojazd, id_paliwo, id_skrzynia)
DO UPDATE SET
    cena = EXCLUDED.cena,
    przebieg = EXCLUDED.przebieg,
    pojemnosc_silnika = EXCLUDED.pojemnosc_silnika,
    liczba_ofert = EXCLUDED.liczba_ofert;

INSERT INTO fact_rejestracje (
    id_czas,
    id_lokalizacja,
    id_pojazd,
    id_paliwo,
    liczba_rejestracji
)
SELECT
    dc.id_czas,
    dl.id_lokalizacja,
    dp.id_pojazd,
    dpf.id_paliwo,
    COUNT(*)::INT AS liczba_rejestracji
FROM stg_cepik c
JOIN dim_czas dc
    ON dc.rok = EXTRACT(YEAR FROM COALESCE(c.data_pierwszej_rejestracji, MAKE_DATE(c.rok_produkcji, 1, 1)))::INT
   AND dc.miesiac = EXTRACT(MONTH FROM COALESCE(c.data_pierwszej_rejestracji, MAKE_DATE(c.rok_produkcji, 1, 1)))::INT
   AND dc.kwartal = EXTRACT(QUARTER FROM COALESCE(c.data_pierwszej_rejestracji, MAKE_DATE(c.rok_produkcji, 1, 1)))::INT
JOIN dim_lokalizacja dl
    ON dl.city = ''
   AND dl.voivodeship = c.wojewodztwo
JOIN dim_pojazd dp
    ON dp.brand = c.marka
   AND dp.model = c.model
   AND dp.year = c.rok_produkcji
   AND dp.engine_capacity IS NOT DISTINCT FROM c.pojemnosc_silnika
JOIN dim_paliwo dpf
    ON dpf.fuel_type = c.rodzaj_paliwa
GROUP BY
    dc.id_czas,
    dl.id_lokalizacja,
    dp.id_pojazd,
    dpf.id_paliwo
ON CONFLICT (id_czas, id_lokalizacja, id_pojazd, id_paliwo)
DO UPDATE SET
    liczba_rejestracji = EXCLUDED.liczba_rejestracji;
