# Long BoE mid-2027 / short ECB 2027 — evaluation

**As-of 2026-09-18.** Desk spread = back − front for curve gaps; this note is a
**cross-currency level** trade.

## Trade interpretation

| Plain language | STIR legs |
|---|---|
| Long BoE mid-2027 | **Receive SONIA Jun’27 (`J8M27`)** — want GBP mid-27 rates **down** |
| Short ECB 2027 | **Pay Euribor matched 2027** — want EUR 2027 rates **up** (or down less) |

**Preferred match:** `J8M27` vs `IMM27` (true mid-year).  
**Peak variant:** `J8U27` vs `IMU27` (both strip peaks).  
**Calendar’27 basket:** pay average of EUR H27–Z27 vs receive SONIA M27/U27.

**P&amp;L (1:1 DV01):** `−Δ(SONIA − EUR)` on the matched contracts  
= **short the cross differential**. Wins when GBP rates fall vs EUR (or EUR
sells off vs GBP).

Data: `data/cache/stir_curves/long_boe_mid27_short_ecb27.json`.

---

## What’s priced

| Contract | SONIA | Euribor | SONIA − EUR (bp) |
|---|---:|---:|---:|
| Z26 | 4.250 | 3.050 | +120.0 |
| H27 | 4.630 | 3.380 | +125.0 |
| **M27** | **4.820** | **3.540** | **+128.0** |
| U27 | 4.880 | 3.585 | +129.5 |
| Z27 | 4.860 | 3.565 | +129.5 |

vs spots: SONIA M27 **+109 bp** / U27 **+115**; Euribor M27 **+104** / U27
**+108.5** — similar hike-from-spot into mid/peak 2027; the cross is mostly
**level**, not a different hike *count*.

### Cross history (SONIA − EUR, bp)

| Tenor | Last | YTD mean | YTD min | YTD max | %ile | Room down | Room up |
|---|---:|---:|---:|---:|---:|---:|---:|
| **M27** | **+128** | +139 | +114 | +166 | **18th** | **14** | **38** |
| U27 | +129.5 | +138.5 | +112.5 | +163.5 | 21st | 17 | 34 |
| Z27 | +129.5 | +137.6 | +111 | +161.5 | 19th | 18.5 | 32 |

**M27 path:** 1-Jul **+145** → 27-Aug **+133.5** → 10-Sep **+134** → 18-Sep
**+128**. Differential has already **compressed ~17 bp** since July.

**Recent trade P&amp;L** (recv SONIA / pay EUR): about **+5 to +6 bp** since
late Aug / ECB week on M27; U27/Z27 similar or slightly better.

**β(SONIA \| EUR) since Aug:** M27 **1.11**, U27 **1.16** (corr ~0.91–0.92) —
1:1 DV01 is a fair starting hedge; slight GBP overweight on selloffs.

---

## vs the PDF macro (why you might like it)

| Support | Friction |
|---|---|
| Bank Rate base **3.75%** hold (Barclays Econ) vs market M27 **4.82** / U27 **4.88** — large GBP “above econ” gap | Cross **already** below YTD mean; you’re joining compression, not initiating at richness |
| ECB DFR at top-of-neutral; staff growth resilient at high rates → EUR terminal can stay firm (supports **pay EUR**) | Barclays Rates wants **more EUR Z7Z8 flattening** (EUR cuts) — fights “short ECB 2027” if that means EUR rates *fall* |
| GS: soft MPC urgency / restrictive judgment → caps BoE path (supports **recv GBP**) | GS Nov hike / M7M8 flatten is *more* near-term GBP hike premium — opposite of receiving mid-27 if the path extends |
| Econ “excess” GBP vs EUR over 3.75/2.75 still **~28–30 bp** on M27/U27 | That excess is **not** showing as a rich liquid cross — M27 cross is **cheap vs its own YTD** |

---

## Skew / risk-reward for initiating *now*

For **short M27 cross** (+128):

- Right-way to YTD mean (+139): already **past** it (−11 bp the wrong side of mean for a fresh short… wait)

Careful: short the cross profits when cross **falls**.  
Last +128, mean +139 → last is **already 11 bp below mean**.  
Further right-way to min (+114): only **~14 bp**.  
Wrong-way to max (+166): **~38 bp**.

**Skew is hostile for a new short** (~14 reward to floor / ~38 risk to YTD
high). Same shape for U27/Z27.

You’ve already earned the easy bit of the trade (Jul +145 → +128). Remaining
edge is thin versus re-steepening risk if energy/CB shocks re-widen GBP–EUR.

---

## Verdict

| | |
|---|---|
| Directional story (recv rich GBP 2027 vs firmer EUR) | **Coherent** with Bank Rate 3.75 vs market ~4.8 and ECB-at-restriction narrative |
| Entry on the liquid cross | **Late** — 18th %ile, below mean, ~14 bp to YTD floor |
| Fit to prior “fade BoE peak” package | **Same direction** as recv J8U27, but hedge is **pay EUR 2027** not pay Z26; cross hedge is the weaker RV leg *at these levels* |
| vs recv U27 / pay Z26 | Own-curve gap still at **YTD max (+63)** — better skewed hedge than EUR |

**Net:** The trade is the right *economic* relative (long GBP mid-27 rates /
short EUR 2027) but **poor initiate skew** on SONIA−EUR M27/U27 after the
Jul–Sep compression. Prefer:

1. **Hold/trim** if already on from wider differentials (~140–150).  
2. **Re-enter** on cross rewidening toward **+145–155** (closer to Jul / YTD
   upper distribution).  
3. Or keep **recv J8M27 or J8U27 / pay J8Z26** as the peak fade with the
   better-skewed hedge, and add EUR only as a smaller overlay when the cross
   is rich again.

**Implementation if you still put it on:** recv **J8M27** / pay **IMM27**,
size EUR ≈ 1.1× GBP DV01 (match recent β), stop if M27 cross **&gt; +145**,
target zone **+115–120** (toward YTD min, not through it blindly).
