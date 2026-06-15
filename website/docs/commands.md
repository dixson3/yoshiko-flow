---
title: Command Reference
sidebar_position: 3
---

# `yf` Command Reference

```
yf <COMMAND>

Commands:
  skills     Manage embedded skills (install / upgrade / remove / status)
  doctor     Diagnose the local environment and skill installs
  preflight  Run a skill's preflight checks
  version    Print the `yf` version and build metadata
```

`yf` exposes `skills`, `doctor`, `preflight`, and `version` (REQ-YF-CLI-001).
Every subcommand supports `--json` for machine-readable output and exits non-zero
on failure (REQ-YF-CLI-003).

## `yf skills`

The skills lifecycle: `install`, `upgrade`, `remove`, `status`. All four accept
the same flags.

| Flag | Default | Meaning |
| :-- | :-- | :-- |
| `[NAMES]...` | resolved set | Explicit skill names to act on. |
| `--scope {user,project}` | `user` | Anchor: `$HOME` (user) or git-root/cwd (project). |
| `--surface {claude,agents}` | `claude` | The `.claude` or `.agents` surface. |
| `--target <PATH>` | — | Explicit destination; overrides scope/surface (rules → sibling `rules/`). |
| `--group <NAME>` | — | Act only on skills in this `skill-group` (`beads`, `utility`, `markdown`). |
| `--strict` | off | Treat a missing `depends-on-tool` as a hard failure (install). |
| `--force` | off | Overwrite an existing companion rule (default preserves hand-edits). |
| `--dry-run` | off | Show what would change; write nothing. |
| `--json` | off | Machine-readable JSON output. |

Destination resolution (REQ-YF-CLI-002, REQ-YF-INSTALL-002): `--target` wins;
otherwise `<anchor>/.<surface>/skills`, with rules at `<anchor>/.<surface>/rules`.

### `yf skills install`

Copies a skill's tree to the resolved destination and copies its companion rules
(`protocols/*.md`) to the sibling `rules/` surface (REQ-YF-INSTALL-001).
Installing a skill transitively includes its `depends-on-skill` closure;
unresolved/external deps are logged, not fatal (REQ-YF-INSTALL-004). On install,
a single integrity marker is injected into the deployed `SKILL.md` after the YAML
frontmatter (REQ-YF-MARK-002):

```
<!-- yf-skills: v=<version> tree=<sha256> -->
```

### `yf skills upgrade`

Rewrites a skill's files, re-injects the marker, refreshes the companion rules,
and **prunes** any deployed files no longer present in the embedded tree
(REQ-YF-MARK-004). Use `--dry-run` to preview the prune set.

### `yf skills remove`

Deletes a skill's deployed directory. A companion rule is removed **only** when
its on-disk bytes are byte-identical to the embedded source (unambiguously
`yf`-owned and unmodified); a hand-edited rule is left in place.

### `yf skills status`

Reports per skill (REQ-YF-MARK-003):

| Column | Meaning |
| :-- | :-- |
| `installed` | The skill's `SKILL.md` is present at the destination. |
| `up-to-date` | The deployed marker's tree hash equals the embedded tree hash. |
| `complete` | Every embedded file for the skill is present on disk. |
| `unmodified` | The deployed tree, recomputed and marker-stripped, hashes equal to the embedded tree (no local tampering). |

The tree hash is a SHA256 over each file (sorted by relpath), with `SKILL.md`
marker-stripped before hashing, so a deployed marked copy hashes identically to
the embedded source (REQ-YF-MARK-001). A tampered file flips `unmodified` to
`no` while the (untouched) marker can still read `up-to-date`.

## `yf doctor`

Diagnoses the local environment and skill installs against the default
user/claude surface, exiting non-zero if any axis fails
(REQ-YF-DOCTOR-001/002). Supports `--json`.

Axes:

- **`version`** — `yf` itself (always reports the build line).
- **`bd`** — present on PATH and version ≥ 1.0.5.
- **`uv`** — present on PATH.
- **`git`** — present on PATH.
- **`skills:<name>`** — per skill, the marker comparison verdict:
  `not installed` / `incomplete` / `outdated (run yf skills upgrade)` /
  `modified` / `ok`.
- **`rules:<name>`** — for skills that ship companion rules, the rule's
  presence + content hash against the embedded source
  (`rule_missing` / `rule_drift`, else current).

## `yf preflight <skill>`

Runs a skill's shared preflight checks and returns a status from the superset
schema (REQ-YF-PRE-001):

```
ok | ignored | system_deps_missing | bd_not_initialized |
rule_missing | rule_drift | rule_deprecated |
manifest_schema_unknown | manifest_missing
```

```bash
yf preflight plan --json
yf preflight research --json
```

`<skill>` is the logical skill name (e.g. `plan`, `research`). With `--json`, the
**`status` field** is the authoritative verdict. The output also carries
`missing`, `instructions`, a `rule` object, and `scaffold_added`. See
[Preflight & Config](./preflight.md) for the full model and the `.yf/` state /
config layout.

## `yf version`

Prints the semver version and build metadata (REQ-YF-CLI-004):

```bash
$ yf version
yf 0.1.0 (30b2d8f)
```

Supports `--json`.
