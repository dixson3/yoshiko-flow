---
type: Review
okf_spec: OKF-PLAN
---
# Plan Red-Team: plan-040-james-dixson-1cabe4

**Pass:** 3 · **Date:** 2026-08-16

> **Independent pass** under a strict calibration: REVISE only for a defect that would break
> execution, make a deliverable unverifiable, or mislead upstream — verified by running a command
> or quoting contradicting text. Wording preferences explicitly ruled out as grounds.

## Verdict: APPROVE

Every pass-2 resolution verified against the plan text an executor reads, not the resolution
table, with the named commands actually run. All seven D-concerns and both Missing items are
genuinely resolved, and the revisions introduced no defect meeting the REVISE bar.

## Strengths

- **D3 verified by execution** — `manifest_update.py skills/yf-beads-upstream/protocols --dry-run`
  exits 0 printing exactly `manifest_update: no changes (all hashes match)`, the literal string SC5
  asserts; `yf preflight yf-beads-upstream --json` returns `rule.outcome: ok`.
- **D1 clean, including the scope boundary** — 2.3 owns GR-BUP-001/REQ-BUP-030, 2.6 owns
  GR-BUP-002/REQ-BUP-031, confirmed against `SPEC.md:269/273`. No two issues edit the same
  guardrail.
- **D2 jointly satisfiable** — SC4's narrowed form (`BACKEND_AUTH` → 0, no `add_argument("--backend"…)`)
  is compatible with SC14's named-error requirement via manual argv inspection. Baselines honest:
  `BACKEND_AUTH` alone greps to 2, the combined pattern to 7.
- **D4's producer chain is real** — 2.2 specifies drop-reporting, 3.4 asserts it, R6 names 2.2.
- **D5 fully swept** — remaining "3.3" occurrences are all correct (its own heading, `3.4
  depends-on`, R7's historical note, R8's provenance, 3.4's parenthetical).
- **D6/D7 verified** — context.md says three skills and no label-write scope; 4.1 says stop calling
  `external_for`, do not delete it (correct: `:460`, `:495` outside `closable`).
- **Graph acyclic, 19 nodes, no dangling targets** — 1.1 → 2.1…2.7, forking to 3.1…3.4 and
  4.1…4.4, rejoining at 5.1 → 5.2a → 5.2b. Counts 1+7+4+4+3 = 19, matching R8.
- **The C2 relocation re-verified independently** — `SKILL.md:688` is §5.2a, `:724` runs
  `record-epic`, `:842` is §5.2b, `:664` confirms `resume-scan` reads the `**Epic:**` field.

Minor observations, none grounds for revision: `SPEC.md:165`'s misreference sits in a passage about
a hand-run push (GR-BUP-005's drift), and 2.3 does not name the replacement — an executor picks it
from context. SC5's preflight clause reads the *installed* rule, so the `--dry-run` clause is the
load-bearing one. `findings/exp-001`'s closing paragraph still frames the pre-reversal choice,
under the correction banner. plan.md cites `beads_hygiene.py:551/579` (enclosing docstrings; argv
is built at `:584`).

## Concerns

None at the REVISE bar.

## Missing

Nothing blocking. SC9's first clause depends on a plan being filed after 4.3 lands; its second is
verifiable within this plan, and 4.3's §5.2b resume branch gives plan-040 itself a path to
exercise the first.

## Gate Assessment

**Start Gate** — well-formed. **Scratch write** — reachable; Test correctly relabelled a smoke
check proving read access not consent, and the ungated alternative now matches the current
decision with an honest consequence. **Upstream write** — reachable; `Blocks: {5.2b}` with
evidence from 5.2a and 4.2, both outside the Blocks set; repo-root-relative test clauses resolve.
**Reconcile Gate** — correct type, with annotations on 3.4/4.3/4.4/5.2b to act on.

**Precondition cross-check:** no unmet preconditions. 4.1 sits after 2.7 so REQ-BUP-052's
amendment precedes the `closable` contract change; 3.1's inputs are all upstream; 4.4's
plan→tracker map has a declared producer inside 4.4; 5.2b's drafts come from 5.2a.

**Premise check:** the one load-bearing inference is isolated in Issue 1.1 with a falsification
test covering both halves and a four-outcome table binding each result to a consequence. The two
`[measured]` figures the criteria depend on re-confirmed: REQ-BUP count 35, combined
`--backend`/`BACKEND_AUTH` count 7.

## Upstream Assessment

`upstream-triage.md` and plan.md agree on all nine dispositions; the stale Resolved-By range is
corrected. The three `include`s are one mechanism. #132's supersede is the only close, last in the
chain behind a draft-then-publish split, with SC11b enumerating all five drafts and SC11 asserting
the other four stay `OPEN`. R5's softening is accurate against `SPEC.md:279`. #117's
partial-discharge reasoning matches REQ-BUP-052's recorded partial. **No upstream claim in this
plan overstates what it delivers.**

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| — | No concerns raised at or above the REVISE bar | — | Verdict is APPROVE; nothing to resolve | n/a |

**Final status:** APPROVE. Pass 3 frozen. This is the last recorded verdict, so `ready-check`'s
REQ-PLAN-030 precondition is satisfied.
