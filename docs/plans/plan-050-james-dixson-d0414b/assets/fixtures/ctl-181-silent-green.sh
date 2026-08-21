#!/usr/bin/env bash
# ctl-181-silent-green — REQ-DATA-061 / #181. SC6.
#
# A FIXTURE per Issue 0.2's definition: exits 0 iff the asserted behaviour holds. The asserted
# behaviour is that `doc_lint.py`'s `classify` PREFLIGHT separates FOUR classes that the lint
# itself reports identically, and carries the mode's own exit contract.
#
# FIVE SCENARIOS ACROSS FOUR CLASSES — the two `not-selected` arms are different ENTRY POINTS,
# not one arm each:
#
#   1  --root <a bundle COPIED outside docs/plans/>   -> not-selected   exit 1   (#181's TITLED scenario)
#   2  --path <a real but unselected file>            -> not-selected   exit 1
#   3  --path <a nonexistent file>                    -> no-such-path   exit 1
#   4  --path <a selected but EMPTY file>             -> empty          exit 0   (the LINTABLE side)
#   5  --path <a selected non-empty file>             -> selected       exit 0   (the POSITIVE arm)
#
# THE EXIT IS ASSERTED ON ARM 4 TOO, not only the class. Pass-11 C111 measured that a
# classes-only fixture is satisfied by a classifier that exits 1 on `empty` — silently
# restoring the skip semantics C96 removed. `empty` is on the LINTABLE side deliberately: a
# selected-but-empty plan.md FAILS its schema and the lint already says so loudly (measured: 6
# E findings, exit 1). Skipping it would manufacture a new silent green inside the fix for a
# silent green.
#
# ARM 5 IS MANDATORY. Without it the fixture is satisfied by a classifier that never returns 0
# — one that skips linting everything, which is #181 made total (pass-10 C102).
#
# Against the unfixed tree there is no `classify` mode at all, so this is RED for the strongest
# possible reason. Arm 6 additionally records the byte-identical PASS that EXP-003 measured —
# the defect being closed — and asserts it is STILL true of the lint, because REQ-DATA-061
# forbids the classifier from changing the lint's own reporting.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
LINT="${YF_TREE}/_shared/doc_lint.py"
[ -f "${LINT}" ] || { echo "ctl-181: HARNESS — no linter at ${LINT}" >&2; exit 2; }

work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT

# A real plan bundle, COPIED OUTSIDE docs/plans/ — #181's titled scenario.
mkdir -p "${work}/elsewhere/some-bundle"
SRC_BUNDLE="${YF_TREE}/docs/plans/plan-049-james-dixson-725bc0"
[ -d "${SRC_BUNDLE}" ] || { echo "ctl-181: HARNESS — no source bundle at ${SRC_BUNDLE}" >&2; exit 2; }
cp "${SRC_BUNDLE}/plan.md" "${work}/elsewhere/some-bundle/plan.md"

# A selected-but-EMPTY file, inside a real bundle root so path routing selects it.
mkdir -p "${work}/root/docs/plans/plan-000-empty-ffffff"
: > "${work}/root/docs/plans/plan-000-empty-ffffff/plan.md"

fail=0
say() { printf 'ctl-181:   %s\n' "$*" >&2; }

# classify <expected-class> <expected-exit> <label> -- <args...>
classify() {
  local want_class="$1" want_rc="$2" label="$3"; shift 4
  local out rc got
  out="$( cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${LINT}" --classify --json "$@" 2>&1 )"
  rc=$?
  got="$( printf '%s' "${out}" | python3 -c '
import json,sys
try:
    print(json.load(sys.stdin).get("class",""))
except Exception:
    print("")
' 2>/dev/null )"
  if [ "${got}" != "${want_class}" ]; then
    say "${label}: class was '${got}', expected '${want_class}'"
    say "  raw: $(printf '%s' "${out}" | head -c 300)"
    fail=1
  fi
  if [ "${rc}" != "${want_rc}" ]; then
    say "${label}: exit was ${rc}, expected ${want_rc}"
    fail=1
  fi
}

classify not-selected 1 "arm 1 (--root, a bundle copied outside docs/plans/)" -- \
  --root "${work}/elsewhere" --path "${work}/elsewhere/some-bundle/plan.md"
classify not-selected 1 "arm 2 (--path, real but unselected)" -- \
  --path "${YF_TREE}/docs/plans/plan-049-james-dixson-725bc0/index.md"
classify no-such-path 1 "arm 3 (--path, nonexistent)" -- \
  --path "${YF_TREE}/docs/plans/NO-SUCH/plan.md"
classify empty 0 "arm 4 (--path, selected but EMPTY — the LINTABLE side)" -- \
  --root "${work}/root" --path "${work}/root/docs/plans/plan-000-empty-ffffff/plan.md"
classify selected 0 "arm 5 (--path, selected and non-empty — the POSITIVE arm)" -- \
  --path "${YF_TREE}/docs/plans/plan-049-james-dixson-725bc0/plan.md"

# ---- arm 6: the LINT itself is unchanged -----------------------------------------------
# EXP-003's measurement, re-run: an unselected path and a NONEXISTENT one return
# BYTE-IDENTICAL lint verdicts. That is the defect #181 names, and it must STILL be true —
# REQ-DATA-061 fixes it with a preflight, not by mutating the lint's reporting. If this arm
# ever goes false, the classifier leaked into the lint and SC7's corpus figure is invalid.
lint_json() {
  ( cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${LINT}" --json --path "$1" 2>/dev/null ) \
    | python3 -c '
import json,sys
d = json.load(sys.stdin)
print(d["files_checked"], d["verdict"])
'
}
u="$( lint_json "${YF_TREE}/docs/plans/plan-049-james-dixson-725bc0/index.md" )"
m="$( lint_json "${YF_TREE}/docs/plans/NO-SUCH/plan.md" )"
if [ "${u}" != "${m}" ]; then
  say "arm 6: the LINT's own reporting changed — unselected='${u}' nonexistent='${m}'."
  say "  REQ-DATA-061 forbids this: the classifier is a PREFLIGHT, not a lint change."
  fail=1
elif [ "${u}" != "0 PASS" ]; then
  say "arm 6: VACUOUS — expected the lint to still report '0 PASS' for both, got '${u}'"
  exit 2
fi

if [ "${fail}" -eq 0 ]; then
  echo "ctl-181: classify separates 4 classes across 5 entry points, with the mode's exit"
  echo "ctl-181: contract on every arm; the lint's own reporting is unchanged (still '0 PASS'"
  echo "ctl-181: for both an unselected and a nonexistent path — EXP-003's measurement)"
fi
exit "${fail}"
