---
okf_version: '0.2'
---

# plan-022-james-dixson-14b3dd

> Certify yf beads skills against bd 1.1.x and harden local-only remote hygiene (#68, #61)

This bundle is **portable** — a cold reader understands its purpose, environment and history from the files below alone, without the drafting conversation.

- [context.md](context.md) - Project Environment Context
- [findings/exp-001-embedded-wedged-commit.md](findings/exp-001-embedded-wedged-commit.md) - EXP-001: Do `bd vc commit` / `bd dolt commit` bypass migration guards on a wedged EMBEDDED Dolt DB (bd 1.1.0)?
- [findings/exp-002-remove-remote-clears-gate.md](findings/exp-002-remove-remote-clears-gate.md) - EXP-002: Does remove-remote-alone clear the bd 1.1.0 remote-migrate gate?
- [plan.md](plan.md) - Plan: Certify yf beads skills against bd 1.1.x and harden local-only remote hygiene (#68, #61)
- [references/upstream-61.md](references/upstream-61.md) - Upstream #61: yf-beads-upstream/hygiene: authorize --remove-remote cleanup + trigger on 'push/sync upstream' phrasing
- [references/upstream-68.md](references/upstream-68.md) - Upstream #68: Confirm/certify yf beads skills against bd 1.1.x (currently pinned to 1.0.5)
- [reviews/pass-1.md](reviews/pass-1.md) - Review pass 1 — plan-022
- [reviews/pass-2.md](reviews/pass-2.md) - Review pass 2 — plan-022
- [upstream-triage.md](upstream-triage.md) - Upstream Issue Triage: Certify bd 1.1.x + local-only remote hygiene
