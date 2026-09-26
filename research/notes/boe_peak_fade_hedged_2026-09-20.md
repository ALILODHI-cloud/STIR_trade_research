# Fade BoE peak + an RV-sensible hedge

**Goal:** Receive the SONIA peak (**J8U27**) without naked terminal risk; hedge
leg should itself be a level you’d want to be short/long for RV reasons.

As-of **2026-09-18**. Convention: back − front.  
Pack: `data/cache/stir_curves/boe_peak_fade_hedged.json`.

---

## What “fade the peak” means

SONIA **U27 = 4.880%** (strip peak, **+115 bp** vs spot 3.73).  
Barclays Econ base case: Bank Rate **hold 3.75%**. Market peak is
**~113 bp** above that anchor. Fading = **receive J8U27**.

You need a hedge that (a) kills parallel STIR beta and (b) is not a junk
short — ideally a gap that is **rich for the side you’re on**.

---

## Hedge candidates (screened)

| Structure | Spread now | YTD context | Hedge quality | RV sense? |
|---|---:|---|---|---|
| **A. vs own Z26** — recv U27 / pay Z26 | U27−Z26 **+63** | **YTD max** (mean +10) | β(U27\|Z26)≈**2.0** since Aug — under-hedges 1:1 on selloffs; still flattens path risk | **Best** — shorting the richest front→peak gap |
| **B. vs wings (fly)** — recv U27, pay ½ Z26 + ½ Z28 | fly Z26−2U27+Z28 **−78.5** | **YTD min** | Classic curvature; both wings | **Best skew** — fly mean-reversion to ~0 is huge if peak settles |
| **C. vs Euribor U27** — recv J8U27 / pay IMU27 | U27ˢ−U27ᵉ **+129.5** | Mean **+138.5**, **21st %ile** | corr≈0.92, β≈1.16 — good beta hedge | **Weak entry** — GBP peak vs EUR already *cheap* vs YTD, not rich |
| **D. vs SOFR U27** | +14 | Mean +33, 17th %ile | Decent beta | Same problem — relative already compressed |

**Economist cross-check:** market peak − econ terminal is **+113 bp GBP** vs
**+83.5 bp EUR** (using 3.75 / 2.75) → **~30 bp** “excess” GBP. That supports
fading *BoE* vs *ECB* in principle, but the **liquid U27−U27 spread is not
trading that richness** (it’s below its YTD average). Don’t force C at +129.

---

## Recommended implementations

### 1. Primary: receive U27 / pay Z26 (path-extension fade)

| Leg | Action |
|---|---|
| Peak fade | **Receive J8U27** |
| RV hedge | **Pay J8Z26** |

- Short **U27 − Z26** at **+63 (YTD max)**.
- Thesis: hike path into Sep’27 stops extending; peak mean-reverts toward
  Dec’26 / toward ~3.75 world.
- **RV sense of hedge:** Z26 still **+52 bp** vs spot (hikes priced) but the
  *gap* is the mispricing — you’re not paying an inverted red.
- **Risk:** β≈2 — on a Z26 +10 bp selloff, U27 often +20 → short gap loses
  ~10. Size smaller or use **1.5–2× Z26 vs 1× U27** if you want beta-neutral
  to recent regime (then it’s less of a pure flattener and more hedged
  receive peak).

P&amp;L (1:1) ≈ **−Δ(U27 − Z26)**.

### 2. Best skew variant: receive U27 vs Z26+Z28 wings

| Leg | Action |
|---|---|
| Peak | **Receive 2× J8U27** |
| Wings | **Pay 1× J8Z26 + 1× J8Z28** |

- Long the fly from **−78.5 (YTD floor)** toward 0 / mean (~−9).
- **RV sense:** fades peak *and* is long the post-peak steepener via Z28
  (Z28−Z27 already −13.5 — wing includes “Z7Z8 has run” as a *long*
  steepener exposure if you think of Z28 vs Z27 separately; as a package
  it’s curvature).
- Cleanest “fade peak with structure” if you don’t want to take a view on
  Dec’26 alone.

### 3. Cross-curve overlay (only as add-on): short GBP path vs EUR path

If you want an **ECB leg** that is actually rich:

| Leg | Action |
|---|---|
| GBP | Short U27−Z26 (recv J8U27 / pay J8Z26) |
| EUR | Long U27−Z26 (pay IMU27 / recv IMZ26) |

- Relative **(U27−Z26)_GBP − (U27−Z26)_EUR = +9.5 bp**, near YTD max
  **+10.5**.
- Thesis: GBP front→peak has run harder than EUR; fade GBP extension, keep
  EUR steepener.
- This **is** the BoE-vs-ECB idea with gaps that are actually at extremes —
  unlike naked U27 vs U27.

Do **not** use recv J8U27 / pay IMU27 alone as the main hedge *at current
levels* (wrong percentile).

---

## What not to use as the hedge

| Hedge | Why not |
|---|---|
| Pay SONIA Z28 only | You’re shorting an already-inverted back (Z28−U27 −15.5 near floor) — fighting the “Z7Z8 has run” conclusion |
| Pay EUR U27 alone at +129.5 U27 spread | Relative peak not rich vs history; better used later if U27ˢ−U27ᵉ revisits 150–160 |
| Pay M7M8 / short Z7Z8 | GS’s gap; already run; not a peak fade |

---

## Practical package (suggested)

**Core (2/3 risk):** receive **J8U27** / pay **J8Z26** at +63, optional
**1.5× Z26** if you want closer beta match to post-Aug regime.  

**Satellite (1/3 risk):** same GBP flattener vs **long EUR U27−Z26** (relative
+9.5), *or* replace core with the **Z26/U27/Z28 fly** if you prefer
curvature skew over a single front hedge.

**Invalidation:** U27−Z26 holds above ~60 into further energy/CB shocks with
β staying ~2 (path still extending). **Take-profit zone:** gap back toward
**+20–30** (still steep vs YTD mean +10) or fly back toward **−30/−20**.

---

## Bottom line

Fade BoE peak = **receive U27**. The hedge that *also* makes RV sense today
is **pay Z26** (gap at YTD max), or **both wings** (fly at YTD min) — not
pay Euribor U27 at the current cross. If you want ECB in the structure, put
it on **U27−Z26 relative** (GBP short / EUR long), not on the peaks 1:1.
