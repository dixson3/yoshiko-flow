---
type: Review
okf_spec: OKF-PLAN
reviewer: red-team (adversarial), cycle 3 (post framework-reframe) · **Presented:**
  2026-07-17 ·
conformance: PASS (after fixing a stale `1.4`→`1.5` cross-ref)
---
# Review pass 3 — plan-029-james-dixson-75fd34

**Reviewer:** red-team (adversarial), cycle 3 (post framework-reframe) · **Presented:** 2026-07-17 ·
**Conformance:** PASS (after fixing a stale `1.4`→`1.5` cross-ref)

## Verdict: REVISE

## Strengths

- Dual-write hash-neutrality holds under inspection — frontmatter + `**Field:**` both sit in the
  preamble above the first `## ` (fields at lines 3-16, first `##` at 17); exp-001's positional
  exclusion makes dual-write hash-neutral by construction. R2 + fingerprint test (2.7) retained.
- All five pass-1 concerns survived the reframe/renumber (C1 fan-out → 3.4; C2 override paragraph;
  C3 captor.md → 2.4; C4 fixtures → 2.8; C5 bootstrap note → 1.5). None regressed.
- Dependency graph acyclic after renumber; the pass-2 fixture-freshness fix preserved (5.2 ← 2.7,
  2.8, 3.4, 4.3).
- R7 (dual-write divergence) is plausible with a complete mitigation chain (single writer,
  frontmatter-first read, audit consistency check 2.6, dual-representation test 2.7).
- SPEC-first discipline intact — every code issue depends on its SPEC/extension issue.

## Concerns

1. **Composition/resolver mechanism unspecified against the independent-installability invariant.**
   severity: medium
   The engine composes BASELINE ∪ YF-EXTENSIONS ∪ per-skill and is *vendored into each consumer*,
   but `OKF-BASELINE.md` / `OKF-YF-EXTENSIONS.md` live in `skills/yf-okf/spec/`, and skills cannot
   read each other (exp-002 — the reason vendoring exists). The plan never says how the
   vendored-into-yf-plan engine obtains BASELINE/YF-EXTENSIONS content without a cross-skill read, nor
   how `resolve_extension` resolves `skills/<skill>/OKF-EXTENSION.md` in the installed (not just
   worktree) address space.
   **Recommendation:** In Issue 1.1/1.3, specify (a) BASELINE+YF-EXTENSIONS rules reach the vendored
   engine without a cross-skill dependency (bake the machine-readable ruleset into `okf.py`; the
   `.md` docs are the human spec, kept in agreement by a drift edge), and (b) the resolver uses
   `__file__`-relative path resolution with each skill's `OKF-EXTENSION.md` bundled alongside its
   vendored `okf.py`. State which surface runs full `check_conformance`.

2. **Resolver/composition only proven end-to-end at Issue 5.2 (last issue); no unit test/gate before
   Epics 2-4 build on it.** severity: medium
   Issue 1.3's tests are "against REQ-OKF-*" but no real `OKF-EXTENSION.md` exists at 1.3.
   **Recommendation:** Add a resolver-composition unit test to Issue 1.3 using a synthetic fixture
   extension; consider a composition-resolution gate distinct from the migration capability gate.

3. **No owner/trigger for re-syncing `OKF-BASELINE.md` against upstream OKF drift.** severity: low
   **Recommendation:** File a follow-on bead for a BASELINE re-sync checkpoint keyed to upstream OKF
   version bumps; note it in R3.

4. **The SPEC placement invariant covers frontmatter but not the `**Field:**` block.** severity: low
   **Recommendation:** Extend the Issue 1.1 placement REQ to state *both* frontmatter and the
   `**Field:**` block MUST sit above the first `## `.

5. **22 issues / 5 epics is large for one land; no interior checkpoint.** severity: low
   **Recommendation:** Optional — note a natural landing checkpoint after Epic 2. Not a blocker given
   Scope Decision #6.

## Missing

The BASELINE/YF-EXTENSIONS→vendored-engine data path (C1); a statement of which surface runs full
`check_conformance`. `okf_spec:` key is present (not missing).

## Gate Assessment

Start gate fine. Epic-2 migrated-legacy capability gate remains strongest; dual-write consistency
correctly folded in via the 2.7 dual-representation test. Gap: the extension-resolver composition has
no gate and no pre-5.2 test (C2) — a unit test in 1.3 or a dedicated composition gate is proportionate
for a foundation dependency.

## Upstream Assessment

#83 include — correct, unchanged. #91 exclude — reasonable, framed as overridden research record. No
change.

## Operator Resolutions

| # | Concern (sev) | Resolution | Status |
|:--|:--|:--|:--|
| 1 | Resolver/composition unspecified vs independent-installability (med) | Issue 1.1 + 1.3 now specify: machine-readable BASELINE+YF-EXTENSIONS ruleset baked into `okf.py` (`.md` docs = human spec, kept in agreement by a drift edge); resolver uses `__file__`-relative path with each skill's `OKF-EXTENSION.md` bundled beside its vendored `okf.py`; `check_conformance` runs from any vendored copy | resolved |
| 2 | Resolver only proven at 5.2 (med) | Added resolver-composition unit test (synthetic fixture) to Issue 1.3; added a composition-resolution capability gate | resolved |
| 3 | No BASELINE re-sync owner (low) | Added to R3 mitigation as an explicit follow-on bead (filed at execution) | resolved |
| 4 | Placement invariant omits `**Field:**` block (low) | Extended Issue 1.1 placement REQ to cover both frontmatter and `**Field:**` | resolved |
| 5 | 22 issues large, no interior checkpoint (low) | Added an optional post-Epic-2 landing-checkpoint note to Scope Decision #6 | resolved |
