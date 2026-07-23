---
type: Review
okf_spec: OKF-PLAN
---
# Review pass 4 — plan-033-james-dixson-46aca2

**Reviewer:** Red-Team (adversarial)
**Date:** 2026-07-22

## Verdict: REVISE

First adversarial pass on the heavily re-scoped 10-epic multi-harness provisioning plan (the
`yf harness skills` CLI relocation + rules-move + auto-detect). Well-grounded — every pillar traces
to a finding/research citation, REQ allocation is collision-free, the 24-issue DAG is acyclic and
enforces SPEC-first, and the load-bearing Epic 4 delta-replay premise is verified against real code
(`MergeReport.changes` already carries the dot-path deltas). But the enlargement introduced a
cluster of coherence gaps, one blocking.

## Strengths

- **Epic 4 delta-replay provably feasible without touching `merge.rs`** — `MergeReport.changes`
  (`ScalarAdded{path,value}`/`ScalarForced{path,from,to}`/`SetUnioned{path,added}`) is exactly the
  dot-path-keyed delta stream the `toml_edit::DocumentMut` replay needs. R10 holds.
- **REQ allocation clean** — existing maxima TUNE-011 / FLOW-006 / INSTALL-006; the plan's
  TUNE-012..025, INSTALL-007..009, FLOW-007 collide with nothing; each impl issue maps to a landed
  REQ; SPEC-first wiring enforced by depends-on Epic 1.
- **naba transfer is real** — `naba/src/harness.rs` ships the exact descriptor table, `surface_alias()`,
  legacy fallback, and a SPEC↔code parity test. Epic 2 is a proven port.
- Fail-safe / idempotent / `Agent`-never-denied preserved structurally (adapter-side work only).

## Concerns

| # | Severity | Concern | Recommendation |
|:--|:---------|:--------|:---------------|
| F1 | high | **Pi rule deployment ships a compiled-in guess to an `[uncertain]` target** — the same logic that deferred Pi *config*. The plan can't even choose: "pi `~/.pi/agent/AGENTS.md` **or** `APPEND_SYSTEM.md`" (semantically different) runs through objective/Approach/Issue 6.2/REQ-YF-TUNE-020/success. Reversibility doesn't save it: a wrong target means the block is written to a file Pi never reads and rules **silently don't load** — invisible to an operator who never runs `--revert`. Textbook hidden-unknown mis-filed as implementation. | (a) Split Pi rules into a short INVESTIGATE experiment resolving the real target vs a first-party Pi source before Epic 6 codes it; or (b) defer Pi rules with Pi config (Pi = skills-only now); or (c) ship only behind explicit `--pi-rule-target` + loud "unverified" notice — never a silent compiled-in default. Resolve the AGENTS.md-vs-APPEND_SYSTEM.md fork to one concrete SPEC choice regardless. **Operator decision.** |
| F2 | medium | **`--revert` is attached to two commands.** Objective/Approach/Issue 1.1 list it on `yf harness skills --install`, but Epic 8/success describe `yf harness tune --revert`, and revert reverses a *tune* (config keys + rule blocks) — a skills-only install wrote nothing to revert. | Drop `--revert` from `harness skills --install` everywhere; it is a flag on `harness tune` only. Fix REQ-YF-CLI-002 grammar in Issue 1.1. |
| F3 | medium | **REQ-YF-CLI-001 and REQ-YF-TUNE-002 not in the Epic 1 revision list** but the relocation invalidates both (CLI-001 enumerates top-level `skills` subcommands; TUNE-002 fixes the `harness` group as `tune`-only). | Add both to Issue 1.1's revision set (CLI-001: `skills` now a deprecated top-level alias + `harness skills`; TUNE-002: `harness` group gains a `skills` subcommand). |
| F4 | medium | **"All harness ops under `yf harness`" is only true for install** — `yf skills upgrade\|remove\|status` are neither relocated nor deprecated, leaving a split topology. Also `--install` as a boolean flag is stylistically inconsistent with the existing `install\|upgrade\|remove\|status` sub-verb style and leaves bare `yf harness skills` undefined. | State whether upgrade/remove/status relocate too (file the work) or are deliberately left; soften the "all harness ops" claim to match. Reconsider `--install` flag vs an `install` sub-verb. **Operator decision.** |
| F5 | medium | **Skills-only bare install is a silently-degraded state.** Moving the YOSHIKO_FLOW.md aggregation to tune means a fresh `yf harness skills --install` without `--tune` deploys skill bodies but NO always-loaded rules — so trigger-based engine skills (yf-change-validation, yf-drift-check, yf-markdown-lint, yf-beads-upstream close-time) are inert until tune runs. A behavior change from plan-032; R2 only covers not-corrupting existing files, not the fresh-install degraded state. | Treat as an explicit documented behavior change: the deprecated alias + bare install emit a "skills-only — run tune to deploy rules" warning; install success output states rules were not deployed; Epic 9 docs call out that bare install is non-functional for trigger-based skills. |
| F6 | medium | **Auto-detect PATH probe is non-hermetic + wide blast radius.** Issue 2.3's "absent harness not detected" test uses sandboxed `HOME`, but detection is home-dir OR `PATH` binary, and `PATH` isn't sandboxed → host-dependent flake. And no-`--harness --tune` writes config+rules to EVERY detected harness with no confirmation. | Inject `PATH` as a parameter so Tier-2 tests are hermetic (state in Issue 2.3). For blast radius: summarize-and-confirm, or dry-run-then-apply printing the resolved target set before writing, for the multi-harness auto path; document it. |
| F7 | low | **Codex `project_doc_max_bytes` (R8) acknowledged but no follow-on filed** in Epic 10.2. | Add the codex block-size-budget check to the Epic 10.2 follow-on list. |

## Missing

- SPEC revisions for REQ-YF-CLI-001 / REQ-YF-TUNE-002 (F3).
- A single concrete Pi rule target (F1) — stays a literal "or" through SPEC/code/docs.
- Disposition for `yf skills upgrade|remove|status` under the new topology (F4).
- Explicit acknowledgment that fresh bare-install behavior changed (F5).
- Codex size-budget follow-on in Epic 10.2 (F7).

## Gate Assessment

Defensible. No capability gate (toml/toml_edit ordinary deps; `MergeReport` already exposes the
deltas — no engine unknown). No reconcile gate (#95 `related`; web beads local). Single human Start
Gate appropriate. Caveat: if F1 is resolved by converting Pi rules to an INVESTIGATE experiment,
that finding should gate Epic 6's Pi target-map code.

## Upstream Assessment

Sound. #95 `related`, plan-033 the follow-on; coarse-granularity contract honored (one tracking
issue, referencing #95; local beads yf-8agh/yf-up7s closed + web beads reconciled without granular
push). Deferred follow-ons (Pi config re-verification; doctor/drift axis) filed as beads. Recommend
the Pi-rules-target verification (if deferred) and codex size-budget follow-ons join Epic 10.2.

## Operator Resolutions

| Concern | Resolution | Status |
|:--------|:-----------|:-------|
| F1 (Pi rule target [uncertain]) | **INVESTIGATE first.** Add a Pi-rule-target investigation issue + a capability gate; Epic 6's Pi rule code is gated on a resolved, first-party-checked target (AGENTS.md vs APPEND_SYSTEM.md → one concrete SPEC choice). If no first-party evidence surfaces, fall back to explicit `--pi-rule-target` opt-in (never a silent default). | resolved |
| F2 (--revert on tune only) | Accepted. `--revert` is a flag on `yf harness tune` ONLY; removed from `harness skills install` everywhere; REQ-YF-CLI-002 grammar fixed. | resolved |
| F3 (revise CLI-001 + TUNE-002) | Accepted. Epic 1 (Issue 1.1) now also revises REQ-YF-CLI-001 (skills = deprecated top-level alias + `harness skills`) and REQ-YF-TUNE-002 (`harness` group gains a `skills` subcommand). | resolved |
| F4 (relocate upgrade/remove/status; flag vs sub-verb) | **Relocate all four as sub-verbs.** `yf harness skills install\|upgrade\|remove\|status` (matching current style), `--tune` a flag on `install`; the whole top-level `yf skills` group becomes a deprecated alias until next major. Objective "all harness ops" claim now literally true. | resolved |
| F5 (bare-install degraded-state warning) | Accepted. Bare install (no `--tune`) + the deprecated alias emit a "skills-only — run tune to deploy rules" warning; success output states rules were not deployed; Epic 9 docs call out bare install is non-functional for trigger-based skills. | resolved |
| F6 (hermetic detect + confirm blast radius) | Accepted. Detection takes `PATH` as an injected parameter (hermetic Tier-2 tests, Issue 2.3); the no-`--harness --tune` multi-harness auto path prints the resolved target set and requires confirm / dry-run-then-apply before writing. | resolved |
| F7 (codex size-budget follow-on) | Accepted. Codex `project_doc_max_bytes` block-size-budget check added to the Epic 10.2 follow-on filing list. | resolved |
