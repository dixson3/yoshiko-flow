#!/usr/bin/env bash
# SC11 — the changelog's released heading matches the crate version, and both are 0.5.0.
CHECK_NAME=check-version-agrees
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
CL="${TREE}/CHANGELOG.md"; CT="${TREE}/yf/Cargo.toml"
[ -f "${CL}" ] || ck_inconclusive "no CHANGELOG.md at ${CL}"
[ -f "${CT}" ] || ck_inconclusive "no yf/Cargo.toml at ${CT}"
CK_RC=0

crate="$(awk -F'"' '/^version[[:space:]]*=/{print $2; exit}' "${CT}")"
[ -n "${crate}" ] || ck_inconclusive "could not read a version from ${CT}"
[ "${crate}" = "0.5.0" ] || ck_fail "the crate version is '${crate}', not 0.5.0"
grep -qE '^## +\[?0\.5\.0\]?' "${CL}" || ck_fail "CHANGELOG.md carries no released '## 0.5.0' heading"
ck_done "the crate and the changelog agree on 0.5.0"
