# Plan: Bundle: PEP-723 shared-helper consolidation (#15), bdplan audit invalid-JSON-on-control-chars fix (#36), beads auto-canonicalize yf projects on preflight/init (#39)

**ID:** plan-016-james-dixson-041b2f
**Author:** james-dixson
**Created:** 2026-06-24
**Status:** complete
**Epic:** beads-skills-mol-3ee
**Phase log:**
- 2026-06-24 scoping: initial scope captured
- 2026-06-24 investigating: 3 experiments: #39 canonicalization gap, #15 helper inventory + yf-owned-asset arch, #36 bug repro
- 2026-06-24 drafting: synthesizing plan: 3 epics — #15 vendoring sweep (zero Rust), #39 canonicalization (yf Rust), #36 regression+reconcile
- 2026-06-24 review: plan v1 presented
- 2026-06-24 approved: operator approved; portability audit pass
- 2026-06-24 intake: epic beads-skills-mol-3ee poured
- 2026-06-24 executing: start gate resolved
- 2026-06-24 reconciling: execution complete; entering reconcile
- 2026-06-24 complete: plan complete; #15/#36/#39 closed; merged b1b38a1; pushed

## Objective
Bundle: PEP-723 shared-helper consolidation (#15), bdplan audit invalid-JSON-on-control-chars fix (#36), beads auto-canonicalize yf projects on preflight/init (#39)

## Motivation

Three open upstream issues against `dixson3/yoshiko-flow` share a single maintenance theme —
reducing per-repo and per-skill manual toil — and are cheaper to land together than apart:

- **#15** — the same `shutil.which` tool-presence check (and other helpers) is duplicated
  across `install.py`, `plan_manager.py`, `research_manager.py`, and more. plan-014 shipped the
  in-repo `_shared/` vendoring pattern for *one* helper (the active-set classifier); the
  duplication of the rest remains. The real obstacle is **runtime import resolution** — an
  installed skill script has no stable path to a sibling shared module.
- **#36** — a concrete bug: `plan_manager.py audit --json-output` emits **invalid JSON** when a
  finding string contains a raw control character (tab/newline), breaking `json.load`
  (`Invalid control character at line 20`). Observed during plan-011 intake.
- **#39** — yf-enabled repos require partly-manual cleanup to reach the canonical local-only +
  upstream-sink end state; a live session (2026-06-24) found stray artifacts `yf doctor
  --repair` did not remove. Goal: zero-per-project manual cleanup. **May be partly addressed
  already** — status to be verified before scoping the work.

Bundling: #36 is a small contained bug; #15 and #39 are both "self-maintaining hygiene"
work in the same `yf`/skills substrate the operator is actively consolidating.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #15 | Consolidate duplicated Python helpers across skills (PEP-723 shared package route) | include | **Two-helper sweep** (`manifest_update.py`, defensive `--json` parser) via `_shared/` vendoring (option a). Tool-check is a false positive (already in `yf` kernel; symbols stale). | Epic A; reconciled D.1 |
| #36 | bdplan audit `--json-output` emits invalid JSON on control chars in findings | include | Bug **absent** from current source (already uses `json.dumps`). Regression test only. | Epic C; reconciled D.1 |
| #39 | beads: auto-canonicalize yf projects on preflight/init (strip stray hooks, untrack runtime jsonl) | include | 3 artifact-cleanup gaps in `beads_init::repair()` (2 auto, 1 confirm-gated) + preflight-converge wiring. `yf` Rust change. | Epic B; reconciled D.1 |
| #40 | PEP-723 micro-package route for shared helpers | exclude | **Spun out** during scoping. Deferred long-term alternative to `_shared/` vendoring. Not in scope. | n/a (deferred) |
| #41 | yf-owned `_shared/` via install-time deploy (option c) | exclude | **Spun out** during scoping. Makes `yf` the vendoring engine — the operator's stronger yf-owned-asset preference, guardrail-safe but not required for the sweep. | n/a (deferred) |

## Scoping decisions (operator)

1. **#15 route = extend `_shared/` vendoring**, not PEP-723. The PEP-723 micro-package route is
   recorded as deferred enhancement **#40** (filed during scoping). Consistency with plan-014,
   offline, no publish/versioning overhead.
2. **#15 breadth = broader sweep** — the tool-presence check **plus** other overlapping helpers
   (JSON parsers, manifest updaters, defensive `--json` parsing), not just the tool-check.
3. **Operator architecture preference (load-bearing):** keep as much shared content as possible
   in a **`yf`-owned asset directory**, minimizing content in the harness-native skills folders.
   Today `_shared/` is repo-root canonical but **vendors copies INTO skill-dir scripts** (runtime
   content still lives in skills/). Reconciling "yf-owned asset dir" with the
   "skills-can't-import-each-other / independently-installable" invariant is a **core design axis**
   for the #15 sweep (does `yf` grow a runtime asset-resolution path?). Investigated, not pre-decided.
4. **#39 posture = verify-first.** Investigate what `yf doctor --repair`/preflight canonicalization
   already does vs the issue's gap list; the auto-canonicalize-vs-propose-and-confirm call is made
   in PLAN, informed by how much is already safe to automate (repo default is propose-not-fix).

## Investigation plan

Pre-investigation checkpoint (experiments dispatched before drafting):

- **Exp 001 — #39 canonicalization gap (drives auto-vs-propose).** What does `yf doctor --repair`
  (and any preflight canonicalization) already do today, measured against #39's canonical
  end-state + gap list (stray hooks, untracked `interactions.jsonl`, `core.hooksPath`,
  local-only assertion, upstream-sink config)? What is genuinely unaddressed? Is the unaddressed
  remainder safe to auto-fix or does it need operator confirmation?
- **Exp 002 — #15 duplicated-helper inventory + yf-owned-asset architecture.** Enumerate the
  Python helpers actually duplicated across skills (broader sweep: tool-check, `--json` parsing,
  manifest updaters, json-get, etc.). Then the architecture question: can `yf` **own/serve** shared
  assets at runtime (embed `_shared/` + expose a resolution path/command) so skill scripts resolve
  shared helpers from a yf-owned location instead of carrying vendored copies — while preserving
  independent installability? Compare: (a) extend current vendoring, (b) yf-owned runtime asset
  resolution. Recommend an architecture for the sweep.
- **Exp 003 — #36 bug reproduction + fix site.** Reproduce the invalid-JSON-on-control-chars bug
  in `skills/yf-plan/scripts/plan_manager.py audit --json-output` (craft a finding with a
  tab/newline). Confirm still present; identify the exact serialization site and the minimal fix
  (proper JSON escaping / `json.dumps` with default escaping rather than manual string building).

## Investigation Findings

Three experiments (full reports in `findings/`):

- **`exp-001-39-canonicalization-gap.md` → hybrid; 3 real gaps; a `yf` Rust change.** `yf doctor
  --repair` (`beads_init::repair()`) already does most of #39. The genuine remainder is the
  live-session axis — *untracking* and *remote removal*: (1) `git rm --cached`
  `.beads/interactions.jsonl` + pre-tracked dolt artifacts (**safe-to-auto**), (2) `git rm` the
  dead tracked `.beads/hooks/*` shims, content-guarded (**safe-to-auto**), (3) remove the Dolt
  remote / `sync.remote` under `--local-only` (**needs-confirm**, destructive — gate behind
  `--remove-remote`). Lives in `beads_init.rs` native steps + a `cli.rs` flag + `yf-beads-init`
  docs. Preflight does no canonicalizing/destructive mutation (its only sanctioned write is the
  additive gitignore scaffold); "converge on preflight" = skills offering/calling `yf doctor
  --repair` via preflight's existing instructions channel, not preflight mutating.
- **`exp-002-15-helper-inventory-arch.md` → two-helper sweep via extended vendoring; zero Rust
  (option a).** The sweep is **`manifest_update.py`** (5 byte-identical copies → 1 canonical) and
  the **defensive `--json` parser** (3 divergent impls → `_extract_first_json`, which also fixes a
  latent correctness bug in yf-plan's weaker `json-get`). **Leave** the `shutil.which` tool-check
  (false positive; the real check already migrated to the `yf` kernel — #15's `_SYSTEM_DEPS`/
  `missing_tools` symbols are **stale**) and PEP-723/argparse (non-shareable). Runtime yf-owned
  assets (option b) are **structurally blocked** (break independent installability, trip GR-003);
  the operator's yf-owned preference is honored at the **authority layer** (canonical in `_shared/`,
  copies are generated artifacts). Making `yf` literally own `_shared/` is **option (c)**
  (install-time deploy, medium Rust) — guardrail-safe but **not required** for the sweep; an open
  decision (ship on (a) now vs bundle (c)).
- **`exp-003-36-audit-json-bug.md` → bug NOT present in current source.** `audit --json-output`
  already uses `json.dumps` (`plan_manager.py:2007`), which escapes control chars — the defect was
  in the old installed `bdplan` copy, not this repo. Action: add a **regression test** to pin the
  invariant + **close #36** as already-fixed. No production code change.

## Approach

Three independent epics, each scoped tightly by the investigation. The three issues turned out
**very differently sized** than their titles suggested, so the plan follows the evidence rather
than the original framing:

- **#15 (Epic A) — a two-helper vendoring sweep, zero `yf` Rust change.** Extend the proven
  plan-014 `_shared/` pattern to the two genuinely-duplicated helpers (`manifest_update.py`,
  defensive `--json` parser). Operator-chosen **option (a)**: canonical in repo-root `_shared/`,
  copies are generated artifacts. The stronger "yf literally owns `_shared/`" route is deferred to
  **#41** (option c, install-time deploy).
- **#39 (Epic B) — the real work: a `yf` Rust change** to `beads_init::repair()` plus
  preflight-converge wiring. Three artifact-cleanup steps (two auto, one confirm-gated) and routing
  the beads skills' preflights to **offer/run `yf doctor --repair`** so a drifted repo converges
  without preflight itself mutating (preserving the read-only-preflight invariant).
- **#36 (Epic C) — a regression test only.** The bug is absent from current source; pin the
  invariant with a test and close upstream.

Decision record (operator, this plan): **#15 = option (a)** (extend vendoring; option (c) → #41,
PEP-723 → #40); **#39 = artifact gaps + preflight-converge**; **#36 = test + close** (no fix).

The three epics are mutually independent (different files: `_shared/` + skill scripts; `yf/src/`;
`test_worktree.py`) and parallelizable; only the reconcile step joins them.

## Epics

### Epic A: #15 helper consolidation — extend `_shared/` vendoring (zero `yf` Rust)

- Issue A.1: Add `_shared/manifest_update.py` as canonical and **extend `_shared/sync.py` with a
  whole-file copy mode** (the existing mode syncs marker-fenced *regions*; `manifest_update.py` is a
  100%-shared whole file). **Mode choice (red-team C4):** whole-file copy is preferred over wrapping
  the body in BEGIN/END markers because a 100%-shared file should not carry in-band vendoring
  markers (they would pollute every consumer and the canonical alike); marker-wrap remains an
  acceptable fallback if whole-file mode proves more invasive to `sync.py` than expected. Register
  the 5 consumers (`yf-beads-upstream`, `yf-optimal-instructions`, `yf-plan`, `yf-research`,
  `yf-skill-authoring`) in the `CONSUMERS`/canonical map; regenerate all 5 copies from canonical so
  they are byte-identical generated artifacts. `sync.py --check` green.
- Issue A.2: Consolidate the **single-value defensive `--json` extractor**. Promote
  `research_manager.py`'s `_extract_first_json` (strongest: warning-prefix + concatenated-array
  tolerant, list-index aware) to `_shared/` canonical; vendor it into `plan_manager.py` and
  `research_manager.py`. **Scope is precise (red-team C1):** this replaces **only the `json-get`
  command's bare `json.load`** in `plan_manager.py`. It does **NOT** touch `plan_manager.py`'s
  `_parse_bd_json` — that helper has a **different contract** (returns a *flat list* of issue dicts,
  unwraps the `{"issues":[…]}` envelope, flattens *multiple* concatenated docs) and `_bd_list`
  depends on that flattening; `_extract_first_json` (first balanced value only) is **not** a superset
  of it. Leave `_parse_bd_json` in place, unmerged (a candidate for a *separate* canonical helper in
  a future sweep, not this one). **This is an intentional `json-get` behavior change, not pure
  preservation (red-team C2):** the canonical extractor adds list-index support (`data[int(key)]`
  succeeds where the old `json.load` path raised) and changes the error-string text — that *is* the
  latent-correctness fix. Verify no skill caller parses `json-get`'s old error string; the happy-path
  CLI contract is otherwise unchanged.
  - depends-on: A.1 (the `sync.py` mode it relies on)
- Issue A.3: Wire enforcement — add DRIFT-CHECK.md `value-equal` edges for each new canonical→copy
  pair (mirror `e-active-set-copy-*`) + add the new consumers to the trigger-scope node table;
  extend `_shared/test_sync.py` to cover the new canonical sources and the whole-file mode.
  - depends-on: A.1
  - depends-on: A.2

### Epic B: #39 canonicalization — `yf doctor --repair` cleanup + preflight-converge

- Issue B.1: Add three **native** cleanup steps to `beads_init::repair()` (`yf/src/beads_init.rs`,
  alongside the existing cleanup block / `apply_native` dispatch):
  (1) **auto** `git rm --cached` of a **pinned untrack set (red-team M1):** `.beads/interactions.jsonl`
  plus the dolt runtime artifacts named in #39 — `.beads/embeddeddolt/`, `.beads/backup/`,
  `.beads/export-state.json`, `.beads/push-state.json`, `.beads/dolt-server.*` — restricted to paths
  **currently tracked** (idempotent no-op when untracked; `--cached` keeps the working file). The
  exact set is a constant so it is deterministic and testable.
  (2) **auto** remove tracked `.beads/hooks/*` shims, **content-guarded** by the `bd hooks run`
  signature (never remove a hand-edited hook);
  (3) **confirm-gated** Dolt-remote / `sync.remote` removal under `--local-only`, behind a new
  `--remove-remote` flag plumbed as `remove_remote: bool` through `DoctorArgs` → `repair()`.
- Issue B.2: **Preflight-converge wiring** — route the beads skills' preflights to **offer/run `yf
  doctor --repair`** when canonicalization drift is detected, so a drifted repo converges with zero
  manual cleanup. **Invariant (red-team C3):** preflight performs **no canonicalizing/destructive
  mutation** — the existing additive gitignore scaffold (`ensure_scaffold`) is the only sanctioned
  preflight write, and B.2 adds none; the offer is emitted through preflight's **existing
  `instructions` channel** (it already surfaces `Run: yf doctor --repair` on the Corrupted path), not
  a new write path. The actual mutation is the explicit `doctor --repair` invocation. **Entry-point
  coverage (red-team C5):** the beads skills (`yf-beads-init`, `yf-beads-extra`, `yf-beads-upstream`,
  `yf-beads-hygiene`, and `yf-plan`/`yf-research` preflights) converge through the **single shared
  `yf preflight` kernel path**, so one wiring covers all of #39's listed entry points; enumerate any
  that bypass that path. Honor interactive-vs-read-only context (an offer that can't persist a
  decision must not nag — mirror the existing upstream/beads-init one-shot offer patterns).
  - depends-on: B.1
- Issue B.3: Rust tests for the new repair steps (untrack idempotency; shim content-guard
  positive/negative; remote-removal gated off by default, on with `--remove-remote`) + update
  `yf-beads-init` `SKILL.md`/`SPEC.md` — correct the `beads_init.rs:320` "never adds a Dolt remote"
  framing and the `--local-only` "asserts the flag / accepts no-remotes" docs to describe the new
  reach-empty-remote behavior.
  - depends-on: B.1
  - depends-on: B.2

### Epic C: #36 regression test (bug already absent)

- Issue C.1: Add a regression test in `skills/yf-plan/scripts/test_worktree.py` (the suite already
  `importlib`-loads the module + uses `CliRunner`): an `audit --json-output` whose finding
  `detail`/`report` contains a raw tab/newline round-trips through `json.loads(output)` with control
  chars preserved. Pins the `json.dumps` invariant against future manual-assembly regressions.

### Epic D: Reconcile

- Issue D.1 (reconcile step): update upstream — **close #36** (already-fixed in current source;
  regression test landed), **close #15** (two-helper sweep delivered via `_shared/` vendoring; note
  the stale `_SYSTEM_DEPS`/`missing_tools` premise and the deferred routes), **close #39** (3
  canonicalization gaps closed + preflight-converge wired). Note **#40** (PEP-723) and **#41**
  (yf-owned `_shared/`) remain open as the deliberately-deferred follow-ons. **Coarse convention
  (AGENTS.md):** #15/#36/#39 are the plan-scale tracking issues — D.1 closes/annotates *those three*
  directly and does **not** push granular sub-beads upstream. Close #39 only after confirming B.2's
  entry-point coverage and B.1's untrack set actually meet #39's acceptance list.
  - depends-on: A.3
  - depends-on: B.3
  - depends-on: C.1

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: shared-helper sync clean
- Type: auto (verified by Test)
- Condition: after A.1/A.2 vendor the new canonical helpers, every generated copy matches canonical
  (no drift) — the `_shared/` invariant holds.
- Test: `uv run _shared/sync.py --check`
- Blocks: A.3 close
- Instructions: if `--check` reports divergence, run `uv run _shared/sync.py` to regenerate, review
  the diff, and re-run.

### Capability Gate: `yf` Rust + parity green (red-team gate gap)
- Type: auto (verified by Test)
- Condition: Epic B's `beads_init.rs`/`cli.rs` change builds and the full Rust suite — including the
  `parity::*` golden — passes before reconcile.
- Test: `cargo test --workspace`
- Blocks: D.1
- Instructions: fix any failure; if the `parity::*` golden diverges from a legitimate
  frontmatter/group change, regenerate it (`uv run yf/src/testdata/gen-install-parity.py >
  yf/src/testdata/install-parity.json`) per the plan-015 precedent, review the diff, and re-run.

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: D.1

## Risks & Mitigations

- **`beads_init::repair()` does destructive git ops.** *Mitigation:* `git rm --cached` is
  non-destructive (keeps the working file); shim removal is **content-guarded** to the `bd hooks
  run` signature; remote removal is **confirm-gated** behind `--remove-remote` (off by default).
  Every step is idempotent — a no-op when the repo is already clean, matching the existing native
  repair steps.
- **Crossing the "never adds a Dolt remote" design boundary.** The new remote *removal* inverts an
  intentional boundary (`beads_init.rs:320`). *Mitigation:* it is opt-in only, documented in B.3's
  SKILL/SPEC updates, and the default behavior (assert `--local-only`, leave remote untouched) is
  unchanged.
- **Preflight-converge could make preflight mutate (breaking the read-only invariant).**
  *Mitigation:* B.2 keeps preflight detection-only; the mutation is an explicit `yf doctor --repair`
  invocation. The offer must not nag in read-only contexts (reuse the established one-shot offer
  pattern).
- **Whole-file `sync.py` mode is new machinery.** *Mitigation:* A.3 extends `test_sync.py` to cover
  it; the capability gate (`sync.py --check`) and DRIFT-CHECK edges backstop divergence.
- **Consolidating `json-get` could change yf-plan/yf-research CLI behavior.** *Mitigation:* the
  canonical `_extract_first_json` is a strict superset of the weaker impl; A.2 preserves each
  script's public CLI and is covered by their existing test suites + the merged-tree validation.
- **`yf` Rust change must stay parity-green.** *Mitigation:* B.3 Rust tests + the existing
  `parity::*` golden; if frontmatter/group data shifts, regenerate the golden (precedent: plan-015
  `install-parity.json`).

## Success Criteria

- **#15:** `manifest_update.py` exists once in `_shared/` with 5 byte-identical generated consumer
  copies; the defensive `--json` parser is canonical in `_shared/` and vendored into `plan_manager.py`
  (weaker `json-get` retired) + `research_manager.py`; `uv run _shared/sync.py --check` is green;
  DRIFT-CHECK edges + `test_sync.py` cover the new pairs. **Zero `yf` Rust change for Epic A.**
- **#39:** `yf doctor --repair` untracks `.beads/interactions.jsonl`, removes dead content-guarded
  `.beads/hooks/*` shims, and (with `--remove-remote`) clears the Dolt remote / `sync.remote`; the
  beads skills' preflights offer/run `doctor --repair` on detected drift while preflight stays
  read-only; Rust tests + `yf-beads-init` docs updated; `parity::*` green.
- **#36:** a regression test asserts `audit --json-output` round-trips control-char findings through
  `json.loads`; no production code change; #36 closed as already-fixed.
- **Upstream:** #15, #36, #39 reconciled (closed); #40 (PEP-723) and #41 (yf-owned `_shared/`)
  remain open as recorded deferrals.
- **Merged-tree validation green** via this repo's approved `CHANGE-VALIDATION.md` FULL tier
  (plan-015 dogfood) — including the new `_shared/` sync and the `yf` Rust change.
