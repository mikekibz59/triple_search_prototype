from __future__ import annotations
"""Convenience exports & a tiny helper to ingest the bundled sample data."""

import json
from pathlib import Path
from typing import List

from .models import Company, CompanyDetail
from .ingest import add_all
from .api import app, run  # expose FastAPI & runner
from . import settings

__all__ = [
    "Company",
    "add_all",
    "app",
    "run",
    "load_sample_data",
]

_SAMPLE_JSON = Path(__file__).resolve().parent / "sample_companies.json"


def load_sample_data() -> int:
    """Load bundled `sample_data/companies.json` into SQLite & FAISS index."""
    if not _SAMPLE_JSON.exists():
        raise FileNotFoundError(_SAMPLE_JSON)

    with _SAMPLE_JSON.open() as f:
        raw: List[dict] = json.load(f)
    companies = [CompanyDetail(**item).to_company() for item in raw]
    return add_all(companies)

# Usage CLI helper -----------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load sample data or run API")
    parser.add_argument("cmd", choices=["load", "serve"], help="action")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.cmd == "load":
        n = load_sample_data()
        print(f"Ingested {n} sample companies → {settings.DB_PATH}")
    else:
        run(host=args.host, port=args.port)
