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

## Findings

**F1 — Neither `ls-files` nor `--others --exclude-standard` is ever correct alone.** They are exact
complements partitioned by tracked-ness: 2 and 2 against a true answer of 4, in *both* the control
and the `-C` case. **The operator's hypothesis is confirmed on this point.**

**F2 — The union hypothesis is REFUTED for the cross-checkout case.** The operator proposed the
union as *"the only candidate that survived both states"*, and asked for it to be proven or refuted
rather than adopted. Measured: the union is correct **within a repository** (A: 4, C: 4) and returns
**0** from the primary cwd across the gitignore boundary (B). It survived both *tracked-ness* states
and does not survive the *cwd* dimension. **Correct per-repo, not correct per-question.**

**F3 — `git ls-files --cached --others --exclude-standard` is a single-command union** and is
exactly as good as the two-call form (4 in A and C, 0 in B). It should be preferred for being
atomic — a two-call union can drift when only one call is updated.

**F4 — A scoped directory listing is the ONLY candidate correct from both cwds.** `find` returns 4
in A, B and C, and 41 on the live repo from the primary checkout. **It is the only tool that crosses
the gitignore boundary at all.**

**F5 — `status --porcelain=v2 --ignored` is a trap, not a fallback.** It is the one git command that
returns non-zero from the primary cwd (**1**), and that 1 is the ignored **directory**, not its four
files. A caller checking "did I get a non-empty result" reads success and enumerates nothing —
#263's two-facts-one-signal shape, in the candidate a reader is most likely to reach for after the
others return 0.

## The prescription this spike supports

For a **presence-on-disk** fact:

1. **A scoped directory listing** — the only tool correct from either cwd, and the only one that
   works across the gitignore boundary; **or**
2. **`git -C <that worktree> ls-files --cached --others --exclude-standard`** — correct, atomic, and
   preferable when git's own ignore semantics are wanted, but **only when run inside a repository
   where the path is not ignored**.

Never `ls-files` alone, never `--others` alone, never either from a checkout that ignores the path,
and never `status --porcelain=v2 --ignored` as a fallback.

## Residue

None. The fixture was removed (`rm -rf`) at the end of the run.
