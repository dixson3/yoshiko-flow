---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 1 - REVISE. The mandatory SPEC gate is unsatisfiable as
  written (measured exit 1), the SPEC epic is misnumbered so the repo coverage checker
  reports all 38 issues uncovered, and 6 verification commands are non-runnable.'
plan: plan-064-james-dixson-a0b7fa
date: 2026-09-05
---
# Red-Team Pass 1: plan-064-james-dixson-a0b7fa

## Verdict: REVISE

Three mechanical blockers make the plan's own mandatory gate unsatisfiable and six of its
verification commands non-runnable. All are cheap to fix. Two further concerns go to framing
rather than mechanics. The plan is otherwise unusually strong.

## Strengths

- **The rescope is evidence-led and honestly stated.** EXP-001 is a real refutation, and the
  Objective says out loud that #316's criteria are not discharged. That is the opposite of
  scope-avoidance dressed as diligence.
- **Verified `doc_lint` PASS** on `plan.md`, and **all 38 issues carry an SC** (mechanically
  checked — zero uncovered). Gate reachability is clean: the SPEC gate's condition is produced by
  Epic 1, which is not in its own `Blocks` set. No cycles, correct frontloading.
- **The pytest vacuity attack is REFUTED in its literal form.** Measured in a sandbox:
  `pytest -k <nonexistent>` exits **5** ("1 deselected"), not 0; a missing file exits 4. The `-k`
  criteria cannot be satisfied by an empty selection. That was the sharpest available attack and
  the plan survives it — the real risk is the inverse (C4).
- **Corroborated independently:** `recover` is absent from argparse choices, so EXP-001's
  "unreachable journal" claim holds. `_shared/sync.py` really does register 5 copies + canonical.
- R7's boundary reasoning (#318/#320/#321 in the `--skill` path) and D1's refusal to let a scope
  item silently vanish are both good instincts, correctly applied.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | high | **The mandatory capability gate and SC1 are unsatisfiable as written — measured.** `check_amendment_log.py` run in a sandbox with a *complete* amendment-log entry for both named ids exits **1**: `implementation issue(s) with no depends-on path to a REQ-naming Epic-1 issue … ['2.7','3.1'…'6.5']` — 22 issues. Cause: 1.3-1.7 say "Add a requirement that…" and name **no `REQ-*` id**, so assertion A2 has nothing to reach, and the plan declares no `no-req-required` set. Worse, A1's derived set is only `{REQ-OKF-012, REQ-OKF-CHK-004}` — the gate that `Blocks: epic:3, epic:4, epic:5` certifies **nothing** about those epics. |
| C2 | high | **The SPEC epic is numbered Epic 1; the repo's convention and its checker require Epic 0.** `check-req-coverage.py:111` hardcodes `i.get("epic") == "0"`. Measured over this plan: exit **1**, `38 non-Epic-0 issue(s); 0 direct Epic-0 dep, 0 transitive` — every issue UNCOVERED. plan-060/062/063 all title `### Epic 0: SPEC-first…`. |
| C3 | high | **Six SC verification commands are non-runnable — missing `--with pyyaml`.** Measured: SC2, SC6, SC7, SC8, SC9, SC12, SC13 die with pytest `INTERNALERROR … SystemExit: 2` from `okf_hygiene.py:45` collection. Adding `--with pyyaml` makes them run (17 passed). SC15 alone has it right, which makes this a copy error, not a policy. |
| C4 | medium-high | **SC9 is green today, before any work — via a test EXP-001 proved wrong.** `-k crash` matches the pre-existing `test_crash_recovery_all_states`; measured `1 passed`. That test is SPEC.md §5's declared coverage for REQ-OKFH-008, while EXP-001 measured the S1 recovery reports `recovered: true` with the bundle gone. The criterion is satisfiable by the exact false-green it exists to remove. SC6's `-k record` has the same latent shape. |
| C5 | medium-high | **Issues 1.3 and 1.5 propose to "add" requirements that already ship.** `skills/yf-okf-hygiene/SPEC.md` REQ-OKFH-010 already states `restore` "shall be **record-driven with a PER-PATH operation kind**"; REQ-OKFH-008 already fixes S0-S4 and "Recovery shall be **deterministic from all five**." EXP-001 found **non-conformance with shipped requirements**, not a SPEC gap. Filing new ids manufactures duplicate authority — the "ambiguous REQ ids" defect #298 tracks, which this plan *excludes* as a different axis. |
| C6 | medium-high | **The deferral is right, but its stated reason over-claims for Epics 3 and 4.** EXP-001's own conclusion is "`backfill --apply` is well-guarded — **`restore` is the dangerous verb**." All three loss paths describe conditions the in-repo transform is *not* in: the 8 targets are tracked and committed, which is the path EXP-001 measured byte-exact. For a committed corpus the rollback is `git revert`, not `restore`. The genuine transform blockers are Epic 2 and Epic 5; Epics 3/4 are engine debt worth paying but not gating. A leaner alternative is nowhere considered. |
| C7 | medium | **D3 is orphaned.** It prescribes the sandbox restore rehearsal, but no issue, gate or SC performs any rehearsal, and the Objective defers that criterion to the follow-on. Residue from the pre-D6 draft — the exact failure the plan names twice (D1, R6). |
| C8 | medium | **SC3's command does not measure SC3's criterion, and it is red today.** A no-op claim needs a before/after member-set comparison (what 2.8 produces); the drift check can only show the corpus is drift-free. Measured exit **1** right now, because **this plan's own bundle drifts** — `references/upstream-294.md` present but absent from `index.md`. |
| C9 | medium | **Epic 1 never says which SPEC file each amendment lands in, and there are three candidates.** `REQ-OKF-012`/`REQ-OKF-CHK-004` appear in **both** root `SPEC.md` and `skills/yf-okf/SPEC.md`; `REQ-OKFH-*` live in `skills/yf-okf-hygiene/SPEC.md`. `check_amendment_log.py` reads **root `SPEC.md` only**. |
| C10 | medium | **R2's mitigation is unowned.** Schema versioning + legacy refusal appears only in the Risks table; no Epic 3 issue implements it. (Blast radius is small — no committed record artifacts exist — so R2's `med` is if anything over-rated. But an unimplemented mitigation is not a mitigation.) |
| C11 | medium | **SC10 is under-powered.** `recover --help -> exit 0` is a real gate (measured: exits 2 today) but proves only that argparse gained a verb. It says nothing about Issue **4.4**'s stale-journal detection, which SC10 also claims to discharge. |
| C12 | low-medium | **"#294 must land before any `backfill --apply`" is over-claimed.** The `ghost`-inversion requires residue **present at backfill time**. Measured: the corpus is residue-free now, and the plan's own third gate enforces exactly that precondition. The accurate claim is "must land before `--apply`, *or* the corpus must be verified residue-free at apply time" — and the plan already implements the second. The follow-on will inherit the phrasing verbatim. |
| C13 | low | The residue gate's `find` covers `docs/plans docs/research` only, while the drift check declares four roots including `Incubator/*/…` (no Incubator roots exist today, so currently a no-op gap). SC17 uses an unexpanded `${SKILL_DIR}`. |

## Missing

- No issue records that **REQ-OKFH-008/010 are currently violated by shipped code whose §5
  traceability rows claim passing coverage** — the most transferable finding in EXP-001, exiting
  the plan unrecorded (C4/C5).
- No `no-req-required` declaration, which the repo's own checker expects (C1).
- No `CHANGE-VALIDATION.md` gate rows for this plan id. Prior plans wire both
  `gate-planNNN-amendment` and `gate-planNNN-reqcoverage`; 1.8's text only says "confirm".
- **Nothing on what EXP-001 did not test.** Uncovered fourth-blocker surfaces: the `_index.md`
  legacy-variant route, whether any of the 8 targets classify `hybrid-partial` rather than
  `legacy-readme`, and `--record` behaviour on a **partially-halted batch** (3.6 addresses the
  exit code, not the record contents).

## Gate Assessment

All four gates are **reachable** and none is a cycle; the SPEC gate is frontloaded as early as the
constraint permits. No frontloading miss.

- **SPEC gate** — correctly placed, but its `Test` **cannot currently pass** (C1), and it is
  *asymmetric*: real for Epic 2, ceremonial for Epics 3/4/5, because only 1.1/1.2 name ids.
- **Vendored-copies gate** — reachable, measured green (`sync.py --check` exit 0).
- **Residue gate** — reachable, measured green. Scope gap per C13.
- **Reconcile gate** — standard.

Correctly, **no consent gate**: this plan runs no corpus `--apply`, so none is owed. Consistent
with D6 and a point in the rescope's favour.

## Upstream Assessment

- **#316 `partial`** — right disposition, honestly executed. 6.1 delivers a genuine slice of scope
  item 4; 6.4/6.5 make the deferral a deliverable. Weakness is C6: the *reason* is broader than
  EXP-001 supports.
- **#294 `include`** — well specified; 1.2 is genuinely corrective, not ceremonial. Verified:
  `_shared/okf.py` has no VCS awareness. Phrasing per C12.
- **Excludes** justified and specific. One tension: **#298 is excluded as "a different axis" while
  C5 shows this plan may add duplicate REQ ids for already-shipped requirements** — the exact
  defect #298 tracks.

## Resolutions

All 13 concerns resolved by the main session; verdict stands as REVISE for pass 1, with pass 2
to re-review. Every mechanical claim below was re-measured after the fix, not assumed.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 SPEC gate unsatisfiable | high | Issues 0.3-0.7 now name concrete ids (`REQ-OKFH-010`, `-008` as amendments; `-011`, `-012`, `-013` as new). Issue 0.8 declares `no-req-required` = {1.7, 5.1, 5.2, 5.3, 5.4, 5.5}, each carrying its own reason string in its issue body as the checker requires. Re-measured: `check_amendment_log.py` now exits **2 (INCONCLUSIVE — no amendment-log entry yet)** rather than **1 (22 unreachable issues)**; the entry itself is Issue 0.8's deliverable at execution, so exit 2 is the correct pre-execution state. | `main-session` | `resolved` |
| C2 SPEC epic must be Epic 0 | high | SPEC epic renumbered to **Epic 0**; former Epics 2-6 shifted to 1-5, and every `depends-on`, gate `Blocks`, SC `Discharged-by` and cross-reference updated. A second capability gate now runs the coverage checker explicitly. Re-measured: `check-req-coverage.py` went from **exit 1, "38 non-Epic-0 issue(s); 0 direct, 0 transitive"** to **exit 0, "every non-Epic-0 issue is covered"** (31 issues: 1 direct, 15 transitive, 10 naming a REQ, 6 declared bug fix). | `main-session` | `resolved` |
| C3 missing `--with pyyaml` | high | Added to all 11 pytest verification commands. Re-measured: the same command that produced `INTERNALERROR … SystemExit: 2` now collects 17 tests. | `main-session` | `resolved` |
| C4 SC9 green via a false-green test | medium-high | Selectors pinned to **new** names (`crash_s1_bundle_present`, `crash_s2_errno66`, `restore_refuses_non_git`, …). **Measured: the broad `-k crash` exits 0 today; the pinned pair exits 5** — red until Issue 3.5 writes them, which is what a criterion should do. Added **Issue 3.6** to repair or replace `test_crash_recovery_all_states` *and* correct its `SPEC.md` §5 traceability row, plus **SC13** and **R9** to own the general defect. | `main-session` | `resolved` |
| C5 duplicate REQ ids for shipped reqs | medium-high | Verified the claim directly: `REQ-OKFH-010` already mandates "record-driven with a PER-PATH operation kind" and `REQ-OKFH-008` already fixes S0-S4 keyed "never on directory presence". Issues 0.3/0.4 recast as **amendments plus a recorded conformance defect**, not new ids. The #298 exclusion row now states the tension explicitly. | `main-session` | `resolved` |
| C6 D6's reason over-claims | medium-high | D6 restated: the strictly blocking defects are **Epic 1 (#294) and Epic 4 (8/8 halt)**. New **D10** records that Epics 2-3 are engine debt rather than transform blockers, states the leaner Epics 0/1/4 + transform alternative that was available, and gives the reason for rejecting it — plus the `git revert` rollback route, handed to the follow-on via Issue 5.4 so the transform is not hostage to Epics 2-3. | `main-session` | `resolved` |
| C7 D3 orphaned | medium | D3 marked discharged as EXP-001, with its sandbox-rehearsal method explicitly routed into Issue 5.4's follow-on payload rather than left dangling. | `main-session` | `resolved` |
| C8 SC3 mismeasures; bundle drifts | medium | Split into **SC4** (the before/after member-set comparison Issue 1.8 actually produces) and **SC5** (the drift check as a second signal). Bundle drift repaired — `references/upstream-294.md` and `reviews/pass-1.md` added to `index.md` with authored descriptions. Re-measured: drift check exit **0**, 69 bundles clean. | `main-session` | `resolved` |
| C9 SPEC target files unnamed | medium | Issues 0.1/0.2 name **both** homes (`SPEC.md` and `skills/yf-okf/SPEC.md`) and state the dual-home rule — that `check_amendment_log.py` reads root `SPEC.md` only, so root alone satisfies the gate while leaving the per-skill copy stale. Issues 0.3-0.7 name `skills/yf-okf-hygiene/SPEC.md`. | `main-session` | `resolved` |
| C10 R2 mitigation unowned | medium | Schema versioning promoted to its own requirement (`REQ-OKFH-013`, Issue 0.7), implemented by Issues 2.1/2.2, asserted by SC8. R2 downgraded `med` -> `low` on the reviewer's own measurement that no committed record artifacts exist. | `main-session` | `resolved` |
| C11 SC10 under-powered | medium | Replaced the `--help` probe with **SC12**, a pytest arm covering both `recover_verb_exists` and `backfill_refuses_stale_journal`, so Issue 3.4's stale-journal detection is actually asserted. | `main-session` | `resolved` |
| C12 ordering claim over-stated | low-medium | Restated in all three places it appeared (findings summary, Approach, EXP-002's verdict paragraph): #294 must land before `--apply` **or the corpus must be verified residue-free at apply time** — and the plan implements both, so the ordering is belt-and-braces rather than strictly forced. | `main-session` | `resolved` |
| C13 residue gate root scope | low | Gate `find` extended to the `Incubator` root with `2>/dev/null` for the no-such-directory case; SC20 now resolves the engine via `yf skill-dir yf-change-validation` instead of an unexpanded `${SKILL_DIR}`. | `main-session` | `resolved` |

### Also taken from the Missing section

- **R8** added, owning the fourth-blocker risk, with Issue **4.4** extended to probe the three
  surfaces EXP-001 did not test — the `_index.md` legacy-variant route, `hybrid-partial`
  misclassification, and the record contents of a partially-halted batch — *before* the follow-on
  inherits the work.
- **Issue 0.8** now explicitly adds the `gate-plan064-amendment` and `gate-plan064-reqcoverage`
  recipe and trigger rows to `CHANGE-VALIDATION.md`, rather than only "confirming" coverage.
- The conformance defect against `REQ-OKFH-008`/`-010` is recorded by Issues 0.3, 0.4 and 3.6.
