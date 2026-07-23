---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: claude-code-docs

Method: `exa` (`mcp__exa__web_search_advanced_exa`, `includeDomains: ["docs.claude.com","docs.anthropic.com"]`).
Retrieved: 2026-07-22. Provider: exa. Four official Claude Code documentation pages captured in full and quoted verbatim below.

Sources:

- **[S-CC-1]** Claude Code settings — https://docs.anthropic.com/en/docs/claude-code/settings
- **[S-CC-2]** Extend Claude with skills — https://docs.anthropic.com/en/docs/claude-code/skills
- **[S-CC-3]** How Claude remembers your project (memory) — https://docs.anthropic.com/en/docs/claude-code/memory
- **[S-CC-4]** Hooks reference — https://docs.anthropic.com/en/docs/claude-code/hooks

All four are first-party Anthropic documentation → credibility **high**.

---

## RQ(a): What of an always-loaded companion-rule surface is replaceable by (i) richer per-skill SKILL.md description triggers and (ii) settings.json keys?

### Finding 1 — Skill `description` IS the auto-activation trigger; it is always in context, the body is not

> "Every skill needs a `SKILL.md` file with two parts: YAML frontmatter between `---` markers that tells Claude when to use the skill, and markdown content with the instructions Claude follows when the skill runs. The directory name becomes the command you type, and the `description` helps Claude decide when to load the skill automatically." [S-CC-2]

> "`description` | Recommended | What the skill does and when to use it. Claude uses this to decide when to apply the skill. If omitted, uses the first paragraph of markdown content. Put the key use case first: the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing to reduce context usage." [S-CC-2]

> "In a regular session, skill descriptions are loaded into context so Claude knows what's available, but full skill content only loads when invoked." [S-CC-2]

Implication: the trigger phrasing that a companion rule now carries can move into `description` + `when_to_use` — but with a hard **1,536-character cap** per skill and a listing-wide budget (see Finding 5). This is the "richer description" ceiling.

### Finding 2 — `when_to_use` frontmatter field is the dedicated home for trigger phrases / example requests

> "`when_to_use` | No | Additional context for when Claude should invoke the skill, such as trigger phrases or example requests. Appended to `description` in the skill listing and counts toward the 1,536-character cap." [S-CC-2]

This is the exact surface a companion rule's "TRIGGER when: …" text can migrate to — but it shares the 1,536-char cap with `description`.

### Finding 3 — `paths` frontmatter makes a skill auto-activate on file globs WITHOUT any always-loaded rule

> "`paths` | No | Glob patterns that limit when this skill is activated. Accepts a comma-separated string or a YAML list. When set, Claude loads the skill automatically only when working with files matching the patterns. Uses the same format as path-specific rules." [S-CC-2]

This is the single most load-bearing finding for the yf question. Many YOSHIKO_FLOW.md companion rules exist to fire "after any create or modify of a file matching glob X" (yf-markdown-lint, yf-drift-check, yf-change-validation on-edit). The skill `paths` field encodes that on-edit-glob trigger **inside the skill frontmatter**, so those rules can in principle collapse into the skill itself — no separate always-loaded rule and no settings.json key needed. `[uncertain]` whether `paths` fires on *every* create/modify or only when Claude reads a matching file; the rules doc's parallel `paths` mechanism is described as read-triggered (see Finding 9), and skills' `paths` "Uses the same format as path-specific rules," so it likely inherits the same read-trigger semantics rather than a filesystem-watch semantics.

### Finding 4 — Settings.json keys that govern skills (settings-level, not description-level)

> "`disableBundledSkills` | Set to `true` to disable the skills and workflows included with Claude Code … Skills from plugins, `.claude/skills/`, and `.claude/commands/` are unaffected." [S-CC-1]

> "The `skillOverrides` setting controls skill visibility from your settings instead of the skill's own frontmatter. Use it for skills whose SKILL.md you don't want to edit … Each key is a skill name and each value is one of four states" (`"on"`, `"name-only"`, `"user-invocable-only"`, `"off"`). [S-CC-2]

> "`disableSkillShellExecution` | Disable inline shell execution for `!`...`` and ````!` blocks in skills and custom commands from user, project, plugin, or additional-directory sources … Most useful in managed settings where users cannot override it" [S-CC-1]

So visibility/enablement is a settings concern; *when-to-fire* is a frontmatter (`description`/`when_to_use`/`paths`) concern. There is **no settings.json key that supplies a skill's trigger** — triggers live only in frontmatter.

### Finding 5 — The catch: descriptions are budget-capped and dropped under pressure; enforcement is NOT guaranteed by a description

> "Claude Code loads a listing of skill names and descriptions into context so Claude knows what's available. The listing always contains every skill name, but if you have many skills, Claude Code shortens descriptions to fit the listing's character budget, which can strip the keywords Claude needs to match your request. The budget scales at 1% of the model's context window. When the listing overflows, Claude Code drops descriptions starting with the skills you invoke least, so the skills you use most keep their full text." [S-CC-2]

> "To raise the budget, set the `skillListingBudgetFraction` setting (e.g. `0.02` = 2%) or the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable to a fixed character count." [S-CC-2]

> "If a skill seems to stop influencing behavior after the first response, the content is usually still present and the model is choosing other tools or approaches. Strengthen the skill's `description` and instructions so the model keeps preferring it, or use hooks to enforce behavior deterministically." [S-CC-2]

This is the irreducible-core boundary: a `description` is a **probabilistic** trigger, subject to truncation and to the model's discretion. Any yf rule whose value is a *guaranteed* fire (the "false-negative invariant", the silent-no-op invariants, "must run at this point") cannot be replaced by a description — it needs a hook or the model may simply not pick it up.

### Finding 6 — Deterministic triggers belong in hooks, not in instruction text

> "Both are loaded at the start of every conversation. Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead." [S-CC-3]

> "If the instruction is something that must run at a specific point, such as before every commit or after each file edit, write it as a hook instead. Hooks execute as shell commands at fixed lifecycle events and apply regardless of what Claude decides to do." [S-CC-3]

Relevant hook events for on-edit / instruction-load triggers [S-CC-4]:

> "`FileChanged` | When a watched file changes on disk. The `matcher` field specifies which filenames to watch" [S-CC-4]

> "`InstructionsLoaded` | When a CLAUDE.md or `.claude/rules/*.md` file is loaded into context. Fires at session start and when files are lazily loaded during a session" [S-CC-4]

> "`PreToolUse` | Before a tool call executes. Can block it" [S-CC-4]

So the replacement hierarchy for an always-loaded on-edit rule is: (1) skill `paths` frontmatter (model-invoked, probabilistic); (2) a `FileChanged` hook (deterministic, shell-executed). The yf-markdown-lint rule already names the `FileChanged` hook as its portable-vs-hook alternative — this confirms the mechanism exists and is the deterministic path.

### Finding 7 — When a CLAUDE.md section should become a skill (Anthropic's own guidance)

> "Create a skill when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact. Unlike CLAUDE.md content, a skill's body loads only when it's used, so long reference material costs almost nothing until you need it." [S-CC-2]

> "Keep it to facts Claude should hold in every session: build commands, conventions, project layout, \"always do X\" rules. If an entry is a multi-step procedure or only matters for one part of the codebase, move it to a skill or a path-scoped rule instead." [S-CC-3]

This is the doc-sanctioned decomposition: **facts / "always do X" → CLAUDE.md or always-loaded rule; procedures / path-specific → skill or path-scoped rule.** A yf companion rule that is a *procedure* is a candidate to fold into its skill; one that is a bare *always-do-X trigger a description can't fire* is the irreducible always-loaded remainder.

---

## RQ(b): Claude Code's global-instruction / rules mechanism and what should live there

### Finding 8 — The instruction surfaces and their load/precedence order

> "CLAUDE.md files can live in several locations, each with a different scope. The table below lists them in load order, from broadest scope to most specific" — Managed policy → User (`~/.claude/CLAUDE.md`) → Project (`./CLAUDE.md` or `./.claude/CLAUDE.md`) → Local (`./CLAUDE.local.md`). [S-CC-3]

> "CLAUDE.md and CLAUDE.local.md files in the directory hierarchy above the working directory are loaded in full at launch. Files in subdirectories load on demand when Claude reads files in those directories." [S-CC-3]

> "CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself. Claude reads it and tries to follow it, but there's no guarantee of strict compliance, especially for vague or conflicting instructions." [S-CC-3]

### Finding 9 — `.claude/rules/` and `~/.claude/rules/` — the modular rules mechanism; `paths` makes them conditional

> "Rules load into context every session or when matching files are opened. For task-specific instructions that don't need to be in context all the time, use skills instead, which only load when you invoke them or when Claude determines they're relevant to your prompt." [S-CC-3]

> "Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`." [S-CC-3]

> "Rules can be scoped to specific files using YAML frontmatter with the `paths` field. These conditional rules only apply when Claude is working with files matching the specified patterns." [S-CC-3]

> "Rules without a `paths` field are loaded unconditionally and apply to all files. Path-scoped rules trigger when Claude reads files matching the pattern, not on every tool use." [S-CC-3]

> "Personal rules in `~/.claude/rules/` apply to every project on your machine. Use them for preferences that aren't project-specific" … "User-level rules are loaded before project rules, giving project rules higher priority." [S-CC-3]

This confirms `~/.claude/rules/YOSHIKO_FLOW.md` (the yf aggregate) is an **unconditionally-loaded, every-project, every-session** surface — the most expensive tier. Two doc-sanctioned reductions: (a) add `paths` frontmatter to make a rule conditional (only loads when matching files are touched); (b) move procedural content to a skill so it loads only on invocation.

### Finding 10 — Global CLAUDE.md size guidance and the token-cost argument

> "CLAUDE.md files are loaded into the context window at the start of every session, consuming tokens alongside your conversation." … "Size: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence." [S-CC-3]

> "Splitting into `@path` imports helps organization but doesn't reduce context, since imported files load at launch." [S-CC-3]

Key portability/token point: `@`-imports do **not** save context (everything loads at launch). Only `paths`-scoping or moving to a skill actually reduces the always-loaded footprint. So a yf `@AGENTS.md`-style split is an *organization* win, not a *token* win.

### Finding 11 — AGENTS.md: Claude Code does NOT read it directly

> "Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it so both tools read the same instructions without duplicating them." [S-CC-3]

Cross-harness relevance: the portable `AGENTS.md` convention reaches Claude Code only via a `CLAUDE.md` that does `@AGENTS.md`. This project's own `CLAUDE.md` already uses exactly that pattern.

### Finding 12 — Managed `claudeMd` key: org-level instructions via settings.json (not a per-user surface)

> "`claudeMd` | (Managed settings only) CLAUDE.md-style instructions injected as organization-managed memory. Only honored when set in managed or policy settings and ignored in user, project, and local settings." [S-CC-1]

> "Settings rules are enforced by the client regardless of what Claude decides to do. CLAUDE.md instructions shape Claude's behavior but are not a hard enforcement layer." [S-CC-3]

Confirms the split: settings.json = enforced/technical; CLAUDE.md/rules = behavioral/probabilistic. `claudeMd`-in-settings is managed-scope only, so it is **not** a lever for an individual's global rules.

### Finding 13 — Settings scope/precedence (for "what should live in settings vs rules")

> "1. Managed (highest): can't be overridden by anything / 2. Command line arguments … / 3. Local … / 4. Project … / 5. User (lowest)". [S-CC-1]

> "`claudeMdExcludes` | Glob patterns or absolute paths of `CLAUDE.md` files to skip when loading memory … Only applies to user, project, and local memory; managed policy files cannot be excluded" [S-CC-1]

---

## Synthesis for the yf question

1. **On-edit/path-scoped trigger rules** (yf-markdown-lint, yf-drift-check, yf-change-validation on-edit firing "after create/modify of matching glob") have TWO doc-sanctioned replacements that remove them from the always-loaded surface: the skill's own `paths` frontmatter [S-CC-2, Finding 3] (probabilistic, model-invoked) and a `FileChanged` hook [S-CC-4, Finding 6] (deterministic). Neither requires an always-loaded companion rule.

2. **Trigger *phrasing*** (the "TRIGGER when: …" prose) can migrate into `description` + `when_to_use` [S-CC-2, Findings 1–2], but is capped at 1,536 chars/skill and subject to listing-budget truncation [S-CC-2, Finding 5]. Rich descriptions are a real but bounded replacement.

3. **The irreducible always-loaded core** is exactly the class the yf rules already claim: triggers a `description` "cannot reliably fire" [maps to S-CC-2 Finding 5 — descriptions are probabilistic and truncatable] and invariants that must fire *deterministically* [S-CC-3 Finding 6 — "no guarantee of strict compliance"; use a hook]. Where determinism is required, the honest replacement is a hook, not a description and not an always-loaded rule (a rule is also just probabilistic context).

4. **What legitimately stays in `~/.claude/rules/` (global always-loaded):** cross-project "always do X" facts that are not path-scopable and not procedural [S-CC-3 Findings 7, 9]. Everything procedural or path-specific is doc-recommended to move to a skill or a `paths`-scoped rule.

5. **Settings.json** owns enablement/enforcement (`disableBundledSkills`, `skillOverrides`, `disableSkillShellExecution`, `skillListingBudgetFraction`, managed `claudeMd`) — it never carries a skill's *trigger*. So "replace a rule with a settings key" only works for enforcement/visibility concerns, never for the when-to-fire concern [S-CC-1, S-CC-2].

## Gaps / uncertainties

- Exact firing semantics of skill `paths` (every filesystem change vs. only when Claude *reads* a matching file) is not stated on the skills page; inferred from the parallel rules `paths` mechanism as read-triggered `[uncertain]` (Finding 3).
- No doc quantifies the token cost of an always-loaded rule vs. a description-triggered skill beyond "1% of context window" listing budget [S-CC-2] and "under 200 lines" [S-CC-3]; a precise cost model is not published.
- Search returned only the four core pages plus noise (SDK reference, release notes, mistranslated/garbled URLs); the four captured are the authoritative primary sources for this cluster, meeting the ~4 expected.
