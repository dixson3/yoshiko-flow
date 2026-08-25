#!/usr/bin/env bash
# ctl-199a-grammar (SC5) — a PROSE cell FAILS the shape check, a CLAUSE-FORM cell passes, and
# a clause containing a GFM-ESCAPED PIPE survives unescaping.
#
# The shape check (`verification-clause`, REQ-DATA-070) is shipped by Issue 1.2. This control
# is built by 1.1, one issue EARLIER, so at build time it observes an interface that does not
# yet exist.
#
# THE UNCOMMISSIONED-INTERFACE RULE APPLIES: an absent check is mapped to EXIT 1 (a real
# negative) — never allowed to escape as the callee's exit 2. Exit 2 is reserved for the
# INSTRUMENT failing (doc_lint unrunnable, unparseable JSON, missing schema dir), which is a
# different claim from "the check is not there".
#
# The fixture is built inline in $(mktemp -d) and leaves no residue.
# Exit: 0 the check discriminates correctly · 1 a real negative · 2 the instrument failed
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
CHECK_ID="verification-clause"

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
FIX="$tmp/plan.md"
cat > "$FIX" <<'FIXEOF'
---
type: Plan
okf_spec: OKF-PLAN
id: plan-998-fixture-grammar
author: fixture
created: '2026-01-01'
status: drafting
---
# Plan: pinned grammar fixture

**ID:** plan-998-fixture-grammar
**Author:** fixture
**Created:** 2026-01-01
**Status:** drafting

## Objective
Three criteria: one PROSE, one CLAUSE-FORM, one CLAUSE WITH A GFM-ESCAPED PIPE.

## Motivation
A shape check that cannot tell prose from a clause is not a shape check.

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
| SC1 | the PROSE row — must be FLAGGED | reviewer confirms it looks right during review | 1.1 |
| SC2 | the CLAUSE row — must NOT be flagged | `true` → exit 0 | 1.1 |
| SC3 | the ESCAPED-PIPE row — must NOT be flagged, and must unescape | `printf 'a\nb\n' \| grep -c a` → exit 0 | 1.1 |
| SC4 | the MANUAL row — a first-class disposition, must NOT be flagged | manual: whether the prose reads well is a reader judgement | 1.1 |
FIXEOF

RAW="$(uv run "$REPO/_shared/doc_lint.py" --type plan --path "$FIX" --json 2>/dev/null || true)"
[ -n "$RAW" ] || { echo "INCONCLUSIVE: doc_lint produced no output" >&2; exit 2; }

python3 - "$CHECK_ID" <<PYEOF
import json, sys
check_id = sys.argv[1]
raw = r'''$RAW'''
try:
    d = json.loads(raw)
except Exception as e:
    print(f"INCONCLUSIVE: doc_lint output is not JSON: {e}", file=sys.stderr)
    raise SystemExit(2)

verdict = d.get("verdict")
if verdict == "INCONCLUSIVE" and "no schema" in (d.get("reason") or ""):
    print(f"INCONCLUSIVE: doc_lint has no schema for type 'plan': {d.get('reason')}",
          file=sys.stderr)
    raise SystemExit(2)
if d.get("files_checked", 0) < 1:
    print("INCONCLUSIVE: doc_lint checked 0 files — the fixture was not selected",
          file=sys.stderr)
    raise SystemExit(2)

findings = d.get("findings") or []
mine = [f for f in findings if f.get("check") == check_id or f.get("id") == check_id]

# THE UNCOMMISSIONED-INTERFACE RULE: an absent check is a REAL NEGATIVE (exit 1), never the
# callee's exit 2. It is a statement about the CHECK, not about the instrument.
if not mine:
    ids = sorted({f.get("check") or f.get("id") for f in findings})
    print(f"FAIL: no '{check_id}' finding — the Verification shape check does not fire.",
          file=sys.stderr)
    print(f"      doc_lint ran fine and reported checks: {ids or '(none)'}", file=sys.stderr)
    raise SystemExit(1)

def rows_flagged():
    out = set()
    for f in mine:
        for key in ("row", "row_id", "id", "cell", "detail", "message"):
            v = str(f.get(key) or "")
            for sc in ("SC1", "SC2", "SC3", "SC4"):
                if sc in v:
                    out.add(sc)
    return out

flagged = rows_flagged()
problems = []
if "SC1" not in flagged:
    problems.append("the PROSE row SC1 was NOT flagged")
for sc, why in (("SC2", "clause-form"), ("SC3", "clause with an escaped pipe"),
                ("SC4", "manual: disposition")):
    if sc in flagged:
        problems.append(f"the {why} row {sc} WAS flagged")

if problems:
    print(f"FAIL: the shape check does not discriminate correctly:", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    raise SystemExit(1)

print("PASS: prose flagged; clause, escaped-pipe clause and manual: all accepted")
PYEOF
