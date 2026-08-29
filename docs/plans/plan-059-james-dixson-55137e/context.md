---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` is a suite of **beads-backed skills for coding agents** (`yf-plan`, `yf-research`,
`yf-herdr`, `yf-okf`, and ~15 others), plus a Rust CLI (`yf`) that embeds and deploys them across
four harnesses. Skills are markdown + Python (`uv` with PEP 723 inline deps); the CLI is Rust with
`rust-embed`. Task tracking is `bd` (beads, Dolt-backed) — never markdown TODOs.

**The non-obvious setup a cold reader must know: this repo is both the SOURCE and a CONSUMER of its
own skills, and they are three separate artifacts** — the repo's `skills/` tree, the binary-embedded
tree, and the session-installed copy the running agent actually resolved. **Editing `skills/`
changes nothing about the skill this session is running.** The repo's `skills/` directory is not on
the `SKILL_DIR` resolver's search path at all, so it is unreachable rather than merely stale. See
`AGENTS.md` §"Three artifacts, not one".

**Consequence for this plan specifically:** plan-059 designs changes to `yf-plan` and `yf-herdr`
while executing *under* them. That is safe by construction — prose and scripts both resolve to the
installed copy — **provided no `yf skills install` / `yf self install` runs mid-execution.**

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-28 -->

- `bd`: bd version 1.2.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.6 (7938ca5d5 2026-08-25 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.98.0 (2026-08-20)
- `glab`: glab 1.115.0 (c3612c8de)
- `claude`: 2.1.247 (Claude Code)
- `jq`: jq-1.8.1 (/usr/bin/jq) — **load-bearing**: most of the Success Criteria pipe JSON through `jq -e`, so its absence turns every one of them into an unexplained `command not found` rather than a failed check
- `herdr`: present — required only for the escalation NOTIFICATION half; the artifact half works without it

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-059-james-dixson-55137e`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson (`james@yoshikostudios.com`), repository owner and sole maintainer.
- Authority scope: **full** over this repository, including SPEC amendments and skill design.
- **Approval authority for this plan is the operator's alone** and is not delegable to the agent
  session or to any parent session in the herdr chain — that is the terminating condition of the
  escalation predicate this plan designs.

## Runtime assumptions

- **OS / shell:** macOS (Darwin 25.5.0, arm64), `zsh`. Nothing in this plan is macOS-specific, but
  the `herdr` measurements in `findings/exp-004` were taken on this host and its live pane topology.
- **Network:** required for `gh` (issue read/write). **Issue 0.2 and Epics 2/6 DO need network** — an earlier draft claimed no epic did, which was false once the coarse-tracker issue was added. Four criteria are network-dependent (SC0b, SC2d, SC9b, SC9c) and every upstream write is an operator-authorized step behind its own gate.
- **Credentials:** `gh` is authenticated against `dixson3/yoshiko-flow`. **No token is ever written
  to config** — `gh` owns its own credential store.
- **Side-effect permissions:** this plan is authored under `bypassPermissions`. Outward-facing
  writes (push, PR, issue create/comment) are a **declared stop class** and are operator-authorized
  individually, never batched.
- **`herdr` is assumed present but NOT assumed to be the execution environment.** The escalation
  design degrades to a written artifact with no push when `YF_PARENT_PANE` is unset — which is the
  provenance-derived autonomy rule of Issue 4.4. A cold reader on a machine without `herdr` can
  execute every epic; only the notification half is inert. **One carve-out, stated because an earlier draft overclaimed:** SC8b runs `test_herdr_channel.py`, which asserts a live `herdr agent prompt` exit-0 behaviour, so Issue 4.2b must SKIP rather than FAIL when `herdr` is absent.
- **Concurrency, and it is load-bearing here:** this plan was authored in a dedicated git worktree
  (`.worktrees/yf-judgement-design`, branch `yf-judgement-design`) because **three other agent
  sessions shared the primary checkout** and branch-switching in it had already landed unrelated
  commits on the wrong branch. Execute this plan in its own worktree.

## Adjacent-concept glossary

| Term | Meaning in this plan |
| :-- | :-- |
| **thrash** | a plan that has stopped converging — the same substantive concern re-raised across review passes. Distinguished from **deliberate re-scoping**, which produces an identical residue and is the detector's dominant false positive. |
| **D3 / severity-decay** | research 005's candidate detector: a HIGH-severity finding surviving into review pass >= 3. |
| **escape / escape rate** | #145's metric: a defect that survived review. Not this plan's subject; cited only for the synergy audit. |
| **one-hop / N-hop** | how far an escalation propagates up the controller chain. One hop = child asks its immediate parent. N-hop = each controller forwards upward, terminating at the human. **N-hop is declined here.** |
| **second-party residue** | evidence about a session written by someone other than that session (a reviewer's verdict, an exit code, a token stamp). Consensus C3 requires the trigger read this, never a self-report. |
| **command vs obligation** | the measured distinction between prose naming a command to run (4/5 followed) and prose naming a duty to honour (2/5), over one stated population. See `findings/finding-command-vs-obligation.md`. |
| **write-then-notify** | the forced architecture: the escalation is a durable artifact and the push is a notification about it, because no answer-return primitive exists. |
| **stop class** | `yf-plan`'s five declared halt conditions. Class 4 (a mechanical counter threshold) is where this plan's primary trigger lives. |

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
