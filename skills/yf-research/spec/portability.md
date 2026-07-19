# Portability Specification

Anchors how the skill locates itself, ships its protocol, and stays runnable across
harnesses. Verified against SKILL.md, the agent files, and the script headers.

REQ-PORT-001: `SKILL_DIR` resolves via `find` over the root list `~/.claude/skills ~/.agents/skills "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" .claude/skills .agents/skills` (where `GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)`), returning the first `yf-research` directory. Both `.claude` and `.agents` are valid surfaces at user, workspace (git-root), and project scope.
Rationale: The skill may be installed on either surface at any scope; covering user, git-root, and project roots makes resolution work everywhere and independent of any `.claude/skills → ../.agents/skills` symlink. The git-root fallback replaces the hardcoded `/workspace` path so the workspace scope tracks the actual repo root; outside a git repo `GIT_ROOT` defaults to `.` so its entries alias the cwd-relative roots. Every root is quoted or literal — no reliance on unquoted word-splitting — so resolution is identical under bash and zsh.
Verification: grep the resolver line in SKILL.md and agent files; confirm the `GIT_ROOT=$(… || echo .)` line, the quoted `"$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills"` roots, and `-name yf-research`.

REQ-PORT-002: Skill-internal paths in SKILL.md use the `${SKILL_DIR}/` prefix. Agent files (spawned as subagents without `SKILL_DIR` in scope) ALSO self-resolve `${SKILL_DIR}` via the canonical resolver (REQ-PORT-001) and use `${SKILL_DIR}/` paths — NOT hardcoded surface paths.
Rationale: The orchestration layer resolves SKILL_DIR once; subagents do not inherit it, so each resolves it itself rather than hardcoding a surface, letting the same skill run on any surface or scope.
Verification: grep SKILL.md and `agents/*.md` for `${SKILL_DIR}/`; confirm zero `.agents/skills/yf-research/` or `.claude/skills/yf-research/` hardcoded paths remain in agent files.

REQ-PORT-003: All scripts are `uv run` PEP 723 scripts (inline `# /// script` dependency metadata); none are installed as packages.
Rationale: `uv run` resolves dependencies per-invocation, keeping the skill self-contained.
Verification: `# /// script` headers in `scripts/*.py`.

REQ-PORT-004: `protocols/RESEARCH.md` is the canonical routing/protocol source; the repo installer (`install.sh`) — not `/yf-research init` — installs a verbatim copy to a rules dir anchored by install scope and surface: user-scope → `~/.<surface>/rules/RESEARCH.md`, project-scope → `<git-root>/.<surface>/rules/RESEARCH.md` (`.claude` or `.agents`). Preflight resolves the rule across locations in precedence order (user/global `~/.<surface>/rules` first) and hash-checks it; a correct user-scope copy satisfies every project, and `install.sh --force` overwrites an existing rule.
Rationale: The skill carries its protocol (upgradeable with the skill); the project gets an always-loaded copy in the matching surface's rules dir so routing is in context without an `@import`; anchoring by scope shares a user-scope copy across all projects and keeps a `.claude` install out of an unrelated `.agents/` tree; installing at install time means the rule lands with the skill.
Verification: `install.sh` rule-copy step (`install_rules`); research_manager.py `_skill_surface()` + `_skill_scope()` + `_git_root()` + `_rules_dir()` + `_rule_candidates()` + `_check_rule()` (preflight hash check); `protocols/RESEARCH.md` header; the installed copy is byte-identical to the source.

REQ-PORT-005: The formula is staged transiently into `.beads/formulas/` for the pour and removed afterward.
Rationale: Keeps the formula's source of truth in the skill while satisfying `bd`'s fixed formula search path.
Verification: SKILL.md Phase 3 step 3 (`cp` then `rm`).

REQ-PORT-006: A completed research directory is self-describing — `plan.yaml` + `index.md` + `sources.json` let a cold reader (or a new session) resume without conversation history.
Rationale: Multi-session handoff requires the directory to stand alone.
Verification: `spec/data.md`; `/yf-research coordinate` reads the directory, not session state.

REQ-PORT-007 *(testable)*: A completed research bundle shall be an OKF-compatible **dir-form bundle** conforming to the **OKF-RESEARCH** member (`skills/yf-research/OKF-EXTENSION.md`), composed as OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ OKF-RESEARCH (`skills/yf-okf/SPEC.md` REQ-OKF-FAM-001). Every **non-reserved `.md`** in the bundle shall carry a parseable YAML frontmatter block with a non-empty `type` (the sole OKF MUST, REQ-OKF-003) and the `okf_spec: OKF-RESEARCH` member selector (REQ-OKF-030), placed **above the first `## ` heading** (REQ-OKF-010). `type` shall be assigned by path (first match wins): `Summary.md` → `Research Report`, `artifacts/*.md` → `Research Artifact`, `sources.md` → `Reference` (OKF-EXTENSION §1). `Summary.md` shall additionally dual-write its prose header fields as frontmatter keys (`idx`, `topic`, `created`, and SHOULD `status`) per OKF-EXTENSION §2/§4 (REQ-OKF-020).
Rationale: OKF frontmatter makes each bundle artifact self-typing and machine-discoverable by `check_conformance`, without displacing the human-readable prose header. Placement above the first `## ` keeps the content fingerprint stable (REQ-OKF-010).
Verification: `skills/yf-okf/scripts/okf.py check_conformance` over a packaged bundle reports zero errors; `skills/yf-research/OKF-EXTENSION.md` §1/§2/§4; Issues 4.2–4.3 implement the writers.

REQ-PORT-008 *(testable)*: The bundle's **non-`.md`** sidecars — `plan.yaml`, `sources.json` (and any `sources.<cluster>.json`), `diagrams/*.png`, `scripts/*.py` — shall be **excluded** from the frontmatter-`type` rule (REQ-OKF-060); `check_conformance` shall not flag them for missing frontmatter.
Rationale: These files are machine records, rendered assets, or code — never OKF concept docs — so the `type` MUST does not apply. Recording the exclusion keeps conformance-checking free of false positives.
Verification: `skills/yf-research/OKF-EXTENSION.md` §2a; `skills/yf-okf/SPEC.md` REQ-OKF-060.

REQ-PORT-009 *(testable)*: The bundle's reserved index shall be **`index.md`** (renamed from the legacy `_index.md`) — the OKF bundle listing (`#` heading + per-artifact bullets) — and the bundle shall carry a reserved **`log.md`** holding newest-first ISO-8601 pipeline history. Both reserved files shall carry **no `type` and no `okf_spec`** (REQ-OKF-031) and are exempt from REQ-PORT-007. The legacy `_index.md` was a single timestamped GFM table (`| Timestamp | Phase | Artifact | Description |`) that served **both** the artifact manifest and the update ledger; OKF splits those roles — the listing role becomes `index.md` (REQ-OKF-001) and the timestamped update-ledger role becomes `log.md` (REQ-OKF-002). `log.md` is scaffolded as a conformant skeleton by the base migrate, with the `_index.md`-ledger → `log.md` content split completed by the Epic-4 adapter (OKF-EXTENSION §1b/§5). The exact retained shape of `index.md` (bullet listing vs. table; where the per-entry `Phase` annotation lands) is the reconciliation decision recorded in OKF-EXTENSION §5, implemented by Issues 4.2–4.3.
Rationale: The single `_index.md` table conflated manifest and ledger; the OKF `index.md`/`log.md` split gives each a single writer and a stable format, and aligns the bundle with the family listing/log convention.
Verification: `skills/yf-research/OKF-EXTENSION.md` §1b/§3/§5; `skills/yf-okf/SPEC.md` REQ-OKF-001/002/031; Issue 4.3 enumerates the `_index.md` → `index.md` rename fan-out (`index_manager.py`, `link_normalizer.py`, packager, formula, `spec/`, tests).
