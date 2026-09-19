from datetime import date

import pytest

from lib.stir import conventions as cv


def test_imm_dates_are_third_wednesdays():
    assert cv.imm_date(2026, 3) == date(2026, 3, 18)
    assert cv.imm_date(2026, 6) == date(2026, 6, 17)
    assert cv.imm_date(2026, 9) == date(2026, 9, 16)
    assert cv.imm_date(2026, 12) == date(2026, 12, 16)
    for y in range(2020, 2035):
        for m in cv.QUARTERLY_MONTHS:
            d = cv.imm_date(y, m)
            assert d.weekday() == 2 and 15 <= d.day <= 21


def test_month_code_roundtrip():
    for m in range(1, 13):
        assert cv.code_to_month(cv.month_to_code(m)) == m


def test_parse_contract_single_and_double_digit_years():
    ref = date(2026, 9, 19)
    assert cv.parse_contract("SR3Z6", ref) == ("SR3", date(2026, 12, 16))
    assert cv.parse_contract("SR3H7", ref) == ("SR3", date(2027, 3, 17))
    # single digit resolves forward within the decade window, not backward
    assert cv.parse_contract("SR3M8", ref)[1].year == 2028
    assert cv.parse_contract("SR3Z26", ref) == ("SR3", date(2026, 12, 16))


def test_parse_contract_rejects_rubbish():
    with pytest.raises(ValueError):
        cv.parse_contract("NOTACONTRACT")


def test_imm_sequence_is_strictly_increasing_and_future():
    start = date(2026, 9, 19)
    seq = cv.imm_sequence(start, 8)
    assert len(seq) == 8
    assert all(d > start for d in seq)
    assert seq == sorted(seq)


def test_dv01s_match_desk_values():
    assert cv.convention("SR3").dv01 == pytest.approx(25.0)
    assert cv.convention("SR1").dv01 == pytest.approx(41.6667, abs=1e-3)
    assert cv.convention("ER").dv01 == pytest.approx(25.0)
    assert cv.convention("SON").dv01 == pytest.approx(25.0)


def test_discount_priced_contracts_refuse_a_fixed_dv01():
    with pytest.raises(ValueError, match="discount-priced"):
        _ = cv.convention("IR").dv01


def test_unknown_root_is_loud():
    with pytest.raises(KeyError):
        cv.convention("XYZ")
