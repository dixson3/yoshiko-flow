---
type: Finding
okf_spec: OKF-PLAN
---
# Experiment 3: Does `hoist` already cover the plain-push case?

**Question.** The plan's central premise is that no in-skill wrapper exists for the push step.
But `hoist --issues <csv>` dry-runs, pushes scoped, and maps `External:` — very close to the
specified `push`. If `hoist` already covers it, #106 is a prose fix and Epic 2 collapses.

This experiment exists because the red-team flagged the premise as **asserted but never
measured**. Measuring it answered the question and exposed a separate, more serious defect.

## Answer: no — `hoist` is push **plus a local close**

`plan_hoist()` emits three stages:

```python
cmds.append(f"{auth} bd {backend} push {ids_csv} --dry-run")   # 1. dry-run
cmds.append(f"{auth} bd {backend} push {ids_csv}")             # 2. real push
for bid in bead_ids:                                            # 3. local close
    cmds.append(f'bd close {bid} -r "{reason}"')
```

Stage 3 is the difference. `hoist` **removes the bead locally** with a reversible tombstone —
that is its purpose. A plain push must leave the bead open and mirrored. The 11-bead push earlier
in this session is the case in point: those beads stayed open locally and simply gained `External:`
mappings.

So a distinct `push` verb is justified: it is `plan_hoist` stages 1–2 without stage 3. The premise
holds, now on evidence rather than assertion.

## The defect this uncovered

`ids_csv = ",".join(bead_ids)` produces **comma-separated** ids. `bd <backend> push` takes
**space-separated** positional ids — as `SKILL.md` itself documents. Measured against bd 1.1.2 on
the live repo:

| Command | Result |
|:--|:--|
| `bd github push yf-m78m --dry-run` | `✓ Pushed 1 issues` |
| `bd github push yf-m78m yf-252c --dry-run` | `✓ Pushed 2 issues` |
| `bd github push yf-m78m,yf-252c --dry-run` | *(no `✓ Pushed` line at all)* |
| `bd github push yf-m78m,yf-252c --dry-run; echo $?` | **`0`** |

The comma form matches **zero** beads, prints no error, and **exits 0**.

## Why that is destructive rather than merely ineffective

`cmd_hoist(--apply)` and `cmd_land(--apply)` run each command via `run(["bash","-c",c])` without
inspecting exit codes — and there is nothing to inspect, because every stage "succeeds". For a
multi-bead hoist the realized behavior is:

1. dry-run push — matches nothing, exit 0
2. real push — matches nothing, exit 0
3. `bd close <bead> -r "hoisted upstream to <dest> (reversible tombstone; un-hoist to restore)"`
   for **every** bead

The beads leave the local worklist, marked hoisted, with **no upstream issue in existence**. The
tombstone text asserts something untrue. Failure and success are indistinguishable in the output.

Call sites: `upstream.py:709` and `:729` (`cmd_land` propose / apply) and `:750` (`cmd_hoist`).
**Single-bead hoist is unaffected** — a one-element join contains no comma — which is likely why
this survived: the common interactive case works.

Recoverable via `unhoist` (the tombstone is reversible by design, the saving grace), but only if
someone notices, and nothing surfaces it.

## Why the test suite did not catch it

The fixture tests assert the **shape** of the emitted command sequence — they compare against an
expected string that itself contains the commas. A test written that way passes while encoding the
defect. This is the failure mode where a test documents the implementation instead of the contract:
nothing in the suite ever asks whether the emitted command *matches beads in `bd`*.

## Consequence for the plan

Filed as **#129** and folded in as its own epic, ahead of the `push` work, because:

- it is the highest-severity item in the area (data-integrity, silent);
- it changes how `push` should be built — fail-closed, verifying its own push before any
  subsequent step — rather than inheriting `plan_hoist`'s pattern of trusting an unverified stage;
- the separator fix and the fail-closed guard are the same edit surface.

The irony is worth recording: in this session the **non-compliant** hand-run push (space-separated)
worked, while the **compliant** path would have silently failed. Routing everything through the
skill is still right — but only once the skill's own machinery is correct, which is why #129
sequences before the routing work rather than after it.
