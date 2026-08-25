#!/usr/bin/env bash
# ctl-199b-rot (SC9) — a criterion TRUE at discharge and FALSE at completion is CAUGHT.
#
# This reproduces plan-051's SC4b, the defect that triggered this whole plan: the criterion
# was measured green at the issue that discharged it and was false two epics later, because a
# file added downstream matched its pattern and nothing re-ran the check. It was caught by an
# operator re-measurement, not by anything the plan shipped.
#
# The fixture reproduces the SHAPE, not the text: a criterion whose command depends on the
# state of a directory. It passes when the fixture is built, then a later write makes it
# false — exactly "a file added downstream matched its pattern".
#
# UNCOMMISSIONED-INTERFACE RULE: an absent verb is EXIT 1, never exit 2.
# Exit: 0 the rot is caught · 1 real negative · 2 instrument failure
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
mkdir -p "$tmp/tree"
printf 'ok\n' > "$tmp/tree/good.txt"

# The criterion: "no .bad file exists under tree/". True now.
mk_fixture "$tmp/fx" <<ROWS
| SC1 | no .bad file exists under the tree | \`test -z "\$(ls $tmp/tree/*.bad 2>/dev/null)"\` → exit 0 | 1.1 |
| SC2 | the tree exists | \`test -d $tmp/tree\` → exit 0 | 1.1 |
ROWS

# --- at DISCHARGE time the criterion is TRUE ---
if ! uv run "$PM" recheck-criteria "$tmp/fx" --json >/dev/null 2>&1; then
  echo "INCONCLUSIVE: the re-check does not pass on a fixture whose criteria are all TRUE" >&2
  exit 2
fi
echo "ok: at discharge time the re-check is green"

# --- two epics later, a file added downstream matches the pattern ---
printf 'rot\n' > "$tmp/tree/added-downstream.bad"

OUT="$(uv run "$PM" recheck-criteria "$tmp/fx" --json 2>/dev/null || true)"
RC=$?
if [ -z "$OUT" ]; then echo "INCONCLUSIVE: no output on the rotted fixture" >&2; exit 2; fi
printf '%s' "$OUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"INCONCLUSIVE: output is not JSON: {e}", file=sys.stderr); raise SystemExit(2)
v = str(d.get("verdict") or d.get("status") or "").upper()
failed = d.get("failed") or d.get("false_criteria") or []
if v in ("FAIL", "FALSE") or failed:
    ids = [f.get("id") if isinstance(f, dict) else f for f in failed] or ["(unnamed)"]
    print(f"PASS: the rotted criterion was CAUGHT at completion — verdict {v}, failed {ids}")
    raise SystemExit(0)
print(f"FAIL: a criterion TRUE at discharge and FALSE at completion was NOT caught "
      f"(verdict {v!r}). This is plan-051 SC4b reproduced.", file=sys.stderr)
raise SystemExit(1)
'
