---
title: skill-authoring
created: '2026-05-25'
tags: []
---

# skill-authoring

Conventions for Claude Code skills, agents, and instruction files. Read by humans authoring skills; loaded by agents via [SKILL](SKILL.md) at the moment of need.

## Prerequisites

- `uv` on `PATH` — the frontmatter declares `depends-on-tool: [uv]`. It is what runs
  `scripts/manifest_update.py` and every PEP 723 helper this skill teaches you to write.

No other tool is required: the conventions themselves are prose, and everything else in this
skill is read rather than executed.

## Install

Deployed by `yf skills install`, which auto-discovers every `skills/*/` by its `SKILL.md`
frontmatter. From a clean `main`, rebuild and deploy in one step:

```bash
yf self install --from-build --build
```

## Usage

**Not user-invocable** (`user-invocable: false`) — there is no `/yf-skill-authoring` command.
The skill loads from its description when you create or edit a file under
`.{claude,agents}/skills/<skill>/`: a `SKILL.md`, an `agents/*.md`, a skill's own rules, or a
`.py` helper meant to run via `uv run`.

Project-root instruction files (`CLAUDE.md`, `AGENTS.md`, `AGENTS/*`) route to
**`yf-optimal-instructions`** instead. That is the distinguishing axis: this skill owns
**skill-dir** instruction files; `yf-optimal-instructions` owns **project-root** ones.

The one command this skill ships is the protocol-manifest refresh, run after editing a
`protocols/*.md` file:

```bash
uv run ${SKILL_DIR}/scripts/manifest_update.py ${SKILL_DIR}/protocols
```

## What this skill covers

- **Structure.** Where skill files live, when to extract a script or module, what the directory layout looks like.
- **Skill Surface Convention.** How skills install companion rules, store config and state, register hooks, and run preflight. Seven elements, adopt as a contract. Full spec in [reference/SURFACE_CONVENTION.md](reference/SURFACE_CONVENTION.md).
- **Token efficiency.** What to cut and what to keep so always-loaded context stays tight. This
  is the single source of truth for the token-efficiency ruleset; `optimal-instructions` cites it.
- **Python helpers.** `uv run` discipline, PEP 723 inline deps, argument parsers, runtime-cache rules.
- **Review pipeline.** Three read-only review agents (general, reviewer-tokens, red-team) plus a
  Python-specific reviewer. The reviewer-tokens agent covers **skill-dir** instruction files; project-root
  instruction files (CLAUDE.md, AGENTS.md, AGENTS/*) are the `optimal-instructions` skill's domain.

## What this skill does NOT cover

- Application code outside `.{claude,agents}/skills/`.
- End-user documentation or operator-facing notes.
- Planning a skill's design beyond conventions — that belongs in the project's planning skill.
- Backend-specific protocol surfaces (beads vocabulary, protocol verbs, etc.) — those live in their own skills.
- Protocol-specific meta-conventions that overlay these rules — those live in protocol-specific authoring skills, applied *after* these conventions.
- Optimizing **project-root** instruction files (CLAUDE.md, AGENTS.md, AGENTS/* not under a skill dir) — that is the `optimal-instructions` skill's domain. The token-efficiency ruleset is shared from here; only the trigger surface differs.

## When to read what

- Authoring a new skill from scratch → read [SKILL](SKILL.md) start to finish, then [reference/SURFACE_CONVENTION.md](reference/SURFACE_CONVENTION.md).
- Adding a helper script → [SKILL](SKILL.md) § Python helpers (or sibling-language equivalent).
- Writing an agent file inside a multi-agent skill → [reference/PIPELINE.md](reference/PIPELINE.md).
- Referencing skill-internal files from a script → [reference/PORTABILITY.md](reference/PORTABILITY.md).
- Reviewing an existing skill → see § Review sequence in [SKILL](SKILL.md).
- Trimming a skill-dir instruction file → dispatch the [agents/reviewer-tokens.md](agents/reviewer-tokens.md) agent. For a project-root instruction file, use the `optimal-instructions` skill.

## Layout shipped by this skill

```
skills/yf-skill-authoring/
├── agents/
│   ├── red-team.md            # adversarial skill check
│   ├── reviewer-python.md     # Python helper review
│   ├── reviewer-tokens.md     # token-efficiency reviewer (skill-dir instruction files)
│   └── reviewer.md            # general skill review
├── reference/
│   ├── AGENT_ROLES.md         # canonical agent role vocabulary + factoring test + role table
│   ├── PIPELINE.md            # multi-agent skill conventions
│   ├── PORTABILITY.md         # SKILL_DIR resolution + portability checklist
│   └── SURFACE_CONVENTION.md  # full Skill Surface Convention spec + worked example
├── scripts/
│   └── manifest_update.py     # shared manifest helper (vendored by adopting skills)
├── README.md                  # this file
├── SKILL.md
└── SPEC.md
```

## Why the convention exists

Skills accumulate divergent init / config / state / hook patterns the moment more than one of them ships. The Skill Surface Convention picks one shape, documents it, and gives adopting skills a hash-checked manifest so installed rule files don't silently drift from the skill source.

The whole convention is an interdependent contract — implementing only some elements produces drift the preflight audit can't recover from. Adopt all seven or none.
