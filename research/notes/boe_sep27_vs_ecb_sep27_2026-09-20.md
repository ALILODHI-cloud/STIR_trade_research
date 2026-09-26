# Long BoE Sep’27 / short ECB Sep’27 (U27 − U27)

**Trade:** receive **J8U27** / pay **IMU27**.  
Spread mark: **SONIA U27 − Euribor U27**.  
P&amp;L ≈ **−Δ(spread)** — wins when the GBP–EUR Sep’27 differential **falls**.

As-of **2026-09-18**. (Not Jun’27 — that is M27.)

---

## Levels

| | Rate | vs policy spot |
|---|---:|---:|
| SONIA U27 (BoE Sep’27) | **4.880%** | +115 bp vs SONIA 3.73 |
| Euribor U27 (ECB Sep’27) | **3.585%** | +108.5 bp vs DFR 2.50 |
| **SONIA − EUR** | **+129.5 bp** | |

Both are the **strip peaks**. Hikes-from-spot into the peak are similar; the
trade is almost pure **cross level**, not a different hike count.

vs Barclays econ anchors (3.75 / 2.75): GBP **+113 bp** above 3.75, EUR
**+83.5** above 2.75 → **~29.5 bp** “excess” GBP — macro rationale for
receiving GBP / paying EUR, but see entry below.

---

## Distribution & path

| | bp |
|---|---:|
| Last | **+129.5** |
| YTD mean | +138.5 |
| YTD min / max | +112.5 / +163.5 |
| Percentile | **21st** |
| Room to floor (further compression) | **17** |
| Room to YTD high (widening) | **34** |

Path: 1-Jul **+144.5** → 27-Aug **+134** → 10-Sep **+137** → 18-Sep **+129.5**.  
Already compressed **~15 bp** since July. Short-diff P&amp;L since Jul **~+15**;
since late Aug **~+4.5**; since 10-Sep **~+7.5**.

β(SONIA U27 \| EUR U27) since Aug ≈ **1.16** (corr 0.92) — use ~1.15× EUR
DV01 vs 1× GBP if you want recent-beta neutral.

---

## Verdict

Same conclusion as the mid-27 version, pinned on **Sep/Sep**:

- **Story:** fine — fade rich BoE peak vs ECB peak / firmer EA restriction.
- **Entry:** late — below YTD mean, ~**2:1 wrong-way skew** (17 down / 34 up).
- **Better peak-fade hedge still:** pay **J8Z26** (U27−Z26 at YTD max +63),
  not pay IMU27 at a cheap cross.

**If putting it on:** recv J8U27 / pay ~1.15× IMU27; prefer add on rewiden
toward **+145–155**; stop **&gt; +150**; target **+115–120** toward the floor.

JSON: `data/cache/stir_curves/boe_sep27_vs_ecb_sep27.json`.
