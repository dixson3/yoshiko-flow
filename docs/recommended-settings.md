Recommended Claude Code `settings.json`
=======================================

The Yoshiko Flow (`yf-*`) skills assume the operator has turned **off** a few
competing Claude Code built-ins. Those assumptions live in always-loaded
`rules/*.md` / `protocols/*.md` prose and per-skill `SKILL.md` contracts — but
prose only steers the model; it does not remove the disallowed mechanism. Setting
these keys aligns the runtime with the contracts so the model cannot reach for a
mechanism a skill forbids.

This baseline serves two axes at once:

- **Alignment / portability** — the original motivation: keep the runtime honest
  to the contracts (native task tools, workflows, and Claude-only memory are all
  forbidden) so yf state stays cross-harness and the model cannot substitute a
  non-portable native mechanism.
- **Efficiency** — the operator's highest-leverage lever. Every unused native tool
  still costs **context / tool-schema budget on every turn**, and a bare tool name
  in `permissions.deny` removes that tool's schema from the model's context
  entirely (see [The permissions block](#the-permissions-block)). Killing whole
  feature categories (`disableWorkflows`, `todoFeatureEnabled`,
  `disableBundledSkills`) and disabling never-used tools reclaims that budget; the
  connector/notification/upload keys reduce needless promiscuity with Anthropic and
  interruptions on long autonomous runs.

These are **recommendations, not hard requirements** — the skills still function
without them. Two keys (`disableWorkflows`, `todoFeatureEnabled: false`) are the
highest-impact alignment settings and worth setting first; the `permissions` block
below is the highest-impact efficiency lever.

## Scope: user vs project

Claude reads `settings.json` at two scopes (project overrides user):

| Scope | Path | Use for |
|:------|:-----|:--------|
| **User (default)** | `~/.claude/settings.json` | The baseline below. These align every repo where you run the `yf-*` skills. Set here once. |
| **Project** | `<repo>/.claude/settings.json` | Repo-specific overrides only. A project-scope file already exists in beads-backed repos because `yf-beads-init` manages an entry-scoped beads hook there; this baseline is **user-scope** and disjoint from that hook surface — keep them separate (do not merge the baseline into the project file). |

Document and set the baseline at **user scope**. Reach for project scope only when
a single repo needs a different value.

## The permissions block

The `permissions` block is the highest-leverage efficiency lever. It does two
distinct jobs — keep them straight:

```jsonc
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "deny": [
      // Safety guards (call-time block, NOT a context saving — see below).
      // Illustrative and operator-tunable; not a fixed yf-* requirement.
      "Bash(rm -rf /)",
      "Bash(rm -rf /*)",
      "Bash(rm -rf ~)",
      "Bash(rm -rf ~/*)",
      "Bash(rm -rf $HOME)",
      "Bash(rm -rf $HOME/*)",
      "Bash(sudo rm -rf *)",

      // Tool disables (bare names → schema removed from context entirely).
      // The yf-* skills never use any of these; disabling reclaims tool-schema budget.
      "EnterPlanMode",
      "ExitPlanMode",
      "EnterWorktree",
      "ExitWorktree",
      "TaskCreate",
      "TaskGet",
      "TaskList",
      "TaskOutput",
      "TaskUpdate",
      "DesignSync",
      "NotebookEdit",
      "SendMessage",
      "PushNotification",
      "RemoteTrigger",
      "ReportFindings",
      "ScheduleWakeup",
      "CronCreate",
      "CronDelete",
      "CronList"
    ]
  }
}
```

**Two mechanisms, not one.** A **bare tool name** in `deny` (e.g. `EnterPlanMode`,
`TaskCreate`) removes that tool's schema from the model's context entirely — the
model never sees it, so this is a real context / tool-schema saving. A **scoped**
pattern (e.g. `Bash(rm -rf *)`) only blocks at call time and leaves the schema
present — so the `rm -rf` denials are a **call-time safety guard, not a context
saving**. Do not conflate them.

**`defaultMode: bypassPermissions` is a real security tradeoff, not a free win.**
It auto-approves tool calls so long autonomous skill runs are not interrupted by
per-call permission prompts — an efficiency choice appropriate for **trusted local
development**, where you have already read the code you are running. Adopt it with
eyes open: it removes the human-in-the-loop guard on every tool call. Pair it with
`skipDangerousModePermissionPrompt: true` (in the baseline below) — without that
companion the dangerous-mode prompt still interrupts, defeating the point. The
`rm -rf` deny globs above are the operator-tunable safety floor that remains under
`bypassPermissions`.

### Tool disables — each tool and why it is safe to drop

Every tool below is denied by **bare name**, so its schema leaves the model's
context. The `yf-*` skills never use any of them. A grep of the repo `skills/` tree
for every denied tool (`SendMessage`, `ReportFindings`, `ScheduleWakeup`,
`RemoteTrigger`, `PushNotification`, `DesignSync`, `Task*`, `*PlanMode`,
`*Worktree`, `Cron*`) found **zero** references — the skills dispatch sub-agents
**exclusively via the `Agent` tool** (`subagent_type=…`) and re-dispatch fresh
agents on resume rather than continuing via `SendMessage`.

> **The `Agent` tool is NOT disabled** — and must not be. It is the sub-agent
> dispatch every `yf-*` coordinator, investigator, and reviewer fans out through;
> denying it would break all fan-out. The denied `Task*` tools are the native
> background-task/workflow surface, a **different** mechanism from `Agent`.

| Tool(s) | Rationale axis | Native mechanism it neutralizes |
|:--------|:---------------|:--------------------------------|
| `EnterPlanMode`, `ExitPlanMode` | Avoids interference + context savings | Native plan mode — `yf-plan` explicitly **overrides** it (never use `EnterPlanMode`/`ExitPlanMode`). Disabling stops the model reaching for a forbidden mechanism. |
| `EnterWorktree`, `ExitWorktree` | Avoids interference + context savings | The harness worktree primitive. `yf-plan` manages its own explicit, persistent `git worktree` for EXECUTE; the native primitive has the wrong lifecycle. |
| `TaskCreate`, `TaskGet`, `TaskList`, `TaskOutput`, `TaskUpdate` | Avoids interference + context savings | The native background-task / workflow surface. `bd` (beads) is the ONLY task tracker; native task tools are forbidden by every beads-backed skill contract. |
| `CronCreate`, `CronDelete`, `CronList` | Data minimization + context savings | Native scheduling. Persistence/scheduling must be portable (beads, not a Claude-only scheduler); [global CLAUDE.md](../CLAUDE.md) forbids `/schedule`-style mechanisms. |
| `SendMessage` | Avoids interference + context savings | Inter-agent continuation. yf-* re-dispatches fresh agents on resume rather than continuing a prior agent via `SendMessage`. |
| `ScheduleWakeup`, `RemoteTrigger` | Data minimization + context savings | Wake/trigger scheduling — same portability reason as `Cron*`; never used by any skill. |
| `PushNotification` | Fewer interruptions + context savings | Push notifications on long runs — noise, never used by a skill. |
| `ReportFindings` | Avoids interference + context savings | A native structured-report surface; yf-research reports through its own agent/plan-folder artifacts, not this tool. |
| `DesignSync` | Context savings | Unused native design-sync surface; no skill references it. |
| `NotebookEdit` | Context savings | Jupyter-notebook editing; the skills edit `.md`/`.py`/`.toml`, never notebooks. Drop the schema. |

## Reference baseline

```jsonc
{
  // Highest-leverage efficiency lever. Bare tool names → schema removed from
  // context; the rm -rf globs are call-time safety only. See "The permissions
  // block" above for the mechanism split and the bypassPermissions tradeoff.
  "permissions": {
    "defaultMode": "bypassPermissions",
    "deny": [
      "Bash(rm -rf /)", "Bash(rm -rf /*)",
      "Bash(rm -rf ~)", "Bash(rm -rf ~/*)",
      "Bash(rm -rf $HOME)", "Bash(rm -rf $HOME/*)", "Bash(sudo rm -rf *)",
      "EnterPlanMode", "ExitPlanMode",
      "EnterWorktree", "ExitWorktree",
      "TaskCreate", "TaskGet", "TaskList", "TaskOutput", "TaskUpdate",
      "DesignSync", "NotebookEdit", "SendMessage", "PushNotification",
      "RemoteTrigger", "ReportFindings", "ScheduleWakeup",
      "CronCreate", "CronDelete", "CronList"
    ]
  },
  // bypassPermissions companion: without this the dangerous-mode prompt still
  // interrupts long autonomous runs.
  "skipDangerousModePermissionPrompt": true,

  // yf-* skills parallelize via the Agent tool; native task tools are forbidden.
  "disableWorkflows": true,

  // bd (beads) is the ONLY task tracker. TodoWrite / markdown checklists /
  // inline task lists are forbidden by every beads-backed skill contract.
  "todoFeatureEnabled": false,

  // Portability: yf state must be cross-harness (beads / incubators / repo
  // files). Native Claude memory traps it in a Claude-only store.
  "autoMemoryEnabled": false,
  "autoDreamEnabled": false,
  "autoUploadSessions": false,

  // Data minimization — keep state off Anthropic's servers.
  "disableClaudeAiConnectors": true,

  // Keep bundled skills from shadowing the description-triggered yf-* skills.
  "disableBundledSkills": true,

  // Fewer interruptions — notification noise on long runs.
  "inputNeededNotifEnabled": false,
  "agentPushNotifEnabled": false,

  // Interactive-correctness tradeoff — "never" BLOCKS the run for a human
  // rather than auto-answering; not a fewer-interruptions win.
  "askUserQuestionTimeout": "never",

  // Operator preference — noise / overhead reduction on long skill runs.
  "disableRemoteControl": true,
  "promptSuggestionEnabled": false,
  "spinnerTipsEnabled": false,
  "effortLevel": "medium"
}
```

> **Boolean note.** For `disable*` keys, *disabling the capability* means `true` —
> so `disableWorkflows`, `disableBundledSkills`, and `disableClaudeAiConnectors` are
> all `true`. The non-`disable*` keys express "off" as `false`
> (`todoFeatureEnabled`, `autoMemoryEnabled`, `autoDreamEnabled`,
> `autoUploadSessions`, `inputNeededNotifEnabled`, `agentPushNotifEnabled`).
>
> **Out of scope.** Operator-specific baseline keys — `spinnerVerbs`, `tui`,
> `enabledPlugins`, `extraKnownMarketplaces`, `attribution` — are personal taste,
> not alignment/efficiency levers, and are intentionally omitted here.

## Each key, and the contract it supports

Keys are grouped by how directly an in-repo contract depends on them.

### Highest-impact — a skill contract is leaky without these

| Key | Value | Supporting contract in this repo |
|:----|:------|:---------------------------------|
| `todoFeatureEnabled` | `false` | "All task tracking MUST use `bd`. Never use TodoWrite, markdown checklists, or inline task lists." — stated in [yf-plan SKILL.md](../skills/yf-plan/SKILL.md), [yf-research SKILL.md](../skills/yf-research/SKILL.md), and [yf-beads-authoring SKILL.md](../skills/yf-beads-authoring/SKILL.md), and bound as always-loaded rules in [yf-plan/protocols/PLANS.md](../skills/yf-plan/protocols/PLANS.md) and [yf-research/protocols/RESEARCH.md](../skills/yf-research/protocols/RESEARCH.md). The [yf-beads-authoring reviewer agent](../skills/yf-beads-authoring/agents/reviewer.md) flags any use of native task tools as a defect. Disabling the feature removes the temptation surface entirely. |
| `disableWorkflows` | `true` | yf-* skills fan out exclusively via the **Agent tool**: the [yf-beads-authoring coordinator](../skills/yf-beads-authoring/SKILL.md) dispatch loop and [yf-skill-authoring](../skills/yf-skill-authoring/SKILL.md) review agents all dispatch through it; the [reviewer agent](../skills/yf-beads-authoring/agents/reviewer.md) forbids the native task/workflow tools. Disabling the Workflow tool keeps the model from substituting a non-portable native workflow for the Agent-tool dispatch the skills assume. |

### Portability — keeps state out of a Claude-only store

| Key | Value | Supporting contract in this repo |
|:----|:------|:---------------------------------|
| `autoMemoryEnabled` | `false` | [AGENTS.md "Memory"](../AGENTS.md) is explicit: "Do NOT use Claude Code memory (`~/.claude/` memory directories)." Durable state goes to beads / `AGENTS/` rules / repo files so another clone, machine, or harness can pick it up. |
| `autoDreamEnabled` | `false` | Same portability contract — any Claude-native persistence traps yf state in a non-portable store. |
| `autoUploadSessions` | `false` | Same. Reinforced by [yf-incubator SKILL.md](../skills/yf-incubator/SKILL.md): "All state lives in vault files; never session-only or Claude-only stores." |

### Trigger hygiene

| Key | Value | Supporting contract in this repo |
|:----|:------|:---------------------------------|
| `disableBundledSkills` | `true` | The yf-* skills rely on **description-based triggering** (see the frontmatter contract in [README.md](../README.md)). A bundled skill whose description overlaps a yf-* trigger can shadow it. Disabling bundled skills removes that ambiguity. (Soft alignment — no single skill hard-fails without it, but it protects the trigger surface the whole set depends on.) |

### Data minimization — keeps state off Anthropic's servers

| Key | Value | Why |
|:----|:------|:----|
| `disableClaudeAiConnectors` | `true` | Turns off the claude.ai connector surface. yf state is local/portable (beads, incubators, repo files); the connectors are needless promiscuity with Anthropic for this workflow. (`autoUploadSessions: false`, `autoMemoryEnabled: false`, and `autoDreamEnabled: false` above serve the same axis.) |

### Fewer interruptions — notification noise on long runs

| Key | Value | Why |
|:----|:------|:----|
| `inputNeededNotifEnabled` | `false` | Suppresses the "input needed" notification. Long, multi-phase, beads-tracked runs generate these repeatedly; the operator is already watching the run. |
| `agentPushNotifEnabled` | `false` | Suppresses agent push notifications on long autonomous runs — same noise-reduction rationale. |

### Interactive-correctness tradeoff — NOT a fewer-interruptions win

| Key | Value | Why |
|:----|:------|:----|
| `askUserQuestionTimeout` | `"never"` | A genuine tradeoff, documented honestly: `"never"` means an `AskUserQuestion` prompt waits **indefinitely** for a human rather than timing out and auto-answering. It favors *never auto-answering wrong* over unattended progress — so it **blocks the run for a human**, the opposite of reducing interruptions. Choose it only if you would rather a run stall than proceed on a guessed answer. |

### Operator preference — no skill contract depends on these

These reduce noise/overhead during long, multi-phase, beads-tracked runs. They are
included for completeness; no in-repo contract requires them, so treat them as
taste, not alignment.

| Key | Value | Why |
|:----|:------|:----|
| `disableRemoteControl` | `true` | Fewer interruptions on long runs. |
| `promptSuggestionEnabled` | `false` | Less UI noise. |
| `spinnerTipsEnabled` | `false` | Less UI noise. |
| `effortLevel` | `"medium"` | Sensible default for the planning / research pipelines. |

## Why settings and prose both

The settings here mirror the `rules/*.md` / `protocols/*.md` protocol files
(task-tracking rule, portability rule) so the runtime and the prose tell a single
story. The prose steers; the settings enforce. Where this doc cites a rule, that
rule remains the source of truth — these keys exist to make the safe state the
default rather than relying on the model honoring prose every turn.

And prose costs more than it enforces: a rule that forbids native workflows or
TodoWrite still leaves those tools' schemas loaded in context every turn, paying
the budget without the benefit. A bare-name disable in `permissions.deny` closes
that gap — it removes the schema, so the rule no longer competes for context with
the very mechanism it forbids. That is the efficiency axis: the settings do not
just enforce the contracts, they stop paying to keep the forbidden mechanisms
visible.
