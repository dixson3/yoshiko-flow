#!/usr/bin/env bash
# ctl-184-dispatch — REQ-AGENT-049 / #184.
#
# A FIXTURE, per Issue 0.2's definition: EXITS 0 IFF THE ASSERTED BEHAVIOUR HOLDS. Here the
# asserted behaviour is that `SKILL.md`'s `### Review` section NAMES `Agent` as the dispatch
# mechanism, in the imperative dispatch form Phase 2 already uses.
#
# SECTION-SCOPED, NEVER WHOLE-FILE. Measured on the un-fixed tree:
#   grep -q 'Agent' skills/yf-plan/SKILL.md   ->   EXIT 0
# because `Agent` appears at `SKILL.md:21` in the frontmatter `allowed-tools:` list. A
# whole-file control therefore ships UNABLE TO FAIL — it is green before the fix and green
# after, and distinguishes nothing. The scope below is the `### Review` heading through the
# next `### ` heading.
#
# WHAT THIS CONTROL DOES **NOT** CLAIM (R2/R3). It is a claim about the TEXT, not about
# conduct. "The red-team was actually dispatched" is not mechanically observable and no exit
# code reaches it. A text-presence control is in principle gameable by the very token it checks
# for — which is why the second clause below exists, and why even with it the control's value
# is that it is currently RED and therefore DISTINGUISHES before from after.
#
# THE SECOND CLAUSE, and why a bare token is not enough (pass-1 C8). Measured: a bare
# `grep -q 'Agent'` over the section is GREEN on BOTH of these:
#     <!-- Agent -->
#     Do NOT use the Agent tool here.
# So the section must additionally carry the IMPERATIVE DISPATCH FORM Phase 2 uses at
# `SKILL.md:315` — `Spawn a sub-agent …` together with a reference to `agents/red-team.md`.
# HTML comments are stripped before matching, so a commented-out token cannot satisfy it.
#
# EXIT
#   0  the section names Agent AND carries the imperative dispatch form
#   1  it does not
#   2  the HARNESS could not run
#
# Tree under test: $YF_TREE (set by redcheck.sh; defaults to the plan's execution worktree).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"

SKILL="${YF_TREE}/skills/yf-plan/SKILL.md"
[ -f "${SKILL}" ] || { echo "ctl-184: HARNESS — no SKILL.md at ${SKILL}" >&2; exit 2; }

python3 - "${SKILL}" <<'PY'
import re, sys
HARNESS, FAIL, OK = 2, 1, 0
lines = open(sys.argv[1], encoding="utf-8").read().split("\n")

start = next((i for i, l in enumerate(lines) if l.strip() == "### Review"), None)
if start is None:
    print("ctl-184: HARNESS - SKILL.md has no '### Review' heading", file=sys.stderr)
    sys.exit(HARNESS)
end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("### ")), len(lines))
section = "\n".join(lines[start:end])

# The whole-file form is rejected BY MEASUREMENT, not by assertion — show the contrast.
whole = "\n".join(lines)
print(f"ctl-184: section = SKILL.md lines {start+1}..{end} "
      f"({end-start} lines); whole-file 'Agent' hits = {whole.count('Agent')}, "
      f"section hits (pre-strip) = {section.count('Agent')}")

# A commented-out token must not satisfy anything.
stripped = re.sub(r"<!--.*?-->", "", section, flags=re.S)

failed = 0
if "Agent" in stripped:
    print("ctl-184: (1) ok   - the ### Review section names `Agent`")
else:
    print("ctl-184: (1) FAIL - the ### Review section does not name `Agent` "
          "(HTML comments stripped)", file=sys.stderr)
    failed += 1

has_spawn = "Spawn a sub-agent" in stripped
has_target = "agents/red-team.md" in stripped
if has_spawn and has_target:
    print("ctl-184: (2) ok   - imperative dispatch form present "
          "(`Spawn a sub-agent` + a reference to agents/red-team.md)")
else:
    missing = []
    if not has_spawn:
        missing.append("`Spawn a sub-agent`")
    if not has_target:
        missing.append("a reference to agents/red-team.md")
    print(f"ctl-184: (2) FAIL - the section names no imperative dispatch form; missing "
          f"{' and '.join(missing)}. A bare token is GREEN on `<!-- Agent -->` and on "
          f"'Do NOT use the Agent tool here', which is why this clause exists.",
          file=sys.stderr)
    failed += 1

sys.exit(FAIL if failed else OK)
PY
