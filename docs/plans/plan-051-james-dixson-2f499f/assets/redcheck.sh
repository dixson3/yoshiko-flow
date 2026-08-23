#!/usr/bin/env bash
# redcheck.sh — plan-051 Issue 0.2. The driven-red harness (D-4), copied byte-for-byte from plan-050 Issue 0.2.
#
# THE CONTRACT IT ENFORCES
# ------------------------
# A control is trusted GREEN only after it has been OBSERVED RED. A fixture that has never
# been seen failing is not evidence — plan-047 shipped six controls that reported clean while
# checking nothing, and plan-049's EXP-002 measured its own safety postcondition PASSING the
# replay it was written to catch.
#
# WHAT A "FIXTURE" IS (the whole harness depends on this definition)
# -----------------------------------------------------------------
# A fixture is a SCRIPT THAT EXITS 0 IFF THE CONTROL'S ASSERTED BEHAVIOUR HOLDS. So a
# control's fixture is non-zero BEFORE its fix and zero AFTER — that is what makes a
# RED->GREEN pair meaningful, and `controls.txt` lists ONLY red->green controls.
#
# A scenario whose assertion is INVARIANT across the fix is a NEGATIVE CONTROL, not a redcheck
# control. It never appears in `controls.txt` and this harness never asks it for a GREEN
# record. (`neg-179-open-wrapper` is the one in this plan: an open wrapper must drive
# `close_cascade.py` non-zero both before AND after Issue 1.2, so a *fixture* for it would
# exit 0 on both sides while SC4 wants the observed cascade exit itself.)
#
# WHY TWO OBSERVING VERBS AND NOT ONE
# -----------------------------------
# The two observations are made at DIFFERENT POINTS IN THE DAG. `record-red` runs against the
# UNFIXED tree, from the fixture-authoring issue; `assert-distinguishes` runs against the
# FIXED tree, from the issue that lands the fix. A single verb would demand a zero-on-GREEN
# exit from a tree where the fix does not yet exist.
#
# The "before the fix" ORDERING IS CARRIED BY THE `depends-on` EDGES (1.1->1.2/1.3,
# 2.1->2.2, 3.1->3.2, 7.1->7.2/7.3), not by anything in the records. Pass-7 C69 measured a
# HEAD-hash ordering check as VACUOUS: nothing requires the fix to be committed before
# `assert-distinguishes` runs, so both records carry the identical hash and "descends from" is
# trivially true. The `git describe --always --dirty` field is recorded FOR DIAGNOSIS ONLY.
# The claim this harness makes is the EXIT-CODE DISTINCTION and nothing more.
#
# USAGE
#   bash redcheck.sh record-red          <fixture> <control>
#   bash redcheck.sh assert-distinguishes <fixture> <control>
#   bash redcheck.sh verify-all
#
# EXIT (every verb)
#   0  the verb's assertion holds
#   1  it does not
#   2  the HARNESS could not run (unknown verb, missing fixture, unreadable manifest)
#
# THE TREE UNDER TEST
#   Fixtures receive `YF_TREE` — an absolute path to the checkout they assert against. It
#   defaults to this plan's execution worktree, which is where the fixes land. Override it to
#   point a fixture at a different tree.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLAN_DIR="$(cd "${HERE}/.." && pwd)"
PLAN_MD="${PLAN_DIR}/plan.md"
MANIFEST="${HERE}/controls.txt"
RECORDS="${HERE}/red-prework.md"
REPO_ROOT="$(cd "${PLAN_DIR}/../../.." && pwd)"
PLAN_ID="$(basename "${PLAN_DIR}")"

# The tree a fixture asserts against. Default: this plan's execution worktree.
: "${YF_TREE:=${REPO_ROOT}/.worktrees/${PLAN_ID}}"
export YF_TREE

harness_fail() { echo "redcheck: HARNESS FAILURE — $*" >&2; exit 2; }

_ensure_records() {
  [ -f "${RECORDS}" ] && return 0
  cat > "${RECORDS}" <<'HDR'
---
type: Reference
okf_spec: OKF-PLAN
id: red-prework
description: Append-only red->green observation log written by assets/redcheck.sh (Issue 0.2)
---

# Red-prework record

Append-only observation log written by `assets/redcheck.sh` (Issue 0.2). One line per
observation. The gate `verify-all` reads THIS FILE and `assets/controls.txt`; nothing else.

Record schema, comma-separated, in this order:

    verb, control, fixture, exit-code, command, utc, git-describe

`git-describe` is recorded FOR DIAGNOSIS ONLY. It makes no ordering claim: pass-7 C69
measured that check vacuous, because nothing requires the fix to be committed before
`assert-distinguishes` runs. The ordering "RED was observed before the fix landed" is carried
by the plan's `depends-on` edges, not by this file.

## Observations

HDR
}

# _run_fixture <fixture> -> sets the GLOBAL `FIXTURE_RC`. Returns 0, or 2 on harness failure.
#
# WHY A GLOBAL AND NOT A COMMAND SUBSTITUTION. The obvious form —
# `rc="$(_run_fixture "$fx")"` with `harness_fail` inside — is BROKEN, and the harness's own
# self-spike caught it: `harness_fail`'s `exit 2` runs inside the substitution SUBSHELL, so it
# kills only that subshell. The caller then continues with an EMPTY `rc`, `[ "" -eq 0 ]` errors
# out non-zero, and the verb reports "RED observed" and exits **0** for a fixture that does not
# exist. A harness that reports success while running nothing is this plan's own thesis defect,
# reproduced inside the instrument built to detect it.
_run_fixture() {
  local fx="$1"
  FIXTURE_RC=""
  if [ ! -f "${fx}" ]; then
    echo "redcheck: HARNESS FAILURE — fixture does not exist: ${fx}" >&2
    return 2
  fi
  bash "${fx}" >&2
  FIXTURE_RC="$?"
  return 0
}

_append() {
  # _append <verb> <control> <fixture> <rc> <cmd>
  local verb="$1" control="$2" fixture="$3" rc="$4" cmd="$5"
  local utc gd
  utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  gd="$(git -C "${YF_TREE}" describe --always --dirty 2>/dev/null || echo 'no-git')"
  _ensure_records
  printf '%s, %s, %s, %s, `%s`, %s, %s\n' \
    "${verb}" "${control}" "${fixture#${PLAN_DIR}/}" "${rc}" "${cmd}" "${utc}" "${gd}" \
    >> "${RECORDS}"
}

_in_manifest() {
  grep -qxF "$1" "${MANIFEST}" 2>/dev/null
}

cmd_record_red() {
  local fixture="$1" control="$2"
  [ -f "${MANIFEST}" ] || harness_fail "manifest missing: ${MANIFEST}"
  _in_manifest "${control}" || harness_fail \
    "control '${control}' is not in ${MANIFEST} — a control the gate cannot see"
  _run_fixture "${fixture}" || return 2
  local rc="${FIXTURE_RC}"
  _append "record-red" "${control}" "${fixture}" "${rc}" \
    "YF_TREE=${YF_TREE} bash ${fixture#${PLAN_DIR}/}"
  if [ "${rc}" -eq 0 ]; then
    echo "redcheck: FAIL — ${control}'s fixture exited 0 against the UNFIXED tree." >&2
    echo "redcheck: a fixture that has never been observed failing is not evidence (D-4)." >&2
    return 1
  fi
  echo "redcheck: RED observed — ${control} exited ${rc} against ${YF_TREE}"
  return 0
}

cmd_assert_distinguishes() {
  local fixture="$1" control="$2"
  [ -f "${MANIFEST}" ] || harness_fail "manifest missing: ${MANIFEST}"
  _in_manifest "${control}" || harness_fail \
    "control '${control}' is not in ${MANIFEST} — a control the gate cannot see"
  _run_fixture "${fixture}" || return 2
  local rc="${FIXTURE_RC}"
  _append "assert-distinguishes" "${control}" "${fixture}" "${rc}" \
    "YF_TREE=${YF_TREE} bash ${fixture#${PLAN_DIR}/}"
  local ok=0
  if [ "${rc}" -ne 0 ]; then
    echo "redcheck: FAIL — ${control}'s fixture exited ${rc} against the FIXED tree; expected 0." >&2
    ok=1
  fi
  # BOTH observations must be on record — this verb never certifies a control it has only
  # ever seen green.
  if ! _has_record "record-red" "${control}" nonzero; then
    echo "redcheck: FAIL — no RED record for ${control}. Run \`record-red\` against the" >&2
    echo "redcheck: UNFIXED tree first; a green that was never preceded by a red is not a" >&2
    echo "redcheck: distinction." >&2
    ok=1
  fi
  [ "${ok}" -eq 0 ] && echo "redcheck: DISTINGUISHED — ${control} red->green on record"
  return "${ok}"
}

# _has_record <verb> <control> <nonzero|zero>
_has_record() {
  local verb="$1" control="$2" want="$3"
  [ -f "${RECORDS}" ] || return 1
  awk -v verb="${verb}" -v ctl="${control}" -v want="${want}" -F', *' '
    $1 == verb && $2 == ctl {
      rc = $4 + 0
      if (want == "zero"    && rc == 0) { found = 1 }
      if (want == "nonzero" && rc != 0) { found = 1 }
    }
    END { exit(found ? 0 : 1) }
  ' "${RECORDS}"
}

cmd_verify_all() {
  [ -f "${MANIFEST}" ] || harness_fail "manifest missing: ${MANIFEST}"
  [ -f "${PLAN_MD}" ]  || harness_fail "plan.md missing: ${PLAN_MD}"

  # ---- manifest completeness, DERIVED from plan.md ---------------------------------
  # The count is derived rather than a hard-coded literal: a literal inside verify-all
  # would be a THIRD enumerating copy of the control set, which is the exact artifact
  # class pass-10 C93 was filed about (the gate passed with all of Epic 7 unobserved).
  #
  # The pattern is ANCHORED as `ctl-[0-9]{3}-[a-z-]+` and the anchoring is load-bearing:
  # a loose `ctl-[a-z0-9-]*` returns 7, because the SPECIFYING SENTENCE in plan.md
  # contains the pattern text and `grep -o` extracts the bare `ctl-` prefix from it. The
  # derivation would then compare 6 manifest lines against 7 and exit 1 forever, sending
  # the executor to hunt a record that does not exist (pass-12 C123).
  #
  # The path is resolved from THIS SCRIPT'S OWN LOCATION, never the caller's cwd: this
  # file lives in `assets/`, one directory down, so a bare relative `plan.md` yields 0
  # from either the repo root or `assets/` (pass-13 C128).
  # plan-051 Issue 0.2 TIGHTENING. The inherited generic pattern `ctl-[0-9]{3}-[a-z-]+` is
  # contaminated by any prose in plan.md naming ANOTHER plan's control ids — EXP-004 measured
  # that wedging the gate at 7-declared-vs-1-manifest. The pattern below is pinned to this
  # plan's own three issue numbers, stated verbatim in Issue 0.2 so an executor copies what the
  # issue prints. OPPOSITE FAILURE MODE, stated rather than discovered: a control for an issue
  # number outside {165, 182, 184} is INVISIBLE to this derivation, so adding one requires
  # widening the alternation here (pass-1 C16).
  local declared manifest_n
  declared="$(grep -oE 'ctl-(165|182|184)-[a-z-]+' "${PLAN_MD}" | sort -u | wc -l | tr -d ' ')"
  manifest_n="$(grep -cvE '^[[:space:]]*(#|$)' "${MANIFEST}" | tr -d ' ')"
  if [ "${declared}" != "${manifest_n}" ]; then
    echo "redcheck: FAIL — ${MANIFEST} lists ${manifest_n} control(s) but plan.md declares ${declared}." >&2
    echo "redcheck: a control missing from the manifest is a control this gate CANNOT SEE." >&2
    return 1
  fi

  local rc=0 n=0
  while IFS= read -r control; do
    case "${control}" in ''|'#'*) continue ;; esac
    n=$((n + 1))
    if ! _has_record "record-red" "${control}" nonzero; then
      echo "redcheck: FAIL — ${control}: no \`record-red\` observation with a NON-ZERO exit." >&2
      rc=1
    fi
    if ! _has_record "assert-distinguishes" "${control}" zero; then
      echo "redcheck: FAIL — ${control}: no \`assert-distinguishes\` observation with a ZERO exit." >&2
      rc=1
    fi
  done < "${MANIFEST}"

  if [ "${n}" -eq 0 ]; then
    harness_fail "manifest is empty — verify-all would certify vacuously"
  fi
  if [ "${rc}" -eq 0 ]; then
    echo "redcheck: all ${n} control(s) distinguished RED from GREEN"
  fi
  return "${rc}"
}

verb="${1-}"
case "${verb}" in
  record-red)
    [ "$#" -eq 3 ] || harness_fail "usage: redcheck.sh record-red <fixture> <control>"
    cmd_record_red "$2" "$3" ;;
  assert-distinguishes)
    [ "$#" -eq 3 ] || harness_fail "usage: redcheck.sh assert-distinguishes <fixture> <control>"
    cmd_assert_distinguishes "$2" "$3" ;;
  verify-all)
    [ "$#" -eq 1 ] || harness_fail "usage: redcheck.sh verify-all"
    cmd_verify_all ;;
  '')
    harness_fail "no verb given. Expected one of: record-red | assert-distinguishes | verify-all" ;;
  *)
    harness_fail "unknown verb: '${verb}'. Expected one of: record-red | assert-distinguishes | verify-all" ;;
esac
