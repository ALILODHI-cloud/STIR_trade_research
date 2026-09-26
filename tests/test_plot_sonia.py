from pathlib import Path

import pandas as pd
import pytest

from scripts.plot_sonia_jun28_jun27 import calculate_spread, plot_spread


def test_calculate_spread_is_in_rate_space_and_uses_calendar_days():
    dates = pd.to_datetime(["2026-08-20", "2026-08-27", "2026-09-25"])
    history = pd.DataFrame(
        {"SOM27": [96.00, 96.10, 96.20], "SOM28": [96.25, 96.30, 96.35]}, index=dates
    )

    spread = calculate_spread(history, days=30)

    assert list(spread.index) == list(dates[1:])
    assert spread.tolist() == pytest.approx([-20.0, -15.0])
    assert spread.name == "Jun-28 minus Jun-27 SONIA (bp)"


def test_calculate_spread_accepts_canonical_symbols_and_requires_both_legs():
    history = pd.DataFrame(
        {"SONM2027": [96.0], "SONM2028": [96.1]}, index=pd.to_datetime(["2026-09-25"])
    )
    assert calculate_spread(history).iloc[0] == pytest.approx(-10.0)

    with pytest.raises(ValueError, match="Jun-28"):
        calculate_spread(history.drop(columns="SONM2028"))


def test_plot_spread_writes_png(tmp_path: Path):
    spread = pd.Series(
        [-20.0, -15.0], index=pd.to_datetime(["2026-09-24", "2026-09-25"])
    )
    output = tmp_path / "chart.png"

    plot_spread(spread, output)

    assert output.read_bytes().startswith(b"\x89PNG")
