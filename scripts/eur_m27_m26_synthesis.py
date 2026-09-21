"""Evaluate the expired Euribor Jun'27 minus Jun'26 one-year calendar.

Desk convention: spread = back minus front, in basis points.  The analysis
stops at IMM26's last observation and reports pre-expiry results separately
because the final settlement print is not an ordinary tradable daily move.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from lib.stir.rv import hedge_ratio, percentile_rank

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "cache" / "stir_curves" / "panel.csv"
OUT = ROOT / "data" / "cache" / "stir_curves" / "eur_m27_m26_synthesis.json"


def beta(y: pd.Series, x: pd.Series) -> float:
    a = pd.concat([y, x], axis=1).dropna()
    return float(hedge_ratio(a.iloc[:, 0], a.iloc[:, 1]))


def sample(df: pd.DataFrame) -> dict:
    d = df.diff().dropna()
    sells = d[d.front > 0]
    rallies = d[d.front < 0]
    corr = float(d.back.corr(d.front))

    def condition(x: pd.DataFrame) -> dict:
        return {
            "n": len(x),
            "mean_front_bp": float(x.front.mean()),
            "mean_back_bp": float(x.back.mean()),
            "mean_spread_bp": float(x.spread.mean()),
            "median_spread_bp": float(x.spread.median()),
            "flatten_pct": float((x.spread < 0).mean() * 100),
            "steepen_pct": float((x.spread > 0).mean() * 100),
        }

    return {
        "start": str(df.index.min().date()),
        "end": str(df.index.max().date()),
        "n_changes": len(d),
        "beta_back_on_front": beta(d.back, d.front),
        "beta_spread_on_front": beta(d.spread, d.front),
        "corr_back_front": corr,
        "r_squared": corr**2,
        "front_daily_vol_bp": float(d.front.std(ddof=1)),
        "back_daily_vol_bp": float(d.back.std(ddof=1)),
        "near_selloffs": condition(sells),
        "near_rallies": condition(rallies),
    }


def main() -> None:
    p = pd.read_csv(PANEL, parse_dates=["date"])
    eur = (
        p[
            (p.curve == "EURIBOR")
            & p.contract.isin(["M26", "M27", "U26", "U27", "Z26", "Z27"])
        ]
        .pivot(index="date", columns="contract", values="rate")
        .sort_index()
    )
    pair = eur[["M26", "M27"]].dropna().rename(columns={"M26": "front", "M27": "back"})
    pair = pair * 100
    pair["spread"] = pair.back - pair.front
    last = pair.index.max()
    pre_expiry = pair.iloc[:-1]

    rolling = hedge_ratio(pair.back.diff(), pair.front.diff(), window=30)
    spread_rolling = hedge_ratio(pair.spread.diff(), pair.front.diff(), window=30)
    snapshots = {}
    for date in ["2026-01-02", "2026-02-02", "2026-03-02", "2026-04-01",
                 "2026-05-01", "2026-05-15", "2026-06-01", "2026-06-12",
                 "2026-06-15"]:
        r = rolling.loc[:date].dropna()
        sr = spread_rolling.loc[:date].dropna()
        level = pair.loc[:date].iloc[-1]
        snapshots[date] = {
            "observation_date": str(pair.loc[:date].index[-1].date()),
            "front_rate": float(level.front / 100),
            "back_rate": float(level.back / 100),
            "spread_bp": float(level.spread),
            "beta30_back_on_front": float(r.iloc[-1]) if len(r) else None,
            "beta30_spread_on_front": float(sr.iloc[-1]) if len(sr) else None,
        }

    # One-year calendar successors as each near leg approaches expiry.
    successors = {}
    for front, back, key in [
        ("M26", "M27", "M27_minus_M26"),
        ("U26", "U27", "U27_minus_U26"),
        ("Z26", "Z27", "Z27_minus_Z26"),
    ]:
        x = eur[[front, back]].dropna()
        s = (x[back] - x[front]) * 100
        successors[key] = {
            "last_date": str(s.index[-1].date()),
            "last_spread_bp": float(s.iloc[-1]),
            "front_rate": float(x[front].iloc[-1]),
            "back_rate": float(x[back].iloc[-1]),
        }
        pair_x = (x * 100).rename(columns={front: "front", back: "back"})
        pair_x["spread"] = pair_x.back - pair_x.front
        if key == "U27_minus_U26":
            # Exclude the final settlement observation, as for M26.
            successors[key]["last30_pre_settlement"] = sample(pair_x.iloc[:-1].tail(30))
            successors[key]["august_pre_settlement"] = sample(
                pair_x.loc["2026-08-01":].iloc[:-1]
            )
        elif key == "Z27_minus_Z26":
            successors[key]["last30"] = sample(pair_x.tail(30))
            successors[key]["august_on"] = sample(pair_x.loc["2026-08-01":])

    ytd = pair.loc["2026-01-01":]
    pre_ytd = ytd.iloc[:-1]
    final_move = pair.diff().iloc[-1]
    out = {
        "definition": "100 * (IMM27 rate - IMM26 rate); desk back minus front",
        "last_valid_observation": str(last.date()),
        "warning": "IMM26 expired; the final settlement move is separated from ordinary pre-expiry changes.",
        "last": {
            "front_rate": float(pair.front.iloc[-1] / 100),
            "back_rate": float(pair.back.iloc[-1] / 100),
            "spread_bp": float(pair.spread.iloc[-1]),
            "final_daily_move_bp": {
                "front": float(final_move.front),
                "back": float(final_move.back),
                "spread": float(final_move.spread),
            },
        },
        "pre_expiry_last_2026_06_12": {
            "front_rate": float(pre_expiry.front.iloc[-1] / 100),
            "back_rate": float(pre_expiry.back.iloc[-1] / 100),
            "spread_bp": float(pre_expiry.spread.iloc[-1]),
        },
        "ytd_through_expiry": {
            "start_spread_bp": float(ytd.spread.iloc[0]),
            "last_spread_bp": float(ytd.spread.iloc[-1]),
            "min_spread_bp": float(ytd.spread.min()),
            "min_date": str(ytd.spread.idxmin().date()),
            "max_spread_bp": float(ytd.spread.max()),
            "max_date": str(ytd.spread.idxmax().date()),
            "last_percentile": float(percentile_rank(ytd.spread).iloc[-1]),
        },
        "pre_expiry_ytd_through_2026_06_12": {
            "start_spread_bp": float(pre_ytd.spread.iloc[0]),
            "last_spread_bp": float(pre_ytd.spread.iloc[-1]),
            "min_spread_bp": float(pre_ytd.spread.min()),
            "max_spread_bp": float(pre_ytd.spread.max()),
            "last_percentile": float(percentile_rank(pre_ytd.spread).iloc[-1]),
        },
        "samples_excluding_final_settlement": {
            "ytd": sample(pre_expiry.loc["2026-01-01":]),
            "march_on": sample(pre_expiry.loc["2026-03-01":]),
            "april_on": sample(pre_expiry.loc["2026-04-01":]),
            "may_on": sample(pre_expiry.loc["2026-05-01":]),
            "last30_sessions": sample(pre_expiry.tail(30)),
        },
        "sample_including_final_settlement": sample(ytd),
        "rolling30_snapshots": snapshots,
        "successors": successors,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
