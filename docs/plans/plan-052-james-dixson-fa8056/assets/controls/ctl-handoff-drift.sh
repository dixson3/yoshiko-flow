#!/usr/bin/env bash
# ctl-handoff-drift (SC22) — the handoff is GENERATED and its check is SENSITIVE TO CONTENT.
#
# `--check` regenerates and diffs against the shipped file. That proves the file matches its
# own regeneration; it does NOT prove the regeneration reads the source. With the `^###`
# extractor the count is 0 for ANY retrospective, so adding an entry changes no output byte
# and `--check` still reports OK — a green built on a number nothing measured.
#
# This control mutates the SOURCE in a copied bundle and requires `--check` to notice.
# Everything happens in $(mktemp -d); the repository is never mutated.
#
# Exit: 0 --check is content-sensitive · 1 a real negative · 2 the instrument could not run
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
SRC="$REPO/docs/plans/plan-051-james-dixson-2f499f"

[ -d "$SRC" ] || { echo "INCONCLUSIVE: plan-051 bundle absent: $SRC" >&2; exit 2; }
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
cp -R "$SRC" "$tmp/bundle" || { echo "INCONCLUSIVE: cannot stage fixture" >&2; exit 2; }
B="$tmp/bundle"
[ -r "$B/plan-retrospective.md" ] || { echo "INCONCLUSIVE: retrospective absent" >&2; exit 2; }

# Baseline: generate, then --check must be clean on an unmutated bundle.
( cd "$B" && uv run scripts/gen_handoff.py --write >/dev/null 2>&1 ) \
  || { echo "INCONCLUSIVE: generator failed" >&2; exit 2; }
if ! ( cd "$B" && uv run scripts/gen_handoff.py --check >/dev/null 2>&1 ); then
  echo "INCONCLUSIVE: --check is dirty on an unmutated freshly-generated bundle" >&2
  exit 2
fi
echo "ok: --check is clean on the unmutated bundle"

# MUTATE THE SOURCE: append a genuine new retrospective entry, in the form the file uses.
cat >> "$B/plan-retrospective.md" <<'ENTRY'

## RE-999

- **kind:** deviation
- **detected-by:** mechanical-check
- **evidence:** appended by ctl-handoff-drift to prove `--check` reads its source
ENTRY

# The check must now FAIL: the source changed, so the regeneration must differ.
if ( cd "$B" && uv run scripts/gen_handoff.py --check >/dev/null 2>&1 ); then
  echo "FAIL: the source gained a retrospective entry and --check still reported OK" >&2
  echo "      the check is INSENSITIVE TO CONTENT — it diffs the file against its own" >&2
  echo "      regeneration, and the regeneration does not read the entry it counts" >&2
  exit 1
fi
echo "ok: --check FAILED after the source gained an entry (content-sensitive)"

# And the regenerated count must actually move.
( cd "$B" && uv run scripts/gen_handoff.py --write >/dev/null 2>&1 ) || {
  echo "INCONCLUSIVE: regeneration failed after mutation" >&2; exit 2; }
OUT=$(ls "$B"/references/handoff-*.md 2>/dev/null | head -1)
GOT=$(sed -n 's/.*`plan-retrospective\.md` carries \*\*\([0-9][0-9]*\)\*\* entr.*/\1/p' "$OUT" | head -1)
TRUTH=$(grep -c '^## RE-' "$B/plan-retrospective.md" || true)
if [ "$GOT" != "$TRUTH" ]; then
  echo "FAIL: after mutation the handoff reports $GOT where $TRUTH exist" >&2
  exit 1
fi
echo "PASS: the handoff is generated and its check is sensitive to content ($GOT == $TRUTH)"
