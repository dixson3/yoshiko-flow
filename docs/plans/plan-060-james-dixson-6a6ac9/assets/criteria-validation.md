---
type: Reference
okf_spec: OKF-PLAN
description: 'Execution record for every success criterion whose command exists today, run under `bash -c` — the shell recheck-criteria actually uses. Adopted as a standing rule after red-team pass 2 found two unsatisfiable criteria.'
---
# Criteria validation record

**The rule this record exists to satisfy:** *every criterion whose command exists TODAY is executed
once, under `bash -c`, before approval.* Adopted after red-team pass 2 found two criteria that could
never pass — one of them the criterion added to fix pass 1's vacuity finding.

**The shell is a COLUMN, not a footnote.** "Exit 0" without "under `bash -c`" is precisely the claim
that failed once in this plan, so the shell is recorded per row rather than asserted once in prose.

**Why `bash -c` and not the interactive shell.** `recheck-criteria` evaluates each clause via
`subprocess.run(["bash", "-c", cmd])`. Measured:

```console
$ bash -c 'command -v grep; grep --version | head -1'
/usr/bin/grep
grep (BSD grep, GNU compatible) 2.6.0-FreeBSD
```

The interactive shell here resolves `grep` to a **`ugrep` shell function**, which is **not exported
to `bash -c`**. A criterion validated interactively is validated in a shell that never runs it —
which is exactly how the unsatisfiable SC2b passed its own validation once.

## Results

Run 2026-08-29, from the repo root, after the pass-2 revision; extended after pass 3 flagged that the record omitted SC32 and miscounted the guard-routed set as 33 (pass 2's *test-backed* count, which included SC4 and SC33 running directly). The corrected figure was **31**; it became **32** when SC10b was added in the pass-3 revision. **This row has now gone stale twice** — it is a derived count in prose, which is the shape Issue 0.10's re-measurement instrument exists to catch.

| # | Shell | Verdict | Exit | Reading |
| :-- | :-- | :-- | --: | :-- |
| SC1 | `bash -c` | not-yet-true | 2 | **Genuine INCONCLUSIVE**, not an argument error: `check_amendment_log.py` does require `--plan`, and it reports *"SPEC.md has no amendment-log entry for plan-060"*. Becomes 0 when Epic 0 lands. |
| SC2 | `bash -c` | **PASS** | 0 | Positional form confirmed. Reports *"38 non-Epic-0 issue(s) … every non-Epic-0 issue is covered"*. The `--plan` form pass 2 flagged was an argparse error at exit 2. |
| SC2b | `bash -c` | **PASS** | 0/1 | Validated in BOTH directions in a sandbox: three fixture files all carrying the forwarding `__main__` -> exit 0; one broken -> exit 1. Against the live tree (the three files absent) -> exit 1, i.e. not-yet-true. The `\|` escaping is handled by `_recheck_unescape`. |
| SC4 | `bash -c` | **PASS** | 0 | `test_cli_enumeration.py` green on the unmodified tree. |
| SC13 | `bash -c` | not-yet-true | 1 | Correct: the `agents/lander.md` dispatch line does not exist until Issue 2.4. |
| SC33 | `bash -c` | **PASS** | 0 | `test_close_contract.py` green on the unmodified tree — the baseline the §6 rewrite must preserve. |
| SC32 | `bash -c` | not-yet-true | 2 | `--assert-invocation` exists today (`test_close_contract.py:428`) and reports *"'land' is not a registered plan_manager.py verb"*. Exit 2 is its unregistered-verb code, not an argument error. Becomes 0 when Issue 1.6 registers the verb. |
| SC34 | `bash -c` | not-yet-true | 1 | Correct: `SKILL.md` still carries the old expression until Issue 5.4. |
| SC37 | `bash -c` | not-yet-true | 2 | `assets/full-tier-record.md` does not exist until Issue 6.2. |

**Deliberately not run:** the **32** criteria routed through `check-pytest-ran.sh` against
`test_land_manifest.py` / `test_land_apply.py` / `test_lander_agent_contract.py`, and SC37's
`full-tier-record.md` — all name artifacts this plan creates. `check-pytest-ran.sh` returns **exit
2 (INCONCLUSIVE)** for a missing file and **exit 1** for a missing test, so neither is a vacuous
pass; a criterion naming a test that is never written fails loudly.

## Separately validated: SC2b's replacement

The unsatisfiable form and its replacement, both under `bash -c`:

```console
# OLD — grep -L changes OUTPUT, not exit status, on BSD and GNU grep
all three good  -> exit 0        # criterion demanded 1: UNSATISFIABLE
one file broken -> exit 0        # and cannot distinguish the two cases

# NEW — an explicit count comparison, implementation-independent
all three good  -> exit 0        # PASSES
one file broken -> exit 1        # FAILS
```

## The distinction this record is careful about

A criterion returning non-zero **today** is one of two different facts, and they are not
interchangeable:

- **not-yet-true** — it asserts post-implementation state (SC13, SC34) or depends on work Epic 0
  has not done (SC1). Expected, and it must become true as the plan executes.
- **unsatisfiable** — it can never return the value it demands, in any state of the world. SC2b and
  the retired SC30 were both this, and both were introduced *as fixes for earlier vacuity findings*.

Only the second is a defect. Collapsing them would reproduce, in this plan's own validation, the
two-facts-one-signal class it carries `#263 (partial)` for.

## The second manifestation: the shells see DIFFERENT FILE SETS

The divergence is not only in exit status. The interactive wrapper passes `--ignore-files`, so it
honours `.gitignore` — and `/.worktrees/` is gitignored. Measured, same pattern, same root, same
recursion, bounded with `--exclude-dir=.git --exclude-dir=target`:

```console
# a pattern that exists ONLY under .worktrees/ (the plan folder is not primary-side)
interactive, recursive from repo root : 0
bash -c,     recursive from repo root : 5

# scoped explicitly at .worktrees (control) — the shells agree
interactive, scoped : 5
bash -c,     scoped : 5

$ git check-ignore .worktrees
.worktrees                                  # IGNORED
```

**An interactive recursive grep cannot see this worktree at all, and returns a confident zero.**

### Why this is a design input, not just a validation caveat

An **absence assertion** — "no occurrences of X remain" — is the form most vulnerable to this, and a
landing preflight is largely absence assertions. Worse, `land` spans the **primary checkout and a
gitignored worktree by definition**: it merges *from* the ignored side. A content grep therefore
under-reports from exactly the tree the landing is about.

This is [#294](https://github.com/dixson3/yoshiko-flow/issues/294)'s class — gitignored paths and
enumeration — meeting the shell divergence above, and it is why **Issue 1.9** forbids recursive
content grep for enumeration and requires `git ls-files` / `git -C <worktree>` /
`git worktree list --porcelain` instead. **R13** carries the risk; **SC10b** tests it.

### Audit of this plan's own criteria against the trap

Verified: **no criterion in this plan uses `grep -r` or `grep -R`.** Every grep-based criterion
(SC2b, SC13, SC34, SC37) names explicit file paths, so all four read the same file set under either
shell. The exit-status divergence still applied to SC2b, which is why it was rewritten; the
visibility divergence never did.

**A caution for anything added later:** a recursive grep that is *bounded enough to finish* in the
interactive shell is also *narrow enough to be wrong*, and one that is broad enough to be right may
not finish — an unbounded `bash -c` recursive grep over this repo timed out at 120 s during this
very measurement. Neither failure mode announces itself.

## A third divergence: TRACKED-ness is not PRESENCE

Red-team pass 4 found that the fix for the previous two traded one blindness for another.
`git ls-files` lists the **index**, not the disk. Measured on this bundle, live:

```console
$ git ls-files docs/plans/plan-060-james-dixson-6a6ac9              # from the primary checkout
0
$ git -C .worktrees/plan-060-development ls-files <same path>       # from the worktree
0
$ git -C .worktrees/plan-060-development ls-files --others --exclude-standard <same path>
37
$ git -C .worktrees/plan-060-development status --porcelain <same path>
?? docs/plans/plan-060-james-dixson-6a6ac9/
```

**This plan's own bundle — 36 files when first measured, 37 by the next review pass — is invisible
to `git ls-files`.** (The figure drifts as review files are added; it is a derived count in prose,
which is why the count itself is not the claim.) And that is not an accident of
timing: **draft comment bodies are untracked BY CONSTRUCTION at `--dry-run` time**, because the
plan-folder writes are not committed until L16 — which is D-2's entire point.

**The cheapest possible fixture for SC10b is sitting in the repository right now**: an untracked
bundle inside a gitignored worktree, exercising both blindnesses at once.

### And a shell-INDEPENDENT reason, which is the one that reaches the Python path

The earlier two divergences both turned on the interactive `grep` wrapper, which
`subprocess.run(["bash","-c",…])` never sees. This one does reach it. Measured under
`/usr/bin/grep`:

```console
$ bash -c "grep -rl 'plan-001' --include='plan.md' docs/plans .worktrees" \
    | sed -E 's|^\.worktrees/[^/]+/||' | sort | uniq -d | wc -l
6
```

Six logical paths returned **twice** — once from the primary checkout, once from the worktree's
copy of the same file. So a recursive content grep is wrong for enumeration **even where the
wrapper cannot reach**, by over-counting rather than under-counting.

Three divergences, three directions: **under-report** (gitignore-blind), **under-report**
(tracked-blind), **over-report** (double-count). Only the first is a shell artifact.

## A fourth: the fix was itself gitignore-blind, and only in the PRIMARY checkout

Red-team pass 5 ran the prescribed commands rather than reading them, and found that **two of the
three tools prescribed for presence-on-disk return zero from the checkout `--apply` actually runs
in**. `--exclude-standard` *is* "honour `.gitignore`", and `git status` honours it too:

```console
# from the PRIMARY checkout, over a bundle under the gitignored .worktrees/
$ git ls-files --others --exclude-standard .worktrees      -> 0
$ git status --porcelain=v2 -- .worktrees                  -> 0
$ git ls-files --others .worktrees                         -> 1   (the dir, not recursed)

# from a repository in which the path is NOT ignored
$ git -C .worktrees/plan-060-development ls-files --others --exclude-standard <bundle>  -> 37

# or a non-git scoped listing, from either side
$ find <bundle> -type f | wc -l                            -> 37

$ git check-ignore -v .worktrees
.gitignore:31:/.worktrees/	.worktrees
```

**The rule is about WHERE the enumerating process runs, not which flag it passes.**

### Correcting this record's own earlier claim

The "third divergence" section above says *"Only the first is a shell artifact."* That sentence is
true and it was **read too narrowly, including by its author**: it was taken to mean gitignore-blindness
*is* a shell artifact. It is not. `--exclude-standard` reproduces gitignore-blindness in **pure
plumbing, with no wrapper involved**, and `git status` does the same.

So the tally is four divergences, in three directions, from two independent causes:

| # | Divergence | Direction | Cause |
| --: | :-- | :-- | :-- |
| 1 | interactive `grep` wrapper honours `.gitignore` | under-report | shell |
| 2 | `git ls-files` is index-only | under-report | plumbing |
| 3 | `/usr/bin/grep -r` across both roots | **over**-report | plumbing |
| 4 | `--exclude-standard` / `git status` honour `.gitignore` | under-report | **plumbing** |

**Three consecutive review rounds carried the same blindness class in the enumeration prescription.**
That recurrence is the finding, more than any individual measurement: each fix was correct about the
defect it named and wrong about the one it introduced, and each was caught only by *running* the
prescribed command rather than reading it.
