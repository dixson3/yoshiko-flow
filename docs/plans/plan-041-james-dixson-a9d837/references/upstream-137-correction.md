## Investigation correction — the root-cause analysis in this issue is partly wrong

Fixing this in `plan-041`. The measurements refuted parts of the analysis above, so recording
them here rather than closing the issue carrying a diagnosis we disproved.

### 1. There are TWO defects here, and the evidence quoted is for the other one

- **1a — embed staleness, on ADDITION only.** A file or directory *added* under `skills/` is
  invisible to an incremental release rebuild.
- **1b — version-stamp staleness, on EVERY skills-only change.** `build.rs` never re-runs, so
  `YF_GIT_HASH` / `YF_GIT_DIRTY` go stale even when the embedded tree is perfectly fresh.

The `5c747c0-dirty` vs `39b09f3` evidence cited for this issue (and in `AGENTS.md`) is an
instance of **1b, not 1a** — stamp evidence used to support an embed claim.

### 2. The defect is addition-scoped, not general

Measured on a warm `target/release`: **content edits, deletes and renames all propagate
correctly.** Only additions fail — a new file under `skills/` gave `Finished in 0.17s` with the
marker absent from the binary.

The mechanism explains why. `rust-embed` is a **proc macro**, so it structurally cannot emit
`cargo:rerun-if-changed` (`grep -rn "rerun" rust-embed-impl-*/src/` returns nothing). Its only
staleness signal is the `include_bytes!` dep-info it expands to, which tracks each embedded
file's **content** but never **the directory listing**. Cargo has no reason to re-expand the
macro when a *new path* appears.

### 3. Direction 1 as written would have caused a silent regression

The issue proposes adding `rerun-if-changed=../skills` *"in addition to the existing
no-narrowing behavior"*. **Cargo does not permit that** — emitting **any** `rerun-if-changed`
disables the implicit whole-package watch.

Measured: with only the `../skills` line, `touch yf/src/main.rs` left `build.rs` un-re-run —
staling `YF_GIT_DIRTY`, which `REQ-YF-PRE-009`'s first short-circuit consumes. The shipped fix is
therefore **two** lines:

```rust
println!("cargo:rerun-if-changed=../skills");
println!("cargo:rerun-if-changed=.");   // re-declares the package dir; NOT optional
```

A second, unnoticed consequence: `yf/profiles/` is a *second* `rust-embed` root. Because it sits
**inside** the `yf/` package it never had the addition blind spot (probed: 6.74 s recompile, new
profile present — vs a 0.17 s no-op with the marker absent for the `skills/` control). The `.`
line **preserves** that existing coverage; `../skills` alone would have silently removed it.

### 4. Per-file emission was tried and refuted

Emitting one `rerun-if-changed` per file (to mirror `embed.rs`'s `*.pyc` / `__pycache__`
excludes and avoid rebuilds on gitignored churn) **does not work**: a per-file watch list can
only name files that existed when `build.rs` last ran, so a newly added file is never watched.
Measured 0.13 s no-op, marker absent — the original bug, intact. A listing snapshot cannot
observe a change to the listing, which is the same reason the `include_bytes!` dep-info fails.

The directory watch is therefore deliberately broader than the embed. The price is a full
recompile on gitignored churn under `skills/` (measured 5.23 s per `uv`/pytest cycle); it is
eliminable from the other side with `PYTHONPYCACHEPREFIX` pointed outside the repo (measured back
to a no-op).

### 5. Scope of the fix — stated honestly

The stamp is now current for changes under **`yf/` and `skills/`**. Repo-wide `HEAD` movement (a
docs-only commit, a `SPEC.md` commit, a `git checkout`, a rebase) touches nothing watched and can
still leave a stale hash on an incremental build. Watching `.git/` was tried previously and
rejected. `yf --version` vs `HEAD` remains the only detector for that residue and is kept in
`AGENTS.md` for exactly that reason.

Also worth noting for anyone reaching for CI as the guard: **CI cannot catch this defect class.**
`actions/checkout@v4` + `Swatinem/rust-cache@v2` produce a clean build every run, and a clean
build cannot exhibit an incremental staleness bug. The guard is a dedicated
addition-propagation test (`yf/tests/embed_addition.rs`, `REQ-YF-EMBED-004`) that asserts both
arms — the addition must be **absent** without the watch lines and **present** with them — so it
can never be vacuously green.

### Direction 3 (fail-loud post-promote tree-hash comparison)

Declined for now. Nothing exists to reuse: `REQ-YF-MARK` compares *embedded ↔ deployed*, never
*embedded ↔ repo source*, so it would need a third file-list builder.
