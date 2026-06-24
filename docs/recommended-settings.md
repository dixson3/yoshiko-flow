Recommended Claude Code `settings.json`
=======================================

The Yoshiko Flow (`yf-*`) skills assume the operator has turned **off** a few
competing Claude Code built-ins. Those assumptions live in always-loaded
`rules/*.md` / `protocols/*.md` prose and per-skill `SKILL.md` contracts — but
prose only steers the model; it does not remove the disallowed mechanism. Setting
these keys aligns the runtime with the contracts so the model cannot reach for a
mechanism a skill forbids.

These are **recommendations, not hard requirements** — the skills still function
without them. Two keys (`disableWorkflows`, `todoFeatureEnabled: false`) are the
highest-impact alignment settings and worth setting first.

## Scope: user vs project

Claude reads `settings.json` at two scopes (project overrides user):

| Scope | Path | Use for |
|:------|:-----|:--------|
| **User (default)** | `~/.claude/settings.json` | The baseline below. These align every repo where you run the `yf-*` skills. Set here once. |
| **Project** | `<repo>/.claude/settings.json` | Repo-specific overrides only. A project-scope file already exists in beads-backed repos because `yf-beads-init` manages an entry-scoped beads hook there; this baseline is **user-scope** and disjoint from that hook surface — keep them separate (do not merge the baseline into the project file). |

Document and set the baseline at **user scope**. Reach for project scope only when
a single repo needs a different value.

## Reference baseline

```jsonc
{
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

  // Keep bundled skills from shadowing the description-triggered yf-* skills.
  "disableBundledSkills": true,

  // Operator preference — noise / overhead reduction on long skill runs.
  "disableRemoteControl": true,
  "promptSuggestionEnabled": false,
  "spinnerTipsEnabled": false,
  "effortLevel": "medium"
}
```

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
