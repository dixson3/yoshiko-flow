#!/usr/bin/env bash
# gate-run.sh — plan-050 Issue 0.2 (adopted verbatim from plan-049 Issue 0.7). The 0/1/2 exit-discipline wrapper for a capability gate.
#
# WHY THIS EXISTS. A capability gate's `Test:` is judged by its EXIT CODE alone, under a
# three-value contract:
#
#   0  the capability is PRESENT   -> the gate opens
#   1  the capability is ABSENT    -> the gate is RED (the only legal reason to be red)
#   2  the HARNESS could not run   -> the gate is UNRESOLVED (neither open nor red)
#
# Every other exit code is a harness failure wearing a capability failure's clothes. The
# specific one that motivated this wrapper is bash's **127**, returned when the script named
# on the command line does not exist. Without the wrapper, a never-authored gate script exits
# 127; 127 is not 1, so the gate does not go red; it is not 0, so the gate does not open — it
# sits UNRESOLVED. The blocked work then never runs and the whole thing reads as a STALL
# rather than as the missing capability it actually is. Mapping the unknown codes to an
# EXPLICIT 2 with a stated reason turns a silent stall into a legible harness failure.
#
# 126 (found but not executable) and 128+N (killed by signal N — 130 SIGINT, 137 SIGKILL,
# 139 SIGSEGV) are the same class and are mapped the same way.
#
# USAGE
#   bash gate-run.sh <script> [args...]
# EXIT
#   0 | 1 | 2   -- and NOTHING else. That is the entire contract.

set -uo pipefail

if [ "$#" -lt 1 ]; then
  echo "gate-run.sh: HARNESS FAILURE — no gate script named on the command line." >&2
  echo "gate-run.sh: usage: bash gate-run.sh <script> [args...]" >&2
  exit 2
fi

target="$1"; shift

if [ ! -e "$target" ]; then
  echo "gate-run.sh: HARNESS FAILURE — gate script does not exist: ${target}" >&2
  echo "gate-run.sh: this is NOT the capability being absent. It is a gate whose test was" >&2
  echo "gate-run.sh: never authored. Exiting 2 (UNRESOLVED) rather than letting bash's 127" >&2
  echo "gate-run.sh: read as a stall. Author the script, then re-run." >&2
  exit 2
fi

bash "$target" "$@"
rc=$?

case "$rc" in
  0) exit 0 ;;
  1) exit 1 ;;
  2)
    echo "gate-run.sh: the gate script reported HARNESS FAILURE (exit 2) — gate UNRESOLVED." >&2
    exit 2 ;;
  126)
    echo "gate-run.sh: HARNESS FAILURE — ${target} exists but is not executable (126)." >&2
    exit 2 ;;
  127)
    echo "gate-run.sh: HARNESS FAILURE — a command INSIDE ${target} was not found (127)." >&2
    echo "gate-run.sh: a missing dependency is not an absent capability. Gate UNRESOLVED." >&2
    exit 2 ;;
  *)
    if [ "$rc" -gt 128 ] 2>/dev/null; then
      echo "gate-run.sh: HARNESS FAILURE — ${target} was killed by signal $((rc - 128)) (exit ${rc})." >&2
    else
      echo "gate-run.sh: HARNESS FAILURE — ${target} exited ${rc}, outside the 0/1/2 contract." >&2
    fi
    echo "gate-run.sh: mapping to 2 (UNRESOLVED). Repair the harness; do not read this either way." >&2
    exit 2 ;;
esac
