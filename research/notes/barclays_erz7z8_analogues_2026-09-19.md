# Barclays ERZ7Z8 flattener — analogues on SOFR / SONIA

Source: `research/pdfs/Barclays_Global_Rates_Weekly_On_the_brink_7afa.pdf`
(Global Rates Weekly, completed 10-Sep-26). Futures arithmetic from our
2026-09-18 Barchart panel — not from the PDF’s charts.

## What Barclays is saying (thesis, not gospel)

- Initiate **ERZ7ERZ8 flattener** (Dec27 / Dec28 Euribor): entry **-13 bp**,
  target **-35 bp**, stop **0 bp** (price spread front−back; more negative =
  more inverted).
- Mechanism: terminal has ripped higher (~100 bp above ECB neutral in their
  telling). As in 2022, once terminal is “too high”, the market starts
  pricing a reversal further out → curve flattens / inverts beyond U7.
- They explicitly say calling a *top* in terminal is fool’s gold; the trade
  is the **back underperforming** if terminal stays high or grinds higher.

Our 10-Sep settle for IMZ27−IMZ28 was **−11 bp** (vs their −13 — settle vs
their print / timing). As of 18-Sep still **−11 bp**. YTD most-inverted
print: **−14 bp** (14-Sep). Their **−35 target is outside anything in our
2024–26 history** (min −14). Treat −35 as an assertion, not a shown level.

## Same structure on the three curves (18-Sep)

Price spread Z27−Z28 (Barclays sign). Terminal = highest rate on the strip.

| | Z27−Z28 now | YTD min | First inverted 2026 | Terminal | Z26→term | Term→Z28 |
|---|---:|---:|---|---|---:|---:|
| Euribor | **−11.0** | −14.0 | 11-May (48/183 sess) | U27 @ 3.585% | +53 bp | −13 bp |
| SOFR | **−13.5** | −14.0 | 4-May (86/180) | U27 @ 4.740% | +41 bp | −16 bp |
| SONIA | **−13.5** | −14.5 | 19-Mar (93/181) | U27 @ 4.880% | +63 bp | −16 bp |

All three already peak at **U27** and invert through the reds. SOFR/SONIA
are **~2.5 bp more inverted** than Euribor on Z27Z28.

## Did the Barclays mechanism actually fire since July?

Rate change 1-Jul → 18-Sep:

| | U27 | Z27 | Z28 | Z27−Z28 move |
|---|---:|---:|---:|---:|
| Euribor | +102.5 | +103.0 | +88.5 | **front +14.5 bp more than back** |
| SONIA | +87.5 | +89.0 | +72.5 | **+16.5 bp** |
| SOFR | +72.5 | +77.5 | +75.0 | only **+2.5 bp** |

Euribor and SONIA ran the script (terminal selloff, reds lag → inversion).
SOFR was already inverted by July (−11), so little incremental.

## Opportunities *akin* to their trade

1. **Closest clone — SONIA `J8Z27` / `J8Z28` flattener**  
   Same July→now mechanics as Euribor, same terminal-at-U27 shape, now
   −13.5. Not “early”; already near YTD extreme. Expression of the same
   view if you prefer sterling liquidity / BoE terminal risk (GS WIPI had
   the largest BoE cumul into EOY27).

2. **Euribor still the one with a bit of relative room**  
   Z27Z28 is 2.5 bp *less* inverted than SOFR/SONIA. If the thesis is
   “euro catches up to the USD/GBP post-terminal cut-pricing”, a **EUR
   flattener vs SOFR or SONIA flattener** is cleaner than chasing EUR
   outright from −11 toward a −35 that our history never printed.

3. **SOFR `SQZ27`/`SQZ28` is the worst fresh entry**  
   Inverted longest, barely moved on the relative since July, already
   −13.5. Paying up for more inversion here is chasing.

4. **U27Z28 (beyond the actual peak)** as a slight variant  
   Now: EUR −13, SOFR −16.5, SONIA −15.5. Same ranking — euro least
   inverted past the terminal contract.

## What we would *not* do from this pack alone

- Copy the **−35 target** without a 2022-style regime argument; it is not
  in the recent distribution.
- Assume “terminal still going up ⇒ flattener prints” on SOFR — that move
  already largely happened before July.
- Ignore that all three Z27Z28s sit at ~**0th percentile** of 2024–26
  (most inverted). Outright flatteners from here are short convexity to a
  bull-steepening if terminal *does* top.

## Bottom line

The Barclays euro idea is “more inversion beyond the terminal as the hike
cycle overshoots.” On our strips that structure **already exists on all
three curves**. The only still-interesting *relative* angle is that
**Euribor is the least inverted Z27Z28**, while **SONIA has run the same
July mechanics hardest**. SOFR is late to join as a *new* flattener.
