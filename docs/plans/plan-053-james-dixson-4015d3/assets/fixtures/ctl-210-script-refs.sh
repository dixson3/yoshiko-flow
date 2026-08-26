#!/usr/bin/env bash
# ctl-210-script-refs — REQ-YF-EMBED-005 / #210, the CLASS fix (D-3).
#
# A FIXTURE per redcheck.sh's definition: exits 0 iff the asserted behaviour holds.
#
# WHAT IT ASSERTS
#   1. The check is PROMOTED to its repo-level home `scripts/check_skill_script_refs.py`
#      (Issue 3.5). A repo-level guard, not a shipped skill script — the precedent is
#      `scripts/check_frontmatter.py`; shipping it inside a skill would make it
#      self-referential.
#   2. FP-CLEAN: the false-positive tree returns exit **0**. Five prose `_shared/` mentions
#      (including plan-050's own note verbatim — the note EXPLAINING this defect, which a
#      naive grep flags), a non-shell `python` fence containing an invocation-shaped comment,
#      and an allow-marked deliberate external.
#   3. THE PLAN-050 MUTANT: the same tree plus plan-050 Issue 7.3's original bug, verbatim,
#      returns exit **1** and names the offending path. This is THE ARGUMENT FOR D-3: volume
#      is the wrong justification (the `_shared/` class is exactly ONE live break), and the
#      right one is that the check catches the FIRST instance too.
#
# HOW THE RED IS DRIVEN, AND WHY NOT THE OBVIOUS WAY
# --------------------------------------------------
# The obvious fixture just invokes `scripts/check_skill_script_refs.py` and fails because the
# file is absent. That is an ABSENT-INSTRUMENT RED — R3's named pattern, and the same shape
# plan-050 measured when a missing fixture reported `RED observed` at exit 0. A control whose
# only failure mode is "file not found" has never demonstrated that its assertions are
# SATISFIABLE, so it cannot distinguish "the fix has not landed" from "the fix is impossible".
#
# So this fixture RESOLVES the checker, preferring the promoted repo-level path and falling
# back to the PROTOTYPE rebuilt at Issue 1.0. It then runs the behavioural assertions against
# whichever it found. Falling back is itself recorded as a failure (assertion 1), so the RED
# is a real behavioural run that additionally reports the promotion is outstanding — never a
# crash, and never an exit 2.
#
# Tree under test: $YF_TREE (set by redcheck.sh).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"

PROMOTED="${YF_TREE}/scripts/check_skill_script_refs.py"
PROTOTYPE="${HERE}/check_skill_script_refs.py"
FP="${HERE}/corpus/fp-clean"
MUT="${HERE}/corpus/plan050-mutant"

[ -d "${FP}" ]  || { echo "ctl-210-script-refs: HARNESS — no FP fixture tree at ${FP}" >&2; exit 2; }
[ -d "${MUT}" ] || { echo "ctl-210-script-refs: HARNESS — no mutant tree at ${MUT}" >&2; exit 2; }

bad=()

if [ -f "${PROMOTED}" ]; then
  CHECK="${PROMOTED}"
elif [ -f "${PROTOTYPE}" ]; then
  CHECK="${PROTOTYPE}"
  bad+=("assertion 1 (PROMOTION): the check is not at its repo-level home \
\`scripts/check_skill_script_refs.py\`. Running the Issue-1.0 prototype instead, so the \
behavioural assertions below are still exercised rather than short-circuited by an \
absent instrument.")
else
  echo "ctl-210-script-refs: HARNESS — no checker at ${PROMOTED} and no prototype at ${PROTOTYPE}" >&2
  exit 2
fi

run_check() {  # run_check <root> [extra args] -> echoes exit code
  local root="$1"; shift
  (cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${CHECK}" --root "${root}" "$@" >/dev/null 2>&1)
  echo "$?"
}

# ---- 2. FP-CLEAN -> exit 0 --------------------------------------------------------------
rc_fp="$(run_check "${FP}")"
if [ "${rc_fp}" != "0" ]; then
  bad+=("assertion 2 (FP-CLEAN): the false-positive tree returned ${rc_fp}, expected 0. \
Its five prose \`_shared/\` mentions, its non-shell python fence and its allow-marked \
external must all be ignored — a checker that flags plan-050's own explanatory note is \
unusable.")
fi

# The FP tree must still contain a REAL invocation, or "0 violations" is vacuous — it would
# be satisfied by a checker that examines nothing at all.
fp_json="$( (cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${CHECK}" --root "${FP}" --all --json 2>/dev/null) )"
fp_checked="$(printf '%s' "${fp_json}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["checked"])' 2>/dev/null || echo 0)"
if [ "${fp_checked}" -lt 1 ]; then
  bad+=("assertion 2 (VACUITY): the FP tree yielded ${fp_checked} invocations. A tree with \
nothing in it passes trivially; the clean verdict must be earned over at least one real \
invocation.")
fi

# ---- 3. THE PLAN-050 MUTANT -> exit 1 ---------------------------------------------------
rc_mut="$(run_check "${MUT}")"
if [ "${rc_mut}" != "1" ]; then
  bad+=("assertion 3 (THE MUTATION): the plan-050 mutant returned ${rc_mut}, expected 1. \
Re-inserting plan-050 Issue 7.3's original bug verbatim must drive the check RED — that is \
the evidence it would have caught the FIRST instance, which is the whole argument for D-3.")
fi

# It must flag the RIGHT path for the RIGHT reason, not merely go non-zero.
mut_json="$( (cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${CHECK}" --root "${MUT}" --json 2>/dev/null) )"
if ! printf '%s' "${mut_json}" | grep -q '_shared/plan_extract.py'; then
  bad+=("assertion 3: the mutant's violation does not name \`_shared/plan_extract.py\`; the \
check went non-zero for some other reason.")
fi
if ! printf '%s' "${mut_json}" | grep -q 'repo-only'; then
  bad+=("assertion 3: the mutant's violation is not classified \`repo-only\`. The two failure \
shapes are DISTINCT — \`repo-only\` (rooted where only this repo resolves) and \
\`missing-in-repo\` (rooted correctly but never vendored) — and collapsing them would \
certify a rooted-but-unvendored path, which is exactly what #210's one-edit fix would have \
produced for pour_fidelity.py.")
fi

if [ "${#bad[@]}" -gt 0 ]; then
  echo "ctl-210-script-refs: ${#bad[@]} failure(s):" >&2
  for b in "${bad[@]}"; do echo "ctl-210-script-refs:   ${b}" >&2; done
  exit 1
fi
echo "ctl-210-script-refs: promoted; FP tree clean over ${fp_checked} invocation(s); plan-050 mutant flagged repo-only"
