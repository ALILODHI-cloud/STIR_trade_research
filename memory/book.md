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
- [ ] GitHub App not installed on the repo — pushes are blocked, so nothing
      here is durable yet. This is the highest-priority open item.

## Decision log

Newest last. One line each: date, decision, why.

- 2026-09-19 — Repo is the memory mechanism, not the agent. Because context
  does not survive across sessions and gets compacted within them.
- 2026-09-19 — Market levels never come from model memory. Training data ends
  ~May 2026; stale levels that look confident are worse than no levels.
