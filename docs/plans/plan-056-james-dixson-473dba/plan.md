---
type: Plan
okf_spec: OKF-PLAN
id: plan-056-james-dixson-473dba
author: james-dixson
created: '2026-08-28'
status: approved
deliverable_class: standard
fingerprint: 5ad6019cc9c37df171bb70b90c749629aedf1fa4e7717773b725085435b8b634
---
# Plan: OKF: make the structural validation that already exists able to fail, and reconcile the two layers that perform it

**ID:** plan-056-james-dixson-473dba
**Author:** james-dixson
**Created:** 2026-08-28
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** 5ad6019cc9c37df171bb70b90c749629aedf1fa4e7717773b725085435b8b634

## Objective
OKF: make the structural validation that already exists able to fail, and reconcile the two layers that perform it

## Motivation

Three independent measurement passes over this repo (2026-08-28) found that **both structural
validation layers are gates that cannot fail**, and that the OKF issue cluster proposes building
*more* structure on top of them.

- `doc_lint`: `STATUS_SEVERITY` demotes `E` and `W` to `R` at `status: complete`, and essentially
  every historical bundle is `complete` (1603 of 1642 findings). **46 of 48 checks are
  structurally incapable of a non-zero exit**; the 2 that escape via `promote = false` fire zero
  times. Full-corpus run, re-measured 2026-08-28: **1088 files, 1642 findings**, `errors: 0`, verdict PASS, exit 0.
- `okf.py reindex`: appears in **zero** `CHANGE-VALIDATION.md` rows, **zero** CI steps, and is
  never called by `plan_manager.py`. Its `_listing_members()` iterates direct children only, so a
  `clean` verdict certifies ~7 top-level names and is silent about the ~80% of files one level
  down.

The consequence is not hypothetical. Root-index drift was fixed ~9 days ago and **has already
regressed in 9 of the 30 index-bearing bundles** — every bundle authored after the fix, plus two
untracked ones, one of which is plan-056's own. Nothing noticed. That is the empirical answer to "would
anything notice if OKF conformance silently regressed".

So this plan does not build more structure. It makes the OKF half **able to fail** — a corpus driver
wired into the validation recipe, on an exit contract that can no longer confuse "no index" with "no such
path" — gives the two layers an explicit ownership boundary, and converts the one key that drives
discovery (`description:`) from emergent convention into a producer contract.

**Be precise about the doc_lint half, because "able to fail" over-claims there.** D-1 deliberately
retains `STATUS_SEVERITY`'s `complete` demotion and no issue touches it, so after this plan 46 of 48
checks remain structurally incapable of failing a completed bundle. What ships is #246's amendment —
resolved *toward* the schema — which **freezes the erosion at 2 of 48** rather than reversing it, plus
the boundary document that stops the two engines re-diverging. Reversing the demotion is a separate
decision with its own remediation cost, and this plan does not take it.

Root-index depth, the `yf-okf-hygiene` skill and the baseline re-pin are **plan-057**.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| #140 | yf-okf: enforce OKF structure below the bundle root | partial | Root-tier enforcement + drift model IN; nested index.md OUT (re-scoped via #171). Stays open: REQ-OKF-CHK-002 has no other tracker home. | 3.1, 3.2, 4.3 |
| #165 | SPEC `Verification:` lines are prose shaped like commands | partial | One instance discharged — REQ-PORT-010's verification becomes an executed CHANGE-VALIDATION row. General class stays open. | 3.2 |
| #168 | yf-okf: projection delivery mode (on-demand OKF export) | exclude | Parked. Trigger not fired: no consumer on this machine; bp/docs/plans holds 3 yf bundles but lacks the AGENTS.md sentinel, so no OKF tool can resolve it. |  |
| #169 | OKF conformance gate for yf-research and yf-incubator | deferred | Parked as filed. Counter-evidence: yf-research's UNGATED indexes are the corpus's best (3 of 28 bundles supply 32 of 107 unique descriptions); yf-plan's GATED ones are 57% boilerplate. |  |
| #170 | OKF consumer round-trip fidelity is unverified | deferred | **Carried whole to plan-057**, which dispositions it `partial` and owns both halves. This plan performs no work on it; the row exists so the cluster reads complete. Background for the successor: okf-lint ran against this repo today (1563 problems, FAIL). Its top finding is ROOT FRAMING — 32 findings, because it takes the repo as OKF root while yf assumes each bundle is one. **`partial`, not `include`**, on TWO grounds. The WRITE half cannot be exercised at all — okf-lint's `--fix` hard-delegates to bookpipe-internal generators and crashes on a yf tree. And the READ half is only **partially** evidenced: EXP-006's per-folder loop `continue`s on a missing `index.md`, so **1285 of 1383 concept documents were never inspected** and its own recommendation 5 says do not carry a B1/B2 pass forward from that run. Both halves stay open; what is discharged is the root-framing characterisation, not corpus conformance. |  |
| #171 | yf-okf: nested index.md generation, deferred behind a `description:` producer change | partial | Re-scoped. IN: make `description:` a producer contract. OUT: nested index.md generation — the leverage is per-file entries in the ROOT index. | 0.4, 2.1, 4.3 |
| #173 | success criteria and upstream dispositions never checked against the engine | exclude | Filed 'record, do not fix'. Different axis. |  |
| #174 | a review-phase validation pass | exclude | Separate mechanism, separate plan. |  |
| #189 | Six shipped scripts have no tests at all | deferred | Not this cluster. Taken as a CONSTRAINT, re-aimed at what this plan actually builds: Issue 1.9's eight harness scripts ship with a RED-fixture selftest (SC35), so they do not become scripts 7-14 of the untested set. |  |
| #192 | Evaluate a structure-first plan DSL with generated markdown | deferred | Interaction recorded: under #192 index generation becomes a by-product — a further reason to re-scope #171 rather than build nested indexes. |  |
| #233 | audit-close's OKF walk has no fixture carve-out | include | Subsumed by the reconciliation. Real defect: the OKF walk has no path-exclusion concept, which doc_lint already solved twice. | 1.3, 1.5 |
| #244 | README-contract drift: e-readme-layout fails 16/19 skills | exclude | Different edge, different contract. |  |
| #246 | REQ-DATA-044 says R* is uniformly W but the schema ships two E close-out checks | include | A conformance defect inside doc_lint. Those two E checks are the ONLY ones surviving status demotion, so they sit directly in the enforcement path. | 0.2, 1.6 |
| #265 | CRITICAL: recheck-criteria reports PASS when criteria were never judged | include | Filed BY this plan's red-team pass 3, not found in scoping. `recheck-criteria` counts `inconclusive` rows in neither `failed` nor `evaluated`, so one green criterion yields `verdict: PASS` while any number of criteria go unjudged. Affects every plan in the repo. Third shape of the collapsed-signal class tracked by #263. | 0.13, 1.10 |
| #247 | Drift findings no edge covers | partial | IN: §1's mechanism only — a declared listing with no generator is the same defect as index drift, so one generator/checker serves both. OUT: the rest. | 3.1 |

## Investigation Findings

### Scoping decisions

| # | Decision | Basis |
| :-- | :-- | :-- |
| D-1 | **Enforcement is forward-only, with a live drift gate.** With the backfill carried to plan-057, this plan modifies no completed bundle's content on any axis; Issue 3.4 repairs live indexes only. Wire `reindex --check` into `CHANGE-VALIDATION.md`; repair whatever the driver enumerates as drifting (9 at scoping, 8 today — the set is live, see Issue 3.4); leave `STATUS_SEVERITY`'s `complete` demotion intact. | Operator decision. Re-judging history would put a large, unmeasured remediation burden on frozen bundles and contradicts "history is not re-judged by a rule". **The "~423 findings" figure this row originally cited was unsourced** — it collided numerically with the stale "0 of 423" spec line Issue 0.8 is fixing. Re-measured 2026-08-28 on the live corpus: **1088 files, 1642 findings, 1603 at `bundle_status: complete`, and 392 findings currently demoted `E`/`W` -> `R`.** That 392 is the real number the "~423" was standing in for, which is why the two were so close. Issue 0.12 re-derives it at execution rather than inheriting this line. |
| D-2 | **CARRIED TO THE SUCCESSOR PLAN.** **`yf-okf-hygiene` owns full OKF health**: `audit` (read-only) / `backfill --apply` / drift repair / `restore`, runnable in any repo. | Operator decision. Gives the D-1 gate a repair tool instead of leaving remediation manual. |
| D-3 | **The two validation layers are both retained, with an explicit written ownership boundary.** No code merge. The OKF walk gains doc_lint's path-exclusion concept. | Operator decision. Closes #233 at its cause rather than with a second bespoke exclude list. |
| D-4 | **CARRIED TO THE SUCCESSOR PLAN.** **Do not build nested `index.md`.** Deepen the ROOT index to enumerate nested files with descriptions instead. | Measured: 6 of 28 bundles already do this by hand and produce the corpus's only irreducible entries; 78% of files are reachable only via a rollup bullet. #171's own measurement (52% of subdirectories would get a valueless listing) argues against the nested form specifically, not against per-file entries. |
| D-5 | **CARRIED TO THE SUCCESSOR PLAN.** **Nested `log.md` stays permanently dropped** (plan-046 D-4). Not re-opened. | Every `okf.append_log` call site targets the bundle root; no producer event is scoped below it. |
| D-6 | **CARRIED TO THE SUCCESSOR PLAN.** **File nothing upstream.** Track `GoogleCloudPlatform/open-knowledge-format` read-only. | Operator decision. |
| D-7 | **CARRIED TO THE SUCCESSOR PLAN.** **Re-pin `OKF-BASELINE.md` to the relocated repo** and record that "v0.2" is an unversioned moving target. | Measured: upstream **announced** the `okf/` snapshot as frozen on 2026-08-21 and has changed v0.2 in place (ISO 8601 offsets) with no version bump. **Corrected by EXP-006:** the old copy is *not* observably stale — it is md5-identical to the live one and received that change 18 hours first. The re-pin rests on upstream's stated intent plus the unversioned mutation, not on measured staleness. |
| D-8 | **`description:` becomes a producer contract**, not an emergent convention. | Measured: no producer write path exists and no schema requires it. **Re-aimed by EXP-002:** the agent side is already at **51/51 since plan-052** and self-sustaining with no prompt instruction, so the unsolved half is the **code** producers, measured at 1% — not the agents. The contract makes the existing convention verifiable and closes the producer gap; it is not a rescue of a failing practice. |
| D-9 | **CARRIED TO THE SUCCESSOR PLAN.** **`yf-okf-hygiene` ships with tests.** | #189 constraint: six shipped scripts already have none; this must not become a seventh. |
| D-10 | Corpus-wide backfill of the wider corpus is **out of scope for execution**, but the skill must be able to run there. | Operator chose the skill route precisely so the backfill is repeatable rather than a one-off. Re-measured: the wider corpus is **514 bundles across 41 repos**, not ~100 across ~25. |
| D-11 | **CARRIED TO THE SUCCESSOR PLAN.** **Ship the tool AND backfill this repo's 30, AND support `_index.md`.** | Operator decision. Measured: a half-done backfill is strictly *worse* than none (`okf_missing_level` flips on `okf_native`), and `_index.md` is 47% of the 514-bundle wider corpus vs README's 26%. |
| D-12 | **CARRIED TO THE SUCCESSOR PLAN.** **Backfill HALTS on both risk classes** — `hybrid-partial` (pre-existing `log.md`) and objective divergence. Nothing is silently discarded. | Operator decision. 8 of 30 bundles need an explicit resolution: plan-030 strands 10 log bullets, and 7 bundles' README objective differs from `plan.md`'s H1 (richer in plan-010/013). |
| D-13 | **CARRIED TO THE SUCCESSOR PLAN.** **The backfill is `migrate` -> DELETE the renamed index -> REGENERATE the listing, never `okf migrate` alone.** The regeneration step is the `index-add`/regeneration surface Issue 2.5 exposes, which wraps `seed_index`; an earlier wording named `seed_index` directly and read as a different operation from 2.5's verb. | Measured: `migrate` alone introduces a NEW hard audit `fail` on 30/30, and `reindex --write` cannot repair it — it appends bullets below legacy prose and reports `clean`. |
| D-14 | **Exclusion lists are independently declared with a shared mechanism**, plus a test asserting the overlap invariant. The mechanism is shared **in both directions**: Issue 1.2 gives `okf.py` an `exclude_globs` concept, and Issue 1.5 makes `doc_lint` able to read the member's §3b so the invariant is checkable from both sides rather than only asserted. | Measured: the two layers use different coordinate systems and granularities, and derivation would miss `assets/fixtures/**` entirely — doc_lint is silent there by non-selection, not exclusion. |
| D-15 | **#246 resolves TOWARD the schema**: amend the spec, keep the two `E` close-out checks. | Measured: they are the only 2 of 48 checks that can produce `E` at `complete`. Deleting them makes doc_lint structurally incapable of failing a completed bundle. |
| D-17 | **Split at the Epic 3/4 seam.** plan-056 keeps the enforcement gap (35 issues); root-index depth, the `yf-okf-hygiene` skill and the baseline re-pin become a successor plan. | Red-team pass 3, supported. The plan grew 46 -> 51 -> 54 under review, each cycle adding issues to close a hole the previous cycle opened; the DAG had zero backward cross-epic edges, so the split was mechanically legal; and Epic 5's `_index.md` route was measured to have **one** live in-repo target while its 47% justification is 227-of-243 in a repo D-10 bars touching. |
| D-16 | **CARRIED TO THE SUCCESSOR PLAN.** Pin the baseline by CONTENT HASH, not by version label. | Measured: upstream changed 41 lines under an unchanged `**Version 0.2**` header with §13 not updated. A label-only pin would have detected nothing; a content hash fires on the actual event. |

### Findings summary

All six experiments returned. Full reports in [`findings/`](findings/).

| # | Headline |
| :-- | :-- |
| [EXP-001](findings/exp-001-reindex-drift-gate.md) | Drift is **9, not 7** (two untracked, one of them plan-056 itself). All 9 trace to ONE structural producer defect: `_INDEX_MEMBERS` is a closed allowlist without `scripts/`, and `seed_index` only emits members non-empty at scoping. **The producer fix must precede the gate.** `reindex_check` cannot distinguish `no-index` from `no-such-path` — both exit 2 with identical JSON — so under D-1's demotion a mistyped path silently checks nothing. Runtime 11.7 ms corpus-wide. |
| [EXP-002](findings/exp-002-description-producer-contract.md) | **The premise was half-wrong.** Of 27 errors a `description` check raises at intake, **27 are code-generated and 0 agent-written**. Agents hit **51/51 since plan-052** with no prompt instruction; code producers sit at 1%. Quality risk did not materialise: **~120 of 126 (95%) are genuinely informative**. A `W` check is corpus-PASS today and becomes the intake gate for free. |
| [EXP-003](findings/exp-003-deepen-root-index.md) | **Zero engine change is needed to ACCEPT nested entries** — 5 of 6 hand-nested bundles round-trip byte-identically; `_covered_by_listed_children` already exists and its docstring cites `exp-003`. Cost moved to descriptions: frontmatter coverage is 18.5%, so widening alone adds ~200 bare bullets. Rule D (enumerate iff <=10 files) bounds every bundle at **max 30 entries**. |
| [EXP-004](findings/exp-004-layer-ownership-boundary.md) | **The overlap is 6 frontmatter keys on 56 files, out of 48 checks and 1105+ documents** — D-3 confirmed by measurement. But **1049 files (94.9%) are covered for identity frontmatter by OKF and nothing else.** #233 reproduces exactly and is generic (plan-029 shows 34 more in a different tree). OKF folds INCONCLUSIVE into FAIL. |
| [EXP-005](findings/exp-005-backfill-and-hygiene-skill.md) | **`okf migrate` introduces a new hard `fail` on 30/30.** The correct backfill is three steps and is **unreachable from any CLI** today. The wider corpus is **514 bundles / 41 repos**, and **`_index.md` (47%) dominates `README.md` (26%)**. `assess` is advertised in two places and does not exist. |
| [EXP-006](findings/exp-006-round-trip-and-repin.md) | **Only 32 of 1563 okf-lint findings are the genuine disagreement**, and all 32 flip on root framing alone. **But only ~100 of 1383 concept documents were inspected** — the walk short-circuits on a missing `index.md`, so no B1/B2 pass may be inferred from the run. **OKF v0.2 is SILENT on identifying a bundle root, and the gap is circular** — the only in-band marker is the one key a wrongly-rooted consumer rejects. The write half **cannot** be tested. Corpus impact of the ISO-8601 change: **zero**. |

**Corrections this investigation forced on the plan's own premises**, recorded rather than quietly fixed:

- The drift count was 7; it is **9**.
- I asserted the old upstream location was frozen and stale. **It is md5-identical to the live copy and received the latest change 18 hours first.** The freeze notice is intent, not state — the re-pin rests on that intent, not on observed staleness.
- I stated D-3's history-rewriting tension against `doc_lint`. **`doc_lint` has zero references to `index.md` or `README`**; the real surface is `_audit_plan`'s `okf_missing_level`, whose grandfather is `okf_native`, not status.
- The wider corpus was scoped at ~100 bundles in ~25 repos. It is **514 across 41**.

### Experiments

| # | Question |
| :-- | :-- |
| EXP-001 | What exactly should the `reindex` drift gate check, and would it be stable? Characterise the 7 regressed bundles, determine the correct FAST/FULL tier placement and path exclusions, and confirm a gate would not false-positive on fixtures. |
| EXP-002 | Is a `description:` producer contract mechanically enforceable? Nested artifacts are written by agents, not code — establish whether this is a schema check, an agent-prompt change, a real producer write path, or some combination. |
| EXP-003 | What does deepening the root index actually require of `okf.py`? Does `reindex --write` support per-file nested entries, and what is the drift model once nested files are listed? |
| EXP-004 | Map the concrete overlap surface between `doc_lint` and `okf.check_conformance` so the D-3 boundary is written from measurement. Include #233's exclusion defect and #246's declared-vs-shipped severity conflict. |
| EXP-005 | Is the README.md to index.md backfill mechanical? Inspect the 30 legacy bundles, assess what `yf-okf migrate` already does, and characterise its risk surface on completed history. |
| EXP-006 | Run the okf-lint round-trip properly and characterise the root-framing disagreement. Determine what OKF-BASELINE must say about bundle-root identification, and what re-pinning to the live upstream changes. |

## Approach

**Five epics, sequenced so that nothing is enforced before the thing it enforces can pass.** That
ordering is not stylistic — EXP-001 and EXP-002 independently measured that landing a check ahead of
its producer turns every future bundle red, and EXP-002 measured that it would hard-fail plan-056's
own intake on 16 errors in files it did not write.

The spine:

1. **Epic 0 — SPEC first.** Every behaviour change below gets its `REQ-*` ahead of the code, per the
   repo's SPEC-first rule. Three of these are amendments to requirements that are currently *false*
   (`REQ-DATA-044`, the `reindex` exit contract, the stale "0 of 423" figure).
2. **Epic 1 — repair the engines' contracts.** The exit-code conflation and the missing exclusion
   concept are both *gate-integrity* defects: a gate built on either would report green while checking
   nothing. This epic is what makes Epic 3's gate trustworthy.
3. **Epic 2 — fix the producers.** The index producer that cannot list post-scoping members, the
   `description` stamp, the splice defect that corrupts grouped indexes today, **and a new public
   `index-add` CLI verb** — which also makes the successor plan's backfill reachable, since `seed_index` is callable only from `init` today.
4. **Epic 3 — turn enforcement on.** Only now: the corpus driver, the `CHANGE-VALIDATION` rows, the
   `description` schema check, and the 9 regressed bundles. **The recipe wiring lands last within the
   epic**, after the producer fix and the corpus repair, because it is the epic's one irreversible act.
5. **Epic 4 — write the boundary document and reconcile.** The doc_lint/OKF ownership boundary is
   enforcement work, not documentation work: it is what stops the two engines from re-diverging once
   Epic 1 has given them a shared exclusion mechanism.

**What moved out, and why (D-17).** Red-team pass 3 argued this plan was too large, and it was right:
across two review cycles it grew 46 -> 51 -> 54 issues, with each pass adding issues to close a hole the
previous pass's issues opened. The DAG already had **zero backward cross-epic edges**, so the split was
mechanically legal. Root-index depth, the `yf-okf-hygiene` skill and its backfill, and the baseline
re-pin are now a successor plan. What remains is exactly the Motivation: **make the structure that
already exists able to fail.**

**What this plan deliberately does not do.** It does not build nested `index.md` (D-4), does not
**re-judge history's severities** (D-1), does not merge the two validation engines (D-3), does not deepen
the root index, does not build the hygiene skill, and does not touch the OKF baseline — the last three
being the successor plan's scope.

With the backfill deferred, this plan touches **no completed bundle's content at all** — Issue 3.4
repairs 9 drifting indexes, which is forward-looking maintenance of live artifacts, not a migration of
frozen history. The tension that D-1 had to be reconciled against moves to the successor plan with the
work that created it.

## Epics

### Epic 0: SPEC amendments (SPEC-first)
- Issue 0.1: Amend `REQ-OKF-011` — `reindex`'s exit contract must distinguish `no-such-path` from `no-index`, run `check_markers` in `--check` mode, and reserve a code for INCONCLUSIVE.
- Issue 0.2 (`REQ-DATA-044` amended, new `REQ-DATA-071`): Amend `REQ-DATA-044`'s severity bullet to permit a `statuses`-scoped `E` close-out binding with `promote = false`, and add a new `REQ-DATA-*` declaring that binding, which is currently documented nowhere.
  - resolves-upstream: #246 (include)
- Issue 0.3 (`REQ-OKF-CHK-003`): Add a requirement declaring the path-exclusion concept — a member-declared `OKF-EXTENSION.md` §3b, applied at every walk site.
  - resolves-upstream: #233 (include)
- Issue 0.4 (`REQ-DATA-072`): Add a requirement for the `description:` producer contract, naming which producers stamp it and which types are deliberately exempt.
  - resolves-upstream: #171 (partial)
- Issue 0.14 (`REQ-CLI-018`): **Codify the harness contract that already exists** rather than drafting a new one — `scripts/checks/_common.sh` (plan-055) declares `0 holds · 1 does not · 2 could NOT RUN` for every instrument in that directory, and Issue 1.9's scripts land in the same directory. The requirement adds what `_common.sh` does not yet state: every check is two-branch where it asserts a failure code, fails loudly on an empty inspection, and reserves 126/127 to the caller. Issue 1.9 creates eight scripts, which is a new repo surface; without this REQ the epic that enforces SPEC-first would itself violate it, and SC1 would be FALSE against 1.9 while being adjudicated by a script 1.9 writes.
- Issue 0.13 (`REQ-PLAN-080` amended): A class-A Success Criterion that is `inconclusive` **at completion** must not be silently equivalent to one that holds. Measured on `plan_manager.py:2945-2969`: `recheck-criteria` counts `inconclusive` rows in neither `failed` nor `evaluated`, so one green criterion alongside any number of unjudged ones yields `verdict: PASS`, exit 0, with the reason string "all N evaluated criterion/criteria hold". `evaluated_fraction` is emitted and consumed by nothing. This defeats the requirement's own rationale — "a criterion is only as good as the last time something re-ran it" — with a criterion nothing can run, and it affects every plan in the repo. Filed upstream as a CRITICAL bug: **dixson3/yoshiko-flow#265** (bead `yf-8u2c`, `external_ref` recorded).
- Issue 0.9 (`REQ-OKF-CHK-004`): Add a requirement for the corpus index-drift driver and its `CHANGE-VALIDATION` binding — root enumeration by depth-1 glob, the exclusion source, the three-valued exit contract, and the minimum-roots guard.
- Issue 0.10 (`REQ-PLAN-081`): Add a requirement for the execution-time index member set, the lifecycle `reindex_write` call sites, and the new public `plan_manager.py index-add` verb. These are three behaviour changes with no requirement today.
- Issue 0.11 (`REQ-CLI-017`): Add a requirement for the test-invocation guard — a Python test entrypoint MUST forward its arguments and MUST fail rather than pass when a selector matches nothing.
- Issue 0.12: Re-derive D-1's basis by measurement: run `doc_lint` corpus-wide with the `complete` demotion disabled and record the real promotion count and its date, replacing the unsourced "~423" figure. Bookkeeping — this issue corrects a number, not behaviour.
- Issue 0.8: Correct every **shipped** instance of the stale "0 of 423" figure — scoped as SC27 scopes it, to specs rather than to frozen bundles, because "every instance" read literally reaches plan-046's completed bundle and contradicts D-1. Re-measured at pass 9 with `grep -rn '423' skills/ _shared/`: **8 occurrences across 4 files** — the five coverage-claim forms (`yf-okf/SPEC.md:288` and `:293`, `OKF-BASELINE.md:150`, `OKF-YF-EXTENSIONS.md:389`, `_shared/test_okf.py:966`) **plus three derived counts equally stale** (`SPEC.md:311` "would write 423 assertions", `OKF-YF-EXTENSIONS.md:395` "producing 423 entries", `test_okf.py:967`). An earlier draft said 5 across 4, counting one variant form and not the others. Re-measure and stamp the measurement date, per **D-4/D-8** — an earlier draft cited D-5, which is about nested `log.md` and is not the relevant decision.

### Epic 1: Engine contract repair
- Issue 1.10: Implement the `REQ-PLAN-080` amendment in `plan_manager.py`'s `recheck-criteria`: an unjudged class-A criterion at the completion binding must block, via a `harness_incomplete` state or a `--require-evaluated` threshold. Mid-flight runs stay advisory. **Ships its test as `skills/yf-plan/scripts/test_recheck_criteria.py`** — named here because SC36 invokes it and, at pass 5, no issue created it.
  - depends-on: 0.13
- Issue 1.1: Make `reindex_check` distinguish `no-such-path` from `no-index`, run `check_markers`, and return INCONCLUSIVE where the instrument could not judge.
  - depends-on: 0.1
- Issue 1.2: Add `exclude_globs` to `ExtensionRuleset`, parsed from a new `OKF-EXTENSION.md` §3b table.
  - depends-on: 0.3
- Issue 1.3: Apply exclusions at all five walk sites — `okf.py` `check_conformance`, `migrate`, `_listing_members`, and `plan_manager.py`'s conformance walk and `dangling-refs` scan. Use `fnmatch`, not `_glob_match`, which cannot do recursive `**`.
  - depends-on: 1.2
  - resolves-upstream: #233 (include)
- Issue 1.4: Add `--no-exclude` to `okf.py check` as the positive control, mirroring `doc_lint`.
  - depends-on: 1.3
- Issue 1.5: Seed `skills/yf-plan/OKF-EXTENSION.md` §3b with `assets/fixtures/**` and `findings/okf-migration-samples/**`; teach `doc_lint` to READ §3b so D-14's shared mechanism is genuinely two-sided rather than `okf.py`-only; and add the overlap-invariant test, asserting both lists are non-empty. plan-029's 34 findings are the RED fixture.
  - depends-on: 1.3
- Issue 1.6: Fix **all four copies** of the false banner — `_shared/document_types/plan-relations.toml:7`, its vendored twin, and `doc_lint.py:339` in both `_shared/` and `skills/yf-plan/scripts/`. `DRIFT-CHECK.md:194` names the engine banner explicitly, so fixing one copy leaves a declared drift edge red.
  - depends-on: 0.2
- Issue 1.7: Vendor-sync `okf.py` to all four `skills/*/scripts/` copies via `_shared/sync.py`.
  - depends-on: 1.4, 1.5
- Issue 1.9 (`REQ-CLI-018`): Author the plan's **verification harness**, **after first evaluating `redcheck.sh verify-red-checks` (plan-054) as prior art** — it already iterates `checks/`, requires a recorded non-zero pre-fix observation per script, supports an allowlist-with-reason, and fails when it finds no instrument, which is precisely `--require N`. plan-055 copied `_common.sh` and three checks into `scripts/checks/` but not `redcheck.sh`, so this is not strict duplication; relocating the proven implementation is nonetheless the default, and writing a bespoke eighth script needs a stated reason. — exactly the eight scripts its criteria invoke, derived mechanically from the Verification column rather than listed by hand: `check-req-coverage.py`, `check-reindex-exit-contract.sh`, `check-description-coverage.py`, `check-fixture-carveout.sh`, `check-closeout-can-fail.sh`, `check-drift-driver-contract.sh`, `check-recipe-row.sh`, `harness-selftest.sh`. (`check-pytest-ran.sh` is 1.8's; `check_okf_index_drift.py` is 3.1's.) Each must be **two-branch where it asserts a failure code** — assert a pair of exits differ, so a missing instrument cannot satisfy it — and each must fail loudly when it inspected nothing. Re-derive this list as an approval preflight; an earlier draft's list was assembled by hand, named a script no criterion invoked, and omitted four that four criteria did. **`harness-selftest.sh` enumerates BY NAME from SC0's list, never by glob, and dispatches per extension** (`bash` for `.sh`, `uv run` for `.py`) — measured, the ten instruments span three naming conventions and two languages, and `redcheck.sh`'s `cmd_verify_red_checks` iterates `check-*.sh` while `record-red-check` hard-rejects any other name, so a glob-based enumerator reaches **6 of 10**. **`check-recipe-row.sh <token>` matches a §1 row whose `id` EQUALS the token or whose `cmd` CONTAINS it** — a whole-row-line match, and it must be defined that way because the two criteria that use it pass different things: SC11 passes the row id `okf-index-drift`, which never appears in `check_okf_index_drift.py`'s underscored filename, while SC11c passes filenames that Issue 3.2a does not declare as ids. An id-only implementation makes SC11c false; a cmd-only one makes SC11 false. **`harness-selftest.sh` excludes itself from its own count**, hence `--require 9`: a selftest cannot be its own RED fixture. SC0 is what proves the tenth exists.
  - depends-on: 0.14
- Issue 1.8: Add `scripts/checks/check-pytest-ran.sh` **and nothing else** — grep the named test's `def`, then run pytest **with the target's own PEP 723 `dependencies` parsed and forwarded** (or via `uv run --script`), and require a non-zero passed count. The forwarding is not optional: measured, `uv run --with pytest python -m pytest _shared/test_okf.py` dies at collection with exit 2 because module form makes `python` the entrypoint and the target's PEP 723 header is never read, while `test_cli_enumeration.py` happens to need nothing — the per-file dependency set is heterogeneous and **6 criteria invoke this script** (SC4, SC7, SC8, SC10b, SC28, SC36) — re-derived at pass 9; the "20" an earlier draft carried was a pre-split figure from the 33-criteria era. Its own INCONCLUSIVE result is **exit 2**, matching `scripts/checks/_common.sh:21-26`'s declared contract for that directory (`0 holds · 1 does not · 2 could NOT RUN`) — an earlier draft pinned it to 3, inventing a second contract for a script landing beside the six that now follow it in that directory (plan-055 added `_common.sh` plus three checks in its Epic 0; six checks live there today), and `record-red-check` refuses to bank a 2 while an exit 3 would be banked as a genuine red observation. 126 and 127 stay reserved to the caller: returning either would make every criterion routed through this script permanently unfailable. It must return **INCONCLUSIVE, never pass**, on a hand-rolled non-pytest entrypoint: measured, `_shared/test_doc_lint.py` has **0 `def test`**, no pytest import and no `__main__`, and 15 repo test files have no `__main__` at all. **Explicitly NOT in scope: rewriting the 34 `pytest.main` call sites.** An earlier draft prescribed that on a false premise (see the Verification convention above); the wrapper closes the gap alone, and a repo-wide refactor touching every skill does not belong on the critical path of the six criteria that invoke it ("12" was likewise a pre-split figure).
  - depends-on: 0.11

### Epic 2: Producer repair
- Issue 2.1: Add `description` to `_stamp_okf_type` and pass `"Upstream issue #N - <title>"` from `_write_upstream_reference`. Measured at 6 lines, spiked and executed.
  - depends-on: 0.4
- Issue 2.2: Stamp `description` on `plan.md` (from the objective) and `upstream-triage.md`. Deliberately exempt `context.md` and `plan-retrospective.md` — a derived value there is 67 identical strings.
  - depends-on: 2.1
- Issue 2.3: Add the missing execution-time member to `_INDEX_MEMBERS` — **`scripts/` only**: `assets/` has been in the allowlist since plan-029 and is unlisted for a different reason, because `seed_index` emits a member only if it is non-empty **at seed time** and call `reindex_write` at intake, execute-start and close, so the index tracks a bundle that grows after scoping.
  - depends-on: 1.1, 0.10
- Issue 2.4: Fix `_ensure_index_lists_member` / `_ensure_index_lists_retrospective` to insert after the last bullet **of any indentation**. This is red today for plan-048/049/050. **No new REQ**: this restores the shipped behaviour `REQ-PLAN-010`'s index contract already implies, so it is a bug fix rather than a behaviour change. Ships its RED fixture as a pytest test in a new `skills/yf-plan/scripts/test_index_members.py` — the function lives in `plan_manager.py:784`, not in `doc_lint.py`, and `_shared/test_doc_lint.py` is a hand-rolled script with zero test functions, so neither is a valid host.
- Issue 2.5: Add a `plan_manager.py index-add <plan_dir> <path> <description>` verb mirroring `index_manager.py add`, and expose index regeneration from the CLI. This is a **new public surface**, and it must ship its own `index_add_verb` test in `skills/yf-plan/scripts/test_cli_enumeration.py` (whose existing tests are set-equality over the verb list). It is also the backfill's step 3 — measured unreachable today, since `seed_index` is callable only from `init`.
  - depends-on: 2.4, 0.10
- Issue 2.6: Name `description` alongside `type`/`okf_spec` in `captor.md`, `investigator.md` and the review agents, billed as a hit-rate lever rather than enforcement. Borrow the working convention: the description carries the answer or verdict, not the question.
  - depends-on: 0.4

### Epic 3: Enforcement
- Issue 3.1: Write `scripts/checks/check_okf_index_drift.py` — a corpus driver enumerating bundle roots by depth-1 glob (never `rglob`), gitignore-aware, exiting 0 clean / 1 drift / 2 INCONCLUSIVE, hard-erroring on a nonexistent enumerated root so demotion cannot mask a typo, and emitting a `bundles_checked` count with a `--min-roots N` guard so a driver that enumerated nothing cannot report clean.
  - depends-on: 1.1, 1.7, 0.9
- Issue 3.2a: Add `CHANGE-VALIDATION.md` rows — ids `uv-recheck-criteria` and `uv-index-members`, following the file's existing `uv-*` convention — for the two test files this plan creates — `test_recheck_criteria.py` (Issue 1.10) and `test_index_members.py` (Issue 2.4). Without them SC36 and SC28 hold once at close and nothing re-runs them; `test_cli_enumeration.py` and `_shared/test_okf.py` already have rows, so the other filtered criteria stay covered after the land.
  - depends-on: 1.10, 2.4
- Issue 3.2: Add `okf-index-drift` to `CHANGE-VALIDATION.md` §1 FAST and FULL, with §3 trigger-scope globs. Both tiers run the whole corpus — at 12 ms that is cheaper than per-bundle mapping. This is Epic 3's one irreversible act: wiring the gate before the producer fix and the corpus repair would make the FAST tier fire red on every subsequent edit, including those performing 3.4.
  - depends-on: 3.1, 2.3, 3.4, 0.9
- Issue 3.3: Add the `description` check to the nested document types at severity `W`, paired with `regex-present` `^description:\s*\S` so an empty string cannot satisfy it. Scope `research-*` out, or accept a permanently unpromoted warning.
  - depends-on: 2.2, 2.6
- Issue 3.4: Repair **every bundle the driver reports drifting** — authoring real descriptions rather than accepting `reindex --write`'s bare bullets. Name the enumeration, not a count: the set is live and moves. Measured at scoping it was 9; re-measured at pass 4 it is still 9 but a **different** 9 — `docs/research/005-*` is now clean and **plan-057, created hours earlier by this plan's own split, is already drifting**, which is the producer defect reproducing in real time. SC10's `--min-roots 30` floors the enumeration; its exit-0 requirement forces the repair.
  - depends-on: 2.3, 2.5

### Epic 4: Boundary document and reconcile
- Issue 4.1: Write the layer boundary document on three axes — container vs content, status-aware vs status-blind, repo-rooted vs bundle-relative — citing the 1049/1105 and 2/48 measurements that make the split non-arbitrary. Resolve the one real duplicate explicitly rather than leaving it to a filter. Each layer must reference the other, closing the measured zero-cross-reference gap.
  - depends-on: 1.7, 0.2
- Issue 4.2: File the follow-on beads: `okf migrate`'s hybrid log loss, the missing `assess`/`init` verbs, OKF's INCONCLUSIVE-as-FAIL, the 21-at-0.1/11-at-0.2 corpus split, the two stale-authority strays, #165's `REQ-PORT-010` ambiguity (it resolves to two unrelated requirements in two specs), that **nothing verifies a bundle's `context.md` and `upstream-triage.md` against its `plan.md`** — both drifted through six red-team passes with audit, `doc_lint` and `reindex` all green, and pass 7 found `context.md` asserting a destructive backfill this plan does not perform; that **nothing verifies a gate's `Instructions:` survive extraction**, which is how pass 6's silent truncation went unseen; and — found at pass 5 — that **the `## Gates` grammar cannot express `test_class` or `cwd`**, the two metadata fields §5.2c's sweep dispatches on, so every capability gate in every plan depends on a value invented at pour time whose default is the one class never executed.
  - depends-on: 4.1
- Issue 4.3: Reconcile upstream dispositions — comment on #165, #171, #247 with what shipped and what remains; comment on **#140** with the root-tier enforcement that shipped; close #233, #246 and #265; record #170 as carried to the successor plan. Run `verify-reconcile` as an approval preflight, not only at close: it detected an unreachable end state in one invocation while this plan was still drafting.
  - depends-on: 4.2, 3.4
  - resolves-upstream: #165 (partial), #171 (partial), #247 (partial)

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Verification harness ready
- Type: auto
- Condition: Every harness script exists, is syntactically runnable, and returns non-zero on its RED fixture — verified before any enforcement work lands.
- Test: scripts/checks/harness-selftest.sh --require 9
- Blocks: 3.2, 3.3, 3.4
- Instructions: This gate exists because the criteria layer failed four consecutive red-team passes, and because the criteria layer cannot police itself here. `recheck-criteria` runs from the INSTALLED skill directory, so Issue 1.10's engine fix lands in the working tree and is NOT in effect for this plan's own close-check, and installing mid-execution is forbidden. A gate's `Test:` is executed by the coordinator and halts on a non-zero exit, entirely outside `recheck-criteria`'s verdict arithmetic — so it is the one defence that reaches this plan. Its evidence is produced entirely by Epic 1 plus the corpus-driver issue, none of which this gate blocks. **The `Blocks:` list is issue-level rather than `epic:3` deliberately:** `--require 9` counts the corpus driver among the instruments, and that driver is authored inside Epic 3 — so blocking the whole epic would have required an instrument produced within the gate's own blocked set, making the gate unreachable and guaranteeing a stop-class-2 override on every run. Naming the enforcement issues individually keeps the driver unblocked while still gating every act that turns the OKF drift gate on. (Issue 3.2a wires the two test-file recipe rows and sits deliberately outside `Blocks:` — its producers precede it via `depends-on`, so R1's ordering hazard does not reach it.)
  **POUR THIS GATE WITH `test_class: probe` AND `cwd: worktree`.** This is not optional and the plan
  cannot express it in the `## Gates` grammar: `plan_extract.py`'s `GATE_FIELD` matches only
  `Type|Approvers|Condition|Test|Blocks|Instructions`, and `test_gates.py:243` defaults an absent
  `test_class` to **`manual`**, which §5.2c never runs and which resolves INCONCLUSIVE — so a gate
  poured without it is inert, which is exactly the failure this gate exists to prevent. `cwd: worktree`
  matters because Epic 1's scripts land in the execution worktree, and a gate poured `cwd: repo-root`
  can never pass and stalls into stop class 2.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **A gate lands ahead of its producer and turns every future bundle red.** Measured twice: EXP-001 (all 9 drifts trace to the producer) and EXP-002 (a check landing first hard-fails plan-056's own intake on 16 errors). | high | Epic 2 precedes Epic 3 by explicit `depends-on` edges on every enforcement issue — including Issue 3.2, the epic's one irreversible act, which now depends on 2.3 and 3.4. **The ordering evidence is the DAG itself, verified mechanically, not a criterion.** An earlier draft claimed SC5 proved it; SC5 was green in both worlds, because Issue 3.3 declares the check at `W` and REQ-DATA-057 maps intake lint findings W->warn. SC5 now checks finding content instead. |
| R2 | **The drift gate is built on an exit contract that cannot distinguish "no index" from "no such path"**, so a mistyped path is demoted and the gate silently checks nothing. | high | Issue 1.1 fixes the contract before Issue 3.1 consumes it; the driver additionally hard-errors on a nonexistent enumerated root (SC3). |
| R4 | **`reindex --write` satisfies the gate while degrading the artifact** — bare descriptionless bullets pass every check the plan adds. | med | Issue 3.4 authors real descriptions rather than accepting the generated ones; `reindex_write` is never presented as the operator remediation (EXP-001 rec 6). |
| R13 | **The criteria layer is the plan's weakest surface, and was measurably vacuous in THREE consecutive review passes** — `-k` no-ops (pass 1), missing-script exit 2 (pass 2), and unjudged-reads-as-PASS (pass 3) — five criteria were green on unmodified HEAD, because every Python test entrypoint in this repo discards `sys.argv` and a `-k` filter matching nothing exits 0. | high | Four defences, one per recurrence, and **one of them does not reach this plan** — stated because pass 4 measured it. Issue 1.8's wrapper (pass 1); the two-branch rule for failure-code criteria (pass 2); SC0 plus Issue 1.10 (pass 3); and the **Verification-harness capability gate** (pass 4). Issue 1.10 is the one that does not reach this plan's own close: `recheck-criteria` runs from the INSTALLED skill, so an engine fix in the working tree is inert at close, and installing mid-execution is forbidden. **SC0 is a floor, not a backstop** — once the files exist it always holds, guaranteeing `evaluated >= 1`, which is itself the arithmetic that converts INCONCLUSIVE into PASS. The gate is the defence that actually applies, because it halts on an exit code outside the verdict arithmetic entirely. |
| R8 | **The `description` check's `research-*` types have no status escape hatch** — `bundle_status` is `None`, so a `W` there is permanent and never demoted. | low | Issue 3.3 scopes them out explicitly rather than accepting a permanent warning by omission. |
| R11 | **This plan edits the very skills it is executing under**, and one of its own fixes therefore cannot protect it. | med | Per AGENTS.md there is no self-modification hazard mid-run — prose and scripts resolve to the installed copy. But the same property makes **Issue 1.10's `recheck-criteria` fix inert for this plan's own close**, since installing mid-execution is forbidden and deploy happens at land-the-plane, after validation. The Verification-harness gate is sited precisely to cover that window. The successor plan inherits the fixed engine and does not have this gap. |
| R12 | **The plan grew under review rather than shrinking** — 46 -> 51 -> 54 issues across two cycles, each pass adding issues to close a hole the previous pass's issues opened. | med | Resolved by splitting (D-17): 35 issues remain, scoped to the Motivation. The regress itself is recorded as the reason, so a future reader sees that the split was evidence-driven rather than cosmetic. |

## Success Criteria

> **Verification convention.** `check-pytest-ran.sh` (Issue 1.8) asserts the named test **exists and
> ran** — grep for its `def`, then invoke pytest with the target's own PEP 723 dependencies forwarded,
> and require a non-zero passed count.
>
> **Three rules, each written because a review pass measured its violation:**
>
> 1. It is NOT true that pytest exits 0 on a selector matching nothing — measured, module-form
>    `pytest -k <no-match>` exits **5**, and `CHANGE-VALIDATION.md:17` already recorded that. The
>    vacuity exists **only** in the direct-file form `uv run <test_file.py> -k …`, whose entrypoints
>    discard `sys.argv`. The repo's recipe never uses that form.
> 2. **No criterion may expect a non-zero exit from a script that does not yet exist** — `uv run
>    <missing>.py` itself exits 2, which silently satisfied two criteria in an earlier draft.
>    Criteria expecting a specific failure code assert a *pair* of exits differ.
> 3. **A missing instrument must read FALSE, never inconclusive.** `recheck-criteria` counts
>    `inconclusive` rows in neither `failed` nor `evaluated`, so unjudged criteria are invisible to
>    its verdict. SC0 exists to make that state fail, and Issue 0.13 fixes the engine.

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC0 | Every instrument **this plan creates** — all ten — is **present and executable**. (SC11b's `_shared/sync.py` and SC26's `plan_manager.py` are also invoked by criteria but pre-exist, so they are out of this check's scope.) **Measured, and this is the third form of this criterion:** `test -x` alone misses a bad shebang; `bash -n` alone returns 0 for a non-executable file *and* for a bad shebang, and returns 127 for a missing one, which `plan_manager.py:2916` maps to `inconclusive` — invisible to the verdict. So pass 4's `bash -n` form was a **net regression** over pass 3's `test -x`, which at least caught the missing case and blocked. **Residual, stated rather than closed a fifth time: a bad shebang passes this check** and surfaces only as a 126 at run time; `harness-selftest.sh` (SC35) is what actually executes each script. Two further residuals, stated rather than discovered later: a **directory** at one of the ten paths satisfies `-x`, and three of the ten are invoked via `uv run`, which does not require the x-bit — so this criterion imposes a `chmod +x` obligation that Issues 1.9 and 3.1 must honour. **SC0 is a floor, not a backstop** — once the files exist it always holds, guaranteeing `evaluated >= 1`, which is why the capability gate rather than SC0 is the load-bearing defence. | `test -x scripts/checks/check-pytest-ran.sh -a -x scripts/checks/check-recipe-row.sh -a -x scripts/checks/check-reindex-exit-contract.sh -a -x scripts/checks/check-fixture-carveout.sh -a -x scripts/checks/check-closeout-can-fail.sh -a -x scripts/checks/check-drift-driver-contract.sh -a -x scripts/checks/harness-selftest.sh -a -x scripts/checks/check_okf_index_drift.py -a -x scripts/checks/check-req-coverage.py -a -x scripts/checks/check-description-coverage.py` → exit 0 | 1.8, 1.9, 3.1 |
| SC36 | An unjudged class-A criterion blocks completion instead of vanishing from the verdict. | `scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_recheck_criteria.py unjudged_class_a_blocks` → exit 0 | 1.10, 1.8 |
| SC35 | Each harness script returns non-zero on a deliberately broken input — the control distinguishing "correct" from "merely present". **and the selftest reports how many scripts it checked** (`--require 9`, covering ALL instruments — an earlier draft said 8, which excluded `check-pytest-ran.sh`, the busiest of them: **6 of 22 criteria invoke it** (SC4, SC7, SC8, SC10b, SC28, SC36). A seventh, SC0, only `test -x`'s its path — counting presence would add the same +1 to all ten instruments and make "busiest" vacuous, and `check_okf_index_drift.py`), so a selftest covering 2 of 10 is distinguishable from one covering 10 — the `--min-roots` pattern this plan invented for Issue 3.1 and had not applied to itself. | `scripts/checks/harness-selftest.sh --require 9` → exit 0 | 1.8, 1.9, 3.1 |
| SC1 | Every Epic 1-4 issue **either** names the `REQ-*` it implements, **or** `depends-on` — **directly or transitively** — an Epic 0 issue that adds one, **or** is explicitly marked a bug fix to a shipped REQ. The transitive reading is load-bearing and is stated so `check-req-coverage.py` implements a criterion rather than defining one: measured over the extracted DAG, **13 of 24** non-Epic-0 issues carry a direct Epic-0 dependency and **23 of 24** carry a transitive one, the sole exclusion being the declared bug-fix carve-out. The literal direct-only reading would make this criterion FALSE by construction. | `uv run scripts/checks/check-req-coverage.py docs/plans/plan-056-james-dixson-473dba` → exit 0 | 0.1, 0.2, 0.3, 0.4, 0.8, 0.9, 0.10, 0.11, 0.12, 0.13, 0.14, 1.9 |
| SC2 | `reindex --check` returns *different* exit codes for a nonexistent path and a real index-less bundle. | `scripts/checks/check-reindex-exit-contract.sh` → exit 0 | 1.1, 1.9 |
| SC3 | The corpus driver returns a *different* exit for a nonexistent enumerated root than for a clean corpus, so a mistyped path can never be read as clean. | `scripts/checks/check-drift-driver-contract.sh` → exit 0 | 3.1, 1.9 |
| SC4 | `--check` no longer reports a marker-imbalanced index as clean. | `scripts/checks/check-pytest-ran.sh _shared/test_okf.py marker_imbalance_check_mode` → exit 0 | 1.1, 1.8 |
| SC5 | The `description` check reports zero findings on plan-056's own nested artifacts — the producers stamped what the check requires. | `uv run scripts/checks/check-description-coverage.py docs/plans/plan-056-james-dixson-473dba` → exit 0 | 2.1, 2.2, 2.6, 3.3, 1.9 |
| SC6 | `audit-close` on plan-053 reports no `okf:` finding under a fixture path, while still reporting on non-fixture paths. | `scripts/checks/check-fixture-carveout.sh docs/plans/plan-053-james-dixson-4015d3` → exit 0 | 1.3, 1.5, 1.9 |
| SC7 | The exclusion concept is member-declared and non-empty: removing §3b restores the findings. | `scripts/checks/check-pytest-ran.sh _shared/test_okf.py exclude_globs_declared` → exit 0 | 1.2, 1.4, 1.5, 1.8 |
| SC8 | The overlap invariant holds and is non-vacuous — both exclusion lists carry at least two entries. | `scripts/checks/check-pytest-ran.sh _shared/test_okf.py overlap_invariant` → exit 0 | 1.5, 1.8 |
| SC9 | `doc_lint` can still FAIL a completed bundle: a RED fixture carrying a close-out violation at `status: complete` produces at least one error. | `scripts/checks/check-closeout-can-fail.sh` → exit 0 | 0.2, 1.6, 1.9 |
| SC10 | The index drift gate reports the corpus clean, having actually enumerated it. | `uv run scripts/checks/check_okf_index_drift.py --min-roots 30` → exit 0 | 2.3, 3.1, 3.4 |
| SC10b | `index-add` is a registered public CLI verb, discoverable by the enumeration test rather than only by `--help` (which exits 0 for any parser). | `scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_cli_enumeration.py index_add_verb` → exit 0 | 2.5, 1.8 |
| SC11 | The gate is wired, not merely written: the `okf-index-drift` row is present in the manifest AND appears in a FULL-tier run's JSON. A bare full-tier run cannot show this — it already exits 0 today, before the row exists. | `scripts/checks/check-recipe-row.sh okf-index-drift` → exit 0 | 3.2, 1.9 |
| SC11c | The two test files this plan creates are wired into the validation recipe, so their criteria are re-run on every land rather than holding once at close. | `scripts/checks/check-recipe-row.sh test_recheck_criteria && scripts/checks/check-recipe-row.sh test_index_members` → exit 0 | 3.2a, 1.9 |
| SC11b | `okf.py`'s four vendored copies are byte-identical to `_shared/`. **This is an invariant, not a progress marker** — it holds on HEAD today and must still hold after Epic 1 edits `okf.py`; its job is to go FALSE if Issue 1.7 is skipped, which `recheck-criteria` cannot show in advance. | `uv run _shared/sync.py --check` → exit 0 | 1.7 |
| SC25 | The boundary document exists and each layer references the other, closing the zero-cross-reference gap. | manual: the boundary doc is cited from both `yf-okf/SKILL.md` and the doc_lint spec | 4.1 |
| SC32 | Every defect this plan found but did not fix is filed, not merely narrated. | manual: each Issue 4.2 item has a bead id recorded in the reconcile notes | 4.2 |
| SC26 | Every upstream row reaches the end state its disposition names. | `uv run skills/yf-plan/scripts/plan_manager.py verify-reconcile docs/plans/plan-056-james-dixson-473dba --json` → exit 0 | 4.3 |
| SC27 | No shipped spec cites a corpus figure the corpus contradicts. | manual: the `0 of 423` claims are replaced by a re-measured figure carrying its measurement date | 0.8, 0.12 |
| SC28 | Adding a member to a grouped index no longer reparents the previous group's children. | `scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_index_members.py ensure_index_lists_member_indentation` → exit 0 | 2.4, 1.8 |
