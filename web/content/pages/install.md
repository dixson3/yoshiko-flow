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
yf skills install                                    # all skills + companion rules
yf skills install --group utility                    # only the beads-free utility skills
yf skills install --group beads                      # only the beads-dependent skills
yf skills install yf-plan yf-research                # named skills (pull their deps)
yf skills install --scope project --surface agents   # <git-root>/.agents/{skills,rules}/
yf skills install --dry-run                          # preview without writing
```

By default this installs into the **user / claude** surface (`~/.claude/skills/`), with
companion rules in the sibling `~/.claude/rules/`. Groups are computed from each skill's
`skill-group` frontmatter (`beads`, `utility`, `markdown`). A missing `depends-on-tool` is a
warning and the install still proceeds (skill files are inert until the tool is present);
`--strict` makes it a hard failure. An existing companion rule is **preserved** unless
`--force` is given, so hand-edits survive a reinstall.

## Verify the install

```bash
yf doctor
```

`yf doctor` checks the environment (`bd` present and ≥ 1.1.0, `uv`, `git`) and every installed
skill's marker + companion rule, exiting non-zero if any axis fails. See [usage](/usage/) to
run your first skill, and [skills](/skills/) for the full catalog.
