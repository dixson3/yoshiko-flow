plan-039 shipped this issue's **cheap precursor** and is leaving the issue open, re-scoped
to the DAG-walk engine only. Recording what shipped, what did not, and the evidence for the
split — this is a narrowing, not a closure.

## What shipped

A **prose precondition cross-check** in the red-team pass, as `REQ-AGENT-047`:

> For each issue, are the artifacts, tools, and capabilities its text assumes either
> produced by a declared `depends-on` predecessor or established by a gate? Report each
> unmet precondition with the node that needed it.

One bullet in `skills/yf-plan/agents/red-team.md`. No schema change, no engine.

It was replayed against a reconstruction of this issue's own Epic 6 defect — plan-013's
pre-fix Epic 6, which re-audits "the hardened tree" with no `depends-on` on Epics 1–5 — in a
fresh session with no access to the plan that built it and no statement of what it was
looking for. It flagged the defect at high severity:

> Epic 6 has no declared dependency on Epics 1–5, yet its every issue presupposes their
> completion. […] Nothing prevents 6.1 from being claimed and run against an unhardened tree
> the moment the Start Gate opens. […] **The failure is silent — every issue closes green
> and the output is wrong.**

and recommended `depends-on: 1.4, 2.3, 3.4, 4.2, 5.4` — the same remedy plan-013 actually
adopted.

## What did not ship, and why

**The topological DAG walk and the `requires:` schema key.** Both remain this issue's live
proposal. The evidence against building them *now*:

**1. No observed defect required a `requires:` key.** Reading the as-landed plan-013 — the
source of all the defects tabulated here — every accepted remedy was expressible in today's
schema:

| Defect | Remedy as landed |
| :-- | :-- |
| Issue 3.4 asserted two tools pass on its output but depended on neither | `depends-on` edges |
| Epic 6 re-audits the hardened tree with no dependency on Epics 1–5 | `depends-on` edges |
| Success criteria required SSH to 9 hosts + a secret env no gate declared | a capability gate |
| Issue 3.4's output would fail a check installed by Issue 1.1 | reorder / dependency |
| Gate condition unreachable from its own `Blocks` set (#112) | split the issue, rewire the gate |

**2. The missing artifact was the edge, not the declaration.** In every case the
precondition was already written out in plain English in the issue body. Only the
machine-readable dependency was absent. A prose-vs-DAG cross-check therefore has enough
information to catch these without anyone authoring a new field.

**3. Two of the five are not reachability failures at all** — one capability gap, one
semantic conflict (an issue's output failing a check an earlier issue installs). Neither is
found by a graph walk. That weakens the "mechanical, pass/fail, therefore conformance"
framing in this issue's original proposal, and is why the check landed in the red-team
(judgment) pass rather than the conformance (mechanical) pass.

## The caveat this issue raised about itself still stands

The original `n=1` caveat survives intact. Everything above is drawn from **one plan** in
one repository by one operator. The prose check has now been observed to fire on exactly one
reconstructed instance of this defect class. That establishes it *can* fire; it does not
establish a rate, and it does not establish that a DAG walk would add nothing.

plan-039 filed a deferred **re-measure checkpoint** for precisely this: after the next two
plans complete, compare defects-found-per-review against the plan-013 baseline (4 found, 1
escaped) and record the result. That is the second-plan evidence this issue asks for, and it
is the input that should decide whether the engine is worth building.

## Disposition

Staying **open**, narrowed to: *should yf-plan add a topological DAG-walk pass and a
`requires:` schema key, given that the prose cross-check already ships?* Revisit when the
re-measure checkpoint reports.

Evidence: plan-039 `findings/exp-002-precondition-inferability.md`,
`references/replay-results.md`.
