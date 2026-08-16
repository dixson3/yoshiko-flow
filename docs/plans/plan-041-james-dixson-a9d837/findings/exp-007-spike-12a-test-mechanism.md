---
type: Finding
okf_spec: OKF-PLAN
id: exp-007
plan: plan-041-james-dixson-a9d837
created: '2026-08-16'
status: complete
---

# E7 — Issue 1.2a spike: the addition-propagation test mechanism

Pass-1 concern **C7** / risk **R5** flagged that Issue 1.2's test mechanism was unspecified
and non-trivial — a nested `cargo build` against a scratch crate, offline resolution, a
private target dir, tens of seconds — and that it is the plan's most load-bearing test,
since the Capability Gate keys on it. The spike had to decide **in-suite vs the pre-agreed
`scripts/` fallback** before Issue 1.2 was committed to.

## Verdict: IN-SUITE IS FEASIBLE — the fallback is not needed

A Rust integration test under `yf/tests/` can drive a nested scratch-crate build and
discriminate a working fix from a broken one, in **~4 s per build phase**.

## Mechanism, as validated

A scratch crate whose embed folder sits **outside the package**, mirroring `skills/`
relative to `yf/`:

```
<scratch>/assets/            <- the embed root, OUTSIDE the crate
<scratch>/cratedir/Cargo.toml   ([workspace] key: detaches from the parent workspace)
<scratch>/cratedir/build.rs     (the watch lines under test)
<scratch>/cratedir/src/main.rs  (#[folder = "../assets"], prints Assets::iter())
```

Driven with a **private `CARGO_TARGET_DIR`**, `--offline`, and the outer cargo's env
scrubbed (`RUSTC`, `RUSTC_WRAPPER`, `CARGO`, `RUSTFLAGS`, `CARGO_ENCODED_RUSTFLAGS`
removed).

## Two findings that change the test's design

### 1. The test MUST build `--release`. A debug build is vacuously green.

The first prototype ran in **debug** and reported the addition as propagating **even with
the pre-fix `build.rs`** — `a.txt, new.txt, red.txt` all present. That is not the fix
working; it is E3's asymmetry: `rust-embed` is declared without `debug-embed`, so a debug
binary resolves paths **from disk at runtime** and can never miss an addition.

This is exactly the **C13 trap** — a test green for a reason unrelated to the property under
test. Had Issue 1.2 been written without this spike, it would very plausibly have been
authored as a debug test, passed immediately, and guarded nothing.

### 2. The discrimination is clean once in release

| `build.rs` under test | Rebuild after addition | Marker in binary |
| :-- | --: | :-: |
| **pre-fix** (rustc-env only, no `rerun-if-changed`) | 0.043 s no-op | **ABSENT — RED** |
| **with fix** (`rerun-if-changed=../assets` + `.`) | 0.424 s | **PRESENT — GREEN** |

## Cost

| Phase | Time |
| :-- | --: |
| cold scratch build, release, `--offline` | 3.36 s |
| warm rebuild after an addition | 0.42 s |
| nested `cargo` invoked from **inside** `cargo test` (fresh target dir) | 3.00 s |

Nested cargo-from-cargo was verified explicitly (the outer test holds a lock on its own
target dir; a separate `CARGO_TARGET_DIR` avoids any contention) and exited 0.

`rust-embed` 8 is present in the local registry cache, so `--offline` resolves. On a cold
cache `--offline` would fail; the test should **skip with a clear message** rather than fail
when cargo is absent or offline resolution fails.

## Design consequence for Issue 1.2 — make RED a permanent assertion, not a one-time ritual

Pass-2 **C13** requires the test be *demonstrated* RED against the pre-fix `build.rs` before
being accepted green. The spike shows the scratch-crate design can do better: because the
scratch `build.rs` is written by the test itself, the test can assert **both arms on every
run** — build without the watch lines and assert the addition is **absent**, then build with
them and assert it is **present**.

That is strictly stronger than a one-time manual demonstration: it makes the guard
self-verifying forever, and it fails loudly if a future cargo change ever makes the pre-fix
form accidentally work.

**Residual, and how it is closed.** This test proves the *mechanism*; it does not by itself
prove `yf/build.rs` actually emits those lines — the scratch crate carries its own copy.
That coupling is **Issue 1.3's** job (assert the `"../skills"` literal in `build.rs` agrees
with `embed.rs`'s `#[folder]`). The two together are airtight; either alone is not. This
decomposition is recorded here because it is not obvious from Issue 1.2's text.
