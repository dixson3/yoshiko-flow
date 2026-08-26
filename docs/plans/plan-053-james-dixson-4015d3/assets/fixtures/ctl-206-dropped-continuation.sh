#!/usr/bin/env bash
# ctl-206-dropped-continuation — REQ-DATA-063 as amended by plan-053 / #206.
#
# A FIXTURE per redcheck.sh's definition: exits 0 iff the asserted behaviour holds.
#
# IT ASSERTS **FIVE** THINGS, NOT TWO (EXP-001):
#
#   1. RECOVERY, drop shape 1 — a continuation line that is ENTIRELY one inline code span
#      reaches `detail`. Pre-fix the capture gate at plan_extract.py:473 tests the MASKED
#      line, which is all whitespace for such a line, so it is dropped silently while
#      `--strict` reports `unparsed: []` and exit 0.
#   2. RECOVERY, drop shape 2 — an INDENTED fenced block reaches `detail` VERBATIM, minus the
#      opening fence's indent, so internal indentation survives.
#   3. ADVERSARIAL — a `depends-on:` written inside a code span produces NO edge.
#   4. ADVERSARIAL — a fence containing `- Issue 9.9:` / `- depends-on: 9.9` / `- touches:`
#      produces no phantom issue, no edge and no touches entry.
#   5. THE COLUMN-0 FENCE BOUNDARY — a column-0 fence inside `## Epics` is plan body and is
#      NOT collected into the preceding issue's `detail`.
#
# ASSERTIONS 3, 4 AND 5 ARE INVARIANT GUARDS, NOT RED-BEARERS. Measured on the unfixed tree:
# all three already hold. The RED comes from 1 and 2 alone. 5 is here because a NAIVE fix
# ("collect every fenced line") breaks it — it swallows a plan-body fence into the last
# issue's bead description, introducing a NEW silent-corruption shape while closing an old
# one. The guard gets a test before the implementation gets written.
#
# DO NOT REUSE ctl-187's BLANKET `"depends-on:" not in detail` ASSERTION. Issue 1.3 of the
# fixture plan legitimately carries that text as PROSE — it is assertion 3's whole point — so
# the blanket form would fail on correct behaviour.
#
# Tree under test: $YF_TREE (set by redcheck.sh).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
EXTRACT="${YF_TREE}/_shared/plan_extract.py"
PLAN="${HERE}/corpus/ctl-206-plan.md"

[ -f "${EXTRACT}" ] || { echo "ctl-206: HARNESS — no extractor at ${EXTRACT}" >&2; exit 2; }
[ -f "${PLAN}" ]    || { echo "ctl-206: HARNESS — no fixture plan at ${PLAN}" >&2; exit 2; }

work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT
mkdir -p "${work}/docs/plans/plan-206-fixture-cccccc"
cp "${PLAN}" "${work}/docs/plans/plan-206-fixture-cccccc/plan.md"

out="${work}/out.json"
if ! (cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${EXTRACT}" \
        "${work}/docs/plans/plan-206-fixture-cccccc" --json) > "${out}" 2>"${work}/err"; then
  echo "ctl-206: extractor exited non-zero" >&2
  sed 's/^/ctl-206:   /' "${work}/err" >&2
  exit 1
fi

python3 - "${out}" <<'PY'
import json, sys
doc = json.load(open(sys.argv[1]))
doc = doc[0] if isinstance(doc, list) else doc
by = {i["id"]: i for i in doc["issues"]}

# A fixture that silently stops describing the document it was written against is worse than
# no fixture: exit 2 (HARNESS), never 0 and never 1.
if set(by) != {"1.1", "1.2", "1.3", "1.4"}:
    print(f"ctl-206: VACUOUS — expected issues 1.1-1.4, got {sorted(by)}", file=sys.stderr)
    sys.exit(2)

bad = []

# --- 1. RECOVERY, drop shape 1: the inline-code-only continuation line -------------------
d11 = by["1.1"]["detail"]
if "RECOVERED_CODE_ONLY_LINE" not in d11:
    bad.append("assertion 1 (drop shape 1): issue 1.1's `detail` is missing the "
               "inline-code-only continuation line; got %r" % d11)
if "ORDINARY PROSE ON THE NEXT LINE." not in d11:
    bad.append("assertion 1: issue 1.1 lost its ORDINARY prose continuation too; got %r" % d11)

# --- 2. RECOVERY, drop shape 2: the indented fenced block, VERBATIM ----------------------
d12 = by["1.2"]["detail"]
if "RECOVERED_FENCE_LINE_ONE" not in d12:
    bad.append("assertion 2 (drop shape 2): issue 1.2's `detail` is missing the indented "
               "fence's content; got %r" % d12)
if "PROSE BEFORE THE FENCE." not in d12:
    bad.append("assertion 2: issue 1.2 lost the prose preceding its fence; got %r" % d12)
# VERBATIM, minus the OPENING fence's indent — so the deeper internal indentation survives.
# A `.strip()`-per-line collector passes the containment check above and fails this one,
# which is why the assertion is on the INDENT and not merely on the text.
if "    RECOVERED_FENCE_INDENTED_LINE" not in d12:
    bad.append("assertion 2: the fence's INTERNAL indentation did not survive — `detail` "
               "must carry the block verbatim minus the OPENING fence's indent; got %r" % d12)

# --- 3. ADVERSARIAL: a code-span `depends-on:` is prose, never an edge -------------------
if by["1.3"]["depends_on"]:
    bad.append("assertion 3: issue 1.3's code-span `depends-on:` produced an edge %r — "
               "masking must still govern every PARSING branch" % by["1.3"]["depends_on"])
if "depends-on: 1.1" not in by["1.3"]["detail"]:
    bad.append("assertion 3: issue 1.3's code-span text should survive as PROSE in `detail`; "
               "got %r" % by["1.3"]["detail"])

# --- 4. ADVERSARIAL: a fence full of issue/sub-key shapes yields nothing -----------------
if "9.9" in by:
    bad.append("assertion 4: a PHANTOM issue 9.9 was extracted from inside a fence")
if by["1.4"]["depends_on"] != ["1.1"]:
    bad.append("assertion 4: issue 1.4's depends_on should be exactly ['1.1'] (its real "
               "sub-key), got %r" % by["1.4"]["depends_on"])
if by["1.4"].get("touches"):
    bad.append("assertion 4: the fenced `- touches:` line produced a real touches entry %r"
               % by["1.4"]["touches"])
for e in doc["edges"]:
    if "9.9" in (e["from"], e["to"]):
        bad.append("assertion 4: a phantom edge to 9.9 was produced: %r" % e)

# --- 5. THE COLUMN-0 FENCE BOUNDARY -----------------------------------------------------
# The column-0 fence sits AFTER issue 1.4 but still inside `## Epics`. A column-0 fence
# terminates nothing, so a naive collector attributes it to the last open issue.
for iid, issue in by.items():
    if "COLUMN_ZERO_FENCE_MUST_NOT_BE_COLLECTED" in issue["detail"]:
        bad.append("assertion 5 (THE GUARD): the COLUMN-0 plan-body fence was swallowed into "
                   "issue %s's `detail` — a naive fence fix introduces this NEW "
                   "silent-corruption shape while closing an old one; got %r"
                   % (iid, issue["detail"]))

# The silent-loss signature must be gone in BOTH directions: nothing may have moved into
# `unparsed[]` either. The fix recovers content; it does not reclassify it as unreadable.
if doc["unparsed"]:
    bad.append("the fix pushed content into `unparsed[]`: %r" % doc["unparsed"])

if bad:
    print(f"ctl-206: {len(bad)} failure(s):", file=sys.stderr)
    for b in bad:
        print(f"ctl-206:   {b}", file=sys.stderr)
    sys.exit(1)
print("ctl-206: both drop shapes recovered, both adversarial shapes edge-free, "
      "column-0 fence boundary held")
PY
