---
type: Finding
okf_spec: OKF-PLAN
description: "plan-067 is DELIBERATELY HELD in `executing` behind TWO open human gates the operator chose to hold on 2026-09-07. 42 of 44 issues closed; 29 of 32 criteria hold. This is not a crashed or abandoned run."
id: parked-state
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# HELD — not crashed, not abandoned

**Read this first if you found this bundle in `executing` and wondered whether something died.**

`plan-067-james-dixson-de852a` is **deliberately held**. Epics 0-5 are complete and Epic 6 is at
4 of 6. The two unfinished issues sit behind two `gate_type: human` capability gates the operator
chose to hold, in a stated order, on 2026-09-07.

## How to tell this apart from a crash

| Signal | A crashed run | **This run** |
| :-- | :-- | :-- |
| Why it stopped | unknown / unrecorded | **recorded here, in `log.md`, and as an `RE-NNN` stop entry** |
| The blocking gates | often already resolved, or absent | `yf-mol-gtcy.10` and `yf-mol-gtcy.11` **deliberately open** |
| Stuck beads | `in_progress` / claimed beads stranded | **none** — `bd ready` returns zero ready TASK beads |
| Uncommitted work | dirty worktree, stranded edits | **clean**; ten commits on `plan-067-james-dixson-de852a-execute` |
| Upstream | half-written, or written before it was true | **nothing written at all**, by instruction |
| Verification | unknown | **29 of 32 criteria hold**, every checker exits 0 |

Nothing here needs recovery. The orphan sweep has nothing to reset.

## The operator's two decisions, recorded

### Gate 2 — Diagram human read (`yf-mol-gtcy.10`) — HELD

The operator is reading the 20 diagrams themselves and will return a verdict. **The agent reads
recorded in this bundle are EVIDENCE, never a discharge.** plan-066 measured a corrected diagram
whose count was right and whose **membership was wrong**, which is exactly the residue no
extractor catches. The material for this read is
[diagram-presentation.md](diagram-presentation.md).

### Gate 3 — Upstream write authorization (`yf-mol-gtcy.11`) — HELD, AND SEQUENCED AFTER GATE 2

Deliberately ordered, and the reason is the interesting part: **the reconcile bodies assert what
this plan DID, and `#373`'s closure depends on the diagram set being accepted.** Publishing before
Gate 2 resolves would risk making a public claim that Gate 2 then contradicts. The ordering is not
caution about the writes; it is that the writes are not yet TRUE.

## What is consequently unmet

**32 criteria, not 28.** The plan's criteria table has 32 rows; `plan067_checks.py` has 28
subcommands. Those are **two different counts**, and a prior status report in this session
conflated them — the same two-facts-one-signal defect (`#263`) this plan exists to close,
committed in a report *about* that defect. The partition, derived mechanically from the extractor
rather than summarised:

| Partition | Count | Ids |
| :-- | --: | :-- |
| hold (verified) | **29** | everything not listed below |
| FALSE | **1** | `SC26b` |
| manual — not evaluated, and not evaluable by any command | **2** | `SC17`, `SC27` |
| **total** | **32** | 28 via `plan067_checks.py` + `SC4` + `SC10` + 2 manual |

- **`SC17`** — "the operator was shown both builds and returned a decision on archify." Its
  Verification cell is `manual:`. **The operator DID return this decision** (KEEP FOR EXPLORATION,
  2026-09-07, recorded in [archify-trial.md](archify-trial.md)), so the criterion is *satisfied in
  substance*; it is listed as not-evaluated because **no command can decide it**, which is what
  `manual:` means. It is not outstanding work.
- **`SC27`** — "the redesigned diagrams were presented to the operator for plan-066's gate." The
  material exists; the presentation-and-read is Gate 2 itself. Genuinely pending.
- **`SC26b`** — plan-066's criteria on this tree. `plan066-still-green` re-runs all 24 of
  plan-066's verbs and reports **no regression**; the single FALSE one is plan-066's own
  `diagram-reads`, which the checker reports as the **DECLARED HANDOFF** rather than a regression.
  It is FALSE because the restructured set has not been human-read — which is Gate 2. Writing read
  entries for diagrams no human has looked at would satisfy the check while destroying the thing
  it checks.

**All three trace to Gate 2.** There is no independent unmet work.

## Do NOT do these

A later session, or a resumed one, must not "helpfully" close any of these:

- **Do NOT resolve `yf-mol-gtcy.10` or `yf-mol-gtcy.11`.** Both are `gate_type: human`. A green
  test establishes that a condition holds; it can never establish that a human authorized
  something.
- **Do NOT write `findings/diagram-reads.md`, or add read entries anywhere.** That would flip
  `SC26b` and plan-066's `diagram-reads` green on reads no human performed.
- **Do NOT run the §6.4 close chain, and do NOT `update-status complete`.**
- **Do NOT write anything upstream.** No `gh issue` create, edit, comment or close. `#373`,
  `#374`, `#375`, `#376` stay open; `#247`, `#263`, `#317` stay open as partials.
- **Do NOT push `yf-w57p`** (the `check_web_counts` `is_d2` single-shape follow-on). It is filed
  as a LOCAL bead only; whether it goes upstream is the operator's call at Gate 3.
- **Do NOT tear down the branch or worktree.** `plan-067-james-dixson-de852a-execute` is intact
  and unmerged by design.
- **Do NOT re-run the plan from the start.** `resume-scan` will report `epic_state: present`; the
  correct action on resume is to re-read this file, not to pour.

## What IS done, so a resumer does not redo it

Epics 0-5 complete (SPEC-first amendments, the omissions-FAIL rule with code-side controls, the
inventory and its repairs, the archify trial, the diagram redesign, the generated per-skill set)
and Epic 6 Issues 6.0-6.3. Every checker exits 0; `pelican --fatal warnings` builds clean unpiped;
all 20 PNGs are sha256-identical to a fresh render under the pinned `d2 v0.8.2 --theme 0 --layout
elk`.

## The route to closure

Gate 2 verdict → plan-066's `diagram-reads` record updated for the new set → `SC26b` and `SC27`
resolve → Gate 3 → Issue 6.5 reconciles `#373`/`#374`/`#375`/`#376` → §6.4 close chain →
`complete`. plan-066's own gate then opens, its Issues 8.1/8.3 run, and `#317` closes — which is
the handoff `D5` exists to guarantee.
