"""Market conventions for developed-market STIR products.

Covers the contract set a DM STIR book typically runs: SOFR, SONIA, ESTR,
Euribor, TONA, CORRA, and the AUD/NZD bank bills (which price on a discount
formula rather than 100-minus-rate, so their DV01 moves with the price).
"""
from __future__ import annotations

import calendar
import re
from dataclasses import dataclass
from datetime import date

MONTH_CODES = "FGHJKMNQUVXZ"  # Jan .. Dec
QUARTERLY_MONTHS = (3, 6, 9, 12)


def month_to_code(month: int) -> str:
    if not 1 <= month <= 12:
        raise ValueError(f"month out of range: {month}")
    return MONTH_CODES[month - 1]


def code_to_month(code: str) -> int:
    code = code.upper()
    if code not in MONTH_CODES:
        raise ValueError(f"not a futures month code: {code!r}")
    return MONTH_CODES.index(code) + 1


def imm_date(year: int, month: int) -> date:
    """Third Wednesday of the month (IMM date)."""
    weds = [
        date(year, month, d)
        for d in range(1, calendar.monthrange(year, month)[1] + 1)
        if date(year, month, d).weekday() == 2
    ]
    return weds[2]


def imm_sequence(start: date, n: int, months=QUARTERLY_MONTHS) -> list[date]:
    """The next `n` IMM dates strictly after `start`."""
    out, year = [], start.year
    while len(out) < n:
        for m in months:
            d = imm_date(year, m)
            if d > start:
                out.append(d)
                if len(out) == n:
                    break
        year += 1
    return out


_CONTRACT_RE = re.compile(r"^(?P<root>[A-Z0-9]{2,4}?)(?P<code>[FGHJKMNQUVXZ])(?P<year>\d{1,2})$")


def parse_contract(symbol: str, reference: date | None = None) -> tuple[str, date]:
    """Parse e.g. 'SR3Z6' -> ('SR3', date(2026,12,16)).

    A single-digit year is resolved to the nearest such year within the
    decade window [reference - 2y, reference + 8y].
    """
    reference = reference or date.today()
    m = _CONTRACT_RE.match(symbol.upper().strip())
    if not m:
        raise ValueError(f"unrecognised contract symbol: {symbol!r}")
    root, month = m.group("root"), code_to_month(m.group("code"))
    raw = m.group("year")
    if len(raw) == 2:
        year = 2000 + int(raw)
    else:
        digit, base = int(raw), reference.year - 2
        year = base + ((digit - base) % 10)
    return root, imm_date(year, month)


@dataclass(frozen=True)
class Convention:
    ccy: str
    index: str
    day_count: str
    day_basis: int
    central_bank: str
    futures_root: str
    notional: float
    term_years: float
    tick: float
    discount_priced: bool = False  # AUD/NZD bank bills

    @property
    def dv01(self) -> float:
        """Currency P&L per contract per basis point (100-minus-rate contracts)."""
        if self.discount_priced:
            raise ValueError(
                f"{self.futures_root} is discount-priced; DV01 depends on the "
                "price level - use futures.bill_dv01(price, conv)."
            )
        return self.notional * self.term_years * 1e-4


CONVENTIONS: dict[str, Convention] = {
    "SR3": Convention("USD", "SOFR", "ACT/360", 360, "FOMC", "SR3", 1_000_000, 0.25, 0.005),
    "SR1": Convention("USD", "SOFR", "ACT/360", 360, "FOMC", "SR1", 5_000_000, 1 / 12, 0.0025),
    "FF":  Convention("USD", "EFFR", "ACT/360", 360, "FOMC", "FF", 5_000_000, 1 / 12, 0.0025),
    "SON": Convention("GBP", "SONIA", "ACT/365F", 365, "MPC", "SON", 1_000_000, 0.25, 0.005),
    "ER":  Convention("EUR", "EURIBOR3M", "ACT/360", 360, "ECB", "ER", 1_000_000, 0.25, 0.005),
    "EST": Convention("EUR", "ESTR", "ACT/360", 360, "ECB", "EST", 1_000_000, 0.25, 0.005),
    "TNA": Convention("JPY", "TONA", "ACT/365", 365, "BOJ", "TNA", 100_000_000, 0.25, 0.005),
    "CRA": Convention("CAD", "CORRA", "ACT/365", 365, "BOC", "CRA", 1_000_000, 0.25, 0.005),
    "COA": Convention("CAD", "CORRA", "ACT/365", 365, "BOC", "COA", 3_000_000, 1 / 12, 0.005),
    "IR":  Convention("AUD", "BBSW3M", "ACT/365", 365, "RBA", "IR", 1_000_000, 90 / 365, 0.01,
                      discount_priced=True),
    "ZB":  Convention("NZD", "BKBM3M", "ACT/365", 365, "RBNZ", "ZB", 1_000_000, 90 / 365, 0.01,
                      discount_priced=True),
}


def convention(root: str) -> Convention:
    key = root.upper()
    if key not in CONVENTIONS:
        raise KeyError(
            f"no convention for {root!r}; known roots: {sorted(CONVENTIONS)}. "
            "Add it to CONVENTIONS rather than hardcoding a DV01 at the call site."
        )
    return CONVENTIONS[key]


def year_fraction(start: date, end: date, basis: int) -> float:
    return (end - start).days / basis
