---
type: Plan
okf_spec: OKF-PLAN
id: plan-050-james-dixson-d0414b
author: james-dixson
created: '2026-08-20'
status: review
---
# Plan: Fix the four mechanical process defects this session's plans demonstrably hit (#178-#181)

**ID:** plan-050-james-dixson-d0414b
**Author:** james-dixson
**Created:** 2026-08-20
**Status:** review

## Objective
Fix the four mechanical process defects this session's plans demonstrably hit (#178-#181)

One deliverable, deliberately narrow:

1. **The four mechanical defects — #178, #179, #180, #181.** Each was hit, diagnosed and worked
   around by hand during plan-047/048/049; every one has a reproduction in a bundle on `main`.
   Each ships with a control that was observed RED before its fix landed.

**Narrowed from six by the D-9 split at review cycle 5.** #182 and #184 (the red-team rule and
sub-agent dispatch) and M9/#149 went to **plan-051**. #177 was scoped in and then dropped on
evidence (D-6). So this plan's set is neither the original six nor a subset of them — see D-9.

Explicitly NOT in scope: M9/#149, #182, #184 (all → plan-051, D-9); the M11 probe mechanism; the
remaining 14 ranked classes; and escape-rate measurement (#145).

## Motivation
Three consecutive plans (047, 048, 049) each hit the same small set of process defects, and
each worked around them by hand. The workarounds were recorded in retrospectives and the
defects filed upstream, but nothing executes: the next plan hits them again. plan-049's
executor was told at launch to expect two of them (#179, #180) and hit both exactly as
predicted — a process defect the operator can forecast but not prevent is the clearest
possible case for making it mechanical.

Research 004 supplies the general form. Its headline, reached independently by five of five
retrieval clusters on disjoint surfaces: **a written rule that nothing executes is unreliably
obeyed, and no exit code records the skip.** Sharpest expression: *a step with no exit code is
not a step.* The corpus's own line — *"Adding a sixth instruction to a five-instruction list
that was partially ignored is a null change"* — is why this plan builds detectors rather than
writing more prose.

M9 is included because it is the reason research 004 could only report lower bounds rather
than prevalences: no bundle in an 83-bundle corpus declares what it fixes, so the population
of remediation pairs is not estimable. That is the process failing to record its own
bookkeeping, and it compounds — every future analysis inherits the same blind spot.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#177](https://github.com/dixson3/yoshiko-flow/issues/177) | red-team: no check that a numeric target is derivable from the plan's own scope rules | partial | **D-6 — DROPPED from this plan after EXP-001 refuted it.** **IN:** a comment recording the refutation, so the next attempt does not rebuild the same inadequate scanner. **OUT:** any check. Derivability is not decidable from `plan.md` — `81` is textually identical whether measured or guessed, and the naive scanner missed **both** plan-049 criteria it was built for | 6.2 |
| [#178](https://github.com/dixson3/yoshiko-flow/issues/178) | generate the upstream-write authorization grant FROM the Upstream Issues table | include | **D-1.** plan-048 halted its own reconcile on an omitted `include` close. plan-049 avoided it only because the operator derived the grant by hand | 3.2a |
| [#179](https://github.com/dixson3/yoshiko-flow/issues/179) | the start-gate wrapper task is orphaned at pour and blocks cascade-close | include | **D-1.** Hit by plan-048 and plan-049. Forecast to plan-049's executor at launch and hit anyway | 1.2 |
| [#180](https://github.com/dixson3/yoshiko-flow/issues/180) | close-reconcile-step requires the reconcile gate resolved first — undocumented chain ordering | include | **D-1.** Same two plans, same forecast-and-hit | 1.3 |
| [#181](https://github.com/dixson3/yoshiko-flow/issues/181) | doc_lint: a bundle outside `docs/plans/` returns a silent green, indistinguishable from clean | include | **D-1, redesigned at operator direction after pass 9.** `--path` on an unselected file returns `files_checked: 0, verdict: PASS` — byte-identical to a nonexistent path. Closed by a **preflight classifier** (2.2) plus the rule change that calls it (2.2a), leaving the lint's own semantics untouched; three earlier scopes were each refuted by measurement, all of them because they mutated the lint's reporting | 2.2 |
| [#184](https://github.com/dixson3/yoshiko-flow/issues/184) | §3: the red-team is never dispatched as a sub-agent — the drafter reviews its own draft | deferred | **D-9 — SPLIT OUT to plan-051**, with #182 (same epic, same deadlock). The evidence for it is unaffected and strong: this plan's own passes 1-2 were main-session self-review and advanced it to `ready-for-approval`; three independent passes then returned REVISE with 11, 17 and 14 concerns |  |
| [#182](https://github.com/dixson3/yoshiko-flow/issues/182) | red-team: the read-only rule forbids the sandbox spike that catches specification defects | deferred | **D-9 — SPLIT OUT to plan-051.** Pass-5 C39: Epic 5's gate membership was an unconditional deadlock — the control-builders sat inside the gate's own `Blocks` set, so neither the RED nor the GREEN observation was producible. The fix is structural, not a patch |  |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | M5/M9: process rules that nothing executes, and remediation edges that exist only in prose | deferred | **D-9 — SPLIT OUT to plan-051.** M9's detector was designed and its premise measured (EXP-004; pass-5 independently reproduced the 26 edges, both `created_at` fields and the 7-hour skew), but pass-5 C40 measured that the host it was wired into cannot express the INCONCLUSIVE contract the design depends on. Goes to plan-051 with that finding as its starting evidence |  |
| [#150](https://github.com/dixson3/yoshiko-flow/issues/150) | research 004: process-defect mining across 83 plan bundles | partial | **D-9.** **IN:** the four mechanical fixes (#178-#181) as worked instances of the ranked classes. **OUT:** M9, the M11 probe mechanism, and the remaining 14 classes — M9 goes to plan-051, the rest stay unscheduled | 6.2 |
| [#173](https://github.com/dixson3/yoshiko-flow/issues/173) | success criteria and upstream dispositions are never checked against the engine that enforces them | partial | Adjacent to #177 and #178 — both are instances of it. The general cross-check stays open | 6.2 |
| [#174](https://github.com/dixson3/yoshiko-flow/issues/174) | a review-phase validation pass — falsify every criterion, cross-check every claim against the code that scores it | partial | #177 and #182 close named sub-cases; the general falsification pass stays open | 6.2 |
| [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | New skill: yf-retrospective — measure escape rate and enforce a fix+prevention contract | deferred | **D-3.** Own plan. The emit side already exists and is accumulating; a consumer built now reads a thin corpus | |
| [#113](https://github.com/dixson3/yoshiko-flow/issues/113) | add an execution-rehearsal review pass (topological DAG walk against running state) | exclude | Different axis — DAG rehearsal, not defect detection | |
| [#186](https://github.com/dixson3/yoshiko-flow/issues/186) | CRITICAL: `plan_extract.py` emits masked titles — inline code spans are blanked out of every issue/epic title | include | **Pulled in after pass 9, operator request.** #181's defect class in a different engine: `--strict` returns `unparsed: []` and exit 0 while 4 of 35 titles came back blanked, and the corruption is written straight into the bead DAG by §5.2a's mechanical pour. **This plan's own pass 8 saw it and dismissed it as pre-existing** | 7.2 |
| [#187](https://github.com/dixson3/yoshiko-flow/issues/187) | CRITICAL: `plan_extract.py` carries no issue detail, so §5.2a's mechanical pour cannot populate `--description` | include | **Pulled in after pass 9, operator request.** 35 of 35 beads with empty descriptions on a DAG that is otherwise perfect. Load-bearing for this plan specifically: every correction nine review passes bought lives in the continuation bullets, and none of it would reach the beads | 7.3 |
| [#183](https://github.com/dixson3/yoshiko-flow/issues/183) | plan-049-james-dixson-725bc0 execution tracking | exclude | plan-049's coarse tracker (currently OPEN); it **is closed by** plan-049's own land-the-plane sweep, not by this plan's reconciliation. Not `tracker`: `_TRACKER_ROW_RE.search()` takes the FIRST `tracker` row, so this row would stamp plan-050's epic with plan-049's URL. Not `supersede`: that requires CLOSED as NOT_PLANNED, false of a completed plan | |

## Scope Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-1 | **The spine is the six session-filed defects (#178–#182, #184)** — #177 was scoped in and then dropped on evidence (D-6), and #184 was folded in after pass 3, so the count is unchanged and the membership is not — not research 004's M11 probe mechanism. | Operator-selected. Each has a reproduction on `main` rather than a hypothesis, and each was hit by more than one plan. M11 is better-evidenced *as a general prescription* but would be built against no local failing instance — the shape #177 itself warns about. |
| D-2 | **Include M9** — make the remediation edge between two plans machine-recorded. | Operator-selected. Top-ranked class (4/4 repos, 5 clusters) and the reason research 004's counts are lower bounds rather than prevalences. Compounds: every future analysis inherits the blind spot. |
| D-3 | **Defer escape-rate measurement (#145).** | Operator-selected. A whole new skill; the `plan-retrospective.md` emit side already exists and is accumulating entries, so a consumer built today would read a thin corpus. |
| D-4 | **Every fix must ship with a demonstrated failing case** — the control is shown RED before it is trusted GREEN. | Not a style preference. plan-047 found six controls that reported clean while checking nothing; plan-048's R3 shipped broken twice over a clean corpus; plan-049's EXP-002 measured its own safety postcondition *passing* the replay it was written to catch. `_shared/test_dag_guard.py`'s mutant suite is the inherited template. |
| D-5 | **Re-measure every figure inherited from research 004 or from #177–#182 before use.** | Carried from plan-048 D-5 and plan-049 D-7, both of which caught a stale inherited literal at execution. Research 004 states its own counts are lower bounds over a recorded subset — citing one as a prevalence would reproduce M9 inside the plan meant to fix it. |
| D-6 | **Drop #177 from the deliverable** after EXP-001 refuted it; comment the refutation upstream instead. | Operator-selected on the finding. The tractable form is a producer-side *citation* contract, not the detector the issue asks for — a different deliverable with its own design. Shipping the naive scanner would put a control in the repo that misses the exact two cases that motivated it: R4's "ships unable to fail" class, which D-4 forbids. |
| D-7 | **M9 is forward-only stamping.** Stamp `metadata.plan` on `discovered-from` beads at creation; leave the 26 historical edges unattributed and say so. | Operator-selected. EXP-004 measured the edges as intact and resolvable — only attribution is missing — so the producer fix is one seam. Backfilling is 26 hand adjudications, and plan-049's SC31/SC23 are a fresh reminder that hand-adjudicated populations expand under contact. |
| D-8 | **#182's fix ships with an honest non-mechanical status.** | EXP-006 measured the rule as one line of agent prose. There is no exit code for "a reviewer obeyed a rule". The verifiable claim is source↔deployed **parity** (class M3), and the plan says that rather than implying the prose itself is enforced — which would be the M5 vacuity this plan is nominally about. |
| D-9 | **SPLIT at review cycle 5.** Epics 4 (M9) and 5 (#182/#184) go to **plan-051**; this plan lands the four mechanical fixes. | Operator decision on measured evidence. Concerns per pass ran **5 → 4 → 11 → 17 → 14**, and every high concern for three consecutive rounds landed on Epic 4, Epic 5, or the resolution round itself — while Epics 1-3 drew almost none after pass 1. Two rounds of resolutions each injected defects at roughly the rate they closed them (36%, then 65%), under two different actors, so the plan was not converging under patch-and-review. Pass-5 C39 and C40 are structural, not patchable: Epic 5's gate membership was an unconditional deadlock, and Epic 4's named host cannot express the INCONCLUSIVE contract its design depends on. D-8's honesty clause about #182 travels with it to plan-051. |

## Investigation Findings

_Pre-investigation checkpoint (written before any experiment ran). Six experiments, one per
scoped defect. Per D-5 every figure below is re-measured here rather than inherited._

| Exp | Question | Why it is a real unknown |
| :-- | :-- | :-- |
| EXP-001 | #177 — what mechanically distinguishes a *derivable* numeric target from a fixed literal, and can a check see the difference? | Six review passes across two plans checked the target was fixed at approval; none checked derivability. It is not obvious a static check can tell them apart at all — this may be unfixable as stated |
| EXP-002 | #179 / #180 — reproduce both close-chain defects mechanically and find the minimal fix | Both were hand-worked around twice. Neither has a recorded root-cause reproduction, only a workaround |
| EXP-003 | #181 — is `doc_lint`'s silent green fixable without breaking path-keyed selection? | `files_checked: 0` is the *correct* answer for an unselected path; the defect is that it is indistinguishable from a nonexistent one. The fix may conflict with the keying design |
| EXP-004 | M9 — what mechanism can record a plan→plan remediation edge, and what is the 0-of-53 figure today? | Three candidate mechanisms (bd `discovered-from`, a plan.md field, bead metadata) with different producer costs. The figure is inherited from research 004 and must be re-measured (D-5) |
| EXP-005 | #178 — can the upstream grant be *generated* from the Upstream Issues table rather than hand-derived? | plan-049 avoided the defect only because the operator derived the grant by hand. A generator needs the disposition→end-state map to be complete and correct |
| EXP-006 | #182 — where does the red-team read-only rule live, and what is the blast radius of the rewrite? | The rule text is drafted in the issue, but its installed locations and any dependent prose are unmeasured |

### Approach hypothesis (pre-investigation, to be confirmed or refuted)

Each of the six is a *detector* problem, not a policy problem: the correct behaviour is already
written down somewhere and simply has no exit code attached. If that holds, the plan is six
small mechanical checks plus one producer change for M9. **EXP-001 and EXP-003 are the two most
likely to refute it** — a derivability check may be undecidable from the document alone, and the
silent green may be inherent to path-keyed selection.

### Results — the hypothesis held for four of six, and was refuted for one

| Exp | Verdict | The measurement that decided it |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-target-derivability.md) | **REFUTED** → #177 dropped (D-6) | The first scanner's figures (6 numeric targets in 101 SC rows) are themselves REFUTED and retained only as the error: a repaired filter counts **167** SC rows over `docs/plans/*/plan.md` at `fb79b44`, and the successor citation-presence check **passes plan-049's SC23 and SC31** — the two cases #177 was filed about. A control that green-lights its own motivating instances |
| [EXP-002](findings/exp-002-close-chain.md) | **CONFIRMED**, and stronger than filed | **49 of 49** start-gate wrapper beads closed **by hand**, with **29 distinct** improvised `close_reason` values. Not intermittent — a universal manual step with no mechanism |
| [EXP-003](findings/exp-003-silent-green.md) | **CONFIRMED** | A nonexistent path and a real-but-unselected file both return `files_checked: 0, verdict: PASS` — **byte-identical**. Three states, one verdict |
| [EXP-004](findings/exp-004-m9-remediation-edge.md) | **CONFIRMED, premise revised** | 26 `discovered-from` edges, **0 with plan attribution on either endpoint**. The edges are intact and resolvable; only attribution is missing, so M9 is a stamping gap, not a missing relationship |
| [EXP-005](findings/exp-005-grant-generation.md) | **CONFIRMED, then SUPERSEDED by the C12 split** | The disposition→end-state map already exists at `plan_manager.py:2012` (`_verify_row`). The finding's original conclusion — that a generator could call `_verify_row` itself — was **refuted at pass 3 C12**: it returns no `required_action`, is network-bound, and rejects `exclude`. Issues 3.2/3.2a replaced it with a shared requirement table both consume (pass-8 C81) |
| [EXP-006](findings/exp-006-red-team-rule.md) | **CONFIRMED, narrowed** | The rule is **one line** (`red-team.md:63`) and says "never writes files" — it never forbids a spike at all. The defect is under-specification; silence read as prohibition |

**Two findings changed the plan's own scope**, which is why they were run before drafting:
EXP-001 removed a deliverable (D-6) and EXP-004 replaced M9's premise (D-7). A third, EXP-006,
removed the plan's ability to claim #182 is mechanically enforced (D-8).

## Approach

**Four fixes (#178-#181), each landing with a control that was shown RED first.**

The organising principle comes from the corpus itself: *a step with no exit code is not a step.*
Every deliverable here either **gets an exit code** or is explicitly declared unenforceable
(D-8). Nothing ships as additional prose asking future agents to remember something — research
004's measured verdict on that strategy is that it is a null change.

Ordering is forced by three constraints:

1. **SPEC first** (AGENTS.md). Every behaviour change lands its `REQ-*` before its code.
2. **The driven-red harness before the fixes it judges** (D-4). A fixture that has never been
   observed failing is not evidence. This is the plan's own instance of research 004's M11 —
   the probe placed *before* the work that depends on it — even though the general M11 mechanism
   is descoped.
3. **The corpus-wide fixes before the plan-folder ones.** `doc_lint` verdicts (#181) change what
   every later check reports, so they land before anything reads those verdicts.

**What this plan deliberately does not do.** It does not add a review pass — research 004's
prescriptive signal is explicitly *not* "add another review pass", and this repo already runs
five to seven per plan while shipping the defects above. It does not touch the 14 unaddressed
ranked classes. It does not backfill history (D-7).

## Epics
### Epic 0: SPEC amendments and the driven-red harness
- Issue 0.1: Land the `REQ-*` requirements for every behaviour change in this plan — the wrapper-close contract (#179), the §6.4 chain ordering constraint (#180), `doc_lint`'s two new verdicts (#181), and the grant generator (#178). **Four NEW ids, enumerated; SC1 checks that list** — plus one **amendment to an existing id**, `REQ-DATA-024`, whose engine contract declares a closed verdict vocabulary (`PASS | FAIL | INCONCLUSIVE`) and pins `INCONCLUSIVE` to "the linter could not run" *and only that*. Issue 2.2's two new verdicts breach the closed set either way, and `DRIFT-CHECK.md`'s `e-doclint-spec` edge treats `spec` as **fixed authority**, so a declaration the engine does not implement is a FAIL (pass-8 C78). The M9 stamping rule and Epic 5's two REQ amendments left with the plan-051 split; they are named in **D-9** and **will be** recorded in `references/handoff-051.md` by Issue 6.5, which does not exist yet (pass-6 C60) — an enumerated list that silently retains ids for descoped work is worse than prose, because it looks exhaustive (pass-5 C41's defect, inverted). SPEC-first per AGENTS.md: no implementation issue below may start before this closes.
- Issue 0.2: Build `assets/redcheck.sh` with **three verbs**. Two make observations, because the two are made at different points in the DAG: `record-red <fixture> <control>` runs the control against the UNFIXED code and appends a non-zero observation; `assert-distinguishes <fixture> <control>` re-runs it against the FIXED code, appends the zero observation, and fails unless BOTH are on record. A single verb would demand a zero-on-GREEN exit from a tree where the fix does not yet exist. **Definition of "fixture", stated here because the whole harness contract depends on it** (pass-7 C67): a fixture is a **script that exits 0 iff the control's asserted behaviour holds**. So a control's fixture is non-zero before its fix and zero after — that is what makes a RED→GREEN pair meaningful, and `controls.txt` lists **only** red→green controls. A scenario whose assertion is invariant across the fix is a **negative control**, not a redcheck control, and never appears in `controls.txt`. **The four control ids, named here verbatim** so no issue has to invent them: `ctl-178-grant`, `ctl-179-wrapper-close`, `ctl-180-chain-order`, `ctl-181-silent-green`. The third verb, `verify-all` (no arguments), is what the capability gate calls: it walks `assets/red-prework.md`, asserts a `record-red` AND an `assert-distinguishes` record for **each control named in the manifest `assets/controls.txt`** (one id per line, written by 0.2 so "each control" enumerates from a file rather than from a reader's judgement), and returns the AGGREGATE 0/1/2. Pass-6 C52 spiked the gate's Test against a redcheck built strictly to an earlier draft of this issue and got `unknown verb: ''` → exit 2, which per the gate's own Instructions leaves it permanently UNRESOLVED. **Record schema** (pass-6 C61), one line per observation: `verb, control, fixture, exit-code, verbatim command, UTC timestamp, git describe --always --dirty`. Pass-7 C69 measured that a bare `git rev-parse --short HEAD` does **not** make an ordering claim checkable — nothing requires the fix to be committed before `assert-distinguishes` runs, and both records then carry the identical hash, so "descends from" is trivially true and carries no information. The `--dirty` marker is recorded for diagnosis only; **the ordering claim is dropped**, and SC2b rests on the exit-code distinction alone, which is sufficient and needs no ordering. Also ship `assets/gate-run.sh`, the 0/1/2 normalising wrapper plan-049 used, so a missing or crashing harness reports **2 (INCONCLUSIVE)** rather than bash's raw 127.
  - depends-on: 0.1
- Issue 0.2a: Capture SC7's **baseline** before any Epic-2 change: record the corpus `files_checked` with the exact `--exclude` invocation that self-excludes this plan's bundle, into `assets/`. Measured at drafting: **757** with the exclusion applied. Only the excluded figure is recorded — the unfiltered count drifted within the drafting session itself (817 → 820), while the excluded one reproduced exactly, which is the whole point of the self-exclusion (pass-5 C51). Re-measure at execution per D-5.
  - depends-on: 0.1

### Epic 1: The close chain (#179, #180)
- Issue 1.1: Author **two fixtures and one raw scenario** for this epic (the distinction matters — see 0.2's fixture definition and pass-8 C80) and run them against the **unfixed** code. (a) `ctl-179-wrapper-close` — SC3's scenario: pour a molecule, resolve the gate, assert the wrapper is `closed` with the generated reason. Non-zero pre-fix, zero post-fix: a genuine red→green pair. (b) `ctl-180-chain-order` — `close-reconcile-step` with the reconcile gate unresolved must drive the ordering assertion non-zero, zero once 1.3 lands. (c) A **negative control**, `neg-179-open-wrapper` — a **raw scenario, not a fixture**: a poured molecule with an open start-gate wrapper must drive `close_cascade.py` non-zero, and must **still** do so after 1.2 (SC4). It is a raw scenario precisely because 0.2's fixture definition inverts here — a *fixture* for this control would exit **0** (its asserted behaviour holds), while SC4 wants the observed `close_cascade.py` exit itself, which is non-zero (pass-8 C80). Its assertion is invariant across the fix, so it is **NOT** in `controls.txt` and the gate never asks it for a GREEN record. Pass-7 C67: an earlier draft made (c) the #179 control, which required the same fixture to be non-zero post-fix (SC4) and zero post-fix (the gate) simultaneously. **Run `redcheck.sh record-red <fixture> <control>` against the unfixed tree for (a) and (b); this issue PRODUCES those records.** Run (c) directly and record its result in `assets/`, not through redcheck.
  - depends-on: 0.2
- Issue 1.2: Close the start-gate wrapper task in the same step that resolves the gate, with one generated `close_reason`. Fix at the pour/resolve seam per EXP-002 — **do not** weaken `close_cascade.py`'s `_bead_is_terminal`, which is reporting correctly. **Then run `redcheck.sh assert-distinguishes <fixture> ctl-179-wrapper-close` against the fixed tree and record the zero observation** — this issue PRODUCES that record (pass-6 C53); the gate's blocked issues only consume it.
  - depends-on: 1.1
  - resolves-upstream: #179 (include)
- Issue 1.3: Document and enforce the §6.4 chain ordering constraint that `close-reconcile-step` requires the reconcile gate resolved first — as an ordering assertion with an exit code, not a prose note. **The exit code needs a caller**: `SKILL.md:1440` currently does `RSTEP=$(... close-reconcile-step ...)` and only echoes it, never checking `$?` — so this issue must edit `SKILL.md` §6.4 too, or the new code is unread (pass-8 C79), which is this plan's own M5 vacuity class. **Then run `redcheck.sh assert-distinguishes <fixture> ctl-180-chain-order` against the fixed tree and record the zero observation** — this issue PRODUCES that record (pass-6 C53); the gate's blocked issues only consume it.
  - depends-on: 1.1
  - resolves-upstream: #180 (include)
- Issue 1.4: **Verify** — assert `assets/red-prework.md` **contains** both records for each of this epic's two controls (the RED from 1.1, the GREEN from 1.2/1.3), and assert `_bead_is_terminal` is unmodified. **Also re-run `neg-179-open-wrapper` directly against the fixed tree and assert `close_cascade.py` still exits non-zero, recording it beside the pre-fix result in `assets/`** — SC4's post-fix arm had no assigned runner (pass-9 C90). Running a raw scenario is not a `redcheck.sh` verb, so this produces no gate evidence. This issue otherwise reads the file; it runs no `redcheck.sh` verb, so no gate evidence is produced inside the gate's own Blocks set. Pass-5 C38: an earlier draft had it recording the GREEN observation, which put the gate's evidence inside the gate's own Blocks set — a REQ-AGENT-046 cycle.
  - depends-on: 1.2, 1.3

### Epic 2: The silent green (#181)
- Issue 2.1: Author the fixture `ctl-181-silent-green` — it drives **all four classifier arms** (a bundle copied outside `docs/plans/` via `--root`, a real-but-unselected `--path`, a nonexistent `--path`, and a selected-but-empty file) and exits 0 iff each returns its own class. Against the unfixed tree there is no `classify` mode at all, so it is RED for the strongest possible reason; also record the byte-identical PASS that EXP-003 measured, which is the defect being closed. **Run `redcheck.sh record-red <fixture> ctl-181-silent-green` against the unfixed tree; this issue PRODUCES that record** (pass-7 C68).
  - depends-on: 0.2
- Issue 2.2: Ship a **preflight classifier** — a new `classify` mode on `doc_lint.py` that runs **before** the lint and decides whether linting this path is meaningful at all. It emits a `class` of `selected` | `not-selected` | `no-such-path` | `empty`, with the exit contract **0 = lintable, 1 = degenerate (do not lint; report the class), 2 = could not run**. **`doc_lint`'s own lint path and verdict vocabulary are UNCHANGED** — no new verdict strings, no new exit codes on the lint itself. That is the whole point of the design and it is what makes it safe: the two rejected scopes both failed because they mutated the lint's own reporting. The general `files_checked == 0` form breaks `_shared/test_doc_lint.py`'s **SC42** (pass-8 C77); a **`--path`-keyed-always** form breaks the same file's **SC17** block (`:722-743`), which pins an unselected `--path` to `PASS`/rc 0 *and identical to a nonexistent path* (pass-9 C86). `doclint-tests` runs in **both** the FAST and FULL tiers, so either would fail the on-edit gate for every `doc_lint.py` edit and fail SC15. A separate classifier touches neither assertion: **SC17 and SC42 remain literally true**, because the behaviour they characterise is not modified. It also subsumes what neither earlier scope reached — a **selected-but-empty** file, and the `--root` form that is #181's *titled* scenario, a bundle **copied** outside `docs/plans/`. **Then run `redcheck.sh assert-distinguishes <fixture> ctl-181-silent-green` against the fixed tree and record the zero observation** — this issue PRODUCES that record. **Named surfaces:** `_shared/doc_lint.py`, its byte-identical vendored copy `skills/yf-plan/scripts/doc_lint.py` (guarded by `_shared/sync.py --check`). **`_shared/test_doc_lint.py` requires NO change** — that is this design's central claim and Issue 2.3 measures it.
  - depends-on: 2.1
  - resolves-upstream: #181 (include)
- Issue 2.2a: Rewrite `skills/yf-plan/protocols/DOC-LINT.md`'s on-edit rule to **run the classifier first and lint only on `class: selected`**, replacing its "Reading the result: `files_checked` is NOT optional" section — prose instructing an agent to parse a field and reinterpret it — with an executed step that carries an exit code. **This is the issue that actually closes #181.** Without it the classifier ships and nothing calls it, which is the M5 vacuity this plan exists to end; #181 would have to drop from `include` to `partial`. Note the reserved OKF `index.md`/`log.md` in every bundle classify as `not-selected` and are therefore **skipped, not failed** — so the protocol's "ordinary, not exceptional" framing survives intact and needs no carve-out. Also update its `files_checked` table, which stays true of the lint but is no longer the caller's decision procedure.
  - depends-on: 2.2
- Issue 2.3: Re-measure the corpus `files_checked` figure and record whether it moved — it must not, since the lint path is unchanged. Then run `uv run _shared/test_doc_lint.py` (expect **`all passed`, zero edits to that file**) and the FAST tier over a `doc_lint.py` change. Both are the regression that pins the classifier design: pass-8 C77 and pass-9 C86 each measured a rejected scope failing exactly here. A change would mean selection was perturbed, which 2.2 forbids.
  - depends-on: 2.2, 2.2a
- Issue 2.4: **Verify** — assert `assets/red-prework.md` **contains** both records for this epic's control (RED from 2.1, GREEN from 2.2). Reads the file; runs no `redcheck.sh` verb (pass-5 C38, pass-6 C53).
  - depends-on: 2.2

### Epic 3: The upstream grant (#178)
- Issue 3.1: Author the fixture `ctl-178-grant` from plan-048's **actual** recorded grant with the `#172` close omitted — a real recorded failure, not a synthetic one. **Run `redcheck.sh record-red <fixture> ctl-178-grant` against the unfixed tree; this issue PRODUCES that record** (pass-7 C68).
  - depends-on: 0.2
- Issue 3.2: Extract the per-disposition **requirement** out of `_verify_row`'s branch conditions into a shared table keyed by the `UPSTREAM_DISPOSITIONS` literals, and make `_verify_row` read it. Pass-3 C12 measured why the original design was unworkable: `_verify_row` returns `{detail, disposition, issue, verdict}` with **no `required_action`**, is **network-bound** (`gh issue view` per row), and returns `fail: "unrecognised literal"` when handed an `exclude` row directly — for a literal that IS in the frozenset.
  - depends-on: 3.1
- Issue 3.2a: Ship the `grant` verb on top of that shared table, so generator and verifier consume one source. It emits a **proposal** from local plan content; it never writes the authorization file, and it must not require network to generate. **Then run `redcheck.sh assert-distinguishes <fixture> ctl-178-grant` against the fixed tree and record the zero observation** — this issue PRODUCES that record (pass-6 C53); the gate's blocked issues only consume it.
  - depends-on: 3.2
  - resolves-upstream: #178 (include)
- Issue 3.3: Cover every disposition including `deferred` and the `tracker`/inconclusive case. A generator silently omitting a disposition is #181's defect class in a new place.
  - depends-on: 3.2, 3.2a
- Issue 3.4: **Verify** — assert `assets/red-prework.md` **contains** both records for this epic's control (RED from 3.1, GREEN from 3.2a). Reads the file; runs no `redcheck.sh` verb (pass-5 C38, pass-6 C53).
  - depends-on: 3.2a

<!-- Epics 4 and 5 were SPLIT OUT to plan-051 at review cycle 5 (D-9). The numbering gap is
DELIBERATE and left un-renumbered: stale issue references were the single most recurrent defect in
this plan's review history (8 at pass 3, 3 at pass 4, 1 at pass 5, under three different actors),
and renumbering ten issues plus their criteria is precisely how that class is produced. -->

### Epic 7: The extractor's silent corruption (#186, #187)
_Added after pass 9 at operator request. Both are `plan_extract.py` defects of this plan's own thesis class — a tool that reports clean while producing corrupt output — and both are already measured upstream against a real 35-issue plan._
- Issue 7.1: Author the two fixtures and run them against the **unfixed** extractor. (a) `ctl-186-masked-title` — a `plan.md` whose issue and epic titles contain inline code spans; the fixture exits 0 iff every extracted title matches the source line verbatim. Today it fails, with `unparsed: []` and exit 0 from `--strict`. (b) `ctl-187-empty-detail` — a `plan.md` whose issues carry continuation bullets beyond `depends-on:`/`resolves-upstream:`; the fixture exits 0 iff the extracted issue carries that prose in a `detail` field. Today there is no such field. **Run `redcheck.sh record-red <fixture> <control>` for both against the unfixed tree; this issue PRODUCES those records.**
  - depends-on: 0.2
- Issue 7.2: Fix the masked-title read — capture the title from `raw`, not from the `mask_inline_code`d line. The masking is correct for **parsing** (`plan_extract.py:142`: a `depends-on:` inside a code span is documentation, not a declaration) and must be preserved for that; only the title capture changes. `raw` is already in scope at the single call site. **Then run `redcheck.sh assert-distinguishes <fixture> ctl-186-masked-title` against the fixed tree and record the zero observation.**
  - depends-on: 7.1
  - resolves-upstream: #186 (include)
- Issue 7.3: Add a `detail` field carrying each issue's continuation lines minus the parsed `depends-on:`/`resolves-upstream:` bullets — #187's framing 1, which keeps SKILL.md §5.2a honest rather than retreating to framing 2 (weakening the doc). **Then run `redcheck.sh assert-distinguishes <fixture> ctl-187-empty-detail` against the fixed tree and record the zero observation.**
  - depends-on: 7.1
  - resolves-upstream: #187 (include)
- Issue 7.4: **Verify** — assert `assets/red-prework.md` contains both records for each of this epic's two controls, and assert the masking behaviour itself is unchanged for parsing: a `depends-on:` written inside a code span must still NOT become an edge. Reads the file; runs no `redcheck.sh` verb.
  - depends-on: 7.2, 7.3
- Issue 7.5: Re-run this plan's own extraction and record the delta — plan-050's `plan.md` uses inline code in issue titles throughout, so its own bead DAG is affected. This is the plan measuring the fix on itself.
  - depends-on: 7.4

### Epic 6: Reconcile and land
_Numbered 6, not 4: Epics 4 and 5 went to plan-051 (D-9) and the gap is deliberate — see the note above._
- Issue 6.1: Run the FULL validation tier over the merged tree and record the result.
  - depends-on: 0.2a, 1.4, 2.3, 2.4, 3.2a, 3.3, 3.4, 7.4, 7.5
- Issue 6.2: Draft the upstream comments **from the Issue 3.2a `grant` verb's output, not from a prose list** — pass-7 C71 measured that `_verify_row`'s `partial` branch requires OPEN **plus** a plan-id mention, and an earlier draft named only #177 and #149 while the table assigns #150, #173 and #174 to this issue, so `verify-reconcile` failed all four `partial` rows. That is #178's late-halt shape in the comments column instead of the closes column, which is exactly why the grant verb enumerates it. Content to carry: **#177's refutation** (EXP-001's corrected measurement, so the next attempt does not rebuild the same inadequate scanner) and **#149's corrected framing** (the edges exist; only attribution is missing — a `deferred` row may carry a mention, it simply does not require one).
  - resolves-upstream: #150 (partial), #173 (partial), #174 (partial)
  - depends-on: 6.1
  - resolves-upstream: #177 (partial)
- Issue 6.3: File plan-050's coarse tracker **and add its `tracker` row to the Upstream Issues table** (Resolved By 6.3). That row is the ONLY row in this plan that may carry `tracker`: `_tracker_url_from_plan_md`'s `_TRACKER_ROW_RE.search()` takes the FIRST match, so a second `tracker` row would stamp this plan's epic with another plan's URL. It is also SC10's one real `tracker` instance rather than a synthetic case.
  - depends-on: 6.1
- Issue 6.4: Post the drafted comments **and perform the closes** the generated grant enumerates — the omitted `include` close is the exact defect #178 was filed for, and plan-048 halted its own reconcile on it. Generate the grant with the Issue 3.2a verb.
  - depends-on: 3.2a, 6.2, 6.3
- Issue 6.5: Author `references/handoff-051.md` from this plan's own tables — every `partial`/`deferred` row and every unmet `Discharged-by` — **plus an explicit "descoped SPEC amendments" section** naming the M9 stamping REQ and Epic 5's two REQ amendments, sourced from **D-9**. Those ids appear in no table, so a tables-only generator would silently drop exactly what plan-051 needs (pass-6 C60).
  - depends-on: 6.4
- Issue 6.6: Deploy at land-the-plane. Expect the AGENTS.md consent gate on the config half; `--allow-permissions-write` is a **separate** operator authorization and must be requested, never assumed.
  - depends-on: 6.5

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: every control in this plan was observed RED before its fix
- Type: auto
- gate_type: auto · test_class: probe · cwd: repo-root
- Condition: for each control shipped by Epics 1-3 **and 7**, TWO observations are recorded in assets/red-prework.md, by two different verbs — the **ordering is enforced by the `depends-on` edges** (1.1→1.2/1.3, 2.1→2.2, 3.1→3.2), not by anything in the records, which assert the exit-code distinction only (pass-8 C83; C69 removed the vacuous hash check) — `redcheck.sh record-red` observed a non-zero exit on the RED fixture against the UNFIXED code (issues 1.1, 2.1, 3.1, 7.1), and `redcheck.sh assert-distinguishes` then observed a zero exit on the GREEN fixture against the FIXED code (issues 1.2/1.3, 2.2, 3.2a, 7.2/7.3). The zero-on-GREEN half cannot exist before the fix lands, which is why it is attributed to the post-fix issues and not to the fixture issues. Every named producer is an ANCESTOR of what this gate blocks and NONE is in its Blocks set; the blocked issues 1.4, 2.4 and 3.4 are VERIFICATION issues that consume this evidence rather than produce it (pass-5 C38)
- Test: bash docs/plans/plan-050-james-dixson-d0414b/assets/gate-run.sh docs/plans/plan-050-james-dixson-d0414b/assets/redcheck.sh verify-all
- Blocks: 1.4, 2.4, 3.4, 7.4
- Instructions: exit 0 = every control distinguished RED from GREEN; 1 = at least one did not; 2 = the harness could not run. A 2 leaves the gate UNRESOLVED — repair the harness rather than reading it either way. This gate is the plan's own instance of the M11 probe-before-dependent-work pattern. The `gate_type`/`test_class`/`cwd` line above uses plan-045's spelling because that is the only spelling any surface recognises; **no parser reads it today** (`plan_extract` gate objects carry no such field), so it is read **by hand at pour** to decide the sweep class — declared, not enforced, and named as such per D-8. **The 0/1/2 mapping above is likewise interpreted by the resolving agent, not by an engine**: no gate-`Test` executor exists in `plan_manager.py`. Disclosing one half and not the other is what pass-6 C66 caught, and C40 died on exactly this distinction.

### Capability Gate: Upstream write
- Type: human
- Approvers: operator
- Condition: the operator has authorized filing the tracker and posting the comments
- Test: test -f docs/plans/plan-050-james-dixson-d0414b/assets/upstream-authorization.txt
- Blocks: 6.3, 6.4
- Instructions: outward-facing writes require explicit authorization. Generate the grant with the Issue 3.2a verb and reconcile it against the Upstream Issues table before presenting it — this plan ships the fix for the exact defect that would otherwise apply here.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Condition: every execution bead under this plan's epic is closed, so reconciliation cannot run against incomplete work
- Test: bd list --all --include-gates --limit 5000 --json | jq -e '[.[] | select(.metadata.plan == "plan-050-james-dixson-d0414b")] as $p | ($p | length > 0) and ([$p[] | select(.status != "closed")] | length == 0)'
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | A fix ships as prose with no exit code, reproducing the very class this plan addresses | high | D-4 plus the Epic-0 gate: every control is observed RED before its fix lands. The one genuinely unenforceable item (#182's rule text) is declared as such under D-8 rather than implied to be enforced |
| R2 | `doc_lint`'s new verdicts perturb selection, invalidating plan-048's and plan-049's corpus figures | high | Issue 2.2 changes reportability only; Issue 2.3 re-measures `files_checked` and treats any movement as a failure |
| R3 | The plan widens into yf-plan's close chain and grows the way plan-047 did (78 issues) | med | Scope is fixed at four fixes (#178-#181), narrowed from six by the D-9 split. #177 was **removed** on evidence (D-6) rather than retained out of momentum; the 14 unaddressed classes and M11 are named out of scope in the Approach |
| R4 | A numeric figure in this plan is inherited rather than measured, and is stale by execution | med | D-5. Every figure in the Investigation Findings table was measured in this session; research 004's cross-repo counts are cited as its figures, never as this repo's |
| R5 | Fixing the wrapper-close at the pour seam masks a real cascade failure | med | Issue 1.2 explicitly forbids weakening `_bead_is_terminal`; **Issue 1.1's negative control `neg-179-open-wrapper`** asserts the cascade still fails on a genuinely open child, before and after the fix |
| R6 | The grant generator and `_verify_row` drift apart over time | med | Issue **3.2a**'s `grant` verb is the consumer (3.2 creates the table); both it and `_verify_row` read the one table, so a divergence requires editing that table. Raised low→med and the wording corrected to the measured claim: pass-3 C12 found `_verify_row` returns no `required_action` at all today, so "structurally impossible" was untested inference about code that does not yet exist. SC8 makes the read behavioral rather than inferred |

## Success Criteria

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | Every `REQ-*` for a behaviour change in this plan landed before its implementation issue closed | the SPEC commit is checked against an ENUMERATED id list, not against 0.1's prose — one landed `REQ-*` each for: the wrapper close (#179), the §6.4 ordering constraint (#180), `doc_lint`'s new verdicts (#181), and the grant generator (#178) — **four** new ids, each named — **plus the `REQ-DATA-024` amendment** for the verdict vocabulary (pass-8 C78); plus git log order putting that commit before each implementing commit. The M9 and Epic-5 ids left with the D-9 split | 0.1 |
| SC2 | Every control shipped by Epics 1-3 and 7 was observed RED on a fixture, with the RED recorded by an issue that is a `depends-on` ANCESTOR of the fix | `assets/red-prework.md` records a `record-red` non-zero exit per control, with the command; the "before the fix" ordering is carried by the DAG edges 1.1→1.2/1.3, 2.1→2.2, 3.1→3.2 and not by any timestamp (pass-8 C83) | 0.2, 1.1, 2.1, 3.1, 7.1 |
| SC2b | Every control was then observed GREEN, and the two observations are distinct records | for each id in `assets/controls.txt`, `assets/red-prework.md` carries a `record-red` record with a **non-zero** exit and an `assert-distinguishes` record with a **zero** exit — `redcheck.sh verify-all` asserts exactly this and exits 0/1/2. The claim is the exit-code distinction, **not** a temporal ordering: pass-7 C69 measured the HEAD-hash ordering check as vacuous when the fix is uncommitted. Pass-5 flagged this half as having no criterion at all | 1.2, 1.3, 2.2, 3.2a, 7.2, 7.3, 1.4, 2.4, 3.4, 7.4 |
| SC3 | The start-gate wrapper closes without a hand-written `close_reason` | pour a molecule, resolve the gate, assert the wrapper is `closed` with the generated reason | 1.2 |
| SC4 | An open wrapper still drives cascade-close RED after the fix | running `neg-179-open-wrapper`'s scenario, **`close_cascade.py` itself exits non-zero** both before and after 1.2 — it is invariant by design and is NOT a redcheck control (pass-7 C67); `_bead_is_terminal` is unmodified (`git diff` empty for that function) | 1.1, 1.4 |
| SC5 | The §6.4 ordering constraint fails loudly when violated | run `close-reconcile-step` with the reconcile gate unresolved; assert non-zero | 1.3, 1.4 |
| SC6 | The classifier separates four states that the lint reports identically, and the lint itself is untouched | `classify --path AGENTS.md` → `not-selected`, exit 1; `--path docs/plans/NO-SUCH/plan.md` → `no-such-path`, exit 1; `--path <an empty selected file>` → `empty`, exit 1; `--path docs/plans/plan-049-.../plan.md` → `selected`, exit 0. **And** `--root <a bundle copied outside docs/plans/>` → `not-selected`, which is #181's *titled* scenario and the arm both rejected scopes left silent. Separately assert the lint path is byte-unchanged: `uv run _shared/test_doc_lint.py` → `all passed` with **no edit to that file** | 2.2, 2.4 |
| SC6b | The classifier has a caller with an exit code | `DOC-LINT.md`'s on-edit rule invokes `classify` and branches on its exit, rather than instructing an agent to parse `files_checked`. A classifier nothing calls would leave #181 open and be this plan's own M5 vacuity | 2.2a |
| SC7 | The verdict change perturbed no selection, against a baseline captured BEFORE the change | corpus `files_checked` before and after are **equal**, measured with `--exclude` over this plan's own bundle per the #135 self-exclusion mechanism plan-049 shipped; any delta is a failure | 0.2a, 2.3 |
| SC8 | The grant generator and the reconcile verifier consume one requirement table | every literal in `UPSTREAM_DISPOSITIONS` has exactly one table entry; and the read is asserted BEHAVIORALLY — mutate one entry in a throwaway copy of the table, re-run `grant` and `_verify_row`, and assert **both** verdicts change. A table that exists and is ignored fails this, where an existence check or an import check passes it (pass-3 C12 measured the import form as undetecting). Run **with `_gh_issue_view` stubbed to a fixed payload**, so the mutation is the only variable and the assertion needs no network: `_verify_row` calls it unconditionally as its first act and returns `inconclusive` BEFORE consulting any table, which would make both verdicts identical for a reason unrelated to the property (pass-5 C47). Mutate the `include` entry, which the fixture exercises | 3.2, 3.2a |
| SC9 | plan-048's omitted-`#172` grant is rejected | the recorded historical grant drives the round-trip check non-zero | 3.1, 3.2a, 3.4 |
| SC10 | Every disposition is covered, including `exclude`, `deferred` and `tracker` | one case per literal in `UPSTREAM_DISPOSITIONS` (`plan_manager.py:3911`); The requirement is about the **shared table's entry set and the `grant` verb's coverage**, NOT about `_verify_row`'s behaviour: `verify-reconcile` filters `exclude` rows out before `_verify_row` ever sees one (the `r["disposition"] not in ("", "exclude")` comprehension in `verify_reconcile`), and REQ-CLI-018 specifies that filter. `_verify_row`'s non-`exclude` filter is **unchanged by this plan** — amending it would need a fifth REQ in 0.1, which pass-6 C55 caught this criterion quietly implying. **Five** of the six are REAL rows in this plan's own table rather than synthetic — `include`, `partial`, `deferred`, `exclude` (#113, #183) and `tracker` (the row 6.3 adds); only `supersede` is synthetic, because `_verify_row` requires it CLOSED as NOT_PLANNED and no issue here satisfies that | 3.3, 6.3 |
| SC21 | Every extracted title matches its source line verbatim, code spans included | `ctl-186-masked-title` exits non-zero pre-fix and zero post-fix; measured upstream at 4 of 35 titles blanked | 7.1, 7.2 |
| SC22 | Masking still suppresses a `depends-on:` written inside a code span | the parsing behaviour `plan_extract.py:142` describes is unchanged — a code-span `depends-on:` produces no edge. The fix must not trade one silent corruption for another | 7.4 |
| SC23 | Each extracted issue carries its continuation prose in a `detail` field | `ctl-187-empty-detail` exits non-zero pre-fix and zero post-fix; a bead poured from the output has a non-empty description | 7.1, 7.3 |
| SC24 | The fix is measured on this plan's own bundle | re-extract plan-050 and record the title/detail delta — its own titles use inline code throughout | 7.5 |
| SC15 | The FULL validation tier passes over the merged tree | `validate-merged` reports 0 failures | 6.1 |
| SC16 | #177's refutation is recorded upstream so the next attempt does not rebuild the scanner | the posted comment carries EXP-001's measurement and the full plan id | 6.2 |
| SC17 | Every upstream row reached the end state its disposition requires | `verify-reconcile --json`: assert `.verdict == "pass"`, **or** `.verdict == "inconclusive"` with the inconclusive rows being exactly the one `tracker` row 6.3 adds. Exit 0 alone is insufficient — only `fail` halts (`verify_reconcile`'s `if verdict == "fail": sys.exit(1)`), so `inconclusive` also exits 0, and the `tracker` row returns `inconclusive` by construction (REQ-CLI-018). Pass-6 C56: a criterion not checked against the engine that scores it is #173's class, inside the plan that lists #173 | 6.3, 6.4 |
| SC18 | The handoff names every unmet `Discharged-by`, every `partial`/`deferred` row, and the descoped SPEC amendments | the table-derived sections are checked by **regenerating them from plan.md's tables and `diff`ing against the shipped file — a non-empty diff fails**. "Generated, not hand-listed" is a provenance claim with no exit code (pass-7 C76); the content assertion is equivalent and checkable. the "descoped SPEC amendments" section is sourced from **D-9** and is explicitly EXEMPT from the tables-only rule, because those ids appear in no table (pass-6 C60) | 6.5 |
| SC19 | plan-050's coarse tracker exists and carries the full plan id | `gh issue view` on the filed tracker; body contains `plan-050-james-dixson-d0414b` | 6.3 |
| SC20 | The deploy ran, and `yf --version` equals HEAD **or** the documented pre-commit-hash case is recorded with its reason | `yf --version` vs `git rev-parse --short HEAD`. AGENTS.md documents the benign case: `build.rs` re-runs only on changes under `yf/` or `skills/`, and Issues 6.2-6.5 commit only under `docs/plans/`, so a rebuild may legitimately carry the pre-commit hash (pass-8 C85). A mismatch is acceptable ONLY with that reason recorded in `log.md` **and** `git diff --name-only <base>...HEAD` touching nothing under `yf/` or `skills/` — one command, so the exemption is checkable rather than merely assertable (pass-9 C91). An unexplained mismatch fails. The consent-gate outcome is recorded either way | 6.6 |
