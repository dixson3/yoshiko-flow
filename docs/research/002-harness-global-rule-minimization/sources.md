---
title: Sources — 002-harness-global-rule-minimization
created: 2026-04-23
tags:
- research
- 002-harness-global-rule-minimization
- sources
type: Reference
okf_spec: OKF-RESEARCH
---

# Sources — 002-harness-global-rule-minimization

Citation format: `[ID](sources.md#id)` from Summary.md and artifacts.

## uncategorized

### S-CC-1
- **Title:** Claude Code settings - Claude Code Docs
- **URL:** https://docs.anthropic.com/en/docs/claude-code/settings
- **Credibility:** {'overall': 79, 'domain_authority': 62, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Configuration scopes, settings precedence (Managed > CLI args > Local > Project > User), settings files, and the full Available settings key reference including disableBundledSkills, skillOverrides, disableSkillShellExecution, claudeMd, claudeMdExcludes, autoMemoryEnabled.
- **Quote:** > When the same setting appears in multiple scopes, Claude Code applies them in priority order: 1. Managed (highest): can't be overridden by anything 2. Command line arguments: temporary session overrides 3. Local: overrides project and user settings 4. Project: overrides user settings 5. User (lowest): applies when nothing else specifies the setting

### S-CC-2
- **Title:** Extend Claude with skills - Claude Code Docs
- **URL:** https://docs.anthropic.com/en/docs/claude-code/skills
- **Credibility:** {'overall': 79, 'domain_authority': 62, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** SKILL.md frontmatter reference including description, when_to_use, paths, disable-model-invocation, user-invocable; how descriptions drive auto-activation; the 1,536-char cap and skillListingBudgetFraction; guidance that a CLAUDE.md procedure should become a skill; use hooks to enforce behavior deterministically.
- **Quote:** > paths | No | Glob patterns that limit when this skill is activated. Accepts a comma-separated string or a YAML list. When set, Claude loads the skill automatically only when working with files matching the patterns. Uses the same format as path-specific rules.

### S-CC-3
- **Title:** How Claude remembers your project - Claude Code Docs
- **URL:** https://docs.anthropic.com/en/docs/claude-code/memory
- **Credibility:** {'overall': 79, 'domain_authority': 62, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** CLAUDE.md vs auto memory; instruction surfaces and load/precedence order (Managed > User ~/.claude/CLAUDE.md > Project > Local); .claude/rules/ and ~/.claude/rules/ with paths frontmatter for conditional loading; CLAUDE.md is context not enforced configuration; AGENTS.md is read only via a CLAUDE.md import; move procedures to a skill or path-scoped rule.
- **Quote:** > Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`. ... Rules can be scoped to specific files using YAML frontmatter with the `paths` field. These conditional rules only apply when Claude is working with files matching the specified patterns.

### S-CC-4
- **Title:** Hooks reference - Claude Code Docs
- **URL:** https://docs.anthropic.com/en/docs/claude-code/hooks
- **Credibility:** {'overall': 79, 'domain_authority': 62, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Hook events reference including FileChanged (fires when a watched file changes on disk, matcher selects filenames), InstructionsLoaded (fires when CLAUDE.md or .claude/rules/*.md loads), and PreToolUse (before a tool call executes; can block it). These are the deterministic, shell-executed alternatives to probabilistic instruction text.
- **Quote:** > `FileChanged` | When a watched file changes on disk. The `matcher` field specifies which filenames to watch

### S-CX-1
- **Title:** Custom instructions with AGENTS.md (Codex) | ChatGPT Learn
- **URL:** https://learn.chatgpt.com/docs/agent-configuration/agents-md
- **Credibility:** {'overall': 68, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Codex reads AGENTS.md before doing any work; global ~/.codex first, then project root down to cwd, concatenated root-down with later files overriding. Chain built once per run; combined size capped at project_doc_max_bytes (32 KiB default).
- **Quote:** > Codex concatenates files from the root down, joining them with blank lines. Files closer to your current directory override earlier guidance because they appear later in the combined prompt.

### S-CX-2
- **Title:** Customization (Codex) | ChatGPT Learn
- **URL:** https://learn.chatgpt.com/docs/customization/overview
- **Credibility:** {'overall': 68, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Customization layers: AGENTS.md (persistent instructions), Memories, Skills (reusable workflows), MCP, Subagents. AGENTS.md always-loaded/persistent; skills use progressive disclosure (metadata for discovery, SKILL.md loaded only when chosen). Complementary, not competing.
- **Quote:** > It starts with metadata (name, description) for discovery ... It loads SKILL.md only when a skill is chosen.

### S-CX-3
- **Title:** The Codex CLI Instruction Stack: How Six Configuration Surfaces Shape Agent Behaviour
- **URL:** https://codex.danielvaughan.com/2026/05/07/codex-cli-instruction-stack-six-surfaces-agents-md-rules-hooks-skills/
- **Credibility:** {'overall': 59, 'domain_authority': 30, 'currency': 95, 'expertise': 75, 'bias_neutrality': 55, 'category': 'questionable', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Independent analysis: ~/.codex/config.toml developer_instructions injects into system prompt; AGENTS.md re-read per turn; rules always-evaluated vs skills/hooks on-demand; skills list ~2% context (~8KB), AGENTS.md capped at 32 KiB.
- **Quote:** > A skill's SKILL.md instructions enter the context only when the agent determines the current task matches the skill's description.

### S-CX-4
- **Title:** codex-rs/core/src/agents_md.rs at main - openai/codex
- **URL:** https://github.com/openai/codex/blob/main/codex-rs/core/src/agents_md.rs
- **Credibility:** {'overall': 71, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 92, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Rust core module implementing AGENTS.md discovery and user-instruction assembly; canonical primary source for the instruction-file mechanism (global + project discovery, concatenation).
- **Quote:** > AGENTS.md discovery and user instruction assembly. Project-level documentation is primarily stored in files name[d] ...

### S-LC-1
- **Title:** YOSHIKO_FLOW.md — installed aggregated always-loaded ruleset (8 companion protocols)
- **URL:** file:///Users/james/.claude/rules/YOSHIKO_FLOW.md
- **Credibility:** {'overall': 83, 'domain_authority': 85, 'currency': 95, 'expertise': 92, 'bias_neutrality': 55, 'category': 'high_trust', 'method': 'manual (local primary source; scorer domain-authority N/A for file:// URLs)'}
- **Snippet:** Single yf-managed file aggregating one fenced section per rule-bearing skill's companion protocol: BEADS_INIT, CHANGE-VALIDATION-TRIGGER, DRIFT-CHECK-TRIGGER, INSTRUCTIONS, MARKDOWN_LINT, PLANS, RESEARCH, UPSTREAM_TRACKING.
- **Quote:** > The engine **executes** a repo's recorded validation recipe (build / test / lint) and reports a verdict from an exit code — so a `description` alone cannot reliably fire it; this rule binds the on-edit and pre-push triggers.

### S-LC-2
- **Title:** yf SPEC.md §3.3.1 — Aggregated ruleset (REQ-YF-FLOW-001..006)
- **URL:** file:///Users/james/workspace/dixson3/yoshiko-flow/SPEC.md
- **Credibility:** {'overall': 83, 'domain_authority': 85, 'currency': 95, 'expertise': 92, 'bias_neutrality': 55, 'category': 'high_trust', 'method': 'manual (local primary source; scorer domain-authority N/A for file:// URLs)'}
- **Snippet:** Defines YOSHIKO_FLOW.md as the single operator-facing aggregate of every rule-bearing skill's companion protocol, one verbatim fenced section per protocol.
- **Quote:** > `yf` surfaces every rule-bearing skill's companion protocol as **one** operator-facing file in the rules dir, `YOSHIKO_FLOW.md`, instead of a scatter of standalone `*.md` files.

### S-LC-3
- **Title:** yf skills/protocols directory inventory
- **URL:** file:///Users/james/.claude/skills/
- **Credibility:** {'overall': 83, 'domain_authority': 85, 'currency': 95, 'expertise': 92, 'bias_neutrality': 55, 'category': 'high_trust', 'method': 'manual (local primary source; scorer domain-authority N/A for file:// URLs)'}
- **Snippet:** 18 yf skills; 8 carry a companion protocol .md (yf-beads-init, yf-beads-upstream, yf-change-validation, yf-drift-check, yf-markdown-lint, yf-optimal-instructions, yf-plan, yf-research) folded into the aggregate; the other 10 are description-only.
- **Quote:** > yf-beads-init: BEADS_INIT.md ... yf-beads-upstream: UPSTREAM_TRACKING.md ... yf-change-validation: CHANGE-VALIDATION-TRIGGER.md ... yf-drift-check: DRIFT-CHECK-TRIGGER.md ... yf-markdown-lint: MARKDOWN_LINT.md ... yf-optimal-instructions: INSTRUCTIONS.md ... yf-plan: PLANS.md ... yf-research: RESEARCH.md

### S-LC-4
- **Title:** yf-* SKILL.md frontmatter descriptions (TRIGGER/SKIP contracts)
- **URL:** file:///Users/james/workspace/dixson3/yoshiko-flow/skills/
- **Credibility:** {'overall': 83, 'domain_authority': 85, 'currency': 95, 'expertise': 92, 'bias_neutrality': 55, 'category': 'high_trust', 'method': 'manual (local primary source; scorer domain-authority N/A for file:// URLs)'}
- **Snippet:** Every yf SKILL.md description follows a rich TRIGGER when: / SKIP for: contract. yf-beads-upstream's description explicitly states the close-time push trigger lives in the always-loaded companion rule, not the description.
- **Quote:** > The close-time / land-the-plane push trigger is NOT carried in this description — it lives in the always-loaded companion rule (protocols/UPSTREAM_TRACKING.md).

### S-LC-5
- **Title:** Recommended Claude Code settings.json baseline
- **URL:** file:///Users/james/workspace/dixson3/yoshiko-flow/docs/recommended-settings.md
- **Credibility:** {'overall': 83, 'domain_authority': 85, 'currency': 95, 'expertise': 92, 'bias_neutrality': 55, 'category': 'high_trust', 'method': 'manual (local primary source; scorer domain-authority N/A for file:// URLs)'}
- **Snippet:** User-scope settings.json baseline that enforces yf contracts the prose only steers; bare-name permission.deny disables remove tool schemas from context; disableWorkflows + todoFeatureEnabled:false are the highest-impact alignment keys.
- **Quote:** > prose only steers the model; it does not remove the disallowed mechanism. Setting these keys aligns the runtime with the contracts so the model cannot reach for a mechanism a skill forbids.

### S-LC-6
- **Title:** naba AGENTS.md — single source of truth; delegates generic bd rules to user scope
- **URL:** file:///Users/james/workspace/dixson3/naba/AGENTS.md
- **Credibility:** {'overall': 83, 'domain_authority': 85, 'currency': 95, 'expertise': 92, 'bias_neutrality': 55, 'category': 'high_trust', 'method': 'manual (local primary source; scorer domain-authority N/A for file:// URLs)'}
- **Snippet:** naba's AGENTS.md is the single source of truth; it explicitly delegates generic bd workflow conventions to user-scope agent rules rather than duplicating them in-repo.
- **Quote:** > Issue tracking uses **beads (`bd`)**; the generic bd workflow conventions live in your user-scope agent rules and are not duplicated here. naba-specific facts:

### S-LC-7
- **Title:** naba CLAUDE.md — thin pointer to AGENTS.md (optimal-instructions K2 pattern)
- **URL:** file:///Users/james/workspace/dixson3/naba/CLAUDE.md
- **Credibility:** {'overall': 83, 'domain_authority': 85, 'currency': 95, 'expertise': 92, 'bias_neutrality': 55, 'category': 'high_trust', 'method': 'manual (local primary source; scorer domain-authority N/A for file:// URLs)'}
- **Snippet:** CLAUDE.md is intentionally a thin pointer; AGENTS.md primary, CLAUDE.md a thin @-include — the exact structure yf-optimal-instructions proposes.
- **Quote:** > CLAUDE.md is intentionally a thin pointer. AGENTS.md is the single source of truth for both project and agent guidance (optimal-instructions: AGENTS.md primary, CLAUDE.md a thin @-include).

### S-LC-8
- **Title:** naba repo directory layout — no per-harness rule scatter
- **URL:** file:///Users/james/workspace/dixson3/naba/
- **Credibility:** {'overall': 83, 'domain_authority': 85, 'currency': 95, 'expertise': 92, 'bias_neutrality': 55, 'category': 'high_trust', 'method': 'manual (local primary source; scorer domain-authority N/A for file:// URLs)'}
- **Snippet:** naba has .claude/ (worktrees only), a root .markdown-lint-on-edit opt-in marker, a root DRIFT-CHECK.md manifest, one embedded skill under skills/naba; no .agents/, no AGENTS/ rules dir, no codex/opencode/pi config.
- **Quote:** > .markdown-lint-on-edit ... DRIFT-CHECK.md ... skills/naba ... .claude/worktrees (no rules/ dir)

### S-OC-1
- **Title:** Rules | opencode
- **URL:** https://opencode.ai/docs/rules/
- **Credibility:** {'overall': 68, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** opencode's AGENTS.md rules mechanism: project root vs global ~/.config/opencode/AGENTS.md, /init, Claude Code compatibility fallbacks (CLAUDE.md, ~/.claude/skills), per-category precedence, and the instructions config key for reusing external rule files.
- **Quote:** > You can provide custom instructions to opencode by creating an `AGENTS.md` file. This is similar to Cursor's rules. It contains instructions that will be included in the LLM's context to customize its behavior for your specific project.

### S-OC-2
- **Title:** Config | opencode
- **URL:** https://opencode.ai/docs/config/
- **Credibility:** {'overall': 68, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** opencode.json config: global location ~/.config/opencode/opencode.json, 8-tier precedence order (remote -> global -> custom -> project -> .opencode dirs -> inline -> managed -> MDM), configs merged not replaced, and .opencode subdirs agents/commands/modes/plugins/skills/tools/themes.
- **Quote:** > Config sources are loaded in this order (later sources override earlier ones): 1. Remote config (from `.well-known/opencode`) - organizational defaults 2. Global config (`~/.config/opencode/opencode.json`) - user preferences 3. Custom config (`OPENCODE_CONFIG` env var) - custom overrides 4. Project config (`opencode.json` in project) - project-specific settings 5. `.opencode` directories - agents, commands, plugins 6. Inline config (`OPENCODE_CONFIG_CONTENT` env var) - runtime overrides 7. Managed config files ... 8. macOS managed preferences (`.mobileconfig` via MDM) - highest priority, not user-overridable

### S-OC-3
- **Title:** Instructions | opencode (v2 docs)
- **URL:** https://v2.opencode.ai/instructions
- **Credibility:** {'overall': 68, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** v2 docs stating global + project AGENTS.md files are combined, not a single winner: rendered global first, then project files from Location toward project root; opencode does not resolve conflicts.
- **Quote:** > The files are combined rather than selecting a single winner. They are rendered in this order: global, then project files from the Location toward the project root. OpenCode does not resolve conflicts between their contents, so keep broad guidance global and put scoped guidance in the relevant project directory.

### S-OC-4
- **Title:** docs: clarify that project and global AGENTS.md files are combined, not overridden (Issue #9282)
- **URL:** https://github.com/anomalyco/opencode/issues/9282
- **Credibility:** {'overall': 59, 'domain_authority': 30, 'currency': 95, 'expertise': 75, 'bias_neutrality': 55, 'category': 'questionable', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Issue reporting the Rules docs 'Precedence' section is ambiguous and can mislead users into thinking project AGENTS.md overrides global, when they are actually combined.
- **Quote:** > The [Rules documentation](https://opencode.ai/docs/rules/) has an ambiguous "Precedence" section that can mislead users.

### S-OC-5
- **Title:** Bug: Global AGENTS.md not loaded when project AGENTS.md exists (Issue #22020)
- **URL:** https://github.com/anomalyco/opencode/issues/22020
- **Credibility:** {'overall': 59, 'domain_authority': 30, 'currency': 95, 'expertise': 75, 'bias_neutrality': 55, 'category': 'questionable', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Bug report claiming global ~/.config/opencode/AGENTS.md is ignored when a project AGENTS.md exists, followed by an in-thread self-correction (verified via opencode-system-prompt-logger plugin) showing BOTH files are in fact loaded.
- **Quote:** > Correction: Issue is NOT valid — both AGENTS.md files ARE loaded. I installed the `opencode-system-prompt-logger` plugin and ran it from my project directory ... The output clearly shows [both loaded]

### S-OC-6
- **Title:** packages/opencode/src/config/config.ts (dev)
- **URL:** https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/config/config.ts
- **Credibility:** {'overall': 71, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 92, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Source: globalConfigFile() checks candidates opencode.jsonc, opencode.json, config.json under the global config path; loadConfig routes through remote .well-known/opencode.
- **Quote:** > function globalConfigFile() { const candidates = ["opencode.jsonc", "opencode.json", "config.json"].map((file) => path.join(Global.Path.config, file), ) for (const file of candidates) { if (existsSync(file)) return file } return candidates[0] }

### S-OC-7
- **Title:** Agent Skills | opencode
- **URL:** https://opencode.ai/docs/skills/
- **Credibility:** {'overall': 68, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Agent skills are loaded on-demand via the native `skill` tool (description-triggered, 1-1024 char description surfaced in tool description); search paths include .opencode/skills, ~/.config/opencode/skills, .claude/skills, ~/.claude/skills, .agents/skills, ~/.agents/skills; per-skill allow/deny/ask permissions.
- **Quote:** > Agent skills let OpenCode discover reusable instructions from your repo or home directory. Skills are loaded on-demand via the native `skill` tool—agents see available skills and can load the full content when needed.

### S-OC-8
- **Title:** Commands | opencode
- **URL:** https://opencode.ai/docs/commands/
- **Credibility:** {'overall': 68, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Custom commands are /name-invoked prompt templates defined as markdown in commands/ (global ~/.config/opencode/commands/ or project .opencode/commands/) or via the config `command` key; on-demand, not always-loaded context.
- **Quote:** > Custom commands let you specify a prompt you want to run when that command is executed in the TUI. ... Create markdown files in the `commands/` directory to define custom commands.

### S-PI-1
- **Title:** Pi Coding Agent
- **URL:** https://pi.dev/
- **Credibility:** {'overall': 72, 'domain_authority': 77, 'currency': 95, 'expertise': 75, 'bias_neutrality': 35, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Pi is a minimal terminal coding harness customizable with extensions, skills, prompt templates, and themes; skips sub-agents and plan mode by default.
- **Quote:** > Pi is a minimal agent harness. Adapt Pi to your workflows, not the other way around. Customize Pi with extensions, skills, prompt templates, and themes. Bundle them as Pi packages and share via npm or git.

### S-PI-2
- **Title:** earendil-works/pi: AI agent toolkit: unified LLM API, agent loop, TUI, coding agent CLI
- **URL:** https://github.com/earendil-works/pi
- **Credibility:** {'overall': 71, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 92, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Monorepo home of the Pi agent harness and its self-extensible coding agent CLI. ~75k stars, MIT, actively released (v0.81.1, 2026-07-21).
- **Quote:** > AI agent toolkit: unified LLM API, agent loop, TUI, coding agent CLI ... Stars: 75444 ... License: MIT License (MIT) ... Latest release: v0.81.1 (2026-07-21T16:45:17Z)

### S-PI-3
- **Title:** Skills - Documentation - Pi
- **URL:** https://pi.dev/docs/latest/skills
- **Credibility:** {'overall': 80, 'domain_authority': 77, 'currency': 95, 'expertise': 75, 'bias_neutrality': 75, 'category': 'high_trust', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Pi implements the Agent Skills standard and loads skills on-demand from global (~/.pi/agent/skills, ~/.agents/skills), project (.pi/skills, .agents/skills), packages, settings, and CLI.
- **Quote:** > Pi implements the Agent Skills standard, warning about most violations but remaining lenient. ... Pi loads skills from: - Global: `~/.pi/agent/skills/`, `~/.agents/skills/` - Project (only after the project is trusted): `.pi/skills/`, `.agents/skills/` in `cwd` and ancestor directories

### S-PI-4
- **Title:** pi-coding-agent-config / references / context-files.md
- **URL:** https://github.com/yukukotani/pi-voice/blob/main/.agents/skills/pi-coding-agent-config/references/context-files.md
- **Credibility:** {'overall': 58, 'domain_authority': 30, 'currency': 95, 'expertise': 55, 'bias_neutrality': 75, 'category': 'questionable', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Reference doc: Pi loads AGENTS.md (or CLAUDE.md) at startup from ~/.pi/agent/AGENTS.md (global), parent dirs, and cwd, all concatenated; system prompt via .pi/SYSTEM.md or ~/.pi/agent/SYSTEM.md, appendable via APPEND_SYSTEM.md.
- **Quote:** > Pi loads `AGENTS.md` (or `CLAUDE.md`) at startup from: - `~/.pi/agent/AGENTS.md` (global) - Parent directories (walking up from cwd) - Current directory ... All matching files are concatenated. ... Replace the default system prompt with `.pi/SYSTEM.md` (project) or `~/.pi/agent/SYSTEM.md` (global). Append without replacing via `APPEND_SYSTEM.md`.

### S-PI-5
- **Title:** @earendil-works/pi-coding-agent (npm)
- **URL:** https://registry.npmjs.org/@earendil-works/pi-coding-agent
- **Credibility:** {'overall': 71, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 92, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Coding agent CLI with read, bash, edit, write tools and session management; 1.2M weekly downloads; author Mario Zechner.
- **Quote:** > Coding agent CLI with read, bash, edit, write tools and session management ... Weekly Downloads: 1.2M ... License: MIT ... Author: Mario Zechner

### S-PI-6
- **Title:** OrestesK/pi - Pi agent config
- **URL:** https://github.com/OrestesK/pi
- **Credibility:** {'overall': 54, 'domain_authority': 30, 'currency': 95, 'expertise': 55, 'bias_neutrality': 55, 'category': 'questionable', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Real-world personal Pi config: always-loaded policy in AGENTS.md, runtime behavior in settings.json/mcp.json/permissions.json, host facts in APPEND_SYSTEM.md, subagent roles in agents/.
- **Quote:** > Always-loaded policy starts in `AGENTS.md`; subagent role behavior is also defined in `agents/`. Runtime behavior comes from `settings.json`, `mcp.json`, enabled packages, and auto-discovered local `extensions/`. Host-specific facts are in `APPEND_SYSTEM.md` where possible.

### S-PI-7
- **Title:** AGENTS.md
- **URL:** https://agents.md/
- **Credibility:** {'overall': 63, 'domain_authority': 30, 'currency': 95, 'expertise': 75, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Official site for the AGENTS.md open format: a predictable place for agent-focused instructions, deliberately non-proprietary so one file works across many agents.
- **Quote:** > Rather than introducing another proprietary file, we chose a name and format that could work for anyone. ... One AGENTS.md works across many agents

### S-PI-8
- **Title:** agentsmd/agents.md - a simple, open format for guiding coding agents
- **URL:** https://github.com/agentsmd/agents.md
- **Credibility:** {'overall': 71, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 92, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Source repo for the AGENTS.md standard; ~23k stars, MIT, created 2025-08-19; 20 contributors including OpenAI staff.
- **Quote:** > AGENTS.md - a simple, open format for guiding coding agents - Stars: 23157 ... License: MIT License (MIT) ... Created: 2025-08-19T17:22:54Z

### S-PI-9
- **Title:** AGENTS.md: Project-Level README for AI Coding Agents - AgentPatterns.ai
- **URL:** https://agentpatterns.ai/standards/agents-md/
- **Credibility:** {'overall': 58, 'domain_authority': 30, 'currency': 95, 'expertise': 55, 'bias_neutrality': 75, 'category': 'questionable', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Describes AGENTS.md as an open standard project-level instruction file; discovery convention is any supporting tool loads the file at repo root.
- **Quote:** > AGENTS.md is an open standard for a project-level instruction file that gives AI coding agents the context they need to work effectively in a codebase. ... any AI coding tool that supports AGENTS.md looks for the file at the repository root. The tool then loads the file

### S-PI-10
- **Title:** AGENTS.md Emerges as Open Standard for AI Coding Agents - InfoQ
- **URL:** https://www.infoq.com/news/2025/08/agents-md/
- **Credibility:** {'overall': 69, 'domain_authority': 62, 'currency': 95, 'expertise': 55, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** News coverage: AGENTS.md adopted by 20,000+ GitHub repos, positioned as machine-readable companion to human docs.
- **Quote:** > Already adopted by more than 20,000 repositories on GitHub, the format is being positioned as a companion to traditional documentation, offering machine-readable context

### S-PI-11
- **Title:** Custom instructions with AGENTS.md - Codex | OpenAI Developers
- **URL:** https://developers.openai.com/codex/guides/agents-md
- **Credibility:** {'overall': 68, 'domain_authority': 30, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Codex reads AGENTS.md before work; discovery precedence: global scope (~/.codex, AGENTS.override.md then AGENTS.md) then project scope walking root to cwd.
- **Quote:** > Codex reads `AGENTS.md` files before doing any work. ... Discovery follows this precedence order: 1. Global scope: In your Codex home directory (defaults to `~/.codex`...), Codex reads `AGENTS.override.md` if it exists. Otherwise, Codex reads `AGENTS.md`... 2. Project scope: Starting at the project root... Codex walks down to your current working directory.

### S-PI-12
- **Title:** Copilot coding agent now supports AGENTS.md custom instructions
- **URL:** https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/
- **Credibility:** {'overall': 84, 'domain_authority': 77, 'currency': 95, 'expertise': 92, 'bias_neutrality': 75, 'category': 'high_trust', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** GitHub Copilot coding agent supports root and nested AGENTS.md, alongside copilot-instructions.md, CLAUDE.md, and GEMINI.md.
- **Quote:** > You can create a single `AGENTS.md` file in the root of your repository. You can also create nested `AGENTS.md` files which apply to specific parts of your project. Alongside `AGENTS.md`, the agent continues to support GitHub's `.github/copilot-instructions.md` and `.github/instructions/**.instructions.md` formats, plus `CLAUDE.md` and `GEMINI.md` files.

### S-PI-13
- **Title:** AGENTS.md - An Open Format for Guiding AI Coding Agents with Project Instructions
- **URL:** https://blog.brightcoding.dev/2025/09/21/agents-md-an-open-format-for-guiding-ai-coding-agents-with-project-instructions
- **Credibility:** {'overall': 76, 'domain_authority': 77, 'currency': 95, 'expertise': 75, 'bias_neutrality': 55, 'category': 'verify', 'method': 'script (credibility_scorer.py; note: keyword-based domain_authority underrates first-party docs)'}
- **Snippet:** Explainer contrasting per-tool proprietary instruction files (CLAUDE.md, .cursor/rules, copilot-instructions.md, GEMINI.md) with a single AGENTS.md.
- **Quote:** > Until now every tool invented its own private instruction file: Claude `CLAUDE.md`, Cursor `.cursor/rules`, Copilot `.github/copilot-instructions.md`, Gemini `GEMINI.md`. Maintaining five hand-written cheat-sheets is silly. AGENTS.md replaces
