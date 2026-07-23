---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: pi-and-cross-harness

Method: `exa` (mcp__exa__web_search_advanced_exa). Retrieved 2026-07-22.

Two targets: (1) the **pi** coding agent at pi.dev and its global-instruction/rules
mechanism; (2) the cross-harness **AGENTS.md** open standard and portability tradeoffs.

---

## Target 1 — pi (https://pi.dev)

### Identity resolution: CONFIRMED as a coding agent

pi.dev **is** the coding agent the operator means. It is the "Pi Coding Agent," a
minimal terminal coding harness published by earendil-works (author Mario Zechner /
"badlogic"), distributed as the npm package `@earendil-works/pi-coding-agent`.

> "Pi is a minimal agent harness. Adapt Pi to your workflows, not the other way around.
> Customize Pi with extensions, skills, prompt templates, and themes. Bundle them as Pi
> packages and share via npm or git." [S-PI-1]

> "Pi ships with powerful defaults but skips features like sub-agents and plan mode." [S-PI-1]

Repository and provenance (the harness is real, actively released, widely used):

> "AI agent toolkit: unified LLM API, agent loop, TUI, coding agent CLI ... Stars: 75444
> ... License: MIT License (MIT) ... Latest release: v0.81.1 (2026-07-21...)" [S-PI-2]

> "Coding agent CLI with read, bash, edit, write tools and session management ... Weekly
> Downloads: 1.2M ... Author: Mario Zechner" [S-PI-5]

Note on the "several things" caveat in the task: the search surfaced only the Pi Coding
Agent for `pi.dev` — no competing product resolved at that domain. Absence-of-ambiguity is
itself the finding: pi.dev unambiguously fronts the earendil-works Pi coding-agent harness.

### Global-instruction / rules / config mechanism

**Context files (the AGENTS.md-equivalent always-loaded surface).** Pi natively loads
`AGENTS.md` (or `CLAUDE.md`) at startup, from a global path plus a walk up from cwd — all
matching files are concatenated:

> "Pi loads `AGENTS.md` (or `CLAUDE.md`) at startup from:
> - `~/.pi/agent/AGENTS.md` (global)
> - Parent directories (walking up from cwd)
> - Current directory
> Use for project instructions, conventions, common commands. All matching files are
> concatenated." [S-PI-4]

**System prompt override / append** (distinct from context files):

> "Replace the default system prompt with `.pi/SYSTEM.md` (project) or
> `~/.pi/agent/SYSTEM.md` (global). Append without replacing via `APPEND_SYSTEM.md`." [S-PI-4]

**Runtime config** lives in JSON files, not in the always-loaded prose surface. A
real-world personal Pi config separates always-loaded policy (AGENTS.md) from runtime
behavior (settings.json etc.) — directly relevant to the research question of what should
live in the always-loaded surface vs. config:

> "Personal Pi coding-agent configuration. Always-loaded policy starts in `AGENTS.md`;
> subagent role behavior is also defined in `agents/`. Runtime behavior comes from
> `settings.json`, `mcp.json`, enabled packages, and auto-discovered local `extensions/`.
> Host-specific facts are in `APPEND_SYSTEM.md` where possible." [S-PI-6]

> "AGENTS.md   # Always-loaded agent policy
> APPEND_SYSTEM.md   # Host/toolchain overlay
> settings.json   # Model, packages, UI, memory, compaction ...
> permissions.json   # Permission mode" [S-PI-6]

**Skills (the on-demand, description-triggered surface, standards-aligned).** Pi implements
the Agent Skills standard and loads skills from both `~/.pi/`-native and the cross-harness
`~/.agents/` / `.agents/` locations:

> "Pi implements the Agent Skills standard, warning about most violations but remaining
> lenient. ... Pi loads skills from:
> - Global: `~/.pi/agent/skills/`, `~/.agents/skills/`
> - Project (only after the project is trusted): `.pi/skills/`, `.agents/skills/` in `cwd`
> and ancestor directories ...
> - Settings: `skills` array with files or directories
> - CLI: `--skill` (repeatable...)" [S-PI-3]

Relevance to this research: Pi supports the **exact same two-tier split** the yf rule-set
is trying to optimize — an always-loaded prose surface (`AGENTS.md` / `SYSTEM.md`) vs.
on-demand skills (Agent Skills standard, discovered from shared `.agents/skills/`). Pi's
skill loading is `~/.agents/`-aware, so a yf skill tree is directly portable to Pi. `[uncertain]`
Whether Pi fires a skill purely off its description (no explicit invocation) is not stated
verbatim in these sources — the docs say skills are "loaded on-demand" but do not spell out
the trigger model as claude-code's description-matching does.

---

## Target 2 — cross-harness AGENTS.md convention

### What it is (open standard, one file across many agents)

> "AGENTS.md complements this by containing the extra, sometimes detailed context coding
> agents need: build steps, tests, and conventions that might clutter a README... Rather
> than introducing another proprietary file, we chose a name and format that could work for
> anyone." [S-PI-7]

> "AGENTS.md is an open standard for a project-level instruction file that gives AI coding
> agents the context they need to work effectively in a codebase." [S-PI-9]

Scale of adoption (why it is the portability lingua franca):

> "AGENTS.md — a simple, open format for guiding coding agents - Stars: 23157 ... License:
> MIT License ... Created: 2025-08-19" [S-PI-8]

> "Already adopted by more than 20,000 repositories on GitHub, the format is being
> positioned as a companion to traditional documentation, offering machine-readable
> context" [S-PI-10]

### Discovery convention and precedence (how portability actually works)

The convention is a single, predictable root file that any supporting tool loads; layering
provides global + project overrides. Codex documents an explicit precedence chain (a
concrete model for "what lives at global vs project scope"):

> "The convention is simple: any AI coding tool that supports AGENTS.md looks for the file
> at the repository root. The tool then loads the file..." [S-PI-9]

> "Codex reads `AGENTS.md` files before doing any work. By layering global guidance with
> project-specific overrides... Discovery follows this precedence order: 1. Global scope: In
> your Codex home directory (defaults to `~/.codex`...), Codex reads `AGENTS.override.md` if
> it exists. Otherwise, Codex reads `AGENTS.md`... 2. Project scope: Starting at the project
> root... Codex walks down to your current working directory." [S-PI-11]

Nested AGENTS.md files scope instructions to subtrees (Copilot):

> "You can create a single `AGENTS.md` file in the root of your repository. You can also
> create nested `AGENTS.md` files which apply to specific parts of your project. Alongside
> `AGENTS.md`, the agent continues to support ... `CLAUDE.md` and `GEMINI.md` files." [S-PI-12]

### Portability tradeoff: always-loaded prose vs. per-tool proprietary files

The core portability argument for AGENTS.md is consolidation of N proprietary
always-loaded files into one:

> "Until now every tool invented its own private instruction file: Claude `CLAUDE.md`,
> Cursor `.cursor/rules`, Copilot `.github/copilot-instructions.md`, Gemini `GEMINI.md`...
> Maintaining five hand-written cheat-sheets is silly. AGENTS.md replaces [them]" [S-PI-13]

Relevance to the research question (always-loaded rules vs description-triggered skills):
The AGENTS.md standard is the **portable substrate for always-loaded prose**; the Agent
Skills standard (which Pi, and `.agents/skills/`, implement) is the **portable substrate
for on-demand/description-triggered behavior**. A yf rule that can only fire via always-loaded
context is portable across harnesses **only** as AGENTS.md-class prose (paid every turn on
every supporting harness); a rule that can be expressed as a skill description is portable as
a skill (paid only when triggered). `[uncertain]` The sources establish that both standards
exist and are cross-harness, but do not quantify per-harness token cost of always-loaded
prose vs skills — that quantitative tradeoff is not directly cited here (absence noted).

---

## Queries tried / coverage notes

- `pi coding agent pi.dev CLI global instructions rules config AGENTS.md` — oversized
  result, discarded (identity later confirmed via cleaner queries).
- `pi.dev coding agent AI` — resolved identity (S-PI-1, S-PI-2, S-PI-5).
- `Pi coding agent AGENTS.md rules skills global instructions ~/.pi configuration`
  (domains pi.dev, github.com) — yielded the context-files + skills mechanism (S-PI-3, S-PI-4, S-PI-6).
- `AGENTS.md open standard portable instruction file for AI coding agents agents.md` —
  yielded the standard, adoption, Codex/Copilot precedence, proprietary-file table (S-PI-7..S-PI-13).
- **Empty angle:** No first-party pi.dev "context-files" doc page resolved
  (`https://pi.dev/docs/latest/context-files` → HTTP 404). The AGENTS.md/SYSTEM.md loading
  behavior is instead cited from a first-party-adjacent pi-config skill reference [S-PI-4]
  and corroborated by a real Pi config repo [S-PI-6]. `[uncertain]` exact current doc URL.
- **Empty angle:** Verbatim statement of Pi's skill *trigger* model (description-match vs
  explicit invoke) not found — noted as absence above.
</content>
