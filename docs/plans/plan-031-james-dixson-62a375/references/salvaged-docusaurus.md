# Salvaged Docusaurus content (issue #28 / `website/docs/`)

**Bead 1.1 staging note.** Verbatim capture of the six reusable `website/docs/*.md`
files before Epic 1.2 removes `website/`. Source of prose for the new Pelican pages
(Epic 3/4). **Stale facts to correct when porting:** the skill count is **18**, not 13
(intro.md and skills.md both say 13); the skills.md catalog omits `yf-beads-hygiene`,
`yf-okf`, `yf-change-validation`, `yf-incubator` variants, and the full markdown group
(`yf-markdown-format`, `yf-markdown-html`). The install-default is switching to the
vendor `curl | sh` at `https://yoshikoflow.sh/install.sh` (not the GitHub-releases URL
these docs use). Frontmatter is Docusaurus-style (`sidebar_position`) — Pelican pages use
`Title:`/`Slug:`/`Subtitle:` instead.


---

## Salvaged: website/docs/intro.md

```markdown
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
```

---

## Salvaged: website/docs/install.md

```markdown
---
title: Install
sidebar_position: 2
---

# Install

## curl | sh (recommended)

The vendor installer downloads a prebuilt `yf` to `~/.local/bin`, adds it to
`PATH`, and writes an install receipt under `~/.config/yf` — the uv-style
self-contained model (REQ-YF-DIST-001):

```bash
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/dixson3/yoshiko-flow/releases/latest/download/yf-installer.sh | sh
```

`yf` is distributed for `{darwin,linux} × {amd64,arm64}` with sha256 checksums.
**Installing `yf` does not install `bd` or `uv`** — install
[`beads`](https://github.com/gastownhall/beads) (the `bd` issue tracker) and
[`uv`](https://docs.astral.sh/uv/) (the Python runner several skills use)
separately (e.g. `brew install beads uv`).

Verify the binary:

```bash
yf version
```

### Keeping `yf` up to date

`yf` manages its **own** binary (distinct from `yf skills upgrade`, which manages
the embedded skills):

```bash
yf self update            # check GitHub Releases + swap the binary in place
yf self update --check    # report whether a newer release exists; do not swap
yf self uninstall         # remove the binary + yf-owned dirs (skills untouched)
```

`yf version` / `yf doctor` show a throttled, vendor-only nudge when a newer
release exists (silence with `YF_NO_UPDATE_CHECK=1`).

### Files and directories (XDG)

`yf` uses the XDG layout on Linux **and** macOS (honoring `XDG_*` overrides):

| Path                 | Contents                                              |
| :------------------- | :---------------------------------------------------- |
| `~/.local/bin/yf`    | the binary (vendor install target)                    |
| `~/.config/yf/`      | install receipt + from-build marker                   |
| `~/.cache/yf/`       | update-check throttle cache                           |
| `~/.local/share/yf/` | reserved for future on-disk content                   |

`YF_NO_UPDATE_CHECK=1` silences the upgrade nudge; `YF_VERSION` overrides the
version `yf self update` compares against.

On macOS, `curl | sh`- and `self update`-installed binaries are **not**
quarantined; only a browser-downloaded archive is — clear it with
`xattr -d com.apple.quarantine ~/.local/bin/yf`.

## Homebrew (secondary)

The tap still ships a working `yf`:

```bash
brew install dixson3/tap/yf
```

Direct brew users upgrade with `brew upgrade` — `yf self update` refuses on a
Homebrew (Cellar) copy and points back to brew. The formula declares **no**
runtime dependencies, so it does not pull in `bd` / `uv` (install those
separately, as above).

## Developer install (from a local build)

```bash
yf self install --from-build                   # copy target/release/yf → ~/.local/bin/yf
yf self install --from-build --debug --build   # build the debug profile first, then promote
```

A from-build install suppresses the upgrade nudge; `yf self update --force`
switches back to a vendor release.

## Install the skills

`yf` embeds the whole skill tree, so a single command deploys them into your
harness (REQ-YF-EMBED-001, REQ-YF-INSTALL-001):

```bash
# Everything (default) — all skills + their companion rules
yf skills install
```

By default this installs into the **user / claude** surface
(`~/.claude/skills/`), with companion rules in the sibling `~/.claude/rules/`
(REQ-YF-INSTALL-002). Each skill is copied with its `protocols/*.md` companion
rules so the always-loaded trigger contracts are present.

### Scope, surface, and destination

```bash
yf skills install --scope project        # <git-root>/.claude/skills/ (+ rules/)
yf skills install --surface agents       # ~/.agents/skills/ (+ rules/)
yf skills install --target /path/to/skills   # explicit dir; rules in sibling rules/
```

- `--scope {user,project}` (default `user`) — anchor is `$HOME` (user) or the
  git-root/cwd (project).
- `--surface {claude,agents}` (default `claude`) — picks the `.claude` or
  `.agents` surface.
- `--target <PATH>` — wins over scope/surface resolution; rules go to a sibling
  `rules/` dir.

### Selecting what to install

```bash
yf skills install --group utility        # only the beads-free utility skills
yf skills install --group beads          # only the beads-dependent skills
yf skills install yf-plan yf-research    # named skills (pulls their in-repo deps)
```

Groups are computed from each skill's `skill-group` frontmatter
(`beads`, `utility`, `markdown`) — not hardcoded (REQ-YF-INSTALL-003). Naming a
skill pulls in its transitive `depends-on-skill` closure; unresolved external
deps are logged, not fatal (REQ-YF-INSTALL-004).

### Preview and strictness

```bash
yf skills install --dry-run              # show what would change, write nothing
yf skills install --strict               # fail if a depends-on-tool binary is absent
yf skills install --force                # overwrite an existing companion rule
```

By default a missing `depends-on-tool` is a warning and the install still
proceeds (skill files are inert until the tool is present); `--strict` makes it a
hard failure. An existing companion rule is **preserved** unless `--force` is
given, so hand-edits survive a reinstall (REQ-YF-INSTALL-005,
REQ-YF-INSTALL-006).

## Verify the install

```bash
yf doctor
```

`yf doctor` checks the environment (`bd` present and ≥ 1.0.5, `uv`, `git`) and
every installed skill's marker + companion rule, exiting non-zero if any axis
fails (REQ-YF-DOCTOR-001/002). See the [Command Reference](./commands.md#yf-doctor)
for the full axis list.
```

---

## Salvaged: website/docs/commands.md

```markdown
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
```

---

## Salvaged: website/docs/preflight.md

```markdown
---
title: Preflight & Config
sidebar_position: 5
---

# Preflight & Config

Yoshiko Flow has a single shared **preflight/config kernel** inside `yf`. Every
beads-backed skill runs the same checks through `yf preflight <skill>` rather than
each skill reimplementing them (REQ-YF-PRE-001).

## What preflight does

`yf preflight <skill>` answers "is this skill ready to run here?" and returns a
single `status` from this enum (REQ-YF-PRE-001):

```
ok | ignored | system_deps_missing | bd_not_initialized |
rule_missing | rule_drift | rule_deprecated |
manifest_schema_unknown | manifest_missing
```

The checks, in evaluation order:

1. **Ignored?** — if the skill's config sets `ignore-skill`, return `ignored`
   (the operator chose to skip it). Exit code is 0 for `ignored`.
2. **System deps** — `git`, `uv`, and `bd` present, and `bd` ≥ 1.0.5
   (REQ-YF-PRE-002). Missing/outdated → `system_deps_missing`, with a `missing`
   list (e.g. `["uv", "bd>=1.0.5"]`) and remediation `instructions`.
3. **Beads initialized** — `bd status` works. If not, `bd_not_initialized`. The
   kernel parses the **JSON for an `error` key**, not the exit code
   (REQ-YF-PRE-006) — `bd status --json` can return an error JSON with exit 0
   (e.g. a wedged schema migration), and that initialized-but-wedged case must be
   classed corrupted, not "not initialized". Repair routes through
   [`yf-beads-init`](./skills.md).
4. **Companion rule** — the skill's always-loaded rule
   (e.g. `PLANS.md`, `RESEARCH.md`) is verified by sha256 + semver against the
   skill's embedded `manifest.json` (REQ-YF-PRE-003), yielding
   `rule_missing` / `rule_drift` / `rule_deprecated`, or the `manifest_*`
   statuses if the manifest itself is absent or has an unknown schema.
5. **Scaffold** — on an otherwise-ready repo the kernel idempotently writes the
   `/.yf/` gitignore anchor and reports it in `scaffold_added`
   (REQ-YF-PRE-005).

With `--json`, the **`status` field is authoritative** — consumers should test it
rather than the process exit code. The output object also carries `missing`,
`instructions`, a `rule` object, and `scaffold_added`.

## The `.yf/` state + config layout

Everything Yoshiko Flow writes per repo lives under a single `.yf/` tree, with
one gitignore anchor (`/.yf/`):

| Purpose | Path |
| :-- | :-- |
| Per-skill runtime state | `.yf/<skill>/` (e.g. `.yf/plan/preflight.json`) |
| Per-skill operator config | `.yf-<skill>.local.json` (e.g. `.yf-plan.local.json`) |
| Gitignore anchor | `/.yf/` (single entry) |

State is the kernel's runtime cache (REQ-YF-PRE-004). A `prereqs-present` flag is
written once the system-deps + `bd status` checks pass, so warm repos skip
straight to the cheap rule-hash check on later runs.

### The config file & `ignore-skill`

The per-skill operator config (`.yf-<skill>.local.json`) is **operator-owned**.
Its main lever is `ignore-skill`: set it truthy to make `yf preflight <skill>`
return `ignored` (and exit 0), opting a repo out of that skill's checks:

```json
{ "ignore-skill": true }
```

## The `rule` object

When `yf preflight` reports on the companion rule, the `rule` object carries:

- `outcome` — `ok | update_available | drift | deprecated | missing |
  manifest_schema_unknown | manifest_missing`.
- `rule` — the companion-rule filename (e.g. `PLANS.md`).
- `path` — the winning installed rule copy (when found).
- `version` — the manifest's declared semver (for `ok` / `update_available`).

The user/global rules dir is evaluated before the project copy; a correct global
copy short-circuits, so no per-project rule copy is required. An
`update_available` rule is non-blocking and collapses to top-level `status: ok`
(surfaced via `instructions`).

This per-rule manifest axis (semver + sha256) is **distinct** from the
whole-tree integrity marker that `yf skills status` / `yf doctor` compare — see
the [Command Reference](./commands.md).
```

---

## Salvaged: website/docs/migration.md

```markdown
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
```

---

## Salvaged: website/docs/skills.md

```markdown
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
```
