#!/usr/bin/env bash
# ctl-199b-fields (SC6) — `recheck-criteria` reports `class_a_fraction` AND
# `evaluated_fraction` as DISTINCT numbers, run against a FIXTURE plan.
#
# Two fields, never one conflated "coverage": they answer different questions. A plan whose
# criteria are 20% machine-readable and one whose harness failed on 80% of them would report
# the same single number, and the two call for opposite responses.
#
# The fixture is built so the two figures MUST differ — a control whose fixture makes them
# coincide cannot tell a real implementation from one returning the same value twice.
#
# The verb is shipped by Issue 2.2; this control is built by 2.1.
# UNCOMMISSIONED-INTERFACE RULE: an absent verb is EXIT 1 (a real negative), never exit 2.
# Exit: 0 both fields present, numeric and distinct · 1 real negative · 2 instrument failure
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
mk_fixture "$tmp/fx" <<'ROWS'
| SC1 | passes | `true` → exit 0 | 1.1 |
| SC2 | passes | `true` → exit 0 | 1.1 |
| SC3 | fails specifically | `false` → exit 1 | 1.1 |
| SC4 | cannot run here | `/nonexistent/definitely-not-a-command-xyz` → exit 0 | 1.1 |
| SC5 | prose, class-(b) | reviewer confirms it looks right | 1.1 |
| SC6 | manual, class-(b) | manual: a reader judgement | 1.1 |
ROWS

OUT="$(uv run "$PM" recheck-criteria "$tmp/fx" --json 2>/dev/null || true)"
[ -n "$OUT" ] || { echo "INCONCLUSIVE: recheck-criteria produced no output" >&2; exit 2; }
printf '%s' "$OUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"INCONCLUSIVE: output is not JSON: {e}", file=sys.stderr); raise SystemExit(2)
missing = [k for k in ("class_a_fraction", "evaluated_fraction") if k not in d]
if missing:
    print(f"FAIL: missing field(s) {missing}; got keys {sorted(d)}", file=sys.stderr)
    raise SystemExit(1)
a, e = d["class_a_fraction"], d["evaluated_fraction"]
for name, v in (("class_a_fraction", a), ("evaluated_fraction", e)):
    if not isinstance(v, (int, float)):
        print(f"FAIL: {name} is {v!r}, not a NUMBER", file=sys.stderr); raise SystemExit(1)
    if not 0.0 <= float(v) <= 1.0:
        print(f"FAIL: {name} = {v} is outside [0,1]", file=sys.stderr); raise SystemExit(1)
if float(a) == float(e):
    print(f"FAIL: class_a_fraction and evaluated_fraction are BOTH {a} on a fixture built to "
          f"make them differ — the two are conflated", file=sys.stderr)
    raise SystemExit(1)
print(f"PASS: class_a_fraction={a} and evaluated_fraction={e} are distinct numbers")
'
