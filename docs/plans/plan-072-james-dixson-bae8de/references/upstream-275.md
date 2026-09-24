---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #275 - yf-herdr: the launch contract REQ-HERDR-015 mandates
  cannot be passed as documented, and three observer-pattern gaps (worktree, PR, merge
  protocol)'
---
# Upstream #275: yf-herdr: the launch contract REQ-HERDR-015 mandates cannot be passed as documented, and three observer-pattern gaps (worktree, PR, merge protocol)

- **Number:** 275
- **Title:** yf-herdr: the launch contract REQ-HERDR-015 mandates cannot be passed as documented, and three observer-pattern gaps (worktree, PR, merge protocol)
- **URL:** 
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

Plan: plan-056-james-dixson-473dba | Bundle: docs/plans/plan-056-james-dixson-473dba (repo-relative)

Filed from a live `yf-herdr` delegation (plan-056 execution, 2026-08-28). Everything below was
measured against the installed `herdr` binary, not inferred. Three CLI defects and three
process gaps.

## A. `-- --append-system-prompt` cannot carry the launch contract. REQ-HERDR-015's recipe is
## unfollowable as written.

`SKILL.md` mandates sending the contract "in the prompt **and** in `-- --append-system-prompt`, so
they survive the subordinate's context compaction (measured free: 3.016s with, 3.061s control)", and
shows a multi-line `read -r -d '' CONTRACT <<EOF` heredoc being passed that way.

Measured, controlled, both after the pane had settled:

| payload | result |
| :-- | :-- |
| `--append-system-prompt "TESTMARKER-SHORT"` | **works** — `argv: ['claude','--append-system-prompt','TESTMARKER-SHORT']` |
| multi-line payload (4 lines, blank line, quotes, `$`) | **`{"code":"invalid_agent_argument","message":"agent arguments cannot be encoded safely for the target shell"}`** |

The contract is inherently multi-line — it is three labelled paragraphs. So the flag works and the
**documented payload is rejected**. A conformant launch is currently impossible via this route, and
`scripts/test_launch_contract.py` (which SKILL.md says mechanically enforces the three elements)
cannot be detecting this, because it checks the prompt text rather than a live `agent start`.

**Ask:** either single-line-encode the contract (escaped `\n`), or add a `--append-system-prompt-file`
/ stdin route, or relax REQ-HERDR-015 to prompt-only and say why. Whichever — the recipe and the
binary have to agree.

## B. `tab create` returns before the pane can accept an agent, so the documented two-step races.

`SKILL.md`'s recipe is `herdr tab create … → .result.root_pane.pane_id` then `herdr agent start …
--pane <that pane id>`, back to back. Measured: an immediate `agent start` fails with

    {"code":"agent_pane_busy","message":"agent target pane wK:p1B is not an available shell"}

and the identical command succeeds after a ~4s settle. This bit the real launch, not just the probe.

**Ask:** have `agent start` wait for shell availability (it already takes `--timeout`, which appears
to govern agent readiness rather than pane readiness), or document a required settle/poll between
the two steps.

## C. The error envelope makes a FAILED start parse as a SUCCESSFUL one.

Success is `{"id":…,"result":{"agent":{…},"argv":[…]}}`. Failure is `{"error":{…},"id":…}` — **no
`result` key at all**. So the natural parse, and the shape SKILL.md itself recommends elsewhere
(`jq -r '.result.agents[]|…'`), yields:

    name=null pane=null status=null

for a failed start. Observed live: I read that as a started agent with unpopulated fields and moved
on; only an explicit `agent list` re-check revealed nothing had registered.

This is the repo's own collapsed-signal class (#263, #265, #266): two facts — "started, fields
absent" and "did not start" — sharing one rendering. **Ask:** document that callers must branch on
the presence of `.error` before reading `.result`, and have the skill's recipe do so.

## D. Observer pattern says nothing about WORKTREES, and the omission caused a real collision.

`SKILL.md` launches the subordinate with `--cwd "$(git rev-parse --show-toplevel)"` — the **shared
repo root**. Measured consequence today, with four sessions in one repo: another pane ran
`git checkout -b …` in that shared root, which switched the branch under three sessions
simultaneously. Two sessions' commits landed on a third session's branch. Recovery took a
human-coordinated worktree split, a branch reset, and a remote-rewrite scare.

`--show-toplevel` is also actively wrong from inside a worktree: it returns the worktree path, so the
recipe silently means different things depending on where the parent runs.

**Ask:** the launch step should (1) prefer a dedicated worktree per delegated plan, (2) state that
`git checkout`/`switch` in a shared root is forbidden while any other session is attached, and
(3) resolve the cwd explicitly rather than via `--show-toplevel`.

## E. Nothing covers the LANDING half of a delegated plan — PR or merge.

`yf-plan` §4.4 says land per `landing-strategy`, default `main` = merge to `main`. Under the
multi-worktree pattern this skill implies, that is **frequently impossible**: git refuses to check out
a branch already checked out elsewhere, so if any session holds `main`, the delegating session cannot
merge. Measured today — `main` was held by the shared root, so `§4.4` was unavailable and I pushed a
branch and opened a PR instead. Correct, but improvised; nothing documents it.

**Ask:** a landing subsection — when to PR vs merge, who lands (parent or subordinate), and the
`main`-is-checked-out-elsewhere case, which is the normal case under this skill.

## F. No merge/conflict protocol for concurrent delegations.

The skill's only concurrency rule is "never spawn a second tab for the same plan". It says nothing
about N sessions in one repo, which is the configuration it makes easy to create. Measured today: four.

**Ask:** a short protocol — one worktree per delegation; the shared root is read-only/unoccupied;
branch naming; who may touch `main`; and how a parent verifies its subordinate's commits landed on the
intended branch. The last one matters: I only noticed the collision because I checked
`git log main..HEAD` before landing and found a commit that was not mine.

## Provenance

All CLI facts reproduced in throwaway tabs created and closed for the purpose; no other session's
panes were touched. The live delegation (pane wK:p1A, agent `plan-056`) was unaffected and is still
executing. Items D-F are from the incident itself rather than a probe.
