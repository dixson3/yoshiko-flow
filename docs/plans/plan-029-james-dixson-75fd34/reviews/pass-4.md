# Review pass 4 — plan-029-james-dixson-75fd34

**Reviewer:** red-team (adversarial), cycle 4 · **Presented:** 2026-07-17 · **Conformance:** PASS

## Verdict: APPROVE

## Strengths

All five pass-3 concerns genuinely resolved (verified against current plan.md):

- **C1 resolved.** Issue 1.1 states the machine-readable BASELINE + YF-EXTENSIONS ruleset is baked
  into `okf.py` (`.md` docs = human spec, kept in agreement by a `yf-drift-check` edge, no cross-skill
  read); `resolve_extension` uses `__file__`-relative resolution with each skill's `OKF-EXTENSION.md`
  bundled beside its vendored `okf.py`; `check_conformance` runs from any vendored copy in both
  address spaces. Independent-installability gap closed.
- **C2 resolved (defense in depth).** Issue 1.3 adds a resolver-composition unit test (synthetic
  fixture); a distinct Epic-1 "extension-resolver composition" capability gate blocks 2.4/3.3/4.3 and
  its Instructions test composition in a simulated installed address space.
- **C3 resolved.** R3 carries a follow-on bead (filed at execution) for a BASELINE re-sync checkpoint.
- **C4 resolved.** Issue 1.1 placement REQ now covers both the frontmatter and the `**Field:**` block.
- **C5 resolved.** Scope Decision #6 adds the optional post-Epic-2 interior-checkpoint note.

SPEC-first discipline and prior-cycle fixes (fan-out 3.4, captor.md 2.4, fixtures 2.8, bootstrap 1.5)
all retained. Dependency graph acyclic; the new composition gate blocks 2.4/3.3/4.3 which already
transitively depend on Epic 1 — no cycle, no new ordering contradiction. The two capability gates
guard orthogonal axes (resolver/installability vs fingerprint/grandfather).

## Concerns

None blocking. One low-severity cosmetic note:

1. **Composition gate Test cites `yf-okf check` on a fixture bundle; Instructions run the Issue 1.3
   test suite.** severity: low
   **Recommendation:** at execution, ensure the `yf-okf check` fixture bundle and the Issue 1.3
   synthetic fixture are the same artifact so gate and unit test prove against one fixture. Cosmetic;
   does not block approval.

## Missing

Nothing material. The BASELINE/YF-EXTENSIONS→vendored-engine data path is now explicit (baked-in
ruleset); the surface running `check_conformance` is answered (any vendored copy).

## Gate Assessment

Three gates coherent and acyclic. Epic-1 composition gate guards resolver/installability before the
construction repoints (2.4/3.3/4.3); Epic-2 migration gate guards fingerprint/grandfather safety
before 5.2 and Epic-2 merge; correctly does not gate 2.3 (dual-mode accessor, no resolver). Reconcile
gate auto on all beads closed.

## Upstream Assessment

Unchanged and correct. #83 include; #91 exclude (overridden research record). Coarse single-issue
upstream tracking per AGENTS.md.

## Operator Resolutions

| # | Concern (sev) | Resolution | Status |
|:--|:--|:--|:--|
| 1 | Gate fixture vs unit-test fixture consistency (low, cosmetic) | Noted for execution — Issue 1.3 synthetic fixture and the composition-gate `yf-okf check` fixture will be the same artifact | resolved |
