"""UVXY vs SVXY, Jan 2013 to today.

Produces three panels:
  1. dual-axis linear      — as requested
  2. shared log axis       — the one to actually read
  3. indexed to 100        — same information, percentage framing

Data is NOT fetched: every provider is blocked by this environment's egress
policy. Drop files in data/raw/ as UVXY.csv and SVXY.csv with a date column
and a price column, and this runs.

TWO THINGS WILL RUIN THIS CHART IF THE INPUT IS WRONG:

  1. Reverse splits. UVXY has reverse-split many times. Raw (unadjusted)
     closes turn each split into a vertical jump and destroy the series.
     Use ADJUSTED closes. This script flags suspected splits rather than
     plotting through them silently.
  2. Leverage changes. In February 2018 ProShares cut UVXY from 2x to 1.5x
     and SVXY from -1x to -0.5x. No price series marks this, but the
     instruments before and after are not the same thing. The script draws
     the break so it cannot be read past by accident. Confirm the exact
     effective date against ProShares' own filings before citing it.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "cache"

START = pd.Timestamp("2013-01-01")
LEVERAGE_CHANGE = pd.Timestamp("2018-02-28")

# Two hues, fixed order, high separation in both normal and CVD vision.
INK = "#1f2933"
MUTED = "#7b8794"
GRID = "#e4e7eb"
COLORS = {"UVXY": "#1f6feb", "SVXY": "#d1561b"}


class DataMissing(FileNotFoundError):
    pass


def load(ticker: str) -> pd.Series:
    """Load a price series; prefer an adjusted-close column if one exists."""
    candidates = sorted(RAW.glob(f"{ticker}*.csv")) + sorted(RAW.glob(f"{ticker.lower()}*.csv"))
    if not candidates:
        raise DataMissing(
            f"no file for {ticker} in {RAW.relative_to(ROOT)}/.\n"
            f"  Expected {ticker}.csv with a date column and a price column.\n"
            f"  Use ADJUSTED closes - raw closes are broken by reverse splits."
        )
    df = pd.read_csv(candidates[0])
    date_col = next((c for c in df.columns if "date" in c.lower()), df.columns[0])
    pref = ["adj close", "adj_close", "adjclose", "adjusted_close", "adjusted close"]
    price_col = next((c for c in df.columns if c.lower().strip() in pref), None)
    used_adjusted = price_col is not None
    if price_col is None:
        price_col = next((c for c in df.columns if c.lower().strip() in ("close", "last", "price")),
                         df.columns[-1])
    s = pd.Series(
        pd.to_numeric(df[price_col], errors="coerce").to_numpy(),
        index=pd.DatetimeIndex(pd.to_datetime(df[date_col], errors="coerce")),
        name=ticker,
    ).dropna().sort_index()
    s.attrs["adjusted"] = used_adjusted
    s.attrs["column"] = price_col
    s.attrs["file"] = candidates[0].name
    if (s <= 0).any():
        raise ValueError(f"{ticker}: non-positive prices present; a log plot is undefined")
    return s


def suspected_splits(s: pd.Series, threshold: float = 1.5) -> pd.Series:
    """Single-day returns above `threshold` (150%) - almost certainly a split.

    Real vol-ETP moves are large but a 1:4 reverse split is +300% in one day.
    Returned as a Series of dates -> return, empty if the data looks adjusted.
    """
    r = s.pct_change()
    return r[r > threshold]


def _style(ax):
    ax.grid(True, color=GRID, linewidth=0.8, alpha=0.9)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)


def _mark_leverage_change(ax, lo, hi):
    if not (lo <= LEVERAGE_CHANGE <= hi):
        return
    ax.axvline(LEVERAGE_CHANGE, color=MUTED, linewidth=1.2, linestyle=(0, (4, 3)), zorder=1)
    # Anchored low: the subtitle occupies the top of the axes and the two
    # collided when this sat at 0.97.
    ax.annotate("Feb 2018: UVXY 2x→1.5x, SVXY −1x→−0.5x",
                xy=(LEVERAGE_CHANGE, 0.02), xycoords=("data", "axes fraction"),
                xytext=(6, 0), textcoords="offset points",
                fontsize=8, color=MUTED, va="bottom", ha="left")


PANELS = ("dual", "log", "indexed")


def plot_all(uvxy: pd.Series, svxy: pd.Series, outdir: Path,
             panels: tuple[str, ...] = ("dual",)) -> list[Path]:
    """Render the requested panels. Defaults to the dual-axis view."""
    unknown = [p for p in panels if p not in PANELS]
    if unknown:
        raise ValueError(f"unknown panel(s) {unknown}; choose from {list(PANELS)}")
    outdir.mkdir(parents=True, exist_ok=True)
    lo, hi = min(uvxy.index[0], svxy.index[0]), max(uvxy.index[-1], svxy.index[-1])
    written = []

    # --- 1. dual axis ---------------------------------------------------
    if "dual" in panels:
     fig, ax = plt.subplots(figsize=(12, 6))
     ax2 = ax.twinx()
     (line_uvxy,) = ax.plot(uvxy.index, uvxy.values, color=COLORS["UVXY"],
                            linewidth=2, label="UVXY (left)")
     (line_svxy,) = ax2.plot(svxy.index, svxy.values, color=COLORS["SVXY"],
                             linewidth=2, label="SVXY (right)")
     ax.set_ylabel("UVXY", color=COLORS["UVXY"], fontsize=10)
     ax2.set_ylabel("SVXY", color=COLORS["SVXY"], fontsize=10)
     ax.tick_params(axis="y", colors=COLORS["UVXY"])
     ax2.tick_params(axis="y", colors=COLORS["SVXY"])
     _style(ax)
     ax2.spines["top"].set_visible(False)
     _mark_leverage_change(ax, lo, hi)
     ax.set_title("UVXY and SVXY — separate y-axes", color=INK, fontsize=13, loc="left", pad=14)
     fig.text(0.125, 0.90, "Two scales: the apparent co-movement is an artefact of axis choice.",
              fontsize=9, color=MUTED)
     # Explicit handles: ax.get_lines() also returns the Feb-2018 axvline,
     # which then appeared in the legend as "_child1".
     ax.legend([line_uvxy, line_svxy],
               [line_uvxy.get_label(), line_svxy.get_label()],
               frameon=False, loc="upper right", fontsize=9, labelcolor=INK)
     fig.tight_layout()
     p = outdir / "uvxy_svxy_dual_axis.png"
     fig.savefig(p, dpi=150, facecolor="white")
     plt.close(fig)
     written.append(p)

    # --- 2. shared log axis ---------------------------------------------
    if "log" in panels:
     fig, ax = plt.subplots(figsize=(12, 6))
     for name, s in (("UVXY", uvxy), ("SVXY", svxy)):
         ax.plot(s.index, s.values, color=COLORS[name], linewidth=2, label=name)
         ax.annotate(name, xy=(s.index[-1], s.iloc[-1]), xytext=(8, 0),
                     textcoords="offset points", color=COLORS[name],
                     fontsize=10, va="center", fontweight="bold")
     ax.set_yscale("log")
     ax.set_ylabel("Price (log scale, USD)", color=MUTED, fontsize=10)
     _style(ax)
     _mark_leverage_change(ax, lo, hi)
     ax.set_title("UVXY and SVXY — one shared log axis", color=INK, fontsize=13, loc="left", pad=14)
     fig.text(0.125, 0.90, "Equal vertical distance = equal percentage move. The honest view.",
              fontsize=9, color=MUTED)
     ax.legend(frameon=False, loc="upper right", fontsize=9, labelcolor=INK)
     fig.tight_layout()
     p = outdir / "uvxy_svxy_log.png"
     fig.savefig(p, dpi=150, facecolor="white")
     plt.close(fig)
     written.append(p)

    # --- 3. indexed to 100 ----------------------------------------------
    if "indexed" in panels:
     fig, ax = plt.subplots(figsize=(12, 6))
     for name, s in (("UVXY", uvxy), ("SVXY", svxy)):
         idx = s / s.iloc[0] * 100.0
         ax.plot(idx.index, idx.values, color=COLORS[name], linewidth=2, label=name)
     ax.set_yscale("log")
     ax.axhline(100, color=MUTED, linewidth=1, linestyle=":")
     ax.set_ylabel(f"Indexed to 100 at {uvxy.index[0].date()} (log)", color=MUTED, fontsize=10)
     _style(ax)
     _mark_leverage_change(ax, lo, hi)
     ax.set_title("UVXY and SVXY — total return from a common base",
                  color=INK, fontsize=13, loc="left", pad=14)
     ax.legend(frameon=False, loc="upper right", fontsize=9, labelcolor=INK)
     fig.tight_layout()
     p = outdir / "uvxy_svxy_indexed.png"
     fig.savefig(p, dpi=150, facecolor="white")
     plt.close(fig)
     written.append(p)
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--panels", default="dual",
                    help=f"comma-separated, any of {list(PANELS)}, or 'all' (default: dual)")
    args = ap.parse_args()
    panels = tuple(PANELS) if args.panels == "all" else tuple(
        p.strip() for p in args.panels.split(",") if p.strip())

    try:
        uvxy, svxy = load("UVXY"), load("SVXY")
    except DataMissing as exc:
        print("BLOCKED — no data\n")
        print(exc)
        print("\n  Every price provider is denied by this environment's egress")
        print("  policy (Yahoo, Stooq, Barchart, Investing all 403 at the gateway).")
        return 2

    for name, s in (("UVXY", uvxy), ("SVXY", svxy)):
        span = f"{s.index[0].date()} to {s.index[-1].date()} ({len(s)} rows)"
        flag = "adjusted" if s.attrs["adjusted"] else "NOT adjusted - suspect"
        print(f"{name}: {span}, column {s.attrs['column']!r} [{flag}]")
        splits = suspected_splits(s)
        if len(splits):
            print(f"  WARNING: {len(splits)} single-day moves above +150% — "
                  f"these look like reverse splits, not market moves:")
            for d, r in splits.head(8).items():
                print(f"    {d.date()}  {r * 100:+.0f}%")
            print("  Re-pull using adjusted closes; this series is not plottable as is.")

    uvxy, svxy = uvxy[uvxy.index >= START], svxy[svxy.index >= START]
    if uvxy.empty or svxy.empty:
        print("No data on or after 2013-01-01.")
        return 1

    written = plot_all(uvxy, svxy, OUT, panels=panels)
    print("\nWritten:")
    for p in written:
        print(f"  {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
