---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (`dixson3/yoshiko-flow`, working name `beads-skills`) is the source of the
`yf` Rust CLI and the 20 skills under `skills/` that it embeds and installs into agent
harnesses (claude-code at `.claude/skills`; pi, codex, opencode at `.agents/skills`).
Skill helpers are Python run through `uv run` with PEP 723 headers. Validation is
`CHANGE-VALIDATION.md` (FAST/FULL tiers, executed by the `yf-change-validation` engine);
doc/spec agreement is `DRIFT-CHECK.md`. SPEC changes land first (AGENTS.md "SPEC-first").
The running session reads **installed** skill copies, never `skills/`, so editing a
description changes nothing live until redeploy (AGENTS.md "Three artifacts").

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-09-24 -->

- `bd`: bd version 1.3.0 (Homebrew)
- `git`: git version 2.54.0 (Apple Git-157)
- `uv`: uv 0.12.18 (01cb90c1a 2026-09-22 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.101.0 (2026-09-15)
- `glab`: glab 1.119.0 (f5016eda2)
- `claude`: 2.1.282 (Claude Code)
- `pi`: 0.87.1 (`@earendil-works/pi-coding-agent`), provider `cliproxyapi`, model `claude-opus-5-5`
- `herdr`: 0.9.1. Eval tabs `cc-eval` (`w1G:p2`) and `pi-eval` (`w1G:p3`) during investigation
- `d2`: `/opt/homebrew/bin/d2`

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-072-james-dixson-bae8de`

## Operator identity

- Git user: `james-dixson`
- Operator: James Dixson (GitHub `dixson3`), repo owner. Sole approver for every human gate
  in this plan, and the only authority for outward-facing GitHub writes and redeploys.

## Runtime assumptions

- **macOS, zsh.** Shell loops must be portable (AGENTS.md: zsh doesn't word-split).
- **In-place execution** (`.yf/plan/config.local.json` → `execute.worktree: false`): one
  address space, execute branch cut in the primary checkout (Issue 0.1).
- **Live model credentials for both harnesses.** The trigger evals start real `claude -p`
  and `pi -p` sessions. At API list rates that's ~$0.05–0.41 per completed CC run
  (EXP-002/pass-1), ~360 runs per harness per FULL tier, and a $200 development ceiling
  for Epic 3 (D9). Both harnesses run on subscription plans here, so the real marginal cost
  depends on when usage crosses into billed extra usage, which isn't observable. The plan
  reports measured tokens next to the list-rate figure. Without auth, evals report
  INCONCLUSIVE.
- **Scratch clones outside the repo** under `~/.cache/plan072-eval/` (investigation) and
  `~/.cache/yf-trigger-eval/` (shipped harness), with the origin remote removed, so an
  eval agent can't push. Eval agents run with CC `bypassPermissions`: inherited from
  the operator's settings in installed mode, and passed explicitly with
  `--permission-mode bypassPermissions` in candidate mode, where `--setting-sources project`
  drops user settings (pass-1 C6). That is only safe inside those clones, and sessions are
  killed at activation or 6 tool calls.
- **Network:** `uv` resolves PEP 723 deps; `gh` needs auth for the upstream-write gate.
- **Results depend on the machine**: installed-mode evals see the operator's full global
  skill/rules/MCP config (EXP-003/004).

## Adjacent-concept glossary

- **Intent**: one eval prompt, optionally with a fixture (shell snippet that creates its
  precondition in the scratch clone), labelled should-trigger (`expect: <skill>`) or near-miss
  (`expect: null`, `near: [siblings]`).
- **Activation**: a CC `Skill` tool call naming the skill, or any tool call whose arguments
  touch an installed `skills/<n>/` path or run `yf skill-dir <n>` (EXP-003).
- **Candidate / installed mode**: evaluating un-deployed description text in isolation
  vs the deployed skills under full operator config (EXP-005).
- **crisp / satisfactory / loose**: the description rating (D1, `REQ-SKAUTH-061`).

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
