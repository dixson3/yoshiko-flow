#!/usr/bin/env bash
# ctl-class-a-fraction (SC7) — this plan's own criteria are >= 90% class-(a), measured by a
# NON-RECURSIVE tool reading plan_extract.py output.
#
# Class-(a) is the MACHINE-RUNNABLE form only: a backticked command plus a polarity marker
# (`-> exit 0|1|2|non-zero`). `manual:` is class-(b) BY DESIGN — counting it as class-(a)
# would make the floor satisfiable by writing `manual:` on every row, which is precisely risk
# R3 ("manual: becomes the universal escape hatch").
#
# The tool is non-recursive on purpose: it reads plan_extract.py's JSON and never invokes
# recheck-criteria, so the criterion measuring coverage cannot be satisfied by the machinery
# it measures.
#
# This plan is GREEN here (35/36 = 97.2%), so RED comes from a PINNED PROSE-CELL FIXTURE.
#   CTL_RED=1  measure the fixture alone and return its verdict (a real negative, exit 1)
#
# Exit: 0 fraction >= floor and the fixture is a real negative · 1 real negative · 2 cannot run
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
PLAN_DIR_REL="docs/plans/plan-052-james-dixson-fa8056"
FLOOR=90

measure() { # <plan-dir-abs> -> prints "class_a total pct"; exit 2 if it cannot run
  uv run "$REPO/_shared/plan_extract.py" "$1" --json 2>/dev/null | python3 -c '
import json, re, sys
try:
    docs = json.load(sys.stdin)
except Exception:
    sys.exit(2)
d = docs[0] if isinstance(docs, list) else docs
rows = d.get("criteria") or []
if not rows:
    sys.exit(2)
# The clause grammar (REQ-DATA-070): a backticked command, then a polarity marker.
CLAUSE = re.compile(r"`.+`\s*(?:→|->)\s*exit\s+(?:0|1|2|non-zero)\s*$")
a = sum(1 for r in rows if CLAUSE.search((r.get("verification") or "").strip()))
print(a, len(rows), round(100.0 * a / len(rows), 1))
'
}

report() { # <label> <plan-dir-abs> -> 0 at/above floor, 1 below, 2 cannot measure
  local out; out=$(measure "$2") || return 2
  [ -n "$out" ] || return 2
  local a t p; read -r a t p <<<"$out"
  local ok; ok=$(python3 -c "print(1 if float('$p') >= $FLOOR else 0)")
  if [ "$ok" = "1" ]; then
    echo "ok: $1 — class-(a) $a/$t = ${p}% (floor ${FLOOR}%)"
    return 0
  fi
  echo "FAIL: $1 — class-(a) $a/$t = ${p}%, below the ${FLOOR}% floor" >&2
  return 1
}

# --- pinned prose-cell fixture ---------------------------------------------------
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/prose"
cat > "$tmp/prose/plan.md" <<'FIX'
---
type: Plan
okf_spec: OKF-PLAN
id: plan-999-fixture-prose
author: fixture
created: '2026-01-01'
status: drafting
---
# Plan: pinned prose-cell fixture

**ID:** plan-999-fixture-prose
**Author:** fixture
**Created:** 2026-01-01
**Status:** drafting

## Objective
A pinned fixture whose Verification cells are PROSE. It exists so this control can be RED.

## Motivation
A control that cannot be RED proves nothing.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Investigation Findings
None.

## Approach
None.

## Epics
### Epic 1: fixture
- Issue 1.1: do the thing

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | none | low | none |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | the thing is done | reviewer confirms it looks right | 1.1 |
| SC2 | the other thing is done | verified by inspection during review | 1.1 |
| SC3 | it works | the team agrees it works | 1.1 |
FIX

if [ "${CTL_RED:-0}" = "1" ]; then
  report "pinned prose-cell fixture" "$tmp/prose"; rc=$?
  echo "CTL_RED: measurement over the pinned prose fixture returned $rc (1 = real negative)"
  exit $rc
fi

report "pinned prose-cell fixture" "$tmp/prose" 2>/dev/null; neg=$?
if [ "$neg" -ne 1 ]; then
  echo "FAIL: the pinned prose fixture did NOT produce a real negative (got $neg)" >&2
  exit 1
fi
echo "ok: pinned prose-cell fixture -> exit 1 (a real negative)"

report "plan-052" "$REPO/$PLAN_DIR_REL"; live=$?
[ "$live" -eq 2 ] && exit 2
[ "$live" -eq 0 ] || exit 1
echo "PASS: class-(a) fraction is at or above the ${FLOOR}% floor"
