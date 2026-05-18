from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import SETTINGS


def get_engine() -> Engine:
    return create_engine(SETTINGS.database_url, future=True)


def execute_sql_file(engine: Engine, sql_file_path: Path) -> None:
    sql = sql_file_path.read_text(encoding="utf-8")
    with engine.begin() as connection:
        connection.execute(text(sql))


def load_staging_tables(engine: Engine, offers_df: pd.DataFrame, cepik_df: pd.DataFrame) -> None:
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE stg_oferty, stg_cepik RESTART IDENTITY;"))

    offers_df.to_sql("stg_oferty", engine, if_exists="append", index=False, method="multi", chunksize=2000)
    cepik_df.to_sql("stg_cepik", engine, if_exists="append", index=False, method="multi", chunksize=2000)
