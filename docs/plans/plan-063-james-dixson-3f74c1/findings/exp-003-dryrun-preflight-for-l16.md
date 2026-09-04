---
type: Finding
okf_spec: OKF-PLAN
description: 'Designs the dry-run preflight for L16 and finds TWO UNFILED defects on the same line. HEADLINE (E): L16 has a FALSE PASS — git commit -m commits the whole index, not just what git add -- <plan_dir> staged, so a pre-staged unrelated file is committed under the plan message, pushed to origin/main, and reported clean because L16 removed the evidence. Also (F): the journal filter is a substring match that does not cover land-beads.json or a collapsed `?? .yf/`. Also: worktree_dirty observes the WRONG TREE, and resolvable_by_agent is written in 5 places and read in none.'
---
# EXP-003 — What should `--dry-run` assert so L16's conditions land before the boundary?

**Question.** How do we catch #341 and #333 before the irreversible boundary?

## Approach Tested

Read L16, `_land_manifest`, `_worktree_dirty`, `_worktree_path`, `LandingContext`, `land_cmd`,
`_land_digest`, L7, the close chain, L18, `agents/lander.md` and `spec/landing.md` §6–§9. Then a
sandbox repo with a bare `origin` and a plan bundle, driving the **real**
`_land_l16_commit_and_push_two` under six scenarios against a prototype of the proposed facts.

## Result

### HEADLINE (E) — an UNFILED false pass, worse than either filed defect

`git commit -m` commits the **whole index**, not just what `git add -- <plan_dir>` staged.
Measured:

```
porcelain before L16: 'M docs/plans/plan-999-x/plan.md\nM  other.txt'
REAL L16 verdict: pass
files in the commit L16 made: … plan.md | other.txt
```

**An unrelated pre-staged file was committed under the plan's commit message, pushed to
`origin/main`, and L16 reported clean** — the porcelain check cannot see it because *L16 itself
removed the evidence*. No dry-run halt fixes this: it is a defect in L16's **commit**, not in its
check. Fix: path-scope the commit (`git commit -o -- <plan_dir>`) to match the `add`.

### (F) — the journal filter is decorative here and inoperative elsewhere

`LAND_JOURNAL_DIR = ".yf/plan/landing-journal"` is matched as a **substring** of a porcelain
line. L13 writes a **sibling**, `.yf/plan/land-beads.json`, which the filter does not cover. And
git collapses untracked directories, so in a repo without the `/.yf/` anchor the line is `?? .yf/`
— which contains neither path. Measured:

```
porcelain: '?? .yf/'   REAL L16 verdict: fail
```

**The anchor is the only thing saving this repo.** A prefix filter also requires
`git status --porcelain -uall`, or the collapse defeats it.

### Q1 — what L16 rejects, and what `--dry-run` sees

`--dry-run`'s halt set is exactly five codes, **none about the working tree, index, remote or
committer identity**.

| L16 rejection | Seen by dry-run? | Pre-boundary? |
| :-- | :-- | :-- |
| `git add` non-zero | no | no |
| `git commit` non-zero | no | effectively yes — L4 commits first |
| push rejected | no | effectively yes — L6 pushes first |
| **whole-repo porcelain non-empty** | **no** | **NO — the only genuinely post-boundary-only condition** |
| `unpushed != 0` | no | no |

**Condition 4 is the whole exposure**, and #341 and #333 are two instances of it. Also noted:
`unpushed = … or "0"` launders an unresolvable `origin/<target>` into a pass.

### Q2 — `worktree_dirty` observes the WRONG TREE

Measured on a demonstrably clean linked worktree:

```
_worktree_dirty(wt)           = (False, [])
SHIPPED bool(_worktree_dirty) = True     <- CLEAN worktree reported DIRTY
after dirtying it, SHIPPED    = True     <- same answer. The field is CONSTANT.
```

The type bug is the shallower half. **L16 runs `git status` in `ctx.root`; the field observes
`.worktrees/<plan-id>` — a different checkout, and one `/.worktrees/` gitignores out of the
primary's porcelain entirely.** Even correctly typed, it would predict nothing about L16.

Recommended shape — both trees, three-valued on the worktree:

| Field | Value | Answers |
| :-- | :-- | :-- |
| `execute_worktree_present` | bool | — |
| `execute_worktree_dirty` | `true \| false \| null` | work L18's `worktree remove` would destroy |
| `primary_checkout_dirty_outside_plan_dir` | bool | **the fact L16 gates on** |
| `primary_checkout_staged_outside_plan_dir` | bool | defect (E) |

`null` is required: under in-place execution there is no worktree, and `false` there asserts
"clean" about a tree that does not exist — the same category error as the shipped `else False`.

**Keep the facts BOOLEAN; put path lists in `halts`.** `_land_digest` covers `facts` only, so a
path list would churn the digest on unrelated edits, while a boolean is stable at `false`. This
also makes dirt appearing *between* dry-run and apply a digest MISMATCH under existing
REQ-LAND-018 machinery — no new mechanism.

### Q3 — #333 needs (a) + (c); (b) is wrong

**(b) "L16 tolerates the decision file" is unworkable** — the only mechanism is a path exemption,
and the decision path is operator-supplied and arbitrary: `--apply /path/to/repo` would exempt
the whole tree.

**(c)** `_land_apply_command` currently emits the literal `<decision.json>` — a
repo-relative-*looking* placeholder that **invites** this failure. Default it to
`${TMPDIR:-/tmp}/<plan-id>-decision.json`. Necessary, but a suggestion, not a control.

**(a)** is the enforcement: refuse a decision path inside the work tree, beside
`_land_assert_primary_checkout`, **before the tty gate**, so a refusal is never preceded by a
write.

**It must cover more than the decision file.** `lander.md:88,96` emits `body_path` values as bare
`"<path>"` with **no guidance on where they live**, and L7 reads them. Same hazard, arriving
later with no `apply_command` to fix it. Add containment to `_land_validate_decision` too.

### Q4 — halt, not field

The objection *"a halt would block a landing for an unrelated file"* is not an objection —
**L16 blocks that landing regardless.** The choice is *where*: a dry-run halt costs one `git
stash`; the L16 failure costs a landing wedged at `L_CLOSED` with comments posted, issues closed,
beads closed and `status: complete` written — the state plan-062 measured, whose recovery
contract is explicitly *"retry-after-rebase, NEVER REVERT"*. **A halt strictly dominates.**

Scope it to **outside the plan folder** — dirt inside it is what `git add -- <plan_dir>` is for.

**Absence finding: `resolvable_by_agent` is written in five places and read in NONE.** No
consumer in `plan_manager.py`, `SKILL.md` or `lander.md`. Adding the first `true` to a dead field
changes no behaviour.

### Q5 — the spike agrees with the real L16 on all three scenarios

```
A clean            -> proposed halt: None                      REAL L16: pass
B unrelated dirty  -> proposed halt: primary-checkout-dirty    REAL L16: fail  'M other.txt'
C decision in tree -> proposed: decision-inside-work-tree      REAL L16: fail  '?? decision.json'
```

Halts exactly where L16 fails, silent where it passes. **#333 is caught twice** — the second is
what makes it a *legible* refusal rather than a generic dirt report.

## Implications for Plan

**The scope is larger than #341 + #333.** Four defects sit on the same line: the constant field
(#341), the in-tree residue (#333), the **pre-staged false pass (E, unfiled)** and the
**journal filter (F, unfiled)**. **E is the most serious and is not fixed by any dry-run halt.**

## Recommendations

1. **SPEC first.** A `REQ-LAND-024`-family addition for the dry-run halt, plus an amendment to
   `REQ-LAND-020` so L16's commit is **path-scoped** and its post-condition uses `-uall` with a
   prefix-based `.yf/plan/` exemption.
2. **#341:** replace the field with the four in Q2. Renaming is mandatory, not cosmetic —
   `worktree_dirty` names the tree L16 does not check.
3. **#333:** ship (a) and (c); extend containment over every `body_path`.
4. **File E and F** before designing around them.
5. **Give `resolvable_by_agent` a consumer, or drop it.**
6. Test at Tier 1 by driving L16 directly against a sandbox repo with an injected `origin` — the
   spike did exactly that in ~120 lines with no network, and every finding here came from it.
