---
type: Asset
okf_spec: OKF-PLAN
description: "Landing handoff (rev 2026-10-20): BI-N2 cause found and fixed (58ce4ec); re-land plan-072 from a fresh session, L19 redeploy skipped in the decision"
---
# plan-072 landing handoff — re-land from a fresh session

**Revised 2026-10-20.** This replaces the 2026-10-16 handoff, whose diagnostic and decide steps
are done. It is written for a **fresh session** that has none of the prior context.

**Start only when the operator says go.** L3 takes about 5 hours and the operator wants it run in
the evening.

## Where things stand

- **Merge state:** the execute branch `plan-072-james-dixson-bae8de-execute` (`eff282d`) is the
  merge source. Its work is in `origin/main` since `5677780`, with 4 bookkeeping commits still
  unmerged. The landing's remaining job:
  - L3: re-validate the merged tree (FULL tier);
  - L7: close #407 with the attributed comment;
  - L8–L15: close the bead tree and write `status: complete`;
  - L16: push;
  - L17–L18: mirror and prune;
  - L19: redeploy. This is **skipped** in the decision file; see Step 3.
- **Five attempts, all halted or stopped at L3, all recovered locally.** No attempt has pushed or
  posted anything.
  - **Attempts 1–3:** an index drift, a stale digest, and a red test. All fixed.
  - **Attempt 4:** the FULL `trigger-eval` row FAILed on a pi cell.
  - **Attempt 5** (2026-10-20 06:55): **stopped by the operator** about 5 minutes into L3, to run
    it in the evening instead. Journal at `$TMPDIR/land072-recover5/`.
- **`main`** at `58ce4ec` or later, clean, `0 0` against origin, landing lock free.

## The attempt-4 failure: diagnosed and fixed

A pi-only diagnostic (`~/.cache/yf-trigger-eval/plan072-pi-diag.*`) passed 119 of 120 cells.
The one failure was **`BI-N2:pi`** (yf-beads-init near-miss "Show me the ready beads."), at a
rate of 0.33.

- **Cause: the eval environment.** The skill's description is not the cause.
  - The eval runs each rep in a fresh `git clone`. `.beads/` is gitignored, so the clone has no
    beads database and `bd ready` fails.
  - pi then follows the always-loaded `BEADS_INIT.md` rule and loads yf-beads-init. That is the
    correct response to a failing `bd`.
  - The description is unchanged since `409593d`.
- **Bisection:**

  | Variant | Misses (yf-beads-init activated) |
  | :-- | :-- |
  | Installed rule | 6 / 12 |
  | Rule block removed | 0 / 9 |
  | "Invoke only when bd fails" rewording | 12 / 12 |
  | Installed rule, with a beads DB in the clone | 1 / 9 |

  A rule rewording was tried and **reverted**. Do not reintroduce it.
- **Fix:** commit `58ce4ec`, operator-approved. `BI-N2` gets the per-rep fixture
  `bd init -q --non-interactive --skip-hooks --skip-agents -p evalfx`. With it the cell measured
  1/9 misses, about a 3% chance of failing an L3 cell (3 reps, needs 2).

## Re-land procedure

The operator authorized running `land --apply` in a **herdr tab**, a named REQ-LAND-014 bypass.
**Every** `herdr tab create` MUST pass `--workspace "$HERDR_WORKSPACE_ID"`; never open a tab in
another workspace.

```bash
cd /Users/james/workspace/dixson3/yoshiko-flow   # PRIMARY checkout
git rev-parse --abbrev-ref HEAD; git status --porcelain
git fetch -q origin && git rev-list --left-right --count origin/main...main   # main, empty, 0 0
SD=$(yf skill-dir yf-plan)
P=docs/plans/plan-072-james-dixson-bae8de
uv run $SD/scripts/plan_manager.py landing-lock status --json            # "held": false
# 1. manifest (pure read)
uv run $SD/scripts/plan_manager.py land --dry-run $P --json > /tmp/land072.json
# 2. decision: refresh the digest; the body must live OUTSIDE the work tree
D="$TMPDIR/plan-072-james-dixson-bae8de-decision.json"
cp -f $P/assets/upstream-drafts/407.md "$TMPDIR/plan-072-407.md"
#   set D.manifest_digest = /tmp/land072.json .digest
#   set D.upstream_writes[0].body_path = $TMPDIR/plan-072-407.md, body_sha256 = sha256 of that file
uv run $SD/scripts/plan_manager.py land --validate-decision "$D" $P --json   # must be pass
# 3. apply, in a NEW tab in this workspace
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --label plan072-land …
#   in that tab:
uv run $SD/scripts/plan_manager.py land --apply "$D" $P 2>&1 | tee /tmp/land072-apply6.log
```

- **The decision file** (`$TMPDIR/plan-072-james-dixson-bae8de-decision.json`, previous copy
  `$TMPDIR/plan-072-decision.prev.json`):
  - closes #407 with `assets/upstream-drafts/407.md`;
  - no refusals, no residual groups;
  - **`l19_redeploy` is `skip:`**, by operator directive. `land --apply` would otherwise run
    through to the redeploy before anyone watching could stop it.
  - **If the file is gone:** dispatch the `lander` again per yf-plan SKILL.md §6.0, and
    re-apply the L19 skip.
- **Runtime:** L3 runs the FULL tier, about **5 h**, ending with the both-harness trigger-eval.
- **Monitoring:** poll `/tmp/land072-apply6.log` with short commands only.
  - **Never** use a long blocking `sleep` in an agent shell. On 2026-10-18 a terminated
    monitoring call took a `nohup`'d eval down with it, because they shared a process group.
  - The landing runs in its own tab, so it is not exposed to this.
- **On an L3 halt** (nothing outward happens before L6):
  1. `git merge --abort`
  2. `mv .yf/plan/landing-journal/plan-072-james-dixson-bae8de.json "$TMPDIR/land072-recover6/"`
  3. `uv run $SD/scripts/plan_manager.py landing-lock release plan-072-james-dixson-bae8de`

  Then report the first failing FULL row to the operator. The `trigger-eval` row persists no
  `--results`, so a trigger-eval FAIL is diagnosed per the 2026-10-18 method: a pi-only run with
  `--results`.

## After a green landing

1. **Redeploy (L19, by hand):** re-check the AGENTS.md preconditions (on `main`, clean, `0 0`
   against origin). Get the operator's go, then run `yf self install --from-build --build`, and
   check that `yf --version` shows the hash of `HEAD`.
2. **#416:** post `assets/upstream-drafts/416.md` as a comment on tracker #416. Read it back with
   `gh issue view 416 --comments`.
3. **SC12:** record post-deploy evidence in `assets/post-deploy.md`:
   - pi startup without `[Skill conflicts]`;
   - a CC `--debug-file` without `Skill listing over budget`;
   - an installed-mode eval pass.
4. Close #416.
5. Remove the temporary `gate-plan072-*` rows from `CHANGE-VALIDATION.md`.
6. **Unblocks plan-073** (tracker #442): its execution is gated on plan-072 showing
   `status: complete` on `origin/main`. Run `/yf-plan execute plan-073-james-dixson-cc76de` in a
   new session, cutting the execute branch from `main`. The old development worktree was pruned.

## Known yf-plan defects met on the way (filed as beads)

- `yf-0xk9`: `land --apply` rejects a committed `body_path` inside the work tree, and
  `--validate-decision` does not catch it.
- `yf-m73l`: CI does not run `test_skill_trigger_eval.py`.
- `yf-htws`: the gate lock is not in the kernel gitignore set. plan-073 fixes it.
- `yf-noin`: the FULL `trigger-eval` row persists no `--results`, and `validate-merged` records
  `first_failure: null`. Together they made the attempt-4 FAIL undiagnosable.
- `yf-9lh9`: `update-status review-pass` overwrites status.
