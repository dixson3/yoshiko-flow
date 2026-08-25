#!/usr/bin/env bash
# ctl-196-enum (SC16) — `prevention_formula` is ENUM-CHECKED; an unknown name is REJECTED.
#
# `prevention` stays PROSE. The split is the point: a retrospective's prevention narrative is
# a human judgement and mechanizing it would produce fake entries, but a FORMULA NAME is an
# identifier with a closed domain — `bd formula list` — so an unchecked one is a typo that
# silently prevents nothing. This is the smallest slice of #196 that has an exit code.
#
# Both directions are asserted: a KNOWN name is accepted and an UNKNOWN one is REJECTED. A
# checker that rejects everything passes a one-sided test while being useless.
#
# Shipped by Issue 5.3; this control is built by 5.0.
# UNCOMMISSIONED-INTERFACE RULE: an absent checker is EXIT 1 (a real negative), never 2.
# Exit: 0 the enum discriminates both ways · 1 a real negative · 2 instrument failure
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
RF="$REPO/skills/yf-plan/scripts/retrospective_fields.py"

command -v bd >/dev/null || { echo "INCONCLUSIVE: bd not on PATH" >&2; exit 2; }

if [ ! -r "$RF" ]; then
  echo "FAIL: the prevention_formula checker does not exist: $RF" >&2
  echo "      The uncommissioned-interface rule maps this to a REAL NEGATIVE (exit 1)." >&2
  exit 1
fi

# A name that really is in the closed domain, read from bd rather than hard-coded.
KNOWN="$(bd formula list 2>/dev/null | sed -n 's/^  \([a-z][a-z0-9-]*\) .*/\1/p' | head -1)"
[ -n "$KNOWN" ] || { echo "INCONCLUSIVE: bd formula list returned no formula names" >&2; exit 2; }
UNKNOWN="definitely-not-a-formula-xyzzy"

check() { # <formula-name> -> exit code of the checker
  uv run "$RF" --check-formula "$1" >/dev/null 2>&1; echo $?
}

RC_KNOWN=$(check "$KNOWN")
RC_UNKNOWN=$(check "$UNKNOWN")

fail=0
if [ "$RC_KNOWN" -ne 0 ]; then
  echo "FAIL: the KNOWN formula '$KNOWN' was rejected (exit $RC_KNOWN) — a checker that" >&2
  echo "      rejects everything passes a one-sided test while being useless" >&2
  fail=1
else
  echo "ok: known formula '$KNOWN' accepted"
fi
if [ "$RC_UNKNOWN" -eq 0 ]; then
  echo "FAIL: the UNKNOWN formula '$UNKNOWN' was ACCEPTED — the field is not enum-checked" >&2
  fail=1
elif [ "$RC_UNKNOWN" -eq 2 ]; then
  echo "FAIL: rejecting an unknown formula returned 2 (INCONCLUSIVE), not 1. A rejection is" >&2
  echo "      a real negative; INCONCLUSIVE would mean the checker could not run." >&2
  fail=1
else
  echo "ok: unknown formula '$UNKNOWN' rejected (exit $RC_UNKNOWN)"
fi

# `prevention` must remain PROSE — an enum there would force fake entries.
if uv run "$RF" --help 2>&1 | grep -qE '(^|[^_-])--check-prevention([^-]|$)'; then
  echo "FAIL: 'prevention' itself is being checked; it must remain prose" >&2
  fail=1
fi

[ "$fail" -eq 0 ] || exit 1
echo "PASS: prevention_formula is enum-checked both ways; prevention remains prose"
