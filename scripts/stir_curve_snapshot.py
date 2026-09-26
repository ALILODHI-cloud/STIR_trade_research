"""STIR curve snapshot: SOFR (SQ), Euribor (IM), SONIA (J8).

Reads cleaned panel + FRED spots from data/cache/stir_curves/ (populated by
the fetch step) and writes:

  research/notes/stir_curve_snapshot_2026-09-18.md
  research/notes/stir_curves_ytd.html          interactive YTD viewer
  data/cache/stir_curves/summary.json

All levels come from files on disk — never from model memory.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache" / "stir_curves"
NOTES = ROOT / "research" / "notes"
ASOF = pd.Timestamp("2026-09-18")
YTD = pd.Timestamp("2026-01-02")
TWO_WEEKS = ASOF - pd.Timedelta(days=14)

MONTH_ORDER = {
    "F": 1,
    "G": 2,
    "H": 3,
    "J": 4,
    "K": 5,
    "M": 6,
    "N": 7,
    "Q": 8,
    "U": 9,
    "V": 10,
    "X": 11,
    "Z": 12,
}


def contract_sort_key(contract: str) -> tuple[int, int]:
    """e.g. 'Z26' -> (2026, 12)."""
    m, y = contract[0], int(contract[1:])
    year = 2000 + y if y < 100 else y
    return year, MONTH_ORDER[m]


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(CACHE / "panel.csv", parse_dates=["date"])
    return df


def load_spot(name: str) -> pd.Series:
    s = pd.read_csv(CACHE / f"spot_{name}.csv", parse_dates=["date"])
    return s.set_index("date")["value"].sort_index()


def latest_strip(panel: pd.DataFrame, curve: str, asof: pd.Timestamp) -> pd.DataFrame:
    sub = panel[(panel.curve == curve) & (panel.date == asof)].copy()
    # Drop stale expired prints that still appear in the vendor feed with old trade dates
    # by requiring the panel date itself (already filtered). Keep quarterly + near serials.
    sub["sort"] = sub["contract"].map(contract_sort_key)
    return sub.sort_values("sort").reset_index(drop=True)


def curve_on_date(panel: pd.DataFrame, curve: str, dt: pd.Timestamp, contracts: list[str]) -> pd.Series:
    sub = panel[(panel.curve == curve) & (panel.date == dt) & (panel.contract.isin(contracts))]
    return sub.set_index("contract")["rate"]


def nearest_session(panel: pd.DataFrame, target: pd.Timestamp) -> pd.Timestamp:
    dates = np.array(sorted(panel.date.unique()))
    dates = dates[dates <= np.datetime64(target)]
    if len(dates) == 0:
        raise ValueError(f"no session on/before {target}")
    return pd.Timestamp(dates[-1])


def main() -> None:
    NOTES.mkdir(parents=True, exist_ok=True)
    panel = load_panel()
    # Restrict to live window used in the note
    panel = panel[panel.date <= ASOF].copy()

    spot_sofr = load_spot("SOFR")
    spot_sonia = load_spot("SONIA")
    spot_ecb = load_spot("ECB_DFR")
    spot_effr = load_spot("EFFR")

    asof = nearest_session(panel, ASOF)
    ytd = nearest_session(panel, YTD)
    twoweek = nearest_session(panel, TWO_WEEKS)

    # Contracts for the displayed strips (whites through reds)
    display_contracts = [
        f"{m}{y}" for y in ("26", "27", "28") for m in ("H", "M", "U", "Z")
    ]
    # Front SOFR serials still relevant through end-2026
    sofr_front = ["U26", "V26", "X26", "Z26"]

    strips = {}
    for curve in ("SOFR", "EURIBOR", "SONIA"):
        s = latest_strip(panel, curve, asof)
        s = s[s.contract.isin(display_contracts + (sofr_front if curve == "SOFR" else []))]
        strips[curve] = s

    # --- End-2026 priced change ---------------------------------------------
    # Compare overnight / policy spot to Dec-26 3M futures implied rate.
    z26 = {
        "SOFR": float(strips["SOFR"].loc[strips["SOFR"].contract == "Z26", "rate"].iloc[0]),
        "EURIBOR": float(strips["EURIBOR"].loc[strips["EURIBOR"].contract == "Z26", "rate"].iloc[0]),
        "SONIA": float(strips["SONIA"].loc[strips["SONIA"].contract == "Z26", "rate"].iloc[0]),
    }
    spot_now = {
        "SOFR": float(spot_sofr.loc[:asof].iloc[-1]),
        "SONIA": float(spot_sonia.loc[:asof].iloc[-1]),
        "ECB_DFR": float(spot_ecb.loc[:asof].iloc[-1]),
        "EFFR": float(spot_effr.loc[:asof].iloc[-1]),
    }
    # Euribor futures are 3M Euribor, not DFR. Use front live Euribor future as
    # near-term tenor anchor (IMU26 just expired; IMZ26 is the first live white
    # after Sep expiry — also report DFR for policy context).
    eur_front_live = strips["EURIBOR"].iloc[0]
    end2026 = {
        "asof": str(asof.date()),
        "spot": spot_now,
        "z26_rate": z26,
        "z26_minus_spot_bp": {
            "SOFR_vs_SOFR": round((z26["SOFR"] - spot_now["SOFR"]) * 100, 1),
            "SONIA_vs_SONIA": round((z26["SONIA"] - spot_now["SONIA"]) * 100, 1),
            "EURIBOR_Z26_vs_ECB_DFR": round((z26["EURIBOR"] - spot_now["ECB_DFR"]) * 100, 1),
        },
        "notes": (
            "Z26 is the 3M forward rate for the Dec-26 IMM quarter, not an "
            "overnight print on 31 Dec. SOFR/SONIA comparisons use the matching "
            "overnight fixing; Euribor is compared to ECB DFR as policy context "
            "plus the live front future."
        ),
        "euribor_front": {
            "contract": str(eur_front_live.contract),
            "rate": float(eur_front_live.rate),
            "z26_minus_front_bp": round((z26["EURIBOR"] - float(eur_front_live.rate)) * 100, 1),
        },
    }

    # Path through end-2026 on each strip (contracts settling in 2026)
    path_2026 = {}
    for curve, s in strips.items():
        c26 = s[s.contract.str.endswith("26")][["contract", "price", "rate"]].copy()
        path_2026[curve] = c26.to_dict(orient="records")

    # Sep-26 Euribor white's last print (expired mid-Sep) as near-term tenor anchor
    imu26 = panel[(panel.curve == "EURIBOR") & (panel.contract == "U26")]
    if not imu26.empty:
        last_u26 = imu26.sort_values("date").iloc[-1]
        end2026["euribor_expired_U26"] = {
            "last_session": str(pd.Timestamp(last_u26.date).date()),
            "rate": float(last_u26.rate),
            "z26_minus_U26_bp": round((z26["EURIBOR"] - float(last_u26.rate)) * 100, 1),
        }

    # --- Two-week movers ----------------------------------------------------
    movers = []
    for curve in ("SOFR", "EURIBOR", "SONIA"):
        for contract in display_contracts:
            a = panel[(panel.curve == curve) & (panel.contract == contract) & (panel.date == asof)]
            b = panel[(panel.curve == curve) & (panel.contract == contract) & (panel.date == twoweek)]
            if a.empty or b.empty:
                continue
            rate0 = float(b.rate.iloc[0])
            rate1 = float(a.rate.iloc[0])
            px0 = float(b.price.iloc[0])
            px1 = float(a.price.iloc[0])
            movers.append(
                {
                    "curve": curve,
                    "symbol": f"{'SQ' if curve=='SOFR' else 'IM' if curve=='EURIBOR' else 'J8'}{contract}",
                    "contract": contract,
                    "rate_from": rate0,
                    "rate_to": rate1,
                    "rate_chg_bp": round((rate1 - rate0) * 100, 2),
                    "price_chg": round(px1 - px0, 4),
                }
            )
    movers_df = pd.DataFrame(movers).sort_values("rate_chg_bp", key=lambda s: s.abs(), ascending=False)
    top_movers = movers_df.head(10)

    # --- Euribor Z27/Z28 inversion theme ------------------------------------
    ez = panel[(panel.curve == "EURIBOR") & (panel.contract.isin(["Z27", "Z28"]))].copy()
    wide = ez.pivot_table(index="date", columns="contract", values="rate")
    wide = wide.dropna()
    wide["z27_minus_z28_bp"] = (wide["Z27"] - wide["Z28"]) * 100
    # positive => Z27 rate above Z28 rate => inverted in rate space (price Z27 < Z28)
    theme = {
        "asof": str(asof.date()),
        "z27_rate": float(wide.loc[asof, "Z27"]) if asof in wide.index else float(wide["Z27"].iloc[-1]),
        "z28_rate": float(wide.loc[asof, "Z28"]) if asof in wide.index else float(wide["Z28"].iloc[-1]),
        "spread_z27_minus_z28_bp": float(wide["z27_minus_z28_bp"].iloc[-1]),
        "ytd_start": str(ytd.date()),
        "spread_at_ytd_bp": float(wide.loc[ytd, "z27_minus_z28_bp"]) if ytd in wide.index else None,
        "spread_2w_ago_bp": float(wide.loc[twoweek, "z27_minus_z28_bp"]) if twoweek in wide.index else None,
        "days_inverted_ytd": int((wide.loc[ytd:, "z27_minus_z28_bp"] > 0).sum()),
        "sessions_ytd": int(len(wide.loc[ytd:])),
        "recent_turn": None,
    }
    # When did the spread last cross above 0?
    sig = (wide["z27_minus_z28_bp"] > 0).astype(int)
    crossings = wide.index[(sig.diff() == 1)]
    if len(crossings):
        theme["recent_turn"] = str(pd.Timestamp(crossings[-1]).date())
    theme["max_spread_ytd_bp"] = float(wide.loc[ytd:, "z27_minus_z28_bp"].max())
    theme["min_spread_ytd_bp"] = float(wide.loc[ytd:, "z27_minus_z28_bp"].min())

    # Terminal (trough) rate on Euribor strip = max rate / min price on whites-reds
    for label, dt in [("asof", asof), ("ytd", ytd), ("twoweek", twoweek)]:
        s = curve_on_date(panel, "EURIBOR", dt, display_contracts)
        if s.empty:
            continue
        theme[f"terminal_contract_{label}"] = s.idxmax()
        theme[f"terminal_rate_{label}"] = float(s.max())

    # --- Interactive HTML ---------------------------------------------------
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.62, 0.38],
        subplot_titles=(
            "3M futures curves (rate, %) — drag the date slider",
            "Euribor Dec27 − Dec28 (bp). Positive = inverted (Z27 richer in rate)",
        ),
        vertical_spacing=0.12,
    )

    # Build frames for each YTD session (weekly to keep file light, plus key dates)
    sessions = sorted(d for d in panel.date.unique() if d >= np.datetime64(ytd) and d <= np.datetime64(asof))
    sessions = [pd.Timestamp(d) for d in sessions]
    # daily is fine for ~180 sessions
    colors = {"SOFR": "#1f77b4", "EURIBOR": "#d62728", "SONIA": "#2ca02c"}

    def curve_xy(curve: str, dt: pd.Timestamp):
        s = curve_on_date(panel, curve, dt, display_contracts)
        if s.empty:
            return [], []
        ordered = sorted(s.index, key=contract_sort_key)
        return ordered, [float(s[c]) for c in ordered]

    # Initial traces (latest)
    for curve in ("SOFR", "EURIBOR", "SONIA"):
        x, y = curve_xy(curve, asof)
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                name=curve,
                line=dict(color=colors[curve], width=2),
                marker=dict(size=7),
            ),
            row=1,
            col=1,
        )

    # Euribor inversion history
    inv = wide.loc[ytd:asof]
    fig.add_trace(
        go.Scatter(
            x=inv.index,
            y=inv["z27_minus_z28_bp"],
            mode="lines",
            name="IMZ27−IMZ28 (bp)",
            line=dict(color="#d62728", width=2),
            showlegend=True,
        ),
        row=2,
        col=1,
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#888", row=2, col=1)

    # Slider frames: update the three curve traces
    frames = []
    for dt in sessions:
        frame_data = []
        for curve in ("SOFR", "EURIBOR", "SONIA"):
            x, y = curve_xy(curve, dt)
            frame_data.append(go.Scatter(x=x, y=y))
        frames.append(go.Frame(data=frame_data, name=str(dt.date()), traces=[0, 1, 2]))
    fig.frames = frames

    steps = []
    for dt in sessions:
        steps.append(
            dict(
                method="animate",
                label=str(dt.date())[5:],  # MM-DD
                args=[
                    [str(dt.date())],
                    dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0)),
                ],
            )
        )
    # Mark YTD start and asof in slider via longer labels already

    fig.update_layout(
        title=dict(
            text=f"DM STIR curves — YTD 2026 through {asof.date()} (Barchart EOD: SQ / IM / J8)",
            x=0.02,
        ),
        height=820,
        template="plotly_white",
        legend=dict(orientation="h", y=1.08),
        sliders=[
            dict(
                active=len(steps) - 1,
                steps=steps,
                currentvalue=dict(prefix="Session: ", font=dict(size=14)),
                x=0.05,
                len=0.9,
            )
        ],
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                y=1.12,
                x=0.85,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            dict(frame=dict(duration=80, redraw=True), fromcurrent=True, transition=dict(duration=0)),
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], dict(mode="immediate", frame=dict(duration=0))],
                    ),
                ],
            )
        ],
        margin=dict(l=60, r=30, t=80, b=60),
    )
    fig.update_yaxes(title_text="Implied 3M rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="bp", row=2, col=1)
    fig.update_xaxes(title_text="Contract", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)

    html_path = NOTES / "stir_curves_ytd.html"
    fig.write_html(html_path, include_plotlyjs="cdn", full_html=True)

    # Static snapshot chart of latest curves
    snap = go.Figure()
    for curve in ("SOFR", "EURIBOR", "SONIA"):
        x, y = curve_xy(curve, asof)
        snap.add_trace(
            go.Scatter(x=x, y=y, mode="lines+markers", name=curve, line=dict(color=colors[curve], width=2))
        )
    snap.update_layout(
        title=f"Latest strips {asof.date()} (rate %)",
        template="plotly_white",
        height=420,
        legend=dict(orientation="h"),
        yaxis_title="Implied 3M rate (%)",
        xaxis_title="Contract",
    )
    snap_path = NOTES / "stir_curves_latest.html"
    snap.write_html(snap_path, include_plotlyjs="cdn", full_html=True)

    # --- Markdown note ------------------------------------------------------
    def fmt_strip(curve: str, only_2026: bool = False) -> str:
        s = strips[curve]
        lines = ["| Contract | Price | Rate % |", "|---|---:|---:|"]
        for _, r in s.iterrows():
            if only_2026 and not str(r.contract).endswith("26"):
                continue
            if curve != "SOFR" and r.contract not in display_contracts:
                continue
            if curve == "SOFR" and r.contract not in display_contracts and r.contract not in sofr_front:
                continue
            lines.append(f"| {r.contract} | {r.price:.4f} | {r.rate:.4f} |")
        return "\n".join(lines)

    md = f"""# STIR curve snapshot — {asof.date()}

Source: Barchart EOD via browser session (`SQ` = 3M SOFR, `IM` = 3M Euribor, `J8` = 3M SONIA).
Spot anchors: FRED `SOFR`, `IUDSOIA` (SONIA), `ECBDFR`, `EFFR`.
Fetched fresh this session — nothing reused from prior repo cache.

Interactive YTD viewer: [`stir_curves_ytd.html`](stir_curves_ytd.html)
Latest overlay: [`stir_curves_latest.html`](stir_curves_latest.html)

## What the market prices into end-2026

Dec-26 futures are the **3M forward rate for the Dec-26 IMM quarter**, not an
overnight fix on 31 Dec. Delta vs spot is the priced change into that window.

| Curve | Spot / policy | As-of | Z26 rate | Z26 − spot (bp) |
|---|---:|---|---:|---:|
| SOFR | SOFR {spot_now['SOFR']:.3f}% | {spot_sofr.loc[:asof].index[-1].date()} | {z26['SOFR']:.3f}% | {end2026['z26_minus_spot_bp']['SOFR_vs_SOFR']:+.1f} |
| SONIA | SONIA {spot_now['SONIA']:.3f}% | {spot_sonia.loc[:asof].index[-1].date()} | {z26['SONIA']:.3f}% | {end2026['z26_minus_spot_bp']['SONIA_vs_SONIA']:+.1f} |
| Euribor | ECB DFR {spot_now['ECB_DFR']:.3f}% | {spot_ecb.loc[:asof].index[-1].date()} | {z26['EURIBOR']:.3f}% | {end2026['z26_minus_spot_bp']['EURIBOR_Z26_vs_ECB_DFR']:+.1f} (vs DFR, not 3M Euribor fix) |

Euribor: Sep-26 white has expired, so **IMZ26 is the only remaining 2026 quarterly**.
Last IMU26 print: {end2026.get('euribor_expired_U26', {}).get('last_session', 'n/a')} at
{end2026.get('euribor_expired_U26', {}).get('rate', float('nan')):.3f}% → Z26 is
**{end2026.get('euribor_expired_U26', {}).get('z26_minus_U26_bp', float('nan')):+.1f} bp** higher.

EFFR for context: {spot_now['EFFR']:.3f}% on {spot_effr.loc[:asof].index[-1].date()}.

### Remaining 2026 contracts only (rate %)

"""
    for curve in ("SOFR", "EURIBOR", "SONIA"):
        md += f"\n**{curve}**\n\n"
        md += fmt_strip(curve, only_2026=True) + "\n"

    md += f"""

### Full latest strips through 2028 (rate %)

"""
    for curve in ("SOFR", "EURIBOR", "SONIA"):
        md += f"\n**{curve}**\n\n"
        md += fmt_strip(curve, only_2026=False) + "\n"

    md += f"""

## Biggest movers — last two weeks ({twoweek.date()} → {asof.date()})

Ranked by absolute rate change (bp). Price fall = rate rise.

| Rank | Symbol | Curve | Δ rate (bp) | From % | To % | Δ price |
|---|---|---|---:|---:|---:|---:|
"""
    for i, r in enumerate(top_movers.itertuples(), 1):
        md += (
            f"| {i} | {r.symbol} | {r.curve} | {r.rate_chg_bp:+.2f} | "
            f"{r.rate_from:.3f} | {r.rate_to:.3f} | {r.price_chg:+.4f} |\n"
        )

    md += f"""

## Euribor end-27 / end-28 inversion theme

Convention: spread = **Z27 rate − Z28 rate** (bp). Positive ⇒ inverted
(terminal/near-terminal above the further reds) — i.e. price(IMZ27) < price(IMZ28).

| | |
|---|---|
| IMZ27 rate | {theme['z27_rate']:.3f}% |
| IMZ28 rate | {theme['z28_rate']:.3f}% |
| Spread now | **{theme['spread_z27_minus_z28_bp']:+.1f} bp** |
| Spread 2w ago ({twoweek.date()}) | {theme['spread_2w_ago_bp']:+.1f} bp |
| Spread at YTD ({ytd.date()}) | {theme['spread_at_ytd_bp']:+.1f} bp |
| Sessions inverted YTD | {theme['days_inverted_ytd']} / {theme['sessions_ytd']} |
| Last cross into inversion | {theme['recent_turn']} |
| YTD range of spread | [{theme['min_spread_ytd_bp']:+.1f}, {theme['max_spread_ytd_bp']:+.1f}] bp |
| Euribor terminal contract now | {theme.get('terminal_contract_asof')} @ {theme.get('terminal_rate_asof', float('nan')):.3f}% |
| Euribor terminal 2w ago | {theme.get('terminal_contract_twoweek')} @ {theme.get('terminal_rate_twoweek', float('nan')):.3f}% |
| Euribor terminal at YTD | {theme.get('terminal_contract_ytd')} @ {theme.get('terminal_rate_ytd', float('nan')):.3f}% |

Verdict is written from these numbers in the session note / chat — the table
above is the arithmetic.

## Data provenance

- Futures: Barchart core-api EOD `historical/get` + `quotes/get` for fixed
  contracts `SQ*`, `IM*`, `J8*` (not generics).
- Spots: FRED CSV downloads same session.
- Panel rows: {len(panel):,} across {panel.symbol.nunique()} contracts,
  {panel.date.min().date()} → {panel.date.max().date()}.
"""

    note_path = NOTES / "stir_curve_snapshot_2026-09-18.md"
    note_path.write_text(md)

    summary = {
        "asof": str(asof.date()),
        "ytd_session": str(ytd.date()),
        "twoweek_session": str(twoweek.date()),
        "end2026": end2026,
        "top_movers": top_movers.to_dict(orient="records"),
        "euribor_inversion": theme,
        "strips": {k: v[["contract", "price", "rate"]].to_dict(orient="records") for k, v in strips.items()},
        "artifacts": {
            "note": str(note_path.relative_to(ROOT)),
            "interactive": str(html_path.relative_to(ROOT)),
            "latest_html": str(snap_path.relative_to(ROOT)),
        },
    }
    (CACHE / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    movers_df.to_csv(CACHE / "movers_2w.csv", index=False)
    wide.loc[ytd:].to_csv(CACHE / "euribor_z27_z28.csv")

    print(json.dumps(summary, indent=2, default=str)[:4000])
    print("wrote", note_path)
    print("wrote", html_path)


if __name__ == "__main__":
    main()
