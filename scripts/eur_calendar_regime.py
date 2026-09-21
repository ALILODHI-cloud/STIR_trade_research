"""Evaluate sequential bear-steepen → bear-flatten on Euribor 1y calendars.

As-of panel last date. Desk spread = back − front (bp). β is OLS on daily
rate changes with no intercept. Bear flatten on a selloff = Δspread < 0.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from lib.stir.rv import hedge_ratio, percentile_rank

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "cache" / "stir_curves" / "panel.csv"
OUT = ROOT / "data" / "cache" / "stir_curves" / "eur_calendar_regime.json"

CALS = [
    ("H27", "H28", "H7H8", "Mar27–Mar28, still pre-peak"),
    ("M27", "M28", "M7M8", "Jun27–Jun28, GS ERM7M8"),
    ("U27", "U28", "U7U8", "Sep27–Sep28, peak vs 1y later"),
    ("Z27", "Z28", "Z7Z8", "Dec27–Dec28, Barclays ERZ7Z8"),
    ("H28", "H29", "H8H9", "Mar28–Mar29"),
    ("M28", "M29", "M8M9", "Jun28–Jun29"),
    ("U28", "U29", "U8U9", "Sep28–Sep29, 2y1y-ish"),
    ("Z28", "Z29", "Z8Z9", "Dec28–Dec29"),
]


def beta_no_int(y: pd.Series, x: pd.Series) -> float:
    a = pd.concat([y, x], axis=1).dropna()
    if len(a) < 8 or float(a.iloc[:, 1].var()) == 0:
        return float("nan")
    return float(hedge_ratio(a.iloc[:, 0], a.iloc[:, 1]))


def cond(spread_d: pd.Series, driver_d: pd.Series, mask: pd.Series) -> dict:
    s = spread_d[mask].dropna()
    n = int(len(s))
    if n == 0:
        return {"n": 0}
    return {
        "n": n,
        "mean_dspread_bp": float(s.mean()),
        "median_dspread_bp": float(s.median()),
        "pct_flatten": float((s < 0).mean() * 100),
        "pct_steepen": float((s > 0).mean() * 100),
        "mean_driver_bp": float(driver_d.reindex(s.index).mean()),
    }


def last_on(s: pd.Series, d) -> float:
    return float(s.loc[:d].dropna().iloc[-1])


def main() -> None:
    p = pd.read_csv(PANEL, parse_dates=["date"])
    eur = p[p.curve == "EURIBOR"].pivot(index="date", columns="contract", values="rate")
    eur = eur.sort_index()
    asof = eur.index.max()
    ytd = eur.loc["2026-01-01":]
    z26_d = ytd["Z26"].diff() * 100
    u27_d = ytd["U27"].diff() * 100

    windows = {
        "ytd": slice("2026-01-01", None),
        "mar": slice("2026-03-01", None),
        "jun": slice("2026-06-01", None),
        "aug": slice("2026-08-01", None),
        "since_27aug": slice("2026-08-27", None),
        "last30": None,
        "post_ecb": slice("2026-09-10", None),
        "pre_ecb_30": None,
    }

    rows = []
    rolling = {}
    path_ecb = {}
    beta_path = {}

    for front, back, name, role in CALS:
        if front not in ytd.columns or back not in ytd.columns:
            continue
        f = ytd[front] * 100
        b = ytd[back] * 100
        spr = b - f  # bp, desk = back − front
        df = f.diff()
        db = b.diff()
        ds = spr.diff()

        full = eur[[front, back]].dropna()
        spr_full = (full[back] - full[front]) * 100

        last30_idx = df.dropna().index[-30:]
        pre_ecb = df.loc[: "2026-09-09"].dropna().index
        pre30 = pre_ecb[-30:] if len(pre_ecb) >= 30 else pre_ecb

        # rolling 30d β(back|front) on the full 2026 sample
        b30 = hedge_ratio(db, df, window=30)
        s30 = hedge_ratio(ds, df, window=30)  # Δspread | Δfront; <0 = flatten on selloff
        # rolling 30d hit rate on near-leg selloffs
        hit = []
        for i, dt in enumerate(ds.dropna().index):
            w = ds.loc[:dt].dropna().tail(30)
            dw = df.reindex(w.index)
            m = dw > 0
            if m.sum() < 5:
                hit.append(np.nan)
            else:
                hit.append(float((w[m] < 0).mean() * 100))
        hit = pd.Series(hit, index=ds.dropna().index)

        def snap(d):
            if d not in b30.index and d not in b30.loc[:d].index:
                return None
            try:
                return {
                    "beta_back_on_front": float(b30.loc[:d].dropna().iloc[-1]),
                    "beta_spread_on_front": float(s30.loc[:d].dropna().iloc[-1]),
                    "selloff_flatten_pct_30d": float(hit.loc[:d].dropna().iloc[-1])
                    if len(hit.loc[:d].dropna())
                    else None,
                    "spread_bp": float(spr.loc[:d].dropna().iloc[-1]),
                }
            except IndexError:
                return None

        dated = {
            "2026-01-02": snap("2026-01-02"),
            "2026-03-02": snap("2026-03-02"),
            "2026-06-01": snap("2026-06-01"),
            "2026-08-03": snap("2026-08-03"),
            "2026-08-27": snap("2026-08-27"),
            "2026-09-09": snap("2026-09-09"),
            "2026-09-10": snap("2026-09-10"),
            "2026-09-14": snap("2026-09-14"),
            "2026-09-18": snap("2026-09-18"),
        }

        # first date in 2026 when 30d β stayed < 1 for 10 consecutive sessions
        below = (b30 < 1).astype(int)
        run = below.groupby((below != below.shift()).cumsum()).cumsum()
        first_regime = None
        for dt, r, bb in zip(b30.index, run, b30):
            if dt < pd.Timestamp("2026-01-01"):
                continue
            if r >= 10 and bb < 1:
                first_regime = str(dt.date())
                break

        sls = {
            "ytd": (df.index >= "2026-01-01"),
            "mar": (df.index >= "2026-03-01"),
            "jun": (df.index >= "2026-06-01"),
            "aug": (df.index >= "2026-08-01"),
            "since_27aug": (df.index >= "2026-08-27"),
            "last30": df.index.isin(last30_idx),
            "post_ecb": (df.index >= "2026-09-10"),
            "pre_ecb_30": df.index.isin(pre30),
        }

        samples = {}
        for k, m in sls.items():
            mm = m & df.notna() & ds.notna()
            samples[k] = {
                "n": int(mm.sum()),
                "beta_back_on_front": beta_no_int(db[mm], df[mm]),
                "beta_spread_on_front": beta_no_int(ds[mm], df[mm]),
                "beta_back_on_z26": beta_no_int(db[mm], z26_d[mm]),
                "beta_front_on_z26": beta_no_int(df[mm], z26_d[mm]),
                "beta_spread_on_z26": beta_no_int(ds[mm], z26_d[mm]),
                "near_sell": cond(ds, df, mm & (df > 0)),
                "near_sell_1bp": cond(ds, df, mm & (df > 1)),
                "z26_sell": cond(ds, z26_d, mm & (z26_d > 0)),
                "z26_sell_1bp": cond(ds, z26_d, mm & (z26_d > 1)),
                "u27_sell": cond(ds, u27_d, mm & (u27_d > 0)),
                "near_rally": cond(ds, df, mm & (df < 0)),
            }

        # ECB path
        dates = [
            "2026-09-09",
            "2026-09-10",
            "2026-09-11",
            "2026-09-14",
            "2026-09-15",
            "2026-09-16",
            "2026-09-17",
            "2026-09-18",
        ]
        path = []
        for d in dates:
            ts = pd.Timestamp(d)
            if ts not in ytd.index:
                continue
            path.append(
                {
                    "date": d,
                    "front": float(ytd.loc[ts, front]),
                    "back": float(ytd.loc[ts, back]),
                    "spread_bp": float(spr.loc[ts]),
                }
            )
        pre = spr.loc["2026-09-09"]
        ev = spr.loc["2026-09-10"]
        last = spr.iloc[-1]
        path_ecb[name] = {
            "path": path,
            "event_dspread": float(ev - pre),
            "post_dspread_10_to_18": float(last - ev),
            "post_dfront_10_to_18": float((ytd.loc["2026-09-18", front] - ytd.loc["2026-09-10", front]) * 100),
            "post_dback_10_to_18": float((ytd.loc["2026-09-18", back] - ytd.loc["2026-09-10", back]) * 100),
            "event_dfront": float((ytd.loc["2026-09-10", front] - ytd.loc["2026-09-09", front]) * 100),
            "event_dback": float((ytd.loc["2026-09-10", back] - ytd.loc["2026-09-09", back]) * 100),
        }

        ytd_s = spr.dropna()
        rows.append(
            {
                "name": name,
                "front": front,
                "back": back,
                "role": role,
                "last_spread_bp": float(spr.iloc[-1]),
                "last_front": float(ytd[front].iloc[-1]),
                "last_back": float(ytd[back].iloc[-1]),
                "ytd_pctile": float(percentile_rank(ytd_s).iloc[-1]),
                "ytd_min": float(ytd_s.min()),
                "ytd_max": float(ytd_s.max()),
                "first_10d_beta_below_1": first_regime,
                "beta30_last": float(b30.dropna().iloc[-1]),
                "beta30_pre_ecb": float(b30.loc[: "2026-09-09"].dropna().iloc[-1]),
                "beta30_ecb": float(b30.loc[: "2026-09-10"].dropna().iloc[-1]),
                "spread_beta30_last": float(s30.dropna().iloc[-1]),
                "hit30_last": float(hit.dropna().iloc[-1]),
                "dated": dated,
                "samples": samples,
            }
        )
        rolling[name] = {
            "date": [str(d.date()) for d in b30.dropna().index],
            "beta30": [None if np.isnan(x) else float(x) for x in b30.dropna()],
        }
        beta_path[name] = dated

    # ranking last30 near-sell mean Δspread (more negative = more shifted)
    last30_rank = sorted(
        (
            (
                r["name"],
                r["samples"]["last30"]["near_sell"].get("mean_dspread_bp"),
                r["samples"]["last30"]["near_sell"].get("pct_flatten"),
                r["beta30_last"],
            )
            for r in rows
        ),
        key=lambda t: (t[1] is None, t[1] if t[1] is not None else 0),
    )
    aug_rank = sorted(
        (
            (
                r["name"],
                r["samples"]["aug"]["near_sell"].get("mean_dspread_bp"),
                r["samples"]["aug"]["near_sell"].get("pct_flatten"),
                r["samples"]["aug"]["beta_back_on_front"],
            )
            for r in rows
        ),
        key=lambda t: (t[1] is None, t[1] if t[1] is not None else 0),
    )
    z26_aug_rank = sorted(
        (
            (
                r["name"],
                r["samples"]["aug"]["z26_sell"].get("mean_dspread_bp"),
                r["samples"]["aug"]["z26_sell"].get("pct_flatten"),
            )
            for r in rows
        ),
        key=lambda t: (t[1] is None, t[1] if t[1] is not None else 0),
    )

    # box M−Z
    m = next(r for r in rows if r["name"] == "M7M8")
    z = next(r for r in rows if r["name"] == "Z7Z8")
    mspr = (ytd["M28"] - ytd["M27"]) * 100
    zspr = (ytd["Z28"] - ytd["Z27"]) * 100
    box = mspr - zspr
    box_d = box.diff()
    box_stats = {
        "last": float(box.iloc[-1]),
        "ytd_pctile": float(percentile_rank(box.dropna()).iloc[-1]),
        "ytd_min": float(box.min()),
        "ytd_max": float(box.max()),
        "beta_dM_on_dZ_ytd": beta_no_int(mspr.diff(), zspr.diff()),
        "beta_dM_on_dZ_aug": beta_no_int(
            mspr.diff().loc["2026-08-01":], zspr.diff().loc["2026-08-01":]
        ),
        "corr_aug": float(
            pd.concat([mspr.diff(), zspr.diff()], axis=1)
            .loc["2026-08-01":]
            .dropna()
            .corr()
            .iloc[0, 1]
        ),
        "corr_ytd": float(
            pd.concat([mspr.diff(), zspr.diff()], axis=1).dropna().corr().iloc[0, 1]
        ),
    }

    out = {
        "asof": str(asof.date()),
        "ecb": "2026-09-10",
        "convention": "spread_bp = 100*(back-front); beta OLS no intercept on daily bp changes",
        "strip_last": {c: float(ytd[c].iloc[-1]) for c in ["Z26", "H27", "M27", "U27", "Z27", "H28", "M28", "U28", "Z28", "H29", "M29", "U29", "Z29"] if c in ytd},
        "calendars": rows,
        "path_ecb": path_ecb,
        "rank_last30_near_sell_flatten": last30_rank,
        "rank_aug_near_sell_flatten": aug_rank,
        "rank_aug_z26_sell_flatten": z26_aug_rank,
        "box_M_minus_Z": box_stats,
        "beta_snapshots": beta_path,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"wrote {OUT}")
    print(f"asof {asof.date()}")
    print("last strip:")
    for c, v in out["strip_last"].items():
        print(f"  {c} {v:.3f}")
    print("\nlevels / 30d beta / last30 near-sell:")
    for r in rows:
        ns = r["samples"]["last30"]["near_sell"]
        aug = r["samples"]["aug"]["near_sell"]
        print(
            f"  {r['name']:5} last={r['last_spread_bp']:+6.1f}  "
            f"β30={r['beta30_last']:.2f} (preECB {r['beta30_pre_ecb']:.2f})  "
            f"last30 sell n={ns.get('n')} meanΔ={ns.get('mean_dspread_bp')} "
            f"flatten%={ns.get('pct_flatten')}  "
            f"Aug sell meanΔ={aug.get('mean_dspread_bp')} flatten%={aug.get('pct_flatten')}"
        )
    print("\nECB path event / 10→18:")
    for name, pe in path_ecb.items():
        print(
            f"  {name:5} event {pe['event_dspread']:+5.1f} "
            f"(front {pe['event_dfront']:+5.1f} back {pe['event_dback']:+5.1f})  "
            f"post {pe['post_dspread_10_to_18']:+5.1f} "
            f"(front {pe['post_dfront_10_to_18']:+5.1f} back {pe['post_dback_10_to_18']:+5.1f})"
        )
    print("\nfirst 10-session β<1:")
    for r in rows:
        print(f"  {r['name']} {r['first_10d_beta_below_1']}")


if __name__ == "__main__":
    main()
