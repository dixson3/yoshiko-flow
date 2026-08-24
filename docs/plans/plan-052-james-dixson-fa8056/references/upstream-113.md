---
type: Reference
okf_spec: OKF-PLAN
id: upstream-113
description: Upstream issue #113 — yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)
---

# Upstream #113: yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/113
- **State:** OPEN
- **Labels:** none

## Body

## Observation

Across `d3-pxe` plan-013, four real defects were found in review. **All four are the same class**, and one escaped every pass:

| Found by | Defect |
| :-- | :-- |
| Conformance | Issue 3.4 asserted two tools pass on its output, but depended on neither — they would not exist when it ran |
| Conformance | Epic 6 re-audits "the hardened tree" but declared no dependency on Epics 1–5, so the DAG permitted it to run first |
| Red-team pass 1 | Two success criteria required SSH to 9 hosts + a full secret env that no gate declared |
| Red-team pass 2 | Issue 3.4's committed output would have failed a check installed by Issue 1.1, and would have enrolled a non-existent CT in a fleet-wide play, breaking every subsequent converge |
| **Nothing** | A capability gate's condition was unreachable from what it blocked (see #112) |

Every one is **a claim about execution-time state that was never checked against what will actually be true at that point in the DAG.**

## Why the existing passes structurally cannot catch these

Both current passes evaluate artifacts **statically**:

- `agents/reviewer.md` — is each element present and well-formed? Is the graph acyclic?
- `agents/red-team.md` — is the approach sound, are risks plausible, are gates needed?

Neither walks the plan **forward in time**. "The dependency graph is acyclic" is checked; "at step N, does everything step N needs actually exist yet" is not. Acyclicity is necessary and nowhere near sufficient.

Patching the checklist per-symptom does not generalise — adding a gate-reachability item (#112) catches that one bug, but would not have caught the phantom-host case, and the next variant will be something nobody enumerated.

## Proposal: an execution-rehearsal pass

Walk the bead DAG in topological order carrying a running state — which files exist, which scripts have been written, which properties have been proven, which capabilities (credentials, network reachability, authorisations) are available — and at each node check its declared preconditions against that state.

Falls out for free:

- **Gate reachability** — a gate whose `Condition` requires evidence produced inside its own `Blocks` set is a cycle the walk hits immediately (#112).
- **Tool-before-use** — an issue invoking a script authored later.
- **Capability gaps** — a success criterion or issue needing credentials/network that no gate declares and no prior step establishes.
- **Self-invalidating output** — an issue whose deliverable violates a check installed by an earlier issue.

## Design notes

- **Mechanical enough to be pass/fail**, which argues for the conformance reviewer rather than red-team. But it needs the *full* DAG, so it must run after epics/dependencies are drafted — later than conformance currently sits. Either move conformance, or add this as a distinct third pass between conformance and red-team.
- Requires issues to declare preconditions more explicitly than today. That may be the real cost: a lightweight `requires:` alongside `depends-on:` (distinguishing "ordering" from "needs this artifact/capability"). Worth scoping before committing — it could be inferred from prose by an LLM pass instead, trading rigour for zero authoring burden.
- Should report the same `PASS | INCOMPLETE` shape as the conformance reviewer, listing each unreachable precondition with the node that needed it.

## Relationship to #112

#112 is the cheap targeted patch for the one escaped defect — worth doing immediately and independently. This issue is the structural fix that subsumes it. If this lands, #112's checklist item becomes redundant.

## Caveat

One plan's evidence. Four defects, one escape, all in this class — suggestive, but a second plan's data should be gathered before investing in the `requires:` schema change.

