---
type: Review
okf_spec: OKF-PLAN
id: pass-7
description: "Red-team pass 7 — REVISE, narrow and terminal-shaped. All five of pass 6's fixes verified sound and no seventh shape in the criteria layer; the remaining defects are in context.md and upstream-triage.md, which six passes never opened."
---

# Red-team pass 7: plan-056-james-dixson-473dba

## Verdict: REVISE

> **All 4 concerns resolved.** All three findings were in artifacts the main session updated at the
> D-17 split for `plan.md` but not for its siblings — a genuine omission, not a reformulation, which is
> why the fix set is deletions and value corrections rather than a redesigned check.

**Narrow, and believed terminal.** All five of pass 6's resolutions verified sound — the first pass at
which that is true. The criteria / gate / harness layer six passes hammered is clean; **no seventh shape
was found in it.** The three remaining items are in **supporting artifacts six passes never opened**, and
every fix is a deletion or a value correction: no re-scoping, no DAG change, no criterion change.

## Strengths

| Item | Verification |
| :-- | :-- |
| **C48** | Extracted gate `instructions` is **1768 chars** and contains both `test_class: probe` and `cwd: worktree` verbatim. `unparsed: []`. Holds. |
| **C49** | Extracted `blocks` = `[3.2, 3.3, 3.4]`; `gate_consistency` PASS, 0 findings. Holds. |
| **C50** | Issue 1.8 reads exit **2**; `_common.sh:20-25` declares it and `ck_inconclusive()` exits 2 at :34. Holds. |
| **C51** | Computed over the DAG: **13 of 23** direct, **22 of 23** transitive, sole exclusion 2.4 — the declared carve-out. Exact. |
| **N1** | SC0 reads "this plan creates"; `index.md` says "Six red-team passes". Holds. |

**C49's specific question — did narrowing leave an enforcement act ungated? No.** Epic 3 is exactly
`{3.1, 3.2, 3.3, 3.4}`; 3.1 authors evidence and is correctly unblocked, 3.2/3.3/3.4 are gated, and 4.3 is
transitively gated via `depends-on: 3.4`. Two things pass 6 did not check also hold: `SKILL.md:1032` says
`bd` rejects a task→epic block, so `Blocks: epic:3` may never have been pourable at all; and the
execute-start red is **transient**, because `coordinator.md:52-59` re-enumerates gates every loop
iteration and §5.2c step 3 narrows rather than stops.

## Concerns

### C52 — `context.md` asserts a destructive operation this plan does not perform, and names four issue ids that do not exist. [HIGH]

Never updated after the D-17 split. Six passes read `plan.md`; none opened it.

- **Side-effect permissions**: *"This plan performs one genuinely destructive local operation: Issue
  **5.9**'s `backfill --apply` **rewrites 30 completed plan bundles in place**. It is gated (human
  capability gate)…"* plus ~9 lines of safety evidence. There is no Issue 5.9, no backfill, and no human
  capability gate here. `plan.md` says the opposite: *"this plan touches no completed bundle's content at
  all."* Diff-confirmed verbatim pre-split text; **it belongs to plan-057**, which already carries it.
- **Network**: cites issues **3.5** and **6.6**, neither of which exists.
- **Glossary**: *"Issue **6.4** fixes that"* — that is Issue **4.1**.

HIGH because `context.md` is the reserved artifact whose declared job is recording **side-effect
permissions**, and `index.md` stakes the bundle's portability on it. **An operator authorizing this plan
is told it will destructively rewrite 30 frozen bundles under a gate that does not exist**, and every
instrument is silent: audit `pass`, `doc_lint` PASS, `reindex --check` clean. The plan's own Motivation,
reproducing inside its own bundle a second time.

### C53 — `upstream-triage.md` disagrees with `plan.md`'s Upstream Issues table. [MEDIUM-HIGH]

`index.md` bills it as *"the triage record behind plan.md's Upstream Issues table."* It is not:

- **#170 is `include`** in the triage file with the pre-split note; `plan.md` says **`deferred`**. A cold
  reader gets opposite answers from the two authoritative artifacts.
- **#265 is entirely absent** — 14 issues vs `plan.md`'s 15. The stated triage record omits an `include`
  issue this plan filed itself.
- #189's note still describes the `yf-okf-hygiene` script, which is plan-057's.

Mechanical execution is unaffected (`reconciler.md` parses `plan.md`'s table), so this is a cold-read
fix, not an execution fix.

### C54 — SEVENTH-SHAPE CANDIDATE: three of the ten instruments are unreachable by the enumerator Issue 1.9 makes the default. [MEDIUM]

Pass 6 verified `--require 10`'s arithmetic (8+1+1) but not whether the ten are **enumerable**:

- `redcheck.sh`'s `cmd_verify_red_checks` (:491) iterates `"${CHECKS_DIR}"/check-*.sh`, and
  `record-red-check` (:299-300) hard-rejects any name not matching `check-*.sh`.
- The ten names span **three** conventions: six `check-*.sh`; `harness-selftest.sh` (outside the `check-`
  namespace); two hyphenated `.py`; one underscored `.py`. **A `check-*.sh` glob finds 6 of 10.**
- The repo's live convention is `.sh` hyphenated / `.py` underscored (`check_smoke_tier.py`), which two of
  the three `.py` names violate.
- Unstated self-reference: `harness-selftest.sh` is one of the ten it must prove.

Not fatal — Issue 1.9 says derive the list from the Verification column, which names all ten. But
`--require 10` is the gate's entire non-vacuity floor, and left unstated the likeliest outcome is a
permanently non-zero test → stop class 2 on every run, which is what C49 was fixed to remove.

## Missing

- **Nothing verifies `context.md` or `upstream-triage.md` against `plan.md`.** Both drifted through six
  passes with every instrument green. Given this plan's Motivation, that belongs in Issue 4.2's filing list.
- Still nothing verifies that a gate's `Instructions:` survive extraction (pass 6's finding).
- **No `CHANGE-VALIDATION` row for the two new test files** — `test_recheck_criteria.py` (1.10) and
  `test_index_members.py` (2.4). SC28 and SC36 hold once at close and then nothing re-runs them. Pass 5
  listed this under Missing; never resolved.

## Non-blocking notes

- **Issue 2.3's `assets/` half is already done** — `_INDEX_MEMBERS` has carried `("assets/", …)` since
  plan-029; `assets/` is unlisted because `seed_index` only emits members non-empty at seed time. The
  `reindex_write` call-site half is the real fix and is stated correctly.
- **Issue 0.8's count is wrong, in the class SC27 polices**: measured, shipped occurrences are **5 across
  4 files**, including `_shared/test_okf.py:966` — a code file "three files" excludes. And "correct every
  instance" read literally reaches frozen bundles, contradicting D-1; SC27's "no shipped spec" scoping is
  the right one.
- D-17 is listed before D-16 — cosmetic.
- `assets/` and `diagrams/` are empty dirs, exempt from `reindex --check` — worth knowing before 2.3.

## Gate Assessment

| Gate | Reachable? | Frontloaded? | Verdict |
| :-- | :-- | :-- | :-- |
| Start Gate | n/a | n/a | fine |
| Verification harness ready | **Yes** — all ten producers outside the blocked set; re-evaluated each iteration so the execute-start red is transient | at its earliest legal position | **Sound**; C54 is a risk in its `Test` argument, not its placement |
| Reconcile Gate | auto | — | fine |

## Upstream Assessment

`plan.md`'s table is internally consistent: 15 rows, 15 reference files, #140 populated and named in 4.3,
#265 in 4.3's close list. `verify-reconcile` fails for the correct pre-execution reason. The defect is
**outside** `plan.md` — see C53.

## Loop termination

C52 and C53 are deletions and value corrections; C54 is one sentence. **None touches the DAG, the criteria
table, the gate, or a severity.** This fix set does not have the shape that produced six consecutive
regressions — those were all *reformulations of a check*. Pass 8 should be a verification pass, not a
discovery pass.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C52 context.md describes a backfill this plan does not do | high | Confirmed and fixed. `context.md`'s destructive-operation paragraph and its nine lines of fingerprint safety evidence were verbatim pre-split text belonging to plan-057; both deleted and replaced with the true statement — every write here is additive except Issue 3.4's repair of live indexes, and this plan modifies no completed bundle's content on any axis. The replacement **records why it survived**: every instrument reads `plan.md` and none cross-checks its siblings. `3.5`/`6.6` -> the reconcile (4.3); `6.4` -> `4.1`. Verified: zero stale issue refs remain in the file. | `main-session` | `resolved` |
| C53 upstream-triage.md disagrees with plan.md | medium-high | Confirmed and fixed. #170 re-dispositioned `include` -> **`deferred`** in the triage file to match `plan.md`, with a note recording that it disagreed after the split. **#265 appended** as a new triage section, flagged as filed by pass 3 rather than found at the scoping scan — which is why it had no entry. #189's note re-aimed from the `yf-okf-hygiene` script (plan-057's) to Issue 1.9's harness. The triage file now carries 15 issues, matching `plan.md`'s 15 rows and 15 reference files. | `main-session` | `resolved` |
| C54 `--require 10` enumerability across three conventions | medium | Accepted; the arithmetic was verified at pass 6 but not the enumerability. Issue 1.9 now states that `harness-selftest.sh` enumerates **by name from SC0's list, never by glob**, and dispatches per extension (`bash` for `.sh`, `uv run` for `.py`) — with the measurement that the ten instruments span three naming conventions and two languages while `redcheck.sh`'s enumerator reaches 6 of 10. **And it excludes itself**, so `--require` is **9**, not 10: a selftest cannot be its own RED fixture, and SC0 is what proves the tenth exists. Value updated consistently in all five places. | `main-session` | `resolved` |
| N2 sibling-artifact drift unchecked; missing recipe rows; 0.8 count; 2.3 overstatement | medium | All four. New Issue **3.2a** adds `CHANGE-VALIDATION` rows for `test_recheck_criteria.py` and `test_index_members.py`, with new **SC11c** — without them SC36 and SC28 would hold once at close and never re-run; this was listed under pass 5's Missing and never resolved. Issue 0.8 rescoped to **shipped** instances (as SC27 scopes it, since 'every instance' reaches frozen bundles and contradicts D-1) and re-measured to **5 across 4 files**, including `_shared/test_okf.py:966`. Issue 2.3 corrected to `scripts/` only — `assets/` has been in `_INDEX_MEMBERS` since plan-029 and is unlisted for the seed-time-emptiness reason instead. Issue 4.2's filing list gains both sibling-artifact drift and gate-`Instructions` extraction fidelity. | `main-session` | `resolved` |
