from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_STAGING_DIR = PROJECT_ROOT / "data" / "staging"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SQL_DIR = PROJECT_ROOT / "sql"


@dataclass(frozen=True)
class Settings:
    postgres_user: str = os.getenv("POSTGRES_USER", os.getenv("CAR_POSTGRES_USER", "car_user"))
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", os.getenv("CAR_POSTGRES_PASSWORD", "change_this_password"))
    postgres_db: str = os.getenv("POSTGRES_DB", os.getenv("CAR_POSTGRES_DB", "car_warehouse"))
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: str = os.getenv("POSTGRES_PORT", "5432")
    database_url: str = os.getenv(
        "DATABASE_URL",
        (
            "postgresql://"
            f"{os.getenv('POSTGRES_USER', os.getenv('CAR_POSTGRES_USER', 'car_user'))}:"
            f"{os.getenv('POSTGRES_PASSWORD', os.getenv('CAR_POSTGRES_PASSWORD', 'change_this_password'))}@"
            f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
            f"{os.getenv('POSTGRES_PORT', '5432')}/"
            f"{os.getenv('POSTGRES_DB', os.getenv('CAR_POSTGRES_DB', 'car_warehouse'))}"
        ),
    )
    offers_csv_path: Path = Path(os.getenv("OFFERS_CSV_PATH", DATA_RAW_DIR / "data_wroclaw_2023.csv"))
    cepik_base_url: str = os.getenv("CEPIK_BASE_URL", "https://api.cepik.gov.pl")
    cepik_resource: str = os.getenv("CEPIK_RESOURCE", "/v1/pojazdy")
    cepik_api_key: str | None = os.getenv("CEPIK_API_KEY")
    cepik_limit: int = int(os.getenv("CEPIK_LIMIT", "200"))
    cepik_max_pages: int = int(os.getenv("CEPIK_MAX_PAGES", "5"))
    cepik_wojewodztwo: str = os.getenv("CEPIK_WOJEWODZTWO", "02")
    cepik_data_od: str = os.getenv("CEPIK_DATA_OD", "20230101")
    cepik_data_do: str = os.getenv("CEPIK_DATA_DO", "20231231")
    cepik_fallback_only: bool = os.getenv("CEPIK_FALLBACK_ONLY", "false").lower() == "true"


SETTINGS = Settings()
