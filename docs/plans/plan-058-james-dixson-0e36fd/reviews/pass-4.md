---
type: Review
okf_spec: OKF-PLAN
id: pass-4
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# Red-team pass 4 — plan-058-james-dixson-0e36fd
## Verdict: REVISE

Dispatched as an isolated sub-agent (REQ-AGENT-049). Read-only with respect to the repository; one
sandbox spike **executing** the Issue 3.1 AST rules against the live `upstream.py` (removed, no
residue). The main session wrote this file.

Run under an explicit convergence standard: APPROVE unless a defect is in the **blocking class**
(wrong behavior, data loss, an unpassable gate, an unclosable plan, or a materially misleading
instruction to an executor). The pass found **one** blocking defect and called the fix one line:
*"If Issue 3.1's rule (a) is moved into Issue 3.1c, this plan is approve-grade."*

## Strengths

- **H1/H2 CONVERGED, verified by execution rather than by reading.** The AST instrument is correct:
  rule (a) matches exactly `:1002` and `:1066` and is blind both to `edge_type()`'s docstring at
  `:664` (pass-3's over-match) and to the token-blanking problem (pass-2's under-match). Rule (d) is
  exactly right — the three `subprocess.run` sites (`:88` in `run`, `:109` in `run_unchecked`,
  `:185` in `_config_get`) are precisely the allow-list, so `--check-timeouts` is green on correct
  code and the `FunctionDef`-ancestor tracking is genuinely free. 3.1c's construct rule correctly
  spares the injected `deps_for` parameter at `:686` that a bare-name ban would have forbidden.
- **H3 is genuinely fixed.** `Blocks: 4.5, 4.1d`; `4.1d <- 4.1b <- 4.1`, `4.2 <- 4.1b`. The gate's
  evidence is outside its Blocks set and Epic 4 goes from 5 gated issues to 2.
- **Graph integrity holds under the pass-3 expansion.** All 39 issues parsed: no dangling
  `depends-on`, no cycles, R7 intact. Nothing depends on 3.1c; only 3.1c depends on 1.7 — so the
  decline branch's blast radius is exactly the three issues it names.
- **The M6 test-ownership fixes are real** (1.6, 1.7, 1.8, 2.5 each own their named test), and the
  SC1/SC3 and SC8/SC8b splits are real.
- **M4 is fixed correctly**: `3.7 <- 1.1`, off the consent gate, with the rationale in the issue.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| B1 | **high — BLOCKING** | **Issue 3.1's rule (a) is red on the tree until Issue 1.7 lands, and 1.7 sits behind a consent gate whose decline branch closes it `wontfix-for-now`.** Confirmed by execution: `RULE-A HIT line 1002` / `RULE-A HIT line 1066` — the two `deps_for` closures **only Issue 1.7** rewrites — while Issue 3.1 is `depends-on: 0.3, 1.1` and ships long before it. Three consequences: (1) **decline path** — the construct stays in `upstream.py` forever, the gate's Test exits 1 forever, `Blocks: 3.2` never releases, SC6b is undischargeable, and the plan is **unclosable on a legal operator answer** — pass-3's H4 class, reintroduced by the H1 fix, one screen away from the fix for it; (2) **accept path** — the gate is red for the whole interval between 3.1b and 1.7, indistinguishable from a genuine violation, and the Instructions ("remove the loop rather than the check") **actively mislead**, since the executor cannot remove the loop; (3) **Issue 3.1b becomes unsatisfiable**, because its *positive control* asserts a rule green against a post-fix source that does not exist until 1.7 lands and never exists under a decline. |
| B2 | med | **Rule (b) cannot detect either N+1 this plan is fixing — both are helper-mediated.** Measured: the only `bd show` argv sites are `:474` (in `external_for`) and `:552` (in `deps_for_show`), **neither lexically inside a loop**. The #268 defect was `for bid in sorted(beads): deps_for_show(bid)` at `:533`; the second was `external_for(bid)` at `:615`. A rule matching a literal argv inside a `for` would not have fired on the pre-fix code. 3.1b's paired controls do not close this. Relatedly the `external_for` restriction is budgeted in the enclosing-function paragraph but **not enumerated** in the rule list, making "for every rule Issue 3.1 ships" ambiguous. Non-blocking because Issue 3.3's scale-independence tests are a real behavioral guard — but the plan claims more for the check than it delivers. |
| B3 | med | **Issue 4.1b is labelled "NON-DESTRUCTIVE — deliberately UNGATED" but two of its three acts mutate live state** — it deletes 118 MB of cache and stops a live `dolt sql-server` to test GC against the repository's own 494 MB bead store, the store this plan's beads live in, with no stated recovery precondition. The H3 fix drew the line correctly for `.beads/backup` and then mislabelled the remainder. Non-blocking: `.beads/backup` still exists at 4.1b time, so DR coverage is intact. |
| B4 | med | **SC8b's verification is vacuous today** — `grep -q REQ-HYG-` returns **26 existing matches**, so the criterion passes before Issue 4.4b writes anything. Same "verification that does not verify" class pass-1 flagged. |
| B5 | low | **SC1's `-k zero_bd_show` selector collides with a pre-existing passing test** — `test_closable_issues_one_bd_list_and_zero_bd_show` (`:685`) already matches, so SC1 is green before Issue 3.3 writes anything. (`-k scale_independence` has no match and fails loudly — the safe direction.) |
| B6 | low | **Issue 3.1b's `depends-on` is missing 1.2** — rule (c) bans `deps_for_show`, which Issue 1.2 deletes; running 3.1b first shows a red positive control for a correct rule. |
| B7 | low | **SC5 and SC4c name `-k` selectors no issue commits to.** Unlike B5 these fail loudly on no-match, so noted for completeness. |

## Missing

- A statement in Issue 3.1 that no rule it ships may presuppose Issue 1.7 — the invariant B1 violates.
- Rule (e), the `external_for` restriction, enumerated rather than only referenced.
- A recovery precondition for 4.1b's stop-and-GC.

## Gate Assessment

| Gate | Reachable | Notes |
| :-- | :-- | :-- |
| Start Gate | yes | correct |
| Fan-out eliminated | yes | evidence (1.4, 1.9) outside the Blocks set; the two-clause Test verified sound |
| Mechanical fan-out check green | **no on decline; intermittently red on accept** | **B1** |
| Follow-on activation | yes, both branches | decline branch traced end to end: 1.7 and 3.1c are the only issues with inbound edges; SC3c/SC3d/SC6c the only SCs discharged by them; nothing depends on 3.1c. Complete **except** that it did not cover rule (a) (B1) |
| Pruning Authorization | yes | H3 fixed; evidence outside the Blocks set; "not warranted yet" closes the epic |
| Reconcile Gate | **conditionally** | unreachable under a decline, via B1 rather than H4 |

## Upstream Assessment

Unchanged and sound. `#268` include-disposition correct; Resolved-By consistent with the tags.
SC10's four-filing set now agrees with the issues that own them — L2 genuinely fixed. The
critical-path claim re-verified: the transitive closure of the three tagged issues touches only
`0.1, 0.1b, 0.2` — never 1.7, never Epic 4.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| B1 | high | **Accepted; confirmed at the source, then fixed exactly as recommended.** `grep -n '"bd", "dep", "list"'` returns only `:1002` and `:1066` — the two sites only Issue 1.7 rewrites. **Rule (a) moved from Issue 3.1 into Issue 3.1c**, which already carries `depends-on: 3.1b, 1.7` and is already N/A under a decline via SC6c; it now sits beside the near-duplicate construct rule targeting the same two lines. Issue 3.1 ships only rules (b)-(e), all green on the tree as of Epic 1. **Added the missing invariant as a named rule of the issue:** *"no rule in this issue may presuppose Issue 1.7 having landed"*, with the decline-path consequence spelled out, so the constraint is stated rather than left to be rediscovered a fourth time. | `main-session` | `resolved` |
| B2 | med | **Accepted, both halves.** Rule (b) restated to cover the **helper-mediated** form — *a call to a name whose own body issues `bd show`, from inside a `For`/`While`/comprehension* — with the measurement written in (the only argv sites, `:474` and `:552`, are not lexically in a loop, so the literal form would have caught neither of this plan's two N+1s). The `external_for` restriction is now **enumerated as rule (e)** rather than only referenced, which also disambiguates 3.1b's "every rule Issue 3.1 ships", and its allow-list is justified by the legitimate comprehension at `:650`. | `main-session` | `resolved` |
| B3 | med | **Accepted.** The label is corrected to **"NON-DESTRUCTIVE TO BEAD CONTENT … with an explicit safety precondition"**, and the precondition is stated: verify `.beads/backup` is current and `bd status` healthy **before** the cache deletion and the stop/GC, and re-verify after. The issue now says plainly that `.beads/backup` still existing at this point is *why* the sequencing is safe and must not be reordered, and that "non-destructive" means no bead content is deleted — not that nothing is written. | `main-session` | `resolved` |
| B4 | med | **Accepted; verified vacuous.** `grep -c REQ-HYG- skills/yf-beads-hygiene/SPEC.md` returns **26**. SC8b's verification now greps for a distinctive clause of the *new* requirement (`dry-run by default`) rather than the id prefix. | `main-session` | `resolved` |
| B5 | low | **Accepted; verified the collision.** `test_closable_issues_one_bd_list_and_zero_bd_show` at `:685` does match `-k zero_bd_show`. Issue 3.3 now **names its tests explicitly** (`test_push_zero_bd_show`, `test_enumerate_zero_bd_show`, `test_enumerate_scale_independence`), as 1.6/1.7/1.8/2.5 already do, and SC1's selector is tightened to `-k 'push_zero_bd_show or enumerate_zero_bd_show'` so it cannot be satisfied by the `closable` test alone. | `main-session` | `resolved` |
| B6 | low | **Accepted.** `Issue 3.1b depends-on: 3.1, 1.2`, with the reason recorded — rule (c) bans the `FunctionDef` that Issue 1.2 deletes. | `main-session` | `resolved` |
| B7 | low | **Accepted.** Issues 2.6 and 2.7 now name their tests explicitly (`test_config_timeout_is_undetermined`, `test_hoist_timeout_closes_no_bead`), matching SC4c's and SC5's selectors. | `main-session` | `resolved` |

## Outcome

All 7 concerns **resolved**; the single blocking one was fixed exactly as recommended and confirmed
at the source first. The plan remains **39 issues / 6 gates** — this cycle **moved** a rule rather
than adding scope, which is the shape a converging review should have.

**B1 is the third appearance of one root cause, and that is worth naming.** Pass-3's H4 found that a
consent gate with no decline branch strands the plan; the fix added the branch. B1 found that a rule
placed upstream of the same gate strands it *again*, through a different edge. The durable remedy is
not a third patch but the **invariant now written into Issue 3.1** — no rule may presuppose the
gated issue — which is checkable by inspection rather than by remembering the last two failures.

Re-dispatched to a fresh red-team cycle (pass 5) per REQ-PLAN-030. Cycle 5 is the review bound, and
per this pass's own assessment it should be a **confirmation**, not another expansion.
