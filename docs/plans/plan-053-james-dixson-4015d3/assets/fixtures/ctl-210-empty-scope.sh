#!/usr/bin/env bash
# ctl-210-empty-scope — pour_fidelity.py's silent exit-0 on an EMPTY SCOPE (#210 / D-7).
#
# A FIXTURE per redcheck.sh's definition: exits 0 iff the asserted behaviour holds.
#
# THE DEFECT. `main()`'s `--strict` arm builds `scope` and then returns
# `1 if any(not r["clean"] for r in scope) else 0`. `any([])` is False, so **an empty scope
# returns 0** — a clean bill of health issued after examining nothing. EXP-002 measured this
# on the `no-mapping` population specifically, which is the population #210 justifies the
# gate BY: #186/#187's masked titles are exactly what destroys the title fallback, so the
# plans the gate most needs to judge are the ones it silently passes.
#
# `extractor_unparsed` already receives the correct treatment two lines above — INCONCLUSIVE
# (2), because a plan the extractor could not fully read cannot be judged either way. The
# three paths below are the same claim and must get the same verdict.
#
# THE THREE MEASURED PATHS (D-7 / Issue 3.1):
#   A. the `no-mapping` population — beads carry no recoverable issue id, so `joinable` is
#      false, so the plan is filtered OUT of `scope` and the scope goes empty.
#   B. a `--plan` value matching nothing — a typo, a renamed bundle, or a plan whose beads
#      were never poured. Scope empty.
#   C. a plan dir with no `**Epic:**` field — `run()` puts it in `skipped[]`, never in
#      `results`, so `scope` is empty.
#
# All three must return **2 (INCONCLUSIVE)**, not 0. Two is the honest verdict: the
# instrument had nothing to measure. Nothing here asks for a 1 — a FAIL would be just as
# false as the PASS, because no divergence was observed either.
#
# WHY SHIPPING FIRST WOULD HAVE BEEN WRONG (D-7). #210 asks to ship this script to the skill
# dir. Shipping it with this hole generalises a silent pass to every adopting repo, so the
# hole closes BEFORE the ship, not after.
#
# Tree under test: $YF_TREE (set by redcheck.sh).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
PF="${YF_TREE}/_shared/pour_fidelity.py"

[ -f "${PF}" ] || { echo "ctl-210-empty-scope: HARNESS — no pour_fidelity at ${PF}" >&2; exit 2; }

work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT

# ---- A plan bundle whose beads are UNJOINABLE ------------------------------------------
# The epic resolves and has children, but no child carries `metadata.plan_issue` and no title
# begins with an issue id — so both join routes fail and `joinable` is false. That is the
# `no-mapping` population, verbatim.
mkdir -p "${work}/plans/plan-nomap-fixture-aaaaaa"
cat > "${work}/plans/plan-nomap-fixture-aaaaaa/plan.md" <<'PLAN'
---
type: Plan
okf_spec: OKF-PLAN
id: plan-nomap-fixture-aaaaaa
author: fixture
created: 2026-08-25
status: executing
---
# Plan: no-mapping fixture

**ID:** plan-nomap-fixture-aaaaaa
**Epic:** fx-epic-1

## Objective
Drive the empty-scope exit-0.

## Motivation
The `no-mapping` population is the one #210 justifies the gate by.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Investigation Findings
None.

## Approach
None.

## Epics
### Epic 1: Work
- Issue 1.1: The first issue
- Issue 1.2: The second issue
  - depends-on: 1.1

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
| SC1 | none | `true` → exit 0 | 1.1 |
PLAN

# ---- The SAME bundle with the `**Epic:**` field removed (path C) ------------------------
mkdir -p "${work}/plans/plan-noepic-fixture-bbbbbb"
grep -v '^\*\*Epic:\*\*' "${work}/plans/plan-nomap-fixture-aaaaaa/plan.md" \
  | sed 's/plan-nomap-fixture-aaaaaa/plan-noepic-fixture-bbbbbb/' \
  > "${work}/plans/plan-noepic-fixture-bbbbbb/plan.md"

# ---- Beads: an epic with two children carrying NO recoverable issue id ------------------
cat > "${work}/beads.json" <<'BEADS'
[
 {"id": "fx-epic-1", "title": "plan-execute", "issue_type": "epic", "status": "open",
  "metadata": {"plan_dir": "plans/plan-nomap-fixture-aaaaaa"}},
 {"id": "fx-epic-1.1", "title": "Do the first thing", "issue_type": "task", "status": "closed",
  "metadata": {}, "dependencies": [{"depends_on_id": "fx-epic-1", "type": "parent-child"}]},
 {"id": "fx-epic-1.2", "title": "Do the second thing", "issue_type": "task", "status": "closed",
  "metadata": {}, "dependencies": [{"depends_on_id": "fx-epic-1", "type": "parent-child"}]}
]
BEADS

run_pf() {  # run_pf <label> <extra-args...> -> echoes the exit code
  (cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${PF}" "$@" >/dev/null 2>&1)
  echo "$?"
}

bad=()

# ---- A. the no-mapping population -------------------------------------------------------
rc_a="$(run_pf "${work}/beads.json" "${work}/plans/plan-nomap-fixture-aaaaaa" \
          --strict --plan plan-nomap-fixture-aaaaaa)"
if [ "${rc_a}" != "2" ]; then
  bad+=("path A (no-mapping population): --strict returned ${rc_a}, expected 2 (INCONCLUSIVE). \
An unjoinable plan is filtered OUT of scope, so \`any([])\` reports a clean bill of health \
after examining nothing — and this is the population #210 justifies the gate BY.")
fi

# ---- B. a --plan value matching nothing --------------------------------------------------
rc_b="$(run_pf "${work}/beads.json" "${work}/plans/plan-nomap-fixture-aaaaaa" \
          --strict --plan plan-does-not-exist-zzzzzz)"
if [ "${rc_b}" != "2" ]; then
  bad+=("path B (--plan matches nothing): --strict returned ${rc_b}, expected 2 \
(INCONCLUSIVE). A typo, a renamed bundle or a never-poured plan all silently certify.")
fi

# ---- C. a plan dir with no **Epic:** field -----------------------------------------------
rc_c="$(run_pf "${work}/beads.json" "${work}/plans/plan-noepic-fixture-bbbbbb" \
          --strict --plan plan-noepic-fixture-bbbbbb)"
if [ "${rc_c}" != "2" ]; then
  bad+=("path C (no **Epic:** field): --strict returned ${rc_c}, expected 2 (INCONCLUSIVE). \
\`run()\` puts such a bundle in \`skipped[]\` and never in \`results\`, so scope is empty.")
fi

# ---- NEGATIVE CONTROL: a genuinely clean, JOINABLE plan must still return 0 --------------
# Without this, "return 2 whenever --strict is passed" would satisfy every assertion above.
# The fix must narrow to the EMPTY case, not blanket the verb.
mkdir -p "${work}/plans/plan-joinable-fixture-cccccc"
sed 's/plan-nomap-fixture-aaaaaa/plan-joinable-fixture-cccccc/' \
  "${work}/plans/plan-nomap-fixture-aaaaaa/plan.md" \
  > "${work}/plans/plan-joinable-fixture-cccccc/plan.md"
cat > "${work}/beads-ok.json" <<'BEADS2'
[
 {"id": "fx-epic-2", "title": "plan-execute", "issue_type": "epic", "status": "open",
  "metadata": {"plan_dir": "plans/plan-joinable-fixture-cccccc"}},
 {"id": "fx-epic-2.1", "title": "Do the first thing", "issue_type": "task", "status": "closed",
  "metadata": {"plan_issue": "1.1"},
  "dependencies": [{"depends_on_id": "fx-epic-2", "type": "parent-child"}]},
 {"id": "fx-epic-2.2", "title": "Do the second thing", "issue_type": "task", "status": "closed",
  "metadata": {"plan_issue": "1.2"},
  "dependencies": [{"depends_on_id": "fx-epic-2", "type": "parent-child"},
                   {"depends_on_id": "fx-epic-2.1", "type": "blocks"}]}
]
BEADS2
sed -i.bak 's/^\*\*Epic:\*\* fx-epic-1$/**Epic:** fx-epic-2/' \
  "${work}/plans/plan-joinable-fixture-cccccc/plan.md"
rc_n="$(run_pf "${work}/beads-ok.json" "${work}/plans/plan-joinable-fixture-cccccc" \
          --strict --plan plan-joinable-fixture-cccccc)"
if [ "${rc_n}" != "0" ]; then
  bad+=("NEGATIVE CONTROL: a clean, JOINABLE, in-scope plan returned ${rc_n}, expected 0. \
The fix must narrow to the EMPTY-scope case; blanketing --strict with a 2 would satisfy \
every assertion above while breaking the verb.")
fi

if [ "${#bad[@]}" -gt 0 ]; then
  echo "ctl-210-empty-scope: ${#bad[@]} failure(s):" >&2
  for b in "${bad[@]}"; do echo "ctl-210-empty-scope:   ${b}" >&2; done
  exit 1
fi
echo "ctl-210-empty-scope: all three empty-scope paths return 2, and a clean joinable plan still returns 0"
