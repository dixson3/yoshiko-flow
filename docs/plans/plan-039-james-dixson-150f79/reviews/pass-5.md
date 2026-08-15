---
type: Review
okf_spec: OKF-PLAN
---
# Plan Red-Team: plan-039-james-dixson-150f79

**Pass:** 5 · **Date:** 2026-08-14

> **Independent pass**, fresh-eyes sub-agent, under an explicit strict calibration: REVISE only
> for a defect that would break execution, make a deliverable unverifiable, or mislead upstream,
> and only when verified by running a command or quoting contradicting text. Wording preferences
> and stylistic inconsistency were explicitly ruled out as grounds.

## Verdict: APPROVE

Pass-4's two high-severity concerns are genuinely resolved — verified against the real files, not
the resolution table. The three low ones are resolved too. No defect introduced by the pass-4
revisions meets the bar. The plan's quantitative core re-reproduces exactly on a fresh run.

## Strengths

- **P1 is genuinely fixed, not paraphrased.** The Approach paragraph now asserts the same thing
  SC6 asserts, in the same direction — the plan is a fixture for signal *honesty*, will still
  classify `ci-release`, and that is the correct outcome. The contradiction is gone in both
  locations, and the twice-falsified-count history travels with the text.
- **P2 is fixed correctly, and the id convention was checked against the actual file.** Root
  `SPEC.md` has zero `^REQ-` lines; §3.2 is `### 3.2 Embedding (REQ-YF-EMBED)` with `-001`/`-002`
  allocated, so "next free" is unambiguous and 1.3 correctly declines to hardcode. The homing is
  licensed by the file itself — §2 states the macro spec is authoritative for **cross-skill
  invariants**, which is exactly what a repo-wide frontmatter rule is.
- **SC1's rewritten regex actually matches the bullet form, verified by running it** — matches a
  conforming bullet, does not match today's `SPEC.md`. Discriminating, and it cannot pass
  vacuously. SC1's other grep correctly uses the *different* convention `spec/agents.md` really
  uses (line-anchored `REQ-AGENT-NNN:`, 22 such lines). The plan now distinguishes the two files'
  conventions rather than assuming one.
- **REQ-AGENT-046/047/048 are still unallocated.**
- **The classifier baseline reproduces exactly** — independent re-run over the 53-plan corpus:
  `corpus=53 ci=40 labeled=17 TP=1 FP=16 TN=0 FN=0`, matching Motivation, EXP-001, and Issue
  3.2's baseline row to the digit.
- **Every success criterion is discriminating today** — each fails before the work, so none can
  pass vacuously: SC1b's `evidence`/`code span` occur 0× in `spec/cli.md`; SC8's greps match 0
  lines; SC11 exits `1` on the unrepaired `reviewer.md`; SC2's three strings are absent from
  `red-team.md`; `grep -c 'plan-039' SPEC.md` → 0. SC10's advisory bound holds with headroom
  (60 lines against 80).
- **P3/P4/P5 verify** — `exp-001` Implications corrected and folded to the invariant form,
  Motivation restated, SC2 now a runnable loop and SC3 spelled out (both executed; no
  placeholders remain).
- **Dependency graph still sound** — 23 issues, 18 `depends-on` lines, every target exists, no
  cycles, Epics 2 and 3 serialized as stated, 4.2 correctly after 3.6.
- **R10 now narrates all four prior cycles** and encodes two structural lessons rather than
  leaving them to be re-learned — the correct response to a plan on its fifth pass.

## Concerns

None at or above the bar. Nothing found would break execution, leave a deliverable unverifiable,
or put a false claim upstream.

Two minor observations were raised and are **not** concerns; both were nonetheless applied:

- SC1's regex required `frontmatter` on the same physical line as the REQ id, while root
  `SPEC.md` wraps bullets at ~100 chars. Satisfiable, and the failure would be loud and
  self-correcting — but split into two greps so a wrapped bullet passes.
- `context.md`'s glossary omitted F5, and `log.md` carried a duplicated `review: review:` prefix.
  Both fixed; a `self-reference class` glossary entry was added at the same time, and
  `context.md`'s sibling-repo note was aligned with the gate (it now names both 3.1 and 2.5 and
  drops the "discharged permanently" overclaim).

## Missing

Nothing material. The pass-3 and pass-4 Missing items are all discharged: SC1b verifies Issue
1.2; SC5b pins F5 independently of any corpus count; the pre-existing false-positive audit is
declined with a rationale the measurement supports (exactly one operator-labeled `ci-release`
plan exists and it is a true positive — confirmed `TP=1`); R10 covers all cycles.

## Gate Assessment

Four gates, unchanged by the pass-4 revisions and still sound. **Evidence corpus:**
`Blocks: 3.1, 2.5` covers both issues that read `d3-pxe`; the test is responsive rather than
always-true (pass-2's BSD `wc -l` padding defect fixed); documented degraded fallbacks exist for
each blocked issue; the "no CI run reaches outside the repo" claim holds because 3.1 vendors the
fixtures. **Upstream write:** the condition depends on artifacts produced by 5.1a/5.2a, which sit
outside the `Blocks` set — reachable under the plan's own REQ-AGENT-046, correctly dogfooded,
with the plan-dir-relative annotation intact. Start and Reconcile gates are conventional. Issue
5.3's ungated upstream write remains an accepted asymmetry: it routes through
`/yf-beads-upstream`, whose contract is confirm-required and dry-run-first.

## Upstream Assessment

Dispositions unchanged and sound; `upstream-triage.md` agrees with plan.md row for row on all six
issues. Every `include`/`partial` row is wired to a resolving issue, and the `resolves-upstream`
annotations are internally consistent. The P1 fix removes the one upstream hazard pass-4 named:
with the Approach paragraph corrected, nothing in the plan would record in #108's narrative a
self-test its own measured behavior contradicts. #113's `partial` is honest — 5.2a/5.2b re-scope
and leave it open, and `5.2b depends-on: 2.5` means the "cross-check shipped" announcement cannot
publish before the fixture proves the check fires. #109's `supersede` concedes the mechanism
claim as code-true and reports only the symptom as non-reproducing, naming the residual `--force`
exposure.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| — | No concerns raised at or above the REVISE bar | — | Verdict is APPROVE; nothing to resolve | n/a |
| — | Minor: SC1 regex brittle against a wrapped bullet | observation | Split into two greps (`^- \*\*REQ-YF-EMBED-[0-9]+\*\*` plus a `frontmatter` grep) so a wrapped edit passes | applied |
| — | Minor: `context.md` glossary omits F5; `log.md` duplicated prefix | observation | F5 and `self-reference class` glossary entries added; log prefix de-duplicated; `context.md`'s sibling-repo note aligned with the gate (names 3.1 **and** 2.5, drops the "discharged permanently" overclaim) | applied |

**Final status:** APPROVE. Pass 5 frozen. This is the last recorded verdict, so `ready-check`'s
REQ-PLAN-030 precondition is satisfied.
