---
type: Reference
okf_spec: OKF-PLAN
id: yf-herdr-skill-user-scope
retrieved: '2026-08-13'
source: file://~/.claude/skills/yf-herdr/SKILL.md
vendored: true
vendored_note: >-
  Verbatim copy of the user-scope `yf-herdr` skill as it stood when plan-037 hoisted it into this repository.
name: yf-herdr
description: >
  Delegate an approved yf-plan or a gated yf-research project to a NEW herdr tab running a fresh
  session of the same agent kind, then observe that subordinate session and mine its deviations for
  process improvements.
  TRIGGER when: /yf-herdr invoked; or the operator asks to "execute the plan" / "execute the
  research" / "run it in a new session" AND this session is running inside herdr (HERDR_ENV=1) AND
  this session has recently asserted that a specific plan or research project is ready to execute.
  SKIP for: sessions not under herdr (say so and hand the command to the operator); a fresh session
  that did no planning work (execute in place — a tab buys nothing); any request to CREATE or
  APPROVE a plan (that is yf-plan) or to drive panes for unrelated reasons (that is the herdr
  skill). This skill never authors plans and never resolves a gate.
user-invocable: true
skill-group: utility
depends-on-tool: [herdr, uv]
depends-on-skill: [herdr]
---

# yf-herdr

Delegates execution to a subordinate session and keeps watching it. Two responsibilities, and the
second is the one that pays: **launch** correctly, then **observe** honestly.

## What this skill is for

`yf-plan` requires execution in a **new session** — the fingerprint, not conversation state, carries
eligibility across the boundary (`yf-plan` SKILL.md §4.6). `yf-research coordinate` says the same.
Left to itself that means the operator opens a terminal, starts an agent, and types the command.
This skill does that in a herdr tab and, crucially, does not then forget about it.

## Preflight — all four must hold

Check in order and stop at the first failure. **Do not spawn a tab speculatively.**

```bash
test "${HERDR_ENV:-}" = 1                     # 1. inside a herdr-managed pane
command -v herdr >/dev/null                   # 2. CLI present
```

3. **Readiness is VERIFIED, not remembered.** The conversation may *say* a plan is ready; confirm it
   mechanically before spawning anything:

```bash
# yf-plan: status must be `approved` AND the fingerprint fresh (not stale-approved)
uv run <yf-plan>/scripts/plan_manager.py resume-scan "<plan_dir>" --json   # stale_approved:false
# yf-research: the coordinate gate must be resolvable
```

   A plan in `ready-for-approval`, or `approved` with a **stale** fingerprint, is **not** ready — it
   needs re-approval, not a session. Report that and stop.

4. **This session must be context-dirty** — it did the planning work. A fresh session has no
   boundary to cross and should run `/yf-plan execute …` **in place**; spawning a tab is pure
   overhead and splits the observer from the work for nothing.

On failure of (1): say plainly that this is not a herdr session, print the command the operator
should run, and stop. On (3) or (4): explain which condition failed rather than proceeding.

## Launch

**Match the current agent kind.** Do not assume `claude` — resolve what *this* session is:

```bash
KIND=$(herdr agent list --json | jq -r --arg p "$HERDR_PANE_ID" '.result.agents[]|select(.pane_id==$p)|.agent')
```

Create the tab in the **current workspace**, at the repo root, without stealing focus:

```bash
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$(git rev-parse --show-toplevel)" \
  --label "<plan-id> execute" --no-focus            # → .result.root_pane.pane_id
herdr agent start "<short-name>" --kind "$KIND" --pane "<that pane id>" --timeout 120000
herdr agent prompt "<short-name>" "/yf-plan execute <plan-id>"
```

Parse every id from the JSON responses; never predict them. Give the agent a **stable short name**
(`plan-014`, `research-003`) — it is the handle every later turn uses.

**Record the delegation** in the conversation: agent name, pane id, what was launched. A later turn
must be able to find the subordinate without re-deriving it.

## Observe — and be honest about what that means

**A turn-based agent cannot watch continuously.** There is no execution between operator turns. So
observation is: **on every subsequent turn while the subordinate is live**, plus on demand. Say this
to the operator once at launch rather than implying a watcher exists.

Each check:

```bash
herdr agent get <name>                                  # agent_status
herdr agent read <name> --source visible                # while working; alternate-screen safe
herdr agent read <name> --source recent-unwrapped --lines 60   # once idle
```

Escalate **in that turn's reply**, not silently:

| Signal | Meaning | Action |
| :-- | :-- | :-- |
| `blocked` | a question or approval UI is open | Read it. Answer only if it is settled by existing plan content; otherwise bring it to the operator |
| a gate is reported | needs operator authority | Surface it with what authorising actually accepts. **Never resolve a gate on the operator's behalf** |
| `idle`/`done` mid-plan | may be waiting, not finished | Check remaining beads before reporting completion |
| an error or refusal | | Report verbatim; do not paper over |

**Two traps, both observed live:**

- A prompt sent to a **`blocked`** agent is consumed by the open dialog and silently lost. Check
  `agent_status` before prompting; if `blocked`, resolve the dialog first, then prompt.
- Subordinates often stop after each epic when told to "report back". If autonomy is wanted, say so
  explicitly: report at boundaries but **continue without waiting**.

## Mine deviations for process improvements

This is the skill's real payload. When execution **diverges from what the plan assumed**, that is
evidence about the *planning* workflow, and it is only visible from the outside. Watch for:

| Deviation observed | Likely upstream defect |
| :-- | :-- |
| A finding's premise is refuted at execution | Investigation recorded an **inference as a measurement**, uncorroborated → `yf-plan` investigator / red-team premise check |
| A gate's condition cannot be satisfied | Gate blocks the issue that produces its own evidence → gate **reachability** |
| An issue needs a tool/artifact authored later | Precondition not checked against DAG order → execution-rehearsal gap |
| Bead count at pour ≠ issue count in plan.md | Pour step mis-read the plan |
| Plan content edited mid-execution | Scope was wrong at approval, or the plan encoded a guess |
| A success criterion proves unachievable, or two contradict | Criteria never checked against each other |
| The same class of defect recurs across plans | The **fix belongs upstream**, not in this plan |

For each: record what was observed, what it implies about the process, and which skill owns the fix
(`yf-plan`, `yf-research`, or a transitive skill). Distinguish a **one-off** from a **class** — a
single occurrence may still be worth a cheap prompt-level fix, but say which it is.

**Report; file only on the operator's say-so.** Surface deviations and proposed improvements in
conversation. File upstream (`dixson3/yoshiko-flow`) only when the operator approves. Do not
auto-file: transient blips generate noise and duplicates, and the operator is the one who knows
whether a pattern is real.

## Rules

- **Never resolve a capability gate.** Gates exist to spend operator attention; a delegating skill
  resolving one defeats the whole mechanism.
- **Never spawn a second tab for the same plan.** Re-use the recorded agent name; a duplicate
  subordinate means two sessions racing the same bead DAG.
- Do not close tabs or panes you did not create, and do not `herdr server stop`.
- Verify readiness mechanically every time. A conversational assertion of readiness is a claim,
  not a fact — that distinction is the same one this skill teaches the operator to look for.

See `SPEC.md` for requirements, and the `herdr` skill for CLI semantics (pane/agent primitives, id
handling, lifecycle states).
