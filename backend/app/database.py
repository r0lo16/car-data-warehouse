from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    (
        "postgresql://"
        f"{os.getenv('POSTGRES_USER', 'car_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'change_this_password')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'car_warehouse')}"
    ),
)

engine: Engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)


def _to_json(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


def fetch_all(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    with engine.connect() as connection:
        result = connection.execute(text(query), params or {})
        rows = []
        for row in result.mappings():
            rows.append({key: _to_json(value) for key, value in row.items()})
        return rows


def fetch_one(query: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    rows = fetch_all(query, params)
    return rows[0] if rows else None
