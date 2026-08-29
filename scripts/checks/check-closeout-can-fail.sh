#!/usr/bin/env bash
# SC9 / REQ-DATA-074 (#246) — `doc_lint` CAN STILL FAIL A COMPLETED BUNDLE.
#
# A RED fixture carrying a close-out violation at `status: complete` must produce at least
# one ERROR, and the same fixture WITHOUT the violation must not. Two branches, so a broken
# or absent linter cannot satisfy the criterion.
#
# WHY THIS IS THE PLAN'S LOAD-BEARING CHECK. Measured 2026-08-28: with the terminal-status
# demotion disabled the corpus yields 197 `E` findings; with it enabled, `errors: 0` across
# 1116 files. **46 of 48 checks are structurally incapable of a non-zero exit at
# `complete`.** The two that escape are `R1-closeout` and `R2a-closeout`, and they escape
# through exactly one mechanism: `plan-relations.toml`'s file-level `promote = false`, which
# stops `STATUS_SEVERITY` demoting `E -> R` at the statuses those checks are scoped to.
#
# #246 reported REQ-DATA-044's "the R* family is uniformly W" as a conformance defect. D-15
# resolved it TOWARD THE SCHEMA — keep the two `E` checks, amend the prose — because deleting
# them to satisfy the old wording would make `doc_lint` structurally unable to fail a completed
# bundle at all. This check is what makes that decision observable rather than asserted.
#
# THE FIXTURE IS BUILT HERE, NOT COMMITTED. `tests/fixtures/doclint/plan-relations/` carries a
# `status: review` bundle; this criterion is specifically about `complete`, where the demotion
# applies. Building it in a temp dir keeps the two fixtures from being confused for each other.
#
# EXIT  0 the violation errors at `complete` AND the clean control does not
#       1 either branch is wrong  ·  2 could not run
CHECK_NAME=check-closeout-can-fail
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ck_need uv
LINT="${TREE}/_shared/doc_lint.py"
[ -f "${LINT}" ] || ck_inconclusive "no _shared/doc_lint.py at ${LINT}"
CK_RC=0

FIX="$(mktemp -d)"
trap 'rm -rf "${FIX}"' EXIT
B="${FIX}/plan-900-fixture-cccccc"
mkdir -p "${B}"
printf '# Log\n\n## 2026-08-28\n\n- scoping: fixture\n' > "${B}/log.md"

# $1 = the `Resolved By` cell for the upstream row. A row naming an issue that does not exist
# is an R2a violation; naming a real one is the clean control.
write_plan() {
  cat > "${B}/plan.md" <<EOF
---
type: Plan
okf_spec: OKF-PLAN
id: plan-900-fixture-cccccc
author: t
created: '2026-08-28'
status: complete
---
# Plan: closeout fixture

**ID:** plan-900-fixture-cccccc
**Status:** complete

## Objective
fixture

## Motivation
fixture

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| #1 | t | include | n | $1 |

## Investigation Findings
none

## Approach
none

## Epics
### Epic 1: e
- Issue 1.1: a thing

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | r | low | m |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | c | \`true\` → exit 0 | 1.1 |
EOF
}

errors_for() {   # -> the linter's `errors` count for the current fixture
  (cd "${TREE}" && uv run "${LINT}" --type plan-relations --path "${B}/plan.md" --json 2>/dev/null) \
    | uv run python3 -c 'import json,sys; print(json.load(sys.stdin).get("errors", -1))'
}

# --- BRANCH 1 (RED): an R2a close-out violation at `status: complete` ---------------
# `Resolved By: 9.9` names an issue this plan does not contain.
write_plan "9.9"
RED="$(errors_for)"
[ "${RED}" != "-1" ] || ck_inconclusive "the linter emitted no parseable \`errors\` count"
if [ "${RED}" -lt 1 ]; then
  ck_fail "a close-out violation at \`status: complete\` produced ${RED} error(s) — \`doc_lint\` is structurally incapable of failing a completed bundle (#246 / REQ-DATA-074)"
fi

# --- BRANCH 2 (the control): the same bundle WITHOUT the violation ------------------
# Without this arm, branch 1 passes on a linter that errors unconditionally — which is a
# different broken instrument, not a working one.
write_plan "1.1"
GREEN="$(errors_for)"
if [ "${GREEN}" -ne 0 ]; then
  ck_fail "the CLEAN control also produced ${GREEN} error(s) — branch 1 above is vacuous"
fi

ck_done "a close-out violation at \`status: complete\` yields ${RED} error(s); the clean control yields ${GREEN}"
