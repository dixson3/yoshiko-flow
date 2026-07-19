# Review pass 6 — plan-029-james-dixson-75fd34

**Reviewer:** red-team (adversarial), cycle 6 · **Presented:** 2026-07-18 · **Conformance:** PASS

## Verdict: APPROVE

## Strengths

All six pass-5 concerns genuinely resolved in the artifact (verified against current plan.md):

- **C1 (paths) resolved.** 2.1 and 2.2 frame corpus enumeration as a discovery step over BOTH roots —
  default `docs/{plans,research}` AND incubator-scoped `Incubator/<slug>/{plans,research}` + single-
  file/dir-form incubators; 2.2 explicitly says "do NOT assume top-level `plans/`."
- **C2 (greenfield frontmatter + engine-fix path) resolved.** 1.1 states merge-and-preserve as a REQ
  (add only `type:`/`okf_spec:`, never drop existing keys); 1.4 implements it with messy-input fixture
  tests; 2.3 routes engine-level findings to reopen 1.4; R10 exists.
- **C3 (R8 structural) resolved.** R8 is "structural, not procedural" (snapshot to scratch copy, all
  Epic-2 ops against the copy); 2.2 opens with snapshot-first.
- **C4 (1.5 dep) resolved.** 2.1 and 2.2 both `depends-on: 1.3, 1.4, 1.5`.
- **C5 (termination lever) resolved.** Ratification gate Instructions name R9 as the explicit lever.
- **C6 (crash-safe + version-drift) resolved.** Report-only/crash-safe REQ in 1.1(b)/1.4; 2.2 notes
  possible vault version/layout drift.

Dependency graph acyclic after adding 1.5 to 2.1/2.2. No ordering conflict between the composition
gate (proven by the 1.4 test) and the new 1.5 dep (1.5→1.4). The `assess` surface on 1.5 makes the
2.1/2.2→1.5 dependency semantically coherent.

## Concerns

None rising to high or medium. One low, non-actionable observation:

1. **Composition gate `Blocks` list vs. the 1.5 dependency.** severity: low
   The gate blocks 2.1/2.2 on the resolver (1.4 test) while 2.1/2.2 also structurally depend on 1.5 —
   two independent, both-satisfiable readiness constraints on the same beads. Correct as written.
   **Recommendation:** none required (optionally note the 1.5 dep in the gate for readers). Not a
   blocker.

## Missing

Nothing. The pass-5 "Missing" items (crash-safe REQ, vault version-drift acknowledgment) are present
in 1.1/1.4 and 2.2.

## Gate Assessment

Four gates well-placed and acyclic. The pass-5 caveat — that the ratification gate's "sample
migrations apply cleanly" test was only as sound as impact reports built from wrong paths + a
clobber-not-merge model — is now closed (C1 fixed paths; C2/R10 fixed merge-preserve), so the impact
reports feeding the gate rest on correct foundations. Ratification gate blocks 3.1/4.1/5.1;
composition and migrated-legacy gates target correct ids.

## Upstream Assessment

Unchanged and correct. #83 include; #91 exclude. Coarse single-issue-per-plan tracking intact.

## Operator Resolutions

| # | Concern (sev) | Resolution | Status |
|:--|:--|:--|:--|
| 1 | Composition gate Blocks vs 1.5 dep (low, non-actionable) | No change required — the two readiness constraints are independent and both satisfiable; noted for reader clarity only | resolved |
