# Receive Euribor belly / pay Z26 — does “ECB protects the belly” work?

Idea: express GS’s hawkish-ECB / belly-protection view as **receive belly,
pay IMZ26** (DV01-matched). Spread convention **back − front**.

P&L (per bp of matched DV01) ≈ **−Δ(belly − Z26)**. Wins when the Z26→belly
segment **flattens** (spread falls): front sells off more than belly, or belly
rallies more than front.

Data: Euribor `IM*` panel as-of **2026-09-18**. Numbers in
`data/cache/stir_curves/eur_recv_belly_pay_z26.json`.

---

## Levels now

| Belly | Rate | belly − Z26 | YTD rank |
|---|---|---|---|
| Z26 (hedge) | 3.050% | — | — |
| U27 (peak) | 3.585% | **+53.5 bp** | **YTD max** (99th pct) |
| Z27 | 3.565% | +51.5 | YTD max |
| 1y1y proxy | 3.529% | +47.9 | YTD max |

Z26 itself is +55 bp vs DFR 2.50%. The segment you would flatten is the
**widest it has been all year** — not a quiet, protected belly; a blowout
steepener into the peak.

---

## Recent scorecard for the trade

Recv U27 / pay Z26:

| Window | Δspread | Trade P&L |
|---|---|---|
| Post-ECB 10→18 Sep | +6.0 bp | **−6.0 bp**/DV01 |
| ~2w | +25 bp | **−25 bp** |
| ~1m | +34 bp | **−34 bp** |

Same sign for Z27, H28, or equal-weight 1y1y basket — all lost mid-single-digits
post-ECB and twenties over two weeks.

---

## The “protection” test (beta)

If hawkish ECB **protects** the belly, β(Δbelly, ΔZ26) should be **&lt; 1**, and
on Z26 selloff days the spread belly−Z26 should **fall**.

| Sample | corr | β(ΔU27 on ΔZ26) |
|---|---|---|
| YTD | 0.94 | **1.01** |
| Since 1 Aug | 0.94 | **1.82** |
| Since 27 Aug | 0.93 | **1.75** |
| Since 10 Sep (ECB) | 0.94 | **1.73** |

On days Z26 rises &gt; 0.5 bp (YTD): mean Δ(U27−Z26) = **+0.80 bp** (spread
*widens*). Protection would print negative.

So since the late-summer hike repricing, belly is a **high-beta** to the front,
not a low-beta. Paying Z26 1:1 **under-hedges** a belly receive on selloffs:
parallel is flat; β≈1.7 means you lose ~0.7× the front selloff on the spread.

---

## Verdict

The construction (recv belly / pay Z26) is the **right expression** of “front
bears, belly protected.” The **premise fails on this strip**:

1. Belly−Z26 at **YTD highs** — you are fading the move after it has already
   run +25–35 bp against the flattener in a month.
2. Post-ECB week and 2w P&L are **red**.
3. Realised β since August is **~1.7–1.8**, opposite of insulation.

If you still want ECB-hawkishness exposure, the strip says it is already in the
**level** of the belly (U27 +108 bp vs DFR) and the **post-peak invert**
(Z28−Z27 = −11), not in a suppressed belly beta vs Z26. A cleaner curve
expression of “peak holds / 2028 softer” is further out the inversion
(Z27Z28), not receiving U27 vs paying Z26.

Wrong-way stays open: another energy-led global rates selloff with β&gt;1 —
exactly the hedge you proposed loses again.
