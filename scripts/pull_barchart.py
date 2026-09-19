"""Pull the three STIR strips from Barchart and answer the standing questions.

Usage:
    BARCHART_API_KEY=... python3 scripts/pull_barchart.py [--start 2026-01-01]

Runs in stages and stops at the first that genuinely blocks, naming what is
needed. Nothing here invents a number: if a strip cannot be pulled, that
market is reported as unavailable rather than estimated.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.stir import barchart as bc  # noqa: E402
from lib.stir import curves  # noqa: E402

ROOT_DIR = Path(__file__).resolve().parents[1]
CACHE = ROOT_DIR / "data" / "cache"

MARKETS = {"SR3": "SOFR 3M (CME)", "ER": "Euribor 3M (ICE)", "SON": "SONIA 3M (ICE)"}
END_2026 = date(2026, 12, 31)
END_2027 = date(2027, 12, 31)
END_2028 = date(2028, 12, 31)


def banner(text: str) -> None:
    print("\n" + "=" * 72)
    print(text)
    print("=" * 72)


def pull(client: bc.BarchartClient, start: date, n: int) -> dict[str, pd.DataFrame]:
    histories: dict[str, pd.DataFrame] = {}
    banner("STAGE 1 — confirming Barchart's symbol root for each market")
    roots: dict[str, str] = {}
    for our_root, label in MARKETS.items():
        try:
            probe = client.probe_roots(our_root)
        except (bc.BarchartAuthError, bc.BarchartUnavailable):
            raise  # environment-level, reported once by main()
        except bc.BarchartError as exc:
            print(f"  {label:<20} UNAVAILABLE — {type(exc).__name__}")
            print(f"    {exc}")
            return histories
        if probe["root"] is None:
            print(f"  {label:<20} NO WORKING ROOT")
            for cand, outcome in probe["tried"].items():
                print(f"      {cand:<6} {outcome}")
        else:
            roots[our_root] = probe["root"]
            print(f"  {label:<20} root={probe['root']}  ({probe['tried'][probe['root']]})")

    if not roots:
        print("\n  No market resolved. Nothing further can run.")
        return histories

    banner("STAGE 2 — pulling fixed-contract history")
    CACHE.mkdir(parents=True, exist_ok=True)
    for our_root, bar_root in roots.items():
        try:
            h = client.strip_history(bar_root, start, n_contracts=n)
        except bc.BarchartError as exc:
            print(f"  {MARKETS[our_root]:<20} FAILED — {exc}")
            continue
        curves.validate_history(h)
        out = CACHE / f"{our_root}_history.csv"
        h.to_csv(out)
        failed = h.attrs.get("failed_symbols", {})
        print(f"  {MARKETS[our_root]:<20} {h.shape[1]} contracts x {len(h)} days "
              f"-> {out.relative_to(ROOT_DIR)}")
        if failed:
            print(f"      no data for: {', '.join(sorted(failed))}")
        histories[our_root] = h
    return histories


def report(histories: dict[str, pd.DataFrame]) -> None:
    if not histories:
        return

    banner("Q1 — total rate change priced through end-2026")
    print("  Forward 3M rate at the last contract expiring on/before 2026-12-31,")
    print("  less the front contract. Negative = cuts priced.\n")
    for root, h in histories.items():
        try:
            pc = curves.priced_change_to(h, END_2026)
        except ValueError as exc:
            print(f"  {MARKETS[root]:<20} n/a — {exc}")
            continue
        print(f"  {MARKETS[root]:<20} {pc.front_symbol} {pc.front_rate:.3f}%  ->  "
              f"{pc.horizon_symbol} {pc.horizon_rate:.3f}%   "
              f"{pc.change_bp:+7.1f} bp  ({pc.in_moves():+.2f} x 25bp)")

    banner("Q2 — latest curves")
    for root, h in histories.items():
        tbl = curves.change_table(h, windows={"ytd": date(h.index[0].year, 1, 1), "2w": 10})
        print(f"\n  {MARKETS[root]}   as of {h.index[-1].date()}")
        print(f"  {'contract':>10} {'price':>9} {'rate %':>9} {'YTD bp':>9} {'2w bp':>9}")
        for sym, r in tbl.iterrows():
            print(f"  {sym:>10} {r['price']:>9.3f} {r['rate_pct']:>9.3f} "
                  f"{r.get('chg_ytd_bp', float('nan')):>9.1f} "
                  f"{r.get('chg_2w_bp', float('nan')):>9.1f}")

    banner("Q3 — biggest movers over the last two weeks")
    for root, h in histories.items():
        try:
            mv = curves.biggest_movers(h, window=10, top=3)
        except ValueError as exc:
            print(f"  {MARKETS[root]:<20} n/a — {exc}")
            continue
        print(f"\n  {MARKETS[root]}")
        for sym, r in mv.iterrows():
            print(f"    {sym:>10} {r['chg_win_bp']:+8.1f} bp   (rate now {r['rate_pct']:.3f}%)")

    banner("Q4 — Euribor end-2027 vs end-2028 segment")
    if "ER" not in histories:
        print("  Euribor unavailable, so this cannot be answered.")
        return
    try:
        slope = curves.segment_slope(histories["ER"], END_2027, END_2028)
    except ValueError as exc:
        print(f"  n/a — {exc}")
        return
    print("  Positive = inverted (end-27 rate above end-28).\n")
    print(f"  latest      {slope.iloc[-1]:+7.1f} bp   ({slope.index[-1].date()})")
    print(f"  2w ago      {slope.iloc[-11]:+7.1f} bp" if len(slope) > 10 else "  2w ago      n/a")
    print(f"  start-year  {slope.iloc[0]:+7.1f} bp   ({slope.index[0].date()})")
    print(f"  change YTD  {slope.iloc[-1] - slope.iloc[0]:+7.1f} bp")
    out = CACHE / "ER_end27_end28_slope.csv"
    slope.to_csv(out)
    print(f"\n  full series -> {out.relative_to(ROOT_DIR)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-01-01")
    ap.add_argument("--contracts", type=int, default=12)
    args = ap.parse_args()
    start = date.fromisoformat(args.start)

    client = bc.BarchartClient()
    try:
        histories = pull(client, start, args.contracts)
    except bc.BarchartAuthError as exc:
        banner("BLOCKED — no API key")
        print(exc)
        return 2
    except bc.BarchartUnavailable as exc:
        banner("BLOCKED — host unreachable")
        print(exc)
        return 3

    report(histories)
    return 0 if histories else 1


if __name__ == "__main__":
    raise SystemExit(main())
