---
type: Finding
okf_spec: OKF-PLAN
---
# EXP-02: `.yf/` layout reality per skill

## Finding: EXP-02 .yf/ layout reality per skill

### Ground truth (from yf code, cited)

The **Rust `yf` binary** implements a single, consistent, **short-name** layout. `<short>`
is the `yf-`-stripped skill name (`plan`, `research`, `beads-init`, …), produced by the one
centralized resolver `resolve_skill` / `skill_short_name`
(`yf/src/preflight.rs:244-264`).

- **Canonical config:** `.yf/<short>/config.local.json`
  (`yf/src/preflight.rs:466-487`, `read_config`). Precedence, first match wins:
  1. `.yf/<short>/config.local.json` (canonical subdir), then
  2. legacy root dotfile named by the skill's `config-basename` descriptor
     (e.g. `.yf-plan.local.json`) — still read as a fallback tier.
  The transitional flat `.yf/<short>.local.json` tier was **removed** — no longer read or
  migrated (`yf/src/migrate.rs:433-457`, test `flat_config_is_ignored`).
- **Canonical state:** `.yf/<short>/preflight.json`
  (`yf/src/preflight.rs:489-492`, `state_path`) — also **short-name**. NOTE: the doc-comment
  on line 489 says `.yf/<skill>/` but the code passes `short`, so the emitted path is
  `.yf/plan/preflight.json`, not `.yf/yf-plan/preflight.json`.
- **Migration** (`yf migrate`, `yf/src/migrate.rs`): `.state/<old>/` → `.yf/<short>/`
  (`migrate.rs:95-105`); legacy root dotfile `.<old>.local.json` → `.yf/<short>/config.local.json`
  (`migrate.rs:107-120`); the short name comes from the SAME `skill_short_name` resolver
  (`migrate.rs:93`), explicitly fixing the historical `.yf/yf-plan/` full-name vs `.yf/plan/`
  short-name disagreement. Gitignore per-skill dotfile anchors collapse to a single `/.yf/`
  (`migrate.rs:123-129`, `collapse_gitignore_anchors` 180-252).
- **Auto-migrate on preflight run? NO.** Preflight's scaffold only writes the `/.yf/`
  gitignore anchor (`preflight.rs:1005-1009`); it does not move legacy files. Migration is
  the separate, operator-invoked `yf migrate` command (`migrate.rs:294`). Legacy state is
  reached only by the tier-2 fallback read until the operator runs `yf migrate`.

**Canonical layout in one sentence:** every skill's per-repo config is
`.yf/<short>/config.local.json` and its runtime state is `.yf/<short>/preflight.json`, where
`<short>` is the `yf-`-stripped name (`plan`, not `yf-plan`), with the legacy root dotfile
`.yf-<skill>.local.json` surviving only as a read-time fallback.

### The full-name-vs-short-name inconsistency (concrete, cross-language)

The Rust binary is uniformly short-name. **`plan_manager.py` disagrees:**

- `skills/yf-plan/scripts/plan_manager.py:143` — `STATE_DIR = Path(".yf") / SKILL_NAME`
  with `SKILL_NAME = "yf-plan"` (line 141) ⇒ writes state to **`.yf/yf-plan/`** (FULL name),
  e.g. `landing.lock` (line 2058). The yf binary writes `preflight.json` to **`.yf/plan/`**
  (SHORT). The same skill's runtime state is thus **split across two directories**.
- `skills/yf-plan/scripts/plan_manager.py:142` — `CONFIG_FILE = Path(f".{SKILL_NAME}.local.json")`
  ⇒ reads config **only** from the legacy root `.yf-plan.local.json`; it never reads the
  canonical `.yf/plan/config.local.json`. An operator who migrates config (or was scaffolded
  fresh under the new layout) has their `landing-strategy` / `validate-cmd` / `execute.worktree`
  keys silently ignored by the manager script.

`research_manager.py` has **no** direct config/state path constants (grep found none) — it
relies on the yf binary for config, so it inherits the correct short-name behavior.

### Per-skill / per-doc table

| Skill or doc | Path it references | Canonical? | Legacy? | Fix = doc-only or upstream-issue (code)? |
| --- | --- | --- | --- | --- |
| `yf/src/preflight.rs` `read_config`/`state_path`/`resolve_skill` | `.yf/<short>/config.local.json`, `.yf/<short>/preflight.json` | Yes | reads legacy dotfile as fallback | none (ground truth) |
| `yf/src/migrate.rs` | migrates → `.yf/<short>/...` | Yes | migrates FROM legacy | none (ground truth) |
| `preflight.rs:489` doc-comment | `.yf/<skill>/preflight.json` | code is short; comment says `<skill>` | — | doc-only (misleading comment) |
| **`plan_manager.py:143` STATE_DIR** | `.yf/yf-plan/` (FULL) | **NO — should be `.yf/plan/`** | full-name | **upstream code fix (yf-plan)** |
| **`plan_manager.py:142` CONFIG_FILE** | `.yf-plan.local.json` only | **NO — misses `.yf/plan/config.local.json`** | legacy-only | **upstream code fix (yf-plan)** |
| **`change_validation.py:44` VALIDATE_CMD_CONFIG** | `.yf-plan.local.json` (seed) | reads legacy only | legacy-only | **upstream code fix (yf-change-validation), minor** |
| `skills/yf-plan/SKILL.md:26` `config-basename:` | `.yf-plan.local.json` | correct (declares legacy fallback name) | intentional | keep (descriptor) |
| `yf-plan/spec/data.md:43` REQ-DATA-020 | config=`.yf-plan.local.json`; state=`.yf/yf-plan/preflight.json` | NO (state FULL; config not canonical) | — | doc-only (+ mirrors code bug) |
| `yf-plan/spec/data.md:51` REQ-DATA-022 | anchors `/.yf-plan.local.json` + `/.state/` | NO (single `/.yf/` now) | — | doc-only |
| `yf-plan/SKILL.md:92-93,121` scaffold anchors | `/.yf-plan.local.json` + `/.state/` | NO (single `/.yf/`) | — | doc-only |
| `yf-plan/README.md:52`, test-harness, smoke.sh | `.yf-plan.local.json`, `/.state/` | legacy-only | — | doc-only |
| `yf-research/spec/data.md:27`, SPEC.md:88-89 | `.yf-research.local.json`; `.yf/yf-research/preflight.json` (FULL) | NO (state FULL; anchors stale) | — | doc-only |
| `yf-research/SKILL.md`, README, spec/prerequisites.md | `.yf-research.local.json`, `/.state/` | legacy-only | — | doc-only |
| `yf-beads-init/SKILL.md:24`, `yf-beads-upstream/SKILL.md:31`, `yf-optimal-instructions/SKILL.md:28` `config-basename:` | `.yf-<skill>.local.json` | correct (legacy fallback name) | intentional | keep (descriptor) |
| `yf-beads-init/SPEC.md:222-224`, `yf-beads-upstream/SPEC.md:173-175`, `yf-incubator/SPEC.md:135` | `.yf-<skill>.local.json` / `.yf/yf-<skill>/` (FULL) | NO (full-name state dir) | — | doc-only |
| `yf-skill-authoring/reference/SURFACE_CONVENTION.md` (81-182) | `.state/<skill>/`, `/.<skill>.local.json` | NO — describes the PRE-migration convention | legacy convention | doc-only (broad — this is the convention source) |
| `yf-skill-authoring/SKILL.md:69-71,160-171`, `SPEC.md:58,75,120` | `.state/<skill>/`, `/.<skill>.local.json` | NO (legacy convention) | — | doc-only |
| `web/content/pages/managed-files.md:25,98` | `.markdown-lint-on-edit` (root) | current | — | doc-only (only if marker is moved) |
| `web/content/pages/harness-tune.md`, `managed-files.md:115` | `.yf/harness-tune-manifest.json` | correct (separate manifest) | — | none (unrelated to per-skill config) |

Note: web `.yf/` references are all the **harness-tune ownership manifest**
(`.yf/harness-tune-manifest.json`), a different artifact from per-skill config/state — those
docs are accurate and out of scope.

### `.markdown-lint-on-edit` marker

- **Defined / consumed:** only in **prose rule text**, never in code. Consumers:
  `skills/yf-markdown-lint/protocols/MARKDOWN_LINT.md:12,32` (the always-loaded trigger the
  agent reads), plus `SKILL.md:118`, `SPEC.md:62,70`, `README.md:26`, and a cross-reference in
  `yf-markdown-format/SKILL.md:113` / `SPEC.md:81`, and the web `managed-files.md:25,98`.
- **Is the move a code change? NO** (for the marker's consumption). `markdown_lint.py` never
  reads the marker (grep: zero hits — its "marker" strings are table-alignment markers); no
  `yf/src/*` code references `markdown-lint-on-edit` (grep: zero hits). The path is
  "hardcoded" only in the rule/SKILL/SPEC prose. Moving it to `.yf/markdown-lint-on-edit` is a
  **rule/doc edit**, not a compiled-code edit.
- **Two real complications an upstream issue MUST address:**
  1. **Gitignore semantics conflict.** `.markdown-lint-on-edit` is a **committed** opt-in
     (shared with the repo). `.yf/` is gitignored (single `/.yf/` anchor,
     `preflight.rs:51-54`). Moving the marker under `.yf/` would make it **gitignored** unless
     a `!.yf/markdown-lint-on-edit` negation is added — otherwise the opt-in stops being
     shared. The issue must specify the intended commit semantics.
  2. **Automatic migration.** To move an operator's existing root marker, add a `yf migrate`
     entry (analogous to `SKILL_MAP` handling in `migrate.rs:35-49,88-121`) that renames
     `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit` — this **is** new code in
     `migrate.rs`. Preflight does not auto-migrate anything (see Ground truth), so without a
     migrate entry the move is manual.
- **What the upstream issue must ask for:** (a) update the four prose surfaces
  (MARKDOWN_LINT.md rule, SKILL.md, SPEC.md, README) + web managed-files.md to the new path;
  (b) decide + implement the gitignore commit semantics; (c) optionally add the `migrate.rs`
  rename entry for automatic migration.

### Which skills need an upstream code-fix issue (and why)

1. **yf-plan** (primary) — `plan_manager.py` diverges from the canonical Rust layout on **two**
   axes: STATE_DIR uses the FULL name `.yf/yf-plan/` (should be short `.yf/plan/`, splitting
   state across two dirs), and CONFIG_FILE reads only the legacy `.yf-plan.local.json` (never
   the canonical `.yf/plan/config.local.json`). Operator config set under the new layout is
   silently ignored by the manager. This is the concrete full-vs-short bug.
2. **yf-change-validation** (minor) — `change_validation.py:44` reads yf-plan's `validate-cmd`
   seed only from the legacy `.yf-plan.local.json`; it should also honor
   `.yf/plan/config.local.json`. Low severity (one-time inference seed).
3. **yf-markdown-lint** (only if the operator's marker-move is approved) — no code consumes the
   marker, so the move is doc/rule work **plus** an optional `migrate.rs` rename entry and a
   gitignore-semantics decision (see marker section).

No other skill emits legacy paths from **code**: `research_manager.py` has no path constants
(defers to the correct binary), and the `config-basename:` frontmatter lines are the
intentionally-supported legacy fallback declarations, not bugs.

### Implications for Plan

- The Rust `yf` engine already implements the intended `.yf/<short>/` layout correctly and
  idempotently; the plan does **not** need an engine change for config/state canonicalization.
- The gap is (a) **doc drift** across ~9 skill/spec surfaces still asserting the legacy dotfile
  and/or full-name `.yf/yf-<skill>/` state dir and the obsolete `/.yf-*.local.json` + `/.state/`
  anchors, and (b) a **genuine code divergence in `plan_manager.py`** (and a minor one in
  `change_validation.py`) that no doc edit can fix.
- The `.markdown-lint-on-edit` move is cheap in code (no consumer) but carries a non-obvious
  gitignore-commit-semantics decision that must be made explicitly.

### Recommendations

1. File an upstream code-fix issue for **yf-plan** `plan_manager.py`: change `STATE_DIR` to the
   short name (`.yf/plan/`, matching the binary) and make `_read_config` read
   `.yf/plan/config.local.json` first with the legacy dotfile as fallback (mirror
   `preflight.rs read_config` precedence). Include a note about migrating any existing
   `.yf/yf-plan/` state to `.yf/plan/`.
2. File a minor upstream code-fix issue for **yf-change-validation** to also read the canonical
   `.yf/plan/config.local.json` validate-cmd seed.
3. Doc-only corrections (single pass, no code): update `yf-plan/spec/data.md` (REQ-DATA-020/022),
   `yf-plan/SKILL.md`/README/test-harness, all `yf-research` config/state/anchor references
   (short name `.yf/research/`, single `/.yf/` anchor), the `SPEC.md` migration paragraphs in
   yf-beads-init/upstream/incubator, and `yf-skill-authoring` SURFACE_CONVENTION.md + SKILL.md +
   SPEC.md (the convention source, still describing `.state/<skill>/` + `/.<skill>.local.json`).
   Fix the misleading `preflight.rs:489` doc-comment (`<skill>` → `<short>`).
4. Keep all `config-basename: .yf-<skill>.local.json` frontmatter lines — they correctly declare
   the still-supported legacy fallback.
5. For the marker move, only proceed with an explicit decision on commit semantics; if approved,
   add the `migrate.rs` rename entry so existing repos migrate automatically.
