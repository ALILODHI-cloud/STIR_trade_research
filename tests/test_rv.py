import numpy as np
import pandas as pd
import pytest

from lib.stir import rv


@pytest.fixture
def curve_changes():
    rng = np.random.default_rng(0)
    n = 400
    level = rng.normal(0, 4, n)
    slope = rng.normal(0, 2, n)
    cols = {}
    for i, name in enumerate(["c1", "c2", "c3", "c4", "c5"]):
        cols[name] = level + slope * (i - 2) * 0.5 + rng.normal(0, 0.2, n)
    return pd.DataFrame(cols, index=pd.bdate_range("2024-01-01", periods=n))


def test_zscore_full_sample_is_standardised():
    s = pd.Series(np.arange(100, dtype=float))
    z = rv.zscore(s)
    assert z.mean() == pytest.approx(0.0, abs=1e-12)
    assert z.std(ddof=1) == pytest.approx(1.0)


def test_rolling_zscore_flags_a_jump():
    s = pd.Series(np.concatenate([np.zeros(200), [10.0]]))
    s = s + np.random.default_rng(1).normal(0, 0.1, len(s))
    z = rv.zscore(s, window=100)
    assert z.iloc[-1] > 5


def test_hedge_ratio_recovers_a_known_beta():
    rng = np.random.default_rng(2)
    x = pd.Series(rng.normal(0, 1, 500))
    y = 1.7 * x + rng.normal(0, 0.01, 500)
    assert rv.hedge_ratio(y, x) == pytest.approx(1.7, abs=0.01)


def test_pca_first_component_dominates_a_level_driven_curve(curve_changes):
    loadings, scores, evr = rv.pca_curve(curve_changes)
    assert evr[0] > 0.7
    assert loadings.shape == (5, 3)
    # level loading has a consistent sign across the curve
    assert np.all(np.sign(loadings["PC1"]) == np.sign(loadings["PC1"].iloc[0]))


def test_pca_needs_enough_observations():
    df = pd.DataFrame(np.eye(3), columns=list("abc"))
    with pytest.raises(ValueError, match="more observations"):
        rv.pca_curve(df.iloc[:2])


def test_pca_residual_is_small_for_a_two_factor_curve(curve_changes):
    # the fixture is exactly two factors plus 0.2sd noise
    daily = rv.pca_residual(curve_changes, n_components=2, cumulative=False)
    assert daily.std().max() < 0.3


def test_pca_residual_does_not_drift(curve_changes):
    """Regression: omitting the column-mean add-back leaves each series' mean
    in the residual, which compounds into a spurious trend under cumsum."""
    daily = rv.pca_residual(curve_changes, n_components=2, cumulative=False)
    assert daily.mean().abs().max() < 1e-10
    cum = rv.pca_residual(curve_changes, n_components=2)
    # a driftless residual ends near zero relative to a random walk of its own
    # daily vol over the sample
    walk_scale = daily.std().max() * len(daily) ** 0.5
    assert cum.iloc[-1].abs().max() < 4 * walk_scale


def test_half_life_of_white_noise_is_short_and_of_a_walk_is_long():
    rng = np.random.default_rng(3)
    noise = pd.Series(rng.normal(0, 1, 2000))
    walk = pd.Series(np.cumsum(rng.normal(0, 1, 2000)))
    assert rv.half_life(noise) < 5
    assert rv.half_life(walk) > 50


def test_rv_screen_shape(curve_changes):
    levels = curve_changes.cumsum()
    out = rv.rv_screen(levels, window=100)
    assert list(out.index) == list(levels.columns)
    assert "z_100d" in out.columns
