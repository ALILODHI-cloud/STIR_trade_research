#!/usr/bin/env python3
"""Write every live STIR contract's one-session rate and price move."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "cache" / "stir_curves" / "panel.csv"
OUT_DIR = ROOT / "data" / "cache" / "stir_curves"

MONTH_ORDER = {
    "F": 1,
    "G": 2,
    "H": 3,
    "J": 4,
    "K": 5,
    "M": 6,
    "N": 7,
    "Q": 8,
    "U": 9,
    "V": 10,
    "X": 11,
    "Z": 12,
}
CURVE_ORDER = {"SOFR": 0, "EURIBOR": 1, "SONIA": 2}


def contract_key(contract: str) -> tuple[int, int]:
    return 2000 + int(contract[1:]), MONTH_ORDER[contract[0]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asof", help="Session date YYYY-MM-DD; defaults to panel max")
    args = parser.parse_args()

    panel = pd.read_csv(PANEL, parse_dates=["date"])
    asof = pd.Timestamp(args.asof) if args.asof else panel.date.max()
    prior_dates = sorted(d for d in panel.date.unique() if d < asof)
    if not prior_dates:
        raise RuntimeError(f"no prior session before {asof.date()}")
    previous = pd.Timestamp(prior_dates[-1])

    two = panel[panel.date.isin([previous, asof])].copy()
    rates = two.pivot_table(
        index=["curve", "symbol", "contract"], columns="date", values=["price", "rate"]
    )
    needed = [
        ("price", previous),
        ("price", asof),
        ("rate", previous),
        ("rate", asof),
    ]
    rates = rates.dropna(subset=needed)
    identifiers = rates.index.to_frame(index=False)
    out = pd.DataFrame(
        {
            "curve": identifiers.curve,
            "symbol": identifiers.symbol,
            "contract": identifiers.contract,
            "previous_date": str(previous.date()),
            "asof_date": str(asof.date()),
            "previous_price": rates[("price", previous)].to_numpy(),
            "current_price": rates[("price", asof)].to_numpy(),
            "price_move": (
                rates[("price", asof)] - rates[("price", previous)]
            ).to_numpy(),
            "previous_rate": rates[("rate", previous)].to_numpy(),
            "current_rate": rates[("rate", asof)].to_numpy(),
            "rate_move_bp": (
                rates[("rate", asof)] - rates[("rate", previous)]
            )
            .to_numpy()
            * 100,
        }
    )
    out["_curve_order"] = out.curve.map(CURVE_ORDER)
    out["_contract_order"] = out.contract.map(contract_key)
    out = out.sort_values(["_curve_order", "_contract_order"]).drop(
        columns=["_curve_order", "_contract_order"]
    )
    path = OUT_DIR / f"stir_daily_moves_{asof.date()}.csv"
    out.to_csv(path, index=False)
    print(f"wrote {path} ({len(out)} contracts)")


if __name__ == "__main__":
    main()
