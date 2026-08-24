#!/usr/bin/env bash
# ctl-ownership-inconclusive (SC18) — `ownership-report` returns INCONCLUSIVE below 80% path
# coverage, the floor is a NUMBER, and it never reports "orthogonal" on no input.
#
# The floor is stated numerically because "sufficient coverage" is not a checkable claim. The
# failure this closes is the silent-green class in its ownership form: with no declared paths
# the pairwise measurement has an empty denominator, and an implementation that reports
# "orthogonal" there is reporting a conclusion drawn from nothing.
#
# The verb is shipped by Issue 1.5; this control is built by 1.3, two issues EARLIER.
# THE UNCOMMISSIONED-INTERFACE RULE APPLIES: an absent verb (argparse exit 2, "invalid
# choice") is mapped to EXIT 1 — a real negative — and never allowed to escape as exit 2.
#
# Exit: 0 the floor holds and no false "orthogonal" · 1 real negative · 2 instrument failure
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
PM="$REPO/skills/yf-plan/scripts/plan_manager.py"
FLOOR=80

[ -r "$PM" ] || { echo "INCONCLUSIVE: plan_manager.py unreadable: $PM" >&2; exit 2; }

# --- Is the verb commissioned at all? -------------------------------------------
HELP="$(uv run "$PM" --help 2>&1 || true)"
if ! printf '%s' "$HELP" | grep -q 'ownership-report'; then
  echo "FAIL: plan_manager.py exposes no 'ownership-report' verb." >&2
  echo "      The uncommissioned-interface rule maps this to a REAL NEGATIVE (exit 1):" >&2
  echo "      the verb is absent, which is a different claim from the instrument failing." >&2
  exit 1
fi

# --- The floor must be observable on a LOW-COVERAGE fixture ---------------------
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mk() { # <dir> <n-issues> <n-with-touches>
  mkdir -p "$1"
  { echo "# Plan: ownership fixture"; echo; echo "## Epics"; echo "### Epic 1: fixture"; } > "$1/plan.md"
  local i
  for i in $(seq 1 "$2"); do
    echo "- Issue 1.$i: issue $i" >> "$1/plan.md"
    [ "$i" -le "$3" ] && echo "  - touches: \`src/f$i.py\`" >> "$1/plan.md"
  done
  { echo; echo "## Gates"; echo "### Start Gate (mandatory)"; echo "- Type: human"; } >> "$1/plan.md"
}
mk "$tmp/low"   10 3    # 30% coverage — below the floor
mk "$tmp/empty" 10 0    # 0% coverage  — the "no input" case
mk "$tmp/high"  10 10   # 100% coverage — above the floor

run() { uv run "$PM" ownership-report "$1" --json 2>/dev/null || true; }

fail=0
assert_inconclusive() { # <label> <dir>
  local out; out="$(run "$2")"
  if [ -z "$out" ]; then
    echo "FAIL: $1 — ownership-report produced no output" >&2; fail=1; return
  fi
  printf '%s' "$out" | python3 -c '
import json, sys
label = sys.argv[1]
try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"FAIL: {label} — output is not JSON: {e}", file=sys.stderr); raise SystemExit(1)
v = str(d.get("verdict") or d.get("status") or "").upper()
if v != "INCONCLUSIVE":
    print(f"FAIL: {label} — verdict is {v!r}, expected INCONCLUSIVE", file=sys.stderr)
    raise SystemExit(1)
blob = json.dumps(d).lower()
if "orthogonal" in blob:
    print(f"FAIL: {label} — reported 'orthogonal' on input below the floor", file=sys.stderr)
    raise SystemExit(1)
floor = d.get("coverage_floor")
if floor is None or float(floor) != float(sys.argv[2]):
    print(f"FAIL: {label} — coverage_floor is {floor!r}, expected the NUMBER {sys.argv[2]}",
          file=sys.stderr)
    raise SystemExit(1)
print(f"ok: {label} -> INCONCLUSIVE, floor={floor}, no 'orthogonal'")
' "$1" "$FLOOR" || fail=1
}

assert_inconclusive "30% coverage" "$tmp/low"
assert_inconclusive "0% coverage (no input)" "$tmp/empty"

# Above the floor it must NOT be INCONCLUSIVE — a floor that always fires is not a floor.
out="$(run "$tmp/high")"
printf '%s' "$out" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"FAIL: 100% coverage — output is not JSON: {e}", file=sys.stderr); raise SystemExit(1)
v = str(d.get("verdict") or d.get("status") or "").upper()
if v == "INCONCLUSIVE":
    print("FAIL: 100% coverage still returned INCONCLUSIVE — the floor always fires",
          file=sys.stderr)
    raise SystemExit(1)
if d.get("report_only") is not True:
    print(f"FAIL: report_only is {d.get('report_only')!r}, expected True (R1)", file=sys.stderr)
    raise SystemExit(1)
print("ok: 100% coverage -> not INCONCLUSIVE, report_only=true")
' || fail=1

[ "$fail" -eq 0 ] || exit 1
echo "PASS: the ${FLOOR}% floor is a number, fires below it, and never reports 'orthogonal' on no input"
