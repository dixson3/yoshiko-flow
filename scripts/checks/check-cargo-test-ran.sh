#!/usr/bin/env bash
# A named cargo test EXISTS and RAN GREEN.
#
# PROVENANCE: copied (never moved) from plan-054's bundle by plan-055 Issue 0.8 and re-based on
# `scripts/checks/_common.sh`. plan-054's copy stays frozen as that plan's record.
#
# THE CHECK ASSERTS THE TEST RAN, and that is the entire point. A `cargo test` filter matching
# ZERO tests prints "0 passed" and EXITS 0 — measured on this very plan while running the
# coverage tests, where `-p yf coverage` filtered everything out and reported success. So a
# criterion spelled "cargo test <name> exits 0" is satisfied by a test that does not exist.
# This asserts a non-zero passing count for the specific filter.
#
# USAGE: check-cargo-test-ran.sh <test-name>
CHECK_NAME=check-cargo-test-ran
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TEST_NAME="${1:-}"
[ -n "${TEST_NAME}" ] || ck_inconclusive "usage: check-cargo-test-ran.sh <test-name>"
ck_need cargo
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
[ -f "${TREE}/Cargo.toml" ] || ck_inconclusive "no Cargo.toml at ${TREE}"
CK_RC=0

# Fail FAST and LOUDLY when the test does not exist, rather than letting a zero-match run
# report success. This is the guard the criterion is named for.
if ! grep -rq "fn ${TEST_NAME}" "${TREE}/yf" --include='*.rs' 2>/dev/null \
   && ! grep -rq "fn ${TEST_NAME}" "${TREE}/tests" --include='*.rs' 2>/dev/null; then
  ck_fail "no test function named '${TEST_NAME}' exists anywhere — a cargo filter matching zero tests exits 0, so this must be checked before running"
  exit "${CK_RC}"
fi

out="$(cd "${TREE}" && env -u VIRTUAL_ENV cargo test "${TEST_NAME}" 2>&1)" || {
  ck_fail "cargo test '${TEST_NAME}' exited non-zero"
  printf '%s\n' "${out}" | tail -20 >&2
  exit "${CK_RC}"
}
passed="$(printf '%s' "${out}" | grep -oE '[0-9]+ passed' | awk '{s+=$1} END{print s+0}')"
if [ "${passed}" -lt 1 ]; then
  ck_fail "cargo test '${TEST_NAME}' exited 0 but ran NOTHING (0 passed) — a zero-match filter is not evidence"
  exit "${CK_RC}"
fi
ck_done "'${TEST_NAME}' ran and passed (${passed} test(s))"
