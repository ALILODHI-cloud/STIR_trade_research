import pytest

from lib.stir import conventions as cv
from lib.stir import futures as fut


def test_price_rate_inverse():
    assert fut.price_to_rate(96.25) == pytest.approx(3.75)
    assert fut.rate_to_price(3.75) == pytest.approx(96.25)


def test_spread_sign_convention():
    # front 96.00 (4.00%), back 96.50 (3.50%) -> rate spread +50bp
    assert fut.structure_level([96.00, 96.50], fut.structure_weights("spread")) == pytest.approx(50.0)
    # price space is the negation for a zero-sum weight vector
    assert fut.structure_level([96.00, 96.50], fut.structure_weights("spread"),
                               space="price") == pytest.approx(-50.0)


def test_fly_is_zero_on_a_linear_curve():
    prices = [96.00, 96.25, 96.50]
    assert fut.structure_level(prices, fut.structure_weights("fly")) == pytest.approx(0.0)


def test_fly_picks_up_curvature():
    # rates 4.00 / 3.70 / 3.50; the straight line through the wings puts the
    # body at 3.75, so the body sits 5bp BELOW the line -> fly = +10bp
    prices = [96.00, 96.30, 96.50]
    assert fut.structure_level(prices, fut.structure_weights("fly")) == pytest.approx(10.0)
    # and the sign flips when the body sits above the line
    assert fut.structure_level([96.00, 96.20, 96.50],
                               fut.structure_weights("fly")) == pytest.approx(-10.0)


def test_condor_zero_on_linear_curve():
    prices = [96.00, 96.25, 96.50, 96.75]
    assert fut.structure_level(prices, fut.structure_weights("condor")) == pytest.approx(0.0)


def test_weights_must_align_with_prices():
    with pytest.raises(ValueError):
        fut.structure_level([96.0, 96.5], fut.structure_weights("fly"))


def test_bill_dv01_falls_as_yields_rise():
    conv = cv.convention("IR")
    low = fut.bill_dv01(97.00, conv)   # 3% yield
    high = fut.bill_dv01(92.00, conv)  # 8% yield
    assert low > high > 0
    # magnitude is in the right neighbourhood for a A$1m 90-day bill
    assert 22.0 < low < 25.0


def test_contract_dv01_requires_price_for_bills():
    with pytest.raises(ValueError, match="price-dependent"):
        fut.contract_dv01("IR")
    assert fut.contract_dv01("IR", price=97.0) > 0
    assert fut.contract_dv01("SR3Z6") == pytest.approx(25.0)


def test_dv01_neutral_weights_scale_by_inverse_dv01():
    w = fut.dv01_neutral_weights([25.0, 12.5], [1.0, -1.0])
    assert w[0] == pytest.approx(1.0)
    assert w[1] == pytest.approx(-2.0)


def test_strip_structures_and_roll():
    s = fut.Strip(["SR3Z6", "SR3H7", "SR3M7", "SR3U7"], [96.00, 96.25, 96.40, 96.45])
    assert s.level("SR3Z6", "SR3H7") == pytest.approx(25.0)
    assert s.level("SR3Z6", "SR3H7", "SR3M7") == pytest.approx(10.0)
    assert len(s.sequential_spreads()) == 3
    assert len(s.sequential_flies()) == 2
    # rolling the Z6H7 spread back one contract is undefined off the front
    with pytest.raises(ValueError):
        s.roll_down if False else fut.roll_down(s, ["SR3Z6", "SR3H7"], periods=1)
    r = fut.roll_down(s, ["SR3H7", "SR3M7"], periods=1)
    assert r == pytest.approx(15.0 - 25.0)


def test_strip_rejects_mismatched_inputs():
    with pytest.raises(ValueError):
        fut.Strip(["A", "B"], [96.0])
