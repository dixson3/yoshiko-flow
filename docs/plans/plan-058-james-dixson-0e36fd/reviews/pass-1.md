---
type: Review
okf_spec: OKF-PLAN
id: pass-1
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# Red-team pass 1 — plan-058-james-dixson-0e36fd
## Verdict: REVISE

## Strengths

- **The equivalence claim survives adversarial audit.** The reviewer read the harness rather than
  trusting the finding, and confirmed it is **not** circular: the slow side runs the real
  `collect_parent_edges` (1,801 live `bd show` subprocesses); the fast side reads the `bd list`
  payload. The comparison key `(blocked, blocker, dep_type)` is exactly the triple
  `classify_active` consumes (`upstream.py:328-380`). Set-comparison would normally mask
  multiplicity, but both sides report `edges=1648` **and** set-equality, closing that hole.
  "A sound exhaustive proof."
- **Epic 2's honesty claim is correct** — 1,801 calls at 0.186 s trip no defensible per-call bound.
  Stating it in four places rather than leaving it inferable was the right call.
- **R7 (Epic 4 separability) is literally true.** Every `depends-on` edge checked: no Epic 0-3 issue
  depends on any Epic 4 issue; the only cross-edge is 4.1 → 1.1, the safe direction.
- **REQ-BUP-071/072/073 are the correct next free ids** (highest existing is `REQ-BUP-070b`).
- **The 60 s LOCAL bound breaks nothing findable.** Slowest local call 0.29 s; ~370k beads of
  headroom. All four `bash -c` sites wrap exactly one `bd close`/`bd update`.
- Epic 0's SPEC-first chaining is correct for Epics 1-3.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | **high** | SC1 and Issue 3.3 assert "exactly one `bd list`" for `push`. **Spike-measured: post-fix `push` issues TWO** — `create_or_update` → `load_universe_rows` (`:922`) and `owner_claim_warning_lines` → `load_universe_rows` (`:1176`). SC1's named test cannot pass as specified. |
| C2 | **high** | The rewrite creates a new **unpinned `bd`-version dependency with a silent fail-open**. If a bd version omits/renames `dependencies[]`, `collect_parent_edges` returns `[]` with no error; `classify_active` loses ancestor propagation, so *more* beads become push candidates — failing toward **extra upstream writes**, invisibly. Fixture tests stay green. `REQ-BUP-055` is the directly applicable, unused precedent. EXP-002 measured bd **1.2.2**; REQ-BUP-055 pins **1.1.2**; never reconciled. |
| C3 | med | "Fan-out eliminated" gate has a **reachability cycle** — `Blocks: 3.3` while `Instructions` names 3.3's tests as the operative assertion. Its second Condition clause ("completes in seconds") has no pre-gate evidence producer. |
| C4 | med | **Epic 4 is not sequenced SPEC-first**, contradicting the Approach. Issue 4.5 implements a destructive verb in `yf-beads-hygiene` (own SPEC, 28 `REQ-*`) with no `REQ-HYG-*` created anywhere. |
| C5 | med | Issue 3.1's check is **materially harder than its cited precedent** — `check_gh_direct.py` is a tokenize-based substring/name scanner with zero dataflow analysis; "flag a `bd show` inside a loop over the universe" is dataflow. And **SC6 does not verify SC6**: it asserts reintroduction *fails*, but verifies the check exits 0 on clean code. No negative control. |
| C6 | med | **SC4b invokes `--check-timeouts`, a flag no issue creates.** Unsatisfiable as written. |
| C7 | med | `REQ-BUP-071`'s drafted wording is **narrower than the change set**. Issue 1.3 is an `external_ref` fan-out, not parent-edge collection; Issue 2.5 is an operator-facing change covered by **no** requirement — yet SC8 claims every behavior change is covered. |
| C8 | med | **EXP-005's sweep missed a third live instance**: `detect_followons` → `deps_for(bid)` → `bd dep list` per subtree bead, from `cmd_followons` (`:1002`) and `cmd_land` (`:1066`). Same shape, same removable cause, and on the **land-the-plane** path. Issue 3.1's check as scoped would not flag it — the recurrence guard is blind to it. |
| C9 | med | **Epic 4 is unfair to the operator in one fixable way: it never evaluates a non-destructive remedy.** The "0.18%" framing is a category error — `.beads/dolt` (494 MB) and `.beads/backup` (289 MB) *are* bead-derived. The defensible claim is narrower: deleting rows cannot reclaim history. The operator raised a real 785 MB problem and the plan answers only why their fix fails, never what would work. `.beads/backup` (37% of total) is likely rotatable with zero data loss; Dolt GC/squash addresses the 494 MB. EXP-006 §7 ("Evidence FOR the operator") is not carried into `plan.md` at all. |
| C10 | med | `_config_get` returning `""` on timeout makes **`push` exit 0 with a success-shaped message** — "Upstream tracking is disabled; nothing to push". A transient `bd` hiccup silently converts a mandated write into a reported no-op, with no compliant fallback. |
| C11 | low | Deferring the stdout-buffering fix is the weakest of the three deferrals — `push --apply` over N beads still buffers through 1-2 s per `gh` write. |
| C12 | low | EXP-002's "targets identical=True" is **vacuous** — both sides do `beads.get(target_id)` on the same dict. Harmless but cited as if independent. |
| C13 | low | Upstream Issues **Resolved-By disagrees with the epic tags** (table `1.1, 1.2, 2.1, 3.1`; tags `1.1, 1.3, 2.1`). |
| C14 | low | Findings cite `scratchpad/exp001.py`, which a cold reader cannot resolve. |
| C15 | low | `upstream-triage.md` has an empty `**Disposition:**` field. |
| C16 | low | Issue 0.4 omits **SPEC.md §5 Verification entries** for 071/072/073. |

## Missing

- **Cold-start `bd` latency** -> **Issue 1.9** measures it; risk **R13** records that the 60 s bound rested on warm numbers.
- **Negative control for every mechanical check** -> **Issue 3.1b**; SC6 now verifies via that control rather than a green run.
- **The `_shared/sync.py` fence** -> written into **Issue 1.1's body** as a HARD CONSTRAINT, not left in R8 where an executor working from the issue alone would never see it.
- **A gated end-to-end `push` re-measurement** -> **Issue 1.9**, which the "Fan-out eliminated" gate's Condition now names.

As originally reported:

- Any measurement of **cold-start `bd`** latency against the 494 MB Dolt store — all timings warm.
- A **negative control for every mechanical check** introduced.
- The `_shared/sync.py` fence (`upstream.py:250-388`) is in R8 and EXP-004 but in **no issue's text**.
- No **gated** end-to-end `push` wall-clock re-measurement post-fix.

## Gate Assessment

| Gate | Reachable | Placement | Notes |
| :-- | :-- | :-- | :-- |
| Start Gate | yes | correct | human/operator, mandatory |
| Fan-out eliminated | **cycle** | correct floor | see C3 |
| Mechanical fan-out check green | yes | correct | 3.1 correctly **not** in Blocks; frontloaded to earliest legal position |
| Pruning Authorization | yes | correct | human/consent, no Test — correct for an irreversible action; admitting "not warranted yet" is good design |
| Reconcile Gate | yes | standard | fine |

The `test_class`/`cwd` grammar-gap blockquote is accurate and its pour-time mitigation is the right one.

## Upstream Assessment

`#268`, disposition `include`, verified OPEN. Disposition correct; body captured verbatim for
portability. Resolved-By mismatch per C13. Issues 3.4/3.5 filing two **new** upstream issues does
not violate coarse granularity — distinct defects, not execution sub-beads — and SC10 guards
against silent drops. If C8 is accepted, the `deps_for` N+1 joins that filing set.

Dispatched as an isolated sub-agent (REQ-AGENT-049). Read-only with respect to the repository;
performed a sandbox spike. The main session wrote this file.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Accepted, option (a).** Verified independently: `load_universe_rows()` is called at both `:922` and `:1176`. Added **Issue 1.6** hoisting the load so `cmd_push` passes `rows`/`beads` into `owner_claim_warning_lines()`. SC1 restated around scale-independence; new **SC1b** asserts the universe is read once; SC3 and Issue 3.3 now assert **zero `bd show`** plus a universe-size-independent `bd list` count, rather than a hard-coded "one". | `main-session` | `resolved` |
| C2 | high | **Accepted in full, plus the free cross-check.** Added **Issue 0.1b** recording the bd version floor as an amendment to `REQ-BUP-055` — the precedent named — with the fields, the measured version (1.2.2), the 1.1.2 reconciliation, and the omitempty caveat, labelled an assertion exactly as 055 is. Added **Issue 1.8** emitting a stderr warning when rows carry `parent` but zero parent-child edges were derived, converting the silent fail-open into a loud one. New **SC2b** and risk **R10**. | `main-session` | `resolved` |
| C3 | med | **Accepted.** Gate `Instructions` repointed at Issue 1.4's direct tests and Issue 1.9's recorded timing — both land before the gate — with an explicit note not to cite 3.3, which is in the gate's own Blocks set. Added **Issue 1.9** as the timing clause's evidence producer, and reworded the Condition to name it. | `main-session` | `resolved` |
| C4 | med | **Accepted.** Added **Issue 4.4b** landing the `REQ-HYG-*` requirement in `yf-beads-hygiene`'s own SPEC — including the dry-run-by-default contract and the export-restore round-trip — as a blocker of 4.5. SC8 broadened from `REQ-BUP-*` to `REQ-*` and now names 4.4b. | `main-session` | `resolved` |
| C5 | med | **Accepted, and the reframing is an improvement.** Issue 3.1 rewritten into the precedent's actual substring/name idiom — ban `deps_for_show`, restrict `external_for(` to `cmd_mappings`/`plan_hoist`, ban `bd dep list` inside `detect_followons` — instead of a dataflow loop heuristic. Added **Issue 3.1b**, a negative control asserting each banned shape exits 1, and made it SC6's verification so the criterion now tests what it claims. | `main-session` | `resolved` |
| C6 | med | **Accepted.** `--check-timeouts` is now explicitly in Issue 3.1's scope (banning any bare `subprocess.run(` outside the three primitives), and SC4b names 3.1 in Discharged-by. | `main-session` | `resolved` |
| C7 | med | **Accepted.** `REQ-BUP-071` broadened to "no verb shall resolve a per-row field with a per-bead subprocess when the bulk query already carries it", naming all three call sites. Issue 2.5's operator-facing change is now covered by an explicit `REQ-BUP-056` amendment in Issue 0.4's scope. | `main-session` | `resolved` |
| C8 | med | **Accepted, and fixed rather than filed.** Added **Issue 1.7** applying the one-call rewrite to `detect_followons`' `deps_for` closures in `cmd_followons` (`:1002`) and `cmd_land` (`:1066`). Deferring it would have repeated precisely the mistake EXP-005 documents. Issue 3.1's check now bans the shape, and new **SC3c** covers the land-the-plane path. | `main-session` | `resolved` |
| C9 | med | **Accepted — this was the most valuable concern in the pass.** The "0.18%" framing is withdrawn from the Approach and replaced with the claim that is actually supported: deleting rows cannot reclaim the space because the space is history and a `DELETE` adds to it. Added **Issue 4.1b** evaluating non-destructive reclamation (`.beads/backup` 289 MB, Dolt GC/squash 494 MB) **ahead of and outside** the consent gate, since neither deletes bead content. EXP-006 §7's evidence *for* the operator is now carried into the Approach. Issue 4.5 gains the export-restore round-trip and dry-run-by-default requirements. New **SC9b** and risk **R11**. The epic was renamed to lead with reclamation rather than pruning. | `main-session` | `resolved` |
| C10 | med | **Accepted.** Issue 2.4 now requires a config-read timeout to exit **non-zero** as "upstream state UNDETERMINED (config read timed out)", never "disabled; nothing to push". New **SC4c** and risk **R12**; `REQ-BUP-072` carries the clause. | `main-session` | `resolved` |
| C11 | low | **Accepted — deferral withdrawn.** `flush=True` folded into Issue 3.6. The reviewer is right that "it dissolves once fast" was true only of the preview; `push --apply` over N beads still buffers through 1-2 s per `gh` write. | `main-session` | `resolved` |
| C12 | low | **Accepted.** EXP-002 now states the `targets identical` line is trivially true (both sides do `beads.get(target_id)` on the same dict), notes it is harmless because `Edge.target` is unread on this path, and identifies the set-equality plus matching edge counts as the load-bearing result. | `main-session` | `resolved` |
| C13 | low | **Accepted.** Upstream Issues table Resolved-By corrected to `1.1, 1.3, 2.1`, matching the `resolves-upstream` tags that reconcile actually reads. | `main-session` | `resolved` |
| C14 | low | **Already resolved before the pass returned.** The harness and both logs were vendored into `assets/` and the findings' Evidence sections repointed at them; the `../` link form was then flattened to plain code spans to satisfy the portability audit's no-parent-traversal rule. Verified: no `scratchpad` reference remains. | `main-session` | `resolved` |
| C15 | low | **Accepted.** `upstream-triage.md` Disposition filled in as `include`, with notes recording why direction 2 was chosen over direction 1, why direction 4 is declined, and the two corrections this plan makes to the issue as filed. | `main-session` | `resolved` |
| C16 | low | **Accepted.** SPEC.md §5 Verification entries for 071/072/073 added to Issue 0.4's scope. | `main-session` | `resolved` |

## Outcome

All 16 concerns **resolved** by the main session under the autonomous default. The plan grew from
27 issues to **35** across the same 5 epics: six new issues in Epics 0-3 (0.1b, 1.6, 1.7, 1.8, 1.9,
3.1b) and two in Epic 4 (4.1b, 4.4b). Success Criteria grew from 14 to 20; risks R10-R13 added.

Two concerns changed the plan's substance rather than its wording:

- **C1** falsified a success criterion **by measurement** — the kind of finding a prose-only pass
  does not produce, and the reason this pass was dispatched with a sandbox spike authorized.
- **C9** identified a fairness failure: the plan told the operator why their remedy would not work
  without ever asking what would. `.beads/backup` alone is 37% of the 785 MB they raised.

Re-dispatched to a fresh red-team cycle (pass 2) per REQ-PLAN-030 — a REVISE blocks
`ready-for-approval` until a *later* cycle returns APPROVE.
