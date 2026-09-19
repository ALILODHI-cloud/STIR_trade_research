# Standing facts — read this before anything else

This file is the durable memory of the book and how its owner works. It is
loaded into every session automatically. If something is true across sessions,
it belongs here. If it only matters to one trade, it belongs in
`research/notes/`.

## Owner

- Runs a developed-markets STIR book (discretionary macro / rates RV).
- New to working with a research agent — prefers plain explanations of what
  the tooling is doing and why, not jargon about the agent itself.
- Wants complete recall across sessions. That is what this directory is for:
  the agent does not remember, it re-reads. Anything said in chat that matters
  later must be written here in the same session it is said.

## Markets in scope

SOFR, SONIA, ESTR/Euribor, TONA, CORRA, AUD/NZD bank bills.

## Conventions agreed

- Fly sign: rate-space `(1,-2,1)`; positive = body rate below the line through
  the wings. NOT YET CONFIRMED against the owner's desk convention — ask.
- Spread sign: rate space, front minus back; positive = inverted.
- OIS steps keyed on policy *effective* dates, not announcement dates.

## Open items / unconfirmed

- [ ] Confirm the desk's fly sign convention.
- [ ] Decide scope of position tracking (ideas only, or full live book).
- [ ] Decide whether to track fills and running P&L.
- [x] RESOLVED 2026-09-19 — GitHub App installed; pushes work. The repo was
      empty, so `claude/hopeful-babbage-ahkapg` is both the only branch and
      the remote's default. New sessions therefore clone it and pick up the
      SessionStart hook with no merge needed. If a separate default branch
      (main/master) is created later, the hook must be merged there or
      sessions will start with no memory loaded.

## Data sourcing plan (as of 2026-09-19, updated same day)

- **Working path:** Barchart core-api via a headed Chrome session that clears
  AWS WAF. Endpoints:
  - `proxies/core-api/v1/historical/get` with `type=eod` for fixed contracts
  - `proxies/core-api/v1/quotes/get` for latest strip prints
- **Confirmed roots on Barchart:** `SQ` = 3M SOFR (not SR3 — that's CME),
  `IM` = 3M Euribor, `J8` = 3M SONIA. Always fixed contracts (`SQZ26`), never
  generics (`SQ*1` / `SQ1`).
- **FRED** is reachable in this environment for spot anchors (`SOFR`,
  `IUDSOIA`/SONIA, `ECBDFR`, `EFFR`). 3M Euribor fixing series not found on
  FRED under the usual tickers; use futures path + DFR for policy context.
- **Yahoo** has SR3 latest only (no useful history). CME settlements HTML
  works in a browser; REST settlements returned empty from this host.
- **API key still preferred** (`BARCHART_API_KEY`) so we can drop the browser
  scrape. Requested as an environment secret; not yet present.
- Scripts: `scripts/fetch_barchart_stir.py` → `data/raw/stir_futures/`,
  `scripts/stir_curve_snapshot.py` → note + interactive HTML.

## Decision log

Newest last. One line each: date, decision, why.

- 2026-09-19 — Repo is the memory mechanism, not the agent. Because context
  does not survive across sessions and gets compacted within them.
- 2026-09-19 — Market levels never come from model memory. Training data ends
  ~May 2026; stale levels that look confident are worse than no levels.
- 2026-09-19 — Memory lives in `memory/` and is loaded by a SessionStart hook,
  not held by the agent. Confirmed working on a session resume.
- 2026-09-19 — Subagents start cold and inherit none of this memory. Use them
  only for parallel, self-contained work (e.g. one PDF each); never for
  judgement that depends on the book.
- 2026-09-19 — Barchart browser scrape is the live futures source until an API
  key lands. Never invent/model missing history (a subagent did; discarded).
- 2026-09-19 — Owner asked for end-2026 priced change + YTD interactive curves
  + 2w movers + Euribor Z27/Z28 inversion check; snapshot asof 2026-09-18 in
  `research/notes/stir_curve_snapshot_2026-09-18.md`.
