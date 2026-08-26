#!/usr/bin/env bash
# ctl-214-id-collision — the REQ-PLAN-073 double allocation (#214 / D-8).
#
# A FIXTURE per redcheck.sh's definition: exits 0 iff the asserted behaviour holds.
#
# WHAT IT ASSERTS
#   1. Every surviving LIVE `REQ-PLAN-073` site is on the explicit STAMP-MEANING ALLOWLIST
#      enumerated below, file by file. No site outside it may survive.
#   2. `REQ-PLAN-079` RESOLVES — a definition line exists for it. Retiring an id into thin
#      air would satisfy assertion 1 while leaving every moved citation dangling.
#   3. The two DEFINITIONS are distinct and each resolves to exactly one requirement.
#
# WHY AN ALLOWLIST AND NOT A PREDICATE. NO GREP CAN DECIDE MEANING (pass-2 C18). An assertion
# phrased "returns only stamp-meaning sites" is unimplementable — the two meanings are
# distinguished by what the surrounding prose is ABOUT, which is not a lexical property. So
# the site set is ENUMERATED here, and any drift in either direction fails.
#
# THE ENUMERATION IS THE POINT — NO COUNT LITERAL. D-8's own figure moved three times across
# three passes (3, then 12, then 14, measured 15 at pass 3). A count that drifts is the same
# moving-fact defect as #221, so this fixture records the SITES and the prose records nothing.
#
# WHY IT IS SCOPED REPO-WIDE. SC15's earlier `SPEC.md`-only grep would have PASSED while 11
# stale citations survived, and its first revision would have passed while `REQ-YF-PRE-004a`
# — a live normative requirement at the repo-root `SPEC.md:919` — still pointed at the
# retired id. Two successive narrower scopes each passed while the ambiguity #214 exists to
# remove survived.
#
# `docs/plans/**` IS EXCLUDED BY DESIGN, NOT BY OVERSIGHT. Plan bundles are FROZEN RECORDS
# that are never rewritten — that is the entire basis of D-8's decision (the stamp meaning
# has 8 such records against roots' 1, which is why the ROOTS side moved). Rewriting them to
# satisfy this control would destroy the evidence the decision rests on.
#
# Tree under test: $YF_TREE (set by redcheck.sh).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
# CTL_RED=1 SELECTS THE PINNED NEGATIVE FIXTURE — the SAME signal ctl-053-spec-order uses.
# The fixture owns the location of its own pinned tree, so a driven RED is marked by ONE
# convention across every control rather than by "notice that YF_TREE looks unusual". A later
# reader asking "which REDs were DRIVEN rather than observed on the live tree?" greps for
# CTL_RED and gets all of them.
if [ "${CTL_RED:-0}" = "1" ]; then
  YF_TREE="${HERE}/corpus/ctl-214-pre-fix"
  echo "ctl-214: CTL_RED=1 — asserting against the PINNED PRE-FIX tree ${YF_TREE}" >&2
fi
cd "${YF_TREE}" || { echo "ctl-214: HARNESS — cannot cd to ${YF_TREE}" >&2; exit 2; }
[ -f SPEC.md ] || { echo "ctl-214: HARNESS — no SPEC.md at ${YF_TREE}" >&2; exit 2; }

# `grep -r`, NOT `git grep`. The control must run against a PINNED NEGATIVE FIXTURE — a plain
# directory that is not a git repository — as well as against the live tree. `git grep` works
# only on the latter, which would leave the RED undrivable.
_sites() {  # _sites -> one `path` per line, live tree only (frozen bundles excluded)
  grep -rl 'REQ-PLAN-073' . \
    --include='*.md' --include='*.py' --include='*.sh' --include='*.toml' \
    --exclude-dir='docs' --exclude-dir='.git' --exclude-dir='.worktrees' \
    --exclude-dir='target' --exclude-dir='node_modules' 2>/dev/null \
    | sed 's|^\./||' | sort -u
}
_lines() { grep -rn 'REQ-PLAN-073' "$1" 2>/dev/null; }

# ---- THE STAMP-MEANING ALLOWLIST, enumerated file by file --------------------------------
# Every entry is a site where `REQ-PLAN-073` correctly means the `stamp-tracker` requirement
# and therefore correctly survives. `yf-beads-upstream/{SPEC.md,SKILL.md}` are included and
# are named by NO OTHER PART of the plan — they were found by measuring rather than by
# reading the issue.
ALLOW=$(cat <<'EOF'
SPEC.md
skills/yf-beads-upstream/SKILL.md
skills/yf-beads-upstream/SPEC.md
skills/yf-plan/SKILL.md
skills/yf-plan/scripts/plan_manager.py
skills/yf-plan/scripts/test_stamp_tracker.py
skills/yf-plan/spec/phases.md
EOF
)

# The live tree: everything except the frozen plan bundles.
#
# A `while read` loop, NOT `mapfile`. `mapfile` is bash 4+, and macOS ships bash 3.2 as
# /bin/bash — redcheck.sh invokes fixtures with `bash "$fx"`, so a bash-4 builtin here makes
# the fixture die with `command not found` and then `HITS[@]: unbound variable`. That would
# surface as exit 2 (HARNESS), which the Issue 1.1(b) guard correctly refuses to record.
HITS=""
while IFS= read -r _f; do
  [ -n "${_f}" ] || continue
  HITS="${HITS}${_f}
"
done < <(_sites)

bad=()

# ---- 1. no surviving site outside the allowlist ------------------------------------------
while IFS= read -r f; do
  [ -n "${f}" ] || continue
  if ! printf '%s\n' "${ALLOW}" | grep -qxF "${f}"; then
    lines="$(_lines "${f}" | sed 's/^/      /')"
    bad+=("assertion 1: ${f} still cites REQ-PLAN-073 and is NOT on the stamp-meaning \
allowlist. Either the roots-meaning citation was missed, or the allowlist needs a stated \
reason for it. Sites:
${lines}")
  fi
done <<< "${HITS}"

# ---- the allowlist must not rot either ---------------------------------------------------
# A file listed here that no longer cites the id means the allowlist is describing a tree
# that no longer exists — the same drift, in the other direction.
while IFS= read -r f; do
  [ -n "${f}" ] || continue
  if ! printf '%s' "${HITS}" | grep -qxF "${f}"; then
    bad+=("assertion 1 (allowlist rot): ${f} is on the stamp-meaning allowlist but no longer \
cites REQ-PLAN-073. The allowlist describes a tree that no longer exists.")
  fi
done <<< "${ALLOW}"

# ---- 2. REQ-PLAN-079 resolves ------------------------------------------------------------
if ! grep -rqE '^- \*\*REQ-PLAN-079\*\*' skills 2>/dev/null; then
  bad+=("assertion 2: REQ-PLAN-079 has no definition line. The roots requirement was retired \
from 073 into thin air — every citation moved to 079 now dangles, which is the SAME ambiguity \
#214 exists to remove, relocated rather than resolved.")
fi

# ---- 3. each id resolves to exactly ONE requirement ---------------------------------------
# The collision itself: two DEFINITION lines sharing one id. Definitions are the `- **REQ-…**`
# bullet form in a SPEC.md and the bare `REQ-…:` form in a spec/*.md.
_ndef() {  # _ndef <id> -> number of DEFINITION lines for that id under skills/
  { grep -rhE "^- \*\*${1}\*\*" skills 2>/dev/null || true
    grep -rhE "^${1}:" skills 2>/dev/null || true; } | grep -c . | tr -d ' '
}
n073_def="$(_ndef REQ-PLAN-073)"
n079_def="$(_ndef REQ-PLAN-079)"
if [ "${n073_def}" -ne 1 ]; then
  bad+=("assertion 3: REQ-PLAN-073 has ${n073_def} definition line(s), expected exactly 1 \
(the stamp-tracker requirement). Two definitions IS the collision; zero means it was retired \
while citations survive.")
fi
if [ "${n079_def}" -ne 1 ]; then
  bad+=("assertion 3: REQ-PLAN-079 has ${n079_def} definition line(s), expected exactly 1 \
(the roots requirement).")
fi

if [ "${#bad[@]}" -gt 0 ]; then
  echo "ctl-214: ${#bad[@]} failure(s):" >&2
  for b in "${bad[@]}"; do echo "ctl-214:   ${b}" >&2; done
  exit 1
fi
echo "ctl-214: every surviving REQ-PLAN-073 site is stamp-meaning and allowlisted; REQ-PLAN-079 resolves; each id has exactly one definition"
