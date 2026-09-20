# Is short U27−Z26 just a peak-down bet? Did pay Z26 help in selloffs?

**As-of 2026-09-18.** Spread = U27 − Z26. Short = **recv J8U27 / pay J8Z26**.  
“Short Dec’26” here = **pay Z26** (profits when Z26 rate rises).

Figure: `research/notes/figures/sonia_z26_hedge_vs_peak_fade_2026-09-18.png`

---

## Short answer

**Mostly yes — especially since August.** The structure is a fade of the Sep’27 peak with a Dec’26 hedge. In selloffs since March the Z26 leg **always reduced** losses vs outright recv U27, but:

| Period (selloff days ΔZ&gt;+0.5) | recv U27 | pay Z26 | short spread | Z offset of U move |
|---|---:|---:|---:|---:|
| Mar–Jul | −414 | **+395** | **−19** | **95%** ≈ full hedge |
| Aug–Sep | −118 | **+51** | **−67** | **43%** — mutes, does not save |
| Mar–Sep all | −532 | +446 | −86 | 84% |

So: **early post-March, paying Z26 almost fully hedged selloffs** (front-led). **Since Aug it only covers ~40–50%** because U27 runs ~2× Z26 — you still lose on the spread. That residual **is** the peak-extension bet.

---

## Selloff episodes since March

| Episode | ΔZ | ΔU | recv U | pay Z | short spread | Z / U |
|---|---:|---:|---:|---:|---:|---:|
| Mar 2–20 hike scare | +128 | +101 | −101 | **+128** | **+27** | 127% — hedge **made** money |
| Apr 17–29 | +52 | +52 | −52 | +52 | **0** | 100% |
| May 7–12 | +18 | +25 | −25 | +18 | −7 | 72% |
| Jul 15–23 path ext | +15 | +27 | −27 | +15 | **−12** | 56% |
| Aug 26–Sep 2 | +10.5 | +24.5 | −24.5 | +10.5 | **−14** | 43% |
| Sep 4–14 peak run | +25 | +49 | −49 | +25 | **−24** | 51% |

Pattern: while Dec’26 was still near/above the peak (Mar–Apr), pay Z26 **helped a lot** — sometimes more than 1:1. Once Sep’27 became the clear peak and β(U\|Z) rose toward 2, pay Z26 became a **partial shock absorber**, not a selloff winner.

---

## Held continuously

| Entry → 18-Sep | recv U27 | pay Z26 | short U27−Z26 |
|---|---:|---:|---:|
| 1-Mar → | −147 | +90.5 | **−56.5** |
| 1-Aug → | −60 | +18 | **−42** |
| 19-Aug → | −52.5 | +18 | **−34.5** |

From Aug onward, ~30% of the outright peak-fade loss was offset by Z26; **~70% of the pain remains** — that remainder is Δ(U−Z), i.e. peak outrunning Dec’26.

---

## How to read the trade

1. **Thesis that pays:** Sep’27 peak comes in (rally with β&gt;1, or peak migrates forward so Z26 outsells U27 like March).
2. **What pay Z26 does *not* do in the live regime:** turn selloffs into winners. It only cuts the loss vs naked recv U27.
3. **If you want selloff protection**, 1:1 vs Z26 is the wrong hedge ratio now — you’d need closer to **~2:1 pay Z / recv U** to be selloff-neutral given Aug–Sep β≈2 (and then you are no longer expressing “peak rich to Dec’26”; you are mostly flat).

Data: `data/cache/stir_curves/sonia_z26_hedge_in_selloffs.json`
