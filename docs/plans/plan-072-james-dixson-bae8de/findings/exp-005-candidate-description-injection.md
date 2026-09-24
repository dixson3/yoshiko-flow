---
type: Finding
okf_spec: OKF-PLAN
id: exp-005
description: Both harnesses can evaluate a CANDIDATE description without deploying it. pi via --no-skills --skill <dir>; CC via --setting-sources project plus a project .claude/skills copy. Other load paths silently keep the installed text
status: complete
created: '2026-09-24'
---
# EXP-005: evaluating a candidate description without deploying it

## Approach Tested

A trim must be rated **before** it is deployed. Otherwise the eval measures the installed
(old) text: the three-artifacts rule in AGENTS.md says the running session reads the
installed copy, never `skills/`. Probe: a copy of `yf-okf/SKILL.md` whose description is
replaced with a marker string (`PROBE-MARKER-7731 …`). Then, with tools disallowed, ask each
harness to quote the `yf-okf` description it was given.

## Result

| harness | load path | description the model saw |
| :-- | :-- | :-- |
| pi 0.87.1 | `--no-skills --skill <tmp>/yf-okf` | **marker** (1 yf skill; 4 pi-lens package skills still load) |
| CC 2.1.282 | `--plugin-dir <tmp>/plug` | installed text as `yf-okf`, **plus** marker as `probe:yf-okf` (two coexist) |
| CC | project `.claude/skills/yf-okf` copy, default setting sources | **installed text**. The user-scope copy wins and the candidate is silently ignored |
| CC | project `.claude/skills/` copy **+ `--setting-sources project`** | **marker**. 14 skills listed: the candidate + CC built-ins, no user-scope skills |
| CC | `HOME=` or `CLAUDE_CONFIG_DIR=` sandbox | `Not logged in`. Auth doesn't follow |

**measured:** all five rows above, one run each. That's enough for this question: the output is a
quoted string, not a trigger rate.

## Implications for Plan

1. **There is a sound candidate path on each harness, and both are isolated** (not full
   config). pi: `--no-skills --skill <dir>` per candidate skill. CC: stage candidates into the
   run clone's `.claude/skills/` and pass `--setting-sources project`.
2. **The obvious paths fail silently in the dangerous direction.** On CC, a project copy without
   `--setting-sources project` is shadowed by the user-scope install, so a trim would be
   "verified" against the text it replaces. `--plugin-dir` puts both versions in the listing,
   which changes the routing problem under test. The eval harness must **assert** that the
   loaded description equals the candidate it meant to test (e.g. a hash check against the
   harness's own init event or a tools-off quote), not assume it.
3. **Isolation changes what is measured.** Isolated runs drop the operator's other ~30 skills
   and (on CC) the user rules aggregate, so they test the description with fewer competitors
   and without the always-loaded yf trigger rules. The EXP-003 baseline ran with full config.
   The plan therefore needs **both modes** and must say which one a rating came from:
   - **candidate mode** (isolated, stageable): used to rate a trim before deploy, and all
     20 yf skills are loaded together so sibling competition is preserved.
   - **installed mode** (full operator config): the FULL-tier run after deploy, which is what
     users actually get.
4. On CC, `--setting-sources project` also drops user **settings**. The candidate-mode runs
   inherit none of the operator's permissions/hooks. Recorded, not a blocker: the runner kills
   on activation, before the permission surface matters.

## Recommendations

Candidate mode = all 20 candidate `skills/*/` staged together (pi: 20× `--skill`; CC: copied
to the run clone's `.claude/skills/`). The harness verifies the staged description hash is
what the model was given before scoring any run.
