# Finding exp-001: Reference recon (naba, homebrew-tap, install.py, rename surface)

Date: 2026-06-14. Sources: `~/workspace/dixson3/naba`, `~/workspace/dixson3/homebrew-tap`,
this repo's `install.py` + skills tree, local `brew` state.

## 1. naba is Go + goreleaser (NOT Rust)

naba (`module github.com/dixson3/naba`, go 1.25, cobra CLI) is the behavioral model, but its
**toolchain does not port directly**:

- Skills embedded via `//go:embed skills` in the package root → Rust equivalent is the
  `rust-embed` or `include_dir` crate (build-time embed of `skills/`).
- Release via **goreleaser** with a `brews:` block that auto-commits `Formula/naba.rb` to
  `dixson3/homebrew-tap` using `HOMEBREW_TAP_TOKEN`. goreleaser's native builder is Go; for a
  Rust binary the idiomatic equivalent is **cargo-dist** (generates the GH Actions release
  matrix + Homebrew formula publishing + checksums + semver from git tags) or a hand-rolled
  matrix. **This is decision A.**

### naba behavioral model worth replicating

- `naba skills {install,upgrade,remove,status}` with persistent flags `--scope {user,project}`,
  `--surface {claude,agents}`, `--target`, `--dry-run`.
- Dest resolution: `--target` wins; else `<anchor>/.<surface>/skills` where anchor = `$HOME`
  (user) or git-root/cwd (project). Identical to this repo's `install.py` `resolve_dests()`.
- **Tree-hash integrity marker**: SHA256 over (sorted relpath bytes ++ file bytes), with
  `SKILL.md` marker-stripped before hashing. On install, a marker comment
  `<!-- naba-skills: v=<ver> tree=<sha256> -->` is injected into `SKILL.md` after frontmatter.
  `skills status`/`doctor` compare deployed-vs-embedded hash → `installed / up-to-date /
  complete / unmodified`. Upgrade **prunes stale files** (rsync --delete parity).
- `naba doctor`: per-axis checks (`version`, `config`, domain checks, `skills:<name>`), `--json`,
  nonzero exit on any fail. yflow's analog axes: `version`, `bd` present+version(≥1.0.5), `uv`
  present, `git`, `skills:<name>` health, companion-rule install/hash.
- Version via ldflags (`git describe --tags`); `naba version` prints `ver (commit, date)`. Rust
  equivalent: `env!("CARGO_PKG_VERSION")` + build-time git info, or cargo-dist's injection.

## 2. homebrew-tap (`dixson3/homebrew-tap`, tap name `dixson3/tap`)

- One formula today: `Formula/naba.rb`, **goreleaser-generated** ("DO NOT EDIT"), prebuilt
  `.tar.gz` per `{darwin,linux}×{amd64,arm64}`, `bin.install "naba"`, `test do … version`.
- No automation in the tap repo itself; the **tool repo pushes** the formula on tag.
- README empty; no contributing conventions.

## 3. Dependencies resolve from homebrew-core (clean)

- `uv` → homebrew-core (`Formula/u/uv.rb`). `depends_on "uv"`.
- `bd` ships as the **`beads`** formula in **homebrew-core** (`Formula/b/beads.rb`, steveyegge/beads,
  v1.0.5). `depends_on "beads"`. **No custom tap needed for either dep.** (`dixson3/tap` is the
  homebrew-tap repo; it does not need to host bd.)

## 4. install.py — what yflow must replicate

`install.py` (307 L, wrapped by `install.sh` via `uv`) responsibilities:

1. Parse `SKILL.md` YAML frontmatter: `name`, `skill-group`, `depends-on-tool`,
   `depends-on-skill`, `user-invocable`.
2. Compute groups (sorted unique `skill-group`); current groups: **beads, utility, markdown**.
3. Transitive `depends-on-skill` closure (logs cross-group pulls + external/unresolved deps).
4. Tool-presence check (`shutil.which`); `--strict` blocks on missing `depends-on-tool`.
5. Dest resolution (§ naba parity above).
6. Copy skill: `rsync -a --delete --exclude=.gitignore`.
7. Install companion rules: each skill's `protocols/*.md` → `<surface>/rules/` (skip if exists
   unless `--force`).
8. Flags: `--scope --surface --target --group --strict --dry-run --list-groups --force` +
   positional skill names.

## 5. Companion-rule + manifest model

Rules and their owning skills (canonical source = `skills/<skill>/protocols/`):

| Skill                | Rule                   | manifest.json?                                    |
| :------------------- | :--------------------- | :------------------------------------------------ |
| bdplan               | PLANS.md               | yes (sha256+version+deprecated+previous_versions) |
| bdresearch           | RESEARCH.md            | yes                                               |
| beads-init           | BEADS_INIT.md          | yes                                               |
| beads-upstream       | UPSTREAM_TRACKING.md   | yes                                               |
| optimal-instructions | INSTRUCTIONS.md        | yes                                               |
| drift-check          | DRIFT-CHECK-TRIGGER.md | no                                                |
| markdown-lint        | MARKDOWN_LINT.md       | no                                                |

The per-rule `manifest.json` (sha256 + semver + previous_versions + deprecated) backs the
preflight outcomes `rule_missing / rule_drift / rule_deprecated`. **This is a different integrity
axis than naba's whole-tree marker** — the rule manifest detects drift of the *installed,
always-loaded rule* vs the skill's shipped version; naba's marker detects *skill upgrade
freshness*. yflow likely needs **both**: tree-freshness for `skills status/upgrade`, and the
rule-hash/semver semantics for preflight. (Design item for PLAN.)

## 6. Per-skill preflight/config surface (migration candidates → yflow)

| Skill      | Script                     | Preflight/config subcommands                                                                                                                                             |
| :--------- | :------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| bdplan     | `plan_manager.py` (2168 L) | `check` (bd≥1.0.5, tools, rule-hash, scaffold/gitignore anchors, `.bdplan.local.json`, `.state/bdplan/preflight.json`)                                                   |
| bdresearch | `research_manager.py`      | `check` (same shape, `.bdresearch.local.json`)                                                                                                                           |
| beads-init | `beads_init.py` (305 L)    | `verify`/`repair`/`status` (tool detect, `.beads/` detect, **parse `bd status --json` for `error` key — not exit code**, wedged-migration diagnosis + idempotent repair) |

Domain logic that **stays Python** (NOT preflight): plan init/scope/triage/audit/pour/worktree/
landing-lock/validate-merged/resume-scan; research index/credibility/search; beads-init repair
engine internals. The shared *kernel* (tool detection, bd-version, rule-hash verification,
`.local.json` config read, `.state` cache, gitignore-anchor scaffold) is the move-to-yflow
candidate. **Depth is decision B.**

## 7. Rename surface (yf- prefix) — mechanical but wide

13 skills. Touch-points (canonical sources only; installed copies regenerate on reinstall):

- `SKILL.md` frontmatter `name:` (13) and `depends-on-skill:` chains (7 edges:
  bdplan,bdresearch,beads-init,beads-upstream,beads-authoring,incubator → beads-extra/-authoring;
  optimal-instructions → skill-authoring).
- `SKILL_DIR` `find … -name <skill> -type d` globs in each SKILL.md (13).
- Python `SKILL_NAME` constants (2: plan_manager.py:31, research_manager.py:27) which derive
  `CONFIG_FILE = .<name>.local.json` and `STATE_DIR = .state/<name>` → renaming changes the
  **config + state filenames** (`.bdplan.local.json` → `.yf-plan.local.json`). Migration concern
  for any repo already carrying operator config. **Decision C.**
- ~26 backtick cross-skill references + trigger text in SKILL.md descriptions.
- Companion rules embed command examples (`/bdplan` → `/yf-plan`) and cross-skill names (8 rules).
- `.beads/formulas/plan-execute.formula.toml` naming, `skill-ecosystem.d2` node ids, this repo's
  `AGENTS.md`/`DRIFT-CHECK.md`/rules, and the **installed global rules + user CLAUDE.md** that
  name `bdplan`/`bdresearch` (out-of-repo; reinstall + manual CLAUDE.md note).
- Special renames: `bdplan→yf-plan`, `bdresearch→yf-research`; all others take the bare prefix
  (`beads-extra→yf-beads-extra`, etc.).

## Open decisions for operator (A–E)

- **A** Rust release toolchain: cargo-dist (recommended) vs goreleaser-rust vs hand-rolled.
- **B** Preflight migration depth: shared-kernel-only (recommended) vs deeper rewrite.
- **C** Clean invocation break (`/yf-plan`, rename config/state files) vs transitional aliases.
- **D** Crate location: root of this repo (`dixson3/yoshiko-flow`), skills embedded from `skills/`,
  releases tagged here (repo name already aligns with "yflow"). Low-controversy — confirm in plan.
- **E** Dependency formulae: `depends_on "beads"` + `depends_on "uv"` (both core). Resolved.
