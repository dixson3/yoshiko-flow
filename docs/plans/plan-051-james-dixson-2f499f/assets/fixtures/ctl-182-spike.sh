#!/usr/bin/env bash
# ctl-182-spike — REQ-AGENT-043 / #182.
#
# A FIXTURE, per Issue 0.2's definition: EXITS 0 IFF THE ASSERTED BEHAVIOUR HOLDS.
#
# TWO CONJUNCTS
# -------------
#   (a) `red-team.md` AUTHORIZES a sandbox spike.
#   (b) For each `grep -qF "<literal>" <path>` pair in REQ-AGENT-043's retargeted
#       `Verification:` line, `<literal>` occurs in `<path>`.
#
# Conjunct (b) is the substance. EXP-002 measured the decisive case: with `red-team.md`
# reworded and `spec/agents.md` still pinning a string that no longer exists, the FAST tier
# returns `pass, first_failure None`. The dangling-pointer state is invisible to every engine
# in the repo, which is why this fixture exists and why D-9 also ships an `e-spec-agent` edge.
#
# THE PAIRING IS POSITIONAL AND MECHANICAL. No prose parsing, no fragment-to-file inference,
# no ellipsis handling. Three prior spikes measured every prose-shape reading as broken —
# literal-vs-regex (pass 1), whitespace (pass 2), and ownership (pass 3, which measured 1/1/1
# under two readings and a FALSE RED under the third). Issue 0.1 has already replaced that
# line's prose shape with the command shape, so authoring against the old shape would target a
# state the DAG destroys before this fixture runs.
#
# TWO GUARDS THAT ARE NOT OPTIONAL
# --------------------------------
#   * `pairs-found` MUST equal the number of `grep -qF` occurrences in the line, else exit 2
#     (INCONCLUSIVE). Measured at pass 4: a double-quote character inside a literal silently
#     parses to ONE pair instead of two, and the self-check below iterates the same parsed set,
#     so the dropped pair is invisible to it. This count comparison is the only thing that
#     sees it. Issue 1.2 points the executor at `AGENTS.md:78-80`, whose own text contains
#     quoted fragments — so this is a live hazard, not a hypothetical one.
#   * `pairs-found == 0` is a FAILURE, never a vacuous pass (pass-4 C39). A control that
#     certifies an empty set is the M5 defect this plan exists to close.
#
# SELF-CHECK BEFORE ANY RED IS RECORDED. Each `<literal>` is asserted to return >= 1 against a
# HAND-FIXED COPY of its `<path>`. A literal that matches nothing ANYWHERE makes the RED false,
# and three separate reviewers produced exactly that false RED without this step.
#
# STATED REDUNDANCY. Under the command shape, conjunct (b) is equivalent to *running*
# REQ-AGENT-043's Verification command, i.e. to `ctl-165-executable`'s assertion for 043.
# That is acceptable and Issue 3.1 books it — it is said here rather than discovered at
# execution.
#
# EXIT
#   0  both conjuncts hold
#   1  a conjunct fails (the capability is absent)
#   2  the HARNESS could not run
#
# Tree under test: $YF_TREE (set by redcheck.sh; defaults to the plan's execution worktree).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"

SPEC="${YF_TREE}/skills/yf-plan/spec/agents.md"
REDTEAM="${YF_TREE}/skills/yf-plan/agents/red-team.md"

[ -f "${SPEC}" ]    || { echo "ctl-182: HARNESS — no spec at ${SPEC}" >&2; exit 2; }
[ -f "${REDTEAM}" ] || { echo "ctl-182: HARNESS — no red-team.md at ${REDTEAM}" >&2; exit 2; }

python3 - "${YF_TREE}" "${SPEC}" "${REDTEAM}" <<'PY'
import re, sys, os, tempfile, shutil

tree, spec_path, redteam_path = sys.argv[1], sys.argv[2], sys.argv[3]
HARNESS, FAIL, OK = 2, 1, 0

spec = open(spec_path, encoding="utf-8").read().split("\n")

# --- locate REQ-AGENT-043's Verification: line ------------------------------------------
req_i = next((i for i, l in enumerate(spec) if l.startswith("REQ-AGENT-043:")), None)
if req_i is None:
    print("ctl-182: HARNESS - REQ-AGENT-043 not found in the spec", file=sys.stderr)
    sys.exit(HARNESS)
ver = next((l for l in spec[req_i + 1: req_i + 8] if l.startswith("Verification:")), None)
if ver is None:
    print("ctl-182: HARNESS - REQ-AGENT-043 has no Verification: line", file=sys.stderr)
    sys.exit(HARNESS)

# --- conjunct (b): POSITIONAL parse of the grep -qF pairs --------------------------------
pairs = re.findall(r'grep -qF "([^"]*)" (\S+?)(?=\s|`|$)', ver)
declared = len(re.findall(r'grep -qF', ver))

if len(pairs) != declared:
    print(f"ctl-182: HARNESS - INCONCLUSIVE: parsed {len(pairs)} pair(s) but the line contains "
          f"{declared} `grep -qF` occurrence(s).", file=sys.stderr)
    print("ctl-182: a double-quote character inside a literal collapses two pairs into one and "
          "is invisible to the self-check, which iterates the same parsed set. Remove it.",
          file=sys.stderr)
    sys.exit(HARNESS)

if len(pairs) == 0:
    print("ctl-182: FAIL - REQ-AGENT-043's Verification: line yields ZERO grep -qF pairs.",
          file=sys.stderr)
    print("ctl-182: zero pairs is a FAILURE, never a vacuous pass (pass-4 C39).", file=sys.stderr)
    sys.exit(FAIL)

# --- SELF-CHECK: every literal must be greppable against a HAND-FIXED copy ----------------
# Without this, a literal that matches nothing anywhere produces a RED that is FALSE.
work = tempfile.mkdtemp()
try:
    for lit, rel in pairs:
        src = os.path.join(tree, rel)
        if not os.path.isfile(src):
            print(f"ctl-182: HARNESS - the line names a path that does not exist: {rel}",
                  file=sys.stderr)
            sys.exit(HARNESS)
        fixed = os.path.join(work, "fixed.md")
        shutil.copyfile(src, fixed)
        with open(fixed, "a", encoding="utf-8") as fh:
            fh.write("\n" + lit + "\n")
        if open(fixed, encoding="utf-8").read().count(lit) < 1:
            print(f"ctl-182: HARNESS - self-check failed: the literal is not greppable even "
                  f"against a hand-fixed copy of {rel}: {lit!r}", file=sys.stderr)
            sys.exit(HARNESS)
finally:
    shutil.rmtree(work, ignore_errors=True)

print(f"ctl-182: self-check ok - {len(pairs)} literal(s) greppable against a hand-fixed copy")

failed = 0
for lit, rel in pairs:
    body = open(os.path.join(tree, rel), encoding="utf-8").read()
    if lit in body:
        print(f"ctl-182: (b) ok      - {rel} carries: {lit}")
    else:
        print(f"ctl-182: (b) DANGLING - {rel} does NOT carry: {lit}", file=sys.stderr)
        failed += 1

# --- conjunct (a): red-team.md AUTHORIZES a spike ----------------------------------------
AUTH = "A sandbox spike is authorized"
if AUTH in open(redteam_path, encoding="utf-8").read():
    print(f"ctl-182: (a) ok      - red-team.md carries: {AUTH}")
else:
    print(f"ctl-182: (a) FAIL    - red-team.md does NOT authorize a spike ({AUTH!r} absent)",
          file=sys.stderr)
    failed += 1

sys.exit(FAIL if failed else OK)
PY
