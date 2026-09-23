#!/usr/bin/env python3
"""Plot the SONIA Sep-27 minus Dec-26 buildup over the last 20 sessions."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "cache" / "stir_curves" / "panel.csv"
OUT_DIR = ROOT / "research" / "notes" / "figures"
DATA_DIR = ROOT / "data" / "cache" / "stir_curves"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-date", default=None)
    parser.add_argument("--z26-price", type=float, default=None)
    parser.add_argument("--u27-price", type=float, default=None)
    parser.add_argument("--sessions", type=int, default=20)
    args = parser.parse_args()

    panel = pd.read_csv(PANEL, parse_dates=["date"])
    rates = (
        panel[
            (panel.curve == "SONIA")
            & panel.contract.isin(["Z26", "U27"])
        ]
        .pivot(index="date", columns="contract", values="rate")
        .dropna()
        .sort_index()
    )
    spread = ((rates.U27 - rates.Z26) * 100).rename("spread_bp")
    settled = pd.DataFrame(
        {
            "date": spread.index,
            "spread_bp": spread.values,
            "observation": "settlement",
        }
    )

    live = None
    if args.live_date and args.z26_price is not None and args.u27_price is not None:
        live = pd.DataFrame(
            {
                "date": [pd.Timestamp(args.live_date)],
                "spread_bp": [
                    ((100 - args.u27_price) - (100 - args.z26_price)) * 100
                ],
                "observation": "intraday screenshot",
            }
        )

    keep_settled = args.sessions - (1 if live is not None else 0)
    plot_data = settled.tail(keep_settled)
    if live is not None:
        plot_data = pd.concat([plot_data, live], ignore_index=True)

    asof = plot_data.date.iloc[-1].date()
    csv_path = DATA_DIR / f"sonia_u27_z26_last20_{asof}.csv"
    png_path = OUT_DIR / f"sonia_u27_z26_last20_{asof}.png"
    plot_data.to_csv(csv_path, index=False, date_format="%Y-%m-%d")

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    settled_plot = plot_data[plot_data.observation == "settlement"]
    ax.plot(
        settled_plot.date,
        settled_plot.spread_bp,
        color="#14213d",
        linewidth=2.3,
        marker="o",
        markersize=4.5,
        label="Settlement",
    )
    if live is not None:
        live_row = plot_data.iloc[-1]
        previous = settled_plot.iloc[-1]
        ax.plot(
            [previous.date, live_row.date],
            [previous.spread_bp, live_row.spread_bp],
            color="#d95f02",
            linewidth=2,
            linestyle="--",
        )
        ax.scatter(
            [live_row.date],
            [live_row.spread_bp],
            color="#d95f02",
            s=70,
            zorder=4,
            label="23-Sep midday",
        )
        ax.annotate(
            f"{live_row.spread_bp:.1f} bp\n(price spread −{live_row.spread_bp/100:.3f})",
            (live_row.date, live_row.spread_bp),
            xytext=(-92, -3),
            textcoords="offset points",
            color="#d95f02",
            fontweight="bold",
            arrowprops={"arrowstyle": "->", "color": "#d95f02"},
        )

    high = float(plot_data.spread_bp.max())
    high_row = plot_data.loc[plot_data.spread_bp.idxmax()]
    ax.annotate(
        f"20-session high {high:.1f}",
        (high_row.date, high),
        xytext=(-30, 12),
        textcoords="offset points",
        ha="center",
        color="#14213d",
    )
    ax.axhline(60, color="#7a8797", linewidth=1, linestyle=":", label="60 bp entry zone")
    fig.suptitle("SONIA buildup: Sep’27 rate − Dec’26 rate", y=0.98, fontsize=15)
    ax.text(
        0,
        1.015,
        "Last 20 trading observations · positive = more tightening priced into the peak",
        transform=ax.transAxes,
        color="#5d6775",
        fontsize=10,
    )
    ax.set_ylim(float(plot_data.spread_bp.min()) - 2, high + 5)
    ax.set_ylabel("Basis points")
    ax.set_xlabel("")
    ax.grid(axis="y", color="#d9dee7", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.tick_params(axis="x", rotation=35)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {csv_path}")
    print(f"wrote {png_path}")


if __name__ == "__main__":
    main()
