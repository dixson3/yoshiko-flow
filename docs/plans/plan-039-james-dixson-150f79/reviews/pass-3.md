---
type: Review
okf_spec: OKF-PLAN
---
# Plan Red-Team: plan-039-james-dixson-150f79

**Pass:** 3 · **Date:** 2026-08-14

> **Independent pass**, fresh-eyes sub-agent, no access to the drafting conversation. Tasked with
> verifying each pass-2 resolution against the plan text rather than the resolution table, and
> with finding defects introduced *by* the revisions.

## Verdict: REVISE

Twelve of the fifteen pass-2 resolutions verify clean against the plan text and against re-run
measurement. Three do not fully land, and one — the H1 fix — reintroduces the exact defect class
H1 named, inside its own remedy.

## Strengths

- **Issue 3.2's per-step table reproduces exactly.** Re-measured in the stated implementation
  order: labeled `FP` 16 → 8 → 3 → 2 → 2, corpus 40 → 22 → 15 → 13 → 13, `FN=0` throughout,
  `plan-031` surviving. H2 fully discharged.
- **M1 is a real fix, verified with a negative control** — the new gate test passes against the
  live corpus and *fails* against a nonexistent one. The old form could not fail.
- **SC11 is discriminating** — exit `1` against the corrupted `reviewer.md`, `0` against a
  repaired copy.
- **SC1's anchoring is correct against the real file**, and 046/047/048 are genuinely unallocated
  (`spec/agents.md` jumps 045 → 050).
- **Epic 4.2's guard will not fire spuriously** — audited all `skills/*/agents/*.md` and
  `skills/*/SKILL.md` across all 20 skills; `reviewer.md` is the only offender.
- **M2's fixture-source chain is real** — d3-pxe plan-013 carries `reviews/pass-0-conformance.md`
  quoting the pre-fix Epic 6 defect verbatim, and pass-1 the SSH/capability one. The reconstruct
  fallback is a genuine third resort, not the actual path.
- **The dependency graph is acyclic, complete, and clean after renumbering** — all 19 issues
  resolve, every `depends-on` target exists, no cycles.

## Concerns

- **C1 — SC6 is falsified by measurement, again. The H1 fix reproduces the H1 defect.** — severity: high

  Measured against the current `plan.md` with F1+F2+F5 exactly as specified:
  `plan-039 preF5=5 → postF5=3 ['release','sign','deploy'], suggested_class=ci-release`.
  SC6 required "at most one residual signal"; the measured residual is **three**, two high-tier.
  **Issue 3.4b's "plan-039 5→1" is therefore wrong — it is 5→3.** The other four figures in that
  sentence were each verified correct. The new matches come from text the H1 resolution itself
  added: 3.4's stop-rule blockquote, 3.4b's own prose, and "redeploying" in the SC trailer.

  Recommendation: assert stable *properties* (evidence basis, confidence, every residual being
  genuine subject-matter prose enumerated at execution time) rather than a count against a
  document still being edited. Correct or drop the plan-039 figure in 3.4b.

- **C2 — SC7 has no completion path when 2.5's escalation rule fires.** — severity: medium

  2.5 says a missed fixture "is a finding, not a tuning signal… a second miss escalates rather
  than iterates". SC7 required 4 × `FLAGGED`. If a fixture legitimately does not fire and the
  operator accepts that, SC7 can never be satisfied — so the only route to completion is to tune
  until it flags, exactly the confirmation bias 2.5 exists to prevent. Both were added by the
  same resolution; neither noticed the other.

  Recommendation: make SC7 satisfiable by either outcome — 4 `FLAGGED`, or fewer plus an explicit
  `- MISS` and a filed follow-on bead carrying verbatim output.

- **C3 — M3's resolution updated `plan.md` but not the finding it cites.** — severity: medium

  `findings/exp-001` still leads with "39 of 53", still reports 31/53 and 29/53 and 12/53, still
  presents only the superseded cumulative F1-first ladder, and still recommends `FP<=2`. Plan of
  record and cited evidence now disagree numerically, and the cold reader opens the stale one.

  Recommendation: update, or add an explicit superseded banner.

- **C4 — the frontmatter REQ is homed in the wrong spec, unnamed, and unverified.** — severity: medium

  Issue 1.2 put a **repo-wide** invariant (all 20 skills) into `skills/yf-plan/spec/cli.md`, the
  yf-plan CLI spec. Repo-wide invariants live in root `SPEC.md` as `REQ-YF-*`. Compounding: 1.2
  is the only SPEC issue that does not name its REQ id, and **no success criterion verifies 1.2
  at all** — in a plan whose stated discipline is SPEC-first, Epic 1's second issue is the one
  with no gate on it. Also, 4.2's deliverable is "a check", with no file named.

  Recommendation: home it as `REQ-YF-*` in root `SPEC.md`, name the id, extend SC1, name 4.2's
  script.

- **C5 — the corpus breakdown is arithmetically wrong in both `plan.md` and `exp-001`.** — severity: low

  Both state "44 `yoshiko-flow`, 9 `d3-pxe`". Measured: 39 and 14. The total (53) is right and no
  downstream measurement is affected; the `9` is the count of *labeled* d3-pxe plans.

- **C6 — the renumber left a live prose collision on `4.1, 4.2`.** — severity: low

  Two places describe the v1 gate cycle as blocking "`4.1, 4.2`", which in current numbering are
  the `reviewer.md` repair and its guard. L3 class, surviving the L3 sweep because the sweep
  predated the renumber.

- **C7 — 2.5 overstates what `exp-002` quotes.** — severity: low

  `exp-002` quotes the **as-landed** Epic 6 verbatim; the pre-fix body appears verbatim only in
  d3-pxe `reviews/pass-0-conformance.md:23`. Fixture is buildable; the sentence points at the
  wrong file.

- **C8 — SC12 is under-specified and 5.3 does not name its filing mechanism.** — severity: low

  "`--label deferred-validation` (or the re-measure label)" is not mechanically checkable. 5.3
  does not say whether it files via `/yf-beads-upstream` or `gh issue create`, though the repo
  carries an explicit routing rule.

## Missing

- **Nothing verifies Issue 1.2**, the SPEC-first artifact for all of Epic 3 and for 4.2 (C4).
- **No criterion asserts F5 actually strips anything** — its only trace in the criteria is SC6's
  signal count, which C1 shows is wrong.
- **The pre-existing-FP audit** raised in pass-2's Missing is still absent and now unacknowledged.
  It may be a legitimate non-goal, but it should be declined explicitly rather than dropped.

## Gate Assessment

Four gates, all well-formed, both capability gates reachable under REQ-AGENT-046, and — unlike
pass 2 — the **instrumentation is now sound**. `Gate: Evidence corpus`'s replacement test was
verified empirically (exits 0 against the real corpus, non-zero against an absent one), closing
M1. `Blocks: 3.1, 2.5` closes M2's coverage gap, and "no **CI run** reaches outside the repo" is
now a true statement. One residual imprecision: `Gate: Upstream write`'s test uses
plan-dir-relative paths with no stated working directory, while every other command in the plan
is repo-root-relative — it would fail for a reason unrelated to its condition.

## Upstream Assessment

Dispositions unchanged and sound; `Resolved By` fully wired; `upstream-triage.md` now back-filled
and agreeing with plan.md row for row (L2 clean). The H3 sequencing fix is the substantive
improvement: `5.2b depends-on: 2.5` means #113 is not told the cross-check shipped until the
`epic6` fixture has been observed firing, which also converts M6 from inference to measurement.
Cosmetic: 3.6's annotation reads "(include, with 3.1–3.5)" where siblings read "3.1–3.6", and
neither range names 3.4b. The upstream *risk* now sits with C1: if SC6 ships as written, #108's
tracking narrative records a self-test the plan's own code cannot pass.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | SC6 falsified again; 3.4b's `5→1` is `5→3` | high | Independently re-verified: 3 signals. **SC6 rewritten to assert stable properties** — `evidence: prose-only`, `confidence: low`, and every residual enumerated as genuine subject-matter prose in `references/sc6-residuals.md` — with the reason recorded that a count was asserted twice and falsified twice, because the measured document is the document being edited. **3.4b's plan-039 figure removed** from the stable-document list and replaced with an explicit "moving target, re-derive at execution" note | resolved |
| C2 | SC7 unsatisfiable when 2.5's escalation fires | medium | SC7 now requires four **outcome** lines, each `FLAGGED` **or** `MISS`; a `MISS` satisfies only with a filed follow-on bead carrying verbatim output. The honesty rule is no longer priced out | resolved |
| C3 | `exp-001` still carries superseded figures | medium | Added a superseded banner at the top of the finding, corrected the headline to 40/53 and the rate to 40→13, labelled the cumulative ladder as superseded by 3.2's per-step table, corrected the corpus split, and updated the recommendation from `FP<=2` to the invariant form | resolved |
| C4 | Frontmatter REQ misfiled, unnamed, unverified | medium | Split into **new Issue 1.3**: `REQ-YF-230` in **root `SPEC.md`** (repo-wide, not the yf-plan CLI key), named, with a "confirm unallocated" instruction. 4.2 now names `scripts/check_frontmatter.py` and depends on 1.3. **SC1 extended** to assert `^REQ-YF-230:`; **new SC1b** verifies the REQ-CLI-015 amendment | resolved |
| C5 | Corpus split stated as 44+9, measured 39+14 | low | Corrected in `plan.md` and `exp-001`, with a note that the `9` was the *labeled* d3-pxe count | resolved |
| C6 | Renumber left live `4.1, 4.2` prose references | low | Both rewritten as "the two upstream-publish issues (`4.1, 4.2` in the v1 draft; now `5.1b, 5.2b`)" | resolved |
| C7 | 2.5 cites the wrong file for pre-fix text | low | Fixture row now cites d3-pxe `reviews/pass-0-conformance.md` for the pre-fix text and `exp-002` for the as-landed remedy | resolved |
| C8 | SC12 selector not checkable; 5.3 lacks a filing route | low | Both beads labelled exactly `plan-039-followon`, quoted in SC12; 5.3 now routes through `/yf-beads-upstream` per the repo's `UPSTREAM_TRACKING.md` safety invariant | resolved |
| — | Missing: nothing verifies 1.2 | — | New SC1b (see C4) | resolved |
| — | Missing: no criterion pins F5 | — | **New SC5b** — a fixture asserting a trigger word inside a fenced block or code span produces no signal, independent of any plan's prose | resolved |
| — | Missing: pre-existing-FP audit unacknowledged | — | **Declined explicitly**, with rationale, in a new note under Success Criteria: the population is currently empty (the one `ci-release`-labelled plan is a true positive), and re-labelling completed plans mutates approved fingerprinted artifacts — a riskier operation than fixing the classifier. A genuine case is a one-line `set-deliverable-class` fix, not a sweep | resolved |
| — | Cosmetic: 3.6's `resolves-upstream` range | — | Corrected to "3.1–3.4b, 3.5" | resolved |
| — | Gate: `Upstream write` test path relativity | — | Test annotated "paths are plan-dir-relative; run from `${plan_dir}`" | resolved |

**Final status:** all concerns resolved. Pass 3 frozen.
