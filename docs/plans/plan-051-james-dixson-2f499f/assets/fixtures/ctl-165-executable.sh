#!/usr/bin/env bash
# ctl-165-executable — #165, narrowed to this plan's own REQs (D-4).
#
# A FIXTURE, per Issue 0.2's definition: EXITS 0 IFF THE ASSERTED BEHAVIOUR HOLDS. Here the
# asserted behaviour is that each of REQ-AGENT-049, REQ-AGENT-043 and REQ-AGENT-045 has a
# `Verification:` line that is a WHOLE-LINE BACKTICKED COMMAND **and that the command exits 0
# from the tree root**.
#
# (`052` was reserved in an early draft and DROPPED at pass 1 — D-1 narrowed #182 to an
# amendment of 043/045, so there is no third behaviour change needing an id.)
#
# THE REDUNDANCY CAVEAT, stated rather than discovered. If the two amended REQs' Verification
# lines ARE Epic 1's and Epic 2's assertions — and they are — then this control being green is
# equivalent to those two being green. It adds exactly one property: **the line parses as a
# command and runs**. That is a real assertion, and it is precisely the M5 defect #165 names.
# It is NOT independent evidence, and this plan does not present it as such.
#
# THE HONEST LIMITATION. Because Issue 0.1 already fixed the line's SHAPE, this control never
# observes the "prose shaped like a command" defect #165 actually names in the wild. It
# observes the *absence of the named test*, which is a narrower thing.
#
# EXIT
#   0  all three lines are whole-line backticked commands AND each exits 0
#   1  at least one is not, or does not
#   2  the HARNESS could not run
#
# Tree under test: $YF_TREE (set by redcheck.sh; defaults to the plan's execution worktree).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"

SPEC="${YF_TREE}/skills/yf-plan/spec/agents.md"
[ -f "${SPEC}" ] || { echo "ctl-165: HARNESS — no spec at ${SPEC}" >&2; exit 2; }

REQS="REQ-AGENT-049 REQ-AGENT-043 REQ-AGENT-045"
failed=0
checked=0

for req in ${REQS}; do
  line="$(awk -v r="^${req}:" '
    $0 ~ r        { inreq = 1; next }
    inreq && /^Verification:/ { print; exit }
    inreq && /^REQ-/ { exit }
  ' "${SPEC}")"

  if [ -z "${line}" ]; then
    echo "ctl-165: HARNESS — ${req} has no Verification: line in the spec" >&2
    exit 2
  fi
  checked=$((checked + 1))

  # SHAPE: the whole value must be ONE backticked span — `Verification: ` + backtick + … + backtick
  body="${line#Verification: }"
  case "${body}" in
    '`'*'`') : ;;
    *)
      echo "ctl-165: ${req} FAIL — the Verification: line is not a whole-line backticked command." >&2
      echo "ctl-165:   ${line}" >&2
      failed=$((failed + 1)); continue ;;
  esac
  cmd="${body#\`}"; cmd="${cmd%\`}"
  case "${cmd}" in
    *'`'*)
      echo "ctl-165: ${req} FAIL — the value contains an inner backtick; it is prose with code" >&2
      echo "ctl-165:   spans, not a single command: ${line}" >&2
      failed=$((failed + 1)); continue ;;
  esac

  # EXECUTION: from the TREE ROOT, which is what the line's relative paths assume.
  if (cd "${YF_TREE}" && env -u VIRTUAL_ENV bash -c "${cmd}") >/dev/null 2>&1; then
    echo "ctl-165: ${req} ok   — whole-line command, exits 0"
  else
    rc=$?
    echo "ctl-165: ${req} FAIL — the command is well-formed but exits ${rc}:" >&2
    echo "ctl-165:   ${cmd}" >&2
    failed=$((failed + 1))
  fi
done

# A vacuity guard, per Issue 3.3's own never-a-count rule applied to this fixture: the set of
# REQs checked must be the declared set, and an empty check set is a FAILURE.
if [ "${checked}" -ne 3 ]; then
  echo "ctl-165: HARNESS — checked ${checked} REQ(s), expected 3 (${REQS})" >&2
  exit 2
fi

[ "${failed}" -eq 0 ] && echo "ctl-165: all 3 Verification: lines are executable and green"
[ "${failed}" -eq 0 ] && exit 0
exit 1
