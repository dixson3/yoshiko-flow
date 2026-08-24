---
type: Review
okf_spec: OKF-PLAN
id: pass-5
description: Red-team pass 5 (fifth independent) — REVISE, 1 high / 3 medium / 4 low; ONE execution-blocking defect, and an explicit recommendation NOT to escalate the review bound
---

# Red-team pass 5

## Verdict: REVISE

1 high, 3 medium, 4 low. **All 8 resolved** (see Resolutions). The reviewer explicitly recommends
**AGAINST escalating `max_review_cycles`** — see the Readiness Statement.

## Strengths (all verified by execution)

- **Every mechanical property clean after the fifth rewrite** — 31 issues, 49 edges, 36 criteria,
  5 gates, 11 risks, 22 upstream rows, `unparsed: []`, acyclic, 0 dangling `Discharged-by`, 0 issues
  discharging no criterion, 31/31 `touches:`. `audit` → `status: pass`, **`findings: []`**.
  `doc_lint` → PASS, 0 errors.
- **Closure still perfect and generated** — 29/29, 0 either direction, **0 controls with >1 builder**;
  sets derive cleanly from builder epic (core 21 / ext 4 / land 4).
- **Both gates' behind-sets re-verified** — `core` 16, violations **NONE**; `ext` 9, **NONE**.
- **P4-C1's class fix is REAL** — the exit-1 rule lives once in 0.2 and is **enforced by the gate
  Conditions themselves**, not merely asserted in prose. All ~18 argparse-exit-2 controls are
  covered by that one rule. **20 of `core`'s 21 controls can now produce a real exit-1 RED, against
  ~4 of 21 at pass 4.**
- **P4-C4 verified decidable and non-trivial** — 0.1 is the DAG's **sole root** and a strict ancestor
  of every other issue; its three `touches:` are all spec paths; **no other issue touches a spec path**.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| P5-C1 | **high** | **`ctl-req-landed` is GREEN at its builder — P4-C1's sweep missed it.** 0.3's ancestry is `['0.1','0.2']`, and 0.1 lands all four `REQ-*` before 0.3 exists. Spiked: working-tree reading → exit 0 at 0.3 (so `red-prework-core`, which blocks **10 issues**, is unsatisfiable); merged-tree reading → SC1 can only go green after 7.1, but **SC1's `Discharged-by` is `0.1, 0.3` — neither is post-merge**. A whole-plan sweep confirms **SC1 is the ONLY builder/fixer inversion in the plan** |
| P5-C2 | med | **`ctl-harness-contract` catches 1 of the 4 defects pass 4 credited it with.** The file-granular predicate catches the ledger; it misses `--fixture` (a *flag*, and `upstream.py` exists so the disjunct passes), `CTL_TXT` (an *env var*), and P3-C4's test files. 0.2 also overclaims that it asserts *"the whole of the above"* — the floor is a different control, the exit-1 rule is enforced by the gate Condition, and the `bash "$ctl"` rule has **no assertion at all** |
| P5-C3 | med | **The hand-grep returns exactly one hit: `assets/controls.txt` is in no `touches:` list.** It is written by `gen-controls.py`, read by `gate-run.sh` on every invocation, and named in **both** gate Conditions and SC0 — surviving only via the *"or demonstrated present on the tree"* escape. The single file the check most exists to protect is protected only vacuously |
| P5-C4 | med | **The three fixtures added by P4-C1's fix declare no path.** 3.1 declares `closable-fixture.json`; 0.3/1.1/1.3's new fixtures and the `CTL_TXT` alternative set declare nothing. SC11b's and P4-C3's shape recurring **inside the fix for P4-C1** |
| P5-C5 | low | **SC0c and SC1b are single-issue-discharged**; their RED rests on intra-issue ordering that nothing sequences or records. Also: 0.2 does not say whether a *missing* declared artifact is exit 1 or exit 2 |
| P5-C6 | low | **R11's acceptance rationale contradicts R10 and D-20.** It calls the lever *"validated"* and then justifies acceptance with *"weakly corroborated"* — both in one row. D-25's weak label attaches to **EXP-006's** overlap inference; **EXP-007's** shared-paths signal is p=3.4e-11. The real and fully defensible reason is **D-19**: no effective remedy exists |
| P5-C7 | low | **Textual residuals** — 0.2 reads *"`ctl-harness-contract` (widening `ctl-harness-contract`)"*, self-referential; and `assets/upstream-authorization.txt` appears in no `touches:` correctly (only the operator writes it) but nothing says so |
| P5-C8 | low | **`ctl-deploy-stamp`'s RED is incidental, not constructed** — it is RED today only because the operator's installed stamp happens to be stale. A `yf self install` before 7.0 would make it green at its builder |

## Missing

- **No control asserts the `bash "$ctl"` invocation rule** — one of the six things 0.2 claims
  `ctl-harness-contract` asserts.
- **No control asserts the builder-precedes-fixer invariant.** The reviewer supplied it as a
  one-predicate sweep that found P5-C1 mechanically.

## Gate Assessment

| Gate | Reachable? | Verdict |
| :-- | :-- | :-- |
| `red-prework-core` | Structurally **yes** (behind-set 16, NONE) | **Blocked by P5-C1 only** — 20 of 21 controls reach a real exit-1 RED; `ctl-req-landed` is the single hold-out |
| `red-prework-ext` | **Yes** (behind-set 9, NONE) | **Sound** — all 4 ext controls reach exit 1 |
| `upstream-write` | **Yes** | Sound, unchanged |
| Reconcile Gate | **Yes** | Sound; exclusion intact, non-self-blocking |

## Upstream Assessment

Unchanged and sound. `verify-reconcile` → `verdict: fail`, **17/17** actionable rows failing
pre-execution — the correct RED for SC20. Every `include` names a resolving issue; #194 and #177
correctly claim none.

## Convergence assessment

Counts **23 → 12 → 12 → 7 → 8**, but severity-weighted the trajectory is still down: pass 4's high
made **both gates unsatisfiable for the majority of controls**; pass 5's high is **one control out of
29**, mechanically isolated, with the remedy already written three lines above it in the same issue.

> The class **was** substantially swept this time — P4-C1's argparse arm (~18 controls) was fixed
> once, as a rule, enforced by an exit code. That is a genuine change of kind. What was *not* swept
> is the green-at-builder arm. **The sweep was half class-fix, half instance-fix** — and the half
> that stayed an instance-fix is exactly the half a reviewer could enumerate mechanically.

## Readiness statement

**Executable as written? No — but the gap is one control and one sentence, not a design defect.**

- **Execution-blocking: P5-C1 only.** It stalls 10 of 31 issues.
- **Carryable: P5-C2 through P5-C8.** None blocks a gate, changes the DAG, the criteria set, or the
  epic structure.

**Recommendation: do NOT escalate `max_review_cycles`.** A sixth adversarial pass buys nothing —
P5-C1 is fully diagnosed, reproduced in a spike, and confirmed by a whole-plan sweep showing it is
the *only* instance of its class. **It needs an edit, not another opinion.**

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| P5-C1 | high | **Fixed, and BOTH your remedies applied — the instance AND the class.** (1) 0.3 now drives **both** `ctl-spec-first-order` and `ctl-req-landed` RED against pinned negative fixtures (for `ctl-req-landed`: a fixture spec tree with one `REQ-*` absent), stating explicitly that 0.1 is 0.3's ancestor so the live tree is already green there. SC1 gains **7.1** in its `Discharged-by` for the merged-tree arm, and its text now states how RED is obtained. (2) **Your sweep is now the third arm of `ctl-harness-contract`** — *for every control criterion, the builder issue must not have any other discharger among its own ancestors; where it is the sole discharger, the criterion must state how RED is obtained.* **I ran it: `SC1 / ctl-req-landed / 0.3 ← 0.1` is the only inversion in the plan, and `SC0c`/`SC1b` are the only single-discharger cases — reproducing your result exactly** | `main-session` | `resolved` |
| P5-C2 | med | **Fixed by SCOPING the claim to what it actually asserts, and adding the arm that was missing.** 0.2 no longer says `ctl-harness-contract` asserts *"the whole of the above"*. It now names **exactly three arms**: FILE (with the tree-fallback narrowed to paths OUTSIDE `assets/`), **INTERFACE** (every subcommand, flag or env var a control passes to a repo script must appear in that script's `--help` or be named as commissioned — *this is the arm that catches `--fixture` and `CTL_TXT`*), and BUILDER-PRECEDES-FIXER. It states explicitly that the floor is asserted by `ctl-empty-set-floor` and the exit-1 rule by the gate Conditions — **neither is claimed here** | `main-session` | `resolved` |
| P5-C3 | med | **Fixed.** `assets/controls.txt` added to 0.2's `touches:`. The FILE arm's *"demonstrated present on the tree"* fallback is now narrowed to paths **outside this bundle's `assets/`**, so the file the check most exists to protect can no longer be protected only vacuously | `main-session` | `resolved` |
| P5-C4 | med | **Fixed with the single sentence you proposed**, in 0.2's contract: *control fixtures are constructed inline in `$(mktemp -d)` and leave no residue, EXCEPT where a fixture is a declared repo path (`assets/closable-fixture.json`), which must appear in its builder's `touches:`.* 3.1 becomes the stated exception; 0.3/1.1/1.3's fixtures and the `CTL_TXT` alternative set need no path | `main-session` | `resolved` |
| P5-C5 | low | **Both halves fixed in 0.2's contract.** Intra-issue ordering is stated — *where a control and the thing it checks are built by the SAME issue (`ctl-empty-set-floor`, `ctl-baseline-pathspec`), the RED observation is recorded to the ledger BEFORE that issue's implementation step*. And the missing-vs-malformed distinction is ruled: **a MISSING declared artifact is exit 1** (real negative); an **unreadable or malformed** one is exit 2 (instrument failure) | `main-session` | `resolved` |
| P5-C6 | low | **Fixed — re-based on D-19, which is the real reason.** R11's mitigation now reads *accepted deliberately, on D-19, because NO EFFECTIVE REMEDY EXISTS*, citing EXP-006's measurement that 0 of 5 independent-pair defects would have been prevented by an edge and that an edge moves overlap-stratum density the WRONG way (0.301 → 0.362). The row records the correction and why the old rationale was wrong: D-25's weak label attaches to EXP-006's overlap inference, not to EXP-007's shared-paths signal at p=3.4e-11. The reasoning is now consistent with R10 and D-20 | `main-session` | `resolved` |
| P5-C7 | low | **Both fixed.** The self-referential *"(widening `ctl-harness-contract`)"* now reads *"(widening the former `ctl-controls-closure`)"* — it was introduced by my own global rename, which is a small instance of the same class. The `upstream-write` gate's Instructions now state that `assets/upstream-authorization.txt` is **written by the operator and by no issue**, which is why it appears in no `touches:` list | `main-session` | `resolved` |
| P5-C8 | low | **Fixed.** 7.0 now requires each land-set RED to be obtained **against a pinned fixture, never live machine state**, naming `ctl-deploy-stamp` explicitly: it is RED today only because the installed stamp happens to be stale, which a `yf self install` before 7.0 would silently reverse | `main-session` | `resolved` |
