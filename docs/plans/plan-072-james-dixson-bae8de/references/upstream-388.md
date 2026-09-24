---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #388 - yf-plan: the reconcile gate is poured with EMPTY
  metadata, so a plan.md-declared `Type: auto` gate is treated as human and deadlocks
  §6.4 after the push'
---
# Upstream #388: yf-plan: the reconcile gate is poured with EMPTY metadata, so a plan.md-declared `Type: auto` gate is treated as human and deadlocks §6.4 after the push

- **Number:** 388
- **Title:** yf-plan: the reconcile gate is poured with EMPTY metadata, so a plan.md-declared `Type: auto` gate is treated as human and deadlocks §6.4 after the push
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

The reconcile gate is poured with **empty metadata**, so nothing ever auto-resolves it, and the
§6.4 close chain deadlocks **after the merge and push are already public**.

## Measured, on plan-068's landing

`land --apply` reached `L_RECONCILED` — merge `c476f05` on `main`, `origin/main == main`, all five
upstream corrections posted — then halted:

```
close-reconcile-step exited 1. HALTING: completion stops here and `complete` is NOT set.
  "unresolved_gates": ["yf-mol-cdqp.9"],
  "reason": "the reconcile gate ['yf-mol-cdqp.9'] is not resolved — §6.4's gate-before-close
             ordering constraint (REQ-COMPLETE-004) forbids closing the reconcile bead
             against incomplete execution"
```

The gate as poured:

```
 id/type/status: yf-mol-cdqp.9 gate open
 metadata      : {}
 description   : Blocks reconciliation until execution complete.
```

`plan.md` declares it:

```markdown
### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step
```

All 23 execution tasks were closed. The gate's declared condition read true. It stayed `open`.

## The cause is a self-contradiction inside `SKILL.md`

§5.2a states the rule:

> **Structure the gate at creation — this is what makes the sweep mechanical.** Carry
> `gate_type`, `test`, `test_class` and `cwd` as **metadata fields**, so the §5.2b sweep reads
> fields instead of regexing prose.

Its **own reconcile-gate snippet**, ~60 lines later in the same document, creates the gate with no
metadata at all:

```bash
RECONCILE_GATE=$(bd create "Gate: Reconcile upstream" \
  --description="Blocks reconciliation until execution complete." \
  -t gate --parent ${EPIC} \
  --json | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get id)
```

Absent `gate_type` is treated as `human` (§5.2d: *"`gate_type` absent → treat as `human`, so the
failure mode of a mis-structured gate is a needless prompt, never an unauthorized action"*). That
default is right for capability gates and wrong here: the reconcile gate is the one gate `plan.md`
declares `auto`, and no auto-resolver exists for it.

## Why it is worse than a needless prompt

The ordering makes it a deadlock rather than an interruption. In §6.4, `close-reconcile-step` runs
**before** `close_cascade.py`. The gate's condition — as a reader would interpret "all execution
beads closed" — cannot be satisfied until the containers close, and the containers close at
cascade, which never runs because the chain halted. Without operator intervention the plan cannot
reach `complete`.

And it halts **after** L6's push and L7's reconcile writes, so the irreversible work is already
public when the chain stops. That is #360's class (`land --apply` … halts AFTER the merge and
push), reached by a different route.

## Class

This is `yf-n8fd`'s class — *"the plan.md Gates grammar cannot express test_class or cwd, so every
capability gate defaults to a class that is never run"* — one step further along: here even the
declared `Type:` never reaches the bead.

## Suggested fix

Carry the declared fields onto the reconcile gate at pour, matching §5.2a's own rule:

```bash
RECONCILE_GATE=$(bd create "Gate: Reconcile upstream" \
  --description="Blocks reconciliation until execution complete." \
  -t gate --parent ${EPIC} \
  --metadata "$(jq -nc '{gate_type:"auto", test_class:"probe"}')" \
  --json | ...)
```

and give §6.4 an auto-resolve step for an `auto` reconcile gate whose execution beads are closed —
or state explicitly that the reconcile gate is operator-resolved, and stop declaring it `auto` in
the plan template.

Either fix is fine; the current state — declared `auto`, poured as `human`, halting after the
push — is not.

Found landing plan-068 (tracker #386).

