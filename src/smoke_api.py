from __future__ import annotations

import argparse
import json
from typing import Any

import requests


def _show(value: Any, limit: int = 240) -> str:
    text = json.dumps(value, ensure_ascii=False)
    return text[:limit] + ("..." if len(text) > limit else "")


def run_smoke(base_url: str, timeout: int = 30) -> int:
    base = base_url.rstrip("/")
    endpoints = [
        "/health",
        "/offers?limit=5",
        "/reports/kpi",
        "/reports/top-brands",
        "/reports/avg-price-by-brand",
        "/reports/fuel-share",
        "/reports/price-by-year",
    ]

    session = requests.Session()
    failures = 0

    print(f"SMOKE TEST BASE URL: {base}")
    for path in endpoints:
        url = f"{base}{path}"
        try:
            response = session.get(url, timeout=timeout)
            ok = response.status_code == 200
            payload = response.json() if "application/json" in response.headers.get("content-type", "") else response.text
            print(f"[{response.status_code}] {path} -> {_show(payload)}")
            if not ok:
                failures += 1
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"[ERR] {path} -> {exc}")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test for FastAPI endpoints.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL, e.g. https://your-domain.duckdns.org")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    args = parser.parse_args()

    failures = run_smoke(args.base_url, args.timeout)
    print(f"RESULT: {'PASS' if failures == 0 else 'FAIL'} (failures={failures})")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
