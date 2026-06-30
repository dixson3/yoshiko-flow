# Plan: Move yf off Homebrew to a self-contained vendor-install model with upgrade detection and self-update (#55)

**ID:** plan-018-james-dixson-1d39eb
**Author:** james-dixson
**Created:** 2026-06-30
**Status:** reconciling
**Epic:** yf-mol-uiw
**Phase log:**
- 2026-06-30 scoping: initial scope captured
- 2026-06-30 scoping: 4 scope decisions captured (delivery, homebrew, location, platforms)
- 2026-06-30 investigating: 3 experiments identified (CLI/CI surface, release matrix, self-update mechanism)
- 2026-06-30 drafting: plan v1 synthesized (6 epics, dist-toolchain gate)
- 2026-06-30 review: plan v1 presented for review
- 2026-06-30 review: pass-2 red-team presented; v3 revisions applied (unix-archive→.tar.gz, 3.7 re-exec+surfaces, 3.3 canonicalize)
- 2026-06-30 approved: operator approved (after 2 red-team passes + portability audit)
- 2026-06-30 intake: epic yf-mol-uiw poured
- 2026-06-30 executing: start gate resolved
- 2026-06-30 reconciling: post-execution reconciliation

## Objective
Move yf off Homebrew to a self-contained vendor-install model with upgrade detection and self-update (#55)

## Motivation
`yf` ships today only through a Homebrew tap (`brew install dixson3/tap/yf`). That couples
install/upgrade to Homebrew's release cadence and Cellar layout, leaves no in-tool upgrade
signal (users must remember `brew upgrade`), and gives no first-class path to run a
locally-built copy during development on this repo. The operator wants a self-contained,
uv-style vendor install: download a prebuilt binary, get notified when a newer version
exists, and let `yf` update itself in place — with a clean dev path to install the local
`cargo build` output. This work is the prerequisite for #56 (embedded-mode beads repair):
fixing repair tooling is moot if operators can't easily get the fixed binary.

## Scope Decisions (operator, 2026-06-30)
| # | Decision | Choice | Implication |
|:--|:---------|:-------|:------------|
| 1 | Delivery mechanism | Prebuilt binaries + `curl\|sh` installer (uv model) | Release CI must build/upload per-platform assets; `yf self update` checks the GitHub Releases API and swaps the binary in place |
| 2 | Homebrew disposition | Keep tap as **secondary** (vendor primary) | Two release pipelines coexist; self-update must **detect install source** and never clobber a Cellar copy (direct brew users to `brew upgrade`) |
| 3 | Install location & dirs | **XDG**, not a self-contained `~/.yf` home (revised) | Binary → `~/.local/bin/yf`; config → `~/.config/yf`; cache → `~/.cache/yf`; data → `~/.local/share/yf`. Binary resolves these via one cross-platform dirs module (`etcetera`, XDG-on-Unix-and-macOS, honors `XDG_*`). `~/.yf` is NOT required. |
| 4 | Platform coverage | macOS (arm64 + x86_64) + Linux (x86_64 + aarch64) **now**; Windows **later** (planned, not built) | 4-target release matrix now; dirs module + installer-generation chosen so Windows can be added later (cargo-dist emits a `.ps1` installer for free; dirs module has a Windows arm, stubbed) |
| 5 | Installer build (revised) | **cargo-dist**, retargeted to `~/.local/bin` + XDG | XDG alignment removes the prior `~/.yf/bin` (O2) risk and the receipt "leak"; free Windows `.ps1` later; minimal code/maintenance. Bespoke considered and set aside once the self-contained `~/.yf` home was dropped as a requirement |
| 6 | Updater build | **Hand-rolled minimal** (`ureq` + `self-replace`), NOT axoupdater | Keeps the binary small (GR-011); reads cargo-dist's install receipt at the now-desired `~/.config/yf`. axoupdater's async stack (reqwest/tokio) is the wrong cost for a small synchronous binary — that dependency is ~free for uv only because uv already pays for async HTTP |
| 7 | On-disk content materialization (new) | Plan the **location + seam** now; build later | Today rust-embed content deploys only to `.claude/skills`/`.agents/skills`. Add a configurable materialization target defaulting to that, optionally `~/.local/share/yf/...`. Follow-on epic — design the dirs/knob now, implement separately |
| 8 | Post-update skills/rules refresh (new) | `yf self update` **re-deploys user-scoped skills/rules** as part of the update cycle | After the binary swap, the updater **re-execs the new binary** to run `yf skills upgrade --scope user` over present user-scope surfaces (`~/.claude/{skills,rules}`, `~/.agents/{skills,rules}`), so freshly-embedded skills/rules land with the new binary. **User-scope only** (global updater must not touch project installs). **Fail-soft** (swap already succeeded). Opt-out: `--binary-only` |

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| #55 | Upgrade detection and self-update (vendor install model) | include | Core objective of this plan | (this plan) |
| #54 | Level up getting-started documentation | partial | Install/getting-started docs need a vendor-install rewrite; broader docs effort stays separate | (install docs only) |
| #41 | yf-owned `_shared/` install-time vendoring engine | exclude | Different axis: vendoring of Python *skill helpers*, not the `yf` binary distribution | — |
| #40 | PEP-723 micro-package route for shared helpers | exclude | Same axis as #41; out of scope here | — |

## Investigation Findings

**Reframing discovery (EXP-001 + EXP-002):** the repo already ships a **cargo-dist (v0.32.0)**
release pipeline. It already builds prebuilt binaries for **exactly the 4 target platforms**,
emits per-asset sha256 checksums, uploads them to **GitHub Releases**, ships a `curl|sh`
shell installer, and auto-publishes the **Homebrew formula** to `dixson3/homebrew-tap`. So the
*production* half of #55 is largely already met — the plan's real surface is **consumer-side**.

> **pass-1+2 corrections (red-team, verified against live v0.3.2):** (1) current assets are
> **`.tar.xz`**, not `.tar.gz`; rather than carry an xz codec, the plan **flips `unix-archive` to
> `.tar.gz`** (1.2) so the consumer uses pure-Rust `flate2` and avoids the Linux GNU-tar-needs-`xz`
> landmine (3.4a, pass-2). (2) **No updater is published** (`_updater_name=""`); EXP-001's "bundled
> axoupdater / duelling updaters" framing is **wrong** and struck — we add the first updater.
> (3) cargo-dist writes its own fixed receipt `~/.config/yf/yf-receipt.json` (not the schema
> EXP-003 invented); vendor detection keys on the canonicalized `install_prefix` (Issues 3.1/3.3).

- **EXP-001** (`findings/exp-001-cli-release-surface.md`): `self` namespace is free/non-breaking;
  `yf skills upgrade` (skills) ≠ `yf self update` (binary). Version from `CARGO_PKG_VERSION`;
  no HTTP client in deps. `release.yml` is **generated — never hand-edit** (route via
  `[workspace.metadata.dist]` + `dist generate`). Gap vs #55: install path is `~/.cargo/bin`
  today (retargeted to `~/.local/bin` per decision 3). _(Struck per pass-1: no updater is published
  — there is no replace-vs-coexist / duelling-updater question.)_
- **EXP-002** (`findings/exp-002-release-matrix.md`): **keep cargo-dist** (don't hand-roll);
  conform to its manifest-driven asset selection (version-in-tag); skip musl + codesigning for v1;
  `curl|sh`-installed/`self update`-swapped macOS binaries are **not quarantined** (no Gatekeeper
  prompt). Retarget `install-path = ~/.local/bin` (decision 3) and flip `unix-archive = .tar.gz`
  (1.2). Open: confirm computed runners + glibc floor via `dist plan`.
- **EXP-003** (`findings/exp-003-self-update-installer.md`): designed `yf self update`
  (`ureq`+`self-replace`, releases/latest redirect → `dist-manifest.json` asset select →
  sha256 verify → atomic self-replace), install-source detection (`classify_source` — Cellar →
  refuse; vendor → proceed; from-build → no-nag), throttled fail-open upgrade-notification, and
  `yf self install --from-build`. Surfaced the pivotal **axoupdater vs hand-rolled-minimal**
  fork (resolved: hand-rolled, decision 6).

## Approach

**Keep cargo-dist as the build/release engine; own the consumer side natively.** cargo-dist
(v0.32.0, now named `dist`; actively maintained) already builds the 4-target binaries +
sha256 + `dist-manifest.json`, uploads them to GitHub Releases, and publishes the Homebrew
formula. We do **not** replace it. Instead we:

1. **Retarget** cargo-dist's generated `curl|sh` installer to an **XDG** layout (binary →
   `~/.local/bin`, config → `~/.config/yf`, cache → `~/.cache/yf`, data → `~/.local/share/yf`),
   keeping the Homebrew tap publish as a **secondary** path. XDG alignment removes the prior
   `~/.yf/bin` install-path risk and makes the install receipt land exactly where we want config.
2. Add a small cross-platform **dirs module** (`etcetera`; XDG on Unix+macOS, honors `XDG_*`,
   Windows arm stubbed) that every dir lookup routes through — the foundation for the receipt,
   the update-check cache, and the future on-disk materialization target.
3. Add a native **`yf self`** command (`update` / `install --from-build` / `uninstall`) using a
   **minimal** dependency set (`ureq` + `self-replace`) — NOT axoupdater — to keep the binary
   small (GR-011). `yf self update` does a Releases-API check + verified atomic in-place swap and
   **refuses on a Homebrew copy** (install-source detection), directing brew users to
   `brew upgrade`.
4. Add a **throttled, fail-open, vendor-only upgrade notification** on `yf version` / `yf doctor`.
5. **Re-sequence docs** (#54 partial): `curl|sh` primary, Homebrew secondary.
6. **Plan (not build)** the on-disk content-materialization seam + Windows: the dirs module
   carries the `~/.local/share/yf` data path and a `--target`/config knob is anticipated, but the
   full feature and Windows targets are follow-on epics.

Distribution stays low-risk: the production pipeline is unchanged and exercised; all new code is
consumer-side and testable against the **existing v0.3.2 release assets** without cutting a new
release.

## Epics

### Epic 1: cargo-dist installer retarget (XDG) + pipeline verification
- Issue 1.1: Install `dist` 0.32.0; run `dist plan` to capture the computed matrix, per-target
  runners, the `aarch64-unknown-linux-gnu` cross method, and the Linux **glibc floor** (resolve
  EXP-002 open questions). Record in `findings/`.
  - gated-by: Capability Gate `dist-toolchain`
- Issue 1.2: In `[workspace.metadata.dist]` set `install-path = "~/.local/bin"` **and**
  `unix-archive = ".tar.gz"` (flip from the current `.tar.xz` — pass-2 decision: lets the consumer
  use pure-Rust `flate2` and removes the Linux GNU-tar-needs-`xz`-userland landmine entirely);
  `dist generate`; review the `release.yml` diff for unintended drift. Confirm the regenerated
  assets are per-target **`yf-<triple>.tar.gz`** + **`.tar.gz.sha256`** + `dist-manifest.json`, and
  that the shell installer + Homebrew formula regenerate consistently for the new format. Note: the
  receipt schema is **not** configurable (1.3).
  - depends-on: 1.1
- Issue 1.3: Confirm the Homebrew publish job still fires (secondary intact); confirm the
  generated installer still writes cargo-dist's **own** receipt `~/.config/yf/yf-receipt.json`
  (fixed schema: `install_prefix`, `install_layout`, `provider`, `source`{repo-descriptor},
  `version`, `binaries`, `modify_path`). The receipt is emitted only when `INSTALL_UPDATER=1`
  (cargo-dist's default) — verify retargeting/`dist generate` does **not** disable it, even
  though we ship **no** cargo-dist updater. (No `yf-update` companion is published today —
  `_updater_name=""` on every arch — so there is no duelling-updater problem.) Defer the
  PowerShell installer (Windows later).
  - depends-on: 1.2

### Epic 2: cross-platform XDG dirs module (foundation)
- Issue 2.1: Add `etcetera` (or a thin resolver); implement a `dirs` module exposing
  `config_dir`/`cache_dir`/`data_dir`/`bin_dir`, XDG on Unix+macOS, honoring `XDG_*` overrides,
  with a stubbed Windows arm. Pure/testable (no real `$HOME`).
- Issue 2.2: Unit tests for path resolution + env overrides across Unix/macOS (and the stubbed
  Windows arm). Document the home-vs-project `~/.yf` distinction (project state stays git-root-anchored).

### Epic 3: `yf self` command surface + self-update + source detection
- Issue 3.1: **Receipt contract (corrected).** (a) Read cargo-dist's **actual**
  `~/.config/yf/yf-receipt.json` — fixed schema `{install_prefix, install_layout, provider,
  source(repo-descriptor object, NOT an install classifier), version, binaries, modify_path}`.
  Derive "vendor" from the canonicalized **`install_prefix`** path, NOT a `source` field (the
  invented `install-receipt.json` schema was wrong — see pass-1). (b) Define a **yf-authored**
  marker `~/.config/yf/yf-from-build.json` written ONLY by `--from-build` (3.5), the one receipt
  yf controls. Path-derived classification (3.3) is authoritative; receipts corroborate.
  - depends-on: 1.1, 2.1
- Issue 3.2: Add `Command::SelfCmd` (clap `#[command(name = "self")]`) with `update`,
  `install`, `uninstall`; wire `--json`. Help text distinguishes `yf self update` (binary) from
  `yf skills upgrade` (skills).
  - depends-on: 2.1
- Issue 3.3: `classify_source(exe, dirs, receipt)` pure fn — **path-primary** on canonicalized
  `current_exe()`: Cellar (`/opt/homebrew/Cellar`, `/usr/local/Cellar`, linuxbrew) → **refuse +
  `brew upgrade` guidance**; under the vendor prefix → vendor → proceed; yf from-build marker
  present (3.1b) → from-build → no-nag/`--force`; else → unknown → refuse. The vendor prefix is
  **derived from the receipt's `install_prefix`** (and the 1.1-confirmed layout), preferred over a
  hardcoded `~/.local/bin` literal (Concern D). **Canonicalize BOTH sides** — `current_exe()` and
  the receipt `install_prefix` — before the prefix test, so a symlinked `~/.local/bin` doesn't
  false-refuse (Concern E); add a symlinked-install-dir unit test. Receipts corroborate but the
  canonicalized path is authoritative (detection survives a missing/`INSTALL_UPDATER=0` receipt).
  - depends-on: 3.1
- Issue 3.4a: **Archive extraction (gzip + untar, pure-Rust).** Enabled by the `unix-archive =
  ".tar.gz"` flip (1.2): assets become `.tar.gz`, decoded with pure-Rust **`flate2`** + **`tar`**
  crates — small, no C, **no system `tar`/`xz` dependency** (avoids the GNU-tar-needs-`xz`-userland
  failure on minimal Linux/Alpine/container hosts). Extract, locate the inner `yf`, hand the path to
  3.4's verify+swap. (`yf self update` only ever pulls **latest**, so it never needs to read a
  pre-flip `.tar.xz` release.)
  - depends-on: 1.2, 2.1
- Issue 3.4: `yf self update [--check|--force|--json]` — `releases/latest` redirect → tag; select
  the host's `executable-zip` artifact (`yf-<triple>.tar.gz`) from `dist-manifest.json` (format-
  driven, not a hardcoded extension); download + sha256 verify (`sha2`) against the manifest
  checksum; **extract via 3.4a**; atomic `self-replace`. Handle already-latest / offline / perms
  cleanly. On a successful vendor update, **warn if another `yf` shadows the updated one earlier on
  PATH** (Concern F). New deps: `ureq` (rustls), `self-replace`. **Acceptance must force the path**
  against a release cut with the new `.tar.gz` config (a pre-release tag, or a local `.tar.gz`
  fixture + sub-version build / `--force` / `YF_VERSION`) so download→extract→verify→swap is
  actually exercised — NOT v0.3.2 (which is pre-flip `.tar.xz`).
  - depends-on: 3.2, 3.3, 3.4a
- Issue 3.5: `yf self install --from-build [--release|--debug] [--build] [--force]` — copy the
  workspace `target/release/yf` to `~/.local/bin/yf` atomically; write receipt `source=from-build`
  (suppresses nag); `yf self update --force` round-trips back to a vendor release.
  - depends-on: 3.2, 3.3
- Issue 3.6: `yf self uninstall` — remove the binary + yf-owned XDG dirs; report (never touches
  `~/.claude/skills`, which is `yf skills remove`'s job). Strip the installer's PATH block if present.
  - depends-on: 3.2
- Issue 3.7: **Post-update skills/rules refresh hook.** After a successful binary swap, refresh
  user-scope skills/rules from the new binary. Two correctness pins from pass-2:
  - **Exec the swap-DESTINATION path, not `current_exe()`** (Concern B): `self-replace` moves the
    running binary aside, so `current_exe()` resolves to the **old** binary — re-exec'ing it would
    deploy the OLD embedded skills and silently defeat the hook. Exec the known install target
    (`bin_dir`/`install_prefix` + `yf`, e.g. `~/.local/bin/yf`). **Acceptance asserts the refreshed
    skills carry the NEW binary's embedded version** (proves the new binary ran).
  - **Iterate present surfaces** (Concern C): `yf skills upgrade --scope user` is `--surface`-
    singular (default `claude`). Detect which user-scope surfaces actually exist and invoke once per
    present surface — `--surface claude` for `~/.claude/{skills,rules}`, `--surface agents` for
    `~/.agents/{skills,rules}`. Document that `upgrade` re-deploys the **default catalog** per
    surface (existing `skills upgrade` semantics — may re-add deliberately-removed skills);
    `--binary-only` is the escape hatch.
  - **User-scope only** (never project installs). **Fail-soft**: a refresh failure is reported with
    the exact re-run command and exits non-zero on the refresh only — never rolls back the
    (successful) swap. Refresh runs only on `self update`'s vendor swap; **from-build (3.5) does NOT
    auto-refresh** — a dev runs `yf skills upgrade` manually. Report the binary version delta + the
    surfaces/skills refreshed.
  - depends-on: 3.4

### Epic 4: upgrade-detection UX (notify-only)
- Issue 4.1: Throttled (24h) check on `yf version` / `yf doctor`; cache in `~/.cache/yf`
  (`update-check.json`); **fail-open** (~1-2s timeout, swallow errors, after real output, stderr);
  **vendor-only** (suppressed for Homebrew/from-build); opt-out `YF_NO_UPDATE_CHECK=1` + skip if `CI`.
  - depends-on: 2.1, 3.3, 3.4

### Epic 5: docs re-sequencing (#54 partial)
- Issue 5.1: Rewrite `README.md` + `website/docs/install.md`: `curl|sh` **primary**, Homebrew
  **secondary**; document `yf self {update,install,uninstall}`, the XDG dirs + env overrides
  (`XDG_*`, `YF_NO_UPDATE_CHECK`, `YF_VERSION`), the macOS browser-download `xattr` note, and uninstall.
  - depends-on: 1.3, 3.4, 4.1
  - resolves-upstream: #54 (partial)
- Issue 5.2: `CHANGELOG.md` `## Unreleased` entry for the vendor-install + self-update feature.
  - depends-on: 5.1

### Epic 6 (follow-on, NOT built in this plan): on-disk materialization seam + Windows
- Captured as deferred scope (decision 7 + Windows). The dirs module (Epic 2) already carries the
  `~/.local/share/yf` data path so this lands cleanly later. Filed as follow-on bead(s); not part
  of this plan's execution set. (Recorded so the seam is anticipated, not retrofitted.)

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: dist-toolchain
- Type: human
- Condition: `dist` (cargo-dist) 0.32.0 is installed and runnable
- Test: `dist --version` (expect `0.32.0`)
- Blocks: Issue 1.1 (and transitively 1.2/1.3)
- Instructions: install via `cargo install cargo-dist --version 0.32.0` or the upstream installer;
  the dist block in `Cargo.toml` is hand-maintained and pinned to 0.32.0, so match that version.

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: the reconcile step (update #55, #54 per dispositions)

## Risks & Mitigations
| Risk | Mitigation |
|:--|:--|
| Can't test `yf self update` end-to-end without a real release | Test against the **existing v0.3.2** release assets; unit-test the pure seams (`classify_source`, asset-select, verify); optionally a throwaway pre-release tag in a fork |
| `dist generate` rewrites `release.yml` with unintended drift | Review the diff carefully (1.2); the dist block is hand-maintained, so regeneration may surface pre-existing drift — reconcile deliberately |
| New deps (`ureq`, `self-replace`, `flate2`+`tar`) grow the binary vs GR-011 | Minimal pure-Rust crates, no async runtime; flipping `unix-archive` to `.tar.gz` (1.2) lets extraction use **pure-Rust `flate2`** — no C codec, no system `tar`/`xz` dependency (3.4a); feature-gate the `self` path if size regresses; deliberately-scoped exception (decision 6) |
| Symlinked `~/.local/bin` → false-refuse; brew copy shadows vendor on PATH | 3.3 canonicalizes **both** `current_exe()` and `install_prefix` before the prefix test (+ symlink unit test); 3.4 warns when another `yf` shadows the updated one earlier on PATH |
| Install-source misclassification via symlinks (brew `bin/yf` → Cellar) | `canonicalize` before prefix checks; unit tests for Cellar/vendor/from-build/unknown |
| macOS unsigned binary quarantine | `curl|sh`- and `self update`-written binaries are **not** quarantined; document the `xattr -d com.apple.quarantine` mitigation only for browser-downloaded archives; defer codesigning |
| Post-update skills refresh fails after the binary swap (3.7) | **Fail-soft**: the swap already succeeded; report the `skills upgrade` failure with the exact re-run command (`yf skills upgrade --scope user`) and exit non-zero on the refresh only — never undo the binary update. Re-exec the **new** binary so new embed + new upgrade logic apply |
| Linux glibc floor too high for some hosts | Verify via `dist plan` (1.1); `cargo-zigbuild` `target.2.17` pin is the lever if needed |

## Success Criteria
- `curl|sh` installs `yf` to `~/.local/bin`, sets PATH, writes the receipt to `~/.config/yf`; the
  Homebrew tap still installs a working `yf` (secondary).
- `yf self update` updates a vendor install in place (verified against a real/pre-release asset)
  and **refuses** on a Homebrew copy with `brew upgrade` guidance.
- `yf self install --from-build` promotes the local `cargo build` output and suppresses the nag.
- `yf self update` re-deploys user-scoped skills/rules **once per present surface** (`~/.claude`,
  `~/.agents`) by exec'ing the **new binary at the swap-destination path** (verified: refreshed
  skills carry the new embedded version); `--binary-only` skips it; from-build does not auto-refresh;
  a refresh failure is reported without rolling back the binary.
- `yf version` / `yf doctor` show a throttled, fail-open, vendor-only upgrade nudge; opt-out honored.
- yf resolves config/cache/data via the XDG dirs module with `XDG_*` overrides; Windows arm stubbed.
- Docs re-sequenced (curl|sh primary, brew secondary); #55 resolved, #54 partial.
- No async runtime pulled in; binary-size impact bounded.
