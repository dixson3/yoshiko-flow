#!/usr/bin/env bash
# plan-052 control dispatcher.
#
# Exit vocabulary (three-valued, REQ-DATA-070):
#   0  PASS          — the assertion holds
#   1  FAIL          — a REAL NEGATIVE: the assertion is false
#   2  INCONCLUSIVE  — the instrument could not run
#
# Subcommands:
#   run <ctl-id>          run one control, append its observation to the ledger
#   verify-all            every id in the control set has a NON-ZERO recorded observation
#   verify-set <set>      every id in <set> has a recorded observation with EXIT 1
#   verify-partition      core u ext u land == all
#   self-test-broken      run the dispatcher against a deliberately broken fixture and
#                         return what it returned (SC3 expects a real negative: exit 1)
#
# Environment:
#   CTL_TXT   override the controls file (default: <assets>/controls.txt)
#   LEDGER    override the RED-observation ledger (default: <assets>/red-observations.tsv)
#
# Every control is invoked as `bash "$ctl"` — never `uv run`, never a bare exec — so no
# control depends on an exec bit.

set -uo pipefail

ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTL_DIR="${ASSETS}/controls"
CTL_TXT="${CTL_TXT:-${ASSETS}/controls.txt}"
LEDGER="${LEDGER:-${ASSETS}/red-observations.tsv}"

die_inconclusive() { echo "INCONCLUSIVE: $*" >&2; exit 2; }

# --- control set ------------------------------------------------------------
# Reads CTL_TXT into two parallel arrays. Applies the NON-EMPTINESS FLOOR:
# an empty or unreadable control set is INCONCLUSIVE (exit 2), NEVER 0.
CTL_IDS=(); CTL_SETS=()
load_controls() {
  [ -r "$CTL_TXT" ] || die_inconclusive "control set unreadable: $CTL_TXT"
  local id set_
  while IFS=$'\t' read -r id set_; do
    [ -z "${id:-}" ] && continue
    case "$id" in \#*) continue ;; esac
    CTL_IDS+=("$id"); CTL_SETS+=("${set_:-orphan}")
  done < "$CTL_TXT"
  [ "${#CTL_IDS[@]}" -gt 0 ] || die_inconclusive "control set is EMPTY: $CTL_TXT"
}

# --- ledger -----------------------------------------------------------------
record() { # id exit
  mkdir -p "$(dirname "$LEDGER")"
  [ -s "$LEDGER" ] || printf 'timestamp\tctl_id\texit\n' > "$LEDGER"
  printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" >> "$LEDGER"
}

# has_observation <id> <predicate>   predicate: "one" (exit==1) | "nonzero" (exit!=0)
has_observation() {
  local id="$1" pred="$2"
  [ -r "$LEDGER" ] || return 1
  awk -F'\t' -v id="$id" -v pred="$pred" '
    $2 == id {
      if (pred == "one"     && $3 == "1") { found = 1 }
      if (pred == "nonzero" && $3 != "0" && $3 != "exit") { found = 1 }
    }
    END { exit(found ? 0 : 1) }
  ' "$LEDGER"
}

# --- subcommands ------------------------------------------------------------
cmd_run() {
  local id="${1:-}"
  [ -n "$id" ] || die_inconclusive "run: missing <ctl-id>"
  local ctl="${CTL_DIR}/${id}.sh"
  # A MISSING declared artifact is exit 1 (a real negative), not INCONCLUSIVE.
  if [ ! -f "$ctl" ]; then
    echo "FAIL: control not built: $ctl" >&2
    record "$id" 1
    return 1
  fi
  bash "$ctl"
  local rc=$?
  record "$id" "$rc"
  return $rc
}

cmd_verify_set() {
  local want="${1:-}"
  [ -n "$want" ] || die_inconclusive "verify-set: missing <set>"
  load_controls
  local i n=0 missing=0
  for i in "${!CTL_IDS[@]}"; do
    [ "${CTL_SETS[$i]}" = "$want" ] || continue
    n=$((n+1))
    if ! has_observation "${CTL_IDS[$i]}" one; then
      echo "FAIL: no recorded RED observation with EXIT 1 for ${CTL_IDS[$i]} (set=$want)" >&2
      missing=$((missing+1))
    fi
  done
  # An empty SELECTION is the non-emptiness floor too: nothing was checked.
  [ "$n" -gt 0 ] || die_inconclusive "verify-set: set '$want' selected 0 controls"
  [ "$missing" -eq 0 ] || return 1
  echo "PASS: $n control(s) in set '$want' each have a recorded RED observation (exit 1)"
  return 0
}

cmd_verify_all() {
  load_controls
  local bad=0 i
  # (a) every id in the generated file has a NON-ZERO recorded observation
  for i in "${!CTL_IDS[@]}"; do
    if ! has_observation "${CTL_IDS[$i]}" nonzero; then
      echo "FAIL: no recorded RED observation (non-zero exit) for ${CTL_IDS[$i]}" >&2
      bad=$((bad+1))
    fi
  done
  # (b) every ASSERTED control id is present in the generated file
  local asserted
  asserted=$(asserted_ids) || die_inconclusive "verify-all: cannot read asserted ids"
  local a
  for a in $asserted; do
    if ! printf '%s\n' "${CTL_IDS[@]}" | grep -qx "$a"; then
      echo "FAIL: asserted control id absent from generated set: $a" >&2
      bad=$((bad+1))
    fi
  done
  [ "$bad" -eq 0 ] || return 1
  echo "PASS: ${#CTL_IDS[@]} control(s) each observed RED; every asserted id is present"
  return 0
}

cmd_verify_partition() {
  load_controls
  local i bad=0 ncore=0 next=0 nland=0
  for i in "${!CTL_IDS[@]}"; do
    case "${CTL_SETS[$i]}" in
      core) ncore=$((ncore+1)) ;;
      ext)  next=$((next+1)) ;;
      land) nland=$((nland+1)) ;;
      *) echo "FAIL: ${CTL_IDS[$i]} is in neither core, ext nor land (set=${CTL_SETS[$i]})" >&2
         bad=$((bad+1)) ;;
    esac
  done
  [ "$bad" -eq 0 ] || return 1
  echo "PASS: core($ncore) u ext($next) u land($nland) == all(${#CTL_IDS[@]})"
  return 0
}

# The asserted set: control ids named in plan.md Success Criteria Verification cells.
asserted_ids() {
  local plan="${ASSETS}/../plan.md"
  [ -r "$plan" ] || return 1
  uv run "${ASSETS}/gen-controls.py" --asserted-only --plan "$plan" 2>/dev/null
}

cmd_self_test_broken() {
  # Re-spike: construct a DELIBERATELY BROKEN control in a scratch tree and run it
  # through this very dispatcher. Return what the dispatcher returned, so SC3's
  # `-> exit 1` asserts a REAL NEGATIVE rather than an INCONCLUSIVE or a silent green.
  local tmp; tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  mkdir -p "$tmp/controls"
  printf '#!/usr/bin/env bash\necho "deliberately broken fixture" >&2\nexit 1\n' \
    > "$tmp/controls/ctl-deliberately-broken.sh"
  printf 'ctl-deliberately-broken\tcore\n' > "$tmp/controls.txt"
  # Point the dispatcher at the scratch tree; keep the real ledger untouched.
  CTL_TXT="$tmp/controls.txt" LEDGER="$tmp/ledger.tsv" CTL_DIR="$tmp/controls" \
    _run_in "$tmp" ctl-deliberately-broken
  local rc=$?
  echo "self-test-broken: dispatcher returned $rc on the broken fixture (1 = real negative)"
  return $rc
}

# Internal: run a control out of an alternate control dir, honouring the same contract.
_run_in() {
  local root="$1" id="$2"
  local ctl="${root}/controls/${id}.sh"
  if [ ! -f "$ctl" ]; then
    echo "FAIL: control not built: $ctl" >&2
    return 1
  fi
  bash "$ctl"
  local rc=$?
  LEDGER="${root}/ledger.tsv" record "$id" "$rc"
  return $rc
}

usage() {
  sed -n '2,25p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

case "${1:-}" in
  run)              shift; cmd_run "$@" ;;
  verify-all)       shift; cmd_verify_all "$@" ;;
  verify-set)       shift; cmd_verify_set "$@" ;;
  verify-partition) shift; cmd_verify_partition "$@" ;;
  self-test-broken) shift; cmd_self_test_broken "$@" ;;
  -h|--help|help|"") usage; exit 0 ;;
  *) echo "INCONCLUSIVE: unknown subcommand: $1" >&2; usage >&2; exit 2 ;;
esac
