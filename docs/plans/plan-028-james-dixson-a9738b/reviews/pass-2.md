# Red-Team Review — pass 2

**Plan:** plan-028-james-dixson-a9738b
**Date:** 2026-07-15
**Reviewer:** red-team (adversarial, independent sub-agent) — re-run after pass-1 REVISE

## Verdict: APPROVE

All four pass-1 concerns verified genuinely and correctly resolved against the real repo. No
High blockers. Two residual items (one medium coordination hazard the revision itself
introduced, one low scoping-hygiene gap) were folded in as clean corrections consistent with
the APPROVE verdict.

## Prior-Concern Verification (all RESOLVED)

- **1 — amendment-log location.** Root `SPEC.md` confirmed as the single per-plan amendment
  log; per-skill SPECs carry only `REQ-*`. Approach + Issues 1.1/2.1 now direct a single
  `plan-028` root-`SPEC.md` entry covering both #87/#86.
- **2 — parked = present-AND-fresh.** Issues 2.1(b)/2.3/2.6 define parked as `status ==
  approved` AND `bool(stored) and stored == current`, the correct complement of
  `_fingerprint_status.stale_approved` (plan_manager.py:1040) and aligned with the
  eligibility caution at 828-829. No-fingerprint and stale cases explicitly excluded.
- **3 — real CHANGE-VALIDATION recipe.** Issue 1.4 adds a command row to fast + full tiers, a
  §3 trigger-scope row, and a §2 fingerprint update — matches the actual manifest structure.
  Issue 2.6 prefers folding into `test_worktree.py` (wired via `uv-yf`).
- **4 — PEP-723 `uv run <file>`.** Issue 1.4 pins the sibling `test_link_normalizer.py`
  convention.

## Residual Concerns (folded in)

- **[medium] Shared root `SPEC.md` contradicted the parallelism claim.** Both Issues 1.1 and
  2.1 wrote the single shared amendment entry with no serialization → collision risk in
  parallel worktrees. Resolved: Issue 1.1 now **owns/authors** the shared `plan-028` entry
  (covers both), Issue 2.1 **references** it and gains `depends-on: 1.1` so the root-`SPEC.md`
  touch serializes; Approach qualifies the "parallel" claim to per-skill files only.
- **[low] Fast-tier scope only fired on the test file, not the scorer source.** Resolved:
  Issue 1.4 now also adds the new fast id to the `skills/yf-research/scripts/**` scope row
  (mirrors the `skills/yf-plan/scripts/**` → two-id precedent).

## Gate & Upstream Assessment

Unchanged and sound. Start Gate (human/operator) + Reconcile Gate (auto, both `include`)
appropriate; no over-gating. Dispositions specific, wired via `resolves-upstream`, bundling
justified by precedent; Issue 2.5's title rename serves #86.

## Line-reference spot check (all accurate)

`_currency_score`@86 (crash `now-pub`@100 outside try/except), `_domain_authority_score`@58
(loop@73-80, gov/edu@92, unknown@30), `TIER_2_DOMAINS`@36 (7 additions absent → additive),
`_commit_plan`@1102 / subject@1151, `_fingerprint_status`@1027 / `stale_approved`@1040,
`list_plans`@740 / stale tag@797, eligibility caution@824-829.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
|:--|:--------|:---------|:-----------|:-------|
| 1 | Shared root SPEC.md entry vs parallel claim | medium | Issue 1.1 owns the shared entry; Issue 2.1 references it + `depends-on: 1.1`; Approach qualifies parallelism | resolved |
| 2 | Fast-tier scope missed scorer source | low | Issue 1.4 adds new fast id to `skills/yf-research/scripts/**` scope row | resolved |
