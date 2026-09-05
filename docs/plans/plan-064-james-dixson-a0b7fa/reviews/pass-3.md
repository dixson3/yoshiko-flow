---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 3 - REVISE. Pass-2''s ten resolutions verified, but the
  negative control added to close C15 cannot work: the crash test mocks the call site
  it observes, so reverting the fix cannot make it fail. Plus five cheap repairs.'
plan: plan-064-james-dixson-a0b7fa
date: 2026-09-05
---
# Red-Team Pass 3: plan-064-james-dixson-a0b7fa

## Verdict: REVISE

One **high** concern, measured by sandbox spike rather than inferred: **Issue 3.8's negative
control cannot do what it says**, and it is the single mechanism the plan offers against its own
highest-severity risk (R9). Everything else pass 2 raised is genuinely fixed; the remaining items
are cheap textual repairs.

## Verification of pass 2's ten resolutions (all re-measured)

| Prior | Claim | Measurement | Holds? |
| :-- | :-- | :-- | :-- |
| C14 | six `-k` expressions now quoted | All six run: SC4/SC8/SC9/SC11/SC12/SC16 -> **exit 5** (no tests collected — correct pre-work red), never exit 4. | **YES** |
| C15 | SC13 rewritten as a negative control | The false green reproduces (`-k crash_recovery_all_states` -> **exit 0, 1 passed**), but the control itself does not work — see C24. | **NO** |
| C16 | 7 unowned selectors now owned | All 16 tokens appear in exactly one issue (1.5, 1.8, 2.5, 2.6, 2.7, 3.5, 4.4). | **YES** |
| C17 | R1->1.4, R4->1.3, R5->3.5 | Each target's text read against the claim. All three correct. | **YES** |
| C18 | #294 `Resolved By` | Now `0.1, 0.2, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8` — every cited issue is Epic-0/1 gitignore work. | **YES** |
| C19 | stale refs outside plan.md | `context.md:32` Epic 0, `:70-71` Epic 5 / Epics 0-4, exp-003:131-134 all four rows -> Epic 5. No remaining stale in-bundle reference. | **YES** |
| C20 | Issue 2.8 added | Reproduced: `-k restore_round_trip` -> **exit 0, 1 passed**. Issue 2.8 exists, but nothing verifies it — see C26. | **PARTIAL** |
| C21 | four vacuous criteria | Now red before the work: **SC7 -> exit 1**, **SC18 -> exit 1**. SC5/SC6 -> 0, explicitly labelled green-before-the-work. | **YES** |
| C22 | 0.4 restates the five-state table | Present, including the §5 amendment and the forward pointer to 3.6/3.8. | **YES** |
| C23 | coverage gate labelled a regression guard | Present; `check-req-coverage.py` -> **exit 0**, 6 declared-bugfix rows matching the declared set exactly. | **YES** |

Also green today: `check_amendment_log.py` -> **exit 2** (correct pre-execution), `sync.py --check`
-> 0, `check_okf_index_drift.py` -> 0, residue gate -> 0, `doc_lint --path plan.md` -> **PASS**.

## Strengths

- **Pass 2's mechanical findings are fully discharged and re-measurable** at source.
- **C21 was fixed the hard way.** SC7 and SC18 now genuinely exit 1 today. Rewriting a criterion so
  it *can* fail is more expensive than relabelling it, and both were rewritten.
- **The scale attack does not land.** 43 issues / 6 epics / 20 SCs is inside the corpus norm
  (plan-060: 49/7/41). The critical path is 7 nodes (`0.1->0.2->1.1->1.2->1.3->1.4->1.8`); no epic is
  a serial chain. Concern-resolution has added issues, not incoherence.
- **`no-req-required` survived the growth honestly.** All four inserted issues reach Epic 0
  transitively; the carve-out was not widened to absorb new work.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C24 | high | **Issue 3.8's negative control is not implementable as written — measured.** `test_crash_recovery_all_states` (`test_okf_hygiene.py:315-360`) **hand-constructs each journal state** (`shutil.copytree`; `j.write("S1")`; `os.rename`; `j.write("S2")`) and never invokes `backfill`'s swap. Spike: applying Issue 3.1's exact phase-ordering change to `okf_hygiene.py:576-582` and re-running the test yields **exit 0, 1 passed** — byte-identical to the unmutated tree. Reverting 3.1's fix therefore **cannot** make this test fail, so `check-crash-test-detects-lag.sh` cannot be authored to spec, and SC13 — the plan's whole answer to its `high`-severity R9 — has no reachable exit code. The cited precedent `check_mock_fidelity.py` is apt for the wrong reason: it names the *diagnosis* (an instrument that mocks its call site) the plan never states. |
| C25 | medium | **Issue 5.4's `depends-on` was not shifted by the Epic-4 renumber.** Its text needs "the post-repair halt profile from **4.5**" and R8 says 4.5's probes are "carried into Issue 5.4's issue body" — but the edge reads `depends-on: 4.4`, the newly inserted test-authoring issue. 5.4 becomes ready with no halt profile to carry, and R8's mitigation is defeated by the graph rather than by a decision. |
| C26 | medium | **SC13 asserts two things and verifies one.** Its text reads "Both false greens are repaired" and its `Discharged-by` names `2.8, 3.6, 3.8`, but its command concerns only `REQ-OKFH-008`. `restore_round_trip` appears in **no** SC verification anywhere. Issue 2.8's deliverable is unverified by exit code — the C21 class reintroduced by the C20 fix. |
| C27 | low-medium | **Three `Discharged-by` cells omit the issue that authors the test their command runs.** SC4 runs `vcs_ignored_floor` (authored by **1.5**) but lists `1.3, 1.8`; SC8 runs `restore_refuses_legacy_record` (**2.5**) but lists `2.1, 2.2, 2.4, 2.7`; SC12 runs both selectors from **3.5** but lists `3.2, 3.4`. Closing the listed issues marks each discharged while its command still exits 5. |
| C28 | low | **Issue 4.6's `depends-on: 4.4` is the same un-shifted edge as C25.** The `warn -> warn` investigation needs the transform re-run (4.5), not the test-authoring issue. |
| C29 | low | **The vendored-copies gate's `Blocks` was not extended for the inserted issues.** `Blocks: 1.8, 2.5, 3.5` predates 2.7, 2.8, 3.8, 4.4, all of which run pytest against the vendored `okf.py`. 2.7 reaches Epic 2 via 2.4, which never touches 2.5, so it can run unsynced. |

## Missing

- **A statement of *why* the two tests are false greens.** Both concerns name the symptom. The
  measured cause for the crash test is that it mocks the call site it is supposed to observe.
  Issues 3.6/2.8 say "repair or replace" without that diagnosis, so the cheaper reading — patch
  assertions, keep the hand-built states — is available and would leave the false green intact
  under a new name.
- **Nothing pins `check-crash-test-detects-lag.sh` against the test being renamed.** 3.6 may
  rename; 3.8 hardcodes `test_crash_recovery_all_states`.

## Gate Assessment

All four capability gates re-measured and **reachable**, no cycles, correctly frontloaded —
unchanged from pass 2 and unharmed by the insertion. SPEC gate exit 2 (correct pre-execution);
coverage gate exit 0 over the grown 35-issue set; vendored-copies gate exit 0 but `Blocks`
under-covers (C29); residue gate exit 0. Correctly **no consent gate**.

## Upstream Assessment

Unchanged and sound. **#316 `partial`** with D6/D10 carrying the deferral; **#294 `include`** with
`Resolved By` now correct; **#298 `exclude`** with the tension stated rather than resolved by fiat.
R6/R8's anti-forgetting machinery is real — but C25 means the graph does not currently enforce the
sequencing R8 describes.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C24 negative control unimplementable | high | **Verified at source before acting** — `test_okf_hygiene.py:315-360` hand-builds every state and never calls `backfill`, so it is insensitive to the production write order by construction. Issue 3.6 changed from "repair or replace" to a **mandatory REPLACE**, with the diagnosis written in: the test *mocks the call site it exists to observe*, so patching assertions would preserve the false green under a new name. The replacement must drive the **real `backfill` swap** through the deterministic `os.rename` SIGKILL seam EXP-001 used. Issue 3.8 now pins its assertion to 3.6's replacement **by its post-3.6 name** (or to `test_crash_s1_bundle_present`, swap-driven by construction), and states that a control pinned to a mocking test is not a control. | `main-session` | `resolved` |
| C25 5.4 un-shifted edge | medium | `5.4 depends-on: 4.5`. **The fix exposed a worse defect the reviewer did not see:** correcting it left `4.5 depends-on: 4.5` — a **self-edge** — which `plan_extract.py --strict` accepted silently and which `check-req-coverage.py` caught only as an UNCOVERED issue. Both edges corrected; a self-edge and cycle scan now runs as part of the validation sweep. | `main-session` | `resolved` |
| C26 SC13 asserts two, verifies one | medium | Split into **SC13a** (crash, `check-crash-test-detects-lag.sh`) and **SC13b** (`restore`, the same script's `--req REQ-OKFH-010` arm). Issue 3.8 extended to give the script that arm; Issue 2.8 extended with 3.6's diagnosis — the replacement must assert the reversal is *driven by the recorded op list*, so a `restore` re-deriving from `rglob` + `git ls-files` fails it. A test passing under both implementations measures nothing. | `main-session` | `resolved` |
| C27 Discharged-by omits test author | low-medium | 1.5 added to SC4, 2.5 to SC8, 3.5 to SC12. | `main-session` | `resolved` |
| C28 4.6 un-shifted edge | low | `4.6 depends-on: 4.5`. | `main-session` | `resolved` |
| C29 vendored gate under-blocks | low | `Blocks: 1.8, 2.5, 2.7, 3.5, 4.4`. | `main-session` | `resolved` |
