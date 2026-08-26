---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #41: yf-owned _shared/: make yf the install-time vendoring engine (embed _shared/, fan into consumers)

- **Number:** 41
- **Title:** yf-owned _shared/: make yf the install-time vendoring engine (embed _shared/, fan into consumers)
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement

## Body

## Summary

Deferred architecture option (c) from plan-016 (#15) scoping. Move the canonical shared-helper source under **`yf` ownership**: embed `_shared/` in the `yf` binary (`#[folder = "../_shared"]` via RustEmbed, alongside the existing `skills/` embed) and extend `yf install` to fan the canonical bodies into each consumer skill's vendored regions at **install time** — making `yf` the vendoring engine instead of the repo-time `_shared/sync.py`.

## Why deferred (not in plan-016)

plan-016 ships the #15 helper consolidation on **option (a)** — extend the proven repo-time `_shared/` + `sync.py` vendoring (zero `yf` Rust change). That satisfies #15 now and honors the operator's yf-owned-asset preference at the **authority layer** (canonical lives in `_shared/`, outside the `skills/` embed root; per-skill copies are generated artifacts no human maintains).

This issue captures the operator's stronger, longer-term preference: content literally **owned by `yf`**, minimizing what lives in the harness-native `skills/` folders.

## Why this is the guardrail-safe route (vs a runtime asset)

A *runtime* yf-owned asset (skill scripts shelling out to `yf shared <helper>` to resolve a path at run time) is **structurally blocked**:
- breaks **independent installability** (GR-006) — a skill installed without `yf` on PATH would fail at runtime, with no offline fallback except vendoring a copy anyway;
- trips **GR-003** (`yf` is not a skill runtime).

Doing the fan-out at **install time** sidesteps both: the deployed copy is self-contained (runs without `yf`), and `yf` only participates in *installation*, not execution — exactly like it already deploys `skills/` today (`deploy_skill`, `yf/src/cmd/common.rs`).

## Sketch

- Add `#[derive(RustEmbed)] #[folder = "../_shared"]` (mirror `embed.rs` Skills).
- Extend `yf install`/upgrade to regenerate each consumer's marker-fenced region from the embedded canonical (the `sync.py` logic, in Rust).
- `sync.py --check` / DRIFT-CHECK edges remain the repo-time backstop; `yf` becomes the install-time enforcement.
- Decide whether `_shared/sync.py` stays as the repo-time authoring tool or is retired in favor of `yf`.

## Acceptance (when revisited)

- `_shared/` embedded in the `yf` binary; `yf install` fans canonical bodies into consumers.
- Independent installability preserved (a skill dir copied without `yf` still runs).
- Drift control at least as strong as today's `sync.py --check` + DRIFT-CHECK edges.

Spun out of #15 during plan-016 scoping. Sibling of #40 (PEP-723 route).
