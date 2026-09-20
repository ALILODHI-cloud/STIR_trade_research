# Pay Euribor mid-2027 peak / receive 1y1y — GS idea in futures

**Thesis (your framing):** the ECB is happy to push the **policy peak** up a
lot; that **spares** the **1y1y**. Express in Euribor futures (no CHF).

**As-of 2026-09-18.** Desk spreads = back − front. DFR **2.50%**.  
Data: `data/cache/stir_curves/panel.csv`.  
Figure: `research/notes/figures/eur_1y1y_vs_peak_2026-09-18.png`  
JSON: `data/cache/stir_curves/eur_1y1y_vs_peak_eval.json`

Compare to prior expressions:
- Failed: recv U27 / pay Z26 (`eur_recv_belly_pay_z26_2026-09-20.md`)
- Prior preferred: short Z28−Z27 (`eur_short_z27z28_2026-09-20.md`)
- GS book trade was CHF−EUR 1y1y (`gs_eur_1y1y_vs_chf_2026-09-20.md`) — no CHF here

---

## 1. Contract map (as of Sep’26)

| Concept | Contracts | Last rate | vs DFR |
|---|---|---:|---:|
| Front | Z26 | 3.050% | +55 |
| **Policy peak (mid-2027)** | **U27** (actual peak); M27 shoulder | **3.585%** / 3.540% | **+108.5** / +104 |
| Near-peak | Z27 | 3.565% | +106.5 |
| **1y1y window** (Sep’27→Sep’28) | U27, Z27, H28, M28, U28 | mean **3.529%** | +103 |
| **Post-peak 1y** (exclude peak) | Z27, H28, M28, U28 | mean **3.515%** | +101.5 |
| Further belly | Z28 | 3.455% | +95.5 |

Why “post-peak 1y” exists: a naive 1y1y basket **includes U27** (the peak).
If you receive that basket and pay U27, most of the peak cancels and you are
left with a diluted short-peak / long-reds book. Cleaner to **define the
protected leg as the year *after* the peak**.

---

## 2. How to do it in futures

Desired P&amp;L when peak ↑ more than 1y1y:

\[
\mathrm{P\&L} \approx +\Delta r_{\mathrm{peak}} - \Delta r_{\mathrm{1y1y}}
\]

= **pay peak / receive 1y1y**.

| # | Expression | Legs (DV01-matched) | Spread to watch | Last |
|---|---|---|---|---:|
| **B (preferred clean)** | pay U27 / recv post-peak 1y | **pay 1× IMU27**; **recv 0.25× each** IMZ27, IMH28, IMM28, IMU28 | U27 − post1y | **+7.0 bp** |
| **C (simplest 2-leg)** | pay U27 / recv Z28 | pay 1× IMU27 / recv 1× IMZ28 | U27 − Z28 | **+13.0 bp** |
| D | pay M27 / recv post1y | pay IMM27 / recv same 0.25× basket | M27 − post1y | +2.5 |
| A (diluted) | pay U27 / recv incl. 1y1y | pay 1× U27 / recv 0.2× U27..U28 | U27 − mean | +5.6 |

**Not** the same as recv U27 / pay Z26 (that *receives* the peak).  
**Close cousin** of short Z28−Z27 (pay Z27 / recv Z28) — same direction,
slightly different peak leg (U27 vs Z27).

---

## 3. Does the mechanism work?

If the ECB “pushes the peak / spares 1y1y,” then β(Δ1y1y \| Δpeak) **&lt; 1**,
and on peak-selloff days pay-peak/recv-1y1y **prints positive**.

| Sample | β(post1y \| U27) | β(Z28 \| U27) | Mean P&amp;L on U27 selloff (&gt;+0.5): B / C / Z7Z8 / failed |
|---|---:|---:|---|
| YTD | **0.84** | **0.70** | **+0.84 / +1.64 / +1.30 / −1.01** |
| Since Aug | **0.86** | **0.68** | **+0.53 / +1.42 / +1.36 / −3.56** |
| Since Mar | 0.83 | 0.69 | +0.96 / +1.85 / +1.47 / −1.13 |

**Mechanism: pass.** Same sample where recv-U27/pay-Z26 **fails**.

### Episodes (P&amp;L bp)

| Episode | pay U27/recv post1y | pay U27/recv Z28 | short Z28−Z27 | recv U27/pay Z26 |
|---|---:|---:|---:|---:|
| Mar hike scare | **+15.1** | **+22.5** | +13.5 | +18.0* |
| Mid Jul | +3.5 | +8.0 | +7.5 | −13.0 |
| Late Aug | +0.9 | +3.0 | +3.0 | −14.0 |
| Sep peak run | +6.0 | +14.0 | +13.0 | −23.5 |
| Post-ECB week | **−0.8** | **−0.5** | 0.0 | −6.0 |

\*March: front led so the *failed* structure also worked — different reason
(Z26 sold more than U27). Since summer the structures diverge hard.

Held Aug 1 → Sep 18: B **+3.2**, C **+10**, Z7Z8 **+10.5**, failed **−39.5**.

---

## 4. Entry / skew — the hard part

Trade wins when **peak − 1y1y rises** (more peak richness). Skew for *initiating*:

| Gap (peak − protected) | Last | YTD pct | Room further rich | Room mean-revert |
|---|---:|---:|---:|---:|
| U27 − post1y | **+7.0** | **90th** | **2.6** to max | **23.7** to min |
| U27 − Z28 | **+13.0** | **98th** | **4.0** | **45** |
| Z27 − Z28 (= −(Z28−Z27)) | **+11.0** | **~98th** | **3.0** | **36** |
| U27 − Z26 (failed long-peak) | +53.5 | 100th | 0 | 62.5 |

So: **directionally this is the right futures expression of the idea**, but
you are **late** — peak is already rich to the post-peak year / Z28. Same
entry problem as short Z7Z8.

Post-ECB week is the warning: peak and reds sold **together** (~+10 across
U27/Z28) → the “spare the 1y1y” gap did **not** widen that week.

---

## 5. Vs previously proposed trades

| | pay U27 / recv 1y1y (this) | short Z28−Z27 (prior) | recv U27 / pay Z26 (failed) |
|---|---|---|---|
| Thesis fit | **Direct** — peak tool vs spared 1y1y | Peak-shoulder vs further belly | Front vs peak (wrong way for this thesis) |
| Selloff β | post1y 0.84 / Z28 0.68 vs U27 | Z28 0.65–0.70 vs U27 | U27 **1.7–1.8** vs Z26 |
| Aug+ selloff P&amp;L | **+** | **+** | **−** |
| Entry skew | Late (90–98th) | Late (~floor of Z7Z8) | Late the other way (max steep) |
| Practical | 5-leg basket or 2-leg vs Z28 | Clean 2-leg calendar | Don’t |

**Ranking for the GS “peak does the work / belly spared” story on *this*
strip:**

1. **pay U27 / recv Z28** (or short Z28−Z27) — mechanism ✓, entry late  
2. **pay U27 / recv post-peak 1y basket** — same story, slightly milder β gap  
3. **recv U27 / pay Z26** — rejects the thesis empirically  

Difference between (1) and short Z7Z8 is small: U27 vs Z27 as the pay leg.
U27 is the true peak (+2 bp over Z27); Z7Z8 pays the co-peak. Prefer **pay
U27 / recv Z28** if you want the purest “policy peak” leg; prefer **Z7Z8**
if you want the liquid calendar already in sell-side notes (Barclays ERZ7Z8).

---

## 6. Verdict

**How:** pay **IMU27** (mid-27 policy peak), receive either **IMZ28** (simple)
or **0.25× (Z27+H28+M28+U28)** (post-peak 1y). That *is* the futures
translation of “peak up a lot, 1y1y spared.”

**Evaluate:** mechanism holds in YTD/Aug selloffs (β&lt;1, positive P&amp;L). Entry
does **not** — peak already 90–98th %ile rich to the protected leg; post-ECB
week showed no spare. Same conclusion as short Z7Z8: right idea, **poor
fresh-entry skew**. Do not confuse with recv-peak/pay-Z26 (opposite trade,
failed).

**If adding:** prefer on a **re-steepening** of post-peak (U27−Z28 back toward
~0 to +5) or a peak selloff that *doesn’t* drag Z28; stop if peak−Z28
compresses through ~+8 on a joint selloff. Target further invert toward
prior extremes (~+17 U27−Z28) only as a runner, not the base case from here.
