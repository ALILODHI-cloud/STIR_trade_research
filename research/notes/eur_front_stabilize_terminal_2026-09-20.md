# What curve is “front-end stabilises terminal / long forwards”? Is it a good trade?

**Source of the slogan:** GS *Hiking More or Less* (18 Sep 2026), EUR section
(Exhibit 7): hawkish ECB / **higher front-end rates insulate belly and longer
forwards** from front-end beta → risk-reward for **EUR 1y1y longs** (their
book trade was vs **CHF 1y1y**, not vs Euribor front).

**The curve:** **Euribor 3M strip** (as-of **2026-09-18**). Mapping:

| GS words | On this strip |
|---|---|
| Front-end rates | **Z26** 3.05% (+55 vs DFR 2.50); U26 expired 14-Sep |
| Terminal | **U27 peak** 3.585% (+108.5) |
| Long-end / 1y1y forwards | mean(U27…U28) **3.53%**; outright **U28 3.47%**, Z28 3.455% |

Figure: `research/notes/figures/eur_front_stabilize_terminal_2026-09-18.png`

If the slogan were true as a **trade vs the EUR front**, long U28 / short
Z26 (or expired U26) would print when Z26 sells. That is the claim to test.

---

## Test: when the front sells, do terminal and 1y1y *stabilise*?

Stabilise = long-end **moves less than** the front (β&lt;1), or even falls.

| Sample | β(U27\|Z26) terminal | β(1y1y\|Z26) | β(U28\|Z26) | On Z26 selloff: mean ΔU27 / ΔU28 | % days \|ΔU28\| &lt; \|ΔZ26\| |
|---|---:|---:|---:|---|---:|
| YTD | 1.01 | 0.85 | 0.72 | +5.4 / +4.1 vs ΔZ +4.6 | 50% |
| **Since Aug** | **1.82** | **1.56** | **1.30** | **+5.9 / +4.8 vs ΔZ +2.9** | **22%** |
| Last 20d | 1.79 | 1.48 | 1.19 | — | — |

**Since August the slogan fails vs the front.** Front +1 → terminal **+1.8**,
1y1y **+1.6**, U28 **+1.3**. Terminal is the *least* stable piece, not a
stabilised long-end.

YTD totals: Z26 **+93.5**, U27 **+126**, U28 **+88**, 1y1y **+107**. Terminal
has *led* the selloff, not lagged it.

Post-ECB week (10→18 Sep): Z26 **+4**, U27 **+10**, 1y1y **+10.6**, U28 **+10.5**
— long-end and terminal sold **more** than the front.

High front *level* (YTD Q4 of Z26) is also **not** calmer: subsequent 5d ΔU27
mean **+12**, ΔU28 **+9.5** vs Q1 **−0.7 / −1.8**. Higher front has coincided
with *more* terminal repricing, not less.

---

## Where the slogan *is* true (different comparison)

Insulation **vs the peak**, not vs Z26:

- β(Z28 \| U27) ≈ **0.68**, β(U28 \| U27) ≈ **0.74** since Aug
- On U27 selloff days, pay U27 / recv Z28 mean P&amp;L **+1.4**

So: **peak does the hawkish work; reds lag the peak.** That is *not* “front
up → terminal/1y1y sit still.” The front is the *low*-β leg in the live
regime.

---

## Is long U28 / short U26 (or Z26) a good trade on this data?

**No.**

| | |
|---|---|
| Fit to GS words | They meant **recv EUR 1y1y vs CHF**, not vs EUR front |
| Fit to EUR-front insulation | **Fails since Aug** (β&gt;1) |
| Aug 1 → 18 Sep P&amp;L | long U28 / short Z26 **−32 bp**; U28/U26 **−51** |
| Entry | U28−Z26 **+42** = 88th %ile; U28−U26 died at YTD **max** |
| Live hedge | U26 expired 14-Sep |

**Data-consistent expression of the same GS *story* (peak absorbs, forwards
spared):** pay **IMU27** / recv **IMZ28** (or short Z7Z8). Mechanism ✓, **entry
late** (U27−Z28 +13 = 98th %ile).

Do **not** express it as long U28 / short front — that is the failed
recv-belly/pay-Z26 family.
