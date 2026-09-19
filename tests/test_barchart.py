"""Barchart client tests. No network: a fake session replays canned payloads."""
from datetime import date

import pandas as pd
import pytest

from lib.stir import barchart as bc


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakeSession:
    """Replays payloads by endpoint; records the params it was called with."""

    def __init__(self, by_endpoint, status_code=200, raise_exc=None):
        self.by_endpoint = by_endpoint
        self.status_code = status_code
        self.raise_exc = raise_exc
        self.calls = []

    def get(self, url, params=None, timeout=None):
        if self.raise_exc:
            raise self.raise_exc
        self.calls.append((url, params))
        endpoint = url.rsplit("/", 1)[-1]
        payload = self.by_endpoint.get(endpoint, {"status": {"code": 200}, "results": []})
        if callable(payload):
            payload = payload(params)
        return FakeResponse(payload, self.status_code)


def client(session, key="testkey"):
    return bc.BarchartClient(api_key=key, session=session)


# ----------------------------------------------------------------- symbols


def test_contract_symbol_format():
    assert bc.contract_symbol("SQ", 2026, 12) == "SQZ26"
    assert bc.contract_symbol("IM", 2027, 3) == "IMH27"
    assert bc.contract_symbol("SO", 2028, 9) == "SOU28"


def test_contract_symbol_rejects_bad_month():
    with pytest.raises(ValueError):
        bc.contract_symbol("SQ", 2026, 13)


def test_quarterly_symbols_are_forward_and_quarterly():
    # 19 Sep 2026 is after the Sep IMM date (16th), so Sep must not appear
    syms = bc.quarterly_symbols("SQ", date(2026, 9, 19), 6)
    assert syms == ["SQZ26", "SQH27", "SQM27", "SQU27", "SQZ27", "SQH28"]


def test_quarterly_symbols_keep_the_current_month_before_its_imm_date():
    """Regression: a day-of-month heuristic kept an already-expired contract
    at the front of the strip."""
    assert bc.quarterly_symbols("SQ", date(2026, 9, 10), 1) == ["SQU26"]
    assert bc.quarterly_symbols("SQ", date(2026, 9, 17), 1) == ["SQZ26"]


def test_history_prices_are_not_lost_to_index_alignment():
    """Regression: constructing the frame from a RangeIndex Series while
    passing a DatetimeIndex made pandas align them, NaN every price, and
    return an empty frame with no error."""
    s = FakeSession({"getHistory.json": _hist([
        {"tradingDay": "2026-09-16", "close": "96.10"},
        {"tradingDay": "2026-09-17", "close": "96.12"},
        {"tradingDay": "2026-09-18", "close": "96.15"},
    ])})
    df = client(s).history("SQZ26", date(2026, 9, 1))
    assert len(df) == 3, "prices were dropped"
    assert df["close"].tolist() == pytest.approx([96.10, 96.12, 96.15])


def test_quarterly_symbols_roll_the_year():
    syms = bc.quarterly_symbols("IM", date(2026, 12, 29), 2)
    assert syms == ["IMH27", "IMM27"]


# ------------------------------------------------------------------- auth


def test_missing_key_names_the_env_var(monkeypatch):
    monkeypatch.delenv("BARCHART_API_KEY", raising=False)
    c = bc.BarchartClient(session=FakeSession({}))
    with pytest.raises(bc.BarchartAuthError, match="BARCHART_API_KEY"):
        c.quote(["SQZ26"])


def test_key_from_environment_is_used(monkeypatch):
    monkeypatch.setenv("BARCHART_API_KEY", "fromenv")
    s = FakeSession({"getQuote.json": {"status": {"code": 200},
                                       "results": [{"symbol": "SQZ26", "settlement": 96.0}]}})
    bc.BarchartClient(session=s).quote(["SQZ26"])
    assert s.calls[0][1]["apikey"] == "fromenv"


def test_api_key_is_never_recorded_in_call_log():
    s = FakeSession({"getQuote.json": {"status": {"code": 200},
                                       "results": [{"symbol": "SQZ26", "settlement": 96.0}]}})
    c = client(s)
    c.quote(["SQZ26"])
    assert all("apikey" not in params for _, params in c._calls)


def test_http_401_is_an_auth_error():
    s = FakeSession({"getQuote.json": {}}, status_code=401)
    with pytest.raises(bc.BarchartAuthError):
        client(s).quote(["SQZ26"])


# --------------------------------------------------------------- transport


def test_connection_failure_points_at_the_egress_policy():
    s = FakeSession({}, raise_exc=OSError("proxy CONNECT refused"))
    with pytest.raises(bc.BarchartUnavailable, match="egress policy"):
        client(s).quote(["SQZ26"])


def test_payload_level_entitlement_error_is_distinguished():
    s = FakeSession({"getQuote.json": {"status": {"code": 403, "message": "Not authorized"}}})
    with pytest.raises(bc.BarchartEntitlementError, match="not entitled|not authorized"):
        client(s).quote(["IMZ26"])


def test_entitlement_error_mentions_the_ice_cme_split():
    s = FakeSession({"getQuote.json": {"status": {"code": 403, "message": "Not authorized"}}})
    with pytest.raises(bc.BarchartEntitlementError, match="ICE"):
        client(s).quote(["IMZ26"])


# ------------------------------------------------------------------ quotes


def test_quote_parses_and_indexes_by_symbol():
    s = FakeSession({"getQuote.json": {"status": {"code": 200}, "results": [
        {"symbol": "SQZ26", "settlement": "96.045"},
        {"symbol": "SQH27", "settlement": "96.320"},
    ]}})
    df = client(s).quote(["SQZ26", "SQH27"])
    assert list(df.index) == ["SQZ26", "SQH27"]
    assert df.loc["SQH27", "settlement"] == pytest.approx(96.320)


def test_empty_quote_results_raise_rather_than_return_nothing():
    s = FakeSession({"getQuote.json": {"status": {"code": 200}, "results": []}})
    with pytest.raises(bc.BarchartError, match="no quote data"):
        client(s).quote(["SQZ26"])


def test_quote_requires_symbols():
    with pytest.raises(ValueError):
        client(FakeSession({})).quote([])


# ----------------------------------------------------------------- history


def _hist(rows):
    return {"status": {"code": 200}, "results": rows}


def test_history_parses_trading_day_and_sorts():
    s = FakeSession({"getHistory.json": _hist([
        {"tradingDay": "2026-01-05", "close": "96.10"},
        {"tradingDay": "2026-01-02", "close": "96.00"},
    ])})
    df = client(s).history("SQZ26", date(2026, 1, 1))
    assert list(df.index) == [pd.Timestamp("2026-01-02"), pd.Timestamp("2026-01-05")]
    assert df["close"].iloc[0] == pytest.approx(96.00)


def test_history_empty_returns_empty_frame_not_error():
    s = FakeSession({"getHistory.json": _hist([])})
    df = client(s).history("SQZ26", date(2026, 1, 1))
    assert df.empty
    assert isinstance(df.index, pd.DatetimeIndex)


def test_history_without_a_date_column_is_loud():
    s = FakeSession({"getHistory.json": _hist([{"close": "96.10"}])})
    with pytest.raises(bc.BarchartError, match="no date column"):
        client(s).history("SQZ26", date(2026, 1, 1))


def test_history_passes_the_date_window():
    s = FakeSession({"getHistory.json": _hist([{"tradingDay": "2026-01-02", "close": "96.0"}])})
    client(s).history("SQZ26", date(2026, 1, 1), date(2026, 9, 19))
    params = s.calls[0][1]
    assert params["startDate"] == "20260101"
    assert params["endDate"] == "20260919"
    assert params["type"] == "daily"


# ------------------------------------------------------------------ probing


def test_probe_finds_the_first_root_returning_a_sane_price():
    def quote_payload(params):
        sym = params["symbols"]
        if sym.startswith("SQ"):
            return {"status": {"code": 200}, "results": [{"symbol": sym, "settlement": 96.05}]}
        return {"status": {"code": 403, "message": "Not authorized"}}

    s = FakeSession({"getQuote.json": quote_payload})
    out = client(s).probe_roots("SR3", reference=date(2026, 9, 19))
    assert out["root"] == "SQ"
    assert out["price"] == pytest.approx(96.05)


def test_probe_rejects_a_root_whose_price_is_not_a_futures_price():
    """A wrong root can return a real number from another market. A 100-minus-
    rate contract must sit in 80-110; anything else is a different instrument."""
    def quote_payload(params):
        sym = params["symbols"]
        if sym.startswith("SQ"):
            return {"status": {"code": 200}, "results": [{"symbol": sym, "settlement": 4210.5}]}
        return {"status": {"code": 200}, "results": [{"symbol": sym, "settlement": 96.05}]}

    s = FakeSession({"getQuote.json": quote_payload})
    out = client(s).probe_roots("SR3", reference=date(2026, 9, 19))
    assert out["root"] == "SR3"
    assert "outside 80-110" in out["tried"]["SQ"]


def test_probe_reports_all_failures_when_nothing_works():
    s = FakeSession({"getQuote.json": {"status": {"code": 403, "message": "Not authorized"}}})
    out = client(s).probe_roots("ER", reference=date(2026, 9, 19))
    assert out["root"] is None
    assert set(out["tried"]) == set(bc.ROOT_CANDIDATES["ER"])


def test_probe_unknown_root_is_loud():
    with pytest.raises(KeyError):
        client(FakeSession({})).probe_roots("TNA")


# ------------------------------------------------------------ strip history


def test_strip_history_assembles_a_frame_curves_can_validate():
    from lib.stir import curves

    def hist_payload(params):
        sym = params["symbol"]
        base = {"SQZ26": 96.00, "SQH27": 96.25, "SQM27": 96.40}.get(sym)
        if base is None:
            return {"status": {"code": 200}, "results": []}
        return _hist([
            {"tradingDay": "2026-09-17", "close": base},
            {"tradingDay": "2026-09-18", "close": base + 0.01},
        ])

    s = FakeSession({"getHistory.json": hist_payload})
    df = client(s).strip_history("SQ", date(2026, 1, 1), n_contracts=3,
                                 reference=date(2026, 9, 19))
    assert list(df.columns) == ["SQZ26", "SQH27", "SQM27"]
    assert len(df) == 2
    # the frame must satisfy the analysis layer's contract
    curves.validate_history(df)


def test_strip_history_raises_when_every_symbol_is_empty():
    s = FakeSession({"getHistory.json": _hist([])})
    with pytest.raises(bc.BarchartError, match="no history returned"):
        client(s).strip_history("SQ", date(2026, 1, 1), n_contracts=2,
                                reference=date(2026, 9, 19))


def test_strip_history_records_partial_failures_rather_than_hiding_them():
    def hist_payload(params):
        if params["symbol"] == "SQZ26":
            return _hist([{"tradingDay": "2026-09-18", "close": 96.0}])
        return {"status": {"code": 403, "message": "Not authorized"}}

    s = FakeSession({"getHistory.json": hist_payload})
    df = client(s).strip_history("SQ", date(2026, 1, 1), n_contracts=3,
                                 reference=date(2026, 9, 19))
    assert list(df.columns) == ["SQZ26"]
    assert set(df.attrs["failed_symbols"]) == {"SQH27", "SQM27"}


def test_probe_stops_immediately_on_a_missing_key(monkeypatch):
    """Regression: a missing key is not a per-root failure. Probing every
    candidate repeated one message four times and buried the real cause."""
    monkeypatch.delenv("BARCHART_API_KEY", raising=False)
    c = bc.BarchartClient(session=FakeSession({}))
    with pytest.raises(bc.BarchartAuthError):
        c.probe_roots("SR3", reference=date(2026, 9, 19))
    assert len(c._calls) <= 1


def test_probe_stops_immediately_when_the_host_is_unreachable():
    s = FakeSession({}, raise_exc=OSError("Tunnel connection failed: 403 Forbidden"))
    with pytest.raises(bc.BarchartUnavailable):
        client(s).probe_roots("ER", reference=date(2026, 9, 19))
