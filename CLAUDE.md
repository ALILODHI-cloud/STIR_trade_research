# DM STIR research

Research support for a developed-markets short-term interest rate book:
SOFR, SONIA, ESTR/Euribor, TONA, CORRA, AUD/NZD bank bills. The work is
evaluating trade ideas — what is priced, what the structure actually pays,
what breaks it — not building a production pricing system.

## Working agreement

- **Never state a market level from memory.** Training knowledge ends around
  May 2026. Every level, spread, fly or meeting-pricing number must come from
  a file in `data/`, something the user pasted, or a source PDF. If it isn't
  one of those, say so rather than filling the gap.
- **Separate what's priced from what's forecast.** Start any idea by pinning
  down what the curve already discounts, then argue about the delta.
- **Show the arithmetic.** Carry, roll, DV01 and breakevens go in code that
  can be re-run, not prose. Prose that can't be reproduced is an opinion.
- **Sell-side research is an input, not an authority.** Extract the thesis and
  the numbers, then test them. Say where it's wrong or where it's asserting
  rather than showing. These PDFs are licensed material — use them for this
  book's analysis; don't reproduce them wholesale.
- The container is ephemeral. Anything worth keeping gets committed.

## Data

This session's egress policy blocks the public data hosts (FRED, CME,
NY Fed, ECB, BoE all return 403 at the proxy). Verified, not assumed. So:

1. **Files on disk win.** `lib/stir/data.py` looks in `data/cache/` then
   `data/raw/` before it ever tries the network. Drop exports in `data/raw/`
   named after the series (`SOFR.csv`, first column dates, second values).
2. **Pasted levels** go in `data/manual/*.yaml` — see `strip_example.yaml`.
3. **If the hosts get allowlisted**, `load_series(..., fetch=True)` starts
   working with no change to call sites.
4. `research/pdfs/` is where sell-side PDFs go. Commit them alongside the
   analysis so the reasoning stays auditable.

## Layout

```
lib/stir/conventions.py   contract specs, IMM dates, DV01s, symbol parsing
lib/stir/futures.py       price/rate, spreads/flies/condors, strips, roll
lib/stir/ois.py           meeting-dated OIS: step bootstrap + reconstruction
lib/stir/rv.py            z-scores, PCA, hedge ratios, half-life, RV screen
lib/stir/data.py          local-first loaders, source registry
research/notes/           one markdown file per trade idea
research/pdfs/            source research
scripts/                  runnable analyses
```

## Conventions worth knowing before reading output

- **Spread** `(1,-1)` in rate space = front rate − back rate. Positive means
  inverted, i.e. cuts priced.
- **Fly** `(1,-2,1)` in rate space = wing1 − 2·body + wing2. Positive means
  the body rate sits *below* the line through the wings. Desks differ on this
  sign — if yours is the other way, negate at the reporting layer, don't
  change the weights (the tests pin them).
- **OIS steps** are keyed on policy *effective* dates, not announcement
  dates. For the Fed that's the day after the FOMC.
- **AUD/NZD bills** are discount-priced, so their DV01 moves with the level.
  `convention("IR").dv01` deliberately raises rather than return a wrong
  constant; use `futures.bill_dv01(price, conv)`.
- A quote spanning several unsolved meetings is under-determined. The
  bootstrap splits it evenly and says so — that's a convention, not a result.

## Running things

```
python3 -m pytest tests/ -q
python3 scripts/example_meeting_pricing.py
```
