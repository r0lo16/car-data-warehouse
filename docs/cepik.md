# CEPiK integration

## Scope
CEPiK API is used to enrich offer analysis with vehicle registration data.

## Current state
- integration started on branch `dawid-cepik`
- test extraction completed for 100 rows
- expected output columns:
  - `marka`
  - `model`
  - `rok_produkcji`
  - `rodzaj_paliwa`
  - `pojemnosc_silnika`
  - `wojewodztwo`
  - `data_pierwszej_rejestracji`
  - `source`

## SSL issue handled
Observed issue:
- `DH_KEY_TOO_SMALL`

Applied workaround:
- custom SSL adapter in `requests`
- lowered security level (`DEFAULT@SECLEVEL=1`) only for CEPiK calls

## Notes
- CEPiK data is joined with offers on aggregated level:
  - brand
  - model
  - year
  - fuel type
  - voivodeship
