"""Cross-market strip analysis: priced change to a horizon, and move tables.

Everything here takes a *history* DataFrame: a DatetimeIndex of observation
dates, one column per contract symbol, values = quoted futures prices. That
is the shape an exchange settlement export lands in, and it is the only shape
these functions accept, so a malformed export fails loudly rather than
producing a plausible wrong number.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from .conventions import parse_contract


def validate_history(history: pd.DataFrame, root: str | None = None) -> pd.DataFrame:
    """Check a settlement history is well formed; return it sorted by date."""
    if not isinstance(history.index, pd.DatetimeIndex):
        raise TypeError("history must be indexed by observation date (DatetimeIndex)")
    if history.index.has_duplicates:
        dupes = history.index[history.index.duplicated()].unique()
        raise ValueError(f"duplicate observation dates in history: {list(dupes)[:5]}")
    bad = [c for c in history.columns if not _is_symbol(c)]
    if bad:
        raise ValueError(f"columns must be contract symbols; unparseable: {bad[:5]}")
    if root is not None:
        wrong = [c for c in history.columns if parse_contract(c)[0].upper() != root.upper()]
        if wrong:
            raise ValueError(f"columns not in root {root!r}: {wrong[:5]}")
    vals = history.to_numpy(dtype=float)
    finite = vals[np.isfinite(vals)]
    if finite.size and (finite.min() < 80.0 or finite.max() > 110.0):
        raise ValueError(
            "values outside 80-110 look like rates, not 100-minus-rate prices. "
            "These functions expect quoted prices."
        )
    return history.sort_index()


def _is_symbol(col: str) -> bool:
    try:
        parse_contract(str(col))
        return True
    except ValueError:
        return False


def expiries(history: pd.DataFrame, reference: date | None = None) -> pd.Series:
    """Map each column to its contract expiry, ordered along the strip."""
    ref = reference or date.today()
    out = {c: parse_contract(str(c), reference=ref)[1] for c in history.columns}
    return pd.Series(out).sort_values()


def strip_on(history: pd.DataFrame, asof: pd.Timestamp | str | None = None) -> pd.Series:
    """The strip as of a date (the last observation at or before it)."""
    h = history.sort_index()
    if asof is None:
        row = h.iloc[-1]
    else:
        ts = pd.Timestamp(asof)
        prior = h.loc[:ts]
        if prior.empty:
            raise KeyError(f"no observations at or before {ts.date()}")
        row = prior.iloc[-1]
    return row.dropna()


def implied_rates(strip: pd.Series) -> pd.Series:
    return 100.0 - strip.astype(float)


@dataclass
class PricedChange:
    """Total change in the implied rate priced between two points on a strip."""

    front_symbol: str
    horizon_symbol: str
    front_rate: float
    horizon_rate: float
    asof: pd.Timestamp

    @property
    def change_bp(self) -> float:
        """Negative = cuts priced, positive = hikes priced."""
        return (self.horizon_rate - self.front_rate) * 100.0

    def in_moves(self, step_bp: float = 25.0) -> float:
        return self.change_bp / step_bp


def priced_change_to(history: pd.DataFrame, horizon: date,
                     asof: pd.Timestamp | str | None = None,
                     front: str | None = None,
                     reference: date | None = None) -> PricedChange:
    """Total rate change the strip prices between the front contract and the
    last contract expiring on or before `horizon`.

    Read this as "what the strip discounts by `horizon`", with one caveat
    worth stating every time: a 3M contract references a forward quarter
    starting at its expiry, so the Dec-26 contract prices the Dec-26 to
    Mar-27 window, not the calendar year to end-2026. The number is a clean
    like-for-like comparison of two forward 3M rates, not a policy-path
    cumulative. For the latter use ois.bootstrap_steps with dated OIS.
    """
    row = strip_on(history, asof)
    exp = expiries(history, reference)
    exp = exp[exp.index.isin(row.index)].sort_values()
    if exp.empty:
        raise ValueError("no contracts with data on that date")

    front_sym = front or str(exp.index[0])
    eligible = exp[exp <= horizon]
    if eligible.empty:
        raise ValueError(
            f"no contract in this strip expires on or before {horizon}; "
            f"earliest is {exp.iloc[0]}"
        )
    horizon_sym = str(eligible.index[-1])
    rates = implied_rates(row)
    ts = pd.Timestamp(asof) if asof is not None else history.sort_index().index[-1]
    return PricedChange(front_sym, horizon_sym,
                        float(rates[front_sym]), float(rates[horizon_sym]), ts)


def change_table(history: pd.DataFrame, asof: pd.Timestamp | str | None = None,
                 windows: dict[str, object] | None = None,
                 reference: date | None = None) -> pd.DataFrame:
    """Per-contract level and change in bp over each named window.

    `windows` maps a label to either an int (observations back) or a date /
    timestamp (change since that date). Changes are in RATE space: positive
    means the implied rate rose (price fell).
    """
    h = history.sort_index()
    ts = pd.Timestamp(asof) if asof is not None else h.index[-1]
    h = h.loc[:ts]
    if h.empty:
        raise KeyError(f"no observations at or before {ts.date()}")
    windows = windows or {"1d": 1, "1w": 5, "2w": 10}

    latest_rates = implied_rates(h.iloc[-1])
    exp = expiries(history, reference)
    out = pd.DataFrame({
        "expiry": exp.reindex(latest_rates.index),
        "price": h.iloc[-1],
        "rate_pct": latest_rates,
    })

    for label, spec in windows.items():
        if isinstance(spec, int):
            if len(h) <= spec:
                out[f"chg_{label}_bp"] = np.nan
                continue
            base = implied_rates(h.iloc[-1 - spec])
        else:
            base_ts = pd.Timestamp(spec)
            prior = h.loc[:base_ts]
            if prior.empty:
                out[f"chg_{label}_bp"] = np.nan
                continue
            base = implied_rates(prior.iloc[-1])
        out[f"chg_{label}_bp"] = (latest_rates - base.reindex(latest_rates.index)) * 100.0

    return out.sort_values("expiry")


def biggest_movers(history: pd.DataFrame, window: int | str | date = 10,
                   asof: pd.Timestamp | str | None = None,
                   top: int = 3, reference: date | None = None) -> pd.DataFrame:
    """Contracts that moved most over a window, ranked by absolute change."""
    tbl = change_table(history, asof, {"win": window}, reference)
    tbl = tbl.dropna(subset=["chg_win_bp"])
    if tbl.empty:
        raise ValueError("no contract has data at both ends of that window")
    return tbl.reindex(tbl["chg_win_bp"].abs().sort_values(ascending=False).index).head(top)


def segment_slope(history: pd.DataFrame, start: date, end: date,
                  asof: pd.Timestamp | str | None = None,
                  reference: date | None = None) -> pd.Series:
    """Rate-space slope in bp between the last contracts expiring on or before
    `start` and `end`. Positive = inverted over that segment (front above back).

    Used for questions like "is the end-27 / end-28 segment inverting".
    """
    h = history.sort_index()
    exp = expiries(history, reference)
    out = {}
    for ts, row in h.iterrows():
        avail = exp[exp.index.isin(row.dropna().index)].sort_values()
        a = avail[avail <= start]
        b = avail[avail <= end]
        if a.empty or b.empty or a.index[-1] == b.index[-1]:
            continue
        rates = implied_rates(row)
        out[ts] = (rates[a.index[-1]] - rates[b.index[-1]]) * 100.0
    if not out:
        raise ValueError(
            f"could not find distinct contracts bracketing {start} and {end} "
            "on any observation date"
        )
    return pd.Series(out, name=f"slope_{start}_{end}_bp").sort_index()
