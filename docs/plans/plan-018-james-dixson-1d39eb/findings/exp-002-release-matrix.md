# Finding EXP-002: Cross-platform prebuilt release matrix

**Status:** complete · **Date:** 2026-06-30

> **CORRECTION (pass-1/2 red-team, verified vs v0.3.2):** current assets are **`.tar.xz`**
> (+ `.tar.xz.sha256`), NOT `.tar.gz`. Rather than carry an xz codec, the plan **flips
> `unix-archive` to `.tar.gz`** (Issue 1.2) so the consumer decodes with pure-Rust `flate2` and
> avoids the Linux GNU-tar-needs-`xz`-userland failure (Issue 3.4a). Also `install-path = ~/.yf/bin`
> is superseded by the XDG decision (`~/.local/bin`). See `reviews/pass-1.md` + `reviews/pass-2.md`.

## Question

Lowest-friction, reliable way to build/publish prebuilt `yf` binaries for the four targets
(`aarch64-apple-darwin`, `x86_64-apple-darwin`, `x86_64-unknown-linux-gnu`,
`aarch64-unknown-linux-gnu`) from GitHub Actions, consumable by a `curl|sh` installer
(`~/.yf/bin`) and `yf self update`, while keeping the Homebrew tap working.

## Headline

**The production side is already done by cargo-dist.** `[workspace.metadata.dist]` already
declares all four targets, `checksum = "sha256"`, `installers = ["shell","homebrew"]`,
`tap = "dixson3/homebrew-tap"`, `publish-jobs = ["homebrew"]`. Releases through v0.3.2 were
cut via this pipeline. **Recommendation: keep cargo-dist; do not hand-roll a matrix.**

## Findings

### 1. Matrix already covers 4/4 targets
`release.yml` is cargo-dist-generated; the matrix is computed from `Cargo.toml` `targets`
(`matrix: ${{ fromJson(needs.plan.outputs.val).ci.github.artifacts_matrix }}`), which lists
exactly the four requested targets. No matrix work needed.

### 2. Cross-compile approach: keep cargo-dist
Only `aarch64-unknown-linux-gnu` needs real cross-compilation; cargo-dist already wires it.
Alternatives only relevant **if** cargo-dist were dropped: `cargo-zigbuild` (single Ubuntu
runner builds all 4, explicit glibc floor pin like `aarch64-unknown-linux-gnu.2.17`),
`taiki-e/upload-rust-binary-action`, or `cross`. All re-implement the
installer/checksum/homebrew wiring cargo-dist gives free → not recommended.
- **glibc floor:** build Linux on the oldest reasonable Ubuntu (GH retired 20.04; confirm
  the regenerated workflow lands on `ubuntu-22.04`/glibc 2.35). zigbuild's `target.2.17` is
  the lever if a lower floor is ever needed.
- **musl: not worth it** here — targets are scoped to glibc Linux; `yf` shells to
  `git`/`bd`/`uv` anyway, so static libc buys little.

### 3. `build.rs` git-hash in CI: works, one cosmetic gotcha
`release.yml` does a real `actions/checkout`, so `git rev-parse` succeeds and `YF_GIT_HASH`
populates. In a **containerized** cross build, missing `git` or git's `safe.directory`
guard makes it fall back to `"unknown"` — cosmetic only (the **version** for `yf self
update` comes from `CARGO_PKG_VERSION` / the release tag, never the hash). Optional fix:
`git config --global --add safe.directory '*'` or inject the hash via env.

### 4. rust-embed → one self-contained binary per target
`yf/src/embed.rs` bakes the whole `skills/` tree in at compile time. **Ship only the single
`yf` executable per target — no sidecar skill assets.** Each `yf-<target>.tar.gz` is standalone.

### 5. Asset conventions (installer/`self update` must conform)
- **Naming:** cargo-dist emits `yf-<target>.tar.gz` (version in the **release tag**, not the
  filename) → stable asset names for a `latest` lookup. Do NOT impose
  `yf-<version>-<target>.tar.gz` (would mean leaving cargo-dist).
- **Checksums:** per-asset `yf-<target>.tar.gz.sha256` (not a single `checksums.txt`).
  Verify before extract.
- **uname → target:** `Darwin/arm64→aarch64-apple-darwin`, `Darwin/x86_64→x86_64-apple-darwin`,
  `Linux/x86_64|amd64→x86_64-unknown-linux-gnu`, `Linux/aarch64|arm64→aarch64-unknown-linux-gnu`.
  Watch aliases (macOS `arm64` not `aarch64`; Linux `aarch64` not `arm64`). Else → from-source.
  cargo-dist's `yf-installer.sh` already encodes this table.
- **Discovery for `self update`:** `GET /repos/dixson3/yoshiko-flow/releases/latest`, compare
  `tag_name` (strip `v`) vs `CARGO_PKG_VERSION`, download matching asset + `.sha256`. Each
  release also has a structured `dist-manifest.json` — more robust than name-matching.
- **macOS Gatekeeper:** the quarantine xattr is applied by the *downloading app*, NOT by
  `curl`. A `curl|sh`-installed (and `self update`-swapped) binary is **not quarantined** →
  runs unsigned, no prompt (same as rustup/uv). Only **browser**-downloaded archives get
  quarantined (document `xattr -d com.apple.quarantine ~/.yf/bin/yf`). **No codesigning/
  notarization needed for v1**; cargo-dist can add it later without leaving cargo-dist.

## Recommended approach
1. Keep cargo-dist (matrix + checksums + shell installer + homebrew publish already wired;
   satisfies "Homebrew secondary" for free).
2. Install `dist` 0.32.0 once, run `dist plan`/`dist generate` to confirm the computed
   runners (esp. aarch64-linux cross + glibc floor) and prove `release.yml` ↔ manifest sync.
3. Point the installer + `yf self update` at cargo-dist's asset names; override install
   prefix to `~/.yf/bin` (cargo-dist `install-path` key).
4. Skip musl + codesigning for v1; document the `xattr` mitigation.
5. No self-containment work — rust-embed already handles it.

## Implications for the plan
- Scope Decision 1's "release CI builds/uploads assets" half is **already done**. Real
  effort is consumer-side: `~/.yf/bin` layout + PATH, `yf self update` (Releases-API check +
  verified in-place swap), `yf self install --from-build`, install-source detection
  (Decision 2). This dominates the estimate, not the builds.
- Conform to cargo-dist asset names; do not adopt a different scheme.
- Low risk — production pipeline is exercised; new code is consumer-side, testable without
  cutting a real release.

## Open questions (carried to PLAN)
1. Exact computed matrix / runners — needs `dist plan` on a machine with dist 0.32.0.
2. glibc floor of the regenerated pipeline (`ubuntu-22.04` = 2.35 acceptable?).
3. aarch64-linux build method in cargo-dist 0.32 (cross-gcc container vs zigbuild vs native arm).
4. `dist-manifest.json` vs asset-name matching for `yf self update` (design choice).
5. git-hash in containerized cross builds (cosmetic).
