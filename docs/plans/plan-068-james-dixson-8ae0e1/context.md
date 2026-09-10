---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** is a repository of beads-backed skills for coding agents (`yf-plan`,
`yf-research`, `yf-okf`, and others), plus a Rust binary `yf` that embeds and deploys them.
Skills are Markdown (`SKILL.md`, `agents/*.md`) plus PEP-723 self-contained Python scripts run
via `uv run`. There is **no pytest/coverage config anywhere** and **no `tests/` directory** —
tests sit beside the implementation as self-running scripts in `skills/yf-plan/scripts/`.

**The repository is both the source and a consumer of its own skills**, which is the single most
important non-obvious fact for this plan. Three artifacts move independently: the repo source
(`skills/`), the binary-embedded tree (`rust-embed`, changes on rebuild), and the
session-installed skill (changes on deploy). **The repo's `skills/` directory is unreachable by
the `SKILL_DIR` resolver** — so editing it does not change the running session.

This plan modifies `skills/yf-plan/scripts/plan_manager.py` (~10,200 lines), specifically its
`land` path: the twenty-step `LAND_EXECUTOR` (L0–L19) that carries a plan from a green execute
branch to a merged, pushed, reconciled, closed and redeployed state. The governing SPEC is
`skills/yf-plan/spec/landing.md` (`REQ-LAND-*`) and `spec/phases.md` (`REQ-BRANCH-*`).

**SPEC-first is mandatory**: the `REQ-*` edit lands ahead of the code, or staged in the same
change-set ahead of it. **Task tracking is `bd` (beads) only** — never TodoWrite or markdown
checklists.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-09-09 -->

- `bd`: bd version 1.2.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.11 (4b53f66b7 2026-09-08 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.100.0 (2026-09-03)
- `glab`: glab 1.117.0 (44790937b)
- `claude`: 2.1.266 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-068-james-dixson-8ae0e1`

## Operator identity

- Git user: `james-dixson` (James Dixson, `james@yoshikostudios.com`)
- Role: repository owner and maintainer of `dixson3/yoshiko-flow`.
- Authority scope: full — may authorize merges to `main`, `git push`, GitHub issue writes via
  `gh`, and `yf self install` redeploys. **Consent is still required per-act**: the `land --apply`
  tty gate (stop-class 1) and this plan's Gate 4 (publishing upstream corrections) are operator
  decisions, not agent ones.
- Agent attribution on commits: `Co-Authored-By: Claude <noreply@anthropic.com>`.

## Runtime assumptions

| Assumption | Detail | Why it is load-bearing |
| :-- | :-- | :-- |
| **In-place execution** | `.yf/plan/config.local.json` sets `"execute.worktree": false`, so `_worktree_ensure` short-circuits on `opted-out` and **no execute branch is created** | This is the defect the plan fixes (#331), and the plan must pay its tax once: **Issue 0.1 hand-cuts `<plan-id>-execute` before any SPEC edit**, because in-place mode has **one address space** and a commit made earlier lands on `main` and escapes the merge L3 validates |
| **Shell is zsh 5.9** | `$SHELL` is `/bin/zsh`; agent tool calls run under it | zsh does **not** word-split unquoted parameter expansions and its arrays are 1-based. Measured cost in plan-063: a `bd update` loop wrote one bead the wrong value and skipped six, **at exit 0**. Write constructs that behave identically in both shells; verify effects by reading writes back, never by exit code |
| **macOS / BSD userland** | Darwin 25.5.0, arm64 | Gate 1's test was rewritten twice for BSD `grep` semantics — BSD `grep` returns 2 on a missing file, and `!` flips that to a **false pass**. Any new gate test must be run literally on this platform, not assumed |
| **Network access** | Required for `gh` (Epic 3), and for `uv run --with` provisioning | Offline, Epic 3's consent gate cannot be satisfied and `uv --with` fetches fail |
| **`gh` credentials** | `gh` authenticated against `dixson3/yoshiko-flow`; `gh` owns its own credential store | Gate 4 (`consent` class) publishes to public issues. **No token is ever passed inline or written to config** |
| **Side-effect permissions** | The plan's own landing performs outward writes: `git push`, `gh` issue edits, and an L19 redeploy | Every one is operator-authorized. **`land --apply` must be run by the operator in their own shell** (stop-class 1, REQ-LAND-013/014) — the session prints the command and stops |
| **No `yf skills install` / `yf self install` mid-execution** | `plan_manager.py` is re-invoked per call, so a mid-execution deploy takes effect in the *same* session for scripts but not for `SKILL.md` prose | A half-deployed session runs **new scripts against old prose**. Redeploy is the **last** step of landing, from clean `main` in sync with `origin` |
| **Sandbox discipline for tests** | Issue 2.5's end-to-end test and the rehearsal build throwaway repos | **Measured hazard:** `_validate_merged` and `_worktree_teardown` resolve their root via cwd-less `_repo_root()` / `_git_root()` falling back to `Path.cwd()` / `Path(".")`. Without Issue 1.1's `root=` parameter, a test that does not `os.chdir()` would run L3's FULL tier and **`git branch -d` in the real checkout** |


### Verified at execution (2026-09-09)

Drafting could state these as expectations; only running the plan could confirm them. Recorded
because the bundle's contract is that a cold reader understands it from the folder alone, and an
assumption that was never checked reads exactly like one that was.

| Assumption | Verified how | Result |
| :-- | :-- | :-- |
| In-place, `execute.worktree: false` | `plan_manager.py config-resolve --json` | `false`, source `config.local` — confirmed, and `_worktree_ensure` returned `viable: false, reason: "opted-out"` before Epic 2 changed it |
| The execute branch must be hand-cut | Issue 0.1 | cut from `main@42bb27dd`, recorded in `assets/execute-base.txt`; SC0 verified (branch exists **and** is HEAD) |
| **The `land` that runs is the INSTALLED copy** | `diff ~/.claude/skills/yf-plan/scripts/plan_manager.py skills/yf-plan/scripts/plan_manager.py` | **DIFFERENT.** This is the three-artifacts rule made concrete: every Epic 1/2 fix takes effect at the next deploy, so this plan lands through the un-repaired path it repairs. See `assets/landing-hazard-playbook.md` |
| `gh` credentials for Gate 4 | `gh auth status` | authenticated as `dixson3` via `GITHUB_TOKEN`; all four issue comments posted and **verified by read-back**, not by exit code |
| `uv run --with` network provisioning | every test invocation | worked throughout; `test_land_apply.py` alone provisions `pytest`, `click`, `pyyaml` per run |
| Baseline suite green before the seam | Gate 2, `--sweep-gates=all` | **66 passed, exit 0, 43.6s** — matching the plan's measured baseline of 66 exactly |
| macOS/BSD `grep` semantics | Gate 1 executed literally on this platform | exit 0; the twice-rewritten form held |

**One assumption was WRONG in a way worth recording.** The plan predicted Issue 1.1 would break
**eight** tests (pass-5 prototyped it). Measured: **sixteen**. The extra eight came from Issue
1.1's own recorded decision to add `env=` to the seam now rather than later — a decision the
prototype did not include. With `FakeRunner` updated to accept and record `env`, the residue was
exactly the predicted eight. The prediction was not wrong about the refactor; it was wrong about
a decision that had not been made when it was measured.
## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
