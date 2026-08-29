#!/usr/bin/env bash
# SC11 / SC11c — `check-recipe-row.sh <token>`: the named recipe row is WIRED, not merely
# written. Asserts the row exists in CHANGE-VALIDATION.md §1 AND appears in a FULL-tier run's
# JSON.
#
# A BARE FULL-TIER RUN CANNOT SHOW THIS. It already exits 0 today, before the row exists — so
# "the full tier is green" is true in both worlds and carries no information about wiring.
#
# THE MATCH IS "id EQUALS the token OR cmd CONTAINS it", A WHOLE-ROW-LINE MATCH, and it must
# be defined that way because the two criteria that use it pass DIFFERENT things:
#
#   * SC11  passes the row ID `okf-index-drift`, which never appears in the underscored
#           filename `check_okf_index_drift.py` — so a cmd-only implementation makes SC11 false;
#   * SC11c passes FILENAMES (`test_recheck_criteria`, `test_index_members`) that Issue 3.2a
#           does not declare as ids — so an id-only implementation makes SC11c false.
#
# Either one alone breaks a shipped criterion. The disjunction is the requirement, not a
# convenience.
#
# EXIT  0 present in the manifest AND in a FULL-tier run  ·  1 absent from either  ·  2 could not run
CHECK_NAME=check-recipe-row
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

TOKEN="${1:-}"
[ -n "${TOKEN}" ] || ck_inconclusive "usage: check-recipe-row.sh <row-id-or-cmd-substring>"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
MANIFEST="${TREE}/CHANGE-VALIDATION.md"
[ -f "${MANIFEST}" ] || ck_inconclusive "no CHANGE-VALIDATION.md at ${MANIFEST}"
ck_need uv
CK_RC=0

# --- (a) the row is in the manifest -------------------------------------------------
# A §1 row is a GFM table line: `| <id> | <tier> | <cmd> | ...`. Match the whole row line, so
# a mention of the token in the manifest's PROSE — which is append-only and full of
# discussion — can never satisfy this.
if ! awk -v tok="${TOKEN}" '
      /^\|/ {
        n = split($0, c, "|")
        id = c[2]; gsub(/^[ \t`]+|[ \t`]+$/, "", id)
        if (id == tok) { found = 1 }
        for (i = 2; i <= n; i++) if (index(c[i], tok)) cmdhit = 1
      }
      END { exit (found || cmdhit) ? 0 : 1 }
    ' "${MANIFEST}"; then
  ck_fail "no CHANGE-VALIDATION.md row whose id EQUALS \`${TOKEN}\` or whose cmd CONTAINS it"
  # SHORT-CIRCUIT. (b) below runs the FULL tier, which is the multi-minute suite §6.1.5
  # reserves for once per land. Paying it to confirm a row we already know is absent would
  # make the RED arm of this check cost minutes — and a check nobody can afford to run is a
  # check that gets skipped.
  exit 1
fi

# --- (b) the row actually RUNS in the FULL tier -------------------------------------
# The manifest half alone would be satisfied by a row that is present and unreachable —
# mis-tiered, or scoped out. Reading it back from the engine's own JSON is what makes this
# "wired" rather than "written".
ENGINE="${TREE}/skills/yf-change-validation/scripts/change_validation.py"
[ -f "${ENGINE}" ] || ENGINE="$(yf skill-dir yf-change-validation 2>/dev/null)/scripts/change_validation.py"
[ -f "${ENGINE}" ] || ck_inconclusive "cannot resolve change_validation.py"

# CACHED ACROSS INVOCATIONS, BY DEFAULT — not only when a caller sets YF_FULL_TIER_JSON.
#
# WHY THE DEFAULT IS NECESSARY, measured. SC11 and SC11c call this script three times between
# them, and the FULL tier is the multi-minute suite. `recheck-criteria` runs each criterion in
# a FRESH SUBPROCESS with a 300s timeout, and SC11c chains TWO invocations in one cell — so it
# paid two full suites (~480s) and TIMED OUT, which the plan-056 engine correctly reported as
# `HARNESS_INCOMPLETE` rather than as a pass. An opt-in cache could not help: a criterion's
# `Verification` cell is a bare command string with NO WAY TO SET AN ENVIRONMENT VARIABLE, so
# the lever existed and was unreachable from the one binding that needed it.
#
# THE CACHE IS KEYED ON THE TREE FINGERPRINT, and that is what makes it safe rather than merely
# fast. A stale FULL-tier result would let this script report a row as WIRED when the tree no
# longer wires it — the precise false-green this check exists to prevent. So the key is
# HEAD + the hash of `git status --porcelain`: ANY change, staged, unstaged or untracked,
# produces a different key and therefore a miss. A second guard caps age at 30 minutes, so a
# fingerprint collision or a clock oddity still cannot serve an ancient result.
_fingerprint() {
  local head dirty
  head="$(git -C "${TREE}" rev-parse HEAD 2>/dev/null || echo nohead)"
  dirty="$(git -C "${TREE}" status --porcelain 2>/dev/null | shasum | cut -d' ' -f1)"
  printf '%s-%s' "${head:0:12}" "${dirty:0:12}"
}
CACHE="${YF_FULL_TIER_JSON:-${TMPDIR:-/tmp}/yf-full-tier-$(_fingerprint).json}"

FULL_JSON=""
if [ -s "${CACHE}" ]; then
  # `find -mmin -30` is the portable age test; an older file is simply not matched.
  if [ -n "$(find "${CACHE}" -mmin -30 2>/dev/null)" ]; then
    FULL_JSON="$(cat "${CACHE}")"
    echo "${CHECK_NAME}: reusing a FULL-tier result for this exact tree state" >&2
  fi
fi
if [ -z "${FULL_JSON}" ]; then
  FULL_JSON="$( (cd "${TREE}" && uv run "${ENGINE}" run --tier full --json 2>/dev/null) )"
  # Write the cache only for a NON-EMPTY result, so a crashed run cannot poison the next call.
  [ -n "${FULL_JSON}" ] && printf '%s' "${FULL_JSON}" > "${CACHE}" 2>/dev/null || true
fi
[ -n "${FULL_JSON}" ] || ck_inconclusive "the FULL-tier run produced no JSON"

if ! printf '%s' "${FULL_JSON}" | grep -qF "${TOKEN}"; then
  ck_fail "\`${TOKEN}\` is in the manifest but does NOT appear in a FULL-tier run's JSON — the row is written, not wired"
fi

ck_done "\`${TOKEN}\` is present in CHANGE-VALIDATION.md and appears in a FULL-tier run"
