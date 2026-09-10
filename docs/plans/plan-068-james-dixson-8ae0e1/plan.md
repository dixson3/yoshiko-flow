---
type: Plan
okf_spec: OKF-PLAN
description: 'Repair the land close chain: cover the --apply preamble with tests,
  make land work under execute.worktree false, and close the L8-L16 injection and
  measurement defects'
id: plan-068-james-dixson-8ae0e1
author: james-dixson
created: '2026-09-09'
status: reconciling
deliverable_class: standard
fingerprint: 463e92860dc3a16bc1f8232d86152c8f30e5f3c6faa24434cbd7c906d8e64dbf
epic: yf-mol-cdqp
---
# Plan: Repair the land close chain: cover the --apply preamble with tests, make land work under execute.worktree false, and close the L8-L16 injection and measurement defects

**ID:** plan-068-james-dixson-8ae0e1
**Author:** james-dixson
**Created:** 2026-09-09
**Status:** reconciling
**Deliverable-class:** standard
**Epic:** yf-mol-cdqp
**Fingerprint:** 463e92860dc3a16bc1f8232d86152c8f30e5f3c6faa24434cbd7c906d8e64dbf

## Objective
Repair the land close chain: cover the --apply preamble with tests, make land work under execute.worktree false, and close the L8-L16 injection and measurement defects

## Motivation
`land` is the single operation that carries a plan from a green execute branch to a merged,
pushed, reconciled, closed and redeployed state. It is the highest-consequence code path in
yf-plan: every step after L2 is either outward-facing or destructive, and the operator's one
informed-consent grant covers all of it.

Nine open beads across seven upstream issues say that path is not trustworthy in three
distinct ways:

1. **It is untested where it matters most.** The `--apply` CLI preamble — six gates in
   sequence, ending in `recover()`'s four-way branch, the one that can re-push — has zero
   test coverage (#349). Inside that same preamble, `_land_tty_gate(allow_list=[None])`
   opens the consent gate unconditionally and its test is vacuous (#334).
2. **It has no injection seam.** L8–L15 bypass `ctx.run` for bare `subprocess.run`, so the
   rehearsal must replace whole steps and three of fifteen are never exercised (#348); L14's
   `bd list` is the only close-chain subprocess launched without `cwd=ctx.root` (#348).
3. **It launders failed measurements into green ones.** L16 reports an unreadable unpushed
   count as `0` (#350) — a failed measurement that reads as success. `LAND_DIGEST_EXCLUDED`
   omits `resolved_target_tip` and `merge_preview`, which L4/L6 self-mutate, making every
   resume at or after `L_VALIDATED` a guaranteed digest mismatch (#353). `land --dry-run`
   never checks that a draft body satisfies `requires_mention`, so that failure surfaces only
   after the writes are public (#352).

Cutting across all of it: **`land` remains incompatible with `execute.worktree: false`**
(#331). Under in-place mode no execute branch is ever created, but `land --dry-run` halts
with `execute-branch-missing`, so the landing route is unreachable. **Two** consecutive plans
— 062 and 063 — worked around it identically, each with a hand-cut `git checkout -b` as an
explicit numbered Issue 0.7 in its own Epic 0. That is accumulating residue, not an edge case.

> **Correction (EXP-001, measured).** The bead `yf-f7lq`, issue #331's residue note, and
> `plan-063/assets/residual-issues/r4-331-residue.md` all claim **three** plans including
> plan-061. That is **false for plan-061**: it ran in *worktree* mode (`context.md:72`), has no
> Issue 0.7, and never mentions #331 — corroborated by its down-merge commit `7dd863c`. The
> residue table is mis-attributed and should be corrected upstream by this plan.

Who is affected: every plan that lands. The workaround tax is paid per plan, and the untested
regions are exactly the ones whose failure mode is a public, irreversible write.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #348 | The landing close chain bypasses `ctx.run` | include | **Fully resolved here.** Beads `yf-9yb0`, `yf-i127`. Closes on Epic 1 | Epic 1 (1.1-1.6) |
| #331 | `land` is incompatible with `execute.worktree: false` | include | **Fully resolved here.** Bead `yf-f7lq`. Closes on Epic 2 | Epic 2 (2.1-2.6) |
| #349 | The `land --apply` executor frame is outside REQ-LAND-030's wrapper and the test suite | partial | **Correction only** (Epic 3). The preamble tests and the bookkeeping guard are **plan-069 (Plan B)**. Per pass-1 Upstream Assessment, #349 is claimed across both plans — **it must NOT be closed by this plan** | 3.1, 3.2 (correction only) |
| #353 | `LAND_DIGEST_EXCLUDED` omits self-mutated facts | partial | **Correction only** (Epic 3): L4-not-L6, and `predicted_tree` stable. The projection fix is **plan-069**, and pass-1 C2/C3 showed its design is not yet settled | 3.1, 3.2 (correction only) |
| #334 | `_land_tty_gate(allow_list=[None])` opens the consent gate unconditionally | deferred | Moved to **plan-069 (Plan B)** at the A/B split | — |
| #350 | A measurement that failed is reported as a green number | deferred | Moved to **plan-069 (Plan B)** | — |
| #352 | `land --dry-run` never checks `requires_mention` | deferred | Moved to **plan-069 (Plan B)** | — |
| #360 | `land --apply` ignores a validated 'skip' adjudication | exclude | Operator decision at scoping — separate adjudication-semantics axis | — |
| #326 | `draft_body_path` posts bundle files verbatim | exclude | Operator decision at scoping — OKF-conformance axis | — |
| #304 | The self-authorization residue #301 does not close | exclude | Operator decision at scoping — would widen to a consent-model redesign | — |

## Investigation Findings

**Pre-investigation checkpoint.** Investigation wisp: `yf-wisp-ac7`. Four experiments, dispatched in parallel.

| Exp | Question | Why it must be answered before drafting |
| :-- | :-- | :-- |
| EXP-001 | Under `execute.worktree: false`, exactly where does `land` halt, and what are the candidate in-place landing semantics? (#331) | The fix could be "make `land` skip L1/L2", "make `worktree ensure` always cut the branch", or "add an explicit in-place route". These have very different blast radii and the plan's epic structure depends on which. |
| EXP-002 | What is `LandingContext.run` today, what do L8–L15 actually invoke, and what is the blast radius of routing every step through it? (#348) | The chosen approach is seam-first. If the seam cannot carry every L-step call shape, the approach must change before drafting, not during execution. |
| EXP-003 | Which facts do L4/L6 self-mutate, and does widening `LAND_DIGEST_EXCLUDED` restore resume — or does it blind the digest to a change that matters? (#353) | The digest exists to detect a changed world between dry-run and apply. A wrong exclusion converts a correctness check into a rubber stamp; this must be settled by measurement, not by reasoning. |
| EXP-004 | What does the existing test suite actually cover for the `--apply` preamble, `recover()`'s four-way branch, and `_land_tty_gate`? Does a drivable rehearsal harness exist? (#349, #334) | "Zero coverage" is the bead's claim. The plan's test epics must be sized against measured coverage, and #334 asserts an existing test is *vacuous* — that needs confirming, not assuming. |

### EXP-001 — in-place landing ([full finding](findings/exp-001-worktree-false-landing.md))

The halt is `_land_manifest:8063`, a bare `git rev-parse --verify <plan-id>-execute`.
**`_land_manifest` never calls `_worktree_opted_out()`** — the manifest has no concept of
in-place mode; the halt is a branch-existence check that in-place mode happens to fail.

**Four of twenty steps assume a branch.** L1 is *harmful*: it never checks out the execute
branch, so in-place it merges the target into whatever HEAD is — measured `Already up to date.`,
**exit 0**, verdict `pass`. L2 the same. L4's tree assertion is the only real safety net, and it
fires *after* the merge is committed and the lock released, with a misleading diagnostic.
**L18 needs no work** (teardown already degrades correctly). L19 is degraded, not broken.

**Design (b) — cut and check out the branch even when opted out — has the strongest evidence:**
a measured passing dry run (`verdict pass`, `halts []`, exit 0) with no other manifest change,
and the smallest SPEC surface (**REQ-BRANCH-001/002/004, zero `REQ-LAND-*`**). Design (a) costs
three of the most test-pinned requirements in `spec/landing.md`; design (c) is **refuted** —
measured, it turns a loud halt into a vacuously-green landing that merges nothing.

**REQ-BRANCH-004 is the one requirement (b) contradicts** ("never left on a plan branch") and
needs an explicit in-place carve-out in the same change-set.

**Two adjacent in-scope defects surfaced:** L1's silent self-merge, and
`_land_merge_preview.changed_paths` using a **symmetric** `git diff` so it cannot distinguish
"branch ahead" from "branch behind" — measured reporting a change set the merge will not land.

**Absence:** no test anywhere exercises `_land_manifest`, `_land_execute`, or any L-step under
`execute.worktree: false`. The spec has **zero** hits for in-place landing.

### EXP-003 — the digest exclusion ([full finding](findings/exp-003-digest-exclusion.md))

**Premise confirmed, remedy refuted.** The guaranteed post-`L_VALIDATED` mismatch is real. But
the bead's proposed WIDE exclusion makes the digest **blind to all three foreign-landing
classes** — clean, conflicting, and delete — and a *conflicting* foreign landing then
**validates as `pass`**, so the landing proceeds to L2 and discovers a conflicted tree. That is
precisely what REQ-LAND-018 exists to prevent. **`yf-jp7z` must not be planned against as
written.**

**Scope is larger than #353 states:** the landing self-mutates **five** covered facts across
**four** resume points (L2's dirt ×2, L4's tip + two `merge_preview` sub-fields, L15's status).
The bead's two-field fix leaves resumes after L3 — the likeliest halt, the multi-minute FULL
tier — and after L15 still broken.

**Two factual errors in #353 to correct upstream:** L6 mutates neither fact (**L4 alone** does),
and `predicted_tree` is *not* invalidated by the landing's own merge.

**A measured alternative exists.** `merge_preview.predicted_tree` is the only covered field
stable under the landing's own merge and unstable under every foreign landing, so a **sub-field**
exclusion preserves detection on all three classes WIDE loses. It does not fix the L2/L15 points;
the journal-projection fix does, and its measured blocker is that `_land_execute` forwards only
`step` to the journal, so L4's already-computed `merged_tree` never becomes durable.

**Absence:** no test in the suite ever computes a digest on a post-L4 tree. REQ-LAND-036's own
verifier *synthetically* flips facts on a repo where no merge ever happened.

### EXP-002 — the `ctx.run` seam ([full finding](findings/exp-002-ctxrun-seam.md))

**Approach validated by measurement.** A zero-stub rehearsal spike, same runner injected into both
copies, three whole-step stubs deleted in both:

| | terminal journal | step rows | programs the runner saw |
| :-- | :-- | --: | :-- |
| **unpatched** | `L_RECONCILED`, halted at `l14_pour_fidelity` | 18 | **`['git']` only** |
| **patched** | `L_DONE` | **23** | `['bd', 'git', 'uv', 'yf']` |

The unpatched run proves the seam is genuinely bypassed — the injected runner never saw a single
`uv` or `bd` call. **Routing L14 fixes `yf-i127` as a side effect of `cwd or self.root`;** no
separate `cwd=` edit is needed.

**`yf-i127` is partly REFUTED.** An AST scan finds **8** bare calls inside L-steps, 6 with `cwd`
and **2 without** — L14's `bd list` (9592) *and* **L17's `bd show` (9759)**. The bead's "the ONLY
one" holds only if "close chain" is read narrowly as L8–L15. L17's is arguably worse: it is the
step's *only* verification signal under REQ-LAND-019, so reading the wrong database fails a push
that actually succeeded. **Scope the epic to all 8 sites, not 7.**

**The seam needs to grow nothing** — all 8 shapes fit `_dispatch(prog, args, cwd=None)` unchanged.
No `stdin`, `Popen`, pipe, `check=`, `timeout=`, `env=`, `shell=` or `os.system` anywhere.

**The epic is SMALL:** 8 call sites, **1** assertion to update (`test_land_apply.py:1327`,
`{"uv"}` → `{"uv","bd"}` — itself an improvement), 3 stubs to delete, 1 new REQ. Not the wide
refactor plan-063 deferred it as; the tests are almost entirely AST-based and survive untouched.

**SPEC-first: the seam is specified NOWHERE** — zero grep hits across `spec/` and `SPEC.md`. It
lives only in a docstring and one test. **`REQ-LAND-037` is confirmed free** and should state that
every process a landing step launches goes through `LandingContext.run` with `cwd` defaulted to the
checkout root — making **both faces of #348 one normative sentence**.

**Two hazards to carry into execution:** the L8–L15 loop builds `args` starting with `"uv"`, so the
routed form must slice the program off or the seam receives `uv` twice; and
`test_pour_fidelity_inconclusive_is_not_a_divergence` binds `f.returncode` by name in an AST walk,
so **renaming the local bindings** `f`/`g`/`s`/`bl`/`back`/`proc` **would make it quietly vacuous**.

### EXP-004 — preamble coverage ([full finding](findings/exp-004-preamble-coverage.md))

**"Zero coverage" is REFUTED as literally stated; the substance holds.** Measured union coverage
(the suite's only real-CLI test runs in a `uv run` subprocess and is invisible to ordinary
coverage — a plugin was needed to see it):

| Region | Stmts | Missed | % |
| :-- | --: | --: | --: |
| `--apply` preamble (8483–8598) | 44 | **17** | **61.4** |
| `_land_tty_gate` | 24 | 6 | 75.0 |

**The 17 missed statements are, without exception, the gate-REFUSAL bodies.** The honest claim:
*61.4% coverage, all happy-path plus exactly one refusal (tty, exit 3); and there is **no "no write
occurred" assertion anywhere in the file**.* `yf-acrn`'s headline must be restated or a red-team
pass refutes it in one coverage run.

**The preamble has NINE steps, not six.** The bead omits **step 8, `_land_repreview_or_halt`** —
the very gate the issue's own prose calls the `halt_class 5` culprit. Sizing the epic off six items
under-scopes it by ~20%.

**A latent re-push path.** The CLI fall-through at 8571 means an `action` outside
`{start,done,halt,resume}` silently yields `resume_from=None` → a fresh landing from L0,
**re-running `l6_push_one` and `l7_reconcile_writes`**. `recover()` is total today, so this guards
against a future edit — but it is the one line between an unhandled action and a re-push.

**`#334` fully confirmed, and its test is PROVABLY vacuous.** `tty` is `None`, so the test's
`or "/dev/ttys999"` fallback builds a list that cannot match, the gate refuses, the first disjunct
short-circuits, and the allow-list test is never reached. **Vacuity probe: the identical assertion
passes against a stub gate that ignores `allow_list` entirely.** Corroborated at line level —
across the entire suite `_land_tty_gate` **never once returns `allowed: True`**.

**`yf-pyqn` confirmed, residue wider than stated.** The wrapper covers **line 10143 and nothing
else**. Steps that *return* rather than raise escape it entirely — measured bare tracebacks for
`AttributeError`, `KeyError` and `ValueError`. **Two sites the bead omits:** the skip-path journal
write (10106) and `_land_resume_done` (10075). And `land_cmd:8589` has **no outer `try`**, so these
reach the operator as a raw traceback with no envelope or halt class.

**The rehearsal cannot reach the preamble** — it calls `_land_execute` directly, executing **zero**
of the 44 preamble statements, and is **never run by pytest** (the tests read a committed artifact).
Its `_build_sandbox` is reusable as-is.

## Approach

> **This is PLAN A of a two-plan split** (pass-1 C1, operator-confirmed). Plan A is the **enabling
> half**: it lands the `ctx.run` seam and makes `land` reachable under `execute.worktree: false`.
> **plan-069 (Plan B)** carries the preamble tests, the executor-bookkeeping guard, the digest
> projection and the two measurement defects.
>
> The cut is not arithmetic. **Plan A lands the in-place-landing fix, so Plan B's own landing is
> the first one in this repo that does not pay #331's tax.** The red-team verified nothing crosses
> the seam backwards.
>
> Corrected from the v1 draft: this plan's v1 was **37 issues with a dependency chain 8 nodes
> deep** — the v1 risk table stated 33 and depth 3, and both were wrong. Plan A is **23 issues** across 5 epics, with a longest dependency chain of **6 nodes** and 16 success criteria — all figures re-measured from `plan_extract.py` after each revision, never asserted.

**Seam first, then tests on the seam; SPEC ahead of both.** EXP-002 measured that this ordering is
not merely tidy — it is what makes the rest possible. The zero-stub rehearsal spike reached
`L_DONE` with 23 step rows once the seam was routed, against 18 rows and a halt without it, and the
unpatched runner **never saw a single `uv` or `bd` call**. Tests written before the seam would have
to monkeypatch whole functions, which is the `#340` stub-fidelity hazard this plan is partly here
to retire.

The work decomposes into six independent repair axes plus a correction pass, sequenced so the
cheapest enabling change lands first:

1. **The seam (E1)** — 8 call sites, 1 assertion, 3 stubs, 1 new requirement. Measured small.
   Subsumes `yf-i127` mechanically via `cwd or self.root`.
2. **In-place landing (E2)** — design (b) from EXP-001: `worktree ensure` cuts *and checks out* the
   branch even when opted out. Measured passing dry run, and the **smallest SPEC surface**
   (REQ-BRANCH-001/002/004, zero `REQ-LAND-*`). Carries the two adjacent defects EXP-001 found.
3. **The preamble (E3)** — 17 uncovered refusal statements, 8 refusal cases, built on the seam and
   on `land_rehearsal.py`'s existing sandbox builder.
4. **Executor bookkeeping (E4)** — `yf-pyqn` option (b), a guard around the loop body.
5. **The digest (E5)** — journal projection over all **five** self-mutated facts, per the operator
   decision after EXP-003 refuted the bead's own remedy.
6. **The two measurement defects (E6)** — L16's laundered count and `--dry-run`'s missing
   `requires_mention` check.
7. **Upstream corrections (E7)** — five measured corrections to beads and issues.

**Design choices explicitly rejected, with the measurement attached** (so a later reader does not
re-litigate them):

| Rejected | Why, measured |
| :-- | :-- |
| Digest WIDE exclusion (`yf-jp7z` as written) | EXP-003: blind to all three foreign-landing classes; a *conflicting* foreign landing validates `pass` and the landing discovers the conflict at L2 |
| Re-computing the digest at resume boundaries | EXP-003: provably vacuous — compares reality to itself |
| `land` synthesizing the branch at dry-run (#331 design (c)) | EXP-001: turns a loud halt into a vacuously-green landing that merges nothing; violates REQ-LAND-026 |
| Keep the halt, flip `resolvable_by_agent` (#331 design (d)) | EXP-001: only automates the workaround, and cuts the branch at *land* time — the B1 no-op case again. Safe only combined with design (b), which supersedes it |
| An explicit in-place route skipping L1/L2 (#331 design (a)) | EXP-001: costs REQ-LAND-002/004/006 — three of the most test-pinned requirements — and needs a fourth per-step state. **Retained as a documentation obligation only** (E2.6) |

**This plan pays #331's tax one last time.** This repo is configured `execute.worktree: false`
(`config.local`), so plan-068 executes in-place and must hand-cut its own execute branch exactly as
plans 062 and 063 did — before any SPEC edit, because in-place mode has one address space and a
commit made before the branch exists lands on `main` and escapes the merge L3 validates. Issue 0.1
is that cut. It is the last time any plan should need it.

## Epics

> **Line numbers are annotations, not anchors** (pass-1 C11). Every citation below is a
> **symbol plus a quoted source fragment**; the `@NNNN` figures are "as measured at investigation
> time" only. Epic 1 edits eight sites and Epic 2 edits `_worktree_ensure`, so any line number in a
> later issue is stale by construction — re-anchor on the symbol and the quoted fragment.

### Epic 0: SPEC-first, and make this plan's own landing reachable
- Issue 0.1: **Create and check out `plan-068-james-dixson-8ae0e1-execute` in the PRIMARY checkout**, cut from the pinned base (`git checkout -b <plan-id>-execute main`), immediately after §5.2a's in-place fallback. This repo is `execute.worktree: false` (`.yf/plan/config.local.json`, verified at pass-1), so `_worktree_ensure` short-circuits on `opted-out` before any branch creation and `land --dry-run` would halt `execute-branch-missing`. **Placed FIRST, before every SPEC edit:** in-place mode has one address space, so a commit made before this branch exists lands on `main` and escapes the merge L3 validates. Precedent: plan-062 / plan-063 Issue 0.7. **Record the base commit SHA to `assets/execute-base.txt`** in the same step — SC9's ordering check reads it, and pinning to the recorded base is what makes that check orientation-independent (pass-4 C5).
- Issue 0.2: **Allocate and RECORD the full `REQ-*` id set this plan needs, in one place.** Plan A needs **two new ids** — `REQ-LAND-037` (the seam) and `REQ-LAND-038` (merge-preview directionality) — **plus amendments to existing ids**, which consume no new number: `REQ-LAND-002`, `REQ-LAND-004`, `REQ-BRANCH-001`, `REQ-BRANCH-002`, `REQ-BRANCH-004`. **`REQ-LAND-018` and `REQ-LAND-036` are NOT in this list** — pass-4 C6 caught v3 over-claiming them, contradicting Issue 3.3 and plan-069's own text, which both assign those two to **plan-069**. **Corrected at pass-3 C8:** v2 said "three new ids" and counted an *amendment* as an allocation, and Issue 0.6's dirty-tree refusal class had no id at all — the same defect pass-2 C4 found one issue over. **Decide and record** whether that refusal class is a new id or a clause inside `REQ-BRANCH-002`; Gate 1's alternation must match whatever 0.2 records. `REQ-LAND-037`/`-038` verified free (0 occurrences across `SPEC.md`, `spec/landing.md`, `spec/phases.md`); `REQ-LAND-027` is reserved at `landing.md:384`. Every id above is spelled in full at least once in this plan so `plan_extract.py` can see it (pass-3 C9).
  - depends-on: 0.1
- Issue 0.3: SPEC — add **`REQ-LAND-037`**: every process a landing step launches **directly** is issued through `LandingContext.run`, with `cwd` defaulting to the checkout root; every *indirect* launcher reachable from an L-step is a **declared ctx-less helper** that resolves its working directory from an explicit argument.

  **DERIVE THE SET MECHANICALLY — and SEED THE CLOSURE ON PROCESS-LAUNCH PRIMITIVES, NEVER ON A HAND-PICKED HELPER SEED.** Four consecutive passes have found a hand-written enumeration short. pass-4 showed that even the *seed* was short: seeding on `{subprocess, _run_git, _run_shell, _run_change_validation}` misses **`_repo_root`** and **`_git_root`**, both bare `subprocess.run(["git", "rev-parse", "--show-toplevel"])` with **no `cwd`**, falling back to `Path.cwd()` / `Path(".")` — the `yf-i127` defect class exactly. Seed only on process-launch attribute calls (`subprocess.*`, `os.system`/`popen`/`spawn*`, `pty.*`), mark every function containing one as a direct launcher, take the transitive closure, then BFS from every `_land_l<N>_*` function. Land the result as **`LAND_CTXLESS_HELPERS: tuple[str, ...]`** in `plan_manager.py`, quoted by `spec/landing.md`, with a companion test pinning the two together.

  **STATE THE CLOSURE DEPTH NORMATIVELY, AND RECORD THE COUNT AS DERIVED — NOT QUOTED.** REQ-LAND-037's word "reachable" is *transitive*. The **depth-1 frontier is six**; **executing this issue's own mandated derivation yields THIRTEEN**, not the ten an earlier draft asserted (pass-5 C1 — the same constant-vs-SPEC mismatch, one number over, which is itself the argument for deriving rather than quoting). The thirteen: `_branch_exists`, `_dirty_outside_plan_dir`, `_git_root`, `_land_abort_merge`, `_land_capture_conflict`, `_land_changed_set`, `_registered_worktree_paths`, `_repo_root`, `_run_change_validation`, `_run_git`, `_run_shell`, `_validate_merged`, `_worktree_teardown`. **The SPEC quotes whatever the script emits**; it does not restate a number. **Exclude the seam edge** (`ctx.run` / `_dispatch`) from the closure explicitly — today that works only by accident, because `self.run = self._dispatch` is an *assignment* so the AST resolves no callee named `run`; if a future edit makes `run` a real `def`, the closure explodes to nearly the whole module.

  **RETIRE THE `REQ-LAND-031` CARVE-OUT — it was an over-read (pass-4 C3, verified).** The requirement mandates *"call `_worktree_teardown` with `force=False` in **keyword** form … and **branch on the returned `status`**"*. It constrains the **call**, and says nothing about how the callee launches. `_worktree_teardown(ctx.plan_dir, force=False, runner=ctx.run)` satisfies it **verbatim** while fully on the seam — the precedent already exists in this file at L16, `_dirty_outside_plan_dir(ctx.plan_dir, root=ctx.root, runner=ctx.run)`. EXP-001 recorded L18 as "deliberately off-seam per REQ-LAND-031"; the finding over-read the requirement and v3 of this plan adopted the over-reading unchecked.

  **The declared set is NOT empty, and the plan must not claim it will be.** pass-5 measured the remainder directly: after Issue 1.1 routes `_validate_merged` and `_worktree_teardown`, **three depth-1 helpers stay off-seam** — `_land_abort_merge` and `_land_capture_conflict` (L1/L2's conflict-recovery path) and `_land_changed_set` (close chain, L19) — plus their transitive launchers. All three take an **explicit root**, so they satisfy 0.3's ctx-less-helper clause; none is structurally unroutable. **Choose one and say so** (this is Issue 1.1's scope decision): extend 1.1 to give those three a `runner=` — after which the constant really is empty — or declare them the expected non-empty content of `LAND_CTXLESS_HELPERS`, with the reason recorded. **What is not safe is landing a constant the SPEC says should be empty.** Consequence for Issue 2.5 either way: the L1/L2 conflict path reaches a real `git merge --abort` against `ctx.root` that the injected runner never sees — contained, because the root is explicit, but a test asserting "every process went through the runner" would be false on that path.

  **Correcting v1's boundary claim:** it named `_land_epic_from_bd` and `_land_route_record_findings` — measured, neither is called from any L-step, so both were the wrong ones. Their fix (Issue 1.4) still needs its own clause: those two resolve their working directory from an explicit root argument. Living-amendment-log entry.
  - depends-on: 0.2
  - resolves-upstream: #348 (include)
- Issue 0.4: SPEC — amend **`REQ-LAND-002`** and **`REQ-LAND-004`** to state that **L1** must operate on the execute branch rather than on ambient HEAD when there is no execute worktree, and to record **L2's in-place behaviour as a declared scope boundary** rather than a specified-then-unimplemented one (pass-3 C7). Measured, L2 is where in-place actually bites: `_land_l2_merge` runs `git checkout <target>` **in `ctx.root`**, and under `execute.worktree: false` `ctx.root` *is* the execute checkout — so L2 switches the one and only working tree off the execute branch, and the subsequent `git pull --rebase`'s return code is ignored. **No issue in Plan A implements or tests L2 in-place**, so specifying it here would leave SC9c/2.6 trivially green (SPEC and implementation "agree" because neither changed). Record the measured behaviour and the boundary; route the L2 work to plan-069 or a follow-on. This is the SPEC precondition for Issues 2.3 and 2.6, which the v1 draft omitted (pass-1 C5) and whose ordering v1 inverted. `SKILL.md` §6.1 already specifies the in-place route in prose (*"In-place (fallback) mode skips the merge"*) and `land` never implemented it; this makes that prose normative.
  - depends-on: 0.2
  - resolves-upstream: #331 (include)
- Issue 0.5: SPEC — add **`REQ-LAND-038`**, a **merge-preview directionality** requirement: `_land_merge_preview.changed_paths` states what the merge **will land**, not the symmetric difference. Names the consequence explicitly — `touches_skills`, and therefore L19's redeploy precondition, is derived from it. SPEC precondition for Issue 2.4, absent from v1 (pass-1 C5).
  - depends-on: 0.2
- Issue 0.6: SPEC — add an in-place carve-out to **`REQ-BRANCH-004`** ("never left on a plan branch"), which design (b) deliberately contradicts for the duration of in-place execution; extend **`REQ-BRANCH-001`/`-002`** to a branch cut with no `worktree add`; and add the **dirty-tree precondition** on the in-place path as a declared refusal class (the SPEC precondition for Issue 2.2, absent from v1 — pass-1 C5).
  - depends-on: 0.2
  - resolves-upstream: #331 (include)

### Epic 1: The `ctx.run` seam
- Issue 1.1: Route **all 8** bare process calls inside L-step functions through `ctx.run`. By symbol: `_land_l5_advisory_recheck` (`uv run … recheck-criteria`), the `LAND_CLOSE_CHAIN` loop in `_land_l8_to_l15_close_chain` (one site, seven launches), `_land_l12_close_cascade`, and in `_land_l13_l15_finish` the `complete-gate` call, **the cwd-less `bd list --all --include-gates --limit 5000 --json`**, the `pour_fidelity.py` call and `update-status`; plus **the cwd-less `bd show <bead> --json` read-back loop in `_land_l17_residual_mirroring`**. Scoped to 8 sites, **not** the 7 that `yf-i127`'s "L8–L15" wording implies. **Patch hazard:** the close-chain loop builds `args` beginning with `"uv"`; the routed form must slice the program off or the seam receives `uv` twice. **Do not rename the local bindings** `f`/`g`/`s`/`bl`/`back`/`proc` — `test_pour_fidelity_inconclusive_is_not_a_divergence` binds `f.returncode` by name in an AST walk and would go quietly vacuous. **Give `_worktree_teardown` and `_validate_merged` BOTH a `runner=` AND a `root=` parameter** on the `_dirty_outside_plan_dir` model (which already carries both), so L3 and L18 route through the seam and the REQ-LAND-031 carve-out disappears. **`runner=` alone closes only half the escape** (pass-5 C4, measured): `_validate_merged`'s tier-1 decision is three **filesystem/config** probes keyed on `_repo_root()` — `_approved_manifest_present`, `_change_validation_script`, and `_resolve_validate_cmd` → `_read_config` — and **no runner intercepts a filesystem read**. Without `root=`, a sandboxed test that does not `os.chdir()` still resolves the **real** repo's `CHANGE-VALIDATION.md` and the **real** engine script, then hands the fake a command whose `cwd` is the real repo. Execution would be contained; *resolution* would not. `_worktree_teardown` has the same shape via `_git_root()`. **Also decide `_run_shell`** (pass-5 C5): it is `shell=True` over a command *string* with no cwd, so it does not fit the `(prog, args, cwd=)` contract — route it as `runner("sh", ["-c", cmd], cwd=root)` and update the program-set expectation in `test_each_step_invokes_the_RIGHT_EXECUTABLE` plus Issue 2.5's argv-recognising fakes, or declare tier-2 `validate-cmd` out of the seam. **This is a SAFETY fix, not tidiness** (pass-4 C4, verified): both resolve their root via `_repo_root()` / `_git_root()`, which are cwd-less and fall back to `Path.cwd()` / `Path(".")` — so in a pytest test that does not `os.chdir()`, L3 would run the **real** repo's FULL `CHANGE-VALIDATION.md` tier and L18 would run `git worktree remove` / `git branch -d plan-068-…-execute` / `git worktree prune` **in the real yoshiko-flow checkout**, against the branch Issue 0.1 just cut. Issue 2.5's runner contract cannot prevent this, because neither call reaches `ctx.run`. **Decide the `env=` question here too** (pass-1 Missing): add an `env` parameter to `_dispatch` now, or record in the issue that it is out of scope and why — Plan B's `recover()` and L19 tests are the consumers that would want it.
  - depends-on: 0.3
  - resolves-upstream: #348 (include)
- Issue 1.2: Update the tests the refactor breaks. **There are EIGHT, not one** — pass-5 prototyped Issue 1.1 end to end and measured the suite going from `4 failed, 62 passed` (sandbox-artifact baseline) to `12 failed, 54 passed`. Six break on **stub arity** (`TypeError: … unexpected keyword argument 'root'`): `test_l18_blocked_teardown` (three `lambda pd, force=False:` stubs), `test_l18_delegates_branch_delete`, `test_each_step_invokes_the_RIGHT_EXECUTABLE` (`_teardown_ok`), and the three `_validate_merged` stubs in `test_red_full_tier_halts_with_lock_held`, `test_inconclusive_validation_is_not_coerced_to_fail` and `test_executor_halts_before_any_destructive_stage`. One breaks on an **exact kwargs-dict equality** (`test_prune_is_strategy_aware`). One fires its **own anti-vacuity guard** (`test_a_skipped_step_is_surfaced_never_silent`: *"halted at l3_validate_merged before reaching the skipped step"*). All eight are mechanical. **This is `check_mock_fidelity` working as designed** — `_teardown_ok`'s docstring says its arity is guarded by that check binding `inspect.signature`, and the signature change is exactly the class of edit it exists to catch. The L17 change from `{"uv"}` to `{"uv", "bd"}` remains an improvement: REQ-LAND-019's read-back becomes visible to the seam for the first time.
  - depends-on: 1.1
- Issue 1.3: Add an **AST** mechanical check (grep cannot do it): no direct process launch inside any function matching `_land_l\d+_*`, **keyed on the derived launcher set from 0.3's closure rather than a token list** (pass-4 C9: `os.system` occurs zero times in this module, so a token list is the same hand-written-enumeration shape 0.3 just retired), **and no call to an indirect launcher outside the declared set**. The second clause is what makes the check match REQ-LAND-037 as 0.3 states it — pass-2 C1 measured that a token-keyed check on `subprocess.*` is structurally blind to `_run_git`, so SC1 and SC2 would both pass while the requirement was violated at five call sites. **Read the `LAND_CTXLESS_HELPERS` constant 0.3 lands** — not a second hand-written list, and not the call graph alone (which would make the check tautological). A companion test pins the constant to the SPEC text, so the two enumerations cannot drift (pass-3 C2).
  - depends-on: 1.1
- Issue 1.4: **Fix the two out-of-L-step cwd-less `bd` calls** — `_land_epic_from_bd` and `_land_route_record_findings` — rather than leaving them advisory. pass-1 flagged that Issue 1.3's advisory tier would let this plan close #348's normative sentence while two calls still read a database from the wrong cwd. Neither has `ctx` in scope, so they need an explicit root argument, not the seam.
  - depends-on: 0.3
- Issue 1.5: Delete the whole-step stubs from `land_rehearsal.py` and pass `runner=` instead. **It disables SIX steps via FIVE monkeypatches plus one decision-level skip** (pass-3 C4, pass-4 C8): the three `_land_l*` step lambdas, **plus `pm._validate_merged`** (L3's entire validation, replaced by `{"status": "pass", "engine": "rehearsal-stub"}`) and **`pm._worktree_teardown`** (L18) — **plus L19, disabled at `land_rehearsal.py:120` by the decision-level adjudication `"l19_redeploy": "skip:sandbox has no yf binary…"`**, which no monkeypatch-keyed enumeration can see. Once Issue 1.1 gives the two helpers a `runner=`, both become injectable and the rehearsal is genuinely stub-free at L3 and L18; L19's decision-level skip must be surfaced in `stubbed_steps` rather than hidden. Derive `stubbed_steps` from **both** sources. **Derive `stubbed_steps` from `LAND_EXECUTOR`** rather than hand-writing it: the current record names three labels while hiding five L-numbers (L9, L10, L11, L13, L14), with `l14_pour_fidelity` absent entirely — the "second enumeration that can drift" defect `spec/landing.md` forbids elsewhere.
  - depends-on: 1.1
- Issue 1.6: Make the rehearsal **run under pytest**. The two tests consuming it read a committed JSON artifact and never execute the harness, so it can rot silently. **State honestly what it does and does not establish** (R9): with an injected runner returning `[]` for `bd list` and `0` for `pour_fidelity`, L14's DAG comparison is not exercised — a poured-bead fixture is out of scope here, and Issue 1.5's derived `stubbed_steps` is what keeps the remaining gap **visible** rather than hidden.
  - depends-on: 1.5

### Epic 2: In-place landing, and the defects it exposes
- Issue 2.1: `_worktree_ensure` cuts **and checks out** `<plan-id>-execute` from the pinned base even when `execute.worktree` is false, returning `viable: false, reason: "opted-out", branch: <name>`. Design (b): measured `land --dry-run` → `verdict pass`, `halts []`, exit 0 with **no other manifest change**. **Create-without-checkout is silently wrong** — the `checkout -b` half is not optional. **Implement the three-way branch** (pass-2 C5): branch absent → `checkout -b <b> <pinned-base>`; branch exists → plain `checkout`; already on it → no-op. `_worktree_ensure` is called on **every** `execute` invocation and its own docstring promises "idempotent create-or-reattach", while `git checkout -b` on an existing branch exits 128 — multi-session execution is the normal case. Note the `opted-out` short-circuit sits at the **top** of the function, before `_worktree_viability`, `_resolve_execute_base` (the REQ-BRANCH-002 pinned base) and the bd-resolution probe, so design (b) must reach the base resolver from the in-place path; **state whether the bd-resolution probe applies in-place**. **Opportunistic fix while in this code** (pass-2 C13): the `opted-out` verdict's `detail` string and `_worktree_opted_out`'s docstring both name `.yf-plan.local.json`; the live file is `.yf/plan/config.local.json`.
  - depends-on: 0.6
  - resolves-upstream: #331 (include)
- Issue 2.2: Add the **dirty-tree precondition** to the in-place path, implementing the refusal class 0.6 declares. Measured: `git checkout -b` refuses on a dirty divergent tree (`error: Your local changes would be overwritten by checkout`, exit 1, HEAD unmoved) — a failure class `_worktree_ensure` has no guard for today.
  - depends-on: 0.6, 2.1
- Issue 2.3: **Fix L1's silent self-merge.** `_land_l1_down_merge` never checks out the execute branch — `wt = ctx.worktree if ctx.worktree.is_dir() else ctx.root` — so in-place it merges the target into whatever HEAD is: measured `Already up to date.`, **exit 0**, verdict `pass`, journals `L_DOWNMERGED`. Implements 0.4. **Necessity, stated honestly** (pass-2 C12): once 2.1 lands, `ctx.root`'s HEAD *is* the execute branch, so EXP-001's measured self-merge disappears with 2.1 alone. This issue is **defence-in-depth against reliance on ambient HEAD** — an explicit checkout rather than an accident of what HEAD happens to be — and SC5 is written to fail under 2.1-only. Not one of the nine beads; absorbed at the operator's direction after EXP-001.
  - depends-on: 0.4, 2.1
- Issue 2.4: **Fix `_land_merge_preview`'s symmetric diff.** `git diff --name-only <target> <execute_branch>` cannot distinguish "branch ahead" from "branch behind"; measured reporting `changed_paths: ["work.txt"]` and `available: true` for a merge guaranteed to be a no-op. Implements 0.5. **Also settle `_land_changed_set`** (pass-1 Missing): EXP-001 measured L19's `HEAD^1..HEAD` degrading in-place because HEAD is not a merge commit. Design (b) mostly fixes this by making HEAD a real merge commit — **state that reasoning explicitly and test it**, rather than leaving it an unstated inference about the redeploy precondition.
  - depends-on: 0.5, 2.1
- Issue 2.5: Add `test_land_manifest.py` coverage for the in-place manifest shape, and an **end-to-end** in-place landing test: `worktree ensure` → branch cut and checked out → work committed → `land --dry-run` → `--apply` → `L_DONE`. pass-1 Missing flagged that nothing asserted the full path — the property #331 is actually about. EXP-001 measured **no test anywhere** exercises `_land_manifest`, `_land_execute`, or any L-step under `execute.worktree: false`, and the spec has **zero** hits for in-place landing. **The harness is named, and it depends on Epic 1** (pass-2 C2): drive it with `land_rehearsal.py`'s `_build_sandbox` (a throwaway repo with a **local bare origin**) plus the **injected runner** — which is why this issue depends on 1.1 and 1.5. EXP-002 measured that unpatched, the runner sees `['git']` only and the run halts at `l14_pour_fidelity` at 18 rows, so without the seam this test cannot reach `L_DONE` at all. The injected runner is also what keeps L6/L7/L12/L16/L17/L19's outward writes — push, `gh` comments, the `bd` close cascade, redeploy — inside the sandbox. **Pass an explicit tty allow-list rather than relying on `#334`'s bypass** (pass-2 C9), so plan-069's fix cannot break this test. **State the runner's contract (pass-3 C5), because `_dispatch` routes EVERY program through an injected runner — `git` included, so a runner that stubs everything makes `L_DONE` a fiction:** pass `git` **through** to the sandbox (it is the local bare `origin` that makes the push safe, not the runner), and intercept `bd`/`gh`/`uv`/`yf` with **argv-recognising** fakes that **fail on an unrecognised argv rather than returning 0** — the hazard `LandingContext`'s own docstring records (*"the injected fake returned 0 for any argv it did not recognise. Every Tier-1 test passed."*). Reach L19 with a non-`skills/` change set, or with a fake that asserts it was never asked to redeploy. **Decide what `_validate_merged` does in the sandbox** — with 1.5's stub removed it would run the repo's real FULL tier against a throwaway repo.
  - depends-on: 1.1, 1.5, 2.1, 2.2, 2.3, 2.4
- Issue 2.6: Verify the SPEC text 0.4 landed matches the implemented behavior of L1/L2 in-place, and correct either side on divergence. **Ordering restored** (pass-1 C5): v1 had this documenting `spec/landing.md` and depending on 2.3, which inverted SPEC-first outright. The SPEC now lands in 0.4; this issue only checks agreement.
  - depends-on: 0.4, 2.3

### Epic 3: Upstream corrections
- Issue 3.1: Publish the **five measured corrections**, each with its evidence: (a) `yf-f7lq`/#331/`plan-063/assets/residual-issues/r4-331-residue.md` claim three plans hand-cut a branch — plan-061 ran in **worktree mode**, so the residue is **two**; (b) `yf-i127` says L14's `bd list` is the only cwd-less call — there are **four**: L14's `bd list`, L17's `bd show` (the sole verification signal under REQ-LAND-019), and the cwd-less `git rev-parse --show-toplevel` launches in `_repo_root` and `_git_root`, reachable from L3/L8–L15/L16/L18/L19 (pass-4); (c) #353 attributes the mutation to "L4's merge commit and L6's push" — **L4 alone**; (d) #353 implies `predicted_tree` is invalidated by the landing's own merge — measured **stable**; (e) `yf-acrn` says "zero test coverage" — measured **61.4%**, all happy-path plus one refusal, and its six-step preamble list omits `_land_repreview_or_halt`. All five are true **today**, independent of any fix, so publishing early is sound.
  - depends-on: 0.1
- Issue 3.2: **Do not close #349 or #353.** Record on each that this plan resolves the correction only, and name plan-069 as the closing plan. pass-1: #349 is claimed across both plans and would otherwise be closed by whichever lands second on partial evidence. **Bead `yf-jp7z`'s re-scoping is explicitly HELD for plan-069** — re-scoping it to match an implementation whose design pass-1 C2/C3 showed is not yet settled would encode a design that does not exist.
  - depends-on: 3.1
- Issue 3.3: **Verify plan-069 carries every item this split relocated**, before Issue 3.2 publishes the cross-reference that points at it. pass-2 C6 measured three items dropped by BOTH plans: the `recover()` fall-through fail-closed fix (EXP-004 implication 6 — *"the single line standing between an unhandled action and a re-push"*, named twice by pass-1 and carried by neither), the **"no write occurred" helper** (implication 5 — the reason the preamble's safety property is checked only by a source-text test), and `_land_assert_primary_checkout`'s missing behavioral test. Also confirm plan-069 records **the `REQ-LAND-036` exclusion-table amendment and the `REQ-LAND-018` rationale amendment** — pass-3 C6 found these were EXP-003's implication 2, carried by neither plan, while plan-069's text *falsely asserted plan-068 had already done them*; that false attribution is now corrected and both are this plan's to verify, not to perform. Also confirm it records **L2's in-place behaviour and the declared scope boundary Issue 0.4 routes there** — pass-4 C7 found this was a *fifth* item created by pass-3's own fix and carried by neither plan, the identical escape class. Also confirm it records EXP-003's post-L4 digest absence finding, EXP-001's L4 misleading-diagnostic defect, and the **cross-plan coupling** (pass-2 C9): Issue 2.5's end-to-end test must pass an explicit tty allow-list, so plan-069's `#334` fix cannot break it. **A concern resolved by relocation must land in the destination's text, not only in this plan's Resolutions cell.**
  - depends-on: 3.1

### Epic 4: This plan's own landing
- Issue 4.1: Write the **landing-hazard playbook** into the bundle, enumerating the known halts waiting on this plan's own landing path and the recovery action for each. This plan lands through the **un-repaired** `land` (the installed copy), which still carries: #353's guaranteed post-`L_VALIDATED` digest mismatch on any resume; #352's `requires_mention` failure surfacing only after the writes are public; #350's laundered unpushed count; and the unwrapped executor bookkeeping that turns a malformed step row into a bare traceback with no envelope. Not speculative — the two most recent commits on `main` are `HALT: plan-066's close chain fails verify-reconcile on 5 of 7 rows` and `HALT 2: plan-066 completes at LAND`. Record the redeploy rule: **L19 last, from clean `main` in sync with `origin`, never from the execute branch**.
  - depends-on: 0.1
- Issue 4.2: Fill `context.md`'s **Runtime assumptions** — in-place execution and its single address space, `gh` credentials for Gate 4, and the `uv --with` network dependency. pass-1 C14: it is boilerplate today and the bundle's stated contract is that a cold reader understands it from the folder alone.
  - depends-on: 0.1

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: the allocated REQ ids are free
- Type: auto
- Condition: Every REQ id Issue 0.2 records is unused across SPEC.md and the yf-plan spec tree
- Test: for f in skills/yf-plan/spec/landing.md skills/yf-plan/spec/phases.md SPEC.md; do test -r "$f" || { echo "MISSING: $f" >&2; exit 1; }; done; ! grep -qE 'REQ-LAND-(037|038)' -- skills/yf-plan/spec/landing.md skills/yf-plan/spec/phases.md SPEC.md
- Blocks: 0.3, 0.5
- Instructions: ONE-SHOT — evaluate before Issue 0.3 lands the requirement; it exits 1 by design afterwards, so do not re-run it on a resume sweep. Rewritten after pass-1 C6 measured the v1 test passing vacuously by TWO routes: with SPEC.md absent the `test ! -r SPEC.md ||` guard was inverted from "skip if no SPEC" into "PASS if no SPEC" (exit 0 on a taken id), and on macOS a missing spec dir made grep return 2, which `!` flipped to exit 0 on a taken id. This form fails loudly on a missing path instead of short-circuiting, and keys on `spec/landing.md`, which actually holds the ids (63 REQ-LAND refs vs SPEC.md's 18 amendment-log mentions). **Rewritten again at pass-2** (C4, C14): the previous form greped `REQ-LAND-037` alone while its Condition said "every id 0.2 records", and Issue 0.5's requirement had **no id anywhere in the plan** — the same defect one issue over. It now covers `037|038`, blocks 0.5 as well as 0.3, adds `spec/phases.md` (where the REQ-BRANCH ids live, so 0.6's amendments are in range), and **echoes the missing path to stderr** instead of failing indistinguishably from "id taken". If 0.2 allocates further ids, extend the alternation.
- test_class: probe
- cwd: repo-root

### Capability Gate: baseline suite is green before the refactor
- Type: auto
- Condition: The land test suite passes on the execute branch before any seam routing
- Test: uv run skills/yf-plan/scripts/test_land_apply.py
- Blocks: 1.1
- Instructions: ONE-SHOT, and RUN THIS EXPLICITLY — it is `build` class, and the execute-start sweep runs the `probe` class ONLY unless invoked with `--sweep-gates=all` (pass-1 C7: otherwise it sits unevaluated while blocking 1.1). Either execute with `--sweep-gates=all` or run this command as Issue 1.1's first step. Measured baseline: 66 passed, exit 0, ~28s. A red baseline means something landed between investigation and execution — investigate before refactoring, or the seam change inherits an unrelated failure. **Marked ONE-SHOT at pass-2** (C11): its Condition is "green **before any seam routing**", and §5.2b re-sweeps gates on resume, so re-running it after 1.1 lands would test the modified suite and green on a condition that is by then false.
- test_class: build
- cwd: repo-root

### Capability Gate: publish the upstream corrections
- Type: human
- Condition: Operator authorizes editing the upstream GitHub issues and beads named in Issue 3.1
- Test:
- Blocks: 3.1, 3.2
- Instructions: Outward-facing writes to #331, #348, #349, #353 and the plan-063 residue asset. Stop-class 1 by design; a green test can never substitute for authorization. Review the five corrections in Issue 3.1 and authorize, or narrow the set — SC10 is worded to accept a narrowed set (pass-1 C9).
- test_class: consent
- cwd: repo-root

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **Plan size.** v1 was 37 issues with a dependency chain **8 nodes deep** — the v1 risk row claimed 33 and depth 3, and both were wrong. | med | Resolved structurally, not by re-wording: pass-1 C1's split makes this Plan A at **23 issues** (pass-2 C7 caught this row still saying 20 while the Approach said 22 — the same not-knowing-its-own-size defect, inside the row that resolved it. Every count in this plan is now taken from `plan_extract.py` output rather than written by hand), with plan-069 carrying the rest. The false "every epic is independently landable" claim is withdrawn — the DAG is a single tree rooted at 0.1, and that is now stated rather than denied. |
| R2 | **This plan must LAND THROUGH the un-repaired path it is repairing.** The installed `land` still carries #353's guaranteed post-`L_VALIDATED` digest mismatch, #352, #350 and the unwrapped executor bookkeeping. The two most recent commits on `main` are both plan-066 landing halts. | high | Issue 4.1 writes a landing-hazard playbook enumerating each known halt with its recovery action. **This is also what the A/B split buys:** Plan A lands the in-place fix, so plan-069's landing is the first in this repo that does not pay #331's tax. |
| R3 | **Self-modification during execution.** The plan edits `plan_manager.py`'s `land` path while executing under it. | med | AGENTS.md's three-artifacts rule: `SKILL.md` prose loads once at invocation and scripts resolve to the **installed** copy, so repo edits do not take effect mid-run. The binding constraint is **no `yf skills install` / `yf self install` mid-execution** — `plan_manager.py` is re-invoked per call, so a mid-execution deploy would run new scripts against old prose. Redeploy is the last step of landing, from clean `main`. |
| R4 | **This plan must hand-cut its own execute branch (Issue 0.1) using the workaround it exists to remove.** | med | Precedent measured (plans 062, 063). Placed FIRST, before every SPEC edit, because in-place mode has one address space and an earlier commit would escape the merge L3 validates. |
| R5 | **The seam refactor can go quietly vacuous.** `test_pour_fidelity_inconclusive_is_not_a_divergence` binds `f.returncode` by name in an AST walk. | med | Named in Issue 1.1 as an explicit do-not-rename list. Issue 1.3's AST check is the durable backstop, and SC1 asserts it. |
| R6 | **Design (b) contradicts REQ-BRANCH-004** by leaving the primary checkout on a plan branch during in-place execution. | med | Issue 0.6 lands an explicit carve-out in SPEC **ahead of** the code, rather than letting it become a silent exception. |
| R7 | **The rehearsal's green does not mean L14 is exercised.** An injected runner returning `[]` for `bd list` and `0` for `pour_fidelity` proves nothing about the DAG comparison — a stub in a different costume. | low | Stated honestly in Issue 1.6 rather than claimed as covered. Issue 1.5's derived `stubbed_steps` makes the residual gap **visible**; SC3 is worded to claim only what is actually established. |
| R8 | **Five of nine beads were measurably wrong, all under-scoping.** Remaining bead text may be trusted uncritically during execution. | med | Epic 3 corrects them upstream. Every issue cites its measured evidence rather than the bead's claim, so execution reads the finding, not the bead. |
| R9 | **#349 and #353 are claimed by both plans** and could be closed on partial evidence by whichever lands second. | med | Issue 3.2 records the split on each issue and names plan-069 as the closing plan; both are dispositioned `partial` here, and no success criterion asserts their closure. |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC0 | This plan's execute branch exists and is checked out in the primary checkout | `git rev-parse --verify --quiet plan-068-james-dixson-8ae0e1-execute` exits 0 and `git rev-parse --abbrev-ref HEAD` reports it | 0.1 |
| SC1 | No `subprocess.*` or `os.system` call appears inside any `_land_l<N>_*` function | Issue 1.3's AST check exits 0 | 1.3 |
| SC2 | Every landing subprocess that has a `ctx` in scope runs through the seam, and the two that do not take an explicit root | Issue 1.3's AST check exits 0 **and** `_land_epic_from_bd` / `_land_route_record_findings` each pass an explicit root argument | 1.1, 1.4 |
| SC3 | The rehearsal reaches terminal `L_DONE` and its record names **every** remaining stub, whatever its symbol | The rehearsal runs under pytest, reports `reached_terminal_state: true`, and its `stubbed_steps` enumerates **any step disabled by EITHER a `pm.*` monkeypatch OR a non-`enable` decision adjudication** — pass-3 C4 found the `_land_l*` wording blind to the two helper stubs, and pass-4 C8 found the monkeypatch wording blind to `land_rehearsal.py`'s decision-level `"l19_redeploy": "skip:sandbox has no yf binary"`, which disables a **sixth** step that Issue 2.5 explicitly requires reaching | 1.5, 1.6 |
| SC4 | An in-place repo reaches a landed state end to end without a hand-cut branch | The Issue 2.5 end-to-end test drives `worktree ensure` → commit → `land --dry-run` → `--apply` and reaches `L_DONE` | 2.1, 2.2, 2.5 |
| SC5 | L1 operates on the execute branch rather than ambient HEAD | A test that **moves HEAD off the execute branch before L1** and asserts L1 still merges the execute branch rather than reporting `pass` on a self-merge — written so it FAILS under 2.1 alone (pass-2 C12) | 2.3 |
| SC6 | `_land_merge_preview.changed_paths` is empty for a branch that is behind its target, and `_land_changed_set` reports the merged range correctly in-place | The Issue 2.4 directionality tests pass | 2.4 |
| SC7 | The in-place path refuses on a dirty divergent tree with a declared refusal class rather than an unhandled `git` error | The Issue 2.2 precondition test passes | 2.2 |
| SC8 | The landing test suite passes on the merged tree | FULL-tier validation green at land (`validate-merged`), not at any individual issue | 1.1, 1.3 |
| SC8b | L17's read-back is visible to the seam | `test_each_step_invokes_the_RIGHT_EXECUTABLE` asserts `{"uv", "bd"}` for `_land_l17_residual_mirroring` and passes | 1.2 |
| SC9 | No commit touching `plan_manager.py` precedes the first SPEC commit, in **every** parent orientation the landing produces | `B=$(cat <plan_dir>/assets/execute-base.txt); fs=$(git log --format=%H --reverse "$B..HEAD" -- skills/yf-plan/spec/ SPEC.md \| head -1); fc=$(git log --format=%H --reverse "$B..HEAD" -- skills/yf-plan/scripts/plan_manager.py \| head -1); if [ -z "$fs" ] && [ -z "$fc" ]; then exit 2; fi; [ -z "$fc" ] \|\| { [ -n "$fs" ] && { [ "$fc" = "$fs" ] \|\| git merge-base --is-ancestor "$fs" "$fc"; }; }` — **pinned to the recorded execute base, NOT to a parent-parity heuristic.** pass-4 C5 reproduced a **FALSE GREEN** in the v3 form: at L1's down-merge the parents invert (HEAD^1 = execute tip, HEAD^2 = target tip), so `HEAD^1..HEAD^2` reads the *target's* commits and excludes the plan's work — a violating branch with an unrelated `spec/` commit on `main` exited **0**. Verified across **nine** cases: violating on-branch 1; violating after L1 down-merge 1; violating after down-merge with an unrelated main `spec/` commit 1; violating after merge to main 1; compliant on-branch, after down-merge, and after merge to main all 0; empty range 2. **Re-verified by pass-5 across 11 further adversarial cases** — detached HEAD, non-ancestor base, rebase, octopus merge, and a missing / empty / whitespace-padded / garbage / `gc`-pruned base file all yield **2 or a correct 1, never a false green**. **Declared limit:** a **squash-merged** history exits 0 for violating and compliant sources alike, because the squash makes the SPEC and code edits one commit and destroys the ordering evidence — no expression over that history can recover it. `land`'s L2 performs a real `--no-ff` merge, never a squash, so this is outside the landing path | 0.3, 0.4, 0.5, 0.6 |
| SC9b | Issue 0.2's recorded allocation and the landed SPEC diff agree **in both directions** | Every id in the landed SPEC diff appears in 0.2's record **and** every id in 0.2's record appears in the landed diff — bidirectional, because the one-directional form could never catch the over-claim pass-4 C6 found | 0.2 |
| SC9c | The landed SPEC text for in-place L1/L2 semantics matches the implemented behavior | The Issue 2.6 agreement check reports no divergence | 2.6 |
| SC10 | Each **authorized** upstream correction is published, and neither #349 nor #353 is closed by this plan | Each correction the operator authorized at Gate 4 is visible on its issue or bead; `gh issue view 349 --json state` and `353` both report `OPEN` | 3.1, 3.2 |
| SC11 | The bundle records the landing hazards and its runtime assumptions | A landing-hazard section naming the four known halts with recovery actions exists, and `context.md`'s Runtime assumptions is non-boilerplate | 4.1, 4.2 |
| SC12 | Neither plan silently drops measured evidence, and neither misstates what the other did | plan-069's plan.md carries all **eight** relocated items — the `recover()` fall-through, the no-write helper, `_land_assert_primary_checkout`'s behavioral test, the **`REQ-LAND-036`** and **`REQ-LAND-018`** amendments, EXP-003's post-L4 digest absence finding, the L4 misleading-diagnostic defect, and **L2's in-place boundary** — plus the #334-vs-SC4 coupling; and it contains no claim about plan-068's SPEC scope that plan-068's Epic 0 does not support | 3.3 |
