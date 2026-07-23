---
type: Finding
okf_spec: OKF-PLAN
---
# Finding: naba's `--harness` install model + what transfers to yf

**Source:** read-only investigation of `/Users/james/workspace/dixson3/naba` (`src/harness.rs`,
`skills.rs`, `skills_install.rs`, `cli.rs`, `docs/specifications/skills.md`) + yf's current
`install.rs` / `common.rs` / SPEC (main session, 2026-07-22).

## naba did this exact refactor (plan-008)

naba migrated `yf`-style `--surface` → **`--harness`** and is a near-perfect reference for the
**skills-install half**. Directly transferable:

1. **Harness-as-data descriptor table** (`harness.rs:40-81`) — one row per harness, keyed by `id`,
   with `user_subpath` / `project_subpath` / `name_transform`. Adding a harness = one row + a SPEC
   row. yf should replace its `Surface` enum with this.
2. **Path data (reuse verbatim, with naba's own caveats):**

   | harness | user subpath | project subpath | note |
   |:--|:--|:--|:--|
   | `claude-code` | `.claude/skills` | `.claude/skills` | — |
   | `opencode` | `.config/opencode/skills` | `.opencode/skills` | user root is `~/.config/opencode` |
   | `pi` | `.pi/agent/skills` | `.pi/skills` | `name_transform: lowercase-hyphen,max64` |
   | `codex` | `.agents/skills` | `.agents/skills` | mapped to `.agents` — "unverified against OpenAI docs" |
   | `agents` (portable) | `.agents/skills` | `.agents/skills` | — |

3. **`--surface` → `--harness` deprecation alias** (`surface_alias()`: `claude`→`claude-code`,
   `agents`→`agents`, passthrough else) + **fallback-to-legacy `.<id>/skills`** for unknown ids.
4. **Repeatable `--harness` + dedupe by resolved absolute path** — codex and agents both resolve to
   `.agents/skills`, so dedupe is mandatory; the registry keys on the `(harness, scope, path)` triple.
5. **SPEC↔code parity test** (`harness.rs:154-223`) — parses the SPEC table and asserts it equals
   the shipped descriptor. Strong fit for yf's SPEC-first + drift-check culture; a model for the
   `yf-8ayq`/doc-agreement work too.
6. **Install registry** (`skills-install.json`, keyed `(harness, scope, path)`) for flag-free
   `upgrade` re-hitting all prior targets, with legacy disk-scan migration.

## What naba does NOT have (net-new for yf)

1. **No rules/instructions axis.** naba deploys only the on-demand skill tree — no aggregated rules
   file, no global-AGENTS.md, no always-loaded surface. yf's descriptor row must grow **beyond**
   naba's single skills path: it needs a **rules/instructions target** per harness. **Note:** yf
   *already* aggregates `YOSHIKO_FLOW.md` from acted-on skills' `protocols/` at install
   (`common.rs::install_rules_aggregate`, REQ-YF-FLOW-001..006) — unlike naba. The per-harness
   global-rule targets (codex `~/.codex/AGENTS.md`, opencode `~/.config/opencode/AGENTS.md`, pi
   `~/.pi/agent/`, claude `~/.claude/rules/`) are the new mapping.
2. **No config tuning.** naba never writes a harness `settings.json`/`config.toml`. yf's `yf harness
   tune` has no naba analogue — the config-engine + profile work stays net-new (this plan's Epics
   2–3 + revert). naba's **clean boundary** (install writes only skill files, never config) is a
   useful principle to preserve: keep `tune` a distinct opt-in step, not silently coupled into
   install.
3. **No auto-detection.** naba never probes which harnesses are installed (its only disk scan is the
   narrow legacy-registry migration). yf's requested **harness auto-detection** is designed fresh:
   user-scope by probing each harness's home dir / binary on `PATH`; project-scope by dot-dir
   presence (`.claude`/`.opencode`/`.agents`/`.pi`).
4. **Single skill vs ~20.** naba ships one skill; pi's `lowercase-hyphen,max64` name transform is
   inert for `naba` but would actually bite yf's longer names (`yf-change-validation`, …) — validate
   against pi's real limit.

## yf-current facts that shape the refactor

- `yf skills` today: `--scope {user,project} × --surface {claude,agents}` (REQ-YF-CLI-002);
  destination resolution REQ-YF-INSTALL-002; `--target` overrides.
- Install **already** aggregates `YOSHIKO_FLOW.md` from acted-on skills' `protocols/` sections
  (`install_rules_aggregate` / `fold_standalone_rules`, REQ-YF-FLOW-001..006).
- **`--tune` opt-in already exists** (REQ-YF-TUNE-010): `yf skills install --tune` runs
  `tune_for_install` post-install; without `--tune`, no settings file is touched.

## Design implications (carried into Approach)

- Replace `Surface` with a naba-style **harness descriptor table** (claude-code, codex, opencode,
  pi, agents), extended with **two** yf-specific targets per row: `skills_subpath` **and**
  `rules/instructions target`. `--surface` becomes a deprecated alias.
- **Rule optimization moves into `yf harness tune`** (operator directive): treat `protocols/` as a
  per-harness tuning strategy — tune minimizes the always-loaded surface (protocols → YOSHIKO_FLOW.md
  → minimized global rules/AGENTS.md) per harness. Install still lays down skills (+ the raw
  aggregate where applicable); the *harness-aware minimization/placement* is tune's job.
- **Config tuning** = claude-code + codex + opencode; **Pi config deferred** (still `[uncertain]`).
  But **Pi IS supported for skills install** (skills + rules), using naba's pi path data.
- **`--tune` stays opt-in** (there is a legitimate skills-only case: an operator who does not want yf
  editing their harness config). Assessment (operator's question): install and tune should remain
  *separable* — but `--tune` is the one-shot convenience, and auto-detect defaults make first-run
  easy (`yf skills install --tune` with no `--harness` = install + tune every detected harness).
- **Auto-detection** (net-new): no `--harness` → detect installed harnesses (user: home dir /
  `PATH` binary; project: dot-dir presence) and act on all detected; explicit `--harness` overrides.
