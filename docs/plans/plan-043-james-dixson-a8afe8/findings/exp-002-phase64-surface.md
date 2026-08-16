---
type: Finding
okf_spec: OKF-PLAN
id: exp-002-phase64-surface
plan: plan-043-james-dixson-a8afe8
created: '2026-08-16'
---

# E2 — The actual implementation surface of Phase 6.4

**Question.** What does the hook contract attach to?

**Answer.** Nothing — there is no seam. Phase 6.4 is **prose in `SKILL.md` that an LLM
executes**, calling four flat CLI verbs. There is no orchestrator, no registry, no plugin
dir, no step table. `plan_manager.py --help` lists 22 commands; there is no `complete`,
`close`, `reconcile`, or `land` verb.

Repo and deployed skill **agree** on the 6.4 surface — the only `SKILL.md` delta is the
one-line install stamp; `scripts/`, `spec/`, `SPEC.md` are identical.

## "Hook" is the wrong word, and the repo says so

`grep -rni "hook" skills/yf-plan/` returns exactly **two** non-fixture hits, and both are
**prohibitions**:

- `SKILL.md:1219-1220` — *"This is a **portable, documented script-verb step** — never a
  harness hook or scheduler"*
- `SPEC.md:197` — *"(a documented script-verb call, never a harness hook or scheduler)"*

So the plan's deliverable is **a documented script-verb step convention**, not a
Claude-Code-style hook. If plan-043 wants a real code seam, *creating* it is the deliverable
— it does not exist to be extended.

## What 6.4 actually runs

| # | Component | Returns | Caller behavior |
| :-- | :-- | :-- | :-- |
| a | `classify-deliverable --changed …` | JSON, **always exit 0** | advisory; no exit-code branch |
| b | `set-deliverable-class` (conditional) | `{written:true}`; exit 1 on invalid | only on operator override |
| c | `bd close ${RECONCILE_STEP}` | raw bd JSON | **exit code unchecked** |
| d | `close_cascade.py --json` | `{closed,blocked,errors,dry_run,root}`; exit **0/2** | `RC != 0` → banner, `exit 1` |
| e | `complete-gate --json` | pass→stdout exit 0; **fail→stderr** exit 1 | `RC != 0` → banner, `exit 1` |
| f | `update-status complete` | `{status,date,log_entry}` | terminal; unconsumed |

**Only d and e are true gates. a/b/c are unguarded.**

## LIVE DEFECT: the stdout/stderr split breaks the documented idiom

`close_cascade.py` writes JSON to **stdout on both paths**. `complete-gate` writes the pass
verdict to stdout but the **fail verdict to stderr** (`plan_manager.py:1652-1657`,
`err=True`). `SKILL.md:1112-1114` uses the *same* capture idiom for both:
`GATE=$(… --json)` then `echo "$GATE"`.

Measured, running the exact SKILL.md idiom against a failing gate:

```
GATE_RC=1
GATE stdout capture = []
len=0
```

**On the failing path `echo "$GATE"` prints nothing.** The remediation reaches an interactive
operator only because uncaptured stderr passes through — any caller that redirects, logs, or
parses `$GATE` loses the verdict entirely.

**This is the single most important thing the contract must settle.** `close_cascade` says
stdout-always; `complete-gate` says stderr-on-fail; `SKILL.md` was written assuming the
former.

## No shared verdict envelope

- cascade: fail signal is a non-empty `blocked` array; exit **2**; no `passed`, no
  `remediation`.
- gate: fail signal is `passed:false`; exit **1**; carries a prose `remediation` with
  copy-pasteable commands.

`spec/cli.md:73` and `SPEC.md:205` claim complete-gate "mirrors" the cascade contract — but
the mirroring is **prose-level only** (non-zero + JSON + halt), not envelope-level. Two
steps, two vocabularies.

Also: cascade exits **0** when the root is not found (lands in `errors[]` with empty
`blocked`), so **a typo'd `${EPIC}` passes the gate silently**.

## REQ-COMPLETE-001 is count-bearing — it blocks all three issues today

`spec/phases.md:89-91`, verbatim:

> REQ-COMPLETE-001: The RECONCILE close step (§6.4) runs a **fixed three-step order**:
> **cascade-close → complete-gate → set complete**. … The complete-gate is inserted **after**
> cascade-close and **before** the status transition, mirroring the `close_cascade.py`
> fail-loud contract (exit non-zero + JSON verdict halts completion).

*"Fixed three-step order"* and the Verification clause (*"between the cascade-close block and
`update-status complete`"*) are both count-bearing. **Adding a fourth step requires amending
REQ-COMPLETE-001** — a step cannot be slotted in while leaving the requirement true.

Note it says nothing about steps a/b/c even though they physically precede cascade-close
inside §6.4 — so its "three steps" are the *gated* steps, and an advisory/propose-only step
could arguably live in the unmentioned prelude. The cleaner reading, and the one SPEC-first
pushes toward, is to amend the REQ to describe an **extensible ordered gate chain**.

## §6.3 leaves nothing to verify, and `${RECONCILE_STEP}` is broken on resume

**§6.3 is not a script.** `SKILL.md:1060-1062` is the entire section — a sub-agent dispatch
with no verdict, no exit code, no captured output. (Corroborates E1.)

The reconcile *bead* is created in **Phase 5.2a** (pour), and §6.4's opening move closes it.
Two findings:

1. **`${RECONCILE_STEP}` is a bare shell variable set only at `SKILL.md:815`** — grep returns
   exactly two hits, `:815` and `:1094`, with no re-derivation from bd. On the **resume path**
   (§5.2b, "Do **not** pour"), the variable is never set, so `bd close ${RECONCILE_STEP}`
   expands to `bd close --reason …`. Its exit is unchecked, so it **fails silently**; the
   cascade then correctly fail-louds on the still-open reconcile task. *Inferred from the
   two-hit grep plus the absence of any re-derivation in §5.2b — not corroborated by a live
   run.*
2. **#136's payload must re-derive reconcile state itself**, since 6.3 returns prose to the
   model rather than a verdict. Its insertion point is **between `bd close ${RECONCILE_STEP}`
   and the cascade block** — the only point where 6.3 is done and nothing destructive has
   happened.

## Idempotency: cascade ✅, gate ✅, `update-status` ❌

`SKILL.md` tells the operator to "re-run §6.4" twice. Measured:

- **cascade** — idempotent (guard at `close_cascade.py:174-175`); two passes, two `bd close`
  calls total.
- **complete-gate** — idempotent, pure read; identical verdict both runs.
- **`update-status complete` — NOT idempotent.** `plan_manager.py:1138` calls
  `okf.append_log(...)` unconditionally; every re-run appends another `- complete:` bullet.

Since `log.md` bullets are what the status/review-count parsers read (`spec/data.md:25`), **a
new step that also appends to `log.md` inherits this defect and multiplies it. A new step
should be a pure read, or dedupe its own log write.**

## Precedent: plan-030 measured the cost at 10 files

`git show --stat 0b0cc78` (the commit that added `complete-gate` itself):

```
10 files changed, 760 insertions(+), 11 deletions(-)
```

The full checklist to add one gated step to 6.4: amend `spec/phases.md` REQ-COMPLETE-001 +
new REQ-COMPLETE-00N · `SPEC.md` §2.7 `REQ-PLAN-0NN` · `spec/cli.md` `REQ-CLI-0NN` ·
`spec/data.md` if new artifact · root `SPEC.md` amendment log (**first**, per SPEC-first) ·
the verb in `plan_manager.py` · a REQ-tagged test · `CHANGE-VALIDATION.md` rows in **both**
tiers (measured: three separate tables each) · the `SKILL.md` §6.4 bash block · optionally a
`spec/<topic>.md` explainer.

**The real cost is the SPEC surface, not the code.** Three issues each paying it
independently is exactly the duplication plan-043 exists to prevent.

## Implications for plan-043

1. **The contract is convention + SPEC, not a code seam** — none exists, and a harness hook
   is doctrinally forbidden. Creating a seam would itself be the deliverable.
2. **Amending REQ-COMPLETE-001 to an extensible ordered gate chain is the highest-leverage
   single edit in the plan** — it currently blocks all three issues.
3. **Settle the verdict envelope and the stream** — the stdout/stderr split is a measured
   live defect. One line of contract (*verdict JSON to stdout on every path; non-zero =
   halt; `{passed, reason, remediation}`*) fixes it and answers all three issues at once.
4. **#136 slots between `bd close ${RECONCILE_STEP}` and the cascade block.**
5. **`${RECONCILE_STEP}` unset-on-resume deserves its own bead** — it will bite any 6.4 step
   that assumes the reconcile bead is closed.

## Not measured

`close_cascade.py` and `complete-gate` were not run against a real plan or live bd DB (per
constraints); bd-side behavior is from code reading plus monkeypatched probes. The
`${RECONCILE_STEP}`-unset-on-resume conclusion is uncorroborated by a live run.
