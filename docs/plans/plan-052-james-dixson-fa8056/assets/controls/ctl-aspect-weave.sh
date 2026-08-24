#!/usr/bin/env bash
# ctl-aspect-weave (SC14) — the `verify-artifact` aspect weaves over ALL FOUR `plan-review`
# steps, and a TOP-LEVEL `aspects` key is shown NOT to weave.
#
# The negative arm is the point. A top-level `aspects` key is SILENTLY IGNORED by bd's
# formula schema — it parses, it pours, and it composes nothing. So an implementation that
# put the key at the top level would look correct in review and do nothing at runtime, which
# is the silent-green class in its composition form. `[compose] aspects` is the key that
# actually weaves.
#
# Both arms are executed, never read off the TOML: the fixture is staged into a scratch
# `.beads/formulas/` and `bd formula show --json` resolves the composition. bd needs no DB
# for that, so the scratch tree is self-contained and leaves no residue.
#
# Exit: 0 woven over all four AND the top-level key does not weave · 1 real negative · 2 instrument
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
FDIR="$REPO/skills/yf-plan/formulas"
ASPECT="$FDIR/verify-artifact.formula.toml"

command -v bd >/dev/null || { echo "INCONCLUSIVE: bd not on PATH" >&2; exit 2; }
[ -d "$FDIR" ] || { echo "INCONCLUSIVE: formulas dir absent: $FDIR" >&2; exit 2; }

# A MISSING declared artifact is EXIT 1 (a real negative).
if [ ! -f "$ASPECT" ]; then
  echo "FAIL: the verify-artifact aspect does not exist: $ASPECT" >&2
  exit 1
fi

steps_of() { # <formulas-dir> <formula> -> step count, via a scratch beads tree
  local src="$1" name="$2" t; t="$(mktemp -d)"
  mkdir -p "$t/.beads/formulas"; cp "$src"/*.formula.toml "$t/.beads/formulas/" 2>/dev/null
  ( cd "$t" && bd formula show "$name" --json 2>/dev/null ) \
    | python3 -c 'import json,sys
try: d=json.load(sys.stdin)
except Exception: print(-1); raise SystemExit
print(len(d.get("steps") or []))'
  rm -rf "$t"
}

# --- baseline: plan-review WITHOUT the aspect ------------------------------------
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/base"; cp "$FDIR"/*.formula.toml "$tmp/base/"
rm -f "$tmp/base/verify-artifact.formula.toml"
python3 - "$tmp/base/plan-review.formula.toml" <<'PYEOF'
import pathlib, re, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text(encoding="utf-8")
s = re.sub(r"(?ms)^\[compose\].*?(?=^\[|\Z)", "", s)
p.write_text(s, encoding="utf-8")
PYEOF
BASE=$(steps_of "$tmp/base" plan-review)
[ "$BASE" -gt 0 ] || { echo "INCONCLUSIVE: could not resolve the un-woven baseline" >&2; exit 2; }
echo "ok: un-woven plan-review has $BASE step(s)"

# --- ARM 1: the real thing must weave over ALL FOUR -------------------------------
WOVEN=$(steps_of "$FDIR" plan-review)
[ "$WOVEN" -gt 0 ] || { echo "INCONCLUSIVE: could not resolve the woven formula" >&2; exit 2; }
WANT=$((BASE * 2))
if [ "$WOVEN" -lt "$WANT" ]; then
  echo "FAIL: the aspect wove $((WOVEN - BASE)) step(s) onto $BASE — it must cover ALL FOUR" >&2
  echo "      expected at least $WANT resolved steps, got $WOVEN" >&2
  exit 1
fi
echo "ok: woven plan-review has $WOVEN step(s) — the aspect covers all $BASE"

# --- ARM 2: a TOP-LEVEL `aspects` key must NOT weave -------------------------------
mkdir -p "$tmp/toplevel"; cp "$tmp/base"/*.formula.toml "$tmp/toplevel/"
cp "$ASPECT" "$tmp/toplevel/"
python3 - "$tmp/toplevel/plan-review.formula.toml" <<'PYEOF'
import pathlib, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text(encoding="utf-8")
lines = s.splitlines(keepends=True)
out, done = [], False
for ln in lines:
    if not done and ln.startswith("[") and not ln.startswith("[vars"):
        out.append('aspects = ["verify-artifact"]\n\n'); done = True
    out.append(ln)
if not done:
    out.append('\naspects = ["verify-artifact"]\n')
p.write_text("".join(out), encoding="utf-8")
PYEOF
TOP=$(steps_of "$tmp/toplevel" plan-review)
[ "$TOP" -gt 0 ] || { echo "INCONCLUSIVE: could not resolve the top-level-key variant" >&2; exit 2; }
if [ "$TOP" -ne "$BASE" ]; then
  echo "FAIL: a TOP-LEVEL \`aspects\` key changed the resolved step count ($BASE -> $TOP)." >&2
  echo "      This control asserts it is IGNORED; if bd now honours it, the negative arm is" >&2
  echo "      stale and the claim in 5.1 must be restated." >&2
  exit 1
fi
echo "ok: a top-level \`aspects\` key resolved to $TOP step(s) — unchanged, so it does NOT weave"
echo "PASS: [compose] aspects weaves over all $BASE steps; a top-level key weaves nothing"
