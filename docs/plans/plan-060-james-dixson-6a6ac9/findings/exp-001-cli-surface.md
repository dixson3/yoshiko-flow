---
type: Finding
okf_spec: OKF-PLAN
description: 'EXP-001 — the plan_manager.py CLI surface a `land` verb must slot into: verb inventory, exit-code contract, verdict envelope, existing git/worktree/lock code, test conventions, and `_shared/` vendoring.'
---
# EXP-001: The `plan_manager.py` CLI surface a `land` verb must slot into

## Approach Tested

**Question.** What are the exact registration, envelope, exit-code and test conventions a new
`plan_manager.py land` verb must conform to, and what git/merge/push code already exists?

**Method.** Read-only survey of `skills/yf-plan/scripts/plan_manager.py` (7461 lines),
`skills/yf-plan/spec/cli.md`, `skills/yf-plan/spec/phases.md`, `CHANGE-VALIDATION.md`,
`_shared/sync.py`, and the `test_*.py` suite.


## Result

## F1 — The single most consequential finding: **nothing in this repo has ever merged or pushed**

`grep` for `merge` / `push` across `plan_manager.py` returns only docstrings, comments, and the
`escalation-push` verb (a herdr pane message, not a git push).

> **`git merge`, `git checkout`, `git pull` and `git push` are executed as PROSE in `SKILL.md`, by
> the LLM, never by the script.**

`_run_git` (`skills/yf-plan/scripts/plan_manager.py:4135`) is the only git primitive, and there are
**20** call sites of it *(corrected from 17 after red-team pass 1 re-measured; a handful of direct
`subprocess.run(["git", …])` calls sit outside the helper and a reader would reasonably count them
in the git surface too)* — all of them `rev-parse`, `symbolic-ref`, `status`, `worktree`, `branch`,
`config`, `check-ignore`, `add`, `diff --cached`. `commit-plan` is the only code that writes a git
commit at all.

**Consequence for this plan:** `land --apply` would be the **first merge-performing and first
push-performing code in the repository**. That is a materially larger step than "add a verb", and
it is the reason the risk table treats the git layer separately from the upstream layer.

## F2 — The seam is already fully shaped; only the gaps are prose

Today's Phase 6, with the script/prose boundary marked:

```
landing-lock acquire      ← SCRIPT  (_landing_lock_acquire, :4496)
git checkout <target>     ← PROSE   (SKILL.md:1484)
git pull --rebase         ← PROSE
git merge --no-ff         ← PROSE
validate-merged           ← SCRIPT  (_validate_merged, :4664)
git commit                ← PROSE
landing-lock release      ← SCRIPT  (_landing_lock_release, :4538)
git push / bd dolt push   ← PROSE, operator-authorized (D4, SKILL.md:1544)
worktree teardown         ← SCRIPT  (_worktree_teardown, :4362)
```

The script **already owns** `_run_git`, `_resolve_landing_strategy` (`:3910`), `_execute_branch`
(`:4125`), `_default_branch`, `_worktree_dirty`, `_landing_lock_acquire/release`, `_validate_merged`
and `_commit_plan`. A `land` verb composes existing helpers; it does not need new git plumbing
beyond `merge`, `pull`, `checkout`, `commit` and `push`.

`MERGE_TARGET` resolution exists **only in SKILL.md prose** (`SKILL.md:1481`) — internalizing it is
a strict improvement.

## F3 — Registration: flat vs group, and the check that fires either way

`plan_manager.py` is a **`click`** CLI (root group at `:1466`), PEP 723 / `uv run`, deps
`click>=8.1`, `pyyaml>=6`.

- **39 flat verbs** (`@cli.command`) constitute the REQ-CLI-006 enumerated set.
- **3 groups** — `fingerprint`, `worktree`, `landing-lock` — whose subcommands are, per
  `spec/cli.md:35`, *"**outside** both the enumeration and the check — which is why REQ-CLI-021
  mandates the flat form."*

`test_cli_enumeration.py:64` scrapes `^@cli\.command\((.*?)\)\s*$` from the source and asserts **set
equality** against the backticked names on `spec/cli.md`'s single `The enumeration (currently 39):`
line. `CHANGE-VALIDATION.md:203` fires `uv-yf-cli-enum` on **any** edit to `plan_manager.py`.

> **Therefore: registering `land` flat without amending `spec/cli.md` in the same change-set is a
> hard FAST-tier failure at the point of the edit.** This is a feature — it is the mechanism that
> makes the SPEC-first sequencing enforceable rather than aspirational.

A `land` **group** (`land dry-run` / `land apply`) would escape the enumeration check entirely.
REQ-CLI-021 explicitly discourages that, so the flat form (`land`, with `--dry-run` / `--apply`
flags) is the conformant choice.

## F4 — The verdict envelope (REQ-COMPLETE-003, `spec/phases.md:107`)

```json
{ "verdict": "pass|fail|inconclusive", "passed": true|false,
  "reason": "<one-line human-readable>", "remediation": "<what the operator should do>" }
```

Rules quoted verbatim from `spec/phases.md`:

- **(a)** *"A step emits one JSON object to **stdout** on *every* path, including failure and
  including its own internal errors. Writing a verdict to stderr is a contract violation."*
- **(b)** *"`inconclusive` — the step **could not determine** the answer… This is *not* a failure
  and must never be reported as one."* `passed` is a **derived** compatibility key
  (`verdict == "pass"`), never authoritative.
- **(c)** *"`inconclusive` **NEVER halts**… a `halting` step exits non-zero on `fail` and zero
  otherwise; an `advisory` step always exits zero."*
- **(f)** *"Any step that makes a network call shall impose a **bounded timeout**… Timeout expiry
  yields `inconclusive`, never `fail`."*

**(f) is load-bearing for `land`**, which is the most network-dependent verb in the skill (`gh`
reads and writes, `git push`).

## F5 — The numeric exit-code convention, and the vocabulary that is NOT uniform

| Code | Meaning |
| --: | :-- |
| `0` | pass / no-op / advisory-always / fail-soft |
| `1` | halting `fail`, or a script crash |
| `2` | **INCONCLUSIVE — the check could not run** (REQ-CLI-029: *"It is **not** `3`"*) |
| `3` | **a GATE signal, distinct from failure** — `ready-check`, `review-loop-check`, `worktree ensure/teardown`, `landing-lock acquire/release`, `commit-plan`, `validate-merged` |
| `126/127` | **reserved to the shell**; REQ-CLI-029(c): *"No check shall return either."* |

**Measured inconsistency, and a trap for this plan:** two verdict vocabularies coexist. §6.4 chain
steps use **lowercase** `pass|fail|inconclusive`; newer report verbs (`ownership-report`,
`verify-beads`, `recheck-criteria`) use **UPPERCASE** `INCONCLUSIVE`/`REPORT`/`FAIL`/
`HARNESS_INCOMPLETE` plus a `severity` key. `validate-merged` uses neither — it emits `status`, not
`verdict`, and exits `3` on non-pass.

`landing-lock` likewise emits `{acquired, held_by, reclaimable, detail}` with **no** envelope keys:
it predates REQ-COMPLETE-003.

> This is issue **#263**'s class showing up inside the very surface `land` must compose. A `land`
> verb that naively branches on `-ne 0` across these helpers would conflate `3` (gate) with `1`
> (fail) with `2` (could-not-run). **`land` must read the code, never the flag.**

## F6 — How a verb is added (the five-step ritual)

1. `@cli.command("<name>")` at column 0 + `@click.argument("plan_dir", type=click.Path(exists=True))`
   + the house triple-alias `@click.option("--json-output", "--json", "as_json", is_flag=True)`.
2. Amend `spec/cli.md` REQ-CLI-006's single `The enumeration (currently N):` line.
3. Wire a call site — `test_close_contract.py --assert-invocation <verb>` exits **1** for a
   registered-but-never-invoked verb (*"a verb with no call site is the 'ships unable to fire'
   defect this flag exists to detect"*, `test_close_contract.py:441`) and **2** for an unregistered
   one.
4. If it is a §6.4 chain step, use the capture idiom in the §6.4 block, or add it to
   `EXEMPT_VERBS`.
5. Add a `CHANGE-VALIDATION.md` §1 row and a §3 trigger-scope glob for any new test file.

**There is NO shared helper for emitting JSON + exit code.** The dominant shape in the
git/worktree region is a private `_verb()` returning a dict plus a thin click wrapper doing
`click.echo(json.dumps(...))` + `sys.exit(...)` — `_worktree_ensure`, `_landing_lock_acquire`,
`_validate_merged`, `_commit_plan` all follow it. `land` should follow it too.

## F7 — `close_contract`'s §6.4 boundary is regex-scraped from SKILL.md

`_section_64()` (`test_close_contract.py:106`) slices `SKILL.md` from the line starting `### 6.4` to
the next `###`, then runs `_CAPTURE_RE` / `_INVOKE_RE` over it. **Comments are deliberately not
stripped** — a `#`-prefixed invocation still counts.

`test_block_boundary_is_well_formed` (`:159`) asserts `"worktree teardown" not in block`.

> **Direct constraint on this plan:** the §6.4 block's *shape* is machine-asserted. Any
> restructuring of Phase 6 that moves steps into or out of §6.4 changes what
> `--list-steps` enumerates, and `test_close_contract.py` must move with it in the same change-set.

## F8 — Test conventions

Every `test_*.py` under `skills/yf-plan/scripts/` is a self-contained **PEP 723 pytest script**
(`# /// script` header, `requires-python >= 3.11`, deps `click`, `pytest`, `pyyaml`), ending in
`sys.exit(pytest.main([__file__, "-q"]))`. They `import plan_manager as pm` and **monkeypatch every
external call** — `test_verify_reconcile.py` states *"`gh` is NEVER shelled out to… No network, in
any test."* `test_worktree.py` builds throwaway git repos in `tmp_path`.

> **This is the strongest available answer to the "first merging code" risk in F1:** a merge is
> perfectly testable against a throwaway `tmp_path` repo, and `test_worktree.py` is the working
> precedent for doing so.

`CHANGE-VALIDATION.md:16` records why pytest rows name an explicit **file** target: *"`pytest -k
<no-match>` exits **5** … and `pytest <missing-file>` exits **4** — neither is a vacuous pass."*

## F9 — `_shared/` vendoring: one hard "do not touch" region

`plan_manager.py` is a **region consumer**, never a whole-file consumer. The one generated region is
the defensive JSON extractor, fenced at `plan_manager.py:286` and `:323`:

```
# >>> BEGIN defensive json extractor (generated by _shared/sync.py — edit _shared/json_extract.py) >>>
# <<< END defensive json extractor (generated by _shared/sync.py — edit _shared/json_extract.py) <<<
```

Everything between those markers is regenerated by `_shared/sync.py`, which enforces byte-identity
by plain string equality and exits 1 under `--check`. `CHANGE-VALIDATION.md`'s `_shared/**` glob
fires it in the FAST tier.

`sync.py:400` records the stake: *"A vendored copy that is absent from this list is invisible to
`--check`, so `sync.py --check` stays exit 0 while that copy drifts SILENTLY AND FOREVER."*

## Absence findings

- **No merge code, no push code, no `land` verb, no landing journal.** Searched
  `plan_manager.py` exhaustively. The `landing-lock` verb group is the only recognition of
  merge-back as a concept, and it locks a merge nothing performs.
- **No shared verdict-emission helper.** Each of ~39 verbs hand-rolls `json.dumps` + `sys.exit`.
  This is why the vocabulary drifted (F5).
- **`spec/cli.md:20` (REQ-CLI-004) is stale** — it says *"Every invocation except `init` runs
  `plan_manager.py check`"*; there is no `check` verb (only `fingerprint check`). Not this plan's
  to fix, but recorded because a reader of `cli.md` will hit it.

## Implications for Plan

**measured:** `land --apply` will be the first merge-performing and first push-performing code in
the repository. That reclassifies the work from "add a verb" to "introduce a new authority class",
and it is why the plan carries a dedicated capability gate for it (R1) rather than folding it into
ordinary implementation.

**measured:** the enumeration check fires on *any* edit to `plan_manager.py`, so the `spec/cli.md`
amendment and the verb must land in one change-set. SPEC-first is mechanically enforced here rather
than merely urged — the plan sequences Epic 0 ahead of Epic 1 for that reason.

**inferred:** the four coexisting exit-code and verdict vocabularies (lowercase envelope, UPPERCASE
report verbs, `validate-merged`'s bare `status`, `landing-lock`'s pre-envelope keys) mean a naive
`-ne 0` branch inside `land` would conflate `3` (gate), `2` (could-not-run) and `1` (fail). `land`
must read the code, never the flag.

## Recommendations

1. Register `land` **flat**, with `--dry-run` / `--apply` as flags; a group escapes the enumeration
   check that REQ-CLI-021 exists to keep it inside.
2. Follow the `_verb()`-returns-dict + thin-click-wrapper shape used by `_worktree_ensure`,
   `_landing_lock_acquire`, `_validate_merged` and `_commit_plan`.
3. Test the merge against throwaway `tmp_path` repos, per `test_worktree.py`.
4. Do not touch the generated JSON-extractor region (`plan_manager.py:286`-`:323`).
