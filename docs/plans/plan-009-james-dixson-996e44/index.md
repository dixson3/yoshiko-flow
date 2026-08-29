---
okf_version: '0.2'
---

# plan-009-james-dixson-996e44

> Make bdplan execute run plans in a git worktree by default, with merge-back/re-validate/push land-the-plane flow

This bundle is **portable** — a cold reader understands its purpose, environment and history from the files below alone, without the drafting conversation.

- [context.md](context.md) - Project Environment Context
- [diagrams/worktree-execute-lifecycle.d2](diagrams/worktree-execute-lifecycle.d2)
- [diagrams/worktree-execute-lifecycle.png](diagrams/worktree-execute-lifecycle.png)
- [findings/dogfood-acceptance.md](findings/dogfood-acceptance.md) - Dogfood acceptance — bdplan worktree execution (Issue 2.5)
- [findings/dogfood_worktree.sh](findings/dogfood_worktree.sh)
- [findings/exp-001-worktree-mechanics.md](findings/exp-001-worktree-mechanics.md) - Finding INV-1: git worktree mechanics & path safety
- [findings/exp-002-beads-across-worktrees.md](findings/exp-002-beads-across-worktrees.md) - Finding INV-2: beads (bd / dolt) behavior across git worktrees
- [findings/exp-003-coordinator-execution-model.md](findings/exp-003-coordinator-execution-model.md) - Finding INV-3: coordinator & sub-agent execution model relative to the worktree
- [findings/exp-004-regression-acceptance-model.md](findings/exp-004-regression-acceptance-model.md) - Finding INV-4: concurrent-merge regression / acceptance model
- [findings/exp-005-embed-vs-skill-architecture.md](findings/exp-005-embed-vs-skill-architecture.md) - Finding INV-5: embed vs distinct `worktree` skill (resolves D1)
- [plan.md](plan.md) - Plan: Make bdplan execute run plans in a git worktree by default, with merge-back/re-validate/push land-the-plane flow
- [reviews/pass-1.md](reviews/pass-1.md) - Plan Red-Team: plan-009-james-dixson-996e44 — Pass 1
