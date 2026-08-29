---
type: Review
okf_spec: OKF-PLAN
id: pass-2
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# Red-team pass 2 — plan-058-james-dixson-0e36fd
## Verdict: REVISE

## Strengths

- Every one of pass-1's 16 resolutions is real and checkable at the source.
- C1's fix is exactly right; the plan now asserts scale-independence rather than a brittle constant.
- **Issue 1.8's predicate is sound and false-alarm-free even though its stated rationale is not** —
  the mitigation survives the falsification of its premise, which is a good sign about how it was
  designed.
- Structural integrity is excellent under an eight-issue expansion.
- C9's reframing is the correct, defensible claim and a real improvement over the withdrawn gloss.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| D1 | **high** | **Issue 1.7 is not behavior-preserving — it silently un-breaks a DEAD AUTO-HOIST path.** Measured: `bd dep list --json` emits `dependency_type` and **`id`** — no `depends_on_id`. `detect_followons` resolves via `depends_on_id or target or to` (`:712`), which against live output is **always `None`**, so the `narrow` set is **permanently empty today**. Switching the source to `bd list`'s `dependencies[]` (which *does* carry `depends_on_id`) makes `narrow` populate — and `narrow` is exactly `plan_land_hoist`'s `auto_eligible` under `auto_hoist_followons=true`, the **no-prompt path that runs `bd close -r` tombstones**. A change framed as a pure performance rewrite would take an unattended destructive path from dead to live. The suite cannot catch it: `test_upstream.py:132` stubs the **`bd list`** shape while commenting it "(bd dep list shape)" — green against output bd never produces. |
| D2 | **high** | **Issue 3.1's `bd dep list` ban is structurally impossible in the chosen idiom, so C8's recurrence guard is a no-op.** Spike-proven: `check_gh_direct.py:code_lines` blanks every `STRING` token, so `run(["bd","dep","list",bid,"--json"])` becomes `run([ , , , bid, ])` — neither `bd dep list` nor `"bd", "dep", "list"` matches. (The precedent's own `FORBIDDEN_SUBSTRINGS` are therefore largely vacuous — a latent defect in the model being cited.) Compounding: the rule names the **wrong location** — `bd dep list` never appears inside `detect_followons`, which takes `deps_for` injected; the calls are in `cmd_followons` (`:1002`) and `cmd_land` (`:1066`). And "`external_for(` only in `cmd_mappings`/`plan_hoist`" needs enclosing-function tracking the flat line-scan precedent has none of. Both the gate and SC6 rest on this. |
| D3 | **high** | **`.beads/backup` is NOT "rotatable with zero data loss" — it is the repo's SOLE local Dolt replica.** `repo_state.json` registers it as a Dolt backup destination (`"backups": {"backup_export": {...}}`) with `"remotes": {}` and `dolt.local-only: true`. It is a content-addressed store, not dated snapshots: **all 109 `.darc` archives are referenced by its manifest**, and `backup_state.json` was timestamped minutes before the review — bd syncs it continuously. `bd backup restore` reads it. Nothing can be individually rotated; the only available operation is destroying the whole DR copy. |
| D4 | med | **"Dolt GC / history squash addresses the 494 MB" is unverified and largely wrong**, now stated as near-fact in the Approach. Measured: `.beads/dolt` = `noms` **375 MB** (105 MB live journal + 232 MB already-archived `oldgen/*.darc`) + `git-remote-cache` **118 MB**. (a) GC reclaims *unreachable* chunks; all `main` history is reachable, so it cannot reclaim the history the Approach says it addresses. (b) The store is **already archived**, bounding the compaction win at the 105 MB journal. (c) A live `dolt sql-server` is running, so GC needs a `bd dolt stop`-class flush first. "History squash" is not a Dolt operation. Pass-1's C9 said the plan was unfair to the operator; the fix replaced an overstated dismissal with an **overstated promise** — the same failure mirrored. |
| D5 | med | **Issue 1.8's warning goes to stderr — the one channel this codebase already proved the routed consumer never sees.** `owner_claim_warning_lines`' own docstring records why it moved to stdout (REQ-BUP-051, #105 residual: "an agent piping `--json` to `jq` never sees it"). Issue 1.8 reintroduces exactly that shape for R10's only runtime layer. Also strike "exact"/"independent corroboration" and state the predicate literally. |
| D6 | med | **The reclamation analysis never inspected the directory and misses the one genuinely safe target.** `.beads/dolt/yoshiko_flow/.dolt/git-remote-cache` is **118 MB — 15% of the 785 MB** — two cache dirs last touched 2026-06-01 and 2026-06-20. A cache by name and by mtime. Absent from the plan and from EXP-006, which is itself evidence the cycle-2 Epic 4 numbers were reasoned from `du -sh` rather than measured. |
| D7 | low | **SC1's criterion and its verification measure different things.** It asserts wall clock but verifies with `-k scale_independence`, a mocked call-count test that cannot observe wall clock. |
| D8 | low | **Issue 1.6 requires a test edit it does not mention** — `test_upstream.py:461` stubs `owner_claim_warning_lines` as zero-arg; adding a `beads` parameter breaks it. No contradiction with SC7 (scoped to the `collect_parent_edges` stubs), but the executor should be told. Related: 1.6's prose says "pass the already-loaded rows from `cmd_push`", but `cmd_push` never loads — `create_or_update` does at `:922`. |
| D9 | low | **The "Fan-out eliminated" gate is `Type: auto` with a Condition clause its Test cannot evaluate.** "Issue 1.9 has recorded a wall clock" is not observable by `pytest`; the gate passes green whether or not 1.9 recorded anything. |

## Missing

- No risk entry for Issue 1.7's semantic change — R2's treatment of the gate-edge gap is the exact template and was not applied.
- No verification that Issue 3.1's rules are *expressible* before 3.1b is written.
- No measurement behind either Epic 4 reclamation claim, and no accounting of `git-remote-cache`.

## Gate Assessment

| Gate | Reachable | Notes |
| :-- | :-- | :-- |
| Start Gate | yes | correct |
| Fan-out eliminated | yes — C3's cycle genuinely closed | D9: one Condition clause unverifiable by its Test |
| Mechanical fan-out check green | **conditionally** | Test invokes a check whose spec is partly unimplementable (D2) |
| Pruning Authorization | yes | but D3: Issue 4.1b routes destruction of the sole DR replica *outside* it |
| Reconcile Gate | yes | fine |

## Upstream Assessment

Unchanged and sound. Resolved-By now consistent with the tags. If D1 is accepted, the
`narrow`-always-empty defect is a **third** filing candidate — a live correctness bug in shipped
code, independent of this plan.

Dispatched as an isolated sub-agent (REQ-AGENT-049). Read-only with respect to the repository; two
sandbox spikes (a throwaway `bd init` repo, and a tokenizer probe reproducing
`check_gh_direct.py`'s blanking pass). Both removed. The main session wrote this file.

## Part 1 — Pass-1 resolutions: all 16 verified REAL, none cosmetic

Verified at the source. `C13`'s Resolved-By matches the three `resolves-upstream` tags; `C14` —
zero `scratchpad` references remain; `C15` — Disposition present with rationale; `C12` — EXP-002
now states the vacuity; `C6` — `--check-timeouts` is in Issue 3.1's scope.

**C1 resolved and verified.** No "exactly one `bd list`" assertion survives; SC1b is satisfiable.

**C2's mitigation SURVIVES, but its stated justification is FALSIFIED.** Measured in a sandbox on
bd 1.2.2: a bead can carry **two** `parent-child` edges (bd accepts `bd dep add` without complaint),
giving 3 edges vs 2 rows-with-`parent`. So EXP-002's `1,648 == 1,648` is a property of *this
corpus*, **not an invariant**.

The mitigation still holds, for a reason the plan did not state: `bd dep add --type parent-child`
*sets* `parent` and `bd dep remove` *clears* it — `parent` is **derived from** the edge. So
`parent set ⟹ ≥1 parent-child edge` is structural, and Issue 1.8's actual predicate (*rows carry
`parent` AND zero edges derived*) is false-alarm-free and fires exactly on R10's failure mode.
What is wrong is the wording: "exact" and "independent corroboration" are both false and would lead
an executor to implement count-equality.

## Part 2 — Regressions from the eight new issues: NONE structural

All 35 `depends-on` edges extracted mechanically: **no cycles, no dangling references, R7 holds**
(only `4.1 → 1.1`). All four gates reachable — each gate's evidence producer lands outside its own
`Blocks` set. Counts check out: 35 issues, 20 SC, R1-R13.

Issue 1.7's mechanism claim — that `bd list --parent <pid> --all --json` returns `dependencies[]` —
is **verified true** by spike (with `omitempty`, matching EXP-002's 122-row finding). The problem
with 1.7 is not the mechanism; it is D1.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| D1 | high | **Accepted; verified independently against live `bd` before designing.** `bd dep list yf-djfx --json` returns keys including `id` and **no `depends_on_id`** — the chain at `:712` is indeed always `None`, so `narrow` is dead. **Chosen treatment: fix it, but make the activation a REVIEWED DECISION rather than a side effect.** Issue 1.7 now states the semantic change in R2's idiom; new risk **R14**; new **Capability Gate: Follow-on activation** (human/consent) blocks 1.7; new **Issue 3.7** files the `narrow`-always-empty defect upstream as the live correctness bug it is; the wrong `test_upstream.py:132` comment is corrected in 1.7's scope; new **SC3d**. Recorded as a mitigating-but-not-relied-upon fact: `auto_hoist_followons` is `(not set)` here, so default-deny currently empties `auto_eligible` (`:1048`) — verified. **The gate is off the #268 critical path**, proven by transitive-closure check: none of 1.1/1.3/1.6/3.1/3.2 depends on 1.7. | `main-session` | `resolved` |
| D2 | high | **Accepted in full — the reviewer's spike is correct and the rule as written could not have matched.** Issue 3.1 rewritten rule-by-rule against what the idiom enforces: bare names (`deps_for_show`, the `deps_for` closure) are kept as substring rules; the `bd dep list` rule is respecified to scan the **unblanked** source and that is documented as a **deliberate departure** from the precedent; the wrong location (`detect_followons`, which takes `deps_for` injected) is corrected to `cmd_followons`/`cmd_land`; and the `external_for` restriction is now explicitly flagged as requiring enclosing-function tracking that must be **declared new work** or dropped. The corollary — that `check_gh_direct.py`'s own `FORBIDDEN_SUBSTRINGS` are largely vacuous — is recorded as a defect to file, not silently inherited. Issue 3.1b now requires a negative-control fixture **rule-for-rule**. New risk **R15**. | `main-session` | `resolved` |
| D3 | high | **Accepted; the earlier claim was wrong and is withdrawn.** Verified independently: `repo_state.json` registers `.beads/backup` as a Dolt backup destination with `remotes: {}`, and a `find`/`wc -l` count of `*.darc` returns **109**, matching the manifest reference count. It is the sole local Dolt replica, not rotatable snapshots. Issue 4.1b's backup clause rewritten to say exactly that, and **moved BEHIND the Pruning Authorization gate** (`Blocks: 4.5, 4.1b`), with the gate's Instructions stating that only the backup half is constrained — the measurement and the `git-remote-cache` half remain non-destructive and ungated. | `main-session` | `resolved` |
| D4 | med | **Accepted; demoted from near-fact to hypothesis.** The Approach no longer asserts Dolt GC addresses the 494 MB; it now says GC reclaims *unreachable* chunks while `main` history is reachable, the store is already archived (bounding the win at the ~105 MB journal), and a live `sql-server` must be stopped first — the last recorded as a **precondition of Issue 4.1b**. The term "history squash" is dropped as it is not a Dolt operation. The Approach explicitly names this as the over-correction it was: pass-1's C9 fix replaced an overstated dismissal with an overstated promise. | `main-session` | `resolved` |
| D5 | med | **Accepted on all three points.** Issue 1.8's warning moves to **inline stdout**, citing the same #105 residual (REQ-BUP-051) that moved `owner_claim_warning_lines` there. "Exact" and "independent corroboration" are struck from both the issue and EXP-002. The predicate is now stated **literally** — *any row carries a non-empty `parent` AND zero parent-child edges derived* — with an explicit "do not implement count-equality" and the reviewer's measured counterexample (bd accepts two parent-child edges on one bead). The soundness argument is restated on the correct ground: `parent` is *derived from* the edge, so `parent set => >=1 edge` holds structurally. | `main-session` | `resolved` |
| D6 | med | **Accepted — and this was the most useful of the medium findings.** `du -sh` confirms `git-remote-cache` at **118 MB**, two directories last touched 2026-06-01 and 2026-06-20. It is now named in both the Approach and Issue 4.1b as **the one genuinely safe reclamation target**, outside the consent gate. Issue 4.1b now opens with a measured breakdown (`noms` 375 MB = 105 MB journal + 232 MB archived; `git-remote-cache` 118 MB; backup 289 MB) rather than `du -sh`, which is the process defect the reviewer correctly inferred from the omission. | `main-session` | `resolved` |
| D7 | low | **Accepted.** SC1 split: **SC1** keeps the automated call-count/scale-independence half, and new **SC1c** carries the wall-clock claim as a `manual:` clause discharged by Issue 1.9's recorded measurement — because a mocked call-count test cannot observe wall clock. | `main-session` | `resolved` |
| D8 | low | **Accepted, both halves.** Issue 1.6 now names the `test_upstream.py:461` zero-arg stub as a test edit it owns, and resolves the prose wrinkle: `cmd_push` does **not** load the universe (`create_or_update` does at `:922`), so the issue requires an explicit choice between lifting the load into `cmd_push` or returning rows from `create_or_update`. | `main-session` | `resolved` |
| D9 | low | **Accepted.** The gate's Test is now two clauses: the pytest run **and** `test -s assets/post-fix-timing.md`, so it cannot pass green on an unrecorded measurement. Issue 1.9 is correspondingly required to write that artifact. | `main-session` | `resolved` |

## Outcome

All 9 concerns **resolved**. Every high concern was **independently re-verified against the live
system before designing against it** — `bd dep list`'s key set (D1), `repo_state.json`'s backup
registration and the 109-archive count (D3), and `git-remote-cache`'s size and mtimes (D6).

The plan grew from 35 to **37** issues and from 5 to **6** gates: new Issues 3.1c and 3.7, and a new
**Follow-on activation** consent gate.

Two structural consequences of the fixes, both checked:

- Gating Issue 1.7 initially blocked Epic 3's mechanical check transitively (3.1 depended on 1.7).
  The `deps_for` rule was split into **Issue 3.1c** so the core recurrence guard is not held behind
  a consent decision about an unrelated destructive path. Verified by transitive closure: none of
  1.1, 1.3, 1.6, 3.1 or 3.2 depends on 1.7.
- Graph re-verified after every edit: 37 issues, no cycles, no dangling refs, **R7 still holds**.

The pass's own framing of the pass-1 fix — *"replaced an overstated dismissal with an overstated
promise, the same failure mirrored"* — is carried verbatim into the Approach, because a plan that
over-corrected once should say so where the next reader will see it.

Re-dispatched to a fresh red-team cycle (pass 3) per REQ-PLAN-030.
