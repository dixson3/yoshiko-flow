# Upstream #67: Migrate legacy root-level skill configs (.<skill>.local.json) into the .yf/ namespace

- **Number:** 67
- **Title:** Migrate legacy root-level skill configs (.<skill>.local.json) into the .yf/ namespace
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Problem

Skill **config** and skill **state** currently live in two different places with inconsistent conventions:

- **Config** (per-machine, gitignored, operator-authored): root-level dotfiles — `.<skill>.local.json`.
  Observed in the wild: `.yf-plan.local.json`, `.blog-publishing.local.json`.
- **State** (runtime cache, tool-written): already namespaced under `.yf/<shortname>/…` —
  e.g. `.yf/plan/preflight.json`, `.yf/research/preflight.json`, `.yf/beads-init/preflight.json`
  (note the state dir drops the `yf-` prefix: `.yf/plan/`, not `.yf/yf-plan/`).

Root-level `.<skill>.local.json` files clutter the repo root, don't group with their skill's state, and each new skill adds another top-level dotfile + its own gitignore anchor.

## Proposal

Migrate config into the same `.yf/` namespace as state. Two candidate patterns (the exact shape is TBD — flagging both):

1. `.yf/<skill>/config.local.json` — **preferred**: co-locates config beside the skill's existing `.yf/<skill>/` state dir; one directory per skill holds everything. A single `.yf/` gitignore anchor (plus per-file rules for the tool-written state that *should* be ignored) covers all skills.
2. `.yf/<skill>.config.local.json` (flat) — fewer directories, but splits config from the `.yf/<skill>/` state dir.

Recommendation: **(1)**, for consistency with the existing `.yf/<shortname>/` state layout. Confirm the `<skill>` vs `<shortname>` (prefix-stripped) form to match the state-dir convention.

## Scope / considerations

- **Backward-compat shim:** resolve new path first, fall back to the legacy root-level `.<skill>.local.json` if present, so existing checkouts don't break. Emit a one-time migration hint (or auto-migrate on write).
- **Affected skills:** at minimum `yf-plan` (`.yf-plan.local.json`) and `blog-publishing` (`.blog-publishing.local.json`); audit for others (`.markdown-lint-on-edit` marker, any `.<skill>.local.*`).
- **Surface Convention docs:** update the skill-authoring "Surface Convention §6" guidance and the preflight-contract doc to point at the new config path.
- **gitignore:** consolidate the per-skill root anchors into `.yf/`-scoped rules; ensure operator config stays gitignored and tool state stays gitignored, without accidentally tracking either.
- **Migration helper:** a small `yf` subcommand or install-time step to move existing `.<skill>.local.json` → the new location.

## Origin

Surfaced while working in `dixson3/writing`: `.yf-plan.local.json` (config, root) sits apart from `.yf/plan/preflight.json` (state), which is the inconsistency this issue proposes to resolve.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
