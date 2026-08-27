Title: architecture
Slug: architecture
Subtitle: the yf kernel, embedded skills, beads, and upstream tracking

**yoshiko-flow** is two things that fit together: a family of portable, cross-harness agent
**skills**, and a single compiled CLI — **`yf`** — that installs, upgrades, verifies, and
preflights those skills and the toolchain they depend on. The product is *yoshiko-flow*; the
binary you install and run is `yf`.

![yoshiko-flow architecture](/images/architecture.png)

## The `yf` kernel

`yf` is one self-contained Rust binary — no runtime, no dependencies of its own. It is the
installer / verifier / preflight kernel. It does **not** run skills, track issues, or render
markdown — those are the skills themselves. Its jobs:

- **`yf harness skills`** — the lifecycle: `install`, `upgrade`, `remove`, `status`. Deploys
  skills into a **scope** (`user` or `project`) and one of **five harnesses**: `claude-code`,
  `codex`, `opencode`, `pi`, `agents`. (`yf skills` is a deprecated alias for the same verbs;
  `--surface claude|agents` is a deprecated alias for `--harness`.)
- **`yf harness tune`** — aligns a harness's config **and** deploys the always-loaded rules as a
  minimized managed block. `--revert` reverses yf's own additions from a sidecar ownership
  manifest, per key, keeping anything you hand-edited.
- **`yf skill-dir <name>`** — resolves an installed skill's directory across **every** harness
  destination above. This is how a shipped skill finds its own scripts, and it reads the same
  descriptor table `install` writes to, so the two cannot disagree.
- **`yf preflight <skill>`** — the shared readiness gate every beads-backed skill runs through,
  rather than each skill reimplementing it. Returns a single authoritative `status`. It is
  **read-only**: it reports a beads-config problem and routes you to `/yf-beads-init` rather
  than repairing it.
- **`yf doctor`** — checks the environment (`bd`, `uv`, `git`) and every installed skill's
  integrity marker and companion rule, plus per-harness settings-drift and managed-block axes.
  `--repair` is the opt-in flag that applies fixes.
- **`yf self`** — the **binary's** own lifecycle: `update`, `install`, `uninstall`. Distinct from
  `skills`, which manages the embedded skills and rules. Both `self install` and `self update`
  sync skills and rules at install time, with harness config behind a consent gate.
- **`yf migrate`** — moves a project from the legacy `.state/<skill>/` + `.<skill>.local.json`
  layout to the canonical `.yf/` namespace.

### The five harnesses

| `--harness` | user scope | project scope |
| :-- | :-- | :-- |
| `claude-code` | `~/.claude/skills` | `<git-root>/.claude/skills` |
| `codex` | `~/.agents/skills` | `<git-root>/.agents/skills` |
| `opencode` | `~/.config/opencode/skills` | `<git-root>/.opencode/skills` |
| `pi` | `~/.pi/agent/skills` | `<git-root>/.pi/skills` |
| `agents` | `~/.agents/skills` | `<git-root>/.agents/skills` |

`codex` and `agents` share a directory deliberately. **pi** applies a lowercase-hyphen name
transform to the on-disk skill directory, and its **config** tuning is deferred — `--harness pi`
deploys skills and rules only.

## Embedded skills

The **entire skill tree is embedded in the `yf` binary at build time**, so installing skills
needs no network access and no repo clone — the skills you get always match the binary you
already have. `yf` ships **19 skills**. Grouped by what they do:

- **workflows (3)** — the end-to-end, beads-tracked skills you invoke to get work done:
  `yf-plan`, `yf-research`, `yf-incubator`.
- **beads (5)** — the `bd` (beads) support layer the workflows build on: `yf-beads-init`,
  `yf-beads-extra`, `yf-beads-authoring`, `yf-beads-hygiene`, `yf-beads-upstream`.
- **utility (7)** — beads-free helpers: skill authoring, drift checking, diagram authoring,
  OKF folders, optimal instructions, change validation, herdr delegation.
- **markdown (4)** — standalone GFM tooling: lint, format, PDF, HTML.

Those four are the **install groups** — each skill's `skill-group` frontmatter — so
`yf harness skills install --group <name>` selects one. Installing a group pulls the **transitive
`depends-on-skill` closure** of its members, so `yf harness skills install --group workflows` also
installs the `beads` support skills the workflows depend on (see [install](/install/)). A
**group invariant** keeps the split honest: no `utility` skill may (transitively, via
`depends-on-skill`) depend on a `beads` skill, so `yf harness skills install --group utility` is
provably beads-free. Browse them all on the [skills](/skills/) page — that catalog, its
grouping, and each skill's dependency links are generated from the same `SKILL.md` frontmatter,
so they never drift from what ships.

## Companion rules

Each skill installs **with its companion rules** (`protocols/*.md`), copied into the sibling
`rules/` surface so the always-loaded trigger contracts are in context. On install, `yf`
injects a single integrity marker into the deployed `SKILL.md`; `yf skills status` and
`yf doctor` compare that marker's tree hash against the embedded source to report
`up-to-date` / `modified` / `outdated`.

## Beads: durable, resumable work tracking

Every stateful skill tracks its work in **beads** (`bd`) — a Dolt-backed issue database — not
in scratch TODO lists. A plan or research project is a DAG of beads with gates and
dependencies; a crashed session resumes from bead state, and the coordinator drains the DAG to
completion. Beads is the reason `/yf-plan` and `/yf-research` can span multiple sessions and
recover cleanly.

## Upstream tracking

At land-the-plane, open and deferred beads are pushed **upstream** to an issue tracker
(GitHub, GitLab, or Jira) so work that outlives the local clone is visible to the team. This
is orthogonal to Dolt replication (`bd dolt push`): upstream tracking mirrors *issues* to a
tracker, while Dolt push replicates the *database*. See the
[yf-beads-upstream](/skills/yf-beads-upstream/) skill.

## Where to go next

- **[skills](/skills/)** — the full catalog, generated from each skill's `SKILL.md`.
- **[lifecycle](/lifecycle/)** — how a skill goes from install to execution.
- **[install](/install/)** — get `yf` and the skills onto your machine.
