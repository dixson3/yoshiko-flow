# Plan Red-Team: plan-026-james-dixson-6e0e2f — pass 3 (post-approval #85 delta)

**Context:** plan-026 was approved (pass-2 APPROVE), then reopened to fold upstream issue **#85**
(absorb `md_table_align.py` → new ML012 alignment rule) into scope. This pass re-reviews the
revised plan, focused on the #85 delta and whether the prior scope remains sound.

## Verdict: APPROVE

The #85 delta integrates coherently; the prior scope is unchanged and still sound. All three
concerns are low / low-medium — none block. Rule-number and wiring claims were verified against
real code.

## Strengths

- **Cohesion is genuine** — #85 is another change to the *same* `yf-markdown-lint` skill as
  #81/#48/#46-lint, landing in the same Epic 1 and extending the existing ML005/ML008 table
  checks. Folding it in beats spawning a near-duplicate plan.
- **Rule number is conflict-free** — `ALL_RULES` ends at ML009; ML010/ML011/ML012 are the next
  three free slots.
- **Dependency wiring is correct** — 1.6 `depends-on: 1.1` (SPEC-first); 1.5 now
  `depends-on: 1.2,1.3,1.4,1.6`. No dangling edges.
- **Tier decision defensible** — ML012 in full-audit (not the authoring subset) matches the
  heavier whole-table reflow; the subset enumeration is correctly left untouched for ML012.
- **Reconcile gate + upstream extended cleanly** — gate lists #85 (reconciles when 1.6 closes);
  coarse tracker #82 references #85.

## Concerns

- **C1 — Reference impl names an un-checked-out repo — severity: low-medium.**
  The plan cites the source as `dixson3/obsidian-primary:scripts/md_table_align.py` in five
  places, but that repo is not checked out locally. The reachable copy is
  `dixson3/d3-pxe/scripts/md_table_align.py` (locally present, ~6 KB, stdlib-only, `--check`/`--write`).
  Recommendation: point Issue 1.6 at the locally-present d3-pxe copy as the vendoring source, with
  a `gh api` fallback for obsidian-primary; confirm the two are byte-identical before treating
  either as canonical.

- **C2 — Mutating `--write` mode is a new capability with no dedicated REQ, and the entry point is
  ambiguous — severity: low-medium.**
  `markdown_lint.py` is today a pure read-only reporter. The plan preserves the aligner's `--write`
  in-place mode but is ambiguous about whether it is exposed through `markdown_lint.py` or stays on
  the standalone script with ML012 shelling out for `--check` only. In-place rewriting is a distinct
  observable behavior deserving its own SPEC line.
  Recommendation: in Issue 1.1 add an explicit `REQ-MDLINT-*` for the idempotent autofix/mutation
  behavior (separate from the ML012 check REQ); in Issue 1.6 state the single canonical `--write`
  entry point.

- **C3 — Alignment check split from its sibling across tiers — severity: low.**
  ML008 (alignment-marker presence) runs in the authoring subset; ML012 (reflow) runs full-audit
  only, so an author won't learn a table is mis-aligned until the full audit. Defensible (reflow is
  heavy); noted, no change required.

## Missing

- The explicit SPEC requirement for the mutating `--write` mode (folded into C2). Everything else
  the delta touches is enumerated in Issues 1.1/1.5/1.6.

## Gate Assessment

Start gate (human/operator) unchanged and appropriate. Reconcile Gate correctly extended: #85 added
to the incorporated set and bound to Issue 1.6 closure; the #46 partial-split (1.4 + 2.2) preserved.
No gate gap introduced.

## Upstream Assessment

#85 `include` disposition is specific and consistent with its Notes (vendor → wire ML012 `--check`
full-audit + `--write` → document → consumer-migration note). Coarse-tracking honored: #85 rolls
into the single plan-026 tracker (#82), not a granular push. Consumer-migration follow-up
(obsidian-primary, d3-pxe dropping vendored copies) is correctly a downstream consequence, not
smuggled into scope.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
|:--|:--------|:---------|:-----------|:-------|
| C1 | Reference impl names un-checked-out obsidian-primary | low-medium | Issue 1.6 + Motivation/Scope/Approach repointed to the locally-present `d3-pxe` copy as vendoring source, with `gh api` fallback for obsidian-primary and a byte-identical-confirmation step | resolved |
| C2 | `--write` mutation mode has no dedicated REQ; entry point ambiguous | low-medium | Issue 1.1 adds an explicit `REQ-MDLINT-*` for idempotent autofix; Issue 1.6 states the canonical `--write` entry point (standalone script; ML012 shells out for `--check`, ML009-style) | resolved |
| C3 | ML008/ML012 split across tiers | low | Accepted as-is (reflow is heavy); already noted in the Risks table | resolved (accepted) |
