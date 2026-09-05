---
type: Plan
okf_spec: OKF-PLAN
description: 'Make the yf-okf-hygiene backfill/restore engine trustworthy enough to
  run the #316 corpus transform: gitignore-aware member enumeration (#294), a restore
  that cannot silently destroy data, a sound and reachable crash journal, an honest
  dry run, and an objective-reconcile path'
id: plan-064-james-dixson-a0b7fa
author: james-dixson
created: '2026-09-05'
status: approved
deliverable_class: standard
fingerprint: 68c76d5248b9f26508d9a4a42193ca0154b9426ffe59a5cb93242aaa65620fcf
---
# Plan: Make the yf-okf-hygiene backfill/restore engine trustworthy enough to run the #316 corpus transform: gitignore-aware member enumeration (#294), a restore that cannot silently destroy data, a sound and reachable crash journal, an honest dry run, and an objective-reconcile path

**ID:** plan-064-james-dixson-a0b7fa
**Author:** james-dixson
**Created:** 2026-09-05
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** 68c76d5248b9f26508d9a4a42193ca0154b9426ffe59a5cb93242aaa65620fcf

## Objective
Make the yf-okf-hygiene backfill/restore engine trustworthy enough to run the #316 corpus transform: gitignore-aware member enumeration (#294), a restore that cannot silently destroy data, a sound and reachable crash journal, an honest dry run, and an objective-reconcile path

**This plan deliberately does NOT run the 8-bundle corpus transform.** EXP-001 measured that the
transform cannot run — 8/8 targets halt — and that its advertised rollback destroys data on
three paths. #316's acceptance criteria (`legacy: 0`, a rehearsed `restore`) are therefore
**not** discharged here; they are discharged by the follow-on transform plan this one unblocks.
Saying so plainly is the point: a plan that claimed `legacy: 0` while the engine halts 8/8 would
be asserting a green it never measured.

## Motivation
Eight historical plan bundles in `docs/plans/` still carry the legacy `README.md` layout
instead of the OKF-reserved `index.md` + `log.md` + frontmatter model that every yf artifact
skill now emits and that `yf-okf-hygiene` classifies against. They are the last `legacy-readme`
population in the repository.

Two things are affected. **Cold readers** — a plan bundle is meant to be portable, readable
from the folder alone; a bundle whose orientation file is a legacy prose `README.md` is not the
artifact the OKF contract promises. And **the corpus-level checks** — `okf_hygiene.py audit`
and the `okf-index-drift` CHANGE-VALIDATION row both reason over the conformant model, so a
persistent legacy tail means the corpus can never be asserted clean, and every future audit
reports the same eight rows that everyone has learned to read past.

The trigger is #316, plan 2 of 3 in a website/docs realignment split. Its sequencing
prerequisite, #315 (README layout standardization, plan-061), is **closed** — the layout
contract that governs what a conformant bundle's files look like is now settled, so
transforming the corpus onto it no longer risks backfilling onto a contract about to change.

The work is a corpus rewrite of tracked files, which is why reversibility is a first-class
deliverable rather than an afterthought: `restore` exists, but a reversal path that has never
been exercised is an assumption, not a capability.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #316 | Plan 2/3: run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles | partial | **Re-dispositioned from `include` on EXP-001.** This plan unblocks #316 by repairing the engine; the 8-bundle transform and #316's `legacy: 0` criterion are discharged by the follow-on it files. | 4.5, 5.4, 5.5 |
| #294 | okf index drift enumerates gitignored build residue | include | Operator scoped a real fix into this plan (D2), not a contingency. EXP-002 then found it is a **hard prerequisite** of any `backfill --apply`. | 0.1, 0.2, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8 |
| #140 | yf-okf: enforce OKF structure below the bundle root; index drift/regeneration model | exclude | Adjacent and larger. This plan runs the transform the existing engine already implements; it does not deepen the model below the bundle root. | — |
| #171 | yf-okf: nested index.md generation, deferred behind a `description:` producer change | exclude | Explicitly deferred upstream behind a producer change this plan does not make. | — |
| #298 | OKF/spec-family hygiene: ambiguous REQ ids, stale authority pointers, okf_version split | exclude | Spec-family hygiene, a different axis. **Tension acknowledged (red-team C5):** an earlier draft would have filed *new* REQ ids for `restore` record-drivenness and journal determinism — behaviors `REQ-OKFH-010` and `REQ-OKFH-008` **already require** — which is exactly the ambiguous-id defect #298 tracks. Issues 0.3 and 0.4 now amend those ids and record a **conformance defect** instead of minting duplicates, so this plan no longer contributes to #298. | — |
| #271 | plan-056 execution tracking | exclude | An unrelated coarse plan tracker; matched only on keyword. | — |

## Investigation Findings

| Exp | Question | Verdict |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-backfill-restore-roundtrip.md) | Does the backfill → restore round-trip reverse a real legacy bundle cleanly? | **REFUTES THE PREMISE.** 8/8 target bundles halt; `restore --apply` has 3 silent total-loss paths; the journal is unsound and unreachable. |
| [EXP-002](findings/exp-002-issue-294-index-drift-residue.md) | Reproduce #294 and find the minimal correct fix. | Fix is ~27 LOC in the **engine**. It must land before `backfill --apply` **or the corpus must be verified residue-free at apply time** — else 8 committed `index.md` files gain permanent `ghost` findings. |
| [EXP-003](findings/exp-003-okf-extension-drift-nodes.md) | Do the 3 per-skill `OKF-EXTENSION.md` files need `DRIFT-CHECK.md` nodes, and does that belong here? | **Route to #247.** Take only a 2-line `CHANGE-VALIDATION.md` slice here. |

### EXP-001 — the backfill is a no-op today, and `restore` is not a safe undo (premise refuted)

**8/8 of the target bundles halt on unmodified real input.** Seven halt on
`objective-divergence` — `plan.md`'s H1 grew during re-scoping while `README.md`'s `>` line did
not, so the guard is correctly detecting real divergence with nothing in the engine to reconcile
it. The eighth, `plan-030`, clears the dry run and then halts under `--apply` on
`phase-log-loss`, **a guard the dry run never runs** (it is computed after staging, inside
`if apply:`), so `would-backfill` is a weaker claim than it reads as.

`SKILL.md` claims 7 of 31 legacy bundles halt on objective divergence. On the population that
actually remains the rate is **7/8** — the easy bundles were already done; what is left is
precisely the residue the guard fires on.

**`restore --apply` is a `git checkout` with an unlink pass, mislabelled as record-driven.** The
`--record` file carries a before/after audit verdict and **no operations at all** — no created,
deleted or modified paths. `restore` re-derives them by `rglob` + `git ls-files` at restore
time. Round-trip *is* byte-exact on the happy path, but only because `git checkout` restores
committed bytes. Three measured paths destroy data while reporting `pass` / exit 0: a **non-git
tree** (entire bundle deleted), an **untracked bundle** (total loss — the realistic case for an
uncommitted plan), and **post-backfill edits** (every untracked file in the bundle unlinked, no
dirty-tree guard, no warning).

**The crash-recovery journal is unsound and unreachable.** `recover()` has **no CLI verb**, and
`backfill` never calls it on entry, so a stale journal is never noticed. Both swap windows are
mis-journalled: a crash after rename 1 leaves the journal reading `S1`, so `recover()` takes the
"nothing irreversible happened" branch, **rmtree's the transformed staging copy**, and reports
`recovered: true` with the bundle gone; a crash after rename 2 raises the unhandled errno-66
the module docstring cites as the reason the two-rename design exists.

**Also measured:** the transform never stamps `description:` (REQ-DATA-075), so a backfilled
bundle still fails that convention; and the audit verdict does not improve (`warn` → `warn`) on
any of the 7. `backfill --apply` itself is well-guarded and idempotent — **`restore` is the
dangerous verb, not `backfill`.**

### EXP-002 — #294 must land BEFORE the backfill

The member walk (`_shared/okf.py:_listing_members`) has **no version-control awareness at all**
— `subprocess` is not even imported. The driver's `git_ignored()` filter applies to **bundle
roots, not members**, so the gitignore-awareness stops one level above where it is needed.

**The defect is bidirectional, and the backfill can make it permanent.** The `ghost` inversion
requires residue to be **present at backfill time**, so the precise claim is: #294 must land
before `--apply`, *or* the corpus must be verified residue-free at the moment of apply. Measured,
the corpus is residue-free today, and this plan's residue gate enforces exactly that precondition
— so the ordering is belt-and-braces rather than strictly forced. The plan takes both. Residue present at
backfill time is enumerated into the new `index.md` (`okf_hygiene.py:486` calls the same
`_listing_members`; `:539` `copytree`s the bundle wholesale, residue included). Once committed,
deleting the residue inverts the polarity: `missing` becomes **`ghost`** — red on every clone,
including a clean one, until 8 `index.md` files are hand-edited. The 8 targets are currently
*invisible* to the check (they short-circuit at `no-index`); writing an `index.md` enters them
into the judged set for the first time.

The fix is **engine**-side: a `_vcs_ignored()` helper using `git ls-files -o -i
--exclude-standard` (not the issue's proposed `git check-ignore` — `-o` makes a tracked member
structurally undroppable, and it is one call per bundle). Measured: a **no-op across all 68 live
bundles**, ~18 ms/bundle. ~27 hand-written LOC + `_shared/sync.py` regenerating 5 vendored
copies.

**Filter on *ignored*, never on *tracked*.** An untracked-but-not-ignored `scratch-notes.md` was
*correctly* flagged; a `git ls-files` fix would suppress it, and since the FAST tier fires
**on edit** — when a newly authored `findings/foo.md` is by definition untracked — that fix
would make the check structurally unable to see the drift it exists to catch. The SPEC is
imprecise the same way (REQ-OKF-CHK-004 says "untracked"; the mechanism is "ignored") and needs
correcting in the same amendment.

**Adjacent hazard:** `.okf-hygiene-staging/` and `.okf-hygiene-journal/` sit **inside** the
`docs/plans/*` root glob, and `pathlib.Path.glob('*')` *does* match dotted names (unlike
`glob.glob`). `Journal.clear()`'s own docstring records this already cost `64 → 66` enumerated
bundles. They survive a halt and are untracked-but-not-ignored, so the driver's root filter
misses them.

### EXP-003 — OKF-EXTENSION drift nodes (D1 resolved)

**#316's premise is overstated and must be restated before a red-team pass sees it.** Measured:
**0/3 noded · 1/3 behaviorally covered · 2/3 uncovered on every axis**. `grep -i extension
DRIFT-CHECK.md` returns nothing, so "no §1 node" is true for all three — but
`CHANGE-VALIDATION.md:268` wires `yf-plan`'s file to `okf-index-drift` + `uv-okf`, and
`_shared/test_okf.py` asserts against it twice. "Nothing checks them" is **false for `yf-plan`**.

**A node would catch real drift, but the modest class of it.** All three still carry plan-029
`Status: DRAFT — proposal only` banners while plan-029 is `complete`; `yf-research` cites
`HEADER_TEMPLATE`, deleted from `index_manager.py` **in the same commit that created the file
citing it**; `yf-plan` cites `seed_readme` (actually `seed_index`). That drift then survived
plan-054's full 52-edge sweep — the sweep that produced #247 — because no node covers it, so the
sweep could not look. Against that: #319/#320/#321 (2×P0, 1×P1) all live *inside* these files and
a cheap cross-ref edge would have caught **none** of them. This is a documentation-hygiene
instrument, not a P0 instrument.

**The rows are ~8 lines; the tail is an epic.** Adding them turns the edges red on day one (2
dangling symbols, 3 false DRAFT banners, 2 shipped-but-"open" decisions, 2 mis-parsed fields),
and the `bundle_form`/`reserved_subdirs` vacuity is a SPEC question — so SPEC-first puts a
`skills/yf-okf/SPEC.md` amendment ahead of it, pulling in 6 `okf.py` copies.

**Three reasons it is not this plan's work:** the subject matter is disjoint (bundles under
`docs/plans/` vs. engine config under `skills/`); #318/#320/#321 are open P0/P1s **in the
`--skill`/member-resolution path this backfill exercises**, so editing member files mid-backfill
changes the inputs to an engine with three live severity-1 defects in that path; and #247 is
already open, is the same class of gap, in the same file, for the same reviewer.

**Adjacent gap, recorded rather than absorbed:** a fifth vendored `okf.py`
(`skills/yf-okf-hygiene/scripts/okf.py`) has no node and no edge — §1 declares four `okf-copy-*`
nodes for five copies. All six are byte-identical today, so it is uncovered but *happens* to be
in sync. Routed to #247 alongside.

## Scoping Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D1 | The `OKF-EXTENSION.md` drift-node question (#316 scope item 4) was **investigated before being decided**. **Resolved by EXP-003: the node work routes to #247; this plan takes only the honest 2-line `CHANGE-VALIDATION.md` slice, and records the routing explicitly.** | #316 says "decide in scoping", and the evidence did not exist. EXP-003 measured it: the manifest rows are ~8 lines but produce a red run whose remediation carries a SPEC-first amendment ahead of it, and the member files sit in the `--skill` resolution path where #318/#320/#321 are open P0/P1s — the exact path this backfill exercises. A scope item that merely disappears is indistinguishable from one that was forgotten, so the routing is a deliverable, not silence. |
| D2 | **#294 is fixed in this plan**, not carried as a contingency. | Operator decision. The backfill rewrites the same bundle surface the drift check enumerates, so the two are touching one artifact; fixing the check while it is already in hand is cheaper than a second pass. |
| D3 | The restore rehearsal runs on a **sandbox copy of a real legacy bundle**, outside the repository. **Discharged as EXP-001, and its method is handed to the follow-on by Issue 5.4** — it is not a live deliverable of this plan. | `backfill` has no per-bundle selector (only `--root`), so a per-bundle rehearsal needs its own root. A sandbox copy exercises the real journal on real content at zero risk to tracked files. The rehearsal already happened once, as the experiment that refuted the premise; re-running it belongs with the transform. |
| D4 | `verdict: pass` from `audit` is **not** the acceptance signal. | `audit` is read-only classification; "pass" means the classification succeeded. The actionable number is `legacy: N`. Reading the verdict as "nothing to do" is the vacuous-check misread (#263) this family of work keeps hitting. |
| D5 | Plan root is `docs/plans/` (no incubator scope). | `pwd` is the repository root, outside `Incubator/`. |
| D6 | **The 8-bundle corpus transform is DEFERRED to a follow-on plan.** This plan delivers engine trustworthiness only. | Operator decision, taken on EXP-001. **The strictly blocking defects are Epic 1 (#294) and Epic 4 (8/8 halt — 7 on objective divergence, 1 on an apply-only guard the dry run never runs).** Epics 2 and 3 are engine debt this plan pays while the engine is in hand, not transform blockers — see D10, which records why they are not deferred with it. |
| D10 | Epics 2 and 3 are **not** transform blockers, and the plan says so rather than borrowing their severity. | Red-team C6, accepted. EXP-001's own conclusion is that `backfill --apply` is well-guarded and **`restore` is the dangerous verb** — and all three loss paths describe conditions the in-repo corpus is *not* in: the 8 targets are tracked and committed, which is exactly the path EXP-001 measured **byte-exact**. For a committed corpus the rollback is `git revert`, not `restore`. A leaner Epics 0/1/4 + transform was therefore genuinely available. It is rejected because the same session would be shipping a `restore` it has just proven destroys data on three paths, and a journal whose recovery verb cannot be invoked — leaving the follow-on to trust an engine this plan measured and declined to fix. The `git revert` route is recorded and handed to the follow-on (Issue 5.4) so the transform is not hostage to Epics 2-3 if they slip. |
| D7 | `restore` gets **both** halves: the three refusal guards **and** a real per-path record written by `backfill`. | Operator decision. Guards alone close the loss paths but leave `restore` a `git checkout` wearing a record-driven label — which is what made criterion 2 of #316 unverifiable in the first place. The record is what makes a reversal claim checkable rather than incidental to `git`. |
| D8 | Objective divergence is resolved by an engine `--reconcile-objective` mode, not 7 hand-edits. | Operator decision. `plan.md`'s H1 is authoritative; the divergence is mechanical and will recur for every future legacy bundle. Seven hand-edits are seven things nobody re-verifies. |
| D9 | This plan is **SPEC-first**: every behavior change below lands its `REQ-*` amendment before its code. | Repo convention (`AGENTS.md`). EXP-002 additionally found the governing requirement already **half-implemented** — REQ-OKF-CHK-004 mandates gitignore-awareness but is scoped to "the driver" while the defective code is the engine — so the amendment is corrective, not merely ceremonial. |

## Approach

**Repair the instrument, then hand the corpus transform to a follow-on that can trust it.**

The three experiments converge on one shape. EXP-001 established that the transform is blocked
by the engine rather than by effort; EXP-002 established that #294's fix must precede any
`backfill --apply` or the damage becomes permanent and committed; EXP-003 established that the
one genuinely adjacent scope item is 2 lines, and the rest belongs to #247. So this plan is
five engine repairs plus a scope-closure epic, sequenced SPEC-first.

**Ordering is forced, not chosen.** The SPEC amendments gate the code (repo convention, D9).
#294's fix gates any future `--apply` unless the corpus is verified residue-free at that moment
(EXP-002's `ghost`-inversion mechanism needs residue *present* to fire; the residue gate is the
second guarantee). The record
rewrite gates the restore guards, because the guards' refusal conditions are stated in terms of
what the record knows. Everything else is parallel.

**What this plan does not do:** it does not transform a bundle, and it does not claim
`legacy: 0`. The deliverable is an engine whose dry run predicts its apply, whose rollback
refuses rather than deletes, and whose crash recovery can be invoked at all.

**Validation posture.** Every repair below is a behavior change to a shipped engine with a
6-copy vendored fan-out (`_shared/okf.py` → 5 skill copies via `_shared/sync.py`, gated in the
FAST tier). Each epic therefore lands its own test arm, and the plan's exit criterion is the
FULL tier green over the merged tree — not a hand-run spot check.

## Epics

### Epic 0: SPEC-first amendments (gates every implementation epic)
- Issue 0.1: Amend **`REQ-OKF-012`(a)** so rule D's recursive member walk skips version-control-ignored paths at every level, binding **producer and checker** to one predicate. Lands in **both** `SPEC.md` and `skills/yf-okf/SPEC.md` (the id is dual-homed; `check_amendment_log.py` reads root `SPEC.md` only, so root alone satisfies the gate but leaves the per-skill copy stale).
  - resolves-upstream: #294 (include)
- Issue 0.2: Correct **`REQ-OKF-CHK-004`**'s "untracked" to "ignored", and widen its scope from "the driver" to the engine walk it delegates to. Same dual home as 0.1.
  - depends-on: 0.1
- Issue 0.3: **Amend `REQ-OKFH-010`** (`skills/yf-okf-hygiene/SPEC.md`) to add `restore`'s three refusal conditions and a per-bundle filter — and **record that the shipped code does not conform to the requirement's existing "record-driven with a PER-PATH operation kind" clause**. This is an amendment plus a conformance defect, **not a new id**: the requirement already says what EXP-001 found missing.
- Issue 0.4: **Amend `REQ-OKFH-008`** to state the journal invariant explicitly — the recorded phase is always **>= the physical phase** — and that recovery is operator-invocable. Record the conformance defect: the shipped swap writes `S2` *after* the first rename, so a crash is recovered from a phase the code never reached, violating the existing "never on directory presence" clause. **Restate the normative five-state table under the over-approximation reading** — the recorded phase is an upper bound, so `S1` becomes a recovery-time-only state never written once the ordering is fixed — and amend the §5 row's "naming **each** of `S0`..`S4`" accordingly, so the amended requirement does not contradict its own table and Issues 3.6/3.8 know what "all states" now means. **State the obligation the over-approximation creates: EVERY `recover()` branch must tolerate a physical phase one step BEHIND its recorded phase.** Without that sentence the reader takes over-approximation as a journal property alone, and the `S3`/`S4` branch — which assumes the swap completed — silently becomes a data-loss path (Issue 3.9).
- Issue 0.5: Add **`REQ-OKFH-011`** (`skills/yf-okf-hygiene/SPEC.md`): a `would-backfill` dry-run verdict shall be **predictive of apply** — every halt condition apply evaluates, the dry run evaluates.
- Issue 0.6: Add **`REQ-OKFH-012`**: the opt-in `--reconcile-objective` mode, with `plan.md`'s H1 as the authority for a divergent legacy objective line.
- Issue 0.7: Add **`REQ-OKFH-013`**: the `--record` artifact carries a **schema version**, and `restore` **refuses** an unversioned or legacy record rather than misreading it.
- Issue 0.8: Record the living-amendment-log entries for 0.1-0.7 in root `SPEC.md`; add the `gate-plan064-amendment` and `gate-plan064-reqcoverage` recipe rows and their trigger-scope rows to `CHANGE-VALIDATION.md`; declare this plan's `no-req-required` set: {1.7, 5.1, 5.2, 5.3, 5.4, 5.5}; and assert that `skills/yf-okf/SPEC.md` received the same `REQ-OKF-012` / `REQ-OKF-CHK-004` amendment as root `SPEC.md` — the dual-home staleness the gate itself cannot see.
  - depends-on: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7

### Epic 1: #294 — gitignore-aware member enumeration
- Issue 1.1: Add `_vcs_ignored(bundle)` to `_shared/okf.py` using `git ls-files -o -i --exclude-standard -z`, computed once per bundle, failing open to `frozenset()`. Implements `REQ-OKF-012`(a) as amended.
  - depends-on: 0.2
  - resolves-upstream: #294 (include)
- Issue 1.2: Thread the ignored set through `_listing_members`, `_recursive_file_count` and `_nested_files` so the count arm and the enumerate arm agree.
  - depends-on: 1.1
- Issue 1.3: Add the hardcoded floor (`__pycache__/`, `*.pyc`) covering the deliberate fail-open outside a git work tree. Not in `OKF-EXTENSION.md` §3b, whose own text reserves it for fixture carve-outs.
  - depends-on: 1.2
- Issue 1.4: Run `uv run _shared/sync.py` to regenerate the 5 vendored copies; verify byte-identity.
  - depends-on: 1.3
- Issue 1.5: Add the two-sided `_shared/test_okf.py` arms — `test_vcs_ignored_drops_residue` (ignored residue absent) and `test_vcs_ignored_keeps_untracked` (an untracked-but-not-ignored member still enumerated) — plus `test_vcs_ignored_floor` (the hardcoded floor holds outside a git work tree) and a force-added-`.pyc` arm.
  - depends-on: 1.2
- Issue 1.6: Add arm 4 to `scripts/checks/check-drift-driver-contract.sh` (gitignore arm; the contract check has none today).
  - depends-on: 1.2
- Issue 1.7: Add `.okf-hygiene-staging/` and `.okf-hygiene-journal/` to `.gitignore` — they sit inside the `docs/plans/*` root glob, survive a halt, and are untracked-but-not-ignored. **No new REQ** — a gitignore entry is repository hygiene with no behavioral requirement to amend. Declared `no-req-required` for the same reason.
- Issue 1.8: Add `test_vcs_ignored_noop` measuring the no-op property — capture each live bundle's member set before and after and assert the sets are identical — and record the added FAST-tier cost.
  - depends-on: 1.4

### Epic 2: a record that records, and a restore that refuses
- Issue 2.1: Have `backfill --apply` write the per-path operation list (created / deleted / modified, with content hashes) it already knows at transform time into `--record`, carrying the `REQ-OKFH-013` schema version.
  - depends-on: 0.3, 0.7
- Issue 2.2: Have `restore` consume that operation list instead of re-deriving it via `rglob` + `git ls-files --error-unmatch`, and **refuse an unversioned or legacy record** (`REQ-OKFH-013`).
  - depends-on: 2.1
- Issue 2.3: Add the three refusals (`REQ-OKFH-010` as amended): non-git tree, bundle untracked at HEAD, bundle dirty relative to its post-backfill state (the last overridable with an explicit `--force`).
  - depends-on: 2.2
- Issue 2.4: Add a per-bundle filter to `restore`, so a batch record does not force whole-batch reversal.
  - depends-on: 2.2
- Issue 2.5: Regression arms for all three EXP-001 loss paths, each asserting a **refusal**, not a `pass`: `test_restore_refuses_non_git`, `test_restore_refuses_untracked`, `test_restore_refuses_dirty`, plus `test_restore_refuses_legacy_record`.
  - depends-on: 2.3
- Issue 2.7: Arms for the positive record-driven behavior: `test_restore_record_driven` (the reversal is driven by the recorded op list, not by `rglob` + `git ls-files`) and `test_restore_bundle_filter`.
  - depends-on: 2.4
- Issue 2.8: **Repair or replace `test_restore_round_trip`, and correct `REQ-OKFH-010`'s `SPEC.md` §5 traceability row.** Measured: it passes today (exit 0) against the `restore` EXP-001 proved is **not** record-driven — the same false-green class as Issue 3.6, on the sibling requirement Issue 0.3 records a conformance defect against. Apply 3.6's diagnosis here too: the replacement must assert the reversal is **driven by the recorded op list**, so that a `restore` re-deriving from `rglob` + `git ls-files` fails it. A test that passes under both implementations measures nothing.
  - depends-on: 2.7
- Issue 2.6: Make a mixed run's exit code legible (`test_mixed_run_exit_*`): a run that mutates N bundles and halts on M must not be readable as "nothing happened". Include what the record contains for a partially-halted batch.
  - depends-on: 2.1

### Epic 3: a journal that is sound and reachable
- Issue 3.1: Fix the phase ordering — write `S2` before `os.rename(bundle, stash)` and `S3` before `os.rename(staging, bundle)`, so the recorded phase is always >= the physical phase (`REQ-OKFH-008` as amended).
  - depends-on: 0.4
- Issue 3.2: Add a `recover` CLI verb. `recover()` exists and is unreachable today.
  - depends-on: 0.4
- Issue 3.9: **Make `recover()`'s `S3`/`S4` branch presence-tolerant — Issue 3.1's fix opens a NEW total-loss window without it.** Measured: 3.1 writes `S3` *before* `os.rename(staging, bundle)`, so a crash in that window records `S3` while the physical state is `S2` (bundle absent, staging and stash both present). The branch at `okf_hygiene.py` `if phase in ("S3","S4")` **assumes the swap completed** and unconditionally `rmtree`s both stash and staging, returning `recovered: True, "completed cleanup"` — with the bundle destroyed. **Today's shipped code is SAFE in this window** (it records `S2`, rolls forward, bundle survives), so the plan's own fix would introduce the exact failure EXP-001 refuted the premise with, relocated from `S1` to `S3`. The fix: if the bundle is absent and staging exists, **complete rename 2 before cleanup**.
  - depends-on: 3.1
- Issue 3.3: Wrap **both lines of the `S2` branch** against errno 66 (`Directory not empty`) — the stash-rollback **and** the roll-forward `os.rename(staging, bundle)`. Red-team pass 5 measured the second: a crash after `Journal.write("S2")` but before rename 1 records `S2` while physically at `S1` (bundle still **present**), so the roll-forward renames onto a live directory and raises an **uncaught** errno-66, wedging `recover()` idempotently. No data is lost, but SC11's "no unhandled errno-66" already forbids it. Implement `test_crash_s2_errno66` on the **journal-write** seam — the `os.rename` seam cannot reach this window either, the same blindness diagnosed for `S3`.
  - depends-on: 3.1
- Issue 3.4: Have `backfill` check for a stale journal on entry and refuse rather than proceed.
  - depends-on: 3.2
- Issue 3.5: Crash-injection arms `test_crash_s1_bundle_present` and `test_crash_s2_errno66` at both swap windows, asserting the bundle is **present** after recovery; plus `test_recover_verb_exists` and `test_backfill_refuses_stale_journal`, and `test_crash_s3_recorded_physical_s2` — a **journal-write seam** arm asserting the bundle survives a crash between `Journal.write("S3")` and rename 2. **The `os.rename` seam cannot reach that window by construction**, so an arm hung off it is blind to Issue 3.9's defect; this arm interposes on the journal write instead.
  - depends-on: 3.3, 3.4
- Issue 3.6: **REPLACE `test_crash_recovery_all_states` — repair-in-place is not sufficient — and correct its `SPEC.md` §5 traceability row.** The diagnosis, measured: the test **hand-constructs each journal state** (`shutil.copytree`; `j.write("S1")`; `os.rename`; `j.write("S2")`) and **never invokes `backfill`'s swap**, so it *mocks the call site it exists to observe*. Applying Issue 3.1's phase-ordering change and re-running it yields byte-identical output — it is **insensitive to the production ordering by construction**, which is why it is green against violating code and why patching its assertions would leave the false green intact under a new name. The replacement must drive the **real `backfill` swap** through the deterministic `os.rename` SIGKILL seam EXP-001 used (the same seam 3.5 uses), never synthesized journal records.
  - depends-on: 3.5
- Issue 3.8: Add `scripts/checks/check-crash-test-detects-lag.sh` — a **negative control**: in a sandbox copy, revert Issue 3.1's phase-ordering fix and assert the **swap-driven** crash test **FAILS**; on the fixed tree assert it passes. **Pin the assertion to Issue 3.6's replacement test by its post-3.6 name** (or to `test_crash_s1_bundle_present`, which is swap-driven by construction) — never to the pre-3.6 name, which 3.6 may change and which measurement shows cannot fail. **A control pinned to a test that mocks its call site is not a control.** Precedent: `scripts/checks/check_mock_fidelity.py` exists for exactly this "instrument calibrated against the call site" class. The script takes a `--req` arm so it covers **both** false greens — `REQ-OKFH-008` (default) and `REQ-OKFH-010`. **Both mutations must be reproducible in a sandbox by a flag flip, not a reconstructed revert:** for `008` that is Issue 3.1's phase-ordering change; for `010`, Issue 2.2 keeps its `rglob` + `git ls-files` derivation behind an internal fallback the script can force, so the mutation is one switch rather than an unpicked function. This is what gives SC13a/SC13b an exit code that means something — pinning selectors prevents *inheriting* a false green but never *detects* one.
  - depends-on: 2.8, 3.6
- Issue 3.7: Reconcile `SKILL.md`'s durability claims with what the code delivers; the current text overstates it.
  - depends-on: 3.6

### Epic 4: an honest dry run, and objective reconciliation
- Issue 4.1: Move `phase-log-loss` (and any other apply-only halt) into the dry-run path by staging into a temp copy without the swap (`REQ-OKFH-011`).
  - depends-on: 0.5
- Issue 4.2: Add the opt-in `--reconcile-objective` mode (`REQ-OKFH-012`): `plan.md`'s H1 is authoritative, the legacy `>` line is rewritten, and the rewrite is reported per bundle.
  - depends-on: 0.6
- Issue 4.3: Stamp `description:` (`REQ-DATA-075`) in the transform's frontmatter output; a backfilled bundle currently still fails that convention.
  - depends-on: 0.5
- Issue 4.4: Author the Epic-4 test arms: `test_dry_run_predictive`, `test_reconcile_objective`, `test_stamps_description`. Every `-k` token in the Success Criteria table is named by exactly one issue; this is Epic 4's.
  - depends-on: 4.1, 4.2, 4.3
- Issue 4.5: Re-run the full 8-bundle dry run and record the halt profile after 4.1-4.3 — the measurement the follow-on transform plan starts from. Probe the surfaces EXP-001 did **not** test: the `_index.md` legacy-variant route, whether any target classifies `hybrid-partial` rather than `legacy-readme`, and the record contents of a partially-halted batch.
  - depends-on: 4.4
- Issue 4.6: Investigate why the audit verdict stayed `warn` -> `warn` on all 7 transformed bundles; a transform that does not improve the verdict needs its reason recorded.
  - depends-on: 4.5

### Epic 5: scope closure and honest handoff
- Issue 5.1: Add the two `CHANGE-VALIDATION.md` §3 rows for `skills/yf-research/OKF-EXTENSION.md` and `skills/yf-incubator/OKF-EXTENSION.md` — the honest slice of #316 scope item 4 (EXP-003). **No new REQ** — a trigger-scope row wires an existing recipe to a path and amends no requirement. Declared `no-req-required` for the same reason.
- Issue 5.2: Comment on #247 with the `OKF-EXTENSION.md` §1/§2/§3/§6 rows from EXP-003, plus the uncovered fifth vendored `okf.py` (`skills/yf-okf-hygiene/scripts/okf.py`). **No new REQ** — filing an upstream comment changes no behavior in this repository. Declared `no-req-required` for the same reason.
- Issue 5.3: File the follow-on beads: (a) documentation remediation — 3 stale `Status: DRAFT` banners, 2 dangling symbols (`HEADER_TEMPLATE`, `seed_readme`), 2 shipped-but-"open" decisions — linked to #247; and (b) **`plan_extract.py --strict` validates neither self-edges nor cycles** (red-team pass 4 C34), measured when a self-edge introduced during this plan's own drafting passed `--strict` green and surfaced only as an unrelated coverage failure. **No new REQ** — filing a bead amends no requirement. Declared `no-req-required` for the same reason.
- Issue 5.4: File the follow-on **corpus transform** issue that this plan unblocks, carrying #316's original acceptance criteria, the post-repair halt profile from 4.5, D3's sandbox-rehearsal method, and the `git revert` rollback route D10 records. **No new REQ** — filing an upstream issue amends no requirement. Declared `no-req-required` for the same reason.
  - depends-on: 4.5
- Issue 5.5: Update #316 with the measured refutation and the split, so the deferral is recorded rather than silent. **No new REQ** — an issue comment amends no requirement. Declared `no-req-required` for the same reason.
  - depends-on: 5.4
  - resolves-upstream: #316 (partial)

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: SPEC amendments landed before implementation
- Type: auto
- Condition: every implementation issue reaches a REQ-naming Epic-0 issue, or is in the declared `no-req-required` set.
- Test: uv run scripts/check_amendment_log.py --plan plan-064-james-dixson-a0b7fa
- Blocks: epic:1, epic:2, epic:3, epic:4
- Instructions: Land Epic 0 first. Issue 0.8 adds this plan's `gate-plan064-amendment` recipe and trigger rows to `CHANGE-VALIDATION.md` and declares the `no-req-required` set; the gate is red until it does.

### Capability Gate: requirement coverage
- Type: auto
- Condition: every non-Epic-0 issue has a direct or transitive dependency on an Epic-0 issue that names a `REQ-*` id.
- Test: uv run scripts/checks/check-req-coverage.py --min-issues 30 docs/plans/plan-064-james-dixson-a0b7fa
- Blocks: epic:1, epic:2, epic:3, epic:4
- Instructions: The checker hardcodes `epic == "0"`, which is why the SPEC epic is Epic 0. Add missing `depends-on` edges rather than renumbering. **This gate is a REGRESSION GUARD, already green at pour time** — it blocks nothing on day one and exists to catch a later edit that breaks coverage. Recorded so a green reading is not mistaken for work done.

### Capability Gate: vendored copies in sync
- Type: auto
- Condition: the 5 vendored `okf.py` copies are byte-identical to `_shared/okf.py`.
- Test: uv run _shared/sync.py --check
- Blocks: 1.8, 2.5, 2.7, 3.5, 4.4
- Instructions: Run `uv run _shared/sync.py` after any `_shared/okf.py` edit.

### Capability Gate: no residue in the corpus before the no-op measurement
- Type: auto
- Condition: no build residue exists under any bundle root the drift check declares.
- Test: test -z "$(find docs/plans docs/research Incubator -name '__pycache__' -o -name '*.pyc' 2>/dev/null)"
- Blocks: 1.8
- Instructions: Remove residue before measuring the no-op property, or the measurement is against a contaminated corpus. The `Incubator` root matches the drift check's declared four roots even though none exists today.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | The vendored fan-out means one hand edit lands in 6 files; a partial sync ships an engine that disagrees with itself across skills. | high | The vendored-copies gate (`_shared/sync.py --check`) blocks the measurement issues, and the FAST tier already gates on sync. Issue 1.4 makes the regeneration an explicit step rather than an assumed one. |
| R2 | Fixing `restore` to be record-driven changes the meaning of existing `--record` files; an old record no longer describes what the new `restore` expects. | low | **Owned, not merely noted:** `REQ-OKFH-013` (Issue 0.7) mandates a schema version, Issues 2.1/2.2 implement writing and refusing it, and SC8 asserts the refusal. Downgraded from `med` on red-team C10's measurement: `git ls-files` shows **no committed record artifacts**, and the record is a transient batch file, so the blast radius is a single in-flight run. |
| R3 | `_vcs_ignored` forks `git` once per bundle, adding ~18 ms/bundle to a check that runs in the FAST tier on every edit. | low | Measured at ~1.25 s over 68 bundles. Issue 1.8 records the actual cost; if it becomes material the driver can compute one corpus-wide set, at the price of changing `_listing_members`' signature for 5 consumers. |
| R4 | The fail-open behavior outside a git work tree means a bundle copied elsewhere still enumerates residue — the very case OKF portability exists to support. | med | Issue 1.3's hardcoded floor covers the common residue classes. The fail-open is deliberate: failing *closed* would make a copied bundle enumerate nothing, which is a worse failure than enumerating too much. |
| R5 | Crash-injection tests are timing-dependent and may be flaky in CI. | med | EXP-001 drove both windows deterministically by injecting `SIGKILL` inside `os.rename`; Issue 3.5 reuses that seam rather than racing a real crash. |
| R6 | The deferred transform is forgotten, and #316 sits half-done with no record of why. | med | Issues 5.4 and 5.5 are deliverables, not courtesies: the follow-on issue carries #316's original acceptance criteria and the post-repair halt profile, and #316 itself is updated with the refutation. EXP-003's lesson applies — a scope item that merely disappears is indistinguishable from one that was forgotten. |
| R7 | Repairing an engine while three open P0/P1s (#318, #320, #321) sit in its `--skill` / member-resolution path risks colliding with a fix in flight. | med | This plan touches the member *walk* and the restore/journal paths, not `--skill` resolution. Issue 5.2's #247 comment and the follow-on beads keep the boundary explicit; if a #318/#320/#321 fix lands mid-execution, re-run the Epic 1 no-op measurement (1.8) before proceeding. |
| R8 | The follow-on transform discovers a **fourth** blocker EXP-001 did not test, and the deferral buys nothing. | med | Named rather than hoped away. Issue 4.5 probes the three known-untested surfaces — the `_index.md` legacy-variant route, whether any target classifies `hybrid-partial` rather than `legacy-readme`, and the record contents of a partially-halted batch — *before* the follow-on inherits the work, and carries the result into Issue 5.4's issue body. |
| R9 | A test that passes against non-conforming code hides the defect it was written to catch. **Two live instances, both on requirements this plan amends:** `test_crash_recovery_all_states` for `REQ-OKFH-008` and `test_restore_round_trip` for `REQ-OKFH-010` — measured, both exit 0 today. | high | Three layers. Issues 3.6 and 2.8 repair both tests **and** correct both `SPEC.md` §5 rows. SC11/SC9's selectors are pinned to *new* names so no criterion inherits a false green. And Issue 3.8 adds a **negative control** — pinning prevents inheriting a false green but never *detects* one, so SC13a/SC13b are now mutation checks with real exit codes. This is the plan's own instance of the vacuous-check misread D4 names. |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | Every implementation issue reaches a REQ-naming Epic-0 issue or is in the declared `no-req-required` set, and the amendments are recorded in the living amendment log. | `uv run scripts/check_amendment_log.py --plan plan-064-james-dixson-a0b7fa` -> exit 0 | 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8 |
| SC2 | Every non-Epic-0 issue is covered by the repo's requirement-coverage checker. | `uv run scripts/checks/check-req-coverage.py --min-issues 30 docs/plans/plan-064-james-dixson-a0b7fa` -> exit 0 | 0.8 |
| SC3 | The member walk skips version-control-ignored paths at every level, in both the count arm and the enumerate arm — while an untracked-but-not-ignored member is still enumerated. | `uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q -k vcs_ignored` -> exit 0 | 1.1, 1.2, 1.5 |
| SC4 | The #294 fix is a no-op on the clean corpus: every live bundle's member set is identical before and after, and the residue floor holds outside a git work tree. | `uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q -k "vcs_ignored_noop or vcs_ignored_floor"` -> exit 0 | 1.3, 1.5, 1.8 |
| SC5 | The corpus carries no root-index drift after the change. **Green before the work** — a regression guard, not evidence of work done. | `uv run scripts/checks/check_okf_index_drift.py --min-roots 30` -> exit 0 | 1.8 |
| SC6 | The 5 vendored `okf.py` copies are byte-identical to `_shared/okf.py`. **Green before the work** — a maintenance invariant the fan-out must not break. | `uv run _shared/sync.py --check` -> exit 0 | 1.4 |
| SC7 | The driver's contract check has a **fourth** arm covering gitignore, and the hygiene scaffolding is genuinely ignored. | `bash scripts/checks/check-drift-driver-contract.sh && grep -q 'arm 4' scripts/checks/check-drift-driver-contract.sh && git check-ignore -q docs/plans/.okf-hygiene-staging` -> exit 0 | 1.6, 1.7 |
| SC8 | `restore` consumes a versioned per-path operation list written by `backfill`, refuses an unversioned or legacy record, and accepts a per-bundle filter. | `uv run --with pytest --with pyyaml python3 -m pytest skills/yf-okf-hygiene/scripts/test_okf_hygiene.py -q -k "restore_record_driven or restore_refuses_legacy_record or restore_bundle_filter"` -> exit 0 | 2.1, 2.2, 2.4, 2.5, 2.7 |
| SC9 | All three EXP-001 data-loss paths refuse instead of deleting: non-git tree, untracked bundle, post-backfill edits. | `uv run --with pytest --with pyyaml python3 -m pytest skills/yf-okf-hygiene/scripts/test_okf_hygiene.py -q -k "restore_refuses_non_git or restore_refuses_untracked or restore_refuses_dirty"` -> exit 0 | 2.3, 2.5 |
| SC10 | A run that mutates N bundles and halts on M is not readable as "nothing happened", and its record says which. | `uv run --with pytest --with pyyaml python3 -m pytest skills/yf-okf-hygiene/scripts/test_okf_hygiene.py -q -k mixed_run_exit` -> exit 0 | 2.6 |
| SC11 | A crash at **any** journalled window — either rename seam **and** the `S3`-recorded/`S2`-physical window Issue 3.1 opens — leaves the bundle present after `recover`, with no unhandled errno-66. | `uv run --with pytest --with pyyaml python3 -m pytest skills/yf-okf-hygiene/scripts/test_okf_hygiene.py -q -k "crash_s1_bundle_present or crash_s2_errno66 or crash_s3_recorded_physical_s2"` -> exit 0 | 3.1, 3.3, 3.5, 3.9 |
| SC12 | Recovery is operator-invocable, and `backfill` refuses on a stale journal. | `uv run --with pytest --with pyyaml python3 -m pytest skills/yf-okf-hygiene/scripts/test_okf_hygiene.py -q -k "recover_verb_exists or backfill_refuses_stale_journal"` -> exit 0 | 3.2, 3.4, 3.5 |
| SC13a | The crash test **detects** the phase-lag defect: it FAILS on a tree with Issue 3.1's fix reverted and passes on the fixed tree, and `REQ-OKFH-008`'s §5 row names it. | `bash scripts/checks/check-crash-test-detects-lag.sh` -> exit 0 | 3.6, 3.8 |
| SC13b | The `restore` round-trip test detects non-record-drivenness: it FAILS against a `restore` that re-derives from the filesystem, and `REQ-OKFH-010`'s §5 row names it. | `bash scripts/checks/check-crash-test-detects-lag.sh --req REQ-OKFH-010` -> exit 0 | 2.8, 3.8 |
| SC14 | `SKILL.md`'s durability claims match what the code delivers. | manual: a prose-vs-code agreement judgement across `SKILL.md` and the journal implementation; no exit code decides it. | 3.7 |
| SC15 | A `would-backfill` dry-run verdict is predictive — every halt condition apply evaluates, the dry run evaluates. | `uv run --with pytest --with pyyaml python3 -m pytest skills/yf-okf-hygiene/scripts/test_okf_hygiene.py -q -k dry_run_predictive` -> exit 0 | 4.1, 4.4 |
| SC16 | `--reconcile-objective` clears the divergence halt with `plan.md`'s H1 as the authority, and the transform stamps `description:`. | `uv run --with pytest --with pyyaml python3 -m pytest skills/yf-okf-hygiene/scripts/test_okf_hygiene.py -q -k "reconcile_objective or stamps_description"` -> exit 0 | 4.2, 4.3, 4.4 |
| SC17 | The post-repair halt profile over all 8 bundles is measured and recorded — including the three surfaces EXP-001 did not test — and the `warn` -> `warn` verdict is explained. | manual: the recorded dry-run output, the untested-surface probes, and the verdict explanation are prose artifacts carried into the follow-on issue. | 4.5, 4.6 |
| SC18 | The `yf-research` and `yf-incubator` `OKF-EXTENSION.md` files carry `CHANGE-VALIDATION.md` trigger rows. | `grep -q 'skills/yf-research/OKF-EXTENSION.md' CHANGE-VALIDATION.md && grep -q 'skills/yf-incubator/OKF-EXTENSION.md' CHANGE-VALIDATION.md` -> exit 0 | 5.1 |
| SC19 | The deferred transform and the routed drift-node work are recorded as issues, not as silence. | manual: #247 carries the node rows and the fifth-copy gap; the follow-on transform issue, the remediation bead, and the #316 update all exist and are linked. | 5.2, 5.3, 5.4, 5.5 |
| SC20 | The FULL validation tier is green over the merged tree. | `uv run "$(yf skill-dir yf-change-validation)/scripts/change_validation.py" run --tier full` -> exit 0 | (landing) |
