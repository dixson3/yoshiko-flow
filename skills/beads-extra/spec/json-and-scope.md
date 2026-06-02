# Spec: JSON parsing & scope boundary

## Requirements

- **REQ-JSON-001:** For status reports or eyeballing state, do not use `--json` — the
  human-readable `bd show`/`bd list`/`bd ready` output is the direct path. — *Rationale:*
  reaching for `--json` + ad-hoc `json.loads` is the common self-inflicted failure that yields
  bogus "?" reports. — *Verify:* SKILL.md "`--json` is not always a single JSON document" § opening.

- **REQ-JSON-002:** Never call `json.loads(stdin)` directly on `bd` output. `bd`'s `--json`
  may carry warning prefixes and may be a multi-document array (`bd show --json` returns an
  array even for one id). Parse defensively (first-balanced-block extraction, or array-aware
  iteration). — *Rationale:* a naive load raises `AttributeError`/`JSONDecodeError` and, if
  swallowed, produces a wrong report. — *Verify:* SKILL.md defensive-parse snippets; `bd show <id> --json`.

- **REQ-JSON-003:** Inside bdplan/bdresearch, prefer the manager script's hardened
  `json-get` extractor over a hand-rolled parser. — *Rationale:* one audited parser, not many.
  — *Verify:* SKILL.md reference to `plan_manager.py json-get`.

- **REQ-JSON-004:** Test-pattern titles (`bd create "TEST-…"`) prepend a multi-line warning
  that breaks naive parsers; use a real title or an isolated DB (`bd --db /tmp/…`). — *Rationale:*
  avoids polluting the project DB and corrupting JSON parses during tests. — *Verify:* SKILL.md
  "Test-data title warnings" §.

## Scope & documentation boundary

- **REQ-DOC-001:** This skill is the 1.0.5-verified layer and **wins** over the bundled
  `beads` plugin's pre-1.0.5 `resources/` where they disagree (named: `ASYNC_GATES.md` gate
  verbs; `CHEMISTRY_PATTERNS.md` bare `bd pour`/`bd wisp`/`bd mol catalog`). — *Rationale:* the
  plugin docs are stale; silent overlap would leave the contradiction unresolved. — *Verify:*
  SKILL.md "Corrects the bundled `beads` plugin docs" callout.

- **REQ-DOC-002:** Stable taxonomy the plugin documents correctly (the four dependency types
  in `DEPENDENCIES.md`; the lifecycle in `WORKFLOWS.md`) is **cited, not restated**; this skill
  keeps only mutation/gotcha mechanics the plugin lacks. — *Rationale:* one source of truth per
  fact. — *Verify:* SKILL.md "Dependency-edge mutation" § citation + "See also" plugin bullet.

- **REQ-DOC-003:** Routine `bd ready`/`bd show`/`bd update --claim`/`bd close` flows belong to
  the canonical `beads` skill, not here; authoring beads-backed skills belongs to
  `beads-authoring`. — *Rationale:* keeps this skill to the runtime-gotcha delta. — *Verify:*
  SKILL.md frontmatter SKIP + "See also".
