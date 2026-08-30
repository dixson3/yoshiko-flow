---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** is a collection of beads-backed skills for coding agents (Claude Code, codex,
opencode, pi), plus `yf` — a Rust binary that embeds those skills and installs them into each
harness. The repository is **both the source and a consumer of its own skills**: this plan is
drafted by `yf-plan` and edits `yf-plan`.

Stack: **Python 3.11+** for the skill engines (PEP 723 `uv run --script` single files, `click` for
CLIs, `pytest` for tests — no packaging, no `requirements.txt`), **Rust** for `yf` (`cargo`,
`rust-embed` for the skill tree), **markdown** for every artifact.

Non-obvious setup a cold reader needs:

- **Three artifacts move independently** — the repo source in `skills/`, the binary-embedded tree
  `yf` carries, and the session-installed copy the running agent resolved. Editing `skills/` changes
  none of what this session is executing. The `SKILL_DIR` resolver never searches the repo's own
  `skills/` directory, so it is unreachable rather than merely stale.
- **`_shared/` is vendored, not imported.** `_shared/sync.py` copies canonical files into consumer
  skills and enforces byte-identity under `--check`, gated in the FAST tier.
- **Task tracking is `bd` (beads)**, backed by Dolt, shared across worktrees because `bd` walks up
  to the repo root. Never markdown checklists.
- **`CHANGE-VALIDATION.md` at the repo root is approved** (`approved: yes`) and defines a FAST tier
  (59 rows, on-edit, glob-scoped) and a FULL tier (57 rows, once per land).
- **SPEC-first is mandatory**: a `REQ-*` amendment lands ahead of the code that implements it, and
  `test_cli_enumeration.py` makes that mechanically enforceable for CLI verbs.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-29 -->

- `bd`: bd version 1.2.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.6 (7938ca5d5 2026-08-25 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.98.0 (2026-08-20)
- `glab`: glab 1.115.0 (c3612c8de)
- `claude`: 2.1.247 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-060-development`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-060-development`
- Plan directory: `docs/plans/plan-060-james-dixson-6a6ac9`

## Operator identity

- Git user: `james-dixson` (James Dixson, `james@yoshikostudios.com`)
- Role: **sole maintainer and operator** of `dixson3/yoshiko-flow`. Owns the repository, the
  upstream issue tracker, and the machine this plan was drafted on.
- Authority scope: the operator is the only party who can authorize an outward-facing write
  (`git push`, `gh issue create/close/comment`), a destructive local operation, or a redeploy of the
  installed toolchain. **No agent holds that authority**, which is the premise this plan is built on.
- Attribution: plan drafted by a Claude Code session (`claude` 2.1.247) under `/yf-plan`, in the
  `plan-060-development` worktree.

## Runtime assumptions

- **OS / shell:** macOS (Darwin 25.5.0, arm64), `zsh`. The tty gate this plan builds is pure POSIX
  and portable, but it was **measured only on macOS**; a cold reader on Linux should re-measure
  `/dev/tty` behaviour inside their harness before trusting the gate's default refusal.
- **Network:** required. `gh` reaches `github.com` for issue reads and writes; `git push` reaches
  `origin`. Every network-calling step must impose a bounded timeout and map expiry to
  `inconclusive`, never `fail`.
- **Credentials:** `gh` owns its own credential store (scopes measured: `gist, read:org, repo,
  workflow`). **No token is ever passed inline or written to config.** `bd` is configured
  `dolt.local-only`, so `bd dolt push` is never proposed.
- **Side-effect permissions — read this before running anything:** this machine's Claude Code
  profile sets `permissions.defaultMode: "bypassPermissions"` and
  `skipDangerousModePermissionPrompt: true`, with **zero** `ask` entries and **no file-write deny
  rule**. An agent session therefore runs as the operator's uid with no write sandbox. **This is the
  central runtime fact of the plan**: it is why no locally-produced artifact can serve as proof of
  operator consent (EXP-005), and why the plan withholds `land --apply` from the session rather than
  guarding it.
- **Git topology:** the plan is drafted in the `plan-060-development` worktree; the primary checkout
  sits on `main`. `main` has **no branch protection** (measured: `404 Branch not protected`), so
  nothing off-machine gates a push.
- **Two different `grep`s, and the criteria layer uses the one you are not looking at.** The
  *interactive* shell here resolves `grep` to a **`ugrep`** shell function; but `recheck-criteria`
  evaluates every criterion via `subprocess.run(["bash","-c", cmd])`, and `bash -c` sees
  **`/usr/bin/grep` — "BSD grep, GNU compatible 2.6.0-FreeBSD"**. A shell function is not exported
  to `bash -c`, so the two never meet.

  **This was measured the wrong way once, and the error is recorded rather than erased.** An earlier
  revision validated SC2b interactively (under ugrep) and read exit 1 / 0 / 2 for
  all-good / one-bad / missing-file. Under `bash -c` the same command returns **0 / 0 / 2** —
  because `grep -L` changes only *output*, not exit status, on both BSD and GNU grep. The criterion
  demanded exit 1 and was therefore **unsatisfiable**, which is the very defect it was written to
  repair. It now uses a `grep -lF … | wc -l` comparison whose exit contract is
  implementation-independent, validated under `bash -c` at exit 0 (all-good) and exit 1 (one-bad).

  This is [#224](https://github.com/dixson3/yoshiko-flow/issues/224)'s hazard with a second edge:
  not only can a `grep` criterion behave differently across implementations, **it can be validated
  in a shell that never evaluates it.** Every `grep`-based criterion in this plan is validated under
  `bash -c`, against a fixture that should pass and one that should fail.
- **Execution assumption:** this plan builds the first code in the repository that merges and pushes.
  It must be rehearsed against a **sandbox clone with a fake origin**, never against the live
  repository, and never as its own landing.

## Adjacent-concept glossary

| Term | Meaning |
| :-- | :-- |
| **landing / land the plane** | the whole post-execution sequence: merge-back, validation, push, reconcile writes, bead close-out, prune, redeploy. This plan's subject. |
| **bead** | a `bd` work item. **Molecule / pour / wisp / burn** are `bd`'s templating verbs — a *molecule* is a poured template instance, a *wisp* a throwaway one, *burning* discards it. |
| **gate** | a first-class `bd` bead of type `gate`. `Type: human` means only a person may resolve it; `Type: auto` means a command establishes the condition. |
| **the close chain** | the twelve ordered §6.4 steps ending in `update-status complete`. Enumerable at runtime via `test_close_contract.py --list-steps`. |
| **halting vs advisory** | a chain step class. A halting step exits non-zero on `fail` and stops the chain; an advisory step always exits 0. |
| **three-valued verdict** | `pass \| fail \| inconclusive`. `inconclusive` means *the check could not run* and never halts — collapsing it into `fail` is the repo's recurring #263 defect. |
| **collapsed signal** | #263's class: one signal carrying two facts whose handling differs, where the permissive consumer reports "clean". |
| **the FAST / FULL tiers** | `CHANGE-VALIDATION.md`'s two recipes — FAST on every edit, glob-scoped; FULL once per land, multi-minute. |
| **red-team / conformance pass** | the two Phase-3 reviews. Both agents are read-only with respect to the repo; the main session writes `reviews/pass-N.md`. |
| **OKF bundle** | the portable plan-folder model: reserved `index.md` and `log.md` plus `plan.md`, `context.md`, `findings/`, `references/`, `reviews/`, `assets/`. |
| **coarse upstream granularity** | this repo's policy: ONE tracking issue per plan-scale effort, not one per bead. |
| **herdr** | the terminal multiplexer this session runs under. A *pane* holds an agent; a *tab* holds panes. |

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
