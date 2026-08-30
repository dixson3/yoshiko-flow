# yf-herdr

Delegates an approved `yf-plan` or gated `yf-research` project to a new herdr tab running a fresh
session of the **same agent kind**, then observes that subordinate and mines its deviations for
defects in the *planning* workflow.

## Why it exists

`yf-plan` and `yf-research` both require a session boundary for execution — the fingerprint, not
conversation state, carries eligibility across it. Without this skill the operator opens a terminal,
starts an agent, and types the command by hand, and nothing watches the result.

The launch half is convenience. **The observation half is the point:** the parent session is the
only vantage point from which a plan's assumptions can be compared against what execution actually
hit, and that comparison is where planning-process defects become visible.

## Two things it deliberately will not do

- **Poll continuously.** A turn-based agent has no execution between operator turns, so the parent's
  own polling happens at turn boundaries and on demand, and the skill says so rather than implying a
  watcher. That is a limit on **pull**, not on observation: the subordinate **pushes** at epic
  boundaries, blockers and completion, so the parent learns of a material event without polling for
  it (REQ-HERDR-026).
- **Resolve a gate, or auto-file an issue.** Gates exist to spend operator attention. Improvements
  are reported; filing waits for authorisation.

## Prerequisites

The **`herdr` binary** on `PATH`, and a session running inside a herdr-managed pane
(`HERDR_ENV=1`). Both are trigger preconditions, so where `herdr` is absent this skill is inert
rather than broken.

`uv` is also declared (`depends-on-tool: [herdr, uv]`) because the readiness check shells out to
`yf-plan`'s `plan_manager.py resume-scan`.

CLI semantics come from the third-party **`herdr` skill**, which this repo does not ship. That
relationship is a **prose soft-dep**, not a `depends-on-skill` entry — see SKILL.md
"Relationship to the `herdr` skill".

## Install

Installed by `yf skills install` / the repo-level `install.sh`, which auto-discover every
`skills/*/` directory. This skill ships **no companion rule**, **no hook**, and **no scripts**,
so no installer change is needed — it is picked up automatically. It belongs to the `utility`
install group, so `yf skills install --group utility` includes it. See the project
[README](../../README.md) for installer flags.

## Usage

User-invocable (`user-invocable: true`). There are no subcommands.

```
/yf-herdr                 # delegate the plan or research project this session just readied
```

It also fires without the explicit slash command when the operator says "execute the plan" /
"execute the research" / "run it in a new session" **and** all four preflight conditions hold:
`HERDR_ENV=1`, `herdr` on `PATH`, a mechanically verified readiness assertion, and a
context-dirty parent session. Any condition failing produces an explanation, never a
speculative tab. SKILL.md carries the checks in order.

## Behavior model

| Phase | What it does |
| :--- | :--- |
| Preflight | Checks the four conditions in order, stopping at the first failure. Readiness is verified mechanically (`resume-scan`), never inferred from the conversation. |
| Launch | Resolves the parent's agent kind from `$HERDR_PANE_ID` against `herdr agent list`, opens a tab in `$HERDR_WORKSPACE_ID` with `--cwd` at the repo root and `--no-focus`, and records the subordinate's name + pane id as the delegation handle. Seeds the parent's own pane id as `YF_PARENT_PANE` and carries the mandatory prompt content — autonomy directive, push contract, parent handle — in both the prompt and `--append-system-prompt` (REQ-HERDR-015). |
| Observe | **Push-primary:** the subordinate pushes at epic completion, a blocker or failed gate, and plan completion or abort — never per bead, and never with `--wait`. Polling is the fallback for a silent or `blocked` subordinate, and runs at operator turn boundaries and on demand. Reads `blocked` before sending any prompt, and never treats `idle`/`done` as completion without checking remaining beads. |
| Mine | Records each divergence from a plan assumption, classified one-off vs recurring class, with the skill that owns the fix. |
| Report | Surfaces gates and escalations to the operator. Improvements are filed upstream only on explicit authorisation. |

At most **one** subordinate per plan or research project; a second spawn for the same target is
refused.

## Layout

```
skills/yf-herdr/
├── scripts/
│   ├── test_herdr_channel.py
│   └── test_launch_contract.py
├── README.md                    # this file
├── SKILL.md                     # trigger contract, launch procedure, observation contract, deviation taxonomy
└── SPEC.md                      # REQ-HERDR-NNN requirements, taxonomy provenance, dependency posture
```

No `scripts/`, `agents/`, `formulas/`, `templates/`, or `protocols/` — the skill is prose only
and drives the third-party `herdr` CLI directly.

## Status

Active. Authored 2026-08-12 in user scope and imported into `dixson3/yoshiko-flow` by plan-037;
the pre-import snapshot is preserved under that plan's `references/user-scope/`. The deviation
taxonomy is seeded from real executions (plan-013, plan-014), three of which produced upstream
issues — yoshiko-flow#112, #113, #114.
