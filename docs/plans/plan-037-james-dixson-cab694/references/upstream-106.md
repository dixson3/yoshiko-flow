---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #106: yf-beads-upstream: SKILL.md Push step §3 instructs hand-running 'bd github push' — contradicts the never-hand-run safety invariant

- **Number:** 106
- **Title:** yf-beads-upstream: SKILL.md Push step §3 instructs hand-running 'bd github push' — contradicts the never-hand-run safety invariant
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

The `yf-beads-upstream` **companion rule** (`protocols/UPSTREAM_TRACKING.md`, always-loaded) states the safety invariant:

> **Route every upstream push through `/yf-beads-upstream` — do not hand-run `bd <backend>` push commands.** … If `/yf-beads-upstream` is unavailable, stop and report — do not substitute a hand-run push.

But the **SKILL.md "Push step §3"** literally documents the hand-run command as the procedure:

```
GITHUB_TOKEN=$(gh auth token) bd github push <id1> <id2> … --dry-run
GITHUB_TOKEN=$(gh auth token) bd github push <id1> <id2> …
```

So **following the skill as written = hand-running the very `bd github *` command the rule forbids.** An operator/agent obeying the skill violates the rule; there is no in-skill wrapper for the push step itself (only `hoist`/`land` in §7–§8 wrap it). This self-contradiction directly enabled a non-compliant hand-run in practice.

## Proposed fix

- Add a first-class **`upstream.py push --issues <csv> [--dry-run]`** subcommand that performs the scoped, dry-run-first, inline-auth push internally (the same machinery §8 `hoist` already emits), and rewrite Push step §3 to call **that**, never a bare `bd github push`.
- Alternatively, if the push step is *meant* to be the raw `bd <backend> push`, then the companion rule's "do not hand-run `bd <backend>` push commands" wording must be reconciled — but the cleaner resolution is to keep the invariant absolute and make the skill's own procedure honor it (no `bd github *` in operator-facing steps).
- Audit the SKILL.md for other operator-facing `bd github`/`bd gitlab`/`bd jira` invocations and route them through `upstream.py` too, so the "never hand-run `bd <backend>`" invariant is enforceable by following the skill rather than contradicted by it.

## Impact
The skill's documented happy path violates its own always-loaded safety rule. Anyone (human or agent) following §3 hand-runs `bd github *`.

Found while dogfooding on `dixson3/transcripts`. Related: the enumerate silent-0 bug (companion issue) is what made the push-step failure mode reachable.
