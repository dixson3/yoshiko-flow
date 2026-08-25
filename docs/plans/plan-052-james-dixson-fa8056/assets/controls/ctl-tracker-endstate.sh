#!/usr/bin/env bash
# ctl-tracker-endstate (SC23) — the coarse tracker is filed THROUGH `/yf-beads-upstream`, so
# the plan epic carries it as `external_ref`.
#
# ASSERTED AS AN END STATE, never against the `stamp-tracker` route. Which verb wrote the ref
# is unobservable after the fact, and asserting the route would be asserting something bd
# does not record — the same overreach D-6 rejects for resolver identity. What IS observable,
# and what actually matters, is that the epic ends up mapped: an unmapped tracker is
# STRUCTURALLY INVISIBLE to `upstream.py closable`, which groups beads by `external_ref`.
# Five trackers have gone stale and been closed by hand for exactly this reason.
#
# Exit: 0 the epic carries a parseable tracker ref · 1 a real negative · 2 instrument failure
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAN="$ASSETS/../plan.md"

command -v bd >/dev/null || { echo "INCONCLUSIVE: bd not on PATH" >&2; exit 2; }
[ -r "$PLAN" ] || { echo "INCONCLUSIVE: plan.md unreadable" >&2; exit 2; }

# Resolve the epic the same way resume-scan does: the **Epic:** field FIRST, then the
# metadata.plan_dir stamp. The fallback is load-bearing rather than defensive — plan-folder
# bookkeeping is written PRIMARY-SIDE (SKILL.md §5.3), so a worktree's plan.md legitimately
# predates `record-epic`. Without it this control is RED for the wrong reason: a stale
# worktree copy, not a missing tracker.
EPIC="$(sed -n 's/^\*\*Epic:\*\*[[:space:]]*\([A-Za-z0-9._-]*\).*/\1/p' "$PLAN" | head -1)"
if [ -z "$EPIC" ]; then
  PLAN_ID="$(basename "$(cd "$ASSETS/.." && pwd)")"
  EPIC="$(bd list --all --limit 5000 --json 2>/dev/null | python3 -c '
import json, sys
pid = sys.argv[1]
try:
    rows = json.load(sys.stdin)
except Exception:
    raise SystemExit
for r in rows if isinstance(rows, list) else []:
    md = r.get("metadata") or {}
    # The plan ROOT is issue_type "molecule" (measured), not "epic" — accept both.
    if r.get("issue_type") in ("molecule", "epic") and str(md.get("plan_dir") or "").endswith(pid):
        print(r["id"]); break
' "$PLAN_ID")"
fi
if [ -z "$EPIC" ]; then
  echo "FAIL: no epic resolvable for this plan — neither a **Epic:** field in plan.md nor a" >&2
  echo "      bead carrying metadata.plan_dir for it. Nothing can carry the tracker ref." >&2
  exit 1
fi
echo "ok: resolved plan epic $EPIC"

ROW="$(bd show "$EPIC" --json 2>/dev/null || true)"
[ -n "$ROW" ] || { echo "INCONCLUSIVE: bd show $EPIC returned nothing" >&2; exit 2; }

printf '%s' "$ROW" | python3 -c '
import json, re, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"INCONCLUSIVE: bd output is not JSON: {e}", file=sys.stderr); raise SystemExit(2)
if isinstance(d, list):
    d = d[0] if d else {}
if d.get("error"):
    print(f"INCONCLUSIVE: bd reported {d['error']!r}", file=sys.stderr); raise SystemExit(2)
ref = (d.get("external_ref") or "").strip()
if not ref:
    print(f"FAIL: epic {d.get('id')} carries NO external_ref — the coarse tracker is "
          f"structurally invisible to `upstream.py closable`, which groups beads by that "
          f"field.", file=sys.stderr)
    raise SystemExit(1)
# It must be PARSEABLE to an issue number, or nothing can map it back (REQ-BUP-062/063).
m = re.search(r"(?:issues/|gh-|#)(\d+)$|^(\d+)$", ref)
if not m:
    print(f"FAIL: epic external_ref {ref!r} does not parse to an issue number; an "
          f"uninterpretable ref is a finding, not a mapping (REQ-BUP-063).", file=sys.stderr)
    raise SystemExit(1)
n = m.group(1) or m.group(2)
print(f"PASS: epic {d.get('id')} carries tracker ref {ref} (issue #{n})")
'
