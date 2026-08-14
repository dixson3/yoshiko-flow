---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #129: yf-beads-upstream: plan_hoist emits COMMA-separated ids that bd matches to ZERO beads — multi-bead hoist/land tombstones beads it never pushed

- **Number:** 129
- **Title:** yf-beads-upstream: plan_hoist emits COMMA-separated ids that bd matches to ZERO beads — multi-bead hoist/land tombstones beads it never pushed
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/129
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`plan_hoist()` builds its push command with **comma-separated** bead ids. `bd <backend> push` takes **space-separated** positional ids. The comma form matches **zero** beads and exits **0**, so the push silently no-ops — and `plan_hoist` then proceeds to close every bead locally with a tombstone claiming it was hoisted upstream.

**Multi-bead `hoist --apply` and `land --apply` can therefore tombstone beads that were never pushed anywhere.** Single-bead hoist is unaffected (a 1-element join contains no comma).

## Root cause

`skills/yf-beads-upstream/scripts/upstream.py`, `plan_hoist()`:

```python
ids_csv = ",".join(bead_ids)
...
cmds.append(f"{auth} bd {backend} push {ids_csv} --dry-run")
cmds.append(f"{auth} bd {backend} push {ids_csv}")
reason = close_reason(dest)
for bid in bead_ids:
    cmds.append(f'bd close {bid} -r "{reason}"')
```

`SKILL.md` itself documents the correct form — `bd github push <id1> <id2> …` (space-separated) — so the helper and the prose disagree.

## Repro (bd 1.1.2, live repo)

```
$ bd github push yf-m78m --dry-run
Dry run mode - no changes will be made
✓ Pushed 1 issues

$ bd github push yf-m78m yf-252c --dry-run          # space-separated
Dry run mode - no changes will be made
✓ Pushed 2 issues

$ bd github push yf-m78m,yf-252c --dry-run          # comma-separated (what plan_hoist emits)
Dry run mode - no changes will be made

$ bd github push yf-m78m,yf-252c --dry-run >/dev/null 2>&1; echo $?
0
```

Note the comma form prints **no `✓ Pushed N issues` line at all** — zero beads matched — and still exits **0**. There is no error, no warning, and no non-zero status for a caller to branch on.

## Impact

`cmd_hoist(--apply)` and `cmd_land(--apply)` execute the sequence with `run(["bash","-c",c])` and do not inspect exit codes (there are none to inspect — everything succeeds). For a multi-bead hoist the realized behavior is:

1. dry-run push → matches nothing, exit 0
2. real push → matches nothing, exit 0
3. `bd close <bead> -r "hoisted upstream to <dest> (reversible tombstone; un-hoist to restore)"` for **every** bead

So the beads are removed from the local worklist, marked as hoisted, and **no upstream issue exists**. The tombstone's own text asserts something untrue.

Blast radius — `plan_hoist` has three call sites: `upstream.py:709` and `:729` (`cmd_land` propose and apply) and `:750` (`cmd_hoist`).

Recoverable via `unhoist` (the tombstone is reversible by design, which is the saving grace), but only if someone notices — and nothing surfaces it. The failure is indistinguishable from success in the output.

## Why it was not caught

The existing fixture tests assert the *shape* of the emitted command sequence, not that the emitted command actually matches beads in `bd`. A test comparing `plan_hoist()` output against an expected string with commas in it will happily pass while encoding the defect.

## Requested change

1. Emit **space-separated** ids in `plan_hoist()` (match `SKILL.md` and the verified CLI contract).
2. Add a regression test asserting the emitted push command uses space separation — and ideally one that fails if a comma appears between ids.
3. Make the hoist/land sequence **fail-closed**: if the push step does not report the expected number of pushed issues, do **not** proceed to the local closes. Step 3 should never run on an unverified push.
4. Audit the other emitted-command builders for the same separator assumption.

## Refs

Found while red-teaming plan-038 (which adds a `push` verb and routes SKILL.md through it) — specifically while verifying the premise that `hoist` does not already cover the plain-push case. It does not: `hoist` = push **plus local close**, which is exactly what makes this bug destructive rather than merely ineffective.
