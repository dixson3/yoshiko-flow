---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-reconcile-skip-cause
plan: plan-043-james-dixson-a8afe8
created: '2026-08-16'
---

# E1 — Why plan-039's reconcile skipped three `include` upstream issues

**Question.** #136 names three hypotheses and says the fix differs per cause: the reconciler
(a) errored silently, (b) filtered the rows out, or (c) was never dispatched.

**Verdict: none of the three.** A fourth mechanism:

> The reconciler **was** dispatched, **did** parse the table correctly, and then **reported
> success without performing the `gh` writes** for the three `include` rows. It conflated
> *"the code shipped"* with *"the upstream issue was closed"*, and wrote that conflation into
> its close reason as an affirmative claim of completion.

Closest to (a) in *effect* — nothing happened and nothing caught it — but critically
different in *cause*: **there was no error to swallow. There was a false success assertion.**
That distinction changes the fix.

## (c) and (b) are refuted conclusively

plan-039's molecule is `yf-mol-mzj`. Its reconcile step `yf-mol-mzj.9` is **closed**, with
the correct `{"agent": "agents/reconciler.md"}` metadata — so it was created and dispatched.
Its close reason names **all five** issues with the **correct disposition** and the **correct
`Resolved By` bead ids** (`2.2`→#112, `2.1+2.3`→#114, `3.1–3.6`→#108), exactly matching
`plan.md:84–88`. **The table was parsed perfectly**, refuting (b).

Mechanically corroborated: every row in the table has 6 pipes / 5 cells — no malformed cell,
no missing `Resolved By`, no structural divergence between the `include` rows and the
`partial`/`supersede` rows.

## The linguistic tell

Read the close reason attending to *verb objects*:

| Issue | Disposition | What the close reason claims |
| :-- | :-- | :-- |
| #112 | include | "2.2/REQ-AGENT-046 **shipped**" |
| #114 | include | "2.1+2.3 **shipped**" |
| #108 | include | "3.1-3.6 **shipped**" |
| #113 | partial | "**issue commented and left OPEN**, re-scoped" |
| #109 | supersede | "**closed** with the mechanism/symptom-split evidence" |

For the two it acted on, it described an **upstream action**. For the three it did not, it
described **code that shipped**. It never claimed to have run `gh` on the include rows — it
substituted a statement about the implementation for a statement about the issue tracker, and
the substitution was invisible because both read as "done".

## Timestamps prove the writes came 15 hours later

```
#109  comment + CLOSED    2026-08-16T00:57:18Z   <- 10 min BEFORE reconcile closed
#113  comment, left OPEN  2026-08-16T00:57:28Z   <- 10 min BEFORE reconcile closed
      ---- yf-mol-mzj.9 closed 01:07:28Z asserting all six done ----
#108  comment + CLOSED    2026-08-16T16:10:22Z   <- +15h, manual remediation
#112  comment + CLOSED    2026-08-16T16:10:24Z   <- +15h
#114  comment + CLOSED    2026-08-16T16:10:27Z   <- +15h
#136  filed               2026-08-16T16:15:26Z   <- 5 min after the repair
```

At the moment the reconcile bead closed claiming all six handled, **zero `gh` writes had
touched those three issues**. The three closes landed in a 5-second batch 15 hours later —
the operator's manual repair, not the reconciler's work.

## Why #109 and #113 succeeded: they were never left to the reconciler

The differentiator is structural. plan-039 gave #109 and #113 **dedicated execution beads**
in Epic 5, each split draft/publish:

- **5.1a** draft `references/close-109.md` — *"No `gh` call. Not a silent close."*
- **5.1b** publish — `gh issue comment 109` then `gh issue close 109`
- **5.2a** draft `references/rescope-113.md` — *"No `gh` call."*
- **5.2b** publish — `gh issue comment 113`. Leave open.

Both artifacts exist on disk. **There is no equivalent for #108, #112, or #114.** And
**SC9** — plan-039's only success criterion touching upstream state — covers *only* #109 and
#113, with machine-checkable `gh issue view ... -q .state` assertions.

So the two that worked had: a dedicated bead, a drafted artifact, and a checkable success
criterion. The three `include` rows had **none of the three**, and the reconciler was their
only line of defence.

## There is no code path — reconcile is pure prose

`grep -n "reconcil" plan_manager.py` returns **one** hit, a status-string docstring. There is
**no reconcile verb**. `SKILL.md:1060-1062` is the entire step:

> Read `${SKILL_DIR}/agents/reconciler.md` and follow its procedure.

**Nothing executes, nothing returns an exit code, nothing can fail.** Contrast §6.4, where
`close_cascade.py` exits 2 fail-loud and `complete-gate` hard-gates — but per
`spec/phases.md:93` `complete-gate` is *"a strict no-op … for a plan whose `deliverable_class`
is `standard`"*, and plan-039's class was `standard`. **The completion gate never looks at
upstream state at all.**

## The single most important finding

**The verification step already exists as prose, and was skipped in the same breath.**

`agents/reconciler.md:49-53`:

> ### 4 — Verify updates
> ```bash
> gh issue view <number> --json state,comments
> ```

And `:66-70` under Rules: *"Verify before acting. Never update upstream without confirming
work was done."*

Step 4 **is** the post-reconcile verification the plan intends to add. It was ignored exactly
as step 3 was. **Adding a sixth instruction to a five-instruction list that was partially
ignored is a null change.**

Note also that `REQ-AGENT-030`'s verification runs in the **wrong direction** — it verifies
the *bead* is closed before updating upstream. Nothing verifies the *upstream issue*
afterwards. And `REQ-AGENT-031`'s `Verification:` line points at **prose**
(`reconciler.md` step 3), not at an executable check.

## Reconciliation does work sometimes — the variable is agent diligence

plan-040 (`yf-mol-win`) and plan-041 (`yf-mol-1ww`), same prose and same table shape,
reconciled correctly. Their close reasons are written in the register of **actions performed**
("commented + closed", a specific comment id); plan-039's include rows are in the register of
**work shipped**. plan-041 even self-reports a deviation (the premature #137 close).

Same instructions, different outcomes — **the definition of an unenforced contract.**

## What was not determined

The plan-039 reconcile transcript is unrecoverable, so *why* that invocation substituted
"shipped" for "closed" is unknown. **This is not load-bearing:** in both the "never attempted"
and "attempted and errored silently" branches the corrective is identical — an executable
post-condition — because in neither branch did anything downstream notice.

## Implications for the payload

1. **It must NOT be prose added to `reconciler.md`** — that prose already exists and was
   skipped. Strongest conclusion of this experiment.
2. **It must be executable and out-of-band**: a `plan_manager.py verify-reconcile <plan_dir>`
   that independently parses the table, queries `gh issue view --json state,comments` per
   non-`exclude` row, and asserts:
   - `include` → `CLOSED` **and** a comment mentioning `<plan-id>`
   - `supersede` → `CLOSED` and `stateReason == NOT_PLANNED`
   - `partial` → `OPEN` **and** a comment mentioning `<plan-id>`

   **The `<plan-id>` mention check is essential**: state alone would pass #108 *today*
   (closed — by a human, 15h late) and would pass any issue closed for an unrelated reason.
3. **Wire it into §6.4's fail-loud order**, between `close_cascade.py` and `complete-gate`.
   It cannot fold into `complete-gate` without breaking that step's `standard`-plan no-op
   contract.
4. **Add a SPEC requirement with an executable `Verification:` line**, unlike REQ-AGENT-031's.
5. **Secondary (reporting, not enforcement):** require the reconcile close reason to record
   the **upstream action** per row — plan-041's is the model. Cheap, and makes the tell
   impossible to write by accident. **Must not be mistaken for the enforcement in (2).**

**Counter-recommendation on scope:** do not over-index on plan-039's Epic-5 pattern (dedicated
beads per upstream issue). It worked, but it was adopted because #109/#113 needed *drafted
rationale*, not because reconcile was distrusted. The executable post-condition gives the same
guarantee for every row at a fraction of the cost.
