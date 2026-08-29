#!/usr/bin/env bash
# SC0c — the plan's `auto` gates WITH AN EXECUTABLE `Test:` were actually POURED as beads
# carrying `test_class: probe`.
#
# --- WHY THIS CHECK EXISTS ---------------------------------------------------------------
# The `test_class` pour directive is PROSE in the gate's `Instructions:` — `plan_extract.py`'s
# GATE_FIELD grammar cannot express the field, and `test_gates.py` defaults an absent
# `test_class` to `manual`, which the execute-start sweep never runs and which resolves
# INCONCLUSIVE. So a gate poured without it is INERT: it reads green to every structural
# instrument while establishing nothing. A directive nobody checks is the same class of defect
# as a missing directive.
#
# --- THE QUERY IS `bd list -t gate --all`, AND THAT IS THE HARD REQUIREMENT ---------------
# MEASURED: `bd list --all --json` returns the whole DB (1986 beads here) containing ZERO
# gate-typed beads and zero `metadata.test_class` — it STRUCTURALLY EXCLUDES the type this
# check counts. An instrument built on it inspects an EMPTY SET and is therefore either
# permanently red or trivially green, which is exactly the vacuity SC0c exists to prevent.
# `bd list -t gate --all --json` returns 185 gates here, 46 carrying `test_class`.
#
# `--all` IS ALSO REQUIRED ON THE `-t gate` FORM. A gate resolved early is CLOSED, and the
# default listing hides it — so a run late in execution would silently stop seeing the very
# gates it is meant to audit.
#
# --- THE DISCRIMINATOR IS `type == auto AND test_kind == executable` ----------------------
# NOT `type == auto` alone. This plan has FOUR `auto` gates: the Reconcile Gate is `auto`, IS
# poured as a bead, and carries no runnable `Test:` — so an instrument enumerating `auto` finds
# four and goes permanently red on the fourth. Hard-coding the number `3` instead would
# reintroduce the hand-maintained count this whole harness exists to eliminate, so the count is
# DERIVED from the plan on every run.
#
# EXIT  0 every auto+executable gate is poured as a bead with `test_class: probe`
#       1 at least one is missing, or is poured without `test_class: probe`
#       2 could not run (no bd, no plan, no gate beads visible at all)
CHECK_NAME=check-gates-poured-probe
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

PLAN_DIR_ARG="${1:-}"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ck_need bd
ck_need uv
ck_need python3

PLAN_DIR="$(ck_plan_dir "${PLAN_DIR_ARG}")"
[ -f "${PLAN_DIR}/plan.md" ] || ck_inconclusive "no plan.md at ${PLAN_DIR}"

EXTRACT=""
for cand in "${TREE}/_shared/plan_extract.py" "${TREE}/skills/yf-plan/scripts/plan_extract.py"; do
  [ -f "${cand}" ] && { EXTRACT="${cand}"; break; }
done
[ -n "${EXTRACT}" ] || ck_inconclusive "cannot locate plan_extract.py under ${TREE}"

PLAN_JSON="$(cd "${TREE}" && uv run "${EXTRACT}" "${PLAN_DIR}" --json 2>/dev/null)" \
  || ck_inconclusive "plan_extract.py failed on ${PLAN_DIR}"
GATE_JSON="$(bd list -t gate --all --json 2>/dev/null)" \
  || ck_inconclusive "\`bd list -t gate --all --json\` failed"

PARSER="$(mktemp)"
trap 'rm -f "${PARSER}"' EXIT
cat > "${PARSER}" <<'PYPARSE'
import json, os, sys


def load(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    return d[0] if isinstance(d, list) and d and isinstance(d[0], dict) else d


plan = load(os.environ["PLAN_JSON_FILE"])

with open(os.environ["GATE_JSON_FILE"], encoding="utf-8") as fh:
    gates_raw = json.load(fh)
if isinstance(gates_raw, dict):
    gates_raw = gates_raw.get("issues", [])
if isinstance(gates_raw, list) and gates_raw and isinstance(gates_raw[0], list):
    gates_raw = [g for chunk in gates_raw for g in chunk]

# THE VISIBILITY GUARD. Zero gate beads DB-wide is the `bd list --all` symptom, and an empty
# input set makes every assertion below vacuous.
print("GATEBEADS=%d" % len(gates_raw))

# The discriminator, derived — never a hard-coded count.
expected = [g for g in plan.get("gates", [])
            if g.get("type") == "auto" and g.get("test_kind") == "executable"]
print("EXPECTED=%d" % len(expected))

by_title = {}
for g in gates_raw:
    title = (g.get("title") or "")
    meta = g.get("metadata") or {}
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except Exception:
            meta = {}
    by_title[title] = meta

bad = []
for g in expected:
    name = g.get("name", "")
    # The pour convention is `Gate: <name>`; accept a bare `<name>` too rather than making the
    # check hostage to one title spelling.
    meta = None
    for cand in ("Gate: %s" % name, name):
        if cand in by_title:
            meta = by_title[cand]
            break
    if meta is None:
        bad.append("%s :: NOT POURED as a gate bead" % name)
        continue
    tc = meta.get("test_class")
    if tc != "probe":
        bad.append("%s :: poured with test_class=%r, not 'probe'"
                   % (name, tc if tc is not None else "<absent>"))
    else:
        print("OK=%s (cwd=%s)" % (name, meta.get("cwd", "<absent>")))

for b in bad:
    print("BAD=%s" % b)
PYPARSE

PJ="$(mktemp)"; GJ="$(mktemp)"
trap 'rm -f "${PARSER}" "${PJ}" "${GJ}"' EXIT
printf '%s' "${PLAN_JSON}" > "${PJ}"
printf '%s' "${GATE_JSON}" > "${GJ}"

RESULT="$(PLAN_JSON_FILE="${PJ}" GATE_JSON_FILE="${GJ}" python3 "${PARSER}")" \
  || ck_inconclusive "could not parse plan_extract / bd output"

GATEBEADS="$(printf '%s\n' "${RESULT}" | sed -n 's/^GATEBEADS=//p')"
EXPECTED="$(printf '%s\n' "${RESULT}" | sed -n 's/^EXPECTED=//p')"

# FAIL LOUDLY ON AN EMPTY INSPECTION (REQ-CLI-029(b)), on BOTH sides.
if [ "${GATEBEADS:-0}" -eq 0 ]; then
  ck_inconclusive "\`bd list -t gate --all --json\` returned 0 gate beads — this is the \`bd list --all\` symptom; the instrument inspected nothing and can prove nothing"
fi
if [ "${EXPECTED:-0}" -eq 0 ]; then
  ck_fail "the plan declares 0 auto+executable gates — nothing to assert, so a pass here would be vacuous"
  exit 1
fi

CK_RC=0
printf '%s\n' "${RESULT}" | sed -n 's/^OK=/'"${CHECK_NAME}"': poured probe — /p'
while IFS= read -r bad; do
  [ -n "${bad}" ] && ck_fail "${bad}"
done <<< "$(printf '%s\n' "${RESULT}" | sed -n 's/^BAD=//p')"

ck_done "${EXPECTED} auto+executable gate(s) poured with test_class: probe (${GATEBEADS} gate bead(s) visible via \`bd list -t gate --all\`)"
