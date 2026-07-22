---
type: Review
okf_spec: OKF-PLAN
---
# Red-Team Review — Pass 1

**Plan:** plan-032-james-dixson-6cb87b
**Presented:** 2026-07-22
**Status:** resolved (revisions applied; re-reviewed in pass-2)

## Verdict: REVISE

## Strengths

- SPEC-first discipline correctly stated; Epic 1 sequences `REQ-YF-TUNE` ahead of code; §3.10 slot is free.
- Recon accurate and load-bearing (verified: `prune_empty_settings` never-clobber precedent; `bd setup claude` owns the hook; `preserve_order`; rust-embed; the `yf/src/cmd/doctor/checks.rs` trait registry gives the doctor extension a clean seam).
- Agent-never-denied invariant well-founded and distinct from `Task*`; polarity-in-data is the right call.
- Multi-harness deferral to a clean refusal is safe; `yf-2gyv` gate is real.
- Idempotence, `--dry-run`, gitignored-`settings.local.json` default are sound.

## Concerns

- **[HIGH] `permissions.deny` is an array; key-granular add-missing/whole-value-conflict either refuses to help or clobbers user safety globs.** Every competing-tool deny lives as an *element inside the `permissions.deny` array*, not a top-level key. Add-missing would refuse (array already present); `--force` would replace the whole array, dropping the user's custom denies and `rm -rf` safety globs.
  Recommendation: array-element-**union** semantics for set-valued entries (add missing elements, never remove; no `--force` needed); profile schema distinguishes scalar vs set-valued. Must land in `REQ-YF-TUNE`, not be discovered in Epic 3.
- **[MEDIUM] No interactive-prompt precedent in the yf binary; both the install-offer and doctor `--repair` "offer" assume one.** Every yf mutation gate is a flag, not a TTY prompt; `yf skills install` often runs non-interactively.
  Recommendation: make the offer flag-gated only (`--tune` for install; `--repair` runs tune for doctor); drop the interactive-prompt framing, or add explicit TTY-detection + non-interactive fallback to the REQ.
- **[MEDIUM] SPEC-first as separately-landed epics collides with the `coverage.rs` gate.** New `*(testable)*` REQs with no tagged test red the build between Epic 1 and Epics 3/4, contradicting "coverage gate stays green."
  Recommendation: land each REQ with its test in the same change-set (vertical slices), or mark REQs non-`(testable)` until covered, or bridge via `ALLOWLIST`. State the choice.
- **[MEDIUM] Drift test underspecified — "derive from" ≠ "drift-check against", and the prose doc is not fully machine-derivable.** The doc carries rationale prose a flat profile can't regenerate.
  Recommendation: scope the drift test to the fenced reference-baseline block only; decide generated (regen-and-diff) vs authored (assert-agreement); prose is not machine-derived.
- **[MEDIUM] "Multi-harness from day one" over-promises — the merge engine is JSON/Claude-specific, so `--harness` is cosmetic.** A codex profile targets `.codex/config.toml` (TOML, different merge/scope).
  Recommendation: reframe `--harness` as a forward-compat lookup key; state the engine + scope logic are Claude-Code-specific in this plan.
- **[MEDIUM] Doctor drift-check reads a file in isolation, but Claude Code layers `settings.json` ← `settings.local.json` (and user scope).** Per-file check false-positives "missing key" when set in another layer.
  Recommendation: compute the effective merged view across precedence layers (or report per-layer); add REQ + test for the "set in a different layer" case.
- **[MEDIUM] "yf-owned-key marker for clean reversal" has no mechanism — strict JSON has no comments; `marker.rs` is Markdown-comment-based.** Reversibility claimed in the risk table with no implementing issue.
  Recommendation: specify the ownership mechanism concretely (sidecar manifest or a `_yfManaged` array), or drop the reversibility claim and add an explicit revert issue if in scope.

## Missing

- No issue wires `docs/recommended-settings.md` to the profile (2.3 adds only the test).
- No issue states where the embedded profile lives; a dir under `../skills` would surface as a bogus skill and pollute tree-hash/marker — needs a separate rust-embed root.
- No test for the array-union case on `permissions.deny` (partial existing deny + preserving `rm -rf` globs).
- No handling for a malformed/unparseable settings.json on the write path (must fail-safe: refuse + report, like `prune_empty_settings`).
- Reversal/undo path has no issue.

## Gate Assessment

Only a mandatory human Start Gate — appropriate; no over-gating. Plan should note the CI/coverage expectation at each epic boundary so the tree isn't stranded red between Epic 1 and Epics 3/4. REQ-tagged tests + coverage gate are adequate epic validation for this codebase.

## Upstream Assessment

Disposition reasonable; coarse-granularity convention correctly invoked; triggering bead `yf-nl8i`, counterpart `yf-8ayq`, and research gate `yf-2gyv` all named. Verify at land-the-plane that the `yf-2gyv`-gated multi-harness follow-on is filed as an actual bead with the dependency edge.

## Operator Resolutions

| # | Concern (severity) | Resolution | Status |
|:--|:-------------------|:-----------|:-------|
| 1 | permissions.deny array clobber (HIGH) | Approach + REQ now specify scalar vs set-valued profile entries; set-valued (`permissions.deny`) use non-destructive **union** (add missing, never remove, no `--force`); scalars use add-missing/conflict-report. New Issue 3.5 + test. | resolved |
| 2 | No prompt precedent (MED) | Offer is **flag-gated only** — `--tune` for `install`, `--repair` runs tune for doctor; interactive-prompt framing dropped; non-interactive is the norm. | resolved |
| 3 | Coverage-gate vs SPEC-first timing (MED) | Epic 1 adds new REQ ids to the `coverage.rs` `ALLOWLIST` in the same change-set; each id is removed from the allowlist as its implementing epic lands the tagged test. Recorded in Approach + Issue 1.3. | resolved |
| 4 | Drift test underspecified (MED) | Drift test scoped to the fenced reference-baseline block only; the profile is the source and the doc block is **generated-and-diffed** (Issue 2.4); prose is not machine-derived. "derived-from" softened accordingly. | resolved |
| 5 | Multi-harness cosmetic (MED) | `--harness` reframed as a forward-compat lookup key; Approach + REQ state the merge engine + scope logic are Claude-Code-specific this plan; a second harness needs a new engine. | resolved |
| 6 | Doctor layer precedence (MED) | Doctor check computes the effective merged view across user ← project `settings.json` ← `settings.local.json`; REQ + test for the "set in a different layer" case (Issue 4.1/4.3). | resolved |
| 7 | Reversal marker mechanism (MED) | Reversibility removed from core scope; doctor uses the profile (not a marker) as its reference set. Revert path filed as a follow-on bead, not in-plan. Risk-table claim corrected. | resolved |
| 8 | Missing: doc-wire issue | Added Issue 2.4 (generate/annotate the fenced doc block from the profile). | resolved |
| 9 | Missing: embed location | Issue 2.2 now specifies a **separate rust-embed root** (not under `../skills`) to avoid polluting skill/tree-hash logic. | resolved |
| 10 | Missing: array-union test | Added to Issue 3.5 test list (partial existing deny + preserve `rm -rf` globs). | resolved |
| 11 | Missing: malformed settings.json fail-safe | REQ + Issue 3.2: refuse to write and report on unparseable input (mirrors `prune_empty_settings`). | resolved |
| 12 | Missing: reversal issue | Filed as follow-on bead (see #7); out of core scope. | resolved |
