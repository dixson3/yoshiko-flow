# Finding EXP-003: Self-update mechanism, install-source detection, installer design

**Status:** complete · **Date:** 2026-06-30

> **CORRECTION (pass-1/2 red-team, verified vs v0.3.2):** (1) assets are **`.tar.xz`**; the plan
> flips `unix-archive` to **`.tar.gz`** (Issue 1.2) so `yf self update` extracts with pure-Rust
> `flate2`+`tar` (Issue 3.4a) — no system `tar`/`xz` dependency. (2) The receipt is cargo-dist's
> fixed **`~/.config/yf/yf-receipt.json`** (fields
> `install_prefix`/`install_layout`/`provider`/`source`(repo-descriptor)/`version`/...), NOT the
> `{schema,source,version,install_path,...}` schema proposed here; `source` is a repo descriptor,
> not an install classifier. Vendor detection keys on the canonicalized **`install_prefix`** path,
> not a receipt `source` field (Issues 3.1/3.3). See plan.md pass-1 corrections + `reviews/pass-1.md`.

## Question

Design the four-part vendor-install story: (1) self-update in Rust, (2) install-source
detection (refuse on Homebrew), (3) upgrade-detection UX, (4) the `curl|sh` installer, plus
(5) `yf self install --from-build`.

## Headline — the pivotal fork

cargo-dist already ships **both** a shell installer **and** a first-party self-updater crate
(**axoupdater**) that reads its install receipt + `dist-manifest.json`. So the real decision
is **adopt-cargo-dist-native vs hand-rolled-minimal**:

- **axoupdater (native):** least code, but pulls `reqwest`/`tokio`/`h2` → **large binary**,
  conflicts with the project guardrail **GR-011 (small self-contained binary)**.
- **hand-rolled-minimal (recommended):** `ureq` (rustls, blocking) + `self-replace` (+ tar/gz
  or shell `tar`) → small footprint, full control, the uv-like feel. ~15-line GitHub lookup.

## Findings

- **F1:** cargo-dist v0.32.0 emits per-target `yf-<triple>.tar.gz` + `.sha256` + a structured
  `dist-manifest.json` per release; its shell installer is configurable and writes an install
  **receipt** (the canonical source-detection / self-update hook).
- **F2:** `~/.yf/` is already used as a **project-local** state dir (git-root anchor). The
  vendor home `$HOME/.yf/` is a **different anchor** (no collision) but the reused name needs
  a doc note.
- **F3:** no HTTP/TLS/archive dep today (`anyhow, clap, rust-embed, serde, serde_json, sha2`);
  `sha2`+`serde_json` reusable.
- **F4:** cargo-dist default install path is `~/.cargo/bin`, **not** `~/.yf/bin` — fixable via
  `install-path = "~/.yf/bin"` in `[workspace.metadata.dist]` (+ regenerate), a plan task.
- **F5:** Homebrew is live (`/opt/homebrew/Cellar/yf/...` symlinked from `/opt/homebrew/bin/yf`);
  source-detection refusal is **load-bearing from day one**.

## Recommended design (hand-rolled-minimal)

**Deps (new, scoped to the `self` feature):** `ureq` (rustls), `self-replace`; tar/gz via
`tar`+`flate2` **or** shell out to system `tar` (O3).

**Q1 — `yf self update [--check] [--force] [--json]`:**
1. `canonicalize(current_exe())`.
2. Latest version: **primary** = `releases/latest` redirect → parse `Location` tag (no API
   rate limit); **fallback** = Releases API with a required `User-Agent: yf/<ver>` (60/hr,
   no token for public repo).
3. Host triple from `env::consts::{OS,ARCH}` → `yf-<triple>.tar.gz` (prefer reading the asset
   list from `dist-manifest.json` over hardcoding).
4. Download tarball + checksum **into the install dir** (same-fs atomic rename).
5. Verify SHA256 (`sha2`) before touching anything; mismatch → abort, binary untouched.
6. Extract → `yf.new`, `chmod 755`, `fsync` file+dir.
7. `self-replace::self_replace("yf.new")` (rename-over-running-binary is legal on Unix).
8. Print old→new; handle already-latest / offline / perms cleanly.

**Q2 — install-source detection (`classify_source(exe, home, receipt)`, pure/testable):**
1. canonicalized path contains a Cellar segment (`/opt/homebrew/Cellar`, `/usr/local/Cellar`,
   `/home/linuxbrew/.linuxbrew/Cellar`) → **Homebrew → REFUSE** (canonicalize first; the
   `bin/yf` symlink resolves into the Cellar).
2. under `$HOME/.yf/bin/` + receipt `source="vendor"` → **Vendor → PROCEED**.
3. receipt `source="from-build"` or under `target/{release,debug}/` → **FromBuild** (no nag;
   `--force` allowed).
4. else → **Unknown → REFUSE** with guidance.

Homebrew refusal points at `brew upgrade dixson3/tap/yf`, exits non-zero (the throttled
*detection* path never errors).

**Receipt** `$HOME/.yf/state/install-receipt.json`: `{schema, source, version, install_path,
target, installed_at, installer}` — written by the installer and by `--from-build`.

**Q3 — upgrade detection UX:** notify-only, on `yf version`/`yf doctor` only (never `--json`,
`preflight`, or CI); throttle once/24h via `$HOME/.yf/state/update-check.json`; **fail-open**
(swallow all errors, ~1-2s timeout, after the command's real output, stderr); **vendor-only**
(no nag for Homebrew/FromBuild); opt-out `YF_NO_UPDATE_CHECK=1` + skip if `CI`.

**Q4 — installer.** Two sub-options:
- **A (less surface):** configure cargo-dist's generated `yf-installer.sh` via
  `install-path = "~/.yf/bin"` — inherits platform detection/checksum/extract/PATH/receipt.
  **Needs O2 confirmation** that 0.32.0 honors `~/.yf/bin` + writes a receipt yf can read.
- **B (full control / literal ask):** bespoke POSIX `sh` installer. `~/.yf/{bin,state}`,
  uname→triple map, `releases/latest` redirect (or `YF_VERSION`), checksum via
  `shasum -a 256`/`sha256sum`, atomic `mv` into `~/.yf/bin/yf`, write receipt,
  **sentinel-guarded idempotent PATH block** (zsh→`~/.zshrc`, bash→`~/.bashrc`, fish→conf.d,
  unknown→print), `YF_NO_MODIFY_PATH`/`YF_HOME`/`YF_VERSION` env. Prior art: rustup
  `rustup-init.sh`, uv `install.sh`.
  Plus `yf self uninstall` (remove `~/.yf/`, strip the sentinel block; leaves `~/.claude/skills`
  to `yf skills remove`).

**Q5 — `yf self install --from-build [--release|--debug] [--build] [--force]`:** copy
`./target/release/yf` (resolved from workspace root) to `~/.yf/bin/yf` atomically; error if
artifact missing unless `--build`; write receipt `source="from-build"` (suppresses nag);
`yf self update --force` round-trips back to a published release (rewrites receipt to vendor).

## Implications for the plan

1. **Decide the fork** (axoupdater vs hand-rolled-minimal) — pivotal, currently implicit.
2. New deps on the hand-rolled path (`ureq`, `self-replace`, tar/gz) — scoped GR-011 exception.
3. New CLI: `Command::SelfCmd` (clap `#[command(name = "self")]`; `self` is a keyword) with
   `update`/`install`/`uninstall`, `--json` convention.
4. New state under `$HOME/.yf/state/` — define receipt + update-check schemas (installer↔binary
   contract); document home-vs-project `~/.yf` distinction.
5. `install-path = "~/.yf/bin"` in dist metadata + `dist generate` (regenerate `release.yml`).
6. Re-sequence docs/README: curl|sh primary, brew secondary (#54 partial); refusal keeps brew safe.
7. Pure/testable seams (`classify_source`, `triple_for_host`, `asset_name`) per `dest.rs` style.

## Open questions (carried to PLAN)

- **O1** axoupdater vs minimal — binary size (GR-011) vs maintenance. _Owner decision._
- **O2** does cargo-dist 0.32 honor `install-path=~/.yf/bin` + emit a receipt yf can read?
  (Determines installer Option A vs B.) Needs a `dist generate` dry run.
- **O3** tar extraction: `tar`+`flate2` crates vs shell-out to system `tar`.
- **O4** `releases/latest` redirect + stable `dist-manifest.json` asset URL reliability.
- **O5** Windows out of scope (Unix-only matrix); `self-replace` covers it but no `install.ps1`.
- **O6** installer installs **only** `yf` (bd/uv provisioned out-of-band, per the formula's
  dropped `depends_on`) — confirm no bootstrap expected.
