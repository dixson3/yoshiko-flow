---
type: Finding
okf_spec: OKF-PLAN
description: "plan-067 is DELIBERATELY HELD in `executing` for the SECOND time, behind the same two human gates. Epic 7 (the restyle) is complete and the restyled set is presented for a second read. 52 of 54 issues closed; 36 of 40 criteria hold. This is not a crashed or abandoned run."
id: parked-state
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# HELD (second time) — not crashed, not abandoned

**Read this first if you found this bundle in `executing` and wondered whether something died.**

`plan-067-james-dixson-de852a` is **deliberately held, for the second time and at the same gate**.
Epics 0-5 and 7 are complete; Epic 6 is at 4 of 6. The two unfinished issues sit behind two
`gate_type: human` capability gates the operator is holding, in a stated order.

## The two halts, and why there are two

| | First halt | **This halt** |
| :-- | :-- | :-- |
| When | after Epic 6 Issue 6.3 | after Epic 7 Issue 7.8 |
| What was presented | the first 20-diagram set | the **restyled** 21-diagram set |
| Gate 2 outcome | **REJECTED** — too wordy, and `architecture.d2` did not read as a stack | **awaiting a second read** |
| What the rejection produced | Epic 7, ten issues, added by amendment | — |
| Gate 3 | held, sequenced after Gate 2 | unchanged |

**The first set was fully green when it was rejected**, and so was plan-066's before it. That is
recorded in [plan-retrospective.md](plan-retrospective.md) as the plan's highest-value
process finding: two independent measurements that *green* and *good* are different predicates.

## How to tell this apart from a crash

| Signal | A crashed run | **This run** |
| :-- | :-- | :-- |
| Why it stopped | unknown / unrecorded | **recorded here, in `log.md`, and as `RE-NNN` stop entries** |
| The blocking gates | often already resolved, or absent | `yf-mol-gtcy.10` and `yf-mol-gtcy.11` **deliberately open** |
| Stuck beads | `in_progress` / claimed beads stranded | **none** — `bd ready` returns zero ready TASK beads |
| Uncommitted work | dirty worktree, stranded edits | **clean**; the branch `plan-067-james-dixson-de852a-execute` is intact |
| Upstream | half-written, or written before it was true | **nothing written at all**, by instruction |
| Verification | unknown | **36 of 40 criteria hold**; every checker exits 0 |

Nothing here needs recovery. The orphan sweep has nothing to reset.

## The operator's decisions, recorded

### Gate 2 — Diagram human read (`yf-mol-gtcy.10`) — HELD, second read in progress

The operator is reading the restyled set themselves. **Agent reads are EVIDENCE, never a
discharge** — plan-066 measured a corrected diagram whose count was right and whose membership
was wrong, and *both* sets rejected at this gate were mechanically green. The material is
[diagram-presentation.md](diagram-presentation.md).

### Gate 3 — Upstream write authorization (`yf-mol-gtcy.11`) — HELD, sequenced AFTER Gate 2

Unchanged from the first halt, and the reason still holds: **the reconcile bodies assert what
this plan DID, and `#373`'s closure depends on the diagram set being accepted.** Publishing
before Gate 2 resolves would risk a public claim Gate 2 then contradicts. The ordering is not
caution about the writes; it is that the writes are not yet true.

### The archify gate (`yf-mol-gtcy.9`) — RESOLVED by the operator, 2026-09-07

KEEP FOR EXPLORATION. Recorded in [archify-trial.md](archify-trial.md). Not outstanding.

## The one place the second set is WORSE than the first

**`lifecycle.png` went from 11602px tall to 13362px** — a regression on the exact dimension the
first read objected to. The mechanism is worth stating because it is not obvious: **expanding 95
sublabels into child boxes is what removed the wordiness, and child boxes are vertical
structure**, so the diagram with the most sublabels gained the most height. The nodes are no
longer wordy; the artifact is taller than ever.

No check caught it and none should have: `build-and-render`'s legibility threshold is 3:1, and
1.56:1 passes comfortably. That check detects a *column masquerading as a graph*, which this is
not; it does not measure "too big to take in", because no threshold does.

**Two remedies are plausible and NEITHER is started:**

1. **Split the combination back into two diagrams** — undoing Issue 4.2's merge of `phase-model`
   and `lifecycle`. That merge was right on *content* and may be wrong on *scale*.
2. **Restructure it horizontally.**

Which is right depends on what a reader objects to. **Do not start either until the operator says
so** — guessing would repeat the error Epic 7 exists to correct: acting on a mechanical signal
where the deciding question is a human one. If the verdict is "everything except lifecycle", it
becomes one issue.

## What is consequently unmet

**40 criteria** — the extractor's row count, derived rather than summarised, and not to be
confused with `plan067_checks.py`'s **33** subcommands. That conflation was committed once in
this session's own reporting and corrected in `log.md`.

| Partition | Count | Ids |
| :-- | --: | :-- |
| hold (verified) | **36** | everything not listed below |
| FALSE | **1** | `SC26b` |
| manual — not evaluable by any command | **3** | `SC17`, `SC27`, `SC33` |
| **total** | **40** | 37 executable + 3 manual |

- **`SC17`** — the archify decision. **Answered** by the operator; listed as not-evaluated only
  because `manual:` means no command can decide it. Not outstanding work.
- **`SC33`** — the restyled set re-presented for plan-067's gate. Material exists; the read is
  Gate 2.
- **`SC27`** — the set presented for **plan-066's** gate. That is Issue 6.4, which
  `depends-on` 7.8 so it structurally cannot present a rejected set.
- **`SC26b`** — plan-066's criteria on this tree. All 24 of its verbs re-run with **no
  regression**; the single FALSE is plan-066's own `diagram-reads`, reported as the **DECLARED
  HANDOFF**. It is FALSE because the set has not been human-read — which is Gate 2.

**All four trace to a human gate.** There is no independent unmet work.

## Do NOT do these

- **Do NOT resolve `yf-mol-gtcy.10` or `yf-mol-gtcy.11`.** Both are `gate_type: human`. A green
  test establishes that a condition holds; it can never establish that a human authorized
  something. **Two mechanically-green sets have already been rejected at Gate 2** — the strongest
  available evidence that this gate is not derivable.
- **Do NOT write `findings/diagram-reads.md`, or add read entries anywhere.**
- **Do NOT start either `lifecycle.png` remedy** until the operator names one.
- **Do NOT run the §6.4 close chain, and do NOT `update-status complete`.**
- **Do NOT write anything upstream.** `#373`, `#374`, `#375`, `#376` stay open; `#247`, `#263`,
  `#317` stay open as partials.
- **Do NOT push `yf-w57p`** (the `check_web_counts` `is_d2` follow-on). Local bead only.
- **Do NOT tear down the branch.** Intact and unmerged by design.
- **Do NOT re-pour.** `resume-scan` reports `epic_state: present`; Epic 7's ten beads were created
  under the existing epic precisely so the molecule was not re-poured. Re-read this file instead.

## What IS done, so a resumer does not redo it

Epics 0-5 (SPEC-first amendments, the omissions-FAIL rule with code-side controls, the inventory
and its repairs, the archify trial, the diagram redesign, the generated per-skill set), Epic 6
Issues 6.0-6.3, and **all ten** of Epic 7 (the restyle). 21 PNGs byte-identical to a fresh render
under the unchanged `d2 v0.8.2 --theme 0 --layout elk`; every checker at 0; **six** negative
controls observed to fail against code-side mutations under passing docs.

## The route to closure

Gate 2 verdict → (any named `lifecycle` remedy) → plan-066's `diagram-reads` updated → `SC33`,
`SC26b` and `SC27` resolve → Gate 3 → Issue 6.5 reconciles `#373`/`#374`/`#375`/`#376` → §6.4
close chain → `complete`. plan-066's own gate then opens, its Issues 8.1/8.3 run, and `#317`
closes — the handoff `D5` exists to guarantee.
