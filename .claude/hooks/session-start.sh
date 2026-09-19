#!/bin/bash
# SessionStart hook.
#
# Two jobs:
#   1. Install dependencies so tests and linters run immediately.
#   2. Print the durable memory into the session's context.
#
# Job 2 is the important one. The agent does not remember anything between
# sessions; it re-reads. Everything this script prints to stdout becomes
# context at the start of every session, so the memory files are loaded
# whether or not anyone thinks to open them.
#
# Installer chatter goes to stderr on purpose - only memory reaches stdout.

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$PROJECT_DIR"

# --- 1. dependencies -------------------------------------------------------
if [ -f requirements.txt ]; then
  python3 -m pip install --quiet --disable-pip-version-check \
    -r requirements.txt >&2 || echo "WARNING: pip install failed" >&2
fi

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PYTHONPATH=\"$PROJECT_DIR\"" >> "$CLAUDE_ENV_FILE"
fi

# --- 2. memory -------------------------------------------------------------
echo "============================================================"
echo " DURABLE MEMORY - loaded automatically, treat as established"
echo "============================================================"
echo
echo "Read this before answering anything. It is what previous sessions"
echo "knew. You have no other recollection of them."
echo

if [ -f memory/book.md ]; then
  echo "--- memory/book.md ---"
  cat memory/book.md
  echo
fi

if [ -f memory/trades.yaml ]; then
  echo "--- memory/trades.yaml ---"
  cat memory/trades.yaml
  echo
fi

# Most recent session logs, newest first, capped so context stays sane.
if [ -d memory/sessions ]; then
  logs=$(find memory/sessions -name '[0-9]*.md' -type f | sort -r | head -5)
  if [ -n "$logs" ]; then
    echo "--- recent sessions (newest first) ---"
    for f in $logs; do
      echo "### $f"
      head -c 4000 "$f"
      echo
    done
  fi
fi

if [ -d research/notes ]; then
  notes=$(find research/notes -name '*.md' ! -name 'TEMPLATE.md' -type f | sort)
  if [ -n "$notes" ]; then
    echo "--- trade notes on file ---"
    for f in $notes; do
      echo "  $f: $(grep -m1 '^# ' "$f" 2>/dev/null | sed 's/^# //')"
    done
    echo
  fi
fi

echo "============================================================"
echo " MEMORY PROTOCOL: anything the user says that matters beyond"
echo " this session goes into memory/ in the SAME session it is"
echo " said - standing facts and decisions into memory/book.md,"
echo " trades into memory/trades.yaml, the running account into"
echo " memory/sessions/\$(date +%F).md. Do not defer this to the end"
echo " of a session; sessions get truncated and containers die."
echo "============================================================"
