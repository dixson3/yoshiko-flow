#!/usr/bin/env bash
# check-pytest-ran.sh <test-file> <test-name> — the TEST-INVOCATION GUARD (REQ-CLI-028).
#
# Asserts that a NAMED test EXISTS and RAN AND PASSED. Six criteria route through it
# (SC4, SC7, SC8, SC10b, SC28, SC36), which makes it this plan's busiest instrument and the
# one whose vacuity would be most expensive.
#
# WHY IT EXISTS. Three consecutive red-team passes of plan-056 found the criteria layer
# vacuous, each through a different mechanism:
#
#   (1) `uv run <test_file.py> -k <name>` DISCARDS `sys.argv` in this repo — every
#       hand-rolled `__main__` calls `pytest.main([])` — so the selector is dropped, the
#       whole file runs, and the criterion asserts "some test passed". It stays GREEN when
#       the named function is deleted.
#   (2) a criterion expecting non-zero from a script that does not exist is satisfied by
#       `uv run <missing>.py`, which itself exits 2.
#   (3) an unjudged criterion read as PASS (#265, fixed by Issue 1.10).
#
# THE VACUITY IS FORM-SPECIFIC, and this comment states the correction because an earlier
# draft got it backwards. It is NOT true that pytest exits 0 on a no-match: measured,
# module-form `python -m pytest -k <no-match>` exits **5** (`N deselected`) and
# `pytest <missing-file>` exits **4**. `CHANGE-VALIDATION.md` recorded this already. The
# defect lives ONLY in the direct-file form — which the repo's recipe never uses and the
# criteria did.
#
# PEP 723 DEPENDENCIES ARE PARSED FROM THE TARGET AND FORWARDED. Not optional: measured,
# `uv run --with pytest python -m pytest _shared/test_okf.py` dies at COLLECTION with exit 2,
# because module form makes `python` the entrypoint and the target's own inline header is
# never read — while `test_cli_enumeration.py` happens to need nothing and passes. The
# per-file dependency set is heterogeneous, so a fixed `--with` list is right by luck.
#
# EXIT  0 the named test ran and passed
#       1 it ran and FAILED, or it does not exist in the file
#       2 INCONCLUSIVE — could not run (no such file, no pytest-driveable entrypoint)
#
# 126/127 STAY RESERVED TO THE CALLER (REQ-CLI-029). Returning either would make every
# criterion routed through this script permanently unfailable, since a caller could not
# distinguish this script's verdict from the shell's report that it could not execute it.
#
# THE INCONCLUSIVE CODE IS 2, NOT 3. `scripts/checks/_common.sh` declares 2 for this whole
# directory, and `redcheck.sh record-red-check` REFUSES to bank a 2 — correctly, because a 2
# is not a red observation. An invented 3 would be banked as a genuine red, converting "the
# instrument could not run" into "the criterion was measured false".
#
# EXPLICITLY NOT IN SCOPE: rewriting the repo's 34 `pytest.main` call sites. The wrapper
# closes the gap alone, and a repo-wide refactor touching every skill does not belong on the
# critical path of the six criteria that invoke it.
CHECK_NAME=check-pytest-ran
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

TARGET_REL="${1:-}"
TEST_NAME="${2:-}"
[ -n "${TARGET_REL}" ] && [ -n "${TEST_NAME}" ] \
  || ck_inconclusive "usage: check-pytest-ran.sh <test-file> <test-name>"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ck_need uv

# Accept a tree-relative or an absolute path.
case "${TARGET_REL}" in
  /*) TARGET="${TARGET_REL}" ;;
  *)  TARGET="${TREE}/${TARGET_REL}" ;;
esac
[ -f "${TARGET}" ] || ck_inconclusive "no such test file: ${TARGET}"

# --- ASSERTION 0: the entrypoint must be pytest-driveable ---------------------------
# FIRST, and the ORDER IS FORCED. If the file cannot be driven by pytest at all, the
# instrument cannot judge the criterion in EITHER direction — so the answer is
# INCONCLUSIVE (2), not FAIL (1). Running the `def` grep first would report `test_x is
# absent` about a file whose functions the instrument could never have run, which is a
# claim about the DOCUMENT dressed up as a claim about the TEST.
# Measured: `_shared/test_doc_lint.py` has 0 `def test`, no pytest import and no `__main__`;
# 15 repo test files have no `__main__` at all. A hand-rolled non-pytest script cannot be
# driven by a selector, so reporting a green on it would be the "check that cannot fail"
# defect one level up from the check.
if ! grep -qE '^[[:space:]]*(import pytest|from pytest)' "${TARGET}"; then
  ck_inconclusive "${TARGET_REL} does not import pytest — not a pytest-driveable entrypoint"
fi

# --- ASSERTION 1 of 3: the named function EXISTS ------------------------------------
# A separate assertion from "it passed", because a renamed-away function and a failing one
# are different facts and a single pytest exit cannot distinguish them: a `-k` selector
# matching nothing exits 5, which is neither of the answers the caller wants.
#
# THE MATCH IS A SUBSTRING, DELIBERATELY, because `-k` is. Callers pass the bare name
# (`marker_imbalance_check_mode`) for a function conventionally spelled
# `test_marker_imbalance_check_mode`. An anchored grep here would disagree with the
# selector used three assertions later — the grep would say "absent" about a function
# pytest then runs — and two assertions that disagree about what "the named test" MEANS is
# the same conflation this whole plan is written against, reproduced inside its own guard.
#
# FAIL (1), not INCONCLUSIVE (2): the instrument ran fine and the claim is false. This is
# the arm that makes the guard bite — it is what goes red when a test is deleted.
if ! grep -qE "^[[:space:]]*(async[[:space:]]+)?def[[:space:]]+[A-Za-z0-9_]*${TEST_NAME}[A-Za-z0-9_]*[[:space:]]*\(" "${TARGET}"; then
  ck_fail "no \`def ${TEST_NAME}(\` in ${TARGET_REL} — the named test does not exist"
  exit 1
fi

# --- PEP 723 dependencies, parsed FROM THE TARGET -----------------------------------
# Read the inline `# /// script` block's `dependencies = [...]` and turn each into a
# `--with`. pytest is added unconditionally, since the module form supplies the runner.
DEPS_ARGS=()
while IFS= read -r dep; do
  [ -n "${dep}" ] && DEPS_ARGS+=(--with "${dep}")
done < <(
  awk '
    /^# \/\/\/ script/       { inblk=1; next }
    inblk && /^# \/\/\//     { exit }
    inblk && /dependencies/  { indep=1 }
    indep {
      line=$0
      gsub(/^#[[:space:]]?/, "", line)
      while (match(line, /"[^"]+"/)) {
        print substr(line, RSTART+1, RLENGTH-2)
        line = substr(line, RSTART+RLENGTH)
      }
      if (index($0, "]")) indep=0
    }
  ' "${TARGET}"
)
DEPS_ARGS+=(--with pytest)

# --- ASSERTIONS 2 and 3: it RAN, and a NON-ZERO number passed -----------------------
# MODULE FORM (`python -m pytest`), never the direct-file form — the direct form is the one
# whose `__main__` discards `sys.argv`. In module form the selector is honoured, a no-match
# exits 5 and a missing file exits 4, so both are loud.
OUT="$(cd "${TREE}" && uv run "${DEPS_ARGS[@]}" python -m pytest "${TARGET}" \
        -k "${TEST_NAME}" -q --no-header 2>&1)"
RC=$?

case "${RC}" in
  0) : ;;                                   # ran; the passed-count check below decides
  1) ck_fail "${TEST_NAME} in ${TARGET_REL} FAILED"; printf '%s\n' "${OUT}" >&2; exit 1 ;;
  5) ck_fail "the selector \`${TEST_NAME}\` matched NOTHING (pytest exit 5) — the \`def\` grep"\
             "passed, so the name exists but pytest did not collect it"; exit 1 ;;
  4) ck_inconclusive "pytest could not collect ${TARGET_REL} (exit 4)" ;;
  2) ck_inconclusive "pytest errored during collection of ${TARGET_REL} (exit 2)"$'\n'"${OUT}" ;;
  *) ck_inconclusive "pytest returned an unhandled exit ${RC} for ${TARGET_REL}"$'\n'"${OUT}" ;;
esac

# A NON-ZERO PASSED COUNT. Exit 0 alone is not enough: pytest exits 0 having run nothing in
# some configurations, and "the suite was green" is not the claim being made — "this named
# test passed" is.
PASSED="$(printf '%s' "${OUT}" | grep -oE '[0-9]+ passed' | head -1 | grep -oE '^[0-9]+')"
if [ -z "${PASSED}" ] || [ "${PASSED}" -eq 0 ]; then
  ck_fail "pytest exited 0 but reported no passing test for \`${TEST_NAME}\` in ${TARGET_REL}"
  printf '%s\n' "${OUT}" >&2
  exit 1
fi

ck_done "${TEST_NAME} exists in ${TARGET_REL}, ran, and ${PASSED} test(s) passed"
