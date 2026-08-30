---
type: Reference
okf_spec: OKF-PLAN
description: 'Machine-readable registry of every re-measurable figure this bundle quotes, paired with the command that re-derives it. Read by scripts/checks/check-cited-figures.py (Issue 0.10, #289).'
---
# Cited-figure registry

**Why this file exists.** Red-team pass 1 found **three** figures in this plan's own text that had
drifted from the repository — the `_run_git` call-site count, two `SKILL.md` line numbers, and the
FULL-tier row count. A plan that cites measurements is the natural place to build the instrument
that re-checks them (`dixson3/yoshiko-flow#289`).

**A figure is only as good as the command that produced it.** During Issue 0.10 two ad-hoc
re-measurements of figures in this table came out **wrong** — `test_close_contract.py --list-steps`
piped through `grep -c .` returned **16** (it counts JSON lines, not steps) and a naive
`@cli\.command\(` regex returned **40** (it double-counts across the bare and named forms). Both
figures are correct at **12** and **39** when the *authoritative* command is used. That is exactly
the failure this registry removes: the command is recorded **with** the figure, so a re-measurement
cannot silently answer a different question.

## Registry

Each row is `<id> | <quoted value> | <command>`. The command shall print the value and **nothing
else** on stdout. `check-cited-figures.py` runs each under `bash -c` — the same shell
`recheck-criteria` uses — and diffs.

| id | quoted | command |
| :-- | --: | :-- |
| `run-git-call-sites` | 20 | `uv run scripts/checks/_figures.py run-git-call-sites` |
| `close-chain-steps` | 12 | `uv run scripts/checks/_figures.py close-chain-steps` |
| `cli-verbs` | 40 | `uv run scripts/checks/_figures.py cli-verbs` |
| `req-families` | 46 | `uv run scripts/checks/_figures.py req-families` |
| `herdr-schema-human` | 0 | `uv run scripts/checks/_figures.py herdr-schema-human` |
| `herdr-schema-attached` | 0 | `uv run scripts/checks/_figures.py herdr-schema-attached` |

**`cli-verbs` is 40, not 39, and the change is deliberate.** Epic 0 Issue 0.3 amended
`REQ-CLI-006`'s enumeration to add `land`, so the *spec* enumerates 40. The **source** carries 39
until Issue 1.6 registers the verb, and `test_cli_enumeration.py` is correspondingly RED across
that window — the SPEC-first ordering, recorded in `criteria-validation.md`. This row tracks the
**spec enumeration**, which is the figure the bundle quotes.

**`run-git-call-sites` is PINNED to `777c5be`, and the pin was forced by a measured drift.**
Gate G1's claim is that *"all 20 **existing** call sites of the `_run_git` helper are read-only or
worktree/branch operations"* — a statement about the repository **as it stood when the gate was
written**. Measured during Issue 1.8: unpinned, the same count reads **29** on the execute branch,
because plan-060's own Epic 1 added nine more (all of them reads — `merge-tree`, `rev-parse`,
`ls-tree`, `diff`, `rev-list`, `ls-files`). That is a **true drift of a false figure**: the claim
never was "this repository contains exactly 20 forever", and a live count of a helper that later
plans may legitimately call more of goes stale on every commit, which teaches its reader to ignore
it. The historical claim gets a historical measurement. An unreachable baseline (a shallow clone)
is **INCONCLUSIVE**, never a drift.

**`req-families` is 46, and the instrument is what corrected it.** `free-req-ids.md` records
**45**, measured against `main` *before* Epic 0. Issue 0.2 then created the `REQ-LAND-*` family, so
the post-Epic-0 tree carries **46**. The very first run of `check-cited-figures.py` reported this as
a drift — an instrument built for `#289` catching a figure inside its own plan on its first
execution, which is the behaviour the issue asks for. `free-req-ids.md` is a **dated snapshot** and
is not rewritten; a note there records the successor value.

**`herdr-schema-*` are ABSENCE figures and are the reason the instrument is three-valued.** They
underwrite `REQ-LAND-014`'s claim that "a pane herdr reports as human-attached" is not a capability
herdr has. On a machine with no `herdr` the command cannot run at all — which is **INCONCLUSIVE**,
not a drift, and must never be reported as a confirmed zero. An absence figure that reads 0 because
the instrument was missing is the worst possible false green.

## Running it during execution (the address-space caveat)

This registry is a **plan-folder** artifact and lives primary-side; `_figures.py` and
`check-cited-figures.py` are **code** and live on the execute branch. Until the landing merges
them into one tree they are in different address spaces, so during execution the instrument must
be run **from the worktree** with an **absolute path** to this registry:

```bash
cd .worktrees/<plan-id>
uv run scripts/checks/check-cited-figures.py "$PWD/../../docs/plans/<plan-id>/assets/cited-figures.md"
```

Running it the other way round — the worktree's script from the primary cwd — silently measures the
**pre-execution** tree, because `_figures.py` resolves its root with `git rev-parse --show-toplevel`
from the caller's cwd. That is not a hypothetical: it is how `req-families` would read 45 instead of
46. After the landing merges both halves onto the target this caveat disappears.

## Verdicts, all three proven by execution rather than asserted

| Case | Exit | Proven by |
| :-- | --: | :-- |
| every figure matches | 0 | the six-row run above |
| a figure drifted | 1 | a sandbox copy with `run-git-call-sites` set to `999` |
| registry empty / below floor | 2 | a registry parsing to zero rows |
| **a `0`-quoted absence figure whose instrument could not run** | **`inconclusive`, not `drift`, not `match`** | a row whose command exits 2 — reported separately and explicitly *"NOT counted as matching"* |
| every figure inconclusive | 2 | a single-row registry whose only command exits 2 |

The fourth row is the one that matters most and is the reason the instrument is three-valued: for an
absence figure, a missing instrument and a genuine zero are indistinguishable from a bare exit code.
