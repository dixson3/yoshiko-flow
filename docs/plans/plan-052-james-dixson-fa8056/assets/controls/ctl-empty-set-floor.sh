#!/usr/bin/env bash
# ctl-empty-set-floor (SC0c) — an EMPTY or UNREADABLE control set is INCONCLUSIVE, never green.
#
# Spiked at pass 3: with an empty set, `∅ == ∅ == ∅` satisfied closure, `verify-all` over an
# empty file exited 0, and `∅ ∪ ∅ ∪ ∅ == ∅` satisfied the partition — all three flagship
# criteria green while NOTHING was checked. This control asserts the floor that closes it.
#
# Exit: 0 all three verbs correctly return 2 · 1 any of them returns 0 or 1 · 2 instrument failure
set -uo pipefail

ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE="${ASSETS}/gate-run.sh"
[ -r "$GATE" ] || { echo "INCONCLUSIVE: dispatcher unreadable: $GATE" >&2; exit 2; }

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
: > "$tmp/empty.txt"                       # empty control set
UNREADABLE="$tmp/nonexistent-controls.txt" # unreadable control set

fail=0
check() { # label expected-exit CTL_TXT verb [arg]
  local label="$1" want="$2" ctl="$3"; shift 3
  local out rc
  out=$(CTL_TXT="$ctl" LEDGER="$tmp/ledger.tsv" bash "$GATE" "$@" 2>&1); rc=$?
  if [ "$rc" -ne "$want" ]; then
    echo "FAIL: $label — expected exit $want (INCONCLUSIVE), got $rc" >&2
    echo "      output: ${out:0:200}" >&2
    fail=1
  else
    echo "ok: $label -> exit $rc"
  fi
}

check "verify-all over an EMPTY set"        2 "$tmp/empty.txt" verify-all
check "verify-partition over an EMPTY set"  2 "$tmp/empty.txt" verify-partition
check "verify-set core over an EMPTY set"   2 "$tmp/empty.txt" verify-set core
check "verify-all over an UNREADABLE set"   2 "$UNREADABLE"    verify-all

exit $fail
