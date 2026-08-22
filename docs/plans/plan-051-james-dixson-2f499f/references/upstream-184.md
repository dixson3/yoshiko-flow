---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #184: yf-plan §3: the red-team is never dispatched as a sub-agent — the drafter reviews its own draft

- **Number:** 184
- **Title:** yf-plan §3: the red-team is never dispatched as a sub-agent — the drafter reviews its own draft
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/184
- **State:** OPEN
- **Labels:** 

## Body

## The defect

`yf-plan` SKILL.md §3 REVIEW never dispatches the red-team as a sub-agent. Compare the two phases:

**§2 INVESTIGATE** (`SKILL.md:315`) — unambiguous:

> Spawn a sub-agent per unknown using `Agent` with `isolation="worktree"`, `mode="bypassPermissions"`. Read `${SKILL_DIR}/agents/investigator.md` for the agent's role...

**§3 REVIEW** (`SKILL.md:488-489`) — read-and-perform:

> 1. **Conformance** — read `${SKILL_DIR}/agents/reviewer.md` and run its mechanical checklist.
> 2. **Adversarial** — once conformance is `PASS`, read `${SKILL_DIR}/agents/red-team.md` and **perform** a structured adversarial review.

Investigate says *spawn*. Review says *read and perform*. Following §3 literally produces a **main-session self-review**: the drafter reviewing its own draft, sharing every assumption it is supposed to attack.

The section header even asserts the opposite (`SKILL.md:487`):

> Two passes, in order. **Both agents are read-only** (REQ-AGENT-043); the main session acts on their verdicts.

It claims two agents exist while the step it governs never creates one.

## Measured consequence (plan-050, this session)

Passes 1 and 2 of plan-050 were performed by the main session — compliant with §3 as written. Pass 3 was dispatched via `Agent` at the operator's explicit request. It returned **REVISE with 11 concerns, 2 high**, over a plan the main session had twice reviewed and advanced to `ready-for-approval`:

- **Epic 4's entire deliverable had no producer seam.** Every `discovered-from` code reference is a *consumer*; the only producers are prose. Its success criterion could not fail — `create one; assert the field is present`, written by whoever creates it.
- **A finding's forward recommendation was falsified by building it.** The successor design would have passed both criteria it was designed to catch, and the corpus denominator was a 61% undercount.
- **Two pass-2 assertions were factually wrong when tested** — a universal claim about the gate DAG that fails for one member, and an exit-code claim (127, not 2).
- **Eight stale issue references** survived a renumbering the main session had declared "re-verified".

None of these are subtle once you look. They were invisible to the drafter and visible to an independent reviewer within one pass. `doc_lint`, `plan_extract` and `audit` were all green throughout.

## Why prose could not prevent this

This is the corpus's own headline from research 004 — *a written rule that nothing executes is unreliably obeyed, and no exit code records the skip* — applied to the review step itself. The same shape as `yf-herdr`'s launch-contract defect, where "if autonomy is wanted, say so explicitly" sat as advisory prose read *after* the prompt was composed.

## Proposed fix

Make §3 imperative and symmetric with §2:

```markdown
2. **Adversarial** — once conformance is `PASS`, **spawn a sub-agent** using `Agent`
   (`subagent_type="general-purpose"`) whose prompt directs it to read
   `${SKILL_DIR}/agents/red-team.md` and follow it. The agent is read-only with respect to the
   repo (REQ-AGENT-043) and returns its review; **the main session writes `reviews/pass-N.md`**.
```

Same for the conformance pass at §3.1.

Worth stating explicitly in the step: a main-session review is **not** a conformant substitute, because independence is the mechanism — not thoroughness.

## Related

- #182 — the read-only rule forbids the sandbox spike. The pass-3 reviewer noted it *"would have declined the spike had the operator not explicitly authorized it"*, so the two compound: the review is both non-independent and, when it is independent, forbidden from testing.
- #174 — a review-phase validation pass. This is the structural precondition for it.
