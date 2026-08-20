---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #163: yf-herdr: multi-harness fan-out — dispatch bead work to secondary sessions of other agent kinds

- **Number:** 163
- **Title:** yf-herdr: multi-harness fan-out — dispatch bead work to secondary sessions of other agent kinds
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Scope

Dispatch bead work to **secondary sessions of other agent kinds** — codex, pi, opencode, and any
future `--kind` — rather than only to a `claude` subordinate. This is the half of #110 that
plan-045 deliberately did **not** build.

Today `yf-herdr` launches exactly one subordinate per plan/research target, resolving the kind
from the parent (`REQ-HERDR-010`). Fan-out means several subordinates, potentially of *different*
kinds, coordinating over one bead DAG.

## Why it was excluded — the measured blocker, not a scheduling decision

plan-045's exp-005 verified the child→parent push channel end to end and found one honest limit
that fan-out has to resolve **first**:

> **Honest limit:** the queuing is **Claude Code's TUI behavior, not herdr's**. `agent prompt` is
> keystroke injection; the queue lives in the claude harness. A non-claude `--kind` may not queue
> the same way — **untested**.

That is load-bearing. The entire push contract rests on a push to a *working* agent being
**queued rather than lost** — measured for `claude`, where the TUI shows `Press up to edit queued
messages`. If another harness drops an injected keystroke while busy instead of queuing it, then
for that kind the push channel silently loses messages, and the token side-channel
(`report-metadata`) becomes the *primary* mechanism rather than the backstop it was designed as.

**So the first work item here is a measurement, not a feature:** for each non-claude `--kind`,
determine whether `agent prompt` into a busy session queues, drops, or interleaves. The answer
decides whether fan-out can reuse the push design at all or needs a pull/token-based protocol per
kind.

A second, related unknown: `agent_prompted` acknowledges **injection, not submission** (exp-005
§B — one measured push returned success and was never submitted). Whether that gap is wider or
narrower on other harnesses is likewise untested.

## What this can now build on

plan-045 shipped the single-subordinate substrate, so fan-out starts from working parts rather
than from scratch:

- **`YF_PARENT_PANE` seeding** via `--env` on `tab create` — measured to reach the agent process
  *and its grandchildren*, so a push works from inside a tool call.
- **The mandatory launch contract** (`REQ-HERDR-015`): the autonomy directive, the push contract
  and the parent handle are required prompt content, in the prompt **and** in
  `-- --append-system-prompt` so they survive context compaction. Enforced by
  `skills/yf-herdr/scripts/test_launch_contract.py`.
- **Three push triggers, `--wait` forbidden** (`REQ-HERDR-026`): epic completion, blocker/failed
  gate/halt, plan completion or abort — never per bead. `--wait --until idle` is measurably wrong
  for claude, which settles at `done` and never `idle`.
- **The `report-metadata` token side-channel**, readable via `pane get` / `agent get` /
  `agent list` — a pull path needing no action from the child, which survives a swallowed push.
- **Observation is push-primary, polling the fallback** (`REQ-HERDR-020/021/026`).

## Constraint to preserve

`REQ-HERDR-014` currently caps this at **one subordinate per target**, because two sessions racing
one bead DAG is a corruption hazard. Fan-out must replace that cap with an actual work-partitioning
scheme — not simply lift it.

## References

- #110 (closed) — the original proposal. Its push-channel/autonomy half landed in plan-045; this
  issue carries the fan-out half so it is relocated rather than dropped.
- plan-045 (`plan-045-james-dixson-9899e1`), tracker #162, landed as 18f3959.
- `docs/plans/plan-045-james-dixson-9899e1/findings/exp-005-herdr-push-verification.md` — the
  measurements quoted above.

