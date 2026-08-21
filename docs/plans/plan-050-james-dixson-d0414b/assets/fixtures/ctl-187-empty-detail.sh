#!/usr/bin/env bash
# ctl-187-empty-detail — REQ-DATA-063 / #187.
#
# A FIXTURE per Issue 0.2's definition: exits 0 iff the asserted behaviour holds. The asserted
# behaviour is that each extracted issue carries its continuation prose in a `detail` field,
# MINUS the sub-key bullets the parser already consumes (`depends-on:`, `resolves-upstream:`).
#
# Pre-fix there is no such field at all, so this is RED for the strongest possible reason.
#
# Tree under test: $YF_TREE (set by redcheck.sh).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
EXTRACT="${YF_TREE}/_shared/plan_extract.py"
PLAN="${HERE}/corpus/ctl-187-plan.md"

[ -f "${EXTRACT}" ] || { echo "ctl-187: HARNESS — no extractor at ${EXTRACT}" >&2; exit 2; }
[ -f "${PLAN}" ]    || { echo "ctl-187: HARNESS — no fixture plan at ${PLAN}" >&2; exit 2; }

work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT
mkdir -p "${work}/docs/plans/plan-187-fixture-bbbbbb"
cp "${PLAN}" "${work}/docs/plans/plan-187-fixture-bbbbbb/plan.md"

out="${work}/out.json"
if ! (cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${EXTRACT}" \
        "${work}/docs/plans/plan-187-fixture-bbbbbb" --json) > "${out}" 2>"${work}/err"; then
  echo "ctl-187: extractor exited non-zero" >&2
  sed 's/^/ctl-187:   /' "${work}/err" >&2
  exit 1
fi

python3 - "${out}" <<'PY'
import json, sys
doc = json.load(open(sys.argv[1]))
doc = doc[0] if isinstance(doc, list) else doc
by = {i["id"]: i for i in doc["issues"]}

if set(by) != {"1.1", "1.2", "1.3"}:
    print(f"ctl-187: VACUOUS — expected issues 1.1/1.2/1.3, got {sorted(by)}", file=sys.stderr)
    sys.exit(2)

bad = []
for iid in ("1.1", "1.2", "1.3"):
    if "detail" not in by[iid]:
        bad.append(f"issue {iid} carries no `detail` field at all")
if bad:
    for b in bad:
        print(f"ctl-187: {b}", file=sys.stderr)
    sys.exit(1)

want = {
    # continuation prose only; the parsed sub-key bullets are excluded
    "1.1": ["THE FIRST CONTINUATION LINE", "A SECOND CONTINUATION LINE"],
    "1.2": ["DETAIL PROSE BEFORE THE SUBKEYS", "DETAIL PROSE AFTER THE SUBKEYS"],
    "1.3": [],
}
for iid, needles in want.items():
    d = by[iid]["detail"]
    for n in needles:
        if n not in d:
            bad.append(f"issue {iid}: `detail` is missing its continuation prose {n!r}; got {d!r}")
    # The SUB-KEY BULLETS MUST NOT APPEAR. The same bytes must not be reachable both as a
    # structured edge and as prose — that exclusion is what makes `detail` a schema field
    # rather than a raw-text dump.
    for forbidden in ("depends-on:", "resolves-upstream:"):
        if forbidden in d:
            bad.append(f"issue {iid}: `detail` leaks the parsed sub-key {forbidden!r}; got {d!r}")

# 1.3 has sub-keys and NOTHING else: its detail must be EMPTY, and empty is a valid value.
if by["1.3"]["detail"].strip():
    bad.append(f"issue 1.3: `detail` should be empty (sub-keys only), got {by['1.3']['detail']!r}")

# The edges must still be read — `detail` must not have eaten them.
for iid in ("1.2", "1.3"):
    if by[iid]["depends_on"] != ["1.1"]:
        bad.append(f"issue {iid}: depends_on should still be ['1.1'], got {by[iid]['depends_on']}")

if bad:
    print(f"ctl-187: {len(bad)} failure(s):", file=sys.stderr)
    for b in bad:
        print(f"ctl-187:   {b}", file=sys.stderr)
    sys.exit(1)
print("ctl-187: every issue carries its continuation prose in `detail`, sub-keys excluded")
PY
