#!/usr/bin/env bash
# ctl-cv-rows (SC19) — CHANGE-VALIDATION.md carries recipe rows for EVERYTHING this plan ships.
#
# A test that exists but is in no recipe row runs exactly once — the day it is written. The
# manifest is what makes it run again, so "shipped a test" and "the tree is validated" are
# different claims and only the second one is what SC19 asserts.
#
# The required set is DERIVED from the plan's own `touches:` declarations, not hand-listed:
# every `skills/**/test_*.py` or `_shared/test_*.py` this plan creates must appear in §1's
# fast tier, and the plan's own gate harness must appear too. A hand-listed set would drift
# from the plan the moment an issue's touches changed — which is the defect SC0 exists for,
# one document over.
#
# Exit: 0 every shipped artifact has a row · 1 a real negative · 2 the instrument could not run
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
CV="$REPO/CHANGE-VALIDATION.md"
PLAN="$ASSETS/../plan.md"

[ -r "$PLAN" ] || { echo "INCONCLUSIVE: plan.md unreadable" >&2; exit 2; }
if [ ! -f "$CV" ]; then
  echo "FAIL: CHANGE-VALIDATION.md is absent: $CV" >&2; exit 1
fi

python3 - "$CV" "$PLAN" <<'PYEOF'
import pathlib, re, sys
cv = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
plan = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")

if not re.search(r"^approved:\s*yes\s*$", cv, re.M):
    print("INCONCLUSIVE: CHANGE-VALIDATION.md §0 is not `approved: yes`", file=sys.stderr)
    raise SystemExit(2)

# The plan's declared paths, from its own `- touches:` sub-keys.
touched = set()
body, inside = [], False
for ln in plan.splitlines():
    if ln.startswith("## "):
        inside = ln.strip() == "## Epics"
        continue
    if inside:
        body.append(ln)
for ln in body:
    if ln.strip().startswith("- touches:"):
        touched |= set(re.findall(r"`([^`\s]+/[^`\s]+)`", ln))

# What must have a recipe row:
#   (a) every test file the plan ships
#   (b) the plan's own control harness (its gate is a runnable command)
required = {p for p in touched if re.search(r"(^|/)test_[a-z0-9_]+\.py$", p)}
harness = "docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh"
required.add(harness)

missing = sorted(p for p in required if p not in cv)
if missing:
    print(f"FAIL: {len(missing)} artifact(s) this plan ships have NO CHANGE-VALIDATION row:",
          file=sys.stderr)
    for p in missing:
        print(f"  - {p}", file=sys.stderr)
    raise SystemExit(1)

# A row must sit in the FAST tier to fire on edit; a full-tier-only row never runs on-edit.
fast = cv.split("### fast", 1)[-1].split("### full", 1)[0] if "### fast" in cv else ""
not_fast = sorted(p for p in required if p not in fast)
if not_fast:
    print(f"FAIL: {len(not_fast)} artifact(s) appear only outside the FAST tier, so they "
          f"never fire on edit:", file=sys.stderr)
    for p in not_fast:
        print(f"  - {p}", file=sys.stderr)
    raise SystemExit(1)

print(f"PASS: all {len(required)} artifact(s) this plan ships carry a FAST-tier recipe row")
PYEOF
