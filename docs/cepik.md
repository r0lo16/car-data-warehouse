# CEPiK integration

## Scope
CEPiK API is used to enrich offer analysis with vehicle registration data.

## Current state
- integration started on branch `dawid-cepik`
- test extraction completed for 100 rows
- strict API test completed on 2026-05-26 (without `fallback_only`)
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

## API endpoint and request mode
- base URL: `https://api.cepik.gov.pl`
- resource: `/pojazdy`
- required query params for list endpoint:
  - `wojewodztwo`
  - `data-od`
- optional:
  - `data-do`
  - `typ-daty`
  - `limit`
  - `page`

## Test result (2026-05-26)
Execution mode:
- `CEPIK_FALLBACK_ONLY=false`
- `CEPIK_STRICT_API=true`
- `CEPIK_LIMIT=100`
- `CEPIK_MAX_PAGES=1`

Result:
- extracted rows: `100`
- source distribution: `{'cepik_api': 100}`
- transformed rows accepted by ETL quality filters: `94`

Notes:
- CEPiK responses can miss `wojewodztwo`; extractor now fills this from configured code (example: `02 -> Dolnośląskie`) to keep rows loadable.
- in strict mode (`CEPIK_STRICT_API=true`) extractor raises errors instead of silently switching to fallback.

## Notes
- CEPiK data is joined with offers on aggregated level:
  - brand
  - model
  - year
  - fuel type
  - voivodeship
