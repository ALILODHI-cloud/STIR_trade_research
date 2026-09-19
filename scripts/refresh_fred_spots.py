#!/usr/bin/env python3
"""Refresh FRED policy spots into data/cache/stir_curves/ for dashboard rebuilds.

Safe for CI — no browser. Futures panel is left as-is (updated separately via
Barchart scrape when available).
"""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd
from curl_cffi import requests as creq

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache" / "stir_curves"

SERIES = {
    "SOFR": "SOFR",
    "SONIA": "IUDSOIA",
    "ECB_DFR": "ECBDFR",
    "EFFR": "EFFR",
}


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    s = creq.Session(impersonate="chrome")
    for name, sid in SERIES.items():
        r = s.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", timeout=60)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
        df.columns = ["date", "value"]
        df = df[df["value"].astype(str) != "."].copy()
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()
        out = CACHE / f"spot_{name}.csv"
        df.to_csv(out, index=False)
        print(f"{name}: {len(df)} rows last={df.iloc[-1].to_dict()}")


if __name__ == "__main__":
    main()
