Title: harness tune
Slug: harness-tune
Subtitle: what yf harness tune writes, per harness and scope

`yf harness tune` is the second half of provisioning: where [`yf harness skills
install`](/install/#the-install-matrix-where-skills-land) deploys skill **bodies**, `tune`
deploys the two things that make the trigger-based engine skills actually fire — the
harness's **always-loaded rules** (a managed block) and, where a profile ships, its
**config** alignment. A bare `install` without `--tune` is non-functional for
`yf-change-validation`, `yf-drift-check`, `yf-markdown-lint`, and the `yf-beads-upstream`
close-time push until `tune` runs; see the [first-run note](/install/#install-the-skills).

```bash
yf harness tune                                 # user scope, all detected harnesses
yf harness tune --harness codex --harness pi    # specific harnesses (repeatable)
yf harness tune --project                       # project-local (gitignored) scope
yf harness tune --project --committed           # project-committed (shared) scope
yf harness tune --revert                         # reverse a prior tune (see below)
yf harness tune --dry-run                        # preview without writing
```

## The tune matrix — config file + rule target

![yf harness tune: the config file and rule managed-block target per harness](/images/tune-matrix.png)

`tune` runs two sub-operations per selected harness × scope: it **aligns the config file**
(only for harnesses that ship a config profile) and it **deploys the always-loaded rule
managed block**. The exact destinations below are derived from the shipped config profiles
(`yf/profiles/*.json` — `surface_dir`, `settings_filename`, `settings_local_filename`,
`format`) and the rule-target map (`yf/src/cmd/harness/managed_block.rs`); a doc↔code
agreement test keeps this page in sync.

### Config file — the three tune scopes

Three scopes resolve per harness (`yf/src/cmd/harness/settings.rs`):

- **user** (default) — `$HOME/<surface_dir>/<settings_filename>`
- **project-local** (`--project`) — `<git-root>/<surface_dir>/<settings_local_filename>` (the
  personal, gitignored file — the safe default)
- **project-committed** (`--project --committed`) — `<git-root>/<surface_dir>/<settings_filename>`
  (the shared, committed file)

Only **claude-code**, **codex**, and **opencode** ship a config profile. **Pi config is
DEFERRED** (see below) and the `agents` surface ships no config profile — both receive skills
and rules but no config alignment.

| Harness | Format | User (`$HOME`) | Project-local (`--project`) | Project-committed (`--project --committed`) |
|:--------|:-------|:---------------|:----------------------------|:--------------------------------------------|
| `claude-code` | JSON | `~/.claude/settings.json` | `<git-root>/.claude/settings.local.json` | `<git-root>/.claude/settings.json` |
| `codex` | TOML | `~/.codex/config.toml` | `<git-root>/.codex/config.toml` | `<git-root>/.codex/config.toml` |
| `opencode` | JSON | `~/.config/opencode/opencode.json` | `<git-root>/.config/opencode/opencode.json` | `<git-root>/.config/opencode/opencode.json` |
| `pi` | — | **deferred — no config file** | **deferred** | **deferred** |
| `agents` | — | no config profile | no config profile | no config profile |

`claude-code` is the only shipped profile whose `settings_local_filename`
(`settings.local.json`) differs from its `settings_filename` (`settings.json`), so its
project-local and project-committed scopes write **different** files. `codex` and `opencode`
carry the same filename in both fields, so their three scopes differ only by anchor
(`$HOME` vs git root), not by filename.

The config merge is **union-only and format-preserving**. Three guarantees:

- **Union-only** — it writes only the profile's own keys, and leaves any `bd setup` hook block
  untouched.
- **Trivia-preserving** — for `codex`'s TOML, it replays deltas through a trivia-preserving
  editor, so operator comments and key order survive.
- **Fail-safe** — a present-but-unparseable file is refused (reported, never overwritten).

### Rule managed-block target

The always-loaded rule text lands differently depending on how each harness reads its rules
(`yf/src/cmd/harness/managed_block.rs`):

| Harness | Rule target (user) | Rule target (project) | How it is placed |
|:--------|:-------------------|:----------------------|:-----------------|
| `claude-code` | `~/.claude/rules/` | `<git-root>/.claude/rules/` | Rules **directory** — the full `YOSHIKO_FLOW.md` aggregate (not a managed block in `AGENTS.md`) |
| `codex` | `~/.codex/AGENTS.md` | `<git-root>/.codex/AGENTS.md` | Managed `BEGIN`/`END` block in a shared `AGENTS.md` |
| `opencode` | `~/.config/opencode/AGENTS.md` | `<git-root>/.config/opencode/AGENTS.md` | Managed block in a shared `AGENTS.md` |
| `pi` | `~/.pi/agent/AGENTS.md` | `<git-root>/.pi/AGENTS.md` | Managed block — **verified default** (see below) |

- **claude-code** reads a rules **directory**, not an `AGENTS.md`. The full aggregate lands
  there; the minimized managed block is not separately placed for this harness.
- **codex / opencode** read a single always-loaded `AGENTS.md`. The minimized irreducible-core
  bundle is deployed there as a `BEGIN`/`END` **managed block** that shares the file with
  operator prose — it appends when absent, replaces only the marked span when present, is
  idempotent (a re-deploy of the same bundle is a byte-identical no-op), and **refuses** rather
  than corrupt a file with partial, duplicate, or out-of-order markers.
- **pi** uses the same non-clobbering managed-block engine. Its target
  `~/.pi/agent/AGENTS.md` (project `<git-root>/.pi/AGENTS.md`) is the **verified** default
  (checked against first-party pi docs, not a compiled-in guess), so `agents-md` is the
  default with no "unverified target" notice. The `--pi-rule-target {agents-md|append-system}`
  flag is the documented override — `append-system` retargets to
  `~/.pi/agent/APPEND_SYSTEM.md` for operators who prefer it.

### Pi config is deferred

**No `pi` config profile ships.** Pi's config surface was marked uncertain during
investigation, and baking a guessed surface into a released binary would be worse than
deferring — so a `pi` **config** tune returns a clean refusal while Pi's **skills** and
**rules** remain fully supported (its verified `~/.pi/agent/AGENTS.md` rule target above).
A follow-on tracks re-verifying the Pi config surface.

### An honesty note on surfaces

A config profile carries a **single `surface_dir`**, used at every scope. Where a harness's
real project-scope config directory differs from its user directory, `tune` writes to that
one `surface_dir` at both scopes rather than tracking a per-scope difference.

The consequence: a harness's config/rules directory is not always the same directory its skill
tree uses (skills land per the [install matrix](/install/#the-install-matrix-where-skills-land)):

| Harness | config/rules dir (`surface_dir`) | skills dir |
|:--------|:---------------------------------|:-----------|
| `opencode` | `.config/opencode` — both user and project scope | `.opencode` — project skills |
| `codex` | `.codex` | `.agents` |

The tables above state what the code actually writes: config and rules track the profile's
`surface_dir`, not always the directory the skill tree uses.

## The `.yf/` ownership manifest

Every tune records exactly what it wrote into a sidecar `.yf/harness-tune-manifest.json`, so a
later `--revert` can reverse it precisely without clobbering operator content. Per tuned
surface it captures:

- **config keys** yf added or forced — each with both the **prior** on-disk value (or none)
  and the **yf-written** value;
- **set unions** — for a set-valued key (e.g. `permissions.deny`), only the elements yf
  actually **added**, never the whole set;
- **rule block markers** — the rule file plus the `BEGIN`/`END` identifiers of the managed
  block (or `kind: "aggregate"` for claude-code's whole-file rules dir).

Location: **user scope** writes `<surface_dir>/.yf/harness-tune-manifest.json` beside each
tuned surface (e.g. `~/.codex/.yf/…`); **project scope** writes a single
`<git-root>/.yf/harness-tune-manifest.json` at the repo root and idempotently adds `.yf/` to
the project `.gitignore`. The manifest is **cumulative** — a re-tune folds fresh records in
(preserving the earliest-recorded prior, unioning set additions) rather than clobbering it — and
a **dry-run never writes a manifest**.

## Reversing a tune — `--revert`

`yf harness tune --revert` is driven **entirely** off the `.yf/` ownership manifest, never the
profile engine, and undoes **only** yf's own additions:

- **config keys** are reverted under a **touched-since-tune guard**: it compares the key's
  *current* on-disk value to the recorded `written` value. If they still match (untouched), it
  restores the recorded `prior` (or removes the key if there was none); if they differ (an
  operator hand-edited it since the tune), it **keeps the operator's value and reports** —
  never clobbering.
- **set unions** remove only the elements yf recorded as added, leaving every operator entry.
- **rule blocks** remove exactly the `BEGIN`..`END` managed span (preserving surrounding
  prose); an `aggregate` rule removes the yf-authored aggregate file.

Revert is **fail-safe** (a malformed target is refused, never corrupted) and **idempotent** (a
consumed surface is cleared, so a second `--revert` is a no-op). Because revert only ever
*removes* what yf added, the `Agent`-tool-never-denied invariant holds structurally.

## The install matrix, for reference

The companion command deploys skill trees. Its per-harness × scope destinations:

![yf harness skills install: where the embedded skill tree lands per harness and scope](/images/install-matrix.png)

See the [install page](/install/#the-install-matrix-where-skills-land) for the full skills
matrix, auto-detection behavior, and the bare-install first-run caveat.

> The tune destinations above are derived from the shipped config profiles
> (`yf/profiles/*.json`) and the rule-target map (`yf/src/cmd/harness/managed_block.rs`) — a
> doc↔code agreement test keeps this page in sync. This page reconciles the local web bead
> `yf-ij06` (per-harness deployment targets).
