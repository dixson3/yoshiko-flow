# Finding EXP-001: Current yf CLI surface, version plumbing, and release CI

**Status:** complete · **Date:** 2026-06-30

> **CORRECTION (pass-1 red-team, verified vs v0.3.2):** this finding's claim that the installer
> "bundles axoupdater (a `yf-update` companion)" is **wrong** — no updater is published
> (`_updater_name=""` on every arch), so there is **no duelling-updater problem**. The receipt
> is `~/.config/yf/yf-receipt.json` (cargo-dist's fixed schema), emitted only when
> `INSTALL_UPDATER=1`. See plan.md pass-1 corrections + `reviews/pass-1.md`.

## Question

Map the current `yf` CLI command surface, version/release plumbing, and existing release
CI so plan-018 can add `yf self update` / `yf self install --from-build` plus a vendor
installer (uv-style, `~/.yf/bin`) without breaking what exists.

## Headline (reshapes the plan)

**The repo already ships a cargo-dist (v0.32.0) release pipeline** driven by
`[workspace.metadata.dist]` in the workspace `Cargo.toml`. It already:

- builds prebuilt binaries for **exactly plan-018's 4 targets** (`aarch64-apple-darwin`,
  `x86_64-apple-darwin`, `aarch64-unknown-linux-gnu`, `x86_64-unknown-linux-gnu`);
- uploads per-target tarballs + sha256 checksums to **GitHub Releases** (`gh release create`);
- ships a `curl|sh` **shell installer** that bundles **axoupdater** (a `yf-update` companion
  binary + an install receipt under `~/.config/yf`);
- auto-publishes the **Homebrew formula** to the separate tap `dixson3/homebrew-tap`.

So #55's "prebuilt binaries + curl|sh + self-update + secondary Homebrew" is **mostly
already present**. The plan shifts from *build it* to *retarget + own the UX*:

1. Install path is `~/.cargo/bin` today, not `~/.yf/bin` (cargo-dist `install-path` key, or
   a bespoke installer).
2. Self-update exists as a **separate `yf-update`/axoupdater**, not a native `yf self update`.
   Adding a bespoke one risks **two updaters fighting over the receipt** — must decide
   replace-vs-coexist.
3. `release.yml` is **generated** — never hand-edit; change `[workspace.metadata.dist]` +
   `dist generate`.

## Findings

### 1. `yf` subcommand tree (implemented)

Dispatch `yf/src/main.rs:48-64`; clap structs `yf/src/cli.rs:22-50`.

| Subcommand | Purpose |
|:--|:--|
| `skills {install,upgrade,remove,status}` | Manage **embedded** skills (not the binary) |
| `doctor` | Diagnose env + skill installs; `--repair` runs beads-init repair |
| `preflight <skill>` | Run a skill's preflight (owns exit code) |
| `migrate` | Migrate legacy `.state/` → `.yf/` |
| `version` | Print semver + git metadata (`--json`) |

No `self`/`update`/`upgrade` (binary) command exists — **`self` namespace is free,
non-breaking** to add (new `Command::Self` arm). `yf skills upgrade` operates on the
embedded skills tree (`cmd/status.rs:69-148`), distinct from a future `yf self update`.

### 2. Version & build metadata

- Source of truth: `yf/Cargo.toml` `version = "0.3.2"` → `CARGO_PKG_VERSION` (`main.rs:33`).
- `yf/build.rs` injects `YF_GIT_HASH` via `git rev-parse --short HEAD`, degrades to
  `"unknown"` (so a tarball build still compiles).
- `VERSION_LINE = "0.3.2 (ac0e2b8)"` (`main.rs:36`); `yf version [--json]` and clap `-V`.
- A version-availability check would compare local `VERSION` (`main.rs:33`) to the latest
  GitHub Release tag. **No HTTP client in deps** (`anyhow, clap, rust-embed, serde,
  serde_json, sha2`) — needs an HTTP crate or shell `curl`.

### 3. Release pipeline (`.github/workflows/release.yml`)

- **100% cargo-dist-generated** (v0.32.0). Driven by hand-authored
  `[workspace.metadata.dist]`. **Do not hand-edit** — regenerate via `dist generate`.
  (Note: `dist` is NOT installed on this machine; the dist block is hand-maintained.)
- Trigger: push of tag `vX.Y.Z`; PRs run in plan mode (no publish).
- 4-target build matrix == plan-018's 4 platforms. Produces per-target tarballs, sha256
  checksums, a shell installer, and a Homebrew formula (`installers = ["shell","homebrew"]`).
- **Uploads binaries to GitHub Releases: YES** (`dist host` → `gh release create <tag>
  artifacts/*`). Prebuilt binaries already land on Releases today.
- **Homebrew tap auto-updated:** `publish-homebrew-formula` job checks out
  `dixson3/homebrew-tap` (via `HOMEBREW_TAP_TOKEN`), drops the `.rb`, commits/pushes. Keeping
  Homebrew "secondary" = leave this intact.
- **Existing updater:** the generated `target/distrib/yf-installer.sh` sets
  `INSTALL_UPDATER=1` (unless `YF_DISABLE_UPDATE=1`), downloads a `yf-update` binary, and
  writes a receipt JSON to `${XDG_CONFIG_HOME:-~/.config}/yf` (`install_prefix`, `version`,
  source). **A self-update path already exists.**
- **Install path today:** `$CARGO_HOME/bin` (`~/.cargo/bin`), NOT `~/.yf/bin`. cargo-dist
  supports an `install-path = "~/.yf/bin"` key (not currently set).

### 4. Release process (manual, no script)

No release script. Manual: bump `yf/Cargo.toml` version → add dated `CHANGELOG.md` section
(rolls `## Unreleased`) → commit `release: yf vX.Y.Z — <summary>` → push `vX.Y.Z` tag →
`release.yml` fires. cargo-dist generates the GitHub Release notes from CHANGELOG.
Cargo.toml↔tag agreement enforced by convention.

### 5. rust-embed — skills baked in

`yf/src/embed.rs:30-35` derives `RustEmbed` over `../skills` (excludes `*.pyc`,
`__pycache__`). A prebuilt binary is fully self-contained — `yf skills install` works
offline. `yf self install --from-build` copying `./target/release/yf` carries the
then-current skills.

## Implications for the plan

1. `self` namespace free/non-breaking; keep `yf skills upgrade` vs `yf self update` distinct.
2. GitHub Releases already host prebuilt binaries for all 4 targets — **build matrix needs
   no change**.
3. **Decide replace-vs-coexist with axoupdater** (the main breakage risk: two updaters +
   receipt at `~/.config/yf`).
4. **Install-path conflict:** `~/.cargo/bin` (today) vs `~/.yf/bin` (#55). Either set
   cargo-dist `install-path` (+ regenerate) or ship a bespoke installer — don't mix (split-brain).
5. Homebrew stays secondary for free (tap publish already wired).
6. `yf self update` needs an HTTP fetch (add crate vs shell `curl`); GR-011 wants a small binary.
7. `release.yml` is generated — route changes through `[workspace.metadata.dist]`.
8. Release is manual — an optional net-new release helper could automate bump/changelog/tag.

## Open questions (carried to PLAN)

- **Coexist vs replace** cargo-dist's axoupdater (`yf-update` + `~/.config/yf` receipt)?
- **Reuse cargo-dist shell installer retargeted to `~/.yf/bin`** (less code, stays in
  generated pipeline) **vs bespoke uv-style installer** (full control, duplicates logic)?
- HTTP dependency choice for the version check / download (crate vs `curl`)?
- `yf self install --from-build` semantics: copy only, or `cargo build --release` first?
  Write/refresh the receipt so upgrade-detection doesn't nag a dev build?
- Want a release helper script to replace the manual bump/changelog/tag flow?

**Key files:** `yf/src/cli.rs`, `yf/src/main.rs:48-78`, `yf/build.rs`, `yf/src/embed.rs`,
`yf/src/cmd/status.rs:69-148`, `.github/workflows/release.yml` (generated),
workspace `Cargo.toml` `[workspace.metadata.dist]`, `CHANGELOG.md`,
`target/distrib/yf-installer.sh`.
