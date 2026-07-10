# Plan: Add a 'Claude Code Optimization' README section (efficiency framing) and expand docs/recommended-settings.md with the permissions block, tool-disables, and notification/upload keys

**ID:** plan-025-james-dixson-0183e8
**Author:** james-dixson
**Created:** 2026-07-09
**Status:** complete
**Epic:** yf-mol-2l1
**Fingerprint:** 4b0015dd80d529a9240fa1dfc569ad5c016686410544df1638d6c518f524726a
**Phase log:**
- 2026-07-09 scoping: initial scope captured
- 2026-07-09 drafting: plan v1 presented (docs-only; no investigation phase — content is fully known)
- 2026-07-09 review: plan v1 presented (docs-only)
- 2026-07-09 approved: operator approved
- 2026-07-09 intake: epic yf-mol-2l1 poured
- 2026-07-09 executing: start gate resolved
- 2026-07-09 reconciling: post-execution reconciliation
- 2026-07-09 complete: plan complete

## Objective

Add a new top-level `## Claude Code Optimization` section to the repo `README.md` that
recommends `settings.json` changes for **more efficient** execution of Claude Code against the
`yoshiko-flow` (`yf-*`) skills, and expand the already-linked `docs/recommended-settings.md`
with the new content (the `permissions` block, the Tool-disable list, and the
notification/upload keys) so the detail lives in one place.

The recommendation disables several Claude Code capabilities the `yf-*` skills never use — they
consume context / tool-schema budget, actively interfere with skill execution, are needlessly
promiscuous with Anthropic, or interrupt long autonomous runs. The operator's own
`~/.claude/settings.json` is the reference baseline.

## Motivation

`yoshiko-flow` skills carry always-loaded rule prose (task-tracking, portability, planning,
upstream) that *forbids* native Claude Code mechanisms — native plan mode, Workflows, TodoWrite,
native memory. Prose only steers the model; it does not remove the mechanism, and every unused
native Tool still costs context/tool-schema budget on every turn. `docs/recommended-settings.md`
already documents an **alignment/portability** baseline, but it omits the operator's highest-leverage
**efficiency** levers: the `permissions` block (`defaultMode: bypassPermissions` + safety denials +
Tool disables for `*PlanMode`/`*Worktree`/`Task*`), plus the connector/notification/upload keys.

The README has no discoverable entry point that frames these as an efficiency win, and the operator
wants the recommendation surfaced there. This plan closes that gap: a concise, efficiency-framed
README section as the front door, backed by the expanded reference doc as the single source of truth.

This is a **documentation-only** change. No `SPEC.md` requirement, `yf` CLI behavior, or skill
contract changes — so the SPEC-first rule (AGENTS.md) does not apply; there is no behavior to
land ahead of code.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|

_No existing upstream issue matches (searched `settings optimization claude code README` → none)._
_Per the project coarse-granularity convention (AGENTS.md), a single coarse tracking issue is
filed at INTAKE: **[#80](https://github.com/dixson3/yoshiko-flow/issues/80)** — "Complete
execution of plan-025: Claude Code Optimization README section"._

## Investigation Findings

No investigation phase. All inputs are in hand and inspected:

- **Reference baseline** — the operator's `~/.claude/settings.json` (the `permissions` block with
  `defaultMode: bypassPermissions`, the `deny` list, and the flag keys).
- **Existing doc** — `docs/recommended-settings.md` already covers `disableWorkflows`,
  `todoFeatureEnabled`, `autoMemoryEnabled`, `autoDreamEnabled`, `autoUploadSessions`,
  `disableBundledSkills`, `disableRemoteControl`, `promptSuggestionEnabled`, `spinnerTipsEnabled`,
  `effortLevel`. It is **already linked** from README §Operating & health (README.md:146–150).
- **README structure** — `## Operating & health` (line 128) is the natural neighbor; the new
  `## Claude Code Optimization` section slots after it, before `## Skill frontmatter contract`.

**Boolean correction (decided at scoping).** The operator's request listed
`disableClaudeAiConnectors: false`, `disableBundledSkills: false`, `disableWorkflows: false`.
For `disable*` keys, *disabling the capability* means `true` — and the operator's own
`settings.json` has all three as `true`. The prose ("why disabling is helpful") confirms intent.
**These three are documented as `true`.** The non-`disable*` keys the operator listed as `false`
(`autoMemoryEnabled`, `autoDreamEnabled`, `todoFeatureEnabled`, `autoUploadSessions`,
`inputNeededNotifEnabled`, `agentPushNotifEnabled`) already correctly express "disable" as `false`.

**Tool-vs-Agent distinction (verified).** The `deny` list disables
`TaskCreate`/`TaskGet`/`TaskList`/`TaskOutput`/`TaskUpdate` (the native background-task/workflow
surface), NOT the `Agent` sub-agent-dispatch tool the `yf-*` skills fan out through. The
recommendation must not disable `Agent` — that would break every coordinator/investigator/reviewer
dispatch. A grep of the repo `skills/` tree for every denied native tool
(`SendMessage`, `ReportFindings`, `ScheduleWakeup`, `RemoteTrigger`, `PushNotification`,
`DesignSync`, `Task*`, `*PlanMode`, `*Worktree`) found **zero** references — the skills dispatch
sub-agents exclusively via the `Agent` tool (`subagent_type=...`) and re-dispatch fresh agents on
resume rather than continuing via `SendMessage`. So denying the whole list is safe; no `yf-*`
contract depends on any denied tool.

**Deny-list mechanism (verified — Claude Code docs).** A **bare tool name** in `permissions.deny`
(e.g. `EnterPlanMode`, `TaskCreate`) **removes that tool's schema from the model's context
entirely** — the model never sees it, so the "context / tool-schema savings" claim is accurate for
the bare-name Tool disables. A **scoped** pattern (e.g. `Bash(rm -rf *)`) only blocks at call time
and leaves the schema present — so the `rm -rf` safety denials are a **call-time guard, not a
context saving**. The doc must keep these two mechanisms distinct: context-savings framing applies
to the bare-name Tool disables and the boolean feature-kills; the `rm -rf` globs are safety-only.

## Approach

**Placement decision (scoping): README section is the concise front door; the reference doc is
the single source of truth.** Add a lean `## Claude Code Optimization` README section (efficiency
framing + the `permissions` block fenced + a short headline bullet list + a pointer), and move all
per-key annotation detail into an expanded `docs/recommended-settings.md`. This keeps the README
lean (its own token-efficiency ethos) and avoids two drifting copies of the key tables.

**Every new annotation is tagged with the rationale axis it serves** (all four selected at
scoping), so the "efficiency" claim is concrete rather than asserted:

- **Context savings** — **bare-name** Tool disables (`Task*`, `*PlanMode`, `*Worktree`, `Cron*`,
  `DesignSync`, `NotebookEdit`, `SendMessage`, `PushNotification`, `RemoteTrigger`,
  `ReportFindings`, `ScheduleWakeup`) remove those tools' schemas from context entirely (verified:
  a bare name in `permissions.deny` withholds the schema; a *scoped* pattern only blocks the call),
  plus the boolean feature-kills (`disableWorkflows`, `todoFeatureEnabled`, `disableBundledSkills`)
  drop whole feature categories. This is the real, mechanism-backed context saving.
- **Avoids interference** — native plan mode / Workflows / TodoWrite conflict with
  `yf-plan` + beads execution; disabling stops the model reaching for a forbidden mechanism.
- **Data minimization** — `autoUploadSessions`, `disableClaudeAiConnectors`, `autoDream`/memory:
  not being needlessly promiscuous with Anthropic; keep state local/portable.
- **Fewer interruptions** — `inputNeededNotifEnabled`/`agentPushNotifEnabled` off reduce
  notification noise on long runs. **`askUserQuestionTimeout: "never"` is documented separately as
  a tradeoff, NOT under this axis** (see honesty guardrails): "never" means a question waits
  indefinitely for a human — it favors never auto-answering wrong over unattended progress.

**Honesty guardrails.** (1) `defaultMode: bypassPermissions` is a real security-posture tradeoff —
framed as an efficiency choice for trusted local development with the tradeoff stated, not a free
win; it pairs with `skipDangerousModePermissionPrompt: true` (else the dangerous-mode prompt still
interrupts). (2) The `rm -rf` deny globs are **illustrative / operator-tunable safety**, not a
fixed `yf-*` requirement, and are a call-time block, not a context saving. (3)
`askUserQuestionTimeout: "never"` blocks the run for a human rather than reducing interruptions —
documented as an interactive-correctness tradeoff. `docs/recommended-settings.md` already says
these are "recommendations, not hard requirements"; the new content preserves that framing.

**Structure of the expanded `docs/recommended-settings.md`:**

1. Reframe the intro to add the **efficiency** axis alongside the existing alignment/portability one.
2. New `## The permissions block` section: the fenced `permissions` object (`defaultMode:
   bypassPermissions` + the `rm -rf` safety denials + the Tool-disable deny list), with the
   `bypassPermissions` tradeoff called out.
3. New per-key table for the **Tool disables** (`EnterPlanMode`/`ExitPlanMode`,
   `EnterWorktree`/`ExitWorktree`, `TaskCreate`/`TaskGet`/`TaskList`/`TaskOutput`/`TaskUpdate`,
   `DesignSync`, `NotebookEdit`, `SendMessage`, `PushNotification`, `RemoteTrigger`,
   `ReportFindings`, `ScheduleWakeup`, `CronCreate`/`CronDelete`/`CronList`) — each tagged with its
   rationale axis and a note on which skill contract / native mechanism it neutralizes.
4. New rows for the flag keys not yet documented: `disableClaudeAiConnectors`,
   `inputNeededNotifEnabled`, `agentPushNotifEnabled`, `askUserQuestionTimeout`.
5. Update the `## Reference baseline` JSONC block to include the `permissions` block and the new keys.

**Structure of the README `## Claude Code Optimization` section:**

- 2–3 sentence efficiency framing.
- The `permissions` block, fenced (the headline artifact).
- A short bullet list of the highest-leverage flag keys (not the full table).
- A pointer to `docs/recommended-settings.md` for the full per-key rationale.
- Reconcile the existing README §Operating & health settings paragraph (README.md:146–150) so it
  does not duplicate the new section — trim it to a cross-reference or fold it in.

## Epics

### Epic 1: Expand `docs/recommended-settings.md` (single source of truth)

- Issue 1.1: Reframe the intro + "Why settings and prose both" to add the efficiency axis
  (context/tool-schema budget, promiscuity) alongside the existing alignment/portability framing.
- Issue 1.2: Add the `## The permissions block` section — fenced `permissions` object
  (`defaultMode: bypassPermissions` + `rm -rf` safety denials + Tool-disable deny list) with the
  `bypassPermissions` tradeoff stated honestly.
  - depends-on: 1.1
- Issue 1.3: Add the Tool-disable per-key table (all denied Tools), each tagged with its rationale
  axis (context savings via bare-name schema removal / avoids interference) and the mechanism it
  neutralizes. State explicitly that `Agent` is NOT disabled (dispatch survives) and record the
  grep evidence that no `yf-*` skill references any denied tool (R1). Distinguish bare-name schema
  removal from the scoped `rm -rf` call-time block.
  - depends-on: 1.1
- Issue 1.4: Add rows/sections for the undocumented flag keys — `disableClaudeAiConnectors` (true,
  data-minimization), `inputNeededNotifEnabled` (false) and `agentPushNotifEnabled` (false)
  (fewer-interruptions / notification noise), and `askUserQuestionTimeout` ("never") documented as
  an **interactive-correctness tradeoff** (blocks for a human; not a fewer-interruptions win).
  - depends-on: 1.1
- Issue 1.5: Update the `## Reference baseline` JSONC block to include the `permissions` block and
  all new keys; apply the boolean correction (the three `disable*` keys are `true`); add
  `skipDangerousModePermissionPrompt: true` as the `bypassPermissions` companion (C4). Add a
  one-line note that operator-specific baseline keys (`spinnerVerbs`, `tui`, `enabledPlugins`,
  `extraKnownMarketplaces`) are consciously out of scope. Verify the JSONC parses.
  - depends-on: 1.2, 1.3, 1.4

### Epic 2: Add the README `## Claude Code Optimization` section

- Issue 2.1: Write the new `## Claude Code Optimization` section (after `## Operating & health`):
  efficiency framing, the fenced `permissions` block, a short headline-keys bullet list, and a
  pointer to `docs/recommended-settings.md`.
  - depends-on: 1.5
- Issue 2.2: Reconcile the existing README §Operating & health settings paragraph (README.md:146–150)
  so it cross-references the new section instead of duplicating it.
  - depends-on: 2.1

### Epic 3: Validate

- Issue 3.1: Run the `yf-markdown-lint` authoring subset over both changed files
  (`README.md`, `docs/recommended-settings.md`); resolve any violation. Confirm all relative
  links/anchors (README ↔ doc) resolve.
  - depends-on: 2.2
- Issue 3.2: Verify the recommended `settings.json` / `permissions` JSON is valid and matches the
  operator's reference baseline (key names, values, boolean correction applied).
  - depends-on: 1.5

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations

| Risk | Severity | Mitigation |
|:-----|:---------|:-----------|
| **R1 — Recommending disabling the `Agent` tool / a tool a skill needs.** If the Tool-disable list is described loosely, a reader could disable `Agent` (breaking all fan-out) or another tool a skill depends on. | High → **retired** | Verified: grep of `skills/` for every denied tool (`SendMessage`, `ReportFindings`, `ScheduleWakeup`, `RemoteTrigger`, `PushNotification`, `DesignSync`, `Task*`, `*PlanMode`, `*Worktree`) found **zero** references; dispatch is exclusively via `Agent`/`subagent_type`. Issue 1.3 states `Agent` stays enabled and records the evidence. |
| **R2 — `bypassPermissions` / `askUserQuestionTimeout` presented as free wins.** Both are genuine tradeoffs a naive reader may adopt without understanding the exposure. | Medium | Frame `bypassPermissions` as an efficiency choice for trusted local development (with `skipDangerousModePermissionPrompt` companion) and the tradeoff stated; document `askUserQuestionTimeout: "never"` as blocking-for-a-human (interactive correctness), not a fewer-interruptions win; preserve the "recommendations, not hard requirements" caveat. |
| **R3 — Drift between the README block and the doc baseline.** Two fenced settings snippets can diverge. | Medium | README carries only the `permissions` block + a short bullet list (not the full key tables); the doc is the single source of truth; both are cross-linked. `yf-drift-check` has no manifest edge here, so agreement is enforced by keeping the README lean, not duplicative. |
| **R4 — Stale line references.** Editing README shifts the line numbers this plan cites (146–150). | Low | Reconcile by section heading (`## Operating & health`), not by line number, at execution time. |

## Success Criteria

- `README.md` has a new `## Claude Code Optimization` section with an efficiency framing, the
  fenced `permissions` block, a headline-keys bullet list, and a working link to
  `docs/recommended-settings.md`.
- The existing README §Operating & health settings paragraph no longer duplicates the new section.
- `docs/recommended-settings.md` documents **every** requested key — the `permissions` block
  (`defaultMode: bypassPermissions` + safety denials + Tool disables), `disableClaudeAiConnectors`,
  `disableBundledSkills`, `disableWorkflows`, `autoMemoryEnabled`, `autoDreamEnabled`,
  `todoFeatureEnabled`, `autoUploadSessions`, `inputNeededNotifEnabled`, `agentPushNotifEnabled`,
  `askUserQuestionTimeout` — each annotated with at least one of the four rationale axes.
- The boolean correction is applied: the three `disable*` keys are `true`, not `false`.
- The `Agent` sub-agent-dispatch tool is NOT among the recommended Tool disables, and the doc says
  so explicitly (R1).
- The context-savings claim is mechanism-correct: bare-name Tool disables remove schemas from
  context; the scoped `rm -rf` denials are called out as call-time safety guards, not savings.
- The `bypassPermissions` tradeoff is stated (with the `skipDangerousModePermissionPrompt`
  companion present in the baseline), and `askUserQuestionTimeout: "never"` is documented as a
  blocks-for-a-human interactive-correctness tradeoff, not a fewer-interruptions win (R2).
- Both files pass the `yf-markdown-lint` authoring subset and the recommended-settings JSONC parses.
