# exp-005 — the checker's RED run against the pre-backfill tree

**Type:** sensitivity evidence (plan-061 Issue 1.5, SC1)
**Date:** 2026-08-30
**Tree:** `plan-061-james-dixson-6d8c97-execute` @ `7cb1ba1` (Epic 0 landed; Epic 2/3/4 NOT started)
**Command:**

```bash
uv run scripts/checks/check_skill_readme_contract.py --min-skills 20 --json
```

**Exit:** `1` · **Verdict:** `FAIL` · **`skills_enumerated`:** `20`

## Why this artifact exists

**A checker first observed green proves nothing about its sensitivity.** It may be green because
the corpus is clean, or because it enumerated nothing, or because it never evaluates the rule at
all — and those three are indistinguishable from a single green run. Epic 1 therefore ends with a
*recorded red run* rather than a passing one, and Gate 1 blocks Epics 2 and 3 until this red run
exists.

This is the `--min-skills` argument (REQ-YF-DOC-015) one level up: the floor makes *"the corpus is
clean"* distinguishable from *"the corpus was not read"* within one run; this artifact makes
*"the backfill worked"* distinguishable from *"the checker never worked"* across the plan.

## Result by class

| Class | Count | Plan's pre-execution estimate |
| :-- | --: | --: |
| `layout` | **18** | 18 |
| `fence-unparseable` | **9** | 9 (the "9 non-tree READMEs" of Issue 2.2) |
| `usage` | **5** | 3 |
| `prereqs` | **1** | 1 |
| `missing-readme` | **1** | 1 |
| **total findings** | **34** | — |

`layout` counts **skills failing the `e-readme-layout` edge**, one finding per skill — so it is
directly comparable to #244's "16/19" and to the plan's re-measured "18 FAIL / 1 PASS / 1 N-A of
20". `yf-beads-hygiene` is the single clean skill; `yf-okf-hygiene` is the `missing-readme` N/A.

An unparseable fence emits **two** findings — a `layout` one (*the edge failed*) and a
`fence-unparseable` one (*why*). They are different facts and collapsing them would make the
layout count depend on how a README happens to be malformed.

## Delta against the plan's estimate: `usage` is 5, not 3

The plan predicted three usage failures and Epic 3 names three (`yf-beads-upstream` 3.1,
`yf-incubator` 3.2, `yf-skill-authoring` 3.3). The checker found **five**. The two extra are
**genuine instances of the identical defect class**, not false positives:

| Skill | Teaches | Skill actually answers to |
| :-- | :-- | :-- |
| `yf-beads-init` | `/beads-init` | `/yf-beads-init` |
| `yf-markdown-lint` | `/markdown-lint` | `/yf-markdown-lint` |

Both were invisible to the plan's manual survey for the same reason #244's figures went stale: a
hand count is a snapshot, and this is exactly the class the checker exists to stop re-deriving.
They are repaired under Epic 3 alongside 3.1/3.2 — SC2 (*the checker passes post-backfill*) is
unsatisfiable otherwise, so this is not scope creep but the scope SC2 already implied.

**SC2b is unaffected and remains true as written**: it greps only for `/beads-upstream` and
`/incubator`, which is a subset of what is repaired.

## What the checker deliberately does NOT claim

`e-readme-desc` is **not implemented** (REQ-YF-DOC-013) and the JSON says so in its own
`not_checked` field rather than staying silent. Its predicate is that the README one-liner
matches the `SKILL.md` `description` **intent**, which tolerates paraphrase and is not
mechanically decidable; `exp-003` could only spot-check it on 3 of 20 skills and rated it
INCONCLUSIVE. Claiming it would be precisely the vacuous check (#263) this plan exists to close.

The `usage` check likewise does **not** require every README to mention `/<name>`. An earlier
draft did, and it manufactured **eleven** findings against correct documents — a
`user-invocable: false` skill is reached by trigger, not by a slash command. Manufacturing
blockers and manufacturing consent are the same error in opposite directions.

## Sensitivity is also proven negatively, in the test suite

18 tests, all passing, each planting a defect the checker must catch:

```bash
uv run --with pytest python3 -m pytest scripts/checks/test_check_skill_readme_contract.py -q
# 18 passed
```

Including: the `--min-skills` floor trips at **exit 2** on an empty enumeration (and outranks a
real failure, so an under-read corpus is never reported as a dirty one); an unparseable fence
genuinely emits `fence-unparseable` (without which SC4 passes vacuously); a missing README emits
`missing-readme` **and no mismatch class**; and enumeration is depth-1, so a nested fixture tree
is not counted as a skill.

> **Recorded discrepancy — SC6's literal command does not run in this repo.** SC6 states
> `uv run -m pytest scripts/checks/test_check_skill_readme_contract.py -q`. Executed on this tree
> that resolves to the project `.venv`, which has no `pytest`, and prints
> `No module named pytest`. The house convention every existing `CHANGE-VALIDATION.md` pytest row
> uses is `uv run --with pytest python3 -m pytest <file> -q`, which passes. The recipe rows added
> in Epic 5 use the house form; SC6's intent (*the tests pass*) holds, its literal spelling does
> not.

## Full finding list

| Skill | Class | Detail |
| :-- | :-- | :-- |
| `yf-beads-authoring` | `layout` | the layout edge fails: the layout section carries no fenced code block (a bullet list is not the conformant form) — REQ-YF-DOC-002 |
| `yf-beads-authoring` | `fence-unparseable` | the layout section carries no fenced code block (a bullet list is not the conformant form) — REQ-YF-DOC-002 |
| `yf-beads-extra` | `layout` | the layout edge fails: the layout section carries no fenced code block (a bullet list is not the conformant form) — REQ-YF-DOC-002 |
| `yf-beads-extra` | `fence-unparseable` | the layout section carries no fenced code block (a bullet list is not the conformant form) — REQ-YF-DOC-002 |
| `yf-beads-init` | `layout` | the layout edge fails: the fence root is 'skills/beads-init/', not the skill's real directory 'skills/yf-beads-init/' (REQ-YF-DOC-004); 1 file(s) on disk are absent from the fence: SPEC.md |
| `yf-beads-init` | `usage` | Usage teaches the unprefixed `/beads-init`, a command the skill does not answer to; it is `/yf-beads-init` — REQ-YF-DOC-008 |
| `yf-beads-upstream` | `layout` | the layout edge fails: the fence root is 'skills/beads-upstream/', not the skill's real directory 'skills/yf-beads-upstream/' (REQ-YF-DOC-004); 7 file(s) on disk are absent from the fence: SPEC.md, scripts/check_gh_direct.py, scripts/check_no_universe_fanout.py, scripts/check_prescriptive_push.py, scripts/test_check_no_universe_fanout.py, scripts/test_upstream.py, scripts/upstream_render.py |
| `yf-beads-upstream` | `usage` | Usage teaches the unprefixed `/beads-upstream`, a command the skill does not answer to; it is `/yf-beads-upstream` — REQ-YF-DOC-008 |
| `yf-change-validation` | `layout` | the layout edge fails: 2 file(s) on disk are absent from the fence: protocols/manifest.json, scripts/test_change_validation.py |
| `yf-diagram-authoring` | `layout` | the layout edge fails: the fence root is 'skills/diagram-authoring/', not the skill's real directory 'skills/yf-diagram-authoring/' (REQ-YF-DOC-004); 1 file(s) on disk are absent from the fence: SPEC.md |
| `yf-drift-check` | `layout` | the layout edge fails: the fence root is 'skills/drift-check/', not the skill's real directory 'skills/yf-drift-check/' (REQ-YF-DOC-004); 1 file(s) on disk are absent from the fence: SPEC.md |
| `yf-herdr` | `layout` | the layout edge fails: 2 file(s) on disk are absent from the fence: scripts/test_herdr_channel.py, scripts/test_launch_contract.py |
| `yf-incubator` | `layout` | the layout edge fails: the layout section carries no fenced code block (a bullet list is not the conformant form) — REQ-YF-DOC-002 |
| `yf-incubator` | `fence-unparseable` | the layout section carries no fenced code block (a bullet list is not the conformant form) — REQ-YF-DOC-002 |
| `yf-incubator` | `usage` | Usage teaches the unprefixed `/incubator`, a command the skill does not answer to; it is `/yf-incubator` — REQ-YF-DOC-008 |
| `yf-markdown-format` | `layout` | the layout edge fails: line 'SKILL.md            entry point — both transforms, --check convention, opt-in' is not an ASCII-tree branch (expected a '├── ' / '└── ' prefix) — REQ-YF-DOC-003 |
| `yf-markdown-format` | `fence-unparseable` | line 'SKILL.md            entry point — both transforms, --check convention, opt-in' is not an ASCII-tree branch (expected a '├── ' / '└── ' prefix) — REQ-YF-DOC-003 |
| `yf-markdown-html` | `layout` | the layout edge fails: line 'SKILL.md            entry point — trigger, invocation, pipeline defaults' is not an ASCII-tree branch (expected a '├── ' / '└── ' prefix) — REQ-YF-DOC-003 |
| `yf-markdown-html` | `fence-unparseable` | line 'SKILL.md            entry point — trigger, invocation, pipeline defaults' is not an ASCII-tree branch (expected a '├── ' / '└── ' prefix) — REQ-YF-DOC-003 |
| `yf-markdown-lint` | `layout` | the layout edge fails: line 'SKILL.md            entry point — rules, table conventions, lint-on-edit' is not an ASCII-tree branch (expected a '├── ' / '└── ' prefix) — REQ-YF-DOC-003 |
| `yf-markdown-lint` | `fence-unparseable` | line 'SKILL.md            entry point — rules, table conventions, lint-on-edit' is not an ASCII-tree branch (expected a '├── ' / '└── ' prefix) — REQ-YF-DOC-003 |
| `yf-markdown-lint` | `usage` | Usage teaches the unprefixed `/markdown-lint`, a command the skill does not answer to; it is `/yf-markdown-lint` — REQ-YF-DOC-008 |
| `yf-markdown-pdf` | `layout` | the layout edge fails: line 'SKILL.md            entry point — trigger, invocation, pipeline defaults' is not an ASCII-tree branch (expected a '├── ' / '└── ' prefix) — REQ-YF-DOC-003 |
| `yf-markdown-pdf` | `fence-unparseable` | line 'SKILL.md            entry point — trigger, invocation, pipeline defaults' is not an ASCII-tree branch (expected a '├── ' / '└── ' prefix) — REQ-YF-DOC-003 |
| `yf-okf` | `layout` | the layout edge fails: 1 fence entr(ies) do not exist on disk: LICENSE |
| `yf-okf-hygiene` | `missing-readme` | skills/yf-okf-hygiene/ has no README.md — there is no contract to measure against (REQ-YF-DOC-001/018) |
| `yf-optimal-instructions` | `layout` | the layout edge fails: the fence root is 'skills/optimal-instructions/', not the skill's real directory 'skills/yf-optimal-instructions/' (REQ-YF-DOC-004); 1 file(s) on disk are absent from the fence: SPEC.md |
| `yf-plan` | `layout` | the layout edge fails: the fence's first line 'SKILL.md                     Claude Code skill entry point (includes all phases inline)' is not a directory root (no trailing '/') — REQ-YF-DOC-003 |
| `yf-plan` | `fence-unparseable` | the fence's first line 'SKILL.md                     Claude Code skill entry point (includes all phases inline)' is not a directory root (no trailing '/') — REQ-YF-DOC-003 |
| `yf-research` | `layout` | the layout edge fails: the layout section carries no fenced code block (a bullet list is not the conformant form) — REQ-YF-DOC-002 |
| `yf-research` | `fence-unparseable` | the layout section carries no fenced code block (a bullet list is not the conformant form) — REQ-YF-DOC-002 |
| `yf-skill-authoring` | `layout` | the layout edge fails: the fence root is '.{claude,agents}/skills/skill-authoring/', not the skill's real directory 'skills/yf-skill-authoring/' (REQ-YF-DOC-004); 1 file(s) on disk are absent from the fence: SPEC.md |
| `yf-skill-authoring` | `prereqs` | no `## Prerequisites` section, but SKILL.md frontmatter declares depends-on-tool: ['uv'] — REQ-YF-DOC-007 |
| `yf-skill-authoring` | `usage` | no `## Usage` section — REQ-YF-DOC-008 |

## Raw verdict (elided to counts; full JSON reproducible with the command above)

```json
{
  "check": "check-skill-readme-contract",
  "verdict": "FAIL",
  "exit": 1,
  "skills_enumerated": 20,
  "by_class": {
    "layout": 18,
    "prereqs": 1,
    "usage": 5,
    "missing-readme": 1,
    "fence-unparseable": 9
  },
  "not_checked": [
    "e-readme-desc"
  ],
  "reason": "34 finding(s) across 20 skill(s)"
}
```
