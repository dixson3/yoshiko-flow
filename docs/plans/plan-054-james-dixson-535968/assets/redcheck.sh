#!/usr/bin/env bash
# redcheck.sh — plan-050 Issue 0.2. The driven-red harness (D-4).
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
#   bash redcheck.sh record-red           <fixture> <control>   (fixtures/, ctl- controls)
#   bash redcheck.sh record-red-check     <checks/check-*.sh>    (checks/, criterion instruments)
#   bash redcheck.sh assert-distinguishes <fixture> <control>
#   bash redcheck.sh verify-manifest     (controls.txt <-> plan.md set agreement, standalone)
#   bash redcheck.sh verify-red-all      (RED half, ctl- CONTROLS — a capability-gate verb)
#   bash redcheck.sh verify-red-checks   (RED half, check- INSTRUMENTS — the other gate verb)
#   bash redcheck.sh verify-all
#
# THE TWO POPULATIONS (plan-053 pass-4 C44, adopted plan-054 Issue 0.6)
#   assets/fixtures/  ctl-<NNN>-<name>  red->green CONTROLS, listed in controls.txt, derived
#                     from plan.md by `_derive_manifest`. Recorded by `record-red`, verified
#                     by `verify-red-all`.
#   assets/checks/    check-<name>.sh   CRITERION instruments. A check-*.sh can NEVER appear
#                     in controls.txt (the derivation pattern is `ctl-`-anchored), so
#                     `verify-red-all` structurally cannot see them. Recorded by
#                     `record-red-check`, verified by `verify-red-checks`.
#
# CONTROL NAMING IS LOAD-BEARING. `_derive_manifest` greps plan.md with the ANCHORED pattern
# `ctl-[0-9]{3}-[a-z-]+`, so every control name must carry EXACTLY THREE DIGITS and no further
# digit: an embedded digit later in the name truncates the match, and a name with no number is
# invisible to the derivation entirely. Plan-local controls with no upstream issue use the
# reserved 9xx range (see controls.txt'"'"'s header).
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
CHECKS_DIR="${HERE}/checks"
CHECKS_ALLOWLIST="${HERE}/checks-allowlist.txt"
RECORDS="${HERE}/red-prework.md"
PLAN_ID="$(basename "${PLAN_DIR}")"

# REPO_ROOT IS ASKED FOR, NOT COUNTED OUT (#229, plan-054 Issue 0.6).
#
# The adopted form was `cd "${PLAN_DIR}/../../.."` — three levels up, which is correct for
# `docs/plans/<plan-id>/assets` and WRONG for `Incubator/<slug>/plans/<plan-id>/assets`, the
# other root yf-plan documents. A hardcoded level count encodes one of the two supported
# layouts and silently resolves ABOVE the repository in the other, where every later path is
# then computed from a directory that is not the checkout.
#
# `git rev-parse --show-toplevel` asks git, which knows, and is correct under BOTH roots and
# under any future one. The arithmetic form is kept only as a fallback for a non-git tree.
# NOTE THE BRACES. `A || B && C` parses as `(A || B) && C`, so the ungrouped form runs `pwd`
# even when `git` SUCCEEDED and REPO_ROOT becomes TWO lines — every later path then silently
# resolves against a two-line string. Caught by spiking this file's own round-trip.
REPO_ROOT="$(git -C "${PLAN_DIR}" rev-parse --show-toplevel 2>/dev/null \
             || { cd "${PLAN_DIR}/../../.." && pwd; })"

# The tree a fixture asserts against.
#
# THE DEFAULT IS RESOLVED, NOT ASSUMED (plan-053 Issue 1.1). plan-050 kept its assets in the
# PRIMARY checkout, so `${REPO_ROOT}/.worktrees/${PLAN_ID}` was always the right answer there.
# This plan keeps its assets in the EXECUTION WORKTREE — which is what makes a fixture and the
# fix it grades land on the same branch, so a RED and a GREEN are observable from one tree. In
# that layout `REPO_ROOT` already IS the worktree, and the inherited default produced the
# doubled path `<worktree>/.worktrees/<plan-id>/`.
#
# Caught by the exit-2 guard added immediately above, on its first real use: the fixture
# reported HARNESS/exit 2, `record-red` REFUSED it and wrote nothing. Under the harness as
# adopted this would have printed `RED observed`, exited 0, and banked a fabricated RED
# record for a fixture that never ran — R3 exactly, inside the instrument built to prevent it.
#
# THE PROBE IS THE WORKTREE ITSELF, NOT A FILE INSIDE IT (#229, plan-054 Issue 0.6). The
# adopted form probed for `.worktrees/<plan-id>/_shared` — a directory that exists because
# THIS repository happens to carry a top-level `_shared/`. That is plan-050's asset layout
# baked into a portability decision: in any checkout without `_shared/` the probe fails, the
# `else` arm fires, and `YF_TREE` silently becomes the PRIMARY tree while the fixes under
# grading are on the worktree branch. Every fixture then measures the wrong tree and reports
# a confident, wrong answer.
#
# The question actually being asked is "does this plan have an execution worktree?", so ask
# THAT — the worktree directory's own existence — and depend on no file within it.
if [ -z "${YF_TREE:-}" ]; then
  if [ -d "${REPO_ROOT}/.worktrees/${PLAN_ID}" ]; then
    YF_TREE="${REPO_ROOT}/.worktrees/${PLAN_ID}"      # assets in the primary checkout
  else
    YF_TREE="${REPO_ROOT}"                            # assets in the execution worktree (or in-place)
  fi
fi
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

The `command` field records the FIXTURE-SELECTING ENVIRONMENT verbatim — `YF_TREE`, and
`CTL_RED` when set. A control whose RED was driven against a PINNED NEGATIVE FIXTURE rather
than against the live tree must say so ON ITS FACE, or the record silently overstates what
was observed.

`git-describe` is recorded FOR DIAGNOSIS ONLY. It makes no ordering claim: pass-7 C69
measured that check vacuous, because nothing requires the fix to be committed before
`assert-distinguishes` runs. The ordering "RED was observed before the fix landed" is carried
by the plan's `depends-on` edges, not by this file.

**`CTL_RED=1` IN THE COMMAND FIELD MARKS A *DRIVEN* RED.** Some controls grade work that,
under SPEC-first ordering, has necessarily already landed on the live tree — so the control is
green there and can never be driven red against it. Those controls carry a PINNED NEGATIVE
FIXTURE and select it with `CTL_RED=1`. This is the single convention: grep the `command` field
for `CTL_RED` to get exactly the set of REDs that were driven rather than observed in place.
(`ctl-214-id-collision` was first recorded by pointing `YF_TREE` at its pinned tree directly;
that record is still accurate, and its `CTL_RED=1` record supersedes it as the canonical form.)

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

  # ---- THE RC CHECK RUNS **BEFORE** `_append`. THIS ORDER IS THE REQUIREMENT. ----------
  #
  # plan-053 Issue 1.1(b), measured. In the ADOPTED plan-050 harness `_append` ran FIRST, so
  # a `record-red` against a fixture exiting **2** printed `RED observed`, returned 0, and
  # left an `rc=2` line on disk that `_has_record … nonzero` later matched. Spiked at pass 3:
  # a fixture exiting 2 made `record-red` print `RED observed`, `assert-distinguishes` say
  # `DISTINGUISHED`, and `verify-all` return **0**.
  #
  # A RECORD-TIME GUARD CANNOT UN-WRITE THE RECORD. Rejecting the exit code while still
  # appending it leaves the evidence behind for every later reader, so the only fix that
  # holds is to refuse to write it at all. An exit 2 is the HARNESS failing to run the
  # fixture — it establishes nothing in either direction, and calling it RED manufactures
  # evidence. R3's failure mode would otherwise occur inside the instrument built to prevent
  # it.
  if [ "${rc}" -eq 0 ]; then
    echo "redcheck: FAIL — ${control}'s fixture exited 0 against the UNFIXED tree." >&2
    echo "redcheck: a fixture that has never been observed failing is not evidence (D-4)." >&2
    echo "redcheck: NOTHING WAS RECORDED." >&2
    return 1
  fi
  if [ "${rc}" -eq 2 ]; then
    echo "redcheck: FAIL — ${control}'s fixture exited 2 (INCONCLUSIVE): the fixture could" >&2
    echo "redcheck: not run at all. That is a statement about the INSTRUMENT, not about the" >&2
    echo "redcheck: tree, so it is not a RED observation and IS NOT RECORDABLE." >&2
    echo "redcheck: NOTHING WAS RECORDED. Repair the fixture, then re-run." >&2
    return 1
  fi

  _append "record-red" "${control}" "${fixture}" "${rc}" \
    "${CTL_RED:+CTL_RED=${CTL_RED} }YF_TREE=${YF_TREE} bash ${fixture#${PLAN_DIR}/}"
  echo "redcheck: RED observed — ${control} exited ${rc} against ${YF_TREE}"
  return 0
}

# cmd_record_red_check — THE WRITE HALF FOR CRITERION INSTRUMENTS (plan-054 Issue 0.6).
#
# WHY A SECOND RECORDER EXISTS RATHER THAN A RELAXED `record-red`.
#
# Measured at source: `cmd_record_red` gates on `_in_manifest`, a `grep -qxF` against
# `controls.txt`. `_derive_manifest` builds that file's authoritative set by grepping plan.md
# for `ctl-[0-9]{3}-[a-z-]+`, and `assets/checks/` is deliberately OUTSIDE that set (the
# plan-053 pass-4 C44 split: `checks/` holds criterion-only instruments, `fixtures/` holds
# red->green `ctl-` controls). So a `check-*.sh` can NEVER appear in `controls.txt`, and
# `record-red` on one hard-fails at the manifest gate and writes NOTHING.
#
# That is the fail-closed gap this plan's context calls out: `verify-red-checks` (below) would
# otherwise read an empty set forever — a verifier with no recorder. Relaxing `_in_manifest`
# was rejected because it would let a MISSPELLED control name through the `ctl-` path too;
# widening a shared gate to admit a second population weakens it for the first. This verb
# instead applies the analogous membership test for its own population: DIRECTORY MEMBERSHIP
# in `assets/checks/`.
#
# Every other guarantee of `record-red` is preserved verbatim, and deliberately so:
#   - the exit-0 refusal (a check green on the unfixed tree is not evidence);
#   - the exit-2 refusal (the harness could not run it — that is a statement about the
#     INSTRUMENT, not the tree, and recording it manufactures evidence);
#   - the rc-check-BEFORE-`_append` ordering, because a record-time guard cannot un-write a
#     record. Both refusals write nothing at all.
cmd_record_red_check() {
  local script="$1"
  local name; name="$(basename "${script}")"
  [ -d "${CHECKS_DIR}" ] || harness_fail "checks dir missing: ${CHECKS_DIR}"
  case "${name}" in
    check-*.sh) : ;;
    *) harness_fail "'${name}' is not a check instrument (expected a check-*.sh under ${CHECKS_DIR})" ;;
  esac
  [ -f "${CHECKS_DIR}/${name}" ] || harness_fail \
    "check '${name}' is not in ${CHECKS_DIR} — an instrument the gate cannot see"

  _run_fixture "${CHECKS_DIR}/${name}" || return 2
  local rc="${FIXTURE_RC}"

  if [ "${rc}" -eq 0 ]; then
    echo "redcheck: FAIL — ${name} exited 0 against the UNFIXED tree." >&2
    echo "redcheck: a criterion instrument that has never been observed failing is not" >&2
    echo "redcheck: evidence. If it LEGITIMATELY holds today, add it to" >&2
    echo "redcheck: ${CHECKS_ALLOWLIST} WITH ITS REASON." >&2
    echo "redcheck: NOTHING WAS RECORDED." >&2
    return 1
  fi
  if [ "${rc}" -eq 2 ]; then
    echo "redcheck: FAIL — ${name} exited 2 (INCONCLUSIVE): the check could not run at all." >&2
    echo "redcheck: That is a statement about the INSTRUMENT, not the tree, so it is not a" >&2
    echo "redcheck: RED observation and IS NOT RECORDABLE." >&2
    echo "redcheck: NOTHING WAS RECORDED. Repair the check, then re-run." >&2
    return 1
  fi

  _append "record-red-check" "${name}" "${CHECKS_DIR}/${name}" "${rc}" \
    "YF_TREE=${YF_TREE} bash assets/checks/${name}"
  echo "redcheck: RED observed — ${name} exited ${rc} against ${YF_TREE}"
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
    "${CTL_RED:+CTL_RED=${CTL_RED} }YF_TREE=${YF_TREE} bash ${fixture#${PLAN_DIR}/}"
  local ok=0
  if [ "${rc}" -ne 0 ]; then
    echo "redcheck: FAIL — ${control}'s fixture exited ${rc} against the FIXED tree; expected 0." >&2
    ok=1
  fi
  # BOTH observations must be on record — this verb never certifies a control it has only
  # ever seen green.
  if ! _has_record "record-red" "${control}" red; then
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
      # `red` is STRICTER than `nonzero`: an exit 2 is the harness failing to run, so it is
      # not a RED. The record-time guard above already refuses to write one, and this is the
      # read-side half of the same rule — a manifest carrying a legacy rc=2 line from an
      # older harness must not certify. The gate Condition says "non-zero, non-2"; this is
      # that sentence, executed.
      if (want == "red"     && rc != 0 && rc != 2) { found = 1 }
    }
    END { exit(found ? 0 : 1) }
  ' "${RECORDS}"
}

# _derive_manifest — assert `controls.txt` and plan.md agree about the control SET.
#
# plan-053 Issue 1.1(c). This is FACTORED OUT so `verify-red-all` PERFORMS the derivation
# ITSELF rather than confirming in prose that `verify-all` would have done it. pass-10 C93's
# protection is only worth what executes it: a gate that states a check runs, and does not
# run it, is downgraded from executed to stated — which is the defect class this whole plan
# is about, reproduced in the gate that guards it.
#
# The comparison is SET-WISE, not count-wise. Two sets can have equal cardinality and
# different members, and a count check calls that agreement.
_derive_manifest() {
  local declared manifest_set declared_set
  declared_set="$(grep -oE 'ctl-[0-9]{3}-[a-z-]+' "${PLAN_MD}" | sort -u)"
  manifest_set="$(grep -vE '^[[:space:]]*(#|$)' "${MANIFEST}" | sort -u)"
  if [ "${declared_set}" != "${manifest_set}" ]; then
    echo "redcheck: FAIL — ${MANIFEST} and plan.md disagree about the control SET." >&2
    echo "redcheck: a control missing from the manifest is a control this gate CANNOT SEE." >&2
    echo "redcheck: only in plan.md:" >&2
    comm -23 <(echo "${declared_set}") <(echo "${manifest_set}") | sed 's/^/redcheck:   /' >&2
    echo "redcheck: only in the manifest:" >&2
    comm -13 <(echo "${declared_set}") <(echo "${manifest_set}") | sed 's/^/redcheck:   /' >&2
    return 1
  fi
  declared="$(echo "${declared_set}" | grep -c . | tr -d ' ')"
  [ "${declared}" -gt 0 ] || { harness_fail "derivation matched no controls in ${PLAN_MD}"; }
  return 0
}

# cmd_verify_red_all — the RED-ONLY gate verb (plan-053 Issue 1.1(a)).
#
# WHY THIS VERB EXISTS AND `verify-all` COULD NOT BE USED. The capability gate "RED observed
# before any fix" blocks all seven fix heads. `verify-all` additionally demands a GREEN
# `assert-distinguishes` record per control — which BY CONSTRUCTION cannot exist before the
# fixes those heads land. Pointing the gate at `verify-all` makes it unsatisfiable while it
# blocks the only work that could satisfy it.
#
# It asserts a non-zero, NON-2 `record-red` for every manifest control, and asserts NOTHING
# ABOUT GREEN. That is the gate's Condition, word for word.
cmd_verify_red_all() {
  [ -f "${MANIFEST}" ] || harness_fail "manifest missing: ${MANIFEST}"
  [ -f "${PLAN_MD}" ]  || harness_fail "plan.md missing: ${PLAN_MD}"

  _derive_manifest || return 1

  local rc=0 n=0
  while IFS= read -r control; do
    case "${control}" in ''|'#'*) continue ;; esac
    n=$((n + 1))
    if ! _has_record "record-red" "${control}" red; then
      echo "redcheck: FAIL — ${control}: no \`record-red\` observation with a NON-ZERO, NON-2 exit." >&2
      rc=1
    fi
  done < "${MANIFEST}"

  if [ "${n}" -eq 0 ]; then
    harness_fail "manifest is empty — verify-red-all would certify vacuously"
  fi
  if [ "${rc}" -eq 0 ]; then
    echo "redcheck: all ${n} control(s) observed RED (non-zero, non-2) against the unfixed tree"
  fi
  return "${rc}"
}

# cmd_verify_manifest — `_derive_manifest` as a STANDALONE ENTRY POINT (plan-054 Issue 0.6).
#
# The adopted harness ships no such verb: its verbs are `record-red`, `assert-distinguishes`,
# `verify-red-all` and `verify-all`, and the derivation is only reachable as a side effect of
# the last two. Exposing it directly lets the plan.md<->controls.txt set agreement be checked
# on its own, at authoring time, without also demanding the RED records that do not exist yet.
cmd_verify_manifest() {
  [ -f "${MANIFEST}" ] || harness_fail "manifest missing: ${MANIFEST}"
  [ -f "${PLAN_MD}" ]  || harness_fail "plan.md missing: ${PLAN_MD}"
  _derive_manifest || return 1
  echo "redcheck: controls.txt and plan.md agree about the control SET"
  return 0
}

# _check_allowlisted <check-name> — is this instrument on the recorded allowlist?
#
# The allowlist is `<name>` optionally followed by whitespace and a REASON. A bare name with
# no reason is REJECTED by `verify-red-checks`: 0.1 requires the reason to be recorded, and an
# allowlist that accepts a naked name is an allowlist with no accountability.
_check_allowlisted() {
  [ -f "${CHECKS_ALLOWLIST}" ] || return 1
  grep -vE '^[[:space:]]*(#|$)' "${CHECKS_ALLOWLIST}" \
    | awk -v n="$1" '{ if ($1 == n) { found=1 } } END { exit(found ? 0 : 1) }'
}

# _check_allowlist_reason <check-name> — the recorded reason, or empty.
_check_allowlist_reason() {
  [ -f "${CHECKS_ALLOWLIST}" ] || return 1
  grep -vE '^[[:space:]]*(#|$)' "${CHECKS_ALLOWLIST}" \
    | awk -v n="$1" '{ if ($1 == n) { $1=""; sub(/^[ \t]+/, ""); print; exit } }'
}

# cmd_verify_red_checks — THE READ HALF (plan-054 Issue 0.6, discharging Issue 0.1's C1).
#
# WHY `verify-red-all` COULD NOT BE REUSED. It iterates `controls.txt`, whose set
# `_derive_manifest` derives with the `ctl-` pattern; `assets/checks/` is deliberately outside
# that set. So `verify-red-all` STRUCTURALLY CANNOT SEE the criterion instruments — not as an
# oversight but by the C44 split's design. Without this verb, Issue 0.1's obligation over the
# check scripts would be STATED AND NEVER EXECUTED.
#
# It iterates `assets/checks/` minus the allowlist and asserts each has a recorded non-zero,
# non-2 pre-fix observation. Vacuity is a HARNESS FAILURE, not a pass: an empty checks dir, or
# one every member of which is allowlisted, certifies nothing and says so.
cmd_verify_red_checks() {
  [ -d "${CHECKS_DIR}" ] || harness_fail "checks dir missing: ${CHECKS_DIR}"

  local rc=0 n=0 allowed=0 name reason
  for script in "${CHECKS_DIR}"/check-*.sh; do
    [ -e "${script}" ] || continue
    name="$(basename "${script}")"
    if _check_allowlisted "${name}"; then
      reason="$(_check_allowlist_reason "${name}")"
      if [ -z "${reason}" ]; then
        echo "redcheck: FAIL — ${name} is allowlisted with NO RECORDED REASON." >&2
        echo "redcheck: 0.1 requires the reason; a naked allowlist entry is unaccountable." >&2
        rc=1
      else
        echo "redcheck: allowlisted — ${name}: ${reason}"
        allowed=$((allowed + 1))
      fi
      continue
    fi
    n=$((n + 1))
    if ! _has_record "record-red-check" "${name}" red; then
      echo "redcheck: FAIL — ${name}: no \`record-red-check\` observation with a NON-ZERO, NON-2 exit." >&2
      rc=1
    fi
  done

  if [ "${n}" -eq 0 ]; then
    harness_fail "no non-allowlisted check instrument found in ${CHECKS_DIR} (${allowed} allowlisted) — verify-red-checks would certify vacuously"
  fi
  if [ "${rc}" -eq 0 ]; then
    echo "redcheck: all ${n} check instrument(s) observed RED (non-zero, non-2) against the unfixed tree (${allowed} allowlisted)"
  fi
  return "${rc}"
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
  _derive_manifest || return 1

  local rc=0 n=0
  while IFS= read -r control; do
    case "${control}" in ''|'#'*) continue ;; esac
    n=$((n + 1))
    if ! _has_record "record-red" "${control}" red; then
      echo "redcheck: FAIL — ${control}: no \`record-red\` observation with a NON-ZERO, NON-2 exit." >&2
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
  verify-red-all)
    [ "$#" -eq 1 ] || harness_fail "usage: redcheck.sh verify-red-all"
    cmd_verify_red_all ;;
  record-red-check)
    [ "$#" -eq 2 ] || harness_fail "usage: redcheck.sh record-red-check <checks/check-*.sh>"
    cmd_record_red_check "$2" ;;
  verify-red-checks)
    [ "$#" -eq 1 ] || harness_fail "usage: redcheck.sh verify-red-checks"
    cmd_verify_red_checks ;;
  verify-manifest)
    [ "$#" -eq 1 ] || harness_fail "usage: redcheck.sh verify-manifest"
    cmd_verify_manifest ;;
  verify-all)
    [ "$#" -eq 1 ] || harness_fail "usage: redcheck.sh verify-all"
    cmd_verify_all ;;
  '')
    harness_fail "no verb given. Expected one of: record-red | record-red-check | assert-distinguishes | verify-manifest | verify-red-all | verify-red-checks | verify-all" ;;
  *)
    harness_fail "unknown verb: '${verb}'. Expected one of: record-red | assert-distinguishes | verify-red-all | verify-all" ;;
esac
