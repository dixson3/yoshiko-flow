---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #110: herdr: leverage `herdr agent *` to launch and monitor agent sessions from a primary session

- **Number:** 110
- **Title:** herdr: leverage `herdr agent *` to launch and monitor agent sessions from a primary session
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

herdr (terminal multiplexer for coding agents) exposes a socket API over its CLI that lets an agent running *inside* a herdr pane create panes, launch other coding agents into them, submit prompts, block on lifecycle state, and read their output. That is a fan-out/coordinate primitive that yf skills currently have no native equivalent for.

Proposal: investigate a yf integration where a **primary** session drives **secondary** agent sessions through `herdr agent *`, rather than through in-process subagents.

## Why this is interesting for yf

The beads-backed coordinator loops (`yf-plan`, `yf-research`, the `yf-beads-authoring` dispatch pattern) currently fan out to in-process subagents. Those are ephemeral, invisible to the operator, and bounded by the parent's context. herdr-launched sessions are the opposite:

- each secondary is a **real, visible pane** the operator can watch, interrupt, or take over;
- secondaries are **full sessions**, not subagents — own context window, own harness;
- they can be a **different harness** (`--kind` covers 21: claude, codex, pi, opencode, gemini, droid, …), so a yf skill could dispatch work to whichever agent suits the task;
- they **survive the parent** — herdr's `session` layer persists panes across server restarts.

## Capabilities (verified against herdr 0.8.0, macOS)

herdr ships an agent skill **bundled in the binary**, printed by `herdr --skill` (added in 0.8.0). It is gated on `test "${HERDR_ENV:-}" = 1` and scoped "use only when the user explicitly mentions Herdr" — so it is safe to install always-on.

The relevant verbs:

| Command | Behavior |
| :-- | :-- |
| `herdr pane split --pane <id> --direction right` | create a pane; returns JSON with the new pane id |
| `herdr agent start <name> --kind <kind> --pane <id> [-- <agent-args>]` | launch an agent into an existing shell pane; **returns only after herdr detects the agent is ready** (30s default, `--timeout` to 300s) |
| `herdr agent prompt <target> <text> --wait --until <state>` | submit a prompt, optionally blocking on state |
| `herdr agent wait` / `read` / `list` / `get` | poll state, read terminal output, enumerate |

Lifecycle states are `idle`, `working`, `blocked`, `done`, `unknown`. `blocked` is herdr recognizing an approval/question UI — a real "needs operator" signal a coordinator could act on. Agents get stable names (`[a-z][a-z0-9_-]{0,31}`), so targets survive layout changes.

An initial prompt appears to be passable as a native agent arg after `--`, e.g.
`herdr agent start reviewer --kind claude --pane <id> -- "review the diff on this branch"` — **unverified**, needs a live test.

## Note on Claude Code's `SendMessage`

Worth recording, since it looks like an alternative and is not: `SendMessage`/`ListAgents` address *Claude Code's own* registry (spawned subagents + peer Claude sessions). Peer sessions running in herdr panes do show up there, so it can reach them — but it cannot launch anything, only reaches `claude`, and a new session is addressable only once it registers. `herdr agent prompt` is the more general injection path and the only one with `blocked`-state semantics.

## Open questions

1. **Scope** — a standalone `yf-herdr` skill, or a dispatch *backend* that existing coordinators can select (in-process subagent vs herdr pane)?
2. **Degradation** — every yf skill must still work outside herdr (`HERDR_ENV` unset). Optional accelerator, never a dependency.
3. **Coordinator resilience** — how do herdr-launched secondaries interact with the crash/resume + stuck-bead sweep contract in `yf-beads-authoring`? A pane outliving its coordinator is new (and possibly an advantage).
4. **Attribution** — can a secondary write beads back, or does the primary own all `bd` mutations?
5. **Cost/limits** — real sessions are not free; fan-out width needs a cap.
6. Does `-- <initial prompt>` work reliably across kinds, or is `agent start` + `agent prompt` the more portable two-step?

## Environment

- herdr 0.8.0 (stable channel), macOS 25.5.0, Ghostty 1.3.1
- herdr integrations installed for claude / codex / opencode / pi

