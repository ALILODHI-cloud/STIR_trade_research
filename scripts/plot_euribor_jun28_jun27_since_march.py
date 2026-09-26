#!/usr/bin/env python3
"""Plot Euribor June-28 minus June-27 since March 2026."""
from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "cache" / "stir_curves" / "panel.csv"
FIG_DIR = ROOT / "research" / "notes" / "figures"
DATA_DIR = ROOT / "data" / "cache" / "stir_curves"


def main() -> None:
    panel = pd.read_csv(PANEL, parse_dates=["date"])
    prices = (
        panel[
            (panel.curve == "EURIBOR")
            & panel.contract.isin(["M27", "M28"])
        ]
        .pivot(index="date", columns="contract", values="price")
        .dropna()
        .sort_index()
        .loc["2026-03-01":]
    )
    data = pd.DataFrame(
        {
            "date": prices.index,
            "jun27_price": prices.M27,
            "jun28_price": prices.M28,
        }
    )
    data["price_spread_jun28_minus_jun27"] = data.jun28_price - data.jun27_price
    data["rate_spread_jun28_minus_jun27_bp"] = (
        -data.price_spread_jun28_minus_jun27 * 100
    )

    asof = data.date.iloc[-1].date()
    csv_path = DATA_DIR / f"euribor_jun28_jun27_since_march_{asof}.csv"
    png_path = FIG_DIR / f"euribor_jun28_jun27_since_march_{asof}.png"
    data.to_csv(csv_path, index=False, date_format="%Y-%m-%d")

    current_rate = float(data.rate_spread_jun28_minus_jun27_bp.iloc[-1])
    current_price = float(data.price_spread_jun28_minus_jun27.iloc[-1])
    mean_rate = float(data.rate_spread_jun28_minus_jun27_bp.mean())
    percentile = float(
        (data.rate_spread_jun28_minus_jun27_bp <= current_rate).mean() * 100
    )

    fig, (rate_ax, price_ax) = plt.subplots(
        2, 1, figsize=(11.5, 8.2), sharex=True, constrained_layout=True
    )
    rate_ax.plot(
        data.date,
        data.rate_spread_jun28_minus_jun27_bp,
        color="#14213d",
        linewidth=2.2,
    )
    rate_ax.axhline(0, color="#7a8797", linewidth=0.9)
    rate_ax.axhline(
        mean_rate,
        color="#2a9d8f",
        linewidth=1,
        linestyle=":",
        label=f"March mean {mean_rate:.1f} bp",
    )
    rate_ax.scatter(
        [data.date.iloc[-1]], [current_rate], color="#d95f02", s=65, zorder=4
    )
    rate_ax.annotate(
        f"{current_rate:+.1f} bp\n{percentile:.0f}th percentile",
        (data.date.iloc[-1], current_rate),
        xytext=(-95, 12),
        textcoords="offset points",
        color="#d95f02",
        fontweight="bold",
        arrowprops={"arrowstyle": "->", "color": "#d95f02"},
    )
    rate_ax.set_title(
        "Rate spread: June 2028 minus June 2027\n"
        "Flattener profits when this line falls"
    )
    rate_ax.set_ylabel("Basis points")
    rate_ax.grid(axis="y", color="#d9dee7", linewidth=0.8)
    rate_ax.spines[["top", "right"]].set_visible(False)
    rate_ax.legend(frameon=False, loc="upper right")

    price_ax.plot(
        data.date,
        data.price_spread_jun28_minus_jun27,
        color="#315f8c",
        linewidth=2.2,
    )
    price_ax.axhline(0, color="#7a8797", linewidth=0.9)
    price_ax.scatter(
        [data.date.iloc[-1]], [current_price], color="#d95f02", s=65, zorder=4
    )
    price_ax.annotate(
        f"{current_price:+.3f}",
        (data.date.iloc[-1], current_price),
        xytext=(-65, -22),
        textcoords="offset points",
        color="#d95f02",
        fontweight="bold",
        arrowprops={"arrowstyle": "->", "color": "#d95f02"},
    )
    price_ax.set_title(
        "Futures-price calendar: June 2028 price minus June 2027 price\n"
        "Buy June 2028 / sell June 2027; flattener profits when this line rises"
    )
    price_ax.set_ylabel("Contract price points")
    price_ax.grid(axis="y", color="#d9dee7", linewidth=0.8)
    price_ax.spines[["top", "right"]].set_visible(False)
    price_ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    price_ax.tick_params(axis="x", rotation=35)

    fig.suptitle(
        "Euribor June 2028 / June 2027 calendar since March 2026",
        fontsize=16,
    )
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {csv_path}")
    print(f"wrote {png_path}")


if __name__ == "__main__":
    main()
