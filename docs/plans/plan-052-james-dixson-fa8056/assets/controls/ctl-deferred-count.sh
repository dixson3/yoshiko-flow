#!/usr/bin/env bash
# ctl-deferred-count (SC21a) — all EIGHT deferred defects are filed, the count DERIVED from
# assets/deferred-defects.md.
#
# SPLIT FROM SC21b DELIBERATELY. Whether each defect carries a CORRECT measurement is a
# reader judgement over issue prose and is waived as `manual:`. The COUNT is checkable, so it
# IS checked — rather than waiving both and calling the pair verified.
#
# The expected total is read from the document's own declaration, not hard-coded here, so the
# control cannot disagree with the artifact it checks. It still asserts the declared total is
# SEVEN, so the document cannot satisfy the control by lowering its own bar.
#
# Exit: 0 seven filed, each with an upstream ref · 1 a real negative · 2 instrument failure
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOC="$ASSETS/deferred-defects.md"
# EIGHT, not seven. An eighth defect was found AT EXECUTION (the gate Test/Condition fidelity
# gap, #219) and added to the enumeration. The alternative — leaving a real defect out of the
# document so this count stayed at 7 — is the inversion this plan exists to prevent: a control
# is for catching reality, not for being kept green.
EXPECTED=8

# A MISSING declared artifact is EXIT 1 (a real negative).
if [ ! -f "$DOC" ]; then
  echo "FAIL: declared artifact absent: $DOC (Issue 7.2 produces it)" >&2
  exit 1
fi

python3 - "$DOC" "$EXPECTED" <<'PYEOF'
import pathlib, re, sys
doc = pathlib.Path(sys.argv[1])
expected = int(sys.argv[2])
try:
    text = doc.read_text(encoding="utf-8")
except OSError as e:
    print(f"INCONCLUSIVE: deferred-defects.md unreadable: {e}", file=sys.stderr)
    raise SystemExit(2)

# One row per defect in the document's table, each naming a filed upstream issue.
rows = []
header: list[str] = []
for ln in text.splitlines():
    if not ln.startswith("|"):
        continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    if set(cells[0]) <= set(":- "):
        continue
    if cells[0].strip().lower() in ("#", "id"):
        header = cells          # the most recent header wins; all tables share a shape
        continue
    if len(cells) < 2:
        continue
    rows.append(cells)

if not rows:
    print("INCONCLUSIVE: deferred-defects.md has no defect table", file=sys.stderr)
    raise SystemExit(2)

if len(rows) != expected:
    print(f"FAIL: {len(rows)} defect(s) recorded, expected {expected}", file=sys.stderr)
    raise SystemExit(1)

# Each must actually be FILED — read the `Filed` CELL, never the whole row. An earlier
# draft scanned the joined row and counted D4 as filed because its MEASUREMENT cites #107;
# a citation in prose is not a filing, and a check that cannot tell them apart reports a
# green for work nobody did.
try:
    filed_col = next(i for i, h in enumerate(header) if h.strip().lower() == "filed")
except (StopIteration, NameError):
    print("INCONCLUSIVE: no `Filed` column in the defect table", file=sys.stderr)
    raise SystemExit(2)
unfiled = [r[0] for r in rows
           if filed_col >= len(r) or not re.search(r"#\d+", r[filed_col])]
if unfiled:
    print(f"FAIL: {len(unfiled)} defect(s) recorded but NOT filed (no #N): {unfiled}",
          file=sys.stderr)
    raise SystemExit(1)

print(f"PASS: all {len(rows)} deferred defects are recorded and filed")
PYEOF
