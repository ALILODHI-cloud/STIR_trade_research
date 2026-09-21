#!/usr/bin/env python3
"""Build the exhaustive GBP/EUR peak buildup/reversal RV workbook.

The four primitive series are economic rate magnitudes in basis points:

    GB_BUILD = SONIA U27 - SONIA Z26
    GB_CUT   = SONIA U27 - SONIA Z28
    EU_BUILD = Euribor U27 - Euribor Z26
    EU_CUT   = Euribor U27 - Euribor Z28

Thus positive BUILD means hikes into the Sep-27 peak and positive CUT means
cuts from the Sep-27 peak to Dec-28.  A raw futures-price U27-Z28 spread has
the opposite sign to CUT.  The sample starts at the first common session on
or after 1 March 2026.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.comments import Comment
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "cache" / "stir_curves" / "panel.csv"
OUTPUT = ROOT / "research" / "peak_rv_universe_2026-09-18.xlsx"
SAMPLE_START = pd.Timestamp("2026-03-01")

PRIMITIVES = ["GB_BUILD", "GB_CUT", "EU_BUILD", "EU_CUT"]
LABELS = {
    "GB_BUILD": "SONIA buildup: U27 − Z26",
    "GB_CUT": "SONIA reversal: U27 − Z28",
    "EU_BUILD": "Euribor buildup: U27 − Z26",
    "EU_CUT": "Euribor reversal: U27 − Z28",
}
DESCRIPTIONS = {
    "GB_BUILD": "Cumulative SONIA rate rise from Dec-26 to the Sep-27 peak",
    "GB_CUT": "Cumulative SONIA rate decline from the Sep-27 peak to Dec-28",
    "EU_BUILD": "Cumulative Euribor rate rise from Dec-26 to the Sep-27 peak",
    "EU_CUT": "Cumulative Euribor rate decline from the Sep-27 peak to Dec-28",
}
SYMBOLS = {
    "GB_Z26": "J8Z26",
    "GB_U27": "J8U27",
    "GB_Z28": "J8Z28",
    "EU_Z26": "IMZ26",
    "EU_U27": "IMU27",
    "EU_Z28": "IMZ28",
}

CONTRACT_ORDER = ["GB_Z26", "GB_U27", "GB_Z28", "EU_Z26", "EU_U27", "EU_Z28"]

NAVY = "14213D"
BLUE = "247BA0"
PALE_BLUE = "DDEBF7"
GREEN = "D9EAD3"
RED = "F4CCCC"
AMBER = "FCE5CD"
GREY = "E7E6E6"
WHITE = "FFFFFF"
BLACK = "000000"
THIN_GREY = Side(style="thin", color="D9E1F2")


@dataclass
class Stat:
    n: int
    start: float
    current: float
    change: float
    mean: float
    median: float
    std: float
    zscore: float
    minimum: float
    min_date: str
    maximum: float
    max_date: str
    percentile: float
    tail_percentile: float
    distance_to_min: float
    distance_to_max: float
    change_5d: float
    change_20d: float
    daily_vol: float
    flag: str
    mr_action: str
    pnl_to_mean: float


def clean_series(s: pd.Series) -> pd.Series:
    return s.replace([np.inf, -np.inf], np.nan).dropna()


def stats(s: pd.Series) -> Stat:
    s = clean_series(s)
    current = float(s.iloc[-1])
    start = float(s.iloc[0])
    std = float(s.std(ddof=1))
    percentile = float((s <= current).mean() * 100)
    tail = min(percentile, 100 - percentile)
    if percentile >= 95:
        flag = "EXTREME HIGH"
        action = "SHORT level / receive positive-rate weights"
    elif percentile <= 5:
        flag = "EXTREME LOW"
        action = "LONG level / pay positive-rate weights"
    elif percentile >= 90:
        flag = "WATCH HIGH"
        action = "Lean SHORT"
    elif percentile <= 10:
        flag = "WATCH LOW"
        action = "Lean LONG"
    else:
        flag = "NEUTRAL"
        action = "No tail signal"
    return Stat(
        n=len(s),
        start=start,
        current=current,
        change=current - start,
        mean=float(s.mean()),
        median=float(s.median()),
        std=std,
        zscore=(current - float(s.mean())) / std if std else np.nan,
        minimum=float(s.min()),
        min_date=str(s.idxmin().date()),
        maximum=float(s.max()),
        max_date=str(s.idxmax().date()),
        percentile=percentile,
        tail_percentile=tail,
        distance_to_min=current - float(s.min()),
        distance_to_max=float(s.max()) - current,
        change_5d=current - float(s.iloc[-6]) if len(s) > 5 else np.nan,
        change_20d=current - float(s.iloc[-21]) if len(s) > 20 else np.nan,
        daily_vol=float(s.diff().std(ddof=1)),
        flag=flag,
        mr_action=action,
        pnl_to_mean=abs(current - float(s.mean())),
    )


def stat_row(name: str, label: str, s: pd.Series, definition: str = "") -> dict:
    st = stats(s)
    return {
        "id": name,
        "label": label,
        "definition": definition,
        "n": st.n,
        "start_bp": st.start,
        "current_bp": st.current,
        "change_since_start_bp": st.change,
        "mean_bp": st.mean,
        "median_bp": st.median,
        "std_bp": st.std,
        "zscore": st.zscore,
        "min_bp": st.minimum,
        "min_date": st.min_date,
        "max_bp": st.maximum,
        "max_date": st.max_date,
        "percentile": st.percentile,
        "tail_percentile": st.tail_percentile,
        "distance_to_min_bp": st.distance_to_min,
        "distance_to_max_bp": st.distance_to_max,
        "change_5d_bp": st.change_5d,
        "change_20d_bp": st.change_20d,
        "daily_vol_bp": st.daily_vol,
        "flag": st.flag,
        "mean_reversion_action": st.mr_action,
        "pnl_to_mean_bp": st.pnl_to_mean,
    }


def hedge_beta(y: pd.Series, x: pd.Series) -> float:
    a = pd.concat([y.diff(), x.diff()], axis=1).dropna()
    yy, xx = a.iloc[:, 0], a.iloc[:, 1]
    denom = float(xx @ xx)
    return float((xx @ yy) / denom) if denom else np.nan


def expression(coeffs: dict[str, int]) -> str:
    parts: list[str] = []
    for key in PRIMITIVES:
        c = coeffs[key]
        if not c:
            continue
        sign = "+" if c > 0 else "−"
        mag = "" if abs(c) == 1 else str(abs(c))
        term = f"{mag}{key}"
        if not parts:
            parts.append(term if c > 0 else f"−{term}")
        else:
            parts.append(f"{sign} {term}")
    return " ".join(parts)


def primitive_to_contract_weights(coeffs: dict[str, float]) -> dict[str, float]:
    return {
        "GB_Z26": -coeffs.get("GB_BUILD", 0),
        "GB_U27": coeffs.get("GB_BUILD", 0) + coeffs.get("GB_CUT", 0),
        "GB_Z28": -coeffs.get("GB_CUT", 0),
        "EU_Z26": -coeffs.get("EU_BUILD", 0),
        "EU_U27": coeffs.get("EU_BUILD", 0) + coeffs.get("EU_CUT", 0),
        "EU_Z28": -coeffs.get("EU_CUT", 0),
    }


def leg_text(weights: dict[str, float], direction: str) -> str:
    """Trading legs for LONG or SHORT of a rate-space structure."""
    legs: list[str] = []
    mult = 1 if direction == "LONG" else -1
    # Position rate P&L coefficient is + for pay, - for receive.
    for key in CONTRACT_ORDER:
        pnl_weight = mult * weights[key]
        if abs(pnl_weight) < 1e-12:
            continue
        action = "PAY" if pnl_weight > 0 else "RECEIVE"
        size = abs(pnl_weight)
        size_txt = "" if np.isclose(size, 1) else f"{size:g}× "
        legs.append(f"{action} {size_txt}{SYMBOLS[key]}")
    return "; ".join(legs)


def canonical_series(x: pd.DataFrame) -> dict[str, tuple[pd.Series, str, str]]:
    return {
        "GB_PEAK_CURV": (
            x.GB_BUILD + x.GB_CUT,
            "2× SONIA U27 − SONIA Z26 − SONIA Z28",
            "Peak richness to both wings; true peak fade is SHORT this level",
        ),
        "EU_PEAK_CURV": (
            x.EU_BUILD + x.EU_CUT,
            "2× Euribor U27 − Euribor Z26 − Euribor Z28",
            "Peak richness to both wings; true peak fade is SHORT this level",
        ),
        "REL_BUILD": (
            x.GB_BUILD - x.EU_BUILD,
            "GB_BUILD − EU_BUILD",
            "BoE Dec-26→peak extension relative to ECB",
        ),
        "REL_CUT": (
            x.GB_CUT - x.EU_CUT,
            "GB_CUT − EU_CUT",
            "BoE post-peak reversal magnitude relative to ECB",
        ),
        "REL_PEAK_CURV": (
            (x.GB_BUILD + x.GB_CUT) - (x.EU_BUILD + x.EU_CUT),
            "GB_PEAK_CURV − EU_PEAK_CURV",
            "BoE peak curvature relative to ECB peak curvature",
        ),
        "GB_FRONT_BACK": (
            x.GB_BUILD - x.GB_CUT,
            "SONIA Z28 − SONIA Z26",
            "Peak cancels: this is front-to-back slope, not a peak trade",
        ),
        "EU_FRONT_BACK": (
            x.EU_BUILD - x.EU_CUT,
            "Euribor Z28 − Euribor Z26",
            "Peak cancels: this is front-to-back slope, not a peak trade",
        ),
        "REL_FRONT_BACK": (
            (x.GB_BUILD - x.GB_CUT) - (x.EU_BUILD - x.EU_CUT),
            "GB_FRONT_BACK − EU_FRONT_BACK",
            "Relative Dec-26→Dec-28 slope",
        ),
        "GB_BUILD_MINUS_EU_CUT": (
            x.GB_BUILD - x.EU_CUT,
            "GB_BUILD − EU_CUT",
            "Mixed-horizon cross; user's example, but factors need not hedge",
        ),
        "GB_CUT_MINUS_EU_BUILD": (
            x.GB_CUT - x.EU_BUILD,
            "GB_CUT − EU_BUILD",
            "Mixed-horizon cross; factors need not hedge",
        ),
    }


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = pd.read_csv(PANEL, parse_dates=["date"])
    rates = (
        panel[
            panel.curve.isin(["SONIA", "EURIBOR"])
            & panel.contract.isin(["Z26", "U27", "Z28"])
        ]
        .pivot_table(index="date", columns=["curve", "contract"], values="rate")
        .sort_index()
    )
    rates = rates.loc[SAMPLE_START:].dropna()
    raw = pd.DataFrame(
        {
            "GB_Z26_rate_pct": rates["SONIA", "Z26"],
            "GB_U27_rate_pct": rates["SONIA", "U27"],
            "GB_Z28_rate_pct": rates["SONIA", "Z28"],
            "EU_Z26_rate_pct": rates["EURIBOR", "Z26"],
            "EU_U27_rate_pct": rates["EURIBOR", "U27"],
            "EU_Z28_rate_pct": rates["EURIBOR", "Z28"],
        }
    )
    x = pd.DataFrame(
        {
            "GB_BUILD": (rates["SONIA", "U27"] - rates["SONIA", "Z26"]) * 100,
            "GB_CUT": (rates["SONIA", "U27"] - rates["SONIA", "Z28"]) * 100,
            "EU_BUILD": (rates["EURIBOR", "U27"] - rates["EURIBOR", "Z26"]) * 100,
            "EU_CUT": (rates["EURIBOR", "U27"] - rates["EURIBOR", "Z28"]) * 100,
        }
    )
    return raw, x


def build_tables(x: pd.DataFrame):
    outright = pd.DataFrame(
        [
            stat_row(key, LABELS[key], x[key], DESCRIPTIONS[key])
            for key in PRIMITIVES
        ]
    )
    outright.insert(
        outright.columns.get_loc("current_bp") + 1,
        "equivalent_futures_price_spread_bp",
        -outright["current_bp"],
    )
    outright.insert(
        outright.columns.get_loc("percentile") + 1,
        "futures_price_percentile",
        100 - outright["percentile"],
    )

    ordered_rows = []
    for y_name in PRIMITIVES:
        for x_name in PRIMITIVES:
            if y_name == x_name:
                continue
            spread = x[y_name] - x[x_name]
            row = stat_row(
                f"{y_name}_MINUS_{x_name}",
                f"{LABELS[y_name]} minus {LABELS[x_name]}",
                spread,
                f"{y_name} − {x_name}",
            )
            corr = float(x[y_name].diff().corr(x[x_name].diff()))
            b = hedge_beta(x[y_name], x[x_name])
            residual = x[y_name] - b * x[x_name]
            rst = stats(residual)
            row.update(
                {
                    "change_corr": corr,
                    "change_r_squared": corr**2,
                    "change_beta_y_on_x": b,
                    "beta_adjusted_current_bp": float(residual.iloc[-1]),
                    "beta_adjusted_percentile": rst.percentile,
                    "beta_adjusted_zscore": rst.zscore,
                    "inverse_id": f"{x_name}_MINUS_{y_name}",
                    "hedge_quality": (
                        "HIGH" if abs(corr) >= 0.75 else "MEDIUM" if abs(corr) >= 0.5 else "LOW"
                    ),
                }
            )
            ordered_rows.append(row)
    ordered = pd.DataFrame(ordered_rows)

    unique_rows = []
    sum_rows = []
    for i, left in enumerate(PRIMITIVES):
        for right in PRIMITIVES[i + 1 :]:
            unique_rows.append(
                {
                    **stat_row(
                        f"{left}_MINUS_{right}",
                        f"{left} − {right}",
                        x[left] - x[right],
                        f"Unique pair difference: {LABELS[left]} minus {LABELS[right]}",
                    ),
                    "change_corr": float(x[left].diff().corr(x[right].diff())),
                    "change_beta_left_on_right": hedge_beta(x[left], x[right]),
                }
            )
            sum_rows.append(
                stat_row(
                    f"{left}_PLUS_{right}",
                    f"{left} + {right}",
                    x[left] + x[right],
                    f"Pair sum: {LABELS[left]} plus {LABELS[right]}",
                )
            )
    unique = pd.DataFrame(unique_rows)
    pair_sums = pd.DataFrame(sum_rows)

    ratio_rows = []
    for numerator in PRIMITIVES:
        for denominator in PRIMITIVES:
            if numerator == denominator:
                continue
            ratio = x[numerator] / x[denominator]
            crosses = bool(
                x[denominator].min() <= 0 <= x[denominator].max()
            )
            row = stat_row(
                f"{numerator}_DIV_{denominator}",
                f"{numerator} / {denominator}",
                ratio,
                "Dimensionless ratio; use only when denominator is safely away from zero",
            )
            row["denominator_crosses_zero"] = crosses
            row["reliability"] = (
                "UNSTABLE — denominator crosses zero in sample"
                if crosses
                else "Usable with caution"
            )
            ratio_rows.append(row)
    ratios = pd.DataFrame(ratio_rows)
    ratios = ratios.rename(
        columns={
            "start_bp": "start_ratio",
            "current_bp": "current_ratio",
            "change_since_start_bp": "change_since_start_ratio",
            "mean_bp": "mean_ratio",
            "median_bp": "median_ratio",
            "std_bp": "std_ratio",
            "min_bp": "min_ratio",
            "max_bp": "max_ratio",
            "distance_to_min_bp": "distance_to_min_ratio",
            "distance_to_max_bp": "distance_to_max_ratio",
            "change_5d_bp": "change_5d_ratio",
            "change_20d_bp": "change_20d_ratio",
            "daily_vol_bp": "daily_vol_ratio",
            "pnl_to_mean_bp": "distance_to_mean_ratio",
        }
    )

    canonical_map = canonical_series(x)
    canonical = pd.DataFrame(
        [
            stat_row(name, description, series, formula)
            for name, (series, formula, description) in canonical_map.items()
        ]
    )

    # Every {-1, 0, +1} linear combination, unique up to global sign.
    # There are (3^4-1)/2 = 40 combinations, including the 4 primitives.
    seen: set[tuple[int, ...]] = set()
    combo_rows = []
    for raw_coeffs in product([-1, 0, 1], repeat=4):
        if not any(raw_coeffs):
            continue
        first = next(c for c in raw_coeffs if c)
        coeff_tuple = raw_coeffs if first > 0 else tuple(-c for c in raw_coeffs)
        if coeff_tuple in seen:
            continue
        seen.add(coeff_tuple)
        coeffs = dict(zip(PRIMITIVES, coeff_tuple))
        series = sum(coeffs[k] * x[k] for k in PRIMITIVES)
        st = stats(series)
        weights = primitive_to_contract_weights(coeffs)
        direction = "SHORT" if st.percentile >= 50 else "LONG"
        row = stat_row(
            f"COMBO_{len(combo_rows)+1:02d}",
            expression(coeffs),
            series,
            "Unique ±1/0 linear combination; inverse represented by trade direction",
        )
        row = {
            "combo_id": row.pop("id"),
            "expression": row.pop("label"),
            **{f"coef_{k}": coeffs[k] for k in PRIMITIVES},
            "primitive_leg_count": sum(c != 0 for c in coeff_tuple),
            "gross_primitive_units": sum(abs(c) for c in coeff_tuple),
            **row,
            "mr_trade_direction": direction,
            "mr_trade_legs": leg_text(weights, direction),
            "contract_rate_weights": ", ".join(
                f"{SYMBOLS[k]} {v:+g}" for k, v in weights.items() if v
            ),
        }
        combo_rows.append(row)
    combinations = pd.DataFrame(combo_rows).sort_values(
        ["tail_percentile", "zscore"], key=lambda s: abs(s) if s.name == "zscore" else s
    )

    corr = x.diff().corr()
    beta = pd.DataFrame(index=PRIMITIVES, columns=PRIMITIVES, dtype=float)
    for y_name in PRIMITIVES:
        for x_name in PRIMITIVES:
            beta.loc[y_name, x_name] = 1.0 if y_name == x_name else hedge_beta(
                x[y_name], x[x_name]
            )

    return outright, ordered, unique, pair_sums, ratios, canonical, combinations, corr, beta


def candidate_table(x: pd.DataFrame, canonical: pd.DataFrame) -> pd.DataFrame:
    c = canonical.set_index("id")
    gb_curv = x.GB_BUILD + x.GB_CUT
    eu_curv = x.EU_BUILD + x.EU_CUT
    # Use a SONIA U27 proxy reconstructed from primitive changes only for the
    # candidate stress?  The exact U27 daily changes are not in x, so the
    # caller later supplies the observed results in explanatory text.  Here
    # all-day structure-change correlations are fully reproducible from x.
    build_corr_aug = float(
        x.GB_BUILD.diff().loc["2026-08-01":].corr(
            x.EU_BUILD.diff().loc["2026-08-01":]
        )
    )
    curv_corr_aug = float(
        gb_curv.diff().loc["2026-08-01":].corr(
            eu_curv.diff().loc["2026-08-01":]
        )
    )
    mixed_corr = float(
        x.GB_BUILD.diff().corr(x.EU_CUT.diff())
    )
    rows = [
        {
            "rank": 1,
            "candidate": "Short GBP peak curvature",
            "structure_id": "GB_PEAK_CURV",
            "current_bp": c.loc["GB_PEAK_CURV", "current_bp"],
            "percentile": c.loc["GB_PEAK_CURV", "percentile"],
            "zscore": c.loc["GB_PEAK_CURV", "zscore"],
            "trade_legs": "RECEIVE 2× J8U27; PAY J8Z26; PAY J8Z28",
            "what_it_is": "Direct fade of SONIA Sep-27 richness to both front and belly wings",
            "why_now": "Highest level since 2-Mar; +78.5 bp versus +14.8 mean",
            "main_risk": "Not a selloff hedge: another BoE path-extension shock sharpens the peak further",
            "hedge_diagnostic": "Absolute curvature fade; no cross-market hedge",
            "assessment": "BEST DIRECT BOE PEAK FADE",
        },
        {
            "rank": 2,
            "candidate": "Short GBP peak curvature vs EUR peak curvature",
            "structure_id": "REL_PEAK_CURV",
            "current_bp": c.loc["REL_PEAK_CURV", "current_bp"],
            "percentile": c.loc["REL_PEAK_CURV", "percentile"],
            "zscore": c.loc["REL_PEAK_CURV", "zscore"],
            "trade_legs": (
                "RECEIVE 2× J8U27; PAY J8Z26/J8Z28; "
                "PAY 2× IMU27; RECEIVE IMZ26/IMZ28"
            ),
            "what_it_is": "Fade BoE peak curvature relative to the same ECB curvature",
            "why_now": "Relative curvature +12 bp, 98.6th percentile; corresponding cut differential is not extreme",
            "main_risk": "Different policy-cycle timing can sustain positive GBP curvature",
            "hedge_diagnostic": f"GBP/EUR curvature daily-change correlation since Aug: {curv_corr_aug:.2f}",
            "assessment": "BEST CROSS-MARKET RV",
        },
        {
            "rank": 3,
            "candidate": "Short GBP buildup vs long EUR buildup",
            "structure_id": "REL_BUILD",
            "current_bp": c.loc["REL_BUILD", "current_bp"],
            "percentile": c.loc["REL_BUILD", "percentile"],
            "zscore": c.loc["REL_BUILD", "zscore"],
            "trade_legs": (
                "RECEIVE J8U27; PAY J8Z26; "
                "PAY IMU27; RECEIVE IMZ26"
            ),
            "what_it_is": "The Dec-26→Sep-27 curve box discussed with the user",
            "why_now": "+9.5 bp, 99.3rd percentile; buildup daily changes correlate strongly across markets",
            "main_risk": "ECB already delivered 50 bp in 2026; positive box partly reflects asynchronous cycles",
            "hedge_diagnostic": f"GBP/EUR buildup daily-change correlation since Aug: {build_corr_aug:.2f}",
            "assessment": "GOOD HEDGE, USE CONSERVATIVE TARGET",
        },
        {
            "rank": 4,
            "candidate": "Short both GBP and EUR peak curvatures",
            "structure_id": "GB_AND_EU_PEAK_CURV",
            "current_bp": float(
                (x.GB_BUILD + x.GB_CUT + x.EU_BUILD + x.EU_CUT).iloc[-1]
            ),
            "percentile": stats(
                x.GB_BUILD + x.GB_CUT + x.EU_BUILD + x.EU_CUT
            ).percentile,
            "zscore": stats(
                x.GB_BUILD + x.GB_CUT + x.EU_BUILD + x.EU_CUT
            ).zscore,
            "trade_legs": (
                "RECEIVE 2× J8U27 and 2× IMU27; "
                "PAY each market's Z26 and Z28 wings"
            ),
            "what_it_is": "Country-neutral fade of the common war/hawkish peak-curvature factor",
            "why_now": "Both absolute peak curvatures are ~3.4 standard deviations above March means",
            "main_risk": "Concentrated short-hawkish-curvature exposure in both markets; no country diversification",
            "hedge_diagnostic": "Adds common curvature exposure rather than hedging it",
            "assessment": "COMMON-FACTOR FADE",
        },
        {
            "rank": 5,
            "candidate": "GBP buildup minus EUR reversal",
            "structure_id": "GB_BUILD_MINUS_EU_CUT",
            "current_bp": c.loc["GB_BUILD_MINUS_EU_CUT", "current_bp"],
            "percentile": c.loc["GB_BUILD_MINUS_EU_CUT", "percentile"],
            "zscore": c.loc["GB_BUILD_MINUS_EU_CUT", "zscore"],
            "trade_legs": "Statistically short the +50 bp difference",
            "what_it_is": "User's mixed example: UK buildup compared with EUR cuts",
            "why_now": "At the March-sample maximum",
            "main_risk": "Daily-change correlation is near zero; subtraction does not create a hedge",
            "hedge_diagnostic": f"GBP buildup / EUR cut daily-change correlation: {mixed_corr:.2f}",
            "assessment": "EXTREME BUT REJECT AS PRIMARY RV",
        },
        {
            "rank": 6,
            "candidate": "Relative post-peak reversal",
            "structure_id": "REL_CUT",
            "current_bp": c.loc["REL_CUT", "current_bp"],
            "percentile": c.loc["REL_CUT", "percentile"],
            "zscore": c.loc["REL_CUT", "zscore"],
            "trade_legs": "No trade at current valuation",
            "what_it_is": "SONIA cut magnitude minus Euribor cut magnitude",
            "why_now": "It is not extreme: +2.5 bp and near the middle of the March distribution",
            "main_risk": "Forcing a trade where corresponding strips are already aligned",
            "hedge_diagnostic": f"GBP/EUR cut daily-change correlation: {x.GB_CUT.diff().corr(x.EU_CUT.diff()):.2f}",
            "assessment": "NO RELATIVE DISLOCATION",
        },
    ]
    return pd.DataFrame(rows)


def write_dataframe(ws, df: pd.DataFrame, start_row: int = 1, start_col: int = 1):
    for j, col in enumerate(df.columns, start_col):
        cell = ws.cell(start_row, j, col)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.font = Font(color=WHITE, bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = Border(bottom=THIN_GREY)
    for i, row in enumerate(df.itertuples(index=False, name=None), start_row + 1):
        for j, value in enumerate(row, start_col):
            if pd.isna(value):
                value = None
            elif isinstance(value, pd.Timestamp):
                value = value.to_pydatetime()
            elif isinstance(value, np.generic):
                value = value.item()
            cell = ws.cell(i, j, value)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = Border(bottom=THIN_GREY)
            if i % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="F7F9FC")
    return start_row + len(df)


def style_table_sheet(ws, df: pd.DataFrame, freeze: str = "A2"):
    ws.freeze_panes = freeze
    ws.auto_filter.ref = f"A1:{get_column_letter(len(df.columns))}{len(df)+1}"
    ws.row_dimensions[1].height = 34
    for idx, col in enumerate(df.columns, 1):
        values = [str(col)] + [str(v) for v in df[col].head(100).dropna()]
        width = min(max(len(v) for v in values) + 2, 48)
        if col in {"definition", "label", "trade_legs", "what_it_is", "why_now",
                   "main_risk", "contract_rate_weights", "mr_trade_legs"}:
            width = 42
        ws.column_dimensions[get_column_letter(idx)].width = width
        if any(
            token in col
            for token in ["_bp", "zscore", "percentile", "beta", "corr", "r_squared", "vol"]
        ):
            for row in range(2, len(df) + 2):
                ws.cell(row, idx).number_format = "0.00"

    if "percentile" in df.columns:
        col = get_column_letter(df.columns.get_loc("percentile") + 1)
        ws.conditional_formatting.add(
            f"{col}2:{col}{len(df)+1}",
            ColorScaleRule(
                start_type="num", start_value=0, start_color="63BE7B",
                mid_type="num", mid_value=50, mid_color="FFEB84",
                end_type="num", end_value=100, end_color="F8696B",
            ),
        )
    if "zscore" in df.columns:
        col = get_column_letter(df.columns.get_loc("zscore") + 1)
        ws.conditional_formatting.add(
            f"{col}2:{col}{len(df)+1}",
            ColorScaleRule(
                start_type="num", start_value=-3, start_color="63BE7B",
                mid_type="num", mid_value=0, mid_color="FFEB84",
                end_type="num", end_value=3, end_color="F8696B",
            ),
        )
    if "flag" in df.columns:
        c = df.columns.get_loc("flag") + 1
        for r in range(2, len(df) + 2):
            value = ws.cell(r, c).value or ""
            if "EXTREME" in value:
                ws.cell(r, c).fill = PatternFill("solid", fgColor=RED)
                ws.cell(r, c).font = Font(bold=True)
            elif "WATCH" in value:
                ws.cell(r, c).fill = PatternFill("solid", fgColor=AMBER)


def add_readme(wb: Workbook, asof: str, sample_first: str, n: int):
    ws = wb.active
    ws.title = "README"
    ws.sheet_view.showGridLines = False
    ws["A1"] = "GBP/EUR peak buildup & reversal RV universe"
    ws["A1"].font = Font(size=18, bold=True, color=WHITE)
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)
    ws.merge_cells("A1:F1")
    rows = [
        ("As of", asof),
        ("Sample", f"{sample_first} to {asof}; {n} common sessions"),
        ("Source", "data/cache/stir_curves/panel.csv (Barchart fixed contracts)"),
        ("Units", "Rate-space basis points unless explicitly marked as a ratio"),
        ("Sign convention", "BUILD = U27−Z26; CUT = U27−Z28. Positive CUT means more cuts after peak."),
        (
            "Futures-price warning",
            "A futures-price U27−Z28 spread has the opposite sign. The workbook uses economic rate magnitudes.",
        ),
        (
            "Critical algebra",
            "BUILD − CUT = Z28−Z26, so the Sep-27 peak cancels. BUILD + CUT = 2×U27−Z26−Z28 and is true peak curvature.",
        ),
        (
            "Percentile",
            "Empirical rank within the March-to-asof sample. 100 = highest; 0 = lowest.",
        ),
        (
            "Exhaustiveness",
            "Ordered_Diffs has all 12 ordered pair differences. All_Combinations has all 40 {-1,0,+1} combinations unique up to overall sign.",
        ),
        (
            "Ratio warning",
            "All four primitives cross zero in the sample; ratio percentiles can explode and are not decision-grade.",
        ),
        (
            "Policy-cycle warning",
            "ECB delivered 50 bp in 2026 before the as-of date. Cross-market buildup levels compare asynchronous cycles.",
        ),
        (
            "Trade directions",
            "For a high rate-space structure, mean reversion is SHORT: receive positive rate weights and pay negative weights.",
        ),
    ]
    for r, (key, value) in enumerate(rows, 3):
        ws.cell(r, 1, key).font = Font(bold=True, color=NAVY)
        ws.cell(r, 2, value).alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    ws.column_dimensions["A"].width = 25
    for c in "BCDEF":
        ws.column_dimensions[c].width = 23
    for r in range(3, 3 + len(rows)):
        ws.row_dimensions[r].height = 35

    ws["A17"] = "Workbook map"
    ws["A17"].font = Font(size=14, bold=True, color=NAVY)
    maps = [
        ("Dashboard", "Key marks and conclusions"),
        ("Candidate_Trades", "Trade ideas, implementation and failure modes"),
        ("Outrights", "Valuation screen for the four primitive strips"),
        ("Difference_Matrix", "Current, percentile and z-score matrices for every row-minus-column permutation"),
        ("Ordered_Diffs", "All 12 A−B permutations, including β-adjusted residuals"),
        ("Unique_Pairs", "Six non-duplicated pair differences"),
        ("Pair_Sums", "Six pair sums; within-market sums are peak curvatures"),
        ("Ratios", "All 12 ordered ratios, explicitly flagged unstable"),
        ("All_Combinations", "Full 40-combination signed linear universe"),
        ("Canonical_RV", "Economically interpretable boxes, flies and mixed crosses"),
        ("Corr_Changes / Beta_Changes", "Daily-change hedge diagnostics"),
        ("Raw_Series", "Reproducible dates, contract rates and all four primitives"),
    ]
    for r, (sheet, purpose) in enumerate(maps, 18):
        ws.cell(r, 1, sheet).font = Font(bold=True)
        ws.cell(r, 2, purpose)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)


def add_dashboard(
    wb: Workbook,
    x: pd.DataFrame,
    outright: pd.DataFrame,
    canonical: pd.DataFrame,
    candidates: pd.DataFrame,
):
    ws = wb.create_sheet("Dashboard")
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Peak RV dashboard"
    ws["A1"].font = Font(size=18, bold=True, color=WHITE)
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)
    ws.merge_cells("A1:H1")

    ws["A3"] = "Four primitive strips"
    ws["A3"].font = Font(size=14, bold=True, color=NAVY)
    cols = ["id", "label", "current_bp", "percentile", "zscore", "min_bp", "max_bp", "flag"]
    dash_out = outright[cols]
    end = write_dataframe(ws, dash_out, 4, 1)

    ws.cell(end + 2, 1, "Canonical RV structures").font = Font(
        size=14, bold=True, color=NAVY
    )
    ids = [
        "GB_PEAK_CURV", "EU_PEAK_CURV", "REL_BUILD", "REL_CUT",
        "REL_PEAK_CURV", "GB_BUILD_MINUS_EU_CUT",
    ]
    dash_can = canonical.set_index("id").loc[ids].reset_index()[
        ["id", "definition", "current_bp", "percentile", "zscore", "mean_bp", "flag"]
    ]
    end2 = write_dataframe(ws, dash_can, end + 3, 1)

    ws.cell(end2 + 2, 1, "Bottom line").font = Font(size=14, bold=True, color=NAVY)
    conclusions = [
        "Both true peak-curvature measures are extreme: GBP +78.5 bp and EUR +66.5 bp.",
        "Corresponding post-peak cut differential is not extreme: GBP−EUR cuts = +2.5 bp near the sample middle.",
        "The strongest clean cross-market signal is GBP peak curvature rich to EUR by +12 bp (98.6th percentile).",
        "The +9.5 bp buildup box is extreme but partly reflects ECB tightening already delivered before the box window.",
        "UK buildup minus EUR cuts is statistically extreme but daily changes are nearly uncorrelated: reject it as a primary hedge.",
        "Within-market buildup minus cuts cancels U27. Use buildup plus cuts to fade the peak.",
    ]
    for r, text in enumerate(conclusions, end2 + 3):
        ws.cell(r, 1, "•")
        ws.cell(r, 2, text)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
        ws.cell(r, 2).alignment = Alignment(wrap_text=True)

    for col, width in {"A": 23, "B": 46, "C": 16, "D": 15, "E": 12, "F": 13, "G": 18, "H": 18}.items():
        ws.column_dimensions[col].width = width

    # Charts reference Raw_Series, where dates are col A and primitives G:J.
    raw_ws = wb["Raw_Series"]
    chart = LineChart()
    chart.title = "Four primitive strips since March 2026"
    chart.y_axis.title = "bp"
    chart.x_axis.title = "Date"
    chart.height = 8
    chart.width = 17
    data = Reference(raw_ws, min_col=9, max_col=12, min_row=1, max_row=len(x) + 1)
    dates = Reference(raw_ws, min_col=1, min_row=2, max_row=len(x) + 1)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(dates)
    chart.legend.position = "b"
    ws.add_chart(chart, "J3")

    # Candidate summary
    ws["J20"] = "Top candidate"
    ws["J20"].font = Font(size=14, bold=True, color=NAVY)
    ws["J21"] = candidates.iloc[0]["candidate"]
    ws["J21"].font = Font(bold=True)
    ws["J22"] = candidates.iloc[0]["trade_legs"]
    ws["J22"].alignment = Alignment(wrap_text=True)
    ws["J23"] = candidates.iloc[0]["main_risk"]
    ws["J23"].alignment = Alignment(wrap_text=True)
    ws.column_dimensions["J"].width = 34
    ws.column_dimensions["K"].width = 18
    ws.column_dimensions["L"].width = 18
    ws.column_dimensions["M"].width = 18
    ws.column_dimensions["N"].width = 18


def add_difference_matrix(wb: Workbook, x: pd.DataFrame):
    ws = wb.create_sheet("Difference_Matrix")
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Ordered differences: row minus column"
    ws["A1"].font = Font(size=16, bold=True, color=WHITE)
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)
    ws.merge_cells("A1:F1")

    current = pd.DataFrame(index=PRIMITIVES, columns=PRIMITIVES, dtype=float)
    percentile = current.copy()
    zscore = current.copy()
    for row in PRIMITIVES:
        for col in PRIMITIVES:
            if row == col:
                current.loc[row, col] = 0.0
                percentile.loc[row, col] = 50.0
                zscore.loc[row, col] = 0.0
            else:
                st = stats(x[row] - x[col])
                current.loc[row, col] = st.current
                percentile.loc[row, col] = st.percentile
                zscore.loc[row, col] = st.zscore

    sections = [
        ("Current level (bp)", current),
        ("March-sample percentile", percentile),
        ("Z-score", zscore),
    ]
    start = 3
    for title, matrix in sections:
        ws.cell(start, 1, title).font = Font(size=13, bold=True, color=NAVY)
        table = matrix.reset_index().rename(columns={"index": "row − column"})
        write_dataframe(ws, table, start + 1, 1)
        lo = start + 2
        hi = start + 1 + len(table)
        ws.conditional_formatting.add(
            f"B{lo}:E{hi}",
            ColorScaleRule(
                start_type="min", start_color="63BE7B",
                mid_type="percentile", mid_value=50, mid_color="FFEB84",
                end_type="max", end_color="F8696B",
            ),
        )
        start = hi + 3
    ws.freeze_panes = "B4"
    ws.column_dimensions["A"].width = 24
    for c in "BCDE":
        ws.column_dimensions[c].width = 16
    ws["A22"] = "Interpretation"
    ws["A22"].font = Font(bold=True, color=NAVY)
    ws["B22"] = (
        "Every off-diagonal cell is also listed in Ordered_Diffs with "
        "correlation, beta-adjusted residual and hedge-quality diagnostics."
    )
    ws.merge_cells("B22:F23")
    ws["B22"].alignment = Alignment(wrap_text=True, vertical="top")


def build_workbook() -> Path:
    raw_rates, x = load_data()
    (
        outright,
        ordered,
        unique,
        pair_sums,
        ratios,
        canonical,
        combinations,
        corr,
        beta,
    ) = build_tables(x)
    candidates = candidate_table(x, canonical)

    wb = Workbook()
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    add_readme(
        wb,
        str(x.index[-1].date()),
        str(x.index[0].date()),
        len(x),
    )

    raw = pd.concat([raw_rates, x], axis=1).reset_index().rename(columns={"date": "date"})
    raw.insert(0, "session", range(1, len(raw) + 1))
    # Put date first for charts and readability.
    raw = raw[["date", "session"] + [c for c in raw.columns if c not in {"date", "session"}]]
    ws_raw = wb.create_sheet("Raw_Series")
    write_dataframe(ws_raw, raw)
    style_table_sheet(ws_raw, raw)
    ws_raw.column_dimensions["A"].width = 13
    for row in range(2, len(raw) + 2):
        ws_raw.cell(row, 1).number_format = "yyyy-mm-dd"

    add_dashboard(wb, x, outright, canonical, candidates)
    add_difference_matrix(wb, x)

    sheets = [
        ("Candidate_Trades", candidates),
        ("Outrights", outright),
        ("Ordered_Diffs", ordered),
        ("Unique_Pairs", unique),
        ("Pair_Sums", pair_sums),
        ("Ratios", ratios),
        ("All_Combinations", combinations),
        ("Canonical_RV", canonical),
    ]
    for name, df in sheets:
        ws = wb.create_sheet(name)
        write_dataframe(ws, df)
        style_table_sheet(ws, df)

    for name, matrix in [("Corr_Changes", corr), ("Beta_Changes", beta)]:
        ws = wb.create_sheet(name)
        m = matrix.reset_index().rename(columns={"index": "dependent / row"})
        write_dataframe(ws, m)
        style_table_sheet(ws, m)
        ws["A1"].comment = Comment(
            "Corr_Changes: correlation of daily changes. Beta_Changes: no-intercept OLS beta of row change on column change.",
            "Cursor",
        )
        ws.conditional_formatting.add(
            f"B2:E5",
            ColorScaleRule(
                start_type="num", start_value=-1, start_color="63BE7B",
                mid_type="num", mid_value=0, mid_color="FFEB84",
                end_type="num", end_value=1, end_color="F8696B",
            ),
        )

    # Move dashboard directly behind README.
    wb._sheets.insert(1, wb._sheets.pop(wb._sheets.index(wb["Dashboard"])))
    wb._sheets.insert(2, wb._sheets.pop(wb._sheets.index(wb["Candidate_Trades"])))

    for ws in wb.worksheets:
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_view.zoomScale = 90

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT)
    return OUTPUT


def validate(path: Path) -> None:
    wb = load_workbook(path, data_only=False, read_only=False)
    required = {
        "README", "Dashboard", "Candidate_Trades", "Outrights", "Ordered_Diffs",
        "Unique_Pairs", "Pair_Sums", "Ratios", "All_Combinations",
        "Canonical_RV", "Corr_Changes", "Beta_Changes", "Raw_Series",
        "Difference_Matrix",
    }
    missing = required - set(wb.sheetnames)
    if missing:
        raise RuntimeError(f"workbook missing sheets: {sorted(missing)}")
    if wb["Ordered_Diffs"].max_row != 13:
        raise RuntimeError("expected 12 ordered pair differences")
    if wb["All_Combinations"].max_row != 41:
        raise RuntimeError("expected 40 unique signed linear combinations")
    if wb["Raw_Series"].max_row < 100:
        raise RuntimeError("unexpectedly short March sample")
    wb.close()


def main() -> None:
    path = build_workbook()
    validate(path)
    print(f"wrote {path} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
