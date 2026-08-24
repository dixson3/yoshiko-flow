#!/usr/bin/env bash
# ctl-touches-coverage (SC5c) — this plan's own issues declare `touches:` at 100%.
#
# NO SLACK, deliberately: the figure is 100% today, and a budget cannot detect the
# degradation it exists to prevent. A 95% floor on 31 issues permits one silent regression
# and reports green.
#
# GREEN on this plan by construction, so RED comes from a PINNED FIXTURE carrying a
# `touches:`-less issue.
#   CTL_RED=1  measure the fixture alone and return its verdict (a real negative, exit 1)
#
# The measurement reads the SOURCE (plan.md), not plan_extract's `touches` field, so this
# control is INDEPENDENT of ctl-touches-subkey: a bug in the extractor cannot make coverage
# read as green, and the two controls fail for different reasons.
#
# Exit: 0 coverage is 100% and the fixture is a real negative · 1 real negative · 2 instrument
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"

coverage() { # <plan.md> -> "declared total"; exit 2 if unreadable
  python3 - "$1" <<'PYEOF'
import pathlib, re, sys
p = pathlib.Path(sys.argv[1])
if not p.is_file():
    raise SystemExit(2)
text = p.read_text(encoding="utf-8")
body, inside = [], False
for ln in text.splitlines():
    if ln.startswith("## "):
        inside = ln.strip() == "## Epics"
        continue
    if inside:
        body.append(ln)
issue_re = re.compile(r"^- Issue (\d+\.\d+[a-z]?): ")
total, declared, cur = 0, 0, None
seen = set()
for ln in body:
    m = issue_re.match(ln)
    if m:
        cur = m.group(1)
        total += 1
        continue
    if cur and ln.strip().startswith("- touches:") and cur not in seen:
        seen.add(cur)
        declared += 1
if total == 0:
    raise SystemExit(2)
print(declared, total)
PYEOF
}

report() { # <label> <plan.md>
  local out; out=$(coverage "$2") || return 2
  local d t; read -r d t <<<"$out"
  if [ "$d" -eq "$t" ]; then
    echo "ok: $1 — $d/$t issues declare touches: (100%)"
    return 0
  fi
  echo "FAIL: $1 — only $d of $t issues declare touches: ($(python3 -c "print(round(100*$d/$t,1))")%); the floor is 100%, with NO slack" >&2
  return 1
}

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
cat > "$tmp/plan.md" <<'FIX'
# Plan: pinned touches-less fixture

## Epics
### Epic 1: fixture
- Issue 1.1: declares its paths
  - touches: `a/b.py`
- Issue 1.2: declares NOTHING — this is the degradation the 100% floor exists to catch
  - depends-on: 1.1
- Issue 1.3: declares its paths
  - touches: `c/d.py`

## Gates
### Start Gate (mandatory)
- Type: human
FIX

if [ "${CTL_RED:-0}" = "1" ]; then
  report "pinned touches-less fixture" "$tmp/plan.md"; rc=$?
  echo "CTL_RED: measurement over the pinned fixture returned $rc (1 = real negative)"
  exit $rc
fi

report "pinned touches-less fixture" "$tmp/plan.md" 2>/dev/null; neg=$?
if [ "$neg" -ne 1 ]; then
  echo "FAIL: the pinned fixture did NOT produce a real negative (got $neg)" >&2
  exit 1
fi
echo "ok: pinned touches-less fixture -> exit 1 (a real negative)"

report "plan-052" "$REPO/docs/plans/plan-052-james-dixson-fa8056/plan.md"; live=$?
[ "$live" -eq 2 ] && exit 2
[ "$live" -eq 0 ] || exit 1
echo "PASS: touches: coverage is 100% with no slack"
