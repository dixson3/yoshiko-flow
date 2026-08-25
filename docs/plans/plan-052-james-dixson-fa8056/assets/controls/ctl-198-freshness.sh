#!/usr/bin/env bash
# ctl-198-freshness (SC17) — the review exit test READS THE FILE THE CHILD WROTE and PROVES
# IT IS FRESH. A stale prior pass file must NOT satisfy the exit test.
#
# The gap: a review cycle's exit test that merely asserts `reviews/pass-*.md` exists is
# satisfied by a file written by an EARLIER cycle. Under a REVISE loop that is the common
# case, not the exotic one — pass-1 is already on disk when cycle 2 runs, so cycle 2's exit
# test passes before its reviewer has written anything.
#
# What this control does NOT claim (D-6): that a gate makes a verdict unfabricatable. bd
# records NO RESOLVER IDENTITY — `--actor` and `BEADS_ACTOR` are both accepted and DISCARDED
# — so a resolution is a RECORD, not a guarantee. Freshness is checkable; authorship is not,
# and 6.1 must say so in red-team.md rather than imply otherwise.
#
# Shipped by Issue 6.1; this control is built by 6.0.
# Exit: 0 stale is rejected, fresh accepted, and the non-guarantee is stated · 1 · 2
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
RT="$REPO/skills/yf-plan/agents/red-team.md"

[ -r "$RT" ] || { echo "INCONCLUSIVE: red-team.md unreadable: $RT" >&2; exit 2; }

fail=0

# --- ARM 1: the exit test must be FRESHNESS-BEARING, not existence-bearing ---------
# A freshness test needs a reference point the child cannot pre-date: an mtime compared
# against a cycle start, a recorded cycle count, or a content hash captured before dispatch.
python3 - "$RT" <<'PYEOF'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
low = text.lower()
if "fresh" not in low:
    print("FAIL: red-team.md's exit test says nothing about FRESHNESS — a stale pass-N.md "
          "from an earlier cycle satisfies a bare existence check, which under a REVISE loop "
          "is the common case.", file=sys.stderr)
    raise SystemExit(1)
# The freshness claim must name a MECHANISM, not merely use the word.
mech = re.search(r"mtime|modified|newer than|hash|digest|cycle (?:start|marker)|"
                 r"captured before|pass-\(?N\+1\)?", low)
if not mech:
    print("FAIL: red-team.md mentions freshness but names no MECHANISM for establishing it "
          "(mtime vs a cycle start, a pre-dispatch content hash, or an explicit cycle "
          "marker). A word is not an exit code.", file=sys.stderr)
    raise SystemExit(1)
print(f"ok: red-team.md's exit test names a freshness mechanism ({mech.group(0)!r})")
PYEOF
[ $? -eq 0 ] || fail=1

# --- ARM 2: the non-guarantee must be STATED (D-6) --------------------------------
python3 - "$RT" <<'PYEOF'
import pathlib, sys
low = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").lower()
if not (("no resolver identity" in low or "records no resolver" in low
         or "resolver identity" in low)
        and ("record, not a guarantee" in low or "not a guarantee" in low)):
    print("FAIL: red-team.md does not state that a gate resolution carries NO RESOLVER "
          "IDENTITY and is a RECORD, NOT A GUARANTEE (D-6). bd accepts and DISCARDS both "
          "--actor and BEADS_ACTOR, so a document implying otherwise overstates what the "
          "mechanism proves.", file=sys.stderr)
    raise SystemExit(1)
print("ok: red-team.md states the resolution is a record, not a guarantee")
PYEOF
[ $? -eq 0 ] || fail=1

# --- ARM 3: EXECUTED — a stale file must not satisfy a freshness predicate ---------
# The predicate is exercised on a fixture so the claim is observed, not read.
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/reviews"
printf '# pass-1\n\nVerdict: REVISE\n' > "$tmp/reviews/pass-1.md"
# Backdate it well before the cycle marker.
touch -t 202601010000 "$tmp/reviews/pass-1.md"
MARKER="$tmp/.cycle-start"; touch "$MARKER"

is_fresh() { # <reviews-dir> <marker> -> 0 if some pass file is NEWER than the marker
  local newest
  newest=$(find "$1" -name 'pass-*.md' -newer "$2" -print -quit 2>/dev/null)
  [ -n "$newest" ]
}

if is_fresh "$tmp/reviews" "$MARKER"; then
  echo "FAIL: a backdated prior pass file was judged FRESH" >&2
  fail=1
else
  echo "ok: a stale prior pass file is NOT fresh"
fi
sleep 1
printf '# pass-2\n\nVerdict: APPROVE\n' > "$tmp/reviews/pass-2.md"
if is_fresh "$tmp/reviews" "$MARKER"; then
  echo "ok: a file written after the cycle marker IS fresh"
else
  echo "FAIL: a freshly written pass file was judged stale — the predicate always says no" >&2
  fail=1
fi

[ "$fail" -eq 0 ] || exit 1
echo "PASS: the exit test is freshness-bearing, the non-guarantee is stated, and the "
echo "      predicate discriminates stale from fresh"
