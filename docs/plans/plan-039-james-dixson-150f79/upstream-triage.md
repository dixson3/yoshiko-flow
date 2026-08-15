---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: Raise yf-plan review quality: gate reachability, premise verification, and deliverable-class classifier accuracy

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #108 — yf-plan: deliberate-class heuristic false-positives ci-release on ordinary infra plans

> Follow-up to #89, which introduced the `ci-release` deliverable class (REQ-PLAN-069a).

`_classify_deliverable()` (`scripts/plan_manager.py`) suggested **`ci-release` with `confidence: high`** on two ...

**Disposition:** include

**Notes:** All four fixes adopted, plus F5 added during review. EXP-001 measured the defect at 16/17 labeled plans and 40/53 corpus-wide, far above the reported n=2. Resolved by 3.1-3.6.

## #112 — yf-plan: red-team should check gate REACHABILITY, not just gate well-formedness

> ## The defect this would have caught

In `d3-pxe` plan-013, a capability gate was authored like this:

- **Condition:** operator has previewed `ansible-playbook host.yml --check --diff --tags otel_age...

**Disposition:** include

**Notes:** Gate-reachability item lands in red-team Evaluate (REQ-AGENT-046). Resolved by 2.2; fixture-verified by 2.5.

## #113 — yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)

> ## Observation

Across `d3-pxe` plan-013, four real defects were found in review. **All four are the same class**, and one escaped every pass:

| Found by | Defect |
| :-- | :-- |
| Conformance | Issu...

**Disposition:** partial

**Notes:** IN: the prose precondition cross-check (2.4). OUT: the DAG-walk engine and the `requires:` schema - EXP-002 found no observed defect needed them. Issue stays OPEN, re-scoped by 5.2a/5.2b.

## #114 — yf-plan: verify the PREMISES a plan rests on, not just its internal consistency (measurement vs inference)

> Split out of #113 as a distinct axis. #113 covers **structural** correctness — does the DAG hold together, is each precondition available when its step runs. This issue covers **factual** correctness ...

**Disposition:** include

**Notes:** Two prompt additions exactly as proposed - investigator (2.1) and red-team premise check (2.3).

## #109 — yf-plan: stale_approved is computed status-independently, so completed plans display "re-review before execute" forever

> `plan_manager.py list` (and `status`) tag a **completed** plan with:

```
⚠ STALE-APPROVED (re-review before execute)
```

For a plan in a terminal state this advice is not merely noisy, it is wrong: ...

**Disposition:** supersede

**Notes:** Does not reproduce: 0/38 completed plans display the tag (EXP-003). Mechanism claim is code-true but the display path is unreachable. Closed with that distinction recorded, not silently (5.1a/5.1b).

## #133 — yf-beads-upstream design: replace 'bd <backend> push' with gh-direct issue creation across push/hoist/land (bd reads beads, gh writes issues)

> ## Proposal

Change the upstream mechanism to: **`bd` reads bead content, `gh` creates and updates issues, `bd update --external-ref` records the mapping.** Apply across all three write paths — `push`...

**Disposition:** exclude

**Notes:** Materially different surface (yf-beads-upstream mechanism swap) with four unresolved design decisions. Gets its own plan.
