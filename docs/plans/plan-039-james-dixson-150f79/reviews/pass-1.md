---
type: Review
okf_spec: OKF-PLAN
---
# Plan Red-Team: plan-039-james-dixson-150f79

**Pass:** 1 · **Date:** 2026-08-14

> **Reviewer-independence caveat.** This pass was performed by the same session that drafted the
> plan, not by a fresh-eyes sub-agent as `agents/red-team.md` specifies ("No access to
> investigation worktrees — fresh eyes only"). Self-review is structurally weaker than the pass
> it stands in for, and this is exactly the confirmation-bias hazard concern C2 below raises
> about Issue 2.5. Recorded here so a cold reader does not over-trust the verdict.

## Verdict: REVISE

## Strengths

- **The evidence is measured, not asserted.** All three findings run against primary artifacts
  (53 real plans, the as-landed plan-013, the live `list` output) rather than restating the
  issues' claims. EXP-001 found the defect an order of magnitude worse than #108 reported;
  EXP-002 *contradicted* the expensive branch of the issue it was investigating rather than
  confirming it. An investigation that can return "no" is doing work.
- **The expensive branch was declined on evidence.** #113's `requires:` schema — its own named
  "real cost" — is deferred because no observed defect needed it. The plan ships the cheap
  precursor and re-scopes the issue rather than closing it.
- **The fix sequence follows the measurement, not the source issue.** F3 is sequenced first
  because it was measured as the dominant fix, though #108 lists it third.
- **Fixture-and-harness before fixes** (Issue 3.1 asserts the *current* baseline) means each
  subsequent change is measured. This is the "prove the check actually catches" pattern.
- **The plan dogfoods its own additions and was caught by them.** The conformance pass found a
  gate-reachability cycle in this plan's own `Gate: Upstream write` — the exact #112 defect —
  and it is now fixed and retained as a replay fixture.

## Concerns

- **C1 — SC6's verification command tests the wrong copy of the code.** — severity: **high**

  SC6 runs `uv run skills/yf-plan/scripts/plan_manager.py …` in prose but the plan's own
  environment has the skill installed user-globally at `~/.claude/skills/yf-plan`, which is a
  *different file* from the `skills/yf-plan/` tree this plan edits. Verified: the installed copy
  currently returns `{"suggested_class": "ci-release", … "confidence": "high"}` for this very
  plan, and will keep returning it after Epic 3 lands, because Epic 3 does not touch it.

  A success criterion that passes or fails independently of the work is not a success criterion.

  **Recommendation:** pin SC4/SC6 explicitly to the in-repo path, and state in `context.md` that
  the installed skill is a separate artifact requiring reinstall. Add an SC asserting the two
  copies agree after install, or explicitly scope the plan to the repo copy only.

- **C2 — Epic 2's entire value rests on a self-graded replay.** — severity: **high**

  Issue 2.5 is the only evidence that three new review items work. It asks the same model that
  authored the items to judge whether they fire, on fixtures the same session assembled. R1
  names this risk and then mitigates it with the mechanism being questioned.

  Prompt additions are the plan's largest deliverable by impact and its least verifiable by
  construction. Without independence this is a check that has been *asserted* to fire, which is
  the failure mode #113 documents at one level up.

  **Recommendation:** require 2.5's replay to run in a **fresh session with no access to this
  plan or its findings** — given only the amended `red-team.md` and the fixture — and to record
  verbatim output in `references/replay-results.md`. A replay that knows the expected answer
  proves nothing.

- **C3 — 2.5 tests that the new items fire, never that the old ones still do.** — severity: **high**

  R2 identifies prompt dilution as a real risk and then measures it with `wc -l` (SC10). Line
  count is not behavior. Three additions to a 60-line prompt could plausibly degrade the checks
  that already work — and those checks have a documented track record (they caught four real
  defects in plan-013).

  **Recommendation:** extend 2.5 with a **regression fixture**: replay a defect the *current*
  prompt already catches (the plan-013 phantom-host / missing-capability case) and require it
  to still be flagged. Then drop or downgrade SC10, which proxies for this badly.

- **C4 — the `1/17 precision` headline is open to a selection-bias objection.** — severity: medium

  Operators record `deliverable_class` at §4.1.5 *after being prompted by the classifier*. If the
  field were only written when `ci-release` was suggested, `TN=0` would be near-tautological
  rather than damning, and EXP-001's headline would be an artifact of how labels are created —
  precisely the measurement-vs-inference error #114 is about, committed by the plan that
  proposes the fix for it.

  Checked, and it survives: plans 031–038 are **eight consecutive plans, all labeled**, so labels
  are written regardless of suggestion. On that unbiased run precision is 1/8. But the finding
  does not say this, and a reader can legitimately reject the headline.

  **Recommendation:** add the consecutive-run check to `findings/exp-001` as the bias control,
  and lead with the full-corpus 39/53 figure — which is unbiased by construction — rather than
  the labeled-set precision.

- **C5 — F2 is shipped despite measuring zero benefit.** — severity: medium

  EXP-001 measured F2 removing **0** labeled-set false positives and 2 corpus-wide, and R3
  concedes the blocklist grows unboundedly and structurally cannot cover the residual class. The
  operator selected all four fixes — but that selection was made *before* EXP-001 existed.
  Shipping a known-ineffective, self-admittedly unbounded maintenance surface deserves an
  explicit re-decision rather than inheriting a pre-evidence choice.

  **Recommendation:** surface the measurement to the operator and let them re-confirm F2. If
  retained, Issue 3.4 should carry a written stop rule: no keyword is added to the blocklist
  without a corpus re-measurement showing it moves `FP`.

- **C6 — Epic 4 is unrelated scope.** — severity: low

  The `reviewer.md` frontmatter repair has nothing to do with the three declared axes. It is a
  one-character fix plus a guard, discovered in-flight, and splitting it into its own plan would
  cost more than it saves — but the Objective does not mention it, so the plan's stated scope and
  its contents disagree.

  **Recommendation:** add one line to the Objective acknowledging the in-flight repair, or split
  it out. Do not leave the mismatch unstated.

- **C7 — Issue 1.1 bundles four SPEC changes.** — severity: low

  Three new REQ ids, one amendment to an existing REQ, and the amendment-log entry, in one
  issue. The conformance contract asks for "a clear, single deliverable". It is one file plus
  one log entry, so it is defensible — but it is the largest issue in the plan and the one whose
  partial completion would be hardest to detect.

  **Recommendation:** acceptable as-is if the issue's deliverable is stated as "the complete
  REQ set for Epic 2, atomically"; otherwise split the REQ-AGENT-021 amendment out, since it
  serves Issue 2.1 (a different file) rather than 2.2–2.4.

## Missing

- No rollback story. If the amended prompts degrade review quality in practice, nothing says how
  that would be noticed or reverted — and prompt regressions are silent by nature. A one-line
  revert note plus "re-measure after the next two plans" would close it.
- The plan measures the classifier but never states what `FP` rate would be *good enough*.
  `FP<=2` appears in R4 as an advisory threshold with no stated basis.

## Gate Assessment

Three gates. The mandatory start gate is well-formed. Both capability gates declare type,
approvers/condition, test, blocks, and instructions.

**Reachability (REQ-AGENT-046, applied to this plan):**

- `Gate: Upstream write` — **reachable**. Blocks `5.1b, 5.2b`; its condition requires artifacts
  produced by `5.1a, 5.2a`, which are outside the `Blocks` set. This was a cycle in the v1 draft
  (blocking `4.1, 4.2` while requiring their output) and is now correctly split.
- `Gate: Evidence corpus` — **reachable**. A pure environment precondition; nothing inside its
  `Blocks` set produces it. Its instructions also declare a degraded fallback, so it cannot
  deadlock the plan.

**Precondition cross-check (REQ-AGENT-047, applied to this plan):** the sibling-repo dependency
for Issue 3.1 is now gated rather than assumed — the one genuine capability gap found. No other
issue references an artifact not produced by a declared predecessor.

## Upstream Assessment

Dispositions are reasonable and the notes justify each. #113 as `partial` is correct and
important — the reconciler comments without closing, so the DAG-walk proposal survives. #109 as
`supersede` is defensible; the disposition maps to close-with-not-planned, which slightly
undersells "verified non-reproducing", but Issue 5.1a authors explicit comment text so the
nuance lands in the comment rather than the close reason. #133 as `exclude` with its own plan is
right — four unresolved design decisions do not belong in this DAG.

The `Resolved By` column is fully wired: every `include`/`partial` maps to at least one issue,
and every mapped issue carries a matching `resolves-upstream` annotation.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | SC6 tests the installed skill, not the repo copy | high | Objective gained a "which copy this plan edits" paragraph; SC4/SC6 pinned to `./skills/yf-plan/...` with the installed copy's current `ci-release`/`high` output recorded; new **SC12** covers install parity after `install.sh --force` | resolved |
| C2 | Epic 2's value rests on a self-graded replay | high | Issue 2.5 now requires the replay to run **in a fresh session with no access to this plan, its findings, or this conversation**, one fixture at a time, with verbatim output recorded. Operator additionally authorized an independent fresh-eyes red-team for pass 2 | resolved |
| C3 | 2.5 never tests that existing checks still fire | high | Issue 2.5 gained a third **regression fixture** (`replay-plan-013-capability.md` — a defect the *current* prompt catches) which must still be flagged; SC7 requires 3 flags; SC10 demoted to advisory with the reason stated | resolved |
| C4 | `1/17` headline open to selection-bias objection | medium | `findings/exp-001` now leads with the unbiased 39/53 full-corpus figure and adds a **bias-control section**: plans 031–038 are 8 consecutive plans, all labeled, so labels are not selected on the classifier's output. Precision 1/8 on that unbiased run | resolved |
| C5 | F2 shipped despite measuring zero benefit | medium | Surfaced to the operator with the measurement; they re-confirmed **keep, with a stop rule**. Issue 3.4 now carries the rule in-code: no keyword joins the blocklist without a corpus re-measurement showing it moves `FP` | resolved |
| C6 | Epic 4 is unstated scope | low | Objective now names the in-flight `reviewer.md` repair and why it is carried here | resolved |
| C7 | Issue 1.1 bundles four SPEC changes | low | Issue 1.1 restated as "the complete REQ set for Epic 2, **atomically**", with the reason a partial landing is worse than a bundle | resolved |

**Final status:** all 7 concerns resolved. Pass 1 frozen. A fresh-eyes red-team (pass 2) follows,
addressing the independence caveat recorded at the top of this file.
