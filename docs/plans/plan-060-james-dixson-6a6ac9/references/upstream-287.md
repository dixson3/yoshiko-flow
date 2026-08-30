---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #287 - INVESTIGATION: bead/issue state drift is one-directional
  in reporting — 17 issues are CLOSED upstream with beads still open, and nothing
  surfaces it'
---
# Upstream #287: INVESTIGATION: bead/issue state drift is one-directional in reporting — 17 issues are CLOSED upstream with beads still open, and nothing surfaces it

- **Number:** 287
- **Title:** INVESTIGATION: bead/issue state drift is one-directional in reporting — 17 issues are CLOSED upstream with beads still open, and nothing surfaces it
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

> **This is an investigation, not a bug report.** The observation is measured; whether it represents
> a problem, and which direction is authoritative, are open questions. Noticed while dogfooding
> `closable` after #268's fix made it runnable again.

## The observation

`upstream.py closable` reports, on this repo today:

```
86 mapped upstream issue(s); 45 closable by beads; 1 actionable (also OPEN upstream)
```

Broken down by drift direction:

| Direction | Count | Reported? |
| :-- | --: | :-- |
| Issue **OPEN**, all mapped beads **closed** — the forward case | **1** | **Yes** — `closable` proposes a `gh issue close` |
| Issue **CLOSED**, one or more mapped beads still **open** — the reverse case | **17** | **No** — rendered `[not-actionable]` and otherwise silent |

Examples: `#119 [CLOSED] (still open: yf-252c)`, `#120 [CLOSED] (still open: yf-297v)`,
`#122`, `#123`, `#124` — 17 in total.

**`closable` is doing exactly what it says.** Its job is to propose closes, and a closed issue is
not closable. The reverse rows are visible in its output only incidentally. **No verb reports the
reverse direction as a finding**, so 17 instances have accumulated without ever being surfaced.

## Why this is worth investigating rather than fixing

**It is not obvious that the reverse case is a defect at all**, and the answer determines whether
anything should change. At least four readings fit the same data:

1. **Benign and expected.** Coarse granularity (`AGENTS.md`: one tracker per plan-scale effort)
   means an issue maps to many beads. Closing the tracker when the *effort* is done, while
   follow-on beads remain open, may be correct — the beads outlived their tracker on purpose.
2. **Real drift.** The issue was closed prematurely and the open beads are unfinished work now
   invisible upstream. If so, closing the tracker deleted the only external signal for them.
3. **Stale mapping.** The beads are effectively dead but never closed locally, so the mapping is
   the stale artifact rather than either endpoint.
4. **A hoist artifact.** Follow-on hoisting closes beads with a `bd close -r` tombstone; a
   partially-completed hoist could leave this shape.

**These have different remedies and two of them are "do nothing."** Filing a fix now would encode a
guess about which one is true.

## Suggested investigation

1. **Classify the 17 by hand** against the four readings above. This is the whole investigation —
   everything else follows from it.
2. **Check whether the population is growing.** A stable 17 accumulated over the project's life is
   a different fact from 17 accrued this quarter.
3. **Establish which endpoint is authoritative.** `UPSTREAM_TRACKING.md` treats upstream as *"the
   authoritative worklist"* on status/pull — if that holds, a closed issue with open beads means the
   BEADS are stale, and the remedy points local, not upstream. That inverts the intuitive reading
   and should be settled before any verb is written.
4. **Only then** decide whether a `drift` report earns its place, and in which skill.

## What NOT to do

**Do not auto-close the beads**, and do not auto-reopen the issues. Both are outward-facing or
destructive on a population whose meaning is not yet established, and the forward direction is
already deliberately propose-only for the same reason.

## Context

Surfaced by `closable` running in **2.90s** after #268's fan-out fix — the verb `REQ-BUP-052` was
written for and which #268 had made unusable. The observation is a side effect of the fix making
the verb runnable again, which is itself worth noting: **an unusable diagnostic hides its own
findings**, and nobody knew these 17 existed.

## Related

- #268 — the fan-out fix that made `closable` runnable
- #280 — `detect_followons`' `narrow` set permanently empty; the follow-on hoist path is implicated
  in reading 4

🤖 Generated with [Claude Code](https://claude.com/claude-code)

