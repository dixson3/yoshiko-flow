---
type: Reference
okf_spec: OKF-PLAN
description: 'Operator runbook for `land`: what the session prints, what you paste, what each halt means, and how to resume from every one of the seventeen enumerated journal states.'
---
# Landing runbook

**Issue 6.3.** What the session prints, what you paste, what each halt means, and how to resume
from each enumerated journal state.

## The shape, in one paragraph

The session runs `land --dry-run`, dispatches the read-only `lander`, writes the decision file,
prints a command, **and stops**. You run the command. The session never runs `land --apply`
(`REQ-LAND-013`), and `--apply` additionally refuses a caller with no controlling terminal at
**exit 3** (`REQ-LAND-014`).

**That refusal is DETECTION, NOT PREVENTION.** `herdr pane run <pane> <cmd>` produces a genuine
pty in one sanctioned call and is a **named known bypass**. Nothing here makes a self-authorized
landing impossible; it makes it unmistakable.

## What you will see

1. **The manifest** — facts only, mutating nothing. `git status --porcelain` is empty after it.
   (It does create one unreferenced object-database tree; that is recorded rather than denied.)
2. **The decision** — groupings, bodies, refusals, and one `enable`/`skip` per `L0`–`L19`.
3. **The consent prompt** — every enumerated write, every refusal, every skip. If it says the
   landing will post 4 comments and close 1 issue, that is the whole outward-facing set.
4. **The command**, fully qualified, naming the checkout it must run from.

## What you paste

```bash
cd <primary checkout> && uv run skills/yf-plan/scripts/plan_manager.py land \
    --apply <decision.json> docs/plans/<plan-id>
```

**Run it from the PRIMARY checkout**, never from `.worktrees/<plan-id>`. `land --apply` refuses
at **exit 1** otherwise, before it takes the lock or touches a branch: every plan-folder read is
cwd-relative and the plan folder is primary-side, so from the wrong checkout the landing would
read a stale bundle — and L2 cannot check out the merge target from a linked worktree anyway.

## Exit codes

| Exit | Meaning | What to do |
| --: | :-- | :-- |
| `0` | the landing completed | nothing |
| `1` | a **verdict of FAIL** — a step's condition was measured and does not hold | read the halt, follow its `remediation` |
| `2` | **INCONCLUSIVE** — the verb could not measure at all | repair the instrument, not the plan |
| `3` | **the controlling-terminal refusal** | run it yourself, in your own shell |

`3` is neither `1` nor `2`: nothing was measured false, and the verb reached a definite
conclusion. Retrying on a `3` loops forever against a gate that never opens on retry.

## Resuming — the seventeen journal states

The journal lives at `.yf/plan/landing-journal/<plan-id>.json`. **Recovery is keyed on the
RECORDED PHASE, never on observed state** (`REQ-LAND-009`): at several boundaries "wrote nothing"
and "wrote everything then died" are indistinguishable from the filesystem.

Re-invoking `land --apply` with the same decision resumes from the recorded phase and
**re-derives every fact first** — a resume whose digest no longer matches halts as a staleness
report rather than continuing against a tree it never saw.

### Progress states

| State | Where the landing got to | Resume |
| :-- | :-- | :-- |
| `L_INIT` | journal created; nothing acquired, nothing mutated | re-run; nothing to undo |
| `L_LOCKED` | landing lock held; no tree mutated | re-run; the lock is re-acquired or reported held |
| `L_DOWNMERGED` | target down-merged into `<plan-id>-execute` | re-run from L2 |
| `L_MERGED_UNCOMMITTED` | merge present on the target, **uncommitted** | re-run from L3; the FULL tier re-validates |
| `L_VALIDATED` | FULL tier green, merge committed, lock released | re-run from L5 |
| `L_PREPUSH_CHECKED` | advisory criteria run done — **the last fully reversible state** | re-run from L6; abandoning here leaves no outward trace |
| `L_PUSHED_1` | **push #1 done — the irreversible boundary is crossed** | re-run from L7; the merge is on the target and stays there |
| `L_RECONCILED` | every enumerated `gh` write posted and read back | re-run from L8 |
| `L_CLOSED` | close chain done; `status: complete` written | re-run from L16 |
| `L_PUSHED_2` | plan-folder writes committed and pushed | re-run from L17 |
| `L_MIRRORED` | residual beads mirrored or proposed | re-run from L18 |
| `L_PRUNED` | worktree, branch and (if authorized) tab pruned | re-run from L19 |
| `L_DONE` | redeploy performed or correctly skipped — **terminal GREEN** | nothing; the journal is cleared |

### Conflict states — four sites, and the recoveries are NOT uniform

| State | Site | Recovery |
| :-- | :-- | :-- |
| `L_CONFLICT_DOWNMERGE` | L1 | captured from three sources, then `git merge --abort`. Fully local; nothing pushed, nothing posted |
| `L_CONFLICT_MERGE` | L2 | same — capture then abort. Still pre-push and pre-outward-write |
| `L_REJECTED_PUSH_1` | L6 | `git pull --rebase`, **RE-VALIDATE**, retry. Never push an unvalidated rebase |
| `L_REJECTED_PUSH_2` | L16 | `git pull --rebase` and retry. **NEVER REVERT** |

**`L_REJECTED_PUSH_2` is the one that differs in kind.** By L16 the reconcile comments are
posted, the bead tree is closed and `status: complete` is written. Reverting would contradict
outward statements already made — so the recovery is retry, and `merge --abort` is the *wrong*
tool there even though it is right at L1 and L2.

**No site is ever auto-resolved.** No `-X ours`, no `-X theirs`, no strategy override. Each
silently discards one side's work and the discarding is invisible in the resulting commit. The
verb hands you the conflict from three independent sources and stops.

## What a halt after L6 means

Every halt after L6 leaves the target **already carrying the merge**. That is stated plainly
rather than implied away. What makes it acceptable is that L3's FULL tier ran first, so the code
on the target is validated; the later halts (L10, L11, L12) concern plan bookkeeping and upstream
state, not code correctness, and each is repairable without a revert.

## Things the landing will refuse to do

- **Close an upstream issue its disposition forbids.** A `partial` row stays OPEN; the decision
  cannot override the contract the plan was approved with.
- **Believe a write it did not read back.** `gh` exiting 0 does not establish the body posted is
  the body intended, and `bd close` refuses *and exits 0* when blocked.
- **Skip `L0`–`L6` or `L16`.** Skipping the merge is a different operation, not a narrower
  landing; skipping L16 reproduces the unpushed-`complete` residue the capability exists to
  remove.
- **Close a herdr tab it cannot prove it created.** Provenance is unanswerable, so the default
  is to propose.
- **Rewind history to a target.** No `reset`, no `revert`, no `cherry-pick`, no forced push
  (`REQ-LAND-017a`).
