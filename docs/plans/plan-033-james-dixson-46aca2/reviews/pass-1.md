---
type: Review
okf_spec: OKF-PLAN
---
# Review pass 1 — plan-033-james-dixson-46aca2

**Reviewer:** Red-Team (adversarial)
**Date:** 2026-07-22

## Verdict: REVISE

Approach is well-grounded in research-002 and the pre-declared REQ-YF-TUNE-011 seam; decomposition,
SPEC-first sequencing, REQ-id non-collision, and upstream mechanics all check out. One **high**
concern (TOML write-path framing) plus four medium/low should be resolved before approval. None are
approach-invalidating.

## Strengths

- **Seam is real, not retrofit.** Verified: `merge.rs` is genuinely pure over `serde_json::Value`
  (new `Value` + structured `MergeReport`, no I/O); REQ-YF-TUNE-011 (SPEC.md:622–626) pre-declares
  "a future harness … needs a *new engine*." The "merge.rs untouched" claim (R8, Epic 2) is credible.
- **REQ-id hygiene confirmed.** `REQ-YF-TUNE-012..021` absent from SPEC.md — no collision; existing
  ids stop at 011. SPEC-first is mechanically enforced via `depends-on: 1.1`.
- **Beads/upstream wiring correct.** `yf-8agh` + `yf-up7s` both depend on the closed `yf-2gyv`; #95
  correctly `related`; "no reconcile gate" call is right, matches AGENTS.md coarse precedent.
- **Diagram authored**; `toml`/`toml_edit` correctly classed as ordinary Cargo deps → "no capability
  gate" justified.
- **Pi honesty.** The `[uncertain]` tag is faithfully carried into R2 / Issue 3.3 / REQ-016.

## Concerns

| # | Severity | Concern | Recommendation |
|:--|:---------|:--------|:---------------|
| C1 | high | Epic 2 / Issue 2.1 / R1 write-path is described as "serialize the merged `serde_json::Value` via `toml_edit`" — but a merged `Value` carries no comment/trivia, so serializing it from scratch preserves nothing, defeating R1's own comment-preservation goal. `serde_json::Value` also can't round-trip TOML datetimes / int-vs-float. | Rewrite to the **delta-replay** design: parse `config.toml` → `toml_edit::DocumentMut` (retains trivia) AND derive a `Value` for the merge; run `merge` → `MergeReport`; then **replay only `report.changes` (ScalarAdded/ScalarForced/SetUnioned deltas, keyed by dot-path) onto the `DocumentMut`** and serialize that. `Value` is used for *decisions only*. Keep the "preserve a pre-existing comment" test — it's the right guard (only passable under delta-replay). |
| C2 | medium | Epic 4.1's "minimized irreducible-core bundle" has unspecified **provenance** (extracted from `YOSHIKO_FLOW.md`? hand-authored? verbatim copy?) and, because the 008/009 drift axis is deferred, **no agreement check** keeps the bundle in sync with the canonical rules it duplicates (the exact duplication research-002 Q5 flags). | Specify provenance in Issue 4.1 (recommend: derived from named `YOSHIKO_FLOW.md` sections, traceable), and either add a lightweight bundle↔source agreement assertion OR explicitly file the drift as an accepted follow-on bead (not silently folded into the deferred doctor axis). If provenance is genuinely open, make it a small investigation issue, not an implementation issue. |
| C3 | medium | "Pi is easy to correct" understates cost: profiles are **rust-embedded** (`profile.rs` via rust-embed) — correcting a wrong Pi path/format needs a code change + rebuild + release, not a config edit. Pi's config *format* is itself `[uncertain]`, so shipping an embedded `pi.json` at a guessed path commits a guess into a released binary. | Either **defer the Pi profile** to the re-verification bead (ship codex+opencode now; Pi tune/deploy arrives with first-party docs), OR keep it but (a) correct the wording to "requires a point release," and (b) gate Pi behind an explicit opt-in acknowledgment in the tune path, not merely a surfaced report line. |
| C4 | medium | `--revert` lacks an explicit **operator-touched-since-tune guard** for added scalars: yf writes `K=v` (ScalarAdded → revert deletes K); if the operator hand-edits `K=v'` between tune and revert, a naive revert deletes their `v'`. Also: manifest sidecar location + gitignore treatment unspecified (an un-ignored manifest could get committed). | Issue 5.2 / R4 must state: before reverting any key, compare current on-disk value to the manifest's recorded yf-written value; if they differ, **do not revert — report and conservative-keep**. Specify the manifest path and its gitignore handling in project scope. |
| C5 | low | Epic 4.1 `depends-on: 3.1` couples the AGENTS.md target map to the codex *settings* profile, which looks like sequencing convenience, not a true data dependency. | Confirm whether 4.1 consumes the codex profile; if not, drop the 3.1 edge so Epic 4 can proceed in parallel. |

## Missing

- **Type-fidelity note** for the TOML bridge: record that `serde_json::Value` cannot round-trip TOML
  datetimes / int-vs-float, which is *why* the write path must be delta-replay (Value for decisions
  only) — else an implementer may widen the Value model instead of fixing the write path.
- **Codex `project_doc_max_bytes` (32 KiB) interaction**: a managed block in `~/.codex/AGENTS.md`
  competes with the concatenation cap (research S-CX-1) — worth a one-line risk acknowledgment.
- Manifest sidecar path/location + gitignore handling (folded into C4).

## Gate Assessment

Start Gate (human/operator) appropriate. Omitted gates correctly justified: no capability gate
(`toml`/`toml_edit` are plain Cargo deps, confirmed absent from `Cargo.toml`); no reconcile gate
(#95 `related`). SPEC-first enforced structurally by `depends-on: 1.1` edges — right lightweight
mechanism. Suggestion: name the Epic 6.2 Tier-2 sandboxed-`HOME` integration test as the
success-criteria verification for revert round-trip correctness.

## Upstream Assessment

Sound. #95 disposition `related` correct (predecessor, not incorporated). Plan commits to one coarse
tracking issue at intake referencing #95 (AGENTS.md coarse mandate, #13/#14/#16 precedent). Closing
beads `yf-8agh` + `yf-up7s` are real and dependency-linked to closed `yf-2gyv`. Two deferred
follow-ons (per-harness doctor/drift axis; Pi first-party re-verification) slated to be filed in
Issue 6.2 — appropriate.

## Operator Resolutions

| Concern | Resolution | Status |
|:--------|:-----------|:-------|
| C1 (TOML write-path delta-replay) | Accepted. Plan v2 rewrites Epic 2 / Issue 2.1 / R1 to the delta-replay design (parse → `toml_edit::DocumentMut` for trivia + derive `Value` for the merge decision; replay `MergeReport` deltas onto the document). Type-fidelity note added (Value for decisions only; can't round-trip TOML datetimes/int-vs-float). | resolved |
| C2 (Epic 4 bundle provenance + drift) | Accepted with amendment. Bundle is **derived from the skills' `protocols/` sources** — recognizing YOSHIKO_FLOW.md is itself aggregated from each skill's `protocols/` section. Derivation is **forward-looking + re-runnable**: a new skill's new `protocols/` rule automatically enters the same minimization analysis. Add a bundle↔source agreement assertion. | resolved |
| C3 (Pi embedded-asset cost / defer?) | **Defer Pi.** Plan v2 covers **codex + opencode** only; the Pi settings profile AND rule-deploy target are deferred to a filed re-verification follow-on bead (pending first-party Pi docs). REQ-YF-TUNE-016 is redefined as the documented Pi-deferral requirement. | resolved |
| C4 (revert touched-since-tune guard + manifest path) | Accepted. Issue 5.2 / R4 state the guard: before reverting a key, compare current on-disk value to the manifest's recorded yf-written value; if they differ, do not revert — report + conservative-keep. Manifest path + project-scope gitignore treatment specified. | resolved |
| C5 (Epic 4.1→3.1 dependency) | Accepted. Drop the Epic 4.1 `depends-on: 3.1` edge (keep `1.2`); the AGENTS.md target map is independent of the codex settings profile. | resolved |
