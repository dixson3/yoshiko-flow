---
type: Plan
okf_spec: OKF-PLAN
id: plan-063-james-dixson-3f74c1
author: James Dixson
created: '2026-09-03'
status: approved
deliverable_class: standard
fingerprint: 4d1c302dccc464b802c5ec9e17b997799a35dbff22608b7311b45e8dd81145da
---
# Plan: Make landings stick — fix the L18 crash, the L16 commit, and the dry-run blind spot

**ID:** plan-063-james-dixson-3f74c1
**Author:** James Dixson
**Created:** 2026-09-03
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** 4d1c302dccc464b802c5ec9e17b997799a35dbff22608b7311b45e8dd81145da

## Objective

Make a landing either **complete correctly** or **fail legibly**. Fix the L18 crash (#340), the
two further L18 defects a one-line patch would ship, L16's whole-index commit (#342) and its
broken journal filter (#343), and give `land --dry-run` the facts that predict L16 (#341, #333).
Wrap **step dispatch** so an exception raised by a `LAND_EXECUTOR` step becomes a halting step instead of a traceback. **Scope stated honestly** (pass-3 C34): the executor's own bookkeeping — the journal write and the row-shape access after a step returns — stays OUTSIDE the wrap, and that residue is filed by Issue 6.1 rather than silently implied to be covered. Then close the
gap that hid all of it: a **mock-fidelity check**.

## Motivation

plan-062 wired `land --apply` to its executor. The **first real landing in the repository's
history** completed every substantive step — two pushes, three public comments, #327 closed,
31/31 beads, `status: complete` — and then **crashed at L18** with a bare `TypeError`, leaving
the journal at `L_MIRRORED` and the execute branch undeleted. A resume re-enters L18 and crashes
identically.

Investigating that produced two defects nobody had filed, and one is worse than the crash:
**L16 commits the whole index and reports `pass`** (#342). A pre-staged unrelated file is
committed under the plan's message and pushed to `origin` — and the post-condition cannot see it
**because the step itself removed the evidence**.

The common thread, stated no more strongly than the evidence supports: A whole-module arity sweep found **1 defect in 252
functions**. It is that **every instrument was calibrated against the call site instead of the
callee**: 4 of 78 monkeypatched stubs fake `_worktree_teardown` with one parameter instead of
two — including `land_rehearsal.py:140`, which is mechanically why plan-060's rehearsal recorded
`l18_prune: pass` on a code path that could not run.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #340 | L18 crashes with a TypeError on every landing | include | The trigger. Closed when the call is fixed, the two adjacent L18 defects are fixed, and the dispatch wrapper makes any future step crash legible. | 1.1, 2.1, 2.2, 2.3 |
| #342 | L16 commits the WHOLE INDEX and reports pass | include | **The most severe defect found**, and found by this plan's own investigation. Not fixed by any dry-run halt — it is a defect in L16's commit, not its check. | 3.1 |
| #343 | L16's journal filter is a substring match | include | Masked in this repo by the `/.yf/` gitignore anchor; inoperative in any repo without it, and it does not even exempt the journal it was written for. | 3.2 |
| #341 | `worktree_dirty` can never report dirty | include | **The issue TITLE states the direction backwards** — measured, `bool((False, []))` is `True`, so the shipped field is constantly `True` and can never report *clean*. The closing comment must correct it. Deeper than the type bug: it observes `.worktrees/<plan-id>` while L16 checks `ctx.root`. A rename-and-redesign, not a one-character fix. | 4.1 |
| #333 | A decision file inside the tree halts L16 | include | The same L16 post-condition by another route. Needs enforcement *and* a better default path — a suggestion alone is not a control. | 4.2, 4.3 |
| #331 | `land` incompatible with `execute.worktree: false` | partial | **This plan depends on the gap and works around it again.** Issue 0.7 hand-cuts the execute branch, exactly as plan-062 did. Not closed. | — |
| #332 | `assets/upstream-drafts/` is undocumented | exclude | Documentation, not landing reliability. Nothing about it makes a landing fail. | — |

## Investigation Findings

Three experiments, all with sandbox spikes driving **real** functions against **real** git repos.
Full text in `findings/`.

**EXP-001 — the dead-code-cluster hypothesis is refuted.** 252 module-level functions, 46
reachable from the 15 steps, one `globals()[...]` dispatch site with a fully-covered target
table — and **exactly one arity defect**, #340. But the same sweep found the systemic gap: **4 of
78 monkeypatched stubs are signature-incompatible**, all four the same one-arg
`_worktree_teardown` fake. It also found **two further L18 defects that are not arity
mismatches**: the execute branch is deleted twice (so once #340 is fixed, L18 will *permanently*
report its own headline action as `ok: false`), and L18 never reads `wt["status"]` (so a
`blocked` teardown — nothing pruned — reports `pass`). `force=False` is confirmed correct against
the CLI path; the SPEC is **silent** on it.

**EXP-002 — the rehearsal did not skip L18; the stub encoded the caller's wrong arity.**
plan-060's record shows `l18_prune: pass` / `L_DONE` on an unrunnable path. The proposed wrapper
was implemented and driven: `inconclusive` + `halting=True` + `journal=None`, exit 2, with
`KeyboardInterrupt`/`SystemExit` re-raised — reproducing `L_MIRRORED`, **exactly the phase
plan-062 observed in production**. A zero-stub spike reached **18 of 19 steps**; only L14 needs a
poured fixture. L8–L15 use bare `subprocess.run`, so they are not injectable, and the rehearsal
has **zero coverage of the `--apply` CLI preamble**.

**EXP-003 — L16's post-condition is the only genuinely post-boundary-only condition**, and #341
and #333 are two instances of it. The proposed dry-run facts agree with the real L16 on all three
scenarios: silent when it passes, halting exactly where it fails. The investigation also found
#342 and #343, and that **`resolvable_by_agent` is written in five places and read in none**.

## Approach

**SPEC-first, then make crashes legible, then fix what crashes, then fix what silently
succeeds, then close the gap that hid it all.**

The ordering constraint that matters is the reverse of the obvious one. **Fix L18 BEFORE
correcting the stubs**: the stubs currently mask the crash, so correcting them first would break
the suite against a still-broken L18. And the check is **authored BEFORE the stubs are corrected**
(pass-1 C3 swapped these) so its gate can observe it finding the one that remains uncorrected — it therefore **does fail on
arrival in that window, by design**, which is why wiring it into `CHANGE-VALIDATION.md` waits
until after the stubs are fixed (pass-2 C23).

**A halt strictly dominates a field.** The objection that a dry-run halt would block a landing
over an unrelated file is not an objection — **L16 blocks that landing regardless**. The choice
is only *where*: a dry-run halt costs one `git stash`; the L16 failure costs a landing wedged at
`L_CLOSED` with comments posted, issues closed and `status: complete` written, whose recovery
contract is explicitly *"retry-after-rebase, NEVER REVERT"*.

**This plan MUST execute in-place, and the config MUST be written before `/yf-plan execute`** —
`printf '{"execute.worktree": false}\n' > .yf/plan/config.local.json`. The reason recurs from
plan-062 and is sharper here: this plan edits the very `plan_manager.py` the landing runs from,
so under worktree mode the primary checkout would stay on `main` carrying the **unfixed L18** and
crash at the prune. In-place mode alone leaves no execute branch (#331), so Issue 0.7 cuts it by
hand.

**The rehearsal extension is deliberately NOT in scope.** EXP-002 showed it is necessary but not
sufficient — removing one stub would have caught this bug while leaving the class untouched. The
mock-fidelity check addresses the class, and is the only one of four candidate passes that would
have caught #340 before the first real `--apply`.

## Epics

### Epic 0: SPEC-first, and make the landing route reachable
- Issue 0.0: **Immediately after the §5.2a pour, SET THEN ASSERT** the gate metadata — `bd update <gate-id> --metadata '{"gate_type":"auto","test":"...","test_class":"probe","cwd":"repo-root"}'` for **ALL** capability gates (`grep -c '^### Capability Gate:' plan.md` is the count; it is load-bearing and was wrong once in plan-062), then read back and halt only if a write did not take. `plan_extract.py` drops those lines silently and `unparsed` stays `[]`, so nothing else catches a miss.
- Issue 0.7: **Create and check out `plan-063-james-dixson-3f74c1-execute` in the PRIMARY checkout** from the pinned base, immediately after §5.2a's in-place fallback. Under `execute.worktree: false` no execute branch is ever created (#331), so `land --dry-run` would halt `execute-branch-missing`. Placed SECOND, before every SPEC edit: in-place mode has one address space, so a commit made before the branch exists lands on `main` and escapes the merge L3 validates.
  - depends-on: 0.0
- Issue 0.1: Add `REQ-LAND-030` — **step dispatch is fail-closed.** An exception raised by a `LAND_EXECUTOR` step shall be caught and reported as a halting `inconclusive` step with no journal advance, never as a traceback.
  - depends-on: 0.7
- Issue 0.2: Add `REQ-LAND-031` — **L18's teardown is non-forcing and its status is surfaced.** The SPEC is currently silent on both, which is how the call site drifted unnoticed.
  - depends-on: 0.1
- Issue 0.3: Add `REQ-LAND-032` — **L16's commit shall be path-scoped to what it staged**, so the step cannot commit work it did not stage.
  - depends-on: 0.2
- Issue 0.4: Add `REQ-LAND-033` — **L16's post-condition shall enumerate untracked entries** (`-uall`) and exempt `.yf/plan/` by path prefix rather than by substring.
  - depends-on: 0.3
- Issue 0.5: Add `REQ-LAND-034` — **`--dry-run` shall report a primary checkout dirty outside the plan folder as a HALTING finding**, and `REQ-LAND-035` — a decision document and every `body_path` shall live outside the work tree.
  - depends-on: 0.4
- Issue 0.5b: Add `REQ-LAND-036` — **the digest's coverage set excludes LANDING-MUTATED facts**, naming `execute_worktree_present` and `execute_worktree_dirty` and the rationale (L18's teardown flips them mid-landing, so a post-teardown resume would mismatch on a fact the landing itself changed). **Amend `REQ-LAND-002` and `REQ-LAND-011`'s "every fact" wording** to match. Required because Issue 4.1's exclusion is a NORMATIVE DEVIATION from both, and AGENTS.md is explicit that the SPEC change lands first (pass-4 C37).
  - depends-on: 0.5
- Issue 0.6: Amend `REQ-LAND-020`'s post-condition wording to match `REQ-LAND-032`/`-033`, and add the living-amendment-log entry in the repo-root `SPEC.md` naming plan-063 and **all TEN** ids — `REQ-LAND-030`…`-036`, **`REQ-LAND-020`**, and the amended `REQ-LAND-002` / `REQ-LAND-011` (pass-4 C37), which this issue amends and which `check_amendment_log`'s A1 derives from this very issue body (pass-1 C8: a six-bullet log fails A1). **The log is in `SPEC.md`, not `spec/landing.md`.**
  - depends-on: 0.5b

### Epic 1: Make a crash legible — the dispatch wrapper
- Issue 1.1: Wrap the dispatch at `plan_manager.py:9747`: `except (KeyboardInterrupt, SystemExit): raise` then `except Exception`. Return `inconclusive`, `halting=True`, `journal=None`, **and return the halted envelope directly from the `except` block**. **The process exit code is 1, NOT 2** (pass-2 C19): `:8382` sets `verdict = "fail"` when `halted` is set, and halted wins over the inconclusive list. EXP-002's measured exit 2 came from calling `_land_execute` directly, where the row *fell through* — an artifact of the very defect this issue removes. **SC1 must assert the exit code explicitly**, since that is the one number the investigation measured wrong. `_land_execute`'s loop predicate is `if r["verdict"] == "fail" and r.get("halting")`, so an `inconclusive` row falls THROUGH and the loop runs the next step (pass-1 C7). For L18 that is invisible because L19 is next; for an early step the landing would walk past a crash into destructive work. Catch bare `Exception` — the whole point is the *unexpected* one, and a `TypeError` from an arity mismatch is on nobody's list. Write the re-raise clause explicitly even though those two do not inherit from `Exception`, so the invariant is readable rather than inferred from the hierarchy.
  - depends-on: 0.6
  - resolves-upstream: #340 (include)
- Issue 1.2: Record in the reason string that **a resume will re-enter the same step and raise again.** This is correct and must not be engineered around: advancing the journal past a step that raised would manufacture the evidence `_land_resume_done` exists to refuse, and `LandingJournal.write` rejects any phase outside the closed 17-state set.
  - depends-on: 1.1

### Epic 2: Fix what crashes — L18
- Issue 2.1: Fix the call at `:9512` to `_worktree_teardown(ctx.plan_dir, force=False)` — **keyword form**, so the next signature change fails loudly rather than silently rebinding a positional. `force=False` is confirmed against the CLI path and is the only value consistent with INV-1. **Correct ALL THREE `test_land_apply.py` stubs — `:1023`, `:1180` and `:1254` — IN THIS SAME CHANGE-SET** (pass-2 C18, corrected by pass-5 C42: `:1023` backs `test_prune_is_strategy_aware`, the first test named below, and omitting it would raise the very `TypeError` this instruction exists to prevent): measured, the arity fix alone makes `test_prune_is_strategy_aware` and `test_each_step_invokes_the_RIGHT_EXECUTABLE` fail with `TypeError`, and the FAST row runs the whole file on every `skills/yf-plan/scripts/**` edit — so without this the on-edit gate is red for six issues. The plan reasons about the stubs-first direction; this is the symmetric one.
  - depends-on: 1.2
  - resolves-upstream: #340 (include)
- Issue 2.2: Delete the duplicate `ctx.run("git", ["branch","-d", …])` at `:9515` — `_worktree_teardown` already deletes the branch at `:4392`. Measured: once #340 is fixed, L18 **permanently** reports `{"action": "delete-execute-branch", "ok": false, "detail": "branch not found"}`. `test_prune_is_strategy_aware:1030-1033` asserts on that duplicate call, so **the fix and the test move together** — and the assertion must be REPLACED, not deleted (pass-1 C10): capture the stub's call args and assert `(ctx.plan_dir, force=False)`, and assert no `branch -d` reaches `ctx.run`. Otherwise L18's headline action becomes untested at the step level, since the real delete happens inside `_worktree_teardown` via `_run_git` and is invisible to `ctx.run`.
  - depends-on: 2.1
- Issue 2.3: Make L18 **branch on `wt["status"]`**, and state the behaviour when the key is **absent** — the stubs do not carry it until Issue 5.1 corrects their return shape (pass-2 C20). Measured: a `blocked` teardown — dirty worktree, nothing pruned, branch left behind — currently reports `verdict: pass`. A landing must not report a prune it did not perform.
  - depends-on: 2.2

### Epic 3: Fix what silently succeeds — L16
- Issue 3.1: **Path-scope L16's commit AND its guard.** The commit becomes `git commit -m <msg> -o -- <plan_dir>` — **argument order is load-bearing**: after `--` every token is a pathspec, so the `-o -- <dir> -m <msg>` form measured as `error: pathspec '-m' did not match any file(s)`, exit 1, which would fail EVERY landing at a post-outward-write step (pass-1 C4). The guard at `:9358` must be scoped too — `git diff --cached --quiet -- <plan_dir>` — because an unrelated staged file otherwise makes the whole-index guard say "staged" while the scoped commit exits 1 `no changes added to commit`, (pass-1 C5). **Scoping the guard removes a MISLEADING COMMIT ERROR; it does NOT remove the halt** (pass-2 C21, measured): the post-condition still sees the unrelated file and returns a halting fail. That halt is **intended**, and is exactly what Issue 4.2 predicts at dry-run time. Measured: a pre-staged unrelated file is currently committed under the plan's message and pushed to `origin`, with L16 reporting `pass` because the commit removed the evidence.
  - depends-on: 0.6
  - resolves-upstream: #342 (include)
- Issue 3.2: Replace the substring journal filter with a **path-prefix test over a `.yf/plan/` allowlist**, and switch the post-condition to `git status --porcelain -uall`. **Without `-uall` no prefix filter can work** — git collapses untracked directories to `?? .yf/`, which contains neither the journal path nor `land-beads.json`. Name the helper **`_dirty_outside_plan_dir`** so the single-definition criterion pins a real identifier (pass-2 C26). Use `--porcelain=v1 -uall -z`, split on NUL and prefix-test the **path field** (pass-1 C12): raw lines carry a two-char status plus a space and quote paths containing spaces, so a naive `startswith` matches nothing and a naive `in` reinstates the substring bug. Add a case with a spaced path.
  - depends-on: 3.1
  - resolves-upstream: #343 (include)
- Issue 3.3: Add Tier-1 cases against a **REAL sandbox git repo with a bare `origin`** — NOT `FakeRunner` (pass-1 C6): the only existing L16 test drives a fake with `{"diff\|--cached": _R(1)}`, so no real git runs and an argv git rejects would still pass. Three cases: (a) a pre-staged unrelated file is **NOT** in the commit — pinning the **expected envelope** (`verdict: fail`, `halting: true`, the file absent from `HEAD`), not merely its absence (pass-2 C21). Writing it to expect `pass` would invite scoping the post-condition, re-opening #342 on the very axis this gate guards; (b) **POSITIVE** — the plan-folder writes, including a newly created untracked file, **ARE** in the commit, and a normal landing still passes; (c) L16 in a sandbox **without** the `/.yf/` anchor, the only configuration where the filter is load-bearing.
  - depends-on: 3.2

### Epic 4: Predict L16 before the boundary — the dry-run facts
- Issue 4.1: Replace `"worktree_dirty"` (`:8043`) with four fields: `execute_worktree_present`, `execute_worktree_dirty` (**three-valued** — `null` when there is no worktree, because `false` would assert "clean" about a tree that does not exist), `primary_checkout_dirty_outside_plan_dir` and `primary_checkout_staged_outside_plan_dir`. **The rename is mandatory, not cosmetic:** `worktree_dirty` names the tree L16 does not check. Keep the facts **boolean** and put path lists in `halts`, so `_land_digest` stays stable when clean and dirt appearing between dry-run and apply becomes a digest MISMATCH for free. The two `primary_checkout_*` fields are computed **via `_dirty_outside_plan_dir`**, the helper Issue 3.2 builds — not by an inline predicate (pass-3 C31), or 4.1 becomes the second definition site SC4c forbids. **`execute_worktree_present` is LANDING-MUTATED** (pass-2 C27): L18's teardown flips it true→false and the digest is re-derived on resume, so a halt after a partial L18 mismatches. **Exclude the execute-worktree fields from the digest, recording the reason** — and the test must assert **BOTH directions** (pass-4 C40): flipping `execute_worktree_present` leaves the digest equal, AND flipping `primary_checkout_dirty_outside_plan_dir` changes it, so the criterion cannot be satisfied by a digest covering nothing — the decision is taken here rather than deferred to the executor (pass-3 C33), because SC5b asserts the digest *survives* a post-teardown resume and only this branch can satisfy it.
  - depends-on: 0.6, 3.2
  - resolves-upstream: #341 (include)
- Issue 4.2: Add the **halting** dry-run finding on `primary_checkout_dirty_outside_plan_dir`, scoped to **outside the plan folder** — dirt inside it is what `git add -- <plan_dir>` is for. **It must call the SAME helper Issue 3.2 builds** (pass-1 C9): 3.2 defines the enforcement predicate and 4.2 the prediction of it, and two independent implementations of one rule is exactly how the dry-run stops predicting L16 — this plan's objective.
  - depends-on: 4.1, 3.2
  - resolves-upstream: #333 (include)
- Issue 4.3: Refuse a decision path **inside the work tree**, placed beside `_land_assert_primary_checkout` and **before the tty gate**, so a refusal is never preceded by a write. Extend the same containment check over every `body_path` in `_land_validate_decision` — `lander.md:88,96` emits those as bare `"<path>"` with no guidance on where they live, and L7 reads them. Also default `_land_apply_command`'s emitted path to `${TMPDIR:-/tmp}/<plan-id>-decision.json`; the current literal `<decision.json>` is a repo-relative-*looking* placeholder that invites the failure.
  - depends-on: 4.2
- Issue 4.4: Give `resolvable_by_agent` a **consumer**, or drop the field. It is written in five places and read in none, so the new halt's `true` would be as inert as the existing five `false`s.
  - depends-on: 4.3

### Epic 5: Close the gap that hid it — mock fidelity
- Issue 5.2: Add `scripts/checks/check_mock_fidelity.py` — bind every `monkeypatch.setattr(pm, …)` / `pm.x = …` stub against `inspect.signature` of the real function. ~60 lines, no network, sub-second. **It is the only one of four candidate passes that would have caught #340 before the first real `--apply`, and no type checker validates a stub against its target.** **Record what it does NOT cover** (pass-2 C20): it binds the argument axis only — return shapes, keyword-only-ness and assignments to non-callables are outside it, so "the class is closed" must not be over-claimed. It must **fail loudly when the target file is absent** rather than reporting zero incompatibilities — an empty result and a clean result must not share an exit code. Also assert no landing step returned `inconclusive` carrying an `exception` key (EXP-002 rec 6): once the wrapper exists, a future crash becomes a green-looking non-halting record unless something looks for it.
  - depends-on: 2.3, 3.3
- Issue 5.1: Fix the four incompatible stubs — `land_rehearsal.py:140` and `test_land_apply.py:1023`, `:1180`, `:1254` — to accept the real signature **AND to return the real shape** (pass-2 C20): `_worktree_teardown` returns `{"status", "path", "branch", "steps"}` and **never** an `"action"` key, while all four stubs return `{"action": "removed"}`. Issue 2.3 makes L18 branch on `wt["status"]`, so the return axis is load-bearing in this same plan — and `check_mock_fidelity` binds `inspect.signature` and is **structurally blind** to it. **Runs after Epic 2 AND after 5.2** (pass-1 C3): the stubs currently mask the crash, so correcting them against an unfixed L18 would break the suite; and the check must exist first so its capability gate can be measured against the still-broken stubs.
  - depends-on: 5.2
- Issue 5.3: Wire the check into `CHANGE-VALIDATION.md` (FAST on `skills/yf-plan/scripts/**`, and FULL), and register `gate-plan063-amendment` with its Trigger Scope entry so this plan's `SPEC.md` and `spec/**` edits are covered by a row of its own rather than firing plan-060's.
  - depends-on: 5.2, 5.1

### Epic 6: Reconcile and land
- Issue 6.1: File anything this plan found and did not fix. At minimum: the `unpushed = … or "0"` laundering at `:9396`; L14's `bd list` being the only close-chain subprocess launched without `cwd=ctx.root`; **the L8–L15 injectability gap** (they use bare `subprocess.run`, which is why the rehearsal must replace whole steps — EXP-002 rec 5b, deliberately unscoped here); and **the accumulating #331 residue** — this is the THIRD consecutive plan to hand-cut its execute branch; and `check_amendment_log`'s success line under-counting `n_impl`; **the `--apply` CLI preamble having zero test coverage** (EXP-002 measured it untested by anything — pass-3 Missing 1); **the executor's own bookkeeping being outside the wrapper** (pass-3 C34); and **the absence of a RETURN-shape fidelity check** — the new check binds signatures only, while the divergence load-bearing in this very plan is the return shape (pass-3 C35).
  - depends-on: 5.3, 4.4
- Issue 6.2: Author the upstream draft bodies for every row requiring a mention (#340, #342, #343, #341, #333 are `include`; #331 is `partial`). `_land_upstream_rows` computes a `draft_body_path` for every non-`exclude` row.
  - depends-on: 6.1
- Issue 6.3: Run the FULL tier on the merged tree and record the run.
  - depends-on: 6.2
- Issue 6.4: Confirm the **primary checkout carries the fixes** before any `--apply` — resolve the primary via `--git-common-dir`, not `--show-toplevel`, which resolves to a worktree root.
  - depends-on: 6.3
- Issue 6.5: **Record the Phase-6 landing route and its halt-recovery contract for the OPERATOR to execute.** A Phase-5 bead must close before the Reconcile Gate opens, so this produces the handoff artifact; it does not land. SKILL.md §6.0 says print the command and stop, and names #293.
  - depends-on: 6.4
- Issue 6.6: Bring `index.md` current with every bundle member and confirm `okf.py reindex --check` exits 0. Author real descriptions, not bare bullets. Placed last so it runs after every Phase-5 bundle write.
  - depends-on: 6.5

## Gates

> **Known grammar gap — the `test_class` / `cwd` lines below do NOT survive extraction.**
> `plan_extract.py` recognizes only `Type|Approvers|Condition|Test|Blocks|Instructions`, and
> `unparsed` stays `[]`, so `--strict` does not flag the loss. **Issue 0.0 is the control.**

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: execution is in-place, not in a worktree
- Type: auto
- test_class: probe
- cwd: repo-root
- Condition: `execute.worktree` resolves to `false`, so the primary checkout carries the fixes at land time
- Test: uv run skills/yf-plan/scripts/plan_manager.py config-resolve --json | jq -e '.keys["execute.worktree"].value == false' > /dev/null
- Blocks: 0.7, 1.1, 3.1, 4.1
- Instructions: REMEDIATION IS A RESTART, NOT A TOGGLE. Blocking the branch-creation issue as well as the code epics is load-bearing (pass-2 C25): that issue's correctness IS that the branch is cut in the PRIMARY checkout, so under worktree mode the SPEC commits and a hand-cut branch would land in the wrong address space before this gate fired — and the remediation is a restart that discards that work. It deliberately does NOT block the gate-metadata issue, which sets the fields this sweep reads. Worded without naming an id, because `gate_consistency` arm 1 reads a named blocked id as a reachability cycle. If this is red the session is already in worktree mode (`worktree ensure` runs before the sweep): set the config, REMOVE `.worktrees/<plan-id>`, and RESTART from §5.2. This plan edits the `plan_manager.py` the landing runs from, so under worktree mode the primary would stay on `main` with the UNFIXED L18 and crash at the prune.

### Capability Gate: the mock-fidelity check is DISCRIMINATING before the stubs are fixed
- Type: auto
- test_class: probe
- cwd: repo-root
- Condition: the new check FAILS against the still-uncorrected stub, finding the ONE that remains at this point, proving it measures the defect rather than passing vacuously
- Test: test "$(uv run scripts/checks/check_mock_fidelity.py --json | jq '[.incompatible[]] | length')" -ge 1
- Blocks: 5.1
- Instructions: ONCE-ONLY, and EXPECTED RED AT THE §5.2c SWEEP until the check is authored. **The authoring issue is now a PREDECESSOR of the blocked issue**, so the evidence exists before the gate is evaluated — pass-1 C3 found the original edge direction made this a genuine reachability cycle that earlier wording had merely stepped around, which is evading the detector rather than removing the cycle. **The count is ONE, and the threshold is deliberately a FLOOR rather than an exact count** (pass-3 C30, pass-5 C42, pass-6 C43 — it has been wrong three times, 4 then 2 then 1, every time because a stub correction moved upstream of this gate). Four one-arg stubs exist today; the L18 issue corrects all three in `test_land_apply.py` in its own change-set and is an ancestor of the issue authoring the check, so only **`land_rehearsal.py:140`** survives to be found. `-ge 1` is stable under any further movement of the `test_land_apply.py` corrections, and discrimination is preserved because a vacuous check returns 0. Run it once the check exists and before those remaining stubs are corrected; record the observed count and `git rev-parse HEAD` in the resolution note; do NOT re-run afterwards, because correcting them inverts the correct answer.

### Capability Gate: L16 no longer commits work it did not stage
- Type: auto
- test_class: probe
- cwd: repo-root
- Condition: a pre-staged unrelated file is absent from the commit L16 makes
- Test: uv run skills/yf-plan/scripts/test_land_apply.py -k l16_commits_only_plan_dir -q
- Blocks: 5.1
- Instructions: EXPECTED RED AT THE §5.2c SWEEP — the test does not exist until Issue 3.3. Hoisted from 6.3 to its floor (pass-1 C16); its evidence exists the moment 3.3 closes. This gate stands between the landing and a silent push of unauthorized work to `main`.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | The stubs are corrected before L18 is fixed, breaking the suite against a still-broken function | high | Issue 5.1 `depends-on` Epic 2; the Approach states the reverse-of-obvious ordering explicitly |
| R2 | The mock-fidelity check is authored after the stubs are fixed and passes vacuously | high | Its capability gate requires it to find the **one** stub still uncorrected at that point (`land_rehearsal.py:140`) — the L18 issue corrects all three `test_land_apply.py` stubs upstream (pass-3 C30, pass-5 C42, pass-6 C43) — expressed as a FLOOR so it survives further movement, and is ONCE-ONLY |
| R3 | Execution runs in a worktree, so the primary keeps the unfixed L18 and the landing crashes at the prune again | high | A capability gate blocks **0.7**, 1.1, 3.1 and 4.1 on `execute.worktree == false` — 0.7 included because its correctness IS that the branch is cut in the primary checkout (pass-2 C25; restated because a stale mitigation cell is how that blocking got lost once already, pass-4 C38), checked at execute start rather than discovered at land time |
| R4 | Any capability gate pours without `test_class`, is classified `manual`, and the sweep never runs it | high | Issue 0.0 SETS the metadata rather than detecting it, and asserts the write took |
| R5 | The dispatch wrapper swallows a control-flow exception or a genuine harness failure | med | `KeyboardInterrupt`/`SystemExit` are re-raised explicitly; the caught row is `inconclusive`, never `pass`, and always halting |
| R6 | Fixing #340 alone ships a permanent false `ok: false` and a prune that reports success without pruning | high | Issues 2.2 and 2.3 land in the same epic; EXP-001 measured both in a real-git sandbox |
| R7 | The `-uall` switch changes what L16 sees and breaks an unrelated landing | med | Issue 3.3 adds a case running L16 **without** the gitignore anchor — the only configuration where the filter is load-bearing |
| R8 | In-place mode leaves no execute branch, so `land` cannot run at all | high | Issue 0.7 cuts it explicitly in the primary checkout; #331 stays open and is recorded as `partial` |
| R9 | A criterion re-evaluated at L11 cannot be true after the gates close, halting past the irreversible boundary | high | SC15 is `manual:`; every clause is measured against the current tree at drafting and recorded as correctly unmet |

## Success Criteria

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC0 | The execute branch `land` requires exists | `git rev-parse --verify --quiet plan-063-james-dixson-3f74c1-execute` → exit 0 | 0.7 |
| SC1 | A step that raises produces a halting envelope with exit 1, not a traceback | `uv run skills/yf-plan/scripts/test_land_apply.py -k step_exception_becomes_halting -q` → exit 0 | 1.1, 1.2 |
| SC2 | L18's call passes `force` | `grep -qE '_worktree_teardown\(\s*ctx\.plan_dir,\s*force=False\s*\)' skills/yf-plan/scripts/plan_manager.py` → exit 0 | 2.1 |
| SC2b | The duplicate branch deletion is gone | `grep -q 'ctx.run("git", \["branch", "-d"' skills/yf-plan/scripts/plan_manager.py` → exit 1 | 2.2 |
| SC2d | ...and L18 still deletes the branch, via the teardown | `uv run skills/yf-plan/scripts/test_land_apply.py -k l18_delegates_branch_delete -q` → exit 0 | 2.2 |
| SC2c | L18 reports a blocked teardown rather than passing | `uv run skills/yf-plan/scripts/test_land_apply.py -k l18_blocked_teardown -q` → exit 0 | 2.3 |
| SC3 | L16 commits only what it staged | `uv run skills/yf-plan/scripts/test_land_apply.py -k l16_commits_only_plan_dir -q` → exit 0 | 3.1, 3.3 |
| SC3b | L16's post-condition enumerates untracked entries | `grep -qE 'porcelain.*-uall\|"-uall"' skills/yf-plan/scripts/plan_manager.py` → exit 0 | 3.2 |
| SC3c | The filter survives a repo without the gitignore anchor | `uv run skills/yf-plan/scripts/test_land_apply.py -k l16_without_anchor -q` → exit 0 | 3.2, 3.3 |
| SC3d | A normal landing still commits its own plan-folder writes | `uv run skills/yf-plan/scripts/test_land_apply.py -k l16_commits_plan_dir_writes -q` → exit 0 | 3.1, 3.3 |
| SC4 | `worktree_dirty` is gone and the L16-predictive fields exist | `grep -q 'primary_checkout_dirty_outside_plan_dir' skills/yf-plan/scripts/plan_manager.py` → exit 0 | 4.1 |
| SC4b | The stale field name is gone, and the file was actually searched | `grep -q 'execute_worktree_dirty' skills/yf-plan/scripts/plan_manager.py && ! grep -q '"worktree_dirty"' skills/yf-plan/scripts/plan_manager.py` → exit 0 | 4.1 |
| SC4c | The dirty-outside-plan-dir rule has ONE definition site | `test "$(grep -cE 'def _[a-z_]*dirty_outside' skills/yf-plan/scripts/plan_manager.py)" -eq 1` → exit 0 | 3.2, 4.1, 4.2 |
| SC2e | Issue 2.1 corrected ALL THREE of its stubs, not just the call — a PROXY on the return shape; SC8 is the authority on arity (pass-4 C39, count corrected by pass-5 C42) | `test "$(grep -c 'lambda pd: {"action"' skills/yf-plan/scripts/test_land_apply.py)" -eq 0` → exit 0 | 2.1 |
| SC5 | A dirty primary checkout halts `--dry-run` | `uv run skills/yf-plan/scripts/test_land_apply.py -k dryrun_halts_on_dirty_primary -q` → exit 0 | 4.2 |
| SC6 | A decision path inside the work tree is refused before the tty gate | `uv run skills/yf-plan/scripts/test_land_apply.py -k decision_inside_tree_refused -q` → exit 0 | 4.3 |
| SC5b | The digest survives a POST-TEARDOWN resume, when `execute_worktree_present` has flipped | `uv run skills/yf-plan/scripts/test_land_apply.py -k digest_survives_resume_after_teardown -q` → exit 0 | 4.1, 4.2 |
| SC7 | `resolvable_by_agent` has a consumer or is gone | manual: Issue 4.4 records which was chosen and, if DROPPED, that all five writes are gone; if KEPT, where the consumer reads it. A field written in five places and read in none cannot be verified by counting writes, and the two branches need different evidence | 4.4 |
| SC8 | No stub fakes a signature its target rejects | `uv run scripts/checks/check_mock_fidelity.py` → exit 0 | 5.1, 5.2 |
| SC8b | The check is wired into the validation manifest | `grep -q 'check_mock_fidelity' CHANGE-VALIDATION.md` → exit 0 | 5.3 |
| SC9 | The seven new REQ-LAND ids exist as DISTINCT ids | `test "$(grep -oE 'REQ-LAND-03[0-6]' skills/yf-plan/spec/landing.md \| sort -u \| wc -l \| tr -d ' ')" -eq 7` → exit 0 | 0.1, 0.2, 0.3, 0.4, 0.5, 0.5b |
| SC9b | The amendment log records plan-063 | `uv run scripts/check_amendment_log.py --plan plan-063-james-dixson-3f74c1` → exit 0 | 0.6 |
| SC10 | All capability gates carry `test_class` and `cwd` as bead metadata | manual: Issue 0.0 records the gate ids and their `bd show` read-back. A repo-wide `bd list` clause is permanently true across historical gates and therefore cannot express this — measured in plan-062 as pass-5 C47 | 0.0 |
| SC11 | The landing suite passes AND has grown | `out=$(uv run skills/yf-plan/scripts/test_land_apply.py -q 2>&1); rc=$?; test $rc -eq 0 && test "$(printf '%s' "$out" \| grep -oE '[0-9]+ passed' \| cut -d' ' -f1)" -ge 56` → exit 0 | 3.3, 5.1 |
| SC12 | The FULL tier is green on the merged tree | manual: recorded by Issue 6.3, whose run is the authoritative one. Deliberately not a clause — `recheck-criteria` would re-run the multi-minute tier at L5 and again at L11, and its 300s cap would record a timeout as FAIL past the irreversible boundary | 6.3 |
| SC13 | The primary checkout carried the fixes before `--apply` | `P="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"; git -C "$P" grep -q 'force=False' -- skills/yf-plan/scripts/plan_manager.py && ! git -C "$P" grep -q '_worktree_teardown(ctx.plan_dir)$' -- skills/yf-plan/scripts/plan_manager.py` → exit 0 | 6.4 |
| SC14 | The landing route and halt-recovery contract are handed to the operator | manual: the artifact is the retrospective entry; the OPERATOR runs `land --apply`, which no check inside the plan may perform or self-certify | 6.5 |
| SC15 | THIS bundle's index is current | `uv run skills/yf-okf/scripts/okf.py reindex --check docs/plans/plan-063-james-dixson-3f74c1` → exit 0 | 6.6 |
| SC15b | Upstream draft bodies exist for every row requiring a mention | `test "$(ls docs/plans/plan-063-james-dixson-3f74c1/assets/upstream-drafts 2>/dev/null \| wc -l \| tr -d ' ')" -ge 6` → exit 0 | 6.2 |
| SC16 | Residual findings are filed, not dropped | manual: issue URLs recorded in the retrospective — filing is an outward-facing write and cannot be self-certified from inside the plan | 6.1 |
