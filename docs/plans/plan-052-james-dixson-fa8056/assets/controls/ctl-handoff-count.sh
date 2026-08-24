#!/usr/bin/env bash
# ctl-handoff-count (SC4) — gen_handoff.py's retrospective count is CORRECT, and a wrong
# extractor makes it fail.
#
# The defect: gen_handoff.py:178 counts entries with `^###\s+(RE-\d+)` — THREE hashes — while
# the entries are written `## RE-001`. It reports 0 where 6 exist, and `--check` reports OK
# because it regenerates the same wrong number and diffs it against itself.
#
# Both arms run against a COPY of the plan-051 bundle in $(mktemp -d): the script derives
# PLAN_DIR from __file__, so a copied bundle is a complete, residue-free fixture and the
# repository is never mutated.
#
# Exit: 0 the count is correct AND a wrong extractor is caught · 1 a real negative · 2 cannot run
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
SRC="$REPO/docs/plans/plan-051-james-dixson-2f499f"

[ -d "$SRC" ] || { echo "INCONCLUSIVE: plan-051 bundle absent: $SRC" >&2; exit 2; }
[ -r "$SRC/scripts/gen_handoff.py" ] || { echo "INCONCLUSIVE: gen_handoff.py absent" >&2; exit 2; }

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
cp -R "$SRC" "$tmp/bundle" || { echo "INCONCLUSIVE: cannot stage fixture" >&2; exit 2; }
GEN="$tmp/bundle/scripts/gen_handoff.py"
RETRO="$tmp/bundle/plan-retrospective.md"
[ -r "$RETRO" ] || { echo "INCONCLUSIVE: plan-retrospective.md absent in fixture" >&2; exit 2; }

# Ground truth: entries are written `## RE-NNN`.
TRUTH=$(grep -c '^## RE-' "$RETRO" || true)
[ "${TRUTH:-0}" -gt 0 ] || { echo "INCONCLUSIVE: fixture retrospective has no '## RE-' entry" >&2; exit 2; }

reported() { # <bundle-dir> -> the N the generated handoff claims
  ( cd "$1" && uv run scripts/gen_handoff.py --write >/dev/null 2>&1 ) || return 2
  local out; out=$(ls "$1"/references/handoff-*.md 2>/dev/null | head -1)
  [ -n "$out" ] || return 2
  sed -n 's/.*`plan-retrospective\.md` carries \*\*\([0-9][0-9]*\)\*\* entr.*/\1/p' "$out" | head -1
}

# --- ARM 1: the live extractor's count must equal ground truth -------------------
GOT=$(reported "$tmp/bundle") || { echo "INCONCLUSIVE: generator failed on the fixture" >&2; exit 2; }
[ -n "$GOT" ] || { echo "INCONCLUSIVE: could not read the reported count" >&2; exit 2; }
if [ "$GOT" != "$TRUTH" ]; then
  echo "FAIL: handoff reports $GOT retrospective entr(y|ies) where $TRUTH exist" >&2
  echo "      extractor: $(sed -n '/re\.findall/p' "$GEN" | head -1 | sed 's/^ *//')" >&2
  exit 1
fi
echo "ok: reported count $GOT == ground truth $TRUTH"

# --- ARM 2: a WRONG extractor must be caught ------------------------------------
# Deliberately break the regex in a second fixture; the control must see a mismatch.
cp -R "$SRC" "$tmp/broken"
python3 - "$tmp/broken/scripts/gen_handoff.py" <<'PYEOF'
import pathlib, re, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text(encoding="utf-8")
s2 = re.sub(r'r"\^#+\\s\+\(RE-\\d\+\)"', r'r"^####\\s+(RE-\\d+)"', s)
if s2 == s:
    s2 = s.replace('re.findall(r"^##', 're.findall(r"^####')
p.write_text(s2, encoding="utf-8")
PYEOF
BGOT=$(reported "$tmp/broken") || { echo "INCONCLUSIVE: generator failed on the broken fixture" >&2; exit 2; }
if [ "$BGOT" = "$TRUTH" ]; then
  echo "FAIL: a deliberately WRONG extractor still reported the correct count ($BGOT)" >&2
  echo "      the check is insensitive to the extractor — it proves nothing" >&2
  exit 1
fi
echo "ok: wrong extractor reported $BGOT != $TRUTH (caught)"
echo "PASS: the retrospective count is correct, and a wrong extractor is caught"
