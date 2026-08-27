#!/usr/bin/env bash
# SC5 — EVERY consumer is generated, and a hand-edit to any one of them fails the check.
#
# THE EXPECTED COUNT IS DERIVED, NEVER EMBEDDED. A literal in a criterion or a filename is the
# drift defect 0.8 bans: it goes stale the moment a consumer is added, and then certifies a
# smaller set than ships. So the denominator here is "every file carrying a SKILL_DIR
# resolver", computed from the tree, and the numerator is "how many of those are generated".
#
# THE MUTATION HALF IS NOT OPTIONAL. `sync.py --check` passing proves the consumers agree with
# the template RIGHT NOW; it does not prove the check can FAIL. An earlier draft asserted only
# the clean run and was green on the unfixed tree while none of the 19 resolver consumers was
# generated at all — a check that cannot fail is not a check. So this hand-edits a consumer in
# a scratch COPY and requires --check to go red.
CHECK_NAME=check-sync-emits-all
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
SYNC="${TREE}/_shared/sync.py"
[ -f "${SYNC}" ] || ck_inconclusive "no _shared/sync.py at ${SYNC}"
ck_need uv
CK_RC=0

# Denominator: every file that carries a SKILL_DIR resolver.
consumers="$(grep -rl 'SKILL_DIR=' "${TREE}/skills" 2>/dev/null | sort -u || true)"
n=0; [ -n "${consumers}" ] && n="$(printf '%s\n' "${consumers}" | grep -c .)"
[ "${n}" -gt 0 ] || ck_inconclusive "found no SKILL_DIR consumer under skills/ — a check over nothing certifies vacuously"

# Numerator: how many of those carry the generated-block marker.
gen=0
while IFS= read -r f; do
  [ -n "${f}" ] || continue
  grep -q 'BEGIN SKILL_DIR resolver' "${f}" && gen=$((gen + 1))
done <<< "${consumers}"

if [ "${gen}" -ne "${n}" ]; then
  ck_fail "${gen} of ${n} SKILL_DIR consumers are generated — $(( n - gen )) are still hand-written"
  while IFS= read -r f; do
    [ -n "${f}" ] || continue
    grep -q 'BEGIN SKILL_DIR resolver' "${f}" || printf '  %s\n' "${f#${TREE}/}" >&2
  done <<< "${consumers}"
fi

out="$(cd "${TREE}" && env -u VIRTUAL_ENV uv run "${SYNC}" --check 2>&1)"; rc=$?
[ "${rc}" -eq 0 ] || { ck_fail "sync.py --check reports the generated consumers are out of date:"; printf '%s\n' "${out}" | tail -10 >&2; }

# The mutation half, in a scratch copy — the repository under test is never modified.
SCRATCH="$(mktemp -d)" || ck_inconclusive "mktemp failed"
trap 'rm -rf "${SCRATCH}"' EXIT
victim="$(printf '%s\n' "${consumers}" | head -1)"
if [ -n "${victim}" ] && [ "${gen}" -eq "${n}" ] && [ "${rc}" -eq 0 ]; then
  cp -Rf "${TREE}" "${SCRATCH}/tree" 2>/dev/null || ck_inconclusive "could not copy the tree for the mutation probe"
  vrel="${victim#${TREE}/}"
  # THE EDIT MUST LAND INSIDE THE REGION. Appending at end-of-file proves nothing: the region
  # is marker-fenced, so `sync.py --check` compares only the marked interior and an append
  # outside it is correctly ignored. An earlier draft appended at EOF and concluded the check
  # "cannot detect drift", which was a defect in the PROBE, not in sync.py.
  awk '
    /BEGIN SKILL_DIR resolver/ { print; print "# hand-edit injected by check-sync-emits-all"; next }
    { print }
  ' "${SCRATCH}/tree/${vrel}" > "${SCRATCH}/mutated" && mv -f "${SCRATCH}/mutated" "${SCRATCH}/tree/${vrel}"
  if (cd "${SCRATCH}/tree" && env -u VIRTUAL_ENV uv run _shared/sync.py --check >/dev/null 2>&1); then
    ck_fail "a hand-edit to ${vrel} did NOT fail sync.py --check — the check cannot detect drift it is supposed to catch"
  fi
fi
ck_done "all ${n} SKILL_DIR consumers are generated, in sync, and a hand-edit is detected"
