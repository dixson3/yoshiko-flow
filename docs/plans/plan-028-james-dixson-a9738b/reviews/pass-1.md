# Red-Team Review — pass 1

**Plan:** plan-028-james-dixson-a9738b
**Date:** 2026-07-15
**Reviewer:** red-team (adversarial, independent sub-agent)

## Verdict: REVISE

No hard blockers (nothing High); three Medium concerns materially affect correctness of
the SPEC-first change-set and the parked classifier, plus one Low. All are concrete plan-text
edits, not investigation gaps.

## Strengths

- Line references all accurate against the real repo (`_currency_score`@86,
  `_domain_authority_score`@58, `TIER_2_DOMAINS`@36, `_commit_plan`@1102, subject@1151,
  `list`@738, `stale_approved` tag@797).
- tz-naive fix is sound: `fromisoformat` succeeds on a naive string; the crash is at
  `now - pub` (line 100), outside the try/except. Inserting the tzinfo normalization between
  parse and subtraction closes the gap without disturbing the except path.
- Domain-heuristic ordering (after exact-tier loop, before unknown fallback) avoids
  downgrading Tier-1 gov/edu (returns 92 before the loop) and Tier-4 substring hits like
  `dev.to`. `startswith("docs.")` / `tld == "dev"` introduces no new substring false-positive.
- No existing test asserts the old commit-subject format
  (`test_commit_plan_commits_on_plan_branch_then_noop` checks only status/branch/commit
  presence, and its seeded plan isn't `approved`). No existing test references the scorer.

## Concerns

- **[medium] Living-amendment-log is mislocated.** Issues 1.1 and 2.1 target only the
  per-skill `skills/<skill>/SPEC.md`, but the amendment log lives **only** in the root
  `SPEC.md` (one entry per plan). Per-skill SPECs carry only `REQ-*`. Recommendation: add
  root `SPEC.md` as a change-set target and record a **single `plan-028` amendment-log
  entry** covering both #87 and #86.
- **[medium] Parked classifier keys on the `status == "approved"` literal / "not stale".**
  `plan_manager.py:828-829` cautions execute-eligibility keys on the fingerprint, never the
  status literal; and `stale_approved = bool(stored) and stored != current` is False both
  when fresh AND when no fingerprint is stored — so an `approved` plan with a missing
  fingerprint would be wrongly nudged. Recommendation: define parked as fingerprint present
  AND fresh (`bool(stored) and stored == current`) with `status == "approved"` as a coarse
  filter only.
- **[medium] CHANGE-VALIDATION wiring won't actually run the new test.** `uv-research` runs
  only `test_link_normalizer.py`; the §3 glob matches a new test file but never executes it
  unless a command row is added. Plan also omits the full tier, which Success Criteria
  requires. Recommendation: add a recipe row running the new file in both fast and full
  tiers, a §3 trigger-scope row, and a §2 fingerprint update. Same for Epic 2.6 if it adds a
  new file (else fold assertions into `test_worktree.py`, already wired via `uv-yf`).
- **[low] New research test should follow the sibling `uv run <file>` PEP-723 convention**
  (`test_link_normalizer.py`), not `python -m pytest`.

## Missing

- Root `SPEC.md` not enumerated as a change-set target despite SPEC-first.
- CHANGE-VALIDATION full-tier row not noted, yet a full-suite pass is a Success Criterion.
- No explicit statement that an intake'd-but-unexecuted plan carries status `approved` (the
  classifier's premise) — correct per the vocabulary, but worth stating in Issue 2.3.

## Gate Assessment

Gates minimal and appropriate. Start Gate (human/operator) standard. Reconcile Gate (auto,
"all execution beads closed," both dispositions `include`) genuinely needed and valid. No
over-gating; the two epics are correctly independent and parallelizable.

## Upstream Assessment

Dispositions reasonable and specific: #87/#86 both `include`, each wired via
`resolves-upstream`, operator scoping decisions recorded. Bundling justified by precedent.
Coarse upstream tracking respected (resolved issues distinct from the single per-plan
tracking issue). Issue 2.5's title rename directly serves #86's complaint.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
|:--|:--------|:---------|:-----------|:-------|
| 1 | Amendment log mislocated (root SPEC.md, one plan-028 entry) | medium | Revised Approach + Issues 1.1/2.1 to target root `SPEC.md` with a single plan-028 amendment entry; per-skill SPECs carry only the REQ edits | resolved |
| 2 | Parked classifier: use fingerprint present-AND-fresh, not "not stale" | medium | Revised Issues 2.1(b)/2.3 to define parked as `status == approved` (coarse filter) AND stored fingerprint present and fresh (`stored == current`); missing/stale fingerprint excluded | resolved |
| 3 | CHANGE-VALIDATION: add real recipe row (fast+full), §3 scope, §2 fingerprint | medium | Revised Issues 1.4/2.6 to add a recipe command row to both tiers, a §3 trigger-scope row, and a §2 fingerprint update | resolved |
| 4 | New research test follows PEP-723 `uv run <file>` convention | low | Revised Issue 1.4 to pin the sibling `test_link_normalizer.py` PEP-723 + `uv run` invocation | resolved |
