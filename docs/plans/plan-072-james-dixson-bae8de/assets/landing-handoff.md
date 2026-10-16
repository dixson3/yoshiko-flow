---
type: Asset
okf_spec: OKF-PLAN
description: "Landing handoff (2026-10-16): L3 trigger-eval FAILed on a pi cell; held pi-only diagnostic eval with persisted results, then the re-land procedure"
---
# plan-072 landing handoff — pi diagnostic eval, then re-land

**Status at handoff:** 2026-10-16. Written by the session that drove the landing so far, for the
session that will finish it.

## Where things stand

- **Merge state:** plan-072's execute branch (`plan-072-james-dixson-bae8de-execute`) has been
  merged into `main` before; that merge is in `origin/main` since `5677780`. The landing's
  remaining job is bookkeeping:
  - L7: close #407 with the attributed comment.
  - L8–L15: close the bead tree and write `status: complete`.
  - L16: push.
  - L17–L19: mirror, prune, redeploy.
- **Halts so far:** `land --apply` has halted at **L3** (validate-merged, FULL tier) four times.
  - **Attempt 1:** a plan-073 scaffold `index.md` drift. Fixed in `dabc07a`.
  - **Attempt 2:** decision digest stale. Refreshed.
  - **Attempt 3:** a red `trigger-eval-tests` test (`fake_run_one` rejected the `pi_model`
    kwarg). Fixed in `e122177`.
  - **Attempt 4** (2026-10-15 16:59 → 21:54): every FULL row passed except the final
    **`trigger-eval`** row. It returned **FAIL** (exit 1), not INCONCLUSIVE.
- **Recovery:** each halt was recovered locally with `git merge --abort`, the journal set aside
  and the lock released. Nothing has been pushed or posted by any attempt. `main` is clean.

## What the attempt-4 FAIL tells us, and what it does not

- **The failure is on pi.** The eval ran confirmation re-runs (3 more reps for any cell that
  scored < 0.5 in its first 3 reps but was recorded ≥ 0.5). A confirmation clone exists only
  for pi (`~/.cache/yf-trigger-eval/clone-pi-7ce98fe4-pi-c`, 21:53), never for CC. The run
  ended FAIL a minute later, so at least one **pi** cell stayed < 0.5 pooled over 6 runs.
- **We do not know which cell.** Three reasons:
  - The FULL row in `CHANGE-VALIDATION.md` passes no `--results`.
  - pi runs with `--no-session`, so it leaves no transcript.
  - The landing recorded `first_failure: null`.
- **Suspected cause, unconfirmed.** Recorded ratings date from Issue 3.4 (`409593d`); a skill
  description changed after that record. `6cb7636` ("yf-plan description cleanup") is the first
  candidate. It may also be a single cell's unlucky streak.

## Goal

1. Identify the failing pi cell(s) with a **pi-only diagnostic eval that persists its results**.
2. Decide: a real description regression (fix the description, re-record if needed) or noise.
3. Re-run the landing to completion, in a herdr tab, under the operator's standing exception
   (below).

## Step 1 — the diagnostic eval (HELD until the operator says go)

**Do not start it until the operator explicitly says to.** When told, run it from the repo root
of a clean `main`, detached so it survives the agent's tool timeout:

```bash
cd /Users/james/workspace/dixson3/yoshiko-flow
nohup uv run scripts/checks/skill_trigger_eval.py \
  --mode candidate --skills all --harness pi --reps 3 \
  --max-runs-per-hour 150 --max-backoff-seconds 1800 --json \
  --results ~/.cache/yf-trigger-eval/plan072-pi-diag.jsonl \
  > ~/.cache/yf-trigger-eval/plan072-pi-diag.summary.json \
  2> ~/.cache/yf-trigger-eval/plan072-pi-diag.log &
```

- **Why these flags:** they are the FULL row's flags with `--harness pi` and a persisted
  `--results`. No `--pi-model` is passed, matching the FULL row that failed.
- **Cost:** 120 intents × 3 reps = **360 runs**. At 150/h that is about **2.4 h**, plus any
  confirmation re-runs. pi spends shared-account tokens; there is no CC list-rate cost.
- **Progress:** `wc -l < ~/.cache/yf-trigger-eval/plan072-pi-diag.jsonl` out of 360, and
  `tail ~/.cache/yf-trigger-eval/plan072-pi-diag.log` for throttle and backoff lines.
- **If it is interrupted or rate-limited:** re-run the same command with
  `--resume ~/.cache/yf-trigger-eval/plan072-pi-diag.jsonl` in place of `--results …`. Runs
  already recorded are skipped.
- **The answer:** the summary JSON's `cells` map holds every `"<intent>:pi"` with `rate` and
  `verdict`, and `status` is the overall verdict. List every cell whose verdict is not `pass`.
  Then read that intent in `skills/<skill>/evals/triggers.json` and the skill's current
  `description` (`git log -p --since=2026-09-25 -- skills/<skill>/SKILL.md`).

## Step 2 — decide

- **Every cell passes:** attempt 4 was noise. Go to Step 3; the landing's own FULL run is
  required anyway.
- **A cell fails and its skill's description changed after `409593d`:** a real regression.
  - Fix the description on a short branch or on `main`, following REQ-SKAUTH-061/062 and the
    yf-skill-authoring Description guidance.
  - Re-run the diagnostic for just that cell (`--intents <ID> --reps 3`) until it passes.
  - Commit, then go to Step 3.
  - This is a description change, so the operator should see it before landing.
- **A cell fails and nothing changed:** report it to the operator. Do not edit `evals/` records
  to make it pass.

## Step 3 — re-land

The operator authorized running `land --apply` in a **herdr tab** (a named REQ-LAND-014
bypass). Open any tab in the **current workspace**: `herdr tab create --workspace
"$HERDR_WORKSPACE_ID" …`. The sequence:

```bash
cd /Users/james/workspace/dixson3/yoshiko-flow   # PRIMARY checkout, on main, clean
SD=$(yf skill-dir yf-plan)
P=docs/plans/plan-072-james-dixson-bae8de
# 1. manifest (pure read)
uv run $SD/scripts/plan_manager.py land --dry-run $P --json > /tmp/land072.json
# 2. decision: reuse the validated one, refresh its digest to the new manifest
D="$TMPDIR/plan-072-james-dixson-bae8de-decision.json"
cp -f $P/assets/upstream-drafts/407.md "$TMPDIR/plan-072-407.md"   # body must live OUTSIDE the work tree
#   set D's manifest_digest = /tmp/land072.json .digest ; upstream_writes[0].body_path = $TMPDIR/plan-072-407.md
#   and body_sha256 = sha256 of that file (python one-liner)
uv run $SD/scripts/plan_manager.py land --validate-decision "$D" $P --json   # must be pass
# 3. apply (in the herdr tab)
uv run $SD/scripts/plan_manager.py land --apply "$D" $P 2>&1 | tee /tmp/land072-apply5.log
```

- **If the decision file is gone from `$TMPDIR`:** dispatch the `lander` again per yf-plan
  SKILL.md §6.0.
- **The decision's content:**
  - Close #407 with `assets/upstream-drafts/407.md`.
  - No refusals, no residual groups, and every L0–L19 step enabled.
  - Before L19 (redeploy) runs, confirm the AGENTS.md preconditions: on `main`, clean, and
    `0 0` against origin.
- **Expected runtime:** L3 runs the FULL tier again, about **5 h**, ending with the
  both-harness trigger-eval.
- **On an L3 halt:** the recovery is `git merge --abort`, then
  `mv .yf/plan/landing-journal/plan-072-james-dixson-bae8de.json "$TMPDIR/"`, then
  `plan_manager.py landing-lock release plan-072-james-dixson-bae8de`. Nothing outward has
  happened before L6.
- **After a green landing:**
  - Post `assets/upstream-drafts/416.md` as a comment on tracker #416.
  - Record SC12 post-deploy evidence in `assets/post-deploy.md`: pi startup without
    `[Skill conflicts]`, a CC `--debug-file` without `Skill listing over budget`, and an
    installed-mode eval pass.
  - Then close #416.
  - Remove the temporary `gate-plan072-*` rows from `CHANGE-VALIDATION.md`.

## Known yf-plan defects met on the way (filed as beads)

- `yf-0xk9`: `land --apply` rejects a committed `body_path` inside the work tree, and
  `--validate-decision` does not catch it.
- `yf-m73l`: CI does not run `test_skill_trigger_eval.py`.
- `yf-htws`: the gate lock is not in the kernel gitignore set. plan-073 fixes it.
- To file: the FULL `trigger-eval` row persists no `--results`, and `validate-merged` records
  `first_failure: null`. Together they made the attempt-4 FAIL undiagnosable.
