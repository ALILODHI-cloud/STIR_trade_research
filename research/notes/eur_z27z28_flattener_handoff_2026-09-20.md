# Euribor curve + Z27Z28 flattener — handoff pack for evaluation

**Purpose:** Self-contained brief for another agent to evaluate the
**Dec27 / Dec28 Euribor flattener** (short the post-peak gap). Do not invent
levels — everything below is from on-disk cache as-of **2026-09-18**.

**Related notes (same repo):**
- `research/notes/eur_short_z27z28_2026-09-20.md` — short Z7Z8 verdict
- `research/notes/eur_recv_belly_pay_z26_2026-09-20.md` — why recv-U27/pay-Z26 fails
- `research/notes/barclays_erz7z8_analogues_2026-09-19.md` — Barclays ERZ7Z8
- `research/notes/gs_eur_1y1y_vs_chf_2026-09-20.md` — GS EUR 1y1y vs CHF
- PDF: `research/pdfs/GS_Global_Rates_Trader_Hiking_More_or_Less.pdf`
- PDF: `research/pdfs/Barclays_Global_Rates_Weekly_On_the_brink_7afa.pdf`

**Machine-readable companions:**
- `data/cache/stir_curves/eur_z27z28_handoff_pack.json`
- `data/cache/stir_curves/euribor_last30d_rates_spreads.csv`
- `data/cache/stir_curves/euribor_betas_windows.csv`
- `data/cache/stir_curves/eur_short_z27z28.json`
- `data/cache/stir_curves/panel.csv` (full history)
- `data/cache/stir_curves/summary.json`

---

## 1. Conventions (desk)

| Item | Rule |
|---|---|
| Rate | `rate = 100 − futures price` |
| Spread / slope | **back − front** (bp) = `(r_back − r_front) × 100` |
| Positive spread | Steep (back > front) |
| Negative spread | Inverted (back < front) |
| Flatten | Spread **falls** |
| Already inverted | Flatten further = **invert more** |
| Z27Z28 flattener (“short the spread”) | Short `(Z28 − Z27)` = **receive IMZ27 / pay IMZ28** (≈1:1 DV01; Euribor 3M IMM ≈ €25/bp/contract) |
| Flattener P&L | `P&L_bp ≈ −Δ(Z28 − Z27)` per matched DV01 |

Older notes that said front−back: negate. Barclays PDF used front−back with
more negative = more inverted; their −11 ≈ our −11 numerically on 10-Sep.

Fly weights if needed later: rate-space `(1, −2, 1)`; positive = body below
wing line (fly sign not desk-confirmed).

---

## 2. Data provenance

| Series | Source on disk |
|---|---|
| Euribor 3M futures (`IM*`) | Barchart fixed contracts → `data/raw/stir_futures/` → `panel.csv` |
| As-of | **2026-09-18** (`summary.json`) |
| ECB DFR spot | **2.50%** (FRED `ECBDFR` in `spot_ECB_DFR.csv` / summary) |
| 30-day window | Calendar ~30d: **2026-08-19 → 2026-09-18** (**23** sessions) |

Do not fetch live levels unless the evaluator refreshes the cache; egress to
public hosts may be blocked.

---

## 3. Euribor strip as-of 2026-09-18

ECB DFR = **2.50%**. Peak = **U27 @ 3.585%** (+108.5 bp vs DFR).

| Contract | Rate % | vs DFR (bp) | Role in thesis |
|---|---:|---:|---|
| Z26 | 3.050 | +55.0 | Front / hedge candidate |
| H27 | 3.380 | +88.0 | Front–belly |
| M27 | 3.540 | +104.0 | Shoulder (often mislabeled “belly”) |
| **U27** | **3.585** | **+108.5** | **Peak / hawkish instrument** |
| **Z27** | **3.565** | **+106.5** | **2 bp off peak — flattener front leg** |
| H28 | 3.530 | +103.0 | Post-peak |
| M28 | 3.495 | +99.5 | |
| U28 | 3.470 | +97.0 | |
| **Z28** | **3.455** | **+95.5** | **Further belly — flattener back leg** |

**Key spreads (back − front, bp):**

| Spread | bp | Note |
|---|---:|---|
| **Z28 − Z27** | **−11.0** | Trade spread; inverted |
| U27 − Z26 | +53.5 | YTD **max** — failed “recv belly/pay Z26” gap |
| H27 − Z26 | +33.0 | Front still steep |
| U27 − Z27 | +2.0 | Z27 ≈ co-peak |
| U27 − Z28 | +13.0 | Peak vs true further belly |
| M28 − M27 | −4.5 | Milder invert than Z7Z8 |

---

## 4. Evolution — last ~30 days (19 Aug → 18 Sep 2026)

### 4.1 Rates (%)

| date | Z26 | H27 | M27 | U27 | Z27 | H28 | M28 | U28 | Z28 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-08-19 | 2.800 | 2.935 | 3.000 | 3.010 | 2.990 | 2.975 | 2.970 | 2.970 | 2.980 |
| 2026-08-20 | 2.785 | 2.910 | 2.970 | 2.980 | 2.960 | 2.950 | 2.945 | 2.950 | 2.960 |
| 2026-08-21 | 2.780 | 2.900 | 2.960 | 2.970 | 2.955 | 2.945 | 2.945 | 2.950 | 2.960 |
| 2026-08-24 | 2.810 | 2.945 | 3.010 | 3.020 | 2.995 | 2.980 | 2.970 | 2.970 | 2.975 |
| 2026-08-25 | 2.780 | 2.890 | 2.945 | 2.950 | 2.930 | 2.915 | 2.910 | 2.910 | 2.920 |
| 2026-08-26 | 2.785 | 2.900 | 2.955 | 2.960 | 2.940 | 2.925 | 2.920 | 2.925 | 2.940 |
| 2026-08-27 | 2.790 | 2.915 | 2.980 | 2.995 | 2.975 | 2.960 | 2.955 | 2.955 | 2.965 |
| 2026-08-28 | 2.810 | 2.950 | 3.030 | 3.055 | 3.035 | 3.015 | 3.005 | 3.000 | 3.005 |
| 2026-08-31 | 2.815 | 2.975 | 3.065 | 3.095 | 3.080 | 3.065 | 3.055 | 3.050 | 3.055 |
| 2026-09-01 | 2.835 | 3.000 | 3.095 | 3.125 | 3.110 | 3.090 | 3.080 | 3.075 | 3.080 |
| 2026-09-02 | 2.865 | 3.055 | 3.155 | 3.180 | 3.160 | 3.140 | 3.130 | 3.125 | 3.130 |
| 2026-09-03 | 2.845 | 3.020 | 3.110 | 3.130 | 3.110 | 3.090 | 3.080 | 3.080 | 3.085 |
| 2026-09-04 | 2.830 | 3.005 | 3.095 | 3.115 | 3.095 | 3.075 | 3.070 | 3.075 | 3.085 |
| 2026-09-07 | 2.855 | 3.045 | 3.145 | 3.175 | 3.160 | 3.140 | 3.130 | 3.130 | 3.140 |
| 2026-09-08 | 2.845 | 3.035 | 3.135 | 3.165 | 3.155 | 3.140 | 3.130 | 3.130 | 3.135 |
| 2026-09-09 | 2.875 | 3.095 | 3.220 | 3.265 | 3.265 | 3.250 | 3.235 | 3.230 | 3.230 |
| 2026-09-10 | 3.010 | 3.300 | 3.445 | 3.485 | 3.460 | 3.420 | 3.385 | 3.365 | 3.350 |
| 2026-09-11 | 3.025 | 3.310 | 3.435 | 3.465 | 3.435 | 3.395 | 3.365 | 3.350 | 3.345 |
| 2026-09-14 | 3.075 | 3.405 | 3.555 | 3.595 | 3.565 | 3.515 | 3.470 | 3.445 | 3.425 |
| 2026-09-15 | 3.020 | 3.340 | 3.480 | 3.525 | 3.510 | 3.475 | 3.440 | 3.420 | 3.410 |
| 2026-09-16 | 3.000 | 3.300 | 3.430 | 3.460 | 3.435 | 3.400 | 3.375 | 3.360 | 3.355 |
| 2026-09-17 | 3.015 | 3.315 | 3.450 | 3.480 | 3.450 | 3.410 | 3.380 | 3.360 | 3.350 |
| 2026-09-18 | 3.050 | 3.380 | 3.540 | 3.585 | 3.565 | 3.530 | 3.495 | 3.470 | 3.455 |

### 4.2 Cumulative rate change from 19 Aug (bp)

| date | Z26 | H27 | M27 | U27 | Z27 | H28 | M28 | U28 | Z28 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-08-19 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| 2026-08-27 | −1.0 | −2.0 | −2.0 | −1.5 | −1.5 | −1.5 | −1.5 | −1.5 | −1.5 |
| 2026-09-09 | +7.5 | +16.0 | +22.0 | +25.5 | +27.5 | +27.5 | +26.5 | +26.0 | +25.0 |
| 2026-09-10 | +21.0 | +36.5 | +44.5 | +47.5 | +47.0 | +44.5 | +41.5 | +39.5 | +37.0 |
| 2026-09-14 | +27.5 | +47.0 | +55.5 | +58.5 | +57.5 | +54.0 | +50.0 | +47.5 | +44.5 |
| 2026-09-18 | **+25.0** | **+44.5** | **+54.0** | **+57.5** | **+57.5** | **+55.5** | **+52.5** | **+50.0** | **+47.5** |

**30d selloff shape:** peak/shoulder (U27/Z27) **+57.5 bp**; Z28 **+47.5**; Z26 only **+25**. Front lag, peak lead, reds lag peak → inversion.

### 4.3 Spreads over the window (bp, back − front)

| date | Z28−Z27 | U27−Z26 | U27−Z27 | U27−Z28 | H27−Z26 |
|---|---:|---:|---:|---:|---:|
| 2026-08-19 | −1.0 | +21.0 | +2.0 | +3.0 | +13.5 |
| 2026-08-27 | −1.0 | +20.5 | +2.0 | +3.0 | +12.5 |
| 2026-09-09 | −3.5 | +39.0 | +0.0 | +3.5 | +22.0 |
| 2026-09-10 | **−11.0** | +47.5 | +2.5 | +13.5 | +29.0 |
| 2026-09-14 | **−14.0** | +52.0 | +3.0 | +17.0 | +33.0 |
| 2026-09-15 | −10.0 | +50.5 | +1.5 | +11.5 | +32.0 |
| 2026-09-18 | **−11.0** | **+53.5** | +2.0 | +13.0 | +33.0 |

**Z28−Z27 over ~30d:** −1.0 → −11.0 (**−10 bp**). Short-spread P&L ≈ **+10 bp**/DV01.
YTD most inverted in window: **−14.0 on 2026-09-14**.

ECB meeting reference in GS note: **10 Sep 2026** — single day Z7Z8 −3.5 → −11.0 (−7.5 bp; short +7.5).

---

## 5. Z27Z28 distribution (YTD and 30d)

### YTD (2026-01-02 → 2026-09-18, 183 sessions)

| Stat | Z28 − Z27 (bp) |
|---|---:|
| Last | −11.0 |
| Min (most inverted) | **−14.0** (2026-09-14) |
| Max (most steep) | **+25.0** |
| Mean | +6.5 |
| Days inverted (&lt; 0) | 48 / 183 |
| First invert YTD | 2026-05-11 |
| Recent sustained turn | ~2026-08-27 (summary) |
| Percentile (fraction *more* inverted than last) | ~1% |

### Skew from −11 for a fresh short

| Path | bp | Implication |
|---|---:|---|
| Right-way to YTD floor (−14) | **3.0** | Thin residual |
| Wrong-way to flat (0) | **11.0** | |
| Wrong-way to YTD max (+25) | **36.0** | |
| Barclays target (PDF) | **−35** | **Outside sample** (min −14) — assertion |

---

## 6. Beta / protection analysis

OLS β of daily rate changes (bp). Windows with n≥8; Sep10-only window too short (NaN).

| window | n | β(Z28\|U27) | β(Z27\|U27) | β(Z28\|Z27) | β(Z28\|Z26) | β(U27\|Z26) | β(Z27\|Z26) | corr(Z28,U27) | corr(U27,Z26) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| last_30d | 23 | **0.65** | 0.96 | 0.69 | 1.07 | **1.80** | 1.66 | 0.94 | 0.94 |
| last_21_sessions | 21 | **0.65** | 0.96 | 0.69 | 1.06 | **1.79** | 1.65 | 0.94 | 0.94 |
| YTD | 183 | 0.70 | 0.93 | 0.76 | 0.67 | 1.01 | 0.92 | 0.95 | 0.94 |
| since 2026-08-01 | 35 | **0.69** | 0.97 | 0.73 | 1.18 | **1.82** | 1.71 | 0.94 | 0.94 |
| since 2026-08-27 | 17 | **0.64** | 0.96 | 0.68 | 1.01 | **1.75** | 1.61 | 0.94 | 0.93 |

### Conditional (YTD daily)

| Condition | n | mean ΔZ27 | mean ΔZ28 | mean Δ(Z28−Z27) |
|---|---:|---:|---:|---:|
| U27 up &gt; +0.5 bp | 87 | +5.22 | +3.93 | **−1.30** |
| U27 down &lt; −0.5 bp | 77 | — | — | **+0.97** |
| Z26 up &gt; +0.5 bp | 87 | — | — | **−1.28** |

**Interpretation for the trade thesis:**

1. **U27 is the hawkish instrument:** β(U27\|Z26) ≈ **1.8** since August (high-β to front).
2. **Z28 is relatively protected vs the peak:** β(Z28\|U27) ≈ **0.65–0.70**.
3. On peak selloff days, Z28 lags Z27 → **Z28−Z27 falls** (mean −1.3 bp) → **short flattener prints**.
4. Contrast — **recv U27 / pay Z26** fails the same sample: U27−Z26 at YTD max (+53.5); β&gt;1 means Z26 under-hedges a belly receive. Different gap, different result.

---

## 7. Trade card — short Z27Z28 flattener

| Field | Value |
|---|---|
| Structure | Receive **IMZ27** / pay **IMZ28** (DV01-matched) |
| Spread mark | Z28 − Z27 = **−11.0 bp** (18-Sep) |
| Thesis | Peak (U27/Z27 shoulder) does hawkish work; further belly (Z28) lags → invert more |
| Recent P&L (short) | ~30d **+10 bp**; since 27-Aug **+10 bp**; post-ECB week 10→18 Sep **0** (both +10.5) |
| Biggest day | 10-Sep: spread −7.5 bp (short **+7.5**) |
| Cross-curve Z28−Z27 | Euribor **−11.0**; SOFR **−13.5**; SONIA **−13.5** (EUR less inverted) |
| Sell-side refs | Barclays ERZ7Z8: entry ~−13, target **−35**, stop 0 (front−back sign); GS ECB “protects belly” narrative |

### Prior book verdict (for challenge, not gospel)

Mechanism/betas **support** the expression. **Initiate at −11 is poor skew**
(3 bp to YTD floor, 11 bp to zero, 36 bp to YTD steep max). Prefer add on
steepener dips, EUR vs SOFR/SONIA Z7Z8 if “euro catch-up,” or treat as
residual of a position opened nearer the late-Aug turn — not a new full-size
short into the floor. Barclays −35 is outside observed history.

---

## 8. What the evaluating agent should do

1. Recompute from `panel.csv` if needed; do not trust memory for levels.
2. Stress: what if terminal (U27) mean-reverts 20–40 bp — path of Z7Z8?
3. DV01 / roll / IMM date check for IMZ27 vs IMZ28.
4. Compare stop/target to **sample** (−14 floor), not Barclays −35.
5. Optional: OIS meeting strip for ECB (not in this cache) — futures only here.
6. Optional: fly U27−2·Z27+Z28 or U27 vs Z28 as alternate expressions.
7. Keep spread sign **back − front** unless explicitly remapped.

### Minimal recompute

```bash
python3 - <<'PY'
import pandas as pd, json
asof = "2026-09-18"
p = pd.read_csv("data/cache/stir_curves/panel.csv", parse_dates=["date"])
w = (p[p.curve=="EURIBOR"].pivot_table(index="date", columns="contract", values="rate", aggfunc="last")
     .sort_index().loc[:asof])
s = (w["Z28"] - w["Z27"]) * 100
print(s.loc["2026-08-19":].tail())
print("last", s.loc[asof], "ytd min", s.loc["2026-01-01":].min())
PY
```

---

## 9. Snapshot JSON pointer

Full pack: `data/cache/stir_curves/eur_z27z28_handoff_pack.json`
(asof, levels, 30d changes, YTD stats, betas, conditionals, SOFR/SONIA analogues).
