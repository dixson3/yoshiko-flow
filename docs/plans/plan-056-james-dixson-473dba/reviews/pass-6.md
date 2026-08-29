---
type: Review
okf_spec: OKF-PLAN
id: pass-6
description: "Red-team pass 6 — REVISE. Sixth shape: the pour directive sits after a blank line and the extractor silently truncates it, and --require 10 created a gate-reachability cycle."
---

# Red-team pass 6: plan-056-james-dixson-473dba

## Verdict: REVISE

A sixth shape exists, in two of pass 5's own fixes. Both were reproduced by the main session before acting.

## Strengths

Verification of pass 5, mechanically re-derived: **C40 holds exhaustively** (SC0's `test -x … -a …` form
returns 0 all-present, non-zero on any missing or non-executable). **C42a/b hold** — R12, D-17 and the
extractor all say 34; #140's `Resolved By` is `['3.1','3.2','4.3']` and Issue 4.3 names it. **C44 holds**,
and `redcheck.sh` is genuinely absent from `scripts/checks/`. **C46 holds.** **C47 holds** — Motivation
now agrees with D-1. Baseline clean: 34 issues, 21 criteria, 34 edges, zero dangling `depends-on`, zero
uncovered issues, zero phantom refs, `doc_lint` PASS, `gate_consistency` PASS, `reindex --check` clean.

## Concerns

### C48 — SIXTH SHAPE. C41's fix is silently deleted by the extractor. [HIGH]

Not "prose in a field nothing parses" — prose in a field that **is** parsed, placed where the parser
**truncates**. Measured against the live extractor:

```
"instructions": "This gate exists because … which the gate does not block."
                 ^ ENDS HERE. "POUR THIS GATE WITH test_class: probe" is absent.
"unparsed": []          <- the drop is completely silent
```

Cause at `plan_extract.py:683`: the continuation loop requires `lines[j].strip()`, so **a blank line
terminates the value**. plan.md:253 is blank; the directive lives at 254-260. `SKILL.md:1145`
interpolates `${instructions}` into the gate bead's description, so a pour driven from the extractor
never carries the directive, and a gate poured without `test_class` defaults to `manual` -> INCONCLUSIVE
-> never FAIL. The one defence pass 4 built and pass 5 patched is back to inert.

*Rec (one character):* delete the blank line at :253. Spiked: with it removed, `'test_class: probe' in
instructions` -> **True**, full text preserved. **As it stands the fix is worse than
documented-but-inert — it is documented in a place that deletes it.**

### C49 — C45's fix created a gate-reachability cycle. [HIGH]

`--require 10` raised from 8. The ten are 8 (Issue 1.9) + `check-pytest-ran.sh` (1.8) +
**`check_okf_index_drift.py` (Issue 3.1)**. Issue 3.1 is in **Epic 3** — exactly what the gate
`Blocks: epic:3`. So the gate's `Test` requires an instrument produced inside its own `Blocks` set; only
9 of 10 can exist before it resolves. Per `coordinator.md:179` a non-zero test routes to stop class 2 —
a **guaranteed operator override on every run** of the plan's single load-bearing automated defence. It
did not exist at `--require 8`, where all eight were Epic 1's.

The gate's `Instructions:` now assert something false: *"Its evidence is produced by Epic 1, which the
gate does not block."* Fourth false claim in this plan's resolutions.

*Rec:* keep `--require 10`; change `Blocks: epic:3` -> `Blocks: 3.2, 3.3, 3.4` (issue-level refs are
supported at `plan_extract.py:721`). 3.1 then runs unblocked, produces the tenth instrument, and the gate
becomes reachable while still gating every enforcement act. Fix the false sentence, and widen SC35's
`Discharged-by` from `1.9` to `1.8, 1.9, 3.1` — SC0 already lists all three and SC35 does not.

### C50 — C43's other half did not land; adjacent dependent issues now contradict. [MEDIUM-HIGH]

Issue 0.14 (:179) codifies `_common.sh`'s contract — `0 holds · 1 does not · **2 could NOT RUN**`. Issue
1.8 (:207), landing a script in that same directory, still reads *"Its own INCONCLUSIVE result is pinned
to **exit 3**"*. Only the 0.14 half landed. Consequence is not cosmetic: `record-red-check` refuses to
bank a 2, so an exit 3 would be banked as a genuine red observation.

### C51 — SC1 is ambiguous between two readings differing by 9 issues, and the literal one makes it FALSE. [MEDIUM]

Computed over the extracted DAG: **direct** dependency on an Epic-0 issue holds for **13** of 23 —
`1.3, 1.4, 1.5, 1.7, 2.2, 3.3, 3.4, 4.2, 4.3` fail, so `check-req-coverage.py` implementing SC1 literally
exits 1 and SC1 is FALSE by construction. **Transitive**: **22** of 23, only the declared bug-fix
carve-out outside. Neither is the annotated "~17". C18/C28's class again — under-specified such that the
implementer picks the semantics.

## Non-blocking notes

- **SC0's "all ten" over-claims**: SC11b invokes `_shared/sync.py` and SC26 `plan_manager.py`, also
  instruments criteria invoke. Reword to "all ten *this plan creates*".
- **Two unstated SC0 residuals**: a **directory** at one of the ten paths satisfies `-x` (measured rc 0);
  and three of the ten are invoked via `uv run`, which does not need the x-bit — so SC0 imposes a
  `chmod +x` obligation no issue text states.
- **`index.md` is drifting on descriptions right now** — it says "*Four* red-team passes … Read pass-4
  first" with five on disk. `reindex --check` reports clean because it checks membership, not description
  content: the plan's own Motivation reproducing in its own bundle, outside the reach of the gate Issue
  3.2 wires.
- #170's Notes still carry an argument for `partial` under a `deferred` disposition.

## Executability

Structurally sound and executable: acyclic DAG, full bidirectional coverage, portable bundle. **C49 is
the only item that blocks execution mechanically** (guaranteed stop class 2). C48 and C50 are one-line
edits; C51 is wording. All four are plan.md edits — no re-scoping.

## Missing

- No criterion verifies that a gate's `Instructions:` survive extraction — the defect class C48 found is
  invisible to every check the plan runs (`unparsed: []`, `doc_lint` PASS, `gate_consistency` PASS).
- Nothing reconciles SC0's `chmod +x` obligation with the issues that create the scripts.

## Gate Assessment

| Gate | Reachable? | Frontloaded? | Verdict |
| :-- | :-- | :-- | :-- |
| Start Gate | n/a | n/a | fine |
| Verification harness ready | **No** — `--require 10` counts an instrument authored inside the gate's own `Blocks: epic:3` set, so only 9 of 10 can exist when it resolves (C49) | evidence otherwise correctly early | **Blocking**; see C49 |
| Reconcile Gate | auto | — | fine |

## Upstream Assessment

`verify-reconcile` fails for the correct pre-execution reason. #140 is now fully wired (`Resolved By`
populated and named in Issue 4.3). #265 is in 4.3's close list. #170's Notes still carry an argument for
`partial` beneath a `deferred` disposition — cosmetic, but a cold reader meets a contradiction.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C48 pour directive truncated by blank line | high | Reproduced before acting: the extracted `instructions` ended at '…which the gate does not block.' with the pour directive absent and `unparsed: []` — a completely silent drop, caused by `plan_extract.py:683` requiring `lines[j].strip()` so a blank line terminates the value. Fixed by deleting the blank line. Verified: instructions grew **605 -> 1768 chars**, and both `test_class: probe` and `cwd: worktree` are now present in the extracted object. Pass 6 is right that this was worse than documented-but-inert — it was documented in a place that deletes it. | `main-session` | `resolved` |
| C49 `--require 10` created a gate cycle | high | Confirmed: `--require 10` counts `check_okf_index_drift.py`, which Issue 3.1 authors inside Epic 3, so `Blocks: epic:3` required an instrument produced within the gate's own blocked set. Changed to issue-level `Blocks: 3.2, 3.3, 3.4`; verified 3.1 is no longer blocked. The false sentence was rewritten — **and then rewritten again**, because naming 3.2/3.3/3.4 explicitly made `gate_consistency` FAIL on the same self-blocking rule that caught the pass-4 retarget. It now describes the roles without naming the ids. SC35's `Discharged-by` widened to `1.8, 1.9, 3.1`. | `main-session` | `resolved` |
| C50 Issue 1.8 still says exit 3 | medium-high | Applied — Issue 1.8's INCONCLUSIVE is now **exit 2**, matching `_common.sh:21-26`, with the `record-red-check` consequence stated. **The root cause was mine and is worth recording:** the pass-5 edit used a bare `t.replace()` with no assertion and silently no-opped because my search string said 'its' where the file says 'Its own'. Every edit in this pass asserts on match first — a silently-failing edit is exactly the defect class this plan exists to close, reproduced in my own tooling. | `main-session` | `resolved` |
| C51 SC1 direct-vs-transitive ambiguity | medium | SC1 restated as **directly or transitively** `depends-on` an Epic 0 issue, with the measured figures in the cell: 13 of 23 direct, 22 of 23 transitive, sole exclusion the declared bug-fix carve-out. The annotated '~17' matched neither reading and is gone. | `main-session` | `resolved` |
| N1 SC0 wording + two residuals; index description drift; #170 notes | low | SC0 rescoped to 'every instrument **this plan creates**', noting `_shared/sync.py` and `plan_manager.py` are pre-existing. Both further residuals stated in the cell — a directory satisfies `-x`, and three instruments run via `uv run` which does not need the x-bit, so the criterion imposes a `chmod +x` obligation Issues 1.9/3.1 must honour. `index.md`'s 'Four red-team passes' corrected to six, with a note that the count is itself drift-prone and outside `reindex --check`'s reach since it checks membership rather than description content. Missing/Gate/Upstream Assessment sections added to pass-5 and pass-6. | `main-session` | `resolved` |
