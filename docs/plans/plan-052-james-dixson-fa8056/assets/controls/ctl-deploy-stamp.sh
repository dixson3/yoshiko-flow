#!/usr/bin/env bash
# ctl-deploy-stamp (SC24) — the DEPLOYED tree matches source and the STAMP matches HEAD,
# verified AFTER the final commit and a rebuild.
#
# THIS CONTROL'S RED MUST COME FROM A PINNED FIXTURE, NEVER FROM LIVE MACHINE STATE. It is
# RED today only because the installed stamp HAPPENS to be stale — and a `yf self install`
# run for any unrelated reason before this issue would silently reverse that, turning the RED
# into a green nobody asked for. A control whose colour depends on when someone last ran an
# install is measuring the machine, not the code.
#
#   CTL_RED=1  compare a pinned STALE fixture pair and return its verdict (exit 1)
#   (unset)    the fixture must be a real negative AND the live machine must agree
#
# Deploy is Issue 7.5 and happens AFTER the final commit — R6/R7: this plan edits the skill
# it executes under, and `plan_manager.py` is re-invoked per call, so a mid-execution deploy
# runs NEW scripts against OLD prose.
#
# Exit: 0 fixture is a real negative and live state agrees · 1 real negative · 2 instrument
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"

# predicate <stamp> <head> -> 0 when the stamp matches HEAD, 1 when it does not
predicate() {
  local stamp="$1" head="$2"
  # A `-dirty` suffix just means uncommitted files; the HASH is what must match.
  stamp="${stamp%-dirty}"
  if [ -z "$stamp" ] || [ -z "$head" ]; then return 2; fi
  if [ "${head#"$stamp"}" != "$head" ] || [ "${stamp#"$head"}" != "$stamp" ]; then
    echo "ok: stamp $stamp matches HEAD $head"
    return 0
  fi
  echo "FAIL: stamp $stamp does NOT match HEAD $head" >&2
  return 1
}

# --- pinned STALE fixture: two hashes that are known not to match ------------------
FIX_STAMP="0000000deadbee"
FIX_HEAD="1111111cafef00"

if [ "${CTL_RED:-0}" = "1" ]; then
  predicate "$FIX_STAMP" "$FIX_HEAD"; rc=$?
  echo "CTL_RED: predicate over the pinned stale fixture returned $rc (1 = real negative)"
  exit $rc
fi

predicate "$FIX_STAMP" "$FIX_HEAD" 2>/dev/null; neg=$?
if [ "$neg" -ne 1 ]; then
  echo "FAIL: the pinned stale fixture did NOT produce a real negative (got $neg)" >&2
  exit 1
fi
echo "ok: pinned stale fixture -> exit 1 (a real negative)"

# --- live machine ------------------------------------------------------------------
command -v yf >/dev/null || { echo "INCONCLUSIVE: yf not on PATH" >&2; exit 2; }
HEAD="$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || true)"
[ -n "$HEAD" ] || { echo "INCONCLUSIVE: cannot resolve HEAD" >&2; exit 2; }
VER="$(yf --version 2>/dev/null || true)"
[ -n "$VER" ] || { echo "INCONCLUSIVE: yf --version produced nothing" >&2; exit 2; }
STAMP="$(printf '%s' "$VER" | grep -oE '[0-9a-f]{7,40}(-dirty)?' | head -1)"
[ -n "$STAMP" ] || { echo "INCONCLUSIVE: no git hash in: $VER" >&2; exit 2; }

predicate "$STAMP" "$HEAD"; live=$?
[ "$live" -eq 2 ] && exit 2
[ "$live" -eq 0 ] || exit 1

# --- the deployed skill tree must match source ------------------------------------
SKILLS_SRC="$REPO/skills"
SKILLS_DEP="$HOME/.claude/skills"
[ -d "$SKILLS_DEP" ] || { echo "INCONCLUSIVE: no deployed skills tree at $SKILLS_DEP" >&2; exit 2; }
drift=0
for d in "$SKILLS_SRC"/*/; do
  name="$(basename "$d")"
  [ -d "$SKILLS_DEP/$name" ] || continue
  if ! diff -rq "$d" "$SKILLS_DEP/$name" >/dev/null 2>&1; then
    echo "FAIL: deployed skill '$name' differs from source" >&2
    drift=1
  fi
done
[ "$drift" -eq 0 ] || exit 1
echo "PASS: stamp matches HEAD ($HEAD) and the deployed tree matches source"
