from datetime import date, timedelta

import pytest

from lib.stir import ois


MEETINGS = [date(2026, 10, 30), date(2026, 12, 11), date(2027, 1, 29), date(2027, 3, 19)]
VAL = date(2026, 9, 21)


def test_flat_path_reprices_to_spot_up_to_compounding():
    r = ois.ois_rate(VAL, VAL + timedelta(days=90), 4.00, {}, basis=360)
    # compounding lifts the simple rate slightly
    assert r > 4.00
    assert r == pytest.approx(4.00, abs=0.02)


def test_step_applies_only_from_its_effective_date():
    path = ois.step_path(VAL, VAL + timedelta(days=30), 4.00, {VAL + timedelta(days=10): -0.25})
    assert path[:10].tolist() == [4.00] * 10
    assert path[10:].tolist() == [3.75] * 20


def test_step_before_window_is_already_in_effect():
    path = ois.step_path(VAL, VAL + timedelta(days=5), 4.00, {date(2026, 1, 1): -0.25})
    assert path.tolist() == [3.75] * 5


def test_bootstrap_recovers_the_path_that_generated_the_quotes():
    """Round trip: build a known step path, price meeting-dated OIS off it,
    bootstrap back, and check we recover the original steps."""
    true_steps = {
        MEETINGS[0]: -0.25,
        MEETINGS[1]: -0.25,
        MEETINGS[2]: 0.0,
        MEETINGS[3]: -0.125,
    }
    spot = 4.00
    quotes = {
        m + timedelta(days=1): ois.ois_rate(VAL, m + timedelta(days=1), spot, true_steps, 360)
        for m in MEETINGS
    }
    curve = ois.bootstrap_steps(VAL, spot, quotes, MEETINGS, basis=360)
    for m, expected in true_steps.items():
        assert curve.steps[m] == pytest.approx(expected, abs=1e-9)


def test_bootstrapped_curve_reprices_its_own_quotes():
    spot = 3.50
    true_steps = {MEETINGS[0]: 0.25, MEETINGS[1]: 0.25, MEETINGS[2]: 0.25, MEETINGS[3]: 0.0}
    quotes = {
        m + timedelta(days=1): ois.ois_rate(VAL, m + timedelta(days=1), spot, true_steps, 360)
        for m in MEETINGS
    }
    curve = ois.bootstrap_steps(VAL, spot, quotes, MEETINGS, basis=360)
    for maturity, quoted in quotes.items():
        assert curve.ois(VAL, maturity) == pytest.approx(quoted, abs=1e-9)


def test_cumulative_and_implied_moves():
    curve = ois.MeetingCurve(VAL, 4.00, 360, {MEETINGS[0]: -0.25, MEETINGS[1]: -0.125})
    assert curve.cumulative()[MEETINGS[1]] == pytest.approx(-0.375)
    assert curve.rate_after(MEETINGS[1]) == pytest.approx(3.625)
    moves = curve.implied_moves(25.0)
    assert moves[MEETINGS[0]] == pytest.approx(-1.0)
    assert moves[MEETINGS[1]] == pytest.approx(-0.5)


def test_steps_from_dated_forwards():
    dated = {MEETINGS[0]: 3.75, MEETINGS[1]: 3.50}
    steps = ois.steps_from_dated_forwards(dated, 4.00)
    assert steps[MEETINGS[0]] == pytest.approx(-0.25)
    assert steps[MEETINGS[1]] == pytest.approx(-0.25)


def test_gap_in_quotes_spreads_the_move_evenly():
    """A quote spanning two unsolved meetings is under-determined, so the move
    is split evenly across them - and the result still reprices the quote."""
    spot = 4.00
    maturity = MEETINGS[1] + timedelta(days=1)
    quotes = {maturity: 3.70}
    curve = ois.bootstrap_steps(VAL, spot, quotes, MEETINGS, basis=360)
    assert curve.steps[MEETINGS[0]] == pytest.approx(curve.steps[MEETINGS[1]])
    assert curve.steps[MEETINGS[0]] < 0
    assert curve.ois(VAL, maturity) == pytest.approx(3.70, abs=1e-9)
    # meetings beyond the last quote are left unsolved, not assumed flat
    assert MEETINGS[2] not in curve.steps


def test_backwards_window_is_rejected():
    with pytest.raises(ValueError):
        ois.ois_rate(VAL, VAL - timedelta(days=1), 4.0, {})
