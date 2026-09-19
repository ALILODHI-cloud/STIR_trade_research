"""Meeting-dated OIS: step decomposition and reconstruction.

The workhorse for DM STIR. The overnight rate is modelled as piecewise
constant, changing only on policy *effective* dates (for the Fed, the day
after the FOMC decision; for the ECB, the start of the following reserve
maintenance period - pass whichever you mean, the code does not guess).

Compounding is calendar-day: weekend and holiday accruals carry the previous
business day's fixing, which for a piecewise-constant path is exactly what
daily compounding gives.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

import numpy as np
from scipy.optimize import brentq


def _days(start: date, end: date) -> int:
    n = (end - start).days
    if n <= 0:
        raise ValueError(f"end ({end}) must be after start ({start})")
    return n


def step_path(start: date, end: date, spot_rate: float,
              steps: dict[date, float]) -> np.ndarray:
    """Daily rate path (in percent) over [start, end).

    `steps` maps an effective date to the *change* in the overnight rate on
    that date, in percent (so a 25bp cut is -0.25).
    """
    n = _days(start, end)
    path = np.full(n, float(spot_rate))
    for eff, delta in sorted(steps.items()):
        if eff <= start:
            path += delta          # already in effect across the whole window
        elif eff < end:
            path[(eff - start).days:] += delta
    return path


def compound_rate(path: np.ndarray, basis: int) -> float:
    """Annualised compounded rate (percent) from a daily rate path."""
    factor = np.prod(1.0 + path / 100.0 / basis)
    return (factor - 1.0) * basis / len(path) * 100.0


def ois_rate(start: date, end: date, spot_rate: float,
             steps: dict[date, float], basis: int = 360) -> float:
    """Fair OIS rate (percent) for [start, end) under a given step path."""
    return compound_rate(step_path(start, end, spot_rate, steps), basis)


@dataclass
class MeetingCurve:
    """A bootstrapped policy path."""

    valuation: date
    spot_rate: float
    basis: int
    steps: dict[date, float] = field(default_factory=dict)

    def rate_after(self, meeting: date) -> float:
        """Overnight rate prevailing once `meeting` has taken effect."""
        return self.spot_rate + sum(d for m, d in self.steps.items() if m <= meeting)

    def cumulative(self) -> dict[date, float]:
        """Cumulative change from spot, by meeting, in percent."""
        out, run = {}, 0.0
        for m in sorted(self.steps):
            run += self.steps[m]
            out[m] = run
        return out

    def implied_moves(self, step_size_bp: float = 25.0) -> dict[date, float]:
        """Priced moves per meeting, expressed in units of a standard move."""
        return {m: (d * 100.0) / step_size_bp for m, d in sorted(self.steps.items())}

    def ois(self, start: date, end: date) -> float:
        return ois_rate(start, end, self.spot_rate, self.steps, self.basis)


def bootstrap_steps(valuation: date, spot_rate: float,
                    quotes: dict[date, float], meetings: list[date],
                    basis: int = 360, start: date | None = None) -> MeetingCurve:
    """Back out per-meeting steps from meeting-dated OIS quotes.

    `quotes` maps an OIS *maturity* date to its quoted rate in percent.
    `meetings` are policy effective dates.

    Normally each quote spans exactly one meeting that the previous quote did
    not, and that meeting's step is determined exactly. Where a quote spans
    several unsolved meetings the system is under-determined, so the move is
    spread *evenly* across them rather than guessed at. That is a convention,
    not a result - if the attribution across those meetings matters to the
    trade, quote the intermediate maturities instead of relying on it.
    """
    start = start or valuation
    meetings = sorted(m for m in meetings if m > start)
    steps: dict[date, float] = {}
    solved: set[date] = set()

    for maturity in sorted(quotes):
        spanned = [m for m in meetings if m < maturity and m not in solved]
        if not spanned:
            continue  # quote adds no new meeting information
        target = quotes[maturity]
        known = dict(steps)

        def err(x: float, _mat=maturity, _span=spanned, _known=known, _t=target) -> float:
            trial = dict(_known)
            for m in _span:
                trial[m] = x
            return ois_rate(start, _mat, spot_rate, trial, basis) - _t

        try:
            x = brentq(err, -10.0, 10.0, xtol=1e-12)
        except ValueError as exc:
            total = _days(start, maturity)
            after = _days(spanned[0], maturity)
            hint = ""
            if after < 0.2 * total:
                hint = (
                    f"\n  Only {after} of the {total} days in this window fall "
                    f"after {spanned[0]}, so the step is barely identified. "
                    "This usually means the quotes are meeting-dated FORWARD "
                    "rates (the rate prevailing between two meetings) rather "
                    "than spot-start OIS. For those use "
                    "steps_from_dated_forwards()."
                )
            raise ValueError(
                f"could not solve the step(s) at {[str(m) for m in spanned]} for "
                f"the {maturity} quote ({target}%) within a +/-1000bp range." + hint
            ) from exc
        for m in spanned:
            steps[m] = x
        solved.update(spanned)

    return MeetingCurve(valuation, spot_rate, basis, steps)


def steps_from_dated_forwards(dated: dict[date, float], spot_rate: float) -> dict[date, float]:
    """Convert a set of 'rate prevailing after meeting X' levels into steps."""
    out, prev = {}, spot_rate
    for m in sorted(dated):
        out[m] = dated[m] - prev
        prev = dated[m]
    return out


def futures_implied_rate(curve: MeetingCurve, ref_start: date, ref_end: date) -> float:
    """Compounded reference rate for a 3M futures reference quarter."""
    return curve.ois(ref_start, ref_end)
