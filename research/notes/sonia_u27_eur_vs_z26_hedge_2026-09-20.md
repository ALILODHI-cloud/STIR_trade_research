# Pay EUR U27 vs pay SONIA Z26 as the hedge for recv SONIA U27

**Question:** Given short U27−Z26 is mostly a peak-down bet and Z26 no longer
fully hedges selloffs, is **recv J8U27 / pay IMU27** better?

**As-of 2026-09-18.**  
Figure: `research/notes/figures/sonia_u27_eur_hedge_vs_z26_2026-09-18.png`

| Structure | Legs | Spread | Last | YTD pct | Room down / up |
|---|---|---|---:|---:|---:|
| Short slope | recv J8U27 / pay J8Z26 | U27−Z26 | **+63** | **100th** | **83.5 / 0** |
| Short cross | recv J8U27 / pay IMU27 | SONIA−EUR U27 | **+129.5** | **22nd** | **17 / 34** |

---

## 1. As a *selloff hedge* since August — yes, EUR is better

On days SONIA U27 sells off (&gt;+0.5 bp):

| Sample | recv U27 | pay Z26 (offset) | short slope P&amp;L | pay EUR (offset) | short cross P&amp;L |
|---|---:|---:|---:|---:|---:|
| **Aug–Sep** | −124.5 | +50 (**40%**) | **−74.5** | +110.5 (**89%**) | **−14.0** |
| Mar–Sep | −549 | +438 (80%) | −110.5 | +424 (77%) | −124.5 |

Same story in the recent episodes:

| Episode | short U27−Z26 | short SONIA−EUR |
|---|---:|---:|
| Late Aug (26-Aug→2-Sep) | **−14** | **−2.5** |
| Sep peak run (4→14 Sep) | **−24** | **−1** |
| Held 1-Aug → 18-Sep | **−42** | **+9** |

β(SONIA U27 \| EUR U27) since Aug ≈ **1.16** — nearly parallel peaks.  
β(SONIA U27 \| Z26) since Aug ≈ **2.03** — peak outruns Dec’26.

So if the complaint is “Z26 doesn’t protect me when the strip sells,”
**paying Euribor Sep’27 does** (≈1:1). Paying Dec’26 does not.

---

## 2. As an *entry / RV short* here — no, cross is late

| | Short slope | Short cross |
|---|---|---|
| Skew for initiating short | **Best** (at YTD max) | **Poor** (21st %ile) |
| Wrong-way room | 0 bp | **34 bp** to YTD high |
| Right-way room | 83.5 to YTD floor | only **17** to floor |
| Already run since Jul | steepened (short lost) | compressed ~15 (short made ~+15) |

The cross has **already done** the easy compression. Putting it on at +129.5
is chasing a move that is below average with 2:1 adverse skew.

---

## 3. They are not the same trade

| | Short U27−Z26 | Short SONIA−EUR U27 |
|---|---|---|
| Wins when | GBP path into Sep’27 **flattens** (peak comes in vs Dec’26) | GBP Sep’27 **richness vs EUR** compresses |
| March ’26 selloff | Z **over**-hedged (front led) → slope short **won** | EUR lagged → cross short **lost** (−38 in Mar scare) |
| Aug–Sep selloff | Z under-hedges → slope short **loses** | EUR keeps up → cross short ~flat |
| Macro story | Fade BoE hike *path extension* | Fade BoE peak *vs ECB* (relative restriction) |

Paying EUR is a **better parallel hedge** for “I want to receive the SONIA
peak and not die in a joint selloff.” It is **not** a better-priced expression
of “this gap is extreme” — that award still goes to U27−Z26 at +63.

---

## 4. Verdict

| Goal | Prefer |
|---|---|
| Fade an **extreme** GBP curve gap with good short skew | **Still pay Z26** (U27−Z26) |
| Receive SONIA peak and **survive strip selloffs** | **Pay EUR U27** (≈1.0–1.15×) |
| Both (skew + hedge) | Not available at these marks — cross cheap, slope rich; or wait for cross rewiden toward **+145–155** then pay EUR |

**Net:** Your instinct that Z26 is a weak hedge now is right, and EUR is the
better hedge empirically since August. That does **not** make the Sep/Sep
cross the better *trade* at +129.5 — entry skew says the opposite.

JSON: `data/cache/stir_curves/sonia_u27_eur_vs_z26_hedge.json`
