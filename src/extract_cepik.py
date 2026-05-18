import ssl
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager


BASE_URL = "https://api.cepik.gov.pl/pojazdy"


class SSLAdapter(HTTPAdapter):
    """
    Adapter SSL dla API CEPiK.
    CEPiK może używać starszych parametrów SSL, które są blokowane
    przez nowsze wersje OpenSSL.
    """

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)


def create_session() -> requests.Session:
    session = requests.Session()
    session.mount("https://", SSLAdapter())
    return session


def fetch_cepik_data(limit: int = 100) -> pd.DataFrame:
    params = {
        "wojewodztwo": "02",
        "data-od": "20230101",
        "data-do": "20231231",
        "typ-daty": 2,
        "tylko-zarejestrowane": "true",
        "pokaz-wszystkie-pola": "true",
        "limit": limit,
    }

    session = create_session()

    response = session.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()
    rows = []

    for item in payload.get("data", []):
        attributes = item.get("attributes", {})

        rows.append({
            "marka": attributes.get("marka"),
            "model": attributes.get("model"),
            "rok_produkcji": attributes.get("rok-produkcji"),
            "rodzaj_paliwa": attributes.get("rodzaj-paliwa"),
            "pojemnosc_silnika": attributes.get("pojemnosc-silnika"),
            "data_pierwszej_rejestracji": attributes.get("data-pierwszej-rejestracji-w-kraju"),
            "wojewodztwo": "dolnośląskie",
            "source": "CEPiK",
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = fetch_cepik_data(limit=100)

    print(df.head())
    print(df.shape)

    output_path = "data/raw/cepik_dolnoslaskie_2023.csv"
    df.to_csv(output_path, index=False)

    print(f"Zapisano: {output_path}")
