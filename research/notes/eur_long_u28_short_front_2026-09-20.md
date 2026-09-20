# Long Euribor U28 / short Sept’26 hedge

**Ask:** outright long **IMU28**, hedged short **IMU26** (Sept’26).

**As-of 2026-09-18.** Figure: `research/notes/figures/eur_long_u28_short_front_2026-09-18.png`  
JSON: `data/cache/stir_curves/eur_long_u28_short_front.json`

---

## 1. What the structure is

| Leg | Futures | Rate view |
|---|---|---|
| **Long** Sept’28 | buy IMU28 | receive U28 (want U28 rate ↓) |
| **Short** Sept’26 | sell IMU26 | pay U26 (want U26 rate ↑) |

P&amp;L ≈ **+ΔU26 − ΔU28 = −Δ(U28 − U26)**.  
Wins when **U28−U26 falls** (front sells more than back, or back rallies more).

That is the **same family** as recv-belly / pay-front — **not** pay-peak /
recv-1y1y.

---

## 2. U26 is dead — live hedge is Z26

| | |
|---|---|
| IMU26 last session | **2026-09-14** @ **2.664%** |
| Cannot hold short U26 past expiry | Use **IMZ26** (3.050%) as the live front hedge |

So the live book is **long IMU28 / short IMZ26** (short U28−Z26).

| Spread | Last | YTD pct | Room up / down |
|---|---:|---:|---:|
| U28 − U26 (at expiry) | **+78.1** | **100th** | 0 / 82 |
| U28 − Z26 (live) | **+42.0** | **88th** | 5.5 / 57 |
| Z28 − Z27 (prior preferred) | −11.0 | 2nd | 36 / 3 |
| U27 − Z28 (pay peak / recv Z28) | +13.0 | 98th | 4 / 45 |

---

## 3. Recent sample — does the hedge help / does the trade work?

| Sample | β(U28 \| front) | Front-selloff mean P&amp;L | Peak-selloff mean P&amp;L |
|---|---:|---:|---:|
| YTD, short U26 | 0.81 | **−0.21** | — |
| **Aug+, short U26** | **1.68** | **−2.29** | — |
| YTD, short Z26 | 0.72 | +0.53 | +0.32 |
| **Aug+, short Z26** | **1.27** | **−1.94** | **−2.50** |

Since August the back **outruns** the front (β&gt;1). Shorting the front
**under-hedges** a long U28 — same failure mode as recv U27 / pay Z26.

### Episodes (P&amp;L bp)

| Episode | long U28/short U26 | long U28/short Z26 | pay U27/recv Z28 | short Z7Z8 | recv U27/pay Z26 |
|---|---:|---:|---:|---:|---:|
| Mar hike | +28.5 | +38.0 | +22.5 | +13.5 | +18 |
| Mid Jul | −14.5 | −6.5 | +8.0 | +7.5 | −13 |
| Late Aug | −16.0 | −12.0 | +3.0 | +3.0 | −14 |
| Sep 4→14 | **−35.6** | **−12.5** | **+14** | **+13** | −23.5 |
| Post-ECB week | −10.6 | −6.5 | −0.5 | 0 | −6 |

Held **1-Aug → last:** U28/U26 **−51**, U28/Z26 **−32**, payU/Z28 **+10**,
Z7Z8 **+10.5**, failed recvU/Z26 **−40**.

---

## 4. Vs the GS “peak up / 1y1y spared” trades

| | long U28 / short U26 (or Z26) | pay U27 / recv Z28 (or short Z7Z8) |
|---|---|---|
| Idea | Front bears, back protected | **Peak** bears, post-peak spared |
| Aug β | U28\|Z26 **1.27** (back high-β) | Z28\|U27 **0.68** (back low-β to peak) |
| Aug peak selloffs | **Loses** (−2.5) | **Makes** (+1.4) |
| Entry | U28−Z26 88th / U28−U26 max | Late too, but right direction |
| Fit to GS EUR story | **Poor** — wrong hedge | **Good** mechanism |

Long U28 with a **front** short is closer to the **failed** recv-belly/pay-Z26
trade than to “ECB pushes the peak.” To express peak-up/1y1y-spared you need
the hedge on the **peak** (pay U27 or Z27), not on Sept’26.

---

## 5. Verdict

1. **Sept’26 hedge:** expired 14-Sep; replace with **Z26** if you still want a
   front short.
2. **As a trade now:** poor — U28−front already very wide (88–100th %ile), and
   since Aug β&gt;1 so the short front **does not** protect long U28 in selloffs.
3. **Vs prior proposals:** worse than pay-U27/recv-Z28 and short Z7Z8 on the
   recent sample; same pathology as recv U27/pay Z26.
4. **Only regime where it shone:** March’26 front-led hike scare (β&lt;1). That
   is not the live regime.
