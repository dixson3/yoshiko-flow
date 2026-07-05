# Review pass 1 — plan-023

**Reviewer:** red-team (adversarial)
**Date:** 2026-07-05
**Verdict:** REVISE

## Strengths

- EXP-001 integration mapping is strong and verified (detect/offer/correct fold-in points exist; reader helpers exist).
- #66 is a correct one-liner (`BEADS_UNTRACK` includes `interactions.jsonl`; `BEADS_GITIGNORE` top-up does not).
- #67 config bugs are real (verified `migrate.rs` `.yf/yf-plan/` full vs `preflight.rs` `.yf/plan/` short; shortname map duplicated).
- SPEC-first ordering respected in every epic; #65 supersede and #60 defer correctly justified.
- Local-only/no-remote invariant reuses proven plan-022 machinery (low-risk).

## Concerns

| # | Sev | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| 1 | HIGH | Engine-mode "embedded is canonical / server is drift" is decided against evidence that skips #58's motivating concern. #58 explicitly frames engine mode as the open question, titles it "embedded/**local-server**," and warns embedded is single-process file-locking while a local server exists for **concurrent** multi-client access (why the requester's repos run server mode). EXP-001 tested only **sequential** worktree read-then-write. The plan would flag the requester's deliberately-server-mode repos (incl. this one) as drift. | Either (a) accept **both** embedded and local-server as conformant — assert only per-project + local-only + worktree-shared, engine mode non-drift (matches the issue's phrasing); or (b) keep embedded-canonical only after testing **concurrent** access and adding the no-concurrent-writer guard invariant #58 requires. Do not ship embedded-only on sequential-only evidence. |
| 2 | MED | server→embedded migration mechanism unspecified & unverified — plan calls it "riskiest" but never says HOW doctor does it (server shutdown, storage conversion, metadata rewrite, data preservation, reversibility). SC#1 promises a passing repair fixture for an operation not established as possible via bd. | Add a capability-gated spike to prove the mechanism + reversibility before 1.3, OR descope 1.3's engine-mode **correction** to detect/warn-only this plan (still deliver local-only/no-remote corrections). Split engine migration into its own plan once proven. |
| 3 | MED | Risk isolation: risky/uncertain #58 gates trivial wins. Reconcile gate is whole-plan-close; #66/#57/#67 don't depend on #58 but can't close their issues until Epic 1's beads close. #58 is the most likely to stall. | Per-issue reconcile (close #66/#57/#67 independently of #58), or split #58 into its own plan and land the small fixes now. |
| 4 | LOW | "Standardize on short" hides a config-basename decoupling trap: in `migrate.rs`, state dest and config dest both key off the same `new` name; naively swapping `yf-plan`→`plan` would misroute config to `.plan.local.json`. State short-name and config-basename are separate axes. | Issue 2.2 should explicitly decouple state-dir short-name from config-basename; fixture proving config still resolves after the SKILL_MAP change. |
| 5 | LOW | Third config shape / 3-tier read: flat `.yf/<short>.local.json` middle tier isn't marked transitional/removable — risks permanent dead weight. | Mark the flat tier transitional; follow-up cleanup bead once migration is ubiquitous. |
| 6 | LOW | Issue 1.1 doesn't name the target SPEC surface (root `REQ-YF-*` vs `skills/yf-beads-init/SPEC.md` `REQ-BINIT-*`). | Name the target file(s) + new REQ id(s). |

## Missing

- No **concurrency** test for the embedded worktree-sharing invariant (the exact #58 scenario).
- No server→embedded conversion commands / reversibility findings.
- The no-concurrent-writer guard invariant #58 requires if embedded is chosen is absent from the profile definition.

## Gate Assessment

Start + auto-reconcile appropriately typed. But EXP-001 did NOT conclude the two things Epic 1 most needs (embedded concurrency safety; server→embedded mechanism) — a capability gate on the migration spike is warranted if engine-mode correction stays in scope. Whole-plan reconcile creates the risk-isolation coupling (concern 3).

## Upstream Assessment

#65 supersede + #60 defer correct; #66/#57 includes accurate. Weakness is #58: adopts embedded-only where the issue left the choice open ("embedded/local-server") and resolved it against untested evidence. Broaden to accept both modes or carry the concurrency investigation the issue demands.

## Operator Resolutions

| # | Resolution | Status |
| :-- | :-- | :-- |
| 1 | **Operator decision: canonical = per-repo local-server; drop embedded.** Local-server is the mode that makes concurrent worktree-issue-sharing safe (the #58 motivation). Profile asserts per-repo local-server + worktree-shared + local-only/no-remote; this repo (server) is now **conformant**, not drift. Resolves the "embedded on sequential-only evidence" objection by picking the concurrency-safe mode. | resolved |
| 2 | **Eliminated by concern-1's resolution.** No server→embedded migration is built. Engine-mode correction is **descoped to detect/warn-only** — the risky/unproven conversion is out of scope; `doctor --repair` corrects only the safe local-only/no-remote axes (plan-022 machinery). No migration fixture promised. | resolved |
| 3 | **Per-issue reconcile.** Reconcile gate note now decouples closure: #66/#57 (Epic 3) and #67 (Epic 2) reconcile/close independently of #58 (Epic 1). Kept bundled (operator intent) but the trivial fixes are no longer hostage to #58. | resolved |
| 4 | Issue 2.2 now explicitly decouples the state short-name from the config-basename axis (the SKILL_MAP short-name fix must not misroute config) + a fixture proving config still resolves. | resolved |
| 5 | Issue 2.3 marks the flat `.yf/<short>.local.json` tier **transitional** (back-compat read only), with a follow-up cleanup bead filed at land-the-plane. | resolved |
| 6 | Issue 1.1 now names the target SPEC surfaces: new `REQ-BINIT-*` in `skills/yf-beads-init/SPEC.md` (repair) + profile invariants in root `SPEC.md` `REQ-YF-*` (preflight); coverage-gate the new ids. | resolved |

**Verdict after revision:** all 6 concerns resolved. The HIGH concern reshaped Epic 1 (local-server canonical, engine-migration out of scope) — a material change, so a **pass-2 red-team cycle** is warranted before approval (per the ready-for-approval discipline of #69).
