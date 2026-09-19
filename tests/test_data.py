import pandas as pd
import pytest

from lib.stir import data


def test_missing_series_with_no_source_is_explicit():
    with pytest.raises(data.DataUnavailable, match="No local file"):
        data.load_series("NOT_A_SERIES", fetch=False)


def test_known_source_without_fetch_still_fails_clearly():
    with pytest.raises(data.DataUnavailable):
        data.load_series("SOFR", fetch=False)


def test_local_file_is_preferred(tmp_path, monkeypatch):
    f = tmp_path / "TESTSERIES.csv"
    f.write_text("date,value\n2026-09-01,4.25\n2026-09-02,4.26\n")
    monkeypatch.setattr(data, "CACHE", tmp_path)
    monkeypatch.setattr(data, "RAW", tmp_path)
    s = data.load_series("TESTSERIES", fetch=False)
    assert len(s) == 2
    assert s.iloc[-1] == pytest.approx(4.26)
    assert isinstance(s.index, pd.DatetimeIndex)


def test_manual_strip_roundtrip(tmp_path, monkeypatch):
    (tmp_path / "strip.yaml").write_text(
        "asof: 2026-09-18\nroot: SR3\ncontracts:\n  SR3Z6: 96.00\n  SR3H7: 96.25\n"
    )
    monkeypatch.setattr(data, "MANUAL", tmp_path)
    symbols, prices = data.manual_strip("strip")
    assert symbols == ["SR3Z6", "SR3H7"]
    assert prices == [96.00, 96.25]


def test_sources_registry_is_wellformed():
    for key, src in data.SOURCES.items():
        assert src.key == key
        assert src.url.startswith("https://")
        assert src.host in src.url
