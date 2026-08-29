---
type: Review
okf_spec: OKF-PLAN
reviewer: red-team (adversarial) · **Presented:** 2026-07-17 · **Conformance pre-pass:**
  PASS
---
# Review pass 1 — plan-029-james-dixson-75fd34

**Reviewer:** red-team (adversarial) · **Presented:** 2026-07-17 · **Conformance pre-pass:** PASS

## Verdict: REVISE

## Strengths

- Findings-to-approach traceability is strong; the "fingerprint safe by construction" claim is
  genuinely substantiated (`_plan_content_sections` drops everything before the first `## `), and
  the residual "frontmatter above first `##`" invariant is gated with a stability test (2.5).
- SPEC-first sequencing is disciplined — every code epic depends on a SPEC issue.
- The highest-risk axis (grandfather clause + stale-approved) is properly gated by the Epic-2
  capability gate against a real migrated legacy plan; migration is opt-in with grandfathering.
- Vendoring respects the independent-installability invariant (`_shared/okf.py` + drift edges).
- The reviewer/red-team portability-section contract is NOT threatened (sections stay `##` headings).

## Concerns

1. **Epic 3 (yf-research) under-scopes the `_index.md` rename — it will ship broken.** severity: high
   `_index.md` is hard-coded beyond `index_manager.py`: `link_normalizer.py`
   (`rewrite_index`/`link_index`, filename AND table-column shape), `agents/packager.md` (step 5),
   `yf-research.formula.toml`, and `spec/portability.md` REQ-PORT-006. Renaming the reserved file
   without updating link-normalization silently breaks the research pipeline.
   **Recommendation:** expand Epic 3 to enumerate `link_normalizer.py`, `packager.md`, the formula
   description, the research spec, and `test_link_normalizer.py` as rename targets; add a
   research-side link-normalization end-to-end check to 5.2.

2. **The plan pursues the path research 001 recommended *against*, and Motivation omits this.**
   severity: medium
   Research 001's primary recommendation is export-emit / least-regret; it warns native-compliant
   frontmatter is high-cost against a draft standard for no fidelity gain, and that phase-log→log.md
   breaks REQ-PORT-006's in-`plan.md` reconciliation. Full-native is a legitimate operator choice,
   but Motivation cites research 001 as its basis while omitting that the research recommended the
   opposite.
   **Recommendation:** add an explicit override-rationale note to Motivation / Scope Decision #2.

3. **`agents/captor.md` is an unenumerated README.md producer.** severity: medium
   captor.md authors `README.md`; Epic 2 doesn't call it out.
   **Recommendation:** name `agents/captor.md` explicitly as an Issue 2.2 target.

4. **Existing tests seed the legacy layout — unaddressed breakage.** severity: medium
   `test_worktree.py` seeds `README.md` + `**Phase log:**`; `test-harness/smoke.sh` scaffolds
   `README.md`.
   **Recommendation:** add an Epic 2 / 5.2 item to update `test_worktree.py` and the smoke harness.

5. **Vendored-`okf.py` bootstrap during EXECUTE is unexamined for the two-address-space model.**
   severity: low
   Vendored `scripts/okf.py` must be committed on the worktree branch before Epics 2-4 invoke it;
   testing drives the worktree copy per TESTING.md, not the installed skill.
   **Recommendation:** add an execution note that 1.4 vendoring must land/commit before consumer
   epics invoke `okf.py`.

## Missing

- Research `packager.md` / formula handling in Epic 3 (see concern 1); `sources.md` `# Citations`
  SHOULD-gap silently dropped — state as explicit non-goal.
- No go-forward construction-correctness gate for research/incubator (only 5.2 smoke) — acceptable
  asymmetry, worth noting.
- `type` vocabulary has no single owner reconciling title-case consistency across the three skills
  (implicitly in 1.1).

## Gate Assessment

Start gate fine. Capability gate genuinely needed, well-targeted, valid runnable test — strongest
gate; only guards the plan migration path (research `_index.md` rename has no capability gate, only
5.2 smoke — consider extending). Reconcile gate correct type, matches coarse-granularity convention.

## Upstream Assessment

#83 include — correct (this plan is the integration #83 asks for; research→plan sequence honored).
#91 exclude — reasonable (completed research record, referenced not resolved), but #91 carries the
recommendation this plan overrides; tighten Notes to reflect the override relationship. No
disposition change.

## Operator Resolutions

| # | Concern (sev) | Resolution | Status |
|:--|:--|:--|:--|
| 1 | Epic 3 under-scopes `_index.md` rename fan-out (high) | Expanded Epic 3: added Issue 3.3 enumerating link_normalizer.py / packager.md / formula / research spec / test_link_normalizer.py as rename targets; extended 5.2 with a research link-normalization e2e check; extended the capability gate note | resolved |
| 2 | Motivation omits that research 001 recommended against full-native (medium) | Added override-rationale paragraph to Motivation + Scope Decision #2 | resolved |
| 3 | captor.md unenumerated README producer (medium) | Named `agents/captor.md` explicitly in Issue 2.2 | resolved |
| 4 | Legacy-layout tests unaddressed (medium) | Added Issue 2.6 (update test_worktree.py + smoke.sh) | resolved |
| 5 | Vendored okf.py EXECUTE bootstrap unexamined (low) | Added execution note to the Approach + Issue 1.4 | resolved |
