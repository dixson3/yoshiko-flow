---
type: Plan
okf_spec: OKF-PLAN
description: Enforce the Agent Skills 1024-char description cap, add a crisp/satisfactory/loose
  description rating with cross-harness trigger evals, and bring skill descriptions
  toward 600 chars (#407)
id: plan-072-james-dixson-bae8de
author: james-dixson
created: '2026-09-24'
status: investigating
---
# Plan: Enforce the Agent Skills 1024-char description cap, add a crisp/satisfactory/loose description rating with cross-harness trigger evals, and bring skill descriptions toward 600 chars (#407)

**ID:** plan-072-james-dixson-bae8de
**Author:** james-dixson
**Created:** 2026-09-24
**Status:** investigating

## Objective
Make skill `description` size a specified, enforced, and measured property of every
shipped skill:

1. **Hard gate (SPEC-first):** every `skills/*/SKILL.md` `description` is ≤1024 chars, and
   `name` meets the Agent Skills spec (≤64, `[a-z0-9-]`, no leading/trailing/double hyphen,
   equals the parent dir). Enforced mechanically by `scripts/check_frontmatter.py` in the
   FAST and FULL validation tiers.
2. **Rating:** a three-tier description rating judged by *measured* trigger behaviour, not
   length alone:
   - **crisp** — description ≤600 chars AND triggers correctly on every declared intent;
   - **satisfactory** — description ≤1024 chars AND triggers correctly on every declared intent;
   - **loose** — description >1024 chars (fails the hard gate).
   New skills target crisp. Satisfactory is accepted only with a recorded operator decision
   that a split/refactor is not approved.
3. **Trigger evals:** a per-skill intent set (should-trigger + near-miss should-not-trigger)
   run against both **pi** and **claude-code**, producing the rating.
4. **Remediation:** trim all five over-cap descriptions below 1024, make a best effort to bring
   every description under 600 without losing trigger fidelity, and treat "cannot reach
   satisfactory/crisp without losing fidelity" as a signal the skill is too broad — a
   split/refactor candidate put to the operator.

## Motivation
Five shipped skills exceed the Agent Skills spec's 1024-char `description` cap (#407):
`yf-drift-check` 1325, `yf-skill-authoring` 1319, `yf-okf` 1209, `yf-beads-upstream` 1183,
`yf-change-validation` 1136. pi v0.87.1 enforces the cap (`MAX_DESCRIPTION_LENGTH = 1024` in
`dist/core/skills.js`) and warns on every startup; Claude Code does not enforce 1024, so the
drift went unnoticed. Nothing in the repo checks field lengths: `check_frontmatter.py` validates
structure only (REQ-YF-EMBED-003).

Length also has a cost where it isn't enforced. Every description is loaded into every
session's system prompt. Claude Code caps each listing entry at 1,536 chars and budgets the
whole listing (~1% of context by default), silently dropping descriptions on overflow. The yf
corpus is ~16.6K chars across 20 skills; 15 of the 20 exceed 600.

But the descriptions are the routing surface — several encode deliberate negative routing
between sibling skills (drift-check / change-validation / optimal-instructions /
skill-authoring; okf / okf-hygiene). Trimming by character count alone risks silent routing
regressions, so the remedy must measure trigger fidelity on both harnesses rather than assume
it. A description that cannot be made short without losing fidelity is evidence of a skill
covering too much, which is a design question for the operator, not a wording one.

Review of #407 (corrections and gaps) is posted as issuecomment-5822003298.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| #407 | Five skill descriptions exceed the Agent Skills 1024-char cap | include | The plan's subject; scope widened per operator to a rating + evals + ≤600 best effort | |
| #302 | plan NUMBER is count-based and collides | exclude | Hit at init: plan-070 is absent, so `get_next_index()` returned 071, colliding with landed plan-071-james-dixson-d19ce8. Folder renamed by hand to plan-072. Evidence added for #302, not fixed here | |
| #189 | Six shipped scripts have no tests | exclude | Adjacent: this plan adds negative-control tests for the new `check_frontmatter.py` rules, but does not take on #189's list | |

The remaining 38 keyword matches from the triage scan (`upstream-triage.md`) are unrelated and excluded.

## Investigation Findings
**EXP-001 pilot (preliminary)** — [findings/exp-001-pilot-herdr-trigger-observation.md](findings/exp-001-pilot-herdr-trigger-observation.md).
herdr tabs `cc-eval` (claude-code) and `pi-eval` (pi) are live, and their session JSONL is a
reliable activation signal. One drift-check intent: pi read `yf-drift-check/SKILL.md` first.
CC routed toward it but made no `Skill` call because the intent's precondition (a real
SPEC edit) was absent, so **intents need fixture state**. pi warns on the five over-cap skills
and still loads them.

_Experiments identified (pre-investigation checkpoint):_

- **EXP-001 — Headless trigger observation.** Can a skill's activation be observed
  reliably and non-interactively on both harnesses? claude-code 2.1.282: `-p
  --output-format stream-json`, detect a `Skill` tool_use naming the skill. pi 0.87.1: `-p
  --mode json`, detect a read of the skill's `SKILL.md` (pi has no Skill tool). Both under a
  sandboxed `HOME` carrying only the repo's `skills/` tree. Must also decide how to stop a
  run once the routing decision is made (tool denial / turn cap) so the eval measures
  routing rather than doing the task.
- **EXP-002 — Cost and runtime of "FULL tier, always".** Measure seconds and tokens per
  invocation on each harness, then project 20 skills × ~16–20 intents × N runs × 2
  harnesses. Determine whether FULL runs anywhere unattended (CI) where harness credentials
  are absent, and what the eval does there (INCONCLUSIVE vs FAIL).
- **EXP-003 — Baseline fidelity pilot.** On the sibling cluster (drift-check /
  change-validation / optimal-instructions / skill-authoring) and okf / okf-hygiene, run a
  small intent set against the current descriptions. Establishes whether today's
  descriptions already route correctly (so the trims have a baseline to regress from) and
  how noisy the run-to-run measurement is (drives N and the pass threshold).
- **EXP-004 — Claude Code listing budget.** Does the current corpus (~16.6K chars) already
  trigger CC's listing-budget drop under the operator's settings? If it does, the eval
  environment must reproduce the full installed skill set, not the yf tree alone, or it
  measures a best case.

## Approach
### Scoping decisions (operator, 2026-09-24)

| # | Decision | Choice |
| :-- | :-- | :-- |
| D1 | Rating tiers | crisp (≤600 + all intents), satisfactory (≤1024 + all intents), loose (>1024) |
| D2 | Hard gate | 1024-char description + full Agent Skills `name` rule in `check_frontmatter.py`, FAST+FULL tiers, `SKILL.md` only (not `agents/*.md`) |
| D3 | Eval placement | **FULL tier, always** — every FULL run re-evaluates every skill on both harnesses |
| D4 | Rating home | per-skill `skills/<name>/evals/triggers.json`: intents + last measured result per harness + description hash; the rating is derived, never hand-asserted |
| D5 | Trim scope | all 20 skills: five over-cap must reach ≤1024; best effort toward ≤600 for all, each verified by evals |
| D6 | Split handling | a skill that cannot reach crisp without losing fidelity gets a recorded split proposal at a human gate; approved splits file a follow-on plan; declined → accepted as satisfactory with the reason recorded |
| D7 | Harnesses | pi and claude-code, both required |
| D8 | Ordering | SPEC-first: `REQ-*` for gate, rating, and evals land before any checker/eval/trim code |

### Approach hypothesis
SPEC amendment → hard gate (checker + negative-control tests) → eval harness + intent sets
→ baseline ratings → trims, re-rated per skill → split-proposal gate → authoring guidance
in `yf-skill-authoring` → redeploy and confirm pi startup emits no skill diagnostics.

D3 is the main open cost risk: EXP-002 decides whether it is feasible as stated, or whether
the plan needs to bring the operator a measured alternative (e.g. re-evaluate only skills
whose description hash changed).

## Epics
_To be determined._

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
