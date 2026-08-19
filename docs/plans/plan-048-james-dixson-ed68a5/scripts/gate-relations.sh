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

# `--type plan-relations` + `--path <plan.md>`. NOT `--kind` (no such flag) and NOT a bare
# bundle dir: the relational rules are declared on `plan.md`, and a path-scoped run is what
# makes REQ-DATA-043 report exit 2 for an unreadable plan instead of degrading to a
# report-only finding the way a corpus sweep does.
run_lint() {
  # $1 = bundle dir. Echoes the exit code.
  uv run _shared/doc_lint.py --type plan-relations --path "$1/plan.md" --json \
    >"$WORK/out.json" 2>"$WORK/err.txt"
  echo $?
}

# A relational rule is severity `W` with promotion DECLARED OFF (REQ-DATA-044), so a
# violation never changes the exit code. The gate therefore asserts on the FINDING SET,
# which is where the rules actually speak. `rule_fired <id>` = that rule reported at least
# one finding on the mutant.
rule_fired() {
  python3 -c '
import json,sys
d=json.load(open(sys.argv[1]))
print("yes" if any(f["check"]==sys.argv[2] for f in d.get("findings",[])) else "no")
' "$WORK/out.json" "$1"
}

# --- control: unmutated plan-047 must be GREEN ------------------------------
cp -Rf "$CONTROL_PLAN" "$WORK/control" || gate_harness "could not copy control bundle"
rc=$(run_lint "$WORK/control")
if [ "$rc" != "0" ]; then
  cat "$WORK/out.json" "$WORK/err.txt" >&2 2>/dev/null || true
  gate_absent "control (unmutated ${CONTROL_PLAN}) exited ${rc}, expected 0 — a red control makes every mutant result meaningless"
fi
for r in R1 R1b R2a R2b R2c; do
  [ "$(rule_fired "$r")" = "no" ] \
    || gate_absent "control (unmutated ${CONTROL_PLAN}) already reports ${r} — a mutant result would be unattributable"
done
echo "control: exit 0, and no relational rule fires on it"

# --- mutants: one per rule, each breaking exactly that rule ------------------
#
# EVERY MUTATION IS SECTION-SCOPED, and that is not tidiness. The first draft anchored the
# R1b mutant on `### Epic 1:` and it silently landed at line 150 — an EARLIER occurrence of
# that string in prose, 190 lines above `## Epics`. The extractor correctly ignored an issue
# bullet outside the Epics section, so the mutant exercised nothing and the gate reported the
# rule "cannot detect its own violation". The gate was right; the mutation was wrong.
#
# A mutant that does not land where it thinks it does is worse than no mutant: it certifies
# a capability nobody tested. So each mutation is applied INSIDE a named `## ` section, and
# a mutation that turns out to be a no-op is a HARNESS failure, not a rule failure.

mutate_R1() {
  # $1 = name, $2 = python body operating on `sec`, $3 = rule id, $4 = `## ` section.
  rm -rf "$WORK/m"
  cp -Rf "$CONTROL_PLAN" "$WORK/m" || gate_harness "could not copy bundle for mutant $1"
  python3 - "$WORK/m/plan.md" "$4" <<PYMUT || gate_harness "mutation $1 could not be applied"
import sys, re
path, want = sys.argv[1], sys.argv[2]
lines = open(path).read().split("\n")
start = end = None
for n, ln in enumerate(lines):
    if ln.startswith("## ") and ln[3:].strip() == want:
        start = n + 1
    elif start is not None and ln.startswith("## "):
        end = n
        break
if start is None:
    sys.exit("section not found: " + want)
end = end if end is not None else len(lines)
sec = before = "\n".join(lines[start:end])
sec = re.sub(r"(\\n\\| SC[0-9a-z]+ \\|[^\\n]*\\| )([0-9][^|\\n]*)(\\|)", r"\\g<1>99.99 \\g<3>", sec, count=1)
if sec == before:
    sys.exit("mutation was a NO-OP inside section " + want)
open(path, "w").write("\n".join(lines[:start] + sec.split("\n") + lines[end:]))
PYMUT
  rc=$(run_lint "$WORK/m")
  if [ "$rc" = "2" ]; then
    cat "$WORK/err.txt" >&2 2>/dev/null || true
    gate_harness "mutant '$1' made the plan UNPARSABLE (exit 2) — it broke the document rather than the relation, so it proves nothing about rule $3"
  fi
  if [ "$(rule_fired "$3")" != "yes" ]; then
    cat "$WORK/out.json" >&2 2>/dev/null || true
    gate_absent "mutant '$1' did not make rule $3 fire — that rule cannot detect its own violation"
  fi
  echo "mutant $1: rule $3 fired (as required)"
}

mutate_R1b() {
  # $1 = name, $2 = python body operating on `sec`, $3 = rule id, $4 = `## ` section.
  rm -rf "$WORK/m"
  cp -Rf "$CONTROL_PLAN" "$WORK/m" || gate_harness "could not copy bundle for mutant $1"
  python3 - "$WORK/m/plan.md" "$4" <<PYMUT || gate_harness "mutation $1 could not be applied"
import sys, re
path, want = sys.argv[1], sys.argv[2]
lines = open(path).read().split("\n")
start = end = None
for n, ln in enumerate(lines):
    if ln.startswith("## ") and ln[3:].strip() == want:
        start = n + 1
    elif start is not None and ln.startswith("## "):
        end = n
        break
if start is None:
    sys.exit("section not found: " + want)
end = end if end is not None else len(lines)
sec = before = "\n".join(lines[start:end])
sec = re.sub(r"(\\n### Epic [0-9A-Z][^\\n]*\\n)", r"\\g<1>- Issue 1.99: an issue no success criterion names.\\n", sec, count=1)
sec = sec.replace("<!-- epic-kind: bookkeeping -->", "")
if sec == before:
    sys.exit("mutation was a NO-OP inside section " + want)
open(path, "w").write("\n".join(lines[:start] + sec.split("\n") + lines[end:]))
PYMUT
  rc=$(run_lint "$WORK/m")
  if [ "$rc" = "2" ]; then
    cat "$WORK/err.txt" >&2 2>/dev/null || true
    gate_harness "mutant '$1' made the plan UNPARSABLE (exit 2) — it broke the document rather than the relation, so it proves nothing about rule $3"
  fi
  if [ "$(rule_fired "$3")" != "yes" ]; then
    cat "$WORK/out.json" >&2 2>/dev/null || true
    gate_absent "mutant '$1' did not make rule $3 fire — that rule cannot detect its own violation"
  fi
  echo "mutant $1: rule $3 fired (as required)"
}

mutate_R2a() {
  # $1 = name, $2 = python body operating on `sec`, $3 = rule id, $4 = `## ` section.
  rm -rf "$WORK/m"
  cp -Rf "$CONTROL_PLAN" "$WORK/m" || gate_harness "could not copy bundle for mutant $1"
  python3 - "$WORK/m/plan.md" "$4" <<PYMUT || gate_harness "mutation $1 could not be applied"
import sys, re
path, want = sys.argv[1], sys.argv[2]
lines = open(path).read().split("\n")
start = end = None
for n, ln in enumerate(lines):
    if ln.startswith("## ") and ln[3:].strip() == want:
        start = n + 1
    elif start is not None and ln.startswith("## "):
        end = n
        break
if start is None:
    sys.exit("section not found: " + want)
end = end if end is not None else len(lines)
sec = before = "\n".join(lines[start:end])
sec = re.sub(r"(\\n\\| \\[?#[0-9]+\\]?[^\\n]*\\| include \\|[^|\\n]*\\| )([^|\\n]*)(\\|)", r"\\g<1>99.99 \\g<3>", sec, count=1)
if sec == before:
    sys.exit("mutation was a NO-OP inside section " + want)
open(path, "w").write("\n".join(lines[:start] + sec.split("\n") + lines[end:]))
PYMUT
  rc=$(run_lint "$WORK/m")
  if [ "$rc" = "2" ]; then
    cat "$WORK/err.txt" >&2 2>/dev/null || true
    gate_harness "mutant '$1' made the plan UNPARSABLE (exit 2) — it broke the document rather than the relation, so it proves nothing about rule $3"
  fi
  if [ "$(rule_fired "$3")" != "yes" ]; then
    cat "$WORK/out.json" >&2 2>/dev/null || true
    gate_absent "mutant '$1' did not make rule $3 fire — that rule cannot detect its own violation"
  fi
  echo "mutant $1: rule $3 fired (as required)"
}

mutate_R2b() {
  # $1 = name, $2 = python body operating on `sec`, $3 = rule id, $4 = `## ` section.
  rm -rf "$WORK/m"
  cp -Rf "$CONTROL_PLAN" "$WORK/m" || gate_harness "could not copy bundle for mutant $1"
  python3 - "$WORK/m/plan.md" "$4" <<PYMUT || gate_harness "mutation $1 could not be applied"
import sys, re
path, want = sys.argv[1], sys.argv[2]
lines = open(path).read().split("\n")
start = end = None
for n, ln in enumerate(lines):
    if ln.startswith("## ") and ln[3:].strip() == want:
        start = n + 1
    elif start is not None and ln.startswith("## "):
        end = n
        break
if start is None:
    sys.exit("section not found: " + want)
end = end if end is not None else len(lines)
sec = before = "\n".join(lines[start:end])
sec = re.sub(r"(\\n\\| \\[?#[0-9]+\\]?[^\\n]*\\| exclude \\|[^|\\n]*\\| )([^|\\n]*)(\\|)", r"\\g<1>1.1 \\g<3>", sec, count=1)
if sec == before:
    sys.exit("mutation was a NO-OP inside section " + want)
open(path, "w").write("\n".join(lines[:start] + sec.split("\n") + lines[end:]))
PYMUT
  rc=$(run_lint "$WORK/m")
  if [ "$rc" = "2" ]; then
    cat "$WORK/err.txt" >&2 2>/dev/null || true
    gate_harness "mutant '$1' made the plan UNPARSABLE (exit 2) — it broke the document rather than the relation, so it proves nothing about rule $3"
  fi
  if [ "$(rule_fired "$3")" != "yes" ]; then
    cat "$WORK/out.json" >&2 2>/dev/null || true
    gate_absent "mutant '$1' did not make rule $3 fire — that rule cannot detect its own violation"
  fi
  echo "mutant $1: rule $3 fired (as required)"
}

mutate_R2c() {
  # $1 = name, $2 = python body operating on `sec`, $3 = rule id, $4 = `## ` section.
  rm -rf "$WORK/m"
  cp -Rf "$CONTROL_PLAN" "$WORK/m" || gate_harness "could not copy bundle for mutant $1"
  python3 - "$WORK/m/plan.md" "$4" <<PYMUT || gate_harness "mutation $1 could not be applied"
import sys, re
path, want = sys.argv[1], sys.argv[2]
lines = open(path).read().split("\n")
start = end = None
for n, ln in enumerate(lines):
    if ln.startswith("## ") and ln[3:].strip() == want:
        start = n + 1
    elif start is not None and ln.startswith("## "):
        end = n
        break
if start is None:
    sys.exit("section not found: " + want)
end = end if end is not None else len(lines)
sec = before = "\n".join(lines[start:end])
sec = sec.replace("| include |", "| incldue |", 1)
if sec == before:
    sys.exit("mutation was a NO-OP inside section " + want)
open(path, "w").write("\n".join(lines[:start] + sec.split("\n") + lines[end:]))
PYMUT
  rc=$(run_lint "$WORK/m")
  if [ "$rc" = "2" ]; then
    cat "$WORK/err.txt" >&2 2>/dev/null || true
    gate_harness "mutant '$1' made the plan UNPARSABLE (exit 2) — it broke the document rather than the relation, so it proves nothing about rule $3"
  fi
  if [ "$(rule_fired "$3")" != "yes" ]; then
    cat "$WORK/out.json" >&2 2>/dev/null || true
    gate_absent "mutant '$1' did not make rule $3 fire — that rule cannot detect its own violation"
  fi
  echo "mutant $1: rule $3 fired (as required)"
}

mutate_R1 "R1-dangling-discharged-by" "" "R1" "Success Criteria"
mutate_R1b "R1b-issue-named-by-no-criterion" "" "R1b" "Epics"
mutate_R2a "R2a-dangling-resolved-by" "" "R2a" "Upstream Issues"
mutate_R2b "R2b-exclude-resolves-something" "" "R2b" "Upstream Issues"
mutate_R2c "R2c-unrecognised-disposition" "" "R2c" "Upstream Issues"

gate_present "control clean and all five relational mutants make their rule fire"
