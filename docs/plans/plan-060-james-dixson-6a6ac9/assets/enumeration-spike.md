---
type: Reference
okf_spec: OKF-PLAN
description: 'EXP-007 — the enumeration spike. Every candidate enumeration run against a fixture holding tracked and untracked files both inside and outside a gitignored worktree, from both cwds, against a known true answer. Refutes the union hypothesis for the cross-checkout case.'
---
# EXP-007: The enumeration spike

**Why this exists.** The enumeration prescription was wrong in **five consecutive review rounds**,
and every fix was prose-reasoned. Each looked like a correction and was a lateral move. This is the
`AGENTS.md` sandbox-spike carve-out applied deliberately: *"Prefer a spike whenever a claim is
cheaper to test than to reason about"* — the plan-049 precedent, where a pass-4 spike caught a
specification defect four prose-only passes had read past.

**A fixture can hold both states at once; the live repository can only ever be in one.** That is
what made five rounds of measurement against the live repo insufficient — each round measured a
true fact about a transient state and generalised it.

## Method

A throwaway git repo in `$(mktemp -d)`, removed afterwards, with `/.worktrees/` gitignored:

- **`ctl`** — a bundle in the **primary** checkout: 2 tracked + 2 untracked files. **TRUE = 4.**
- **`sub`** — a bundle inside a **gitignored worktree**: 2 tracked + 2 untracked files. **TRUE = 4.**

Every candidate was run against each, from the **primary cwd** and via **`git -C <worktree>`**, and
the row count compared against the known answer.

## Results

### A — control bundle (primary checkout, not gitignored), from the primary cwd

| Candidate | Count | vs TRUE = 4 |
| :-- | --: | :-- |
| `ls-files` | 2 | **wrong** — tracked only |
| `ls-files --others --exclude-standard` | 2 | **wrong** — untracked only |
| union of the two | 4 | correct |
| **`ls-files --cached --others --exclude-standard`** | **4** | **correct, single command** |
| `status --porcelain=v2` | 2 | **wrong** — reports changed/untracked, not contents |
| `find -type f` | 4 | correct |

### B — subject bundle (inside the gitignored worktree), from the PRIMARY cwd

| Candidate | Count | vs TRUE = 4 |
| :-- | --: | :-- |
| `ls-files` | **0** | wrong |
| `ls-files --others --exclude-standard` | **0** | wrong |
| **union of the two** | **0** | **wrong — this refutes the union hypothesis** |
| `ls-files --cached --others --exclude-standard` | **0** | wrong |
| `ls-files --others` (no `--exclude-standard`) | **0** | wrong |
| `status --porcelain=v2` | **0** | wrong |
| `status --porcelain=v2 --ignored` | **1** | wrong — and *deceptively* so: it reports the ignored **directory**, not its four files |
| `ls-files --recurse-submodules` | **0** | wrong |
| **`find -type f`** | **4** | **correct — the only candidate that works here** |

### C — subject bundle, via `git -C <worktree>`

| Candidate | Count | vs TRUE = 4 |
| :-- | --: | :-- |
| `ls-files` | 2 | wrong — tracked only |
| `ls-files --others --exclude-standard` | 2 | wrong — untracked only |
| union of the two | 4 | correct |
| **`ls-files --cached --others --exclude-standard`** | **4** | **correct, single command** |
| `status --porcelain=v2` | 2 | wrong |
| `find -type f` | 4 | correct |

### Confirmed against the live repository

Same shape, on this plan's own bundle (now fully committed, TRUE = 41 on disk):

```console
# from the PRIMARY cwd, path through the gitignored worktree
ls-files --cached --others --exclude-standard  -> 0
union (two calls)                              -> 0
find -type f                                   -> 41

# via git -C <worktree>
ls-files --cached --others --exclude-standard  -> 41
ls-files only                                  -> 41     # all 41 are tracked NOW
--others --exclude-standard only               -> 0      # ... and none untracked NOW
```

The last two lines are the state-dependence in one frame: **the same two commands that read
`0 / 39` before the mid-review commit read `41 / 0` after it.**

## CORRECTION (red-team pass 7): the CAUSE was mis-attributed

> Pass 7 rebuilt this fixture independently, reproduced **all 18 rows**, and then ran three cases
> this spike did not. **The counts were right and the causal story was wrong**, which is the more
> dangerous kind of error and exactly the class (#263) this plan exists to close — recurring inside
> the artifact commissioned to close it.

### Case D — the worktree is NOT gitignored at all

| Candidate (from the primary cwd) | Count | TRUE = 4 |
| :-- | --: | :-- |
| `ls-files` | 0 | wrong |
| `ls-files --others --exclude-standard` | 0 | wrong |
| `ls-files --cached --others --exclude-standard` | 0 | wrong |
| `status --porcelain=v2` | 0 | wrong |
| `status --porcelain=v2 --ignored=matching` | 0 | wrong |
| `ls-files --others --ignored --exclude-standard` | 0 | wrong |
| `find -type f` | 4 | correct |

`git check-ignore wt` -> **NO**. **With gitignore entirely out of the picture, every git candidate
still returns nothing.**

### Case E — a PLAIN gitignored directory, no worktree, no `.git` marker

| Candidate (from the primary cwd) | Count | TRUE = 2 |
| :-- | --: | :-- |
| `ls-files --others --exclude-standard` | 0 | wrong |
| **`ls-files --others --ignored --exclude-standard`** | **2** | **correct** |
| `find -type f` | 2 | correct |

**So git CAN cross a gitignore boundary.** It cannot cross a **checkout** boundary.

### The corrected mechanism

The real cause is **nested-repo opacity**, confirmed at the byte level: a linked worktree's `.git` is an
**88-byte ASCII FILE, not a directory** — `gitdir: /…/.git/worktrees/plan-060-development` — and git treats
that marker as a **nested-repo boundary**, which is opaque *regardless of gitignore*. That is precisely why
un-ignoring the path (case D) changes nothing. **Gitignore is a second,
independent reason** that happens to apply in this repository. Two facts, one observed signal.

**What this falsifies in the original write-up:** F4's *"the only tool that crosses the gitignore
boundary at all"* is **false** (case E), and the applicability condition *"only when run inside a
repository where the path is not ignored"* **mispredicts** — un-ignoring the path fixes nothing
(case D). A maintainer acting on that reading during Epic 1 would conclude a constraint had
dissolved when it had not.

### Case F — `find -type f` is wrong in BOTH directions

A bundle with one tracked `a.md`, a **symlink** `link.md`, and an ignored `.DS_Store`:

| Candidate | Count | Correct? |
| :-- | --: | :-- |
| `find -type f` | 2 | **wrong twice** — misses the symlink, counts the `.DS_Store` |
| `find ! -type d` | 3 | catches the symlink, still counts the `.DS_Store` |
| **`git -C wt ls-files -co --exclude-standard`** | **2** | **correct** — `a.md` + `link.md`, junk excluded |

`.DS_Store` is near-certain on macOS in any directory opened in Finder, so this is not a contrived
case.

## Findings (as corrected)

**F1 — Neither `ls-files` nor `--others --exclude-standard` is ever correct alone.** Exact
complements partitioned by tracked-ness: 2 and 2 against 4, in both the control and the `-C` case.
**Confirmed and unchanged.**

**F2 — The union is correct WITHIN a checkout and returns 0 ACROSS one.** The operator's hypothesis
survives tracked-ness and not the checkout dimension. **Confirmed; only the stated cause changes.**

**F3 — `git ls-files --cached --others --exclude-standard` is a correct single-command union**, and
is preferable to two calls for being atomic. **Confirmed.**

**F4 — CORRECTED.** A scoped listing is the only candidate correct from both cwds *among those
measured* — but the boundary it crosses is the **checkout** boundary, not the gitignore boundary
(case E), and it is **not** reliably correct even then (case F).

**F5 — `status --porcelain=v2 --ignored` is a trap, and pass 7 made it stronger.** It returns **1**
from the primary cwd — the ignored *directory*, not its files. Pass 7 measured that the two
candidates an implementer reaches for next — `--ignored=matching` (the documented fix for
directory-collapsing) and `ls-files --others --ignored --exclude-standard` — **also return 1** in
the worktree case. **The trap survives its own documented workaround.**

## The prescription this spike supports

For a **presence** fact about a bundle inside a **linked worktree**:

1. **Preferred — `git -C <that worktree> ls-files --cached --others --exclude-standard`.** Correct,
   atomic, handles symlinks as git does, and excludes ignored junk (case F). It must run **inside
   that worktree's checkout**; from the primary checkout it returns 0 regardless of gitignore.
2. **Fallback, when the process cannot run inside that checkout — an explicit scoped listing**,
   written as `find <dir> ! -type d` (never `-type f`, which drops symlinks). Accept that it counts
   ignored junk, and filter deliberately if that matters.

**The two branches answer different questions and the choice must be deliberate:** the listing
answers *"what is on disk"*; the `git -C` form answers *"what git considers part of the tree"*. For
`upstream.rows[].draft_present` the second is the wanted question — a `.DS_Store` is not a draft.

Never `ls-files` alone, never `--others` alone, never any git form from a **different checkout**,
and never `status --porcelain=v2 --ignored` (or `--ignored=matching`) as a fallback.

## Scope limits, stated

- **`--recurse-submodules` was listed as a candidate against a fixture containing no submodule.**
  That row measures nested-repo opacity like every other, not submodule behaviour. It is retained
  only as a negative result about the worktree case and claims nothing about submodules.
- **`core.excludesFile` (global gitignore) is untested.** It is immaterial to the listing branch and
  material to the `git -C` branch, where `--exclude-standard` honours it — so a user's global
  `.DS_Store` or `*.local` pattern participates in what branch 1 returns.

## Residue

None. Both fixtures were removed (`rm -rf`) at the end of their runs.
