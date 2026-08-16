---
type: Finding
okf_spec: OKF-PLAN
id: exp-005
plan: plan-041-james-dixson-a9d837
created: '2026-08-16'
status: complete
---

# E5 — Does `yf/profiles/` share the `skills/` addition blind spot?

Run during execution of **Issue 0.5**, which pass-3 concern **N3** required be *measured*
before the claim reached `SPEC.md` ("believed — not yet measured"; neither E2 nor E3 probed
it).

## Question

Issue 0.5 asserted, as incidental free coverage, that `yf/profiles/` — the **second**
`rust-embed` root (`yf/src/cmd/harness/profile.rs:26`, `#[folder = "profiles"]`, 3 JSON
files) — carries the same addition blind spot as `skills/`, and is fixed by the same
`cargo:rerun-if-changed=.` line.

## Method

Against the **pre-fix** `build.rs` (primary checkout, `main` at `754b5ed`, warm
`target/release`):

1. `cargo build --release -p yf` → establish a warm no-op baseline.
2. Add a **new** file `yf/profiles/zz-probe-plan041.json` carrying a unique marker.
3. `cargo build --release -p yf` → observe rebuild vs no-op.
4. `strings target/release/yf | grep <marker>` → did it reach the embedded payload?
5. Repeat the identical shape as a **control** against `skills/`
   (`skills/zz-probe-plan041/marker.txt`).

## Result — the claim is REFUTED

| Root | Rebuild on addition | Marker in binary | Blind spot? |
| :-- | --: | :-: | :-: |
| baseline (no change) | 0.27 s no-op | — | — |
| `yf/profiles/` | **6.74 s recompile** | **present** | **NO** |
| `skills/` (control) | **0.17 s no-op** | **absent** | **YES** |

`yf/profiles/` does **not** share the defect. The reason is structural and, in hindsight,
the same one that explains `skills/`: `yf/profiles/` sits **inside** the `yf/` package, so
cargo's **implicit whole-package watch** already observes additions there. `skills/` is
blind precisely *because it is outside the package*. The blind spot was never about
`rust-embed` roots in general — it is about roots cargo is not already watching.

The control also **re-confirms the plan's core premise** (E2) independently and supplies
the **RED baseline** Issue 1.2 must demonstrate against: a file newly added under `skills/`
is invisible to an incremental release rebuild.

## Consequence — the significance of D2's second line inverts

Issue 0.5 planned to record `rerun-if-changed=.` as *free new coverage* for `yf/profiles/`.
It is the opposite: emitting `../skills` **alone** would disable the implicit whole-package
watch and thereby **remove** coverage `yf/profiles/` has today. The `.` line **preserves**
it.

This strengthens D2 rather than weakening it — the second line is load-bearing on a second,
previously unnoticed axis — but it changes what the SPEC may claim, and it adds a
verification obligation: **Issue 1.4 must assert that a `yf/profiles/` addition still
propagates after the fix.** Without that assertion the regression is silent, since no
existing test covers the profiles embed root on the addition axis.

## Cost

Under two minutes, exactly as N3 estimated. Both probe artifacts were removed and the tree
restored (`git status` clean apart from plan-folder edits).
