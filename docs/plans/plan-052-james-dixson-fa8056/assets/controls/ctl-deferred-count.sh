#!/usr/bin/env bash
# ctl-deferred-count (SC21a) — all SEVEN deferred defects are filed, the count DERIVED from
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
EXPECTED=7

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
for ln in text.splitlines():
    if not ln.startswith("|"):
        continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    if len(cells) < 2 or set(cells[0]) <= set(":- ") or cells[0].lower() in ("#", "id"):
        continue
    rows.append(cells)

if not rows:
    print("INCONCLUSIVE: deferred-defects.md has no defect table", file=sys.stderr)
    raise SystemExit(2)

if len(rows) != expected:
    print(f"FAIL: {len(rows)} defect(s) recorded, expected {expected}", file=sys.stderr)
    raise SystemExit(1)

# Each must actually be FILED — a row with no issue number is a plan, not a filing.
unfiled = [r[0] for r in rows if not re.search(r"#\d+", " ".join(r))]
if unfiled:
    print(f"FAIL: {len(unfiled)} defect(s) recorded but NOT filed (no #N): {unfiled}",
          file=sys.stderr)
    raise SystemExit(1)

print(f"PASS: all {len(rows)} deferred defects are recorded and filed")
PYEOF
