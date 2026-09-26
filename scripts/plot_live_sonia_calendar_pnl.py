#!/usr/bin/env python3
"""Plot the live SONIA Sep-27/Dec-26 calendar and leg P&L decomposition."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "cache" / "stir_curves" / "panel.csv"
FIG_DIR = ROOT / "research" / "notes" / "figures"
DATA_DIR = ROOT / "data" / "cache" / "stir_curves"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entry-date", required=True)
    parser.add_argument("--entry-z-price", type=float, required=True)
    parser.add_argument("--entry-u-price", type=float, required=True)
    parser.add_argument("--combo-fill", type=float, required=True)
    parser.add_argument("--current-date", required=True)
    parser.add_argument("--current-z-price", type=float, required=True)
    parser.add_argument("--current-u-price", type=float, required=True)
    parser.add_argument("--stop", type=float, default=None)
    args = parser.parse_args()

    panel = pd.read_csv(PANEL, parse_dates=["date"])
    prices = (
        panel[
            (panel.curve == "SONIA")
            & panel.contract.isin(["Z26", "U27"])
        ]
        .pivot(index="date", columns="contract", values="price")
        .dropna()
        .sort_index()
    )
    start = pd.Timestamp(args.entry_date) - pd.Timedelta(days=5)
    history = prices.loc[start : pd.Timestamp(args.current_date) - pd.Timedelta(days=1)]
    path = pd.DataFrame(
        {
            "date": history.index,
            "z26_price": history.Z26,
            "u27_price": history.U27,
            "source": "Barchart settlement",
        }
    )
    current = pd.DataFrame(
        {
            "date": [pd.Timestamp(args.current_date)],
            "z26_price": [args.current_z_price],
            "u27_price": [args.current_u_price],
            "source": ["IBKR displayed mark"],
        }
    )
    path = pd.concat([path, current], ignore_index=True)
    path["price_spread"] = path.u27_price - path.z26_price
    path["rate_slope_bp"] = -path.price_spread * 100

    entry_z_rate = 100 - args.entry_z_price
    entry_u_rate = 100 - args.entry_u_price
    entry_slope_legs = (entry_u_rate - entry_z_rate) * 100
    entry_slope_combo = -args.combo_fill * 100

    current_z_rate = 100 - args.current_z_price
    current_u_rate = 100 - args.current_u_price
    current_slope = (current_u_rate - current_z_rate) * 100

    u_pnl_bp = (args.current_u_price - args.entry_u_price) * 100
    z_pnl_bp = (args.entry_z_price - args.current_z_price) * 100
    net_pnl_bp = u_pnl_bp + z_pnl_bp

    csv = path.copy()
    csv["entry_combo_slope_bp"] = entry_slope_combo
    csv["entry_leg_average_slope_bp"] = entry_slope_legs
    csv.to_csv(
        DATA_DIR / f"sonia_live_calendar_path_{args.current_date}.csv",
        index=False,
        date_format="%Y-%m-%d",
    )

    fig, (ax, bars) = plt.subplots(
        1, 2, figsize=(13, 5.8), gridspec_kw={"width_ratios": [2.1, 1]}
    )
    settled = path[path.source == "Barchart settlement"]
    ax.plot(
        settled.date,
        settled.rate_slope_bp,
        color="#14213d",
        marker="o",
        linewidth=2.3,
        label="Settlement slope",
    )
    last_settle = settled.iloc[-1]
    current_row = path.iloc[-1]
    ax.plot(
        [last_settle.date, current_row.date],
        [last_settle.rate_slope_bp, current_row.rate_slope_bp],
        color="#d95f02",
        linestyle="--",
        linewidth=2,
    )
    ax.scatter(
        [current_row.date],
        [current_row.rate_slope_bp],
        color="#d95f02",
        s=75,
        zorder=4,
        label="IBKR displayed mark",
    )
    entry_date = pd.Timestamp(args.entry_date)
    ax.scatter(
        [entry_date],
        [entry_slope_combo],
        marker="D",
        color="#2a9d8f",
        s=70,
        zorder=5,
        label=f"Entry {entry_slope_combo:.1f} bp",
    )
    ax.axhline(
        entry_slope_combo, color="#2a9d8f", linestyle=":", linewidth=1
    )
    if args.stop is not None:
        stop_slope = -args.stop * 100
        ax.axhline(
            stop_slope,
            color="#b23a48",
            linestyle="--",
            linewidth=1,
            label=f"Stop {stop_slope:.1f} bp",
        )
    ax.annotate(
        f"Current {current_slope:.1f} bp",
        (current_row.date, current_row.rate_slope_bp),
        xytext=(-78, 15),
        textcoords="offset points",
        color="#d95f02",
        fontweight="bold",
        arrowprops={"arrowstyle": "->", "color": "#d95f02"},
    )
    ax.set_title("SONIA buildup: September 2027 rate − December 2026 rate")
    ax.set_ylabel("Basis points")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.tick_params(axis="x", rotation=35)
    ax.grid(axis="y", color="#d9dee7")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left")

    labels = ["Long Sep’27", "Short Dec’26", "Net"]
    values = [u_pnl_bp, z_pnl_bp, net_pnl_bp]
    colors = ["#2a9d8f" if x >= 0 else "#b23a48" for x in values]
    bars.bar(labels, values, color=colors)
    bars.axhline(0, color="#7a8797", linewidth=0.8)
    for i, value in enumerate(values):
        bars.text(
            i,
            value + (0.25 if value >= 0 else -0.4),
            f"{value:+.1f} bp\n£{value * 25:+.0f}",
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontweight="bold",
        )
    bars.set_title("P&L since entry by leg")
    bars.set_ylabel("Price basis points")
    bars.set_ylim(-6, 9)
    bars.spines[["top", "right"]].set_visible(False)
    bars.grid(axis="y", color="#e4e8ef", linewidth=0.8)

    fig.suptitle(
        "Live SONIA Sep’27/Dec’26 calendar",
        fontsize=16,
        y=0.99,
    )
    fig.text(
        0.5,
        0.01,
        (
            f"Official combo fill {args.combo_fill:.3f} = {entry_slope_combo:.1f} bp; "
            f"leg averages imply {entry_slope_legs:.1f} bp. "
            "Final point uses the supplied IBKR marks."
        ),
        ha="center",
        color="#5d6775",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path_out = FIG_DIR / f"sonia_live_calendar_path_{args.current_date}.png"
    fig.savefig(path_out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path_out}")
    print(
        f"entry slope combo={entry_slope_combo:.1f} bp; "
        f"leg averages={entry_slope_legs:.1f} bp; current={current_slope:.1f} bp; "
        f"net={net_pnl_bp:+.1f} bp"
    )


if __name__ == "__main__":
    main()
