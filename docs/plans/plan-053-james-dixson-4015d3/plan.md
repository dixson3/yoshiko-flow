---
type: Plan
okf_spec: OKF-PLAN
id: plan-053-james-dixson-4015d3
author: james-dixson
created: '2026-08-25'
status: complete
deliverable_class: standard
fingerprint: 36936c6e41e812cf4639ec6161660f729396cf013db935c54d212eeb28f26c71
epic: yf-mol-bh8
---
# Plan: Close the yf-plan execution engine's silent-data-loss and plan-stranding defects (#206, #207, #208, #209, #210, #214)

**ID:** plan-053-james-dixson-4015d3
**Author:** james-dixson
**Created:** 2026-08-25
**Status:** complete
**Deliverable-class:** standard
**Epic:** yf-mol-bh8
**Fingerprint:** 36936c6e41e812cf4639ec6161660f729396cf013db935c54d212eeb28f26c71

## Objective
Close the yf-plan execution engine's silent-data-loss and plan-stranding defects (#206, #207, #208, #209, #210, #214)

Six upstream defects in the yf-plan execution engine. Five of them (#206-#210) share one
property: **they report success while losing or misrepresenting data**, so no configuration of
the existing gates surfaces them. The sixth (#214) is spec hygiene filed alongside them.

The plan fixes each instance AND, where a defect is the second occurrence of a mechanism,
installs a check in front of the failing component rather than patching the instance again.
## Motivation
**Four of these six were found in a different repository.** #206, #207, #208, #209 and #210
all surfaced on a single recovery path in `dixson3/astrospike` `plan-001` — a repo that
consumes the installed skill rather than this one's working tree. That is the finding beneath
the findings: the engine's silent-loss defects are structurally invisible from inside
`yoshiko-flow`, because this is the only repo where `_shared/` paths resolve and the only one
whose corpus the fixtures were built from.

**What each costs.**

| Issue | The silence |
| :-- | :-- |
| #206 | Two natural markdown shapes — an inline-code-only continuation line, and any fenced block under an issue — are dropped **whole** from a bead's `detail`, reporting `unparsed: 0`. `--strict` gates on `unparsed[]`, so **no setting surfaces the loss.** Measured: a bead told an executor to "port the markup from the ys source" and deleted the only statement of where that source is. |
| #210 | `SKILL.md` §6.4 invokes `_shared/pour_fidelity.py`, a path that exists **only in this repo**. The completion fidelity gate — the specific control that would have caught #186/#187 — has never been runnable anywhere else. A halting gate that cannot run has no correct handling: read as failure it blocks a good completion, read as success it passes an unverified one. |
| #207 | `resume-scan` reports `found: true` for an epic that was **burned**. Both `SKILL.md` §5.2 branches then dead-end — Resume resumes against beads that do not exist, New stops and tells the operator to do the pour they were trying to do. Burning a bad molecule is the *documented* remedy for a corrupt pour, so this sits on the recovery path. |
| #208 | `update-status` accepts any string. An out-of-vocabulary status strands the plan (invisible to `parked`, ineligible for `execute`) **and silently relaxes `doc_lint`** — `STATUS_SEVERITY` has no mapping, so findings fall through to their declared severity and the document returns a green that is an artifact of the unrecognised status. |
| #209 | Since #187 a bead's description is the plan's `detail` verbatim, and that prose cites `EXP-001` / `SC8` / `R11` by identifier. Issue beads carry no `plan_dir`, so the executor is told to rely on a measurement it cannot locate. Measured: **21 of 35** issues in one plan, 36 citations — but **14.2% across this repo's 53 bundles** (EXP-006), and this plan's own bundle is a **zero-`detail`** bundle. The remedy is right; the urgency argument does not survive contact with this corpus. |
| #214 | Two different requirements are both numbered `REQ-PLAN-073`, making every citation of it ambiguous — including `SKILL.md` §5.2a's. |

**Who is affected.** Every repo that installs yf-plan. #210 in particular is inert here and
broken everywhere else, which is why it went two instances without detection.
## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #206 | plan_extract.py silently drops detail lines — inline-code-only continuations and fenced blocks | include | CRITICAL. Third instance of the #186/#187 family. **EXP-001 confirmed the mechanism and refuted the line numbers** (stale by ~+43). Split into two issues (D-12); the column-0 guard is load-bearing | 0.1, 2.1, 2.2, 2.3 |
| #210 | pour_fidelity.py is not shipped to the skill dir | include | **Class fix (D-3).** EXP-002 **refuted** the positional-id warning and found a worse, unfiled defect — `--strict` exits 0 on an empty scope, fixed first (D-7). EXP-003 found #210 needs **two** edits: the script has no vendored copy at all | 0.7, 3.1, 3.2, 3.3, 3.5 |
| #209 | Issue beads carry no plan_dir | include | **Both remedies (D-2).** EXP-006 measured that **nothing compares a bead description to plan text**, which is what makes the header cheap — and corrected severity to a **14.2%** corpus mean, not 60% | 0.6, 6.1, 6.2 |
| #207 | resume-scan reports found: true for a BURNED epic | include | **EXP-005 refuted the diagnosis** — `epic_resolves` shipped with plan-044; `SKILL.md` never reads it. Six states, not three; #207's proposed JSON shape rejected (D-10) | 0.5, 4.1, 4.4, 4.5 |
| #208 | update-status accepts out-of-vocabulary statuses silently | include | **Widest remedy (D-1).** EXP-004 disqualified `incomplete` (verdict-vocabulary collision) in favour of `abandoned` (D-9), and found the guardrail edge **vacuous** (D-6). Narrow fail-closed is free; the broad form breaks 31 documents | 0.3, 0.4, 5.1, 5.2, 5.3, 5.4 |
| #214 | REQ-PLAN-073 id collision | include | Spec hygiene. EXP-007: renumber the **roots** requirement to the free `REQ-PLAN-079`, not the stamp — citation counts favour the counter-intuitive side (D-8) | 0.2, 1.6c |
| [#231](https://github.com/dixson3/yoshiko-flow/issues/231) | plan-053-james-dixson-4015d3 execution tracking | tracker | The single coarse tracking issue for this plan-scale effort (AGENTS.md convention). Filed at Issue 7.3 through `/yf-beads-upstream` and stamped onto the epic as `external_ref` (REQ-PLAN-073), which is what makes it an ordinary MAPPED bead rather than the structurally-invisible kind that produced five stale trackers | 7.3 |
| #189 | Six shipped scripts have no tests at all | partial | This plan ships regression fixtures for every script it touches. **EXP-002 measured that `pour_fidelity.py` is NOT among #189's six** — it has tests, though they cannot run outside this repo. That gap is fixed at 3.4; the other five stay open | 3.4, 3.6 |
| #188 | Test suites assert output STRUCTURE and never payload FIDELITY | partial | #206 and #210 are both payload-fidelity defects, worked as instances. The general form stays open. EXP-002 supplies a fresh instance: `pour_fidelity`'s suite asserts structure and never that the join is *right* on lettered ids | 1.2, 1.5 |
## Scoping Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-1 | **#208 takes the widest remedy**: warn on an out-of-vocabulary write, make `doc_lint`'s `STATUS_SEVERITY` fail **closed**, AND add a real status to the vocabulary | Operator decision. The stranding that triggered #208 happened because there was no legal state for "approved but deliberately not executing mid-flight", so an operator invented one. Fixing only the silences leaves that gap. Cost: the vocabulary is a declared `DRIFT-CHECK` authority edge (`e-status-values`), so SPEC, the `SKILL.md` Phase Model line, `STATUS_SEVERITY`, `_is_parked` and the §5.1 execute filter must move **together** — SPEC-first |
| D-2 | **#209 takes both remedies**: stamp `plan_dir` into issue metadata AND prepend a one-line provenance header to each issue description at pour time | Operator decision. They answer different halves: metadata is what a program needs to find the bundle from any bead; the header is what a human or agent reading the bead text needs. The issue author recommended only the header, on the grounds that the biting case is a reader — but that argument does not reach the programmatic case at all |
| D-3 | **#210 takes the class fix**, not the instance: ship `pour_fidelity.py` AND add a mechanical check that every script path referenced in a skill instruction doc resolves under an installed `SKILL_DIR`, wired into `CHANGE-VALIDATION` | Operator decision, and it is plan-052's `RE-002` remedy applied verbatim: *when N successive fixes to one defect are each refuted by the same mechanism, stop iterating on the fix and put a check in front of the failing component.* This is the second instance — plan-050 Issue 7.3 fixed exactly this for `plan_extract.py` and did not close the class |
| D-4 | **Every fix ships a RED fixture observed failing before the fix, and GREEN after** | Not an operator question — it is forced by the defect class. All five of #206-#210 are defects that *report success*, so a fix asserted by reading is a fix asserted by the same faculty that missed the bug. plan-052 measured this directly: six defects found by RUNNING, none by six review passes |
| D-5 | **Fix every `yf-diagram-authoring` unrooted `scripts/render.py` row in this plan** — the count is deliberately not recorded; `ctl-210-script-refs` enumerates | Operator decision. They are genuine breaks of the same class — the script resolves from no cwd but the skill dir. Landing the check with standing suppressions is how a check gets ignored |
| D-6 | **Fix the vacuous `e-status-values` drift edge in this plan** | Operator decision, and it corrects D-1's own rationale. EXP-004 measured the edge as **unable to fail**: scoped to `SKILL.md → agents/*.md`, and no yf-plan agent file carries a status literal, so the target set is empty. This plan is about to make a vocabulary change; doing that without a working guardrail is how the next one drifts silently |
| D-7 | **Fix `pour_fidelity.py`'s empty-scope exit-0 BEFORE shipping it** | Operator decision. EXP-002 measured `--strict` returning 0 on the `no-mapping` population — which is the population #210 justifies the gate by (#186/#187's masked titles are exactly what destroys the title fallback). Shipping first would generalise a silent pass to every adopting repo |
| D-8 | **Renumber the ROOTS requirement to `REQ-PLAN-079`, not the stamp** — decided on the **frozen-record** argument ALONE, against the live-site cost | **EXP-007's live-site figures were WRONG and pass-1 C5 refuted them**: the finding conflated the repo-root `SPEC.md` with `skills/yf-plan/SPEC.md`, which carries exactly **one** `REQ-PLAN-073` line. Re-measured **repo-wide**: the roots meaning is cited in **six** files (the repo-root `SPEC.md`, `skills/yf-plan/SPEC.md`, `plan_manager.py`, `test_config_tiers.py`, `spec/data.md`, `test-harness/smoke.sh`) against the stamp meaning's four. **No count literal is recorded here** — the figure moved three times across three passes (3, then 12, then 14, measured 15 at pass 3), and a drifting literal in a decision record is the same moving-fact defect as #221. `ctl-214-id-collision` enumerates; this row does not. Live cost points the **opposite** way from EXP-007's claim, and the decision now rests on one argument only: plan bundles are **records that must never be rewritten**, so whichever meaning is retired strands its citations *permanently and unfixably*, and the stamp meaning has **8** such records against roots' **1**. A one-time mechanical edit across six files is preferred to eight permanently-wrong records. `REQ-PLAN-079` is confirmed unallocated |
| D-9 | **The new status is `abandoned`, NOT `incomplete`** | EXP-004. `incomplete` collides with the reviewer agent's verdict vocabulary (`PASS \| INCOMPLETE`), and `doc_lint.py`'s docstring already carries a line written to keep that word out of its namespace. `abandoned` has a direct in-repo precedent: `yf-incubator` ships `parked` and `abandoned` as **distinct** values, exactly this distinction |
| D-10 | **Reject #207's `found:false + stale_pointer` shape; add an `epic_state` enum** | EXP-005. The proposed shape makes `found` assert something false and re-overloads one boolean with two facts whose handling differs — **the #181 defect, third instance, same codebase**. A boolean also cannot express the six measured states. `found` and `epic_resolves` are kept verbatim for back-compat |
| D-11 | **Do NOT re-implement #207's existence check — read the one that already shipped** | EXP-005. `epic_resolves` landed with plan-044 (#143), is specified at REQ-CLI-013 and tested. #207's defect is narrower than filed: `SKILL.md` §5.2 extracts only `found` and never reads it |
| D-12 | **#206 splits into two execution issues** | EXP-001. Shape 1 is a one-token operand change; shape 2 needs a `_fence_indents` helper plus a **load-bearing** column-0 guard. Measured: a naive fence collection swallows a plan-body fence into the last issue's bead description — fixing #206 carelessly introduces a new silent-corruption shape while closing an old one. Two issues so each earns its own RED |
| D-13 | **Title-borne citations are explicitly OUT of scope** | EXP-006. Measured: this repo's four newest bundles carry **zero** non-empty `detail`; citations migrated into issue **titles**, which #209's header does not reach. **plan-053 is itself such a bundle — measured 0 of ALL its issues carrying non-empty `detail`** (pass-1 C9; the issue count has since moved, so no literal is recorded), so this plan will hit #209 during its own execution and Epic 6 will not reach it. Recorded rather than papered over: the header still makes the bundle findable from a bead, which is a real gain on an otherwise-blank description, but it is not the larger class |

## Investigation Findings

Seven findings in `findings/`. **Five of the six premises the plan was scoped on were revised
by measurement**, and in three cases the correction is what the plan is now built around.

| # | Finding | What it changed |
| :-- | :-- | :-- |
| EXP-001 | #206's fix is clean — the parse/capture split **already exists structurally**, so no restructuring is needed. Corpus delta: **zero** edges, zero counts, 2 of 53 plans gain detail | Split #206 into two issues (D-12); made the column-0 guard a first-class assertion after measuring that a naive fence fix **swallows a plan-body fence into a bead description** |
| EXP-002 | **#210's warning is REFUTED** — the comparator joins metadata-first, title-second, never by id suffix; it reproduces plan-052's 31/31, 49/49 exactly. But `--strict` **exits 0 on an empty scope**, including the `no-mapping` population the gate is justified by | Added Issue 3.1 ahead of the ship (D-7) |
| EXP-003 | The `_shared/` class is **exactly one** live break. The class fix is justified by a **mutation** — re-inserting plan-050's original bug makes the check go red — not by volume. FP surface measured at **zero** | Revealed that #210 needs **two** edits: `pour_fidelity.py` has no vendored copy at all. Pulled the `yf-diagram-authoring` rows in (D-5) |
| EXP-004 | **`e-status-values` is VACUOUS** — it cannot fail. `incomplete` collides with the reviewer's verdict vocabulary. Narrow fail-closed = **0/917**; the naive broad form breaks **31** documents | Corrected D-1's stated rationale; added Issue 5.4 (D-6); chose `abandoned` (D-9). Found a scope **reduction**: the execute filter is prose-only |
| EXP-005 | **#207's diagnosis is REFUTED** — `epic_resolves` shipped with plan-044. The defect is that `SKILL.md` never reads it. There are **six** states, and `foreign` is a measured live hazard: a copied bundle silently resumes another plan's epic | Rejected #207's proposed JSON shape (D-10); dropped the re-implementation (D-11); `clear-epic` grew an `okf.py` delete path and a `metadata_fallback_remains` report |
| EXP-006 | **Nothing in the repo compares a bead description to plan text** — that absence is what makes the header cheap. But corpus severity is **14.2%**, not 60%, and the four newest bundles carry **zero** non-empty `detail` | Scoped title-borne citations out explicitly (D-13); required the plan to cite the mean alongside the peaks (R7) |
| EXP-007 | `REQ-PLAN-073` is confirmed double-allocated; `REQ-PLAN-079` is free. Citation counts favour renumbering the **older** requirement | D-8, against the instinct to move the newer one |

**The through-line:** three separate defects in this plan are the **same conflation** — two
different facts sharing one signal. `doc_lint`'s `not-selected` vs `no-such-path` (#181, fixed),
`resume-scan`'s `found` (#207), and `pour_fidelity`'s exit 1 vs 2 as read by §6.4. The remedy
#181 established — *add a field that names the state; branch on it, never on the flag* — is
applied verbatim in Epic 4 and Epic 3.

## Approach

**Three ordering constraints shape every epic below.**

1. **SPEC-first, mechanically enforced.** Epic 0 lands every `REQ-*` before any implementation.
   This is not merely policy here: `test_cli_enumeration.py` asserts the verb list as a **set
   equality**, so `clear-epic` cannot land without its `spec/cli.md` edit, and `REQ-STATUS-001`
   /`-002` pin the status count at **9** by `grep`. The SPEC edits *fail the build* if skipped.
2. **RED before GREEN** (D-4). Epic 1 builds and observes every control **failing** before any
   fix exists. All five of #206-#210 are defects that *report success*; a fix asserted by
   reading is asserted by the faculty that missed the bug.
3. **`pour_fidelity`'s hole closes before it ships** (D-7), because shipping first generalises
   a silent pass to every adopting repo.

**What the investigation changed.** Two of the six premises were refuted and one guardrail was
found inoperative — so the plan is *cheaper* than scoping assumed in two places and *wider* in
one:

- #210's warning about positional bead ids is **refuted** — the comparator's join is correct
  (EXP-002). But `--strict` exits **0** on an empty scope, which is worse and unfiled.
- #207's "`resume-scan` never checks the tracker" is **refuted** — `epic_resolves` shipped with
  plan-044 (EXP-005). The defect is that `SKILL.md` never reads it, and there are **six**
  states, not three.
- `e-status-values`, the drift edge D-1's rationale named as the guardrail, **cannot fail**
  (EXP-004). Fixing it is now in scope (D-6).

## Epics

### Epic 0: SPEC-first amendments
- Issue 0.1: Amend `REQ-DATA-063` so the **parse/capture split is the requirement**, not an implementation detail: the capture gate reads the **unmasked** line while every parsing branch reads the masked line. State that an **indented** fenced block is continuation collected verbatim minus the opening indent, and that a **column-0** fence is plan body and is not collected. Both facts are load-bearing and both are currently unstated (EXP-001).
  - resolves-upstream: #206 (include)
  - touches: `skills/yf-plan/spec/data.md`
- Issue 0.2: Resolve the `REQ-PLAN-073` collision by renumbering the **roots** requirement to the unallocated `REQ-PLAN-079` (D-8), leaving `stamp-tracker` at `073`. **Every roots-meaning citation across all six files** must move — not the 3 EXP-007 claimed in 1 file (pass-1 C5), and not the 12-in-5 that fix settled on (pass-2 C18). The sixth file is the **repo-root `SPEC.md`**, whose line 919 cites the id in the roots meaning **inside the body of `REQ-YF-PRE-004a`** — a live normative requirement. Scoping the fix to `skills/yf-plan/` was an over-correction of C5, which was itself about conflating the two `SPEC.md` files — a citation left behind points at a retired id and preserves exactly the ambiguity #214 exists to remove. **Two of the six files carry BOTH meanings and need line-precise edits, not a file-scoped rename** (pass-4 C49): the repo-root `SPEC.md` (roots at `:239`/`:919`, **stamp at `:349`**) and `plan_manager.py` (roots ×3, **stamp at `:1461`**). A whole-file substitution corrupts the stamp citations. Add a disambiguation note at `REQ-PLAN-079` recording that plan-037-era records cite this requirement as `073`; **write it so it does not itself match a `^- \*\*REQ-PLAN-073\*\*` definition grep**, or SC15 fails on the note.
  - resolves-upstream: #214 (include)
  - touches: `SPEC.md`, `skills/yf-plan/SPEC.md`, `skills/yf-plan/scripts/plan_manager.py`, `skills/yf-plan/scripts/test_config_tiers.py`, `skills/yf-plan/spec/data.md`, `skills/yf-plan/test-harness/smoke.sh`
- Issue 0.3: Land the status-vocabulary SPEC change for `abandoned` (D-9): `REQ-PLAN-001`, a new abandonment edge sentence in `REQ-PLAN-002`, `REQ-STATUS-001`'s **"Exactly 9"** and its `Verification:`, and `REQ-CLI-024`'s "nine". **`REQ-STATUS-002` is deliberately NOT amended**: it counts `py update-status` **call sites** in `SKILL.md`, not status values, and adding `abandoned` adds no call site — amending it would break a passing grep (pass-2 Missing), and `REQ-DATA-024`'s promotion bullet. Record the contract: IN from any non-`complete` status, OUT by **exactly one edge → `drafting`**, explicitly **no → `complete`**; not execute-eligible; not `parked`; profile `{WARN: REPORT, ERROR: REPORT}`; **deliberately excluded** from all three schema `statuses` lists, stated rather than inherited.
  - depends-on: 0.2
  - resolves-upstream: #208 (include)
  - touches: `skills/yf-plan/SPEC.md`, `skills/yf-plan/spec/phases.md`, `skills/yf-plan/spec/cli.md`, `skills/yf-plan/spec/data.md`
- Issue 0.4: Add two new `REQ-*`: **warn-on-unrecognised-write** (stderr-only, **exit 0** — `test_update_status_gate.py:111` asserts exit 0 for every non-`approved` status and would otherwise flip) and the **narrow** fail-closed `STATUS_SEVERITY` mapping, scoped in the SPEC text as *"a status that is present and unrecognised"* and never *"absent or unrecognised"* (EXP-004).
  - depends-on: 0.3
  - resolves-upstream: #208 (include)
  - touches: `skills/yf-plan/spec/cli.md`, `skills/yf-plan/spec/data.md`
- Issue 0.5: Amend `REQ-CLI-013` to add `epic_state` (six-valued: `none|present|complete|stale|foreign|unknown`), `epic_status` and `epic_plan_dir`, keeping `found` and `epic_resolves` **verbatim** for back-compat (D-10). Amend `REQ-RESUME-001` and `REQ-RESUME-004`, which today specify the branch on `found`. Add a new `REQ-CLI-*` for `clear-epic` and take the `spec/cli.md` enumeration literal from **31 to 32**.
  - resolves-upstream: #207 (include)
  - touches: `skills/yf-plan/spec/cli.md`, `skills/yf-plan/spec/phases.md`
- Issue 0.6: Add a new `REQ-*` stating the issue-bead description is `<provenance header>\n\n<detail>` and that issue metadata carries `plan_dir`, with a verification asserting both. Do **not** amend `REQ-DATA-063` for this — it constrains the extractor, not the pour (EXP-006).
  - resolves-upstream: #209 (include)
  - touches: `skills/yf-plan/spec/data.md`
- Issue 0.7: Add `REQ-YF-EMBED-005` in `SPEC.md` §3.2, modelled on `REQ-YF-EMBED-003`, requiring that every script path referenced in a skill instruction doc resolve under an installed `SKILL_DIR`, enforced by a repo check running in the fast and full tiers.
  - resolves-upstream: #210 (include)
  - touches: `SPEC.md`

### Epic 1: RED observations
- Issue 1.0: **REBUILD the investigation's fixtures into `assets/fixtures/` from the findings' stated specifications** — **the `check_skill_script_refs.py` prototype** (from `exp-003`'s stated predicate), its FP-clean and plan-050-mutant fixtures, and EXP-001's `ctl-206` fixture plan. **Rebuild, not commit** (pass-3 C32): `.worktrees/` and `assets/` are both empty and the findings record no retrievable path, so pass-2's "commit the sandbox artifacts" named artifacts that do not exist — C23 was renamed, not resolved. The plan-050 mutant is **re-derived** from its description, not recovered. No `depends-on`: rebuilding a fixture does not depend on amending a REQ (pass-3 C43).
- Issue 1.1: Adopt plan-050's driven-red harness (`assets/redcheck.sh`, `assets/controls.txt`, `assets/fixtures/`) **and EXTEND it in three measured ways** (pass-1 C1/C2/C4). (a) Add a **red-only** verb `verify-red-all`: assert a **non-zero, non-2** `record-red` for every manifest control — the same wording as the gate Condition, which 1.1(a) previously contradicted and assert **nothing about green** — `verify-all` demands a GREEN `assert-distinguishes` record per control, which by construction cannot exist before the fixes land. (b) Make exit 2 **unrecordable, not merely rejected**: in the adopted harness `_append` runs **before** the rc check, so a `record-red` on an exit-2 fixture prints `RED observed`, returns 0, and leaves an `rc=2` line that `_has_record … nonzero` later matches — **a record-time guard cannot un-write the record** (pass-2 C15). **Move the rc check ahead of `_append`. One branch, mandated — not two offered as equals** (pass-3 C30): the `want=red` alternative leaves `verify-all`, which is SC2's own command, still certifying an rc=2 record. Spiked at pass 3: a fixture exiting 2 makes `record-red` print `RED observed`, `assert-distinguishes` say `DISTINGUISHED`, and `verify-all` return **0**. R3's failure mode otherwise occurs inside the instrument built to prevent it. (c) `verify-red-all` **performs the manifest derivation itself** — not merely a prose confirmation, or pass-10 C93's protection is downgraded from executed to stated (pass-2 C15). Confirm the anchored pattern `grep -oE 'ctl-[0-9]{3}-[a-z-]+'` matches every control this plan names **and nothing else**. Two criteria-only assertions (`check-full-tier-record`, `check-suite-portable`) deliberately live in `assets/checks/` under a `check-` prefix **outside** the `ctl-` namespace and outside `controls.txt`: they are plain criterion checks with no RED/GREEN pair, and naming them `ctl-NNN-` made the derivation count 13 against 11 builders, rendering the gate unsatisfiable while it blocked every fix head (pass-4 C44). **`controls.txt` is authoritative; the derivation must agree with it.** the anchoring is documented load-bearing, so **the controls were renamed to fit the pattern rather than the pattern loosened**, which would reintroduce the `ctl-187` false positive it was anchored against.
  - depends-on: 1.0
- Issue 1.2: `ctl-206-dropped-continuation` — port the sandbox fixture verbatim (EXP-001). It asserts **five** things: both recoveries, both adversarial no-edge cases (a code-span `depends-on:`, a fence containing `- Issue 9.9:`), and the **column-0 fence boundary**. Do **not** reuse `ctl-187`'s blanket `"depends-on:" not in detail` assertion — the adversarial issue legitimately carries that text as prose. Measured RED: exit 1, 6 failures.
  - depends-on: 1.1
- Issue 1.3a: `ctl-207-human-output` — assert the **human** `resume-scan` output names the state on a **fixture bundle whose pointer is stale**. Not against a live plan: that hard-codes another repo's bead state, which is the very defect 3.4 exists to fix.
  - depends-on: 1.1
- Issue 1.3: `ctl-207-epic-state` — the five RED assertions in `test_epic_ref_audit.py` (stale / unknown / foreign / complete / none), which fail today with `KeyError: 'epic_state'`. **Ship a thin `.sh` wrapper in `assets/fixtures/`** — `redcheck.sh` runs manifest controls with `bash "$fx"`, so a bare pytest arm is not runnable by the harness (pass-4 C53). Extend `_write_plan` to dual-write the frontmatter `epic:` key, which it currently omits.
  - depends-on: 1.1
  - touches: `skills/yf-plan/scripts/test_epic_ref_audit.py`
- Issue 1.3b: `ctl-208-vocabulary-sites` — enumerate **every** site in 5.1's `touches` list and the three schema `statuses` lists; assert `abandoned` present at every site and absent from every list. RED today at all of them. **The fixture enumerates and the prose does not** — the old count literal moved twice and survived three deletion attempts (pass-4 C52), so no count is recorded anywhere.
  - depends-on: 1.1
- Issue 1.4: `ctl-208-fail-closed` — a **two-armed** control (EXP-004). Arm 1: a present-but-unrecognised status flips `PASS`→`FAIL`. Arm 2: a **null-`bundle_status`** document is **unchanged**. Without arm 2 the naive one-liner ships and reddens 31 documents plus the repo's own FAST tier. **Ship a thin `.sh` wrapper** — the harness runs `bash "$fx"` (pass-4 C53). **Only arm 1 carries the RED** — arm 2 is invariant across the fix, which `redcheck.sh` defines as a *negative control*, so the RED record does not certify it (pass-1 C12). Arm 2's value is regression protection at 7.1, not evidence at Epic 1.
  - depends-on: 1.1
- Issue 1.5: `ctl-210-empty-scope` — assert `pour_fidelity.py --strict` returns **2**, not 0, on each of the three measured empty-scope paths: the `no-mapping` population, a `--plan` value matching nothing, and a plan dir with no `**Epic:**`.
  - depends-on: 1.1
- Issue 1.6: `ctl-210-script-refs` — the two sandbox fixtures from EXP-003: an FP-clean tree (prose `_shared/` mentions including plan-050's own note verbatim, a non-shell fence, an allow-marked external) asserting exit **0**, and the **plan-050 mutant** re-inserting `uv run _shared/plan_extract.py` asserting exit **1**. The mutant is the control that proves the check would have caught the first instance, which is the whole argument for D-3. **Drive the RED against the checker prototype REBUILT at Issue 1.0**, not against the absence of `scripts/check_skill_script_refs.py` — a fixture that fails because its instrument is missing is an absent-instrument red, which is precisely R3's named pattern (pass-1 C10).
  - depends-on: 1.1
- Issue 1.6a: `ctl-053-spec-order` — port plan-052's control: assert the commit touching `skills/*/spec/**` or `skills/*/SPEC.md` **precedes** the first commit touching any other `skills/**` path, over the merge-parent range `M^1..M^2`. Returns **exit 2 under a squash merge**, never a pass and never a fail — commit order, the whole claim, is unrecoverable there. §6.1 mandates `--no-ff`, so that arm does not fire today. **Its RED comes from a PINNED NEGATIVE FIXTURE** — a throwaway git history in which an implementation commit precedes the SPEC commit — because `1.1 depends-on 0.1` means Epic 0 has already landed on the live tree, so the control is green or inconclusive there and can never be driven red against it (pass-1 C4; plan-052 Issue 0.3 solved the same inversion the same way).
  - depends-on: 1.1
- Issue 1.6b: `ctl-208-edge-scope` — a **non-vacuity** assertion over `DRIFT-CHECK.md`, because there is no drift verifier to invoke: `skills/yf-drift-check/` ships **no `scripts/` directory** and `CHANGE-VALIDATION.md`'s header excludes yf-drift-check as a prose/LLM trigger, not a runnable command (pass-1 C3). The control asserts the property the edge is actually **for**: that a status literal **outside the declared vocabulary**, planted in a file the §6 globs select, is inside the edge's declared target set. **EXP-004's premise is REFUTED and the naive form is unsatisfiable** (pass-2 C17): `agents/coordinator.md:238` and `agents/reconciler.md:64` *do* carry `` `complete` ``, so the target set was never empty — the edge is weak because `complete` **is in** the vocabulary and the subset check therefore passes. And "every selected target contains a status literal" measures **2 of 23** agent files and **3 of 19** SKILL.md, getting *worse* after the widening (**6 of 33**), so it could never reach exit 0. The planted-mutation dispatch remains as a **manual** record in `assets/`, run on a copy in `$(mktemp -d)` rather than in-place-with-revert, so an abort cannot leave a modified `skills/` file behind.
  - depends-on: 1.1
- Issue 1.6c: `ctl-214-id-collision` — assert repo-wide that every surviving `REQ-PLAN-073` site is on an **explicit stamp-meaning allowlist** (file:line, enumerated in the fixture — including `skills/yf-beads-upstream/{SPEC.md,SKILL.md}`, which no other part of the plan names), and that `REQ-PLAN-079` resolves. **The allowlist is required because no grep can decide meaning** (pass-2 C18) — an assertion phrased as "returns only stamp-meaning sites" is unimplementable. RED today across all six files; the fixture's allowlist enumerates the exact site set, so no count literal can drift. The control exists because SC15's earlier `SPEC.md`-only grep would have passed while 11 stale citations survived, and its first revision would have passed while `REQ-YF-PRE-004a` still pointed at the retired id.
  - depends-on: 1.1
- Issue 1.7: `ctl-209-provenance` — assert a poured issue bead's metadata carries all three keys and its description's first line matches `^Plan: \S+ \| Bundle: \S+`, with a blank line before the detail.
  - depends-on: 1.1

### Epic 2: #206 — the extractor drops
- Issue 2.1: Route the capture gate at `plan_extract.py:473` on `raw` rather than the masked `ln`. One token. The branch is capture-only — it calls `_collect_detail(raw, False)` and matches no parsing pattern — so this widens capture and **cannot** widen parsing (EXP-001).
  - depends-on: 0.1, 1.2
  - resolves-upstream: #206 (include)
  - touches: `_shared/plan_extract.py`
- Issue 2.2: Collect **indented** fenced continuations verbatim via a new `_fence_indents` helper, stripping the opening fence's indent so internal indentation survives. **Keep the column-0 guard** — measured, its absence swallows a plan-body fence into the last issue's bead description, introducing a new silent-corruption shape while fixing an old one.
  - depends-on: 2.1
  - resolves-upstream: #206 (include)
  - touches: `_shared/plan_extract.py`
- Issue 2.3: Sync the vendored copy and confirm byte-identity. `_shared/sync.py` enforces it and the FAST tier gates on it, so patching `_shared/` alone fails the on-edit gate.
  - depends-on: 2.2
  - touches: `skills/yf-plan/scripts/plan_extract.py`

### Epic 3: #210 — ship the gate, and the check that closes its class
- Issue 3.1: Fix `pour_fidelity.py`'s empty-scope exit-0 **before shipping** (D-7): return **2** when the `--plan`-scoped result set is empty and when a scoped plan is in the `no-mapping` population, matching the treatment `extractor_unparsed` already receives.
  - depends-on: 1.5
  - resolves-upstream: #210 (include)
  - touches: `_shared/pour_fidelity.py`
- Issue 3.2: Add a `_shared/sync.py` whole-file vendoring entry for `pour_fidelity.py` beside `plan_extract.py`'s and regenerate. **This is the half #210 omits** — the script has no vendored copy at all, so the `SKILL.md` line rewrite alone lands in the checker's `missing-in-repo` class (EXP-003).
  - depends-on: 3.1
  - resolves-upstream: #210 (include)
  - touches: `_shared/sync.py`, `skills/yf-plan/scripts/pour_fidelity.py`
- Issue 3.3: Correct `SKILL.md` §6.4 — the path to `${SKILL_DIR}/scripts/pour_fidelity.py`, **and** the caller's exit handling, which today branches on `-ne 0` and so reports **exit 2 (INCONCLUSIVE) as a divergence**. Stop losing the stderr reason under `--json`.
  - depends-on: 3.2
  - resolves-upstream: #210 (include)
  - touches: `skills/yf-plan/SKILL.md`
- Issue 3.4: Ship `test_pour_fidelity.py` alongside, add the four missing arms (exit 2 on unparsed, no-mapping under `--strict`, `--plan` mismatch, skipped dir), and **decouple it from live `bd` state** — it currently cannot run in any repo but this one, which is the same portability defect #210 is about. Ship `assets/checks/check-suite-portable.sh`, which SC5b reads (pass-5 C54: the `check-` files had no builder after C44 correctly moved them out of the `ctl-` namespace).
  - depends-on: 3.2
  - touches: `_shared/test_pour_fidelity.py`
- Issue 3.5: Build `scripts/check_skill_script_refs.py` — a **repo-level guard**, not a shipped skill script (precedent: `scripts/check_frontmatter.py`; shipping it inside a skill would make it self-referential). Promote the prototype **rebuilt at Issue 1.0** — carrying the 0/1/2 contract, `--json`, an `--all` mode, the `illustrative` carve, and the `<!-- skill-script-refs: allow <why> -->` opt-out marker — into its repo-level home. It is rebuilt from `exp-003`'s stated predicate, never recovered: no worktree survives (pass-4 C48).
  - depends-on: 1.6, 0.7
  - resolves-upstream: #210 (include)
  - touches: `scripts/check_skill_script_refs.py`
- Issue 3.6: Seed `test_check_skill_script_refs.py` from the two Issue 1.6 fixtures, and wire the check into `CHANGE-VALIDATION.md` §1 **fast and full** with §3 globs on `skills/*/{SKILL.md,README.md,agents/*.md,protocols/*.md,reference/*.md,scripts/**}` plus a self-glob — a **deleted** script must fire it. **`README.md` is in scope** (pass-3 C33): the same break lives there, and excluding it would repeat the prototype-convenience scoping error the check exists to catch. **`skills/*/scripts/fixtures/**` is carved OUT explicitly** — it holds corpus fixture documents carrying arbitrary invocations, a false-positive surface EXP-003's "FP measured to zero" never covered (pass-4 C45). Widening §3 pulls `yf-beads-hygiene`, `yf-beads-init` and the three `yf-markdown-*` READMEs into 3.7's fix scope, and **7.2 no longer files them**: the plan must not both fix and defer the same defect.
  - depends-on: 3.5
  - touches: `CHANGE-VALIDATION.md`, `scripts/test_check_skill_script_refs.py`
- Issue 3.7: Fix **every** `yf-diagram-authoring` bare `scripts/render.py` row (D-5) — in `README.md` as well as `SKILL.md` — and apply the opt-out marker to `yf-incubator/SKILL.md:138`, whose external `obsidian-lint` reference is deliberate and guarded in prose. **No count literal**: EXP-003's "8 rows" was an artifact of its prototype scanning exactly four doc kinds, and re-measurement found more in `SKILL.md` *and* a second file entirely (pass-3 C33). The control enumerates; the prose does not. The check lands **green**, not with standing suppressions.
  - depends-on: 3.5
  - touches: `skills/yf-diagram-authoring/SKILL.md`, `skills/yf-diagram-authoring/README.md`, `skills/yf-beads-hygiene/README.md`, `skills/yf-beads-init/README.md`, `skills/yf-markdown-format/README.md`, `skills/yf-markdown-lint/README.md`, `skills/yf-markdown-pdf/README.md`, `skills/yf-incubator/SKILL.md`

### Epic 4: #207 — the resume-scan state model
- Issue 4.1: Derive `epic_state`, `epic_status` and `epic_plan_dir` in `_resume_scan` from signals **already in hand** — do not re-implement the existence check (D-11). Keep `found` and `epic_resolves` unchanged. Guard the latent false negative: `_all_plan_beads` merges two `bd list` calls, so a partial failure yields a gates-only dict in which a healthy epic reports `epic_resolves: false`.
  - depends-on: 1.3, 0.5
  - resolves-upstream: #207 (include)
  - touches: `skills/yf-plan/scripts/plan_manager.py`
- Issue 4.2: Make the **human** `resume-scan` output print the state. Today a dangling ref is invisible on that path — it prints the epic, the descendant count and "no stuck beads", and says nothing about `epic_resolves`.
  - depends-on: 4.1
  - touches: `skills/yf-plan/scripts/plan_manager.py`
- Issue 4.3: Add a delete path to `_shared/okf.py`'s frontmatter writer, which is **merge-only** today, plus a `_clear_plan_fields` helper. This touches an OKF module `_shared/sync.py` declares **four** consumers for — `yf-plan` (this plan's own subject), `yf-research`, `yf-incubator` and `yf-okf` (pass-2 C22). Budget a `_shared/test_okf.py` case and re-run all four.
  - depends-on: 4.1
  - touches: `_shared/okf.py`, `_shared/test_okf.py`
- Issue 4.4: Ship `clear-epic <plan_dir> [-m REASON] [--force] [--json]`: removes the frontmatter `epic:` key and the `**Epic:**` line, **keeps** the `intake: … poured` history bullet and appends a `pointer cleared` bullet, idempotent, **refuses on `present` and `unknown` without `--force`**. It must report `metadata_fallback_remains` — measured, clearing the fields does **not** reopen the pour path if the epic bead survives, because `_resume_scan` falls back to the `metadata.plan_dir` stamp.
  - depends-on: 4.3
  - resolves-upstream: #207 (include)
  - touches: `skills/yf-plan/scripts/plan_manager.py`, `skills/yf-plan/spec/cli.md`
- Issue 4.5: Rewrite `SKILL.md` §5.2's branch to read `epic_state`, six ways, with `unknown` halting as INCONCLUSIVE and `foreign` halting for an operator decision. Never pour on an unreachable tracker: it looks exactly like a burned epic, and guessing "gone" produces the duplicate pour §5.2 exists to prevent.
  - depends-on: 4.4
  - resolves-upstream: #207 (include)
  - touches: `skills/yf-plan/SKILL.md`

### Epic 5: #208 — the status vocabulary
- Issue 5.1: Add `abandoned` across the measured vocabulary change-set — `plan_manager.py`, both `doc_lint.py` copies, the three `document_types/*.toml` schema `statuses` lists (**excluded** deliberately), `SKILL.md`'s Phase Model line and parked nudge, `yf-herdr/SKILL.md`, and the four `web/content/**` lifecycle tables. `list` renders `⏹ ABANDONED`; `_is_parked` stays `approved`-only, because the parked nudge's text is literally *"run /yf-plan execute"*, exactly wrong here.
  - depends-on: 0.3, 0.4, 5.4
  - resolves-upstream: #208 (include)
  - touches: `skills/yf-plan/scripts/plan_manager.py`, `_shared/doc_lint.py`, `_shared/document_types/plan.toml`, `_shared/document_types/upstream-triage.toml`, `_shared/document_types/plan-relations.toml`, `skills/yf-plan/SKILL.md`, `skills/yf-herdr/SKILL.md`, `skills/yf-herdr/SPEC.md`, `web/content/pages/workflows.md`, `web/content/pages/glossary.md`, `web/content/skills/yf-herdr.md`, `web/content/images/phase-model.d2`
- Issue 5.2: Warn on an unrecognised status at write time — **stderr-only, exit 0**, naming the vocabulary and the three known consequences. Add `abandoned` to `test_update_status_gate.py:111`'s status tuple.
  - depends-on: 5.1
  - resolves-upstream: #208 (include)
  - touches: `skills/yf-plan/scripts/plan_manager.py`, `skills/yf-plan/scripts/test_update_status_gate.py`
- Issue 5.3: Implement the **narrow** fail-closed `STATUS_SEVERITY` mapping as a two-line predicate distinguishing `None` from present-but-unrecognised. The obvious one-liner is the **broad** form, measured to break 31 documents and redden the repo's own FAST tier.
  - depends-on: 1.4, 5.1
  - resolves-upstream: #208 (include)
  - touches: `_shared/doc_lint.py`, `_shared/test_doc_lint.py`
- Issue 5.0: Regenerate the `_shared/` vendored copies Epics 4 and 5 perturb — `doc_lint.py`, the three `document_types/*.toml`, and `okf.py` — via `_shared/sync.py`, and confirm byte-identity. **Epic 2 has Issue 2.3 for exactly this reason and Epics 4-5 had no analogue** (pass-2 C21), so the FAST byte-identity gate would have reddened on every one of their `_shared/` edits.
  - depends-on: 5.3, 4.3
  - touches: `_shared/sync.py`, `skills/yf-plan/scripts/doc_lint.py`, `skills/yf-plan/scripts/okf.py`, `skills/yf-research/scripts/okf.py`, `skills/yf-incubator/scripts/okf.py`, `skills/yf-okf/scripts/okf.py`, `skills/yf-plan/scripts/document_types/plan.toml`, `skills/yf-plan/scripts/document_types/upstream-triage.toml`, `skills/yf-plan/scripts/document_types/plan-relations.toml`
- Issue 5.4: Make `e-status-values` non-vacuous (D-6) by **replacing the `agent` target node with the real restatement set** — `skills/*/spec/*.md`, `plan_manager.py`, `_shared/doc_lint.py`, `skills/yf-herdr/**` and `web/content/**`. **One branch, chosen, not two offered as equals** (pass-2 C17): widening §6 alone makes the ratio of targets-carrying-a-status-literal *worse*, so it cannot be what fixes the edge. **This runs BEFORE 5.1, not after** (pass-1 C7): every site it adds exists on the tree today and nothing in the widening depends on `abandoned` existing, so the original ordering was a declared edge rather than a real constraint. Inverted, the vocabulary change becomes the **first divergence the repaired edge sees** — the guardrail doing its job rather than arriving after the risk.
  - depends-on: 1.6b
  - resolves-upstream: #208 (include)
  - touches: `DRIFT-CHECK.md`

### Epic 6: #209 — bead provenance
- Issue 6.1: Add `plan_dir:$d` as a third `jq -nc` key and prepend `Plan: <plan_id> | Bundle: <plan_dir> (repo-relative)` plus **one blank line** at both `bd create` sites in `SKILL.md` §5.2a. ASCII `|` over `·` — the `·` round-trips through `bd` byte-exact, but the description also becomes a GitHub issue body. The blank line is load-bearing: without it a renderer joins the header to any `detail` opening with a list, heading or fence.
  - depends-on: 1.7, 0.6
  - resolves-upstream: #209 (include)
  - touches: `skills/yf-plan/SKILL.md`
- Issue 6.2: Amend the §5.2a prose at `:989` that asserts the verbatim identity. **Add no description-equality check anywhere** — the absence of one is what makes this safe, and adding one would re-create the coupling #209 needs broken.
  - depends-on: 6.1
  - resolves-upstream: #209 (include)
  - touches: `skills/yf-plan/SKILL.md`

### Epic 7: Validate, file, reconcile
- Issue 7.1: Re-observe every Epic-1 control **GREEN** via `redcheck.sh verify-all`, as a record distinct from its RED, and run the FULL tier over the merged tree — **writing its verdict, command and date to `assets/full-tier-record.md`, and shipping `assets/checks/check-full-tier-record.sh` that reads it**. SC16 asserts on that record rather than re-running the tier, because `recheck-criteria`'s 300 s default turns the run into a silent `inconclusive` that completion walks past (pass-3 C38). **Its `depends-on` names every epic leaf** — pass-1 C6 measured six issues (`3.1`-`3.4`, `4.2`, `5.2`) outside 7.1's ancestor set, so SC16 could have discharged while the entire tail of the #210 fix was still open. A validation issue that does not depend on the work it validates is the same silent-green shape this plan exists to close.
  - depends-on: 1.3a, 1.3b, 1.6a, 1.6b, 1.6c, 2.3, 3.3, 3.4, 3.6, 3.7, 4.2, 4.5, 5.0, 5.2, 6.2
- Issue 7.2: File the out-of-scope defects this investigation measured, each with its evidence: the **column-0 paragraph** drop (#206's third family member); the **leading-code-span trailing declaration** gap; `yf-incubator`'s `STATUS_VALUES` dead-code enum (#208's defect one skill over); and **title-borne citations** (D-13). **The `yf-markdown-*` stale README paths are NOT filed here** — 3.6's widened globs and 3.7's `touches` now fix them, and a plan must not both fix and defer the same defect (pass-4 C45).
  - depends-on: 7.1
- Issue 7.3: Reconcile every upstream row to the end state its disposition requires, and file the coarse tracker through `/yf-beads-upstream` so the epic carries it as `external_ref`.
  - depends-on: 7.2
- Issue 7.4: Deploy — `yf self install --from-build --build`, then confirm `yf --version` matches HEAD. **Expect the consent gate to refuse the config half** and re-run with `--allow-permissions-write` if the operator authorizes it; the command as written exits non-zero when a `consent_required` key changes, which is the gate working, not a failure (pass-1 Missing).
  - depends-on: 7.3

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: RED observed before any fix
- Type: auto
- Condition: every control in `assets/controls.txt` has a dated RED record naming a non-zero, **non-2** exit code observed
- Test: bash docs/plans/plan-053-james-dixson-4015d3/assets/redcheck.sh verify-red-all
- Blocks: 2.1, 3.1, 3.5, 4.1, 5.1, 5.4, 6.1
- Instructions: run each control against the unfixed tree via `redcheck.sh record-red`; a control that cannot be observed RED is a control that cannot fail, and must be rewritten rather than recorded. The verb is `verify-red-all`, **not** `verify-all` — the latter additionally demands a GREEN observation per control and so cannot be satisfied before the fixes this gate blocks

### Capability Gate: deploy consent
- Type: human
- Condition: the operator authorizes the local `yf self install` sync
- Test: manual
- Blocks: 7.4
- Instructions: deploy only at land-the-plane, after the work is merged and validated — never mid-execution, since `plan_manager.py` is re-invoked per call and a mid-execution deploy runs new scripts against old prose

### Reconcile Gate
- Type: auto (all execution beads closed)
- Test: bd list --all --include-gates --json | jq -e '[.[]|select(.metadata.plan=="plan-053-james-dixson-4015d3" and .metadata.plan_issue != null and .issue_type!="gate" and ((.title|startswith("Reconcile:"))|not) and .status!="closed")]|length==0'
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **The `okf.py` frontmatter delete path (4.3) touches a module with FOUR declared consumers** — yf-plan, yf-research, yf-incubator, yf-okf. A regression breaks three skills this plan otherwise never tests | high | 4.3 budgets a `_shared/test_okf.py` case and re-runs **all four** consumers' suites (pass-2 C22 measured the earlier "two" as wrong); 5.0 regenerates the vendored copies; the FULL tier at 7.1 covers the merged tree |
| R2 | **`e-status-values` cannot be proven fixed by execution** — there is no runnable drift verifier, so 5.4's repair is asserted by a non-vacuity proxy rather than by a real FAIL on a planted drift | high | `ctl-208-edge-scope` asserts the exact property EXP-004 measured false (empty target set), so it is behavioural, not cosmetic. The planted-mutation dispatch is recorded as an honest **manual** artifact rather than faked into a shape check. **The ordering risk this row previously described is gone** — pass-1 C7 measured the premise false, and 5.4 now runs before 5.1 |
| R3 | **A control is written so it cannot go RED.** plan-050 measured a missing fixture reporting `RED observed` at exit 0 — a silent green inside the instrument built to grade silent greens | high | The gate Test asserts a RED record **naming the exit code observed**, not merely present; 1.1 adopts plan-050's hardened harness rather than a fresh one |
| R4 | **The naive fence fix introduces a new corruption.** Measured: collecting every fenced line swallows a plan-body fence into the last issue's bead description | med | 1.2's control asserts the column-0 boundary explicitly, as one of its five assertions — the guard has a test before it has an implementation |
| R5 | **The naive fail-closed one-liner ships.** Measured: the broad form breaks 31 documents and reddens the repo's own FAST tier | med | 1.4 is two-armed; arm 2 asserts a null-`bundle_status` document is unchanged |
| R6 | **`clear-epic` appears to succeed and does nothing.** Measured: clearing the fields does not reopen the pour path while the epic bead survives | med | 4.4 must report `metadata_fallback_remains`; 4.5's prose tells the operator to stop and treat it as `foreign` |
| R7 | **#209's 60% severity figure does not hold on this corpus** — measured 14.2% mean, and the four newest bundles carry zero non-empty `detail` | med | The Motivation row now cites the mean alongside the peak (pass-1 C8 measured that it did not); D-13 scopes the larger title-borne class out explicitly and records that **plan-053's own pour carries no non-empty `detail` at all** |
| R8 | **Two `test_doc_lint.py` failures already exist on `main`**, identical on base and fixed | low | Recorded as pre-existing in EXP-001 rather than attributed to this plan; 7.1 must not claim to have fixed them |
| R9 | **#206's line numbers in the issue are stale by ~+43**, written against a pre-#193 revision | low | EXP-001 re-derived every line number on the current tree; issues cite the finding, not the issue body |
| R10 | **Deploying mid-execution runs new scripts against old prose** | low | The deploy gate is human-typed and blocks only 7.4, the last issue |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | Every behaviour change landed its `REQ-*` **before** its implementation issue closed — asserted on the **commit range**, not on the DAG. Uses plan-052's `M^1..M^2` merge-parent form so the check outlives the merge, and returns **INCONCLUSIVE (exit 2) under a squash**, where commit order is unrecoverable. **Discharged at 7.1, post-merge**: pre-merge there is no merge commit, so the control returns 2 by its own specification and could never reach exit 0 at the earlier discharge point (pass-2 C26) | `bash docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/ctl-053-spec-order.sh` → exit 0 | 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1.6a, 7.1 |
| SC2 | **Every control was observed RED on a fixture, and GREEN afterward, as two distinct dated records** | `bash docs/plans/plan-053-james-dixson-4015d3/assets/redcheck.sh verify-all` → exit 0 | 1.0, 1.1, 1.2, 1.3, 1.3a, 1.3b, 1.4, 1.5, 1.6, 1.6a, 1.6b, 1.6c, 1.7, 7.1 |
| SC3 | **Both #206 drop shapes reach `detail`, and neither adversarial shape produces an edge** | `bash docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/ctl-206-dropped-continuation.sh` → exit 0 | 2.1, 2.2 |
| SC3b | **A column-0 fence is NOT swallowed** into the preceding issue's detail — the guard against the corruption this fix could introduce | `bash docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/ctl-206-dropped-continuation.sh` → exit 0 | 2.2 |
| SC4 | The vendored `plan_extract.py` is byte-identical to `_shared/`, and so is the newly vendored `pour_fidelity.py`. The `test -f` guard is load-bearing: `test_sync.py` alone exits 0 **before** `pour_fidelity.py` has any vendoring entry, so the criterion could not observe 3.2 (pass-2 C28). SC6 already carried this guard; the two were inconsistent | `test -f skills/yf-plan/scripts/pour_fidelity.py && uv run --with pytest -- python -m pytest _shared/test_sync.py -q` → exit 0 | 2.3, 3.2 |
| SC5 | **`pour_fidelity.py --strict` returns 2, not 0, on all three empty-scope paths** | `bash docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/ctl-210-empty-scope.sh` → exit 0 | 3.1 |
| SC6 | `pour_fidelity.py` is resolvable under an installed `SKILL_DIR`, and `SKILL.md` §6.4 names that path | `test -f skills/yf-plan/scripts/pour_fidelity.py && grep -q '${SKILL_DIR}/scripts/pour_fidelity.py' skills/yf-plan/SKILL.md` → exit 0 | 3.2, 3.3 |
| SC6b | **§6.4 distinguishes exit 1 from exit 2** — an INCONCLUSIVE is no longer reported as a divergence. Asserted on the TEXT, which is the honest claim: no exit code can reach a caller's phrasing | `grep -qE 'FIDELITY_RC.*-eq 2' skills/yf-plan/SKILL.md` → exit 0 | 3.3 |
| SC7 | **The shipped-path check flags #210 on the unfixed tree and passes on the FP fixture** — and flags the plan-050 mutant, proving it would have caught the first instance | `bash docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/ctl-210-script-refs.sh` → exit 0 | 3.5, 3.6 |
| SC7b | **The check lands GREEN over the whole tree**, with no standing suppression other than the one marked `yf-incubator` external | `uv run scripts/check_skill_script_refs.py --json` → exit 0 | 3.7 |
| SC8 | **`resume-scan` distinguishes all six epic states**, and `found`/`epic_resolves` are unchanged | `uv run skills/yf-plan/scripts/test_epic_ref_audit.py` → exit 0 | 4.1 |
| SC8b | **A burned epic routes to the POUR path, not to either dead end** — #207's wedge, stated as the outcome rather than as a field value | `uv run skills/yf-plan/scripts/test_epic_ref_audit.py` → exit 0 | 4.1, 4.5 |
| SC8c | **The HUMAN `resume-scan` output names the epic state for a DANGLING ref** — the case 4.2 is about, and the surface EXP-005 called *"worse than the JSON"*. Asserted against a **fixture bundle with a stale pointer**, not against plan-052's healthy live epic: pass-2 C24 measured the earlier form testing the one case that was never broken, hard-coding another plan's bead state, and passing on any constant containing `state` | `bash docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/ctl-207-human-output.sh` → exit 0 | 4.2 |
| SC9 | **`clear-epic` removes both dual-written surfaces, and reports `metadata_fallback_remains` when the clear will not take effect** | `uv run skills/yf-plan/scripts/test_epic_ref_audit.py` → exit 0 | 4.3, 4.4 |
| SC10 | The verb enumeration is self-consistent at **32** | `uv run skills/yf-plan/scripts/test_cli_enumeration.py` → exit 0 | 0.5, 4.4 |
| SC11 | **An unrecognised status warns on stderr and still exits 0**, and `abandoned` is accepted silently | `uv run skills/yf-plan/scripts/test_update_status_gate.py` → exit 0 | 5.2 |
| SC11b | **`abandoned` is present at EVERY site the vocabulary change-set names, and absent from all three schema `statuses` lists** — the exclusion is asserted, not inherited by accident. 5.1 previously had NO criterion at all (pass-2 C27), which is how a multi-site edit could have landed partial and green | `bash docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/ctl-208-vocabulary-sites.sh` → exit 0 | 5.1, 5.0 |
| SC12 | **The fail-closed mapping is NARROW**: an unrecognised status flips PASS→FAIL, and a null-`bundle_status` document is unchanged | `uv run _shared/test_doc_lint.py` → exit 0 | 5.3 |
| SC12b | **The whole-corpus doc_lint verdict is unchanged by the fail-closed change**: errors remain **0**. The second clause ("no pre-existing document gains a finding") was **dropped rather than left unproven** — the command compares no finding-set (pass-2 C29). The file-count literal is likewise deliberately absent — pass-1 C11 measured 913 without this bundle against EXP-004's 917 with it, and this plan adds findings, reviews and assets, so any count is a MOVING fact and would be #221's shape (SC24) repeated | `uv run _shared/doc_lint.py --root . --json` → exit 0 | 5.3 |
| SC13 | **`e-status-values`' declared target set is non-empty AND contains at least one status literal OUTSIDE the declared vocabulary would be caught.** Stated this way because there is **no runnable drift verifier** to invoke (pass-1 C3) and because the naive "every target contains a status literal" form is measurably unsatisfiable — 2 of 23 agent files, worsening to 6 of 33 after the widening (pass-2 C17). The planted-mutation dispatch is an honest **manual** artifact in `assets/`, run on a `mktemp -d` copy | `bash docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/ctl-208-edge-scope.sh` → exit 0 | 1.6b, 5.4 |
| SC14 | **`SKILL.md` §5.2a's two `bd create` calls carry `plan_dir` in their `jq` metadata and prepend the provenance header with a blank line.** Asserted on the TEXT — §5.2a is agent-executed prose, so no exit code can reach what an agent actually transcribes (pass-1 C9, SC6b's form). The behavioural claim is discharged by the sandbox pour in `ctl-209-provenance`, which tests the fixture's own copy and says so | `bash docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/ctl-209-provenance.sh` → exit 0 | 6.1 |
| SC15 | **`REQ-PLAN-073` resolves to exactly one requirement REPO-WIDE.** Scoped to the whole repo, not `skills/yf-plan/` — the roots meaning is cited normatively in the repo-root `SPEC.md:919` inside `REQ-YF-PRE-004a` (pass-2 C18). Two successive narrower scopes each passed while the ambiguity #214 exists to remove survived | `bash docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/ctl-214-id-collision.sh` → exit 0 | 0.2 |
| SC16 | The FULL tier passes over the **merged** tree, asserted on a **dated run record** written by 7.1 rather than by re-executing the tier inside the criteria check. Two defects forced this (pass-2 C19, pass-3 C38): the path was wrong in v1 (measured exit 2 `Failed to spawn`), and `recheck-criteria` turns a `TimeoutExpired` into `status: inconclusive` and `continue`s — never counted, never in `failed` — while the FULL tier (`cargo clippy --workspace --all-targets`, `cargo test --workspace`, ~25 more rows) far exceeds the 300 s default. **The plan's broadest criterion would have timed out, recorded inconclusive, and let completion proceed at exit 0** — this plan's own thesis defect, inside this plan. Follows plan-050's `assets/sc15-full-validation.md` precedent | `bash docs/plans/plan-053-james-dixson-4015d3/assets/checks/check-full-tier-record.sh` → exit 0 | 7.1 |
| SC5b | **`test_pour_fidelity.py` runs in a repo that is NOT this one** — the four new arms pass under a sandboxed `HOME` with no live `bd` state. This is the same portability defect #210 is about, in the suite that guards #210's fix | `bash docs/plans/plan-053-james-dixson-4015d3/assets/checks/check-suite-portable.sh` → exit 0 | 3.4 |
| SC14b | **`SKILL.md` §5.2a no longer asserts the description is the detail VERBATIM**, and no description-equality check was added anywhere — the absence is what makes the header safe | `! grep -q 'populated from' skills/yf-plan/SKILL.md && ! git grep -qE 'description.*==.*detail' -- '_shared/**' 'skills/**'` → exit 0 | 6.2 |
| SC20 | **The deployed tree matches source and the version stamp matches HEAD** | `test "$(yf --version \| grep -oE '[0-9a-f]{7,}' \| head -1)" = "$(git rev-parse --short HEAD)"` → exit 0 | 7.4 |
| SC17 | **Every out-of-scope defect this investigation measured is filed, with its measurement** — the set is enumerated in 7.2, not counted here | manual: filing is an outward-facing write whose *content quality* no exit code reaches; the URLs are recorded in `log.md` and read back per AGENTS.md | 7.2 |
| SC18 | Every upstream row reached the end state its disposition requires | `uv run skills/yf-plan/scripts/plan_manager.py verify-reconcile docs/plans/plan-053-james-dixson-4015d3 --json` → exit 0 | 7.3 |
| SC19 | The coarse tracker is filed **through** `/yf-beads-upstream`, so the epic carries it as `external_ref`. **Verification command AMENDED at close (plan-053 Issue 7.4, RE-006), per §6.4's sanctioned remediation — the CLAIM is unchanged, only the INSTRUMENT.** The original piped `json-get epic < plan.md`, but `json-get` is a JSON extractor and `plan.md` is markdown, so it returned `ERROR: key epic not found`, that text became the bead id, and `jq` failed with `Cannot index object with number` (exit 5) while the asserted end state was true throughout. The replacement reads the `**Epic:**` line directly and hard-codes no id. This is the third of the three criterion-MECHANICS defects RE-007 is about, and it is the one that HALTED completion — the gate working correctly. Asserted on the **end state**, never on the route — `stamp-tracker` is specified **fail-soft** and exits 0 with no epic and no tracker at all, so the earlier clause was structurally unable to fail (pass-2 C25) | `bd show "$(sed -n 's/^\*\*Epic:\*\* //p' docs/plans/plan-053-james-dixson-4015d3/plan.md \| head -1)" --json \| jq -e '.[0].external_ref \| startswith("https://github.com/")'` → exit 0 | 7.3 |

