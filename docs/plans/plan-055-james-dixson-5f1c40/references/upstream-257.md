---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #257: Deploy skills ONCE to .agents/skills for every harness that reads it; keep only config/hooks/extensions harness-specific

- **Number:** 257
- **Title:** Deploy skills ONCE to .agents/skills for every harness that reads it; keep only config/hooks/extensions harness-specific
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Proposal

**For any harness that reads `.agents/skills` with no configuration, deploy SKILLS there and
nowhere else.** Harness-specific directories keep only what is genuinely harness-specific —
config, hooks, extensions, the always-loaded rule target.

Concretely: `pi` and `opencode` stop receiving a private skills tree and read the shared
`.agents/skills` that `codex` and `agents` already use.

## Measured evidence

Both harnesses read `.agents/skills` by default:

| harness | evidence |
| :-- | :-- |
| **opencode** | its bundle references `.agents/skills`, `.claude/skills`, `.config/opencode/skill(s)`, `.opencode/skill(s)` |
| **pi** | its package (`@earendil-works/pi-coding-agent/dist/cli.js`) references `.agents/skills` |

And **opencode demonstrably PREFERS it.** Running the plan-054 skew test in a real opencode
session with a distinct marker planted in each tree:

```
~/.config/opencode/skills/yf-plan  -> OPENCODE      ← where yf deploys FOR opencode
~/.agents/skills/yf-plan           -> AGENTS-codex  ← what opencode ACTUALLY loaded
```

opencode resolved `SKILL_DIR=/Users/james/.agents/skills/yf-plan`. **yf's opencode-specific
deployment is shadowed** on any machine that also has `.agents/skills` populated — which is
every machine with codex installed.

pi, by contrast, loaded from its own `~/.pi/agent/skills`. So today the two harnesses that both
read `.agents/skills` disagree about which root wins, and yf pays for a private tree in both
cases.

## What this fixes

1. **Eliminates the staleness class outright.** With one tree there is no divergence to go
   stale, and no shadowing to detect. Today it is harmless only because every tree comes from a
   single `yf self install` and is byte-identical — a fix deployed to `.config/opencode` while
   `.agents` lagged would be silently overridden, and nothing would report it.
2. **Reduces install work** — one skills deployment instead of one per harness.
3. **Removes a whole verification surface.** The per-destination `SKILL_DIR_INSTALLED_AT` stamp
   (plan-054 Issue 6.10, #248) exists to keep prose and scripts in the same tree. With one
   shared tree the skew is not merely detected, it is **unrepresentable**. The stamp should
   stay — it is still load-bearing for claude-code, which has its own root — but the number of
   trees it must disambiguate drops.

## Scope of the SPEC change

`yf/src/harness_desc.rs` currently gives every harness a skills subpath. This proposal splits
the descriptor's two concerns, which are conflated today:

- **skills root** — shared `.agents/skills` for harnesses that read it; private only for those
  that do not (claude-code).
- **surface dir** — unchanged, harness-specific: config, hooks, extensions, rule target.

`REQ-YF-INSTALL-002` and the `harness_cross_e2e` per-harness dest-resolution assertions both
encode the current one-root-per-harness model and would need amending. SPEC-first, per
AGENTS.md.

## Open questions, not assumptions

- **Does claude-code read `.agents/skills`?** Not measured here. If it does, the shared tree
  could be universal and the private-root case disappears entirely. If it does not, it stays the
  one exception. **Measure before deciding** — this proposal does not assume either way.
- **Project scope.** The same question applies to `$GIT_ROOT/.agents/skills` versus the
  per-harness project dirs. The measurement above was user-scope only.
- **Migration.** Existing installs have populated private trees. A `yf` upgrade would need to
  deploy to the shared root and *remove* the now-unread private ones, or they become exactly the
  stale shadowing copies this proposal exists to eliminate.
- **Is preference stable?** opencode preferring `.agents` over its own root is measured on
  1.18.23. If that ordering is an implementation detail rather than a contract, relying on it is
  a bet. Deploying only to `.agents` is safe either way — it is the root both harnesses agree
  they read — but the reasoning should rest on "both read it", not on "opencode prefers it".

## Provenance

Found while validating the plan-054 cross-tree-skew fix (#248) in live pi, opencode and codex
sessions. The skew fix itself passed on all three — zero resolved to `~/.claude`, where all
three did before v0.5.0. This is the layer above: not prose-vs-scripts within a tree, but
**yf's deployment target versus the harness's own choice of root**.

