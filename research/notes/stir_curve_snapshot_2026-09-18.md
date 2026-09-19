# STIR curve snapshot — 2026-09-18

Source: Barchart EOD via browser session (`SQ` = 3M SOFR, `IM` = 3M Euribor, `J8` = 3M SONIA).
Spot anchors: FRED `SOFR`, `IUDSOIA` (SONIA), `ECBDFR`, `EFFR`.
Fetched fresh this session — nothing reused from prior repo cache.

Interactive YTD viewer: [`stir_curves_ytd.html`](stir_curves_ytd.html)
Latest overlay: [`stir_curves_latest.html`](stir_curves_latest.html)

## What the market prices into end-2026

Dec-26 futures are the **3M forward rate for the Dec-26 IMM quarter**, not an
overnight fix on 31 Dec. Delta vs spot is the priced change into that window.

| Curve | Spot / policy | As-of | Z26 rate | Z26 − spot (bp) |
|---|---:|---|---:|---:|
| SOFR | SOFR 3.850% | 2026-09-17 | 4.325% | +47.5 |
| SONIA | SONIA 3.730% | 2026-09-16 | 4.250% | +52.0 |
| Euribor | ECB DFR 2.500% | 2026-09-18 | 3.050% | +55.0 (vs DFR, not 3M Euribor fix) |

Euribor: Sep-26 white has expired, so **IMZ26 is the only remaining 2026 quarterly**.
Last IMU26 print: 2026-09-14 at
2.664% → Z26 is
**+38.6 bp** higher.

EFFR for context: 3.880% on 2026-09-17.

### Remaining 2026 contracts only (rate %)


**SOFR**

| Contract | Price | Rate % |
|---|---:|---:|
| U26 | 95.9975 | 4.0025 |
| V26 | 95.8600 | 4.1400 |
| X26 | 95.7650 | 4.2350 |
| Z26 | 95.6750 | 4.3250 |

**EURIBOR**

| Contract | Price | Rate % |
|---|---:|---:|
| Z26 | 96.9500 | 3.0500 |

**SONIA**

| Contract | Price | Rate % |
|---|---:|---:|
| U26 | 96.1500 | 3.8500 |
| Z26 | 95.7500 | 4.2500 |


### Full latest strips through 2028 (rate %)


**SOFR**

| Contract | Price | Rate % |
|---|---:|---:|
| U26 | 95.9975 | 4.0025 |
| V26 | 95.8600 | 4.1400 |
| X26 | 95.7650 | 4.2350 |
| Z26 | 95.6750 | 4.3250 |
| H27 | 95.4150 | 4.5850 |
| M27 | 95.2850 | 4.7150 |
| U27 | 95.2600 | 4.7400 |
| Z27 | 95.2900 | 4.7100 |
| H28 | 95.3300 | 4.6700 |
| M28 | 95.3650 | 4.6350 |
| U28 | 95.3950 | 4.6050 |
| Z28 | 95.4250 | 4.5750 |

**EURIBOR**

| Contract | Price | Rate % |
|---|---:|---:|
| Z26 | 96.9500 | 3.0500 |
| H27 | 96.6200 | 3.3800 |
| M27 | 96.4600 | 3.5400 |
| U27 | 96.4150 | 3.5850 |
| Z27 | 96.4350 | 3.5650 |
| H28 | 96.4700 | 3.5300 |
| M28 | 96.5050 | 3.4950 |
| U28 | 96.5300 | 3.4700 |
| Z28 | 96.5450 | 3.4550 |

**SONIA**

| Contract | Price | Rate % |
|---|---:|---:|
| U26 | 96.1500 | 3.8500 |
| Z26 | 95.7500 | 4.2500 |
| H27 | 95.3700 | 4.6300 |
| M27 | 95.1800 | 4.8200 |
| U27 | 95.1200 | 4.8800 |
| Z27 | 95.1400 | 4.8600 |
| H28 | 95.1850 | 4.8150 |
| M28 | 95.2300 | 4.7700 |
| U28 | 95.2600 | 4.7400 |
| Z28 | 95.2750 | 4.7250 |


## Biggest movers — last two weeks (2026-09-04 → 2026-09-18)

Ranked by absolute rate change (bp). Price fall = rate rise.

| Rank | Symbol | Curve | Δ rate (bp) | From % | To % | Δ price |
|---|---|---|---:|---:|---:|---:|
| 1 | IMU27 | EURIBOR | +47.00 | 3.115 | 3.585 | -0.4700 |
| 2 | IMZ27 | EURIBOR | +47.00 | 3.095 | 3.565 | -0.4700 |
| 3 | IMH28 | EURIBOR | +45.50 | 3.075 | 3.530 | -0.4550 |
| 4 | IMM27 | EURIBOR | +44.50 | 3.095 | 3.540 | -0.4450 |
| 5 | SQM27 | SOFR | +43.00 | 4.285 | 4.715 | -0.4300 |
| 6 | J8U27 | SONIA | +43.00 | 4.450 | 4.880 | -0.4300 |
| 7 | SQU27 | SOFR | +43.00 | 4.310 | 4.740 | -0.4300 |
| 8 | IMM28 | EURIBOR | +42.50 | 3.070 | 3.495 | -0.4250 |
| 9 | J8Z27 | SONIA | +42.00 | 4.440 | 4.860 | -0.4200 |
| 10 | SQZ27 | SOFR | +42.00 | 4.290 | 4.710 | -0.4200 |


## Euribor end-27 / end-28 inversion theme

Convention: spread = **Z27 rate − Z28 rate** (bp). Positive ⇒ inverted
(terminal/near-terminal above the further reds) — i.e. price(IMZ27) < price(IMZ28).

| | |
|---|---|
| IMZ27 rate | 3.565% |
| IMZ28 rate | 3.455% |
| Spread now | **+11.0 bp** |
| Spread 2w ago (2026-09-04) | +1.0 bp |
| Spread at YTD (2026-01-02) | -25.0 bp |
| Sessions inverted YTD | 48 / 183 |
| Last cross into inversion | 2026-08-27 |
| YTD range of spread | [-25.0, +14.0] bp |
| Euribor terminal contract now | U27 @ 3.585% |
| Euribor terminal 2w ago | U27 @ 3.115% |
| Euribor terminal at YTD | Z28 @ 2.645% |

Verdict is written from these numbers in the session note / chat — the table
above is the arithmetic.

## Data provenance

- Futures: Barchart core-api EOD `historical/get` + `quotes/get` for fixed
  contracts `SQ*`, `IM*`, `J8*` (not generics).
- Spots: FRED CSV downloads same session.
- Panel rows: 66,660 across 56 contracts,
  2018-07-03 → 2026-09-18.
