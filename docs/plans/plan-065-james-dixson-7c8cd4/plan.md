---
type: Plan
okf_spec: OKF-PLAN
description: Run the yf-okf-hygiene corpus backfill on the repaired engine - 8 legacy-readme
  bundles to the reserved index.md + log.md model
id: plan-065-james-dixson-7c8cd4
author: james-dixson
created: '2026-09-05'
status: reconciling
deliverable_class: standard
fingerprint: e457c90986407e17bee7c3473494ca381e7b20874ce35e5b00279dcfc94dda67
epic: yf-mol-e7k4
---
# Plan: Run the yf-okf-hygiene corpus backfill on the repaired engine — 8 legacy-readme bundles to the reserved index.md + log.md model

**ID:** plan-065-james-dixson-7c8cd4
**Author:** james-dixson
**Created:** 2026-09-05
**Status:** reconciling
**Deliverable-class:** standard
**Epic:** yf-mol-e7k4
**Fingerprint:** e457c90986407e17bee7c3473494ca381e7b20874ce35e5b00279dcfc94dda67

## Objective
Run the yf-okf-hygiene corpus backfill on the repaired engine — 8 legacy-readme bundles to the reserved index.md + log.md model

## Motivation

Fifty-two of the repository's sixty-nine artifact bundles already carry the OKF-reserved
`index.md` + `log.md` model. Eight do not: they still carry a legacy `README.md`, and they have
resisted three separate attempts to migrate them.

plan-057 tried and halted on all eight (recorded as its unresolved SC19, filed as #295).
plan-064 discovered why the retry was unsafe: EXP-001 measured that `backfill` halted **8/8**,
and that the advertised rollback — `restore --apply` — **destroyed data on three paths while
reporting `pass` and exiting 0**. plan-064 therefore repaired the instrument and deliberately
deferred the corpus transform to #359.

The engine is now repaired and deployed. Measured on this repository at drafting time:

| Run | checked | would-backfill | halted |
| :-- | --: | --: | --: |
| default | 70 | 0 | 8 |
| `--reconcile-objective` | 70 | 7 | 1 |

*(Measured 2026-09-05. `checked` was 69 before this plan's own bundle existed and 70 after; the
count is pinned here to 70 because every later assertion in this plan is stated against that
number. Unpinned corpus figures are the defect class this plan's own #322 disposition names.)*

This plan spends that repair. It is the last of the three attempts to leave the corpus
inconsistent, and the first with a rollback that has been measured rather than assumed.

**Who is affected.** Every reader of a plan bundle — human or agent. A legacy bundle has no
reserved `index.md`, so the OKF orientation contract does not hold for it, and corpus-level
tooling must special-case eight bundles indefinitely.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #359 | Plan 2/3 (part 2): run the corpus backfill on the repaired engine | include | The primary issue. Carries #316's acceptance criteria verbatim. | 4.4, 6.2 |
| #316 | Plan 2/3: run the corpus backfill — 8 legacy-readme bundles | include | Parent. #359 carries its criteria; both close together. | 6.2 |
| #295 | plan-057 follow-on: 8 unresolved backfill halts (SC19) and 4 ungranted reconcile comments (SC24) | partial | **SC19 only** — the same 8 bundles. SC24 (ungranted reconcile comments) is out of scope and #295 stays open for it. | 6.2 |
| #362 | the `_index.md` legacy-variant transform route manufactures a hybrid | exclude | Blocks nothing here: 0 of the 8 targets are `_index.md` (plan-064 EXP-004). | — |
| #361 | `plan_extract.py --strict` validates neither self-edges nor cycles | exclude | plan-064 follow-on, unrelated axis. | — |
| #322 | docs: the "31 legacy, 7 halt" figure reads as repo-agnostic | exclude | Docs defect in `SKILL.md`; this plan changes no docs figure. | — |

**A defect found during this plan's scoping is deliberately NOT listed above**: `_tracked_at_head`
(`okf_hygiene.py:1185`) queries `HEAD:{rel}` while the record stores **absolute** paths under
`--root`, so `restore` refuses 100% of the time in that mode. It is **fail-safe** — it refuses
rather than destroys — and per decision **D3** it is filed as its own issue and fixed separately.
It has no upstream number yet because filing is an outward-facing write awaiting operator
authorization.

## Investigation Findings

Two experiments ran. **One refuted a premise this plan was scoped on.**

**measured:** baseline on this repository at drafting time — `audit` reports `legacy: 8` of 70
bundles checked; `check_okf_index_drift.py --min-roots 30` exits 1 with `no_index: 8`;
`test_okf_hygiene.py` passes 35/35. **measured:** the default `backfill` dry run halts 8/8;
with `--reconcile-objective` it clears 7 and halts 1.

### exp-001 — objective-divergence classification ([findings](findings/exp-001-objective-divergence-classification.md))

Adopting `plan.md`'s H1 is **correct for 5 of the 7** divergent bundles and **lossy for 2**
(plan-010, plan-013). Derived independently, the same pair #295's decision D-5 recorded.

**No mechanical rule separates the groups.** plan-014 and plan-021 have *longer* READMEs
describing scope that was explicitly **deferred**; plan-010 and plan-013 have longer READMEs
carrying real delivery facts. Length, issue-number count and superset tests all get one pair
wrong. Stale-scope READMEs are the **common** case here (3 of 7).

A blanket prefer-README rule would be **strictly worse** than the engine default.

### exp-002 — plan-030's `phase-log-loss` ([findings](findings/exp-002-plan-030-phase-log-loss.md))

**The halt is a detector artifact. Nothing is lost.** `okf.py:1292` skips the entire log
reconciliation when a `log.md` already exists, so for plan-030 the transform never moves the phase
log **and never strips it** — while the guard compares `plan.md`'s dates against a staged `log.md`
the transform did not write. It reports a loss that cannot occur.

plan-030 is the **only** one of the eight carrying a pre-existing `log.md` (written by
`plan_manager`'s close-time `append_log` into an otherwise-legacy bundle).

**This corrects the scoping premise.** The halt was characterised at scoping time as a real
data-loss refusal. It is not. It is still **not forceable** — the repair is to fix the bundle, not
to override the guard — but the repair is a content edit, and the correct one is the **move
migrate skipped**: merge the history into `log.md` *and* delete `plan.md`'s `**Phase log:**`
block, reaching the end state the other seven reach mechanically (measured on a plan-013 control:
`plan.md` blocks 1 -> 0, `log.md` 11 entries).

### Decisions

| # | Decision | Basis |
| :-- | :-- | :-- |
| D1 | Pre-merge the richer objective into `plan.md`'s H1 for plan-010 and plan-013 **only**, then run `--reconcile-objective`. The other five adopt plan.md unchanged. | exp-001; operator |
| D2 | Repair plan-030 by performing migrate's skipped move by hand, then backfill all 8. Target `legacy: 0`. | exp-002; operator |
| D3 | The `restore --root` absolute-path defect is **out of scope** — filed, fixed separately. All rehearsals `cd` into the sandbox and pass no `--root`. | operator |
| D4 | The two engine defects exp-002 exposed (one-sided guard, skip-if-exists reconciliation) are **filed, not fixed here**. This plan changes no engine code. | exp-002 |
| D5 | Rollback is **`git revert`**, not `restore` — for a committed corpus that is the simpler and stronger reversal (plan-064 D10). `--record` is still written, and `restore` is still exercised once to discharge #359's criterion. **The revert boundary does not exist until Issue 4.5 commits the backfill**, which runs AFTER 4.4's restore round-trip. In the window between the apply (4.2) and that commit the rollback verb is `git checkout -- docs/plans && git clean -fd docs/plans`, which is stated here because the plan previously named no rollback at all for a partial-apply failure. | plan-064 D10 |
| D6 | Verify with **per-bundle finding counts**, never the `audit` verdict — the verdict is a saturating label that reads `warn` for one residual finding or fifty. **The command is `uv run skills/yf-okf/scripts/okf.py check <bundle> --json`, reading `len(findings)`** — measured, `okf_hygiene.py audit --json` rows carry `{bundle, class, detail}` and NO finding count, so D6 was previously unsourced. The before-counts are destroyed by the transform and are captured in Issue 0.3. | #359 |

## Approach

Repair the two content obstacles, rehearse the whole transform on a committed sandbox, then apply
it once to the real corpus behind an operator gate, and verify against counts rather than verdicts.

**This plan changes no engine code.** Every defect it finds is filed. That is deliberate: plan-064
repaired the instrument, and mixing a fresh engine change into the run that spends it would make a
failure ambiguous between the transform and the change.

**Ordering is load-bearing.** The content repairs (Epics 1-2) are committed *before* the corpus
apply (Epic 4), and the apply is itself committed by Issue 4.5 — AFTER 4.4's restore round-trip, never before — so the backfill lands as a single
revertable commit with a clean boundary — which is what makes D5's `git revert` rollback precise.

**What the transform DELETES is boilerplate.** **measured:** all 8 target `README.md` files are the
identical 38-line template (`## File map` at line 9, `## Reading order` at line 28). Beyond the
`>` objective line — the one thing Epic 1 exists to preserve — there is **nothing bundle-specific
to lose**. This materially shrinks R1 and R3, and is stated here rather than left for a reader to
rediscover.

**`restore --apply` MUST NOT run after the backfill is committed. MEASURED, this session.** A
sandbox spike of the exact sequence — commit base, `backfill --apply --record`, **commit**,
`restore --record --bundle <one> --apply` — returns `verdict: pass`, `exit: 0` and leaves the
bundle with **no `README.md`, no `index.md`, no `log.md`**. Mechanism: committing the backfill
removes `README.md` from `HEAD`, so the `created` unlink pass (`okf_hygiene.py:1367`) deletes
`index.md`/`log.md` while the `git checkout` that should restore `README.md`
(`okf_hygiene.py:1371-1372`) fails with its **return code never checked**. The control — the same
sequence without the commit — restores correctly.

This is a **fourth** silent data-loss path in `restore`, distinct from the three plan-064 repaired,
and it was reachable only because a pass-1 remediation added the commit step. The plan's response
is ordering, not an engine change (SC12): **Issue 4.4 runs on the uncommitted tree; Issue 4.5
commits afterwards.** Post-commit, the reversal verb is `git revert` (D5) — never `restore`.

**Epics 1-2 mutate three completed plans BEFORE any capability gate fires, and that is by design.**
Only the Start Gate authorizes rewriting plan-010's and plan-013's H1 and deleting plan-030's
phase-log block. Those edits are small, reviewed line-by-line against exp-001/exp-002, and
reversed by an ordinary `git revert`; gating them behind the corpus-apply authorization would
block the very rehearsal that earns that authorization. The corpus `--apply` — the irreversible,
70-bundle step — is what the capability gate protects.

## Epics

### Epic 0: Author the verification instrument (before anything is measured)
- Issue 0.1: Author **ONE** script, `scripts/checks/plan065_checks.py`, with ten subcommands. Each exits 0 on PASS, non-zero on FALSE, and 2 when it could not run. **One script, not ten**: the missing-input contract, `--input` override and JSON envelope are then implemented once instead of ten times. Subcommands and their assertions:
  - `audit-strict` — `legacy == 0` AND `unclassifiable == 0` AND `hybrid-partial == 0` AND `bundles_checked >= 70`. **`legacy` alone is blind to the measured failure mode**: it sums only `legacy-readme + legacy-underscore-index + hybrid-partial` (`okf_hygiene.py:977-978`), so a bundle wrecked into `unclassifiable` yields `legacy: 0`, `verdict: pass`, exit 0. The count floor closes R9's enumerate-nothing vacuity
  - `bundle-shape` — all 8 targets carry `index.md` + `log.md` and no `README.md`; fails if the target list is empty
  - `phaselog-bullets` — every bullet of plan-030's original phase log appears in `log.md`, compared as BULLET TEXT not dates. **Its input VANISHES** (Issue 2.2 deletes it), so it embeds the ten bullets literally or reads `git show <base>:...`, and asserts `len(expected) == 10`. Do not extract with `(?s)` — measured, that matches 38 lines, not 10
  - `merged-objectives` — plan-010's and plan-013's `index.md` `>` lines match exp-001's merged text verbatim
  - `no-engine-edits` — the diff from the pinned base touches no `skills/**/*.py` and no `_shared/*.py`
  - `index-drift-strict` — wraps `check_okf_index_drift.py` and additionally asserts `no_index == 0`. **`no_index` contributes nothing to the bare check's verdict** — measured at drafting it reported `no_index: 8` and still exited 0
  - `apply-result` — `transformed == 8`, `halted == 0`, `bundles_checked >= 70`, and exactly **8 rows with `action == backfilled`**. Not "8 bundle rows": the run JSON carries one row per bundle CHECKED; only the record carries 8
  - `restore-roundtrip` — `post_backfill == post_reapply` AND `post_reversal == pre_backfill` AND `post_reversal != post_backfill`. **The last conjunct is load-bearing**: an earlier draft asserted pre- and post-reversal were EQUAL, which is what a **no-op** restore produces — it would have reported green on the exact silent failure exp-003 measured
  - `finding-counts` — every bundle's after-count is <= its before-count, with at least one strict decrease
  - `negative-controls` — `findings/negative-controls.json` has ten rows all with `exit != 0`, and a recorded FALSE for every tree-property subcommand
- Issue 0.2: Pin the diff base — record `git merge-base origin/main HEAD` to `findings/diff-base.txt`. **A checker diffing an unpinned base is vacuously green at Epic 0** because the diff is empty
- Issue 0.3: Capture the PRE-TRANSFORM per-bundle finding counts to `findings/finding-counts-before.json` using `uv run skills/yf-okf/scripts/okf.py check <bundle> --json` and `len(findings)`. **This datum is destroyed by the transform**; measured today, plan-010 reports 12
  - depends-on: 0.1
- Issue 0.4: Prove all ten subcommands with NEGATIVE CONTROLS — mutate the condition each claims to detect, confirm non-zero, and write `findings/negative-controls.json` (`{subcommand, mutation, exit}`) plus a prose companion. **`negative-controls`' own control runs against a synthesized `--input` fixture**, since its real input is the file this issue writes. **No mutation of the live repository occurs**: the four tree-property subcommands need no mutation at all (the pre-transform tree already reports FALSE — that is Issue 0.5), and the six artifact-readers are driven entirely by synthesized `--input` fixtures. A literal reading of "mutate the condition" for `no-engine-edits` would mean editing a `skills/**/*.py`, which would breach SC12
  - depends-on: 0.1
- Issue 0.5: Run every **tree-property** subcommand against the CURRENT pre-transform tree and record that it reports the condition FALSE. **Scope is deliberate — only `audit-strict`, `bundle-shape`, `phaselog-bullets`, `index-drift-strict`.** The other six read artifacts this plan creates, so pre-transform they can only report "input absent", and **an absent input is not evidence the condition is false** — the same distinction the plan draws for `FileNotFoundError`. This issue must REJECT `reason == "input absent"` as a FALSE report
  - depends-on: 0.4

### Epic 1: Pre-merge the two lossy objectives
- Issue 1.0: (ordering) The pre-transform captures in Issues 0.3 and 0.5 MUST complete before ANY bundle is mutated. **Prose is not an edge** — declared here because SC7's and SC8's conditions become true at Epic 2 and Epic 1 respectively, not at Epic 4, so the pre-transform tree is destroyed earlier than a reader might assume
  - depends-on: 0.3, 0.5
- Issue 1.1: Replace plan-010's `plan.md` H1 with the merged objective from exp-001, importing the three live delivery facts (install/upgrade lifecycle, Homebrew distribution, replacing `install.{sh,py}`) and NOT the rejected `yflow` name. **The H1 must remain ONE PHYSICAL LINE** — `_objective()` (`okf_hygiene.py:565`) matches with `.` excluding newline, so a soft-wrapped H1 is silently truncated. Also read plan-010's `## Objective` and confirm the imported facts are already stated there, so this is a summary-fidelity fix and not an invention
  - depends-on: 1.0
- Issue 1.2: Replace plan-013's `plan.md` H1 with the merged objective from exp-001, restoring the policy's second half and the two-skill delivery decomposition. **One physical line**, same reason as 1.1
  - depends-on: 1.1
- Issue 1.3: Confirm no external consumer breaks — the H1 sits above the first `## `, so it is fingerprint-excluded; verify plan-010 and plan-013 carry no `**Fingerprint:**` field and that the edit is additive
  - depends-on: 1.2
- Issue 1.4: Dry run and verify the five non-merged bundles still reconcile to plan.md unchanged, and the two merged bundles reconcile to the merged text. Compare `reconciled_objectives[].to` BYTE-FOR-BYTE against the intended string — this is the explicit truncation check for 1.1/1.2's one-line constraint
  - depends-on: 1.3

### Epic 2: Repair plan-030 (the move migrate skipped)
- Issue 2.1: Merge plan-030's ten `plan.md` phase-log bullets into `log.md`, newest-first, grouped under `## YYYY-MM-DD`, date prefixes stripped, preserving the existing `complete:` entry
  - depends-on: 1.0
- Issue 2.2: Delete the `**Phase log:**` block from plan-030's `plan.md`, reaching parity with the seven bundles the transform migrates mechanically
  - depends-on: 2.1
- Issue 2.3: Verify at BULLET level via `plan065_checks.py phaselog-bullets` that every one of the ten bullets survives — the engine's own guard compares dates only and would not catch a lost bullet under a surviving date
  - depends-on: 2.2, 0.4
- Issue 2.4: Verify plan-030's stored `**Fingerprint:**` is unperturbed by the repair (the phase log is fingerprint-excluded); measure, do not assume
  - depends-on: 2.2
- Issue 2.5: Dry run and confirm plan-030 moves from `halt: phase-log-loss` to `would-backfill`
  - depends-on: 2.3, 2.4

### Epic 3: Full-corpus rehearsal on a committed sandbox
- Issue 3.1: Build a sandbox holding all 8 repaired bundles, `git init` + `git add -A` + commit, so the `restore` guards have a real HEAD. **Scope limit, stated rather than implied**: the sandbox holds only the 8, so it never exercises the classify-and-skip path across the 62 conformant bundles the real apply walks. **`mixed_run` does NOT cover that gap** — it is `bool(mutated) and bool(halted)` (`okf_hygiene.py:1115-1126`), redundant with `halted == 0` and carrying zero information about the 62. Issue 4.3b covers it
  - depends-on: 1.4, 2.5
- Issue 3.2: Run `backfill --reconcile-objective --apply --record` from INSIDE the sandbox with no `--root` (D3), and verify 8 transformed / 0 halted
  - depends-on: 3.1
- Issue 3.3: Run `restore --record --apply` on the UNCOMMITTED tree and verify a byte-identical round-trip. **This is deliberately the same sequence Epic 4 runs** (`4.2 -> 4.4`), which is what makes the rehearsal predictive
  - depends-on: 3.2
- Issue 3.4: Write `findings/rehearsal-result.json`. **The gate's Test hard-codes these four keys and types, and a misspelling raises `KeyError` -> non-zero, INDISTINGUISHABLE from a failed rehearsal**: `legacy_before` (int), `transformed` (int), `halted` (int), `roundtrip_identical` (bool). The Test path is relative to the repository checkout root
  - depends-on: 3.3
- Issue 3.5: Confirm the rehearsal is NON-VACUOUS — assert the sandbox contained 8 legacy bundles before the run, so a rehearsal over an empty or already-conformant set cannot report green
  - depends-on: 3.4

### Epic 4: Apply to the real corpus
- Issue 4.1: Commit the Epic 1-2 content repairs on their own, establishing the clean revert boundary D5 depends on
  - depends-on: 3.5
- Issue 4.2: Run `backfill --reconcile-objective --apply --record findings/backfill-record.json` from the repo root with no `--root`
  - depends-on: 4.1
- Issue 4.3: Verify all 8 are reported explicitly — 8 transformed, 0 halted, 0 silently skipped; write the run JSON to `findings/apply-result.json`
  - depends-on: 4.2
- Issue 4.3b: Prove the 62 conformant bundles were UNTOUCHED — assert `bundles_checked >= 70`, every non-target row reports a skip action, and `git status --porcelain` names nothing OUTSIDE an explicit allowlist: the 8 target bundles, `findings/backfill-record.json`, `docs/plans/plan-065-james-dixson-7c8cd4/**`, `scripts/checks/plan065_checks.py`, and `CHANGE-VALIDATION.md`. **The allowlist is not slack** — without it the assertion is false by construction, because this plan's own uncommitted deliverables are in the tree at this moment, and a spurious failure mid-apply would tempt an executor to waive the ONLY check covering the 62 non-target bundles
  - depends-on: 4.3
- Issue 4.4: Exercise `restore` on ONE real bundle, then re-apply — discharging #359's "restore exercised on a real bundle" criterion against the real corpus. **Run on the UNCOMMITTED post-apply tree, before Issue 4.5** (see the hazard note). Reverse with `restore --record findings/backfill-record.json --bundle docs/plans/plan-030-james-dixson-65526e --apply`; **the `--bundle` value is the record's RELATIVE path — an absolute path is refused**. Re-apply with `backfill --reconcile-objective --apply --record findings/reapply-record.json`. **`--reconcile-objective` mirrors 4.2 so the re-apply is the SAME operation** — that symmetry is the reason, not necessity. **measured:** plan-030's `README.md` `>` line and `plan.md` H1 are byte-identical, so it is the one non-divergent target and a bare re-apply of it also succeeds. An earlier draft claimed the flag's omission was "measured to HALT (`mutated 0, halted 1, exit 1`)"; that signature belongs to an **un-repaired** plan-030 halting on `phase-log-loss`, and was propagated from a pre-Epic-2 tree to a post-Epic-2 step. Recorded rather than deleted: it is the same wrong-tree-state error this plan is about. The re-apply MUST use a SECOND record path: `backfill` has no per-bundle selector, so overwriting 4.2's record would leave the other 7 with no record-driven reversal. Record `pre_backfill`, `post_backfill`, `post_reversal`, `post_reapply` to `findings/restore-roundtrip.json`. Pass NO `--root`. **If the restore fails here**, the tree is still uncommitted, so the rollback verb is D5's pre-commit route (`git checkout -- docs/plans && git clean -fd docs/plans`) — not `git revert`, which has no boundary to revert to until 4.5
  - depends-on: 4.3, 4.3b
  - resolves-upstream: #359 (include)
- Issue 4.5: Commit the backfill result as ONE commit touching **only the 8 bundles** — not the records, which 5.4b carries — because the tightest possible diff is the cleanest `git revert` boundary D5 wants (untouched-elsewhere verified by 4.3b). **D5's revert boundary does not exist until this runs**, and it runs AFTER 4.4 because `restore` is unsafe on a committed backfill
  - depends-on: 4.4, 4.3b

### Epic 5: Verify the acceptance criteria
- Issue 5.1: `plan065_checks.py audit-strict` passes — `legacy: 0` and no bundle became `unclassifiable`
  - depends-on: 4.5
- Issue 5.2: Run `plan065_checks.py finding-counts`, comparing against `findings/finding-counts-before.json`, and report the delta per bundle — per D6 the saturating `warn` verdict is not evidence
  - depends-on: 5.1, 0.3
- Issue 5.2b: Reindex this plan's OWN bundle, **then author a real one-line description for every `.json` artifact and assert no bare bullet remains**. `reindex` gives frontmatter-less `.json` files BARE bullets, and `check_okf_index_drift.py:231` says verbatim that this "degrades the artifact while passing the check — it is not the operator remediation"
  - depends-on: 5.1
- Issue 5.3: `plan065_checks.py index-drift-strict` passes over the whole corpus, including this plan's own bundle
  - depends-on: 5.2b
- Issue 5.4: Run `bundle-shape` and `merged-objectives`. Assert for ALL EIGHT that any stored `**Fingerprint:**` is byte-identical to its pre-transform value — Issues 1.3/2.4 cover only three
  - depends-on: 5.1, 0.4
- Issue 5.4c: Register `plan065_checks.py` in `CHANGE-VALIDATION.md` — recipe rows for at least `audit-strict` and `bundle-shape` **in the FULL tier**. **It runs HERE, not in Epic 0, and the placement is load-bearing**: `§3 Trigger Scope` maps globs to the **FAST** tier, so a `docs/plans/plan-065-*/**` row registered at Epic 0 would turn the FAST tier RED for every edit from Epic 0 through Epic 4 — the two subcommands only go green after 4.5. (The manifest has sections 0-3; there is no §4.) Without registration the checkers are hand-run-only and become permanent unexercised residue, unlike plan-060/062/063/064
  - depends-on: 4.5, 0.1
- Issue 5.4b: Commit this plan's OWN deliverables — `plan065_checks.py`, the `CHANGE-VALIDATION.md` registration, every `findings/*` artifact, the reviews, and 4.4's re-apply residue. **Issues 4.1 and 4.5 are both explicitly scoped to exclude them**
  - depends-on: 5.4, 5.4c
- Issue 5.5: Run the FULL change-validation tier over the merged tree (base: the commit 5.4b creates), and run `no-engine-edits` against the base pinned in Issue 0.2
  - depends-on: 5.2, 5.3, 5.4b, 0.4, 0.2
- Issue 5.6: Draft the four upstream issue bodies and the exact close set to `findings/upstream-drafts.md`, so the Epic 6 gate has evidence to authorize against
  - depends-on: 5.5

### Epic 6: Scope closure
- Issue 6.1: File the SIX engine defects upstream (**AMENDED from FOUR during execution — ESC-001**): `restore --root` absolute-path (D3); the one-sided phase-log guard including the dead `src_bul`/`dst_bul`; migrate's skip-if-exists log reconciliation (D4); **`restore`'s unchecked `git checkout` return code (`okf_hygiene.py:1371-1372`), which makes the post-commit total-loss path SILENT** — measured this session, reproduction in `findings/exp-003-post-commit-restore-loss.md`; **`backfill --apply`'s non-conformant generated `index.md`** (no member listing, so every transformed bundle immediately fails `check_okf_index_drift.py` — measured on all 8); and **`reindex`'s dry run reporting `verdict: clean` while proposing 9 changes**
  - depends-on: 5.6
- Issue 6.2: Reconcile the upstream dispositions — close #359 and #316, and update #295 for the SC19 half only, leaving it open for SC24
  - depends-on: 6.1
  - resolves-upstream: #359 (include), #316 (include), #295 (partial)

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Sandbox rehearsal green
- Type: auto
- Condition: the 8-bundle sandbox rehearsal transformed 8, halted 0, and round-tripped byte-identically
- Test: uv run python3 -c "import json,sys;d=json.load(open('docs/plans/plan-065-james-dixson-7c8cd4/findings/rehearsal-result.json'));sys.exit(0 if d['legacy_before']==8 and d['transformed']==8 and d['halted']==0 and d['roundtrip_identical'] else 1)"
- Blocks: epic:4
- Instructions: Complete Epic 3. The gate reads the rehearsal artifact; it cannot be satisfied by assertion.

### Capability Gate: Corpus apply authorization
- Type: human
- Condition: the operator authorizes `backfill --apply` against the real corpus, a destructive local operation over 8 tracked bundles
- Blocks: epic:4
- Instructions: Present the rehearsal evidence and the `git revert` rollback route (D5), then obtain explicit operator authorization. A green rehearsal is NOT authorization.

### Capability Gate: Upstream write authorization
- Type: human
- Condition: the operator authorizes filing four new issues and closing #359 and #316, and updating #295
- Blocks: epic:6
- Instructions: Read `findings/upstream-drafts.md` (written by Issue 5.6, which is OUTSIDE this gate's Blocks set) and present the four drafted issue bodies and the exact close set, then obtain explicit authorization. **The plan previously gated a reversible local operation and left the irreversible public one ungated** — this gate closes that asymmetry. A green Epic 5 is NOT authorization.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | A merged H1 is itself wrong, rewriting history badly | med | exp-001 justifies each against the plan body; the merge is additive; Issue 1.4 verifies the reconciled text; `git revert` reverses it |
| R2 | plan-030's repair silently drops a bullet | high | Issue 2.3 verifies at BULLET level. The engine's own guard compares dates only and would not catch this — the check must not reuse the defective instrument |
| R3 | The corpus apply damages bundles | high | Rehearsed on a committed sandbox first (Epic 3); repairs committed separately (4.1) so the backfill is one revertable commit; `--record` written; `git revert` is the rollback (D5) |
| R4 | A green `audit` verdict is mistaken for success | high | D6 — verify on `legacy: N` and per-bundle finding counts. The verdict saturates at `warn` and is explicitly not the signal (#359) |
| R5 | A rehearsal uses `--root` and hits the broken `restore` path | med | D3 — every rehearsal `cd`s into the sandbox and passes no `--root`. Measured: `restore` round-trips byte-identically that way |
| R6 | `okf-index-drift` fails on this plan's own bundle rather than the corpus | low | Issue 5.3 covers the whole corpus including plan-065; reindex this bundle before the FULL tier |
| R7 | A partial batch leaves the corpus in mixed state | med | Issue 4.3 asserts `mixed_run` is false and all 8 reported; the record contains mutated bundles only, so halted bundles are provably untouched |
| R8 | An edit perturbs a stored fingerprint and wedges a completed plan | low | Issues 1.3 and 2.4 measure it. The H1 and the phase log both sit above the first `## ` and are fingerprint-excluded; plan-010/013 carry no fingerprint at all |
| R9 | The rehearsal passes vacuously over an empty or already-conformant set | med | Issue 3.5 asserts `legacy_before == 8` and the gate's Test checks that field, so a rehearsal that selected nothing cannot report green |
| R10 | A success criterion is satisfied BEFORE the plan runs, so it measures nothing | high | **measured during drafting:** SC3 as first written was already green (`check_okf_index_drift.py` exits 0 today with `no_index: 8`). Every command-form criterion must be run against the CURRENT tree during review and shown to FAIL; a criterion green at drafting is not a criterion |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | `audit` reports `legacy: 0` AND no bundle became `unclassifiable` or `hybrid-partial`, over at least 70 bundles | `uv run python3 scripts/checks/plan065_checks.py audit-strict` → exit 0 | 5.1 |
| SC2 | All 8 target bundles carry `index.md` + `log.md` and no `README.md` | `uv run python3 scripts/checks/plan065_checks.py bundle-shape` → exit 0 | 5.4 |
| SC3 | `okf-index-drift` is green over the whole corpus AND no bundle lacks an index | `uv run python3 scripts/checks/plan065_checks.py index-drift-strict` → exit 0 | 5.3 |
| SC4 | `restore` has been exercised on a REAL bundle and reverses cleanly | `uv run python3 scripts/checks/plan065_checks.py restore-roundtrip` → exit 0 | 4.4 |
| SC5 | Every one of the 8 is explicitly reported; none silently skipped | `uv run python3 scripts/checks/plan065_checks.py apply-result` → exit 0 | 4.3 |
| SC6 | Per-bundle finding counts recorded before AND after for all 8, and no bundle regressed | `uv run python3 scripts/checks/plan065_checks.py finding-counts` → exit 0 | 0.3, 5.2 |
| SC7 | All ten of plan-030's phase-log bullets survive into `log.md` | `uv run python3 scripts/checks/plan065_checks.py phaselog-bullets` → exit 0 | 2.3 |
| SC8 | plan-010's and plan-013's `index.md` carry the merged objectives verbatim | `uv run python3 scripts/checks/plan065_checks.py merged-objectives` → exit 0 | 5.4 |
| SC9 | The FULL change-validation tier is green on the merged tree | `uv run "$(yf skill-dir yf-change-validation)/scripts/change_validation.py" run --tier full --json` → exit 0 | 5.5 |
| SC10 | **All SIX** engine defects are filed upstream with reproductions. **AMENDED DURING EXECUTION from FOUR (ESC-001).** The four scoped at drafting: (1) `restore --root`'s absolute-path refusal (D3); (2) the one-sided phase-log guard including the dead `src_bul`/`dst_bul`; (3) migrate's skip-if-exists log reconciliation (D4); (4) `restore`'s unchecked `git checkout` return code (`okf_hygiene.py:1371-1372`), the silent total-loss path this plan discovered. Two found DURING the corpus apply: (5) `backfill --apply` generates a NON-CONFORMANT `index.md` — header and objective only, no member listing — so every freshly transformed bundle immediately fails `check_okf_index_drift.py`; measured on all 8, and the generated prose asserts “the files below” with no files below; (6) `reindex`'s dry run reports `verdict: clean`, `exit: 0` while proposing 9 `add-missing` changes — a verdict that contradicts its own change list. **The pre-amendment text said “All FOUR” and named the fourth explicitly, so it would have PASSED while silently dropping (5) and (6)** — the same undercount shape pass-3 caught in the other direction | `manual: filing is an outward-facing write requiring operator authorization; evidence is the six issue URLs recorded in log.md` | 6.1 |
| SC11 | #359 and #316 are closed; #295 updated for SC19 and left open for SC24 | `manual: verified by reading the issues back with gh issue view, never by trusting an exit 0` | 6.2 |
| SC12 | No engine source file is modified by this plan | `uv run python3 scripts/checks/plan065_checks.py no-engine-edits` → exit 0 | 5.5 |
| SC13 | Each of the **ten** subcommands was OBSERVED exiting non-zero on a mutated input | `uv run python3 scripts/checks/plan065_checks.py negative-controls` → exit 0 | 0.4 |
| SC14 | Every **tree-property** subcommand was observed reporting its condition FALSE — not merely `input absent` — against the pre-transform tree | `manual: the pre-transform tree ceases to exist once Epics 1-2 land; evidence is the recorded output in findings/negative-controls.json` | 0.5 |
| SC15 | A FULL-tier recipe ROW invokes `plan065_checks.py`, so it runs in CI rather than by hand | `uv run python3 scripts/checks/plan065_checks.py registered` → exit 0 (parses the §1 FULL tier for a row whose command names the script — **not** a substring grep, which a comment or a stale line would satisfy) | 5.4c |

**Epic 3 is discharged by the capability gate, not by a success criterion.** The `Sandbox
rehearsal green` gate's Test reads `findings/rehearsal-result.json` and blocks `epic:4`, which is
a stronger binding than a criterion — it is machine-enforced at execution time. A reader counting
criterion coverage will see Epic 3 as uncovered; it is not.

**Two kinds of criterion, and they are checked differently.** A *progress* criterion (SC1, SC2,
SC3, SC4, SC5, SC6, SC7, SC8) asserts something this plan makes true, so it MUST be red before
execution — **measured:** SC1 exits 1 today (`legacy: 8`). A *regression* criterion (**SC9 and
SC12**) asserts something already true that must stay true, so it is green now by design.

**SC9's colour is NOT pinned here, and the reason is instructive.** This paragraph has twice
asserted a colour that flipped before it was read — first RED, then GREEN, each true when written.
The cause is structural, not carelessness: the FULL tier includes `okf-index-drift`, which goes
**red every time a review pass is added to this bundle** and green again after Issue 5.2b's
reindex. So SC9 is a regression criterion **for the repository** and a progress criterion **for
this bundle**, and any snapshot of its exit code is stale on write. SC12 is genuinely a regression
criterion. Read SC9 by running it, never by reading a claim about it.
Conflating the two is how SC3 was first written vacuously (R10).

**SC12 is a REGRESSION criterion, not a progress one.** "No engine source file is modified" is
true today and stays true; the moment Issue 0.1 writes the instrument it exits 0. Listing it as
progress would have demanded it be red before execution, which is unsatisfiable — the plan's own
R10 discipline applied to the wrong criterion.

**A `FileNotFoundError` is not evidence.** SC1-SC8 are "red" today only because `scripts/checks/plan065_checks.py` does not yet exist —
measured, every subcommand exits **2**, the plan's own "could not run" code. That says the instrument is absent, not
that the condition is false. Issue 0.5 closes the gap: once the instrument exists, each tree-property subcommand is run
against the pre-transform tree and its FALSE report recorded (SC14).

**Three of the fifteen are `manual:`, and the count came DOWN twice on review.** SC4, SC5 and SC6 were
first written `manual:` on the reasoning that the apply is a one-shot event. That was wrong, and
it was wrong in a way this plan explicitly warns against: it conflated **re-running the apply**
with **re-checking the evidence the apply recorded**. Epic 3 already mechanizes a one-shot event
by writing `rehearsal-result.json` and testing it. The same shape applies, so SC4/SC5/SC6 are now
command-form against `restore-roundtrip.json`, `apply-result.json` and `finding-counts-before.json`.

The four that remain `manual:` are genuinely so: SC10 and SC11 gate on **outward-facing writes**
requiring operator authorization, and SC14 asserts an **observation of a tree that no longer
exists** once Epics 1-2 land (SC13 became command-form in cycle 3) — a re-run would measure a different claim.

The **ten subcommands of one script** are authored by Issue **0.1** and proven by **0.4**; Issues
2.3, 5.4 and 5.5 merely *discharge* the criteria that consume them. **They were ten separate
scripts until cycle 3**, which had pushed the plan to 44 issues with 70% named by no criterion;
consolidating implements the missing-input contract and the negative-control harness once. They are what make these
criteria re-checkable at completion rather than only at discharge — the plan-051 defect
REQ-PLAN-080 exists to catch.
