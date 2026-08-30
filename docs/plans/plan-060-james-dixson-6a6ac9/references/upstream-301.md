---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #301 - yf-plan: the close chain stops at ''complete''
  — merge-back, pruning, reconcile writes, bead mirroring and redeploy are all manual'
---
# Upstream #301: yf-plan: the close chain stops at 'complete' — merge-back, pruning, reconcile writes, bead mirroring and redeploy are all manual

- **Number:** 301
- **Title:** yf-plan: the close chain stops at 'complete' — merge-back, pruning, reconcile writes, bead mirroring and redeploy are all manual
- **URL:** 
- **State:** OPEN
- **Labels:** type::feature, priority::high

## Body

## The close chain ends at `update-status complete`. Everything after it is manual.

`test_close_contract.py --list-steps` enumerates **12** steps — `audit-close`, `retrospective-report`, `judgement-never-fired-report`, `classify-deliverable`, `set-deliverable-class`, `close-reconcile-step`, `verify-reconcile`, `recheck-criteria`, `close_cascade.py`, `complete-gate`, `pour_fidelity.py`, `update-status`.

All twelve operate on the **plan document and its bead tree**. Not one touches git, the worktree, the harness, or upstream. So a plan reaches `complete` with its branch unmerged, its worktree live, its herdr tab open, its reconcile comments unposted, its residual findings unmirrored, and the installed toolchain still carrying pre-plan engines.

`landing-lock` already exists as a verb (single-machine merge-back serialization), so merge-back is a recognised concept in the CLI that was never carried through to an actual landing.

## Measured: landing plan-057 took ELEVEN separate operator instructions

Each asked for explicitly, one at a time, *after* the plan was already `complete` and verified green:

1. merge to `main` · 2. push · 3. close the branch, worktree and herdr tab · 4. mark the plan complete · 5. close the upstream issues · 6. open issues for the open concerns · 7. close the execution beads · 8. push residual findings upstream · 9. group those findings into coherent issues · 10. clean up a stray molecule · 11. `yf self install`

Then a twelfth round trip to answer *"when can we close `.9` and `.10`?"* — whose real answer was **"post the four reconcile comments"**, a step already implied by the merge that had simply never been done.

One conceptual operation — *land this plan* — decomposed into a dozen prompts.

## The design insight

**Authorizing the merge IS the authorization.** When an operator says "merge this plan to `main`", they have already decided the plan is done. Everything downstream is mechanical consequence of a decision already taken. Re-soliciting consent per step buys nothing except attrition — and attrition is the condition under which an operator starts rubber-stamping, which is the precondition for #293.

The genuinely outward-facing subset still needs consent, but it should be **enumerated up front and batched into that one grant**. *"Here are the 4 comments I will post, the 1 issue I will close, the 5 I will file — approve the landing"* is **more** informed consent than eleven separate yes-es, at one round trip instead of eleven.

---

# RECOMMENDED DESIGN: three layers, with the agent unable to write

A mechanical verb alone is not sufficient — landing has a judgement-laden core (see below). But an agent that both decides *and* acts would be the highest-privilege role in the system, with write authority over `main`, the upstream tracker, the worktree set and the installed toolchain. #293 is an executing agent closing a consent gate by writing its own authorization into the close reason. **Do not build a second, larger version of that.**

Split the responsibility three ways:

| Layer | Produces | Authority |
| :-- | :-- | :-- |
| `plan_manager.py land --dry-run` | the **facts** — manifest, exit codes, merge preview, enumerated writes with their bodies | reads only |
| **`lander` agent** | a **decision document, not commands** — a data structure | **read-only against the repo** (`REQ-AGENT-043`) |
| `plan_manager.py land --apply <decision.json>` | the **execution** | the only layer that writes |

The agent therefore **cannot fabricate an authorization, because it never issues a write**, and **cannot close a gate** — the verb does, and only when the verb re-derives the condition itself. That is a *structural* answer to #293 rather than a procedural one.

It also slots into the existing architecture: `skills/yf-plan/agents/` already carries `reconciler.md`, `captor.md` is already marked read-only, and "the main session writes every artifact" is already the house convention.

### What the `lander` agent adjudicates — and why a script cannot

Five decisions from plan-057's landing, all measured:

1. **Grouping 15 residual beads into 5 coherent upstream issues.** `zeyz`/`pctx`/`2yo2` belong together because they share a *cause* — `plan_extract.py` is the sole reader of `plan.md` and nothing diffs the read against the source — not because they share a filename. One-issue-per-bead violates `AGENTS.md`'s coarse policy; one-issue-for-all is useless.
2. **Refusing an instruction that was literally wrong.** The operator said *"close the upstream issues."* Every plan-057 row is `partial`, `deferred` or `exclude` — **none is `include`** — and `partial` means the issue stays open. A script obeying that closes #140/#170/#171/#189 and contradicts the dispositions the plan was approved with. Correct action: close **one** (#290, genuinely fixed) and explain why the rest stay open.
3. **Noticing a mechanical condition had gone falsely true.** Closing Issue 3.5 as *deferred* made the reconcile gate's condition (`all execution beads closed`) read true while its four comments were unposted. Only `verify-reconcile`'s exit 1 disagreed.
4. **Cross-plan sequencing.** D-13 required plan-059 to land before plan-057, for a reason (`index.md` contention, a settled `_INDEX_MEMBERS`) that lives in a risk row, not any machine-readable field.
5. **Judging whether the reconcile bodies were accurate** before posting them outward.

### The operator-attention argument

The payoff is not automation. It is that **one consent prompt on an adjudicated, annotated manifest is better than eleven prompts on raw mechanical steps** — in information conveyed *and* in the probability the operator reads it. The agent's job is to make the single prompt worth reading.

---

## Execution order, and the constraint that makes it safe

**Preflight** — `--dry-run` enumerates everything and stops. Then, on one grant:

1. **Document close** — the existing 12-step chain, unchanged
2. **Reconcile writes** — post the pre-authored comments for every non-`exclude` row until `verify-reconcile` exits 0, each **verified by read-back** (`gh` returned exit 0 on a wrong body this session — #292 carried uppercase `BLIND` against a case-sensitive test)
3. **Bead close-out** — close the execution tree; **refuse** to close a gate whose condition does not hold; mirror residual open beads upstream with `external_ref` set, grouped per the agent's adjudication
4. **Merge-back** — `--no-ff`, re-run the FULL validation tier **on the merged tree before pushing** (plan-058 landed red because nobody did)
5. **Prune** — remove the worktree, delete the branch local and remote, close the herdr tab **only if this session created it**
6. **Redeploy** — `yf self install --from-build --build --force` if the landed change touched `skills/`, which is otherwise silently deferred and leaves every session on stale engines

Fail closed at any step; never proceed past a red FULL tier.

**Order is load-bearing, not stylistic.** Step 3 must not close a gate in order to satisfy step 4. Measured: the reconcile gate `yf-mol-4jb2.9` was correctly left open by the executing agent while Issue 3.5 was open; closing 3.5 as *deferred* then made the gate's mechanical condition read **true** while the work was undone. `verify-reconcile` was the only honest signal. **A `land` verb that closes beads before running `verify-reconcile` automates exactly that error.** Reconcile writes first, then bead close-out, then merge.

## Why an issue, not a retrospective or a rule

- **Not a retrospective** — it dies with its plan; this recurs on every plan.
- **Not a rule alone** — a rule can bind a trigger but cannot create a verb, and the failure is that the verb does not exist. A rule saying "also do these eleven things" is a checklist an agent will partially honour, which is how the drip-feed happened.
- **An issue, then a rule** — build the verb and the agent, then bind them with a rule that fires on merge-back intent.

## Related

- **#293** — a consent gate closable by asserting consent. The three-layer split above is the structural fix for that class, not just for this one.
- **#295** — plan-057's residue, which exists *because* landing was manual.

