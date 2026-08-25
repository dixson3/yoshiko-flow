#!/usr/bin/env bash
# ctl-aspect-weave (SC14) — the `verify-artifact` aspect weaves over ALL FOUR `plan-review`
# steps, and a TOP-LEVEL `aspects` key is shown NOT to weave.
#
# THE OBSERVATION POINT IS `bd cook --dry-run`, AND THAT IS THE WHOLE MECHANISM.
# Aspects weave at COOK time, over formula-declared steps only (EXP-005, verbatim). Two other
# surfaces show NO woven steps BY DESIGN and asserting on either is a reading error:
#   * `bd formula show` renders the RAW FORMULA — weaving is not a property of the file;
#   * `bd mol wisp/pour` of an UNCOOKED proto has nothing woven yet.
# An earlier draft of this control checked both of those and drove six schema variations
# against them, concluding — wrongly, from correct measurements — that bd could not weave.
#
# The negative arm is the point. A TOP-LEVEL `aspects` key is SILENTLY IGNORED: it parses, it
# cooks, and it composes nothing, so an implementation using it looks correct in review and
# does nothing at runtime. Only `[compose] aspects` weaves.
#
# Everything runs in $(mktemp -d) — the shared .beads/formulas/ is never touched.
# Exit: 0 woven over all four AND the top-level key does not weave · 1 real negative · 2 instrument
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
FDIR="$REPO/skills/yf-plan/formulas"
ASPECT="$FDIR/verify-artifact.formula.toml"
CONSUMER="$FDIR/plan-review.formula.toml"

command -v bd >/dev/null || { echo "INCONCLUSIVE: bd not on PATH" >&2; exit 2; }
[ -r "$CONSUMER" ] || { echo "INCONCLUSIVE: plan-review formula absent" >&2; exit 2; }
# A MISSING declared artifact is EXIT 1 (a real negative).
if [ ! -f "$ASPECT" ]; then
  echo "FAIL: the verify-artifact aspect does not exist: $ASPECT" >&2
  exit 1
fi

# ONE initialized scratch repo, reused for every cook. `bd cook` needs a DATABASE (unlike
# `bd formula show`, which does not), and `bd init` is the expensive part — initialising once
# and swapping the formulas dir between cooks keeps this control in the cheap, self-cleaning
# `probe` class rather than paying init five times.
SANDBOX="$(mktemp -d)"
cleanup() { rm -rf "$SANDBOX" "${tmp:-}"; }
trap cleanup EXIT
( cd "$SANDBOX" && git init -q -b main >/dev/null 2>&1; bd init >/dev/null 2>&1 )
[ -d "$SANDBOX/.beads" ] || { echo "INCONCLUSIVE: could not init a scratch beads repo" >&2; exit 2; }

cook() { # <formulas-dir> -> raw `bd cook --dry-run` output
  rm -rf "$SANDBOX/.beads/formulas"; mkdir -p "$SANDBOX/.beads/formulas"
  cp "$1"/*.formula.toml "$SANDBOX/.beads/formulas/" 2>/dev/null
  ( cd "$SANDBOX" && bd cook plan-review --dry-run 2>/dev/null )
}
cook_steps() { cook "$1" | sed -n 's/^Steps (\([0-9][0-9]*\)).*/\1/p' | head -1; }
cook_ids()   { cook "$1" | sed -n 's/^[^a-z]*\([a-z][a-z0-9-]*\):.*/\1/p'; }

tmp="$(mktemp -d)"

# --- baseline: plan-review WITHOUT the aspect -------------------------------------
mkdir -p "$tmp/base"; cp "$FDIR"/*.formula.toml "$tmp/base/"
rm -f "$tmp/base/verify-artifact.formula.toml"
python3 - "$tmp/base/plan-review.formula.toml" <<'PYEOF'
import pathlib, re, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text(encoding="utf-8")
p.write_text(re.sub(r"(?ms)^\[compose\].*?(?=^\[|\Z)", "", s), encoding="utf-8")
PYEOF
BASE=$(cook_steps "$tmp/base")
[ -n "${BASE:-}" ] && [ "$BASE" -gt 0 ] 2>/dev/null \
  || { echo "INCONCLUSIVE: could not read the un-woven baseline step count" >&2; exit 2; }
echo "ok: un-woven plan-review cooks to $BASE step(s)"

# --- ARM 1: the real thing must weave over ALL of them -----------------------------
WOVEN=$(cook_steps "$FDIR")
[ -n "${WOVEN:-}" ] && [ "$WOVEN" -gt 0 ] 2>/dev/null \
  || { echo "INCONCLUSIVE: could not read the woven step count" >&2; exit 2; }
WANT=$((BASE * 2))
if [ "$WOVEN" -ne "$WANT" ]; then
  echo "FAIL: the aspect wove $((WOVEN - BASE)) step(s) onto $BASE — it must cover ALL of them" >&2
  echo "      expected $WANT cooked steps, got $WOVEN" >&2
  exit 1
fi
echo "ok: woven plan-review cooks to $WOVEN step(s) — one verify per declared step"

# Every declared step must have its OWN verify — a single blanket step would satisfy a count.
MISSING=0
for s in $(cook_ids "$tmp/base"); do
  if ! cook_ids "$FDIR" | grep -qx "${s}-verify"; then
    echo "FAIL: step '$s' has no woven '${s}-verify'" >&2
    MISSING=1
  fi
done
[ "$MISSING" -eq 0 ] || exit 1
echo "ok: every declared step has its own verify step"

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
TOP=$(cook_steps "$tmp/toplevel")
[ -n "${TOP:-}" ] && [ "$TOP" -gt 0 ] 2>/dev/null \
  || { echo "INCONCLUSIVE: could not read the top-level-key step count" >&2; exit 2; }
if [ "$TOP" -ne "$BASE" ]; then
  echo "FAIL: a TOP-LEVEL \`aspects\` key changed the cooked step count ($BASE -> $TOP)." >&2
  echo "      This control asserts it is IGNORED; if bd now honours it, the negative arm is" >&2
  echo "      stale and 5.1's claim must be restated." >&2
  exit 1
fi
echo "ok: a top-level \`aspects\` key cooks to $TOP step(s) — unchanged, so it does NOT weave"
echo "PASS: [compose] aspects weaves over all $BASE steps; a top-level key weaves nothing"
