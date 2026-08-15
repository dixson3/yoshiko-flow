---
type: Review
okf_spec: OKF-PLAN
---
# Plan Red-Team: plan-039-james-dixson-150f79

**Pass:** 4 · **Date:** 2026-08-14

> **Independent pass**, fresh-eyes sub-agent. Tasked with verifying pass-3's resolutions against
> the plan text and finding defects introduced *by* those revisions, under an explicit
> calibration instruction: REVISE only for defects that would break execution, make a deliverable
> unverifiable, or mislead upstream — cosmetic imprecision is not grounds.

## Verdict: REVISE

Eleven of thirteen pass-3 resolutions verify clean, and the plan's quantitative core reproduces
exactly. Two defects were introduced by the pass-3 revisions themselves, both narrow, both
verifiable, both would bite an executor.

## Strengths

- **Issue 3.2's per-step table reproduces exactly, including under the plan's own narrower F2
  list.** The reviewer re-implemented F5 separately from F2 (the scratchpad script folds them and
  uses a wider blocklist than Issue 3.4 specifies): labeled `FP` 16 → 8 → 3 → 2 → 2, corpus
  40 → 22 → 15 → 13 → 13, `FN=0` at every step, `plan-031` surviving. F5's no-class-change claim
  is true, not assumed.
- **Issue 3.4b's four stable-document figures are exact**; removing the plan-039 figure was right.
- **SC6's rewritten properties are the ones that actually hold** — measured: no path marker ⇒
  `confidence: low`, evidence prose-only, three residual signals. Asserting properties instead of
  a count is the correct fix for a document that is its own measurement subject.
- **SC11 and SC1b are both discriminating, verified live.** `evidence` and `code span` occur zero
  times in `spec/cli.md` today, so SC1b cannot pass vacuously.
- **REQ-AGENT-046/047/048 are genuinely unallocated** (`spec/agents.md` runs 040–045 then 050).
- **Corpus split corrected and correct** — 39 + 14 = 53, 8 + 9 = 17 labeled.
- **SC12 is mechanically checkable**; the label is quoted exactly in both 5.3 and SC12.
- **The dependency graph is acyclic and complete** with Epic 1 at three issues — all 20 issues
  resolve, every `depends-on` target exists, no cycles.
- **C2's SC7 rewrite is sound** — genuinely removes the tune-until-green trap without weakening
  2.5's escalation rule.
- **The "Declined explicitly" note is factually correct** — exactly one operator-labeled
  `ci-release` plan exists and it is a true positive, so the audit's population really is empty.
- **C6/C7/C8 and the cosmetic fixes all verify.**

## Concerns

- **P1 — the Approach section still asserts the opposite of the rewritten SC6.** — severity: high

  Approach read "After Epic 3, `classify-deliverable` on this plan must return `standard`. That is
  a success criterion (SC6)"; SC6 now reads "not expected to classify `standard`". Measurement
  agrees with SC6. The C1 resolution repaired the criterion but not the sentence naming it, so
  the plan claimed and denied the same thing — and Approach is what an executor reads first. An
  executor taking it literally concludes Epic 3 failed, and the obvious remedy (add keywords until
  this plan stops matching) is exactly what R3, 3.4's stop rule, and 3.4b forbid. Same defect
  class as H1 and C1, in its third location.

- **P2 — Issue 1.3's `REQ-YF-230` fits nothing in root `SPEC.md`, and SC1's grep for it could not
  pass a conforming edit.** — severity: high

  Root `SPEC.md` has **zero** line-anchored `REQ-` lines; every requirement is a bullet
  `- **REQ-YF-<SUBKEY>-NNN** *(testable)* …` homed in a numbered §3.x section declaring its
  subkey. A bare `REQ-YF-230` has no home. Two concrete consequences: SC1's
  `grep -q '^REQ-YF-230:' SPEC.md` passes **only if the executor breaks the root SPEC's format**;
  and 1.3's "adjust the number if not [unallocated]" latitude directly contradicts SC1's
  hardcoded `230`. A pass-3 artifact — C4 correctly moved the invariant out of the CLI spec, but
  neither the id shape nor the grep was checked against the real target file.

- **P3 — C3 landed in `exp-001`'s banner and Recommendations but not its Implications.** — severity: low

  Implications still said "39/53" and still recommended `FP<=2` — the exact formulation the same
  file's Recommendations now retracts. Plan.md is authoritative and unambiguous, so execution was
  unaffected.

- **P4 — the Motivation's 16/17 phrasing misstates what was measured.** — severity: low

  The classifier suggests `ci-release` on **17 of 17** labeled plans; 16 of those are wrong. The
  headline number described an error rate, not a suggestion rate.

- **P5 — SC2 and SC3 used `…` as a path placeholder.** — severity: low

  Not runnable as written; intent unambiguous, so transcription shorthand rather than an
  unverifiable criterion.

## Missing

- Nothing material. The three pass-3 Missing items are genuinely discharged: SC1b verifies Issue
  1.2 and is discriminating; SC5b pins F5 independently of any plan's prose (the two-document
  backtick fixture tests the transform, not a corpus count); the pre-existing-FP audit is
  declined with a rationale measurement supports.
- R10 narrated passes 1–2 only, while pass 3 also found a high-severity defect inside a prior
  fix. Worth a clause, not a blocker.

## Gate Assessment

Four gates, all well-formed, both capability gates reachable under REQ-AGENT-046. Evidence
corpus: `Blocks: 3.1, 2.5` matches the two issues that read `d3-pxe`; the corpus is present and
the test is responsive rather than always-true; the "no CI run reaches outside the repo" claim
holds. Upstream write: the condition depends on artifacts produced by 5.1a/5.2a, which are
outside the `Blocks` set — reachable; the plan-dir-relative annotation resolves pass-3's residual
imprecision. One observation, not a defect: **Issue 5.3 performs an upstream write no capability
gate blocks** — defensible, since it routes through `/yf-beads-upstream`, whose own contract is
confirm-required and dry-run-first, and the gate's condition is specific to the two drafted
comments. Flagged so the asymmetry is deliberate rather than accidental.

## Upstream Assessment

Dispositions unchanged and sound. `upstream-triage.md` agrees with plan.md row for row on all six
issues. Every `include`/`partial` row is wired to a resolving issue; `resolves-upstream`
annotations are consistent including 3.6's corrected range. The H3 sequencing remains the
strongest upstream property: `5.2b depends-on: 2.5` gates the #113 announcement on evidence
rather than on completion. #109's supersede is honest — the mechanism claim is conceded as
code-true and only the symptom reported as non-reproducing, with the residual `--force` exposure
named. One carried-over risk from P1: shipping the Approach paragraph as written would record in
#108's tracking narrative a self-test the plan's own measured behavior contradicts.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| P1 | Approach asserts the opposite of the rewritten SC6 | high | Approach paragraph rewritten: the plan is an adversarial fixture **for signal honesty, not for a `standard` verdict**. It states plainly that the plan will still classify `ci-release`, that this is the **correct** outcome under the self-reference limit (3.4b), and that SC6 asserts `evidence: prose-only` / `confidence: low` / traceable residuals. The twice-falsified-count history is recorded inline so the lesson travels with the text | resolved |
| P2 | `REQ-YF-230` fits no convention; SC1's grep unsatisfiable | high | Verified against the real file (zero `^REQ-` lines; 13 declared subkeys). Issue 1.3 now homes the requirement in **§3.2 Embedding (`REQ-YF-EMBED`)** — the section governing the shape of the embedded `skills/` tree, which is what the invariant constrains — as the **next free** `REQ-YF-EMBED-NNN`, with **no hardcoded number**. SC1 verifies **id-agnostically** via `grep -qE '^- \*\*REQ-YF-EMBED-[0-9]+\*\*.*frontmatter'`, so 1.3's latitude and SC1 can no longer disagree. 4.2's reference updated | resolved |
| P3 | `exp-001` Implications still stale | low | "39/53" corrected and phrased as 17-of-17-suggested / 16-wrong; Implications #4 folded into the invariant form (`FN=0` + `FP` non-increasing), matching the same file's Recommendations and plan.md R4 | resolved |
| P4 | Motivation's 16/17 misstates the measurement | low | Restated: suggests on **all 17**, **16 of them wrongly**, zero correct negatives. Same fix applied in `exp-001` | resolved |
| P5 | SC2/SC3 used `…` placeholders | low | SC2 rewritten as a runnable loop over the three strings; SC3's second grep spelled out in full | resolved |
| — | Missing: R10 narrates only passes 1–2 | — | R10 rewritten to cover all four cycles, and to encode the two structural lessons rather than leave them to be re-learned: **assert properties, not counts**, against a document still being edited; and **verify an id or command against the real target file**, not its assumed shape | resolved |
| — | Gate: 5.3's ungated upstream write | — | Acknowledged as deliberate, not accidental — 5.3 routes through `/yf-beads-upstream`, whose contract is confirm-required and dry-run-first, and the capability gate's condition is specific to the two drafted comments. No change | accepted |

**Final status:** all concerns resolved. Pass 4 frozen.
