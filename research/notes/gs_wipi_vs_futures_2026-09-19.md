# GS “What is Priced In” vs our futures snapshot

Source PDF: `research/pdfs/GS_What_is_Priced_in_end_week_ef93.pdf`
(desk WIPI, 19 Sep 2026 07:27 SGT). Ours: Barchart EOD 18 Sep 2026.

## Why the levels don’t match

Goldman is showing **meeting-dated OIS / policy-rate paths** (WIPI).
We showed **3M exchange futures** (SOFR `SQ`, Euribor `IM`, SONIA `J8`).

Those are different instruments:

| | GS | Us |
|---|---|---|
| Object | Overnight / policy OIS on meeting dates + EOY | 3M forward rate for an IMM quarter |
| “EOY26” | OIS-implied overnight on 31 Dec 2026 | Dec-26 futures = average 3M rate over Dec IMM → Mar IMM |
| ECB | Deposit facility (€STR OIS) | 3M Euribor (trades rich to DFR) |

So a direct Z26-vs-EOY26 or Z26−spot-vs-GS-cumul comparison is **not like-for-like**.

## Spots (these do match)

| | GS OIS spot | Our spot |
|---|---:|---:|
| FOMC | 3.892 | EFFR 3.880 / SOFR 3.850 |
| ECB | 2.446 | DFR 2.500 |
| BOE | 3.743 | SONIA 3.730 |

## Levels: GS EOY OIS vs our Z futures (gap ≈ basis + tenor mismatch)

| | GS EOY26 | Our Z26 | Gap | GS EOY27 | Our Z27 | GS EOY28 | Our Z28 |
|---|---:|---:|---:|---:|---:|---:|---:|
| FOMC / SOFR | 4.219 | 4.325 | +11 bp | 4.633 | 4.710 | 4.483 | 4.575 |
| ECB / Euribor | 2.838 | 3.050 | +21 bp | 3.373 | 3.565 | 3.266 | 3.455 |
| BOE / SONIA | 4.130 | 4.250 | +12 bp | 4.835 | 4.860 | 4.694 | 4.725 |

Euribor gap (~20 bp) is roughly the usual **Euribor − DFR/€STR** basis — expected when you put Euribor futures next to ECB deposit OIS.

Cumul to end-2026 also diverges for the same reason: GS FOMC **+32.7 bp**, our Z26−SOFR **+47.5 bp**. Subtract ~10–15 bp of futures/OIS basis and the Dec-quarter vs 31-Dec point difference and most of the gap goes away.

## Shape: this *does* match

EOY27 − EOY28 (GS OIS) vs Z27 − Z28 (our futures):

| | GS | Futures |
|---|---:|---:|
| FOMC / SOFR | +15.0 bp | +13.5 bp |
| ECB / Euribor | +10.7 bp | +11.0 bp |
| BOE / SONIA | +14.1 bp | +13.5 bp |

So the **end-27 / end-28 inversion as terminal re-priced higher** theme in the GS pack is the same story we saw on Euribor futures — just read off OIS instead of IMZ27/IMZ28.

## What to use when

- Want “how many cuts/hikes into year-end / each meeting” → GS-style **meeting OIS** (build from OIS, not from 3M futures alone).
- Want liquid futures RV / strip trades → **SQ / IM / J8** as we did.

Next step if we want to reconcile tightly: bootstrap meeting-dated SOFR/€STR/SONIA OIS from the same session and put EOY26/27/28 next to GS.
