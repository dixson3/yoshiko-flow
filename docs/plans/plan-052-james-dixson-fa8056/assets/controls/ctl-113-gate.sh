#!/usr/bin/env bash
# ctl-113-gate (SC13) — a gate is CAUGHT when an issue in its `Blocks` produces its evidence
# (ARM 1), **or** when a required control's dischargers all sit inside — or transitively
# behind — that `Blocks` set (ARM 2).
#
# ARM 2 is what pass-2's C2 needed and what C8 showed a NAME-MATCH CANNOT SEE: the pre-fix
# `red-prework-core` named no blocked issue anywhere in its prose, so an arm-1-only predicate
# read it as clean while six of the controls its Condition required were built by issues the
# gate itself blocked. The gate could never open.
#
# FIVE fixtures, regression protection in BOTH directions:
#   P1  a clean gate                              -> must PASS
#   P2  the CURRENT red-prework-core, verbatim    -> must PASS
#   N1  arm-1 violation (Blocks issue named as producing the evidence)
#   N2  arm-2 violation (a required control's dischargers all inside Blocks)
#   N3  the PRE-FIX red-prework-core reproduced   -> must FAIL, on ARM 2 only
#
# The current gate is clean under both arms, so a negative reproducing IT cannot exist —
# which is exactly why N3 is the historical pre-fix shape rather than today's.
#
# The predicate is shipped by Issue 4.2; this control is built by 4.1.
# UNCOMMISSIONED-INTERFACE RULE: an absent predicate is EXIT 1 (a real negative), never 2.
# Exit: 0 all five fixtures classify correctly · 1 a real negative · 2 instrument failure
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
GC="$REPO/skills/yf-plan/scripts/gate_consistency.py"

if [ ! -r "$GC" ]; then
  echo "FAIL: gate_consistency.py does not exist: $GC" >&2
  echo "      The uncommissioned-interface rule maps this to a REAL NEGATIVE (exit 1):" >&2
  echo "      the predicate is absent, which is a different claim from it failing to run." >&2
  exit 1
fi

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

# --- fixture builder -------------------------------------------------------------
# Each fixture is a minimal plan.md: an Epics section (so dischargers resolve), a Gates
# section, and a Success Criteria table (so the Condition's control ids have dischargers).
mk() { # <name>  — body on stdin
  mkdir -p "$tmp/$1"; cat > "$tmp/$1/plan.md"
}

# P1 — clean: the gate's Condition needs ctl-a, built by 1.1, which is NOT blocked.
mk p1 <<'EOF'
# Plan: clean gate fixture

## Epics
### Epic 1: prework
- Issue 1.1: build ctl-a
  - touches: `assets/controls/ctl-a.sh`
### Epic 2: fixes
- Issue 2.1: ship the fix
  - depends-on: 1.1

## Gates
### Capability Gate: clean
- Type: auto
- Condition: ctl-a has a recorded RED observation
- Test: bash assets/gate-run.sh run ctl-a
- Blocks: 2.1
- Instructions: ctl-a is built by 1.1, outside this Blocks set

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | ctl-a works | `bash assets/gate-run.sh run ctl-a` → exit 0 | 1.1, 2.1 |
EOF

# N1 — ARM 1: the Instructions name a BLOCKED issue as producing the evidence.
mk n1 <<'EOF'
# Plan: arm-1 violation fixture

## Epics
### Epic 1: prework
- Issue 1.1: build ctl-a
  - touches: `assets/controls/ctl-a.sh`
### Epic 2: fixes
- Issue 2.1: ship the fix AND record the RED observation
  - depends-on: 1.1

## Gates
### Capability Gate: self-satisfying
- Type: auto
- Condition: ctl-a has a recorded RED observation
- Test: bash assets/gate-run.sh run ctl-a
- Blocks: 2.1
- Instructions: the RED observation is recorded by 2.1, which produces this gate's evidence

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | ctl-a works | `bash assets/gate-run.sh run ctl-a` → exit 0 | 1.1, 2.1 |
EOF

# N2 — ARM 2: ctl-b's ONLY discharger (2.2) sits INSIDE the Blocks set. No prose names it.
mk n2 <<'EOF'
# Plan: arm-2 violation fixture

## Epics
### Epic 1: prework
- Issue 1.1: build ctl-a
  - touches: `assets/controls/ctl-a.sh`
### Epic 2: fixes
- Issue 2.1: ship the fix
  - depends-on: 1.1
- Issue 2.2: build ctl-b
  - touches: `assets/controls/ctl-b.sh`

## Gates
### Capability Gate: unopenable
- Type: auto
- Condition: ctl-a and ctl-b each have a recorded RED observation
- Test: bash assets/gate-run.sh verify-set core
- Blocks: 2.1, 2.2
- Instructions: builders sit outside this Blocks set

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | ctl-a works | `bash assets/gate-run.sh run ctl-a` → exit 0 | 1.1 |
| SC2 | ctl-b works | `bash assets/gate-run.sh run ctl-b` → exit 0 | 2.2 |
EOF

# N3 — the PRE-FIX red-prework-core (pass-2 C2): the core controls' builders are INSIDE
# the Blocks set. The prose names nobody, so ARM 1 alone reads it as clean.
mk n3 <<'EOF'
# Plan: pre-fix red-prework-core reproduced

## Epics
### Epic 0: harness
- Issue 0.2: build the harness
  - touches: `assets/controls/ctl-harness-contract.sh`
### Epic 1: grammar
- Issue 1.1: build ctl-199a-grammar
  - touches: `assets/controls/ctl-199a-grammar.sh`
- Issue 1.2: ship the grammar
  - depends-on: 1.1
### Epic 2: recheck
- Issue 2.1: build the ctl-199b controls
  - touches: `assets/controls/ctl-199b-fields.sh`
- Issue 2.2: ship recheck-criteria
  - depends-on: 2.1

## Gates
### Capability Gate: red-prework-core
- Type: auto
- Condition: every core control has a recorded RED observation with EXIT 1 — ctl-199a-grammar, ctl-199b-fields
- Test: bash assets/gate-run.sh verify-set core
- Blocks: 1.1, 1.2, 2.1, 2.2
- Instructions: split from ext so the epics stay severable

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | grammar | `bash assets/gate-run.sh run ctl-199a-grammar` → exit 0 | 1.1, 1.2 |
| SC2 | fields | `bash assets/gate-run.sh run ctl-199b-fields` → exit 0 | 2.1, 2.2 |
EOF

# P2 — the CURRENT red-prework-core, taken VERBATIM from this plan.
mkdir -p "$tmp/p2"
cp "$ASSETS/../plan.md" "$tmp/p2/plan.md"

# --- run the predicate over each fixture -----------------------------------------
verdict() { # <dir> -> 0 clean, 1 finding, 2 could not run
  uv run "$GC" "$1" --json >/dev/null 2>&1
}

fail=0
expect() { # <label> <dir> <expected 0|1>
  verdict "$2"; local rc=$?
  if [ "$rc" -eq 2 ]; then
    echo "INCONCLUSIVE: predicate could not run on $1" >&2; exit 2
  fi
  if [ "$rc" -ne "$3" ]; then
    echo "FAIL: $1 — predicate returned $rc, expected $3" >&2
    fail=1
  else
    echo "ok: $1 -> $rc"
  fi
}

expect "P1 clean gate"                              "$tmp/p1" 0
expect "P2 the CURRENT red-prework-core (verbatim)" "$tmp/p2" 0
expect "N1 arm-1 violation (Blocks issue named)"    "$tmp/n1" 1
expect "N2 arm-2 violation (dischargers inside)"    "$tmp/n2" 1
expect "N3 PRE-FIX red-prework-core reproduced"     "$tmp/n3" 1

# N3 must be caught on ARM 2 specifically: an arm-1-only predicate would read it clean, and a
# control that only checked "N3 fails" could not tell the two apart.
OUT="$(uv run "$GC" "$tmp/n3" --json 2>/dev/null || true)"
printf '%s' "$OUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"INCONCLUSIVE: predicate output is not JSON: {e}", file=sys.stderr); raise SystemExit(2)
blob = json.dumps(d).lower()
findings = d.get("findings") or []
arms = {str(f.get("arm") or "") for f in findings if isinstance(f, dict)}
if "2" in arms or "arm2" in arms or "discharger" in blob or "transitively" in blob:
    print("ok: N3 is caught on ARM 2 (the discharger-closure arm)")
    raise SystemExit(0)
print(f"FAIL: N3 was caught, but not on ARM 2. An arm-1-only predicate reads the pre-fix "
      f"gate as CLEAN — that is pass-2 C2, and a name-match cannot see it. findings={findings}",
      file=sys.stderr)
raise SystemExit(1)
' || fail=1

[ "$fail" -eq 0 ] || exit 1
echo "PASS: five fixtures classify correctly; N3 is caught on ARM 2"
