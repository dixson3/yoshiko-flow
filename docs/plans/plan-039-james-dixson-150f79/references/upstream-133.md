---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #133: yf-beads-upstream design: replace 'bd <backend> push' with gh-direct issue creation across push/hoist/land (bd reads beads, gh writes issues)

- **Number:** 133
- **Title:** yf-beads-upstream design: replace 'bd <backend> push' with gh-direct issue creation across push/hoist/land (bd reads beads, gh writes issues)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Proposal

Change the upstream mechanism to: **`bd` reads bead content, `gh` creates and updates issues, `bd update --external-ref` records the mapping.** Apply across all three write paths — `push`, `hoist`, and `land`.

Today every write path shells out to `bd github push` (≡ `bd github sync --push-only --issues <ids>`). That choice is **never justified anywhere in the repo** — `SPEC.md` presupposes it (REQ-BUP-030 "never a bare `bd <backend> sync`", REQ-BUP-031 inline auth) without arguing for it. It was inherited from bd 1.0.5 shipping the feature.

Everything below was measured in-session, not inferred.

## Measurement 1 — `external_ref` is the entire mapping; there is no hidden sync state

This was the blocking question: is `External:` a plain field, or does bd maintain a dedup index / sync table that hand-writing would desynchronize?

`yf-uz5k` was mapped to #92 **by hand** (`bd update --external-ref …`). bd never pushed that bead. Yet:

```
$ bd github push yf-uz5k --dry-run
  [dry-run] Would update in GitHub: OKF export-emit integration for yf-plan/research/incubator (deferred)
```

**`Would update`, not `Would create`.** Since bd never pushed it, no sync-table entry could exist — so the create-vs-update decision is driven by the field alone. Corroborating: `bd github status` reports only config (token/owner/repo), no last-sync or per-issue records; `bd dolt sql` is not exposed.

**Consequence:** writing the mapping ourselves is indistinguishable from bd writing it. The strongest argument for keeping bd is gone.

## Measurement 2 — what bd actually produces

Bead `yf-1656` → issue #132:

| Bead field | Issue |
| :-- | :-- |
| `title` | title, verbatim |
| `description` | body, **verbatim — bd adds nothing** |
| `issue_type: task` | label `type::task` |
| `priority: 2` | label `priority::medium` |
| `labels: [upstream-followup]` | passed through |
| — | `external_ref` written back |

No dependency graph, no bead metadata footer, no structure. The body is the description.

## Measurement 3 — the skill forbids bd's only unique capability

`bd github push` ≡ `bd github sync --push-only --issues`. What `sync` uniquely offers over a `gh` call is **bidirectional sync with conflict resolution** (`--prefer-newer` / `--prefer-github` / `--prefer-local`).

The skill's central safety invariant is **"never run a bare `bd <backend> sync`"** — GR-BUP-002. So the dependency is retained and then deliberately disabled from doing the one thing that justifies it, leaving bd as a one-directional issue creator with a field write-back. That is precisely what a small `gh` wrapper is.

## Measurement 4 — costs bd imposes today

- **Two network round-trips** (dry-run + real) vs one `gh issue create` that returns the URL. gh-direct is *fewer* network ops, not more.
- **#129 is an artifact of bd's CLI surface.** `sync --issues` takes **comma-separated** ids; `push` takes **positional space-separated** ids. Translating between the two produced a command matching zero beads at exit 0, which then tombstoned beads locally. A wrapper we own has no such trap.
- **The fail-closed guard is fragile because bd offers nothing better.** REQ-BUP-050 parses `Pushed N issues` — a human-readable string from a third-party binary, explicitly recorded as bd-version-dependent. `gh issue create` returns a URL; `gh --json` returns structured data.
- **Opaque field mapping.** `notes` and `design` silently do not sync (SKILL.md Push §6) — documented as a gotcha rather than fixed, because we do not own the mapping. Under gh-direct it becomes a choice.

## What must be reimplemented (~20 lines)

1. **Create-or-update on `external_ref`**: present → `gh issue edit <n>`; absent → `gh issue create` then `bd update <id> --external-ref <url>`. This is the idempotency that prevents duplicates.
2. **Label mapping**: `issue_type` → `type::<t>`, `priority` → `priority::<level>`, plus pass-through of bead labels. Keep the existing convention so already-pushed issues stay consistent.
3. **`--parent <id>` subtree walking**, if retained — bd currently does the descendant walk.

## Scope: all three write paths

`hoist` and `land` compose the same `bd` push into their emitted command sequences (`plan_hoist()` at `upstream.py`, three call sites). Migrating only `push` leaves two mechanisms coexisting with different failure modes and separator conventions — the exact condition that produced #129. **Do all three or none.**

## Open decisions for the plan

1. **Non-GitHub backends.** GitLab is an untested config-only stub; Jira is actively broken (#132 — `BACKEND_AUTH` has no jira entry, so `--backend jira` emits `GITHUB_TOKEN`). Options: (a) gh-direct for GitHub and leave gitlab/jira on bd — two mechanisms, the thing this proposal is trying to avoid; (b) `glab`-direct for GitLab, defer Jira; (c) declare GitHub the only supported backend and demote the others explicitly. Materially different scopes. Note #132 may be **mooted** by (b) or (c).
2. **The never-hand-run invariant needs rewording, not deletion.** GR-BUP-002 exists because a raw `bd <backend> sync` is *destructive* (re-imports every upstream issue as a duplicate bead). A raw `gh issue create` is not — worst case it creates an unmapped duplicate. The rationale changes, so `protocols/UPSTREAM_TRACKING.md` (restamped in plan-038, hash-pinned in `protocols/manifest.json`) must be revised and re-stamped in the same commit.
3. **What replaces the dry-run stage.** With bd, dry-run is how we preview *and* how we fail-closed. With `gh` there is no dry-run; the preview would be a locally-rendered plan, and verification becomes checking the returned issue number. Arguably better, but it changes REQ-BUP-050's shape.
4. **Migration of the `Pushed N issues` parse.** REQ-BUP-050's fail-closed guard is written against bd's output. Under gh-direct it becomes "did we get an issue URL back", which is structural rather than textual.

## Related

- **#117** (push is write-only, no `closable` for hand-filed trackers) — unaffected in principle, but `closable` reads `external_ref`, so it inherits whatever this changes.
- **#132** — possibly mooted depending on decision 1.
- **#129** (closed) — its root cause is bd's dual separator convention; gh-direct removes the class.
- **#106** (closed) — plan-038 routed SKILL.md through `upstream.py push`; this changes what that verb does internally, not the routing.

## Why now

plan-038 just made `upstream.py push` the single documented write path and routed all of SKILL.md through it. That means there is now **exactly one place** the mechanism lives — the cheapest moment to swap the implementation underneath it, before more callers accumulate.
