"""Relative-value statistics: z-scores, PCA, hedge ratios, mean reversion."""
from __future__ import annotations

import numpy as np
import pandas as pd


def zscore(series: pd.Series, window: int | None = None, min_periods: int | None = None) -> pd.Series:
    """Z-score of a series. `window=None` uses the full sample."""
    s = series.dropna()
    if window is None:
        return (series - s.mean()) / s.std(ddof=1)
    mp = min_periods or max(20, window // 4)
    mu = series.rolling(window, min_periods=mp).mean()
    sd = series.rolling(window, min_periods=mp).std(ddof=1)
    return (series - mu) / sd


def percentile_rank(series: pd.Series, window: int | None = None) -> pd.Series:
    """Where today's level sits in its own history, 0-100."""
    if window is None:
        return series.rank(pct=True) * 100.0
    return series.rolling(window).apply(lambda x: (x[-1] >= x).mean() * 100.0, raw=True)


def hedge_ratio(y: pd.Series, x: pd.Series, window: int | None = None) -> pd.Series | float:
    """OLS beta of y on x (no intercept on changes; use on differences)."""
    if window is None:
        aligned = pd.concat([y, x], axis=1).dropna()
        yy, xx = aligned.iloc[:, 0], aligned.iloc[:, 1]
        return float((xx @ yy) / (xx @ xx))
    cov = y.rolling(window).cov(x)
    var = x.rolling(window).var()
    return cov / var


def residual(y: pd.Series, x: pd.Series, beta: float | None = None) -> pd.Series:
    """Residual of y after hedging with x. Positive = y rich vs the fit."""
    b = hedge_ratio(y, x) if beta is None else beta
    return y - b * x


def pca_curve(changes: pd.DataFrame, n_components: int = 3):
    """PCA on curve changes.

    Returns (loadings, scores, explained_variance_ratio). `changes` should be
    differences (bp), one column per tenor/contract, not levels.
    """
    df = changes.dropna()
    if df.shape[0] < df.shape[1]:
        raise ValueError(
            f"need more observations ({df.shape[0]}) than series ({df.shape[1]}) for PCA"
        )
    x = df.values - df.values.mean(axis=0)
    u, s, vt = np.linalg.svd(x, full_matrices=False)
    k = min(n_components, vt.shape[0])
    loadings = pd.DataFrame(
        vt[:k].T, index=df.columns, columns=[f"PC{i+1}" for i in range(k)]
    )
    scores = pd.DataFrame(
        (u[:, :k] * s[:k]), index=df.index, columns=[f"PC{i+1}" for i in range(k)]
    )
    evr = (s**2 / np.sum(s**2))[:k]
    return loadings, scores, evr


def pca_residual(changes: pd.DataFrame, n_components: int = 2,
                 cumulative: bool = True) -> pd.DataFrame:
    """Residual of each series after stripping the first N PCs.

    The standard rich/cheap screen: run it on daily changes, cumulate, then
    z-score the result. `cumulative=False` returns the per-observation
    residuals instead.

    Note the mean add-back: PCA is fitted on de-meaned changes, so the column
    means must be restored to the fit. Omitting them leaves each mean in the
    residual, which then compounds into a spurious drift under cumsum.
    """
    df = changes.dropna()
    loadings, scores, _ = pca_curve(df, n_components)
    means = df.mean(axis=0)
    fitted = pd.DataFrame(
        scores.values @ loadings.values.T, index=df.index, columns=df.columns
    ).add(means, axis=1)
    resid = df - fitted
    return resid.cumsum() if cumulative else resid


def half_life(series: pd.Series) -> float:
    """Ornstein-Uhlenbeck half-life in observations. inf if not mean-reverting."""
    s = series.dropna()
    lag, delta = s.shift(1).dropna(), s.diff().dropna()
    idx = lag.index.intersection(delta.index)
    lag, delta = lag.loc[idx], delta.loc[idx]
    x = np.column_stack([np.ones(len(lag)), lag.values])
    beta = np.linalg.lstsq(x, delta.values, rcond=None)[0][1]
    if beta >= 0:
        return float("inf")
    return float(-np.log(2) / np.log(1 + beta))


def rv_screen(levels: pd.DataFrame, window: int = 250) -> pd.DataFrame:
    """One-row-per-structure summary: level, z, percentile, half-life."""
    rows = []
    for col in levels.columns:
        s = levels[col].dropna()
        if s.empty:
            continue
        z = zscore(levels[col], window=window)
        rows.append(
            {
                "structure": col,
                "level": s.iloc[-1],
                "chg_1d": s.diff().iloc[-1] if len(s) > 1 else np.nan,
                "chg_1w": s.diff(5).iloc[-1] if len(s) > 5 else np.nan,
                f"z_{window}d": z.iloc[-1],
                "pctile": percentile_rank(levels[col], window).iloc[-1],
                "half_life_d": half_life(s.tail(window)),
            }
        )
    return pd.DataFrame(rows).set_index("structure")
