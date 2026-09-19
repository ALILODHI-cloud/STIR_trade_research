"""Build compact JSON for the STIR strip dashboard.

Reads data/cache/stir_curves/panel.csv + spot_*.csv and writes
research/dashboard/data/curves.json (and a light meta file).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache" / "stir_curves"
OUT = ROOT / "research" / "dashboard" / "data"

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

# Policy spot series keyed to each curve tab
SPOT_MAP = {
    "SOFR": ("SOFR", "SOFR overnight"),
    "EURIBOR": ("ECB_DFR", "ECB deposit facility"),
    "SONIA": ("SONIA", "SONIA overnight"),
}

ROOT_SYM = {"SOFR": "SQ", "EURIBOR": "IM", "SONIA": "J8"}


def contract_key(c: str) -> tuple[int, int]:
    return 2000 + int(c[1:]), MONTH_ORDER[c[0]]


def load_spot(name: str) -> pd.Series:
    s = pd.read_csv(CACHE / f"spot_{name}.csv", parse_dates=["date"])
    return s.set_index("date")["value"].sort_index().astype(float)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(CACHE / "panel.csv", parse_dates=["date"])
    panel = panel[panel.date >= "2025-01-01"].copy()  # keep file lean but > YTD

    spots = {k: load_spot(v[0]) for k, v in SPOT_MAP.items()}

    payload: dict = {
        "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "asof": str(panel.date.max().date()),
        "curves": {},
    }

    for curve in ("SOFR", "EURIBOR", "SONIA"):
        sub = panel[panel.curve == curve].copy()
        # Prefer quarterlies + near SOFR serials still live on latest day
        latest = sub.date.max()
        latest_contracts = sorted(
            sub.loc[sub.date == latest, "contract"].unique(), key=contract_key
        )
        # Keep a stable display set: from first live-ish 26 contract through Z28
        display = [
            c
            for c in latest_contracts
            if contract_key(c) <= contract_key("Z28")
            and contract_key(c) >= contract_key("U26")
        ]
        if curve == "SOFR":
            # include V26 X26 if present
            for extra in ("V26", "X26"):
                if extra in latest_contracts and extra not in display:
                    display.append(extra)
            display = sorted(display, key=contract_key)

        # sessions from 2026-01-02 (or first available)
        sessions = sorted(d for d in sub.date.unique() if d >= pd.Timestamp("2026-01-02"))
        if not sessions:
            sessions = sorted(sub.date.unique())[-180:]

        spot_s = spots[curve]
        # Align spot to each session (last available on/before)
        spot_by_date = {}
        for d in sessions:
            hist = spot_s.loc[:d]
            if len(hist):
                val = float(hist.iloc[-1])
                spot_by_date[str(pd.Timestamp(d).date())] = None if pd.isna(val) else val
            else:
                spot_by_date[str(pd.Timestamp(d).date())] = None

        # rates[date][contract] = rate
        rates: dict[str, dict[str, float]] = {}
        prices: dict[str, dict[str, float]] = {}
        for d, g in sub[sub.contract.isin(display)].groupby("date"):
            if d not in sessions and d != latest:
                continue
            key = str(pd.Timestamp(d).date())
            rates[key] = {
                r.contract: round(float(r.rate), 4)
                for _, r in g.iterrows()
                if pd.notna(r.rate)
            }
            prices[key] = {
                r.contract: round(float(r.price), 4)
                for _, r in g.iterrows()
                if pd.notna(r.price)
            }

        # Ensure latest in rates
        asof_key = str(pd.Timestamp(latest).date())
        if asof_key not in rates:
            g = sub[(sub.date == latest) & (sub.contract.isin(display))]
            rates[asof_key] = {r.contract: round(float(r.rate), 4) for _, r in g.iterrows()}
            prices[asof_key] = {r.contract: round(float(r.price), 4) for _, r in g.iterrows()}

        session_keys = [str(pd.Timestamp(d).date()) for d in sessions if str(pd.Timestamp(d).date()) in rates]
        if asof_key not in session_keys:
            session_keys.append(asof_key)

        payload["curves"][curve] = {
            "root": ROOT_SYM[curve],
            "label": curve.title() if curve != "SOFR" else "SOFR",
            "policy_name": SPOT_MAP[curve][1],
            "policy_id": SPOT_MAP[curve][0],
            "contracts": display,
            "symbols": {c: f"{ROOT_SYM[curve]}{c}" for c in display},
            "sessions": session_keys,
            "asof": asof_key,
            "spot": spot_by_date,
            "rates": {k: rates[k] for k in session_keys},
            "prices": {k: prices[k] for k in session_keys},
            "latest_rates": rates[asof_key],
            "latest_prices": prices[asof_key],
            "latest_spot": spot_by_date.get(asof_key),
        }

    out_path = OUT / "curves.json"
    # allow_nan=False so we never emit invalid JSON NaN tokens
    out_path.write_text(json.dumps(payload, separators=(",", ":"), allow_nan=False))
    meta = {
        "generated_at": payload["generated_at"],
        "asof": payload["asof"],
        "bytes": out_path.stat().st_size,
        "curves": {
            k: {"n_sessions": len(v["sessions"]), "n_contracts": len(v["contracts"])}
            for k, v in payload["curves"].items()
        },
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
