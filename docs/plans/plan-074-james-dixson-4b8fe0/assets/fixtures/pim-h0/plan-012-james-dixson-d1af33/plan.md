---
type: Plan
okf_spec: OKF-PLAN
description: Bounded H0 regression bootstrap and proposed current-format safety contract,
  without future-capability certification or storage/lifecycle repairs.
id: plan-012-james-dixson-d1af33
author: james-dixson
created: '2026-10-28'
status: executing
deliverable_class: standard
fingerprint: 2dd5d32c657cac2a4b15027285cf62f1760181494fbd3b46aa6b143aa05d2db7
epic: pim-mol-vp2
---
# Plan: Reloadable multi-app regression foundation and bounded current-format contract

**ID:** plan-012-james-dixson-d1af33
**Author:** james-dixson
**Created:** 2026-10-28
**Status:** executing
**Deliverable-class:** standard
**Epic:** pim-mol-vp2
**Fingerprint:** 2dd5d32c657cac2a4b15027285cf62f1760181494fbd3b46aa6b143aa05d2db7

## Objective

Establish a finite, reloadable real-PIM regression foundation for #36 and a bounded, explicitly accepted current-format admission/reload contract for #27. Deliver a strict fixture loader, real SQLite/Git/library/CLI adapters, semantic oracles, machine-readable per-cell outcomes and fail-closed certification selection. Bootstrap records known defects and accepted-unimplemented behavior honestly; it neither repairs every capability nor certifies them by reproducing their failures.

## Motivation

The operator permits incremental real-core hydration without backward compatibility or forward migrations, but requires strong reusable multi-app regressions. Existing tests and frozen investigations provide useful evidence, not a unified correctness oracle: some historical green probes demonstrate defects, while accepted lifecycle/deletion decisions are not implemented. This plan supplies the bounded foundation before later slices, rather than pouring plan-010's broad roadmap or waiting for all future storage/BPMN work.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #36 | H0 reloadable corpus and real-backend gates | partial | Deliver finite bootstrap profile, loader, report and gate machinery; future capabilities and additional certification remain open. Do not claim whole-issue completion or waive #40 prerequisites. | 4.2 |
| #27 | Current-format safety and reloadable fixtures | partial | Publish only the explicitly accepted bounded contract and inventory; safe-open/admission/recovery fixes remain separately owned. No migrations or active-store obligations. | 1.2 |
| #46 | plan-012-james-dixson-d1af33 execution tracking | tracker | https://github.com/dixson3/pim/issues/46 — intake mirror pim-w3p; execution epic not yet poured | execute/reconcile |

#14–#22 remain live upstream defects, not completed local hoist markers. Current full bodies are preserved in references/defect-14.json through defect-22.json. This plan neither closes nor supersedes those issues. #28, #39, #40/#41 and #29/#30 retain their separate implementation/certification ownership; #37 standards and plan-011 tooling remain separate.

## Investigation Findings

[EXP-001](findings/exp-001-real-backend-seams.md): disposable existing SQLite/Git journal/sync tests passed (13 total) and CLI app tests passed (10 total). Reuse Store/Journal/pim-app and actual CLI in a non-published test-support crate. Existing low-level Facade is SQLite-only; Rust facade tests are not actual Node/Python runtime proof. Current source corroborates individually owned #14–#22 failure paths; these defects were not all freshly reproduced.

[EXP-002](findings/exp-002-semantic-oracles.md): issue, guidance, provenance, foreign-dependency and cyclic non-task seeds can reuse frozen scenario intent. Historical probe passes sometimes mean a defect reproduced; plan-008 participation and plan-009 named-deletion targets remain accepted-unimplemented. All 16 overview source pins match; planning alone needs no re-pin. Main planner read accepted operator-decision records independently before synthesis.

Investigators inspected baseline-identical code at 78c714ce2c87a6e97ca85703e36ef32e1af96e08; production/test sources matched requested baseline 098ee943080fa0f2a8e389e8b47dfdeaf9b13cad. Development worktree is `.worktrees/plan-012-james-dixson-d1af33-development`, pinned to that requested baseline. Tracking wisp is `pim-wisp-bsm`; no execute molecule was poured.

## Approach

### Bounded architecture and authority

Use `crates/pim-regression` as a non-published workspace test-support crate with `fixture`, `loader`, `oracle`, `runner`, `result` modules and a `pim-regression` binary. Inputs live in `tests/regression/`; policy/coverage docs in `docs/regression/`. Reuse real production APIs; no replacement readiness, participation, deletion or BPMN engine. Workspace/Cargo.lock changes are allowed only for the test harness. Production semantics remain unchanged.

[Corpus contract](design/corpus-contract.md) defines the finite floor: ten executable/calibration families, nine individually owned defect families and two accepted-unimplemented guards; mandatory SQLite/Git live/reopen/reconstruction cells, exact-stream replay, bounded Git schedules and six CLI app cells. Fresh D17/D21/D22 companions are required; other defect records may retain historical-measured/current-not-run status with reason. Actual Node/Python runtime imports may remain explicitly not-run; Rust facade smoke is separately labelled. No generic "all backends/surfaces passed" claim.

[Current-format contract](design/current-format-contract.md) is proposed, not already accepted. New/empty initialization is distinct from admission of existing input; refuse unsupported/ambiguous/corrupt input rather than silently stamp, decode/drop/re-hash or migrate. Exact-stream IDs/provenance remain exact; logical regeneration records fresh mappings. Fixture-loader refusal is implemented here; backend safety defects are measured and deferred, not fixed. No trusted import/sync/recovery claim while applicable defects remain.

[Archify proposal](diagrams/foundation.html) illustrates oracle → validated loader → actual scratch backends → classified evidence → separate later certification. Automated artifact/browser checks passed; no perceptual review claimed. Historical diagrams remain unchanged.

### Explicit acceptance requested

The operator in the master must explicitly accept or amend the following proposed decisions, separately from merely authorizing a study:

| Decision | Proposed choice | If not accepted |
| :-- | :-- | :-- |
| P1 | Accept protected-input/admission boundary in design/current-format-contract.md, including strict fixture unknown-field refusal and no automatic mutation of unrecognized existing inputs. Backend gaps remain defects. | Policy publication and loader implementation stay gated; inventory may proceed. |
| P2 | Accept reload/identity/oracle-regeneration boundary: exact captured streams preserve identity/provenance; logical regeneration has explicit mappings; no silent oracle rebasing, migration or general-convergence claim. | Same gate; do not invent a translation policy. |
| P3 | Accept the finite corpus profile and two-dimensional result/exit contract in design/corpus-contract.md: bootstrap may succeed with explicitly reproduced defects; certification requires every selected required cell to pass. | Same gate; no count-based substitute for consent. |

Record the operator's actual master-session answer and reviewed content digests in `references/policy-acceptance.json` only after it arrives. The file is not created during drafting and a green file-existence check is not authorization. The earliest decidable human gate is execute start; no result-dependent policy choice is presumed accepted. Newly discovered conflicts or architectural choices return to the master. Approval to investigate unknown results never accepts those results.

### Explicit exclusions

No repairs to #14–#22, stable-edge implementation #28, new app-state/deletion implementation #39, new BPMN/process/ontology model, full restore/purge, cancellation/cascade choice, production preview-security scheme, migrations, actual beads import/cutover, native-binding feature expansion, release/publication, global install or authoring-tool development. D4/D5 and PR1-1j remain unresolved/bounded as recorded. Original plan-007/008/009 evidence and deliberately retained historical fixtures remain unchanged. No probes use real .beads or operator stores. Python only via uv; all scratch roots are owned and cleaned by the runner.

## Epics

### Epic 1: Freeze the bounded contract and source inventory

- Issue 1.1: Inventory current format and oracle authority without changing production behavior
  Produce `docs/regression/format-inventory.md` and `tests/regression/source-index.json`: actual SQLite metadata/schema recognition, Git WAL/snapshot recognition, Iota identity, AppSpec/binding/envelope shapes and entry points. Pin current source paths/commits/hashes and frozen plan-007/008/009 manifests; record every #14–#22 owner, injected-input provenance and current versus historical status. No active-store search or database opening. Inventory disagreements are evidence for a question, not authority to choose new semantics.
- Issue 1.2: Publish the explicitly accepted bounded current-format contract
  - depends-on: 1.1
  - resolves-upstream: #27 (partial)
  After the human policy gate, publish `docs/regression/current-format-contract.md` from the accepted proposal with its exact acceptance receipt and actual inventory references. State desired safety separately from known implementation gaps, and name the later owners of safe-open/admission/recovery work. No new production format version, migration or fallback implementation. Acceptance changes require re-review rather than silent edits to the proposal.

### Epic 2: Implement strict logical fixture infrastructure

- Issue 2.1: Add non-published regression crate and strict fixture/result schemas
  - depends-on: 1.2
  Add `crates/pim-regression/Cargo.toml`, workspace registration and `src/{fixture,loader,oracle,runner,result}.rs` plus `src/bin/pim-regression.rs`. Add `tests/manifest_contract.rs`. Decode/validate the complete fixture and oracle envelope before any store side effect; reject unknown/duplicate/malformed inputs and unsafe paths. Use owned temporary roots, explicit namespaces/AppSpec/actor/order, two identity modes and required-cell enumeration. Initial oracle helpers inspect actual projections only; no competing algorithm. Negative parser/path controls must prove zero target mutation.
- Issue 2.2: Author the finite logical corpus and stable semantic oracle mappings
  - depends-on: 2.1
  Add `tests/regression/manifest.json`, `fixtures/`, `oracles/` and coverage/source links implementing the 21-family floor in design/corpus-contract.md. Capture accepted authority separately from shipped calibration and historical measurement. Preserve original evidence byte-for-byte; translate consumer intent explicitly. Pin fixture/oracle/spec digests and declared normalization, with exact identity assertions untouched. A8/A9 remain accepted-unimplemented; generic permissiveness and X2 refusal cannot be counted as support for missing policies.

### Epic 3: Exercise real backends and classify evidence honestly

- Issue 3.1: Implement disposable SQLite/Git reload, replay and schedule adapters
  - depends-on: 2.2
  Implement actual Store/Journal/pim-app loading and read observations, all-handles-dropped reopen, reconstruction, exact copied-iota replay, Git snapshot-plus-tail versus full-WAL and the four finite sync schedules. Add `crates/pim-regression/tests/backend_matrix.rs`. No skipped mandatory cell, shadow readiness/deletion engine, accidental ambient store target or SQLite-sync claim. Adapter errors are setup errors, not semantic failures. Compare namespace/object/edge/reference identities, multiplicity, readiness and lineage at every applicable stage. For I1 on both backends verify effective app/spec binding after reopen and a known AppSpec-invalid mutation remains rejected without journal/projection changes; keep unbound N1 distinct. Separate valid exact-stream replay from malformed negative injection. Keep CLI distinct for Issue 4.1.
- Issue 3.2: Implement defect companions, result classifier and fail-closed certification
  - depends-on: 3.1
  Add isolated fresh D17/D21/D22 raw-input companions, preserve all nine issue records and produce complete per-cell JSON with command/evidence provenance. Implement `bootstrap` and `certify --profile` behavior specified in the corpus contract, with separate execution and semantic statuses. Add `crates/pim-regression/tests/report_contract.rs`: invert each named negative control, reject omitted/duplicate/stale results, empty selection and defect-as-pass; prove an always-failing certifier cannot pass with one synthetic valid positive control. Synthetic records never certify real capabilities. Unexpected defect pass is a review-triggering mismatch, not closure. Do not repair production code while adding a probe.

### Epic 4: Surface coverage, repeatability and bounded handoff

- Issue 4.1: Exercise real CLI and existing facade surfaces with explicit coverage gaps
  - depends-on: 3.2
  Add `crates/pim-regression/tests/surface_smoke.rs` and `scripts/check-h0.sh` modes `surfaces` and `all`. Build the actual pim executable and pass its explicit binary path; I1/G1/P1 run on each backend with fresh processes, explicit scratch URIs and JSON semantic assertions after reopen. Run existing Rust pim-node facade tests with their correct SQLite/Git scope. Inventory actual Node/Python runtime coverage as separate cells; absence may remain not-run under this profile, not a native parity claim. No global installs or binding feature implementation. The shell runner must reject unknown modes, missing binaries and zero-test selections, propagate failures, and clean owned scratch on both success and failure.
- Issue 4.2: Produce verified bootstrap evidence, coverage index and overview impact
  - depends-on: 4.1
  - resolves-upstream: #36 (partial)
  Run `scripts/check-h0.sh all` twice from fresh scratch stores, compare stable observations/digests while keeping separate run receipts and generated-ID mappings, and run the four exact retained-suite selectors listed in the corpus contract (backend journal/sync, CLI app/convenience, pim-node facade targets, and core/app/formula suites). Commit primary-side `evidence/bootstrap-report.json`, `evidence/validation.md`, `evidence/frozen-preservation.json`, `evidence/overview-impact.md` and `docs/regression/coverage.md` with all five status counts, required denominators, exact supported schedules/surfaces and per-capability blocking owners. Preserve original frozen evidence hashes and protected-data boundaries. Assess docs/overview: narrowly update implemented/accepted/proposed explanation if warranted, otherwise record no-change rationale; do not silently re-pin sources. Reconcile #36/#27 only as partial scoped progress through yf-beads-upstream after authorized landing; neither whole issue nor #14–#22 closes here. Report capability gaps and proposed next safe-open lane, not an execution authorization for it.

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator
- Instructions: Only the master-session operator may approve this plan. Execution needs a fresh approved fingerprint and a separate fresh executor session; this planner stops at ready-for-approval.

### Capability Gate: Explicit bounded policy and profile acceptance
- Type: human
- Approvers: operator
- Condition: Operator explicitly accepted P1, P2 and P3 against the reviewed proposal digests; master-routed receipt is present and verified by the executor. Study approval alone is insufficient.
- Test: test -s docs/plans/plan-012-james-dixson-d1af33/references/policy-acceptance.json
- test_class: consent
- cwd: repo-root
- Blocks: 1.2, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2
- Instructions: Frontload at execute start because all proposals are already available. Read the actual master answer and verify the receipt's decision set and content digests; never auto-resolve from file existence. If withheld, only 1.1 may proceed; route concrete amendments to the planner/master. The planner does not create its own acceptance.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Approvers: operator
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | Expected defect appears as correctness pass | high | Separate execution/semantic outcomes, five totals and required-cell denominator; negative classifier controls; no automatic promotion on unexpected pass. |
| R2 | Loader recreates a second lifecycle engine | high | Reuse real APIs; assert observations against source-linked static oracles; accepted-unimplemented cells stay non-passing. |
| R3 | Scratch test reaches real beads or operator store | high | Own temp roots only, no store-destination argument, explicit CLI URIs, scrub ambient selection, path/symlink controls and fail-path cleanup. |
| R4 | Oracle regeneration erases counterexamples or identity | high | Immutable source hashes, separate encoding/oracle digests and exact-stream mode; old/new review for any oracle change. |
| R5 | Large matrix turns into universal repair or certification | med | Fixed 21-family floor, explicit mandatory/optional cells and selected D17/D21/D22 companions; other failures retain owners, no production fixes. |
| R6 | Harness test setup errors masquerade as negative-control success | high | Exact expected exit/outcome matching, setup-error separation, positive certifier control and mandatory run coverage. |
| R7 | Human policy approval inferred from plan approval or green gate test | high | Explicit P1–P3 consent receipt plus human gate; unknown results require fresh acceptance. |
| R8 | Backend or binding coverage is overstated | med | Distinct live/reopen/rebuild/snapshot/sync/surface cells; rust-facade is not native runtime; no convergence claim beyond named schedules. |

## Success Criteria

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | Exact P1–P3 authority is recorded and published policy matches acceptance; inventory does not invent migrations or active stores | manual: master/operator verifies references/policy-acceptance.json against actual routed answer and reviewed digests, then docs/regression/current-format-contract.md and format-inventory.md; consent cannot be proven by a test | 1.1, 1.2 |
| SC2 | Strict loader, source/authority maps and finite manifest admit valid fixtures and reject invalid/escaping ones before store side effects | `test -f crates/pim-regression/tests/manifest_contract.rs && cargo test --locked -p pim-regression --test manifest_contract` → exit 0 | 2.1, 2.2 |
| SC3 | Mandatory real SQLite/Git stage cells, exact identity replay and named schedules execute and compare actual observations | `test -f crates/pim-regression/tests/backend_matrix.rs && cargo test --locked -p pim-regression --test backend_matrix` → exit 0 | 3.1 |
| SC4 | Fresh D17/D21/D22 evidence and all owned gaps remain explicit; report/certifier detects false greens and missing/stale/duplicate evidence | `test -f crates/pim-regression/tests/report_contract.rs && cargo test --locked -p pim-regression --test report_contract` → exit 0 | 3.2 |
| SC5 | Six real CLI app/backend cells and scoped existing facade tests run; native runtime gaps stay separate | `test -f scripts/check-h0.sh && bash scripts/check-h0.sh surfaces` → exit 0 | 4.1 |
| SC6 | Repeatable full bootstrap validates the required profile without claiming all semantic cells pass | `test -f scripts/check-h0.sh && bash scripts/check-h0.sh all` → exit 0 | 4.2 |
| SC7 | Frozen plan-007/008/009 evidence and deliberately retained fixtures remain unchanged; current coverage and overview impact are honest | manual: review evidence/frozen-preservation.json against baseline hashes and evidence/validation.md command receipts; compare two bootstrap runs, coverage.md and evidence/overview-impact.md, including any explicitly reviewed overview pin changes | 4.2 |
