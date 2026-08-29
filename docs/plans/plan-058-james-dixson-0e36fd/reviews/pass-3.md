---
type: Review
okf_spec: OKF-PLAN
id: pass-3
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# Red-team pass 3 — plan-058-james-dixson-0e36fd
## Verdict: REVISE

Dispatched as an isolated sub-agent (REQ-AGENT-049). Read-only with respect to the repository; one
sandbox spike reproducing `check_gh_direct.py`'s blanking pass over `upstream.py` (removed, no
residue). The main session wrote this file.

## Strengths

- **Structural integrity is clean under a third expansion.** 37 issues (0:5, 1:9, 2:7, 3:9, 4:7),
  no cycles, no dangling references, R7 holds (only cross-edge `4.1 -> 1.1`), all six gates
  reachable, and the new 3.1c/3.7/gate introduced no graph regression.
- **The #268 critical-path claim is VERIFIED end to end.** Transitive closure of the three
  `resolves-upstream` tags touches only `0.1, 0.1b, 0.2` — never `1.7`, never Epic 4. Epics 1-3 can
  land and close #268 with both human gates unresolved.
- **7 of pass-2's 9 resolutions are real.** D9's two-clause gate Test is called out as a real fix.
- **The plan should NOT be split on size** — see the Missing/Item-4 assessment below.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| H1 | **high** | **Issue 3.1's unblanked-source `bd dep list` rule is RED ON CLEAN CODE.** Spike: after Issue 1.7 lands, the only occurrence of the literal `bd dep list` in unblanked source is **`upstream.py:664`** — `edge_type()`'s **docstring**. The check would exit 1 on the correctly-fixed tree, so the "Mechanical fan-out check green" gate **can never pass**, and the executor's only escape is deleting a docstring that `check_gh_direct.py`'s own design forbids erasing and that Issue 1.1 depends on keeping. Pass-2 diagnosed *under*-matching; the fix produced *over*-matching, and the other direction was never checked. |
| H2 | **high** | **Issue 3.1c's `deps_for` rule over-matches code Issue 1.7 does not remove.** Blanked-source hits for `deps_for`: `:686` (the **injected parameter** of `detect_followons`), `:709`, `:1005`, `:1069`. Issue 1.7 rewrites closure *bodies*; Issue 3.1's own text says `detect_followons` takes `deps_for` **injected** — so the name survives and a bare-name ban is red after 1.7 too. Pass-2's "spike-confirmed both match" tested only the positive direction. |
| H3 | **high** | **`Blocks: 4.1b` blocks the Pruning Authorization gate's OWN EVIDENCE.** The gate's Condition is "the operator has read Issue 4.1's measurements", but D3/D6 moved the load-bearing measurement — the 785 MB breakdown, the 109-archive DR analysis, the `git-remote-cache` finding — into 4.1b, which the gate now Blocks. **Beads are blocked whole**, so the Instructions' prose carve-out is something the mechanism cannot honour. It also drags `4.2 -> 4.1b` and everything downstream behind the gate: 5 of 7 Epic-4 issues, rather than the one destructive act. The plan already solved this exact problem once, by splitting 3.1c out of 3.1; the pattern was not applied here. |
| H4 | **high** | **The Follow-on activation gate has NO DECLINE BRANCH, so the plan cannot close if the operator says no.** Condition is stated purely as acceptance. Decline -> 1.7 never lands -> 3.1c and 3.7 permanently blocked -> SC3c/SC3d/SC6c undischargeable -> the Reconcile Gate (`auto (all execution beads closed)`) can never fire. The plan stalls on a **legal** outcome of a human gate. The Pruning Authorization gate encodes the right pattern one screen below ("OR accepts 'not warranted yet'"), and the new gate did not inherit it. |
| M1 | med | **D5's resolution is partly cosmetic — the falsified justification survives in two places.** "Exact"/"independent corroboration" were struck from Issue 1.8 but **not** from `findings/exp-002-...md:91-93`, which still reads "an **independent corroboration** … two unrelated fields … agreeing **exactly**". **R10 was never updated either** — it still says "which EXP-002 measured as exactly equal to the parent-child edge count". An executor reading R10 or EXP-002 implements the count-equality Issue 1.8 forbids. |
| M2 | med | **R11 contradicts the D3 fix.** It still says 4.1b evaluates `.beads/backup` "**ahead of** and **outside** the consent gate"; D3 moved that half behind it and `Blocks: 4.5, 4.1b` says so. |
| M3 | med | **SC9b carries two withdrawn figures and omits the one the plan added.** It names "Dolt GC (494 MB)" — demoted to a hypothesis bounded at ~105 MB — and omits `git-remote-cache` (118 MB), the one genuinely safe target. |
| M4 | med | **Issue 3.7 depends on 1.7, so a live shipped bug gets filed only if the operator consents.** Decline, and the `narrow`-always-empty defect is never filed. It also inverts D1's rationale: the filing meant to *inform* the decision lands *after* it. |
| M5 | med | **`--check-timeouts` needs the same enclosing-function tracking the plan flagged as unbudgeted for `external_for`.** The three legitimate `subprocess.run` sites (`:88`, `:109`, `:185`) are inside exactly the allowed functions, so "outside" requires scope tracking. SC4b rests on it. |
| M6 | med | **SC1b names a test no issue creates** (`push_reads_universe_once`) — pass-1 C6's exact class, reintroduced. Weaker instances: SC2b, SC3c, SC5b. |
| L1 | low | **SC8's verification does not check what its criterion claims** — greps only `REQ-BUP-071/072/073` while Discharged-by includes 4.4b (`REQ-HYG-*`) and 0.4 (§5 entries). |
| L2 | low | **SC10 is triple-inconsistent and stale** — criterion says "three", verification names two, and two new filings appeared (3.7, plus Issue 3.1's `check_gh_direct.py` vacuity filing, which **no issue owns**). |
| L3 | low | **R9 is stale** — "bans the three known *names*" predates the rule-by-rule rewrite. |
| L4 | low | **SC1 and SC3 share an identical verification command** with different Discharged-by sets; leftover from the D7 split. |
| L5 | low | **EXP-006 has no `git-remote-cache` entry**, so a cold reader following the citation gets the pre-D6 picture. |

## Missing

- A **positive** control per mechanical-check rule — the negative-control-only requirement cannot catch H1 or H2.
- An issue owning the `check_gh_direct.py` `FORBIDDEN_SUBSTRINGS` vacuity filing that Issue 3.1's own text calls for.
- A decline branch for the Follow-on activation gate.

### Item 4 — is the plan too big to execute as one unit?

**No split is needed, and the sequencing genuinely handles it — but only after H3 and H4 are fixed.**
Verified end to end: the #268 critical path crosses **no** capability gate, R7 holds mechanically,
and Epic 4 has exactly one edge into Epics 0-3 in the safe direction. "The 37-issue size is carried
by the dependency graph, not by an execution session's attention." The two things that could strand
it are structural, not scale: H4 (a decline leaves the plan un-closable) and H3 (a coarse `Blocks`
edge swallowing 5 of 7 Epic-4 issues plus its own evidence).

## Gate Assessment

| Gate | Reachable | Notes |
| :-- | :-- | :-- |
| Start Gate | yes | correct |
| Fan-out eliminated | yes | D9's two-clause Test is a real fix; evidence (1.4, 1.9) outside its Blocks |
| Mechanical fan-out check green | **no** | H1: its Test invokes a check that is red on clean code |
| Follow-on activation | approve-only | **no path to decline** (H4) |
| Pruning Authorization | **partially** | H3: blocks its own evidence; the prose carve-out is unenforceable at bead granularity |
| Reconcile Gate | **conditionally** | unreachable under an H4 decline |

## Upstream Assessment

Unchanged and sound. `#268` include-disposition correct; Resolved-By consistent with the tags. The
filing set is now **four** candidates (3.4, 3.5, 3.7, and the unowned `check_gh_direct` vacuity),
which SC10 does not track (L2).

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | high | **Accepted; confirmed at the source before redesigning.** `grep -n 'bd dep list' upstream.py` returns exactly one line — **`:664`, `edge_type()`'s docstring**. After Issue 1.7 the argv is gone and the docstring is the sole match, so the check would be red on correct code. **Resolution goes further than the recommendation: Issue 3.1 is now an AST check for ALL rules**, not a substring scanner with one AST exception. The rationale is recorded in the issue: substring matching failed in *both* directions across two cycles — blanked-token scanning **under**-matched (pass-2 D2), raw-source scanning **over**-matched (this concern) — and AST matches the construct while being blind to both comments and prose. The 'deliberate departure from the precedent' is dropped entirely. | `main-session` | `resolved` |
| H2 | high | **Accepted; confirmed at the source.** `deps_for` occurs at `:686` (the **injected parameter**), `:698` (docstring), `:709`, `:1005`, `:1069`. Issue 1.7 rewrites only the closure *bodies* at `:1001`/`:1065`, so a bare-name ban would forbid the injection seam that makes `detect_followons` testable. Issue 3.1c now bans the **construct** — a nested `FunctionDef` whose body calls `run`/`run_unchecked` with a per-bead argv — and the reasoning is written into the issue so it is not re-simplified later. | `main-session` | `resolved` |
| H3 | high | **Accepted, using the plan's own precedent.** Issue 4.1b is **split**: 4.1b keeps the measurement, the `git-remote-cache` reclamation and the Dolt-GC test (non-destructive, **ungated**), and new **Issue 4.1d** carries the `.beads/backup` DR-versus-space decision (destructive, gated). The gate is repointed to `Blocks: 4.5, 4.1d`. This applies exactly the 3.1c pattern the reviewer identified — and it is the right fix rather than better prose, because `Blocks` operates on **whole beads**, so no carve-out written in Instructions could ever have been honoured. The gate no longer blocks its own evidence, and Epic 4 goes from 5 of 7 issues gated to 2. | `main-session` | `resolved` |
| H4 | high | **Accepted — this was the most consequential structural catch of the pass.** The Follow-on activation gate now has an explicit **decline branch**: on decline, Issues 1.7 and 3.1c close as `wontfix-for-now`, Issue 3.7 files the defect regardless, and SC3c/SC3d/SC6c are marked **N/A**. The Instructions state plainly that a decline is a first-class outcome that must close the epic cleanly, and why — without it, refusing would strand three issues open and the `auto` Reconcile Gate could never fire, stalling the plan on a **legal** answer. Mirrors the Pruning Authorization gate's 'not warranted yet' pattern, which this gate should have inherited when it was written. | `main-session` | `resolved` |
| M1 | med | **Accepted; the pass-2 resolution overstated what it had done and this is the correction.** The passage was struck from Issue 1.8 only. Now also struck from `findings/exp-002` — the bullet is re-labelled **`withdrawn:`** (not `inferred:`) and states both halves are false, with the measured counterexample — and from **R10**, whose mitigation text now states the literal predicate and explicitly says it is *not* a count-equality check. Those were the two places an executor would actually have read. | `main-session` | `resolved` |
| M2 | med | **Accepted.** R11 rewritten to match what the plan now does: `git-remote-cache` outside the gate (Issue 4.1b), `.beads/backup` inside it (Issue 4.1d), with the pass-1/pass-2/pass-3 provenance recorded. | `main-session` | `resolved` |
| M3 | med | **Accepted.** SC9b restated around the three candidates in their true risk classes — safe-and-reclaimed, hypothesis-under-test with the win bounded near the 105 MB journal, and consent-gated DR-versus-space — with **no figure promised in advance**. The withdrawn '494 MB' is gone and `git-remote-cache` is named. | `main-session` | `resolved` |
| M4 | med | **Accepted, and the reasoning is now written into the issue.** Issue 3.7 depends on **1.1**, not 1.7. The issue records why: the defect is real and shipped regardless of consent, so making the filing downstream of the gate would let a decline bury a live correctness bug forever — and it inverts the filing's purpose, since it is **pre-read material for that very decision**. The gate's Condition now names it as pre-read. | `main-session` | `resolved` |
| M5 | med | **Accepted.** Enclosing-function tracking is declared **once**, as work, covering both rules that need it (`--check-timeouts` and the `external_for` restriction). The earlier draft budgeted it for one and silently assumed it for the other. The AST rewrite gives it for free by tracking the `FunctionDef` ancestor — the third independent reason for the H1 redesign. | `main-session` | `resolved` |
| M6 | med | **Accepted for all four instances.** Each SC-named test now has an owning issue that explicitly creates it: `push_reads_universe_once` -> Issue 1.6; `parent_without_edges_warns` -> Issue 1.8; `followons_no_per_bead_dep_list` -> Issue 1.7; `existing_labels_read_failure...` -> Issue 2.5. The recurrence of pass-1's C6 class is noted in Issue 1.6's text so the pattern is visible rather than merely fixed. | `main-session` | `resolved` |
| L1 | low | **Accepted.** SC8 is now scoped to what its grep actually checks (`REQ-BUP-071/072/073`, Discharged-by 0.1-0.3), and new **SC8b** carries the `REQ-HYG-*` and §5-entry obligations with its own verification and Discharged-by (0.4, 4.4b). | `main-session` | `resolved` |
| L2 | low | **Accepted, including the unowned filing.** New **Issue 3.8** owns the `check_gh_direct.py` `FORBIDDEN_SUBSTRINGS` vacuity filing that Issue 3.1's text called for and nothing owned. SC10 restated over the actual set of **four** filings (3.4, 3.5, 3.7, 3.8), so criterion, verification and Discharged-by now agree. | `main-session` | `resolved` |
| L3 | low | **Accepted.** R9 rewritten for the AST idiom, and it now cites the **paired** controls: two cycles produced one under-matching rule and one over-matching rule, which is precisely why both a negative and a positive control are required. | `main-session` | `resolved` |
| L4 | low | **Accepted.** SC1 and SC3 differentiated: SC1 is the **zero per-bead subprocess** claim (`-k zero_bd_show`), SC3 is the **scale-independence** claim (`-k scale_independence`, equal at 10 and 1,000 beads). Discharged-by sets corrected to match. | `main-session` | `resolved` |
| L5 | low | **Accepted.** EXP-006 carries an `AMENDED after review` block at the head of §5 recording all three corrections — backup is not rotatable, Dolt GC is a hypothesis, and `git-remote-cache` was **missed** — plus the process note that this experiment reasoned from `du -sh .beads/*`, which is why Issue 4.1b now begins by measuring the tree. | `main-session` | `resolved` |

## Outcome

All 15 concerns **resolved**. Both high concerns about the mechanical check (H1, H2) and both
structural gate defects (H3, H4) were re-verified at the source before redesigning.

The plan is now **39 issues / 6 gates**: new Issues 4.1d and 3.8, and Issue 3.1 rewritten from a
substring scanner to an **AST check**.

Three things this cycle changed that earlier cycles had got wrong in *both* directions:

- **The mechanical check.** Pass 2 found it under-matched; pass 3 found the fix over-matched. The
  resolution is not a third substring tweak but a change of instrument — AST — plus a **positive
  control per rule** alongside the negative one, because negative-only controls are structurally
  incapable of catching the over-match.
- **The Pruning Authorization gate blocked its own evidence.** Fixed by splitting the destructive
  half into its own issue, applying the same pattern the plan had already used once for 3.1c —
  because `Blocks` operates on whole beads and no prose carve-out could be honoured.
- **The Follow-on activation gate had no way to say no.** A legal operator answer would have left
  the plan permanently un-closable.

The pass also **verified the critical-path claim end to end** and answered the size question:
no split is needed — "the 37-issue size is carried by the dependency graph, not by an execution
session's attention."

Re-dispatched to a fresh red-team cycle (pass 4) per REQ-PLAN-030.
