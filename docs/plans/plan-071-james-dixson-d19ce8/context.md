---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (working dir `beads-skills`) is the source **and** a consumer of the `yf` skill
family for Claude Code and sibling harnesses. The skill under change is `skills/yf-plan/`: a
Python click script (`plan_manager.py`, `uv run`, PEP 723 inline deps), prose instruction files
(`SKILL.md`, `agents/*.md`), a per-skill spec (`spec/*.md`, `SPEC.md`) and beads formulas. Task
tracking is `bd` (beads, Dolt-backed, embedded, `dolt.local-only`). Validation is
`CHANGE-VALIDATION.md` (FAST on edit, FULL at land). Three artifacts move independently: repo
source, the `rust-embed`-baked `yf` binary, and the installed skill copy this session runs under
(`/Users/james/.claude/skills/yf-plan`). Editing `skills/` changes nothing about the running
session until `yf self install --from-build --build` at land-the-plane.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-09-10 -->

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
- Plan directory: `docs/plans/plan-071-james-dixson-d19ce8`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson (repo owner, sole operator; authority over spec, code and upstream issues). Contact: james@yoshikostudios.com. Plan drafted by Claude (Fable 5.1) in an interactive session at the operator's direction; the operator's verbatim scope instructions are quoted in plan.md §Motivation.

## Runtime assumptions

- macOS (Darwin 25.5), interactive shell **zsh 5.9**; criteria and gate tests run under `bash -c` from the repo root (see AGENTS.md "Shell"). Every `Verification` cell is written to behave identically in both. **`grep` under `bash -c` on this host is ugrep 7.8.4**, which honours `.gitignore`; every grep in this plan targets tracked files, so the difference is inert here, but a cold reader on GNU grep should expect identical results only for tracked paths.
- `execute.worktree` is **false** in `.yf-plan.local.json`, so execution runs in place on a branch cut from `main`; `land` must work under that setting (#331, fixed by plan-068).
- Network: `gh` authenticated against `dixson3/yoshiko-flow`; upstream writes only via `/yf-beads-upstream` at land-the-plane. No Dolt remote.
- Side effects: Epics 3–4 **delete** code, tests, formulas and check scripts. All deletions are git-reversible; none touch operator config or the installed skill copy.
- The plan runs through the **installed (pre-change) yf-plan skill**; its own reconcile gate may be poured without `gate_type` metadata (#388) until plan-070 lands, in which case the operator resolves it by hand.
- plan-070 (`ready-for-approval` at authoring) may land before or after this plan; Issue 3.2 branches on that.

## Adjacent-concept glossary

- **Provably necessary** (D-1): a verb/check/REQ with a live call path AND a fixture-failing test.
- **Reading pass / execution pass**: a red-team pass that reads plan prose vs. one that runs checkers and criteria commands and may raise only `measured:` findings.
- **Fidelity metric**: `sc_flipped_post_approval` + `halts_post_irreversible`, the two numbers that say whether approval predicted a clean landing.
- **Close chain**: `LAND_CLOSE_CHAIN` / SKILL.md §6.4, the L8–L15 verbs `land` runs after the push.
- **INCONCLUSIVE**: exit 2, "the instrument could not run" — distinct from FAIL (exit 1).

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
