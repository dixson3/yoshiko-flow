#!/usr/bin/env bash
# ctl-199b-halt (SC10) — a FAILING re-check HALTS the close chain.
#
# OBSERVED ON A FIXTURE, never grepped from prose. A token in SKILL.md proving that a halt is
# *documented* is exactly the class of evidence this plan exists to replace: "a step with no
# exit code is not a step, and an exit code that reads the wrong thing is worse than none".
# REQ-COMPLETE-004 records the same defect in its second form — §6.4 captured
# `close-reconcile-step`'s output and never read `$?`, so an ordering violation reported
# `inconclusive`, exited 0, and the chain walked on.
#
# So this control asserts the VERB'S EXIT CODE (which is what a caller can branch on) and
# that SKILL.md's §6.4 invocation actually branches on it.
#
# UNCOMMISSIONED-INTERFACE RULE: an absent verb is EXIT 1, never exit 2.
# Exit: 0 a failing re-check exits non-zero AND §6.4 branches on it · 1 real negative · 2 instrument
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"
PM="$REPO/skills/yf-plan/scripts/plan_manager.py"

# ---------------------------------------------------------------------------------------
# Helpers are INLINED rather than sourced from a sibling library. A shared file under
# assets/ would be an artifact no issue's `touches:` declares — and amending the plan's
# Epics to declare it would invalidate the approval fingerprint mid-execution. Issue 2.1 is
# the sole writer of all five ctl-199b-* files, so the single-writer rule still holds.
# ---------------------------------------------------------------------------------------
# require_verb — the UNCOMMISSIONED-INTERFACE RULE in one place.
# An absent `recheck-criteria` is a REAL NEGATIVE (exit 1), never argparse's exit 2.
require_verb() {
  [ -r "$PM" ] || { echo "INCONCLUSIVE: plan_manager.py unreadable: $PM" >&2; exit 2; }
  if ! uv run "$PM" --help 2>&1 | grep -q 'recheck-criteria'; then
    echo "FAIL: plan_manager.py exposes no 'recheck-criteria' verb." >&2
    echo "      The uncommissioned-interface rule maps this to a REAL NEGATIVE (exit 1):" >&2
    echo "      the verb is absent, which is a different claim from the instrument failing." >&2
    exit 1
  fi
}

# mk_fixture <dir>  — Success Criteria rows on stdin. Builds a minimal conformant bundle.
mk_fixture() {
  local dir="$1"; mkdir -p "$dir"
  local rows; rows="$(cat)"
  cat > "$dir/plan.md" <<PLANEOF
---
type: Plan
okf_spec: OKF-PLAN
id: plan-997-fixture-recheck
author: fixture
created: '2026-01-01'
status: executing
---
# Plan: pinned recheck fixture

**ID:** plan-997-fixture-recheck
**Author:** fixture
**Created:** 2026-01-01
**Status:** executing

## Objective
A pinned fixture for the completion-time re-check. Never live plan state.

## Motivation
A control written against live state is not a control.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Investigation Findings
None.

## Approach
None.

## Epics
### Epic 1: fixture
- Issue 1.1: do the thing
  - touches: \`src/a.py\`

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | none | low | none |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
${rows}
PLANEOF
  printf '# Log\n\n## 2026-01-01\n\n- executing: fixture\n' > "$dir/log.md"
}


require_verb
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mk_fixture "$tmp/fx" <<'ROWS'
| SC1 | holds | `true` → exit 0 | 1.1 |
| SC2 | is FALSE — the chain must halt on it | `false` → exit 0 | 1.1 |
ROWS

uv run "$PM" recheck-criteria "$tmp/fx" --json >/dev/null 2>&1
RC=$?
if [ "$RC" -eq 0 ]; then
  echo "FAIL: a re-check with a FALSE criterion exited 0 — nothing downstream can halt on it" >&2
  exit 1
fi
if [ "$RC" -eq 2 ]; then
  echo "FAIL: a re-check with a FALSE criterion returned 2 (INCONCLUSIVE), not 1." >&2
  echo "      INCONCLUSIVE maps to warn and must NOT halt; a real FALSE must exit 1." >&2
  exit 1
fi
echo "ok: a failing re-check exits $RC (a real negative)"

# The caller must BRANCH on that exit code, not merely capture it (REQ-COMPLETE-004).
SKILL="$REPO/skills/yf-plan/SKILL.md"
[ -r "$SKILL" ] || { echo "INCONCLUSIVE: SKILL.md unreadable" >&2; exit 2; }
python3 - "$SKILL" <<'PYEOF'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
if "recheck-criteria" not in text:
    print("FAIL: SKILL.md §6.4 never invokes recheck-criteria", file=sys.stderr)
    raise SystemExit(1)
# Find the invocation and require an exit-code read near it: `$?` captured into a var that a
# subsequent `if [ ... -ne 0 ]` branches on.
idx = text.index("recheck-criteria")
window = text[idx: idx + 900]
if not re.search(r'_RC=\$\?', window) or not re.search(
        r'if \[ "\$[A-Z_]*RC" -ne 0 \]', window):
    print("FAIL: SKILL.md captures recheck-criteria's output but does not BRANCH on its exit "
          "code. An exit code nothing reads is the REQ-COMPLETE-004 defect in its second form.",
          file=sys.stderr)
    raise SystemExit(1)
print("ok: SKILL.md §6.4 branches on recheck-criteria's exit code")
PYEOF
# READ THE HEREDOC'S EXIT CODE. Without this the block printed its FAIL to stderr, the
# script fell through, and the final echo made the control exit 0 — a FALSE GREEN inside the
# control whose whole subject is "an exit code nothing reads is not a step". Caught by
# reading the output rather than the exit code, which is the same discipline in reverse.
SKILL_RC=$?
if [ "$SKILL_RC" -ne 0 ]; then
  exit "$SKILL_RC"
fi
echo "PASS: a failing re-check exits non-zero and the close chain branches on it"
