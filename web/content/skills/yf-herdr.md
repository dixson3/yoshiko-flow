`yf-herdr` hands an already-approved plan to a second agent session and then keeps
watching that session. It creates a new [herdr](https://github.com/dixson3/herdr) tab,
starts a fresh session of the **same agent kind** as the one you are talking to, gives it
the execute command, and records the handle. From then on it reports what the subordinate
is doing, escalates what needs you, and collects the places where execution disagreed with
the plan.

The launch half is convenience. **The observation half is the point.** The parent session
holds the plan's assumptions; the subordinate discovers what those assumptions were
actually worth. Comparing the two is how a defect in the *planning* workflow becomes
visible, and the parent is the only vantage point from which that comparison can be made.

## Why a second session at all

`yf-plan` will not execute a plan in the session that wrote it. Eligibility crosses the
session boundary as a **content fingerprint** written at approval, not as conversation
state. `yf-research coordinate` works the same way. That boundary is deliberate — it is
what stops a drafting session from quietly executing a plan it is still editing.

Without this skill you satisfy the boundary by hand: open a terminal, start an agent, type
the command, and then nothing watches the result. `yf-herdr` does those steps and keeps the
observer.

## Four conditions, checked in order

The skill will not spawn a tab speculatively. All four must hold, and the first failure
stops the check with an explanation rather than a launch:

| Condition | Why it is required |
| :--- | :--- |
| `HERDR_ENV=1` | The session is inside a herdr-managed pane. Outside one there is no workspace to open a tab in. |
| `herdr` on `PATH` | The CLI that creates the tab and reports agent state. |
| A **verified** readiness assertion | Readiness is checked mechanically, never inferred from what the conversation claimed. |
| A **context-dirty** parent | A fresh session has no boundary to cross, so it should execute in place. |

**Readiness is a measurement, not a claim.** For a plan, it means status `approved` *and* a
non-stale fingerprint — `resume-scan` reporting `stale_approved: false`. A plan sitting in
`ready-for-approval` is not ready, and neither is one in `abandoned` — that status is terminal
and not execute-eligible. Neither is an `approved` plan whose content changed after
approval; that one needs a fresh review cycle, not a subordinate.

The context-dirty condition is the one that surprises people. If you just opened a session
and did no planning work, delegating buys nothing and costs you the observer's co-location.
Run it in place instead.

## What "observing" honestly means

A turn-based agent has no execution between your turns. `yf-herdr` says so at launch rather
than implying a background watcher:

- **Your polling happens at your turn boundaries and on demand.** There is no polling loop,
  no daemon, no cron. But that is a limit on *pull*, not on observation: the subordinate
  **pushes** to your pane at epic boundaries, blockers and completion, so you learn of a
  material event without asking for it. Polling is the fallback for a subordinate that has
  gone silent or reads `blocked`.
- **`blocked` is read before any prompt is sent.** A prompt delivered to a blocked agent is
  swallowed by its open dialog and lost. This was observed live, twice, before it became a
  rule.
- **`idle` and `done` are not completion.** Both states also occur when a subordinate is
  simply waiting. The skill checks the remaining beads before reporting a plan finished.
- **The parent answers a question only when the approved plan already settles it.** Anything
  touching scope, risk, or a success criterion goes to you.

Capability gates are never resolved by the parent. A gate exists to spend operator
attention; a subordinate agent's parent resolving one defeats the whole mechanism. The
skill surfaces each gate with what authorizing it actually accepts.

## Mining deviations

For each place execution diverged from a plan assumption, the parent records what was
observed, what it implies about the planning process, and which skill owns the fix. Each
deviation is then classified as a **one-off** or a **recurring class** — a class implies an
upstream fix, a one-off may not, and stating which is which is part of the report.

The seed taxonomy comes from real executions, not speculation. Three of its classes already
produced upstream issues:

| Class | Observed in |
| :--- | :--- |
| A premise refuted at execution — an inference recorded as a measurement | plan-014 |
| A gate condition unreachable from what it blocks | plan-013 |
| A precondition unavailable at its position in the DAG | plan-013 |
| Bead count at pour not matching the plan's issue count | plan-013 |
| Plan content edited mid-execution | plan-013, plan-014 |

Improvements are **reported to you and filed upstream only on explicit authorization**.
Auto-filing is prohibited: a transient blip becomes noise and duplicates, and only you can
judge whether a pattern is real.

## Boundaries

- **One subordinate per plan.** A second spawn for the same target is refused. Two sessions
  racing one bead DAG is a corruption hazard, not a parallelism win.
- **Not a supervisor.** The subordinate owns its execution.
- **Never authors or approves a plan.** That is `yf-plan`.
- **Outside herdr it does not pretend.** With no herdr session it explains the situation and
  hands you the command.

The `herdr` CLI semantics — pane and agent primitives, id handling, lifecycle states — come
from the third-party `herdr` skill, which `yf` does not ship. That is a **prose soft-dep**,
not a declared skill dependency: present, `yf-herdr` delegates to it; absent, it says so.
The hard requirement is the `herdr` binary itself, declared as a tool dependency, so on a
machine without it the skill is inert rather than broken.
