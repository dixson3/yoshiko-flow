# exp-003: yf-drift-check shape reusable for yf-change-validation

## drift-check structure (the shape to mirror)

Fixed engine / per-repo markdown manifest split, fired by an always-loaded trigger rule,
executing via an isolated report-only sub-agent. Files: `SKILL.md`, `SPEC.md`,
`spec/{engine,schema,checks}.md`, `agents/drift-verifier.md`, `templates/manifest.md`,
`protocols/DRIFT-CHECK-TRIGGER.md`.

- **Manifest** = `DRIFT-CHECK.md`: §0 Status (`approved: yes|no`) + 7 ordered `##` sections.
- **Discovery** (precedence, first hit): `$GIT_ROOT/DRIFT-CHECK.md`, `.agents/rules/…`,
  `.claude/rules/…` (`SKILL.md:70-75`).
- **Approval gate:** approved iff §0 reads `approved: yes`; missing or unapproved = no approved
  manifest = **silent no-op** (`REQ-ENGINE-001/002`).
- **Bootstrap** (hybrid infer→approve→enforce, `SKILL.md:93-105`): infer a draft from what's on
  disk (never a hardcoded filename — the E4 lesson, `REQ-ENGINE-003`); present inert; operator
  sets `approved: yes`; engine enforces. Offered only on explicit invoke / first install.

## Reusable → `_shared/` (check-type-AGNOSTIC)

1. **Manifest discovery** (parameterize filename + precedence list).
2. **Approved-marker parse** (§0 `approved: yes`).
3. **The 3-state machine** (no-manifest / unapproved-draft / approved → first two = silent
   no-op) + bootstrap gated to explicit-invoke/first-install.
4. **Draft-and-gate scaffolding** (write inert draft, `approved: no`, never enforce unreviewed).
5. **Trigger-scope glob matching** (changed path → scoped IDs).
6. **Generic schema validators** (exactly-N-ordered-sections, referential closure,
   bounded-vocabulary).
7. **Report-only dispatch wrapper** + verdict-block parser.
8. **`tool_on_path` availability** (port `yf/src/tool.rs` semantics or shell `command -v`).

## Stays per-skill (check-type-SPECIFIC)

- Manifest **schema content** (drift = nodes/edges/contracts; change-validation = toolchain
  validation recipe: layered fast/full commands + trigger points).
- **Check taxonomy** (agreement vs validity).
- **Inference source** (file-graph vs toolchain).
- **Verdict-acting policy** (drift's fixed-authority CONFLICT vs validation PASS/FAIL).
- **Run vs read-only:** drift-verifier is read-only (Read/Grep/Bash); a validation runner
  **executes** build/test/lint — so it is NOT report-only. INCONCLUSIVE = tool not installed /
  can't run here (why the tool-availability primitive matters).

## Toolchain inference — net-new

**No repo-toolchain-recipe inference exists.** `yf/src/tool.rs` only does PATH lookup
(`resolve_tool`/`tool_on_path`); tools are **declared** via `depends-on-tool` frontmatter, not
inferred. Nothing reads `Cargo.toml`/`package.json`/`pyproject.toml`/`justfile`/`Makefile` to
derive a recipe. So #27's "infer the validation recipe from the toolchain" (Cargo→cargo
build/test/clippy, package.json scripts→npm run, pyproject→pytest/ruff, just/Make target
enumeration) is the substantive net-new build. Follow drift's "infer from what exists on disk,
never a hardcoded filename" discipline, applied to build-tool manifests. `tool_on_path` is the
availability primitive to confirm a proposed tool is installed.

## Dispatch pattern

`agents/drift-verifier.md` (`role: verify`), spawned `subagent_type="general-purpose"` with
MANIFEST + SCOPED_EDGES + CHANGED_PATHS + evidence standard; returns a parseable
PASS/FAIL/INCONCLUSIVE/CONFLICT block. yf-change-validation mirrors the wrapper but its runner
executes recipes and returns PASS/FAIL/INCONCLUSIVE per step (no CONFLICT bucket).
