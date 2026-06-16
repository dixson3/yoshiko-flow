---
slug: /
title: Overview
sidebar_position: 1
---

# Yoshiko Flow

**Yoshiko Flow** is a family of portable, cross-harness agent **skills** plus a
single compiled CLI, **`yf`**, that installs, upgrades, verifies, and preflights
those skills and the toolchain they depend on.

The product is *Yoshiko Flow*; the binary you install and run is **`yf`**.

## What you get

- **13 portable skills** (`yf-*`) — beads-backed planning and research, beads
  setup and upstream tracking, instruction-file and skill-authoring helpers,
  drift checking, and markdown tooling. See the [Skill Catalog](./skills.md).
- **The `yf` CLI** — one self-contained binary that **embeds the entire skill
  tree at build time** (REQ-YF-EMBED-001), so installing skills needs no network
  access or repo clone. See the [Command Reference](./commands.md).

## How it fits together

```
brew install dixson3/tap/yf     # the binary (+ beads + uv, pulled in)
yf skills install               # deploy the embedded skills into your harness
yf doctor                       # verify the environment + every install
```

`yf` installs skills into a **scope** (`user` or `project`) and a **harness
surface** (`claude` or `agents`) — e.g. `~/.claude/skills/` for the default
user/claude target (REQ-YF-INSTALL-002). Each skill is deployed with its
companion **rules** (`protocols/*.md`) copied into the sibling `rules/` surface
so the always-loaded trigger contracts are in context.

## What `yf` is not

`yf` is the installer/verifier/preflight kernel. It does **not** run skills,
track issues (that is [`bd` / beads](https://github.com/gastownhall/beads)), or
render markdown/diagrams — those are the skills themselves.

## Next steps

- [Install](./install.md) — Homebrew, `yf skills install`, `yf doctor`.
- [Command Reference](./commands.md) — every subcommand and flag.
- [Skill Catalog](./skills.md) — the 13 `yf-*` skills.
- [Preflight & Config](./preflight.md) — the shared preflight/config kernel.
- [Migration Guide](./migration.md) — upgrading from the old `bd*` skill names.
