---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #105: yf-beads-upstream: enumerate silently returns 0 when bd auto-assigns an owner (owner_on_create unset) — must fail loud

- **Number:** 105
- **Title:** yf-beads-upstream: enumerate silently returns 0 when bd auto-assigns an owner (owner_on_create unset) — must fail loud
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/105
- **State:** CLOSED
- **Labels:** 

## Body

## Summary

`upstream.py enumerate` (the land-the-plane push-candidate discovery) **silently returns `0 candidates`** in a repo where `bd create` auto-assigns an `owner`, whenever `custom.upstream.owner_on_create` is unset. Every open bead is misclassified as *claimed → active → excluded*. A silent empty result directly invites the operator/agent to conclude "nothing to push" or to improvise — in a real session it led to a hand-run `bd github push` (the exact anti-pattern the safety invariant forbids).

## Root cause

- `enumerate_candidates()` (skills/yf-beads-upstream/scripts/upstream.py) defines push candidates as the **NON-ACTIVE** set from `classify_active`. A bead with a non-empty `owner` is treated as **claimed → active** and excluded.
- `owner_on_create()` is **default-DENY**: `custom.upstream.owner_on_create` unset/empty/`false` → `False`. So in a repo where `bd create` auto-assigns `owner` (e.g. `owner = user@example.com` on every new bead), **all** open beads are owner-claimed → active → excluded → enumerate returns `[]`.

## Repro (bd 1.1.2)

```
$ bd list --status open --json | jq length          # 3 open beads, all owner=<user>
3
$ uv run skills/yf-beads-upstream/scripts/upstream.py enumerate
0 candidate(s) (open/blocked/deferred); 0 not yet mapped:
```
Setting `custom.upstream.owner_on_create true` is the current workaround, but it is undocumented in the Push step and buried in a code comment.

## Proposed fixes

1. **Fail loud, never a silent 0 (primary).** When enumerate would exclude open beads *solely* because of owner-claim while `owner_on_create` is unset, emit a clear warning to stderr and/or the JSON, e.g. `"N open bead(s) excluded as owner-claimed; if bd auto-assigns owners here, set custom.upstream.owner_on_create true"`. Never return a bare `0 candidates` when `bd list --status open` is non-empty without saying why.
2. **Auto-detect owner-on-create.** If every open bead shares a single `owner` equal to the configured bd/git user, treat it as auto-owner (i.e. behave as `owner_on_create=true`) rather than reading them all as claims.
3. **Surface the knob at init.** Have `yf-beads-init` / `yf-beads-upstream init` set `custom.upstream.owner_on_create true` when it detects `bd create` auto-assigns an owner, and document the knob in SKILL.md §5 (currently only `granularity` / `auto_hoist_followons` are listed there; `owner_on_create` lives only in code).

## Impact
Land-the-plane upstream push finds nothing in any auto-owner repo, defeating the whole close-time hoist and inviting non-compliant hand-runs.

Found while dogfooding on `dixson3/transcripts` (bd 1.1.2).
