---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: local-codebase — findings

Method: `direct` (local file reads; no web search). Retrieved 2026-07-22.

Scope covered: `~/.claude/rules/YOSHIKO_FLOW.md` (the aggregated always-loaded
ruleset), all `~/.claude/skills/yf-*/SKILL.md` frontmatter descriptions, the
`skills/*/protocols/*.md` companion rules, `docs/recommended-settings.md`, the
repo `SPEC.md` (`REQ-YF-FLOW`), and the sibling repo `../naba`
(`AGENTS.md`, `CLAUDE.md`, `.claude/`, `skills/`).

---

## 1. The always-loaded companion-rule surface (`YOSHIKO_FLOW.md` aggregate)

`YOSHIKO_FLOW.md` is a single `yf`-managed file that aggregates one fenced
section per rule-bearing skill's companion protocol. It is the entire
always-loaded rule surface for the yf skill set.

> "`yf` surfaces every rule-bearing skill's companion protocol as **one**
> operator-facing file in the rules dir, `YOSHIKO_FLOW.md`, instead of a scatter
> of standalone `*.md` files." `[S-LC-2]` (SPEC §3.3.1, REQ-YF-FLOW)

> "Each section body is the protocol file **verbatim**, so its `sha256` equals
> the `manifest.json` file sha256." `[S-LC-2]`

**Enumerated sections (8 protocols), each with the stated "trigger a description
alone cannot fire" reason** (all quotes from `[S-LC-1]`, the installed
`YOSHIKO_FLOW.md`):

| # | Protocol (skill) | Stated reason it must be always-loaded |
|:--|:-----------------|:----------------------------------------|
| 1 | `BEADS_INIT.md` (yf-beads-init) | Binds the preflight trigger + false-negative invariant; also the sole home for two general bd-usage mandates. |
| 2 | `CHANGE-VALIDATION-TRIGGER.md` (yf-change-validation) | Engine executes a recipe → verdict from exit code; a description cannot fire the on-edit/pre-push trigger. |
| 3 | `DRIFT-CHECK-TRIGGER.md` (yf-drift-check) | Engine is `user-invocable: false`; only a rule can fire its on-edit trigger. |
| 4 | `INSTRUCTIONS.md` (yf-optimal-instructions) | On-edit routing of instruction-file optimization by file location. |
| 5 | `MARKDOWN_LINT.md` (yf-markdown-lint) | Portable cross-harness equivalent of the Claude-Code `FileChanged` hook; binds the on-edit trigger. |
| 6 | `PLANS.md` (yf-plan) | Planning-intent triggers + override of native plan mode. |
| 7 | `RESEARCH.md` (yf-research) | Routing vs the compiled-in built-in `deep-research` (a description cannot override the built-in). |
| 8 | `UPSTREAM_TRACKING.md` (yf-beads-upstream) | Close-time push trigger explicitly NOT carried in the SKILL description. |

### Verbatim "description cannot fire" reasons

**BEADS_INIT.md** — the rule carries triggers a description misses AND is the only
home for cross-cutting bd mandates:

> "this rule binds only the triggers a description cannot reliably catch. It is
> the shared **dependency-verification home** for every beads-backed skill, and —
> as the sole skill-owned always-loaded beads surface — also carries the two
> general bd-usage mandates below." `[S-LC-1]`

The two mandates with no other home (irreducible):

> "**Use `bd` for ALL task tracking.** Never markdown TODOs, `TodoWrite`, or
> inline task lists." `[S-LC-1]`

> "**Use non-interactive shell flags** so an `-i` alias can't hang on a
> confirmation prompt: `rm -f` / `rm -rf`, `cp -f`, `mv -f`; `ssh`/`scp -o
> BatchMode=yes`; `apt-get -y`; `HOMEBREW_NO_AUTO_UPDATE=1` for `brew`."
> `[S-LC-1]`

Note the false-negative invariant is a genuine behavioral rule, not a mere
trigger:

> "**Never infer \"bd not initialized\" from `bd status`'s exit code alone.**
> `bd status --json` can return an **error JSON with exit 0**" `[S-LC-1]`

**CHANGE-VALIDATION-TRIGGER.md** — the engine's verdict comes from executing
commands, so the model cannot self-fire it from prose:

> "The engine **executes** a repo's recorded validation recipe (build / test /
> lint) and reports a verdict from an exit code — so a `description` alone cannot
> reliably fire it; this rule binds the on-edit and pre-push triggers." `[S-LC-1]`

Gated on a per-repo approved manifest (so the rule is a silent no-op most repos):

> "**Unless the repo has an approved `CHANGE-VALIDATION.md`** (§0 `approved:
> yes`), this trigger is a **silent no-op**" `[S-LC-1]`

**DRIFT-CHECK-TRIGGER.md** — non-invocable engine:

> "The engine is `user-invocable: false`, so a `description` alone cannot reliably
> fire it — this rule binds the on-edit trigger that a description cannot."
> `[S-LC-1]`

Also gated on an approved manifest → silent no-op otherwise. `[S-LC-1]`

**INSTRUCTIONS.md** — this one is a routing/hygiene rule, not strictly a
"description can't fire" case; it fires on every instruction-file edit:

> "Always-loaded instruction surfaces … must stay token-efficient. They load on
> every turn, so waste is paid repeatedly." `[S-LC-1]`

> "**Apply on every create or modify** of an instruction file, routed by where
> the file lives" `[S-LC-1]`

**MARKDOWN_LINT.md** — the rule is the portable substitute for a native hook, and
is opt-in per repo:

> "It is the **portable, cross-harness** equivalent of the optional Claude-Code
> `FileChanged` hook documented in `SKILL.md` — use one, not both." `[S-LC-1]`

> "**Unless the repo has a `.markdown-lint-on-edit` marker at its root**, this
> trigger is a **silent no-op**" `[S-LC-1]`

**PLANS.md** — overrides a native harness mechanism:

> "All planning uses the `/yf-plan` skill. Do not use native plan mode." `[S-LC-1]`

(This content is largely duplicated in the SKILL description — see §2 — making it
a partial candidate for collapse, though the native-plan-mode override is the
load-bearing part a description cannot guarantee.)

**RESEARCH.md** — cannot override a compiled-in harness feature via a description:

> "`yf-research` does not override the built-in (it can't — the built-in is
> compiled into the CLI)" `[S-LC-1]`

**UPSTREAM_TRACKING.md** — the close-time trigger is explicitly excluded from the
description and lives only in the rule:

> "Procedure … lives in the skill's `SKILL.md`; this rule binds only what a
> description cannot reliably catch." `[S-LC-1]`

> "On push-like operations, session or plan close, or \"land the plane\": invoke
> `/yf-beads-upstream` to push **open + deferred** beads … upstream before the
> session ends." `[S-LC-1]`

The SKILL description itself confirms the split (see `[S-LC-4]`):

> "The close-time / land-the-plane push trigger is NOT carried in this
> description — it lives in the always-loaded companion rule
> (protocols/UPSTREAM_TRACKING.md)." `[S-LC-4]`

### Irreducible-core reading (secondary Q)

The rules that genuinely cannot collapse into a `description` are those whose
firing signal is an **event a description never sees**:

- **On-edit / on-file-change events** — CHANGE-VALIDATION, DRIFT-CHECK,
  MARKDOWN_LINT, INSTRUCTIONS. A `description` triggers on user-intent language,
  not on "a file was just written." `[S-LC-1]`
- **Close-time / land-the-plane events** — UPSTREAM_TRACKING (and BEADS_INIT's
  preflight). Session/plan-close is not a user utterance. `[S-LC-1]`
- **Override of a compiled-in native mechanism** — PLANS (native plan mode),
  RESEARCH (built-in deep-research). `[S-LC-1]`
- **Cross-cutting bd mandates** with no skill-description home — the two mandates
  folded into BEADS_INIT. `[S-LC-1]`

By contrast, PLANS.md's planning-intent triggers and RESEARCH.md's routing prose
overlap heavily with their own SKILL descriptions (§2), so those portions are the
weakest always-loaded content.

---

## 2. Which yf skills carry rich SKILL.md description triggers vs. rely on always-loaded rules

**Finding:** 18 yf skills exist; **8 have a companion protocol** folded into the
`YOSHIKO_FLOW.md` aggregate (always-loaded); the other **10 rely purely on their
SKILL.md `description:` trigger** with no always-loaded surface. `[S-LC-3]`

Protocol-dir mapping (each dir with a `*.md` protocol → one aggregate section):
yf-beads-init, yf-beads-upstream, yf-change-validation, yf-drift-check,
yf-markdown-lint, yf-optimal-instructions, yf-plan, yf-research. `[S-LC-3]`

Skills with **no** companion rule (description-only): yf-beads-authoring,
yf-beads-extra, yf-beads-hygiene, yf-diagram-authoring, yf-incubator,
yf-markdown-format, yf-markdown-html, yf-markdown-pdf, yf-okf,
yf-skill-authoring. `[S-LC-4]`

**Every yf SKILL.md description follows a rich TRIGGER/SKIP contract.** Examples
(all `[S-LC-4]`):

- yf-beads-hygiene: `"TRIGGER when: /yf-beads-hygiene invoked; \"clean up\" /
  \"cleanup\" open or orphaned beads … SKIP for: verifying/repairing beads CONFIG
  or DB health …"`
- yf-drift-check: `"TRIGGER when: a file covered by an approved DRIFT-CHECK.md
  manifest is created or modified … SKIP for: repos with no approved
  DRIFT-CHECK.md (silent no-op …)"` — note the trigger is duplicated in both the
  description AND the always-loaded rule, because `user-invocable: false` means
  the description alone will not fire the model reliably.
- yf-plan: `"TRIGGER when: /yf-plan invoked, user uses planning-intent language …
  OVERRIDE: replaces EnterPlanMode/ExitPlanMode — never use native plan mode."` —
  the OVERRIDE line mirrors PLANS.md, confirming the description/rule overlap.

**Observation `[uncertain]`:** For the 3 engine-style skills (change-validation,
drift-check, markdown-lint) the trigger text appears in BOTH the description and
the always-loaded rule. The stated reason the rule is still needed is the
event-firing gap (on-edit), not novel content — so the descriptions are rich but
insufficient by themselves for event triggers. This is the crux of the research
question and is asserted by the rules' own preambles `[S-LC-1]`, but whether the
description could in practice fire on-edit is an empirical harness question this
DIRECT cluster cannot settle.

---

## 3. Recommended `settings.json` keys (`docs/recommended-settings.md`)

The repo ships an explicit recommended user-scope `settings.json` baseline whose
stated purpose is to make the runtime enforce what the prose rules only steer, and
to reclaim per-turn tool-schema budget. `[S-LC-5]`

> "prose only steers the model; it does not remove the disallowed mechanism.
> Setting these keys aligns the runtime with the contracts so the model cannot
> reach for a mechanism a skill forbids." `[S-LC-5]`

**Two axes:** alignment/portability and efficiency:

> "a bare tool name in `permissions.deny` removes that tool's schema from the
> model's context entirely" `[S-LC-5]`

> "A **bare tool name** in `deny` … removes that tool's schema from the model's
> context entirely — the model never sees it, so this is a real context /
> tool-schema saving. A **scoped** pattern (e.g. `Bash(rm -rf *)`) only blocks at
> call time and leaves the schema present" `[S-LC-5]`

**Recommended keys (verbatim baseline)** `[S-LC-5]`:

- `permissions.defaultMode: "bypassPermissions"` + `skipDangerousModePermissionPrompt: true`
- `permissions.deny`: `rm -rf` safety globs PLUS bare-name tool disables:
  `EnterPlanMode`, `ExitPlanMode`, `EnterWorktree`, `ExitWorktree`,
  `TaskCreate`, `TaskGet`, `TaskList`, `TaskOutput`, `TaskUpdate`, `DesignSync`,
  `NotebookEdit`, `SendMessage`, `PushNotification`, `RemoteTrigger`,
  `ReportFindings`, `ScheduleWakeup`, `CronCreate`, `CronDelete`, `CronList`
- `disableWorkflows: true`
- `todoFeatureEnabled: false`
- `autoMemoryEnabled: false`, `autoDreamEnabled: false`, `autoUploadSessions: false`
- `disableClaudeAiConnectors: true`
- `disableBundledSkills: true`
- `inputNeededNotifEnabled: false`, `agentPushNotifEnabled: false`
- `askUserQuestionTimeout: "never"`
- `disableRemoteControl: true`, `promptSuggestionEnabled: false`,
  `spinnerTipsEnabled: false`, `effortLevel: "medium"`

**Directly relevant to the research question — settings replace prose:**

> "a rule that forbids native workflows or TodoWrite still leaves those tools'
> schemas loaded in context every turn, paying the budget without the benefit. A
> bare-name disable in `permissions.deny` closes that gap — it removes the schema,
> so the rule no longer competes for context with the very mechanism it forbids."
> `[S-LC-5]`

> "The `Agent` tool is NOT disabled — and must not be. It is the sub-agent
> dispatch every `yf-*` coordinator, investigator, and reviewer fans out through"
> `[S-LC-5]`

**Highest-impact keys** (a skill contract is "leaky" without them): `[S-LC-5]`

> "Two keys (`disableWorkflows`, `todoFeatureEnabled: false`) are the
> highest-impact alignment settings and worth setting first; the `permissions`
> block below is the highest-impact efficiency lever."

`todoFeatureEnabled: false` directly enforces the bd-only mandate that
BEADS_INIT.md (§1) carries in prose:

> "\"All task tracking MUST use `bd`. Never use TodoWrite, markdown checklists, or
> inline task lists.\" … Disabling the feature removes the temptation surface
> entirely." `[S-LC-5]`

**Scope:** the baseline is user-scope (`~/.claude/settings.json`); project scope
overrides. `[S-LC-5]` These are recommendations, not requirements:

> "These are **recommendations, not hard requirements** — the skills still
> function without them." `[S-LC-5]`

**Cross-harness caveat `[uncertain]`:** These keys are Claude-Code-specific
(`settings.json`). The doc does not map them to codex/opencode/pi equivalents —
those are out of this cluster's DIRECT scope.

---

## 4. What `../naba` does for global rules across harnesses

**Finding:** naba uses the **AGENTS.md-primary / CLAUDE.md-thin-pointer** pattern
— the same structural convention `yf-optimal-instructions` proposes (§1, K2). It
has **no `AGENTS/` rules dir, no `.agents/` surface, and no per-harness rule
scatter**; global bd conventions are delegated to user-scope rules, not
duplicated in-repo.

CLAUDE.md is a thin pointer to AGENTS.md `[S-LC-7]`:

> "CLAUDE.md is intentionally a thin pointer. AGENTS.md is the single source of
> truth for both project and agent guidance (optimal-instructions: AGENTS.md
> primary, CLAUDE.md a thin @-include)." `[S-LC-7]`

> "All project and agent instructions live in @AGENTS.md." `[S-LC-7]`

AGENTS.md is the single source of truth `[S-LC-6]`:

> "This file is the single source of truth for both human and agent guidance."
> `[S-LC-6]`

**Global/cross-harness bd rules are NOT duplicated in-repo — they are delegated
to user-scope agent rules** `[S-LC-6]`:

> "Issue tracking uses **beads (`bd`)**; the generic bd workflow conventions live
> in your user-scope agent rules and are not duplicated here. naba-specific facts:"
> `[S-LC-6]`

This is the transferable pattern for the research question: keep the *generic*
rule at user scope (out of every repo), and put only *repo-specific* facts in
the project AGENTS.md. naba does still repeat the non-interactive-shell mandate
locally `[S-LC-6]`:

> "**ALWAYS use non-interactive flags** with file operations to avoid hanging on
> confirmation prompts (cp/mv/rm may be aliased to `-i`)" `[S-LC-6]`

— which is the same mandate BEADS_INIT.md carries globally (§1), i.e. an example
of the duplication the minimization effort targets.

**Structural facts** (from directory listing `[S-LC-8]`):

- naba has a `.claude/` dir containing only `worktrees/` — **no `.claude/rules/`,
  no `.claude/skills/` scatter**. Its one skill (`skills/naba/`) is
  compile-time-embedded in the binary, not a rules surface. `[S-LC-8]`
- naba opts into markdown-lint-on-edit via a root `.markdown-lint-on-edit` marker
  file (the exact opt-in mechanism MARKDOWN_LINT.md §1 requires). `[S-LC-8]`
- naba has a root `DRIFT-CHECK.md` (28 KB) — i.e. it opts into the drift-check
  engine via the per-repo manifest, consistent with the always-loaded
  DRIFT-CHECK-TRIGGER.md being a silent no-op until a manifest exists. `[S-LC-8]`

**Transferable to the minimization strategy:** naba demonstrates that a repo can
run the yf engine skills (drift-check, markdown-lint) purely via **per-repo opt-in
marker/manifest files** plus **user-scope global rules**, with the project-root
instruction file kept to a thin CLAUDE.md → AGENTS.md pointer and repo-specific
facts only. It does not carry any of the `YOSHIKO_FLOW.md` aggregate itself in the
repo — that lives at user scope.

---

## Gaps / absences (valid findings)

- **No per-harness (codex/opencode/pi) rule files exist locally.** naba has no
  `.codex/`, no `.opencode/`, no pi config, and no `.agents/` surface — searched
  and absent. Cross-harness mechanism comparison must come from the web clusters,
  not this DIRECT cluster. `[S-LC-8]`
- **No `AGENTS/` (multi-file rules dir) in naba** — the INSTRUCTIONS.md rule
  references `AGENTS/*` as a possible surface, but naba uses a single AGENTS.md.
  `[S-LC-8]`
- The recommended-settings doc is **Claude-Code-only**; it offers no mapping of
  its keys to other harnesses. `[S-LC-5]` `[uncertain]` whether equivalents exist.
