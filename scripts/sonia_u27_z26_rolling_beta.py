#!/usr/bin/env python3
"""Rolling beta diagnostics for receive SONIA U27 / pay SONIA Z26.

Outputs a daily CSV, summary JSON and figure.  Rates are in percent in the
source panel; changes and spreads are reported in basis points.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "cache" / "stir_curves" / "panel.csv"
OUT_DIR = ROOT / "data" / "cache" / "stir_curves"
FIG_DIR = ROOT / "research" / "notes" / "figures"
CSV_OUT = OUT_DIR / "sonia_u27_on_z26_rolling30_beta.csv"
JSON_OUT = OUT_DIR / "sonia_u27_z26_rolling_beta_summary.json"
FIG_OUT = FIG_DIR / "sonia_u27_z26_rolling_beta_level.png"


def beta(y: pd.Series, x: pd.Series) -> float:
    a = pd.concat([y, x], axis=1).dropna()
    return float(a.iloc[:, 0].cov(a.iloc[:, 1]) / a.iloc[:, 1].var())


def main() -> None:
    panel = pd.read_csv(PANEL, parse_dates=["date"])
    rates = (
        panel[
            (panel.curve == "SONIA")
            & panel.contract.isin(["Z26", "U27"])
        ]
        .pivot(index="date", columns="contract", values="rate")
        .sort_index()
        .dropna()
    )
    changes = rates.diff() * 100
    spread = (rates.U27 - rates.Z26) * 100
    beta30 = changes.U27.rolling(30).cov(changes.Z26) / changes.Z26.rolling(30).var()
    corr30 = changes.U27.rolling(30).corr(changes.Z26)
    vol_z30 = changes.Z26.rolling(30).std()
    vol_u30 = changes.U27.rolling(30).std()

    daily = pd.DataFrame(
        {
            "date": rates.index,
            "Z26_rate": rates.Z26,
            "U27_rate": rates.U27,
            "spread_U27_minus_Z26_bp": spread,
            "beta30_U27_on_Z26": beta30,
            "corr30": corr30,
            "vol30_Z26_bp": vol_z30,
            "vol30_U27_bp": vol_u30,
        }
    ).reset_index(drop=True)
    daily.to_csv(CSV_OUT, index=False)

    march = daily[daily.date >= "2026-03-01"].dropna(
        subset=["beta30_U27_on_Z26"]
    )
    level_beta_corr = float(
        march.spread_U27_minus_Z26_bp.corr(march.beta30_U27_on_Z26)
    )
    slope = float(
        march.spread_U27_minus_Z26_bp.cov(march.beta30_U27_on_Z26)
        / march.spread_U27_minus_Z26_bp.var()
    )

    # Non-overlapping blocks guard against mistaking overlapping rolling
    # windows for independent evidence.
    post_march = rates.loc["2026-03-02":].diff().dropna() * 100
    blocks = []
    for i in range(0, len(post_march), 30):
        block = post_march.iloc[i : i + 30]
        if len(block) < 10:
            continue
        start_level_index = rates.index.get_loc(block.index[0]) - 1
        start_level_date = rates.index[start_level_index]
        start_spread = float(spread.loc[start_level_date])
        end_spread = float(spread.loc[block.index[-1]])
        blocks.append(
            {
                "start": str(block.index[0].date()),
                "end": str(block.index[-1].date()),
                "n": len(block),
                "beta_U27_on_Z26": beta(block.U27, block.Z26),
                "spread_start_bp": start_spread,
                "spread_end_bp": end_spread,
                "spread_change_bp": end_spread - start_spread,
            }
        )

    bins = pd.cut(
        march.spread_U27_minus_Z26_bp,
        [-np.inf, 0, 20, 40, np.inf],
        right=False,
    )
    beta_bins = []
    for interval, group in march.groupby(bins, observed=True):
        beta_bins.append(
            {
                "spread_bin": str(interval),
                "n": len(group),
                "mean_beta": float(group.beta30_U27_on_Z26.mean()),
                "median_beta": float(group.beta30_U27_on_Z26.median()),
                "min_beta": float(group.beta30_U27_on_Z26.min()),
                "max_beta": float(group.beta30_U27_on_Z26.max()),
            }
        )

    last30 = changes.dropna().tail(30)
    hedge = []
    for ratio in [1.0, 1.5, 2.0, float(beta30.dropna().iloc[-1])]:
        pnl = -last30.U27 + ratio * last30.Z26
        hedge.append(
            {
                "pay_Z26_per_receive_U27": ratio,
                "daily_pnl_vol_bp": float(pnl.std()),
                "mean_daily_pnl_bp": float(pnl.mean()),
                "worst_daily_pnl_bp": float(pnl.min()),
                "pnl_corr_with_Z26_change": float(pnl.corr(last30.Z26)),
            }
        )

    key_dates = {}
    indexed = daily.set_index("date")
    for date in [
        "2026-03-02",
        "2026-03-20",
        "2026-04-30",
        "2026-05-12",
        "2026-06-01",
        "2026-06-30",
        "2026-07-23",
        "2026-08-19",
        "2026-09-02",
        "2026-09-10",
        "2026-09-14",
        "2026-09-18",
    ]:
        row = indexed.loc[:date].iloc[-1]
        key_dates[date] = {
            "observation_date": str(indexed.loc[:date].index[-1].date()),
            "spread_bp": float(row.spread_U27_minus_Z26_bp),
            "beta30": float(row.beta30_U27_on_Z26),
            "corr30": float(row.corr30),
            "vol30_Z26_bp": float(row.vol30_Z26_bp),
            "vol30_U27_bp": float(row.vol30_U27_bp),
        }

    summary = {
        "asof": str(rates.index[-1].date()),
        "definition": "beta30 = cov(dU27,dZ26)/var(dZ26), 30 sessions",
        "spread_definition": "100*(U27 rate - Z26 rate)",
        "march_level_beta_correlation": level_beta_corr,
        "descriptive_beta_change_per_10bp_higher_spread": slope * 10,
        "march_beta_first": float(march.beta30_U27_on_Z26.iloc[0]),
        "march_beta_last": float(march.beta30_U27_on_Z26.iloc[-1]),
        "march_beta_min": float(march.beta30_U27_on_Z26.min()),
        "march_beta_min_date": str(
            march.loc[march.beta30_U27_on_Z26.idxmin(), "date"].date()
        ),
        "march_beta_max": float(march.beta30_U27_on_Z26.max()),
        "march_beta_max_date": str(
            march.loc[march.beta30_U27_on_Z26.idxmax(), "date"].date()
        ),
        "key_dates": key_dates,
        "spread_bins": beta_bins,
        "non_overlapping_blocks": blocks,
        "last30_hedge_ratios": hedge,
    }
    JSON_OUT.write_text(json.dumps(summary, indent=2))

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    axes[0].plot(march.date, march.spread_U27_minus_Z26_bp, color="#14213d", lw=2)
    axes[0].axhline(0, color="grey", lw=0.8)
    axes[0].set_ylabel("U27 − Z26 (bp)")
    axes[0].set_title("SONIA peak gap steepened as β rose")

    axes[1].plot(march.date, march.beta30_U27_on_Z26, color="#d95f02", lw=2)
    axes[1].axhline(1, color="grey", lw=0.8, ls="--", label="β = 1")
    axes[1].set_ylabel("30-session β(U27 | Z26)")
    axes[1].set_xlabel("Date")
    axes[1].legend(frameon=False)
    fig.savefig(FIG_OUT, dpi=170)
    plt.close(fig)

    print(f"wrote {CSV_OUT}")
    print(f"wrote {JSON_OUT}")
    print(f"wrote {FIG_OUT}")


if __name__ == "__main__":
    main()
