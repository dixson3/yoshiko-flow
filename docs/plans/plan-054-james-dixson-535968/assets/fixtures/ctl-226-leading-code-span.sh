#!/usr/bin/env bash
# ctl-226-leading-code-span — grades #226 / plan-054 Issue 3.3.
#
# ASSERTED BEHAVIOUR (post-fix): a REAL trailing declaration sitting behind a LEADING inline
# code span still yields its edge:
#
#     - Issue 1.2: second
#       `foo.py` depends-on: 1.1        ->  edge 1.2 -> 1.1
#
# MECHANISM OF THE DEFECT: the two-space continuation branch tests the MASKED line. The
# leading mask replaces the code span with spaces, pushing the first non-space character past
# column 2, so `^ {2}(?![ \t*-])\S` no longer matches and the line never reaches
# `try_trailing`. Measured unchanged on both the base and the plan-053 fixed tree.
#
# THE NEGATIVE HALF IS THE LOAD-BEARING ONE. This fix touches a PARSING branch, which is
# exactly the class of change that can start manufacturing phantom edges — and `REQ-DATA-063`
# deliberately has the parsing branches read the masked line so that a `depends-on:` written
# INSIDE a code span produces no edge. A fix that simply read the unmasked line everywhere
# would satisfy the positive half while destroying that requirement. So this fixture asserts:
#   (a) POSITIVE — a real declaration behind a leading code span yields its edge;
#   (b) NEGATIVE — a declaration written wholly inside a code span still yields NO edge.
# Only a fix that keeps the two apart satisfies both.
#
# EXIT  0 both halves hold  ·  1 they do not  ·  2 could not run
set -uo pipefail

# YF_TREE SELF-RESOLUTION (added at close). A fixture is invoked TWO ways: by `redcheck.sh`,
# which exports YF_TREE, and DIRECTLY by its Success Criterion's Verification command, which does
# not. Exiting 2 on an unset YF_TREE made every criterion that invokes a fixture directly
# UNSATISFIABLE — SC7, SC7b, SC8, SC23 and SC24 could never pass, in either direction. That is a
# criterion that cannot be met, which is worse than one that cannot fail: it halts the close
# chain over nothing.
#
# So resolve it the way redcheck.sh does: the plan's execution worktree while its branch is still
# UNMERGED, else the repo root. A genuinely unresolvable tree is still INCONCLUSIVE.
if [ -z "${YF_TREE:-}" ]; then
  _fx_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  _fx_plan="$(cd "${_fx_here}/../.." && pwd)"
  _fx_root="$(git -C "${_fx_plan}" rev-parse --show-toplevel 2>/dev/null)" || _fx_root=""
  _fx_id="$(basename "${_fx_plan}")"
  if [ -n "${_fx_root}" ] && [ -d "${_fx_root}/.worktrees/${_fx_id}" ] \
     && ! git -C "${_fx_root}" merge-base --is-ancestor "${_fx_id}-execute" main 2>/dev/null; then
    YF_TREE="${_fx_root}/.worktrees/${_fx_id}"
  else
    YF_TREE="${_fx_root}"
  fi
  export YF_TREE
  unset _fx_here _fx_plan _fx_root _fx_id
fi
[ -n "${YF_TREE:-}" ] || { echo "ctl-226: INCONCLUSIVE — YF_TREE is not set" >&2; exit 2; }
EXTRACT="${YF_TREE}/skills/yf-plan/scripts/plan_extract.py"
[ -f "${EXTRACT}" ] || { echo "ctl-226: INCONCLUSIVE — no plan_extract.py at ${EXTRACT}" >&2; exit 2; }
command -v uv >/dev/null 2>&1 || { echo "ctl-226: INCONCLUSIVE — uv not on PATH" >&2; exit 2; }

TMP="$(mktemp -d)" || { echo "ctl-226: INCONCLUSIVE — mktemp failed" >&2; exit 2; }
trap 'rm -rf "${TMP}"' EXIT

PD="${TMP}/plan-999-fixture-ctl226"
mkdir -p "${PD}"
cat > "${PD}/plan.md" <<'EOF'
---
type: Plan
okf_spec: OKF-PLAN
id: plan-999-fixture-ctl226
author: fixture
created: 2026-08-26
status: drafting
---
# Plan: ctl-226 fixture

**ID:** plan-999-fixture-ctl226
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
  `foo.py` depends-on: 1.1
- Issue 1.3: third issue
  `depends-on: 1.1` is written here wholly inside a code span and must yield NO edge.

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
[ -n "${out}" ] || { echo "ctl-226: INCONCLUSIVE — plan_extract produced no output" >&2; exit 2; }

verdict="$(printf '%s' "${out}" | python3 -c '
import json,sys
try:
    d = json.load(sys.stdin)
except Exception as e:                      # noqa: BLE001
    print("INCONCLUSIVE:%s" % e); raise SystemExit(0)
if isinstance(d, list):
    if not d: print("INCONCLUSIVE:empty array"); raise SystemExit(0)
    d = d[0]
edges = {(e.get("from"), e.get("to")) for e in d.get("edges", []) if e.get("kind") == "depends-on"}
real    = ("1.2", "1.1") in edges      # must be PRESENT post-fix
phantom = ("1.3", "1.1") in edges      # must be ABSENT always (REQ-DATA-063)
if phantom: print("PHANTOM")
elif real:  print("EDGE")
else:       print("NOEDGE")
' 2>/dev/null)"

case "${verdict}" in
  EDGE)          echo "ctl-226: trailing declaration behind a leading code span yields its edge, and the in-span declaration still yields none"; exit 0 ;;
  PHANTOM)       echo "ctl-226: FAIL — a declaration written WHOLLY INSIDE a code span produced an edge." >&2
                 echo "ctl-226: that is REQ-DATA-063 broken: the parsing branches read the masked line" >&2
                 echo "ctl-226: precisely so an in-span declaration is inert. Manufacturing phantom" >&2
                 echo "ctl-226: edges is a worse defect than the one being fixed." >&2
                 exit 1 ;;
  NOEDGE)        echo "ctl-226: FAIL — the real trailing declaration behind a leading code span yielded NO edge." >&2
                 echo "ctl-226: the leading mask pushes the first non-space char past column 2, so the" >&2
                 echo "ctl-226: continuation branch never matches and try_trailing is never reached." >&2
                 exit 1 ;;
  INCONCLUSIVE*) echo "ctl-226: ${verdict}" >&2; exit 2 ;;
  *)             echo "ctl-226: INCONCLUSIVE — unrecognised probe output: ${verdict}" >&2; exit 2 ;;
esac
