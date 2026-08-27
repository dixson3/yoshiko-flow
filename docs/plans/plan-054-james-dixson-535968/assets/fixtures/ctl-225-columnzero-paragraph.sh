#!/usr/bin/env bash
# ctl-225-columnzero-paragraph — grades #225 / plan-054 Issue 3.2.
#
# ASSERTED BEHAVIOUR (post-fix): a COLUMN-0 PARAGRAPH inside `## Epics`, under an open issue,
# is REPORTED IN `unparsed[]` rather than dropped silently.
#
# THE DEFECT (measured by plan-053 EXP-001, re-verified on the merged tree AFTER both #206
# fixes landed — so it is a surviving shape, not one those fixes were expected to reach):
# the paragraph vanishes, `unparsed` stays `[]`, and `--strict` exits 0. Content disappears
# while the extractor reports it read the document completely.
#
# WHAT THE FIX MUST **NOT** DO, and why this fixture checks for it. Collecting the paragraph
# into the issue's `detail` would be WRONG: a column-0 line is not a continuation under
# CommonMark, so attributing it to the issue is precisely the corruption plan-053's column-0
# fence guard exists to prevent. So the fixture asserts BOTH that the construct is reported
# AND that it was not swallowed into `detail`. A one-sided check would pass on the wrong fix.
#
# EXIT  0 reported in unparsed[] and not swallowed  ·  1 dropped silently (the defect)  ·  2 could not run
set -uo pipefail

[ -n "${YF_TREE:-}" ] || { echo "ctl-225: INCONCLUSIVE — YF_TREE is not set" >&2; exit 2; }
EXTRACT="${YF_TREE}/skills/yf-plan/scripts/plan_extract.py"
[ -f "${EXTRACT}" ] || { echo "ctl-225: INCONCLUSIVE — no plan_extract.py at ${EXTRACT}" >&2; exit 2; }
command -v uv >/dev/null 2>&1 || { echo "ctl-225: INCONCLUSIVE — uv not on PATH" >&2; exit 2; }

TMP="$(mktemp -d)" || { echo "ctl-225: INCONCLUSIVE — mktemp failed" >&2; exit 2; }
trap 'rm -rf "${TMP}"' EXIT

PD="${TMP}/plan-999-fixture-ctl225"
mkdir -p "${PD}"
cat > "${PD}/plan.md" <<'EOF'
---
type: Plan
okf_spec: OKF-PLAN
id: plan-999-fixture-ctl225
author: fixture
created: 2026-08-26
status: drafting
---
# Plan: ctl-225 fixture

**ID:** plan-999-fixture-ctl225
**Author:** fixture
**Created:** 2026-08-26
**Status:** drafting

## Objective
Fixture.

## Motivation
Fixture.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| — | | | | |

## Investigation Findings
Fixture.

## Approach
Fixture.

## Epics
### Epic 1: fixture
- Issue 1.1: first issue
- Issue 1.2: second issue
THIS COLUMN ZERO PARAGRAPH MUST NOT VANISH SILENTLY.

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

out="$(uv run "${EXTRACT}" "${PD}" --json 2>/dev/null)" || true
[ -n "${out}" ] || { echo "ctl-225: INCONCLUSIVE — plan_extract produced no output" >&2; exit 2; }

verdict="$(printf '%s' "${out}" | python3 -c '
import json,sys
MARK = "THIS COLUMN ZERO PARAGRAPH MUST NOT VANISH SILENTLY."
try:
    d = json.load(sys.stdin)
except Exception as e:                      # noqa: BLE001
    print("INCONCLUSIVE:%s" % e); raise SystemExit(0)
if isinstance(d, list):
    if not d: print("INCONCLUSIVE:empty array"); raise SystemExit(0)
    d = d[0]
unparsed = json.dumps(d.get("unparsed", []))
swallowed = any(MARK in (i.get("detail") or "") for i in d.get("issues", []))
reported  = MARK in unparsed or bool(d.get("unparsed"))
if swallowed: print("SWALLOWED")
elif reported: print("REPORTED")
else: print("DROPPED")
' 2>/dev/null)"

case "${verdict}" in
  REPORTED)      echo "ctl-225: column-0 paragraph reported in unparsed[]"; exit 0 ;;
  SWALLOWED)     echo "ctl-225: FAIL — the paragraph was collected into an issue's \`detail\`." >&2
                 echo "ctl-225: a column-0 line is not a continuation under CommonMark; attributing" >&2
                 echo "ctl-225: plan body to an issue is the corruption the fence guard prevents." >&2
                 exit 1 ;;
  DROPPED)       echo "ctl-225: FAIL — the column-0 paragraph vanished and unparsed[] is empty." >&2
                 echo "ctl-225: content disappeared while the extractor reported a complete read." >&2
                 exit 1 ;;
  INCONCLUSIVE*) echo "ctl-225: ${verdict}" >&2; exit 2 ;;
  *)             echo "ctl-225: INCONCLUSIVE — unrecognised probe output: ${verdict}" >&2; exit 2 ;;
esac
