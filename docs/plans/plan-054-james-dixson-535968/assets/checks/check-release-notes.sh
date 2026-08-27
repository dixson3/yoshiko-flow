#!/usr/bin/env bash
# SC36 — the release notes state pi's rules-and-skills-only tuning and the symlink-revert dirtying.
#
# Both are things a user will otherwise discover by surprise: D-7 keeps pi's config surface
# DEFERRED rather than guessing at it, and the symlink-revert half of #154 ships unfixed at
# tune time (Issue 6.4 files the successor). An honest release says so.
CHECK_NAME=check-release-notes
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
CL="${TREE}/CHANGELOG.md"
[ -f "${CL}" ] || ck_inconclusive "no CHANGELOG.md at ${CL}"
CK_RC=0

body="$(sed -n '/^## \[\?0\.5\.0/,/^## \[\?0\.4\.0/p' "${CL}")"
[ -n "${body}" ] || { ck_fail "no 0.5.0 section found in CHANGELOG.md"; exit "${CK_RC}"; }
printf '%s' "${body}" | grep -qi 'pi' \
  && printf '%s' "${body}" | grep -qiE 'rules[^.]*skills|skills[^.]*rules' \
  || ck_fail "the release notes do not state that \`--harness pi\` tunes rules and skills only"
printf '%s' "${body}" | grep -qi 'symlink' \
  || ck_fail "the release notes do not mention the symlink-revert behaviour"
ck_done "the release notes carry both disclosures"
