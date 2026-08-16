---
type: Finding
okf_spec: OKF-PLAN
id: exp-002-force-reembed
plan: plan-041-james-dixson-a9d837
created: '2026-08-16'
---

# E2 — Cheapest reliable way to force a `skills/` re-embed

**Question.** Which mechanism should implement direction 2 (`--build` forces the
re-embed)?

**Answer.** None of them — because the measured root cause makes a `--build` wrapper the
wrong layer. Two lines in `build.rs` fix the defect for *everyone*, including plain
`cargo build --release` and CI, and the `--build` wrapper then needs **no change at all**.

Independently corroborates E3 on every overlapping point.

## The key insight: rust-embed emits no `rerun-if-changed`, and structurally cannot

Read from the macro source: `rust-embed-impl-8.11.0/src/lib.rs:279` emits
`const BYTES: &'static [u8] = include_bytes!(#full_canonical_path);` per file.
`grep -rn "rerun" rust-embed-impl-*/src/` returns **nothing**; neither does the README. No
feature (`debug-embed`, `include-exclude`, `compression`, `deterministic-timestamps`)
changes this.

rust-embed is a **proc macro** — build directives can only come from a build script, so it
cannot emit one. Its entire staleness story is rustc's `include_bytes!` dep-info, which
tracks **the content of files that existed at the last expansion** and never **the
directory listing**.

## There are TWO defects, not one

**Measured behaviour matrix (control, current tree):**

| `skills/` change | rebuild | embed fresh? | `build.rs` re-ran? |
| :-- | --: | :-: | :-: |
| edit existing file content | 4.99 / 6.89 / 12.70 s | **yes** | **no** |
| revert that edit | 6.00 s | yes | no |
| rename a file | 5.15 s | yes | no |
| delete a file | 4.79 s | yes | no |
| **add a new file** | **0.10 s** | **NO — stale** | no |
| **add a new skill dir** | **0.09 s** | **NO — stale** | no |
| touch any `yf/` file | 5.16 s | yes | yes |

1. **Embed staleness occurs only on ADDITION.** Content edits, deletes and renames all
   propagate — each has (or had) an `include_bytes!` dep-info entry. Corroborated twice:
   the marker appeared after a content edit and *disappeared* after reverting it, while the
   pure-add case no-op'd in 0.10 s.
2. **Version-stamp staleness occurs on EVERY skills-only change.** `build.rs` never
   re-runs (output mtime pinned at `1786908265` across a skills content edit that *did*
   recompile the crate), so `YF_GIT_HASH` / `YF_GIT_DIRTY` go stale even when the embed is
   fresh.

**This means the `5c747c0-dirty` vs `39b09f3` evidence quoted in `AGENTS.md` is about the
version stamp, not the embed.** `AGENTS.md`'s claim that a skills-only commit *"leaves both
the embedded tree and the version stamp stale"* is **half wrong**: version stamp always;
embedded tree only on addition.

## Mechanism comparison (measured)

Every row: warm target, a **new** file added under `skills/` — the only failing case.

| # | Mechanism | Works? | Rebuild (reps) | Steady-state no-op | Fixes stamp? |
| :-- | :-- | :-: | --: | --: | :-: |
| — | control (bare `cargo build --release`) | **NO** | 0.28 / 0.12 / 0.12 s | 0.10 s | no |
| a | `touch yf/src/embed.rs` (current workaround) | yes | 8.30 / 5.71 / 5.82 s | — | yes |
| b1 | `rerun-if-changed=../skills` + pkg watch + tree-hash `rustc-env` | yes | 5.65 / 5.93 / 6.15 s | 0.09 s | yes |
| **b1n** | **`rerun-if-changed=../skills` + `rerun-if-changed=.`** | **yes** | **5.82 / 5.82 s** | **0.10 s** | **yes** |
| b3 | `rerun-if-env-changed` + caller stamp | **NO** (regressive) | 0.10 / 0.10 s | 0.10 s | no |
| c | `cargo clean --release -p yf` first | yes | 8.40 / 8.15 / 6.43 s | **+6 s always** | yes |
| d | force-recompile "just the embed unit" | **N/A** | — | — | — |
| e | a rust-embed feature/attribute | **none exists** | — | — | — |
| f | `touch yf/build.rs` | yes | 6.97 / 6.18 / 6.29 s | — | yes |

- **(b3) is actively harmful.** Under `rerun-if-env-changed` only, `touch yf/src/main.rs`
  gave `buildrs_reran=no` — emitting it *also* suppresses cargo's implicit whole-package
  watch, silently regressing the dirty-flag accuracy REQ-YF-PRE-009 protects. Corroborated
  by the control in the same script giving `reran=yes` on the identical touch.
- **(d) is not a thing.** The crate is Rust's compilation unit; any "force the embed unit"
  reduces to (a).
- **(b1n) needs no stamp.** A `rustc-env` cache-buster was assumed load-bearing, measured
  otherwise: once the build script re-runs, cargo recompiles the dependent crate anyway, so
  b1's ~40-line FNV `skills_stamp()` walk is dead weight.

**b1n full coverage (measured):** `touch yf/Cargo.toml` 5.85 s reran=yes · `yf/tests/*.rs`
5.72 s yes · `yf/build.rs` 5.90 s yes · `yf/src/embed.rs` 5.67 s yes · skills content edit
5.80 s embed_fresh=1 yes · **new skill dir with nested `scripts/x.py` 5.84 s, both markers
embedded, yes** (proves the `../skills` watch is recursive) · debug ok ·
`cargo test --release` 4 passed 0 failed · no-op 0.10 s vs 0.10 s control — **no measurable
overhead**.

**Cost is not a discriminator.** Variance is high (the same content edit measured 4.99 s
and 12.70 s across runs); all working mechanisms sit within noise at ~5–8 s, dominated by
the unavoidable `yf` crate recompile. **Robustness is the discriminator.**

## Robustness ranking

1. **(b1n) — best.** Its only path literal is `"../skills"`, mirroring
   `#[folder = "../skills"]` in `embed.rs` — coupled to *the thing it must track*, not to a
   filename. It fixes the **default**, so plain `cargo build --release`, CI, a human, and
   `yf self install --build` all become correct: there is no step anyone can forget. Fixes
   the version-stamp half for free.
2. **(c) `cargo clean -p yf`.** No path hardcoding, but fixes only the
   `yf self install --build` path, costs an unconditional ~6 s, and leaves bare
   `cargo build --release` broken.
3. **(a) `touch yf/src/embed.rs` — the current documented workaround, and the weakest.**
   Hardcodes a filename with no reason to be stable. If `embed.rs` is renamed or the derive
   moves, the touch still *succeeds* (touch creates whatever is named), the build still
   exits 0, and staleness returns **silently**. It is also manual — the exact failure mode
   #137 documents.
4. **(f) `touch yf/build.rs`** — same hardcoded-filename class, marginally more stable
   name, same silent-failure profile.
5. **(b3)** — does not work and regresses the dirty flag.

## Recommendation

Two lines in `yf/build.rs`, replacing the "deliberately emit NO rerun-if-changed" block:

```rust
// The embedded `skills/` tree lives OUTSIDE this package. rust-embed is a proc
// macro and emits no rerun-if-changed of its own; its only staleness signal is
// `include_bytes!` dep-info, which tracks the CONTENT of files that existed at
// the last expansion but never the DIRECTORY LISTING. Result (#137): a file
// ADDED under skills/ is invisible to an incremental release rebuild.
println!("cargo:rerun-if-changed=../skills");
// Emitting ANY rerun-if-changed disables cargo's implicit whole-package watch,
// which REQ-YF-PRE-009 relies on for dirty-flag accuracy. Re-declare the package
// dir explicitly to preserve it (verified: src/, tests/, Cargo.toml, build.rs).
println!("cargo:rerun-if-changed=.");
```

Consequences:

- **`AGENTS.md` step 0 can be deleted outright**, not reworded.
- **Correct the "why" prose** — it asserts an over-broad claim and cites version-stamp
  evidence for an embed defect. Both halves are fixed by this patch; the wording should not
  survive it.
- **Optional cheap guard:** a unit test asserting the `"../skills"` literal appears in both
  `build.rs` and `embed.rs` (or hoist it to a shared `const`), so a future folder move
  cannot silently desync the watch from the embed.
- **The `--build` wrapper needs no change.** Do not also add `cargo clean -p yf` — ~6 s per
  invocation for no additional correctness.

## Housekeeping

Two early commands ran in the main checkout by mistake; the source edit was reverted and
`target/` rebuilt. Verified independently afterwards: `git status --porcelain` in the main
checkout shows only the untracked plan folder, and `git diff HEAD -- yf/` is empty.
