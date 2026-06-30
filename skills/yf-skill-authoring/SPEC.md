# SPEC — Skill Authoring (`yf-skill-authoring`)

> **Status: Active.** Per-skill SPEC for the skill-authoring conventions. The `yf-skill-authoring` rename is complete and the
> skill is shipped; this SPEC tracks the live behavior. Requirements use RFC-2119 "shall"; composed
> by the root `SPEC.md` macro spec.

## 1. Purpose & scope

`yf-skill-authoring` is the conventions skill for authoring Claude Code **skills, agents, and
instruction files**: directory layout, the inline-vs-script threshold, modularization, the
**token-efficient writing ruleset** (the canonical Cut/Keep/Extract rules other skills reference),
the Skill Surface Convention, **Python helper conventions** (uv invocation discipline, PEP 723
inline deps, argument parsers), the canonical agent-role vocabulary, and the read-only review
sequence. It is `user-invocable: false` — a conventions reference applied when authoring skill-dir
content. It is the **single source of truth for the token-efficiency ruleset**.

**In scope:** skill-dir instruction files (a skill's `SKILL.md`, `agents/*.md`, a skill's own
`.{claude,agents}/rules/*`), the Surface Convention's seven-point contract, the script/modularize
thresholds, Python helper discipline, and the review-agent set.

**Out of scope:** **project-root** instruction files (`CLAUDE.md`, `AGENTS.md`, `AGENTS/*` NOT
inside a skill dir, repo-root `.{claude,agents}/rules/*`) — those route to
`yf-optimal-instructions`. Also application code outside skills, end-user docs, the *structural*
project-root convention (AGENTS-primacy / CLAUDE-index — owned by `yf-optimal-instructions`),
and design-level skill planning (the planning skill). Content-agreement verification across edges
is `yf-drift-check`'s axis.

## 2. Requirements (`REQ-SKAUTH-NNN`)

### 2.1 Layout & thresholds

- **REQ-SKAUTH-001** a skill shall root at `.{claude,agents}/skills/<skill>/` with `SKILL.md` as
  the entry point and helpers/modules adjacent to it.
- **REQ-SKAUTH-002** *(testable)* the script threshold shall hold: inline glue stays inline;
  scripts >~25 lines or reused move to a file under the skill dir; logic >~200 lines factors into
  modules; CLI entrypoints use a real argument parser, never ad-hoc `sys.argv` slicing.

### 2.2 Token-efficiency ruleset (canonical — referenced by `yf-optimal-instructions`)

- **REQ-SKAUTH-010** *(testable)* this skill shall be the **single source of truth** for the
  Cut / Keep / Extract token-efficiency ruleset; other skills (notably `yf-optimal-instructions`'
  K1) cite the "Token efficiency" § anchor and shall not restate it.
- **REQ-SKAUTH-011** the ruleset shall govern always-loaded context (`SKILL.md`, `CLAUDE.md`,
  `AGENTS.md`, `.{claude,agents}/rules/*`): **Cut** narrative/soft-guidance/decorative content,
  **Keep** literal templates / verbatim commands / behavioral & edge-case constraints / state
  transitions / agent output structures, **Extract** JSON-parsing bash and >~15-line one-phase
  behavior to scripts/agents.
- **REQ-SKAUTH-012** the *structural* project-root convention (AGENTS.md primary, CLAUDE.md a thin
  `@-include` index, behavioral rules in the rules subdir) is **owned by
  `yf-optimal-instructions`**, not here; this skill references it.

### 2.3 Skill Surface Convention (see `reference/SURFACE_CONVENTION.md`)

- **REQ-SKAUTH-020** *(testable)* a skill adopting the Surface Convention shall adopt all seven
  points or none: (1) companion rules sourced from `protocols/<NAME>.md`, installed by the repo
  installer to the scope+surface rules dir, never to `AGENTS/`, never editing `CLAUDE.md`;
  (2) a `protocols/manifest.json` hash manifest with the six preflight outcomes; (3) committed
  `.<skill>.json` + gitignored `.<skill>.local.json` config; (4) runtime state under `.state/<skill>/`
  only; (5) hook installation via `hooks/manifest.json` merged by `<skill> init`; (6) enumerated
  anchored gitignore entries; (7) the preflight contract (checks + idempotent scaffold).
- **REQ-SKAUTH-021** *(testable)* an unknown `schema_version` in `protocols/manifest.json` shall
  make preflight FAIL.
- **REQ-SKAUTH-022** config shall be operator decisions only; **state ≠ config**, and runtime
  state shall never be written under the skill source dir or under `.{claude,agents}/`.

### 2.4 Python helper conventions

- **REQ-SKAUTH-030** *(testable)* skill helper scripts shall run via `uv run` — never a direct
  `python` / `python3` call and never a manually activated virtualenv.
- **REQ-SKAUTH-031** single-file helpers shall declare dependencies inline via PEP 723
  (`# /// script ... ///`); escape to an explicit `uv venv` + `requirements.txt`/`pyproject.toml`
  inside the skill dir only when dep count >~10 or specific pins matter.
- **REQ-SKAUTH-032** *(testable)* CLI argument parsing shall use `click`, `typer`, or stdlib
  `argparse` — never `sys.argv` slicing.
- **REQ-SKAUTH-033** helpers that persist runtime state shall write to `.state/<skill>/` resolved
  from a caller-supplied `project_root`, not a hardcoded cwd.

### 2.5 Agent roles & review (see `reference/AGENT_ROLES.md`, `reference/PIPELINE.md`)

- **REQ-SKAUTH-040** every agent in a multi-agent skill shall map to exactly one of six canonical
  roles (GATHER, PRODUCE, EVALUATE, REVISE, ORCHESTRATE, CLOSEOUT) and carry a front-matter block
  declaring it; EVALUATE agents additionally carry a `stance` (`reviewer` | `red-team`); the
  bead-DAG driver is always `coordinator`.
- **REQ-SKAUTH-041** the review sequence shall be three read-only agents dispatched via the Agent
  tool, the caller applying fixes: `reviewer` (general), `reviewer-tokens` (skill-dir
  instruction-file token efficiency), `red-team` (adversarial); for Python helpers, also
  `reviewer-python`.
- **REQ-SKAUTH-042** *(testable)* every markdown file a skill ships (`SKILL.md`, `agents/*.md`,
  `README.md`, `spec/*.md`, `reference/*.md`) shall be plain **GFM** — never Obsidian
  `[[wikilinks]]` or `![[embeds]]`, GFM links and tables (explicit alignment markers) only — and
  every authored/edited `.md` shall be linted with the `yf-markdown-lint` authoring subset
  (`ML001,ML002,ML005,ML006,ML007,ML008`) with all violations resolved before the skill is
  considered done; this lint gate is part of the review sequence (REQ-SKAUTH-041), not optional.

### 2.6 Spec diagrams (conditional)

- **REQ-SKAUTH-050** when a diagram aids a skill's `SKILL.md`/spec, the author SHOULD use the
  `yf-diagram-authoring` skill, co-resident at `skills/<name>/spec/<slug>.{d2,png}`, referenced
  from the README by relative path; this is conditional (no `depends-on-skill` edge), degrading to
  prose if `d2` is absent. A new `spec/<slug>.{d2,png}` must be listed in the README layout fence
  (the `e-readme-layout` `field-set-equal` coupling).

### 2.7 Routing

- **REQ-SKAUTH-060** **project-root** instruction files (`CLAUDE.md`, `AGENTS.md`, `AGENTS/*` not
  inside a skill dir, repo-root `.{claude,agents}/rules/*`) shall **route to
  `yf-optimal-instructions`**; this skill owns only **skill-dir** instruction files. The two
  skills' `description` fields are mutually exclusive on this axis.

## 3. Interfaces

- **CLI / scripts:** `scripts/manifest_update.py` — recomputes companion-rule sha256, bumps semver,
  appends to `previous_versions[]`; each adopting skill vendors a copy into its own `scripts/`.
  No domain CLI (this skill is conventions, not a runtime engine).
- **Review agents:** `agents/reviewer.md`, `agents/reviewer-tokens.md`, `agents/red-team.md`,
  `agents/reviewer-python.md` — read-only, dispatched via the Agent tool; the caller applies fixes.
- **Companion rule:** **none** (the conventions are loaded on demand when authoring skill-dir
  content; there is no always-loaded trigger rule for this skill).
- **Config / state:** none for the skill itself; it *defines* the `.<skill>.json` /
  `.<skill>.local.json` / `.state/<skill>/` conventions that adopting skills follow.

## 4. Guardrails (`GR-SKAUTH-NNN`)

- **GR-SKAUTH-001** *Drift:* restating the token-efficiency ruleset, or claiming the project-root
  structural convention. *Rule:* this skill is the single source of the Cut/Keep/Extract ruleset;
  the AGENTS-primacy / CLAUDE-index structure is owned by `yf-optimal-instructions` and only
  referenced here. *Why:* one-source-of-truth — the ruleset must have exactly one home.
- **GR-SKAUTH-002** *Drift:* claiming project-root instruction files. *Rule:* this skill owns
  **skill-dir** instruction files; project-root files route to `yf-optimal-instructions`. *Why:*
  the two skills are mutually exclusive on the skill-dir vs project-root axis.
- **GR-SKAUTH-003** *Drift:* the review agents editing files. *Rule:* all review agents are
  **read-only**; the caller applies fixes. *Why:* auditable, deterministic review.

## 5. Verification

- The toolchain rules (REQ-SKAUTH-030/032) and the script threshold (REQ-SKAUTH-002) are checkable
  by linting/inspecting any adopting skill's helpers; the Surface Convention points
  (REQ-SKAUTH-020/021) by the preflight outcomes of an adopting skill. The single-source-of-truth
  invariant (REQ-SKAUTH-010, GR-SKAUTH-001) is verified by grep — the ruleset appears only here,
  cited (not restated) by `yf-optimal-instructions`. Each *(testable)* REQ is the anchor a
  plan-010 Epic 6 integration test names.

## 6. References

- `skills/yf-skill-authoring/SKILL.md` (layout, thresholds, Surface Convention summary, token
  efficiency §, Python helpers, agent roles, review sequence).
- `skills/yf-skill-authoring/reference/SURFACE_CONVENTION.md` (full seven-point contract + worked
  example), `reference/PORTABILITY.md` (`SKILL_DIR` resolution + portability checklist),
  `reference/PIPELINE.md` (multi-agent conventions), `reference/AGENT_ROLES.md` (role vocabulary,
  factoring test, front-matter schema, role table).
- `skills/yf-skill-authoring/agents/*.md` (the review agents); `scripts/manifest_update.py`.
- Root `SPEC.md` §4 (SKAUTH) and `GUARDRAILS.md` (GR-006, per-skill guardrails note).
