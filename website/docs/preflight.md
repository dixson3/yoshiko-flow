---
title: Preflight & Config
sidebar_position: 5
---

# Preflight & Config

Yoshiko Flow has a single shared **preflight/config kernel** inside `yf`. Every
beads-backed skill runs the same checks through `yf preflight <skill>` rather than
each skill reimplementing them (REQ-YF-PRE-001).

## What preflight does

`yf preflight <skill>` answers "is this skill ready to run here?" and returns a
single `status` from this enum (REQ-YF-PRE-001):

```
ok | ignored | system_deps_missing | bd_not_initialized |
rule_missing | rule_drift | rule_deprecated |
manifest_schema_unknown | manifest_missing
```

The checks, in evaluation order:

1. **Ignored?** — if the skill's config sets `ignore-skill`, return `ignored`
   (the operator chose to skip it). Exit code is 0 for `ignored`.
2. **System deps** — `git`, `uv`, and `bd` present, and `bd` ≥ 1.0.5
   (REQ-YF-PRE-002). Missing/outdated → `system_deps_missing`, with a `missing`
   list (e.g. `["uv", "bd>=1.0.5"]`) and remediation `instructions`.
3. **Beads initialized** — `bd status` works. If not, `bd_not_initialized`. The
   kernel parses the **JSON for an `error` key**, not the exit code
   (REQ-YF-PRE-006) — `bd status --json` can return an error JSON with exit 0
   (e.g. a wedged schema migration), and that initialized-but-wedged case must be
   classed corrupted, not "not initialized". Repair routes through
   [`yf-beads-init`](./skills.md).
4. **Companion rule** — the skill's always-loaded rule
   (e.g. `PLANS.md`, `RESEARCH.md`) is verified by sha256 + semver against the
   skill's embedded `manifest.json` (REQ-YF-PRE-003), yielding
   `rule_missing` / `rule_drift` / `rule_deprecated`, or the `manifest_*`
   statuses if the manifest itself is absent or has an unknown schema.
5. **Scaffold** — on an otherwise-ready repo the kernel idempotently writes the
   `/.yf/` gitignore anchor and reports it in `scaffold_added`
   (REQ-YF-PRE-005).

With `--json`, the **`status` field is authoritative** — consumers should test it
rather than the process exit code. The output object also carries `missing`,
`instructions`, a `rule` object, and `scaffold_added`.

## The `.yf/` state + config layout

Everything Yoshiko Flow writes per repo lives under a single `.yf/` tree, with
one gitignore anchor (`/.yf/`):

| Purpose | Path |
| :-- | :-- |
| Per-skill runtime state | `.yf/<skill>/` (e.g. `.yf/plan/preflight.json`) |
| Per-skill operator config | `.yf-<skill>.local.json` (e.g. `.yf-plan.local.json`) |
| Gitignore anchor | `/.yf/` (single entry) |

State is the kernel's runtime cache (REQ-YF-PRE-004). A `prereqs-present` flag is
written once the system-deps + `bd status` checks pass, so warm repos skip
straight to the cheap rule-hash check on later runs.

### The config file & `ignore-skill`

The per-skill operator config (`.yf-<skill>.local.json`) is **operator-owned**.
Its main lever is `ignore-skill`: set it truthy to make `yf preflight <skill>`
return `ignored` (and exit 0), opting a repo out of that skill's checks:

```json
{ "ignore-skill": true }
```

## The `rule` object

When `yf preflight` reports on the companion rule, the `rule` object carries:

- `outcome` — `ok | update_available | drift | deprecated | missing |
  manifest_schema_unknown | manifest_missing`.
- `rule` — the companion-rule filename (e.g. `PLANS.md`).
- `path` — the winning installed rule copy (when found).
- `version` — the manifest's declared semver (for `ok` / `update_available`).

The user/global rules dir is evaluated before the project copy; a correct global
copy short-circuits, so no per-project rule copy is required. An
`update_available` rule is non-blocking and collapses to top-level `status: ok`
(surfaced via `instructions`).

This per-rule manifest axis (semver + sha256) is **distinct** from the
whole-tree integrity marker that `yf skills status` / `yf doctor` compare — see
the [Command Reference](./commands.md).
