"""STIR futures pricing, risk and RV structures.

Rate-space convention throughout: a *positive* structure level means the
rate-space combination is positive. Because 100-minus-rate contracts invert,
a zero-sum weight vector has rate-space value = -(price-space value); helper
functions handle the sign so call sites never do it by hand.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .conventions import Convention, convention, parse_contract

# ---------------------------------------------------------------- price/rate


def price_to_rate(price: float | np.ndarray) -> float | np.ndarray:
    """100-minus-rate quotation -> rate in percent."""
    return 100.0 - np.asarray(price, dtype=float) if isinstance(price, np.ndarray) else 100.0 - price


def rate_to_price(rate: float | np.ndarray) -> float | np.ndarray:
    return 100.0 - np.asarray(rate, dtype=float) if isinstance(rate, np.ndarray) else 100.0 - rate


# ------------------------------------------------------------------ discount


def bill_value(price: float, conv: Convention) -> float:
    """Value of one AUD/NZD 90-day bank bill contract at `price`."""
    if not conv.discount_priced:
        raise ValueError(f"{conv.futures_root} is not discount-priced")
    r = (100.0 - price) / 100.0
    return conv.notional / (1.0 + r * conv.term_years)


def bill_dv01(price: float, conv: Convention) -> float:
    """DV01 of a discount-priced bill contract, in contract currency per bp.

    Positive number = P&L for a long position when the rate falls 1bp.
    Unlike 100-minus-rate contracts this is level-dependent: it shrinks as
    yields rise.
    """
    return bill_value(price, conv) - bill_value(price - 0.01, conv)


def contract_dv01(symbol_or_root: str, price: float | None = None) -> float:
    """DV01 per contract per bp. `price` is required for AUD/NZD bills."""
    root = symbol_or_root.upper()
    try:
        conv = convention(root)
    except KeyError:
        root, _ = parse_contract(symbol_or_root)
        conv = convention(root)
    if conv.discount_priced:
        if price is None:
            raise ValueError(
                f"{conv.futures_root} DV01 is price-dependent; pass price="
            )
        return bill_dv01(price, conv)
    return conv.dv01


# ---------------------------------------------------------------- structures

# Sign conventions, stated once so no call site has to reason about them:
#   spread (1,-1) in rate space = front rate - back rate. Positive = inverted
#     (front above back), i.e. the curve is pricing cuts.
#   fly (1,-2,1) in rate space = wing1 - 2*body + wing2. Positive = the body
#     rate sits BELOW the straight line between the wings.
#   Desks differ on the fly sign. If yours quotes it the other way, negate at
#   the reporting layer - do not change these weights, the tests pin them.
STRUCTURE_WEIGHTS: dict[str, tuple[float, ...]] = {
    "outright": (1.0,),
    "spread": (1.0, -1.0),
    "fly": (1.0, -2.0, 1.0),
    "condor": (1.0, -1.0, -1.0, 1.0),
    "double_fly": (1.0, -3.0, 3.0, -1.0),
}


def structure_weights(name: str) -> np.ndarray:
    if name not in STRUCTURE_WEIGHTS:
        raise KeyError(f"unknown structure {name!r}; known: {sorted(STRUCTURE_WEIGHTS)}")
    return np.array(STRUCTURE_WEIGHTS[name], dtype=float)


def structure_level(prices, weights, space: str = "rate") -> float:
    """Level of a weighted combination, in basis points.

    space='rate'  : combination of implied rates (desk default for flies)
    space='price' : combination of quoted prices
    """
    p = np.asarray(prices, dtype=float)
    w = np.asarray(weights, dtype=float)
    if p.shape != w.shape:
        raise ValueError(f"prices {p.shape} and weights {w.shape} must align")
    if space == "price":
        return float(w @ p) * 100.0
    if space == "rate":
        return float(w @ (100.0 - p)) * 100.0
    raise ValueError("space must be 'rate' or 'price'")


def dv01_neutral_weights(dv01s, raw_weights) -> np.ndarray:
    """Rescale leg weights so each leg's DV01 contribution matches the intent.

    For same-DV01 contracts this returns `raw_weights` unchanged. It matters
    for cross-market structures (e.g. SR3 vs IR) and for bills, where DV01
    drifts with the price.
    """
    d = np.asarray(dv01s, dtype=float)
    w = np.asarray(raw_weights, dtype=float)
    if np.any(d == 0):
        raise ValueError("zero DV01 leg")
    return w * d[0] / d


@dataclass
class Strip:
    """An ordered futures strip: symbols with quoted prices."""

    symbols: list[str]
    prices: list[float]

    def __post_init__(self):
        if len(self.symbols) != len(self.prices):
            raise ValueError("symbols and prices must be the same length")

    @property
    def rates(self) -> np.ndarray:
        return 100.0 - np.asarray(self.prices, dtype=float)

    def index(self, symbol: str) -> int:
        try:
            return self.symbols.index(symbol.upper())
        except ValueError:
            raise KeyError(f"{symbol!r} not in strip {self.symbols}") from None

    def level(self, *symbols: str, structure: str | None = None, space: str = "rate") -> float:
        """Level of a named structure across the given contracts, in bp."""
        idx = [self.index(s) for s in symbols]
        w = structure_weights(structure or _infer_structure(len(idx)))
        return structure_level([self.prices[i] for i in idx], w, space=space)

    def sequential_spreads(self, space: str = "rate") -> np.ndarray:
        """All adjacent calendar spreads, in bp."""
        return np.array(
            [
                structure_level(self.prices[i : i + 2], structure_weights("spread"), space=space)
                for i in range(len(self.prices) - 1)
            ]
        )

    def sequential_flies(self, space: str = "rate") -> np.ndarray:
        return np.array(
            [
                structure_level(self.prices[i : i + 3], structure_weights("fly"), space=space)
                for i in range(len(self.prices) - 2)
            ]
        )


def _infer_structure(n_legs: int) -> str:
    return {1: "outright", 2: "spread", 3: "fly", 4: "condor"}.get(
        n_legs, ""
    ) or _raise_legs(n_legs)


def _raise_legs(n: int):
    raise ValueError(f"cannot infer a structure for {n} legs; pass structure=")


def roll_down(strip: Strip, symbols: list[str], periods: int = 1,
              structure: str | None = None, space: str = "rate") -> float:
    """Roll of a structure, in bp: today's level minus the level of the same
    structure shifted `periods` contracts earlier along the strip.

    This is pure roll on an unchanged curve. It is *not* carry - for carry on
    a dated structure you need the fixing path, see ois.step_path.
    """
    idx = [strip.index(s) for s in symbols]
    if min(idx) - periods < 0:
        raise ValueError("roll window runs off the front of the strip")
    w = structure_weights(structure or _infer_structure(len(idx)))
    now = structure_level([strip.prices[i] for i in idx], w, space=space)
    then = structure_level([strip.prices[i - periods] for i in idx], w, space=space)
    return now - then
