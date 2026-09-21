# Short UK buildup vs long EUR buildup — GS research cross-check

**Trade:** short

\[
(U27-Z26)_{\mathrm{SONIA}}-(U27-Z26)_{\mathrm{Euribor}}
\]

Receive `J8U27`, pay `J8Z26`; pay `IMU27`, receive `IMZ26`, on
FX-adjusted DV01. Data as of **2026-09-18**. Rate-space buildup is
Sep’27 minus Dec’26.

## What is priced

| | SONIA | Euribor | GBP−EUR |
|---|---:|---:|---:|
| Z26 | 4.250% | 3.050% | |
| U27 | 4.880% | 3.585% | |
| U27−Z26 buildup | **+63.0 bp** | **+53.5 bp** | **+9.5 bp** |

The 1:1 box is at the **99th percentile** of the 2-Mar–18-Sep sample
(maximum +10.5; mean +0.3). It is not literally “10 bp more BoE hikes”:
the contracts are three-month forwards and the box also includes timing,
basis and risk-premium differences.

## Research inputs

### BoE: GS *Opening the Door to a November Hike* (17-Sep)

- MPC voted 6–3 to hold. GS retains one 25 bp November hike to 4%.
- A hold remains possible if energy falls or activity/employment weakens.
- GS sees no strong signal for tightening beyond November: labour softness,
  benign underlying inflation and tight financial conditions argue against it.
- Its probability-weighted path remains notably below market even after a
  25% further-hikes scenario; the other scenario weights shown are 50%
  baseline and 25% no hikes.

This is direct support for **short SONIA buildup**. A November hike occurs
before the Dec’26 front leg and should not by itself create a +63 bp
Dec’26-to-Sep’27 slope. The buildup requires persistence or additional
tightening beyond the one-hike baseline.

### ECB: user-pasted GS *ECB Recap—Higher Rates Ahead*

- Baseline adds 25 bp in December to 2.75%; low hurdle for 3%, with October
  possible if energy, September HICP or second-round evidence strengthens.
- Scenario weights: 50% baseline, 35% further hikes to 3.5%, 15% rapid cuts.
- Probability-weighted near-term peak is close to market around 3%, but GS
  says its path remains notably below market in 2027.
- Cuts are delayed to 2027Q4/2028Q1; terminal forecast raised to 2.25%.

This supports a **more persistent ECB path than BoE** as the relative hedge,
but not an outright long Euribor buildup without qualification: GS still
regards 2027 market rates as too high.

### Euro inflation nearcast (19-Sep)

- Model-implied Dec’26 headline **3.85% yoy** and core **2.62%**; core peaks
  around **2.8%** in early 2027.
- Upside risk is concentrated in core goods; pressures re-firmed since August.
- Spot core was still benign at 2.4% in August, and the model is close to GS’s
  official forecast. It outperformed in 2022 but only matched peers broadly
  in 2023–25.

The nearcast supports the ECB hawkish tail and delayed cuts. It does not by
itself imply hikes after Dec’26: most of the named October/December tightening
would affect both Z26 and U27, not necessarily widen U27−Z26.

## Statistical qualification

The 1:1 box is extreme, but GBP buildup has higher common-shock beta:

| Sample | β(ΔGBP buildup \| ΔEUR buildup) | Corr | β-adjusted residual percentile |
|---|---:|---:|---:|
| Mar+ | **1.11** | 0.81 | **79th** (z +0.78) |
| Aug+ | **1.23** | 0.93 | **15th** (z −1.23) |

At 1:1 the box is +9.5 and 99th percentile. At the March β, the residual is
only +3.4 bp and 79th percentile. At the live August β, GBP buildup is not
rich after scaling. Therefore the trade is partly a bet that the recent
high GBP beta normalises, not a pure static dislocation.

## Verdict

The **direction is supported**: GS is much more explicit that BoE market
pricing exceeds its weighted path, while ECB inflation persistence and a
35% further-hikes tail make Euribor the more sensible hedge. But the **full
1:1 box is only moderately attractive**, not a free 10 bp:

1. ECB has already delivered 50 bp, so some positive future UK catch-up is
   structurally reasonable.
2. GS also sees 2027 ECB rates below market, weakening the long-EUR-buildup leg.
3. β-adjusted valuation is not extreme.

Preferred expression if the core conviction is BoE peak fade: short one unit
of GBP buildup with **0.5–0.75 units** of long EUR buildup. Use 1:1 only if
the view explicitly includes normalisation of GBP’s higher buildup beta.
For a full 1:1 box, a conservative compression objective is +3 to +5 bp,
not zero by assumption.

Main catalysts: UK energy relief/soft labour/no second-round effects; stronger
Euro HICP/core-goods pipeline or ECB second-round evidence. Main invalidation:
persistent UK energy pressure that activates the further-hikes scenario while
Euro data soften enough to pull down 2027 ECB pricing.

Sources:

- `research/pdfs/GS_European_Daily_BoE_Recap_2026-09-17.pdf`
- `research/pdfs/GS_Euro_Area_Inflation_Nearcast_2026-09-19.pdf`
- User-pasted GS ECB recap in the 21-Sep conversation
- `data/cache/stir_curves/panel.csv`
