# Plan Red-Team: plan-024-james-dixson-76cee9 — pass 1

## Verdict: REVISE

Conformance (mechanical) pass returned **PASS** (all checklist items satisfied). The adversarial
red-team returned **REVISE** with one high-severity and three medium-severity concerns.

## Strengths

- Investigation findings are accurate and verified: `update_status` is genuinely free-form (no
  enum change needed), `_shared/sync.py --check` is a real vendoring + change-validation surface,
  and the bd primitives (`bd mol stale --json`, `bd children --json`, `bd close -f`) exist as
  claimed.
- The cascade-close fail-loud contract (REQ-PLAN-067) matches upstream #73's "Expected" verbatim
  and correctly does not hide the incomplete-plan signal; wiring the halt to *not* set `complete`
  is the right enforcement point.
- SPEC-first sequencing is correct in both epics (the `REQ-*` edit has no `depends-on`; code/test
  issues depend on it transitively).
- Both upstream issues are genuine `include` dispositions, mapped 1:1 to an epic.

## Concerns

- **C1 (high): the `_shared/` extraction rests on a phantom second consumer.** yf-beads-authoring
  has no `scripts/` dir and no `agents/coordinator.md` (only `reviewer.md`) — it is a *conventions*
  skill and can carry at most a prose cross-reference, not run a vendored helper. The
  "land-the-plane sweep" consumer is not scheduled as any issue. That leaves exactly one real
  runtime consumer (yf-plan), and a future sweep would live in `skills/yf-plan/scripts/` anyway
  (same skill, no cross-skill vendoring). Rule-of-three is not met; Issue 2.5 as written is not
  executable.
  Recommendation: land the helper directly in `skills/yf-plan/scripts/close_cascade.py` (no
  `_shared/` extraction, no sync/drift row) until a genuine second in-repo runtime consumer
  exists; if a cross-skill pointer is still wanted, rewrite 2.5 to target yf-beads-authoring
  *doctrine* as a documentation pointer, not a code consumer.

- **C2 (medium): status-enumeration audit misses two source-of-truth points.** (1) `spec/phases.md`
  REQ-STATUS-001 hard-counts "Exactly 8 status values" + enumerates them — adding
  `ready-for-approval` makes 9; the count and list must be amended (Issue 1.1 says only "update
  spec/phases.md" generically). (2) `SKILL.md` status-vocabulary line is the declared source of
  truth for the `DRIFT-CHECK.md` `e-status-values` edge; if it is not updated, drift-check FAILs.
  Recommendation: add explicit edits to 1.1 (REQ-STATUS-001 count+list) and 1.4 (SKILL.md
  vocabulary line), and note `e-status-values` as the backstop.

- **C3 (medium): Issue 1.3 mischaracterizes the execute-eligibility gate.** Execute/resume keys on
  the fingerprint (`stale_approved`), not `status == "approved"` in the script; the literal
  `approved` filter lives in SKILL.md §5.1 doctrine. A `ready-for-approval` plan is correctly
  non-eligible, but the audit target is the wrong artifact.
  Recommendation: point 1.3 at SKILL.md §5.1 (the `approved` + fresh-fingerprint filter) as the
  real eligibility surface; keep the not-execute-eligible test framed against that doctrine.

- **C4 (medium): cascade helper's "all children closed" predicate does not define gate handling.**
  `resume-scan` excludes `issue_type == "gate"` from open-work accounting because a gate can be
  resolved/verified without `status: closed`. Treating `closed` as the sole terminal state would
  report a container whose only non-closed child is a *resolved* gate as `blocked` — a false
  fail-loud that halts a genuinely-complete plan.
  Recommendation: define "all children terminal" in REQ-PLAN-067 / Issue 2.2 consistently with
  resume-scan's gate treatment (a resolved/verified gate is terminal); add a 2.6 test for a
  resolved-not-closed gate child.

## Missing

- **M1:** the "land-the-plane sweep" consumer named in the Objective/justification is not scheduled
  (no issue/gate/follow-up). Drop it from the justification or file it.
- **M2:** no coverage of the REQ-PLAN-031 `count(pass-*.md) == count(review: lines)` invariant under
  the new re-run-red-team loop — state that each re-run still writes exactly one `pass-N.md` + one
  `review:` line.
- **M3:** fingerprint-write timing across the new `ready-for-approval → approved` split is
  unspecified — the audit runs at `ready-check` (before approval) while `**Fingerprint:**` is
  written at approval (REQ-PLAN-034). A content edit between the two could let a stale-but-audited
  plan be approved. State that ready-check and approval are adjacent / ready-check re-validates at
  approval time.

## Gate Assessment

Gates are appropriate and not over-used. The Capability Gate is a near-no-op assertion (bd ≥ 1.1.0
already required) — acceptable. If C1 is accepted and `_shared/` extraction is dropped, the
`sync.py --check` merged-state row no longer applies to this helper and the DRIFT-CHECK
`e-status-values` edge becomes the key Epic-1 backstop.

## Upstream Assessment

Dispositions sound (#69 → Epic 1, #73 → Epic 2, both `include`, no partials/supersedes). One
nuance: #73's acceptance says the cascade reaches "up through the epic → molecule hierarchy"; the
plan scopes the walk to "the plan's epic subtree" bottom-up — confirm the **top-level plan
molecule itself** is in the close set (the plan-002 `mol-bw0` example), not just intermediate epic
children.

## Operator Resolutions

| # | Concern (sev) | Resolution | Status |
|:--|:--|:--|:--|
| C1 | `_shared/` extraction / phantom second consumer (high) | Operator chose: land helper in `skills/yf-plan/scripts/close_cascade.py`; drop `_shared/` extraction + sync/drift row; Issue 2.5 becomes a doctrine cross-reference only. Objective/Approach/Epic 2 revised. | resolved |
| C2 | status-enum audit misses REQ-STATUS-001 + SKILL.md vocab line (med) | Issue 1.1 now amends `spec/phases.md` REQ-STATUS-001 count (8→9) + list; Issue 1.4 updates the SKILL.md status-vocabulary line; `e-status-values` drift edge noted as backstop. | resolved |
| C3 | Issue 1.3 wrong eligibility surface (med) | Issue 1.3 re-pointed at SKILL.md §5.1 (`approved`+fingerprint filter) as the real eligibility surface; test frames `ready-for-approval` non-eligibility against that doctrine. | resolved |
| C4 | cascade predicate gate handling / false fail-loud (med) | REQ-PLAN-067 / Issue 2.2 define "terminal" to include a resolved/verified gate (align with resume-scan); Issue 2.4 adds a resolved-gate test. | resolved |
| M1 | land-the-plane sweep unscheduled (missing) | Dropped from the justification (Objective/Approach); noted as a possible future consumer living in the same yf-plan `scripts/`. | resolved |
| M2 | REQ-PLAN-031 count invariant under re-run loop (missing) | Issue 1.1 notes each red-team re-run writes exactly one `pass-N.md` + one `review:` line, preserving the count invariant. | resolved |
| M3 | fingerprint timing across ready-for-approval→approved (missing) | Issue 1.1 notes ready-check and the approval transition are adjacent (ready-check re-runs at approval), so no content edit slips between a green check and the fingerprint write. | resolved |
| U1 | top-level plan molecule in close set (upstream nuance) | REQ-PLAN-067 / Issue 2.2 explicitly include the top-level plan molecule in the close set; Success Criteria + 2.4 test updated. | resolved |
