# CLI Specification

Anchors the skill's invocation surface, the pre-flight gate, and the
`research_manager.py` CLI. Verified against SKILL.md and `scripts/research_manager.py`.

## Skill Invocation

REQ-CLI-001: The skill provides 4 subcommands: `init`, `<topic>` (new project), `coordinate`, `status`.
Rationale: Each maps to a distinct user intent; missing any leaves a workflow gap.
Verification: SKILL.md Invocation section lists all 4.

REQ-CLI-002: The skill triggers on `/yf-research` and on research-intent language when the output should be tracked, cited, or resumable.
Rationale: The explicit command is the reliable trigger; the intent language captures the common case.
Verification: SKILL.md `TRIGGER` line in frontmatter.

REQ-CLI-003: yf-research does NOT override the built-in `deep-research` harness; the two coexist and are routed by intent.
Rationale: The built-in is compiled into the CLI and cannot be suppressed; they serve different jobs (quick lookup vs tracked pipeline). A false override claim would be unenforceable and wrong.
Verification: SKILL.md frontmatter `SKIP` line; `protocols/RESEARCH.md` Routing section; `.agents/rules/RESEARCH.md` (installed copy).

## Pre-flight

REQ-CLI-004: Every invocation except `init` runs `yf preflight yf-research --json` and stops (directing to `init`) on any non-`ok`/`ignored` status.
Rationale: Running the pipeline without prerequisites — or against a drifted/missing rule — produces confusing failures. The preflight (config gating, state caching, installed-rule hash) moved out of `research_manager.py` into the `yf preflight` kernel in plan-010; the JSON contract is a superset of the legacy schema (same status values).
Verification: SKILL.md Pre-flight section (the `yf preflight yf-research --json` invocation and its status branches).

REQ-CLI-005: If `.yf-research.local.json` (repo root) contains `"ignore-skill": true`, the skill exits silently.
Rationale: Projects that can't satisfy prerequisites need a clean opt-out without repeated errors.
Verification: SKILL.md Pre-flight `ignored` branch; the `yf preflight` kernel returns `{"status": "ignored"}` for that config.

## research_manager.py CLI

REQ-CLI-006: `research_manager.py` exposes exactly 2 subcommands: `json-get`, `record-epic`.
Rationale: The manager is deliberately narrow. Preflight moved to the `yf preflight` kernel (plan-010), so the manager carries only a defensive `json-get` plus `record-epic` (the idempotent epic-pointer writer, ported from `plan_manager.py`). Research-directory and `_index.md` state stays in `index_manager.py`; citation/report tooling in `link_normalizer.py` and `credibility_scorer.py`.
Verification: `grep -c '@cli.command' scripts/research_manager.py` == 2.

REQ-CLI-007: `research_manager.py record-epic <research_dir> <epic_id>` writes/updates a single top-level `epic: <id>` line in `<research_dir>/plan.yaml` (replacing the commented `# epic: <id>` placeholder or an existing `epic:` line in place, else appending) and emits a JSON object with keys `epic_id` and `epic_field` (`written` when a line was replaced, `appended` when none existed). It is idempotent — re-running for the same epic leaves `plan.yaml` byte-identical.
Rationale: SKILL.md Phase 3 calls this to persist the durable resume pointer (REQ-ORCH-008) a crashed `coordinate` session reads to recover after the start gate is already resolved. Hand-writing the line risks a duplicate `epic:` key; the helper guarantees idempotency. (The legacy `check --json-output` schema this requirement formerly anchored moved with preflight to the `yf preflight` kernel in plan-010 — see docs/yf/preflight-contract.md — and is no longer a `research_manager.py` surface.)
Verification: the `record_epic` command in `scripts/research_manager.py`; its JSON echo (`epic_id`, `epic_field`); SKILL.md Phase 3 `record-epic` invocation.

REQ-CLI-008: `research_manager.py json-get` parses defensively — it extracts the first balanced JSON value (tolerating a warning prefix or a concatenated/array document such as `bd show --json`) and supports numeric keys as list indices.
Rationale: `bd` output is not always a single clean JSON document; naive `json.load` breaks on arrays/prefixes.
Verification: `_extract_first_json()` and `int(key)` list handling in `json_get`.
