# Plan: Create skills/optimal-instructions: an auto-fix skill for CLAUDE.md/AGENTS.md/AGENTS instruction files

**ID:** plan-002-james-dixson-b8b610
**Author:** james-dixson
**Created:** 2026-05-31
**Status:** approved
**Phase log:**
- 2026-05-31 scoping: initial scope captured
- 2026-05-31 drafting: scope locked from Q&A; overlap investigated; synthesizing plan
- 2026-05-31 review: plan v1 presented; reviewer verdict REVISE; 5 concerns + 3 gaps resolved; operator chose split apply (K1 auto / K2 propose) and consistency-only verification; recorded in reviews/pass-1.md
- 2026-05-31 approved: operator approved; audit pass

## Objective
Create `skills/optimal-instructions`, a Claude Code skill that transforms the intent of
pybridge's `.claude/rules/OPTIMIZED_INSTRUCTIONS.md` into an actionable, auto-fixing skill
for project **instruction files**: `CLAUDE.md`, `AGENTS.md`, and `AGENTS/*`. When such a
file is created or modified, the skill reads it, applies optimization + structural edits
directly, and reports what changed.

## Motivation
Instruction files (`CLAUDE.md`, `AGENTS.md`, `AGENTS/*`) are always-loaded context — every
wasted line is paid on every turn. pybridge's `OPTIMIZED_INSTRUCTIONS.md` rule captures how
to keep them tight (action over narrative, one source of truth) and how to structure them
(**AGENTS.md is primary; CLAUDE.md is a thin `@-include` index; behavioral rules live in
`AGENTS/*`**), but it is a passive rule a human must remember to apply. The operator wants
that intent enforced *actively, on write*, as a skill — with primary focus on establishing
**AGENTS.md primacy over CLAUDE.md** and the **`AGENTS/*` pattern** across projects.
Affected: any project that adopts these skills and edits its instruction files via an agent.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| — | (none) | — | Scanned `dixson3/beads-backed-skills`; all 7 open issues are bdplan-specific, none relate to instruction-file optimization. No upstream work incorporated. | — |

## Investigation Findings

**exp-001 — overlap with skill-authoring** (`findings/exp-001-skill-authoring-overlap.md`):
`skill-authoring/agents/optimizer.md` is already a read-only token-efficiency optimizer that
explicitly names `AGENTS.md`/`CLAUDE.md` as targets, with principles near-identical to
`OPTIMIZED_INSTRUCTIONS.md`. skill-authoring's `SKILL.md` "Token efficiency" section is the
canonical Cut/Keep/Extract ruleset. What `OPTIMIZED_INSTRUCTIONS.md` adds and the optimizer
**lacks** is the *structural* convention: CLAUDE.md as a thin `@-include` index with the
AGENTS split. Cross-skill reference is repo-idiomatic (bdplan defers to beads/beads-extra).

**Two distinct bodies of knowledge:**
- **K1 — token-efficiency ruleset** (cut narrative, keep templates, extract scripts). Already
  owned by `skill-authoring`. Applies to all always-loaded files including SKILL.md/agents.
- **K2 — instruction-file structure** (AGENTS.md primary; CLAUDE.md thin `@-include` index;
  behavioral rules in `AGENTS/*`). New; the operator's primary focus; **unowned today.**

**install.sh** (line 112) auto-discovers every `skills/*/` dir; companion rules install only
when a `protocols/` dir exists. optimal-instructions ships **no rule**, so install.sh needs
**zero changes** — verification only.

## Approach

Build `optimal-instructions` as a **doing-skill** that owns **K2** and the **auto-fix-on-write
workflow**, and **references** `skill-authoring` for **K1** (no duplication — per operator and
per the "one source of truth" principle the skill itself enforces).

**Division of ownership (single source of truth for each):**
- `skill-authoring` keeps K1 (token-efficiency Cut/Keep/Extract) and skill-file structure.
- `optimal-instructions` owns K2 (AGENTS.md primacy / CLAUDE.md index / AGENTS/* pattern) in
  its `spec/`, plus the auto-fix workflow, the apply agent, and the change-report format.
- Reciprocal references replace duplication: optimal-instructions → skill-authoring for K1;
  skill-authoring → optimal-instructions for project-instruction-file structure, and its
  optimizer scope note **defers** project instruction files (CLAUDE.md/AGENTS.md/AGENTS/*) to
  optimal-instructions to avoid trigger/scope collision.

**Trigger** (per locked scope): skill only, modeled on `skill-authoring` — `user-invocable:
false`, fires via its `description` TRIGGER text when CLAUDE.md / AGENTS.md / AGENTS/* are
created or modified. No companion rule, no hook. (Accepted limitation: description-only
triggering is best-effort, not guaranteed every write — see Risks.)

**Action** (per locked scope, refined in review): **split apply mode.**
- **K1 (token-efficiency cuts)** — auto-applied. Low-risk, reversible. The apply agent's
  K1 criteria are *cited* from a single named anchor (skill-authoring `SKILL.md` "Token
  efficiency" §), never restated.
- **K2 (structural relocation)** — propose-and-confirm. Demoting CLAUDE.md to an index and
  relocating behavioral rules into AGENTS.md/AGENTS/* is a destructive restructure of
  operator-authored governance, so the agent emits a *proposed* edit set + report and the
  main session writes only after operator confirmation. Never deletes — only relocates.

A dedicated agent reads the changed file, auto-applies K1, proposes K2, and returns a
change report; the main session writes K1 edits, then K2 edits on confirmation.

**Idempotency:** running the skill on an already-optimized file is a no-op (spec REQ) —
required because an auto-fix-on-write skill re-processes its own output on the next write.

**Surface handling:** the behavioral-rules subdir convention exists in two forms in this
codebase — `AGENTS/*` (capitalized, repo-root; as in this repo's `AGENTS/BEADS.md`) and
`.agents/rules/*` (skill-authoring Surface Convention). The skill detects which surface a
project uses and normalizes to *that* surface rather than imposing one (spec REQ).

**Surface-Convention carve-out:** skill-authoring's Surface Convention §1 forbids its
*installer* from writing to `AGENTS/` or editing `CLAUDE.md`. This skill edits those files
at **runtime via its apply agent** — a different mechanism, explicitly permitted. The spec
records this carve-out so a consistency reviewer doesn't read it as a contradiction.

## Epics

### Epic 1: Author the optimal-instructions skill
- Issue 1.1: Write `skills/optimal-instructions/SKILL.md` — YAML frontmatter with a
  `description` whose TRIGGER fires on create/modify of CLAUDE.md / AGENTS.md / AGENTS/*, and
  SKIP routing that hands skill *authoring* files to skill-authoring; `user-invocable: false`;
  `SKILL_DIR` resolver; orchestration: identify changed instruction file → dispatch apply
  agent → write edits → surface change report. References skill-authoring for K1; summarizes
  K2 inline only as a pointer to `spec/`. Frontmatter must pass the OPTIMIZED_SKILLS.md audit.
- Issue 1.2: Write the dedicated apply agent `skills/optimal-instructions/agents/<name>.md`
  (distinct name from skill-authoring's read-only `optimizer.md` — e.g. `instruction-optimizer.md`).
  Inputs: target file path + file kind (CLAUDE.md | AGENTS.md | AGENTS/* | .agents/rules/*).
  Behavior, **split apply mode**: (1) auto-apply K1 token-efficiency edits — cite the single
  canonical anchor **skill-authoring `SKILL.md` "Token efficiency" §** as the criteria source,
  do NOT restate the ruleset; (2) emit K2 structural changes as a *proposal* (AGENTS.md primacy;
  CLAUDE.md reduced to `@-include` index + Upstream-Tracking-class essentials; behavioral rules
  relocated to the project's detected rules surface) — never write K2 without confirmation.
  Only relocate, never delete. Idempotent: a no-op on already-optimized input. Preserve literal
  command blocks, behavioral constraints, output-format specs. Emits edited K1 content + K2
  proposal + structured change report.
  - depends-on: 1.1
- Issue 1.3: Write `skills/optimal-instructions/spec/` capturing as numbered REQ-*:
  K2 structure (AGENTS.md primacy, CLAUDE.md `@-include` index, behavioral-rule subdir pattern,
  what content belongs where); the **split apply contract** (K1 auto / K2 propose-and-confirm,
  relocate-never-delete); **idempotency** (re-run on optimized file = no-op); **surface
  detection** (recognize/normalize to `AGENTS/*` *or* `.agents/rules/*`, do not impose one);
  the **runtime carve-out** vs Surface Convention §1; and the no-duplication-with-skill-authoring
  boundary (K1 lives only in skill-authoring). Include one inline before/after acceptance
  example so behavior is falsifiable without a separate fixture harness. Per AGENTS/CONSISTENCY.md
  a new skill drafts a proposed spec for operator approval.
  - depends-on: 1.1

### Epic 2: Integrate with skill-authoring (no duplication)
- Issue 2.1: Tweak `skills/skill-authoring/` so K1/K2 cohere without duplication and triggers
  don't collide: (a) **edit skill-authoring's `description` SKIP clause** (not just the body)
  to carve out project-root instruction files (CLAUDE.md/AGENTS.md/AGENTS/* not under a skill
  dir) and route them to optimal-instructions — routing is driven by the two `description`
  fields, so deferral must live there. The distinguishing axis (skill-dir vs project-root)
  goes in BOTH descriptions: skill-authoring SKIPs project-root instruction files;
  optimal-instructions SKIPs instruction files inside a skill dir. (b) optimizer scope note +
  SKILL.md body defer the structural convention to optimal-instructions; (c) add a one-line
  reference to optimal-instructions for K2; (d) confirm skill-authoring does not restate K2.
  Net: reciprocal references, descriptions mutually exclusive on the CLAUDE.md/AGENTS.md case,
  zero duplicated content.
  - depends-on: 1.1, 1.3

### Epic 3: Documentation + install wiring (AGENTS/DOCUMENTATION.md)
- Issue 3.1: Write `skills/optimal-instructions/README.md` with the required sections
  (one-line description, prerequisites, install, usage, phase/behavior model, file layout).
  - depends-on: 1.1, 1.2, 1.3
- Issue 3.2: Update project `README.md` — add optimal-instructions to the skills index table,
  add a per-skill summary section, update the prerequisites table if any new dep. Verify
  install.sh auto-discovers the skill (no code change expected; confirm by dry-run/read).
  - depends-on: 3.1
- Issue 3.3: If Epic 2 changed skill-authoring's documented behavior, update
  `skills/skill-authoring/README.md` and the project README skill-authoring summary to match.
  - depends-on: 2.1

### Epic 4: Consistency verification (AGENTS/CONSISTENCY.md)
- Issue 4.1: Run the CONSISTENCY.md sub-agent check on `skills/optimal-instructions/` (all 4
  categories + spec compliance) AND on `skills/skill-authoring/` (changed in Epic 2). Resolve
  every FAIL in-pass; report INCONCLUSIVE items to the operator. Two extra cross-checks beyond
  the standard categories: (a) the apply agent's K1 citation resolves to the named anchor
  (skill-authoring SKILL.md "Token efficiency" §) and that anchor still exists; (b) the two
  skills' `description` fields are mutually exclusive on the CLAUDE.md/AGENTS.md case
  (skill-dir vs project-root axis present in both).
  - depends-on: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2, 3.3

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations
- **Description-only trigger is best-effort.** A pure `description`-triggered skill cannot
  guarantee it fires on every CLAUDE.md/AGENTS.md/AGENTS/* write (no rule, no hook, per locked
  scope). *Mitigation:* invest in a high-quality `description` with explicit TRIGGER/SKIP
  routing; document the limitation in README; the operator accepted this tradeoff.
- **Trigger collision with skill-authoring** on CLAUDE.md/AGENTS.md (both claim them via their
  `description`). *Mitigation:* Epic 2.1 edits BOTH `description` fields (not just bodies) so
  routing is mutually exclusive on the skill-dir vs project-root axis; Epic 4.1 verifies it.
- **Auto-fix over-reach** — the apply agent could strip content that looks like narrative but
  encodes a behavioral constraint (e.g. the "Landing the Plane" session protocol).
  *Mitigation:* K1 "What to keep" is explicit about constraints/templates/command blocks; K1
  cuts are reversible and reported; structural moves (K2) are propose-and-confirm, not auto.
- **CLAUDE.md primacy demotion is destructive.** Relocating content out of CLAUDE.md could
  break projects relying on it. *Mitigation (operator decision):* K2 structural relocation is
  **propose-and-confirm** — the agent never writes K2 edits unattended; only relocates, never
  deletes; spec defines exactly what may move; every relocation is in the operator-visible report.
- **Duplication creep** — the very anti-pattern the skill enforces. *Mitigation:* Epic 2 +
  CONSISTENCY check explicitly verify no K1/K2 restatement across the two skills.

## Success Criteria
1. `skills/optimal-instructions/` exists with `SKILL.md`, the apply agent, `spec/`, and
   `README.md`; frontmatter passes the OPTIMIZED_SKILLS.md audit.
2. The skill's `description` contains explicit TRIGGER text naming create/modify of
   CLAUDE.md / AGENTS.md / AGENTS/* and a SKIP clause routing skill-authoring's domain
   (skill-dir instruction files) away. (Routing is best-effort per the documented limitation;
   this criterion is about the description's content, which is verifiable — not a runtime guarantee.)
3. Split apply works: K1 token-efficiency edits auto-apply; K2 structural changes are proposed
   and written only on confirmation; the agent returns a change report and is idempotent
   (no-op on already-optimized input). K1 criteria are *cited* from skill-authoring, not restated.
4. K2 (AGENTS.md primacy / CLAUDE.md @-include index / behavioral-rule subdir pattern) is
   defined once, in optimal-instructions `spec/`, with surface detection (AGENTS/* or
   .agents/rules/*) and the runtime carve-out vs Surface Convention §1 recorded.
5. The two skills' `description` fields are mutually exclusive on the CLAUDE.md/AGENTS.md case;
   no duplicated ruleset content between them.
6. Project README + skill READMEs updated; install.sh auto-discovers the skill with no edit.
7. CONSISTENCY.md check passes (no FAIL) on both changed skills, including the K1-anchor and
   description-mutual-exclusivity cross-checks.
