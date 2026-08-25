#!/usr/bin/env bash
# ctl-199b-inconclusive (SC8) — an INCONCLUSIVE re-check maps to `warn` and NEVER hard-fails
# completion.
#
# The corpus is unmigrated: measured over `docs/plans/plan-*/plan.md`, 6 of 52 bundles carry
# the four-column shape and exactly ONE carries a clause-form criterion. So INCONCLUSIVE is
# the EXPECTED verdict almost everywhere, and hard-gating on it would be an outage rather
# than a check. This follows the REQ-DATA-057 precedent, where the linter's own breakage must
# not become an intake outage.
#
# UNCOMMISSIONED-INTERFACE RULE: an absent verb is EXIT 1, never exit 2.
# Exit: 0 INCONCLUSIVE maps to warn and does not hard-fail · 1 real negative · 2 instrument
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

# A plan with NO machine-readable criterion: nothing can be evaluated -> INCONCLUSIVE.
mk_fixture "$tmp/fx" <<'ROWS'
| SC1 | prose only | reviewer confirms it looks right during review | 1.1 |
| SC2 | prose only | verified by inspection | 1.1 |
ROWS

OUT="$(uv run "$PM" recheck-criteria "$tmp/fx" --json 2>/dev/null || true)"
RC=$?
[ -n "$OUT" ] || { echo "INCONCLUSIVE: no output" >&2; exit 2; }

printf '%s' "$OUT" | python3 -c '
import json, sys
rc = int(sys.argv[1])
try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"INCONCLUSIVE: output is not JSON: {e}", file=sys.stderr); raise SystemExit(2)
v = str(d.get("verdict") or d.get("status") or "").upper()
if v != "INCONCLUSIVE":
    print(f"FAIL: a plan with no machine-readable criterion returned {v!r}, "
          f"expected INCONCLUSIVE", file=sys.stderr)
    raise SystemExit(1)
sev = str(d.get("severity") or d.get("maps_to") or "").lower()
if sev != "warn":
    print(f"FAIL: INCONCLUSIVE maps to {sev!r}, expected \"warn\" (REQ-DATA-057 precedent)",
          file=sys.stderr)
    raise SystemExit(1)
if rc == 1:
    print("FAIL: an INCONCLUSIVE re-check exited 1 (a hard fail); it must never hard-fail "
          "completion", file=sys.stderr)
    raise SystemExit(1)
print(f"PASS: INCONCLUSIVE maps to warn and exits {rc} — completion is not hard-failed")
' "$RC"
