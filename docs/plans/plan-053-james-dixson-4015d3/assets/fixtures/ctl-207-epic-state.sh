#!/usr/bin/env bash
# ctl-207-epic-state — the six-valued `epic_state` and `clear-epic` (#207).
#
# A THIN WRAPPER, and it exists for a mechanical reason (pass-4 C53): `redcheck.sh` runs a
# fixture with `bash "$fx"`, so a bare pytest invocation is not runnable by the harness. The
# assertions live in `skills/yf-plan/scripts/test_epic_ref_audit.py`, which is also SC8/SC8b/
# SC9's verification command — one implementation, two consumers, so they cannot disagree.
#
# WHAT THE UNDERLYING SUITE ASSERTS (plan-053 additions):
#   epic_state ∈ {none, stale, present, complete, foreign, unknown}, each on its own fixture;
#   `found` and `epic_resolves` UNCHANGED for back-compat;
#   `epic_status` / `epic_plan_dir` surfaced so a caller can report WHY, not merely THAT;
#   the gates-only-bead-dict false negative (D-11) classifies `unknown`, never `stale`;
#   `clear-epic` removes BOTH dual-written surfaces, is idempotent, refuses on `present` and
#   `unknown` without --force, keeps the `intake:` history bullet, appends `pointer cleared`,
#   and reports `metadata_fallback_remains`.
#
# Tree under test: $YF_TREE (set by redcheck.sh).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
SUITE="${YF_TREE}/skills/yf-plan/scripts/test_epic_ref_audit.py"

[ -f "${SUITE}" ] || { echo "ctl-207-epic-state: HARNESS — no suite at ${SUITE}" >&2; exit 2; }

out="$(cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${SUITE}" 2>&1)"; rc=$?

# Distinguish a real test failure (1) from the suite being unable to RUN (2). A collection
# error, a missing interpreter or an unresolvable dependency says nothing about `epic_state`
# in either direction, and reporting it as a failure would manufacture a red.
if [ "${rc}" -ne 0 ] && printf '%s' "${out}" | grep -qE 'ERROR collecting|ModuleNotFoundError|No such file or directory|error: Failed to spawn'; then
  echo "ctl-207-epic-state: HARNESS — the suite could not run:" >&2
  printf '%s\n' "${out}" | tail -20 | sed 's/^/ctl-207-epic-state:   /' >&2
  exit 2
fi

if [ "${rc}" -ne 0 ]; then
  echo "ctl-207-epic-state: the epic-state / clear-epic suite FAILED:" >&2
  printf '%s\n' "${out}" | grep -E '^(FAILED|E  )' | sed 's/^/ctl-207-epic-state:   /' >&2
  printf '%s\n' "${out}" | tail -3 | sed 's/^/ctl-207-epic-state:   /' >&2
  exit 1
fi
echo "ctl-207-epic-state: all six epic_state values distinguished; clear-epic clears both surfaces"
