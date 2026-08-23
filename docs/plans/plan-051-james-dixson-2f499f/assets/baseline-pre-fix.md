---
type: Reference
okf_spec: OKF-PLAN
id: baseline-pre-fix
description: Pre-fix baseline figures (Issue 0.3), each re-measured with its verbatim pathspec
---

# Pre-fix baseline (Issue 0.3)

**Every figure here is RE-MEASURED, not inherited** (D-5). Each is recorded **with the verbatim
command that produced it**, because a figure without its pathspec is unreproducible rather than
merely imprecise — a pass-3 reconstruction of the corpus census returned **257** against
`plan.md`'s drafting literal of **251**, and EXP-003 never recorded its pathspec, so the
difference was unresolvable. Issue 4.2 quotes **this file**, never the drafting literals.

`<tree>` below is the plan's execution worktree, `.worktrees/plan-051-james-dixson-2f499f`.
`main` is the pre-plan baseline commit.

## 1. `Agent` occurrences across `agents/*.md` — expected 0

```bash
# from the tree root
ls skills/yf-plan/agents/*.md | wc -l          # → 7
cat skills/yf-plan/agents/*.md | grep -c Agent # → 0
```

| File | `grep -c Agent` |
| :-- | --: |
| `skills/yf-plan/agents/captor.md` | 0 |
| `skills/yf-plan/agents/coordinator.md` | 0 |
| `skills/yf-plan/agents/investigator.md` | 0 |
| `skills/yf-plan/agents/planner.md` | 0 |
| `skills/yf-plan/agents/reconciler.md` | 0 |
| `skills/yf-plan/agents/red-team.md` | 0 |
| `skills/yf-plan/agents/reviewer.md` | 0 |
| **Total across all 7** | **0** |

**7 files, 0 occurrences — #184's RED, confirmed by re-measurement.** This is also why
`ctl-184-dispatch` must be **section-scoped to `SKILL.md`'s `### Review`** rather than
whole-file: `Agent` appears at `SKILL.md:21` in the frontmatter `allowed-tools:` list, so a
whole-file `grep -q 'Agent' SKILL.md` exits **0 on the un-fixed tree** and ships unable to fail.

## 2. Sites carrying the literal `Read-only — never writes files`

**Re-grepped, not copied from the plan's list.**

```bash
# from the REPO ROOT — the pathspecs are repo-root-relative
git grep -n 'Read-only — never writes files' main -- ':!docs/plans' ':!docs/research'
```

| # | Site (at `main`, pre-plan) |
| --: | :-- |
| 1 | `skills/yf-plan/agents/red-team.md:63` |
| 2 | `skills/yf-plan/agents/reviewer.md:43` |
| 3 | `skills/yf-plan/spec/agents.md:73` (REQ-AGENT-043's `Verification:`) |
| 4 | `skills/yf-plan/spec/agents.md:97` (REQ-AGENT-045's `Verification:`) |

**Four sites — the plan's figure confirmed independently.** The same command run against the
worktree **after Issue 0.1** returns **2**: rows 3 and 4 are gone because 0.1 retargeted those
two `Verification:` lines to the executable command shape. That drop is the **SPEC-first
ordering visible in the data**, not a regression — and it is why 0.3 runs after 0.1 in the DAG
and re-greps rather than trusting a list.

## 3. Corpus `Verification:` census — six pathspecs, six different numbers

This is the figure that motivated the whole issue. **The number is meaningless without the
command**, so all six are recorded rather than one being presented as *the* answer.

| Id | Command (from the repo root) | Count |
| :-- | :-- | --: |
| **P1** | `git grep -h '^Verification:' -- '*.md' ':!docs/plans' ':!docs/research'` | **221** |
| P2 | `git grep -h '^Verification:'` | 221 |
| P3 | `git grep -oh 'Verification:' -- '*.md' ':!docs/plans' ':!docs/research'` | 347 |
| P4 | `git grep -oh 'Verification:'` | 487 |
| P5 | `grep -rn 'Verification:' skills/` (**untracked files included**) | 256 |
| **P6** | **P1 evaluated at `main`** — the pre-plan baseline | **220** |

**P1 is this plan's declared census pathspec.** It counts *clauses* — one `Verification:` line
per REQ, at line start, in tracked markdown, with historical plan and research bundles excluded
as records rather than surfaces.

**The 251-vs-257 divergence is now explained rather than left open.** Neither figure is
reproducible under P1. P5 — the recursive `grep` that includes **untracked** files — returns
**256**, which is the family pass-3's reconstruction landed in; an untracked working-tree file
moves it by one or two between runs. That is precisely the instability `git grep` removes, and
it is the same class as SC4's `git grep`-not-`grep` requirement.

## 4. Executed `Verification:` clauses — and a correction to EXP-003's "1 of 251"

```bash
# from the repo root, at main
git grep -h '^Verification:' main -- '*.md' ':!docs/plans' ':!docs/research' \
  | grep -cE '^Verification: `[^`]*`$'      # → 0
```

**Under the definition this plan's SC8 and `ctl-165-executable` actually use — the whole line
is a single backticked command — the pre-plan corpus count is `0`, not `1`.**

EXP-003's "**1 of 251**" is true under a *different* definition: `REQ-CLI-006`'s clause names
`test_cli_enumeration.py`, that test is registered at `CHANGE-VALIDATION.md:80` as
`uv-yf-cli-enum`, and it is green — so the *loop closes*, even though the clause itself is
prose containing inline code spans rather than a runnable line. Both figures are correct under
their own definitions, and the disagreement is a **definitional** one, not an error in either.

This is recorded here because it sharpens Issue 3.1's honesty note rather than softening it:
the three lines this plan lands are the corpus's **first** whole-line-executable `Verification:`
clauses, and the precedent EXP-003 found is a precedent for *closing the loop*, not for the
line shape. `test_cli_enumeration.py` remains the template Issue 3.2 follows verbatim.
