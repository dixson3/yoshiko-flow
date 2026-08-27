#!/usr/bin/env bash
# SC26 — every instrument named in #203 returns a non-zero exit when it reports failure.
#
# The one that lives in the BINARY is `yf skills status`, which ends in a bare Ok(()) on every
# path: it prints a uniformly-"no" health table and exits 0, so any caller branching on $?
# reads success from an instrument that just reported everything broken (REQ-YF-CLI-003).
CHECK_NAME=check-exit-discipline
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
YF="${TREE}/target/debug/yf"
[ -x "${YF}" ] || ck_inconclusive "no debug binary at ${YF} (run: cargo build)"
CK_RC=0

TMP="$(mktemp -d)" || ck_inconclusive "mktemp failed"
trap 'rm -rf "${TMP}"' EXIT
EMPTY="${TMP}/skills"; mkdir -p "${EMPTY}"

out="$("${YF}" skills status --target "${EMPTY}" --json 2>&1)"; rc=$?
if ! printf '%s' "${out}" | grep -q '"installed"[[:space:]]*:[[:space:]]*false'; then
  ck_inconclusive "no skill reported installed:false against an EMPTY dir, so there is no unhealthy state for the exit code to report"
fi
[ "${rc}" -eq 0 ] && ck_fail "\`yf skills status\` reported an unhealthy tree and exited 0"
ck_done "the #203 instruments report failure in their exit code"
