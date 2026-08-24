#!/usr/bin/env bash
# ctl-197-injection (SC15) — `plan-execute` gets its verify beads at INJECTION time.
#
# `plan-execute` declares ONE step (the start gate) and therefore CANNOT BE WOVEN: an aspect
# composes over steps, and there is nothing to compose over. So its verify beads are emitted
# at injection time instead — a different mechanism for a structurally different formula,
# not the same mechanism applied twice.
#
# The control asserts the emitter exists, that it targets plan-execute, and that it emits ONE
# verify bead per real execution bead rather than a single blanket bead (which would satisfy
# a count check while verifying nothing in particular).
#
# The emitter is shipped by Issue 5.2; this control is built by 5.0.
# UNCOMMISSIONED-INTERFACE RULE: an absent emitter is EXIT 1 (a real negative), never 2.
# Exit: 0 injection-time verify beads are emitted · 1 a real negative · 2 instrument failure
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
VB="$REPO/skills/yf-plan/scripts/verify_beads.py"
FORMULA="$REPO/skills/yf-plan/formulas/plan-execute.formula.toml"

[ -r "$FORMULA" ] || { echo "INCONCLUSIVE: plan-execute formula absent" >&2; exit 2; }

# The premise this issue rests on: plan-execute really does declare exactly one step.
NSTEPS=$(grep -c '^\[\[steps\]\]' "$FORMULA" || true)
if [ "${NSTEPS:-0}" -ne 1 ]; then
  echo "INCONCLUSIVE: plan-execute declares $NSTEPS steps, not 1 — the premise that it" >&2
  echo "              cannot be woven no longer holds; restate 5.2 before trusting this." >&2
  exit 2
fi
echo "ok: plan-execute declares exactly 1 step, so it cannot be woven"

if [ ! -r "$VB" ]; then
  echo "FAIL: the injection-time emitter does not exist: $VB" >&2
  echo "      The uncommissioned-interface rule maps this to a REAL NEGATIVE (exit 1)." >&2
  exit 1
fi

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
cat > "$tmp/beads.json" <<'JSON'
[
 {"id":"e.1.1","title":"Issue 1.1: first","status":"open","issue_type":"task",
  "metadata":{"plan":"plan-996-fixture","plan_issue":"1.1"}},
 {"id":"e.1.2","title":"Issue 1.2: second","status":"open","issue_type":"task",
  "metadata":{"plan":"plan-996-fixture","plan_issue":"1.2"}},
 {"id":"e.9","title":"Gate: something","status":"open","issue_type":"gate",
  "metadata":{"plan":"plan-996-fixture"}}
]
JSON

OUT="$(uv run "$VB" --fixture "$tmp/beads.json" --plan plan-996-fixture --json 2>/dev/null || true)"
[ -n "$OUT" ] || { echo "INCONCLUSIVE: verify_beads.py produced no output" >&2; exit 2; }

printf '%s' "$OUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"INCONCLUSIVE: output is not JSON: {e}", file=sys.stderr); raise SystemExit(2)
beads = d.get("verify_beads") or d.get("beads") or []
if not beads:
    print(f"FAIL: no verify beads emitted; got keys {sorted(d)}", file=sys.stderr)
    raise SystemExit(1)
if str(d.get("formula") or d.get("target") or "").find("plan-execute") < 0:
    print(f"FAIL: the emission does not target plan-execute (formula={d.get(\"formula\")!r})",
          file=sys.stderr)
    raise SystemExit(1)
# ONE verify bead per real execution bead — never a single blanket bead.
targets = {str(b.get("verifies") or b.get("target") or "") for b in beads}
if len(beads) < 2 or len(targets) < 2:
    print(f"FAIL: {len(beads)} verify bead(s) over {len(targets)} target(s) for 2 execution "
          f"beads — a blanket bead satisfies a count check while verifying nothing in "
          f"particular", file=sys.stderr)
    raise SystemExit(1)
# Gates are not execution beads and must not get one.
if any("e.9" in t for t in targets):
    print("FAIL: a verify bead was emitted for a GATE", file=sys.stderr)
    raise SystemExit(1)
print(f"PASS: {len(beads)} injection-time verify bead(s) over {len(targets)} execution beads")
'
