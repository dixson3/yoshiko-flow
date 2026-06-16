---
title: Skill Catalog
sidebar_position: 4
---

# `yf-*` Skill Catalog

Yoshiko Flow ships **13 skills**, grouped by `skill-group` frontmatter. Install
all of them with `yf skills install`, or a single group with
`yf skills install --group <name>` (see [Install](./install.md)). Invocable
skills are triggered with `/yf-<skill>`; `auto` skills fire from their
`description` conditions when relevant work appears.

## beads group

Skills that depend on (or feed) the `bd` issue tracker.

| Skill | Invocable | Purpose |
| :-- | :-- | :-- |
| `yf-plan` | `/yf-plan` | Structured planning with beads-tracked execution and upstream issue reconciliation. |
| `yf-research` | `/yf-research` | Multi-phase, beads-tracked deep research producing citation-backed, resumable reports. |
| `yf-incubator` | `/yf-incubator` | Create, fork, bookmark, resume, and triage research topics ("incubators") under `Incubator/`. |
| `yf-beads-init` | `/yf-beads-init` | Verify / initialize / repair a functioning beads config — the dependency-verification home other beads skills' preflights route to; fixes wedged migrations and the `bd status` error-JSON false-negative. |
| `yf-beads-extra` | auto | Advanced/gotcha layer for using the `bd` CLI directly — issue-type semantics, gates, bulk intake, JSON parsing. |
| `yf-beads-authoring` | auto | Conventions for building beads-backed skills — `.formula.toml`, `bd mol pour`, the coordinator dispatch loop. |
| `yf-beads-upstream` | `/yf-beads-upstream` | Configurable, GitHub-first upstream tracking — push open/deferred beads to an issue tracker as a land-the-plane step; upstream issues as the worklist. |

## utility group

Beads-free skills (no `bd` binary needed).

| Skill | Invocable | Purpose |
| :-- | :-- | :-- |
| `yf-skill-authoring` | auto | How to author, structure, and optimize Claude Code skills themselves; owns the token-efficiency ruleset. |
| `yf-optimal-instructions` | auto | Auto-fix skill for project instruction files (`CLAUDE.md`, `AGENTS.md`, `AGENTS/*`) — token-efficiency cuts + AGENTS.md-primacy structural proposals. |
| `yf-drift-check` | auto | Verifies content agreement across a repo's declared source-of-truth edges (impl ↔ docs ↔ spec) via a per-repo `DRIFT-CHECK.md` manifest; reports drift, never auto-fixes. |
| `yf-diagram-authoring` | `/yf-diagram-authoring` | Render light-mode, white-background diagram PNGs from `d2` source, with the `.d2` kept beside every `.png`. |

## markdown group

Standalone GFM tooling, beads-free.

| Skill | Invocable | Purpose |
| :-- | :-- | :-- |
| `yf-markdown-lint` | `/yf-markdown-lint` | Conventional GitHub-Flavored-Markdown linter — no Obsidian wiki-links/embeds, resolvable relative links/anchors, well-formed tables. |
| `yf-markdown-pdf` | `/yf-markdown-pdf` | Render a `.md` file to PDF via pandoc + xelatex, tuned for Unicode glyphs and relative image paths. |

## Group invariant

No `utility` skill may (transitively, via `depends-on-skill`) depend on a `beads`
skill — that keeps `yf skills install --group utility` provably beads-free.

## Each skill's preflight

Every beads skill's preflight routes through the shared `yf preflight` kernel and
`yf-beads-init`'s verify/repair engine. See [Preflight & Config](./preflight.md)
for the status schema and the per-skill `.yf/` state + config layout.
