# Plan Red-Team: plan-010-james-dixson-73eebd — pass 1

**Verdict:** REVISE
**Date:** 2026-06-14
**Status:** resolved (all concerns addressed in plan v2; operator approval pending)

## Strengths

- Investigation sufficient for the approach. `findings/exp-001` enumerates the full `install.py`
  responsibility set, both integrity axes, rename touch-points with counts, and the preflight
  kernel boundary. Verified: 13 skills, 7 `depends-on-skill` edges, `protocols/`+`manifest.json`
  distribution (5/7 rules have manifests), `.state/bdplan/` runtime root.
- R1 (cargo-dist `depends_on`) externally confirmed feasible via
  `[workspace.metadata.dist.dependencies.homebrew]` emitting `depends_on`. Mitigation sound.
- Dual-integrity-model risk (R4) correctly identified; Issue 3.4 `manifest_update.py` refresh +
  Gate G2 are the right controls.
- Sequencing rationale explicit; dependency chain coherent; gates guard genuinely irreversible
  steps.
- Upstream dispositions reasonable and verified live (#14, #15 OPEN; coarse granularity matches
  AGENTS.md precedent).

## Concerns

1. **Self-rename hazard: `bdplan → yf-plan` breaks the executor mid-flight** — severity: high.
   The skill driving this plan is installed at `~/.claude/skills/bdplan`. Epic 3.1/3.3 rename the
   dir, `SKILL_NAME`/`STATE_DIR` (`.state/bdplan → .yflow/yf-plan`), and the `SKILL_DIR` resolver
   is a hardcoded `find … -name bdplan`. During `/bdplan execute` of THIS plan, once Epic 3 lands,
   any bdplan subcommand re-resolving `SKILL_DIR` or reading `.state/bdplan/` against the renamed
   canonical tree can fail; the installed `~/.claude` copy still says `bdplan`, so driver and
   canonical tree diverge. R2 only covers the post-install steady state, not the during-execution
   hazard of renaming the orchestrator performing the rename.
   Recommendation: execute the `yf-plan`/`yf-research` rename (and `.state`/config moves) in the
   merge-back worktree per plan-009, run the driving session from the *installed* user-scope copy,
   and/or split the self-renaming skill's rename into a final step after plan-010 closes. State in
   Approach sequencing, not just R2.

2. **No tests/CI epic for the Rust crate as a first-class deliverable** — severity: high.
   Epic 4.3 mentions `cargo test` but no issue authors the tests and no epic owns crate-level
   verification. The crate reimplements parity-critical logic (frontmatter parsing, transitive
   closure, tree-hash, the `bd status --json` error-key invariant, the preflight status schema).
   G1/G2 are integration smoke-checks, not unit coverage. A `cargo test` with nothing to run is a
   hollow gate.
   Recommendation: add a testing issue/thin verification epic covering closure parity vs
   `install.py` (golden-file on the real `skills/` tree), tree-hash determinism + prune, marker
   inject/strip/verify, and the `bd status` error-key classifier. Make G1/G2 depend on it.

3. **Migration safety for `.state/`/config is "note only" with optional auto-migrate** — severity:
   medium. R3/Issue 3.6 reduce orphaning to a note ("optionally yflow migrates"). This repo itself
   carries `.state/bdplan/`. A manual note is fragile for the exact repo executing the plan.
   Recommendation: promote legacy-path read-and-migrate from optional to a defined idempotent Issue
   (`yflow` reads `.state/<oldname>/` + `.<oldname>.local.json` once and migrates). If it stays a
   note, drop "optionally" and make it a checklist item in the land step.

4. **Gate G2 tests only the happy path** — severity: medium. Condition lists
   ok/system_deps_missing/rule_drift but the Test only proves `.status` exists on one run.
   Condition and test are mismatched.
   Recommendation: drive all three states (missing-tool fixture, tampered-rule fixture) asserting
   the exact legacy status string for each, or fold into the testing issue and have G2 reference it.

## Missing

- An issue authoring the Rust crate's unit/parity tests.
- Explicit worktree/branch isolation for the self-renaming `yf-plan`/`yf-research` step.
- A defined (not optional) state/config migration path for the executing repo.
- Epic 3.2 names "7 edges" without listing `incubator`; minor (count is right).

## Gate Assessment

Three capability gates + human start gate, all on irreversible boundaries (correct, not
over-gated). But two are smoke-level and G2's test doesn't exercise its stated condition. Gates are
necessary and well-placed but not sufficient as the only verification — they need a tests issue
behind them.

## Upstream Assessment

Dispositions sound and verified. #14 supersede justified (logic genuinely reimplemented). #15
partial specific about in/out. New coarse tracking issue matches policy. Gap: Issue 5.3 should
specify the close-vs-leave-open action — close #14, and close-with-followup or comment-and-leave-
open #15 for the residual Python-helper scope.

## Operator Resolutions

| #   | Concern                                       | Severity | Resolution                                                                                                                                                                                                                                                                                                 | Status   |
| :-- | :-------------------------------------------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- |
| 1   | Self-rename hazard breaks executor mid-flight | high     | Added Approach §"Self-rename isolation (INV-1)"; new Issue 3.7 sequences `yf-plan`/`yf-research` dir+state+config rename as the LAST execution step, performed in the plan-009 merge-back worktree with the driving session pinned to the installed `~/.claude/skills/bdplan` copy; R7 records the hazard. | resolved |
| 2   | No tests/CI epic for the Rust crate           | high     | Added **Epic 6: yflow crate verification** (parity vs install.py golden-file, tree-hash determinism+prune, marker inject/strip/verify, `bd status` error-key classifier, preflight 3-state fixtures). G1/G2 now depend on Epic 6.                                                                          | resolved |
| 3   | Migration path note-only/optional             | medium   | Promoted to **Issue 2.7**: `yflow` idempotently reads legacy `.state/<old>/` + `.<old>.local.json` and migrates to `.yflow/<new>/` + `.<new>.local.json`; referenced as a checklist item in Issue 5.3. "optionally" dropped from R3.                                                                       | resolved |
| 4   | G2 happy-path-only test                       | medium   | G2 condition+test rewritten to drive all three states via Epic 6 fixtures (missing-tool, tampered-rule) and assert exact legacy status strings; G2 references Epic 6.                                                                                                                                      | resolved |
| 5   | Upstream close action unspecified             | low      | Issue 5.3 now specifies: close #14; comment-and-leave-open #15 noting residual Python-helper scope.                                                                                                                                                                                                        | resolved |
