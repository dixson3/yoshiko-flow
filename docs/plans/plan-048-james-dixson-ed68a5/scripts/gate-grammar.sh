#!/usr/bin/env bash
# gate-grammar.sh — Capability Gate: "grammar widening is non-vacuous" (plan-048).
#
# Blocks Issue 3.1. Invoked ONLY through gate-run.sh, which owns the {0,1,2} remap.
#
#   0 = capability PRESENT : residue <= TARGET, zero documents modified, audit adjudicated
#   1 = capability ABSENT  : one of those three is not yet true
#   2 = harness failure    : a required tool or input is missing (never red)
#
# The residue TARGET is 81. It was RE-BASED from 54 at execution, by explicit operator
# decision, because 54 was MISDERIVED — it inherited EXP-001's "~96 recoverable" estimate,
# which counted classes that Issues 1.4/1.4a later declared must be REFUSED. See
# ../assets/residue-analysis.md for the full derivation.
#
# It is still NOT re-derived from whatever this run happens to measure — a target computed
# from the measurement it grades is not a target, it is a tautology. 81 is the count of
# constructs the plan's own refusal rules make unrecoverable, computed from those rules, and
# a residue ABOVE it still fails. ../assets/residue-mutant.md drives that direction.

set -u
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

TARGET=81
BASELINE=150   # measured 2026-08-19 across 33 of 48 plans (EXP-001, D-5 re-measurement)

require_tool git
require_tool uv
cd "$REPO_ROOT" || gate_harness "cannot cd to repo root: $REPO_ROOT"
require_file "_shared/plan_extract.py"

# --- 1. residue --------------------------------------------------------------
raw=$(uv run _shared/plan_extract.py docs/plans/*/ --json 2>/dev/null) \
  || gate_harness "plan_extract.py did not run"
[ -n "$raw" ] || gate_harness "plan_extract.py produced no output"

residue=$(printf '%s' "$raw" | python3 -c '
import json,sys
try: d=json.load(sys.stdin)
except Exception: sys.exit(9)
print(sum(len(doc.get("unparsed") or []) for doc in d))
') || gate_harness "could not count unparsed constructs (malformed extractor JSON)"

docs_with=$(printf '%s' "$raw" | python3 -c '
import json,sys; d=json.load(sys.stdin)
print(sum(1 for doc in d if doc.get("unparsed")))')

echo "residue: ${residue} (baseline ${BASELINE}, target <= ${TARGET}); plans still carrying unparsed: ${docs_with}"

if [ "$residue" -gt "$TARGET" ]; then
  gate_absent "unparsed residue ${residue} exceeds the approval-fixed target of ${TARGET}"
fi

# --- 2. zero documents modified (D-4 / SC1) ----------------------------------
# Everything after `--` is a pathspec; without it git parses `docs/plans` as a revision
# and exits 128. The exclusion keeps plan-048's OWN bundle out of the assertion.
modified=$(git diff --stat HEAD -- docs/plans ':!docs/plans/plan-048-james-dixson-ed68a5' 2>/dev/null)
if [ -n "$modified" ]; then
  echo "$modified" >&2
  gate_absent "the widening modified corpus documents; it must be hash-neutral by construction"
fi

# --- 3. hand audit adjudicated (SC1b) ----------------------------------------
audit="docs/plans/plan-048-james-dixson-ed68a5/assets/edge-audit.md"
[ -s "$audit" ] || gate_absent "hand-audit not adjudicated: ${audit} is absent or empty"

rows=$(grep -cE '^\| *(before|[0-9]+) ' "$audit" 2>/dev/null || true)
plans=$(grep -oE 'plan-[0-9]{3}' "$audit" 2>/dev/null | sort -u | wc -l | tr -d ' ')
adverse=$(grep -cE '^\*\*Adverse findings:\*\* *0\b' "$audit" 2>/dev/null || true)

echo "audit: ${rows} adjudicated rows across ${plans} plans"
[ "${rows:-0}" -ge 20 ] || gate_absent "hand audit has ${rows} rows; SC1b requires >= 20"
[ "${plans:-0}" -ge 10 ] || gate_absent "hand audit spans ${plans} plans; SC1b requires >= 10"
[ "${adverse:-0}" -ge 1 ] || gate_absent "hand audit does not carry an explicit adverse-finding count"

gate_present "residue ${residue} <= ${TARGET}, zero corpus documents modified, ${rows} edges adjudicated across ${plans} plans"
