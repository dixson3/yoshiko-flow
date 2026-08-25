#!/usr/bin/env bash
# ctl-199b-recursion (SC6b) — DEPTH 0 and DEPTH 1 EVALUATE; DEPTH 2 returns exit 2
# (INCONCLUSIVE) WITHOUT EXECUTING.
#
# Asserted on DEPTH, never on a name match. `YF_RECHECK_DEPTH` is the LOAD-BEARING guard; any
# name-check is BEST-EFFORT and scans the EXECUTED COMMAND STRING ONLY, never the criterion
# row — a criterion row may legitimately *discuss* the verb, and in this plan every clause
# routes through gate-run.sh so no clause contains the literal `recheck-criteria` at all.
#
# Depth 1 MUST evaluate: a criterion's command routes through the plan's harness and so runs
# one level down when the verb is invoked from the §6.4 close chain. A guard refusing at
# depth 1 would make the four fixture-driven controls (SC6/SC8/SC9/SC10) valid standalone and
# INCONCLUSIVE under the chain — which is the state this plan exists to prevent.
#
# UNCOMMISSIONED-INTERFACE RULE: an absent verb is EXIT 1, never exit 2.
# Exit: 0 the depth rule holds · 1 real negative · 2 instrument failure
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
PM="$REPO/skills/yf-plan/scripts/plan_manager.py"

# ---------------------------------------------------------------------------------------
# Helpers are INLINED rather than sourced from a sibling library. A shared file under
# assets/ would be an artifact no issue's `touches:` declares — and amending the plan's
# Epics to declare it would invalidate the approval fingerprint mid-execution. Issue 2.1 is
# the sole writer of all five ctl-199b-* files, so the single-writer rule still holds.
# ---------------------------------------------------------------------------------------
# require_verb — the UNCOMMISSIONED-INTERFACE RULE in one place.
# An absent `recheck-criteria` is a REAL NEGATIVE (exit 1), never argparse's exit 2.
require_verb() {
  [ -r "$PM" ] || { echo "INCONCLUSIVE: plan_manager.py unreadable: $PM" >&2; exit 2; }
  if ! uv run "$PM" --help 2>&1 | grep -q 'recheck-criteria'; then
    echo "FAIL: plan_manager.py exposes no 'recheck-criteria' verb." >&2
    echo "      The uncommissioned-interface rule maps this to a REAL NEGATIVE (exit 1):" >&2
    echo "      the verb is absent, which is a different claim from the instrument failing." >&2
    exit 1
  fi
}

# mk_fixture <dir>  — Success Criteria rows on stdin. Builds a minimal conformant bundle.
mk_fixture() {
  local dir="$1"; mkdir -p "$dir"
  local rows; rows="$(cat)"
  cat > "$dir/plan.md" <<PLANEOF
---
type: Plan
okf_spec: OKF-PLAN
id: plan-997-fixture-recheck
author: fixture
created: '2026-01-01'
status: executing
---
# Plan: pinned recheck fixture

**ID:** plan-997-fixture-recheck
**Author:** fixture
**Created:** 2026-01-01
**Status:** executing

## Objective
A pinned fixture for the completion-time re-check. Never live plan state.

## Motivation
A control written against live state is not a control.

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
  - touches: \`src/a.py\`

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
${rows}
PLANEOF
  printf '# Log\n\n## 2026-01-01\n\n- executing: fixture\n' > "$dir/log.md"
}


require_verb
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
SENTINEL="$tmp/executed"
mk_fixture "$tmp/fx" <<ROWS
| SC1 | evaluates, and leaves a trace that it ran | \`touch $SENTINEL\` → exit 0 | 1.1 |
ROWS

fail=0
at_depth() { # <depth> -> prints "rc verdict executed"
  rm -f "$SENTINEL"
  local out rc
  out="$(YF_RECHECK_DEPTH="$1" uv run "$PM" recheck-criteria "$tmp/fx" --json 2>/dev/null)"; rc=$?
  local ex=no; [ -e "$SENTINEL" ] && ex=yes
  local v; v="$(printf '%s' "$out" | python3 -c 'import json,sys;
try: d=json.load(sys.stdin)
except Exception: print("?"); raise SystemExit
print(str(d.get("verdict") or d.get("status") or "?").upper())' 2>/dev/null)"
  echo "$rc ${v:-?} $ex"
}

for d in 0 1; do
  read -r rc v ex <<<"$(at_depth $d)"
  if [ "$ex" != "yes" ]; then
    echo "FAIL: at depth $d the criterion command did NOT execute (verdict $v, rc $rc)" >&2
    echo "      depth 0 and depth 1 must EVALUATE" >&2
    fail=1
  elif [ "$v" = "INCONCLUSIVE" ]; then
    echo "FAIL: at depth $d the verdict is INCONCLUSIVE; depth $d must evaluate" >&2
    fail=1
  else
    echo "ok: depth $d evaluated (verdict $v, rc $rc, command ran)"
  fi
done

read -r rc v ex <<<"$(at_depth 2)"
if [ "$ex" = "yes" ]; then
  echo "FAIL: at depth 2 the criterion command EXECUTED; depth 2 must refuse WITHOUT executing" >&2
  fail=1
elif [ "$rc" != "2" ]; then
  echo "FAIL: at depth 2 the exit code is $rc, expected 2 (INCONCLUSIVE)" >&2
  fail=1
else
  echo "ok: depth 2 returned exit 2 without executing (verdict $v)"
fi

[ "$fail" -eq 0 ] || exit 1
echo "PASS: depth 0 and 1 evaluate; depth 2 is INCONCLUSIVE without executing"
