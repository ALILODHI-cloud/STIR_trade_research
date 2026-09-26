# GS Euro trade — EUR 1y1y vs CHF vs the Euribor strip

Source: GS *Global Rates Trader: Hiking More or Less*, 18 Sep 2026.

**Trade (book):** Pay CHF 1y1y vs EUR 1y1y (long EUR 1y1y / short CHF 1y1y).
Opened 11-Sep-26 at **3.02** (CHF−EUR), latest **2.96**, target **2.65**, stop **3.25**
(+6 bp on their mark at publication).

Desk spreads: **back − front**. Euribor data as-of **2026-09-18**
(`data/cache/stir_curves/`). **No CHF/SARON strip on disk** — cross leg cannot be
marked from our files; only the EUR thesis is tested below.

---

## What GS argues (EUR leg)

1. Hawkish ECB reaction to energy **insulates belly / longer forwards** from
   front-end beta (Exhibit 7 claim).
2. That builds risk-reward for **belly longs**.
3. Therefore **1y1y EUR should compress vs CHF** (receive EUR, pay CHF).
4. SNB: on hold near-term; trade also works if SNB hikes / CHF weakens / ECB
   tightens again.

Energy is the named uncertainty.

---

## What the Euribor strip shows (2026-09-18)

ECB DFR **2.50%**. Peak **U27 3.585%** (+108.5 bp vs DFR).

```
Z26  3.050  (+55)
H27  3.380  (+88)
M27  3.540  (+104)
U27  3.585  (+108.5)  ← peak
Z27  3.565  (+106.5)
H28  3.530
M28  3.495
U28  3.470
Z28  3.455  (+95.5)
```

Rough **EUR 1y1y futures proxy** (not OIS): mean(U27…U28) ≈ **3.53%**
(+103 bp vs DFR). mid(Z27,Z28) ≈ **3.51%**.

**Z28−Z27 = −11.0 bp** (inverted). YTD range −14 to +25; already near the
most-inverted prints. **M28−M27 = −4.5**. Front still steep: H27−Z26 = **+33**.

Belly−front proxy mean(U27…U28)−Z26 = **+47.9 bp** — **YTD maximum** (YTD min
−13.4, mean +10.9). So vs the front, EUR belly/1y1y is as *rich in level /
wide in spread* as it has been all year — not a cheap entry on the EUR curve
alone.

### Post-ECB week (10 → 18 Sep) — tests “belly protection”

Rate changes (bp):

| | Z26 | H27 | U27 | Z27 | Z28 |
|---|---|---|---|---|---|
| Δ | +4.0 | +8.0 | +10.0 | +10.5 | +10.5 |

Belly/back **sold off more** than the front. Front gaps **steepened**
(H27−Z26 +29 → +33). Z28−Z27 unchanged at −11.

That is the opposite of “hawkish ECB insulated the belly” over this window:
beta to the selloff was *higher* out the curve, not lower. (GS’s Exhibit 7 is a
longer beta history; this week’s strip move does not corroborate the
near-term “protection” slogan.)

2w movers in the same cache: IMU27 / IMZ27 **+47 bp** — the belly was the
*largest* selloff on the board, not a haven.

---

## Evaluation

| Claim | Vs data |
|---|---|
| ECB hawkishness protects belly | Not in 10–18 Sep strip: belly sold more than front |
| Belly-long risk-reward | EUR 1y1y proxy already +103 bp vs DFR; belly−Z26 at **YTD max** |
| Post-ECB front flattening “holding” | Front **steepened** +4 bp (H27−Z26) that week |
| Compress EUR 1y1y vs CHF | Needs CHF 1y1y. GS marks 3.02→2.96 (+6 toward 2.65). **We have no CHF series** — cannot verify richness of the cross or whether EUR or CHF drove the +6 |
| SNB on hold / ECB can tighten | Directional story for the *spread*; EUR leg alone is long a high, already-inverted post-peak strip |

**Net on the EUR book we can see:** the outright “long EUR belly / 1y1y because
ECB protects it” leg looks **late and wrong-footed by the post-ECB week**. The
curve has already inverted Z27Z28 (−11, near YTD floor) and priced ~4×25 bp of
hikes into the peak. Further “insulation” is an assertion; recent beta went the
other way.

**On the actual recommended trade (CHF−EUR 1y1y):** it is a *relative* value
call. Without CHF data this book cannot grade entry/target. If the edge is
“SNB more hikeable / CHF front rich vs EUR,” that can work even if EUR belly is
rich — but then the note’s EUR-belly rhetoric is marketing, not the P&L driver.
If the edge is meant to be EUR downside from ECB protection, the strip
disagrees with the last week’s evidence.

Wrong-ways: energy spike that forces **both** ECB and SNB (spread may not
compress); EUR fiscal/OAT shock that lifts EUR belly vs CHF; continued global
bear-steepening of EUR STIR like 10–18 Sep.

---

## Numbers file

`data/cache/stir_curves/eur_1y1y_vs_chf_eval.json`
