# Is Jun’28−Jun’27 just Dec’28−Dec’27 with a better entry?

**Claim:** short **M28 − M27** (Jun’28 − Jun’27) is the same trade as short
**Z28 − Z27** (Dec’28 − Dec’27), only cheaper to enter.

As-of **2026-09-18**. Desk = back − front.  
Figure: `research/notes/figures/eur_m7m8_vs_z7z8_same_trade.png`

| | M28−M27 | Z28−Z27 | Box (M − Z) |
|---|---:|---:|---:|
| Last | **−4.5** | **−11.0** | **+6.5** |
| YTD %ile | 47th | 2nd | **100th** (widest YTD) |

The **+6.5 bp** gap *is* the “better entry.” It is also the **widest** that
gap has been all year — M is as *uncoupled* from Z as the sample gets.

---

## 1. Same family — not the same two contracts

Both are **1y calendars on the Euribor strip**, one quarter apart:

| Leg | M7M8 | Z7Z8 |
|---|---|---|
| Pay (near) | **Jun’27** — shoulder, 4.5 bp under U27 peak | **Dec’27** — co-peak, 2 bp under U27 |
| Recv (far) | **Jun’28** — first post-peak June | **Dec’28** — further reds |

If the strip is a static snake, M7M8 **rolls into** today’s Z7Z8 in ~6 months.
That is the only precise sense in which they are “the same trade later.”

They are **not** a relabeling of the same legs. Jun’27 is still on the hike
path; Dec’28 is the lagging belly. Substituting one calendar for the other
changes *which* year-end the ECB has to “spare.”

---

## 2. Empirically: cousins YTD, weaker substitutes since August

Daily **Δ(M28−M27) vs Δ(Z28−Z27)**:

| Sample | β(ΔM \| ΔZ) | corr | R² | Tracking error |
|---|---:|---:|---:|---:|
| **YTD** | **1.01** | 0.83 | **0.69** | 1.3 bp/day |
| Mar+ | 1.01 | 0.83 | 0.70 | 1.4 |
| **Aug+** | **0.61** | 0.66 | **0.43** | 1.4 |
| Post-ECB (10–18 Sep) | 0.69 | 0.76 | 0.58 | 2.5 |

YTD, when Z7Z8 moves 1 bp, M7M8 moves ~1 bp on average — **~70% shared**.
Since August only **~43%** of M’s daily variance is Z. One-for-one replacement
leaves **~1.3 bp/day** of residual (not noise: ECB week residual was large).

On YTD days Z inverts ≥1 bp, M also inverts **84%** of the time. **August:
57%.** The lockstep broke in the live regime.

---

## 3. “Better entry” is true — and that *is* the disagreement

| Test | Result |
|---|---|
| Outright percentile | **True** — 47th vs 2nd; 13 bp vs 3 bp to sample floor |
| Box M−Z at +6.5 | **True, and extreme** — 100th %ile: M is the *least* inverted vs Z in 2026 |
| Therefore a substitute you just prefer on skew | Only if you think the box **mean-reverts** (M catches down toward −11) |

If they were the same trade, **short M / cover Z** (short the box) is the RV
expression of “better entry.” That bet is: the +6.5 closes. It is **not**
free — August says the box can stay open or widen because Jun’28 still
trades with the hike path (β(M28\|U27)≈0.83 vs β(Z28\|U27)≈0.69).

---

## 4. Swap scorecard — replacing Z7Z8 with M7M8 has cost

| Hold to 18-Sep | short M7M8 | short Z7Z8 | Swap (M minus Z) |
|---|---:|---:|---:|
| From 1-Mar | +19.5 | +28.0 | **−8.5** |
| From 1-Aug | **−0.5** | **+10.5** | **−11.0** |
| From 27-Aug | +2.0 | +10.0 | **−8.0** |
| From ECB 10-Sep | −1.5 | 0 | **−1.5** |

Same direction on the ECB **day** (both −7.5). **Not** the same after: Z held
−11, M retraced to −4.5. That week is the claim failing in real time.

---

## 5. Verdict on the claim

| Piece | Grade |
|---|---|
| Same *story* (1y flatten past the peak) | **Mostly** |
| Same *instrument* | **No** — adjacent calendars; Jun’28 ≠ Dec’28 |
| Better *outright* entry | **Yes** |
| Therefore interchangeable | **No** in the live sample (R² 0.43 since Aug; swap −8 to −11 bp) |

**Use M7M8 as a related, cheaper-looking calendar**, not as a relabel of
Z7Z8. You get better skew and ~7 bp of *static* rolldown toward today’s
Z7Z8 **only if** Jun’28 starts to lag like Dec’28 already does. Until that
β gap closes, “same trade, better entry” overstates it: you are long the
**box** (M less inverted than Z) at a YTD extreme, which is a view, not a
free upgrade.

Implementation if you believe the box should compress: **short M7M8 vs a
smaller/no Z7Z8** (or explicit short M / long Z). Do not blindly flatten
M7M8 1:1 as if it were ERZ7Z8 at −4.5 instead of −11.
