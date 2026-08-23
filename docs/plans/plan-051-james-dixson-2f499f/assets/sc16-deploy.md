---
type: Reference
okf_spec: OKF-PLAN
id: sc16-deploy
description: SC16 — land-the-plane deploy, verified by PAYLOAD as well as by version stamp
---

# SC16 — deploy at land-the-plane

```bash
yf self install --from-build --build --force      # real exit 0
```

Run **only after** the merge was validated and pushed, never mid-execution. `--force` is the
established path rather than an exception: the binary at `~/.local/bin/yf` always exists after a
first install, so every subsequent deploy needs it (plan-050's `log.md` records the identical
command). It was operator-authorized, because overwriting an installed binary is a destructive
local operation.

**The consent gate did NOT fire.** `sync: deployed to claude-code, agents, codex, opencode, pi` —
the config half applied without needing `--allow-permissions-write`, matching plan-050. Had it
fired, skills and the rules aggregate would still have deployed and that would have been a
**partial success**, not a failure.

## 1. Version stamp — proves the BINARY was promoted

| | |
| :-- | :-- |
| `git rev-parse --short HEAD` | `ee2a449` |
| `yf --version` | `yf 0.4.0 (ee2a449-dirty)` |
| hash comparison | **MATCH** |

The `-dirty` suffix is benign and expected: exactly two uncommitted files, `plan-retrospective.md`
and `assets/closable-sweep.md`, both reconcile artifacts due at COMPLETE. **The hash is what must
match**, and it does. This line is the only detector for a stale stamp after a `HEAD` move that
touched nothing `build.rs` watches.

## 2. PAYLOAD — proves the embedded SKILL TREE deployed

**A matching version stamp does not prove this**, and given this plan's own thesis the deploy is
not reported on the stamp alone.

| Check | Result |
| :-- | :-- |
| `ls ~/.claude/skills/yf-plan/formulas/` | `plan-execute`, `plan-investigate`, **`plan-review.formula.toml`** — present |
| `grep -c 'Spawn a sub-agent to perform the adversarial pass' …/SKILL.md` | **1** |
| `agents/red-team.md` — scoped read-only / spike authorized | **1 / 1** |
| `agents/reviewer.md` — scoped read-only / spike authorized | **1 / 1** |
| `spec/agents.md` — `REQ-AGENT-049:` | **1** |
| `scripts/test_review_agent_contract.py` | present |

**The installed test run against the installed tree: 6 passed.** That is the strongest available
payload check — the deployed spec and the deployed agent templates agree with each other, verified
by the deployed checker rather than by inspection.

## 3. Deployed tree vs repo source — content hashes

| File | |
| :-- | :-- |
| `agents/red-team.md` | identical |
| `agents/reviewer.md` | identical |
| `spec/agents.md` | identical |
| `formulas/plan-review.formula.toml` | identical |
| `scripts/test_review_agent_contract.py` | identical |
| `SKILL.md` | **differs by exactly one line** |

The `SKILL.md` difference was **classified, not waved off**: a single injected provenance marker,
`<!-- yf-skills: v=0.4.0 tree=38da227e… -->`. With that line stripped both sides hash to
`34ae9e1ae648b4fc83ac9b2950ce4a68c0c23096` — byte-identical.

## Pre-deploy contrast, for the record

Before the deploy the installed tree was **genuinely stale**, verified structurally rather than by
version string: `plan-review.formula.toml` was **absent**, and the installed `SKILL.md` had
**zero** occurrences of the dispatch phrase. Epics 2 and 3 were undeployed.
