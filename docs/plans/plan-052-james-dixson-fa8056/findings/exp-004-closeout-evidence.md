---
type: Finding
okf_spec: OKF-PLAN
id: exp-004-closeout-evidence
description: What evidence predicate is available at close-out? The false positive is a TYPED bug, and it is live right now.
---

# EXP-004 — the false positive is narrower and cheaper than #205 assumed, and it is LIVE

**Verdict: three predicates buildable now, three not.** #205 framed the false positive as the hard
epistemics problem *"`bead closed` is a weak proxy for `work done`"*. Measured, both worked
instances are one **typed** failure with a mechanical signature.

## 1. The headline: hoist tombstones, and #147 is a live false positive

A **hoist tombstone** is a bead closed *because the work moved upstream and is not going to be
done locally*. `upstream.py:735` writes it in a **fixed format**. `closable` reads `status=closed`
and proposes closing the very issue the bead was hoisted **into**.

Re-measured by the main session — **5 of 47** mapped-closed beads are tombstones:

```
yf-mol-62k.5   #147   hoisted upstream to .../issues/147
yf-uc0p        #142   hoisted upstream to plan-040 (reversible tombstone; un-hoist to restore)
yf-nl8i        #152   Hoisted upstream to .../issues/152
yf-sklq        #153   Hoisted upstream to .../issues/153
yf-b0mb        #143   hoisted upstream to plan-040 (reversible tombstone; un-hoist to restore)
```

**This is not a three-day-old historical incident.** `closable` right now emits **2 actionable
proposals**, and **#147 is one of them**. #147's defect was reproduced live by running the scorer
in isolation — 6 of its 8 named first-party doc hosts still score 30. Closing it would be wrong
today.

Corroborating detail: `gh issue view 153` shows `stateReason: NOT_PLANNED` — the human closed it
as *withdrawn*, whereas the `gh issue close` that `closable` proposes defaults to **COMPLETED**.
The proposal is wrong in the *reason* as well as the *act*.

**Counter-check, and it came out clean:** #152 is also a tombstone and was closed COMPLETED
earlier. Verified independently — `yf/profiles/claude-code.json` ships `permissions.deny`
(`EnterPlanMode`, `ExitPlanMode`, `Task*`, …) plus `todoFeatureEnabled: false` and
`disableWorkflows: true`. **That is #152's feature, and it shipped.** The close was correct. Being
a tombstone makes a proposal *unreliable*, not *wrong* — which is precisely why the fix is to
**suppress and annotate**, never to invert.

## 2. The ranking

| # | Predicate | Verdict | Evidence |
| :-- | :-- | :-- | :-- |
| **P0** | **Exclude hoist tombstones** from `closable` | **BUILDABLE NOW** | 5/47 mapped-closed; fixed format written by `upstream.py` itself; suppresses the live #147 proposal and would have suppressed #153 |
| **P1** | **Render the evidence** — print each proposal's mapped beads, their `close_reason`, and the criteria they discharge | **BUILDABLE NOW** | every input already in `bd list --json` + `plan_extract`; **zero new records** |
| **P2** | **Traverse `Resolved By` → issue id → `Discharged-by` → criterion**, require the join to exist | **BUILDABLE NOW** (completeness only) | 100% complete for plans 048–051 (4/4, 5/5, 10/10, 7/7); `plan-relations` R1/R2a already compute it — they only need promoting off `severity = "W"` |
| P3 | Require the tracker to be a mapped bead **by construction** | needs a recorded change | mechanism works (#200), but see §3 |
| P4 | Commit correlation | **NOT BUILDABLE AS A GATE** | 20/210 strong (9.5%), 35% best case. **No commit anywhere names a bead id.** `#NNN` refs reach 65% recall but carry ~18 immediate false positives, and closing-keyword discipline is absent — 20 hits in 576 commits, **one of them a negation** (*"did not fix #181's…"*) |
| P5 | A green recipe row covering the changed paths | **NOT BUILDABLE** | see §4 — decisive |
| P6 | The discharged criterion re-checked green | **NOT BUILDABLE THIS PLAN** | 0 of 172 criteria have an executable `Verification` (independently reproduces EXP-003) |

## 3. P3 — plan-051's SC12b passed, but NOT by the mechanism it declared

**The stamp is real** (`yf-mol-3he` carries #200's URL, and #200 appears in live `closable`).
**But `stamp-tracker` did not produce it.** `stamp-tracker` resolves the URL solely from a
`plan.md` row whose Disposition is literally `tracker` — and **plan-051's table has no such row**,
so the verb returns `skipped`. The stamp came from `/yf-beads-upstream`'s own
`bd update --external-ref`, a **side effect**.

**Nothing caught it.** `verify-reconcile` returns `verdict: pass`, exit 0 — it grades rows that
*are* in the table and is blind to an absent one. Corpus-wide: 52 plans, **11** have a `tracker`
row, **28** epics carry an `external_ref`.

**So a check written against the declared route would report a false green on plan-051 itself.**
Assert the **end state** (the epic carries an `external_ref` naming a tracker), not the route —
and add the missing-row assertion separately.

## 4. P5 is decisive and negative — there is no run record

`change_validation.py` is **970 lines and contains exactly one file write** — `dest.write_text()`
at line 630, inside `cmd_infer --write`, writing **the manifest itself**. `cmd_run` builds
`{tier, status, commands, first_failure}` and hands it to `json.dump(..., sys.stdout)`. **No
timestamp, no tree SHA, no persistence.**

The *coverage* half is a pure function that already works (`_scoped_ids()` over the live manifest
maps a path to its row ids) — it simply has no CLI verb. The **verdict** half does not exist.

The two prose substitutes have tiny adoption: hand-written validation assets in **4 of 51**
bundles, and `attest-validation`'s free-text `- validated:` bullet in **2 of 23** `log.md` files
(exactly the 2 `ci-release` plans).

**Any design gating close-out on a green recipe row must first land a persisted run-record** keyed
by (tier, changed paths, row ids, exit codes, tree SHA). That is its own epic, not a rider.

## 5. Implications

| # | Implication |
| :-- | :-- |
| I-1 | **Ship P0 + P1 + P2.** Together they produce a strictly better artifact than today's without inventing any new record — a proposal can already read *"#N; mapped bead X closed with reason R; discharges SC7, SC12 of plan-051"*. That is #205's own stated fallback |
| I-2 | **P0 removes 100% of observed false positives**, including the one live right now |
| I-3 | **Scope P5 and P6 OUT, and record why.** File the run-record as its own upstream issue — it is the shared prerequisite for both |
| I-4 | **P4 is dead as a gate.** It may still be worth rendering as *context* under P1, clearly labelled unreliable |
| I-5 | **`REQ-PLAN-073` is an ID COLLISION** — `SPEC.md:345` binds it to roots-configurability (plan-037/#107); `spec/phases.md:150` binds the same id to stamp-tracker. Two requirements, one id. Out of scope, but any requirement written near the stamp inherits the ambiguity. **File it** |
