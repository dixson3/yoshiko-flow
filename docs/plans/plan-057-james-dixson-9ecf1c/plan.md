---
type: Plan
okf_spec: OKF-PLAN
id: plan-057-james-dixson-9ecf1c
author: james-dixson
created: '2026-08-28'
status: drafting
---
# Plan: OKF part 2: deepen the root index, ship yf-okf-hygiene with the legacy backfill, and realign OKF-BASELINE to the relocated upstream

**ID:** plan-057-james-dixson-9ecf1c
**Author:** james-dixson
**Created:** 2026-08-28
**Status:** drafting

## Objective
OKF part 2: deepen the root index, ship yf-okf-hygiene with the legacy backfill, and realign OKF-BASELINE to the relocated upstream

## Motivation

**This plan is the deferred half of plan-056**, split at that plan's Epic 3/4 seam on the
recommendation of its red-team pass 3 and the operator's decision (plan-056 D-17).

plan-056 grew 46 -> 51 -> 54 issues across two review cycles, each pass adding issues to close a hole
the previous pass's issues opened. Its DAG had **zero backward cross-epic edges**, so the split was
mechanically legal, and its Epics 0-3 close its entire stated Motivation on their own: making the
structural validation that already exists able to fail. What is left over is three bodies of work that
are real but not part of that gap.

**1. The root index is 19.9% covered and 57% boilerplate.** Measured across 28 indexed bundles: 210 of
1053 files are named by an index entry, and coverage is inversely proportional to bundle size —
plan-054 names **4%** of its 135 files. Of 276 entries, 257 carry a description but only **127 are
distinct**; 142 are byte-identical strings reused across bundles, and 17 of 28 bundles carry no
bundle-specific description text at all. On three sampled bundles a plain `ls -R` conveyed more than
the index did.

**2. Half the corpus was never migrated.** 30 of 59 bundles here still carry `README.md` and no
`index.md` — purely a function of age, adopted at plan-031 and never backfilled. And `okf migrate`,
the tool that would do it, **introduces a new hard audit failure on 30 of 30**: it adds `plan.md`
frontmatter, which flips `okf_missing_level` from `warn` to `fail`, while leaving legacy prose in
`index.md` that `reindex --write` cannot repair. The correct transform is three steps and is currently
**unreachable from any command line**.

**3. The baseline pins a document that has moved and mutated.** OKF now lives at
`GoogleCloudPlatform/open-knowledge-format`, and the `okf/` directory we cite carries an upstream
notice to stop building against it. The spec has since changed **without a version bump** — still
`Version 0.2`, now mandating ISO 8601 offsets. Corpus impact is zero, but `okf_spec: 0.2` no longer
identifies a fixed document, which defeats the plan-029 R3 isolation strategy that assumed a version
string is a pin. Separately, OKF v0.2 is **silent on how a consumer identifies a bundle root**, and the
gap is circular: the only in-band marker is the one key a wrongly-rooted consumer rejects.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| #140 | yf-okf: enforce OKF structure below the bundle root | partial | The index-depth half, carried from plan-056 when it split. Root-tier drift enforcement shipped there. Stays open either way: REQ-OKF-CHK-002 has no other tracker home. | 0.1, 3.5 |
| #170 | OKF consumer round-trip fidelity is unverified | partial | Carried from plan-056. `partial` on TWO grounds: the WRITE half cannot be exercised at all (okf-lint's `--fix` hard-delegates to bookpipe-internal generators and crashes on a yf tree), and the READ half is only partially evidenced — 1285 of 1383 concept documents were never inspected. What is discharged is the root-framing characterisation, not corpus conformance. | 3.2, 3.5 |
| #171 | yf-okf: nested index.md generation | partial | The `description:` producer contract shipped in plan-056; the index-depth consumption of it is this plan's Epic 1. | 0.1, 1.2, 3.5 |
| #168 | yf-okf: projection delivery mode | exclude | Trigger not fired — no consumer anywhere on this machine. | |
| #169 | OKF conformance gate for yf-research and yf-incubator | deferred | Parked. Measured counter-evidence: yf-research's UNGATED indexes are the corpus's best while yf-plan's GATED ones are 57% boilerplate. | |
| #192 | Evaluate a structure-first plan DSL | deferred | If ever pursued, index generation becomes a by-product — a further reason D-1 deepens the root index rather than building nested ones. | |
| #189 | Six shipped scripts have no tests at all | partial | Taken as a CONSTRAINT (D-8): `okf_hygiene.py` ships with `test_okf_hygiene.py` and a recipe row, so it does not become a seventh. | 2.8, 2.10 |

## Investigation Findings

**No new investigation was run for this plan.** It inherits plan-056's six experiments verbatim —
`findings/exp-001..006*.md` are copied into this bundle so it reads cold — and the decisions below are
carried from plan-056 with their original evidence. Re-measure before citing: every figure was taken on
2026-08-28.

| # | Headline (inherited) |
| :-- | :-- |
| [EXP-001](findings/exp-001-reindex-drift-gate.md) | The drift gate's producer cause and exit contract. Relevant here because Epic 1 **widens** what counts as drift against a gate plan-056 makes live. |
| [EXP-002](findings/exp-002-description-producer-contract.md) | `description:` is at 51/51 on the agent side since plan-052 and 1% on the code side. plan-056 fixes the producers; this plan consumes the key. |
| [EXP-003](findings/exp-003-deepen-root-index.md) | **Zero engine change is needed to ACCEPT nested entries** — 5 of 6 hand-nested bundles round-trip byte-identically. Cost is entirely on the description path. Rule D bounds every bundle at 30 entries. |
| [EXP-004](findings/exp-004-layer-ownership-boundary.md) | The layer overlap. Its boundary document ships in plan-056; this plan must not re-diverge from it. |
| [EXP-005](findings/exp-005-backfill-and-hygiene-skill.md) | **`okf migrate` makes the audit strictly worse on 30/30.** The correct backfill is three steps and unreachable from any CLI. The wider corpus is **514 bundles / 41 repos**, and `_index.md` (47%) dominates `README.md` (26%). |
| [EXP-006](findings/exp-006-round-trip-and-repin.md) | **Only 32 of 1563 okf-lint findings are the genuine disagreement**, all flipping on root framing. OKF v0.2 is silent on bundle-root identification. **Only ~100 of 1383 concepts were inspected** — no B1/B2 pass may be inferred. |

### Decisions carried from plan-056

| # | Decision | Basis |
| :-- | :-- | :-- |
| D-1 | **Do not build nested `index.md`.** Deepen the ROOT index instead. | 6 of 28 bundles already do this by hand and produce the corpus's only irreducible entries; #171's own measurement says 52% of subdirectories would get a valueless listing. |
| D-2 | **Nested `log.md` stays permanently dropped** (plan-046 D-4). | Every `okf.append_log` call site targets the bundle root. |
| D-3 | **`yf-okf-hygiene` owns full OKF health** and absorbs `yf-okf`'s advertised-but-unimplemented `assess` verb rather than adding a fourth name. | Operator decision; `assess` is documented as exactly this and is measured absent from `okf.py`'s CLI. |
| D-4 | **The backfill is `migrate` -> DELETE the renamed index -> REGENERATE the listing.** Never `okf migrate` alone. | Measured: `migrate` alone introduces a new hard `fail` on 30/30, and `reindex --write` cannot repair it. |
| D-5 | **Backfill HALTS on both risk classes** — `hybrid-partial` and objective divergence. | 8 of 30 bundles need explicit resolution: plan-030 strands 10 log bullets; 7 READMEs' objective differs from `plan.md`'s H1, richer in plan-010/013. |
| D-6 | **Ship the tool AND backfill this repo's legacy bundles, AND support `_index.md`.** | Operator decision. A half-done backfill is strictly worse than none, because `okf_missing_level` flips on `okf_native`. |
| D-7 | Executing the backfill across the other 40 repos is **out of scope**, but the skill must be able to run there. | The wider corpus is 514 bundles / 41 repos. |
| D-8 | **`yf-okf-hygiene` ships with tests.** | #189: six shipped scripts already have none. |
| D-9 | **File nothing upstream.** Track the OKF repo read-only. | Operator decision. |
| D-10 | **Re-pin `OKF-BASELINE.md`** and record that "v0.2" is a mutable label. | Upstream announced the snapshot frozen and changed v0.2 in place with no version bump. **The old copy is NOT observably stale** — md5-identical, and it got that change 18 hours first; the re-pin rests on stated intent plus the unversioned mutation. |
| D-11 | **Pin by CONTENT HASH, not version label.** | A label-only pin would have detected nothing; a content hash fires on the actual event. |
| D-12 | **Do not add a bundle-root marker file.** | A unilateral extension to a format whose selling point is "no required tooling", that no consumer would look for. |

## Approach

**Four epics.** Epic 0 lands the SPEC amendments; Epics 1-3 are the three bodies of work the Motivation
names, and they are largely independent of one another — only Epic 1 has a hard ordering constraint,
because it widens what counts as drift against a gate plan-056 makes live.

**This plan has one hard external precondition: plan-056 must be complete.** Three of its outputs are
load-bearing here — the `description:` producer contract (Epic 1 consumes the key), the member-declared
path-exclusion mechanism (Epic 2's root detection reuses it), and the layer boundary document (nothing
here may re-diverge from it). That precondition is a capability gate rather than prose, so it is checked
rather than assumed.

**What this plan deliberately does not do.** It does not build nested `index.md` (D-1), does not
re-open nested `log.md` (D-2), does not execute the backfill outside this repository (D-7), does not add
a bundle-root marker file (D-12), and files nothing upstream to the OKF project (D-9).

## Epics
### Epic 0: SPEC amendments (SPEC-first)
- Issue 0.1 (`REQ-OKF-012`): Add a requirement for root-index depth — the selection rule, the flat entry format, the description fallback chain, and the inverse drift signal.
- Issue 0.2 (`REQ-OKFH-001`..`REQ-OKFH-010`): Add the requirement family for the `yf-okf-hygiene` skill — verbs, exit contract, halt classes, the crash-recovery journal, and the record/restore round trip.
- Issue 0.3 (`REQ-OKF-033`): Add a requirement for the content-hash baseline pin and its read-only drift detector.
- Issue 0.5 (`REQ-CLI-018` extended): Extend the verification-harness requirement plan-056 establishes to this plan's four additional instruments, so no criterion is adjudicated by an unowned script.
- Issue 0.4 (`REQ-OKF-034`): Add a requirement recording that OKF v0.2 specifies no bundle-root identification procedure, and declaring the yf layer's resolution.

### Epic 1: Root-index depth
- Issue 1.0: Author this plan's **four additional harness scripts** — `check-index-boilerplate-ratio.py`, `check-baseline-pin-contract.sh`, `check-skill-classified.sh`, `check-backfill-audit-delta.py` — plus its `harness-selftest.sh` entry. plan-056 owns the shared six via its Issue 1.9; these four are new here and, at pass 4, had no creating issue in either plan. Each must be two-branch where it asserts a failure code, and must fail loudly when it inspected nothing. Derive the list mechanically from the Verification column rather than by hand — that hand-assembly is exactly what pass 2 caught in the predecessor.
  - depends-on: 0.5
- Issue 1.1: Give `_listing_members` a selection parameter implementing rule D — enumerate a subdirectory's files iff it holds <=10, else emit a bare directory bullet. K is a constant, not a config knob. Measured yield: 463 entries, median 14.5, **max 30 regardless of bundle size**.
  - depends-on: 0.1
- Issue 1.2: Make `render_index` and `add_index_entry` read `description:` from the linked file, falling back frontmatter -> H1 -> bare, never synthesizing. Measured: `render_index` builds bullets from `iterdir()` and never reads the key today, so deepening needs two changes, not one.
  - depends-on: 1.1
- Issue 1.3: Adopt the flat entry format the research bundles already use — it is OKF v0.2 §8's example shape verbatim, cannot be corrupted by the splice defect, and cannot trip the audit's `^- \[` regex. **Do not touch `reindex_write`'s preserve-and-append contract**: that contract is what makes the 6 existing nested bundles migrate for free, measured at 5-of-6 byte-identical.
  - depends-on: 1.2
- Issue 1.4: Add the inverse drift signal — report `missing` for nested files the rule selects but the index omits. Today an unlisted nested file is invisible, so drift is one-directional. **Re-repair the corpus in the same issue**, because 1.1 and 1.4 widen what counts as drift against a gate that is already live.
  - depends-on: 1.3
- Issue 1.5: Decide `assets/**` explicitly — add an `asset` document type or state it is out of contract scope. 45 authored descriptions live there, selected by no schema; leaving it uncovered silently is the class this work exists to close.
  - depends-on: 1.4

### Epic 2: yf-okf-hygiene
- Issue 2.1: Author `skills/yf-okf-hygiene/SKILL.md` and `SPEC.md`, absorbing the advertised-but-unimplemented `assess` verb.
  - depends-on: 0.2
- Issue 2.2: Implement `audit` — read-only bundle discovery and classification into `conformant | legacy-readme | legacy-underscore-index | hybrid-partial | unclassifiable`, exit 0/1/2, never writing.
  - depends-on: 2.1
- Issue 2.3: Implement config-driven root detection with hard exclusions for `.git/**`, `.worktrees/**`, `.claude/worktrees/**`, `.yf/**`, archives, and the fixture trees. **Its default exclusion set must be self-contained** — the yf-plan member file does not exist in the 40 foreign repos D-7 targets, so §3b is an override where present, never a prerequisite. Must find `yf/<slug>/plans/`, which the four known roots miss.
  - depends-on: 2.2
- Issue 2.4: Implement `backfill` as the three-step transform, **crash-recoverable by mechanism**. Recovery keys on a **durable per-bundle journal** — target path plus phase, written and fsynced before the first rename, unlinked after cleanup — not on directory presence. Measured: `os.rename` onto a non-empty directory raises `OSError errno 66`, so the swap is two renames with a window in which the bundle is absent; a table keyed on directory presence alone is not total over the five reachable states and reads "staged, crashed before rename 1" as "done". Stage inside the repo tree, never `$(mktemp -d)` (measured `EXDEV` risk).
  - depends-on: 2.3
- Issue 2.5: Implement the D-5 halt classes — `hybrid-partial` and objective divergence both block and require explicit operator resolution.
  - depends-on: 2.4
- Issue 2.6: Add the `_index.md` route, dispatching by detected member rather than filename. It has exactly **one live in-repo target**, `docs/research/001-okf-compliance-delta`; the 47% figure that motivates it is 227-of-243 in a single foreign repo D-7 bars touching, so beyond that bundle the route is built speculatively.
  - depends-on: 2.4
- Issue 2.7: Implement `reindex` (refusing on a legacy prose index — that is backfill's job) and `restore`, record-driven with a **per-path operation kind**: a modified or deleted tracked file is `git checkout`, but a **created** `index.md`/`log.md` is absent from HEAD and must be unlinked. All 30 depth-1 READMEs are git-tracked, verified per file, which is what makes the git-backed half sound.
  - depends-on: 2.4
- Issue 2.8: Write `test_okf_hygiene.py` with a pure, fixture-driven classification core. Minimum cases: two-variant equivalence; the plan-030 hybrid named for the case; fingerprint invariance; phase-log bullet AND distinct-date equality; `reindex` refusal on legacy prose; objective-divergence halt; root detection; `audit` never writing; migration samples untouched; and **deterministic recovery from all five crash points**, not one.
  - depends-on: 2.5, 2.6, 2.7
- Issue 2.10: Add a `CHANGE-VALIDATION.md` row for `test_okf_hygiene.py` in both tiers, so the suite runs on every land rather than once.
  - depends-on: 2.8
- Issue 2.9: Run `backfill --apply` over this repo's 30 **depth-1** legacy plan bundles plus the one live `_index.md` bundle, 31 in total, resolving each halt explicitly. Depth-1 is load-bearing: an unscoped root reaches 39 READMEs, 9 of them frozen fixtures.
  - depends-on: 2.8

### Epic 3: Baseline realignment
- Issue 3.1: Re-pin `OKF-BASELINE.md` and `yf-okf/SPEC.md:13` to the relocated repo with a content-hash pin. Only **2 lines of live prose** are normative; the other ~144 citations are immutable provenance and must not be rewritten.
  - depends-on: 0.3
- Issue 3.1a: Add the baseline-pin drift detector as a FULL-tier row — `curl` plus `sha256sum` against `okf_baseline_sha256`, INCONCLUSIVE on network failure, reporting only. Files nothing.
  - depends-on: 3.1
- Issue 3.2: Add the "What OKF does not say: locating a bundle root" section to `OKF-BASELINE.md`, recording the silence and its circularity as measured fact — **and the coverage caveat with it**: okf-lint inspected only ~100 of 1383 concept documents, so nothing here may be read as evidence the corpus passes OKF's B1/B2 rules.
  - depends-on: 0.4, 3.1
- Issue 3.3: Add the corresponding decision to `OKF-YF-EXTENSIONS.md` — a yf artifact folder is a bundle root, and a consumer that roots elsewhere reports false violations: an upstream gap, not a yf defect.
  - depends-on: 3.2
- Issue 3.4: Reconcile `yf-okf` against the new skill — remove the `assess` verb it advertises at four places but does not implement, and write the **trigger/description boundary** between the two OKF skills. Two skills with adjacent names is exactly the disambiguation problem this repo's always-loaded rules are about.
  - depends-on: 2.1, 3.3
- Issue 3.5: Reconcile upstream dispositions — comment on #140, #170, #171 and #189 with what shipped and what remains. Run `verify-reconcile` as an approval preflight, not only at close.
  - depends-on: 3.4, 2.9, 1.5
  - resolves-upstream: #140 (partial), #170 (partial), #171 (partial), #189 (partial)

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Predecessor complete
- Type: auto
- Condition: plan-056 is complete, so the `description:` producer contract, the member-declared exclusion mechanism and the layer boundary document all exist.
- Test: grep -q '^status: complete' docs/plans/plan-056-james-dixson-473dba/plan.md
- Blocks: 1.1, 2.3
- Instructions: The predecessor's outputs are load-bearing here — Epic 1 consumes the `description:` key its producers stamp, and Epic 2's root detection reuses its exclusion mechanism. If the predecessor is abandoned rather than completed, this plan must be re-scoped, not force-started.

### Capability Gate: Backfill authorization
- Type: human
- Condition: The operator authorizes `backfill --apply` over 31 bundles, having seen the dry-run plan and the resolved halt list.
- Test: none
- Instructions: This is a CONSENT gate — no command can establish it, which is why `Test:` is the `none` sentinel (any non-sentinel value classifies as `executable` and would be run as bash). Run the backfill dry-run scoped to depth 2, confirm it names 31 bundles and not 40, review every `hybrid-partial` and objective-divergence halt, then authorize explicitly. **Read the safety evidence precisely:** the content fingerprint covers `plan.md` only and excludes every file the backfill mutates, so the real guarantees are the separate phase-log equality and audit-delta checks.
- Blocks: 2.9

### Capability Gate: Upstream network reachable
- Type: auto
- Condition: The live OKF SPEC.md is fetchable, so the content hash can be computed against real upstream bytes.
- Test: curl -sfI https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md > /dev/null
- Blocks: 3.1
- Instructions: Requires network access to raw.githubusercontent.com. The gate's evidence is the `curl` in `Test:` alone — nothing it blocks produces it. The read-only drift detector is deliberately left unblocked, since it ships either way and an offline run exercises its INCONCLUSIVE path.

### Capability Gate: Verification harness ready
- Type: auto
- Condition: Every harness script exists, is syntactically runnable, and returns non-zero on its RED fixture.
- Test: scripts/checks/harness-selftest.sh --require 12
- Blocks: epic:2
- Instructions: Carried from plan-056, where four consecutive red-team passes found the criteria layer vacuous in four different shapes. A gate halts on an exit code outside `recheck-criteria`'s verdict arithmetic, which is why it — not a criterion — is the load-bearing defence. Evidence is produced by Issue 1.0, which the gate does not block.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **Epic 1 re-arms the drift gate plan-056 made live.** 1.1 and 1.4 widen what counts as drift against a running gate, so the corpus goes red mid-epic. | high | Issue 1.4 re-repairs the corpus in the same issue that widens the signal, and SC7 measures the corpus clean afterwards. The ordering is a `depends-on` chain, not prose. |
| R2 | **A half-done backfill is strictly worse than none** — `okf_missing_level` flips to `fail` the moment `plan.md` gains frontmatter, so an interrupted run leaves bundles failing an audit they previously passed. | high | Recovery keys on a durable per-bundle journal fsynced before the first rename, not on directory presence — measured, `os.rename` onto a non-empty dir raises errno 66, so the swap is two renames and a presence-keyed table is not total over the five reachable states. SC11 asserts deterministic recovery from all five crash points. |
| R3 | **The content fingerprint does not cover what the backfill moves.** It covers `plan.md` only, excludes `README.md`/`index.md`/`log.md`, and excludes the header preamble where `migrate` adds frontmatter — so "30/30 byte-identical" is near-tautological and blind to the phase log, the one measured data-loss mode. | high | Fingerprint invariance, phase-log bullet AND distinct-date equality, and per-bundle audit delta are **three separate** fail-closed preconditions (SC9, SC10, SC12). The gate's Instructions say so, because that is what an operator reads before authorizing. |
| R4 | **Widening the index without descriptions makes the boilerplate ratio worse**, adding ~200 bare entries to a corpus already 142-of-257 repeated. | med | Epic 1 depends on plan-056's `description:` contract via the predecessor gate; 1.2's fallback chain never synthesizes; SC3 measures the ratio rather than the entry count. |
| R5 | **The `_index.md` route has one live in-repo target.** Its 47% justification is 227-of-243 in a repo D-7 bars touching, so it is largely built against self-authored fixtures. | med | Issue 2.6 states this plainly rather than resting on the 47% figure; SC13 exercises the route against the one real target, and the risk of over-building is accepted knowingly rather than discovered later. |
| R6 | **The three-step transform was measured at n=1** (plan-020), and the 30/30 and 29/30 figures were measured over `migrate` alone — the transform D-4 rejects. | med | SC9/SC10 are the generalisation test over all 31 bundles, not a confirmation of inherited evidence. The n=1 provenance is recorded in Issue 2.4 so no reader mistakes it for a corpus result. |
| R7 | **Adopting the flat index format could reformat the 3 grouped bundles.** | med | Issue 1.3 preserves `reindex_write`'s preserve-and-append contract, measured at zero clobber on 5 of 6 nested bundles; SC5 asserts it. |
| R8 | **The content-hash pin fires on cosmetic upstream edits**, training the operator to ignore it. | low | The hash covers `SPEC.md`'s body only, not the repo; the detector reports and proposes a human diff rather than failing a land; the row is FULL-tier, paid once per land. |
| R9 | **Recording the root-framing silence commits yf to a position upstream may later contradict.** | low | D-9 keeps us read-only, so nothing is filed. The BASELINE records the silence as measured fact; the *decision* lives in YF-EXTENSIONS, the layer designed to absorb upstream change. |
| R10 | **This plan edits the skills it executes under.** | low | Per AGENTS.md, prose and scripts resolve to the installed copy, so there is no self-modification hazard mid-run. The one real constraint is no `yf skills install` mid-execution; deploy at land-the-plane. |
| R11 | **Criteria vacuity — the defect that recurred three times in the predecessor's review.** | high | Three rules carried forward verbatim: no bare `-k` filter; no criterion may expect a non-zero exit from a script that does not exist; and a missing instrument must read FALSE, not `inconclusive`. SC0 enforces the third with shell builtins only. plan-056's Issue 1.10 fixes the engine, and the predecessor gate means it is already in place here. |

## Success Criteria

> **Verification convention, inherited from plan-056 and non-negotiable here.** Its red-team found the
> same vacuity three times in three shapes: `-k` filters that are no-ops in this repo's direct-file test
> form; criteria expecting exit 2 that a *missing* script also returns; and unjudged criteria that
> `recheck-criteria` counts in neither bucket, so one green criterion reports `PASS`. Every criterion
> below is written against all three: filtered tests route through `check-pytest-ran.sh`, failure-code
> criteria assert a *pair* of exits differ, and SC0 makes a missing harness read FALSE using builtins
> only.

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC0 | Every instrument this plan's criteria invoke — **including `check-skill-classified.sh`, which an earlier draft omitted** — exists and is syntactically runnable, not merely `+x`. Uses `bash -n` and builtins only. **SC0 is a floor, not a backstop**: once the files exist it always holds, guaranteeing `evaluated >= 1`, which is itself the arithmetic that converts INCONCLUSIVE into PASS. The harness gate is the real defence. | `bash -n scripts/checks/check-pytest-ran.sh && bash -n scripts/checks/check-recipe-row.sh && bash -n scripts/checks/check-baseline-pin-contract.sh && bash -n scripts/checks/check-skill-classified.sh && bash -n scripts/checks/harness-selftest.sh` → exit 0 | 1.0, 2.8 |
| SC0b | Each harness script returns non-zero on a deliberately broken input, and the selftest reports how many it checked. | `scripts/checks/harness-selftest.sh --require 12` → exit 0 | 1.0 |
| SC1 | Every Epic 1-3 issue names the `REQ-*` it implements or is explicitly marked a bug fix. | `uv run scripts/checks/check-req-coverage.py docs/plans/plan-057-james-dixson-9ecf1c` → exit 0 | 0.1, 0.2, 0.3, 0.4, 0.5 |
| SC2 | No bundle's index exceeds the selection rule's bound. | `scripts/checks/check-pytest-ran.sh _shared/test_okf.py selection_rule_bound` → exit 0 | 1.1 |
| SC3 | Deepening the index lowers the share of byte-identical boilerplate entries, against a baseline measured 2026-08-28: 276 entries, 257 described, 127 distinct, **142 repeated**. | `uv run scripts/checks/check-index-boilerplate-ratio.py --baseline 142/257` → exit 0 | 1.2, 1.3 |
| SC4 | The description fallback chain never synthesizes a value. | `scripts/checks/check-pytest-ran.sh _shared/test_okf.py description_fallback_never_synthesizes` → exit 0 | 1.2 |
| SC5 | The 6 existing hand-nested bundles survive regeneration unchanged, as measured at 5-of-6 byte-identical today. | `scripts/checks/check-pytest-ran.sh _shared/test_okf.py preserve_and_append_contract` → exit 0 | 1.3 |
| SC6 | An unlisted nested file the rule selects is reported, not silently tolerated. | `scripts/checks/check-pytest-ran.sh _shared/test_okf.py inverse_drift_signal` → exit 0 | 1.4 |
| SC7 | The corpus is clean after the widening, having actually been enumerated. | `uv run scripts/checks/check_okf_index_drift.py --min-roots 30` → exit 0 | 1.4 |
| SC8 | `assets/**` is covered by a document type or declared out of scope — not silently uncovered. | manual: an `asset` schema exists, or the boundary document states the exclusion and why | 1.5 |
| SC9 | The backfill preserves `plan.md`'s fingerprinted content sections across all 31 bundles. | `scripts/checks/check-pytest-ran.sh skills/yf-okf-hygiene/scripts/test_okf_hygiene.py fingerprint_invariance` → exit 0 | 2.4, 2.9 |
| SC10 | The backfill preserves every phase-log bullet and distinct date — the signal the fingerprint is blind to, and the one plan-030 was measured to lose. | `scripts/checks/check-pytest-ran.sh skills/yf-okf-hygiene/scripts/test_okf_hygiene.py plan030_hybrid_log_preserved` → exit 0 | 2.5, 2.9 |
| SC11 | Recovery is deterministic from **all five** crash points, including "staged, crashed before the first rename", which a presence-keyed table misreads as done. | `scripts/checks/check-pytest-ran.sh skills/yf-okf-hygiene/scripts/test_okf_hygiene.py crash_recovery_all_states` → exit 0 | 2.4, 2.8 |
| SC12 | No backfilled bundle's audit verdict is worse than before the run. | `uv run scripts/checks/check-backfill-audit-delta.py --record backfill.json` → exit 0 | 2.4, 2.9 |
| SC13 | The `_index.md` route is exercised against the one live in-repo target, not only fixtures. | `scripts/checks/check-pytest-ran.sh skills/yf-okf-hygiene/scripts/test_okf_hygiene.py underscore_index_live_target` → exit 0 | 2.6, 2.9 |
| SC14 | `restore` returns a backfilled bundle to its pre-run state, including unlinking files the backfill created — which `git checkout` alone cannot do. | `scripts/checks/check-pytest-ran.sh skills/yf-okf-hygiene/scripts/test_okf_hygiene.py restore_round_trip` → exit 0 | 2.7 |
| SC15 | `audit` never writes, and `reindex` refuses a legacy prose index rather than appending beneath it. | `scripts/checks/check-pytest-ran.sh skills/yf-okf-hygiene/scripts/test_okf_hygiene.py audit_readonly_and_reindex_refusal` → exit 0 | 2.2, 2.7 |
| SC16 | Root detection finds the incubator-analog root the four known roots miss, skips worktrees, and skips the frozen fixture trees — using a self-contained default set that needs no yf-plan-private file. | `scripts/checks/check-pytest-ran.sh skills/yf-okf-hygiene/scripts/test_okf_hygiene.py root_detection_self_contained` → exit 0 | 2.3 |
| SC17 | The whole hygiene suite passes, so the skill does not become a seventh untested script. | `uv run --with pytest python3 -m pytest skills/yf-okf-hygiene/scripts/test_okf_hygiene.py -q` → exit 0 | 2.8 |
| SC18 | The hygiene suite runs on every land, not once — the row is present in the manifest and appears in a FULL-tier run. | `scripts/checks/check-recipe-row.sh okf-hygiene-tests` → exit 0 | 2.10 |
| SC19 | This repo's legacy bundles are conformant after the backfill, and the audit enumerated all 31. | `uv run skills/yf-okf-hygiene/scripts/okf_hygiene.py audit --root docs/plans --maxdepth 2 --min-roots 30 --json` → exit 0 | 2.9 |
| SC19b | The hygiene skill's `SKILL.md` is *selected* by the linter's classifier — asserting the `class` value, not the exit code, since `class: empty` also exits 0. | `scripts/checks/check-skill-classified.sh yf-okf-hygiene` → exit 0 | 2.1 |
| SC20 | The baseline names the live upstream and pins by content hash, not by version label. | manual: `OKF-BASELINE.md` §0 carries `okf_baseline_sha256` and the relocated source URL | 3.1 |
| SC21 | Upstream drift is detected read-only, and a simulated network failure yields a *different* exit from a clean check — so the detector's absence cannot satisfy the criterion. | `scripts/checks/check-baseline-pin-contract.sh` → exit 0 | 3.1a |
| SC22 | The baseline records the root-identification silence as measured fact **with its coverage caveat**, and the decision filling it lives in the extensions layer. | manual: BASELINE carries the silence section and the ~100-of-1383 caveat; YF-EXTENSIONS carries the decision | 3.2, 3.3 |
| SC23 | `yf-okf` no longer advertises a verb it does not implement, and the two OKF skills declare a trigger boundary. | manual: `yf-okf/SKILL.md` no longer offers `assess`; both SKILL.md files name the other in their SKIP-for clause | 3.4 |
| SC24 | Every upstream row reaches the end state its disposition names. | `uv run skills/yf-plan/scripts/plan_manager.py verify-reconcile docs/plans/plan-057-james-dixson-9ecf1c --json` → exit 0 | 3.5 |
