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

## Data sourcing plan (as of 2026-09-19)

- Chosen candidate: **Barchart**, for both latest-day settles and historical
  daily bars per fixed contract. Owner corrected an earlier claim of mine that
  futures settlement history was only obtainable from a terminal — Barchart's
  API serves history too.
- Blocked on two things:
  1. Egress. Every external host is denied (17/17 providers tested, incl.
     Barchart, Yahoo, Stooq, FRED, CME, ICE). The proxy bypass list contains
     only package registries and Anthropic APIs. Fix is the environment's
     network access policy at claude.ai/code, not a different vendor.
  2. An API key. Preferred over page-scraping: stable format, no terms
     friction. Store as an env var, never in the repo.
- UNVERIFIED: Barchart's coverage of ICE products (Euribor, SONIA). CME
  (SOFR) expected fine. Cheaper tiers often exclude ICE entitlements. Test
  empirically before designing around it.
- Contract symbols on Barchart must be confirmed against the live API, not
  assumed. Use FIXED contracts (ERZ6, SR3H7), never generics (ER1, SFR1) —
  generics roll, which silently splices contracts and invalidates any
  change-over-time or biggest-mover calculation.

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
