#!/usr/bin/env bash
# gate-run.sh — the exit-code discipline wrapper for plan-048's capability gates.
#
# CONTRACT (plan-048 Issue 0.6a, SC10d):
#   0 = capability PRESENT
#   1 = capability ABSENT      <- the ONLY reason a gate may be red
#   2 = harness COULD NOT RUN  <- INCONCLUSIVE; never red
#
# Any exit code outside {0,1,2} is remapped to 2 with an explicit harness-failure
# message on stderr. The motivating case is bash's 127 (script missing / not
# executable): without this wrapper a gate whose script has not been written yet
# reports 127, which a naive `exit != 0` reading calls FAIL — manufacturing a
# blocker out of an absent harness.
#
# This is a WRAPPER, not a resolver change: no SPEC amendment is required.
#
# Usage:  bash .../gate-run.sh <gate-script> [args...]

set -u

if [ "$#" -lt 1 ]; then
  echo "gate-run.sh: HARNESS FAILURE — no gate script named (usage: gate-run.sh <script> [args...])" >&2
  exit 2
fi

script="$1"; shift

if [ ! -f "$script" ]; then
  echo "gate-run.sh: HARNESS FAILURE — gate script not found: ${script}" >&2
  echo "gate-run.sh: reporting INCONCLUSIVE (2); an absent harness is not an absent capability." >&2
  exit 2
fi

if [ ! -r "$script" ]; then
  echo "gate-run.sh: HARNESS FAILURE — gate script not readable: ${script}" >&2
  exit 2
fi

bash "$script" "$@"
rc=$?

case "$rc" in
  0|1|2)
    exit "$rc"
    ;;
  *)
    echo "gate-run.sh: HARNESS FAILURE — gate script '${script}' exited ${rc}, outside the declared {0,1,2} set." >&2
    if [ "$rc" -eq 127 ]; then
      echo "gate-run.sh: 127 is bash's command-not-found — a missing script or a missing tool, not an absent capability." >&2
    fi
    echo "gate-run.sh: remapping ${rc} -> 2 (INCONCLUSIVE)." >&2
    exit 2
    ;;
esac
