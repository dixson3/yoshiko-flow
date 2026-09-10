---
type: Review
okf_spec: OKF-PLAN
id: pass-5
plan: plan-068-james-dixson-8ae0e1
created: '2026-09-09'
description: >-
  [red-team pass 5, EXECUTION] REVISE - 6 concerns, all sentence-level. Executed the pass-4 fixes
  rather than reading them: closure depth is 13 not 10, the ctx-less set does NOT become empty
  (three helpers remain), Issue 1.1's runner= closes only half the sandbox escape (three filesystem
  probes need root=), and 8 tests break not 1. SC9, the REQ-LAND-031 retirement, runner= feasibility
  and all counts HELD under adversarial execution.
---
# Red-Team Pass 5 (EXECUTION) — plan-068-james-dixson-8ae0e1

## Verdict: REVISE
no new prose concerns were sought or raised."*

Targeted verification pass, dispatched on pass-4's own judgement that a general reading pass has
negative value. Every check below was **run**, not read.

## What HELD

- **SC9's base-pinned range holds under adversarial input.** 11 cases beyond the nine already
  verified — detached HEAD, non-ancestor base, rebase, octopus merge, and a missing / empty /
  whitespace-padded / garbage / `gc`-pruned base file. **Every degenerate input fails to exit 2 or
  gives a correct 1; no false green.**
- **The `REQ-LAND-031` carve-out retirement is correct**, verified against the requirement's full
  text at `landing.md:464-478`. All four clauses are satisfied by a `runner=`-carrying call.
- **The `runner=` change is feasible**, prototyped end to end in a sandbox copy. Only `_run_shell`
  resists, and only cosmetically.
- **Counts, extraction and SC12's eight relocated items are all exactly as stated** — every one of
  the eight independently located in plan-069's text by line number.

## Concerns

| # | Severity | Concern | Resolution |
| :-- | :-- | :-- | :-- |
| C1 | medium | **Closure depth is 13, not the 10 stated normatively.** Executing 0.3's *own mandated derivation* yields thirteen — the same constant-vs-SPEC mismatch pass-4 C1 diagnosed, one number over. Also: the derivation only excludes the seam edge *by accident*, because `self.run = self._dispatch` is an assignment so the AST resolves no callee named `run`; a future `def run` would explode the closure to nearly the whole module | **Independently reproduced** (my own AST closure: frontier **6**, transitive **13**). 0.3 now names all thirteen, states that **the SPEC quotes whatever the script emits rather than restating a number**, and mandates excluding the seam edge explicitly |
| C2 | medium | **The ctx-less set does NOT become empty**, so 0.3's "target state is everything on the seam … ideally empty" was aspirational. After 1.1 routes `_validate_merged` and `_worktree_teardown`, **three depth-1 helpers remain**: `_land_abort_merge`, `_land_capture_conflict` (L1/L2 conflict recovery) and `_land_changed_set` (close chain, L19) | 0.3 now states the remainder explicitly and makes it **Issue 1.1's scope decision** — route those three too (then it really is empty), or declare them the expected content with the reason. *"What is not safe is landing a constant the SPEC says should be empty."* The L1/L2 `git merge --abort` consequence for Issue 2.5 is recorded |
| C3 | medium | **Issue 1.2's "the ONLY assertion the refactor breaks" is measurably false — 8 tests break.** Prototyped: `4 failed, 62 passed` baseline → `12 failed, 54 passed`. Six on stub arity (`TypeError: … unexpected keyword argument 'root'`), one on an exact kwargs-dict equality, one on its own anti-vacuity guard | All eight enumerated by name in 1.2. Noted that this is **`check_mock_fidelity` working as designed** — `_teardown_ok`'s docstring says its arity is guarded by that check binding `inspect.signature`, and a signature change is exactly what it exists to catch |
| C4 | medium | **`runner=` alone closes only HALF the pass-4 C4 escape.** `_validate_merged`'s tier-1 decision is three **filesystem/config** probes keyed on `_repo_root()` — `_approved_manifest_present`, `_change_validation_script`, `_resolve_validate_cmd` → `_read_config` — and **no runner intercepts a filesystem read**. A sandboxed test without `os.chdir()` would still resolve the **real** repo's manifest and engine, then hand the fake a command whose `cwd` is the real repo. Execution contained; *resolution* not | 1.1 now says **`runner=` AND `root=`** on the `_dirty_outside_plan_dir` model (which already carries both), naming the three probes as the reason |
| C5 | low | `_run_shell` is `shell=True` over a command *string* with no cwd, so it does not fit the `(prog, args, cwd=)` contract; routing it introduces an `sh` program token visible to the program-set assertion and to Issue 2.5's fakes | Folded into 1.1 alongside the deferred `env=` question: route as `sh -c` and update both expectations, or declare tier-2 `validate-cmd` out of the seam |
| C6 | low | SC9 exits 0 on a **squash-merged** history for violating and compliant sources alike — indistinguishable | Recorded in SC9 as a **declared limit**: the squash makes the SPEC and code edits one commit and destroys the ordering evidence, so no expression over that history can recover it. `land`'s L2 performs a real `--no-ff` merge, never a squash, so it is outside the landing path |

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 depth 13 not 10 | medium | Independently reproduced; 0.3 names all 13, derives rather than quotes, excludes the seam edge | `main-session` | `resolved` |
| C2 set is not empty | medium | Remainder stated; made 1.1's explicit scope decision | `main-session` | `resolved` |
| C3 eight tests break | medium | All eight enumerated in 1.2 | `main-session` | `resolved` |
| C4 runner= half-closes the escape | medium | 1.1 now requires `root=` as well, with the three probes named | `main-session` | `resolved` |
| C5 `_run_shell` contract mismatch | low | Decision folded into 1.1 | `main-session` | `resolved` |
| C6 squash-merge blind spot | low | Declared limit recorded in SC9 | `main-session` | `resolved` |

**Final status: all concerns resolved.** Re-verified — 5 epics, 23 issues, 31 edges, 5 gates,
16 criteria, 9 risks, zero `unparsed`, zero dangling, zero undischarged.

*"The residual risk remains execution-surfaced. C1-C4 are four sentence-level edits inside Issues
0.3, 1.1 and 1.2 — no design change, no re-scoping, no new investigation. A sixth general reading
pass would still have negative value."*
