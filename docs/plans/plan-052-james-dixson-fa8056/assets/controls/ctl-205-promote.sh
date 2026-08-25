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

# THE CLOSE-OUT BINDING, asserted against the mechanism that actually implements it rather
# than a key name. `statuses` decides WHETHER a check runs (REQ-DATA-058), and `reconciling`
# / `complete` are the only statuses the §6.3-§6.4 close-out runs under — so a check scoped
# to them IS close-out-bound. An earlier draft of this control looked for a `promote_at` key
# that no engine reads; it would have gone green on a declaration nothing consumed, which is
# the defect this plan exists to remove.
CLOSEOUT = {"reconciling", "complete"}
problems = []

for base in ("R1", "R2a"):
    if base not in by_id:
        problems.append(f"{base}: absent; present ids are {sorted(by_id)}")
        continue

    # ARM 1: authoring-time severity is UNCHANGED. An in-flight plan legitimately has rows
    # whose Discharged-by / Resolved By are not yet knowable.
    authoring = [r for r in rules
                 if str(r.get("rule") or r.get("id")) == base
                 and not (set(r.get("statuses") or []) and
                          set(r.get("statuses") or []) <= CLOSEOUT)]
    if not authoring:
        problems.append(f"{base}: no authoring-time check remains — the promotion replaced "
                        f"it instead of adding a binding")
    for r in authoring:
        if str(r.get("severity") or "").upper() == "E":
            problems.append(f"{base}: authoring-time check {r.get('id')!r} is severity E — "
                            f"the promotion is GLOBAL, not close-out-scoped; an in-flight "
                            f"plan would hard-fail")

    # ARM 2: a close-out-scoped check exists AND is error-severity there.
    bound = [r for r in rules
             if str(r.get("rule") or r.get("id")) == base
             and set(r.get("statuses") or []) and set(r.get("statuses") or []) <= CLOSEOUT]
    if not bound:
        problems.append(f"{base}: no check is scoped to the close-out statuses {sorted(CLOSEOUT)}")
    elif not any(str(r.get("severity") or "").upper() == "E" for r in bound):
        problems.append(f"{base}: a close-out-scoped check exists but none is severity E — "
                        f"it is bound but not promoted")

# ARM 3: the promotion must SURVIVE at `complete`. STATUS_SEVERITY demotes E -> R there, and
# only the file-level `promote = false` bypasses it. Without that the close-out E is silently
# downgraded at the exact status it exists to fire on.
if d.get("promote", True):
    problems.append("the schema does not set `promote = false`, so STATUS_SEVERITY demotes "
                    "the close-out E to R at `complete` — the promotion would be inert")

if problems:
    print("FAIL: the R1/R2a promotion is not close-out-scoped:", file=sys.stderr)
    for x in problems:
        print(f"  - {x}", file=sys.stderr)
    raise SystemExit(1)

print("PASS: R1/R2a promote at the close-out binding only; authoring severity unchanged")
PYEOF
