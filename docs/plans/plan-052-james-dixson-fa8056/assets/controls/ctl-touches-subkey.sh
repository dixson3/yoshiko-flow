#!/usr/bin/env bash
# ctl-touches-subkey (SC5b) — `- touches:` is a FIRST-CLASS field returned by plan_extract.
#
# REQ-DATA-071: each issue object carries a `touches` ARRAY, consumed like `depends_on` and
# `resolves_upstream` rather than left inside `detail`. An issue declaring no touches carries
# an EMPTY array, which is a valid value.
#
# The field is shipped by Issue 1.4; this control is built by 1.3, one issue EARLIER.
# THE UNCOMMISSIONED-INTERFACE RULE APPLIES: an absent field is EXIT 1 (a real negative),
# never the callee's exit 2.
#
# Exit: 0 the field is first-class and correctly populated · 1 real negative · 2 instrument
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
PLAN="$REPO/docs/plans/plan-052-james-dixson-fa8056"

RAW="$(uv run "$REPO/_shared/plan_extract.py" "$PLAN" --json 2>/dev/null || true)"
[ -n "$RAW" ] || { echo "INCONCLUSIVE: plan_extract produced no output" >&2; exit 2; }

printf '%s' "$RAW" | python3 -c '
import json, sys
try:
    docs = json.load(sys.stdin)
except Exception as e:
    print(f"INCONCLUSIVE: plan_extract output is not JSON: {e}", file=sys.stderr)
    raise SystemExit(2)
d = docs[0] if isinstance(docs, list) else docs
issues = d.get("issues") or []
if not issues:
    print("INCONCLUSIVE: plan_extract returned no issues", file=sys.stderr)
    raise SystemExit(2)

# (a) the field must EXIST on every issue object
missing = [i["id"] for i in issues if "touches" not in i]
if missing:
    print(f"FAIL: `touches` is not a first-class field — absent on {len(missing)} of "
          f"{len(issues)} issue object(s), e.g. {missing[:5]}", file=sys.stderr)
    print(f"      keys present: {sorted(issues[0].keys())}", file=sys.stderr)
    raise SystemExit(1)

# (b) it must be a LIST
bad = [i["id"] for i in issues if not isinstance(i.get("touches"), list)]
if bad:
    print(f"FAIL: `touches` is not a list on: {bad[:5]}", file=sys.stderr)
    raise SystemExit(1)

# (c) it must be POPULATED where the source declares it — a field that is always empty is
#     a field in name only.
populated = [i for i in issues if i["touches"]]
if not populated:
    print("FAIL: `touches` is present but EMPTY on every issue — the sub-key is not parsed",
          file=sys.stderr)
    raise SystemExit(1)

# (d) the consumed sub-key must be EXCLUDED from `detail` (REQ-DATA-071, as for depends-on)
leaked = [i["id"] for i in issues if "- touches:" in (i.get("detail") or "")]
if leaked:
    print(f"FAIL: the consumed `- touches:` sub-key still leaks into `detail` on "
          f"{len(leaked)} issue(s), e.g. {leaked[:5]} — the same bytes must not be reachable "
          f"both as a structured field and as prose", file=sys.stderr)
    raise SystemExit(1)

n = sum(len(i["touches"]) for i in issues)
print(f"PASS: `touches` is first-class on all {len(issues)} issues "
      f"({len(populated)} populated, {n} paths), and is excluded from `detail`")
'
