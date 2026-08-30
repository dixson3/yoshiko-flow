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
content grep for enumeration. **R13** carries the risk; **SC10b** tests it.

> **SUPERSEDED — read before acting on the tool list this paragraph originally gave.** It named
> `git ls-files` / `git -C <worktree>` / `git worktree list --porcelain`, and that prescription was
> corrected **three** times: see *"A third divergence: TRACKED-ness is not PRESENCE"*, *"A fourth:
> the fix was itself gitignore-blind"*, and *"A fifth: `--others` is a tracked-ness filter too"*
> below. The current prescription is a **scoped directory listing**, or the explicit **union**
> `ls-files ∪ ls-files --others --exclude-standard`, run via `git -C <worktree>`.
>
> *(This pointer was recorded as landed in `reviews/pass-5.md`'s C4 resolution and did NOT land —
> the edit silently no-opped on an unmatched string. That is #250's class: a resolution recorded as
> done and never written. Caught by red-team pass 6, not by any check.)*

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
37     # ... AT THE TIME. Now 0 — see the fifth divergence below.
$ git -C .worktrees/plan-060-development status --porcelain <same path>
?? docs/plans/plan-060-james-dixson-6a6ac9/
```

**This plan's own bundle — 36 files when first measured, 37 by the next review pass — is invisible
to `git ls-files`.** (The figure drifts as review files are added; it is a derived count in prose,
which is why the count itself is not the claim.) And that is not an accident of
timing: **draft comment bodies are untracked BY CONSTRUCTION at `--dry-run` time**, because the
plan-folder writes are not committed until L16 — which is D-2's entire point.

**That fixture no longer exists.** When this was written the bundle was untracked and this sentence
claimed it was "the cheapest possible fixture for SC10b". The operator then committed it
(`a5664e7`), so the bundle is now **40 tracked / 0 untracked**. SC10b must construct its own — and
per the fifth divergence below it must carry **both** a tracked and an untracked draft.

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

## A fifth: `--others` is a tracked-ness filter too, and the premise died mid-review

Red-team pass 6 ran the prescription again after the operator's mid-review commit and found the
fourth fix incomplete on a new axis. `git ls-files --others` is the **exact complement** of
`git ls-files`, so it is *also* a tracked-ness filter and omits every **tracked** file:

```console
# same bundle, from the worktree, AFTER it was committed (a5664e7)
$ git ls-files <bundle>                                            -> 40
$ git ls-files --others --exclude-standard <bundle>                 -> 0     # the prescribed tool
$ { ls-files ; ls-files --others --exclude-standard ; } | sort -u   -> 40
$ find <bundle> -type f                                             -> 40
```

**Neither `ls-files` nor `--others` alone is a presence fact.** Only the union, or a non-git scoped
listing, answers "is this file here".

### The premise was falsified by this plan's own history

Issue 1.9 rested on *"draft comment bodies are untracked BY CONSTRUCTION at `--dry-run` time,
because the plan-folder writes are not committed until L16."* `commit-plan` exists precisely to
commit a bundle **before** landing, the operator invoked it here, and the command that returned
**37** while the bundle was untracked returns **0** now. `draft_present` would have been wrong in
*both* directions, depending on nothing but whether someone had committed.

### Five divergences, and the shape of the recurrence

| # | Divergence | Direction | Cause |
| --: | :-- | :-- | :-- |
| 1 | interactive `grep` wrapper honours `.gitignore` | under-report | shell |
| 2 | `git ls-files` is index-only | under-report | plumbing |
| 3 | `/usr/bin/grep -r` across both roots | **over**-report | plumbing |
| 4 | `--exclude-standard` / `git status` honour `.gitignore` | under-report | plumbing |
| 5 | `--others` is the complement of `ls-files` | under-report | plumbing |

**Four consecutive review rounds carried the same blindness class, and each fix was correct about
the defect it named and wrong about the one it introduced.** Every one was caught by *running* the
prescribed command rather than reading it — and #5 was invisible to five passes purely because the
bundle happened to be untracked until the operator committed it.

## Post-Epic-0 re-run (2026-08-29, execution)

Every criterion whose command exists **at this point in execution**, re-run from the **execute
worktree** (`.worktrees/plan-060-james-dixson-6a6ac9`) under `bash -c` — the shell
`recheck-criteria` actually uses, where `grep` resolves to `/usr/bin/grep` rather than to the
interactive `ugrep` shell function. Re-confirmed live this session: `type grep` reports *"grep is a
shell function"* even inside the Bash tool, so the shell column stays a column.

| # | Shell | Verdict | Exit | Reading |
| :-- | :-- | :-- | --: | :-- |
| SC1 | `bash -c` | **PASS** | 0 | Was `2` (not-yet-true) at approval. Epic 0 landed the amendment-log entry: *"10 amended id(s) all carry an amendment-log bullet; all 37 non-exempt implementation issues reach a REQ-naming Epic-0 issue"*. |
| SC2 | `bash -c` | **PASS** | 0 | 39 non-Epic-0 issues, all covered; floor 30 satisfied. |
| SC2b | `bash -c` | not-yet-true | 1 | Correct: the three test files do not exist until Epics 1–3. |
| SC4 | `bash -c` | **RED** | 1 | **The criteria layer demonstrably CAN fail — this is the point of Issue 0.9.** `spec/cli.md` now enumerates `land` while `plan_manager.py` does not register it (`2 failed, 5 passed`). SPEC-first makes this window expected; it closes at Issue 1.6. Before Epic 0 this criterion was green, so the transition green→red→green is *observed*, not asserted. |
| SC13 | `bash -c` | not-yet-true | 1 | The `agents/lander.md` dispatch line lands at Issue 2.4. |
| SC32 | `bash -c` | not-yet-true | 2 | `--assert-invocation land` reports the verb is unregistered. Exit 2 is its unregistered-verb code. Closes at 1.6/5.2. |
| SC33 | `bash -c` | **PASS** | 0 | `10 passed` — the §6.4 baseline the Epic-5 rewrite must preserve, re-confirmed after the Epic-0 spec edits. |
| SC34 | `bash -c` | not-yet-true | 1 | The `SKILL.md` prose fix lands at Issue 5.4. |
| SC37 | `bash -c` | not-yet-true | 2 | `assets/full-tier-record.md` does not exist until Issue 6.2. |

## The exit-2 collapse, recorded rather than left implicit (Issue 0.9)

`scripts/checks/check-pytest-ran.sh` is three-valued — `0` the named test ran and passed, `1` it ran
and failed **or does not exist**, `2` **INCONCLUSIVE**, the instrument could not run. **The
`recheck-criteria` clause grammar is binary**, and it collapses that `2` to *criterion FALSE*.

**Measured, not inferred.** `plan_manager.py:3229`:

```python
def _recheck_holds(rc: int, want: str) -> bool:
    if want == "non-zero":
        return rc != 0
    return rc == int(want)
```

Every criterion in this plan is written `-> exit 0`, so `want == "0"` and `_recheck_holds(2, "0")`
evaluates `2 == 0` → `False`. An INCONCLUSIVE is therefore reported as a criterion that does not
hold.

**This is the fail-closed direction, and it is a property of the grammar rather than of this plan.**
An instrument that could not run must never be read as a criterion that holds. But a plan carrying
`dixson3/yoshiko-flow#263` — and whose own `spec/landing.md` `REQ-LAND-012` and `spec/cli.md`
`REQ-CLI-030` both require that `inconclusive` is **never coerced to `fail`** — must not leave its
own criteria layer quietly doing the opposite. So it is stated here:

- **Inside `land`'s own verdicts**, `inconclusive` is a distinct third value and is never coerced
  (`REQ-LAND-012`).
- **At the `recheck-criteria` binding**, an INCONCLUSIVE from a criterion's command is read as
  FALSE, because the clause grammar has no third value to read it into.

The two are not in conflict, but they are also not the same rule, and a reader who assumed the first
implied the second would misread a red SC as a measured regression when it may be a broken
instrument. The remedy when this bites is to read the instrument's own output — `check-pytest-ran.sh`
prints its INCONCLUSIVE reason — never to relax the clause.

## R13 instance #2 — zsh does not word-split, and it reported eight false INCONCLUSIVEs

**Found during execution, Issue 1.8.** A fourth incarnation of R13's class, recorded here because
the class keeps arriving in a new disguise and the bundle — not a pane scrollback — is where it has
to live.

The verification loop was written:

```bash
for sc in "SC6 test_dry_run_does_not_mutate" ...; do
  set -- $sc
  bash scripts/checks/check-pytest-ran.sh <file> $2 ; echo "$1 exit=$?"
done
```

Run under the ambient **zsh**, every row reported `exit=2`. Run directly, the identical check
reported `exit=0`.

**Cause: `zsh` does not word-split unquoted parameter expansions**, where `bash` does (`SH_WORD_SPLIT`
is off by default). So `set -- $sc` set `$1` to the **entire string** `"SC6 test_dry_run_does_not_mutate"`
and left `$2` **empty**; `check-pytest-ran.sh` received no test name and correctly returned
**INCONCLUSIVE**. The tell was visible in the output and easy to read past: the label column printed
`SC6 test_dry_run_does_not_mutate` where it should have printed `SC6`.

**Why this belongs to R13 rather than being a separate curiosity.** R13's shape is *"an assertion
reads a different answer depending on the shell"*, and its first three incarnations were all about
`grep` resolving to a ugrep function. This one has nothing to do with `grep` — it is
**word-splitting** — which is the point: the invariant is the **shell**, not the command. Both
incarnations produce a **wrong answer at a plausible exit code**, and both vanish under `bash -c`.

**The failure direction was benign here and that is luck, not design.** Eight false INCONCLUSIVEs
are loud: `recheck-criteria`'s binary grammar collapses a `2` to *criterion FALSE* (recorded above),
so the mistake would have surfaced as eight red criteria, not eight green ones. The **same** cause
in a loop whose check defaults to green would have been silent.

**Mitigation, unchanged from R13's original: run it under `bash -c`.** Every criterion in this plan
was validated that way, and the re-run above was redone that way, at which point all eight reported
`exit=0`. `recheck-criteria` itself uses `subprocess.run(["bash", "-c", cmd])`, so `bash -c` is not
a convention — it is the shell the criteria are actually evaluated in.
