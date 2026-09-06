---
okf_version: '0.2'
---

# plan-023-james-dixson-b618bb

> Beads infra / local-only hardening (#58, #67, #66, #57)

This bundle is **portable** — a cold reader understands its purpose, environment and history from the files below alone, without the drafting conversation.

- [context.md](context.md) - Project Environment Context
- [findings/exp-001-minimal-local-profile.md](findings/exp-001-minimal-local-profile.md) - EXP-001 — Minimal-local beads profile surface (#58) + config-resolution/migration facts (#67)
- [plan.md](plan.md) - Beads infra / local-only hardening (#58, #67, #66, #57)
- [references/upstream-57.md](references/upstream-57.md) - Upstream #57: yf-beads-upstream: close-time Safety invariant reads as a hand-CLI recipe, inviting raw bd github push over /yf-beads-upstream
- [references/upstream-58.md](references/upstream-58.md) - Upstream #58: Define + enforce a canonical 'minimal local' beads profile (embedded/local-server, per-project, local-only, worktree-shared) via yf preflight
- [references/upstream-60.md](references/upstream-60.md) - Upstream #60: yf-beads-upstream: support mutually-exclusive requires:<platform> labels in worklist filtering + hoist
- [references/upstream-65.md](references/upstream-65.md) - Upstream #65: plan-019: Preflight yf self-update offer + preflight cache version-invalidation
- [references/upstream-66.md](references/upstream-66.md) - Upstream #66: yf-beads-init: gitignore .beads/interactions.jsonl in repair's gitignore top-up (canonicalization #39 gap)
- [references/upstream-67.md](references/upstream-67.md) - Upstream #67: Migrate legacy root-level skill configs (.<skill>.local.json) into the .yf/ namespace
- [reviews/pass-1.md](reviews/pass-1.md) - Review pass 1 — plan-023
- [reviews/pass-2.md](reviews/pass-2.md) - Review pass 2 — plan-023
- [upstream-triage.md](upstream-triage.md) - Upstream Issue Triage: beads infra local-only hardening
