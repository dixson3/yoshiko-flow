#!/usr/bin/env bash
# ctl-185-empty-triage — grades #185 / plan-054 Issue 3.1.
#
# ASSERTED BEHAVIOUR (post-fix): `upstream-cells-filled` DISTINGUISHES a triage that ran and
# measured nothing from a triage that was never run. Today both produce the identical
# artifact — a zero-row `## Upstream Issues` table — and the check fires on both.
#
# WHY THAT MATTERS: at `review`/`ready-for-approval` the finding promotes W -> E, so
# `_audit_plan` fails and `ready-check` blocks approval. The second case is EVERY PLAN
# AUTHORED IN A FRESH REPOSITORY, so today the only exits are fabricating a row (strictly
# worse than the finding it silences) or `--force` (which also suppresses any genuine finding
# in the same run). Measured live in `dixson3/astrospike` plan-001.
#
# THE FIXTURE ASSERTS BOTH HALVES, WHICH IS THE WHOLE POINT. A fix that simply stopped firing
# on a zero-row table would pass a one-sided check while destroying the signal the check
# exists for. So this fixture requires:
#   (a) DECLARED-EMPTY  (a `no-upstream-issues:` sentinel recording the command and date)
#                       -> the check must NOT fire;
#   (b) SKIPPED         (a zero-row table and no sentinel at all)
#                       -> the check MUST still fire.
# Only a real distinction satisfies both. #185's option 2 (keying on `upstream-triage.md`
# evidence) also satisfies this fixture: neither document here has a sibling triage file, so
# (b) stays red under that remedy too.
#
# EXIT  0 the distinction holds  ·  1 it does not (the defect)  ·  2 could not run
set -uo pipefail

[ -n "${YF_TREE:-}" ] || { echo "ctl-185: INCONCLUSIVE — YF_TREE is not set" >&2; exit 2; }
LINT="${YF_TREE}/skills/yf-plan/scripts/doc_lint.py"
[ -f "${LINT}" ] || { echo "ctl-185: INCONCLUSIVE — no doc_lint.py at ${LINT}" >&2; exit 2; }
command -v uv >/dev/null 2>&1 || { echo "ctl-185: INCONCLUSIVE — uv not on PATH" >&2; exit 2; }

TMP="$(mktemp -d)" || { echo "ctl-185: INCONCLUSIVE — mktemp failed" >&2; exit 2; }
trap 'rm -rf "${TMP}"' EXIT      # self-cleaning ON BOTH EXIT PATHS (the `probe` contract)

_write_plan() {
  # _write_plan <file> <upstream-section-body>
  cat > "$1" <<EOF
---
type: Plan
okf_spec: OKF-PLAN
id: plan-999-fixture-ctl185
author: fixture
created: 2026-08-26
status: review
---
# Plan: ctl-185 fixture

**ID:** plan-999-fixture-ctl185
**Author:** fixture
**Created:** 2026-08-26
**Status:** review

## Objective
Fixture document for ctl-185.

## Motivation
Fixture document for ctl-185.

## Upstream Issues
$2

## Investigation Findings
None.

## Approach
None.

## Epics
### Epic 1: fixture
- Issue 1.1: fixture issue

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
| SC1 | fixture | fixture | 1.1 |
EOF
}

EMPTY_TABLE='| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |'

_write_plan "${TMP}/declared.md" "${EMPTY_TABLE}

no-upstream-issues: \`gh issue list\` returned \`[]\` on 2026-08-26 — triage ran and measured zero upstream issues."
_write_plan "${TMP}/skipped.md" "${EMPTY_TABLE}"

# _fires <doc> -> 0 the check fired  ·  1 it did not  ·  2 could not tell
#
# THE INCONCLUSIVE CHECK IS NOT OPTIONAL. An earlier draft tested only that the output was
# non-empty, and a doc_lint INCONCLUSIVE (`verdict: INCONCLUSIVE`, `files_checked: 0`) is
# non-empty JSON containing no finding — so it read as "the check did not fire" and the
# fixture reported a confident, WRONG reason for its red. A verdict that means "nothing was
# measured" must never be read as a measurement. The schema type is `plan`, lowercase, after
# `document_types/plan.toml`; `--type Plan` is precisely what produces that INCONCLUSIVE.
_fires() {
  local out
  out="$(uv run "${LINT}" --path "$1" --type plan --json 2>/dev/null)" || true
  [ -n "${out}" ] || return 2
  printf '%s' "${out}" | grep -q '"verdict"[[:space:]]*:[[:space:]]*"INCONCLUSIVE"' && return 2
  printf '%s' "${out}" | grep -q '"files_checked"[[:space:]]*:[[:space:]]*0' && return 2
  printf '%s' "${out}" | grep -q 'upstream-cells-filled'
}

_fires "${TMP}/declared.md"; declared=$?
_fires "${TMP}/skipped.md";  skipped=$?

if [ "${declared}" -eq 2 ] || [ "${skipped}" -eq 2 ]; then
  echo "ctl-185: INCONCLUSIVE — doc_lint produced no readable JSON for one or both documents" >&2
  exit 2
fi

rc=0
if [ "${declared}" -eq 0 ]; then
  echo "ctl-185: FAIL — the check fired on a DECLARED-EMPTY triage (sentinel present)." >&2
  echo "ctl-185: a measured absence is an assertion, not an omission; firing here is the" >&2
  echo "ctl-185: first-run blocker #185 was filed for." >&2
  rc=1
fi
if [ "${skipped}" -ne 0 ]; then
  echo "ctl-185: FAIL — the check did NOT fire on a SKIPPED triage (no sentinel, zero rows)." >&2
  echo "ctl-185: that is the case the check exists for; silencing it would trade a false" >&2
  echo "ctl-185: positive for a lost signal (#185's option 3, its own weakest)." >&2
  rc=1
fi
[ "${rc}" -eq 0 ] && echo "ctl-185: declared-empty and skipped triage are distinguished"
exit "${rc}"
