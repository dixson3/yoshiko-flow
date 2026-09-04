---
type: Finding
okf_spec: OKF-PLAN
description: 'Traces exactly what glue wires land --apply to _land_execute (~38 lines, verified working in a sandbox) and establishes that ~80% of helpers already exist. HEADLINE: _land_execute resume is a confirmed no-op bug that wiring the seam makes REACHABLE for the first time — a resumed landing re-executes L6 push and L7 gh comments. The plan therefore lands the RESUME FIX FIRST: ordering is not atomicity, and resume-first leaves no window in which the bug is live. Also records that plan-060 never assigned the seam to any issue.'
---
# EXP-002 — What glue does `land --apply` need, and is anything else broken?

**Question.** Is wiring `--apply` to `_land_execute` one call, or is real work missing?

## Approach Tested

Read the `--apply` branch, `_land_execute`, `LandingContext`, `LandingJournal`,
`_land_bind_decision`, `_land_repreview_or_halt` and `_land_exit_code`. Ran an AST analysis of the
resume block's store/load sites, an orphan sweep over every `_land*` function, and a sandbox spike
(`$(mktemp -d)`, local bare `origin`) driving a fresh apply, a forced halt at L17, and a resume.
Searched `SPEC.md`, `spec/landing.md`, plan-060's plan.md, `test_land_apply.py` and `git log -S`.

## Result

## HEADLINE: wiring the seam makes a LATENT DATA-LOSS BUG REACHABLE

`_land_execute`'s resume path is a **confirmed no-op**. Today that is harmless because
**nothing can invoke it**. The moment `--apply` works, the first halted landing resumes by
**re-executing every step from L0** — including `l6_push_one` and `l7_reconcile_writes`.

Measured in a sandbox: halt forced at L17, journal on disk `L_PUSHED_2`, `recover()` correctly
returned `{'action': 'resume', 'resume_after': 'L_PUSHED_2'}` — and the resume re-ran all
fifteen steps:

```
steps re-executed: ['l0_lock_acquire', 'l1_down_merge', 'l2_merge', 'l3_validate_merged',
 'l4_commit_merge', 'l5_advisory_recheck', 'l6_push_one', 'l7_reconcile_writes',
 'l8_close_chain_head', 'l12_close_cascade', 'l15_update_status',
 'l16_commit_and_push_two', 'l17_residual_mirroring', 'l18_prune', 'l19_redeploy']
    l6_push_one pass | push #1 complete — THE FIRST IRREVERSIBLE STEP HAS BEEN CROSSED
```

**Concretely: L7 re-posts every reconcile `gh` comment** (duplicate public comments), L12
re-runs the bead close cascade, L0 re-acquires the lock, L3 re-runs the multi-minute FULL tier.
A variant run instead *failed* — `could not commit the merge` at L4, because L2's re-merge was
already-up-to-date. So the behaviour is **non-deterministic between silently duplicating
outward writes and halting with a nonsense reason.**

**Therefore the seam and the resume fix MUST LAND TOGETHER.** Shipping the seam alone converts
a dormant bug into a live one that writes to public issues.

### The bug, statically confirmed

```python
9550    done: set[str] = set()
9551    if resume_from:
9552        order = list(LAND_PROGRESS_ORDER)
9553        if resume_from in order:
9554            reached = set(order[: order.index(resume_from) + 1])
9555            for key, _ in LAND_EXECUTOR:
9556                # A step is complete when the journal state it WRITES has been reached.
9557                pass
9558            done = reached
```

AST measurement: `done` **stores at 9550, 9558; loads at NONE**. Written twice, read zero
times; the step loop at `:9560` never consults it. `done` is also the **wrong type** even if
read — `reached` holds *journal states* (`L_LOCKED`…) while the loop iterates *step keys*
(`l0_lock_acquire`…). **The `pass` loop is the missing translation, left unwritten.**

`REQ-LAND-011` ("A partial failure **is resumable**") is unimplemented at **every** layer: no
caller of `recover()`, no computation of `resume_from`, and the parameter ignored inside.

## The glue: ~38 lines, and 80% of it already exists

| Step | Helper | Status |
| :-- | :-- | :-- |
| Load + parse decision JSON | — | **write** (~8 lines; mirror `:8264-8277`) |
| Re-derive manifest, verify digest, narrowing-only | `_land_bind_decision` `:8674` | **exists** |
| Staleness framing | `_land_repreview_or_halt` `:8689` | **exists — but ORPHANED** |
| Construct context | `LandingContext` `:8736` | **exists**, one line |
| Detect resume | `LandingJournal.recover()` `:8531` | **exists — also ORPHANED** |
| Map `recover()`'s 4 actions to envelopes | — | **write** (~7 lines) |
| Call the engine | `_land_execute` `:9538` | **exists**, one line |
| Verdict → envelope → exit code | `_land_envelope` `:7715`, `_land_exit_code` `:7737` | primitives exist; **mapping must be written** |

A 38-line candidate ran end-to-end in a sandbox on the first try: `exit 0, verdict pass, phase
L_DONE`, all fifteen executor rows.

**The verdict derivation is design work, not a call.** `_land_execute` returns a bare progress
dict, never an envelope. And `halted → fail / reached_terminal_state → pass` is **wrong**: L8's
and L12's `inconclusive` results are explicitly **non-halting** (`:9112`, `:9132`, `:9158`), so
a landing can reach `L_DONE` carrying inconclusive steps. Laundering that into `pass` is the
coercion `REQ-LAND-012` forbids. The wrapper must scan `results` and derive a **three-valued**
verdict.

## Q3 — this was a deferral nobody picked up, not a forgotten deletion

- `git log -S"the --apply executor is not implemented"` → **one commit, `f9eddd9` plan-060
  Epic 1.** Epic 3 (`26a88a4`) and Epic 4 (`26bb490`) both landed afterwards and never removed
  it.
- **No test asserts exit 2 on the stub.** The only CLI-level `--apply` invocation in the suite
  is `test_tty_refusal_exits_three_not_one_or_two` (`:397`), which never gets past the gate —
  so the stub is **untested in both directions**.
- **plan-060's decomposition never contained the work.** Epic 3: journal, binding, tty gate,
  route record, conflicts, re-preview, tests. Epic 4: steps L0–L19, tests. **No issue owns the
  CLI seam.**
- An orphan sweep found exactly **two** uncalled `_land*` functions: `_land_repreview_or_halt`
  (Issue 3.6's deliverable) and `_land_execute` (Epic 4's engine). The seam is the only gap.

## Bonus defect (unasked, load-bearing)

A decision file written **at the repo root** halts the landing at L16 — *past the irreversible
boundary*:

```
REASON: L16's post-condition FAILED — porcelain='?? d.json' unpushed=0
```

L16's porcelain check (`:9290-9294`) filters only `LAND_JOURNAL_DIR`, and
`_land_apply_command` (`:8077`) hands the operator `--apply <decision.json>` with **no
guidance that the file must live outside the tree**. plan-061 avoided this only because its
lander happened to store the decision at `~/`.

## Implications for Plan

**measured:** every quantitative claim above came from a runnable spike or an AST read, not
from reading prose. **inferred:** the judgements about agent behaviour and about what a
future reader would conclude are reasoning, not measurement, and are labelled as such where
they appear.

The consequences for the plan are carried in the sections above and in `plan.md`'s Approach.

## Recommendations

1. **Replace `:8306-8311` with ~40 lines** of glue (verified in sandbox).
2. **Fix the resume (~13 lines):** translate step→journal via `LAND_STEP_JOURNAL`; for the
   three keys absent from it (`l3_validate_merged`, `l8_close_chain_head`, `l12_close_cascade`)
   resolve by backward scan; then **actually consult `done`** at `:9560`, skipping completed
   steps with an explicit `resumed` marker.
3. **Derive the verdict three-valued**, so a non-halting `inconclusive` is not laundered.
4. **Two seam tests:** (a) `--apply` reaches at least `l0_lock_acquire`; (b) a resume after a
   forced L17 halt **does not re-execute `l6_push_one` or `l7_reconcile_writes`**. Test (b) is
   the one that catches the resume bug.
5. **Amend the SPEC:** `REQ-LAND-011`'s `Verification:` points at
   `test_stale_decision_halts_before_merge`, which tests staleness, **not resume** — a vacuous
   verification. Retarget it (SPEC-first).
6. **Cheap hardening:** emit a decision path outside the worktree, or have L16 tolerate it.

Estimated: ~40 lines in `land_cmd`, ~13 in `_land_execute`, ~60 in `test_land_apply.py`, 1 SPEC
line.
