# Plan: Split skills into install groups via per-skill frontmatter contract and a dependency-aware install.py

**ID:** plan-006-james-dixson-bf6e21
**Author:** james-dixson
**Created:** 2026-06-03
**Status:** complete
**Epic:** beads-skills-mol-g0b
**Phase log:**
- 2026-06-03 scoping: initial scope captured
- 2026-06-03 investigating: 2 unknowns resolved by direct inspection (no worktree experiments)
- 2026-06-03 drafting: plan v1 presented
- 2026-06-03 review: plan v1 presented
- 2026-06-03 approved: operator approved
- 2026-06-03 intake: epic beads-skills-mol-g0b poured
- 2026-06-03 executing: start gate resolved
- 2026-06-04 complete: plan complete

## Objective

Let users install the harness/utility skills (`optimal-instructions`, `skill-authoring`)
independently of the beads-dependent skills. Achieve this with a **declarative per-skill
frontmatter contract** (`skill-group`, `depends-on-tool`, `depends-on-skill`) and a
**dependency-aware `install.py`** that computes install groups from frontmatter, so the
installer needs no edits when skills are added or regrouped.

## Motivation

Today `install.sh` installs all skills or a hand-named subset. Six of the eight skills hard-
depend on the `bd` (beads) binary; two (`optimal-instructions`, `skill-authoring`) have **no
`bd` runtime dependency** and run standalone (their docs may mention beads, but no code path
invokes `bd`). A user who only wants the harness-authoring skills must
either install everything (pulling beads-coupled skills they can't use without `bd`) or
hand-enumerate skill names. There is no machine-readable record of which skills need which
tools or which other skills — group membership lives only in operator memory. This plan makes
the dependency structure explicit in each skill's frontmatter and teaches the installer to act
on it, so `install.py --group utility` installs exactly the beads-free set, and adding a new
skill self-declares its group with no installer edit.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| _none_ | — | — | No matching upstream issue (open issues #6/#7 are unrelated: mermaid, obsidian links). File a new tracking issue at land-the-plane. | — |

## Investigation Findings

Two load-bearing unknowns, both resolved by direct repo inspection (no worktree experiments needed):

1. **Frontmatter loader tolerance — RESOLVED (favorable).** Adding custom frontmatter keys is
   safe. Evidence: `optimal-instructions` and `skill-authoring` already carry non-standard keys
   (`title`, `created`, `tags`); every skill carries `user-invocable` and most carry
   `allowed-tools`. The Claude Code skill loader ignores unknown frontmatter keys. So
   `skill-group` / `depends-on-tool` / `depends-on-skill` will not break skill loading.

2. **The dependency-check logic to "reuse" — located, NOT shared.** Each skill manager
   re-implements the same check: a binary→`[bin, --version]` map probed with `shutil.which`
   (`skills/bdplan/scripts/plan_manager.py` `_SYSTEM_DEPS` ~line 362; duplicated in
   `skills/bdresearch/scripts/research_manager.py`). There is **no shared module**. Decision
   (scoping Q4): `install.py` re-implements the trivial `shutil.which` check self-contained;
   duplication is noted for a future factoring, not solved here.

Supporting facts:
- No `check-prereqs.sh` exists in any skill (DOCUMENTATION.md references them aspirationally).
  Per-skill tool requirements must be derived from each SKILL.md's stated prereqs plus its
  manager script's `_SYSTEM_DEPS`.
- Frontmatter is real YAML (folded `>` blocks). `install.py` must use a YAML parser (PyYAML via
  PEP 723 inline deps), not regex.
- Companion rules ship from `skills/<skill>/protocols/*.md` and are surfaced to the rules dir by
  the installer (`install_rules` in `install.sh`). `install.py` must preserve this.

## Scoping Decisions

| # | Decision | Choice |
|---|----------|--------|
| Groups | Two groups | `beads` (bdplan, bdresearch, beads-authoring, beads-extra, beads-upstream, **incubator**) and `utility` (optimal-instructions, skill-authoring). Group set is **computed** from the union of `skill-group` frontmatter values, not hardcoded. |
| incubator | Soft beads dep placement | Joins **beads** group (its reason-to-promote is filing beads), though it runs without `bd`. |
| Mechanism | Membership source | `skill-group: <name>` frontmatter key per SKILL.md. |
| Flag | Selector shape | `--group <group-name>`; valid `<group-name>` set computed from frontmatter. Default (no `--group`, no skill args) = install all. Explicit skill-name args still override. |
| install.sh | Fate | Thin bash wrapper: `exec uv run "$(dirname "$0")/install.py" "$@"`. Preserves the documented `./install.sh` entrypoint. uv becomes an install-time prereq (already required at runtime by every skill). |
| Prereq strictness | depends-on-tool enforcement | **Warn, install anyway** (skill files are inert until the tool arrives; each skill's own preflight re-checks at runtime). Print a gap summary; `--strict` flag hard-blocks. |
| External skill deps | depends-on-skill naming | **Bare names only.** Installer resolves names under `skills/*` and pulls them transitively; an unresolved name is warned as "external / assumed-provided" and skipped. Accepts that a typo is indistinguishable from an intended external reference. |
| Dep-check reuse | Code sharing | install.py self-contained `shutil.which` check; note duplication for future factoring. |

## Approach

### Frontmatter contract (added to each `skills/<skill>/SKILL.md`)

```yaml
skill-group: beads | utility        # required; membership for --group
depends-on-tool: [bd, uv, git]      # binaries probed with shutil.which at install
depends-on-skill: [beads-extra]     # bare in-repo skill names, resolved + pulled transitively
```

Finalized values (Issue 1.2 — see `findings/deps-table.md` for per-skill evidence):

| Skill | skill-group | depends-on-tool | depends-on-skill |
|-------|-------------|-----------------|------------------|
| bdplan | beads | bd, uv, git | beads-extra, beads-authoring |
| bdresearch | beads | bd, uv, git | beads-extra, beads-authoring |
| beads-authoring | beads | bd | beads-extra |
| beads-extra | beads | bd | _(none in-repo; `beads` is external)_ |
| beads-upstream | beads | bd, uv, gh | beads-extra |
| incubator | beads | uv | beads-extra |
| optimal-instructions | utility | uv | skill-authoring |
| skill-authoring | utility | uv | _(none)_ |

Notes: the external `beads` skill (marketplace plugin) is intentionally **not** listed under
`depends-on-skill` because bare-names resolution would warn on it every run; the hard `bd`
binary requirement is captured by `depends-on-tool` instead. `incubator` ships
`incubator-index.py` so it needs `uv` (its `bd` need is soft/promotion-only, expressed by group
+ tie-break). Cross-group invariant asserted: closure(utility)={optimal-instructions,
skill-authoring}, reaching no beads skill.

### install.py (PEP 723, PyYAML; run via `uv run`)

Responsibilities, preserving all current `install.sh` behavior:
- Parse YAML frontmatter of every `skills/*/SKILL.md`.
- Compute the valid `--group` set as the union of `skill-group` values. `--group <unknown>`
  errors and lists valid groups.
- Selection precedence: explicit skill-name args > `--group <name>` > default (all).
- **Transitive in-repo skill-dep resolution:** the install set is closed over `depends-on-skill`
  (bare names found under `skills/*`). A pulled dep crossing group boundaries is logged. An
  unresolved name → warn "external / assumed-provided", continue.
- **Tool prereq check:** for the final install set, union their `depends-on-tool`; probe each
  with `shutil.which`. Missing → warning + summary, **install still proceeds and the process
  exits 0** (skill files are inert until the tool arrives — preserving install.sh's
  exit-0-on-success contract). `--strict` makes a missing tool a hard failure (non-zero exit,
  no install). Exit-code parity is verified in Issue 2.2.
- Preserve flags: `--scope user|project`, `--surface claude|agents`, `--target <path>`,
  `--force`, bare skill-name args, and `--help`. Add `--group <name>`, `--strict`, `--dry-run`
  (print the resolved install set + tool report, install nothing), `--list-groups`.
- `--group` × `--target`: `--group` still filters the install set under an explicit `--target`
  (target only overrides the *destination*, not the *selection*). Exercised by Issue 2.3.
- Copy mechanics: shell out to `rsync -a --delete --exclude=.gitignore` to preserve exact
  mirror-delete semantics. `rsync` is an existing implicit prereq (today's `install.sh` already
  requires it — no regression); no Python copytree fallback (it would have to re-implement
  `--delete`).
- Companion rules: port `install_rules` (protocols/*.md → rules dir, keep-unless-`--force`).

### install.sh wrapper

Replace the body with a thin wrapper that guards for `uv` then `exec uv run
"$(dirname "$0")/install.py" "$@"`, keeping a short usage comment. The guard prints a helpful
"install uv: https://docs.astral.sh/uv/" message and exits non-zero if `uv` is absent (instead
of a raw `uv: command not found`). README and any `./install.sh` references stay valid.

## Epics

### Epic 1: Frontmatter contract
- Issue 1.1: Document the frontmatter schema (`skill-group`, `depends-on-tool`,
  `depends-on-skill`): semantics, resolution rules, bare-names policy, and the **soft-dep
  tie-break rule** — `skill-group` reflects intended-use coupling, not just hard tool deps, so a
  standalone skill whose purpose is to feed a tool (e.g. `incubator` → beads) joins that tool's
  group even with an empty `depends-on-tool`. Land the schema as a new "Skill frontmatter"
  section in README, with a one-line governing pointer added to `AGENTS/DOCUMENTATION.md` (it
  owns README-sync). Entry issue.
- Issue 1.2: Derive each skill's tool/skill deps by reading its SKILL.md + manager
  `_SYSTEM_DEPS`; record the finalized table. **Assert the cross-group invariant**: no `utility`
  skill transitively (via `depends-on-skill`) depends on a `beads` skill (guarantees Success
  Criterion 2/7). depends-on: 1.1
- Issue 1.3: Apply the three frontmatter keys to all 8 SKILL.md files (single batched edit pass
  to bound the CONSISTENCY.md sub-agent runs). depends-on: 1.2

### Epic 2: Dependency-aware installer
- Issue 2.1: Write `install.py` (PEP 723 + PyYAML): frontmatter parse, group computation,
  `--group`/`--strict`/`--dry-run`/`--list-groups`, transitive in-repo skill-dep closure,
  `shutil.which` tool check, and parity with all existing flags + companion-rule install.
  depends-on: 1.1 (schema)
- Issue 2.2: Convert `install.sh` to a thin wrapper (uv-presence guard, then
  `exec uv run install.py "$@"`); verify `./install.sh --help`, the default all-install path,
  and the **exit-0-on-success / non-zero-only-under-`--strict`** contract are unchanged.
  depends-on: 2.1
- Issue 2.3: Verify behavior: `--dry-run` for `--group beads`, `--group utility`, default-all,
  and a bare-name + transitive-dep case, each into a temp `--target` (confirming `--group`
  filters under explicit `--target`); assert the resolved skill set and tool report, the
  cross-group invariant (no beads skill under `--group utility`), and a **post-edit load check**
  that all 8 edited SKILL.md still parse/load (Success Criterion 5). depends-on: 2.1

### Epic 3: Docs + consistency + upstream
- Issue 3.1: Update README install section to match `install.py --help` (the `--group` usage,
  `--list-groups`, group membership), per DOCUMENTATION.md project-README requirements.
  depends-on: 2.2
- Issue 3.2: Run the CONSISTENCY.md sub-agent over every changed skill and the DOCUMENTATION.md
  README-sync checks; resolve FAIL items. depends-on: 1.3, 2.2, 3.1
- Issue 3.3: File the upstream tracking issue (per CLAUDE.md upstream config: github,
  dixson3/beads-backed-skills) describing the install-group feature; land-the-plane. depends-on: 3.2

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Reconcile Gate
- Not needed — no upstream issues incorporated (the tracking issue is filed fresh at 3.3, not reconciled).

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| A harness's skill loader is stricter than Claude Code's and rejects unknown frontmatter keys. | Verified Claude Code tolerates them (existing `title`/`tags`/`user-invocable` keys load). For other harnesses (`.agents` surface), keys are still plain YAML; if a future harness objects, the keys are namespaced/removable. Low likelihood. |
| `rsync` unavailable on a target host now that copy logic moves to Python. | install.py shells to rsync exactly as today; document rsync as an existing implicit prereq, or add a Python copytree fallback. |
| Editing 8 SKILL.md files triggers 8 CONSISTENCY.md sub-agent passes (project rule). | Batch all frontmatter edits into one pass (Issue 1.3) and run a single consolidated consistency sweep (3.2). |
| Bare-names policy can't tell a typo'd in-repo dep from an intended external. | Accepted per scoping decision. Mitigated by the derived-table review (1.2) catching typos at authoring time. |
| Group/skill-name selection precedence is ambiguous when both are passed. | Explicit spec: skill-name args override `--group`; documented in `--help` and README. |

## Success Criteria

1. `uv run install.py --list-groups` prints `beads` and `utility`, computed from frontmatter.
2. `install.py --group utility --target <tmp> --dry-run` resolves exactly
   `optimal-instructions`, `skill-authoring` (+ their transitive in-repo deps) and **no** beads
   skill.
3. `install.py --group beads --dry-run` resolves the six beads skills and warns on missing `bd`
   when absent (does not block without `--strict`; blocks with `--strict`).
4. `./install.sh` (wrapper) with no args still installs all skills + companion rules, matching
   pre-change behavior.
5. All 8 SKILL.md still load as skills (no loader regression) and carry the three new keys.
6. README install section matches `install.py --help`; CONSISTENCY + DOCUMENTATION sweeps pass.
7. No `utility` skill transitively depends on a `beads` skill — the install set for
   `--group utility` is closed under `depends-on-skill` without pulling any beads skill.
