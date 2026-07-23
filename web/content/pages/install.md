Title: install
Slug: install
Subtitle: get yf on your machine

`yf` is a single self-contained Rust binary — no runtime, no dependencies of its own. The
**vendor `curl | sh` installer** below is the recommended way in; other paths follow.

## Vendor install (curl | sh) — recommended

This runs the vendor installer (a mirror of cargo-dist's `yf-installer.sh`) via a short
bootstrap URL, drops the binary in `~/.local/bin`, adds that dir to `PATH`, and writes an
install receipt under `~/.config/yf` so `yf` can update itself later with
[`yf self update`](#keeping-yf-up-to-date):

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://yoshikoflow.sh/install.sh | sh
```

Then verify:

```bash
yf version
```

> The `yoshikoflow.sh/install.sh` bootstrap is a byte-for-byte mirror of the cargo-dist
> installer published on GitHub Releases — it in turn fetches sha256-checksummed release
> tarballs from GitHub. **GitHub Releases** remains canonical for every binary; the
> `yoshikoflow.sh` domain hosts only the convenience `install.sh`.

`yf` is distributed for `{darwin,linux} × {amd64,arm64}` with sha256 checksums.

## Prerequisites

**Installing `yf` does not install `bd` or `uv`.** `yf` is the installer/verifier kernel; the
skills it deploys depend on a small toolchain you install separately. `git` is assumed present.

| Tool  | Version   | Purpose                                            | Install |
|:------|:----------|:---------------------------------------------------|:--------|
| `bd`  | ≥ 1.1.0   | Task tracking (beads) — the beads-group skills     | `brew install beads` — <https://github.com/gastownhall/beads> |
| `uv`  | any       | Python env & script runner (skill helper scripts)  | `brew install uv` — <https://docs.astral.sh/uv/> |
| `git` | any       | Assumed already present                            | — |

Optional: `d2` for the `yf-diagram-authoring` skill (`brew install d2`); `pandoc` + `xelatex`
for `yf-markdown-pdf`.

## Keeping `yf` up to date

`yf` manages its **own** binary (distinct from `yf skills upgrade`, which manages the embedded
skills):

```bash
yf self update            # check GitHub Releases + swap the binary in place (vendor installs)
yf self update --check    # report whether a newer release exists; do not swap
yf self uninstall         # remove the binary + yf-owned dirs (installed skills untouched)
```

`yf version` / `yf doctor` show a throttled, vendor-only nudge when a newer release exists
(silence with `YF_NO_UPDATE_CHECK=1`). On macOS, `curl | sh`- and `self update`-installed
binaries are **not** quarantined.

## Alternatives

### Homebrew (macOS and Linux)

If you already live in Homebrew, the tap works too — upgrades come through `brew upgrade`
(a Homebrew install does **not** self-update via `yf self update`):

```bash
brew install dixson3/tap/yf
brew upgrade yf          # update later
```

The formula declares **no** runtime dependencies, so it does not pull in `bd` / `uv` — install
those separately (see [Prerequisites](#prerequisites)).

### Build from source

```bash
git clone https://github.com/dixson3/yoshiko-flow.git
cd yoshiko-flow
cargo build --release --manifest-path yf/Cargo.toml   # binary at yf/target/release/yf

# Optionally register this build as a from-build install on your PATH (~/.local/bin):
./yf/target/release/yf self install --from-build
```

A from-build install suppresses the upgrade nudge; `yf self update --force` switches back to a
vendor release.

### Which one should I use?

| Path | Self-updates in place | Best for |
|:-----|:----------------------|:---------|
| **Vendor install `curl \| sh`** | **yes** (`yf self update`) | **most people — fast install + in-place updates** |
| Homebrew | no (use `brew upgrade`) | macOS/Linux users already on Homebrew |
| From source | with `self install --from-build` | hacking on `yf` |

## Install the skills

`yf` embeds the whole skill tree, so a single command deploys them into your harness:

```bash
yf harness skills install                                    # all skills into every detected harness
yf harness skills install --tune                             # skills + always-loaded rules + config (first-run)
yf harness skills install --harness claude-code              # one specific harness
yf harness skills install --harness codex --harness pi       # repeatable — several harnesses at once
yf harness skills install --group workflows                  # yf-plan/research/incubator + the beads skills they need
yf harness skills install --group beads                      # only the beads support skills (yf-beads-*)
yf harness skills install --group utility                    # only the beads-free utility skills
yf harness skills install yf-plan yf-research                # named skills (pull their deps)
yf harness skills install --scope project --harness codex    # <git-root>/.agents/skills/
yf harness skills install --dry-run                          # preview without writing
```

> `yf harness skills install` is the **canonical** command. `yf skills install` is kept as a
> **deprecated alias** (it still works, including `yf skills install --tune`) and will be
> removed in the next major release — prefer the `yf harness` spelling.

Groups are computed from each skill's `skill-group` frontmatter (`workflows`, `beads`,
`utility`, `markdown`) — the valid `--group` names are the union of all skills' values, never
hardcoded. **Installing a skill or a group pulls its transitive `depends-on-skill` closure**, so
`--group workflows` also installs the `beads` skills those workflows depend on; an
unresolved/external dependency is logged, not fatal. A missing `depends-on-tool` is a warning and
the install still proceeds (skill files are inert until the tool is present); `--strict` makes it
a hard failure.

> **First run? Use `--tune`.** A **bare `yf harness skills install` (without `--tune`) deploys
> skill bodies only — no always-loaded rules — and is non-functional for the trigger-based engine
> skills.** `yf-change-validation`, `yf-drift-check`, `yf-markdown-lint`, and the
> `yf-beads-upstream` close-time push all fire from always-loaded rules, and those rules are
> deployed **only** by `yf harness tune`. Until tune runs, those skills are inert (their bodies
> are present but nothing triggers them). A bare install prints a warning and states that rules
> were **not** deployed. So on a fresh machine run `yf harness skills install --tune` (or run
> `yf harness tune` after a plain install).

### The install matrix — where skills land

Each harness resolves to a skills directory under a scope anchor: **user** scope anchors at
`$HOME` (`~`); **project** scope anchors at the **git root** (cwd fallback). The five shipped
harnesses and their resolved skills directories:

| `--harness` | User scope (anchor `$HOME`) | Project scope (anchor git root) | Skill-name transform |
|:------------|:----------------------------|:--------------------------------|:---------------------|
| `claude-code` (default) | `~/.claude/skills/` | `<git-root>/.claude/skills/` | — |
| `codex` | `~/.agents/skills/` | `<git-root>/.agents/skills/` | — |
| `opencode` | `~/.config/opencode/skills/` | `<git-root>/.opencode/skills/` | — |
| `pi` | `~/.pi/agent/skills/` | `<git-root>/.pi/skills/` | `lowercase-hyphen,max64` |
| `agents` | `~/.agents/skills/` | `<git-root>/.agents/skills/` | — |

Companion rules land in the sibling `rules/` directory of each skills dir (e.g.
`~/.claude/rules/` for `claude-code` user scope) — but only when `--tune` (or `yf harness tune`)
runs; see the first-run note above.

Notes on the matrix:

- **`--harness` is repeatable** — `--harness codex --harness pi` installs into both in one run.
- **`codex` and `agents` both resolve to `.agents/skills`.** When both are selected they
  **dedupe to a single write** — the tree is deployed once, not twice.
- **`pi` applies a `lowercase-hyphen,max64` transform** to each skill's on-disk directory name
  (lowercase, every non-`[a-z0-9]` character → `-`, truncated to 64 chars). The `yf-*` skill
  names are already lowercase-hyphenated and under 64 chars, so the transform is the identity on
  them; it only matters for names that would otherwise violate pi's constraint.

### Auto-detection (no `--harness`)

With **no `--harness`**, `yf` **auto-detects** which harnesses are installed and targets those:

- **User scope** — a harness is detected if its home directory is present **or** its binary is on
  `PATH` (either signal hits).
- **Project scope** — a harness is detected by the presence of its dot-directory in the git root.

Explicit `--harness` always overrides detection. Because an unattended multi-harness `--tune` run
writes config and rules, the no-`--harness --tune` auto path **prints the resolved target set and
requires confirmation (or a dry-run-then-apply)** before any write; `--dry-run` surfaces the
detected set without writing.

> The install-matrix paths above are derived from the shipped harness descriptor table and scope
> resolution in `yf` (`harness_desc.rs` / `dest.rs`) — a doc↔code agreement test keeps this page
> in sync. This section reconciles the local web bead `yf-8ayq` (recommended per-harness settings
> block).

## Verify the install

```bash
yf doctor
```

`yf doctor` checks the environment (`bd` present and ≥ 1.1.0, `uv`, `git`) and every installed
skill's marker + companion rule, exiting non-zero if any axis fails. See [usage](/usage/) to
run your first skill, and [skills](/skills/) for the full catalog.

## Tune Claude Code for the skills

The `yf-*` skills deliberately **replace** several Claude Code built-ins — and those built-ins
will happily usurp the skills if left on. `/yf-plan` overrides native plan mode; `bd` (beads) is
the only task tracker; state must stay portable, not trapped in a Claude-only store. The
skills' always-loaded rules *forbid* the native mechanisms, but prose only steers the model — it
still pays the tool-schema budget every turn. Disabling the competitors in `~/.claude/settings.json`
makes the safe state the default and reclaims that context.

The highest-impact settings, and the skill each one protects:

| Setting | Value | Why — what it would otherwise usurp |
|:--------|:------|:------------------------------------|
| `permissions.deny: ["EnterPlanMode", "ExitPlanMode"]` | — | Native plan mode; `/yf-plan` replaces it. A bare name in `deny` also drops the tool's schema from context. |
| `permissions.deny: ["TaskCreate", "TaskGet", "TaskList", "TaskOutput", "TaskUpdate"]` | — | The native task surface; `bd` (beads) is the only task tracker every skill uses. |
| `permissions.deny: ["EnterWorktree", "ExitWorktree"]` | — | The harness worktree primitive; `/yf-plan` manages its own persistent git worktree. |
| `todoFeatureEnabled` | `false` | `TodoWrite` — forbidden by every beads-backed skill; use `bd`. |
| `disableWorkflows` | `true` | Native workflows; skills fan out only via the `Agent` tool (which must stay **enabled**). |
| `autoMemoryEnabled` / `autoDreamEnabled` / `autoUploadSessions` | `false` | Claude-only memory/session stores; yf state lives in beads / repo files so it is cross-harness. |
| `disableBundledSkills` | `true` | Bundled skills whose descriptions can shadow the `yf-*` description triggers. |

> **Keep the `Agent` tool enabled** — every coordinator, investigator, and reviewer fans out
> through it. The denied `Task*` tools are a *different*, native background-task surface.

The full per-key rationale — including the `bypassPermissions` and `askUserQuestionTimeout`
tradeoffs and the bare-name-vs-scoped `deny` mechanics — is in
[`docs/recommended-settings.md`](https://github.com/dixson3/yoshiko-flow/blob/main/docs/recommended-settings.md).
