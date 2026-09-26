"""Plot the Jun-28 minus Jun-27 three-month SONIA futures spread.

The input is the fixed-contract history written by ``pull_barchart.py``.  The
spread is reported in rate space: Jun-28 implied rate less Jun-27 implied
rate.  With futures quoted as 100 minus rate, that is price(Jun-27) minus
price(Jun-28), multiplied by 100 to express the result in basis points.

Usage:
    python3 scripts/plot_sonia_jun28_jun27.py
    python3 scripts/plot_sonia_jun28_jun27.py --input path/to/SON_history.csv
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "cache" / "SON_history.csv"
DEFAULT_OUTPUT = ROOT / "research" / "charts" / "sonia_jun28_minus_jun27_30d.png"


def _june_contract(columns: pd.Index, year: int) -> str:
    """Return the unique June contract column for ``year``.

    Supports both Barchart's candidate roots (for example ``SOM27``) and a
    locally supplied canonical name such as ``SONM2027``.
    """
    suffixes = (f"M{year % 100:02d}", f"M{year}")
    matches = [str(c) for c in columns if any(re.search(f"{s}$", str(c), re.I) for s in suffixes)]
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one Jun-{year % 100:02d} column, found {matches or 'none'}"
        )
    return matches[0]


def calculate_spread(history: pd.DataFrame, days: int = 30) -> pd.Series:
    """Return Jun-28 minus Jun-27 implied rate in bp over calendar ``days``."""
    if days <= 0:
        raise ValueError("days must be positive")
    jun27 = _june_contract(history.columns, 2027)
    jun28 = _june_contract(history.columns, 2028)
    prices = history[[jun27, jun28]].apply(pd.to_numeric, errors="coerce").dropna()
    if prices.empty:
        raise ValueError("the two June contracts have no overlapping observations")
    end = prices.index.max()
    start = end - pd.Timedelta(days=days)
    spread = (prices[jun27] - prices[jun28]).loc[lambda s: s.index >= start] * 100.0
    spread.name = "Jun-28 minus Jun-27 SONIA (bp)"
    return spread


def plot_spread(spread: pd.Series, output: Path) -> None:
    """Render ``spread`` to ``output``."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(spread.index, spread, color="#17365d", linewidth=2)
    ax.axhline(0, color="black", linewidth=0.8, alpha=0.55)
    latest = spread.iloc[-1]
    ax.scatter(spread.index[-1], latest, color="#c43b33", zorder=3)
    ax.annotate(f"{latest:.1f} bp", (spread.index[-1], latest), xytext=(-8, 9),
                textcoords="offset points", ha="right", fontweight="bold")
    ax.set_title("SONIA: Jun-28 minus Jun-27 implied rate")
    ax.set_ylabel("basis points")
    ax.set_xlabel("")
    ax.grid(axis="y", alpha=0.25)
    fig.autofmt_xdate()
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--days", type=int, default=30, help="calendar-day lookback")
    args = parser.parse_args()

    if not args.input.exists():
        parser.error(
            f"no SONIA history at {args.input}. Pull it with scripts/pull_barchart.py "
            "or pass --input; market levels are never fabricated."
        )
    history = pd.read_csv(args.input, index_col=0, parse_dates=True)
    spread = calculate_spread(history, args.days)
    plot_spread(spread, args.output)
    print(f"{spread.index[0].date()} to {spread.index[-1].date()}: "
          f"{spread.iloc[-1]:.1f} bp -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
