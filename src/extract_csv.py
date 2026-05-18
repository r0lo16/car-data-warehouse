from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import SETTINGS

REQUIRED_COLUMNS = [
    "brand",
    "model",
    "price_in_pln",
    "mileage",
    "gearbox",
    "engine_capacity",
    "fuel_type",
    "city",
    "voivodeship",
    "year",
]


def _read_csv_with_fallback(path: Path) -> pd.DataFrame:
    attempted = []
    for encoding in ("utf-8", "utf-8-sig", "cp1250", "latin1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            attempted.append(encoding)
    raise UnicodeDecodeError("csv", b"", 0, 1, f"Cannot decode file. Tried: {attempted}")


def extract_offers_csv(path: Path | None = None) -> pd.DataFrame:
    csv_path = Path(path or SETTINGS.offers_csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Offers CSV file not found: {csv_path}")

    df = _read_csv_with_fallback(csv_path)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"CSV file is missing required columns: {missing}")

    df = df[REQUIRED_COLUMNS].copy()
    df["source"] = "csv_offers"
    return df


if __name__ == "__main__":
    dataframe = extract_offers_csv()
    print(f"Extracted {len(dataframe)} rows from CSV.")
