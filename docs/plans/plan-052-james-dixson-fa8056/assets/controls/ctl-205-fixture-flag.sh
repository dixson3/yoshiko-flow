#!/usr/bin/env bash
# ctl-205-fixture-flag (SC11b) — the `--fixture` flag EXISTS.
#
# It does NOT today: `closable --help` shows `[-h] [--json]` only. Pass 2 caught two criteria
# depending on this uncommissioned interface, which is why it gets a criterion of its own
# rather than being assumed by the two that use it.
#
# Without `--fixture`, every control over `closable` runs against LIVE `bd` STATE — which is
# not a control at all: it passes or fails for reasons that have nothing to do with the code
# under test, and it cannot be RED on demand.
#
# Exit: 0 the flag exists and reads the fixture · 1 a real negative · 2 instrument failure
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
issues = d.get("issues")
if issues is None:
    print(f"FAIL: no `issues` key; got {sorted(d)}", file=sys.stderr); raise SystemExit(1)
# The flag must actually READ THE FIXTURE, not merely be accepted and ignored.
refs = {str(i.get("issue") or i.get("external") or "") for i in issues}
want = {"900", "901", "902"}
if not any(w in r for w in want for r in refs):
    print(f"FAIL: --fixture is accepted but the fixture was NOT read; issues={sorted(refs)}",
          file=sys.stderr)
    raise SystemExit(1)
unmapped = [i for i in issues if "fx-unmapped" in json.dumps(i)]
if unmapped:
    print("FAIL: an unmapped bead appeared in the report; it maps to no issue",
          file=sys.stderr)
    raise SystemExit(1)
print(f"PASS: --fixture exists and the pinned fixture was read ({len(issues)} issue(s))")
'
