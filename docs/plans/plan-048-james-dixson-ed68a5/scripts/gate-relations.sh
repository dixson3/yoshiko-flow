#!/usr/bin/env bash
# gate-relations.sh — Capability Gate: "relational checks can fail" (plan-048).
#
# Blocks Issue 3.4. Invoked ONLY through gate-run.sh, which owns the {0,1,2} remap.
#
#   0 = capability PRESENT : every generated mutant drives exit 1, control drives exit 0
#   1 = capability ABSENT  : a rule is missing, or a mutant fails to drive it red
#   2 = harness failure    : a required tool or input is missing (never red)
#
# This gate generates its OWN mutants, against the rules produced by its ANCESTORS
# (3.2 / 3.3) — never against Issue 3.5's committed fixtures, which sit in its BLOCKED
# set. A gate that executed the deliverable it gates would be circular: 3.5's fixtures
# cannot exist before 3.4, which this gate blocks.
#
# The distinction R4 exists to enforce: a check that cannot fail is not a check. Each
# mutant below breaks exactly one rule, and the control proves the red is caused by the
# mutation rather than by a pre-existing failure.

set -u
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

require_tool uv
require_tool python3
cd "$REPO_ROOT" || gate_harness "cannot cd to repo root: $REPO_ROOT"
require_file "_shared/doc_lint.py"
require_file "_shared/plan_extract.py"

# The control: a real, conformant plan bundle.
CONTROL_PLAN="docs/plans/plan-047-james-dixson-dec9ff"
[ -d "$CONTROL_PLAN" ] || gate_harness "control plan bundle not found: $CONTROL_PLAN"

# --- capability presence: does the plan-relations kind exist at all? ---------
grep -q 'plan-relations' _shared/doc_lint.py \
  || gate_absent "doc_lint.py declares no 'plan-relations' check kind (Issue 3.1 not landed)"

for rule in R1 R1b R2a R2b R2c; do
  grep -qE "\"${rule}\"|'${rule}'|id *= *\"${rule}\"" _shared/document_types/*.toml _shared/doc_lint.py 2>/dev/null \
    || gate_absent "relational rule ${rule} is not declared (Issues 3.2/3.3 not landed)"
done

WORK=$(mktemp -d) || gate_harness "cannot create scratch dir"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT INT TERM   # self-cleaning on BOTH exit paths — this gate is class `probe`

run_lint() {
  # $1 = bundle dir. Echoes exit code.
  uv run _shared/doc_lint.py --path "$1" --kind plan-relations --json >"$WORK/out.json" 2>"$WORK/err.txt"
  echo $?
}

# --- control: unmutated plan-047 must be GREEN ------------------------------
cp -Rf "$CONTROL_PLAN" "$WORK/control" || gate_harness "could not copy control bundle"
rc=$(run_lint "$WORK/control")
if [ "$rc" != "0" ]; then
  cat "$WORK/out.json" "$WORK/err.txt" >&2 2>/dev/null || true
  gate_absent "control (unmutated ${CONTROL_PLAN}) exited ${rc}, expected 0 — a red control makes every mutant result meaningless"
fi
echo "control: exit 0 (green)"

# --- mutants: one per rule, each breaking exactly that rule ------------------
mutate() {
  # $1 = name, $2 = python mutation applied to plan.md
  rm -rf "$WORK/m"
  cp -Rf "$CONTROL_PLAN" "$WORK/m" || gate_harness "could not copy bundle for mutant $1"
  python3 - "$WORK/m/plan.md" <<PYEOF || gate_harness "mutation $1 could not be applied"
import sys,re
p=sys.argv[1]; s=open(p).read()
$2
open(p,"w").write(s)
PYEOF
  rc=$(run_lint "$WORK/m")
  if [ "$rc" != "1" ]; then
    cat "$WORK/out.json" >&2 2>/dev/null || true
    gate_absent "mutant '$1' exited ${rc}, expected 1 — the rule it breaks cannot fail"
  fi
  echo "mutant $1: exit 1 (red, as required)"
}

# R1  — `Discharged-by` names an issue that does not exist.
mutate "R1-dangling-discharged-by" \
  's=re.sub(r"(\| SC1 \|[^\n]*\| )([0-9][^|]*)(\|)", r"\g<1>99.99 \g<3>", s, count=1)
assert "99.99" in s, "R1 mutation did not apply"'

# R1b — an issue named by no criterion, in an epic NOT declared bookkeeping.
mutate "R1b-issue-named-by-no-criterion" \
  's=re.sub(r"(### Epic 1:[^\n]*\n)", r"\g<1>- Issue 1.99: an issue no success criterion names.\n", s, count=1)
s=s.replace("<!-- epic-kind: bookkeeping -->","")
assert "1.99" in s, "R1b mutation did not apply"'

# R2a — `Resolved By` names an issue that does not exist.
mutate "R2a-dangling-resolved-by" \
  's=re.sub(r"(\n\| \[?#\d+\]?[^\n]*\| include \|[^|]*\| )([^|\n]*)(\|)", r"\g<1>99.99 \g<3>", s, count=1)'

# R2b — an `exclude` row that nonetheless claims a resolver.
mutate "R2b-exclude-resolves-something" \
  's=re.sub(r"(\n\| \[?#\d+\]?[^\n]*\| exclude \|[^|]*\| )([^|\n]*)(\|)", r"\g<1>1.1 \g<3>", s, count=1)'

# R2c — an unrecognised disposition literal.
mutate "R2c-unrecognised-disposition" \
  's=s.replace("| include |","| incldue |",1)
assert "incldue" in s, "R2c mutation did not apply"'

gate_present "control green and all five relational mutants drive exit 1"
