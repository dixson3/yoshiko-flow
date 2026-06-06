---
title: optimal-instructions
created: '2026-05-31'
tags: []
---

# optimal-instructions

Auto-fix skill for project instruction files (`CLAUDE.md`, `AGENTS.md`, `AGENTS/*`, repo-root
`.{claude,agents}/rules/*`). On create/modify it reads the file, auto-applies token-efficiency
cuts, and proposes structural relocation toward AGENTS.md-primacy, then reports what changed.

## Prerequisites

- Claude Code (the skill loads as part of this repo's skill set).
- The `skill-authoring` skill present in the same skill set — it is the single source of truth
  for the token-efficiency (K1) ruleset this skill cites.
- `uv` — required only by `scripts/manifest_update.py` (a PEP 723 `uv run --script`), which
  maintains `protocols/manifest.json`. Not needed for the skill's core auto-fix behavior. No
  `check-prereqs.sh`.

## Install

Installed by the repo-level `install.sh`, which auto-discovers every `skills/*/` directory. This
skill ships one **companion rule** (`protocols/INSTRUCTIONS.md`) that `install.sh` surfaces to
the install's rules dir (always-loaded), and **no hook**. No install changes needed — both the
skill and its rule are picked up automatically. See the project [README](../../README.md) for
`install.sh` flags.

## Usage

Not user-invocable (`user-invocable: false`). It fires from its `description` TRIGGER when a
project-root instruction file is created or modified. Triggering is **best-effort** — a
description-only skill (the skill registers no hook) cannot guarantee it runs on every write,
which is why it ships the always-loaded `protocols/INSTRUCTIONS.md` backstop. There are no
subcommands.

Scope boundary: instruction files **inside a skill directory** under `.{claude,agents}/skills/<skill>/`
(a skill's `SKILL.md`, `agents/*.md`, its own rules) belong to `skill-authoring`. The two
skills' descriptions are mutually exclusive on this skill-dir vs project-root axis.

## Behavior model

```
changed instruction file
        │
        ▼
detect file kind + rules surface (AGENTS/*, .agents/rules/*, or .claude/rules/*)
        │
        ▼
dispatch instruction-optimizer agent
        │
        ├─ K1 token-efficiency edits ──▶ auto-apply (write)
        │
        └─ K2 structural proposal ─────▶ propose ──▶ operator confirm ──▶ write (relocate, never delete)
        │
        ▼
surface change report
```

- **K1** (token efficiency) cites skill-authoring `SKILL.md` "Token efficiency" §; auto-applied.
- **K2** (AGENTS.md primary, CLAUDE.md a thin `@-include` index, behavioral rules in the rules
  subdir) is propose-and-confirm; relocate-never-delete.
- **Idempotent**: a no-op on already-optimized input.

## Layout

```
skills/optimal-instructions/
├── SKILL.md                          # entry point: trigger, SKILL_DIR, workflow, rules
├── README.md                         # this file
├── agents/
│   └── instruction-optimizer.md      # apply agent: K1 auto + K2 proposal + change report
├── protocols/
│   ├── INSTRUCTIONS.md               # always-loaded companion rule (installed to rules surface)
│   └── manifest.json                 # hash/version manifest for INSTRUCTIONS.md
├── scripts/
│   └── manifest_update.py            # recompute manifest hashes + bump versions (vendored)
└── spec/
    ├── structure.md                  # K2 structural convention (REQ-STRUCT-*)
    ├── apply.md                      # split-apply contract + idempotency + before/after example (REQ-APPLY-*)
    └── integration.md                # surface detection, runtime carve-out, no-dup boundary (REQ-INT-*)
```
