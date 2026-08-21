#!/usr/bin/env bash
# ctl-186-masked-title — REQ-DATA-062 / #186.
#
# A FIXTURE, per Issue 0.2's definition: EXITS 0 IFF THE ASSERTED BEHAVIOUR HOLDS. Here the
# asserted behaviour is that every title `plan_extract.py` emits — issue titles AND epic names —
# equals its source line's span VERBATIM, inline code spans included.
#
# Pre-fix the extractor captures the title from the MASKED line, so every backticked term is
# blanked to spaces and the output is corrupt while `--strict` reports `unparsed: []` and exit 0.
#
# BOTH capture sites are asserted. Pass 11 measured the plan's earlier "the single call site"
# claim FALSE by spike: an epic name carrying a code span blanks identically. A one-site fix
# ships half of #186, and this fixture is what catches that.
#
# Tree under test: $YF_TREE (set by redcheck.sh; defaults to the plan's execution worktree).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
EXTRACT="${YF_TREE}/_shared/plan_extract.py"
PLAN="${HERE}/corpus/ctl-186-plan.md"

[ -f "${EXTRACT}" ] || { echo "ctl-186: HARNESS — no extractor at ${EXTRACT}" >&2; exit 2; }
[ -f "${PLAN}" ]    || { echo "ctl-186: HARNESS — no fixture plan at ${PLAN}" >&2; exit 2; }

work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT
mkdir -p "${work}/docs/plans/plan-186-fixture-aaaaaa"
cp "${PLAN}" "${work}/docs/plans/plan-186-fixture-aaaaaa/plan.md"

out="${work}/out.json"
if ! (cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${EXTRACT}" \
        "${work}/docs/plans/plan-186-fixture-aaaaaa" --json) > "${out}" 2>"${work}/err"; then
  # A non-zero extractor exit is a FAILED ASSERTION for this fixture, not a harness failure:
  # the naive `ln = raw` repair was measured at pass 10 producing a spurious edge and driving
  # --strict non-zero, and this fixture must catch that too rather than report INCONCLUSIVE.
  echo "ctl-186: extractor exited non-zero" >&2
  sed 's/^/ctl-186:   /' "${work}/err" >&2
  exit 1
fi

python3 - "${out}" "${PLAN}" <<'PY'
import json, re, sys
doc = json.load(open(sys.argv[1]))
doc = doc[0] if isinstance(doc, list) else doc
src = open(sys.argv[2]).read().split("\n")

expected_issue = {}
expected_epic = {}
for ln in src:
    m = re.match(r'^- Issue ([0-9]+\.[0-9]+[a-z]?): (.*)$', ln)
    if m:
        expected_issue[m.group(1)] = m.group(2)
    m = re.match(r'^### Epic ([0-9]+): (.*)$', ln)
    if m:
        expected_epic[m.group(1)] = m.group(2)

bad = []
for i in doc["issues"]:
    want = expected_issue.get(i["id"])
    if want is None:
        bad.append(f"issue {i['id']}: extracted but absent from the source")
    elif i["title"] != want:
        bad.append(f"issue {i['id']} title\n    want: {want!r}\n    got : {i['title']!r}")
for e in doc["epics"]:
    want = expected_epic.get(e["num"])
    if want is None:
        bad.append(f"epic {e['num']}: extracted but absent from the source")
    elif e["name"] != want:
        bad.append(f"epic {e['num']} name\n    want: {want!r}\n    got : {e['name']!r}")

missing = set(expected_issue) - {i["id"] for i in doc["issues"]}
if missing:
    bad.append(f"issues declared in the source but never extracted: {sorted(missing)}")

# GUARD THE GUARD. A fixture that asserts over an empty extraction passes vacuously — the
# exact class this plan exists to close. The fixture plan carries 3 issues and 1 epic, and at
# least one title on each side carries an inline code span, so a masked read MUST differ.
if len(doc["issues"]) != 3 or len(doc["epics"]) != 1:
    print(f"ctl-186: VACUOUS — expected 3 issues / 1 epic, got "
          f"{len(doc['issues'])}/{len(doc['epics'])}", file=sys.stderr)
    sys.exit(2)
if not any("`" in t for t in list(expected_issue.values()) + list(expected_epic.values())):
    print("ctl-186: VACUOUS — no source title carries an inline code span", file=sys.stderr)
    sys.exit(2)

if bad:
    print(f"ctl-186: {len(bad)} title(s) do not match their source verbatim:", file=sys.stderr)
    for b in bad:
        print(f"ctl-186:   {b}", file=sys.stderr)
    sys.exit(1)
print("ctl-186: every extracted title matches its source line verbatim")
PY
