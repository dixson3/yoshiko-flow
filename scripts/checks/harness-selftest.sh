#!/usr/bin/env bash
# SC35 / REQ-CLI-029 — every harness instrument RETURNS NON-ZERO ON A DELIBERATELY BROKEN
# INPUT, and this selftest reports HOW MANY it checked.
#
# THE CONTROL DISTINGUISHING "CORRECT" FROM "MERELY PRESENT". SC0 asserts the ten instruments
# exist and are executable; that is a floor, and once the files exist it always holds. This
# script is what actually EXECUTES each one and requires it to go red on input it must reject.
#
# --- PRIOR ART, EVALUATED (Issue 1.9's explicit obligation) -------------------------------
# plan-054's `redcheck.sh cmd_verify_red_checks` is close prior art: it iterates `checks/`,
# requires a recorded non-zero pre-fix observation per script, supports an allowlist-with-
# reason, and fails when it finds no instrument — which is `--require N` under another name.
# It is NOT reused, for two reasons that are facts rather than preferences:
#
#   1. IT READS A LEDGER; THIS EXECUTES. `verify-red-checks` asserts that a red observation
#      was RECORDED at some past moment. SC35 asserts each instrument goes red NOW, against a
#      broken input this script constructs. Those are different claims, and only the second
#      survives an instrument that was correct when banked and has since regressed.
#   2. ITS ENUMERATOR REACHES 6 OF 10. `cmd_verify_red_checks` globs `check-*.sh`, and
#      `record-red-check` HARD-REJECTS any other name. This plan's instruments span three
#      naming conventions and two languages (`check-*.sh`, `check-*.py`, `check_*.py`,
#      `harness-selftest.sh`), so the glob silently misses four and REPORTS SUCCESS. Also,
#      plan-055 copied `_common.sh` and three checks into `scripts/checks/` but NOT
#      `redcheck.sh`, so the verb is not present at this path in the first place.
#
# --- ENUMERATION IS BY NAME, NEVER BY GLOB (REQ-CLI-029) ---------------------------------
# The list below is SC0's list. A glob-based enumerator is exactly the defect above: it would
# reach a subset and report a confident green over it. Dispatch is per extension — `bash` for
# `.sh`, `uv run` for `.py`.
#
# --- WHY `--require 9` AND NOT 10 --------------------------------------------------------
# A selftest cannot be its own RED fixture, so it EXCLUDES ITSELF from its own count. SC0 is
# what proves the tenth exists.
#
# EXIT  0 every enumerated instrument went red on its broken input, and the count met --require
#       1 an instrument did not go red, or the count fell short
#       2 could not run
CHECK_NAME=harness-selftest
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

REQUIRE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --require) REQUIRE="${2:-0}"; shift 2 ;;
    --require=*) REQUIRE="${1#*=}"; shift ;;
    *) ck_inconclusive "unknown argument: $1" ;;
  esac
done

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
CHECKS="${TREE}/scripts/checks"
[ -d "${CHECKS}" ] || ck_inconclusive "no scripts/checks at ${CHECKS}"
ck_need uv
CK_RC=0

FIX="$(mktemp -d)"
trap 'rm -rf "${FIX}"' EXIT

# BY NAME. Each row: <instrument>|<argv that MUST be rejected>|<what makes it broken>
# The broken input is chosen per instrument to exercise its own FAIL branch (exit 1), never
# merely its INCONCLUSIVE branch (exit 2) — a 2 says the instrument could not run, which is
# not evidence that it can judge.
INSTRUMENTS=(
  "check-pytest-ran.sh|_shared/test_okf.py no_such_test_function_xyz|a test name that is not in the file"
  "check-recipe-row.sh|definitely-no-such-recipe-row|a recipe row id no manifest carries"
  "check-reindex-exit-contract.sh|__SELF_BREAK__|the engine's exits folded back together"
  "check-fixture-carveout.sh|__SELF_BREAK__ docs/plans/plan-053-james-dixson-4015d3|an OKF-EXTENSION.md with no §3b, so the carve-out is absent"
  "check-closeout-can-fail.sh|__SELF_BREAK__|a linter that cannot fail a completed bundle"
  "check-drift-driver-contract.sh|__SELF_BREAK__|a driver that folds no-such-path into clean"
  "check_okf_index_drift.py|--root definitely/not/a/real/root/* --min-roots 0|a nonexistent enumerated root"
  "check-req-coverage.py|${FIX}/uncovered-plan|a plan whose issues name no REQ and reach no Epic-0 source"
  "check-description-coverage.py|${FIX}/unstamped-bundle|a bundle whose nested artifacts carry no description"
  # --- plan-057 Issue 1.0: one named RED row per instrument this plan authors -------------
  "check-index-boilerplate-ratio.py|--baseline 0/1 --frozen-set ${FIX}/sc3-frozen.txt --root ${FIX}|a ratio that is NOT strictly lower than its baseline"
  "check-backfill-audit-delta.py|--record ${FIX}/regressed-backfill.json|a bundle whose audit verdict is WORSE after the backfill"
  "check-skill-classified.sh|definitely-no-such-skill-xyz|a skill whose SKILL.md no schema selects (class no-such-path)"
  "check-assets-decided.py|__SELF_BREAK__|a tree where no schema selects assets/ and no blanket assets/** exclusion exists"
  "check-assess-verb-gone.sh|__SELF_BREAK__|a SKILL.md advertising an engine-backed verb its script cannot dispatch"
  "check-baseline-pin-contract.sh|__SELF_BREAK__|a baseline with no okf_baseline_sha256 pin and no detector"
  "check-gates-poured-probe.sh|__SELF_BREAK__ docs/plans/plan-901-fixture-dddddd|an auto+executable gate poured test_class: manual, not probe"
)

# Fixtures the rows above point at.
mkdir -p "${FIX}/no-fixtures-bundle"
printf -- '---\ntype: Plan\nokf_spec: OKF-PLAN\nstatus: complete\n---\n# p\n' \
  > "${FIX}/no-fixtures-bundle/plan.md"
printf '# Log\n\n## 2026-08-28\n\n- scoping: f\n' > "${FIX}/no-fixtures-bundle/log.md"
mkdir -p "${FIX}/unstamped-bundle/findings"
printf -- '---\ntype: Plan\nokf_spec: OKF-PLAN\nstatus: complete\n---\n# p\n' \
  > "${FIX}/unstamped-bundle/plan.md"
printf '# Log\n\n## 2026-08-28\n\n- scoping: f\n' > "${FIX}/unstamped-bundle/log.md"
# A nested artifact with NO `description:` — the RED input for the producer-contract check.
printf -- '---\ntype: Finding\nokf_spec: OKF-PLAN\n---\n# f\n' \
  > "${FIX}/unstamped-bundle/findings/exp-000.md"

# A plan whose non-Epic-0 issues are genuinely UNCOVERED — no REQ named, no Epic-0 dependency,
# no bug-fix carve-out. This reaches check-req-coverage.py's FAIL branch; a nonexistent dir
# would only reach its INCONCLUSIVE branch, which is not evidence that it can judge.
mkdir -p "${FIX}/uncovered-plan"
printf '# Log\n\n## 2026-08-28\n\n- scoping: f\n' > "${FIX}/uncovered-plan/log.md"
cat > "${FIX}/uncovered-plan/plan.md" <<'UPEOF'
---
type: Plan
okf_spec: OKF-PLAN
id: plan-901-fixture-dddddd
author: t
created: '2026-08-28'
status: drafting
---
# Plan: uncovered fixture

**ID:** plan-901-fixture-dddddd
**Status:** drafting

## Objective
fixture

## Motivation
fixture

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Investigation Findings
none

## Approach
none

## Epics
### Epic 0: bookkeeping only
- Issue 0.1: correct a figure
### Epic 1: work
- Issue 1.1: do a thing that names no requirement
- Issue 1.2: do another thing
- Issue 1.3: and another
- Issue 1.4: and another
- Issue 1.5: and another

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | r | low | m |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | c | manual: look | 1.1 |
UPEOF

# --- plan-057 fixtures ---------------------------------------------------------------------
# A frozen "corpus" whose boilerplate ratio is 0.5 — measured against `--baseline 0/1` (0.0) it
# is NOT strictly lower, which is the comparator's FAIL branch. A baseline of 0.0 is
# unreachable by construction, so this row can never accidentally go green.
mkdir -p "${FIX}/ratio-bundle"
printf -- '- [a](a.md) - same text\n- [b](b.md) - same text\n' > "${FIX}/ratio-bundle/index.md"
printf 'ratio-bundle\n' > "${FIX}/sc3-frozen.txt"

# A backfill record in which a bundle went `warn -> fail`: the regression SC12 exists to catch.
printf '%s\n' '{"bundles":[{"bundle":"fixture","before":{"verdict":"warn"},"after":{"verdict":"fail"}}]}' \
  > "${FIX}/regressed-backfill.json"

# `__SELF_BREAK__` instruments assert a property OF ANOTHER COMPONENT, so their RED fixture is
# a broken copy of that component rather than an argument. Constructing one per instrument is
# what makes this a real control instead of an argument-validation test.
self_break_rc() {   # $1 = instrument name, $@ = argv to forward -> exit against a BROKEN component
  local name="$1"; shift
  local sandbox="${FIX}/sb-${name}"
  rm -rf "${sandbox}"; mkdir -p "${sandbox}"
  # A tree-shaped sandbox: the instrument resolves YF_TREE, so a copy with one component
  # sabotaged is a complete RED fixture.
  mkdir -p "${sandbox}/scripts/checks" "${sandbox}/_shared"
  cp "${CHECKS}/_common.sh" "${sandbox}/scripts/checks/"
  cp "${CHECKS}/${name}" "${sandbox}/scripts/checks/"
  case "${name}" in
    check-reindex-exit-contract.sh)
      # Sabotage: fold `no-such-path` back into `no-index`, the pre-plan-056 behaviour.
      sed 's/"no-such-path": 3/"no-such-path": 2/' "${TREE}/_shared/okf.py" > "${sandbox}/_shared/okf.py"
      ;;
    check-closeout-can-fail.sh)
      # Sabotage: delete the two `E` close-out checks, which is what #246 read literally
      # would have done — the change D-15 rejected.
      cp -R "${TREE}/_shared/document_types" "${sandbox}/_shared/document_types"
      python3 - "$sandbox" <<'PY'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1]) / "_shared" / "document_types" / "plan-relations.toml"
t = p.read_text()
t = re.sub(r'\[\[checks\]\]\nid = "(R1|R2a)-closeout".*?(?=\n\[\[checks\]\]|\Z)', '', t, flags=re.S)
p.write_text(t)
PY
      cp "${TREE}/_shared/doc_lint.py" "${sandbox}/_shared/doc_lint.py"
      cp -R "${TREE}/_shared/plan_extract.py" "${sandbox}/_shared/" 2>/dev/null || true
      ;;
    check-fixture-carveout.sh)
      # Sabotage: an OKF-EXTENSION.md with NO §3b. The carve-out concept is absent, so the
      # fixture findings come back and clause 1 must go red. This reaches the FAIL branch;
      # a bundle with no fixtures would only reach INCONCLUSIVE.
      mkdir -p "${sandbox}/skills/yf-plan/scripts"
      cp "${TREE}/_shared/okf.py" "${sandbox}/skills/yf-plan/scripts/okf.py"
      cp "${TREE}/skills/yf-plan/scripts/plan_manager.py" "${sandbox}/skills/yf-plan/scripts/" 2>/dev/null || true
      for f in "${TREE}"/skills/yf-plan/scripts/*.py; do cp "$f" "${sandbox}/skills/yf-plan/scripts/" 2>/dev/null || true; done
      cp -R "${TREE}/skills/yf-plan/scripts/document_types" "${sandbox}/skills/yf-plan/scripts/" 2>/dev/null || true
      sed '/^## 3b\./,$d' "${TREE}/skills/yf-plan/OKF-EXTENSION.md" > "${sandbox}/skills/yf-plan/OKF-EXTENSION.md"
      mkdir -p "${sandbox}/docs/plans"
      cp -R "${TREE}/docs/plans/plan-053-james-dixson-4015d3" "${sandbox}/docs/plans/" 2>/dev/null || true
      cp -R "${TREE}/_shared" "${sandbox}/_shared" 2>/dev/null || true
      ;;
    check-assets-decided.py)
      # Sabotage: a document_types set with NO schema selecting `assets/`, and an
      # OKF-EXTENSION whose §3b excludes only a SUBDIRECTORY of assets. That is the exact
      # "silently uncovered" state — and it is the state the LIVE tree is in until Issue 1.5
      # decides, which is why the RED fixture is a sandbox rather than the tree itself.
      mkdir -p "${sandbox}/_shared/document_types" "${sandbox}/skills/yf-plan"
      cp "${TREE}/_shared/okf.py" "${sandbox}/_shared/okf.py"
      cp "${TREE}/_shared/document_types/finding.toml" "${sandbox}/_shared/document_types/"
      sed '/^| `assets\/\*\*`/d' "${TREE}/skills/yf-plan/OKF-EXTENSION.md" \
        > "${sandbox}/skills/yf-plan/OKF-EXTENSION.md"
      ;;
    check-assess-verb-gone.sh)
      # Sabotage: a SKILL.md advertising a verb the engine cannot dispatch, with NO
      # `Non-engine-backed subcommands:` declaration — so nothing is exempt and the check
      # must go red. Both skills are present, so the row fails on the PROPERTY rather than
      # on the two-skill floor.
      for s in yf-okf yf-okf-hygiene; do
        mkdir -p "${sandbox}/skills/${s}/scripts"
      done
      cp "${TREE}/_shared/okf.py" "${sandbox}/skills/yf-okf/scripts/okf.py"
      cp "${TREE}/_shared/okf.py" "${sandbox}/skills/yf-okf-hygiene/scripts/okf_hygiene.py"
      printf '# s\n## Invocation\n| Subcommand | Purpose |\n|:--|:--|\n| `%s` | p |\n\nNon-engine-backed subcommands: none\n' \
        "definitely-not-dispatchable" > "${sandbox}/skills/yf-okf/SKILL.md"
      printf '# s\n## Invocation\n| Subcommand | Purpose |\n|:--|:--|\n| `check` | p |\n\nNon-engine-backed subcommands: none\n' \
        > "${sandbox}/skills/yf-okf-hygiene/SKILL.md"
      ;;
    check-baseline-pin-contract.sh)
      # Sabotage: a baseline carrying NO `okf_baseline_sha256:` key and no detector script.
      # This reaches the FAIL branch (1), never the INCONCLUSIVE one — the check treats a
      # missing detector as FALSE by design (R11's third rule).
      mkdir -p "${sandbox}/skills/yf-okf/spec"
      printf '# OKF Baseline\n\nVersion 0.2, with no content pin at all.\n' \
        > "${sandbox}/skills/yf-okf/spec/OKF-BASELINE.md"
      ;;
    check-gates-poured-probe.sh)
      # Sabotage: a STUBBED `bd` on PATH returning a gate bead poured `test_class: manual`.
      #
      # THE STUB IS DELIBERATE AND IS BETTER THAN A REAL SANDBOX DB. A `bd init` fixture
      # would prove that metadata round-trips through beads — which is already proven, against
      # the LIVE database, by the green arm of this instrument. What the RED row must prove is
      # that the check's FAIL BRANCH FIRES, and a stub does that hermetically, with no DB, no
      # network, and no possibility of writing to the shared graph.
      mkdir -p "${sandbox}/bin" "${sandbox}/_shared" "${sandbox}/docs/plans"
      cp "${TREE}/_shared/plan_extract.py" "${sandbox}/_shared/" 2>/dev/null || true
      cat > "${sandbox}/bin/bd" <<'BDSTUB'
#!/usr/bin/env bash
cat <<'JSON'
[{"id":"fix.1","title":"Gate: Capability Gate: Fixture gate","issue_type":"gate","status":"open",
  "metadata":{"gate_type":"auto","test":"true","test_class":"manual","cwd":"repo-root"}}]
JSON
BDSTUB
      chmod +x "${sandbox}/bin/bd"
      mkdir -p "${sandbox}/docs/plans/plan-901-fixture-dddddd"
      printf '# Log\n\n## 2026-08-28\n\n- scoping: f\n' \
        > "${sandbox}/docs/plans/plan-901-fixture-dddddd/log.md"
      cat > "${sandbox}/docs/plans/plan-901-fixture-dddddd/plan.md" <<'GFEOF'
---
type: Plan
okf_spec: OKF-PLAN
id: plan-901-fixture-dddddd
author: t
created: '2026-08-28'
status: approved
---
# Plan: gate fixture

**ID:** plan-901-fixture-dddddd
**Status:** approved

## Objective
fixture

## Motivation
fixture

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Investigation Findings
none

## Approach
none

## Epics
### Epic 0: bookkeeping
- Issue 0.1: correct a figure

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Fixture gate
- Type: auto
- Condition: a condition
- Test: true
- Blocks: 0.1

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | r | low | m |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | c | manual: look | 0.1 |
GFEOF
      ;;
    check-drift-driver-contract.sh)
      # Sabotage: a driver that exits 0 on everything — the "gate that cannot fail" shape.
      printf '#!/usr/bin/env -S uv run --script\n# /// script\n# requires-python = ">=3.11"\n# dependencies = []\n# ///\nimport sys\nsys.exit(0)\n' \
        > "${sandbox}/scripts/checks/check_okf_index_drift.py"
      chmod +x "${sandbox}/scripts/checks/check_okf_index_drift.py"
      ;;
  esac
  # Argv is TREE-RELATIVE and is re-anchored on the sandbox, so a row can point the
  # instrument at a real bundle inside the sabotaged copy rather than at the live tree.
  local args=() a
  for a in "$@"; do
    case "${a}" in /*) args+=("${a}") ;; *) args+=("${sandbox}/${a}") ;; esac
  done
  # `${args[@]+...}` — NOT a bare `${args[@]}`. Under `set -u` (which `_common.sh` sets) an
  # EMPTY array expansion is an unbound-variable error, so the three no-arg rows were exiting
  # non-zero because of THIS SCRIPT rather than because the instrument judged anything. An
  # accidental red is the same defect as an accidental green: the exit code stops meaning what
  # the selftest reports it means.
  # A sandbox MAY ship a `bin/` of stubbed external tools. Prepending it is what lets a RED
  # fixture sabotage a tool the instrument shells out to (`bd`), rather than only a file it
  # reads — with no DB, no network, and no possibility of touching shared state.
  local sbpath="${PATH}"
  [ -d "${sandbox}/bin" ] && sbpath="${sandbox}/bin:${PATH}"
  # DISPATCH PER EXTENSION, exactly as the non-self-break path does (REQ-CLI-029). This
  # branch used to hard-code `bash`, which was invisible while every `__SELF_BREAK__` row
  # happened to be a `.sh`. The first `.py` self-break row exposed it: `bash file.py` reads
  # the PEP-723 header as comments, hits Python syntax, and exits 2 — an INCONCLUSIVE that
  # this selftest then correctly refused to accept as a red observation. The instrument was
  # fine; the harness could not run it.
  local runner=(bash)
  case "${name}" in *.py) runner=(uv run) ;; esac
  ( cd "${sandbox}" && git init -q . 2>/dev/null; YF_TREE="${sandbox}" PATH="${sbpath}" \
      "${runner[@]}" "${sandbox}/scripts/checks/${name}" ${args[@]+"${args[@]}"} >/dev/null 2>&1 )
  echo $?
}

CHECKED=0 SKIPPED=0
for row in "${INSTRUMENTS[@]}"; do
  IFS='|' read -r name argv why <<< "${row}"
  path="${CHECKS}/${name}"
  if [ ! -f "${path}" ]; then
    echo "${CHECK_NAME}: SKIP — ${name} is not present" >&2
    SKIPPED=$((SKIPPED + 1))
    continue
  fi
  if [ "${argv%% *}" = "__SELF_BREAK__" ]; then
    # shellcheck disable=SC2086 - the remaining argv is a deliberate word-split list
    rc="$(self_break_rc "${name}" ${argv#__SELF_BREAK__})"
  else
    case "${name}" in
      *.py) ( cd "${TREE}" && eval uv run "${path}" ${argv} >/dev/null 2>&1 ) ;;
      *)    ( cd "${TREE}" && eval bash "${path}" ${argv} >/dev/null 2>&1 ) ;;
    esac
    rc=$?
  fi
  CHECKED=$((CHECKED + 1))
  # NON-ZERO, and specifically NOT 126/127 — those are the shell's report that the instrument
  # could not be executed, and counting them would let a broken shebang pass as a red
  # observation (REQ-CLI-029(c)).
  if [ "${rc}" -eq 0 ]; then
    ck_fail "${name} exited 0 on a deliberately broken input (${why}) — it cannot fail"
  elif [ "${rc}" -eq 126 ] || [ "${rc}" -eq 127 ]; then
    ck_fail "${name} exited ${rc} — that is the SHELL saying it could not run the instrument, not a verdict"
  elif [ "${rc}" -eq 2 ]; then
    # A 2 IS NOT A RED OBSERVATION. It says the instrument COULD NOT RUN, which is a
    # statement about the harness rather than a demonstration that the instrument can
    # judge — and `redcheck.sh record-red-check` refuses to bank a 2 for exactly this
    # reason. Accepting it here would let a RED fixture that never reaches the FAIL branch
    # certify the instrument, which is this selftest's own vacuity mode.
    ck_fail "${name} exited 2 (INCONCLUSIVE) on '"'"'${why}'"'"' — the RED fixture did not reach its FAIL branch, so this proves nothing about the instrument"
  else
    echo "${CHECK_NAME}: ${name} -> ${rc} on '${why}'"
  fi
done

# THE COUNT (REQ-CLI-029(b) and (e)). A selftest that enumerated 2 of 16 must be
# distinguishable from one that enumerated 16.
#
# EQUALITY, NOT A MINIMUM — amended by plan-057 Issue 0.5 / REQ-CLI-029(e). The shipped
# comparison was `-lt`, i.e. a FLOOR, and a floor is the wrong comparator for a hand-maintained
# list that is KNOWN to drift: measured, six instruments sit in this directory unenumerated. A
# floor is satisfied by a run that SKIPPED an instrument as long as the remainder clears it, and
# it is equally satisfied by an array that has grown past it without anyone noticing. Equality
# makes the number an ASSERTION about the enumerated set rather than a lower bound on it, so
# adding an instrument to the array is a deliberate act of taking ownership of it.
if [ "${CHECKED}" -ne "${REQUIRE}" ]; then
  if [ "${CHECKED}" -lt "${REQUIRE}" ]; then
    ck_fail "checked ${CHECKED} instrument(s), --require ${REQUIRE} (${SKIPPED} absent) — this selftest would certify vacuously"
  else
    ck_fail "checked ${CHECKED} instrument(s), --require ${REQUIRE} — the enumerated array has GROWN past the required count; --require asserts EQUALITY, so raise it deliberately rather than letting the set drift"
  fi
fi

ck_done "${CHECKED} instrument(s) each returned non-zero on a deliberately broken input (--require ${REQUIRE}; ${SKIPPED} absent; this selftest excludes itself)"
