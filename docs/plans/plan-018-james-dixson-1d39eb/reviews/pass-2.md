# Review pass-2 — plan-018

**Reviewer:** red-team (adversarial, 2nd cycle) · **Date:** 2026-06-30 · **Plan status at review:** review

## Verdict: REVISE

Pass-1's three HIGH/MEDIUM concerns about the *actual* cargo-dist output are now genuinely
resolved — verified directly against the live v0.3.2 release and installer (receipt schema,
`.tar.xz` assets, `INSTALL_UPDATER=1` receipt gating, `_updater_name=""`). The remaining objections
concentrate in the newly-reviewed **Issue 3.7**, plus an under-stated Linux dependency in 3.4a with
a cleaner unconsidered fix. All localized — REVISE, not INVESTIGATE-MORE.

## Verification of pass-1 resolutions
- **C1 (`.tar.xz`; extraction) — GENUINELY RESOLVED** (live `gh release view v0.3.2` confirms
  `.tar.xz` + `.sha256` + manifest; 3.4a owns extraction). See Concern A on codec choice.
- **C2 (receipt schema/filename) — GENUINELY RESOLVED.** Downloaded `yf-installer.sh` emits exactly
  the schema 3.1 names to `~/.config/yf/yf-receipt.json`; `source` is a repo descriptor. 3.1/3.3
  key vendor on `install_prefix`, path-primary.
- **C3 (axoupdater framing / `INSTALL_UPDATER`) — GENUINELY RESOLVED.** `_updater_name=""` on all
  arches; receipt written only inside `if [ "$INSTALL_UPDATER" = "1" ]` (default 1). 1.3 check is
  real/testable; 3.1 path-primary fallback survives a missing receipt.
- **C4 (forcing the test path) — RESOLVED.** 3.4 acceptance mandates forcing.
- **C5 (`install-path` unconfirmed) — RESOLVED (deferred to 1.1).** Current installer has no
  `install-path` → cargo-home layout; setting `~/.local/bin` yields a flat layout where
  `install_prefix == ~/.local/bin`. 1.1 confirms flat-vs-hierarchical (Concern D).
- **C6 (sequencing 1.3↔3.1 + manifest selection) — RESOLVED.** 3.1 `depends-on 1.1`; 3.4 specifies
  `executable-zip`/artifact selection; false "Epic-1 writes Epic-3 schema" claim gone.

## Strengths
- Pass-1's factual corrections applied accurately and verifiably (receipt schema byte-for-byte).
- Architecture remains low-risk: production untouched, consumer-side unit-testable.
- `classify_source` path-primary-with-receipt-corroboration survives a missing/`INSTALL_UPDATER=0`
  receipt; custom `install-path` still classifies vendor via the receipt; absent receipt + non-default
  dir → `unknown → refuse` (fail-safe).

## Concerns
**A. [MEDIUM] 3.4a system `tar` for `.tar.xz` is conditionally broken on Linux; cleaner fix unconsidered.**
macOS `tar` (libarchive+liblzma) reads `.xz`; **GNU tar (Linux default) shells to the `xz` binary**,
absent on minimal/Alpine/container hosts → failure. *Recommendation:* set **`unix-archive = ".tar.gz"`**
in the dist config Epic 1 already edits → consumer uses pure-Rust `flate2`, no system-tar/xz dep at
all. Raise the flip as the recommended option.

**B. [MEDIUM] 3.7 re-exec target unspecified; `current_exe()` after `self-replace` is the OLD binary.**
`self-replace` renames the running exe aside, then moves the new binary into the canonical path. So
`current_exe()` resolves to the moved-aside OLD binary → a naive re-exec deploys OLD embedded skills,
silently defeating 3.7. *Recommendation:* exec the **swap-destination path** (`install_prefix`/`bin_dir`
+ `yf`), never `current_exe()`; acceptance asserts refreshed skills carry the NEW embedded version.

**C. [MEDIUM] `yf skills upgrade --scope user` covers ONE surface and deploys the full catalog.**
`--surface` is single-valued (default Claude); `upgrade` deploys the resolved default selection, not
"installed only." So 3.7's literal command refreshes only `~/.claude`, contradicting the success
criterion's `~/.claude`+`~/.agents`, and can re-add deliberately-removed skills. *Recommendation:*
detect present surfaces and invoke once per surface; document the full-catalog semantics + `--binary-only`
escape.

**D. [LOW] 3.3's hardcoded `~/.local/bin` constant coupled to an unconfirmed layout.** Derive the
vendor-prefix from 1.1's confirmed `install_prefix`; prefer the receipt's `install_prefix` over a literal.

**E. [LOW] Symlinked `~/.local/bin` → false-refuse.** 3.3 canonicalizes `current_exe()` but not the
receipt `install_prefix`. *Recommendation:* canonicalize both sides; add a symlink unit test.

**F. [LOW] Dual-install PATH-shadow UX.** No misclassification (keys on `current_exe()`), but a brew
copy earlier on PATH can shadow the updated vendor copy → "updated but nothing changed."
*Recommendation:* warn on successful vendor update if another `yf` shadows it earlier on PATH.

## Missing
- 3.4a did not consider `unix-archive=.tar.gz` (Concern A) — the single edit that removes the xz question.
- 3.7 lacked an acceptance proving the NEW binary ran (Concern B) and surface-iteration (Concern C).
- No note that from-build (3.5) deliberately does not refresh skills.

## Gate Assessment
Unchanged and appropriate. `dist-toolchain` (human, `dist --version == 0.32.0`) genuinely needed; Start
(human) + Reconcile (auto) correctly scoped; 1.1 is the right home for the `dist plan` confirmations.

## Upstream Assessment
Unchanged and correct. #55 include / #54 partial (wired to 5.1) / #41,#40 exclude on a defensible axis.
Consistent with AGENTS.md coarse-granularity + one-coarse-issue precedent. No disposition changes.

## Operator Resolutions
| # | Concern | Severity | Resolution | Status |
|:--|:--------|:---------|:-----------|:-------|
| A | xz/system-tar Linux-fragile | medium | **Adopted `unix-archive=.tar.gz` flip in 1.2**; 3.4a rewritten to pure-Rust `flate2`+`tar` (no system tar/xz dep); 3.4 selects `.tar.gz`; test forces against a `.tar.gz` release (not v0.3.2); GR-011 risk row + corrections block updated | resolved |
| B | 3.7 re-exec runs OLD binary | medium | **3.7 now execs the swap-destination path** (`bin_dir`/`install_prefix`+`yf`), never `current_exe()`; acceptance asserts refreshed skills carry the NEW embedded version | resolved |
| C | single-surface / full-catalog refresh | medium | **3.7 iterates present surfaces** (`--surface claude`/`agents` once each); full-catalog semantics + `--binary-only` escape documented; success criterion updated to "per present surface" | resolved |
| D | hardcoded `~/.local/bin` constant | low | 3.3 derives vendor-prefix from the receipt's `install_prefix` (+ 1.1-confirmed layout), preferred over a literal | resolved |
| E | symlinked `~/.local/bin` false-refuse | low | 3.3 canonicalizes **both** sides before the prefix test; symlink unit test added | resolved |
| F | PATH-shadow UX | low | 3.4 warns on successful vendor update if another `yf` shadows it earlier on PATH | resolved |
| — | from-build no auto-refresh note | — | Stated explicitly in 3.7 | resolved |

**Disposition:** all pass-2 concerns addressed in plan v3 (this revision). Pass-1 concerns
independently re-verified RESOLVED against live artifacts. Re-presented for operator approval.
