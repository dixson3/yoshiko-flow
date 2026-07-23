Title: managed files
Slug: managed-files
Subtitle: every file the yf skills produce or consume, and which skill owns each

The yf skills read and write a handful of on-disk files: always-loaded instruction
surfaces, per-repo manifests that arm the trigger-based engines, marker files, and the
artifact bundles the workflow skills emit. This page is a **hub** — one place to see every
managed file, what it is for, and which skill owns it.

For the deep detail on the harness-specific surfaces `yf harness tune` writes — the managed
`BEGIN`/`END` blocks, the `.yf/` ownership manifest, and the per-harness × per-scope config
matrix — see the [harness tune page](/harness-tune/). This page links there rather than
restating it. For one-line definitions of the vocabulary, see the
[glossary](/glossary/).

## At a glance

| File | What it is | Owning skill |
|:-----|:-----------|:-------------|
| `AGENTS.md` (per harness / project root) | Always-loaded instructions; carries the yf-managed rule block | [`yf harness tune`](/harness-tune/) |
| `CLAUDE.md` | Claude Code's project instruction file (often a thin `@AGENTS.md` include) | `yf-optimal-instructions` |
| `YOSHIKO_FLOW.md` | Aggregated always-loaded ruleset (all yf trigger rules) | [`yf harness tune`](/harness-tune/) |
| `CHANGE-VALIDATION.md` | Per-repo validation recipe (build/test/lint tiers) | `yf-change-validation` |
| `DRIFT-CHECK.md` | Per-repo content-agreement manifest | `yf-drift-check` |
| `.markdown-lint-on-edit` | Opt-in marker enabling on-edit markdown linting | `yf-markdown-lint` |
| `.yf/harness-tune-manifest.json` | Records yf's tune writes, for `--revert` | [`yf harness tune`](/harness-tune/) |
| `.beads/` | The beads (Dolt) database dir + gitignore/hooks | `yf-beads-*` + `yf` preflight |
| Plan / research / incubator bundle files | The OKF artifact folder contents | `yf-plan` / `yf-research` / `yf-incubator` |

## Always-loaded instruction surfaces

These files load on **every** turn of an agent session, so they are the surface the
trigger-based engine skills rely on to fire.

### `AGENTS.md`

The harness-neutral always-loaded instruction file — read by codex
(`~/.codex/AGENTS.md`), opencode (`~/.config/opencode/AGENTS.md`), pi, and the `agents`
surface, and also honored at a project root (`<git-root>/AGENTS.md`). `yf harness tune`
deploys the yf trigger rules into it as a managed `BEGIN`/`END` block that shares the file
with operator prose. The block detail — how it appends when absent, replaces only the
marked span when present, and refuses rather than corrupt a file with partial markers — is
documented on the [harness tune page](/harness-tune/#rule-managed-block-target).

### `CLAUDE.md`

Claude Code's project instruction file at the repo root. In the yf convention it is a
**thin index** — often just a one-line `@AGENTS.md` include — with the substantive
behavioral rules living in `AGENTS.md` and the rules surface. It is owned and optimized by
`yf-optimal-instructions`, which on any edit auto-applies token-efficiency cuts and
proposes the AGENTS.md-primary / CLAUDE.md-index structure. Claude Code itself reads its
always-loaded rules from a rules **directory** (`~/.claude/rules/` or
`<git-root>/.claude/rules/`), not from `AGENTS.md`; `yf harness tune` writes the aggregate
there for this harness.

### `YOSHIKO_FLOW.md`

The **aggregated** always-loaded ruleset — the beads-init, change-validation, drift-check,
markdown-lint, and planning / research / upstream-tracking trigger rules combined into one
file. `yf harness tune` composes and deploys it (this is the aggregate that lands in
claude-code's rules directory). Because it is a tune output, its composition and
destinations are covered on the [harness tune page](/harness-tune/); this page does not
restate them.

## Per-repo engine manifests

Each trigger-based engine skill reads a per-repo manifest that must be present and
**approved** (`§0 approved: yes`) before the engine will act. Absent or unapproved, the
engine is a silent no-op.

### `CHANGE-VALIDATION.md`

The repo's recorded **validation recipe**, owned by `yf-change-validation`. It lives at the
repo root and declares:

- **tiers** (§1) — a `fast` tier of affected-only checks and a `full` tier that is the
  CI ∪ repo-checks superset, each a table of `id` / `cmd` / `cwd` / `timeout` rows;
- **trigger-scope globs** (§3) — the changed paths that arm an on-edit FAST run;
- **§0 approval** — the gate that turns the engine from no-op to active.

The engine *executes* those commands and reports PASS / FAIL / INCONCLUSIVE plus the first
failing command; it never auto-fixes and never rewrites the manifest.

### `DRIFT-CHECK.md`

The repo's **content-agreement manifest**, owned by `yf-drift-check`. Also at the repo
root, it declares the artifact graph the engine verifies — source-of-truth **nodes** and
**edges** (implementation ↔ docs ↔ spec), per-edge contracts, the changed-path
**trigger-scope globs**, and the fixed-authority policy — behind the same `§0 approved:
yes` gate. On an in-scope edit the engine dispatches a report-only sub-agent that checks
each edge and returns PASS / FAIL / INCONCLUSIVE / CONFLICT. It verifies agreement only; it
never authors or auto-fixes.

`yf-change-validation` and `yf-drift-check` are **orthogonal**: the first proves a
change-set is behaviorally valid by running commands, the second proves already-written
artifacts agree. A single `.md` edit may arm both on their own axes.

### `.markdown-lint-on-edit`

A per-repo **opt-in marker** at the repo root, owned by `yf-markdown-lint`. Its mere
presence enables on-edit linting of `.md` files against the fast authoring rule subset;
without it the on-edit trigger is a silent no-op. An empty marker means "use the default
subset"; a non-empty marker may override the rule set or list exclude globs.

## Beads and tune sidecar state

### `.beads/`

The beads database directory at the repo root — the Dolt (versioned SQL) DB that backs all
yf task tracking, plus the formulas staged by preflight and the gitignore / hooks entries
that keep it healthy. It is owned collectively by the `yf-beads-*` skills and the `yf`
preflight (which verifies and repairs it). For what beads is and how the six `yf-beads-*`
skills divide the work, see the [beads concepts page](/beads-concepts/).

### `.yf/harness-tune-manifest.json`

The tune **ownership manifest**, owned by `yf harness tune`. It records exactly what each
tune wrote — config keys, set-union additions, and rule-block markers — so a later
`--revert` can reverse precisely without clobbering operator content. Its structure and
per-scope location are documented on the
[harness tune page](/harness-tune/#the-yf-ownership-manifest); this page does not restate
them.

## Artifact bundle files

The workflow skills emit their output as **OKF bundles** — self-describing artifact
folders that a cold reader in a different repo can understand from the folder alone. Each
plan, research project, or incubator topic lives in one such folder (under `docs/plans/`,
`docs/research/`, or `Incubator/<slug>/`, or the incubator-scoped equivalents). The files
inside:

| File | Role |
|:-----|:-----|
| `plan.md` | The plan document itself (yf-plan) |
| `index.md` | OKF-reserved bundle listing — the folder's manifest |
| `log.md` | OKF-reserved newest-first phase history |
| `context.md` | Portable context a cold reader needs |
| `references/` | Cited / linked source material |
| `reviews/` | Review artifacts produced during the workflow |
| `findings/` | Research findings (yf-research) |

`plan.md` and its siblings are owned by `yf-plan`; the research and incubator variants are
owned by `yf-research` and `yf-incubator`. The reserved `index.md` / `log.md` + frontmatter
+ non-empty `type` model is defined by the OKF spec family and conformance-checked by
`yf-okf` (report-only `check`, opt-in per-folder `migrate`). For how these bundles are
produced by the multi-phase pipelines, see the [workflows page](/workflows/).
