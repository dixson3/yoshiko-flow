---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: codex-cli — OpenAI Codex CLI instruction / rules mechanism

Method: exa (Exa MCP `web_search_advanced_exa` + `get_code_context_exa`, then WebFetch on
official-doc URLs). Target: how OpenAI Codex CLI loads project + global instructions, its
global config, and whether it has always-loaded "rules" vs on-demand skills.

Retrieved 2026-07-22. Sources: `sources-codex-cli.json` (ids `S-CX-*`).

---

## Finding 1 — AGENTS.md is Codex's project/global instruction file; hierarchical, concatenated, later-overrides-earlier

Codex reads `AGENTS.md` before doing any work and assembles a **chain** from global scope down
to the current working directory.

- Global scope first, in the Codex home dir:
  > "In your Codex home directory (defaults to `~/.codex`, unless you set `CODEX_HOME`), Codex reads `AGENTS.override.md` if it exists. Otherwise, Codex reads `AGENTS.md`." [S-CX-1]
- Project scope second, walking root → cwd:
  > "Starting at the project root (typically the Git root), Codex walks down to your current working directory... In each directory along the path, it checks for `AGENTS.override.md`, then `AGENTS.md`, then any fallback names in `project_doc_fallback_filenames`." [S-CX-1]
- Merge / precedence order:
  > "Codex concatenates files from the root down, joining them with blank lines. Files closer to your current directory override earlier guidance because they appear later in the combined prompt." [S-CX-1]

So the **global** always-loaded instruction file is `~/.codex/AGENTS.md` (or `AGENTS.override.md`),
and precedence is **most-specific-wins by position** (later in the concatenated prompt). The
mechanism is implemented in the Codex Rust core:
> "AGENTS.md discovery and user instruction assembly. Project-level documentation is primarily stored in files name[d] ..." [S-CX-4]

## Finding 2 — Loading timing: built once per run/session (not lazily), so it is genuinely always-loaded

> "Codex builds an instruction chain when it starts (once per run; in the TUI this usually means once per launched session)." [S-CX-1]

This confirms AGENTS.md content is an **always-loaded** surface — paid at session start,
equivalent in role to Claude Code's always-loaded rules / `CLAUDE.md`.

## Finding 3 — Size cap on the always-loaded surface (32 KiB default)

> "Codex skips empty files and stops adding files once the combined size reaches the limit defined by `project_doc_max_bytes` (32 KiB by default)." [S-CX-1]

Relevant to the minimization thesis: the always-loaded budget is bounded and configurable via
`project_doc_max_bytes`.

## Finding 4 — Customization layers: AGENTS.md (persistent) vs Skills (on-demand) — analogous to rules-vs-skills

Codex's own docs frame the same split this research is about. Customization is layered:
> Project guidance (`AGENTS.md`) – persistent instructions; Memories; Skills – reusable workflows; MCP; Subagents. [S-CX-2]

- AGENTS.md = always loaded / persistent:
  > "AGENTS.md ... gives Codex durable project guidance that travels with your repository and applies before the agent starts work." [S-CX-2]
  > "the rules you want Codex to follow every time in a repo" [S-CX-2]
- Skills = progressive disclosure (metadata always visible, body on-demand):
  > "It starts with metadata (name, description) for discovery" ... "It loads SKILL.md only when a skill is chosen." [S-CX-2]
- The two are explicitly complementary:
  > "complementary, not competing" [S-CX-2]

**Key transferable insight:** Codex uses the *same* progressive-disclosure model as Claude Code
skills — a `description` field is the discovery trigger and the full `SKILL.md` loads only when
the task matches. This directly supports the research thesis that content movable into a skill
description need not sit in the always-loaded AGENTS.md.

## Finding 5 — Global config is `~/.codex/config.toml`; skills-vs-rules loading model; token costs [S-CX-3, medium credibility]

Independent technical analysis (not official docs — corroborates official where they overlap):

- Global config file:
  > "`developer_instructions` key in config.toml injects additional text into the agent's system prompt without modifying any file in the repository" [S-CX-3] — i.e. `~/.codex/config.toml` is the user-level config, and it carries a system-prompt-injection key. [uncertain] `developer_instructions` is not confirmed in the official docs pages fetched; treat as blog-sourced.
- AGENTS.md persistence within a session:
  > "AGENTS.md instructions are re-read on every turn and survive context compaction intact" [S-CX-3] [uncertain] — official docs (S-CX-1) say the chain is built once per run; "re-read every turn" is a stronger claim, blog-sourced only.
- Skills / hooks load conditionally, unlike always-evaluated rules:
  > "A skill's SKILL.md instructions enter the context only when the agent determines the current task matches the skill's description." [S-CX-3]
  > "Hooks are the only surface that injects instructions during a turn rather than at session start." [S-CX-3]
- Token / context cost of the on-demand skills index vs activation:
  > "The initial skills list costs roughly 2% of the context window (~8,000 characters)" [S-CX-3]
  > "the full SKILL.md instructions enter the context — potentially adding thousands of tokens" [S-CX-3]
  > AGENTS.md is "capped at project_doc_max_bytes (default: 32 KiB)" [S-CX-3] (corroborates S-CX-1)

## Absence / gaps

- **No dedicated always-loaded "rules" file distinct from AGENTS.md in official Codex docs.** The
  official customization layers are AGENTS.md, Memories, Skills, MCP, Subagents [S-CX-2] — there
  is no separate first-class "rules" surface analogous to Claude Code's `~/.claude/rules/*.md`.
  The blog [S-CX-3] uses "rules" for command-evaluation-time enforcement (a different concept,
  closer to permission/policy gates than instruction text). So Codex's answer to "always-loaded
  rules" is effectively **AGENTS.md itself** (global `~/.codex/AGENTS.md` + repo `AGENTS.md`).
  [uncertain — based on the fetched pages; a separate rules surface was not found, which per
  epistemic rules is itself a finding, not proof of non-existence.]
- **`config.toml` full key surface not enumerated here.** Only the AGENTS.md-related keys
  (`CODEX_HOME`, `project_doc_fallback_filenames`, `project_doc_max_bytes`) are confirmed from
  official docs [S-CX-1]. The `developer_instructions` system-prompt injection is blog-sourced
  only [S-CX-3].

### Queries tried
- Exa advanced (`includeDomains: github.com, developers.openai.com, openai.com`): "OpenAI Codex
  CLI AGENTS.md project and global instructions ~/.codex config.toml precedence merge order" —
  result payload exceeded token limit (saved to tool-results file); pivoted to code-context.
- Exa `get_code_context_exa`: "OpenAI Codex CLI AGENTS.md global ~/.codex/AGENTS.md instructions
  config.toml precedence loading" — returned the official guide, customization page, the
  `agents_md.rs` source, and issues #18189 / #14687 / #15683 (global-AGENTS.md loading bugs).
- WebFetch on official doc URLs (both 308-redirect from developers.openai.com to
  learn.chatgpt.com) + the danielvaughan instruction-stack blog for config.toml / token detail.
