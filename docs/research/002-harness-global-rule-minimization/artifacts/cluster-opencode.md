---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: opencode

Target: opencode (opencode.ai / the opencode agent, repo `anomalyco/opencode`, formerly
`sst/opencode`) instruction/rules mechanism — `AGENTS.md` support, project vs global config,
precedence, always-loaded vs on-demand loading, and custom commands/agents/skills/plugins as
alternatives to always-loaded rules.

Method: exa (`web_search_advanced_exa` + `crawling_exa`), domains scoped to `opencode.ai` and
`github.com`. Retrieved 2026-07-22.

---

## Finding 1 — `AGENTS.md` is opencode's primary always-loaded instruction file

opencode's rules mechanism is the `AGENTS.md` file, injected into LLM context to customize
behavior — directly analogous to Claude Code's `CLAUDE.md`/`AGENTS.md`.

> "You can provide custom instructions to opencode by creating an `AGENTS.md` file. This is
> similar to Cursor's rules. It contains instructions that will be included in the LLM's context
> to customize its behavior for your specific project." [S-OC-1]

Created/maintained via `/init`:

> "To create a new `AGENTS.md` file, you can run the `/init` command in opencode." [S-OC-1]

---

## Finding 2 — Project vs global rules: two locations, distinct purposes

**Project** (committed, team-shared):

> "Place an `AGENTS.md` in your project root for project-specific rules. These only apply when
> you are working in this directory or its sub-directories." [S-OC-1]

**Global** (personal, not committed) — this is the direct analog to `~/.claude/CLAUDE.md`:

> "You can also have global rules in a `~/.config/opencode/AGENTS.md` file. This gets applied
> across all opencode sessions." [S-OC-1]

> "Since this isn't committed to Git or shared with your team, we recommend using this to specify
> any personal rules that the LLM should follow." [S-OC-1]

---

## Finding 3 — Claude Code compatibility: opencode reads `CLAUDE.md` and `~/.claude/skills` as fallbacks

Relevant to cross-harness portability — opencode natively falls back to Claude Code's files:

> "For users migrating from Claude Code, OpenCode supports Claude Code's file conventions as
> fallbacks:
> - Project rules: `CLAUDE.md` in your project directory (used if no `AGENTS.md` exists)
> - Global rules: `~/.claude/CLAUDE.md` (used if no `~/.config/opencode/AGENTS.md` exists)
> - Skills: `~/.claude/skills/` — see Agent Skills for details" [S-OC-1]

Disable-able via env vars:

> "export OPENCODE_DISABLE_CLAUDE_CODE=1 # Disable all .claude support
> export OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1 # Disable only ~/.claude/CLAUDE.md
> export OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1 # Disable only .claude/skills" [S-OC-1]

---

## Finding 4 — Rule-file precedence: first match wins *per category*; files are combined across categories

The official docs state a per-category resolution order:

> "When opencode starts, it looks for rule files in this order:
> 1. Local files by traversing up from the current directory (`AGENTS.md`, `CLAUDE.md`)
> 2. Global file at `~/.config/opencode/AGENTS.md`
> 3. Claude Code file at `~/.claude/CLAUDE.md` (unless disabled)
> The first matching file wins in each category. For example, if you have both `AGENTS.md` and
> `CLAUDE.md`, only `AGENTS.md` is used." [S-OC-1]

Crucially, the categories are **combined, not overridden** — global + project both load. This is
confirmed most explicitly by the v2 docs, which describe conflicting-content behavior:

> "1. The global file at `$XDG_CONFIG_HOME/opencode/AGENTS.md`, normally
> `~/.config/opencode/AGENTS.md`. 2. Every `AGENTS.md` from the current Location up to and
> including the project root." [S-OC-3]

> "The files are combined rather than selecting a single winner. They are rendered in this order:
> global, then project files from the Location toward the project root. OpenCode does not resolve
> conflicts between their contents, so keep broad guidance global and put scoped guidance in the
> relevant project directory." [S-OC-3]

This combine-not-override semantic is the subject of a docs-clarification issue, confirming the
official docs' "Precedence" wording is ambiguous but the intended behavior is additive:

> "docs: clarify that project and global AGENTS.md files are combined, not overridden" [S-OC-4]

> "The [Rules documentation] has an ambiguous 'Precedence' section that can mislead users."
> [S-OC-4]

`[uncertain]` There is a bug report (#22020) claiming global `AGENTS.md` is *not* loaded when a
project `AGENTS.md` exists — but that same thread contains a self-correction showing both files
DO load when tested with a system-prompt-logger plugin:

> "When both a global `~/.config/opencode/AGENTS.md` and a project-level `AGENTS.md` exist, only
> the project-level file is loaded. The global rules are silently ignored." [S-OC-5]

> "Correction: Issue is NOT valid — both AGENTS.md files ARE loaded. I installed the
> `opencode-system-prompt-logger` plugin and ran it from my project directory ... The output
> clearly shows [both loaded]" [S-OC-5]

Net: intended and observed behavior is that global + project AGENTS.md are **combined**; the
apparent contradiction is a resolved/invalid bug report.

---

## Finding 5 — Global config file location and JSON config precedence

Rules (`AGENTS.md`) are separate from JSON config (`opencode.json`). The global JSON config lives
at `~/.config/opencode/opencode.json`:

> "Place your global OpenCode config in `~/.config/opencode/opencode.json`. Use global config for
> user-wide server/runtime preferences like providers, models, and permissions." [S-OC-2]

Config source (candidates checked) confirms filenames:

> "function globalConfigFile() { const candidates = ['opencode.jsonc', 'opencode.json',
> 'config.json'].map((file) => path.join(Global.Path.config, file)) ... }" [S-OC-6]

Full config precedence (later overrides earlier), and note configs are **merged not replaced**:

> "Config sources are loaded in this order (later sources override earlier ones):
> 1. Remote config (from `.well-known/opencode`) - organizational defaults
> 2. Global config (`~/.config/opencode/opencode.json`) - user preferences
> 3. Custom config (`OPENCODE_CONFIG` env var) - custom overrides
> 4. Project config (`opencode.json` in project) - project-specific settings
> 5. `.opencode` directories - agents, commands, plugins
> 6. Inline config (`OPENCODE_CONFIG_CONTENT` env var) - runtime overrides
> 7. Managed config files (`/Library/Application Support/opencode/` on macOS) - admin-controlled
> 8. macOS managed preferences (`.mobileconfig` via MDM) - highest priority, not
> user-overridable" [S-OC-2]

> "Configuration files are merged together, not replaced. ... Later configs override earlier ones
> only for conflicting keys. Non-conflicting settings from all configs are preserved." [S-OC-2]

---

## Finding 6 — `instructions` config key: point at existing rule files instead of duplicating into AGENTS.md

This is the closest opencode analog to "recommended settings.json" driving rule loading — a config
key that pulls arbitrary files (globs, remote URLs) into the always-loaded instruction context:

> "You can specify custom instruction files in your `opencode.json` or the global
> `~/.config/opencode/opencode.json`. This allows you and your team to reuse existing rules rather
> than having to duplicate them to AGENTS.md." [S-OC-1]

> `{ "instructions": ["CONTRIBUTING.md", "docs/guidelines.md", ".cursor/rules/*.md"] }` [S-OC-1]

> "You can also use remote URLs to load instructions from the web. ... Remote instructions are
> fetched with a 5 second timeout. All instruction files are combined with your `AGENTS.md`
> files." [S-OC-1]

`[note]` opencode does **not** auto-parse `@file` references inside AGENTS.md; the `instructions`
key (or explicit lazy-load instructions in AGENTS.md prose) is the supported mechanism:

> "While opencode doesn't automatically parse file references in `AGENTS.md`, you can achieve
> similar functionality in two ways: ... The recommended approach is to use the `instructions`
> field in `opencode.json`". [S-OC-1]

---

## Finding 7 — Always-loaded vs on-demand: Skills are the on-demand analog (native `skill` tool)

This is the central question for rule-minimization. opencode splits, exactly like Claude Code,
between **always-loaded** instructions (`AGENTS.md` + `instructions` files) and **on-demand**
skills loaded by description via a native tool:

> "Agent skills let OpenCode discover reusable instructions from your repo or home directory.
> Skills are loaded on-demand via the native `skill` tool—agents see available skills and can load
> the full content when needed." [S-OC-7]

The trigger surface is the skill's `description` (1–1024 chars), surfaced in the tool description —
identical model to Claude Code's description-triggered skills:

> "`description` must be 1-1024 characters. Keep it specific enough for the agent to choose
> correctly." [S-OC-7]

> "OpenCode lists available skills in the `skill` tool description. Each entry includes the skill
> name and description ... `<available_skills><skill><name>git-release</name>
> <description>Create consistent releases and changelogs</description></skill>...` The agent loads
> a skill by calling the tool: `skill({ name: 'git-release' })`" [S-OC-7]

Skill search paths include the yf-relevant `.agents/skills/` and `~/.agents/skills/` plus
`.claude/skills/`:

> "OpenCode searches these locations: Project config: `.opencode/skills/*/SKILL.md`; Global
> config: `~/.config/opencode/skills/*/SKILL.md`; Project Claude-compatible:
> `.claude/skills/*/SKILL.md`; Global Claude-compatible: `~/.claude/skills/*/SKILL.md`; Project
> agent-compatible: `.agents/skills/*/SKILL.md`; Global agent-compatible:
> `~/.agents/skills/*/SKILL.md`" [S-OC-7]

Skill loading is gated by pattern-based permissions in `opencode.json` (`allow`/`deny`/`ask`) —
relevant to whether a description-triggered skill fires automatically:

> "| `allow` | Skill loads immediately | | `deny` | Skill hidden from agent, access rejected | |
> `ask` | User prompted for approval before loading |" [S-OC-7]

---

## Finding 8 — Custom commands & agents: user/agent-invoked, NOT always-loaded

Custom commands are `/name`-invoked prompt templates — an on-demand alternative, not always-loaded
context:

> "Custom commands let you specify a prompt you want to run when that command is executed in the
> TUI. ... Create markdown files in the `commands/` directory to define custom commands." [S-OC-8]

> Global: `~/.config/opencode/commands/`; Per-project: `.opencode/commands/`. "The markdown file
> name becomes the command name." [S-OC-8]

The `.opencode` (and `~/.config/opencode`) directory hosts the full on-demand extension family:

> "The `.opencode` and `~/.config/opencode` directories use plural names for subdirectories:
> `agents/`, `commands/`, `modes/`, `plugins/`, `skills/`, `tools/`, and `themes/`." [S-OC-2]

Implication for yf: the opencode split maps cleanly onto the research question — always-loaded
surface = `AGENTS.md` (global `~/.config/opencode/AGENTS.md` + project) plus the `instructions`
config globs; on-demand surface = `skills/` (description-triggered via native `skill` tool),
`commands/` (slash-invoked), and `agents/`. A rule that only needs to fire on an explicit
invocation or by description can live as a skill/command instead of always-loaded `AGENTS.md`.

---

## Queries tried / coverage notes

- exa advanced, domains `[opencode.ai, github.com]`: "opencode AGENTS.md rules instructions
  project global configuration precedence" — hit rules + config docs, v2 instructions, GH
  issues/PRs/source. Good coverage.
- exa advanced: "opencode global config location rules file loading always-loaded custom commands
  agents plugins" — surfaced config precedence + config.ts source.
- crawling_exa full-page: `docs/rules/`, `docs/config/`, `docs/skills/`, `docs/commands/` —
  authoritative verbatim text for all findings above.
- No empty angles: every sub-question (AGENTS.md support, project vs global, precedence, global
  config location, always-loaded vs on-demand, commands/agents/plugins as alternatives) returned
  authoritative sources. The only `[uncertain]` item is the #22020 load-order bug, which resolves
  to "both files load (combined)".
