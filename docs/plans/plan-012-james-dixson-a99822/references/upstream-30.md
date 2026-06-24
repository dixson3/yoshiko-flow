# Upstream #30: Document recommended Claude settings.json baseline for yoshiko-flow skills

- **Number:** 30
- **Title:** Document recommended Claude settings.json baseline for yoshiko-flow skills
- **URL:** 
- **State:** OPEN
- **Labels:** documentation, enhancement

## Body

## Summary

Document a recommended Claude Code `settings.json` baseline that materially
improves how the yoshiko-flow (`yf-*`) skills behave. Several skill contracts
assume the operator has *turned off* competing built-in mechanisms (native
workflows, the TodoWrite task feature, Claude-native memory). Today that
assumption lives only in always-loaded `rules/*.md` prose; if the settings
aren't set, the model can still reach for the disallowed mechanism and the
skill's invariants leak.

Proposal: ship a documented reference config (README section or a
`docs/recommended-settings.md`) so installers can align settings with the skill
contracts in one step.

## Reference config (current user-scope, trimmed to the relevant keys)

```jsonc
{
  // yoshiko-flow uses the Agent tool for parallelism, never the Workflow tool.
  // The global rule says "never run dynamic Workflow tool calls"; this enforces it.
  "disableWorkflows": true,

  // Task tracking is beads (bd) ONLY. PLANS.md / BEADS.md forbid TodoWrite,
  // markdown checklists, and inline task lists. Disabling the feature removes
  // the temptation surface entirely.
  "todoFeatureEnabled": false,

  // Portability requirement: nothing yoshiko-flow needs may live in a
  // Claude-only store (it must be pickup-able cross-harness). Keep persistence
  // in beads / incubators / repo files, not native memory.
  "autoMemoryEnabled": false,
  "autoDreamEnabled": false,
  "autoUploadSessions": false,

  // Avoid bundled skills shadowing or conflicting with the yf-* skill set.
  "disableBundledSkills": true,

  // Noise / overhead reduction during long multi-phase skill runs.
  "disableRemoteControl": true,
  "promptSuggestionEnabled": false,
  "spinnerTipsEnabled": false,
  "effortLevel": "medium"
}
```

## Rationale by key

| Setting | Why it helps yoshiko-flow |
|:------------------------|:------------------------------------------------------------|
| `disableWorkflows` | yf-* skills parallelize via the **Agent** tool; the Workflow tool is explicitly disallowed. Setting this enforces the rule instead of relying on prose. |
| `todoFeatureEnabled:false` | `bd` (beads) is the single task tracker. Disabling TodoWrite prevents a parallel, non-portable tracking system. |
| `autoMemoryEnabled` / `autoDreamEnabled` / `autoUploadSessions` | Portability: yoshiko-flow state must be cross-harness (beads/incubators/repo). Native memory traps it in a Claude-only store. |
| `disableBundledSkills` | Prevents bundled skills from shadowing yf-* triggers. |
| `disableRemoteControl`, `promptSuggestionEnabled:false`, `spinnerTipsEnabled:false` | Reduce noise/overhead during long, multi-phase, beads-tracked runs. |
| `effortLevel` | Sensible default for the planning/research pipelines. |

## Notes / scope

- These are **recommendations**, not hard requirements — the skills should still
  function without them, but `disableWorkflows` and `todoFeatureEnabled:false`
  in particular align the runtime with contracts the skills already assume.
- Document at **user scope** (`~/.claude/settings.json`) as the default;
  project scope (`<repo>/.claude/settings.json`) for repo-specific overrides.
- Consider a short note that these mirror the `rules/*.md` protocol files
  (Workflows rule, BEADS/PLANS task-tracking rule, portability rule) so the
  settings and the prose stay a single story.

## Acceptance criteria

- [ ] A documented recommended-settings section/page exists in the repo.
- [ ] Each recommended key is tied to the skill behavior / rule it supports.
- [ ] `disableWorkflows` and `todoFeatureEnabled:false` are called out as the
      highest-impact alignment settings.
- [ ] User-scope vs project-scope guidance is included.

---
_Reference config is drawn from a working user-scope `settings.json` running the
yoshiko-flow skill set._

