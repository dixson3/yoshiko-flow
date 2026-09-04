---
type: Finding
okf_spec: OKF-PLAN
description: 'Designs and sandbox-proves the _land_execute exception wrapper (catch Exception, re-raise KeyboardInterrupt/SystemExit, inconclusive + halting + journal=None, exit 2). HEADLINE: plan-060 Epic 6 did NOT skip L18 — it executed L18 with the crashing call stubbed, and the stub encoded the CALLER wrong arity, so every instrument in the repo was calibrated against the call site instead of the callee. Also: a zero-stub spike ran 18 of 19 steps for real; only L14 needs new fixture work.'
---
# EXP-002 — The dispatch wrapper, and why the rehearsal missed L18

**Question.** How should `_land_execute` turn an exception into a halting step? And why did
plan-060's Epic-6 rehearsal miss L18?

## Approach Tested

Read the dispatch loop, `_step`, `LAND_STEP_JOURNAL`, `LandingJournal.write`, `_land_envelope`
and `_land_exit_code`; read `land_rehearsal.py` and plan-060's committed
`assets/rehearsal-record.json`. Then four sandbox spikes on a copy: reproduce plan-060's green
record; delete one stub line and reproduce plan-062's crash; implement and drive the proposed
wrapper; and drive a maximal-coverage **zero-stub** rehearsal with only outward processes
injected.

## Result

### HEADLINE: the rehearsal did NOT skip L18 — the stub encoded the caller's wrong arity

`land_rehearsal.py:139`:

```python
pm._worktree_teardown = lambda pd: {"action": "not-registered"}
```

A **one-parameter lambda** standing in for a two-parameter function. `_land_l18_prune` calls it
with one argument, so **the stub accepts exactly what the real function rejects.** plan-060's
record shows `"l18_prune": "pass"` with `"terminal_journal_state": "L_DONE"` — green, on a code
path that cannot run.

The Tier-1 suite makes the identical mistake in three more places (`test_land_apply.py:1023`,
`:1180`, `:1254`). **Every instrument in the repo was calibrated against the call site instead of
the callee**, which is why neither tier could see the defect. This independently corroborates
EXP-001's mock-fidelity finding, by a different route.

**inferred:** the defect class is *"a hand-written stub whose signature is copied from the call
site."* No arity check over production code would catch it — the production call and the stub
agree; it is the *real function* they both disagree with.

### The wrapper, implemented and driven

Inserted at `:9747`, catching `Exception` after re-raising `KeyboardInterrupt`/`SystemExit`:

```json
{"halted": true, "at": "l18_prune", "crashed": true,
 "journal_phase": "L_MIRRORED",
 "l18_row": {"verdict": "inconclusive", "halting": true, "journal": null},
 "l18_detail_exception": "TypeError",
 "terminal_state_reported": false}
```

`L_MIRRORED` is **exactly the phase plan-062 observed in production** — the wrapper reproduces
the real journal outcome while replacing the traceback with an envelope. Control-flow types
verified separately: `KeyboardInterrupt: PROPAGATED`, `SystemExit: PROPAGATED (code 7)`.
`_land_exit_code("inconclusive")` → **2**.

**The wrapper does NOT fix the resume loop, and should not.** A resume still re-enters L18 and
raises identically. Advancing the journal past a step that raised would manufacture exactly the
evidence `_land_resume_done` exists to refuse, and `LandingJournal.write` (`:8604`) rejects any
phase outside the closed 17-state set — there is no `L_CRASHED` to write without a
`spec/landing.md` amendment. State it in the reason string; do not engineer around it.

### A zero-stub rehearsal already reaches 18 of 19 steps

Real `_validate_merged`, real `_worktree_teardown`, real bd close chain, L19 enabled, only
`gh`/`uv`/`yf` faked through `runner`:

```
l0..l7 pass (L_LOCKED → L_RECONCILED, real fetch/merge/commit/push to a fake origin)
audit-close · retrospective-report · judgement-never-fired · classify-deliverable  pass
close-reconcile-step · verify-reconcile  pass
recheck-criteria  inconclusive (exit 2, correctly non-halting)
l12_close_cascade · l13_complete_gate  pass
l14_pour_fidelity  FAIL (INCONCLUSIVE — no poured bead DAG)   <- the only genuine blocker
```

### Blocker taxonomy — measured

- **Injectable:** every outward process in L0–L7 and L16–L19 goes through `ctx.run`, so `gh`
  (L7 `:9147`), `upstream.py push` (L17 `:9450`) and `yf self install` (L19 `:9582`) are all
  fakeable.
- **NOT injectable: L8–L15 use bare `subprocess.run`, never `ctx.run`** — which is precisely why
  the rehearsal had to replace three whole step functions.
- `bd list` at L14 is the **only** subprocess in that block launched **without `cwd=ctx.root`**;
  it inherits the process cwd. Latent, harmless today only because `rehearse()` chdirs.
- **Absence finding: the rehearsal has ZERO coverage of the `--apply` CLI preamble.** It calls
  `_land_execute` directly (`:142`), entering below the seam at `:8308` — so the tty gate,
  `_land_assert_primary_checkout`, decision parsing and `journal.recover()` are never exercised.
- `bd init` in a throwaway repo is cheap (seconds). The expensive fixture is a **poured** DAG so
  `pour_fidelity --strict` returns 0; pouring is `bd mol pour` from a `.formula.toml`.

## Implications for Plan

**measured:** the crash reproduction, the wrapper behaviour, the control-flow propagation and
the 18-of-19 coverage all came from runnable spikes. **inferred:** the causal claim about stub
provenance.

**Extending the rehearsal is necessary but NOT sufficient.** Removing the `_worktree_teardown`
stub would have caught this bug; the general defect — hand-written stubs carrying the caller's
signature — survives any amount of extension. The rehearsal and Tier-1 shared one wrong
assumption, and adding more of the same instrument does not remove it.

## Recommendations

1. **Wrap the dispatch**: `except (KeyboardInterrupt, SystemExit): raise` then `except
   Exception`. Catch bare `Exception` — the whole point is the *unexpected* one, and a
   `TypeError` from an arity mismatch is on nobody's list. Write the re-raise clause explicitly
   even though those two do not inherit from `Exception`, so the invariant is readable rather
   than inferred from the hierarchy.
2. **The caught row is `inconclusive`, `halting=True`, `journal=None`**, exit **2**.
   `inconclusive` because nothing was measured false — this is the instrument; `halting` because
   the executor cannot know what the step did before it raised, and what follows is destructive.
3. **Fix the actual bug in the same change-set.** The wrapper makes the crash legible; it does
   not stop it happening.
4. **Fix all four stubs**, then add the structural guard: a test binding each monkeypatched
   replacement against `inspect.signature` of the real function.
5. **Extend the rehearsal toward zero stubs**, in value order: (a) drop the `_worktree_teardown`
   and `_validate_merged` stubs — free today; (b) route L8–L15's three `subprocess.run` sites
   through `ctx.run` and pass `cwd=ctx.root` to L14's `bd list`; (c) add `bd init` + a poured
   fixture to clear L14; (d) drive it through the **CLI** with a faked tty, the only way the
   gate, the checkout assertion and `recover()` are ever exercised.
6. **Assert no step returned `inconclusive` with an `exception` key.** Once the wrapper exists, a
   future crash becomes a green-looking non-halting record unless the rehearsal looks for it —
   the same "green on a path that cannot run" shape this investigation is about.
