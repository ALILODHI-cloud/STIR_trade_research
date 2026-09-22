#!/usr/bin/env python3
"""Merge Barchart fixed-contract history into the canonical STIR panel."""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "stir_futures"
JSON_PATH = RAW_DIR / "histories_raw.json"
GZIP_PATH = RAW_DIR / "histories_raw.json.gz"
PANEL_PATH = ROOT / "data" / "cache" / "stir_curves" / "panel.csv"

ROOTS = {
    "SQ": "SOFR",
    "IM": "EURIBOR",
    "J8": "SONIA",
}


def number(value, *, integer: bool = False):
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text or text.lower() in {"unch", "nan", "none", "n/a"}:
        return 0 if text.lower() == "unch" else None
    # Barchart appends "s" to final settlement prices.
    text = text.rstrip("s")
    try:
        return int(float(text)) if integer else float(text)
    except ValueError:
        return None


def load_raw() -> dict:
    if JSON_PATH.exists():
        return json.loads(JSON_PATH.read_text())
    with gzip.open(GZIP_PATH, "rt") as f:
        return json.load(f)


def parse(raw: dict) -> pd.DataFrame:
    rows = []
    for symbol, history in raw.items():
        root = symbol[:2]
        if root not in ROOTS:
            continue
        contract = symbol[2:]
        for item in history:
            price = number(item.get("lastPrice"))
            date = pd.to_datetime(item.get("tradeTime"), errors="coerce")
            if price is None or pd.isna(date):
                continue
            rows.append(
                {
                    "date": date,
                    "price": price,
                    "rate": 100.0 - price,
                    "volume": number(item.get("volume"), integer=True),
                    "priceChange": number(item.get("priceChange")),
                    "symbol": symbol,
                    "curve": ROOTS[root],
                    "contract": contract,
                }
            )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("Barchart history produced no usable rows")
    return frame.sort_values(["curve", "contract", "date"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--asof",
        help="Keep observations on or before YYYY-MM-DD (use to exclude an incomplete live session)",
    )
    args = parser.parse_args()

    fresh = parse(load_raw())
    if args.asof:
        asof = pd.Timestamp(args.asof)
        fresh = fresh[fresh.date <= asof]
    if PANEL_PATH.exists():
        existing = pd.read_csv(PANEL_PATH, parse_dates=["date"])
        has_future_rows = bool(args.asof and (existing.date > asof).any())
        if has_future_rows:
            existing = existing[existing.date <= asof]
        existing_keys = pd.MultiIndex.from_frame(existing[["symbol", "date"]])
        fresh_keys = pd.MultiIndex.from_frame(fresh[["symbol", "date"]])
        additions = fresh[~fresh_keys.isin(existing_keys)].sort_values(
            ["date", "symbol"]
        )
        combined = pd.concat([existing, additions], ignore_index=True)
        if has_future_rows:
            combined.to_csv(PANEL_PATH, index=False, date_format="%Y-%m-%d")
        elif not additions.empty:
            additions.to_csv(
                PANEL_PATH,
                mode="a",
                header=False,
                index=False,
                date_format="%Y-%m-%d",
            )
    else:
        combined = fresh
        PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        combined.to_csv(PANEL_PATH, index=False, date_format="%Y-%m-%d")

    # Preserve the auditable raw response compactly.
    if JSON_PATH.exists():
        with gzip.open(GZIP_PATH, "wt") as f:
            json.dump(load_raw(), f)
        JSON_PATH.unlink()

    latest = combined.groupby("curve").date.max()
    print(f"wrote {PANEL_PATH} ({len(combined):,} rows)")
    for curve, date in latest.items():
        print(curve, date.date())


if __name__ == "__main__":
    main()
