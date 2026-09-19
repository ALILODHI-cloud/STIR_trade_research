"""Barchart market-data client for STIR futures strips.

Written to be verifiable without network access: every HTTP call goes through
an injectable session, so the parsing, symbol construction and error handling
are covered by tests that never leave the process.

Two things must be true before this does anything useful, and neither is
something the code can arrange for itself:

  1. `marketdata.websol.barchart.com` must be allowed by the environment's
     network egress policy.
  2. BARCHART_API_KEY must be set in the environment (never committed).

When either is missing the client raises with the specific remedy rather
than returning empty data that would quietly become a wrong answer.

Symbol roots below are CANDIDATES. Barchart's root for each contract is
confirmed at runtime by `probe_roots`, not assumed - getting this wrong
silently returns another market's data.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import pandas as pd

from .conventions import MONTH_CODES, QUARTERLY_MONTHS, imm_date, month_to_code

BASE_URL = "https://marketdata.websol.barchart.com"
HOST = "marketdata.websol.barchart.com"

# Our root -> ordered candidate roots on Barchart. Probed, never trusted.
ROOT_CANDIDATES: dict[str, list[str]] = {
    "SR3": ["SQ", "SR3", "SFR", "SRA"],
    "ER": ["IM", "ER", "FEI"],
    "SON": ["SO", "SON", "SFI", "SA"],
}


class BarchartError(RuntimeError):
    """Base class for all Barchart failures."""


class BarchartUnavailable(BarchartError):
    """The host could not be reached - almost always the egress policy."""


class BarchartAuthError(BarchartError):
    """Missing or rejected API key."""


class BarchartEntitlementError(BarchartError):
    """Key is valid but not entitled to this exchange or symbol."""


def _require_key(api_key: str | None) -> str:
    key = api_key or os.environ.get("BARCHART_API_KEY")
    if not key:
        raise BarchartAuthError(
            "BARCHART_API_KEY is not set. Export it in the environment "
            "(never commit it). Without a key only page scraping is possible, "
            "which is fragile and sits poorly with Barchart's terms."
        )
    return key


def contract_symbol(root: str, year: int, month: int) -> str:
    """Barchart contract symbol, e.g. ('SQ', 2026, 12) -> 'SQZ26'."""
    if not 1 <= month <= 12:
        raise ValueError(f"month out of range: {month}")
    return f"{root}{month_to_code(month)}{year % 100:02d}"


def quarterly_symbols(root: str, start: date, n: int) -> list[str]:
    """The next `n` quarterly contract symbols with expiry after `start`."""
    out, year = [], start.year
    while len(out) < n:
        for m in QUARTERLY_MONTHS:
            # Use the real IMM expiry, not a month heuristic: on 19 Sep the
            # Sep contract (3rd Wednesday, the 16th) has already expired, and
            # a day-of-month rule would wrongly keep it at the strip front.
            if imm_date(year, m) > start:
                out.append(contract_symbol(root, year, m))
                if len(out) == n:
                    break
        year += 1
    return out


@dataclass
class BarchartClient:
    api_key: str | None = None
    base_url: str = BASE_URL
    session: Any = None
    timeout: int = 30
    _calls: list[tuple[str, dict]] = field(default_factory=list, repr=False)

    def _session(self):
        if self.session is not None:
            return self.session
        import requests

        self.session = requests.Session()
        return self.session

    def _get(self, endpoint: str, params: dict) -> dict:
        key = _require_key(self.api_key)
        params = {**params, "apikey": key}
        url = f"{self.base_url}/{endpoint}"
        self._calls.append((endpoint, {k: v for k, v in params.items() if k != "apikey"}))
        try:
            resp = self._session().get(url, params=params, timeout=self.timeout)
        except Exception as exc:  # noqa: BLE001 - classify, then re-raise
            raise BarchartUnavailable(
                f"could not reach {HOST} ({type(exc).__name__}: {exc}).\n"
                f"  This environment's egress policy denies it by default. Add "
                f"{HOST} to the environment's network access settings at "
                f"claude.ai/code. Verified blocked as of 2026-09-19."
            ) from exc

        status = getattr(resp, "status_code", 200)
        if status in (401, 403):
            raise BarchartAuthError(
                f"Barchart rejected the API key (HTTP {status}). Check the key "
                "is current and that the plan covers this endpoint."
            )
        if status >= 400:
            raise BarchartError(f"Barchart returned HTTP {status} for {endpoint}")

        payload = resp.json()
        return self._check_payload(payload, endpoint)

    @staticmethod
    def _check_payload(payload: dict, endpoint: str) -> dict:
        status = payload.get("status") or {}
        code = status.get("code", 200)
        msg = str(status.get("message", ""))
        if code in (401, 403) or "not authorized" in msg.lower():
            raise BarchartEntitlementError(
                f"Barchart says: {msg or 'not authorized'} (code {code}) for "
                f"{endpoint}. The key is valid but this plan is not entitled "
                "to that exchange. ICE products (Euribor, SONIA) are commonly "
                "excluded where CME (SOFR) is included."
            )
        if code >= 400:
            raise BarchartError(f"Barchart error on {endpoint}: {msg} (code {code})")
        return payload

    # ------------------------------------------------------------------ api

    def quote(self, symbols: list[str]) -> pd.DataFrame:
        """Latest quote per symbol. Returns symbol-indexed frame."""
        if not symbols:
            raise ValueError("no symbols requested")
        payload = self._get("getQuote.json", {"symbols": ",".join(symbols)})
        rows = payload.get("results") or []
        if not rows:
            raise BarchartError(f"no quote data returned for {symbols[:4]}")
        df = pd.DataFrame(rows)
        for col in ("lastPrice", "settlement", "close"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if "symbol" in df.columns:
            df = df.set_index("symbol")
        return df

    def history(self, symbol: str, start: date, end: date | None = None,
                max_records: int = 400) -> pd.DataFrame:
        """Daily bars for one contract, date-indexed."""
        params = {
            "symbol": symbol,
            "type": "daily",
            "startDate": start.strftime("%Y%m%d"),
            "maxRecords": max_records,
            "order": "asc",
        }
        if end is not None:
            params["endDate"] = end.strftime("%Y%m%d")
        payload = self._get("getHistory.json", params)
        rows = payload.get("results") or []
        if not rows:
            return pd.DataFrame(columns=["close"], index=pd.DatetimeIndex([], name="date"))
        df = pd.DataFrame(rows)
        if "tradingDay" in df.columns:
            idx = pd.to_datetime(df["tradingDay"], errors="coerce")
        elif "timestamp" in df.columns:
            idx = pd.to_datetime(df["timestamp"], errors="coerce", utc=True).dt.tz_localize(None)
        else:
            raise BarchartError(f"history rows for {symbol} have no date column: {list(df.columns)[:6]}")
        # .to_numpy() is load-bearing: passing the Series directly makes
        # pandas align its RangeIndex against the DatetimeIndex, producing
        # all-NaN prices that dropna() then quietly discards.
        closes = pd.to_numeric(df.get("close"), errors="coerce").to_numpy()
        out = pd.DataFrame({"close": closes}, index=pd.DatetimeIndex(idx, name="date"))
        return out.dropna().sort_index()

    # -------------------------------------------------------------- probing

    def probe_roots(self, our_root: str, reference: date | None = None) -> dict:
        """Find which candidate root actually returns data for `our_root`.

        Returns {'root': <working root or None>, 'tried': {root: outcome}}.
        Run this before any pull - a wrong root returns another market's
        prices without complaining.
        """
        ref = reference or date.today()
        candidates = ROOT_CANDIDATES.get(our_root.upper())
        if not candidates:
            raise KeyError(f"no Barchart candidates registered for {our_root!r}")
        tried: dict[str, str] = {}
        for cand in candidates:
            sym = quarterly_symbols(cand, ref, 1)[0]
            try:
                df = self.quote([sym])
            except (BarchartAuthError, BarchartUnavailable):
                # Not a per-root problem: no key, or the host is unreachable.
                # Retrying every candidate just repeats one message N times.
                raise
            except BarchartEntitlementError as exc:
                tried[cand] = f"not entitled: {exc}"
                continue
            except BarchartError as exc:
                tried[cand] = f"error: {exc}"
                continue
            price = None
            for col in ("settlement", "lastPrice", "close"):
                if col in df.columns and pd.notna(df[col]).any():
                    price = float(df[col].dropna().iloc[0])
                    break
            if price is None:
                tried[cand] = "no price field"
                continue
            if not 80.0 <= price <= 110.0:
                tried[cand] = f"price {price} outside 80-110; not a 100-minus-rate contract"
                continue
            tried[cand] = f"OK ({sym} @ {price})"
            return {"root": cand, "symbol": sym, "price": price, "tried": tried}
        return {"root": None, "tried": tried}

    def strip_history(self, root: str, start: date, n_contracts: int = 12,
                      reference: date | None = None,
                      end: date | None = None) -> pd.DataFrame:
        """Pull `n_contracts` quarterly contracts into one price history frame.

        Columns are Barchart symbols; index is the observation date. This is
        the shape `curves.validate_history` expects.
        """
        ref = reference or date.today()
        symbols = quarterly_symbols(root, ref, n_contracts)
        frames, failed = {}, {}
        for sym in symbols:
            try:
                h = self.history(sym, start, end)
            except BarchartError as exc:
                failed[sym] = str(exc)
                continue
            if not h.empty:
                frames[sym] = h["close"]
        if not frames:
            raise BarchartError(
                f"no history returned for any of {symbols[:4]}... "
                f"First failure: {next(iter(failed.values()), 'empty results')}"
            )
        out = pd.DataFrame(frames).sort_index()
        out.attrs["failed_symbols"] = failed
        return out


def month_code_for(month: int) -> str:
    """Exposed for callers that build symbols by hand."""
    return MONTH_CODES[month - 1]


def default_start_of_year(today: date | None = None) -> date:
    t = today or date.today()
    return date(t.year, 1, 1)


def two_weeks_ago(today: date | None = None) -> date:
    return (today or date.today()) - timedelta(days=14)
