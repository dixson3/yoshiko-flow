---
type: Finding
okf_spec: OKF-PLAN
id: exp-006
plan: plan-041-james-dixson-a9d837
created: '2026-08-16'
status: complete
---

# E6 — Issue 1.5 spike: per-file vs directory `rerun-if-changed`

Pass-1 concern **C4** / risk **R2a** asked whether `build.rs` should emit **per-file**
`rerun-if-changed` lines mirroring `embed.rs`'s `#[exclude]` set, rather than a plain
`../skills` **directory** watch, so that `__pycache__`/`*.pyc` churn does not force a
spurious full recompile. The spike had to choose the form Issue 1.1 implements.

## Method

Both variants measured in the primary checkout against a warm `target/release`, each run
settled to a NOOP baseline first. Signal: `Compiling yf` in cargo output ⇒ `build.rs`
re-ran; otherwise a no-op.

- **Variant A** — `rerun-if-changed=../skills` + `rerun-if-changed=.` (the D2 form).
- **Variant B** — a `build.rs` walk of `skills/` emitting one `rerun-if-changed` per file,
  skipping `__pycache__` dirs and `*.pyc` files, + `rerun-if-changed=.`.

Six probes: `.pyc` touch; a new `__pycache__` dir; a **real** `uv run pytest` cycle; an
**addition** under `skills/` (with a binary marker check); `touch yf/src/main.rs` (the
dirty-flag guard); and an **addition** under `yf/profiles/` (the E5 regression guard).

## Results

| Probe | Variant A (directory) | Variant B (per-file) |
| :-- | :-- | :-- |
| baseline no-op | NOOP 0.20 s | NOOP 0.22 s |
| M2a touch existing `.pyc` | **REBUILT 5.51 s** | NOOP 0.13 s |
| M2b new `__pycache__` dir | **REBUILT 5.25 s** | NOOP 0.12 s |
| M2c real `uv run pytest` | **REBUILT 5.23 s** | NOOP 0.14 s |
| **M3 addition under `skills/`** | **REBUILT 5.07 s — marker PRESENT** | **NOOP 0.13 s — marker ABSENT** |
| M4 `touch yf/src/main.rs` | REBUILT 5.25 s | REBUILT 5.48 s |
| M5 addition under `yf/profiles/` | REBUILT 5.80 s — profile PRESENT | REBUILT 6.20 s — profile PRESENT |

## Verdict — Variant A selected; Variant B is REFUTED, not merely costlier

**Variant B fails M3: it does not fix #137 at all.** A per-file watch list can only name
files that existed *when `build.rs` last ran*. A **newly added** file was never emitted as a
watch, so cargo has no reason to re-run the build script — and it did not (0.13 s no-op,
marker absent from the binary). This is *structurally the same defect* as the one being
fixed: `rust-embed`'s `include_bytes!` dep-info is itself a per-file listing snapshot. A
listing snapshot cannot observe a change to the listing, whoever writes it.

That makes the choice not a trade-off. Variant B is cheaper on the churn axis **because** it
is blind on the addition axis — the cost it saves is the cost of correctness. Only the
directory watch satisfies `REQ-YF-EMBED-004`.

Both variants pass **M4** (dirty flag preserved, via the `.` line) and **M5** (the E5
`yf/profiles/` coverage is preserved rather than lost).

## The churn tax is real — and fully eliminable

R2a's worry is **confirmed** for the selected form: one real `uv run pytest` cycle costs a
**5.23 s** recompile where a 0.20 s no-op was expected, and this repo's always-loaded rules
run `uv`/pytest constantly.

`rerun-if-changed` has no exclude mechanism and cargo walks a watched directory
**recursively**, so the tax cannot be avoided from inside `build.rs` while keeping addition
coverage. It *can* be avoided from the other side — by keeping bytecode out of `skills/`
entirely. Measured:

```
purge skills/**/__pycache__, settle          -> NOOP
PYTHONPYCACHEPREFIX=<scratch> uv run pytest  -> NOOP        (272 .pyc files written OUTSIDE skills/)
```

With `PYTHONPYCACHEPREFIX` pointed outside the repo, a full pytest cycle leaves the build a
**no-op under Variant A** — the tax goes to zero with no loss of addition coverage.

Per **SC3**'s disjunction (pass-2 C12) this spike discharges the *documented* arm: Variant A
is selected and its tax is measured and recorded (in the `build.rs` comment and Issue 0.5's
amendment). **Wiring `PYTHONPYCACHEPREFIX` into the repo's `uv`/pytest invocations is left as
a follow-up** rather than taken here — it changes developer-environment behavior repo-wide,
which is outside this plan's "no behavior changes" boundary. A follow-up bead records it.
