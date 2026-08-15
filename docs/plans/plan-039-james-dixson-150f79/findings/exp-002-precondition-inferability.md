---
type: Finding
okf_spec: OKF-PLAN
---
# Finding: Does an execution-rehearsal pass need a `requires:` schema change, or can preconditions be inferred from plan prose?

**Experiment:** EXP-002 · **Date:** 2026-08-14 · **Issue:** [#113](https://github.com/dixson3/yoshiko-flow/issues/113)

Findings are marked **[measured]** / **[inferred]** per the [#114](https://github.com/dixson3/yoshiko-flow/issues/114) convention.

## Approach Tested

#113's central open question, and the reason it was scoped as an investigation rather than
built directly:

> Requires issues to declare preconditions more explicitly than today. That may be the real
> cost: a lightweight `requires:` alongside `depends-on:` … it could be inferred from prose by
> an LLM pass instead, trading rigour for zero authoring burden.

The test: read the **as-landed** `plan.md` of `d3-pxe` plan-013 — the source of all four defects
#113 tabulates — and determine, for each defect, (a) whether the precondition was recoverable
from the prose already written, and (b) what the accepted remedy actually was.

`plan-013` is available locally at
`~/workspace/dixson3/d3-pxe/Incubator/ansible/plans/plan-013-james-dixson-1692d0`. Read-only;
nothing in d3-pxe was modified.

## Result

### Every observed remedy was expressible in today's schema **[measured]**

| Defect (#113's table) | Precondition stated in prose? | Remedy as landed |
| :-- | :-- | :-- |
| Issue 3.4 asserted two tools pass on its output but depended on neither | Yes — the assertion names both tools | added `depends-on` edges |
| Epic 6 re-audits "the hardened tree" with no dependency on Epics 1–5 | Yes — "the hardened tree", "the new gates' actual output" | added `depends-on: 1.5, 2.3, 3.4, 4.2, 5.4` |
| Success criteria required SSH to 9 hosts + a secret env no gate declared | Yes — the criteria name the hosts and the env | added a capability gate |
| Issue 3.4's output would fail a check installed by Issue 1.1 | Yes — 1.1 specifies the check; 3.4 specifies the output | reordered / added dependency |
| Gate condition unreachable from its own `Blocks` set (#112) | Yes — condition and `Blocks` both stated | split issue into `5.1a`/`5.1b`, rewired gate |

Epic 6 as landed **[measured]** — the fix is a dependency edge plus a rationale note, no new
schema:

```
- **Issue 6.1:** Re-run the full `ansible/`-vs-SPEC structure audit against the hardened tree,
  using the new gates' actual output as evidence rather than reading by eye.
  - depends-on: 1.5, 2.3, 3.4, 4.2, 5.4
  - Note: the dependency set is the terminal issue of each of Epics 1–5. A re-audit that runs
    before the hardening lands would re-measure the tree this plan set out to change, and its
    A–D verdict would be worthless.
```

### The missing artifact was the **edge**, not the **declaration** **[inferred]**

In all five cases the precondition was written down in the issue body in plain English. What
was absent was the machine-readable `depends-on` edge asserting it. **[inferred]** A pass that
compares *stated* preconditions against the *declared* DAG has enough information to catch every
observed defect. A `requires:` schema would have made the same information easier to parse — it
would not have made otherwise-invisible information visible.

### Two of the five are not reachability failures at all **[measured]**

- "success criteria required SSH + secret env" is a **capability** gap — no DAG edge expresses
  it; the remedy was a gate.
- "3.4's output would fail 1.1's check" is a **semantic** conflict — 3.4 and 1.1 could be
  correctly ordered and the defect would persist.

**[inferred]** So "topological walk carrying running state" describes at most 3 of the 5. The
other 2 need domain reasoning about what each step *produces* and what each check *rejects* —
which is an LLM judgment, not a graph algorithm. #113's framing as a mechanical pass-fail check
is only partly supported by its own evidence.

### The plan corpus is one plan deep **[measured]**

`d3-pxe` holds 9 plans, but the four-defect tabulation comes from plan-013 alone; plan-014
supplies #114's single premise defect. No second plan's review artifacts contradict or confirm
the 4-of-4 rate. #113's own caveat ("one plan's evidence") stands unchanged after this
experiment.

## Implications for Plan

1. **The expensive branch is not justified yet.** The `requires:` schema change — #113's named
   "real cost" — is not required to catch any observed defect. Building it now would be
   speculative.
2. **The cheap branch is well-supported and mostly prose.** A precondition-vs-DAG cross-check
   is an LLM reading task over artifacts that already exist, with no authoring burden and no
   schema change. It belongs in a review prompt, not a new script.
3. **#113's "mechanical, pass/fail, therefore conformance" argument is weakened.** 2 of 5
   defects need judgment. That argues for red-team (or a judgment-capable third pass), not the
   mechanical conformance reviewer — and it aligns with the operator's decision to put #112's
   reachability item in red-team for now.
4. **#113 should not be closed by this plan.** The evidence supports a prose cross-check now and
   defers the DAG-walking script; #113 stays open, re-scoped, pending a second plan's data.

## Recommendations

- Add a **precondition cross-check** to the red-team prompt: for each issue, are the artifacts,
  tools and capabilities its text assumes either produced by a declared `depends-on` predecessor
  or established by a gate? Report each unmet precondition with the node that needed it.
- Do **not** build the topological-walk script or the `requires:` schema in this plan.
- Update #113 with this finding, re-scoping it to the DAG-walk script only, and record that the
  prose cross-check has shipped as its cheap precursor.
- Revisit after a second plan's review artifacts exist, as #113's caveat asks.
