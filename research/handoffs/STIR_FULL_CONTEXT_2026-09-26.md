# DM STIR research — complete agent handoff

**Prepared:** 26 September 2026  
**Market-data cutoff:** 25 September 2026 settlement, except where an intraday
broker screenshot is explicitly identified  
**Repository:** `ALILODHI-cloud/STIR_trade_research`

## Instructions to the receiving agent

Read this file before answering. Treat it as the controlling handoff for this
book, then read `memory/book.md`, `memory/trades.yaml`, and the newest file in
`memory/sessions/`. Do not infer a current market level from model memory or
silently substitute an intraday print for a settlement. Refresh the source
data if the user asks where a trade is trading now.

The user wants an analytical research partner for a developed-markets STIR
book, not a production pricer. Start with what the curve discounts, distinguish
that from any forecast, show reproducible arithmetic, and state what would
invalidate a trade. Use full sentences and actual contract months in prose,
not contract codes alone. Sell-side research is evidence to test, not an
authority.

This file is a reconstruction of the decision-relevant context from the full
conversation. The repository is the durable memory system; the agent does not
have guaranteed hidden recall between sessions.

## Non-negotiable conventions

All curve slopes are quoted in **rate space as back contract minus front
contract**:

- Buildup: September 2027 minus December 2026.
- Reversal: December 2028 minus September 2027.
- June calendar: June 2028 minus June 2027.
- Peak curvature: buildup minus reversal, or
  `2 × September 2027 − December 2026 − December 2028`.
- A positive slope is steep. A flattening is a fall in the slope.
- A negative reversal means cuts from the peak. A further flattening when the
  reversal is already negative means deeper inversion.

For a futures-price calendar, the signs reverse because implied rate is
`100 − price`. For example, buying September 2027 and selling December 2026
creates a price spread `September 2027 price − December 2026 price`; its rate
slope is the negative of that price spread, multiplied by 100 to express basis
points.

The user's fly-sign convention is still unconfirmed. Do not quote a fly without
restating the weights and economic direction.

Use actual month names in user-facing answers. Codes used in files are:

- `Z` = December, `H` = March, `M` = June, `U` = September.
- `IM` = Euribor, `J8` = SONIA, `SQ` = SOFR on Barchart.

## Stable deliverables

- Live curves dashboard:
  https://raw.githack.com/ALILODHI-cloud/STIR_trade_research/gh-pages/stir-strips.html
- Latest four-strip peak relative-value workbook:
  https://raw.githubusercontent.com/ALILODHI-cloud/STIR_trade_research/gh-pages/peak_rv_universe_latest.xlsx
- Latest exhaustive contract/segment relative-value workbook:
  https://raw.githubusercontent.com/ALILODHI-cloud/STIR_trade_research/gh-pages/stir_full_rv_universe_latest.xlsx

The raw.githack dashboard is the durable working link. It may show a one-click
safety interstitial on first use. GitHub Pages was not enabled when this
handoff was prepared. Cloudflare quick-tunnel URLs are temporary and must
never be presented as permanent links.

## Source data and provenance

The latest canonical curves are through **25 September 2026 settlement**.
Barchart fixed-contract end-of-day data were fetched through a headed Chrome
session:

- Raw histories: `data/raw/stir_futures/histories_raw.json.gz`
- Latest quote response: `data/raw/stir_futures/latest_quotes.json`
- Canonical aligned panel: `data/cache/stir_curves/panel.csv`
- Latest one-day and five-session moves:
  `data/cache/stir_curves/stir_daily_moves_2026-09-25.csv`

Local FRED caches provide SONIA, SOFR, effective federal funds and the ECB
deposit-facility rate. The repository does not contain a reliable daily
three-month Euribor fixing series. Barchart contract histories are fixed
contracts, not continuation generics.

Intraday marks and fills in this handoff came from user screenshots. They must
remain labelled as such. Cross-currency sizing requires current EUR/GBP and
FX-adjusted DV01; do not imply that equal lots are exactly risk matched.

## Live position

The user is live in one SONIA calendar:

- Buy September 2027 SONIA futures.
- Sell December 2026 SONIA futures.
- Official combination fill: **−0.625** in futures-price terms.
- Equivalent entry slope: **+62.5 bp** in rate space.
- Size: one spread.
- Approximate DV01: **£25 per bp**.
- Stop: **−0.725** price spread, equivalent to **+72.5 bp** rate buildup.
- Thesis: BoE peak buildup compresses because policy is already restrictive
  and tightening materially beyond the expected next hike is overpriced.

The official combination fill is authoritative. The broker's allocated leg
averages were:

- Short December 2026 at 95.774, implying 4.226%.
- Long September 2027 at 95.151, implying 4.849%.
- Those allocations imply a 62.3 bp slope, but the combo fill implies 62.5 bp.

The latest user screenshot showed:

- December 2026 at 95.820, implying 4.180%.
- September 2027 at 95.220, implying 4.780%.
- Marked calendar price of −0.600 and rate slope of +60.0 bp.
- Executable liquidation estimate from shown bid/ask: −0.610.

At those screenshot marks, the September long had gained 6.9 price bp
(approximately £172.50), the December short had lost 4.6 bp (approximately
£115), and net marked profit was about 2.3 bp or £57.50. The executable
estimate was about +1.5 bp or £37.50. The 25 September Barchart settlement was
−0.615 / +61.5 bp, implying about +1 bp or £25 versus the combo fill.

The position path is in
`research/notes/figures/sonia_live_calendar_path_2026-09-25.png`; its raw data
are in
`data/cache/stir_curves/sonia_live_calendar_path_2026-09-25.csv`.

The latest rolling 30-session beta of September 2027 to December 2026 was about
**2.12**. December 2026 is therefore only a partial hedge in a peak-led
selloff. High beta helps the long calendar in rallies because September 2027
rallies more; it hurts in hawkish selloffs because September 2027 sells off
more. The hedge has not become safer as the slope steepened. Since March, the
relationship went the other way: the slope and rolling beta rose together.

The detailed position record is in `memory/trades.yaml`.

## Latest weekly curve state: 18 to 25 September 2026

These are changes in implied rates, not futures prices.

### SOFR

The front was roughly unchanged while 2028–29 rates rose about 14–17.5 bp.
The September 2027 minus December 2026 buildup steepened 7 bp. The December
2028 minus September 2027 reversal steepened 7.5 bp. Peak curvature fell
0.5 bp. June 2028 minus June 2027 steepened 8 bp to 0 bp.

### Euribor

December 2026 rallied 3.5 bp, September 2027 sold off 3 bp, December 2028 sold
off 10 bp, and December 2029 sold off 12 bp. Buildup steepened 6.5 bp to
**+60 bp**. Reversal steepened 7 bp to **−6 bp**. Peak curvature fell 0.5 bp
to **+66 bp**. June 2028 minus June 2027 steepened 9 bp to **+4.5 bp**.

### SONIA

December 2026 rallied 4.5 bp, September 2027 rallied 6 bp, and December 2028
sold off 5 bp. Buildup flattened 1.5 bp to **+61.5 bp**. Reversal steepened
11 bp to **−4.5 bp**. Peak curvature fell 12.5 bp to **+66 bp**. June 2028
minus June 2027 steepened 11.5 bp to **+6.5 bp**.

The week's important pattern was a pronounced steepening of the post-peak
reversal curves, especially SONIA, while the live SONIA buildup finally
flattened modestly. The GBP-minus-EUR buildup box compressed to only +1.5 bp,
so the formerly extreme cross-market entry largely disappeared.

## Current ranked opportunities at the data cutoff

### 1. Euribor June 2028 minus June 2027 flattener

The preferred outright idea is to pay/sell June 2027 and receive/buy June
2028, profiting if the rate slope falls.

- Current rate slope: **+4.5 bp**.
- Futures-price calendar: **−0.045**.
- Percentile since March: about **95th**.
- March-to-date mean: **−5.7 bp**.
- Rolling beta of June 2028 to June 2027: **0.89**.
- Correlation: **0.94**.

This has a much better valuation entry than it did when first examined at
−4.5 bp. The plot is
`research/notes/figures/euribor_jun28_jun27_since_march_2026-09-25.png`; raw
data are in
`data/cache/stir_curves/euribor_jun28_jun27_since_march_2026-09-25.csv`.

### 2. Long Euribor June calendar versus short SONIA June calendar

The relative trade is:

- Euribor: receive June 2027 and pay June 2028, which is long a flattening of
  the Euribor June calendar.
- SONIA: pay June 2027 and receive June 2028, which is short that flattening.

The Euribor-minus-SONIA segment level was **−2 bp**, at the 9th percentile for
the long direction. Beta of the Euribor segment to the SONIA segment was
**0.70**, with **0.77** correlation. This was the best cross-market curve
relative-value candidate, subject to FX-adjusted DV01 sizing.

### 3. SOFR June 2028 minus June 2027 flattener

The slope was **0 bp**, about the 94.5th percentile, with beta of approximately
**0.84**. This is attractive but ranked behind Euribor.

### 4. SONIA June 2028 minus June 2027 flattener

The slope was **+6.5 bp**, about the 95.9th percentile, with beta around
**1.04**. Valuation is strong, but it overlaps the live SONIA peak exposure;
the relative Euribor-versus-SONIA version is cleaner for this book.

### 5. SONIA reversal flattener

Pay September 2027 and receive December 2028. The December 2028 minus
September 2027 reversal was **−4.5 bp**, with beta about **0.86**. This is a
fair hedge entry, not an extreme valuation. In equal size it cancels the live
position's September 2027 leg and leaves a December 2028 versus December 2026
exposure, so it materially changes rather than merely hedges the live thesis.

### Trades not to chase

The GBP-minus-EUR buildup box had compressed to **+1.5 bp** and was no longer
extreme. Relative peak curvature was around zero. Receiving SONIA September
2027 against paying Euribor September 2027 stood at a +120.5 bp differential,
the floor of the March sample, while beta of SONIA to Euribor was about 1.084.
It failed the user's stated requirement that the long UK leg have beta below
one to the short EUR leg.

The Barclays Euribor December 2028 minus December 2027 flattener was at
**−6.5 bp**, versus the report's −13 bp entry, −35 bp target and 0 bp stop.
The entry had improved, but it was still near the 9th percentile and the
−35 bp target lay outside the observed 2026 floor of approximately −14 bp.
The June calendar was preferred.

## How the thesis evolved

### Sequential bear-steepening to bear-flattening in Euribor

The user's hypothesis was that a hawkish ECB eventually protects longer
forwards during selloffs: peak-adjacent curves first bear-steepen, but as the
market accepts persistent restriction the farther contract stops selling off
more than the nearer contract. Different one-year curve segments could cross
from bear-steepening to bear-flattening sequentially.

The evidence through 18 September supported a qualified version:

- December 2028 minus December 2027 had shifted most clearly in the 2027–28
  block. Its rolling beta was about 0.72, and it flattened on 76% of recent
  near-leg selloff days.
- June 2028 minus June 2027 was the incomplete boundary, not yet a completed
  copy. Beta was about 0.84 and it flattened on only 44% of recent near-leg
  selloff days.
- March 2028 minus March 2027 still bear-steepened.
- September and December 2027–28, and some 2028–29 calendars, showed stronger
  flattening behaviour.
- The post-ECB sequence was the best evidence: nearer calendars re-steepened
  while farther calendars progressively held or flattened.

Subsequent selloffs steepened the June calendar sharply from −4.5 bp to
+4.5 bp. That improved the valuation entry for a flattener but also showed
that the regime shift was not mechanically complete. The trade is now an
attractive valuation-plus-beta expression, not proof that every hawkish
selloff must flatten the curve.

### June 2027 minus June 2026 was not the same trade

June 2026 expired on 15 June 2026. June 2027 minus June 2026 was a
fixing-to-peak gap, not a live post-peak forward calendar. Before expiry it
bear-steepened strongly: ex-final beta was roughly 1.8, and on recent June
2026 selloff days June 2027 sold off much more. The sequential protection
thesis begins when the **back** leg lies beyond the peak; it does not extend
back to an anchored fixing contract.

### Fading BoE peak pricing

The user's core conviction was to receive the UK peak, but only with a hedge
that made relative-value sense in hawkish conditions. Several expressions
were tested.

Receiving September 2027 and paying December 2026 was attractive at the
original +63 bp extreme, but the December hedge was not selloff-neutral.
Rolling beta rose from below one in March to above two by September because
December volatility collapsed while September remained volatile. A 1:1
calendar reduced outright volatility but did not protect fully in hawkish
selloffs. A roughly 2× December hedge would neutralise the latest beta but
would introduce paid parallel DV01 and severe regime-reversal risk.

The cross-market box—short SONIA buildup versus long Euribor buildup—was
initially compelling at about +9.5 bp, near the top of the March sample.
Recent buildup-change correlation was high and a 1:1 box materially reduced
daily volatility. A 0.5–0.75 EUR hedge was preferred when the true conviction
was mainly an absolute BoE fade; 1:1 was appropriate only with an additional
view that GBP's higher beta would normalise.

Fundamentally, the user highlighted that the ECB had already raised twice,
was at the top of its neutral range, explicitly downplayed neutral and was
willing to enter restrictive territory, whereas the BoE already described
conditions as restrictive. Yet the curve priced approximately 10 bp more
post-December buildup in the UK than in the euro area. That was difficult to
justify as a base case.

The important qualification was that the two delivered ECB hikes did not
mechanically enter the box, because both legs begin at December 2026. They
altered the fair-value context by front-loading the ECB cycle. The 10 bp was
also not literally ten basis points of policy hikes: it included three-month
basis, risk premium, different cycle timing and energy-tail compensation.
The trade was a tail-premium fade, not deterministic arbitrage.

By 25 September the box had compressed to +1.5 bp. The thesis had paid, but
the fresh relative entry no longer offered the original valuation asymmetry.

## Sell-side evidence and how it was used

The key PDFs are under `research/pdfs/`:

- `GS_European_Daily_BoE_Recap_2026-09-17.pdf`
- `GS_Euro_Area_Inflation_Nearcast_2026-09-19.pdf`
- `GS_Global_Rates_Trader_Hiking_More_or_Less.pdf`
- `Barclays_Global_Rates_Weekly_On_the_brink.pdf`
- `Barclays_Global_Rates_Weekly_Not_enough_to_break.pdf`
- `Barclays_Global_Economics_Weekly_High_oil_high_rates.pdf`
- `GS_What_is_Priced_in_end_week_ef93.pdf`

The GS BoE recap had a baseline of one November hike to 4%, with a
probability-weighted path below market. It cited soft labour, benign
underlying inflation and tight financial conditions. This supported fading
additional UK buildup beyond the next hike.

The GS euro inflation nearcast projected December headline inflation around
3.85%, core around 2.62%, and an early-2027 core peak around 2.8%. It supported
a hawkish ECB tail but did not itself prove post-December hikes.

The user pasted a GS ECB recap that expected a December hike to 2.75%, saw a
low hurdle for 3%, assigned a meaningful tail to 3.5%, and delayed cuts to
late 2027/early 2028. The report said the probability-weighted near-term path
was close to market but 2027 pricing was notably above its forecast. Thus it
supported ECB persistence relative to the BoE while not establishing that the
EUR buildup was independently cheap.

Barclays recommended the Euribor December 2028 minus December 2027 flattener.
Its target was more extreme than the observed 2026 sample, which is why it was
not accepted uncritically.

Detailed source evaluations are in:

- `research/notes/gbp_eur_u27_z26_buildup_box_gs_2026-09-21.md`
- `research/notes/boe_peak_fade_hedged_2026-09-20.md`
- `research/notes/barclays_erz7z8_analogues_2026-09-19.md`
- `research/notes/eur_short_m27m28_2026-09-21.md`
- `research/notes/eur_calendar_regime` results are represented by
  `data/cache/stir_curves/eur_calendar_regime.json`.

## Workbook contents

`research/stir_full_rv_universe_latest.xlsx` is the broad screen. It contains:

- 45 active fixed contracts.
- 1,980 ordered contract pairs.
- 702 ordered curve-segment pairs.
- Contract and segment directories.
- Curated and algorithmic opportunity sheets.
- Within-market pairs, cross-market pairs, matched bellies and matched
  segment relative value.
- Raw rates, prices, changes and segment histories.

For each pair it reports the current level, percentile, z-score, range,
one-day and five-day P&L, rolling 30-session beta of the long leg to the short
leg, beta-below-one flag, correlation, R-squared, long/short volatility,
residual volatility, 1:1 and beta-hedged P&L volatility, win rate and explicit
month-by-month implementation.

Interpret beta carefully:

- Beta below one means one short unit overhedges the long leg against the
  sampled common factor.
- Beta around one means broadly matched sampled sensitivity.
- Beta above one means one short unit underhedges the long leg.
- Beta is descriptive and regime-dependent, not a guarantee.
- Cross-currency pairs still require FX-adjusted DV01.

`research/peak_rv_universe_latest.xlsx` is the focused four-primitive screen:
GBP and EUR buildup and reversal. It includes all ordered differences, unique
differences and sums, ratios, signed combinations, correlations, betas,
candidate trades and raw data. Remember that buildup plus reversal cancels
September 2027 and equals December 2028 minus December 2026. The true peak
richness measure is buildup minus reversal.

## Reproducible refresh

From the repository root:

```bash
PYTHONPATH=. python3 scripts/fetch_barchart_stir.py
PYTHONPATH=. python3 scripts/build_stir_panel.py --asof YYYY-MM-DD
PYTHONPATH=. python3 scripts/build_peak_rv_workbook.py
PYTHONPATH=. python3 scripts/build_full_rv_workbook.py
python3 scripts/build_dashboard_data.py
python3 scripts/pack_dashboard_bundle.py
python3 -m pytest tests/ -q
```

The fetch depends on a headed browser because Barchart's WAF blocks ordinary
requests. A `BARCHART_API_KEY` or institutional feed remains the highest-value
reliability upgrade.

## Repository map for continuity

- Standing conventions and decisions: `memory/book.md`
- Live trade ledger: `memory/trades.yaml`
- Reconstructable chronology: `memory/sessions/YYYY-MM-DD.md`
- Current market panel: `data/cache/stir_curves/panel.csv`
- Raw Barchart histories: `data/raw/stir_futures/histories_raw.json.gz`
- One note per trade thesis: `research/notes/`
- Source research: `research/pdfs/`
- Reproducible calculations: `scripts/` and `lib/stir/`
- Tests: `tests/`

The dated session files from 19–26 September preserve the progression from
initial curve construction, through the Euribor sequential-regime analysis,
the BoE peak-fade debate, trade entry, adverse selloff, weekly recovery and
the final exhaustive relative-value screen.

## What the user expects next

When asked for “this morning,” “midday,” or “now,” refresh or use a supplied
broker screenshot. Do not answer with the 25 September settlement as if it
were live. State the timestamp and source.

When reviewing the live SONIA trade, decompose P&L by leg. The user wants to
know whether the peak contract or the front hedge caused the move, not merely
the net.

When proposing a cross-market trade, report valuation and rolling beta in the
requested direction—long leg conditional on short leg—and explain whether a
1:1 short overhedges or underhedges. Also state the FX/DV01 caveat.

The immediate opportunity set at this handoff favours the Euribor June
2028-minus-June 2027 flattener and the relative Euribor-versus-SONIA June
calendar trade. The old UK-versus-EUR buildup box should not be recommended
from stale +9.5 bp valuation because it had compressed to +1.5 bp.

## Potential upgrades

The agent is personalised through repository-backed memory, not perfect chat
recall. It can fetch, analyse, build workbooks, test, commit and publish while
active. It does not stay continuously awake without an automation.

The most useful upgrades are:

1. Add a Barchart API key or institutional futures feed.
2. Enable GitHub Pages and ensure the refresh workflow is on the default
   branch.
3. Schedule a daily post-settlement research refresh.
4. Import broker fills and positions.
5. Add live EUR/GBP for exact cross-currency sizing.
6. Add OIS, fixings, options and meeting-pricing inputs.
7. Record explicit targets, stops and risk budgets for every live trade.

If this file and the repository disagree, prefer the newest timestamped source
and explain the discrepancy rather than silently choosing one.
