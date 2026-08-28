---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #243: Successor to #154: harness tune OVERWRITES a pre-existing rules aggregate with no backup

- **Number:** 243
- **Title:** Successor to #154: harness tune OVERWRITES a pre-existing rules aggregate with no backup
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

**Successor to the closed #154**, covering the half that survived it.

#154 is closed, and correctly: its `--revert` half genuinely works — the `REQ-YF-TUNE-029`
sha256 guard fires, and as of v0.5.0 revert is additionally symlink-aware and will not unlink a
symlinked rule target. This issue is **not a reopen**. It files the *adjacent* loss that
#154's remedy did not reach, which EXP-006 measured while verifying that remedy.

## The surviving defect: the loss happens at TUNE, not at revert

`yf harness tune` **overwrites a pre-existing rules aggregate that `yf` did not author, with no
backup**. Revert's guard protects content yf wrote and recorded a sha for; it can do nothing
about content that was destroyed before any sha was ever recorded.

So the failure sequence is:

1. an operator has their own `YOSHIKO_FLOW.md` (or other rule target) — hand-written, or from
   another tool;
2. `yf harness tune` writes yf's aggregate over it. No backup is taken, and no sha of the
   *prior* content is recorded, because the manifest only records what yf wrote;
3. the content is unrecoverable. `--revert` cannot restore it — `REQ-YF-TUNE-029` says plainly
   that restoring content requires a real backup and deletion is not restoration, which is
   exactly why revert now *keeps* rather than deletes.

## Proposed remedy

Symmetry with what revert already does. `tune` should, before overwriting a rule target it did
not author:

- **refuse and report**, requiring an explicit flag — the `--allow-permissions-write` precedent
  from the config side; **or**
- **back it up** and record the backup path in the ownership manifest, which then gives
  `--revert` something real to restore.

Refusing is the safer default and matches `REQ-YF-TUNE-029`'s stated posture: the operator's
own content is never destroyed to make room for yf's.

## Evidence

`docs/plans/plan-054-james-dixson-535968/findings/exp-006-symlink-revert-spike.md` — six
sandbox spikes under a fake `HOME`, including a high-fidelity replica using the real
`AGENTS.md` files with every path rewritten to the sandbox.

Filed by plan-054 Issue 6.4.

