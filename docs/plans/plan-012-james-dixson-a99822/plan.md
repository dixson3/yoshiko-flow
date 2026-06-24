# Plan: yf/beads health, hygiene & rule consolidation: yf doctor (#32), suppress bd-init cruft (#31), yf-beads-hygiene skill (#29), settings docs (#30), fold orphan BEADS.md rule (E), upstream default-none + preflight offer (F)

**ID:** plan-012-james-dixson-a99822
**Author:** james-dixson
**Created:** 2026-06-23
**Status:** complete
**Epic:** beads-skills-mol-2bi
**Phase log:**
- 2026-06-23 scoping: initial scope captured
- 2026-06-23 investigating: 3 experiments identified (INV-1 yf CLI, INV-2 bd-init cruft, INV-3 hygiene vs sweep)
- 2026-06-23 drafting: 3 findings synthesized; drafting plan v1
- 2026-06-23 review: plan v1 presented
- 2026-06-23 review: operator added two beads-init/upstream-surface scope items — Epic E (fold orphan `~/.claude/rules/BEADS.md` into skill-owned `BEADS_INIT.md`) and Epic F (yf-beads-upstream default `none` + preflight detect-and-offer); re-review pending
- 2026-06-23 approved: operator approved
- 2026-06-23 intake: epic beads-skills-mol-2bi poured
- 2026-06-23 executing: start gate resolved
- 2026-06-23 reconciling: all 6 epics complete; branch green; entering merge-back
- 2026-06-23 complete: plan complete

## Objective
A coherent "yf/beads health, hygiene, and operator-alignment" plan delivering four
upstream issues plus two operator-requested rule/behavior consolidations that share the
beads/yf runtime-integrity + preflight surface:

- **#32** — a `yf doctor` subcommand that validates `yf`'s runtime prerequisites
  (`beads`, `uv`), built on a small **extensible check framework** so future prereqs
  drop in.
- **#31** — extend `yf-beads-init` to **suppress/clean the cruft `bd init` injects**
  (instruction-file boilerplate, harness hook dirs, git hooks) so a fresh/repaired repo
  matches our conventions automatically.
- **#29** — a new **`yf-beads-hygiene`** skill: safe, read-only-first audit and gated
  repair of orphaned beads and dangling dependency edges, correctly classifying
  gate-typed edges.
- **#30** — document a recommended Claude `settings.json` baseline, tying each key to the
  skill contract / rule it supports (shares the `.claude/settings.json` surface with #31).
- **(E)** — fold the orphan, unowned user-scoped rule `~/.claude/rules/BEADS.md` into the
  **skill-owned `yf-beads-init/protocols/BEADS_INIT.md`** so its keep-worthy content travels
  with the skill (delivered by `yf skills install`) and the standalone global rule is retired.
- **(F)** — make `yf-beads-upstream` **default to `none`** (upstream disabled until explicitly
  configured) and add a **preflight detect-and-offer**: when a github/gitlab origin is detected
  and upstream is still unconfigured, ask the operator once whether to configure sync.

**Out of scope (operator decision):** the version bump + tag **release** is a separate
land-the-plane step triggered after this plan lands — not an epic here.

## Motivation
Each issue closes a gap where the yf/beads runtime can silently diverge from our
conventions or corrupt real state:

- **#32:** the Homebrew formula dropped hard `depends_on "beads"`/`"uv"` (a brew `uv` was
  shadowing the vendor copy and breaking `uv self update`). Nothing now guarantees the
  two runtime deps are present and usable; `yf` needs a read-only self-check that also
  surfaces a shadowed/duplicate install.
- **#31:** `bd init` injects instruction-file boilerplate, `.agents/skills/beads/`,
  `.codex/`, a `.claude/settings.json` hook, and activates beads git hooks — all of which
  fight our conventions (AGENTS.md hand-authored primary; user-scoped `~/.claude/rules/BEADS.md`;
  manual `bd dolt push`, no beads git hooks). Today every fresh repo needs manual cleanup.
- **#29:** a real ad-hoc "cleanup orphaned beads" session produced a **dangerous false
  positive** — 11 valid live-gate edges flagged as "dangling" because `bd list` hides
  gate beads and truncates at 50 rows. Blindly removing them would have un-gated 7 live
  beads. The safe audit/repair discipline must be encoded once.
- **#30:** several skill contracts assume the operator disabled competing built-ins
  (Workflows, TodoWrite, native memory). That assumption lives only in `rules/*.md` prose;
  unset, the model can still reach for the disallowed mechanism and skill invariants leak.
- **(E):** `~/.claude/rules/BEADS.md` is an always-loaded global rule owned by **no skill** —
  it can't be installed, upgraded, or carried to another machine/harness by `yf skills`. Its
  content overlaps the skill-owned `BEADS_INIT.md`, `yf-beads-extra`, and the landing-the-plane
  step. Folding the keep-worthy parts into `BEADS_INIT.md` makes them portable and removes a
  duplicate always-loaded surface (token-efficiency win per the instruction-file protocol).
- **(F):** today an unconfigured upstream is ambiguous (no explicit `none` marker), and the
  operator only ever configures upstream by remembering to run `/yf-beads-upstream init`. A repo
  cloned with a github/gitlab origin gives no signal that sync *could* be wired. Defaulting to an
  explicit `none` and offering setup once on first preflight (then honoring the decision) makes
  the safe state the default and surfaces the opportunity without nagging.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:--|:--|:--|:--|:--|
| [#32](references/upstream-32.md) | `yf doctor` subcommand (validate beads/uv) | include | yf Rust CLI; extensible check framework | Epic A |
| [#31](references/upstream-31.md) | yf-beads-init: suppress bd-init cruft | include | direct edits to `yf/src/beads_init.rs` | Epic B |
| [#29](references/upstream-29.md) | yf-beads-hygiene skill (orphan/edge cleanup) | include | net-new standalone skill (INV-3 verdict) | Epic C |
| [#30](references/upstream-30.md) | Recommended Claude settings.json baseline docs | include | docs; shares settings.json surface with #31 | Epic D |
| _(none)_ | Fold orphan `~/.claude/rules/BEADS.md` into skill-owned `BEADS_INIT.md` | include | operator-requested; no pre-existing issue; rolls into the plan's single coarse tracking issue | Epic E |
| _(none)_ | yf-beads-upstream default `none` + preflight detect-and-offer | include | operator-requested; no pre-existing issue; rolls into the plan's single coarse tracking issue | Epic F |

## Scoping Decisions
- **Release scope:** release (bump `yf/Cargo.toml` + tag) is **separate** — not an epic in
  this plan. Plan delivers #29/#30/#31/#32; release is triggered afterward.
- **#32 `yf doctor` breadth:** **extensible check framework** — a small check registry so
  future prereqs (git, gh, dolt) drop in, not a one-off beads+uv hardcode.
- **#29 hygiene reuse:** **investigate then decide** — compare the existing yf-plan
  coordinator resume-sweep classification logic to #29's audit before building, to reuse
  rather than duplicate (experiment INV-3).
- **(E) fold scope — selective, not verbatim (DEC-2):** `BEADS_INIT.md` is always-loaded, so the
  fold is **deduplicated**, not a wholesale paste — keep-worthy always-needed content stays in the
  rule; CLI detail routes to `yf-beads-extra`; landing-the-plane overlaps the existing close-time
  triggers. Governed by the instruction-file token-efficiency ruleset (yf-skill-authoring). See DEC-2.
- **(F) offer cadence — once, gated on unconfigured (DEC-3):** the preflight offer fires only when a
  github/gitlab origin is detected **and** upstream is still unconfigured (neither enabled nor explicit
  `none`). Once the operator decides — configure or decline → write the explicit `none` marker — it is
  **silent forever** (no nag). See DEC-3.
- **Plan root:** vault-default `docs/plans/` (standalone repo, no `Incubator/`).

## Investigation Findings

Three experiments completed; full writeups in `findings/`. Two surprises reshaped the plan.

- **[exp-001 — yf CLI structure](findings/exp-001-yf-cli-structure.md):** **`yf doctor` already
  exists** (`yf/src/cmd/doctor.rs`, hardcoded axes version/bd/uv/git/skills/rules **+ a
  `--repair` mode**). So #32 is a **refactor to an extensible `Check` registry**, not greenfield.
  The existing `Axis` struct + `Vec` push is ~80% of a registry. Recommended shape: a `Check`
  trait + `CheckResult { name, ok, required, detail, remediation }` + a data-driven registry
  (`BinCheck`) so git/gh/dolt become one-line adds. Concrete bundled win: consolidate **3
  duplicate `which` impls + 2 version parsers**; add the missing "resolved-path + version in
  one call" helper (needed for path reporting **and** the homebrew-shadow warning). Switch the
  exit idiom from `anyhow::bail!` to preflight's `Result<ExitCode>`. New need: a `required` vs
  warning severity (homebrew-shadow must warn, not fail). **Open decision → DEC-1** (`--repair`
  vs #32's read-only mandate).
- **[exp-002 — bd-init cruft](findings/exp-002-bd-init-cruft.md):** `bd init --skip-hooks
  --skip-agents` suppresses **all four cruft classes at init time** (cleanest path). The
  yf-beads-init **Python engine is retired** — the live engine is the Rust source
  **`yf/src/beads_init.rs` (present and editable in this repo)**: `repair()` at line 309,
  the contradictory `bd hooks install --force` at line 349. (exp-002's "not readable here"
  caveat was wrong — corrected in the finding.) #31's work is direct Rust edits to
  `beads_init.rs` plus the skill's init branch, not `beads_init.py`. **Direct conflict:**
  repair step `bd hooks install --force` (`beads_init.rs:349`) is the inverse of #31 and must
  be made conditional. Repair-time removers are bd-native + idempotent
  (`bd hooks uninstall`, `bd setup claude/codex --remove`, `rm -rf .agents/skills/beads/`,
  marker-scoped CLAUDE.md strip). This repo is the reference "correct" target. **#30 coupling:**
  #31's settings.json cleanup must be **entry-scoped** (prefer `bd setup claude --remove`), never
  wholesale-delete, so it can't clobber a #30 baseline.
- **[exp-003 — hygiene vs sweep](findings/exp-003-hygiene-vs-sweep.md):** **VERDICT: standalone
  skill.** yf-plan's coordinator sweep computes only `stuck` (by status) over a parent subtree
  and never resolves dependency edges — none of #29's four classifications exist to reuse.
  Build `yf-beads-hygiene` independently; **reference** yf-beads-extra for gate/edge/JSON
  gotchas (don't restate); optionally copy (not import) the ~12-line universe-builder pattern.
  Two doc gaps to close under #29: add the "`bd list` hides gates + truncates at 50" gotcha and
  `bd dep cycles` to yf-beads-extra.

### Pre-investigation checkpoint
Experiments (independent, run in parallel):
- **INV-1 — yf CLI structure:** How is the `yf` Rust CLI organized (clap subcommand
  wiring, where `preflight`/kernel logic lives, error/exit-code + output conventions)?
  Where does a new `doctor` subcommand slot in, and what's the cleanest shape for an
  extensible check registry? _Feeds #32._
- **INV-2 — bd-init cruft surface:** What does `bd init` actually create (the four cruft
  classes in #31), and what does `yf-beads-init`/`beads_init.py` already verify/repair?
  Where would suppress-at-init vs clean-on-repair hook in, and is there a `hooks.install`
  knob? _Feeds #31._
- **INV-3 — hygiene vs coordinator sweep:** Compare yf-plan's coordinator resume
  orphan-sweep classification (stuck/orphan detection, gate-edge handling) to #29's audit
  spec. What is reusable (shared classifier/helper) vs genuinely skill-specific? _Feeds
  #29; drives the reuse-vs-standalone decision._

## Approach

Four independent deliverables, sequenced by coupling rather than hard dependency. The only
real ordering constraint is the **#31 ↔ #30 settings.json surface**: #31's cleanup must be
entry-scoped before #30 documents a project-scope baseline, so Epic B (#31) lands before
Epic D (#30). #32 (Rust) and #29 (new skill) are fully parallel to each other and to B/D.

- **#32 (Rust):** refactor the existing `yf doctor` into a `Check`-trait registry, consolidate
  the duplicated `which`/version helpers into one resolver returning path+version, add the
  homebrew-shadow warning with a `required` vs warning severity, and switch to `Result<ExitCode>`.
- **#31 (kernel + skill):** make hook/agents install opt-out, add repair-time cruft cleanup
  (bd-native removers), neutralize the contradictory `bd hooks install --force` repair step,
  and update the yf-beads-init skill docs.
- **#29 (new skill):** author `yf-beads-hygiene` standalone (read-only audit → gated repair),
  cross-referencing yf-beads-extra; close the two yf-beads-extra doc gaps.
- **#30 (docs):** a `docs/recommended-settings.md` page (or README section) tying each key to
  the rule/contract it supports, user-scope default + project-scope guidance.
- **(E) (skill rule):** audit `~/.claude/rules/BEADS.md` section-by-section, produce a fold map
  (keep-in-rule / route-to-skill / drop-as-dup), fold the keep set into `BEADS_INIT.md` under the
  token-efficiency ruleset, refresh the manifest hash, and document retirement of the orphan rule.
- **(F) (skill behavior + rule):** make unconfigured upstream resolve to `none` everywhere the
  push/status short-circuits already check `enabled=false`; add the preflight detect-and-offer to
  the shared beads preflight (companion rule `UPSTREAM_TRACKING.md`), gated and one-shot per DEC-3;
  update the `init` flow and refresh the manifest hash.

### DEC-1 — `yf doctor --repair` vs the read-only mandate (operator decision)
#32 says doctor must be read-only; the existing command already has a `--repair` mode that
delegates to `beads_init::repair`. **Recommendation:** keep `--repair` as an **explicit
opt-in flag** with read-only as the default — this satisfies #32 (default verifies, never
mutates) without removing working repair functionality (and #31's cleanup naturally extends
that same `--repair` path). Surfaced for red-team / operator confirmation; not blocking the draft.

### DEC-2 — what folds from BEADS.md into BEADS_INIT.md (operator decision)
`~/.claude/rules/BEADS.md` is a large operational reference (bd onboard, quick-reference,
non-interactive shell flags, issue-types/priorities/workflow, auto-sync, "use bd for ALL
tracking", Landing the Plane). `BEADS_INIT.md` is **always-loaded** and deliberately thin.
**Recommendation:** a **selective, deduplicated** fold — keep in the rule only the genuinely
always-needed mandates (use-bd-for-all-tracking; non-interactive shell-flag safety; the
land-the-plane push sequence as a pointer), route CLI/issue-type detail to `yf-beads-extra`,
and drop content already covered by the existing close-time triggers. The fold map (E.1) is the
reviewable artifact. **Not** a verbatim paste — that would bloat an always-loaded surface and
violate the instruction-file token-efficiency ruleset. Surfaced for red-team / operator confirmation.

### DEC-3 — preflight detect-and-offer cadence (operator decision)
The offer must not become a nag. **Recommendation:** fire the AskUserQuestion offer **only** when
(a) `git remote origin` is github/gitlab **and** (b) upstream is unconfigured — no
`custom.upstream.*` keys and no explicit `none` marker. On either outcome write a durable marker
(configure → backend keys; decline → explicit `none`), after which the offer is a **silent no-op**
forever. This preserves the existing "disabled is honored everywhere / no nag" invariant while
making `none` the safe default and surfacing setup exactly once. Surfaced for red-team / operator confirmation.

## Epics

### Epic A: `yf doctor` extensible check framework (#32)
- A.1: Extract a shared tool-resolution helper — one `resolve_tool(bin) -> Option<PathBuf>`
  (from `preflight.rs::which_in`) + `tool_version` (reusing `extract_version_tuple`); replace
  the 3 duplicate `which` impls (`beads_init.rs:581`, `preflight.rs:542`, `common.rs::tool_on_path`)
  and 2 version parsers. **Acceptance (C2):** the existing `preflight` and `beads_init` test
  suites must pass post-consolidation (not just new helper unit tests); resolution semantics
  (symlink/PATHEXT) preserved 1:1 per call site; migrate one call site at a time behind the
  shared helper rather than a big-bang swap, since `yf preflight` gates other skills. Unit tests
  for PATH-override + version parse.
- A.2: Define the check abstraction — `Check` trait + `CheckResult { name, ok, required,
  detail, remediation }`; generalize `Axis`. depends-on: A.1
- A.3: Implement `BinCheck` (present + version + resolved path + min-version) and port bd/uv
  to it with remediation strings; implement `HomebrewShadowCheck` (warning severity) for uv.
  depends-on: A.2
- A.4: Port skills/rules axes to `Check` impls delegating to `cmd/common.rs`; build the
  registry `checks()`; wire `required` → exit code; switch doctor body to `Result<ExitCode>`.
  depends-on: A.3
- A.5: Resolve DEC-1 — keep `--repair` as explicit opt-in, default read-only; update help text.
  **Exit-idiom split (C4):** only the read-only check path adopts `Result<ExitCode>`; `run_repair`
  (`doctor.rs:120`) deliberately stays on `anyhow::bail!` (a repair *failure* is a genuine error,
  unlike a read-only check verdict). depends-on: A.4
- A.6: Update human + `--json` rendering for the new shape (severity, path, remediation);
  update/extend doctor tests. depends-on: A.4
- resolves-upstream: #32 (include)

### Epic B: Suppress bd-init cruft in yf-beads-init (#31)
> Engine confirmed editable here: `yf/src/beads_init.rs` (C1). B.1–B.3 are direct Rust edits
> to that file — no "confirm engine location" step needed.
- B.1: Init-time suppression — wire the `not_initialized` path to `bd init --skip-hooks
  --skip-agents` (+ `dolt.local-only`, `doctor.suppress.git-hooks true`).
- B.2: Neutralize the contradiction — make the repair engine's `bd hooks install --force`
  step (`beads_init.rs:349`) conditional/removed so repair never re-installs hooks. depends-on: B.1
- B.3: Repair-time cleanup (idempotent, bd-native) for already-dirtied repos: `bd hooks
  uninstall` + reset `core.hooksPath`; `bd setup claude --remove` + `bd setup codex --remove`;
  `rm -rf .agents/skills/beads/`; marker-scoped CLAUDE.md/AGENTS.md block strip. depends-on: B.2
- B.4: Entry-scoped settings.json cleanup (never wholesale-delete; delete file only if empty)
  to stay compatible with #30. depends-on: B.3
- B.5: Update yf-beads-init SKILL.md/SPEC.md to document suppression + cleanup; refresh
  manifest hash. depends-on: B.4
- resolves-upstream: #31 (include)

### Epic C: `yf-beads-hygiene` skill (#29)
- C.1: Close **yf-beads-extra** doc gaps (note: this edits a *different* skill than the epic
  delivers, so it is subject to yf-beads-extra's authoring/manifest conventions) — add the
  "`bd list` hides gate beads + truncates at 50" gotcha and `bd dep cycles`. Close criteria
  include the manifest-hash refresh.
- C.2: Scaffold `yf-beads-hygiene` skill (SKILL.md trigger contract, SPEC.md) per
  yf-skill-authoring; route to yf-beads-init on wedged/corrupted DB. depends-on: C.1
- C.3: Read-only audit engine — resolve edge targets via `bd show` (never `bd list`), full
  universe (`--all` + `--type gate`); classify true-orphan / truly-dangling / satisfied-gate /
  live-gate. depends-on: C.2
- C.4: Gated repair — propose only truly-dangling removals, require confirmation, never touch
  live-gate edges; post-mutation `bd dep cycles` + land-the-plane push; round-trip restore.
  depends-on: C.3
- C.5: Tests/fixtures for the four classifications incl. the live-gate false-positive
  regression from #29. depends-on: C.4
- resolves-upstream: #29 (include)

### Epic D: Recommended settings.json baseline docs (#30)
- D.1: Author `docs/recommended-settings.md` — the reference config with each key tied to its
  rule/contract; call out `disableWorkflows` + `todoFeatureEnabled:false` as highest-impact;
  user-scope default vs project-scope guidance. depends-on: B.4 — **insurance only (C3):** #31's
  cleanup (project-scope hook) and #30's baseline (user-scope keys) are disjoint surfaces, so D.1
  blocks only on B.4's entry-scoped-cleanup *decision being recorded*, not on B.4 implementation.
- D.2: Link it from README; lint as GFM. depends-on: D.1
- resolves-upstream: #30 (include)

### Epic E: Fold orphan `~/.claude/rules/BEADS.md` into skill-owned `BEADS_INIT.md`
> Mechanism: `BEADS_INIT.md` ships from `skills/yf-beads-init/protocols/` and is delivered to the
> rules surface by `yf skills install` (no repo-level `install.sh`; the `yf` CLI is the installer).
> The orphan `~/.claude/rules/BEADS.md` is owned by no skill — retiring it is a manual delete the
> epic documents, not a file this repo tracks.
- E.1: **Fold map (DEC-2 artifact, R5)** — audit `~/.claude/rules/BEADS.md` section-by-section;
  classify each (keep-in-rule / route-to-`yf-beads-extra` / drop-as-dup). The dedup check must run
  against **every existing always-loaded surface**, not just BEADS_INIT.md — in particular the
  land-the-plane / close-time push is **already owned** by `UPSTREAM_TRACKING.md`, so route to it or
  cross-reference, never restate (restating would recreate the duplicate always-loaded surface Epic
  E exists to remove). Record as a short table in the epic / a finding; operator-reviewable before
  E.2 mutates the rule.
- E.2: Apply the fold to `skills/yf-beads-init/protocols/BEADS_INIT.md` under the instruction-file
  token-efficiency ruleset (Cut/Keep/Extract; yf-skill-authoring); keep the trigger-contract framing
  intact. **Charter (R5):** general bd-usage mandates (use-bd-for-all-tracking, non-interactive
  shell-flag safety) sit slightly outside BEADS_INIT.md's stated "init/health trigger contract"
  charter — since it is the only skill-owned home for them, add a one-line scope-note widening the
  charter so the fold is on-charter (don't smuggle off-charter content in silently). depends-on: E.1
- E.3: Update yf-beads-init `SKILL.md`/`README.md` to note the consolidated content and document
  retirement of the orphan rule (operator deletes `~/.claude/rules/BEADS.md` post-install). Refresh
  the protocols manifest hash (`manifest_update.py`). depends-on: E.2
- E.4: Lint `BEADS_INIT.md` as GFM (lint-on-edit marker is present); resolve any DRIFT-CHECK.md
  edge that scopes the protocols surface. depends-on: E.3
- resolves-upstream: (none — operator-requested; rolls into the coarse tracking issue)

### Epic F: yf-beads-upstream default `none` + preflight detect-and-offer
> Coupling: F's preflight offer lives on the shared beads-preflight surface that `BEADS_INIT.md`
> (Epic E) anchors — sequence F after E so the offer text lands in a settled rule, or wire it into
> `UPSTREAM_TRACKING.md` independently. Either way the offer is gated + one-shot per DEC-3.
- F.1: **Default-deny comparison (R1, load-bearing).** Today the short-circuits read
  `bd config get custom.upstream.enabled` and branch on the **literal string `false`** — an
  unconfigured repo (key absent → empty) fails **open** (proceeds to auth/enumerate). Invert to
  **default-deny**: treat anything `!= "true"` (empty/unset/`false`/`none`) as disabled. Change the
  comparison at every site: SKILL.md Push §0 (line 137), Status/pull (line 236), the init §1/§2
  default proposal (lines 87/92), and confirm the Backends `none` row (line 72) stays accurate.
  **Acceptance:** a repo with no `custom.upstream.*` keys short-circuits to disabled (new test
  fixture). The explicit `none` marker (R2) is **optional disambiguation only, never required for
  correctness** — default-deny is the load-bearing mechanism so repos initialized before this change
  still fail closed; do not ship a marker-only path.
- F.2: **Preflight detect-and-offer (DEC-3, R3).** When `remote.origin.url` is github/gitlab **and**
  upstream is unconfigured (gate reads the **same key/precedence** as F.1's §0 short-circuit),
  `AskUserQuestion`: configure now (→ `/yf-beads-upstream init`) or decline (→ write explicit
  `none`). Offer fires **only in an interactive context that can persist the decision** (never in a
  read-only preflight that can't write the marker — it would re-fire). One-shot; honored thereafter.
  **Acceptance:** a second preflight after a decline produces **zero** prompts (test). depends-on: F.1
- F.3: Update `SKILL.md` `init` flow (default-deny; the detect-and-offer **procedure** lives here per
  the trigger-split design) and the companion rule `protocols/UPSTREAM_TRACKING.md` (**minimal**:
  the gated preflight-offer **trigger + gate condition + pointer to SKILL.md init**, mirroring the
  close-time trigger's shape — procedure does *not* move into the always-loaded rule, R4). Fix the
  stale `install.sh` reference at SKILL.md line 79 → `yf skills install` (R6). Refresh the protocols
  manifest hash. depends-on: F.2
- F.4: Lint touched `*.md` as GFM; add/resolve the concrete DRIFT-CHECK.md edge between
  `yf-beads-upstream/SKILL.md` ↔ `protocols/UPSTREAM_TRACKING.md` for the `none`-default + offer
  semantics (R4). depends-on: F.3
- resolves-upstream: (none — operator-requested; rolls into the coarse tracking issue)

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Verification Gate — Rust epics (M1)
- Type: auto
- Condition: `cd yf && cargo test && cargo build` green; `cargo clippy --all-targets -- -D
  warnings && cargo fmt --check` clean (matches `.bdplan.local.json` `validate-cmd`)
- Blocks: Epic A and Epic B completion (an epic is not "complete" until the build/tests are green)

### Reconcile Gate (upstream incorporated)
- Type: auto (all execution beads closed)
- Condition: Epics A–F complete (A/B tests-green per Verification Gate; C/E/F manifest-valid +
  GFM-lint clean on touched `*.md`; E.1 fold map recorded; F honors the DEC-3 one-shot invariant);
  #29/#30/#31/#32 verified resolved; E and F verified delivered (no upstream issue to close)
- Blocks: reconcile step

## Risks & Mitigations
- **#32 is a refactor of a shipped command** — regressing existing doctor axes (skills/rules/
  git) or the `--repair` path. *Mitigation:* A.6 extends existing tests; port axes 1:1 before
  adding registry sugar; DEC-1 keeps `--repair` behavior.
- **#31 engine is Rust, not `beads_init.py`** — Epic B is direct Rust edits, not skill-doc-only.
  *Resolved (C1):* the engine is `yf/src/beads_init.rs`, present and editable in this repo
  (`repair()` line 309, `bd hooks install --force` line 349). No "confirm engine location"
  step needed; B.1–B.3 target that file directly. Net: the earlier "may widen Epic B" risk is
  retired.
- **#31 settings.json cleanup clobbering a #30 baseline.** *Mitigation:* B.4 entry-scoped
  cleanup + D.1 sequenced after B.4; never wholesale-delete.
- **yf-beads-hygiene reproducing the original false positive** (un-gating live work).
  *Mitigation:* C.3 resolves via `bd show`; C.5 regression test on the 11-live-gate-edge case;
  C.4 confirmation-gated, never auto-removes live-gate edges.
- **CLAUDE.md END-marker convention unconfirmed** (exp-002 caveat). *Mitigation:* B.3 verifies
  against a real `bd init` in a throwaway dir before implementing the strip; prefer
  `bd setup claude --remove` over manual sed.
- **(E) over-folding bloats an always-loaded rule** — pasting BEADS.md verbatim into
  `BEADS_INIT.md` would violate the instruction-file token-efficiency ruleset and duplicate
  `yf-beads-extra`. *Mitigation:* DEC-2 mandates a selective dedup fold; E.1 produces the
  reviewable fold map before E.2 mutates the rule; retirement of the orphan is documented, not
  silent (the user deletes `~/.claude/rules/BEADS.md` — losing content already covered elsewhere).
- **(F) preflight offer becomes a nag, or `none`-default breaks existing enabled repos** —
  *Mitigation:* DEC-3 gates the offer on unconfigured-only and makes it one-shot (durable marker
  on either outcome); F.1 changes only the *unset → none* default, leaving explicitly-enabled
  configs untouched; the never-bare-`sync` + disabled-honored invariants are preserved.

## Success Criteria
- `yf doctor` runs read-only by default, reports bd+uv presence/version/resolved-path, warns
  (non-fatal) on a homebrew-shadowed uv, exits non-zero with remediation when a required dep is
  missing; adding a new prereq check is a one-line registry edit; duplicate which/version
  helpers consolidated; existing axes + tests still pass. (#32)
- A fresh `bd init` via yf-beads-init produces no instruction-file boilerplate, no `.codex/`,
  no `.agents/skills/beads/`, no beads `.claude/settings.json` hook, and leaves
  `core.hooksPath` at the git default; repair cleans an already-dirtied repo idempotently and
  no longer force-installs hooks. (#31)
- `yf-beads-hygiene` exists with the trigger contract; audit resolves edge targets via
  `bd show` over the full universe, classifies gate edges by status, never reports live-gate
  edges as dangling; destructive repair is confirmation-gated + followed by `bd dep cycles` and
  push; routes to yf-beads-init on a wedged DB; the #29 false-positive case is a passing test. (#29)
- `docs/recommended-settings.md` exists, ties each key to its rule/contract, flags the two
  highest-impact keys, covers user vs project scope, linked from README, valid GFM. (#30)
- Rust epics A and B land with `cargo test`/`cargo build` green and clippy/fmt clean (M1
  Verification Gate); no regression to existing `yf preflight` / `yf doctor` axes.
- `BEADS_INIT.md` carries the folded keep-worthy content (selective, token-efficient per DEC-2);
  a recorded fold map shows each BEADS.md section's disposition; yf-beads-init docs note the
  orphan rule's retirement; manifest hash refreshed; GFM-lint clean. (E)
- `yf-beads-upstream` treats unconfigured upstream as `none`; a github/gitlab origin on an
  unconfigured repo triggers the offer exactly once (then silent per DEC-3); explicitly-enabled
  configs are unaffected; `SKILL.md` + `UPSTREAM_TRACKING.md` document the default + offer; manifest
  hash refreshed. (F)
- All four upstream issues reconciled (closed with disposition notes); E and F verified delivered.

### Reconcile mechanics (M2, M3)
- **Closing #29–#32 (M2):** these are **pre-existing discrete upstream issues**, each closed on
  its own merits with a disposition note.
- **Coarse plan-012 tracking issue (M2b):** Epics E and F are net-new work with **no pre-existing
  upstream issue**. Per the repo's coarse upstream-tracking rule (AGENTS.md — one coarse issue per
  plan-scale effort), file **one** plan-012 tracking issue at land-the-plane that links the plan +
  epic and notes the E/F deliverables (and references the four discrete issues for completeness).
  Do **not** file granular per-epic upstream issues for E/F — they roll into this single coarse issue.
  **Additive-only (R7):** the coarse issue covers the **E/F deliverables only**; #29–#32 are closed
  independently and merely cross-linked from it, never folded into it or re-opened.
- **Release handoff (M3):** at reconcile, file a release bead (`discovered-from` this plan's
  epic) capturing "bump `yf/Cargo.toml` + tag to ship #31/#32 (and the rest)" so the
  out-of-scope release is tracked, not stranded in prose. Release is **not** executed by this plan.
