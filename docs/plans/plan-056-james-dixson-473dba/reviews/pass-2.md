---
type: Review
okf_spec: OKF-PLAN
id: pass-2
description: "Red-team pass 2 — REVISE. Pass 1's finding recurs inside its own resolution: the vacuity moved from -k filters into unowned instruments and missing-script exit codes."
---

# Red-team pass 2: plan-056-james-dixson-473dba

## Verdict: REVISE

> **All 16 concerns resolved by the main session.** Three of pass 2's measurements were independently
> reproduced before acting on them (pytest exit 5, `os.rename` errno 66, two `_index.md`). Re-dispatched
> as pass 3.

Pass 1's central finding **recurs in its own resolution**, in a new shape, measured rather than reasoned.

## Strengths

Verified genuinely resolved, each checked mechanically: **C5** (3.2's transitive ancestors now include
2.3 and 3.4), **C7** (read `_plan_content_fingerprint` at `plan_manager.py:3082`; `context.md`'s amended
text is accurate on every exclusion), **C9** (gate retargeted, evidence outside `Blocks`, no cycle;
`test_gates.py` 22/22), **C10** (zero backward cross-epic edges), **C16** (Approach carries 2.5/4.5 and
the severities wording). **C12** verified *reachable*: `verify-reconcile` now exits 1 with 7 rows failing
on ordinary execution-time comment requirements — #170's structural unreachability is gone.

## Concerns

### C17 — SC3 and SC24 are GREEN on unmodified HEAD. Pass 1's exact finding, reproduced by its own fix. [HIGH]

Measured via `recheck-criteria`: 40 criteria, 34 class-A, **17 evaluated, 13 FALSE, 15 inconclusive** —
and **SC3 and SC24 report `holds`**. They hold because `uv run <nonexistent>.py` exits **2**, and both
criteria expect exit 2. The harness's `126/127 -> inconclusive` guard catches missing **bash** scripts
but not missing **Python** ones. The vacuity is no longer in `-k`; it is in "expected exit == the exit a
missing instrument returns".

*Rec:* no criterion may expect a non-zero exit from a script that does not yet exist. Make SC3/SC24
two-branch predicates asserting a pair of exits differ, as C2 correctly did for SC2.

### C18 — 7 of the 8 new check scripts have no creating issue. [HIGH]

All ten named check scripts are missing from disk, and seven appear in **exactly one line of plan.md —
their own Verification cell**. Only `check_okf_index_drift.py` (3.1) and `check-pytest-ran.sh` (1.8) have
an authoring issue; `check_okf_baseline_pin.py` is only implied. `Discharged-by` lists the issues that
create the *behaviour*, never the *instrument*. R13 — the risk pass 1 created — is realised one level up.

*Rec:* add an issue owning the whole check harness, with its own SC, and add it to every affected
criterion's `Discharged-by`.

### C19 — Issue 1.8's stated rationale is FALSE, and its scope is unnecessary. [HIGH]

Measured, sandbox spike: `pytest.main([file,"-q","-k","nothing_matches_xyz"])` returns **5, not 0**. The
repo already records this — `CHANGE-VALIDATION.md`'s preamble carries a plan-046 correction: *"Executed
on this tree: `pytest -k <no-match>` exits 5 … neither is a vacuous pass."* Measured on HEAD:

- `python3 -m pytest _shared/test_okf.py -k this_matches_nothing_xyz` -> **exit 5**
- `uv run _shared/test_okf.py -k this_matches_nothing_xyz` -> **exit 0**

**The vacuity exists only in the direct-file invocation form, which the repo's recipe never uses.** So the
script alone closes C1 with zero test-file edits. Issue 1.8 instead prescribes rewriting "every Python
test entrypoint": **34 `pytest.main` sites** plus **15 test files with no `__main__`**, several
hand-rolled non-pytest — a repo-wide refactor on the critical path of 12 criteria, to enable a filter the
recipe does not use.

*Rec:* correct the false clause, citing `CHANGE-VALIDATION.md`'s existing measurement. Re-scope 1.8 to
the script only, invoking module-form pytest.

### C20 — SC28 targets a file with zero test functions; SC10b names a test nothing creates. [HIGH]

`_shared/test_doc_lint.py` has **0 `def test`**, no pytest import, no `__main__` — a flat `check()`-call
script. And `_ensure_index_lists_member` lives in **`plan_manager.py:784`**, not `doc_lint.py`, so SC28
names the wrong file entirely. SC10b's `index_add_verb` test exists in no issue's scope — 2.5 says only
"add the verb".

*Rec:* retarget SC28; have 2.5 create the test; specify `check-pytest-ran.sh`'s behaviour on hand-rolled
entrypoints (INCONCLUSIVE, not pass).

### C21 — C8 is NOT resolved: the "single directory swap" is not atomic. [HIGH]

Measured, sandbox spike: `os.rename(stage_dir, existing_bundle_dir)` -> **OSError errno 66, Directory not
empty**. POSIX `rename(2)` cannot replace a non-empty directory. The minimum is two renames, with a window
in which **the bundle does not exist at all** — so R3's "untouched or complete" is literally false.
`renamex_np(RENAME_SWAP)` is macOS-only and unexposed in Python, and D-2 requires cross-repo portability.
`$(mktemp -d)` also risks `EXDEV`. SC31b does not cover this — it kills between transform *steps*, not
inside the swap.

Pass 1 said atomicity was asserted, not mechanised. The resolution named a mechanism that is not atomic
either — a renamed problem.

*Rec:* state the real invariant — **crash-recoverable**, not atomic — with a three-state recovery table.
Stage inside the repo tree. Add an SC killing between the two renames.

### C22 — SC33b is unsatisfiable without violating R11. [HIGH]

Measured: `./target/debug/yf skill-dir yf-okf-hygiene` -> **exit 1**, "not installed at any known
destination (4 searched)". The resolver searches install destinations only; the repo's `skills/` tree
matches none. The skill becomes resolvable only after `yf skills install`, which **R11 forbids
mid-execution**.

*Rec:* move SC33b past land-the-plane, or replace with a repo-tree assertion plus an install dry-run.

### C23 — The `_index.md` route has no valid target, and the claim justifying its exclusion is false. [HIGH]

Issue 5.3 says "the repo's ONLY `_index.md`" is inside plan-029's fixtures. **There are two** — that
fixture and **`docs/research/001-okf-compliance-delta/_index.md`, a live bundle**. EXP-005's count of 1
referred to the live one; the plan merged them and named the wrong instance. Consequence: D-11 mandates
`_index.md` support on a figure that is **227 of 243 concentrated in one foreign repo**, D-10 bars
executing there, 5.9 is scoped to `docs/plans`, and SC19b asserts the fixture is never touched — so 5.6
and SC30 can only ever run against self-authored fixtures.

*Rec:* correct the claim; either bring `docs/research/001` into 5.9's scope as the live target, or state
plainly that 5.6 is speculative and SC30 is fixture-only.

### C24 — D-13 and Issue 2.5 name different third steps. [HIGH]

D-13 says step 3 is **`seed_index`**; Issue 2.5 says the new **`index-add`** verb "is also the backfill's
step 3". Different operations, and 5.4 `depends-on: 2.5`, so the implementation follows 2.5 and diverges
from the decision. 5.4 never enumerates the three steps. Compounding: the three-step transform was
measured on **plan-020 only, n=1**, while the 30/30 and 29/30 figures were measured over `migrate`
**alone** — the transform D-13 rejects. The evidence does not transfer.

*Rec:* reconcile D-13 with 2.5; enumerate the steps in 5.4; state n=1 and that SC15/SC15b are the
generalisation test.

### C25 — C15's fix replaced one unsourced figure with two more. [HIGH]

`140/247` appears in **no finding's measurement** — only in EXP-003's *Implications* as an assumed
figure; the "EXP-003: 140/247" attribution originates in `pass-1.md`. SC12 now calls it "the measured
140-of-247 baseline" and hard-codes it as a gate argument. `1634 / 1603` appears in **no finding at all**.
`0 of 498` (D-8's basis, labelled "Measured:") appears only in pre-experiment `upstream-triage.md`.

*Rec:* cite the finding and line, or re-run the measurement now; strip "measured" from any cell that
cannot cite one.

### C26 — EXP-006's own "do not carry this forward" instruction was dropped. [HIGH]

EXP-006 rec 5: *"Do not carry forward any claim that the corpus passes B1/B2 from this run — 1285 of 1383
concepts were never inspected."* `1285`, `1383` and `B1/B2` appear **nowhere in plan.md**. The plan states
the bare "32 of 1567" and declares #170's read half "discharged" with **93% of concept documents never
examined**. The finding said X-with-caveat; the plan says X. Separately EXP-006's categorisation sums to
**1563, not 1567**, and plan.md carries both numbers four lines apart.

*Rec:* carry the coverage caveat into #170's Notes and Issue 6.2; reconcile 1563/1567.

## Missing

- An issue owning the check-script harness (C18).
- Any criterion that `check-pytest-ran.sh` itself is correct — 12 criteria rest on one unverified script.
- A `CHANGE-VALIDATION` row for `test_okf_hygiene.py`; without it SC20 is a one-shot.
- Anything reconciling `yf-okf`'s SKILL.md after `assess` migrates, and anything setting the two OKF
  skills' trigger boundary — in a repo whose always-loaded rules are almost entirely about that.
- A recovery criterion covering the **swap window** rather than the transform steps.

### Medium

- **SC11 is vacuous w.r.t. the row it verifies**: `change_validation.py run --tier full` exits 0 today,
  before 3.2 adds the row. Assert the row id is present in the manifest and in the run's JSON.
- **SC33 branches on `--classify`'s exit code**, which the always-loaded rule explicitly forbids; `class:
  empty` also exits 0, so an empty `SKILL.md` satisfies it. Assert `class == "selected"`.
- **SC3's expected exit 2 is also the driver's INCONCLUSIVE code** — the plan's own thesis reproduced.
  And `--root /nonexistent` tests the top root, not a nonexistent *enumerated* root.
- **Epic 0 exempts itself from SPEC-first**: 1 of 12 issues names a concrete REQ id; 8 are bare `REQ-*`
  placeholders. SC1's scope is "Epic 1-6", so nothing checks Epic 0's own requirements.
- **D-14's "shared mechanism" is one-sided** — no issue makes `doc_lint` read §3b.
- **Issue 5.3 makes a cross-repo skill depend on a yf-plan-private file** absent from the 41 foreign repos.
- **Issue 1.6 fixes 1 of 4 copies of the false banner.**
- **Epic 4 re-arms R1 after the gate is live** — 4.1/4.4 widen what counts as drift with no re-repair
  issue and no `depends-on: 3.4`.
- **Issue 0.8 misses 4 of 6 "0 of 423" instances** and a third file; cites D-5 where it means D-4/D-8.
- **D-7 and D-8's Basis cells still carry premises the findings retracted.**
- **D-1 is violated on the `okf_native` axis** by the backfill; SC15c mitigates, the decision table never
  records it.

### Low

- R9 cites "Issue 3.5", which no longer exists. "Six epics" vs seven. R12 says "46 issues" vs 51.
- The Motivation carries a mangled sentence from the C15 edit (duplicated clause, dangling "That is,").
- `uv run …check-fixture-carveout.sh` is a category error — drop `uv run` for bash scripts.
- "the 2 that escape fire zero times" is unsourced and sits in tension with D-15.
- "max 30 entries" promotes an observed corpus maximum to a rule bound.
- `133` vs `134` disagree inside EXP-002 itself.

## Gate Assessment

| Gate | Reachable? | Frontloaded? | Verdict |
| :-- | :-- | :-- | :-- |
| Start Gate | n/a | n/a | fine |
| Backfill authorization -> 5.9 | Yes | correctly late | Sound; counts verified (39 total / 30 depth-1 / all 30 git-tracked) |
| Upstream network -> 6.1 | Yes | yes | **Resolved** — C9 closed correctly |
| Reconcile Gate | auto | — | fine |

No gate cycles. `test_gates.py` 22/22.

## Upstream Assessment

`verify-reconcile` now runs and fails legitimately (exit 1, 7 rows), all execution-time comment
requirements — C12 resolved. Two residuals: #170's read half is declared discharged over a
93%-uninspected corpus (C26), and **#165's discharge via 3.2 is questionable** — `REQ-PORT-010` resolves
to two unrelated requirements in two specs, and the intended one is scoped to `docs/research/*/`, which
Issue 3.1's driver and SC10's `--min-roots 30` do not cover.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C17 SC3/SC24 green on HEAD | high | SC3 and SC24 rewritten as two-branch contract scripts asserting a PAIR of exits differ, so a missing instrument cannot satisfy them. Verified: `recheck-criteria` now reports 10 FALSE / 1 holds, and the single remaining `holds` (SC11b) is a documented invariant, not a progress marker. A second rule added to the Verification convention block forbidding any criterion from expecting a non-zero exit from a not-yet-existing script. | `main-session` | `resolved` |
| C18 7 of 8 check scripts unowned | high | New Issue 1.9 owns the whole verification harness — all eight check scripts, each required to be two-branch where it asserts a failure code and to fail loudly when it inspected nothing. Added to the `Discharged-by` of every criterion that invokes one (SC1, SC2, SC3, SC5, SC6, SC9, SC11, SC12, SC15c, SC24, SC33, plus the new SC20b/SC30b). | `main-session` | `resolved` |
| C19 1.8 rationale false, scope excessive | high | Independently reproduced: module-form `pytest -k <no-match>` exits **5** (`22 deselected`), and `CHANGE-VALIDATION.md:17` already recorded that from plan-046. My earlier exit-2 reading was a collection error from missing PEP 723 deps. The convention block now states the narrow truth — the vacuity exists ONLY in the direct-file `uv run <file>` form, which the recipe never uses — and Issue 1.8 is re-scoped to the wrapper script alone, with the 34-call-site refactor explicitly out of scope. | `main-session` | `resolved` |
| C20 SC28 wrong file; SC10b test unowned | high | SC28 retargeted to a new `skills/yf-plan/scripts/test_index_members.py` created by Issue 2.4, since `_ensure_index_lists_member` lives in `plan_manager.py:784` and `_shared/test_doc_lint.py` has zero test functions. Issue 2.5 now explicitly creates the `index_add_verb` test. Issue 1.8 must return INCONCLUSIVE, never pass, on a hand-rolled non-pytest entrypoint. | `main-session` | `resolved` |
| C21 directory swap is not atomic | high | Independently reproduced: `os.rename` onto a non-empty directory raises **OSError errno 66**. R3 and Issue 5.4 no longer claim atomicity — the invariant is now **crash-recoverable**, with a documented three-state recovery table and a startup resume check. Staging moved inside the repo tree (measured `EXDEV` risk with `$(mktemp -d)`). New SC31c kills the run inside the swap window specifically, which SC31b did not cover. | `main-session` | `resolved` |
| C22 SC33b unsatisfiable under R11 | high | Verified: `yf skill-dir yf-okf-hygiene` exits 1 today and cannot pass without `yf skills install`, which R11 forbids mid-execution. SC33b replaced with a deploy dry-run that greps for the skill name — verified non-vacuous, since the dry-run enumerates all 19 currently-installed skills and `yf-okf-hygiene` is absent. Switched to the non-deprecated `yf harness skills` verb. The reasoning is recorded in the criterion cell so the omission of a resolver assertion reads as deliberate. | `main-session` | `resolved` |
| C23 two `_index.md`; route has no target | high | Verified: there are **two** `_index.md`, and the live one is `docs/research/001-okf-compliance-delta`. Issue 5.3's false claim corrected; Issue 5.6 now names that bundle as the route's only real in-repo target and states plainly that beyond it the route is speculative; Issue 5.9 scope extended to 31 bundles; new SC30b exercises the route against the live target rather than only fixtures. | `main-session` | `resolved` |
| C24 D-13 vs 2.5 third step; n=1 | high | D-13's third step reworded to 'regenerate the listing' — the surface Issue 2.5 exposes — so decision and issue name the same operation. Issue 5.4 now enumerates all three steps explicitly and records that the end-to-end transform was measured at **n=1 (plan-020)** while the 30/30 and 29/30 figures were measured over `migrate` alone, so SC15/SC15b are the generalisation test rather than a confirmation. | `main-session` | `resolved` |
| C25 replaced unsourced figure with two | high | Both figures re-measured today rather than re-cited. Boilerplate is **142/257** over 276 entries with 127 distinct strings — not 140/247 — and SC12's gate argument updated to match, with the measurement date in the cell. D-1's basis replaced with the measured corpus totals: 1088 files, 1642 findings, 1603 at `bundle_status: complete`, and **392 findings currently demoted E/W->R**, which is the real number the old '~423' was standing in for. | `main-session` | `resolved` |
| C26 EXP-006 caveat dropped | high | EXP-006's coverage caveat carried into three places: #170's Notes cell, Issue 6.2's text, and the findings-summary row. #170's `partial` is now justified on BOTH halves — the untestable write half and the 1285-of-1383 uninspected read half — rather than the write half alone. 1567 reconciled to 1563 throughout. | `main-session` | `resolved` |
| M1 SC11 vacuous; SC33 exit-code branch; SC3 signal collision | medium | SC11 replaced with a recipe-row assertion (a bare full-tier run exits 0 today, before the row exists). SC33 now asserts `class == "selected"` via a check script rather than branching on the classify exit code, which `class: empty` also returns — the always-loaded rule forbids exactly that. SC3's expected-exit collision with INCONCLUSIVE removed by the two-branch rewrite. | `main-session` | `resolved` |
| M2 Epic 0 exempts itself from SPEC-first | medium | Nine Epic-0 issues now name concrete REQ ids (`REQ-DATA-044`/`-071`/`-072`, `REQ-OKF-CHK-003`/`-004`, `REQ-OKF-012`/`-033`, `REQ-OKFH-001..010`, `REQ-PLAN-081`, `REQ-CLI-017`) instead of bare `REQ-*` placeholders. 0.8 and 0.12 remain deliberately id-less: both correct figures rather than declare behaviour, and 0.12's text now says so. | `main-session` | `resolved` |
| M3 D-14 one-sided; 5.3 cross-repo dep; 1.6 partial | medium | D-14 made two-sided — Issue 1.5 now teaches `doc_lint` to READ §3b, so the invariant is checkable from both layers rather than asserted. Issue 1.6 extended to all four copies of the false banner, since `DRIFT-CHECK.md:194` names the engine banner and fixing one leaves a declared edge red. Issue 5.3's default exclusion set made self-contained, because `skills/yf-plan/OKF-EXTENSION.md` does not exist in the 41 foreign repos D-2 targets. | `main-session` | `resolved` |
| M4 Epic 4 re-arms R1; 0.8 scope; D-7/D-8/D-1 basis rows | medium | Issue 4.4 gains `depends-on: 3.4` and an in-issue re-repair, so Epic 4's widening of drift cannot re-arm R1 after Epic 3 closed it. Issue 0.8 rescoped to all 6 instances across three files, with the off-by-one line reference and the D-5/D-4 citation error corrected. D-7's and D-8's Basis cells now carry the findings' retractions rather than the superseded premises, and D-1 records the `okf_native` axis explicitly. | `main-session` | `resolved` |
| M5 yf-okf reconciliation and trigger boundary missing | medium | New Issue 6.7 removes `yf-okf`'s advertised-but-unimplemented `assess` verb once 5.1 absorbs it and writes the trigger boundary between the two OKF skills, with new SC34. New Issue 5.10 adds a `CHANGE-VALIDATION` row for `test_okf_hygiene.py` with new SC20b, so the suite runs on every land rather than once. | `main-session` | `resolved` |
| L1 stale counts, mangled sentence, `uv run` on bash | low | Motivation's mangled duplicate clause removed. 'Six epics' -> seven; R12's '46 issues' -> 51; R9's dead 'Issue 3.5' reference -> 6.1a. `uv run` dropped from every bash-script verification. 1563/1567 reconciled. | `main-session` | `resolved` |
