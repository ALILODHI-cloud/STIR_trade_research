# Asymmetric trade ideas from the current STIR strips

As-of **2026-09-18** (our Barchart panel). Sell-side (Barclays ERZ7Z8,
GS WIPI) is input only. Fly sign in the book is still unconfirmed — ideas
below are stated as **contract legs**, not desk fly P&L.

Asymmetry here means: **limited room one way in the recent distribution,
more room the other**. Not “free money.” Left tails exist if the hike
repricing keeps going.

---

## 1. Best skew: fade Z27/Z28 inversion (bull-steepener) — especially SOFR / SONIA

Barclays wants *more* inversion. Our history says you’re already at the
floor.

| Curve | Z27−Z28 price now | YTD min | Room to invert more | Room back to flat |
|---|---:|---:|---:|---:|
| Euribor | −11 | −14 | **3 bp** | **11 bp** |
| SOFR | −13.5 | −14 | **0.5 bp** | **13.5 bp** |
| SONIA | −13.5 | −14.5 | **1 bp** | **13.5 bp** |

**Trade (price space):** buy Z27 / sell Z28 (bull-steepener / fade the
flattener). Rough R:R to flat using YTD min as stop: ~**4× EUR**, much
higher on SOFR/SONIA because you’re already sitting on the YTD low.

**Why asymmetric:** YTD has barely printed through −14. Barclays’ −35
target is outside that sample. **Why it can still lose:** a 2022-style
regime where post-terminal cut-pricing deepens inversion beyond the 2026
range — that’s their thesis; you’re fading it.

**Cleaner than copying Barclays**, which from −11 toward −35 with stop at 0
is ~13 bp risk / ~3 bp of *historically observed* reward.

---

## 2. Receive the terminal peak (U27) vs the wings

Strip peaks at **U27** on all three. Rate-space `(Z26 − 2·U27 + Z28)` is at
**~0th percentile YTD** (body rich / high):

| Curve | Z26/U27/Z28 now | YTD range | YTD median |
|---|---:|---|---:|
| Euribor | −66.5 bp | [−69, +15.5] | −0.5 |
| SOFR | −58.0 | [−60, +31.5] | −9.3 |
| SONIA | −78.5 | [−78.5, +14.5] | −4.5 |

**Trade:** buy U27 futures (receive terminal) vs selling a DV01-weighted
blend of Z26 and Z28 (or tighter wings M27/Z28 if you want less wing risk).

**Skew:** SONIA is *at* the YTD low on that fly (−78.5); EUR/SOFR within a
few bp. Mean-reversion back toward ~0 is tens of bp if terminal tops;
further selloff in U27 has so far been a short trip from here in 2026 data.

**Caveat (real):** Barclays’ line that calling a terminal top is fool’s
gold — this trade *is* that call. Use tight risk; size smaller than (1).

Tighter, less heroic wing set: **M27/U27/Z28** (now ~−17.5 to −21.5 bp,
also ~0th %ile) — less carry-from-steep-hike-path, still fades the peak.

---

## 3. Mild relative: Euribor Z27Z28 flattener vs SOFR (or SONIA)

EUR is **2.5 bp less inverted** than SOFR/SONIA on Z27Z28. Not extreme
(EUR−SOFR differential ~60th %ile YTD) — **not strongly asymmetric**, but
it’s the only way to express Barclays’ euro-specific story without paying
outright extreme levels.

**Trade:** sell IMZ27 / buy IMZ28, and hedge with the opposite on SQ (or J8).
Wins if euro catches up on post-terminal cut-pricing; loses if euro
bull-steepens alone. Roughly balanced R:R — use as a hedge/overlay, not
the main asymmetry.

---

## 4. What we would *not* call asymmetric here

- **Outright Barclays ERZ7Z8 flattener** at −11 toward −35: historically
  observed upside ~3 bp, stop 11 bp away. Skew is the wrong way.
- **Chasing more SOFR Z27Z28 inversion** after it has been inverted since
  May and barely moved on the relative since July.
- Anything that needs **options** for true convexity — we have no vol
  surface in this pull; don’t invent one.

---

## Ranking (skew first)

1. **SOFR or SONIA Z27/Z28 bull-steepener** — best defined historical skew  
2. **Same on Euribor** — still fine, 3 bp more room to stop  
3. **Receive U27 vs wings** (prefer tighter M27/U27/Z28) — larger payoff if
   terminal tops, but it *is* a terminal-top call  
4. **EUR vs SOFR Z27Z28 relative flattener** — thesis overlay, not skew

Arithmetic lives in `data/cache/stir_curves/`; this note is the judgement
layer on top.
