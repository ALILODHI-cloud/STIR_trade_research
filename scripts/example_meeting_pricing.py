"""Worked example: from a pasted strip to what the curve is actually pricing.

Runs end to end on the illustrative strip in data/manual/strip_example.yaml.
The numbers are made up - replace the yaml with real settles before drawing
any conclusion from the output.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.stir import data, ois
from lib.stir import futures as fut
from lib.stir.conventions import convention, parse_contract

# Illustrative FOMC effective dates (the day after each decision).
FOMC_EFFECTIVE = [
    date(2026, 10, 29), date(2026, 12, 10), date(2027, 1, 28),
    date(2027, 3, 18), date(2027, 5, 6), date(2027, 6, 17),
]


def main() -> None:
    symbols, prices = data.manual_strip("strip_example")
    strip = fut.Strip(symbols, prices)
    conv = convention("SR3")

    print("=" * 66)
    print("SR3 strip (ILLUSTRATIVE DATA - not market levels)")
    print("=" * 66)
    print(f"{'contract':>10} {'price':>9} {'rate %':>9} {'expiry':>12}")
    for s, p, r in zip(strip.symbols, strip.prices, strip.rates, strict=True):
        _, expiry = parse_contract(s, reference=date(2026, 9, 18))
        print(f"{s:>10} {p:>9.3f} {r:>9.3f} {expiry!s:>12}")

    print("\nadjacent calendar spreads (rate space, bp; +ve = inverted)")
    for a, b, v in zip(strip.symbols, strip.symbols[1:],
                       strip.sequential_spreads(), strict=False):
        print(f"  {a}/{b:<8} {v:>8.1f}   DV01 {conv.dv01:>6.2f}/contract/leg")

    print("\nadjacent flies (rate space, bp; +ve = body below the wings' line)")
    for a, b, c, v in zip(strip.symbols, strip.symbols[1:], strip.symbols[2:],
                          strip.sequential_flies(), strict=False):
        print(f"  {a}/{b}/{c:<8} {v:>8.1f}")

    # --- what the meeting-dated curve implies -------------------------------
    # Two ways in, both of which a desk actually has to hand.
    #
    # (a) Dated forwards: "the rate prevailing after each meeting". This is
    #     what you read off a meeting-dated OIS grid, and it maps to steps
    #     exactly - no solving required.
    spot = 4.00  # illustrative prevailing SOFR
    valuation = date(2026, 9, 18)
    dated_forwards = dict(zip(FOMC_EFFECTIVE, [3.88, 3.70, 3.58, 3.50, 3.46, 3.44], strict=True))
    steps = ois.steps_from_dated_forwards(dated_forwards, spot)
    curve = ois.MeetingCurve(valuation, spot, conv.day_basis, steps)

    print("\n" + "=" * 66)
    print("implied policy path (ILLUSTRATIVE)")
    print("=" * 66)
    print(f"{'meeting':>12} {'step bp':>9} {'cum bp':>9} {'25bp units':>12} {'rate after':>11}")
    cum, moves = curve.cumulative(), curve.implied_moves(25.0)
    for m in sorted(curve.steps):
        print(f"{m!s:>12} {curve.steps[m]*100:>9.1f} {cum[m]*100:>9.1f} "
              f"{moves[m]:>12.2f} {curve.rate_after(m):>11.3f}")

    # (b) Spot-start OIS quotes: the bootstrap solves each step in turn. Here
    #     the quotes are generated off the path above, so recovering it is a
    #     round-trip check on the solver rather than new information.
    quotes = {
        m + timedelta(days=1): curve.ois(valuation, m + timedelta(days=1))
        for m in FOMC_EFFECTIVE
    }
    rebuilt = ois.bootstrap_steps(valuation, spot, quotes, FOMC_EFFECTIVE,
                                  basis=conv.day_basis)
    worst_step = max(abs(rebuilt.steps[m] - steps[m]) for m in FOMC_EFFECTIVE) * 1e4
    worst_px = max(abs(rebuilt.ois(valuation, mat) - q) for mat, q in quotes.items()) * 1e4
    print(f"\nbootstrap round trip: max step error {worst_step:.2e} bp, "
          f"max repricing error {worst_px:.2e} bp")

    # --- risk ---------------------------------------------------------------
    lots = 100
    leg_dv01 = conv.dv01 * lots
    print("\n" + "=" * 66)
    print(f"Risk on a {lots}-lot SR3Z6/SR3H7 spread")
    print("=" * 66)
    print(f"  DV01 per leg          : {leg_dv01:>12,.0f} USD/bp")
    print(f"  P&L, 1bp flattening   : {leg_dv01:>12,.0f} USD")
    print(f"  Current level         : {strip.level('SR3Z6', 'SR3H7'):>12.1f} bp")
    roll = fut.roll_down(strip, ['SR3H7', 'SR3M7'], periods=1)
    print(f"  3m roll on H7/M7      : {roll:>12.1f} bp  "
          f"({roll * leg_dv01:,.0f} USD on {lots} lots)")

    # Cross-market DV01 matching, where the naive 1:1 is wrong.
    aud_px = 96.10
    aud_dv01 = fut.bill_dv01(aud_px, convention("IR"))
    w = fut.dv01_neutral_weights([conv.dv01, aud_dv01], [1.0, -1.0])
    print(f"\n  SR3 vs AUD IR @ {aud_px}: AUD bill DV01 {aud_dv01:.2f} "
          f"(vs {conv.dv01:.2f}) -> hedge ratio {abs(w[1]):.3f}")


if __name__ == "__main__":
    main()
