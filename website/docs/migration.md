---
title: Migration Guide
sidebar_position: 6
---

# Migration Guide: the `yf-` rename

A one-time guide for upgrading from the old `bd*` skill names to Yoshiko Flow's
`yf-` prefix (REQ-YF-RENAME-001, REQ-YF-MIGRATE-001). Read once, apply, discard.

## Skill names

All skills moved to a `yf-` prefix. Notably:

- `bdplan` → `yf-plan`
- `bdresearch` → `yf-research`
- every other skill → `yf-<skill>`

Invocations now use the prefixed names: `/yf-plan`, `/yf-research`,
`/yf-<skill>`. The old `/bdplan` and `/bdresearch` invocations no longer resolve
once the renamed skills are installed.

## Command changes

| Old | New |
| :-- | :-- |
| `/bdplan <objective>` | `/yf-plan <objective>` |
| `/bdplan continue` | `/yf-plan continue` |
| `/bdplan execute` | `/yf-plan execute` |
| `/bdresearch <topic>` | `/yf-research <topic>` |
| `/<other-skill>` | `/yf-<other-skill>` |

The subcommands and their behavior are unchanged — only the skill prefix moves.

## State & config rename

| Purpose | Old path | New path |
| :-- | :-- | :-- |
| Runtime state | `.state/<skill>/` | `.yf/<skill>/` |
| Operator config | `.<skill>.local.json` | `.yf-<skill>.local.json` |

For example, `.bdplan.local.json` → `.yf-plan.local.json` and
`.bdresearch.local.json` → `.yf-research.local.json`.

`yf` migrates these paths **idempotently** when run (REQ-YF-MIGRATE-001):
existing state and config are moved to the new locations on first run, and
re-running is a no-op. Once migration has run, the old `.state/` directory and
`.<skill>.local.json` files can be removed. There are **no runtime aliases** —
the migration moves the files and the kernel reads only the new paths.

## Reinstall the renamed skills

If you already have the old skills installed, reinstall to deploy the renamed
skill directories plus their companion rules:

```bash
yf skills install
```

(See [Install](./install.md) for scope/surface/group options.)

## Update your `.gitignore`

Repos carrying the old skill-runtime anchors:

```
/.state/
/.bdplan.local.json
```

should update to the new naming:

```
/.yf/
/.yf-plan.local.json
/.yf-research.local.json
```

## Update personal instruction files manually

Your `~/.claude/CLAUDE.md` or `AGENTS.md` may still reference `/bdplan` or
`/bdresearch`. These files are **operator-owned** — `yf` does **not** edit them.
Update any such references to `/yf-plan` / `/yf-research` (and any other renamed
skill) by hand.
