---
type: Plan
okf_spec: OKF-PLAN
id: plan-050-james-dixson-d0414b
author: james-dixson
created: '2026-08-20'
status: review
---
# Plan: Fix the five process defects this session's plans demonstrably hit (#178-#182), and make the plan-to-plan remediation edge attributable (research 004's top-ranked class M9)

**ID:** plan-050-james-dixson-d0414b
**Author:** james-dixson
**Created:** 2026-08-20
**Status:** review

## Objective
Fix the five process defects this session's plans demonstrably hit (#178-#182), and make the plan-to-plan remediation edge attributable (research 004's top-ranked class M9)

Two deliverables, deliberately narrow:

1. **The five filed defects** — each was hit, diagnosed and worked around by hand during
   plan-047/048/049. (#177 was scoped in and then **dropped on evidence**; see D-6.) They are not hypotheses; every one has a reproduction in a bundle on
   `main`.
2. **M9** — research 004's top-ranked class: the remediation relationship between two plans
   exists nowhere except Motivation prose. **Research 004** measured **0 of 53** `discovered-from`
   edges connecting two plan epics **across its five-repo corpus**; re-measured locally (EXP-004),
   this repo has **26** such edges, **0** of them attributable to a plan on either endpoint.

Explicitly NOT in scope: the M11 probe mechanism, the remaining 14 ranked classes, and
escape-rate measurement (#145).

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
| [#178](https://github.com/dixson3/yoshiko-flow/issues/178) | generate the upstream-write authorization grant FROM the Upstream Issues table | include | **D-1.** plan-048 halted its own reconcile on an omitted `include` close. plan-049 avoided it only because the operator derived the grant by hand | 3.2 |
| [#179](https://github.com/dixson3/yoshiko-flow/issues/179) | the start-gate wrapper task is orphaned at pour and blocks cascade-close | include | **D-1.** Hit by plan-048 and plan-049. Forecast to plan-049's executor at launch and hit anyway | 1.2 |
| [#180](https://github.com/dixson3/yoshiko-flow/issues/180) | close-reconcile-step requires the reconcile gate resolved first — undocumented chain ordering | include | **D-1.** Same two plans, same forecast-and-hit | 1.3 |
| [#181](https://github.com/dixson3/yoshiko-flow/issues/181) | doc_lint: a bundle outside `docs/plans/` returns a silent green, indistinguishable from clean | include | **D-1.** `--path` on an unselected file returns `files_checked: 0, verdict: PASS` — byte-identical to a nonexistent path | 2.2 |
| [#184](https://github.com/dixson3/yoshiko-flow/issues/184) | §3: the red-team is never dispatched as a sub-agent — the drafter reviews its own draft | include | **Folded in after pass-3.** Measured this session: passes 1-2 were main-session (compliant with §3 as written) and advanced the plan to `ready-for-approval`; the first **independent** pass returned REVISE with 11 concerns, 2 high, including a deliverable whose criterion could not fail. `doc_lint`/`plan_extract`/`audit` were green throughout | 5.3 |
| [#182](https://github.com/dixson3/yoshiko-flow/issues/182) | red-team: the read-only rule forbids the sandbox spike that catches specification defects | include | **D-1.** plan-049 pass-4 built the deliverable in scratch space and got `files_checked: 0`; four prior passes read the same issue and saw nothing | 5.1 |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | M5/M9: process rules that nothing executes, and remediation edges that exist only in prose | partial | **D-2.** **IN:** M9 — the remediation edge becomes machine-recorded. **OUT:** M5's general prose-binding axis, which is the M11 mechanism this plan descopes | 4.2 |
| [#150](https://github.com/dixson3/yoshiko-flow/issues/150) | research 004: process-defect mining across 83 plan bundles | partial | **D-2/D-3.** **IN:** M9, plus the six filed defects as worked instances. **OUT:** the remaining 14 ranked classes and the M11 probe mechanism | 4.3, 6.2 |
| [#173](https://github.com/dixson3/yoshiko-flow/issues/173) | success criteria and upstream dispositions are never checked against the engine that enforces them | partial | Adjacent to #177 and #178 — both are instances of it. The general cross-check stays open | 6.2 |
| [#174](https://github.com/dixson3/yoshiko-flow/issues/174) | a review-phase validation pass — falsify every criterion, cross-check every claim against the code that scores it | partial | #177 and #182 close named sub-cases; the general falsification pass stays open | 6.2 |
| [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | New skill: yf-retrospective — measure escape rate and enforce a fix+prevention contract | deferred | **D-3.** Own plan. The emit side already exists and is accumulating; a consumer built now reads a thin corpus | |
| [#113](https://github.com/dixson3/yoshiko-flow/issues/113) | add an execution-rehearsal review pass (topological DAG walk against running state) | exclude | Different axis — DAG rehearsal, not defect detection | |

## Scope Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-1 | **The spine is the six session-filed defects (#177–#182)**, not research 004's M11 probe mechanism. | Operator-selected. Each has a reproduction on `main` rather than a hypothesis, and each was hit by more than one plan. M11 is better-evidenced *as a general prescription* but would be built against no local failing instance — the shape #177 itself warns about. |
| D-2 | **Include M9** — make the remediation edge between two plans machine-recorded. | Operator-selected. Top-ranked class (4/4 repos, 5 clusters) and the reason research 004's counts are lower bounds rather than prevalences. Compounds: every future analysis inherits the blind spot. |
| D-3 | **Defer escape-rate measurement (#145).** | Operator-selected. A whole new skill; the `plan-retrospective.md` emit side already exists and is accumulating entries, so a consumer built today would read a thin corpus. |
| D-4 | **Every fix must ship with a demonstrated failing case** — the control is shown RED before it is trusted GREEN. | Not a style preference. plan-047 found six controls that reported clean while checking nothing; plan-048's R3 shipped broken twice over a clean corpus; plan-049's EXP-002 measured its own safety postcondition *passing* the replay it was written to catch. `_shared/test_dag_guard.py`'s mutant suite is the inherited template. |
| D-5 | **Re-measure every figure inherited from research 004 or from #177–#182 before use.** | Carried from plan-048 D-5 and plan-049 D-7, both of which caught a stale inherited literal at execution. Research 004 states its own counts are lower bounds over a recorded subset — citing one as a prevalence would reproduce M9 inside the plan meant to fix it. |
| D-6 | **Drop #177 from the deliverable** after EXP-001 refuted it; comment the refutation upstream instead. | Operator-selected on the finding. The tractable form is a producer-side *citation* contract, not the detector the issue asks for — a different deliverable with its own design. Shipping the naive scanner would put a control in the repo that misses the exact two cases that motivated it: R4's "ships unable to fail" class, which D-4 forbids. |
| D-7 | **M9 is forward-only stamping.** Stamp `metadata.plan` on `discovered-from` beads at creation; leave the 26 historical edges unattributed and say so. | Operator-selected. EXP-004 measured the edges as intact and resolvable — only attribution is missing — so the producer fix is one seam. Backfilling is 26 hand adjudications, and plan-049's SC31/SC23 are a fresh reminder that hand-adjudicated populations expand under contact. |
| D-8 | **#182's fix ships with an honest non-mechanical status.** | EXP-006 measured the rule as one line of agent prose. There is no exit code for "a reviewer obeyed a rule". The verifiable claim is source↔deployed **parity** (class M3), and the plan says that rather than implying the prose itself is enforced — which would be the M5 vacuity this plan is nominally about. |

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
| [EXP-001](findings/exp-001-target-derivability.md) | **REFUTED** → #177 dropped (D-6) | The naive scanner found 6 numeric targets in 101 SC rows — and **missed plan-049's SC31 and SC23**, the two cases #177 was filed about. A control that cannot fire on its own motivating instances |
| [EXP-002](findings/exp-002-close-chain.md) | **CONFIRMED**, and stronger than filed | **49 of 49** start-gate wrapper beads closed **by hand**, each with a different improvised `close_reason`. Not intermittent — a universal manual step with no mechanism |
| [EXP-003](findings/exp-003-silent-green.md) | **CONFIRMED** | A nonexistent path and a real-but-unselected file both return `files_checked: 0, verdict: PASS` — **byte-identical**. Three states, one verdict |
| [EXP-004](findings/exp-004-m9-remediation-edge.md) | **CONFIRMED, premise revised** | 26 `discovered-from` edges, **0 with plan attribution on either endpoint**. The edges are intact and resolvable; only attribution is missing, so M9 is a stamping gap, not a missing relationship |
| [EXP-005](findings/exp-005-grant-generation.md) | **CONFIRMED, cheaper than filed** | The disposition→end-state map already exists at `plan_manager.py:2012` (`_verify_row`). A generator can call the **same function that verifies its output**, so the two cannot drift |
| [EXP-006](findings/exp-006-red-team-rule.md) | **CONFIRMED, narrowed** | The rule is **one line** (`red-team.md:63`) and says "never writes files" — it never forbids a spike at all. The defect is under-specification; silence read as prohibition |

**Two findings changed the plan's own scope**, which is why they were run before drafting:
EXP-001 removed a deliverable (D-6) and EXP-004 replaced M9's premise (D-7). A third, EXP-006,
removed the plan's ability to claim #182 is mechanically enforced (D-8).

## Approach

**Five fixes and one producer change, each landing with a control that was shown RED first.**

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
- Issue 0.1: Land the `REQ-*` requirements for every behaviour change in this plan — the wrapper-close contract (#179), the §6.4 chain ordering constraint (#180), `doc_lint`'s two new verdicts (#181), the grant generator (#178), and the `discovered-from` stamping rule (M9). SPEC-first per AGENTS.md: no implementation issue below may start before this closes.
- Issue 0.2: Build `assets/redcheck.sh` — a harness that runs a named fixture against a named control and asserts the control exits **non-zero** on the RED fixture and **zero** on the GREEN one, appending each observation to `assets/red-prework.md`. Exit contract: 0 = both observed as specified, 1 = the control failed to distinguish them, 2 = the harness could not run. Also ship `assets/gate-run.sh`, the 0/1/2 normalising wrapper plan-049 used, so a missing or crashing harness reports **2 (INCONCLUSIVE)** rather than bash's raw 127.
  - depends-on: 0.1
- Issue 0.2a: Capture SC7's **baseline** before any Epic-2 change: record the corpus `files_checked` with the exact `--exclude` invocation that self-excludes this plan's bundle, into `assets/`. Measured at drafting for reference: 817 unfiltered, **757** excluded — re-measure at execution per D-5, never copy this number.
  - depends-on: 0.1

### Epic 1: The close chain (#179, #180)
- Issue 1.1: Author both fixtures and run them against the **unfixed** code: a poured molecule with an open start-gate wrapper must drive `close_cascade.py` non-zero, and `close-reconcile-step` with the reconcile gate unresolved must drive the ordering assertion non-zero. Record both RED observations.
  - depends-on: 0.2
- Issue 1.2: Close the start-gate wrapper task in the same step that resolves the gate, with one generated `close_reason`. Fix at the pour/resolve seam per EXP-002 — **do not** weaken `close_cascade.py`'s `_bead_is_terminal`, which is reporting correctly.
  - depends-on: 1.1
  - resolves-upstream: #179 (include)
- Issue 1.3: Document and enforce the §6.4 chain ordering constraint that `close-reconcile-step` requires the reconcile gate resolved first — as an ordering assertion with an exit code, not a prose note.
  - depends-on: 1.1
  - resolves-upstream: #180 (include)
- Issue 1.4: Re-run both fixtures against the fixed code and record the GREEN observations. Assert `_bead_is_terminal` is unmodified.
  - depends-on: 1.2, 1.3

### Epic 2: The silent green (#181)
- Issue 2.1: Author the fixture — a bundle copied outside `docs/plans/` — and run it against the **unfixed** `doc_lint`, recording the byte-identical PASS that EXP-003 measured. Record the RED observation.
  - depends-on: 0.2
- Issue 2.2: Add the distinguishing verdicts to `doc_lint.py` so an unselected path and a nonexistent path stop being byte-identical to a clean one. Reuse the existing 0/1/2 gate vocabulary rather than inventing a fourth. Selection semantics are **unchanged** — only their reportability.
  - depends-on: 2.1
  - resolves-upstream: #181 (include)
- Issue 2.3: Re-measure the corpus `files_checked` figure after the verdict change and record whether it moved. A change would mean selection was perturbed, which 2.2 forbids.
  - depends-on: 2.2
- Issue 2.4: Re-run the fixture and record the GREEN observation.
  - depends-on: 2.2

### Epic 3: The upstream grant (#178)
- Issue 3.1: Author the fixture from plan-048's **actual** recorded grant with the `#172` close omitted, and run it against the unfixed path to record the RED observation — a real recorded failure, not a synthetic one.
  - depends-on: 0.2
- Issue 3.2: Extract the per-disposition **requirement** out of `_verify_row`'s branch conditions into a shared table keyed by the `UPSTREAM_DISPOSITIONS` literals, and make `_verify_row` read it. Pass-3 C12 measured why the original design was unworkable: `_verify_row` returns `{detail, disposition, issue, verdict}` with **no `required_action`**, is **network-bound** (`gh issue view` per row), and returns `fail: "unrecognised literal"` when handed an `exclude` row directly — for a literal that IS in the frozenset.
  - depends-on: 3.1
- Issue 3.2a: Ship the `grant` verb on top of that shared table, so generator and verifier consume one source. It emits a **proposal** from local plan content; it never writes the authorization file, and it must not require network to generate.
  - depends-on: 3.2
  - resolves-upstream: #178 (include)
- Issue 3.3: Cover every disposition including `deferred` and the `tracker`/inconclusive case. A generator silently omitting a disposition is #181's defect class in a new place.
  - depends-on: 3.2
- Issue 3.4: Re-run the fixture and record the GREEN observation.
  - depends-on: 3.2

### Epic 4: M9 attribution (#149)
_Re-scoped after pass-3 C10 measured that no `discovered-from` **producer** exists in code — every code reference is a consumer, and the only producers are prose (`coordinator.md:279`, `yf-research/spec/phases.md:24`). The deliverable is therefore the **detector at a real seam**, not a prose edit._
- Issue 4.1: Author the two-sided fixture and run it against the **unmodified** `beads_hygiene.py`: an unstamped `discovered-from` bead must be reported, a stamped one must not. Against today's code neither is reported, so both halves are RED. Record both observations.
  - depends-on: 0.2
- Issue 4.2: Add the check to `beads_hygiene.py audit` — a `discovered-from` bead created after a recorded cutoff with no `metadata.plan` is a finding. The cutoff makes D-7's forward-only scope mechanical rather than aspirational, and keeps the 26 historical edges out of the input set by construction.
  - depends-on: 4.1
  - resolves-upstream: #149 (partial)
- Issue 4.3: Wire the check into a **named runnable surface** — a `CHANGE-VALIDATION.md` §1 recipe row with an id, so it has an exit code and a caller. A check with no host is the M5 vacuity this plan exists to end.
  - depends-on: 4.2
- Issue 4.4: Update the two producer prose sites to stamp `metadata.plan`, and state in the plan that this half is **supporting, not load-bearing** — it has no exit code, and Issue 4.3's check is what makes the rule real. Same honest treatment D-8 gives #182.
  - depends-on: 4.2
- Issue 4.5: Re-run the fixture GREEN against the fixed code, and record the re-measured count of pre-existing unattributed edges as explicitly **not** backfilled (D-7), with the cutoff value used.
  - depends-on: 4.3, 4.4

### Epic 5: The red-team rule (#182)
- Issue 5.1: Rewrite `agents/red-team.md:63` — scope the prohibition to the repository under review, and explicitly authorize a sandbox spike with the worked `mktemp -d` example. Keep REQ-AGENT-043's authorship rule verbatim.
  - depends-on: 0.1
  - resolves-upstream: #182 (include)
- Issue 5.2: Add the source↔deployed parity check for the rewritten rule (class M3). State in the plan that the prose itself has no exit code (D-8) — the verifiable claim is parity and clause presence, never reviewer obedience.
  - depends-on: 5.1
- Issue 5.3: Make `SKILL.md` §3 **dispatch** the red-team and conformance reviewers as sub-agents via `Agent`, symmetric with §2's "Spawn a sub-agent per unknown". State that a main-session review is not a conformant substitute, because independence is the mechanism — not thoroughness. The agents stay read-only per REQ-AGENT-043; the main session still writes `reviews/pass-N.md`.
  - depends-on: 5.1
  - resolves-upstream: #184 (include)
- Issue 5.4: Add the parity/consistency assertion for §3 — the review step's prose must name `Agent` wherever it names an `agents/*.md` role file, so the §2/§3 asymmetry cannot silently return.
  - depends-on: 5.3

### Epic 6: Reconcile and land
- Issue 6.1: Run the FULL validation tier over the merged tree and record the result.
  - depends-on: 0.2a, 1.4, 2.3, 2.4, 3.3, 3.4, 4.5, 5.2, 5.4
- Issue 6.2: Draft the upstream comments, including **#177's refutation** — EXP-001's measurement, so the next attempt does not rebuild the same inadequate scanner — and #149's corrected framing (the edges exist; only attribution is missing).
  - depends-on: 6.1
  - resolves-upstream: #177 (partial)
- Issue 6.3: File plan-050's coarse tracker.
  - depends-on: 6.1
- Issue 6.4: Post the drafted comments per the grant generated by the Issue 3.2 verb.
  - depends-on: 6.2, 6.3
- Issue 6.5: Author `references/handoff-051.md` from this plan's own tables — every `partial`/`deferred` row and every unmet `Discharged-by`.
  - depends-on: 6.4
- Issue 6.6: Deploy at land-the-plane. Expect the AGENTS.md consent gate on the config half; `--allow-permissions-write` is a **separate** operator authorization and must be requested, never assumed.
  - depends-on: 6.5

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: every control in this plan was observed RED before its fix
- Type: auto
- Test-class: probe
- Condition: for each control shipped by Epics 1-4, `redcheck.sh` observed a non-zero exit on the RED fixture and zero on the GREEN one, recorded in assets/red-prework.md by the per-epic fixture issues 1.1, 2.1, 3.1 and 4.1, each of which is an ANCESTOR of the issues this gate blocks and is deliberately outside its Blocks set
- Test: bash docs/plans/plan-050-james-dixson-d0414b/assets/gate-run.sh docs/plans/plan-050-james-dixson-d0414b/assets/redcheck.sh
- Blocks: 1.4, 2.4, 3.4, 4.3
- Instructions: exit 0 = every control distinguished RED from GREEN; 1 = at least one did not; 2 = the harness could not run. A 2 leaves the gate UNRESOLVED — repair the harness rather than reading it either way. This gate is the plan's own instance of the M11 probe-before-dependent-work pattern.

### Capability Gate: Upstream write
- Type: human
- Approvers: operator
- Condition: the operator has authorized filing the tracker and posting the comments
- Test: test -f docs/plans/plan-050-james-dixson-d0414b/assets/upstream-authorization.txt
- Blocks: 6.3, 6.4
- Instructions: outward-facing writes require explicit authorization. Generate the grant with the Issue 3.2 verb and reconcile it against the Upstream Issues table before presenting it — this plan ships the fix for the exact defect that would otherwise apply here.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Condition: every execution bead under this plan's epic is closed, so reconciliation cannot run against incomplete work
- Test: bd list --all --include-gates --limit 5000 --json | jq -e '[.[] | select(.metadata.plan == "plan-050-james-dixson-d0414b") | select(.status != "closed")] | length == 0'
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | A fix ships as prose with no exit code, reproducing the very class this plan addresses | high | D-4 plus the Epic-0 gate: every control is observed RED before its fix lands. The one genuinely unenforceable item (#182's rule text) is declared as such under D-8 rather than implied to be enforced |
| R2 | `doc_lint`'s new verdicts perturb selection, invalidating plan-048's and plan-049's corpus figures | high | Issue 2.2 changes reportability only; Issue 2.3 re-measures `files_checked` and treats any movement as a failure |
| R3 | The plan widens into yf-plan's close chain and grows the way plan-047 did (78 issues) | med | Scope is fixed at five fixes plus one producer change. #177 was **removed** on evidence (D-6) rather than retained out of momentum; the 14 unaddressed classes and M11 are named out of scope in the Approach |
| R4 | A numeric figure in this plan is inherited rather than measured, and is stale by execution | med | D-5. Every figure in the Investigation Findings table was measured in this session; research 004's cross-repo counts are cited as its figures, never as this repo's |
| R5 | Fixing the wrapper-close at the pour seam masks a real cascade failure | med | Issue 1.2 explicitly forbids weakening `_bead_is_terminal`; **Issue 1.1's** open-wrapper RED fixture asserts the cascade still fails on a genuinely open child |
| R6 | The grant generator and `_verify_row` drift apart over time | low | Issue 3.2 consumes the shared requirement table rather than re-encoding its rules — there is one map, so drift is structurally impossible rather than merely unlikely |

## Success Criteria

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | Every `REQ-*` for a behaviour change in this plan landed before its implementation issue closed | git log order: the SPEC commit precedes each implementing commit | 0.1 |
| SC2 | Every control shipped by Epics 1-4 was observed RED on a fixture before its fix landed | `assets/red-prework.md` records a non-zero exit per control, with the command | 0.2, 1.1, 2.1, 3.1, 4.1 |
| SC3 | The start-gate wrapper closes without a hand-written `close_reason` | pour a molecule, resolve the gate, assert the wrapper is `closed` with the generated reason | 1.2 |
| SC4 | An open wrapper still drives cascade-close RED | the RED fixture exits non-zero; `_bead_is_terminal` is unmodified (`git diff` empty for that function) | 1.1, 1.4 |
| SC5 | The §6.4 ordering constraint fails loudly when violated | run `close-reconcile-step` with the reconcile gate unresolved; assert non-zero | 1.3, 1.4 |
| SC6 | A real-but-unselected path is distinguishable from a nonexistent one | `doc_lint --path AGENTS.md` and `--path docs/plans/NO-SUCH/plan.md` return different verdicts | 2.2, 2.4 |
| SC7 | The verdict change perturbed no selection, against a baseline captured BEFORE the change | corpus `files_checked` before and after are **equal**, measured with `--exclude` over this plan's own bundle per the #135 self-exclusion mechanism plan-049 shipped; any delta is a failure | 0.2a, 2.3 |
| SC8 | The grant generator and the reconcile verifier consume one requirement table | every literal in `UPSTREAM_DISPOSITIONS` has exactly one table entry, and `_verify_row` reads it — asserted on the table, **not** by an import, which pass-3 C12 measured as undetecting | 3.2, 3.2a |
| SC9 | plan-048's omitted-`#172` grant is rejected | the recorded historical grant drives the round-trip check non-zero | 3.1, 3.4 |
| SC10 | Every disposition is covered, including `exclude`, `deferred` and `tracker` | one case per literal in `UPSTREAM_DISPOSITIONS` (`plan_manager.py:3911`); `exclude` must not return `unrecognised literal` | 3.3 |
| SC11 | The attribution check distinguishes an unstamped bead from a stamped one | two-sided fixture: unstamped post-cutoff bead is **reported**, stamped bead is **not**; both observed RED before 4.2 lands. Replaces a pass-3-C10 criterion that could not fail — it was discharged by whoever created the bead | 4.1, 4.5 |
| SC12 | The unattributed historical population is stated, not silently left | `assets/` records the re-measured count of pre-existing unattributed `discovered-from` beads and the cutoff value | 4.5 |
| SC12b | The attribution check has a named caller with an exit code | a `CHANGE-VALIDATION.md` §1 row names it by id and the recipe runs it | 4.2, 4.3 |
| SC12c | The forward-only boundary is mechanical, not aspirational | the check reads a recorded cutoff; a pre-cutoff unstamped bead is **not** reported, a post-cutoff one **is** | 4.2 |
| SC12d | The producer prose is declared supporting, not load-bearing | the plan states the prose half has no exit code and names 4.3's check as what makes the rule real | 4.4 |
| SC13 | The red-team rule authorizes a sandbox spike and scopes the prohibition to the repo under review | the rewritten line contains both clauses and the worked example | 5.1 |
| SC14 | The deployed rule matches the repo source | parity check exits 0 across every installed copy | 5.2 |
| SC14b | §3 dispatches both reviewers via `Agent`, symmetric with §2 | the review step names `Agent` wherever it names an `agents/*.md` role file; asserted mechanically | 5.3, 5.4 |
| SC15 | The FULL validation tier passes over the merged tree | `validate-merged` reports 0 failures | 6.1 |
| SC16 | #177's refutation is recorded upstream so the next attempt does not rebuild the scanner | the posted comment carries EXP-001's measurement and the full plan id | 6.2 |
| SC17 | Every upstream row reached the end state its disposition requires | `verify-reconcile` exits 0 | 6.4 |
| SC18 | The handoff names every unmet `Discharged-by` and every `partial`/`deferred` row | generated from this plan's own tables, not hand-listed | 6.5 |
| SC19 | plan-050's coarse tracker exists and carries the full plan id | `gh issue view` on the filed tracker; body contains `plan-050-james-dixson-d0414b` | 6.3 |
| SC20 | The deploy ran and `yf --version` equals HEAD, with the config half authorized separately or not attempted | `yf --version` vs `git rev-parse --short HEAD`; the consent-gate outcome recorded in `log.md` | 6.6 |
