#!/usr/bin/env bash
# ctl-205-promote (SC12b) — the `plan-relations` R1/R2a promotion binds at the CLOSE-OUT
# binding ONLY; authoring-time severity is UNCHANGED.
#
# Promoting R1/R2a globally would hard-fail authoring on a plan that is legitimately
# mid-draft — an in-flight plan has rows whose `Resolved By` is not yet knowable. The claim
# is therefore explicitly BINDING-SCOPED, and a control that only checked "R1 is an error"
# could not tell a correct scoped promotion from an incorrect global one.
#
# So both arms are asserted: promoted at close-out, and NOT promoted at authoring time.
#
# Exit: 0 promoted at close-out only · 1 a real negative · 2 instrument failure
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

TOML="$REPO/_shared/document_types/plan-relations.toml"
[ -r "$TOML" ] || { echo "INCONCLUSIVE: plan-relations.toml unreadable: $TOML" >&2; exit 2; }

python3 - "$TOML" <<'PYEOF'
import pathlib, sys, tomllib
p = pathlib.Path(sys.argv[1])
try:
    d = tomllib.loads(p.read_text(encoding="utf-8"))
except Exception as e:
    print(f"INCONCLUSIVE: plan-relations.toml is not parseable TOML: {e}", file=sys.stderr)
    raise SystemExit(2)

# The rules are INDIVIDUAL [[checks]] entries keyed by `id`, each with kind
# "plan-relations" — not a `rules` list under one check. (An earlier draft of this control
# looked for the latter and reported "no R1/R2a rules", which was a PARSER BUG reported as a
# finding: RED for the wrong reason is indistinguishable from RED for the right one, and it
# would have gone green spuriously the moment the parser was fixed.)
rules = [c for c in (d.get("checks") or []) if c.get("kind") == "plan-relations"]
if not rules:
    print("FAIL: plan-relations.toml declares no plan-relations checks; the close-out "
          "binding has nothing to bind to.", file=sys.stderr)
    raise SystemExit(1)

by_id = {str(r.get("id") or r.get("name")): r for r in rules if isinstance(r, dict)}
missing = [r for r in ("R1", "R2a") if r not in by_id]
if missing:
    print(f"FAIL: rule(s) {missing} absent; present: {sorted(by_id)}", file=sys.stderr)
    raise SystemExit(1)

problems = []
for rid in ("R1", "R2a"):
    r = by_id[rid]
    # ARM 1: a CLOSE-OUT binding must promote it to error severity.
    promote = r.get("promote_at") or r.get("promote") or r.get("bindings")
    blob = str(promote).lower()
    if "close" not in blob:
        problems.append(f"{rid}: no close-out binding declared (promote_at={promote!r})")
    # ARM 2: authoring-time severity must be UNCHANGED (not a hard error).
    sev = str(r.get("severity") or "").upper()
    if sev == "E":
        problems.append(f"{rid}: severity is E at AUTHORING time — the promotion is GLOBAL, "
                        f"not close-out-scoped; an in-flight plan would hard-fail")

if problems:
    print("FAIL: the R1/R2a promotion is not close-out-scoped:", file=sys.stderr)
    for x in problems:
        print(f"  - {x}", file=sys.stderr)
    raise SystemExit(1)

print("PASS: R1/R2a promote at the close-out binding only; authoring severity unchanged")
PYEOF
