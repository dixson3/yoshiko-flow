---
type: Finding
okf_spec: OKF-PLAN
---
# Experiment 2: What machinery exists, and what `closable` can actually detect

**Questions.** (a) Does implementing `upstream.py push` require new execution capability, or can
it reuse what `hoist` already does? (b) With the per-bead-only signal chosen for `closable`, what
does it actually catch?

## (a) The executor already exists — `push` is a factoring-out

An initial read suggested `upstream.py` only *emits* command strings and never runs them, which
would have made #106 a much larger job. That is wrong. The verified structure:

```python
def plan_hoist(bead_ids, dest, *, backend, gran) -> list[str]:
    """Build the EXACT command sequence a hoist would run (no execution).
       ALWAYS emits the dry-run [push] first…"""

def cmd_hoist(issues_csv, dest, backend, apply) -> int:
    cmds = plan_hoist(ids, dest, backend=backend, gran=gran)
    for c in cmds: print(f"  {c}")
    if not apply:
        print("\nDry run. Re-run with --apply to execute the sequence above.")
        return 0
    for c in cmds:
        print(f"+ {c}")
        run(["bash", "-c", c])          # ← real execution
```

So the pattern is already established and proven: a **pure planner** (`plan_hoist`,
fixture-testable with no live `bd`) plus a **thin executor** (`cmd_hoist --apply`). Inline auth is
already table-driven:

```python
BACKEND_AUTH = {"github": ("gh", "GITHUB_TOKEN"), "gitlab": ("glab", "GITLAB_TOKEN")}
DEFAULT_BACKEND = "github"
```

`upstream.py push` is therefore `plan_push()` + `cmd_push()` mirroring that pair — the dry-run
-first ordering (REQ-SAFE-001) and the never-bare-`sync` scoping come free by construction, which
is the actual point: the invariant stops being prose the reader must honor and becomes a property
of the only code path that exists.

**Correction recorded:** an earlier reading of this plan's scope claimed the executor was missing.
It is not. Scope shrinks accordingly.

## (b) `closable` with the per-bead signal: what it catches, and what it misses

**Chosen signal (operator decision):** an upstream issue is closable when *every bead carrying an
`External:` mapping to it is closed*. Rejected alternatives were reading `yf-plan`'s configurable
`plans-root` (couples two skills; recreates the two-readers-disagree class of bug #100 existed to
fix) and taking the plan root as a CLI arg (caller must know it; silent nothing on a wrong path).

**What it catches.** Any issue created by this skill's own push/hoist path, because those record
`External:` on the bead. That includes all 11 backlog issues pushed as #118–#128, and every
future `granular` hoist.

**What it misses — stated plainly.** The four cases that *motivated* #117 are
`gh issue create`-filed coarse plan trackers:

| Tracker | Plan | Filed by |
|:--|:--|:--|
| #103 | plan-036 | `yf-plan` Phase 4.5, hand-filed |
| #95 | plan-032 | ditto |
| #96 | plan-033 | ditto |
| #98 | plan-034 | ditto |

`yf-plan` §4.5 files these directly with `gh issue create`; **no bead ever carries an `External:`
mapping to them.** So the per-bead signal cannot see them, and `closable` would not have surfaced
any of the four sweeps that produced this issue.

This is a real limitation of the chosen design, not an oversight — it is the price of zero
coupling. The plan must not claim #117 is fully closed by it.

## The cheap fix that would close the gap (out of scope here)

The per-bead signal *would* catch coarse trackers if the tracker URL were recorded on the plan's
epic bead. `yf-plan` already knows both halves at §4.5: it has the epic id (`record-epic`) and it
creates the issue. One `bd update <epic> --external-ref <url>` would make every future coarse
tracker detectable by the per-bead rule — **with no coupling**, because the mapping travels on the
bead rather than requiring `upstream.py` to read plan files.

That is a `yf-plan` change, not a `yf-beads-upstream` one, so it belongs in its own issue. Filing
it is in scope; implementing it is not. Without it, `closable` is forward-looking only: it will
catch granular pushes and future mapped trackers, and the existing four remain human-swept.
