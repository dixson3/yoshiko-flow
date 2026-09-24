---
type: Plan
okf_spec: OKF-PLAN
description: Enforce the Agent Skills 1024-char description cap, add a crisp/satisfactory/loose
  description rating with cross-harness trigger evals, and bring skill descriptions
  toward 600 chars (#407)
id: plan-072-james-dixson-bae8de
author: james-dixson
created: '2026-09-24'
status: review
---
# Plan: Enforce the Agent Skills 1024-char description cap, add a crisp/satisfactory/loose description rating with cross-harness trigger evals, and bring skill descriptions toward 600 chars (#407)

**ID:** plan-072-james-dixson-bae8de
**Author:** james-dixson
**Created:** 2026-09-24
**Status:** review

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
| #407 | Five skill descriptions exceed the Agent Skills 1024-char cap | include | The plan's subject; scope widened per operator to a rating + evals + ≤600 best effort | 0.3, 1.1, 3.2 |
| #302 | plan NUMBER is count-based and collides | exclude | Hit at init: plan-070 is absent, so `get_next_index()` returned 071, colliding with landed plan-071-james-dixson-d19ce8. Folder renamed by hand to plan-072. Evidence added for #302, not fixed here | |
| #189 | Six shipped scripts have no tests | exclude | Adjacent: this plan adds negative-control tests for the new `check_frontmatter.py` rules, but does not take on #189's list | |

The remaining 38 keyword matches from the triage scan (`upstream-triage.md`) are unrelated and excluded.

## Investigation Findings
**EXP-005 candidate injection (complete)** — [findings/exp-005-candidate-description-injection.md](findings/exp-005-candidate-description-injection.md).
A trim can be rated before deploy. pi: `--no-skills --skill <dir>`. CC: a project
`.claude/skills/` copy **plus `--setting-sources project`**. Without that flag, CC silently
shadows the candidate with the user-scope install, and `--plugin-dir` lists both versions.
The eval must verify the loaded text is the candidate. Isolation drops the operator's other
skills and CC's rules aggregate, so ratings name their **mode**: candidate (isolated, all
20 yf candidates together) vs installed (full config).

**EXP-004 CC listing budget (complete)** — [findings/exp-004-cc-listing-budget.md](findings/exp-004-cc-listing-budget.md).
`--debug-file` shows `Skill listing over budget: 50 skills, 33313 chars > 30000 budget` on
the operator's machine today. yf is 16,898 chars (51%) of it, so the trims bring the listing
under budget. CC eval runs must record whether that WARN fired.

**EXP-003 baseline (complete)** — [findings/exp-003-baseline-trigger-fidelity.md](findings/exp-003-baseline-trigger-fidelity.md).
21 intents × 3 reps × 2 harnesses against the current descriptions of the six sibling
skills: **CC 59/63, pi 57/63, near-misses 18/18, one wrong-sibling activation in 126
runs.** All misses are "agent did the task without a skill" (pi D3, O1; CC O2), not
confusion between siblings, so on this evidence none of the six is a split candidate.
The harnesses load different always-on surfaces: CC's rules aggregate has 9 yf protocol
blocks (including the drift-check / change-validation / instructions triggers), pi's has 4. So a
pi pass is the stricter test of the description alone. "Triggers on all intents" needs a
rate threshold, not 3/3.

**EXP-001 (resolved by EXP-003).** Detector: CC `Skill` tool_use, or tool arguments referencing an
installed `skills/<n>/` path, or `yf skill-dir <n>`. On CC, 39 of 50 passes were a `Skill`
call, 11 were direct script use via `yf skill-dir` (the skill in use without a `Skill`
call). Intents need fixture state.

**EXP-002 (partial)** — [findings/exp-002-eval-cost-and-runtime.md](findings/exp-002-eval-cost-and-runtime.md).
CC 23.6 s/run, about $0.22/run; pi 13.3 s/run. Projection for D3 as decided: about 2.4 h wall and about
$55–90 (CC) per FULL run. The operator re-confirmed D3 with these numbers (see D3).

**EXP-001 pilot (preliminary, superseded)** — [findings/exp-001-pilot-herdr-trigger-observation.md](findings/exp-001-pilot-herdr-trigger-observation.md).
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
| D3 | Eval placement | **FULL tier, always**: every FULL run re-evaluates every skill on both harnesses, 3 reps. **Re-confirmed 2026-09-24 after EXP-002**: the operator chose this over hash-scoped and reduced-rep alternatives with the measured cost in hand (~360 runs per harness, ~2.4 h wall, ~$55–90 CC per FULL run). Unattended/CI runs without harness credentials report INCONCLUSIVE, never PASS |
| D4 | Rating home | per-skill `skills/<name>/evals/triggers.json`: intents + last measured result per harness + description hash; the rating is derived, never hand-asserted |
| D5 | Trim scope | all 20 skills: five over-cap must reach ≤1024; best effort toward ≤600 for all, each verified by evals |
| D6 | Split handling | a skill that cannot reach crisp without losing fidelity gets a recorded split proposal at a human gate; approved splits file a follow-on plan; declined → accepted as satisfactory with the reason recorded |
| D7 | Harnesses | pi and claude-code, both required |
| D8 | Ordering | SPEC-first: `REQ-*` for gate, rating, and evals land before any checker/eval/trim code |

### Chosen approach

![plan-072 structure](diagrams/plan-072-structure.png)

1. **SPEC first (Epic 0).** Three requirements, homed where their siblings live:
   - `REQ-YF-EMBED-007` (SPEC.md §3.2, next to `-003`, which already owns the frontmatter
     invariant and names `check_frontmatter.py` as its enforcer). The Agent Skills field
     rules on every `skills/*/SKILL.md`: `description` 1–1024 chars; `name` 1–64 chars,
     `[a-z0-9-]`, no leading/trailing hyphen, no `--`, equal to the parent directory name.
     Scoped to `SKILL.md` only. `agents/*.md` are not Agent Skills (D2).
   - `REQ-SKAUTH-061` (`skills/yf-skill-authoring/SPEC.md`, the conventions skill). The
     **description rating**: crisp / satisfactory / loose (D1), "triggers on all intents"
     defined as per-intent trigger rate ≥ 0.5 over ≥3 reps on **both** harnesses (EXP-003:
     3/3 would flap). The rating is **derived** from `evals/triggers.json` and never
     hand-asserted (D4). New skills target crisp. Satisfactory needs a recorded operator
     decision (D6).
   - `REQ-SKAUTH-062`. The **trigger-eval contract**: intent-set schema (should-trigger
     with fixtures + near-miss with named siblings), the activation detector (EXP-001/003),
     the two modes and the candidate-verification step (EXP-005), the per-run
     listing-budget capture (EXP-004), and the verdicts. PASS only on a completed run.
     INCONCLUSIVE when a harness binary or its auth is absent (EXP-002: CI has neither),
     never PASS.
2. **Hard gate (Epic 1).** Extend `check_frontmatter.py`, the existing gated check (FAST+FULL,
   CHANGE-VALIDATION §3 rows for both skill globs), so it needs no new recipe row or glob.
   Negative controls: a fixture the check must **fail** on for every rule. The gate cannot
   turn on while five skills are over, so Epic 1 lands the check in the same change-set as
   Epic 3's five over-cap trims, ahead of the rest of the trim work.
3. **Eval harness (Epic 2).** Promote the EXP-003 scratch tooling (`assets/exp-003/`) to a
   shipped `scripts/checks/skill_trigger_eval.py` plus per-skill `skills/<n>/evals/triggers.json`,
   seeded from the EXP-003 intents for the six siblings and authored fresh for the other
   14. Wired as a FULL-tier row (D3: every skill, 3 reps, both harnesses, every FULL run).
4. **Trim + rate (Epic 3).** Per skill: candidate-mode rating of the current text (baseline),
   trim, candidate-mode re-rate, keep the shortest text whose rating does not regress.
   EXP-003 shows the current misses are "did it without the skill", so where fidelity is
   short the lever is TRIGGER wording, not a split.
5. **Split gate (Epic 4).** Any skill still not crisp after its best-effort trim gets a
   written split proposal. One human gate covers all of them (D6): approve → follow-on
   plan filed; decline → satisfactory with the reason recorded in its `triggers.json`.
6. **Guidance + land (Epic 5).** `yf-skill-authoring` gains the length rules and the rating
   procedure (it is 295 over the cap itself and carries no length guidance today). Redeploy
   from `main`, then prove it on the operator's machine: pi startup shows no skill
   diagnostics (#407's own check) and CC's debug log has no `Skill listing over budget`
   line (EXP-004).

**Deliberately out of scope:** closing the pi-vs-CC rules-aggregate asymmetry (EXP-003
implication 3). It changes what the evals measure, so it is filed as a follow-on issue
(Issue 5.4), not fixed silently. Also out of scope: skill splits themselves (D6: they go to
a follow-on plan).

D3 is settled (re-confirmed after EXP-002). Its cost is a known, accepted property of the FULL
tier, not a risk to mitigate by scoping it down. The plan still has to make that cost
*bearable*: run the two harnesses in parallel, stop each session on activation, and
report progress. It must not silently weaken the tier.

## Epics

> **Execution mode is in-place** (`.yf/plan/config.local.json` → `execute.worktree: false`),
> so Issue 0.1 cuts and checks out the execute branch before any SPEC commit (precedent:
> plan-068 Issue 0.1). Scratch eval clones live under `~/.cache/plan072-eval/`, outside the
> repo, with the origin remote removed.

### Epic 0: SPEC-first
- Issue 0.1: Cut and check out `plan-072-james-dixson-bae8de-execute` from `main` in the primary checkout, and record the base SHA to `assets/execute-base.txt`. First, before every SPEC edit: in-place mode has one address space, so an earlier commit would land on `main`.
- Issue 0.2: Confirm the three allocated ids are free (`REQ-YF-EMBED-007`, `REQ-SKAUTH-061`, `REQ-SKAUTH-062`) and record them in `assets/req-allocation.md`. If any is taken, allocate the next free one and record it; SC1b reads this file.
  - depends-on: 0.1
- Issue 0.3: SPEC.md §3.2: add `REQ-YF-EMBED-007` (Agent Skills field rules on `skills/*/SKILL.md`: description 1–1024; name 1–64, `[a-z0-9-]`, no edge or double hyphen, equals parent dir; enforced by `scripts/check_frontmatter.py` FAST+FULL; `agents/*.md` excluded with the reason). Amendment-log entry citing #407.
  - depends-on: 0.2
  - resolves-upstream: #407 (include)
- Issue 0.4: `skills/yf-skill-authoring/SPEC.md`: add `REQ-SKAUTH-061` (the rating: crisp ≤600 / satisfactory ≤1024 / loose >1024; "all intents" = every intent's trigger rate ≥0.5 over ≥3 reps on pi AND claude-code; derived from `evals/triggers.json`; new skills target crisp; satisfactory requires a recorded operator decline of a split). Living-amendment entry.
  - depends-on: 0.2
- Issue 0.5: `skills/yf-skill-authoring/SPEC.md`: add `REQ-SKAUTH-062` (trigger-eval contract: `triggers.json` schema; detector = CC `Skill` call or tool args touching an installed `skills/<n>/` path or `yf skill-dir <n>`; stop rule; candidate vs installed mode; mandatory loaded-text verification before scoring; per-CC-run listing-budget capture; verdict PASS / FAIL / INCONCLUSIVE, where missing harness binary or auth = INCONCLUSIVE). Plus the `SPEC.md` amendment-log line that the FULL tier now carries the eval row (D3).
  - depends-on: 0.2

### Epic 1: Hard gate
- Issue 1.1: Extend `scripts/check_frontmatter.py` to enforce `REQ-YF-EMBED-007` on `skills/*/SKILL.md` only, measuring the parsed YAML scalar (what harnesses measure). Report every violation with its count, e.g. `description 1325 > 1024 (over by 301)`. Tag the code with the REQ id.
  - depends-on: 0.3
- Issue 1.2: Negative controls: `scripts/test_check_frontmatter.py` with one fixture per rule (description >1024, empty description, name >64, bad charset, leading hyphen, `--`, name ≠ dir) that the check must FAIL, plus an `agents/*.md` with a 2000-char description that it must PASS. Add a FAST+FULL recipe row `frontmatter-tests` and a §3 glob for the test file.
  - depends-on: 1.1

### Epic 2: Trigger-eval harness
- Issue 2.1: Ship `scripts/checks/skill_trigger_eval.py`, promoted from `assets/exp-003/runner.py` + `rescore.py` and implementing `REQ-SKAUTH-062`. `--mode candidate|installed`, `--harness pi|cc|both` (parallel), `--skills <csv>|all`, `--reps N` (default 3), `--json`. Scratch clones under `~/.cache/yf-trigger-eval/`, origin removed. Exit 0 PASS / 1 FAIL / 4 INCONCLUSIVE (matching `change_validation.py`'s `EXIT_INCONCLUSIVE`). Before scoring, the candidate mode **must** verify the loaded description text equals the staged candidate (EXP-005) and fail INCONCLUSIVE on mismatch.
  - depends-on: 0.5
- Issue 2.2: Tests for the harness that need no live model: detector unit tests over the recorded EXP-003 streams (they must reproduce `assets/exp-003/rescored.txt` exactly), fixture-application and reset tests, and the INCONCLUSIVE paths (binary absent on PATH, auth failure text, candidate-hash mismatch). Recipe row `trigger-eval-tests` in FAST+FULL.
  - depends-on: 2.1
- Issue 2.3: Author `skills/<n>/evals/triggers.json` for all 20 skills: ≥3 should-trigger (with fixtures where a precondition matters) + ≥3 near-miss naming the siblings, the six from EXP-003 seeded verbatim. Update each skill README's layout fence for the new `evals/` file (the `e-readme-layout` mechanical check requires it).
  - depends-on: 0.5
- Issue 2.4: Wire `uv run scripts/checks/skill_trigger_eval.py --mode installed --skills all --harness both --reps 3` as a FULL-tier recipe row (D3). The row runs from the checkout under test and never on the FAST tier.
  - depends-on: 2.1, 2.3

### Epic 3: Trim and rate
- Issue 3.1: Baseline: candidate-mode rating of all 20 **current** descriptions, both harnesses, 3 reps. Record per skill in `triggers.json` (per-harness per-intent rates, description sha256, harness versions, mode) and snapshot to `assets/ratings-baseline.json`.
  - depends-on: 2.1, 2.3
- Issue 3.2: Trim the five over-cap descriptions (`yf-drift-check`, `yf-skill-authoring`, `yf-okf`, `yf-beads-upstream`, `yf-change-validation`) to ≤1024, aiming ≤600. Where a TRIGGER/SKIP clause is dropped, put the rationale into the SKILL.md body rather than deleting it. Re-rate in candidate mode. Accept a trim only if no intent's rate falls below 0.5 on either harness. After this issue, `check_frontmatter.py` is green on the tree.
  - depends-on: 1.1, 3.1
- Issue 3.3: Best-effort trim of the other 15 toward ≤600 (starting with `yf-okf-hygiene` at 997, the nearest to the cap). Same accept rule. A skill whose baseline already misses an intent gets TRIGGER-wording changes first (EXP-003 implication 2). Record, for each, the shortest accepted text and its rating.
  - depends-on: 3.1
- Issue 3.4: Write `assets/ratings-final.md`: the before/after table (chars, rating per harness) for all 20, and the list of skills still not crisp with the measured reason (which intent, which harness, what rate).
  - depends-on: 3.2, 3.3

### Epic 4: Split proposals
- Issue 4.1: For each not-crisp skill in 3.4, write `assets/split-proposals/<skill>.md`: what the description is carrying that won't fit, the proposed split lines, and which intents each half would own. If 3.4 lists none, record that and close.
  - depends-on: 3.4
- Issue 4.2: Apply the operator's decisions from the split gate. **Approve** → file a follow-on upstream issue (via `/yf-beads-upstream`, not a hand-run `gh`) and leave the skill satisfactory pending it. **Decline** → record `accepted: satisfactory` + reason + date in the skill's `triggers.json`.
  - depends-on: 4.1

### Epic 5: Guidance, follow-ons and landing
- Issue 5.1: `skills/yf-skill-authoring/SKILL.md` + reference: the length rules (`REQ-YF-EMBED-007`), the rating (`REQ-SKAUTH-061`), and how to run the eval for a new or edited skill (`REQ-SKAUTH-062`), with the pointer that the description is routing, not documentation. Keep its own description within its rating.
  - depends-on: 0.4, 0.5, 3.2
- Issue 5.2: README/docs touch-ups the drift manifest requires for the new script, the new recipe rows, and the `evals/` convention. Run the FULL tier on the execute branch before landing.
  - depends-on: 1.2, 2.4, 3.3, 5.1
- Issue 5.3: After landing and redeploy from clean `main` (the AGENTS.md preconditions), verify on the operator's machine: pi startup lists no `[Skill conflicts]`, the CC `--debug-file` log has no `Skill listing over budget` line, and an installed-mode eval run passes. Record the outputs in `assets/post-deploy.md`.
  - depends-on: 5.2
- Issue 5.4: File a follow-on upstream issue for the rules-aggregate asymmetry (pi's `~/.pi/agent/AGENTS.md` carries 4 yf protocol blocks and CC's `YOSHIKO_FLOW.md` carries 9; EXP-003), stating the measured effect on the drift-check/instructions misses. Via `/yf-beads-upstream`.
  - depends-on: 3.4
- Issue 5.5: Post the #302 evidence (plan-070 is absent, so `get_next_index()` returned 071, colliding with the landed plan-071-james-dixson-d19ce8 at this plan's init) as a comment on #302.
  - depends-on: 0.1

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: both harnesses are authenticated and runnable headless
- Type: auto
- Condition: `claude -p` and `pi -p` each complete a trivial prompt non-interactively on this machine
- Test: claude -p "Reply ok." >/dev/null 2>&1 && pi -p --no-session "Reply ok." >/dev/null 2>&1
- Blocks: 3.1, 2.4
- Instructions: Frontloaded to execute start: every live eval depends on it, and it's decidable before any code runs. On failure, log in to the failing harness (`claude` → `/login`, `pi` → provider auth) and re-run.
- test_class: probe
- cwd: repo-root

### Capability Gate: split decisions
- Type: human
- Condition: The operator has decided approve or decline for every proposal in `assets/split-proposals/`
- Test:
- Blocks: 4.2
- Instructions: Mid-DAG by necessity: which skills need a split proposal is only known after Epic 3 measures the trims, so this gate can't be decided at execute start. Review each proposal. Approve (a follow-on plan is filed) or decline with a reason (the skill is accepted as satisfactory). If 4.1 recorded no proposals, answer "none".
- test_class: consent
- cwd: repo-root

### Capability Gate: upstream writes
- Type: human
- Condition: The operator authorizes three classes of outward-facing GitHub write on dixson3/yoshiko-flow: filing follow-on issues for approved skill splits, filing the rules-aggregate asymmetry issue, and commenting the plan-number collision evidence on #302
- Test:
- Blocks: 4.2, 5.4, 5.5
- Instructions: Consent class, decidable at execute start because it authorizes the classes of write, not specific issue text. Answer it with the Start Gate. Each write then goes through `/yf-beads-upstream`'s previewed push, or `gh issue comment` with a quoted-heredoc body, read back after posting.
- test_class: consent
- cwd: repo-root

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **FULL-tier cost and time (D3).** ~360 runs per harness, ~2.4 h wall, ~$55–90 CC per FULL run, every land-the-plane. | high | Accepted by the operator with the numbers (D3 re-confirmation). Made bearable, not reduced: parallel harnesses, stop-on-activation, progress output. The row is FULL-only, never FAST. |
| R2 | **A trim is "verified" against the old text.** CC silently shadows a project skill copy with the user-scope install (EXP-005). | high | Candidate mode uses `--setting-sources project`, and the harness **verifies** the loaded description equals the staged candidate before scoring; a mismatch is INCONCLUSIVE. Issue 2.2 tests that path. |
| R3 | **Nondeterministic evals flap ratings and the FULL tier.** | med | Rate threshold ≥0.5 over ≥3 reps (REQ-SKAUTH-061), not all-pass. The EXP-003 baseline measured 116/126 with a known miss set, which calibrates what "normal" looks like. |
| R4 | **Candidate mode ≠ what users get.** Isolated runs drop other skills and the CC rules aggregate (EXP-005). | med | Every rating records its mode. The FULL-tier row runs installed mode after deploy (Issue 5.3), so the shipped result is also measured under full config. |
| R5 | **Unattended FULL runs have no harness auth.** | med | INCONCLUSIVE, never PASS (REQ-SKAUTH-062), matching `change_validation.py`'s existing fail-closed contract. CI (`ci.yml`) calls checkers by name and does not run the FULL tier, so it is unaffected. |
| R6 | **The hard gate goes red on the tree the moment it lands.** Five skills are over. | med | Issue 3.2 (the five trims) lands in the same change-set as 1.1, and SC3 is checked on the merged tree, not per issue. |
| R7 | **Trims drop deliberate negative routing.** | med | The accept rule is measured (no intent below 0.5 on either harness), near-miss intents name the siblings, and a dropped SKIP clause moves into the SKILL.md body instead of being deleted. |
| R8 | **Self-modification.** The plan edits skills (including `yf-skill-authoring`) while the session runs installed copies. | low | AGENTS.md three-artifacts rule: no `yf skills install` / `yf self install` mid-execution. Redeploy only in Issue 5.3, from clean `main`. |
| R9 | **Eval outcomes depend on the machine.** CC's listing drop order depends on usage history (EXP-004). | low | Each CC run captures whether the budget WARN fired, and candidate mode is unaffected (14-skill listing, far under budget). |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | The three REQs are in the SPECs | `grep -q 'REQ-YF-EMBED-007' SPEC.md && grep -q 'REQ-SKAUTH-061' skills/yf-skill-authoring/SPEC.md && grep -q 'REQ-SKAUTH-062' skills/yf-skill-authoring/SPEC.md` -> exit 0 | 0.3, 0.4, 0.5 |
| SC1b | SPEC commits precede code commits on the execute branch | `B=$(cat docs/plans/plan-072-james-dixson-bae8de/assets/execute-base.txt); fs=$(git log --format=%H --reverse "$B..HEAD" -- SPEC.md skills/yf-skill-authoring/SPEC.md \| head -1); fc=$(git log --format=%H --reverse "$B..HEAD" -- scripts/check_frontmatter.py scripts/checks/skill_trigger_eval.py \| head -1); test -n "$fs" && { test -z "$fc" \|\| git merge-base --is-ancestor "$fs" "$fc"; }` -> exit 0 | 0.1, 0.2, 0.3, 0.5 |
| SC2 | Every skill is within the hard limits | `uv run scripts/check_frontmatter.py` -> exit 0 | 1.1, 3.2 |
| SC3 | The hard gate is observed to fail on each rule | `uv run scripts/test_check_frontmatter.py` -> exit 0 | 1.2 |
| SC4 | The eval harness is tested without live models and reproduces the EXP-003 scoring | `uv run scripts/checks/test_skill_trigger_eval.py` -> exit 0 | 2.1, 2.2 |
| SC5 | Every skill has an intent set with ≥3 trigger and ≥3 near-miss intents | `uv run scripts/checks/skill_trigger_eval.py --validate-intents --min-trigger 3 --min-nearmiss 3` -> exit 0 | 2.3 |
| SC6 | The FULL tier carries the eval row for every skill, both harnesses | `grep -F 'skill_trigger_eval.py --mode installed --skills all --harness both --reps 3' CHANGE-VALIDATION.md` -> exit 0 | 2.4 |
| SC7 | No skill is loose, and every skill has a recorded rating | `uv run scripts/checks/skill_trigger_eval.py --report --require-rated --max-rating satisfactory` -> exit 0 | 3.1, 3.2, 3.3, 3.4 |
| SC8 | Every not-crisp skill carries an operator decision | `uv run scripts/checks/skill_trigger_eval.py --report --require-decision-for-noncrisp` -> exit 0 | 4.1, 4.2 |
| SC9 | Aggregate description size fell | manual: assets/ratings-final.md shows the corpus description total below the 16,898-char baseline, with a per-skill before/after table | 3.4 |
| SC10 | pi and CC start clean on the operator's machine after redeploy | manual: assets/post-deploy.md shows pi's startup with no [Skill conflicts] block and a CC --debug-file log with no "Skill listing over budget" line (EXP-004), both from after the Issue 5.3 redeploy | 5.3 |
| SC11 | The authoring guidance is in the conventions skill | `grep -q 'REQ-SKAUTH-061' skills/yf-skill-authoring/SKILL.md && grep -q 'skill_trigger_eval' skills/yf-skill-authoring/SKILL.md` -> exit 0 | 5.1 |
| SC12 | FULL tier green on the merged tree | manual: land's L3 validate-merged reports PASS for the FULL tier, including the eval row | 5.2 |
| SC13 | The follow-ons are filed | manual: the rules-asymmetry issue (5.4) exists and #302 carries the collision evidence comment (5.5) | 5.4, 5.5 |
