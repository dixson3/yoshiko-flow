---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-bd-subdag-loop
description: Can bd 1.1.2 express the start-gate -> stage -> exit-gate sub-DAG with a bounded, non-resettable loop?
---

# EXP-001 — the sub-DAG loop is expressible, but the gate is NOT a verification primitive

**Verdict: EXPRESSIBLE IN A MODIFIED FORM — and the design's central claim is REFUTED.**

Measured against three throwaway `bd init` repos, never this repo's `.beads/`.

## 1. The refutation, first — because it changes what #198 may claim

The [#198 comment](https://github.com/dixson3/yoshiko-flow/issues/198) argues the core move
"converts a **claim** into a **process with an exit code**" and that "the parent structurally
cannot fabricate the verdict".

**The second half does not hold.** `bd` records **no resolver identity for any gate
resolution**. Independently re-measured by the main session, not taken from the investigator:

```bash
BEADS_ACTOR=my-script bd gate resolve vfy-i3e --actor "conform_stage.py" --reason "auto-resolved by script"
bd show vfy-i3e --json
#   await_type   = 'human'
#   close_reason = 'auto-resolved by script'
#   closed_at    = '2026-08-24T14:18:22Z'
#   created_by   = 'James Dixson'
```

`--actor` is a **documented global flag** (`Actor name for audit trail`) and `BEADS_ACTOR` is
its documented env form. **Both vanish.** There is no `closed_by`, no `resolved_by`. `bd
history` attributes every entry to the Dolt commit author (`root`).

**Consequence.** A stage script that skips the child entirely and calls
`bd gate resolve --reason "exit test passed"` produces a database state **byte-identical** to
one that did the work. The structural guarantee is not in the gate — it is in **the file the
child wrote**, and only if something independent later re-reads that file.

**A gate is a stall point and a legible record. It is not a verification primitive.** #198's §2
must be corrected before this plan builds on it.

`bd audit record` (append-only `.beads/interactions.jsonl`) is the only real provenance channel,
and nothing about `bd gate resolve` writes to it — a stage script must call it explicitly.

## 2. Gate types — three functional, one dead, and an unvalidated free-text field

| Claim | Measured |
| :-- | :-- |
| Five types (`human`, `timer`, `gh:run`, `gh:pr`, `bead`) | `bd gate --help` says five; **`bd gate create --help` lists only four**, omitting `bead`. bd's two help texts disagree |
| No type runs a shell command | **CONFIRMED.** Every self-resolving type polls something bd knows how to poll (wall clock, GitHub API). None executes a command; none reads the filesystem |
| `bead` type works | **REFUTED** — `cross-rig bead gate cannot be checked (multi-rig routing removed)` in 1.1.2 |

**`--type` is not validated.** All ten probed values were accepted with exit 0, including
`shell`, `exec` and the deliberate junk `nonsense`, persisted verbatim as `await_type`. An
unknown type behaves exactly like `human`: it blocks readiness and is only closable by
`bd gate resolve`. `bd gate check` ignores unknown types entirely (`Checked 0 gates`).

**This is usable, and it is the one place the design gets *better* than proposed.** A custom
`--type=exit:conform` is strictly more honest than mislabelling a script-resolved gate `human`
— but per §1 it remains a **label**, not a guarantee.

## 3. Q2 / Q5 / Q6 — the mechanical answers

- **`bd gate create --blocks <id>` is ad-hoc and scriptable — CONFIRMED.** No formula, no wisp,
  no pour. `bd gate resolve` closes it and the blocked bead enters `bd ready` in the same run.
- **Cycle checking is unconditional — CONFIRMED, and stronger than the design assumed.** A 3-node
  loop is refused; a self-edge is refused. `--no-cycle-check` **still refuses on the single-edge
  path**, which its own flag text (`Skip per-edge cycle checks for speed`) does not lead you to
  expect. The bulk `--file` path documents a final whole-graph check and performs one. Net:
  **do not plan on `--no-cycle-check`** — the loop cannot be an edge.
- **No gate can read the filesystem.** There is no gate hook, watcher-command, or config key;
  `bd gate add-waiter` is a wake-notification registry, not a predicate. **The script must decide
  externally, then resolve.**

## 4. D-2 is VINDICATED by measurement

The bound-bite spike (`MAX=2`, exit test rigged never to pass):

```
[conform] pass 1 … pass 2 … BOUND HIT at pass 3 (max 2) -> refuse   rc=2
[redteam] BOUND HIT at pass 3 (max 2) -> refuse                     rc=2
```

`len(glob('reviews/pass-*.md'))` read fresh from disk each iteration was **monotonic across
stage boundaries** — redteam refused immediately because conform's two files were still on disk
— and **no bead held the counter**, so burning every bead in the sandbox would not have reset
it. Nothing in the gate model tempts the counter back inward, because no gate can read the
filesystem anyway.

## 5. Design corrections this finding forces

| # | Correction | Basis |
| :-- | :-- | :-- |
| C-1 | **#198 may NOT claim the gate makes a verdict unfabricatable.** State that bd records no resolver identity, so a resolution's audit value is exactly the honesty of its `close_reason` | §1, re-measured |
| C-2 | **One gate per stage, not `start-gate -> stage -> exit-gate`.** The previous stage's `blocks` edge *is* the start gate; a start-gate adds a node only the about-to-run script can resolve | spike |
| C-3 | **Use a custom `await_type`** (`exit:conform`), not `human` | §2 |
| C-4 | **The `dispatch -> record` sub-DAG is OBSERVABILITY, not control.** The spike closed both beads from one script with no dispatch check. What is load-bearing is that the exit test greps a file the child wrote | spike |
| C-5 | **On bound-hit, leave the exit gate OPEN and the stage bead unclosed.** The first spike closed the stage unconditionally, silently converting "bound exceeded" into "stage complete". Pair with `--timeout`, since custom-typed gates are invisible to `bd gate check` and will never be swept | spike |
