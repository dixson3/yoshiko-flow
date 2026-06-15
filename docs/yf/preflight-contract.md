# `yf preflight <skill>` — JSON contract

Status: CONTRACT (spec only). This document defines the output contract for the
`yf preflight` kernel command (plan-010 bead 2.1, **REQ-YF-PRE-001**). The Rust
implementation lands in later beads (2.2–2.6); bead 6.3's tests anchor to the REQ
ids cited throughout.

## 0. Provenance — what this must match

This contract is a **superset of, and bit-compatible with**, the legacy per-skill
Python `check` output, so `yf preflight <skill> --json` is a drop-in replacement
for `<skill>_manager.py check --json-output`. Every status string and field name
below was lifted verbatim from the actual legacy code (no invention):

- `skills/bdplan/scripts/plan_manager.py` — `_check_prerequisites()` (lines ~804–854),
  `_check_rule()` (~734–777), `check()` (~866–890), `_ensure_scaffold()` (~723),
  constants (lines 31–41, 125–127).
- `skills/bdresearch/scripts/research_manager.py` — `_check_prerequisites()`
  (~261–315), `_check_rule()` (~192–232), `_provider_warnings()` (~318–338),
  constants (lines 27–41, 120–122).
- `skills/yf-beads-init/scripts/beads_init.py` — `verify_beads()` (~106–185).

GUARDRAILS **GR-005**: the preflight kernel is shared *mechanism*, not skill
*domain logic*. Only tool/version, rule-hash, config/state, gitignore scaffold,
and beads-verify move into `yf`. Each skill's init/audit/pour/index/credibility
logic stays in that skill's Python.

## 1. CLI surface and exit codes (REQ-YF-CLI-003)

```
yf preflight <skill> [--json]
```

- `<skill>` (required) — the logical skill name, e.g. `plan`, `research`. The
  legacy scripts are mono-skill (`SKILL_NAME = "bdplan"` / `"bdresearch"`); the
  kernel selects the per-skill rule name, manifest, config, and state paths from
  this argument.
- `--json` — emit the JSON object of §3 to stdout, indented. (Legacy flag was
  `--json-output`; the kernel standardizes on `--json` per **REQ-YF-CLI-003**.)

Exit codes (**REQ-YF-CLI-003** — exit non-zero on failure). This reproduces the
legacy `check()` exit behavior exactly:

| Condition | Exit |
| :-- | :-- |
| `status == "ok"` | `0` |
| `status == "ignored"` | `0` (operator chose to ignore the skill) |
| any other status (`system_deps_missing`, `bd_not_initialized`, `rule_*`, `manifest_*`) | non-zero (legacy: `1`) |

Legacy nuance preserved: with `--json`, the legacy `check` always `sys.exit(0)`
after printing the JSON; the **status field**, not the process exit code, is the
machine-readable verdict in JSON mode. The kernel SHOULD follow **REQ-YF-CLI-003**
and exit non-zero on a failing status even in `--json` mode; consumers MUST treat
the `status` field as authoritative regardless. (Tests should pin the `status`
field, not rely solely on the exit code — this mirrors the **REQ-YF-PRE-006**
"parse the JSON, not the exit code" discipline.)

## 2. Status enum (the superset)

The full enum, exactly as the legacy Python emits it:

```
ok | ignored | system_deps_missing | bd_not_initialized |
rule_missing | rule_drift | rule_deprecated |
manifest_schema_unknown | manifest_missing
```

Note on the `rule_*` and `manifest_*` families: `_check_rule()` returns an
**outcome** (`ok | update_available | drift | deprecated | missing |
manifest_schema_unknown | manifest_missing`); `_check_prerequisites()` then maps
the *blocking* rule outcomes (`missing`, `drift`, `deprecated`) to the top-level
status by prefixing `rule_` (`rule_missing`, `rule_drift`, `rule_deprecated`).
The `manifest_*` outcomes pass through **unprefixed** (they are already top-level
status strings). The two **non-blocking** outcomes — `ok` and `update_available`
— both collapse to top-level `status == "ok"` (an `update_available` rule is
surfaced via `instructions`, not a distinct status). So the exact `manifest_*`
members the legacy code emits are precisely:

- `manifest_schema_unknown` — `protocols/manifest.json` exists but its
  `schema_version` != the code's `MANIFEST_SCHEMA` (= `1`).
- `manifest_missing` — `protocols/manifest.json` is absent / unreadable.

There are no other `manifest_*` strings in the legacy source.

### 2.1 When each status is returned, and what accompanies it

Evaluation order in `_check_prerequisites()` (short-circuits top to bottom):

| Status | Returned when | Source check | Accompanying fields |
| :-- | :-- | :-- | :-- |
| `ignored` | `_read_config()["ignore-skill"]` is truthy | operator config (**REQ-YF-PRE-004**) | `missing: []`, `instructions: []`, `rule: null` (research also: `warnings: []`) |
| `system_deps_missing` | `git`/`uv`/`bd` absent, or `bd` < `MIN_BD_VERSION` (1.0.5) — only when `prereqs-present` is not cached in state | tool/version probe (**REQ-YF-PRE-002**) | `missing: [..]`, `instructions: [..]`, `rule: null` (research also: `warnings`) |
| `bd_not_initialized` | tools OK but `bd status --json` raises (non-zero/not found) | beads check (**REQ-YF-PRE-006**; see §5 note) | `missing: []`, `instructions: ["Run: bd init"]`, `rule: null` (research also: `warnings`) |
| `rule_missing` | rule outcome `missing` — companion rule not found in any candidate dir | `_check_rule()` (**REQ-YF-PRE-003**) | `missing: []`, `instructions: [..]`, `rule: {outcome:"missing", rule}` |
| `rule_drift` | rule outcome `drift` — installed rule sha256 matches neither current nor any `previous_versions` hash | `_check_rule()` (**REQ-YF-PRE-003**) | `missing: []`, `instructions: [..]`, `rule: {outcome:"drift", rule, path}` |
| `rule_deprecated` | rule outcome `deprecated` — manifest entry has `deprecated: true` | `_check_rule()` (**REQ-YF-PRE-003**) | `missing: []`, `instructions: [..]`, `rule: {outcome:"deprecated", rule, path}` |
| `manifest_schema_unknown` | manifest `schema_version` != `MANIFEST_SCHEMA` | `_check_rule()` (**REQ-YF-PRE-003**) | `instructions: [..]`, `rule: {outcome:"manifest_schema_unknown", rule, schema_version}` |
| `manifest_missing` | `protocols/manifest.json` absent | `_check_rule()` (**REQ-YF-PRE-003**) | `instructions: [..]`, `rule: {outcome:"manifest_missing", rule}` |
| `ok` | tools OK, bd initialized, rule outcome `ok` or `update_available`; scaffold ensured | full pass (**REQ-YF-PRE-003/005**) | `missing: []`, `rule: {outcome:"ok"\|"update_available", ...}`, `scaffold_added: [..]`, `instructions: []` or update-available note |

`prereqs-present` caching: the system-deps + `bd status` block runs only when
`state["prereqs-present"]` is unset. Once it passes, `prereqs-present: true` is
written to state and that block is skipped on subsequent runs — so a warm repo
goes straight to the rule-hash check. The rule-hash check runs **every** time
(cheap). (**REQ-YF-PRE-004** — state under `.yf/<skill>/`.)

## 3. JSON object schema

Top-level object fields (`--json` mode). Presence varies by status as tabulated
in §2.1; the schema below is the union.

| Field | Type | Meaning |
| :-- | :-- | :-- |
| `status` | string (enum §2) | The verdict. Authoritative in JSON mode. |
| `missing` | array of string | Missing/outdated system deps. Non-empty only for `system_deps_missing` (e.g. `"git"`, `"uv"`, `"bd"`, `"bd>=1.0.5"`). Empty (`[]`) for every other status. |
| `instructions` | array of string | Human-readable remediation lines. Empty for `ok` (unless `update_available`) and `ignored`; one or more lines for every failing status. |
| `rule` | object \| null | The companion-rule verdict (see §3.1). `null` for `ignored`, `system_deps_missing`, `bd_not_initialized`. Always an object for `ok` and all `rule_*`/`manifest_*` statuses. |
| `scaffold_added` | array of string | Idempotent scaffold actions taken this run (e.g. `"gitignore /.yf/"`). **Present only when `status == "ok"`** (the scaffold runs only on an otherwise-ready project). Empty `[]` when nothing was added. |
| `warnings` | array of string | **bdresearch only** (see §6). Advisory, non-blocking search-provider notes. **Absent from bdplan output.** |

### 3.1 The `rule` object

Emitted by `_check_rule()`. Fields:

| Field | Type | Meaning | When present |
| :-- | :-- | :-- | :-- |
| `outcome` | string | One of `ok \| update_available \| drift \| deprecated \| missing \| manifest_schema_unknown \| manifest_missing`. | always (when `rule` is an object) |
| `rule` | string | The companion-rule filename — `"PLANS.md"` (bdplan) / `"RESEARCH.md"` (bdresearch). | always |
| `path` | string | Absolute path to the winning installed rule copy. | when a rule file was found (outcomes `ok`, `update_available`, `drift`, `deprecated`) — **not** for `missing`, `manifest_*` |
| `version` | string | The manifest's declared semver for the rule (e.g. `"1.0.0"`). | only for outcomes `ok` and `update_available` |
| `schema_version` | (any, usually int/null) | The manifest's `schema_version` as read. | only for outcome `manifest_schema_unknown` |

Outcome semantics (from `_check_rule()` / `outcome_for()`):

- `ok` — installed sha256 == manifest current `sha256`.
- `update_available` — installed sha256 matches an entry in `previous_versions`
  (an older shipped version; non-blocking — collapses to top-level `ok`).
- `drift` — installed sha256 matches neither current nor any previous version.
- `deprecated` — manifest entry has `deprecated: true`.
- `missing` — no rule file in any candidate dir.
- Candidate precedence: the user/global home rules dir is evaluated **before**
  the project copy; a correct global copy short-circuits (so no per-project copy
  is required). Best-outcome ranking is `ok < update_available < deprecated <
  drift`.

### 3.2 Concrete examples (Gate G2 parity states)

`ok` (bdplan, warm repo, current rule, scaffold already present):

```json
{
  "status": "ok",
  "missing": [],
  "rule": {
    "outcome": "ok",
    "rule": "PLANS.md",
    "path": "/Users/me/.claude/rules/PLANS.md",
    "version": "1.0.0"
  },
  "scaffold_added": [],
  "instructions": []
}
```

`system_deps_missing` (bd outdated, uv absent):

```json
{
  "status": "system_deps_missing",
  "missing": ["uv", "bd>=1.0.5"],
  "instructions": [
    "Install uv: https://docs.astral.sh/uv/",
    "Upgrade beads: bd upgrade (current: 1.0.2, required: >= 1.0.5)"
  ],
  "rule": null
}
```

`rule_drift` (installed PLANS.md diverges from the manifest):

```json
{
  "status": "rule_drift",
  "missing": [],
  "instructions": [
    "Installed PLANS.md diverges from the manifest — re-run the repo installer with --force (install.sh --force) to restore the shipped version, or resolve manually"
  ],
  "rule": {
    "outcome": "drift",
    "rule": "PLANS.md",
    "path": "/Users/me/project/.claude/rules/PLANS.md"
  }
}
```

(For the bdresearch skill, each example object additionally carries a
`"warnings": [...]` array — see §6.)

## 4. Legacy → yf parity mapping

Each legacy status, the exact Python check that produces it, and the yf kernel
responsibility (REQ cross-reference).

| Status / outcome | Legacy source (function) | Produced by | yf kernel responsibility |
| :-- | :-- | :-- | :-- |
| `ignored` | `_check_prerequisites()` | `_read_config()["ignore-skill"]` truthy | Read `.yf-<skill>.local.json` config — **REQ-YF-PRE-004** |
| `system_deps_missing` + `missing`/`instructions` | `_check_prerequisites()` | `shutil.which("git"/"uv")`, `_parse_bd_version()` vs `MIN_BD_VERSION=(1,0,5)` | Tool detection + min-bd-version enforcement — **REQ-YF-PRE-002** |
| `bd_not_initialized` | `_check_prerequisites()` | `subprocess.check_output(["bd","status","--json"])` raises | beads-init **verify** classification — **REQ-YF-PRE-006** (see §5) |
| `ok` / `update_available` rule outcome | `_check_rule()` → manifest sha256/semver compare | `_sha256(path)` vs `manifest.files[RULE].sha256` / `previous_versions` | Rule hash + semver vs embedded `manifest.json` — **REQ-YF-PRE-003** |
| `rule_missing` | `_check_rule()` → `_check_prerequisites()` prefix | no rule file in `_rule_candidates()` | Rule presence check — **REQ-YF-PRE-003** |
| `rule_drift` | `_check_rule()` → prefix | sha256 matches neither current nor previous | Rule hash drift — **REQ-YF-PRE-003** |
| `rule_deprecated` | `_check_rule()` → prefix | manifest entry `deprecated: true` | Rule deprecation — **REQ-YF-PRE-003** |
| `manifest_schema_unknown` | `_check_rule()` | `manifest.schema_version != MANIFEST_SCHEMA` | Manifest schema gate — **REQ-YF-PRE-003** |
| `manifest_missing` | `_check_rule()` | `protocols/manifest.json` unreadable | Embedded-manifest presence — **REQ-YF-PRE-003** |
| `scaffold_added` (field, status `ok`) | `_ensure_scaffold()` | gitignore anchors `/.yf/` written once per `SCAFFOLD_VERSION` | Idempotent gitignore scaffold — **REQ-YF-PRE-005** |
| (beads verify/repair) | `beads_init.py verify_beads()` / `repair` | `bd status --json` JSON `error`-key parse; repair sequence | beads-init verify (**REQ-YF-PRE-006**) + repair (**REQ-YF-PRE-007**) |

## 5. The `bd_not_initialized` ↔ beads-init verify relationship (REQ-YF-PRE-006/007)

The legacy preflight uses a **coarse** beads check: it simply runs
`bd status --json` and, if that raises, returns `bd_not_initialized`. This is the
naive exit-code path that **REQ-YF-PRE-006** explicitly corrects.

The richer classifier is `yf-beads-init`'s `verify_beads()` (the
dependency-verification home). Its verdict enum is **distinct** from the preflight
enum:

```
verify status ∈ { ok | deps_missing | not_initialized | corrupted }
```

with fields `status, tools_missing, repo_initialized, bd_functional, diagnostics,
remediations`. The load-bearing invariant (**REQ-YF-PRE-006**): it inspects the
**parsed JSON for an `error` key**, not the exit code — because `bd status --json`
can return an error JSON with exit code 0 (a pending schema migration blocked by a
dirty Dolt working set). So:

- `.beads/` absent **and** (`bd status` unparseable or has `error`) → `not_initialized`.
- `bd status --json` parses **and** has an `error` key → `corrupted` (initialized
  but wedged — the false-negative case the exit-code-only check would mislabel).
- parse OK, no `error` → functional (`ok`).

The repair sequence (**REQ-YF-PRE-007**, in `beads_init.py repair`): for
`corrupted`, `bd dolt stop → bd migrate schema → bd migrate`; plus idempotent
gitignore/hooks/perms/JSONL hardening and the local-only assertion.

Kernel responsibility: `yf preflight`'s coarse `bd_not_initialized` status MUST be
preserved for parity, but the kernel SHOULD route a failing beads check through
the beads-init verify classifier (the `error`-key parse) so an initialized-but-
wedged repo is classed `corrupted`, not `not_initialized`. Mapping the verify
verdict back to the preflight enum: verify `deps_missing` → preflight
`system_deps_missing`; verify `not_initialized` **or** `corrupted` → preflight
`bd_not_initialized` (the preflight enum has no `corrupted` member; the richer
verdict lives in beads-init's own `verify --json` output and its `diagnostics`/
`remediations`).

## 6. bdplan vs bdresearch `check` differences (the kernel must know)

The two legacy `check` outputs are **identical in status enum, evaluation order,
and the `missing`/`instructions`/`rule`/`scaffold_added` fields**, with these
differences:

1. **`warnings` field (research only).** `research_manager._check_prerequisites()`
   computes `warnings = _provider_warnings()` and includes a `"warnings"` array in
   **every** returned object (including `ignored`, `system_deps_missing`,
   `bd_not_initialized`, `ok`, and the `rule_*`/`manifest_*` cases).
   `plan_manager` emits **no** `warnings` key at all. The kernel must make
   `warnings` a **per-skill, optional** field — present for `research`, absent for
   `plan` — to stay bit-compatible with each.
   - `_provider_warnings()` content (non-blocking, advisory): if the Exa MCP is
     not detected via `claude mcp list`, it appends
     `"Exa MCP not detected — falling back to API-key providers"` and, when the
     respective env vars are unset, `"TAVILY_API_KEY not set"` and/or
     `"PERPLEXITY_API_KEY not set"`. These are domain-specific to research and
     under GR-005 are skill domain logic; the kernel should treat `warnings` as an
     **opaque, skill-supplied** array (a plug-in axis), not bake provider checks
     into `yf`.

2. **`RULE_NAME` / config / state names** differ by skill (mechanical, driven by
   the `<skill>` argument): bdplan → `PLANS.md`, `.bdplan.local.json`,
   `.state/bdplan/`; bdresearch → `RESEARCH.md`, `.bdresearch.local.json`,
   `.state/bdresearch/`. Under the new `.yf/` naming (§7) these become per-skill
   `.yf-<skill>.local.json` and `.yf/<skill>/`.

3. Everything else (`MIN_BD_VERSION=(1,0,5)`, `MANIFEST_SCHEMA=1`,
   `SCAFFOLD_VERSION=1`, the `_RULE_INSTRUCTIONS` text, exit behavior) is the same
   between the two.

## 7. New `.yf/` paths vs legacy (REQ-YF-PRE-004, REQ-YF-MIGRATE-001)

Under plan-010 **decision C**, config and state move into a single `.yf/` tree:

| Purpose | Legacy path | New `yf` path | REQ |
| :-- | :-- | :-- | :-- |
| Per-skill operator config | `.<skill>.local.json` (e.g. `.bdplan.local.json`) at repo root | `.yf-<skill>.local.json` | **REQ-YF-PRE-004** |
| Per-skill runtime state | `.state/<skill>/` (e.g. `.state/bdplan/preflight.json`) | `.yf/<skill>/` (e.g. `.yf/plan/preflight.json`) | **REQ-YF-PRE-004** |
| Gitignore anchors | `/<config-file>`, `/.state/` (per-skill, enumerated) | `/.yf/` (single anchor) | **REQ-YF-PRE-005** |

Note the skill rename (**REQ-YF-RENAME-001**): `bdplan → plan`, `bdresearch →
research`, so the new config/state use the short `<skill>` names (`.yf/plan/`,
`.yf/research/`).

Migration is one-time and idempotent (**REQ-YF-MIGRATE-001**): `yf` shall migrate
legacy `.state/<old>/` → `.yf/<new>/` and `.<old>.local.json` →
`.yf-<new>.local.json`. There are **no runtime aliases** (GR-009) — the migration
moves the files, the kernel reads only the new paths.

## 8. REQ index (for bead 6.3 tests)

- **REQ-YF-PRE-001** — status superset + `scaffold_added`/`instructions`, §2/§3.
- **REQ-YF-PRE-002** — tool detection + min bd version, §2.1/§4.
- **REQ-YF-PRE-003** — rule hash/semver vs `manifest.json`, §3.1/§4.
- **REQ-YF-PRE-004** — config `.yf-<skill>.local.json` + state `.yf/<skill>/`, §2.1/§7.
- **REQ-YF-PRE-005** — gitignore scaffold `/.yf/`, §3/§4/§7.
- **REQ-YF-PRE-006** — beads-init verify, `error`-key parse not exit code, §5.
- **REQ-YF-PRE-007** — beads-init repair sequence, §5.
- **REQ-YF-CLI-003** — every subcommand `--json` + non-zero on failure, §1.
- **REQ-YF-MIGRATE-001** — idempotent legacy→`.yf/` migration, §7.
- **GR-005** — shared mechanism, not skill domain logic, §0/§6.
