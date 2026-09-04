# Landing handoff — the route and its halt-recovery contract (Issue 6.5 / SC14)

**This document does not land anything.** A Phase-5 bead must close before the Reconcile Gate
opens, so Issue 6.5's deliverable is the *artifact*. `SKILL.md` §6.0 is explicit: the session
prints the command and stops, and it names `dixson3/yoshiko-flow#293` — an executing agent
closing a consent gate by writing its own authorization. This session does not become its
second instance.

## Step 0 — the dry run (already computed, re-run before landing)

```bash
uv run skills/yf-plan/scripts/plan_manager.py land --dry-run docs/plans/plan-063-james-dixson-3f74c1 --json
```

Last observed: **`verdict: pass`, `halts: []`**, all six upstream rows `draft_present: true`,
`merge_preview.available: true` with `conflicts: []`, `execute_branch:
plan-063-james-dixson-3f74c1-execute` resolving, `execute_worktree_present: false` (in-place
mode — correct, and now *excluded from the digest* per `REQ-LAND-036`).

**Re-run it.** The manifest carries a digest over `resolved_target_tip` and `predicted_tree`;
if another plan lands on `main` first, the stored digest goes stale and `--apply` halts as a
staleness report rather than proceeding.

## Step 1 — the `lander` agent

Dispatch `agents/lander.md` with the dry-run manifest; it returns a **decision document**,
never a command. The main session writes the file, then:

```bash
uv run skills/yf-plan/scripts/plan_manager.py land --validate-decision <decision> docs/plans/plan-063-james-dixson-3f74c1
```

**Write the decision OUTSIDE the work tree.** `REQ-LAND-035` (added by this plan) now *refuses*
an in-tree decision path — and every in-tree `body_path` it names — before the tty gate. The
dry run's emitted `apply_command` already defaults it to `$TMPDIR`.

## Step 2 — THE OPERATOR RUNS THIS. The session does not.

```
\
  uv run skills/yf-plan/scripts/plan_manager.py land \
    --apply ${TMPDIR:-/tmp}/plan-063-james-dixson-3f74c1-decision.json \
    docs/plans/plan-063-james-dixson-3f74c1
```

`land --apply` refuses without a controlling terminal at **exit 3** (`REQ-LAND-014`). Read that
gate for what it is: **detection, not prevention.** `herdr pane run <pane> <cmd>` produces a
genuine pty in one sanctioned call and is a *named known bypass*. Using it to self-authorize is
not a clever loophole — it is an unmistakable act, and making it unmistakable is the entire
thing the gate buys.

## Halt-recovery contract

The landing is journalled and **resumable**: re-invoking `--apply` with the same decision file
reads the journal, resumes from the recorded phase, and re-derives every fact in the digest's
coverage set before continuing. `l0_lock_acquire` is exempt and always re-executes.

| Halt | Meaning | Recovery |
| :-- | :-- | :-- |
| exit 1, `primary-checkout-dirty-outside-plan-dir` | **NEW this plan.** The dry run predicts the L16 failure | `git stash` or commit the unrelated paths listed in `halts[].paths`, re-run `--dry-run` |
| exit 1, decision/`body_path` inside the tree | **NEW this plan.** Refused *before* the tty gate, so no write preceded it | Move the file outside the checkout; nothing to undo |
| exit 3 | no controlling terminal | Run it yourself, in your own shell |
| exit 2, journal corrupt/conflicted | INCONCLUSIVE — the journal could not be read | Read `remediation`; resolve by hand |
| halt at or before **L5** | pre-outward-write | Fix and re-run; nothing has been published |
| halt at **`L_REJECTED_PUSH_2`** (L16) | **post-outward-write** | `git pull --rebase`, **re-validate**, retry. **NEVER REVERT** — reverting contradicts comments already posted, issues already closed and `status: complete` already written |
| a step **raises** | **NEW this plan** (`REQ-LAND-030`). Halting `inconclusive`, exit **1**, journal NOT advanced, traceback in `detail.traceback` | Fix the cause and re-run. **A resume re-enters the same step and raises again** — that is correct, not a bug: advancing the journal past a step that raised would manufacture the evidence the resume checks |
| **L18 `blocked`** | **NEW this plan** (`REQ-LAND-031`). The teardown pruned nothing | Inspect the worktree, confirm no work is lost, re-run; L18 re-executes |

## What is deliberately NOT authorized here

- **Upstream filing of the eight residual findings.** Drafted at `assets/residual-issues/`,
  filed as local beads, `gh issue create` **proposed only**. Outward-facing write.
- **`git push`.** `main` was already 2 commits ahead of `origin` and unpushed before this plan
  began — a pre-existing condition this plan did not create and must not silently resolve.
- **`yf self install --from-build --build`.** L19 runs it *iff* the change set touches
  `skills/` — it does — and only when the decision enables it. Its preconditions are: on
  `main`, clean tree, in sync with `origin`. **None of those hold right now**, which is why the
  redeploy is the last step of landing and not a step of execution.
