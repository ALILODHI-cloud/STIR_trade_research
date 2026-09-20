# BoE vs ECB post-peak reversal RV — scrutiny + implementation

**Idea (yours):** Cumulative hike *reversals* / cuts from the cycle peak should be
**greater for the BoE than the ECB**, because the euro-area economy is stronger
and the ECB’s starting point is less restrictive. Express as a **curve RV**, not
outright duration.

**As-of:** 2026-09-18 futures (`data/cache/stir_curves/`). Spots: ECB DFR
**2.50%**, SONIA **3.7303%**, Bank Rate **3.75%** (Barclays Econ Weekly).

**Convention:** spread = **back − front** (bp). Negative = inverted. Short a
post-peak gap = receive front / pay back of that gap.

**Sources used (on disk):**
- GS *Hiking More or Less* (18-Sep-26)
- Barclays *Global Economics Weekly: High oil…* (11-Sep-26)
- Barclays *Global Rates Weekly: On the brink* (10-Sep-26)
- Barclays *Global Rates Weekly: Not enough to break* (17-Sep-26)

Arithmetic: `data/cache/stir_curves/boe_vs_ecb_reversal_rv.json`.

---

## 1. Thesis → testable market claim

| Macro claim | Market implication |
|---|---|
| EA growth stronger / more resilient at high rates | ECB keeps terminal high longer → **fewer** cuts from peak in EUR |
| ECB less restrictive *starting* point (DFR at top of neutral) | ECB can hike into restriction without as much later unwind *or* hikes are “catch-up”; either way **less** post-peak easing than BoE |
| BoE starts tighter (Bank Rate 3.75% vs DFR 2.50%) and/or UK weaker relative | From peak, **more** cumulative cuts in GBP |

**Priced metric (primary):**
`cut = Z28 − peak` (bp, usually negative).  
**Relative:** `rel_cut = cut_SONIA − cut_EURIBOR`.  
More negative `rel_cut` = market already prices **more** GBP reversal than EUR.

**Secondary (liquid STIR expression):**  
`rel_z7z8 = (Z28−Z27)_SONIA − (Z28−Z27)_EUR`.  
Same sign convention; highly related to post-peak shape.

Your directional bet if you think the *outcome* gap exceeds what is priced:
**rel_cut and/or rel_z7z8 should fall** (GBP inverts / cuts from peak *more*
relative to EUR).

---

## 2. What the reports actually say (not what we need them to say)

### Supports parts of the macro story

| Claim | Evidence in PDFs | Verdict |
|---|---|---|
| ECB starting point less restrictive | Barclays Econ: DFR hike to **2.50%** = **upper bound of nominal neutral**; “moves into restrictive territory.” | **Supported** |
| EA growth resilient at higher rates | Barclays Econ: Q2 GDP **0.6% q/q**; Rates NE: ECB staff **2027 growth at trend (1.4%) even off ~3% terminal** (~100bp above mid-neutral). | **Supported** |
| BoE already tighter in levels | Bank Rate **3.75%** (hold base case); SONIA ~3.73%. Far above ECB DFR. | **Supported** |
| BoE not eager to hike | GS: MPC still calls policy **restrictive**, muted passthrough, limited urgency; economists Nov hike but soft messaging. Barclays Econ: **hold 3.75%**, hawkish tone / dissents. | **Mixed** — hold ≠ “must reverse hard later” |

### Pushback / contradictions

| Issue | What reports say | Why it hurts the RV |
|---|---|---|
| UK growth not weak | Barclays Econ: UK GDP forecast **revised up to 1.3%**; July GDP strong. | Undercuts “BoE must ease more because UK soft.” |
| EUR underprices reversal (Barclays Rates) | *On the brink*: terminal ~**100bp above ECB neutral**, yet “**virtually nothing**” in reversals (~**13bp** cuts 2027→2028). Initiate **ERZ7ERZ8 flattener**. | They want **more EUR** post-peak flattening — **opposite EUR leg** to “EUR cuts less than GBP.” |
| GS EUR belly protection | Hawkish ECB **insulates** longer forwards / long EUR 1y1y vs CHF. | Consistent with *less* EUR cut premium — aligns with you on EUR — but their trade is vs CHF, not vs GBP. |
| GS UK | Nov hike → flatten **M7M8** (front-end), QT bull-flattens *gilts*. | Not a “GBP cuts from peak vs EUR” call; front hike premium, not reds. |
| Economist terminals vs market | Barclays CB table: BoE **3.75** hold through ’27; ECB **2.75** after Dec hike. Market peaks: SONIA U27 **4.88**, Euribor U27 **3.58**. | Market is **far above** BoE econ terminal (~+113bp) vs EUR (~+83bp above 2.75). Bigger story may be **GBP hike overpricing vs staff**, not relative cut shape. |

**Sell-side net:** Macro *levels* (ECB less restrictive start; EA can grow through higher rates) are real. The **cleanest sell-side curve trade in the pack is Barclays’ EUR Z7Z8 flattener** (more EUR cuts), which **fights** a relative that needs EUR to stay *less* inverted than GBP. Do not treat the PDFs as endorsing GBP-vs-EUR reversal RV.

---

## 3. What the strips price now (2026-09-18)

### Absolute

| | Spot | Peak | Peak − spot | Z28 − peak (cut) | Z28 − Z27 | cut / hike |
|---|---:|---|---:|---:|---:|---:|
| **Euribor** | DFR 2.50 | U27 3.585% | **+108.5 bp** | **−13.0** | **−11.0** | 0.12 |
| **SONIA** | 3.730 | U27 4.880% | **+115.0 bp** | **−15.5** | **−13.5** | 0.13 |
| SOFR (ref) | 3.85 | U27 4.740% | +89.0 | −16.5 | −13.5 | 0.19 |

Both peaks at **U27**. Hikes-from-spot into peak are similar (~4.3–4.6 × 25bp).  
Post-peak cuts are **small on both** (&lt;1 × 25bp to Z28) — Barclays’ “almost no reversal” point applies to **EUR and GBP**.

### Relative (GBP − EUR)

| Metric | Last | YTD min | YTD max | YTD mean |
|---|---:|---:|---:|---:|
| `rel_cut` = (Z28−peak)_GBP − (Z28−peak)_EUR | **−2.5** | −29.0 | +3.0 | **−4.6** |
| `rel_z7z8` = (Z28−Z27)_GBP − (Z28−Z27)_EUR | **−2.5** | −18.0 | +2.0 | **−3.4** |

**Market already prices slightly more GBP cut/inversion than EUR** (−2.5 bp).  
That is **near / slightly tighter than** the YTD mean (−4.6 / −3.4), not an extreme
where GBP “hasn’t priced the relative story yet.”

30d colour: through early Sep `rel_cut` hovered ~0 to −2; on **10-Sep** (ECB
week shock) EUR briefly inverted *more* (`rel_cut` **+3.0**); by 18-Sep GBP
again slightly ahead of EUR on cuts (**−2.5**).

---

## 4. Rigorous scrutiny of the idea

### What holds

1. **Starting-point asymmetry is real:** DFR at top-of-neutral vs Bank Rate
   3.75% already restrictive (GS/BoE language). Peak *levels* differ by
   ~130 bp (SONIA peak − Euribor peak).
2. **EA growth-through-restriction** is documented (staff trend at ~3%
   terminal). That is a fair reason to expect **stubborn EUR terminal** /
   shallow EUR cuts.
3. **Liquid structure exists:** post-peak Z27/Z28 on both `IM*` and `J8*`.

### What does not hold / is already priced

1. **Relative cut depth is not mispriced in your favour in an obvious way.**
   GBP already shows **more** peak→Z28 cut than EUR (−15.5 vs −13.0). To be
   long the thesis you need the gap to go from −2.5 toward −5/−10/−20. YTD
   mean is −4.6 — only ~2 bp “catch-up” to average, not a dislocation.
2. **UK is not the soft underbelly in these notes.** Growth revised *up*.
   BoE base case is *hold*, not a deep cutting cycle from 3.75. Extra GBP
   cuts are a *market* path (peak 4.88) mean-reverting toward ~3.75, not a
   Barclays/GS “UK recession” call.
3. **Barclays’ highest-conviction EUR trade is the other way on the EUR leg**
   (price *more* EUR reversal via ERZ7Z8). Stacking “short GBP flat / long EUR
   steep” fights that.
4. **Cut/hike ratios are almost identical** (0.12 vs 0.13). The curves are
   rhyming, not diverging.
5. **Common energy shock** dominates both (all four PDFs). Relative reversal
   is a second-order call on *which CB stays restrictive longer* after oil —
   fragile vs a correlated global rates move.

### Verdict on the idea

| | |
|---|---|
| Macro sketch (ECB less restrictive start; EA resilient) | **Reasonable** |
| “Therefore initiate GBP-vs-EUR more-cuts RV here” | **Weak** — relative already has GBP slightly ahead; residual to YTD mean is tiny; sell-side EUR flattener fights you |
| Better framing if you like the macro | **EUR terminal stays high** (receive EUR reds / long EUR Z7Z8 steepener or fade Barclays flattener) *or* **GBP peak rich vs 3.75 Bank Rate** (receive SONIA U27/Z27 outright / vs OIS) — cleaner than the cross |

Only lean into the **relative** if you have a specific view that
`rel_cut` should re-widen to the left tail (toward −10/−20), e.g. BoE forced
into a faster disinflation path than ECB while EA stays hot — a view the
attached econ weeklies do **not** push.

---

## 5. Implementation (if you still want the RV)

Desk sign: short post-peak gap = **more cuts/inversion**.  
For “GBP cuts more than EUR”: **short SONIA gap / long Euribor gap**.

### A. Preferred STIR expression — relative Z27Z28

| Leg | Action | Contracts |
|---|---|---|
| GBP | Short Z28−Z27 | **Receive J8Z27 / pay J8Z28** |
| EUR | Long Z28−Z27 | **Pay IMZ27 / receive IMZ28** |

- Match **DV01** (Euribor ≈ €25/bp; SONIA ≈ £25/bp — size notionals so bp P&amp;L
  matches; FX-hedge residual if needed).
- P&amp;L ≈ `−Δ(z7z8_gbp) + Δ(z7z8_eur) = −Δ(rel_z7z8)`.
- Wins if GBP inverts more / EUR steepens relative.

**Levels now:** rel_z7z8 = **−2.5 bp**.  
**Stop idea:** rel_z7z8 → **0 to +2** (GBP loses relative invert).  
**Target idea (thesis):** rel_z7z8 → **−8 to −12** (toward richer YTD GBP
relative, not the −18 extreme without evidence).  
**Do not** use Barclays’ −35 on either leg as a relative target.

### B. Cleaner “cut from peak” expression — relative U27 vs Z28

| Leg | Action |
|---|---|
| GBP | Receive J8U27 / pay J8Z28 (short Z28−U27) |
| EUR | Pay IMU27 / receive IMZ28 (long Z28−U27) |

Same relative P&amp;L on `rel_cut`. Slightly more peak risk (U27 is the hawkish
instrument on both curves).

### C. What not to do as “the” implementation

- **Outright short EUR Z7Z8 alone** — that is Barclays’ trade (more EUR cuts),
  not your BoE&gt;ECB relative.
- **Outright short GBP Z7Z8 alone** — ignores the EUR leg; GBP already −13.5
  near its own YTD floor (~−14.5).
- **Recv EUR belly / pay Z26** — fails realised β (see prior note).

### D. Hedge / monitoring

- Track `rel_cut` and `rel_z7z8` daily from `panel.csv`.
- Energy: correlated selloff often compresses both; watch *relative* on ECB
  vs BoE meeting weeks (10-Sep showed EUR can invert *more* on ECB shock).
- If Bank Rate path re-prices toward economist 3.75 while ECB terminal holds,
  prefer **B** or outright receive SONIA peak vs pay Euribor peak
  (`peak_gbp − peak_eur` is +129.5 bp — separate RV).

---

## 6. Bottom line

The macro premise (ECB less restrictive *start*, EA can live with higher
rates) is **compatible with the reports**. The jump to “put on a BoE-vs-ECB
cuts-from-peak curve RV **now**” is **not**: the strip already prices a bit
more GBP reversal; the gap is near its YTD average; and Barclays’ EUR desk
is explicitly pushing *more* EUR post-peak flattening.

**If you express it anyway:** DV01-matched **short SONIA Z27Z28 / long Euribor
Z27Z28** (or U27/Z28 analogue), small size, target a move in `rel_z7z8` of
order **−5 to −10 bp**, stop if relative goes back through **0**.

**If you want the highest-integrity trade from this pack instead:** either
fade/join Barclays on **EUR Z7Z8 on its own merits**, or treat **SONIA peak
vs 3.75 Bank Rate** as the mispricing — not the cross cut differential.
