# Migration: `yf-` rename

A one-time guide for the skill/state/config rename introduced in plan-010
(`REQ-YF-RENAME-001`, `REQ-YF-MIGRATE-001`). Read once, apply, discard.

## Skill rename

All skills moved to a `yf-` prefix. Notably:

- `bdplan` → `yf-plan`
- `bdresearch` → `yf-research`
- every other skill → `yf-<skill>`

Invocations now use the prefixed names: `/yf-plan`, `/yf-research`, `/yf-<skill>`.
The old `/bdplan` and `/bdresearch` invocations no longer resolve once the renamed
skills are installed.

## State / config rename

Per `REQ-YF-RENAME-001`:

- Runtime state: `.state/<skill>/` → `.yf/<skill>/`
- Operator config: `.<skill>.local.json` → `.yf-<skill>.local.json`
  (e.g. `.bdplan.local.json` → `.yf-plan.local.json`,
  `.bdresearch.local.json` → `.yf-research.local.json`)

`yf` migrates these paths **idempotently** when run (`REQ-YF-MIGRATE-001`): existing
state and config are moved to the new locations on first run, and re-running is a
no-op. Once migration has run, the old `.state/` directory and `.<skill>.local.json`
files can be removed.

## Installed copies / out-of-repo

Users who already have the old skills installed should reinstall:

```sh
yf skills install
```

This installs the renamed skill directories plus their companion rules.

Personal instruction files — your `~/.claude/CLAUDE.md` or `AGENTS.md` — may still
reference `/bdplan` or `/bdresearch`. These files are **operator-owned**: `yf` does
**not** edit them (per `GR-008`). Update any such references to `/yf-plan` /
`/yf-research` manually.

## Old `.gitignore` anchors

Repos that carry the old skill-runtime anchors in `.gitignore`:

```
/.state/
/.bdplan.local.json
```

should update them to the new naming:

```
/.yf/
/.yf-plan.local.json
/.yf-research.local.json
```

This repo's `.gitignore` is already updated.
