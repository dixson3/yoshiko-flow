#!/usr/bin/env bash
# ctl-205-tombstone (SC11) — `closable` emits NO close proposal for an issue whose only
# closed mapped beads are HOIST TOMBSTONES.
#
# The follow-on hoist closes a bead locally with a reversible `bd close -r` tombstone
# PRECISELY BECAUSE the work moved upstream and is still open there. Counting that closure as
# evidence of completion inverts its meaning: REQ-BUP-052's per-bead signal reads a hoisted
# issue as fully discharged at the exact moment it became least discharged.
#
# The suppressed row must be ANNOTATED, NEVER DROPPED. A dropped row is indistinguishable
# from "no such issue" — the same silent-absence failure REQ-BUP-064 rejects for an
# unresolvable ref. So this control asserts BOTH halves: no proposal, and a row that says why.
#
# Exit: 0 suppressed and annotated · 1 a real negative · 2 instrument failure
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
UP="$REPO/skills/yf-beads-upstream/scripts/upstream.py"
FIXTURE="$ASSETS/closable-fixture.json"

[ -r "$UP" ] || { echo "INCONCLUSIVE: upstream.py unreadable: $UP" >&2; exit 2; }
# A MISSING declared artifact is EXIT 1 (a real negative); an unreadable/malformed one is 2.
if [ ! -f "$FIXTURE" ]; then
  echo "FAIL: declared fixture absent: $FIXTURE" >&2; exit 1
fi
python3 -c "import json,sys;json.load(open(sys.argv[1]))" "$FIXTURE" 2>/dev/null \
  || { echo "INCONCLUSIVE: fixture is malformed JSON: $FIXTURE" >&2; exit 2; }

# require_fixture_flag — THE UNCOMMISSIONED-INTERFACE RULE, in one place.
# `--fixture` does not exist today (`closable --help` shows `[-h] [--json]` only, baseline
# B3.1/B3.2). Its absence must read as a REAL NEGATIVE (exit 1) and must NEVER escape as
# argparse's exit 2 — an uncommissioned interface reads as INCONCLUSIVE, which the gates
# now refuse, and would silently satisfy nothing while looking like an instrument fault.
require_fixture_flag() {
  if ! uv run "$UP" closable --help 2>&1 | grep -q -- '--fixture'; then
    echo "FAIL: \`closable\` exposes no --fixture flag." >&2
    echo "      Baseline B3.1: closable --help shows [-h] [--json] only." >&2
    echo "      The uncommissioned-interface rule maps this to a REAL NEGATIVE (exit 1)." >&2
    exit 1
  fi
}

# run_closable — always against the PINNED FIXTURE, never live bd state.
run_closable() { uv run "$UP" closable --fixture "$FIXTURE" --json 2>/dev/null || true; }

require_fixture_flag
OUT="$(run_closable)"
[ -n "$OUT" ] || { echo "INCONCLUSIVE: closable --fixture produced no output" >&2; exit 2; }
printf '%s' "$OUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"INCONCLUSIVE: output is not JSON: {e}", file=sys.stderr); raise SystemExit(2)
issues = d.get("issues") or []
def find(n):
    for i in issues:
        if str(n) in str(i.get("issue") or "") or str(n) in str(i.get("external") or ""):
            return i
    return None

t = find(901)
# HALF 1: the row must still be PRESENT (annotated, never dropped).
if t is None:
    print("FAIL: the tombstone-only issue 901 is ABSENT from the report. It must be "
          "ANNOTATED, never dropped — a dropped row is indistinguishable from `no such "
          "issue` (the REQ-BUP-064 silent-absence failure).", file=sys.stderr)
    raise SystemExit(1)
# HALF 2: it must not be proposed for closing.
if t.get("closable") or t.get("actionable"):
    print(f"FAIL: issue 901 is proposed closable, but its only closed mapped beads are HOIST "
          f"TOMBSTONES — the work moved upstream and is still open there. row={t}",
          file=sys.stderr)
    raise SystemExit(1)
blob = json.dumps(t).lower()
if "tombstone" not in blob and "hoist" not in blob:
    print(f"FAIL: issue 901 is suppressed but the row does not SAY WHY; the operator cannot "
          f"tell it from an ordinary not-closable. row={t}", file=sys.stderr)
    raise SystemExit(1)

# The control must not pass by suppressing everything: a genuinely clean issue stays closable.
c = find(900)
if c is None or not c.get("closable"):
    print(f"FAIL: the genuinely-finished issue 900 is not closable — the suppression is too "
          f"broad. row={c}", file=sys.stderr)
    raise SystemExit(1)
o = find(902)
if o is None or o.get("closable"):
    print(f"FAIL: issue 902 has an OPEN mapped bead and must be not-closable. row={o}",
          file=sys.stderr)
    raise SystemExit(1)

print("PASS: 901 suppressed AND annotated; 900 still closable; 902 not-closable")
'
