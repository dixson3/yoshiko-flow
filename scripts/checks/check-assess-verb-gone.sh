#!/usr/bin/env bash
# SC23 / REQ-OKFH-001 — EVERY ENGINE-BACKED SUBCOMMAND A `SKILL.md` ADVERTISES IS DISPATCHABLE
# BY ITS ENGINE SCRIPT. Asserted over BOTH OKF skills.
#
# --- WHY THE GENERAL PROPERTY, AND NOT `! grep -q assess` -------------------------------
# The originating defect is `yf-okf` advertising an `assess` verb its engine cannot dispatch.
# A substring check for that one word is wrong in three measured ways:
#
#   1. IT IS OVER-BROAD. `yf-okf/SKILL.md` carries 11 occurrences over 10 lines — 5 bare
#      `assess`, 3 `assessment`, 3 `assessor`. Six of eleven are not the verb.
#   2. IT IS PERMANENTLY RED BY DESIGN. `yf-okf-hygiene` ABSORBS the capability, so the
#      boundary prose that documents the absorption reintroduces the substring.
#   3. IT CANNOT SEE A RELOCATION. Deleting the verb from `yf-okf` and re-advertising it,
#      still undispatchable, from `yf-okf-hygiene` satisfies a `yf-okf`-scoped grep while
#      moving the defect one directory over. That is why this check inspects BOTH skills.
#
# --- WHY `ENGINE-BACKED` IS A QUALIFIER AND NOT A LOOPHOLE -------------------------------
# Measured: `yf-okf` advertises `init check migrate assess` while `okf.py --help` dispatches
# `check migrate reindex scaffold`. `init` is advertised-and-undispatchable LEGITIMATELY — the
# SKILL.md itself says only engine-backed subcommands route to the script. A literal "every
# advertised verb dispatches" would be permanently red on a CONFORMING skill, which is the same
# trap this check exists to avoid, inverted.
#
# --- THE EXEMPTION IS DECLARED, NEVER INFERRED -------------------------------------------
# A hard-coded `init` exemption re-creates the hand-maintained list this repo keeps measuring
# as drifted. So a skill declares its non-engine-backed subcommands on a line-start marker in
# its own `SKILL.md`:
#
#     Non-engine-backed subcommands: init
#
# and this check reads that line. An UNDECLARED exemption is indistinguishable from an
# oversight — the same rule `check-req-coverage.py` states for its bug-fix carve-out — so a
# skill with no marker has an EMPTY exempt set and every advertised verb must dispatch. That is
# the fail-closed direction: the cost of forgetting the marker is a loud red, never a silent
# pass. (`Non-engine-backed subcommands: none` is the explicit spelling of "there are none".)
#
# EXIT  0 for every inspected skill, advertised-minus-exempt is a subset of dispatched
#       1 at least one skill advertises an engine-backed verb its script cannot dispatch
#       2 could not run (no skill inspected, unreadable SKILL.md, engine --help unavailable)
CHECK_NAME=check-assess-verb-gone
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ck_need uv
ck_need python3

PARSER="$(mktemp)"
trap 'rm -f "${PARSER}"' EXIT
cat > "${PARSER}" <<'PYPARSE'
import os, re

text = open(os.environ["SKILL_MD"], encoding="utf-8").read()
help_text = os.environ["HELP_TEXT"]

# ADVERTISED: the leading backticked token of each row of the `## Invocation` table. The table
# is the skill's own declaration of its operator surface; a prose mention is not an advertisement.
adv, in_inv = [], False
for ln in text.splitlines():
    if ln.startswith("## "):
        in_inv = ln.strip().lower().startswith("## invocation")
        continue
    if not in_inv or not ln.startswith("|"):
        continue
    cell = ln.split("|")[1].strip() if ln.count("|") >= 2 else ""
    m = re.match(r"`([a-z][a-z0-9-]*)", cell)
    if m and m.group(1) not in adv:
        adv.append(m.group(1))

# EXEMPT: declared on a line-start marker, never inferred.
exempt = set()
m = re.search(r"(?m)^Non-engine-backed subcommands:[ \t]*(.*)$", text)
declared = m is not None
if m:
    raw = m.group(1).strip()
    if raw.lower() not in ("", "none"):
        exempt = {t.strip().strip("`,.") for t in re.split(r"[,\s]+", raw) if t.strip().strip("`,.")}

# DISPATCHED: argparse's subcommand choices, e.g. `{check,migrate,reindex,scaffold}`.
disp = set()
for m2 in re.finditer(r"\{([a-z0-9,\-]+)\}", help_text):
    disp |= {t for t in m2.group(1).split(",") if t}

missing = [v for v in adv if v not in disp and v not in exempt]

print("ADV=" + " ".join(adv))
print("DISP=" + " ".join(sorted(disp)))
print("EXEMPT=" + (" ".join(sorted(exempt)) if exempt else "-"))
print("DECLARED=" + ("yes" if declared else "no"))
print("MISSING=" + " ".join(missing))
PYPARSE

# BY NAME (REQ-CLI-029). `<skill>|<engine script, skill-relative>`
SKILLS=(
  "yf-okf|scripts/okf.py"
  "yf-okf-hygiene|scripts/okf_hygiene.py"
)

CK_RC=0
INSPECTED=0

for row in "${SKILLS[@]}"; do
  IFS='|' read -r skill engine_rel <<< "${row}"
  skill_md="${TREE}/skills/${skill}/SKILL.md"
  engine="${TREE}/skills/${skill}/${engine_rel}"

  if [ ! -f "${skill_md}" ]; then
    ck_fail "${skill}: no SKILL.md at skills/${skill}/SKILL.md — a skill that advertises nothing still owes the file this check reads"
    continue
  fi
  if [ ! -f "${engine}" ]; then
    ck_fail "${skill}: no engine at skills/${skill}/${engine_rel} — every advertised engine-backed verb is undispatchable by construction"
    continue
  fi

  HELP="$(cd "${TREE}" && uv run "${engine}" --help 2>/dev/null)" || true
  if [ -z "${HELP}" ]; then
    ck_inconclusive "${skill}: \`uv run ${engine_rel} --help\` produced no output — the instrument cannot read the dispatch set"
  fi

  RESULT="$(SKILL_MD="${skill_md}" HELP_TEXT="${HELP}" SKILL_NAME="${skill}" python3 "${PARSER}")" \
    || ck_inconclusive "${skill}: could not parse the SKILL.md invocation table"

  ADV="$(printf '%s\n' "${RESULT}" | sed -n 's/^ADV=//p')"
  DISP="$(printf '%s\n' "${RESULT}" | sed -n 's/^DISP=//p')"
  EXEMPT="$(printf '%s\n' "${RESULT}" | sed -n 's/^EXEMPT=//p')"
  DECLARED="$(printf '%s\n' "${RESULT}" | sed -n 's/^DECLARED=//p')"
  MISSING="$(printf '%s\n' "${RESULT}" | sed -n 's/^MISSING=//p')"

  if [ -z "${ADV}" ]; then
    # AN EMPTY INSPECTION IS NOT A PASS (REQ-CLI-029(b)). A skill whose Invocation table this
    # check could not read would otherwise satisfy "every advertised verb dispatches"
    # vacuously — zero advertised verbs, zero failures.
    ck_fail "${skill}: read 0 advertised subcommands from its \`## Invocation\` table — a vacuous pass, not a clean one"
    INSPECTED=$((INSPECTED + 1))
    continue
  fi

  INSPECTED=$((INSPECTED + 1))
  echo "${CHECK_NAME}: ${skill} — advertised [${ADV}] · dispatched [${DISP}] · exempt [${EXEMPT}] (declared: ${DECLARED})"

  if [ -n "${MISSING}" ]; then
    ck_fail "${skill}: advertises engine-backed verb(s) its script cannot dispatch: ${MISSING}$([ "${DECLARED}" = "no" ] && printf '%s' " — and it declares no \`Non-engine-backed subcommands:\` marker, so nothing is exempt")"
  fi
done

if [ "${INSPECTED}" -lt 2 ]; then
  ck_fail "inspected ${INSPECTED} skill(s), expected both OKF skills — a relocation is only visible when both are read"
fi

ck_done "${INSPECTED} skill(s): every advertised engine-backed subcommand is dispatchable"
