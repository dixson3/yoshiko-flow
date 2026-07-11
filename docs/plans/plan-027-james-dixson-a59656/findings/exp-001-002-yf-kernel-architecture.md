# exp-001/002: yf preflight/doctor architecture, scope model, seam, SPEC surface

**Questions:** How is `yf` preflight/doctor built, what is its user-scope vs project-scope model,
where does a formula-resolvability check hook in, and should it be static or runtime?

## exp-001 — Architecture & scope model

**Two surfaces, two shapes:**
- **`yf preflight <skill>`** (`yf/src/preflight.rs`) — a **linear short-circuit pipeline**
  (`run_with_env`, `:259`), not a registry: ignore → cache → system-deps → bd-init → rule-hash →
  gitignore-scaffold, producing `Outcome { status, missing, rule, scaffold_added, instructions }`.
  Per-skill config comes from the `preflight:` **frontmatter descriptor** (`frontmatter.rs:36`),
  read from the **embedded** SKILL.md.
- **`yf doctor`** (`yf/src/cmd/doctor/`) — a real **`Check` trait registry** (`check.rs:79`).
  `checks()` (`checks.rs:215`) assembles `Vec<Box<dyn Check>>` and loops over
  `frontmatter::load_skills()` pushing per-skill `SkillCheck` + `RuleCheck` (`checks.rs:239-252`).
  **Adding a check is a one-line push here** — the documented extension pattern.

**Scope model — the pivotal finding.** "Which skills exist" comes from the **embedded tree**
(`rust-embed`-compiled into the binary, `embed.rs:30-35`), **not** filesystem globbing. There is
**no dir-globbing over `~/.claude`, `~/.agents`, `<git-root>/.claude`, `<git-root>/.agents` to
discover installed skills.**
- `yf doctor` **hardcodes a single scope+surface**: `dirs_from(Scope::User, Surface::Claude)`
  (`mod.rs:41`); `DoctorArgs` has no `--scope`/`--surface` flag.
- `yf preflight` reads the *embedded* SKILL.md for the skill under test; it enumerates both scopes
  **only for rules** (`Env.rule_dirs`, `preflight.rs:182-193`), not skills/formulas.
- **Net: no existing check enumerates installed skill dirs across both scopes.** The requirement's
  literal "validate BOTH user- and project-scope per-repo" has **no filesystem precedent**.

**Formulas are embedded & cleanly addressable.** basename == internal `formula = "<name>"` key ==
`bd mol pour|wisp <name>` arg (e.g. `plan-execute.formula.toml` ↔ `formula = "plan-execute"` ↔
`bd mol pour plan-execute`). The SKILL.md staging is a fixed `cp/rm` bracket around the pour
(`skills/yf-plan/SKILL.md:305-309, 648-650`; `skills/yf-research/SKILL.md:263-266`). So a static
check has an exact, greppable contract: every `bd mol (pour|wisp) <name>` needs (a) an embedded
`formulas/<name>.formula.toml` and (b) a preceding staging reference.

**SPEC surface (root `SPEC.md`, not per-skill):** preflight REQs §3.5 `REQ-YF-PRE` (highest -010 →
new `REQ-YF-PRE-011`); doctor REQs §3.6 `REQ-YF-DOCTOR` (highest -003 → new `REQ-YF-DOCTOR-004`);
plus the SPEC.md living-amendment-log entry. A new preflight **status** also needs
`docs/yf/preflight-contract.md` §2 enum (`:58-76`) + returns table.

## exp-002 — Check form: recommendation

**Recommend STATIC as the core**, hosted as a new doctor `Check` (`FormulaCheck`) beside
`RuleCheck`, reading the **embedded tree**. Do **not** build a bd-invoking runtime proto-resolution
check. Reasoning:
1. The failure mode is a **static authoring defect** — fully determinable from the shipped
   SKILL.md + `formulas/` dir. No bd, no `.beads/`, CI-friendly, matches how `RuleCheck` hashes
   embedded content.
2. **Embedded == both scopes, for free.** Install is a verbatim byte-identical copy (`deploy_skill`,
   `common.rs:100`), and the §3.4 marker health axes (`complete`/`unmodified`) already prove the
   installed copy matches. So **a static check over the embedded tree transitively covers user- and
   project-scope installs** without the 4-way enumeration that doesn't exist.
3. A **runtime** check has nothing stable to resolve — staging is transient by design (`cp`
   immediately precedes the pour, `rm` immediately follows); at rest `.beads/formulas/` is empty.
4. **Seam:** new `FormulaCheck` in `checks.rs`, pushed in the per-skill loop (`:239-252`) beside
   `SkillCheck`/`RuleCheck`, guarded by "skill ships a `formulas/` dir". Optionally mirror as a
   preflight pipeline step (new status `formula_unresolvable`, +contract §2 edit, +`REQ-YF-PRE-011`).

**On the literal "both scopes on disk":** genuine installed-copy sweep across the 4 locations
requires generalizing doctor's hardcoded single scope+surface (`mod.rs:41`) into scope×surface
iteration — a structural `doctor::run()` refactor, likely new `DoctorArgs` flags. Incremental value
is **low** (the marker health axes already catch missing/tampered deployed files), so scope this
deliberately rather than assume it.

## Synthesis with exp-003 (staging ownership)

exp-003 recommends moving staging out of SKILL.md into preflight/doctor (own-and-repair,
gitignored, copy-based, drop the `cp`/`rm`). Combined design:
- **preflight OWNS staging** — writes each skill's embedded `formulas/*` into the project's
  `.beads/formulas/` (idempotent; `.beads/formulas/` gitignored), so `bd mol pour|wisp` just works
  and the SKILL.md `cp`/`rm` dance is dropped → the silent-omission bug becomes **structurally
  impossible**.
- **doctor validates** the embedded authoring contract fleet-wide (every pour/wisp name ↔ shipped
  formula) as a static `FormulaCheck`.

Open scoping decisions (for the operator): (1) validator-only vs own-the-staging; (2) accept
embedded-static as both-scope coverage vs budget the on-disk multi-scope doctor refactor.

Key files: `yf/src/cmd/doctor/checks.rs` (seam), `mod.rs:41` (single-scope obstacle),
`preflight.rs:259` (pipeline), `frontmatter.rs:36` (descriptor), `embed.rs` (formulas embedded),
`common.rs:100` (verbatim deploy), `SPEC.md:197-303` (REQ homes), `docs/yf/preflight-contract.md:58`
(status enum).
