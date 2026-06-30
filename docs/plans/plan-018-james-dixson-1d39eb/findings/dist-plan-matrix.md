# Finding: `dist plan` matrix / runners / glibc floor (Issue 1.1)

**Date:** 2026-06-30
**Tool:** `dist` (cargo-dist) 0.32.0
**Command:** `dist plan --output-format=json` (run from the plan worktree)
**Resolves:** EXP-002 open questions (computed runners, aarch64-linux cross method, glibc floor, install layout)

## Release matrix (4 targets, all native runners)

| Target triple | CI runner | Build method | Notes |
|:--|:--|:--|:--|
| `aarch64-apple-darwin` | `macos-14` | native | Apple Silicon |
| `x86_64-apple-darwin` | `macos-15-intel` | native | Intel mac runner |
| `aarch64-unknown-linux-gnu` | `ubuntu-22.04-arm` | **native ARM runner** | NOT cross-compiled — no `cargo-zigbuild`, no QEMU |
| `x86_64-unknown-linux-gnu` | `ubuntu-22.04` | native | — |

**Key correction to EXP-002:** the `aarch64-unknown-linux-gnu` artifact is built on a
**native `ubuntu-22.04-arm` GitHub runner**, not via a cross toolchain. There is no
`cargo-zigbuild` / `target.2.17` glibc pin in play — the glibc floor is simply whatever the
runner ships.

## glibc floor

Both Linux targets build on **Ubuntu 22.04** runners → **glibc 2.35**. That is the effective
minimum-glibc floor for the published Linux binaries. Hosts older than glibc 2.35 (e.g. RHEL/
CentOS 7 = glibc 2.17, Ubuntu 20.04 = glibc 2.31) would need a lower floor. If that becomes a
requirement, the lever is `cargo-zigbuild` with a `target = ["...@2.17"]`-style pin (per the
plan's Risks table) — **not needed today** given the macOS-primary / modern-Linux audience.

## Current asset format (confirms pass-1 correction)

`dist plan` reports the executable-zip artifacts as **`.tar.xz`** today:

- `yf-aarch64-apple-darwin.tar.xz` (+ `.sha256`)
- `yf-x86_64-apple-darwin.tar.xz` (+ `.sha256`)
- `yf-aarch64-unknown-linux-gnu.tar.xz` (+ `.sha256`)
- `yf-x86_64-unknown-linux-gnu.tar.xz` (+ `.sha256`)
- `sha256.sum` (unified checksum), `source.tar.gz` (+ `.sha256`)
- installers: `yf-installer.sh` (shell), `yf.rb` (homebrew)

This is exactly the `.tar.xz` that Issue 1.2 flips to `.tar.gz` so the consumer (3.4a) can use
pure-Rust `flate2` and avoid the GNU-tar-needs-`xz` landmine.

## Install layout / `install_prefix`

cargo-dist's shell installer default is a **flat** layout writing the binary into the configured
`install-path` and emitting its receipt at `~/.config/<app>/<app>-receipt.json`. Issue 1.2 sets
`install-path = "~/.local/bin"`; the receipt's `install_prefix` is therefore the canonicalized
`~/.local/bin` (the value 3.1/3.3 key vendor-detection on). No hierarchical
`CARGO_DIST_FORCE_INSTALL_DIR`-style layout is in use.

## Downstream implications

- **1.2** flips `unix-archive` to `.tar.gz` and sets `install-path = ~/.local/bin`; re-run
  `dist generate` and diff `release.yml`. The matrix above should be unchanged by that flip
  (only the archive extension changes).
- **3.1/3.3** derive the vendor prefix from the receipt's canonicalized `install_prefix`
  (`~/.local/bin`), not a hardcoded literal.
- **3.4a** can rely on `.tar.gz` (post-1.2); `flate2`+`tar` decode it with no system `xz`.
- No glibc pin work required for 1.2/1.3.
