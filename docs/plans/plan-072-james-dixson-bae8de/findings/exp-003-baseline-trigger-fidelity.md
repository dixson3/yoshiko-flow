---
type: Finding
okf_spec: OKF-PLAN
id: exp-003
description: Baseline trigger fidelity of the six sibling skills on pi and claude-code, 21 intents x 3 reps per harness, before any trim; also resolves EXP-001 (detector) and gives the first EXP-002 cost figures
status: complete
created: '2026-09-24'
---
# EXP-003: baseline trigger fidelity (with the EXP-001 detector and EXP-002 cost)

## Approach Tested

- **Subjects:** the two ambiguous sibling clusters from #407. (a) `yf-drift-check` /
  `yf-change-validation` / `yf-optimal-instructions` / `yf-skill-authoring`; (b) `yf-okf` /
  `yf-okf-hygiene`. All descriptions are the current `main` text (the installed copies are
  byte-identical to `skills/`).
- **Intents:** 21 in [assets/exp-003/intents.json](../assets/exp-003/intents.json): 3 should-trigger
  per skill (18) + 3 near-miss should-not-trigger (N1–N3), each listing the siblings it must
  **not** fire. Where an intent's precondition matters (an edited SPEC, AGENTS.md, rules file,
  script), a **fixture** creates it in the clone first (the lesson from the EXP-001 pilot).
- **Runs:** 3 reps × 21 intents × 2 harnesses = 126 fresh headless sessions, driven from the
  herdr tabs `cc-eval` (`claude -p --output-format stream-json`, CC 2.1.282, Opus 5.5) and
  `pi-eval` (`pi -p --mode json --no-session`, pi 0.87.1, cliproxyapi/claude-opus-5-5).
  Each harness had its own scratch clone of `main@5ced143` under `~/.cache/plan072-eval/`,
  with the origin remote removed and `git reset --hard && git clean -fd` before each intent.
  Real operator global config (all installed skills, rules, hooks, MCP).
- **Stop rule:** kill the session once the expected skill activates, or after 6 tool calls,
  or after 150 s. This measures routing, not task completion.
- **Detector** (`rescore.py`, re-scored from raw streams, only tool calls within the 6-call
  cutoff): activation = CC `Skill` tool_use naming the skill; or any tool argument that
  references an installed `.{agents,claude}/skills/<n>/SKILL.md`; or any other file under an
  installed `skills/<n>/`; or `yf skill-dir <n>`. The repo's own `skills/<n>/SKILL.md` is
  deliberately not counted, since authoring intents read it as a target.

## Result

**measured:** CC 59/63, pi 57/63. Every near-miss passed on both (18/18). Per intent:

| id | expect | cc | pi |
| :-- | :-- | :-- | :-- |
| D1–D2 | drift-check | 6/6 | 6/6 |
| D3 | drift-check (edit to `skills/yf-okf/spec/*.md`) | 3/3 | **0/3** |
| V1–V3 | change-validation | 9/9 | 9/9 |
| O1 | optimal-instructions ("tighten my new AGENTS.md section") | 2/3 | **0/3** |
| O2 | optimal-instructions ("add a rule to CLAUDE.md") | **0/3** | 3/3 |
| O3 | optimal-instructions (new `.agents/rules/` file) | 3/3 | 3/3 |
| S1–S3 | skill-authoring | 9/9 | 9/9 |
| K1–K3 | okf | 9/9 | 9/9 |
| H1–H3 | okf-hygiene | 9/9 | 9/9 |
| N1–N3 | none of the near siblings | 9/9 | 9/9 |

Full per-run signal table: [assets/exp-003/rescored.txt](../assets/exp-003/rescored.txt).
Raw per-run JSONL: `run-cc.jsonl`, `run-pi.jsonl` in the same folder.

**measured:** only one wrong-sibling activation in 126 runs: cc O2, where
`yf-change-validation` ran after CC had already edited AGENTS.md itself.

### The misses, read from the transcripts

- **pi D3 (0/3):** the agent treated "make sure nothing else contradicts it" as a manual
  consistency review. It did grep-driven checking of its own and never loaded drift-check.
  **inferred:** the intent is half-covered by drift-check's TRIGGER ("a file covered by an
  approved DRIFT-CHECK.md manifest is modified"). pi only sees the description. CC also has the
  always-loaded `DRIFT-CHECK-TRIGGER.md` rule, which names the edit-time trigger (see below).
- **pi O1 (0/3), cc O1 (1 miss):** the agent tightened the AGENTS.md prose itself with a plain
  edit. The description's trigger is "a project-root instruction file … is created or
  modified". The intent names the file and the task, and the agent judged it didn't need a
  skill (the agentskills.io point that simple tasks don't trigger skills).
- **cc O2 (0/3):** CC read `CLAUDE.md`, saw `@AGENTS.md`, placed the rule in AGENTS.md itself,
  then ran markdown-lint and change-validation. It followed the *policy* optimal-instructions
  encodes without loading the skill. pi loaded the skill in all 3 runs.

## Implications for Plan

1. **Today's descriptions route the sibling clusters well: 116/126 overall, zero near-miss
   false triggers.** The trims therefore have a high baseline to regress from, and this intent
  set is a usable regression gate.
2. **The misses are not description-length problems.** None involve confusion *between*
   siblings. All are "agent did the task without a skill". The fix lever there is TRIGGER
   wording (e.g. naming "tighten/edit a project instruction file" explicitly), not a split.
   So none of the six is a split candidate on this evidence.
3. **The two harnesses are not equivalent eval surfaces.** **measured:** `~/.claude/rules/YOSHIKO_FLOW.md`
   carries 9 yf protocol blocks, including `CHANGE-VALIDATION-TRIGGER.md`, `DRIFT-CHECK-TRIGGER.md`
   and `INSTRUCTIONS.md`. `~/.pi/agent/AGENTS.md` carries only 4 (BEADS_INIT, UPSTREAM_TRACKING,
   PLANS, RESEARCH). Several skills' edit-time triggers live in always-loaded rules on CC and
   are **absent on pi**, where the description is the whole routing surface. **inferred:** this
   explains the pi D3 miss, and means a CC pass can be carried by the rule rather than the
   description. The rating must be defined per harness and state which surfaces were loaded.
   A pi pass is the stricter test of the description itself.
4. **"Triggers on all intents" needs a threshold.** One of three CC O1 runs missed. The plan
   should define pass as trigger rate ≥ a threshold (agentskills.io suggests 0.5 as a
   default), not 3/3, or ratings will flap.

## Recommendations

- Keep this intent set as the seed of `skills/<n>/evals/triggers.json` for the six skills,
  plus the fixtures.
- Record the rules-surface asymmetry as its own finding. It could be an installer gap (the
  pi rules aggregate is missing 5 protocols CC gets) or deliberate. The plan must not fix it
  silently, since it changes what the evals measure.
- Before trimming, re-run D3/O1/O2 on pi with only the description wording changed, to check
  that the misses respond to wording.
