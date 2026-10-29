---
type: Plan
okf_spec: OKF-PLAN
description: Receipt-bound native gate-wrapper compatibility with fail-closed fidelity
  and an unapproved self-hosting bootstrap proposal.
id: plan-074-james-dixson-4b8fe0
author: james-dixson
created: '2026-10-29'
status: review
---
# Plan: Gate-wrapper compatibility for start resolution and pour fidelity

**ID:** plan-074-james-dixson-4b8fe0
**Author:** james-dixson
**Created:** 2026-10-29
**Status:** review

## Objective
Repair yf-plan's start resolution and pour fidelity for genuine native task- and gate-typed Begin wrappers, without hiding real gates, changing executed graphs or inferring consent. Establish a bounded, explicitly gated self-hosting proposal; this planning session stops at ready-for-approval, not execution.

## Motivation
PIM H0 plan-012 remains held after code and packaging verification. Its unchanged graph matches eight issues, seven issue-dependency edges and four epics, but installed fidelity counts four gates against three declarations because bd 1.3.1 types the Begin wrapper as a gate. Supported manual start remediation did not waive fidelity. Other repositories report the same seam in #417. A title-only subtraction would turn a compatibility fix into a false-green gate bypass.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #417 | Start resolver cannot find native gate-typed Begin wrapper | include | Reuse existing defect for resolver and fidelity; local mirror yf-05k1. Original body preserved with bounded planning note. | 3.3 |
| #445 | Standing fidelity override request | exclude | Evidence only; no waiver or consent adopted. | — |
| #414 | Fidelity after cascade ordering | exclude | Related ordering facts only; general landing overhaul excluded. | — |

No matching open plan was found. Plans 047/050/053 are historical predecessors; open 069/072/073 have different scopes. This bundle is not a second execution of those plans.

## Investigation Findings
[EXP-001](findings/exp-001-native-roles.md) measured genuine native bd 1.1.0 TASK and 1.3.1 GATE wrappers using the identical installed formula. Both have no await semantics and block a distinct sibling human gate. Native list/show edge shapes differ, and persisted graphs lack formula/role provenance. Critically, `bd gate resolve` on the gate-typed wrapper can close it while the actual human gate stays open. A closed wrapper is not consent.

[EXP-002](findings/exp-002-self-hosting.md) establishes the installed bootstrap cycle: validated implementation push L6 precedes fidelity L14; deployment is L19. Ending the executor alone cannot authorize reordering. AST-stub measurement found a failed resumed close chain can overwrite L_RECONCILED with L_LOCKED. That is not a live/rehearsed landing, nor authority for a landing-engine rewrite.

[EXP-003](findings/exp-003-held-h0-reproduction.md) retains a portable 18-node H0 snapshot, exact historical plan/mapping and reproduced exit-1 verdict. Source main was clean and synchronized at `8c97581e85fd48ebdfac45866b03fd213b9a783a`. Installed yf reports `0.5.0 (5677780-dirty)`; relevant source/installed scripts match bytewise and read-only skill status separately matches the embedded hash. Beads/plan preflights pass. No actual graph was altered or used as a test store.

## Approach

### Compatible semantics, not title filtering
Adopt the proposed [compatibility contract](references/compatibility-contract.md): one shared pure role classifier, normalized complete graph input, explicit plan/root/fingerprint binding and retained native pour/create evidence. Accept genuine wrapper types task or gate only after exact role validation; count the actual human gate once and retain every other real gate. Strengthen count-only gate comparison to a one-to-one declared-role identity comparison so equal-count substitutions cannot hide missing/extra gates.

A versioned `references/execution-roles.json` binds the three native role keys and all declared gate identities. Record native start evidence immediately after root linkage; finalize after capability/reconcile creation and before resolution. No title, ID prefix or generic Gate fallback establishes identity. Missing/ambiguous provenance is INCONCLUSIVE, including old plans without sufficient evidence; document that stricter safety boundary explicitly rather than claiming automatic historical migration. Receipt hashes prove bytes, not authorship or human authorization.

PIM's existing mapping is historical executor evidence, not raw native output. The separate `legacy-attested` path requires explicit operator acceptance of its binding, a fresh fingerprint/root check and unchanged frozen inputs. No PIM writes occur during this plan's development/testing. A future NEW live supplemental receipt needs separate authorization and cannot alter existing consent records, graph, code or frozen evidence. Read-only external-receipt validation alone is not normal landing eligibility.

Resolver mutation targets only the validated real human gate, verifies its state, then ordinary-closes the wrapper and re-reads both. Never gate-resolve the wrapper or force-close. Unresolved human capability consent stays unresolved. Definite inconsistency fails; incomplete input is nonzero inconclusive; no exit-0 fallback advances execution with `passed=false`.

The [Archify role-boundary proposal](diagrams/roles.html) separates identity checking, fidelity and human authority. Automated artifact/browser checks passed; no perceptual review is claimed.

### Self-hosting decisions are explicit and UNAPPROVED
[Bootstrap proposal](references/bootstrap-proposal.md) requests B0, an explicit old-tool intake bridge for this repair with durable native pour/create capture, supported actual-human-gate start remediation and post-deployment conversion by the newly installed recorder; B1, a one-plan promotion-timing exception after fully validated implementation push and executor termination but before old-checker completion; and B2, a separately authorized new historical role receipt for PIM. Master permitted drafting only. None is accepted, and none is implied by ordinary plan approval. B0 retains raw inputs, not a fabricated preseeded receipt; missing native evidence stops for a separate decision and cannot borrow PIM-specific B2.

The operator must separately accept the exact proposal with reviewed content hashes before any live action. Disposable mechanical rehearsal is mandatory before a landing handoff is described as executable. It covers real native graph behavior, actual old/new manager paths, L14 halt/replay, bookkeeping HEAD changes, full actual changed-set detection, exact clean synchronized FULL-validated deployment tree, destination manifests/hashes and repeated-failure stop behavior. A green AST stub is not that proof. If no safe route is established, execution-readiness remains unresolved. Landing-engine code changes require a fresh scope decision.

No source-checker substitution, permission/config broadening, silent journal editing, unreviewed decision reuse or fidelity waiver. Fresh completion loads the newly installed skill, re-previews/validates actual facts, and gives apply back to the operator's plain terminal. Any replay failure stops rather than blindly retrying. PIM remains held until master independently verifies installed checks and explicitly resumes it.

### Delivery boundaries and exclusions
SPEC requirements and amendment log precede implementation. Repo source, rebuilt embedded binary, installed skill and fresh invocation each have separate evidence. Tier-1 tests import modified source; Tier-2 installs only into owned sandbox HOME and mechanically drives verbs. Reviewers/investigators are read-only; only the main planner writes this bundle. Shared retry fallback stays 3; PIM's 10 is project-local.

Excluded: PIM implementation changes, graph retyping/re-pour, production stores, frozen evidence edits, global retries, general role-isolation tooling, audit-warning cleanup, plan-number allocator repair, general landing recovery/order overhaul, unrelated issues and live deployment now. Record relevant follow-up candidates without filing them in this blocker. New diagram artifacts use Archify; historical diagrams remain untouched.

## Epics

### Epic 0: Ratify the bounded compatibility contract before code
- Issue 0.1: Amend requirements and living log for receipt-bound native roles and fail-closed resolution
  Amend `skills/yf-plan/spec/phases.md` REQ-PLAN-077 for both native wrapper types and actual-gate-only mutation; amend `skills/yf-plan/spec/data.md` REQ-DATA-026 to preserve existing issue/edge checks and add explicit gate identity semantics. Allocate REQ-DATA-077 for the versioned role receipt, provenance limits, complete/incomplete states and historical attestation policy; allocate REQ-PLAN-087 for normalized role classification and refusal behavior. Update `skills/yf-plan/spec/cli.md` and CLI requirement/test inventories for `record-execution-roles` and diagnostic receipt arguments, including resolver nonzero INCONCLUSIVE. Add the plan-074 entry in `SPEC.md` before implementation. Use references/compatibility-contract.md as the reviewed proposal, not as already effective SPEC. No global landing-order requirement is changed by this issue.

### Epic 1: Implement and verify the shared identity boundary
- Issue 1.1: Add pure role classification and native positive/adversarial tests
  - depends-on: 0.1
  Implement `_shared/gate_roles.py` and `_shared/test_gate_roles.py`. Normalize native list/show representations, enforce exact distinct role IDs/root/fingerprint/evidence binding, parent/blocks/await predicates, competing roles and complete-input checks. Accept genuine 1.1.0 task and 1.3.1 gate forms. Retain raw fixtures from this bundle in supported test fixture locations with byte/hash manifests, label all derived mutations synthetic. Cover every adversary in the compatibility contract, including copied topology without provenance and closed wrapper/open real human gate. No graph-writing or consent authority exists in this module.
- Issue 1.2: Retain native execution role receipts and explicit historical imports
  - depends-on: 1.1
  Add `record-execution-roles` to `skills/yf-plan/scripts/plan_manager.py` and `skills/yf-plan/scripts/test_execution_roles.py`. Persist exact pour/create evidence, start-only/finalized receipt states, plan/root/fresh fingerprint binding, idempotence and atomic validated writes with readback; conflicting writes refuse. Historical import requires explicit provenance acceptance and never fabricates native origin. Test immutable PIM copies with the supplied mapping, plus stale/foreign/conflicting/missing-acceptance cases and zero writes on refusal. Retain actual authority separately; no acceptance file is created by tests in a live bundle.

### Epic 2: Integrate start resolution and fidelity without bypasses
- Issue 2.1: Use proven roles for actual-gate resolution and postcondition checks
  - depends-on: 1.2
  Replace `_find_start_gate_pair` title/type and generic Gate fallback with complete gate-inclusive acquisition and shared classification. Update `resolve-start-gate` to preserve existing fresh-session approval checks/caller boundaries, target only the actual human gate, re-read it before ordinary wrapper close, and re-read both before pass. Add `skills/yf-plan/scripts/test_gate_wrapper_resolver.py`: genuine task/gate positives, idempotent success, wrong-target prevention, preclosed wrapper/open human gate, CLI errors, partial mutation recovery and zero mutations under bad identity/absent authority. Never force-close or rewrite gate types. Update installed-surface SKILL prose source and affected CLI callers to handle nonzero inconclusive without advancing status.
- Issue 2.2: Compare exact real-gate identities while retaining graph safety and installed packaging
  - depends-on: 2.1
  Integrate classifier into `_shared/pour_fidelity.py`; keep all issue/epic/duplicate and dependency checks, validate declared gate/entry/reconcile relations, and remove only the one proven wrapper from gate counts. Require finalized role receipts for completion; add read-only `--roles PATH` for explicit diagnostic evidence without hidden environment overrides. Extend `_shared/test_pour_fidelity.py` and add `_shared/test_gate_wrapper_fidelity.py` for all positive/negative boundaries, count-preserving gate substitution, incomplete snapshots, actual H0 archived red-to-green and unchanged 8/7/4 denominators. Preserve exit 0/1/2 and landing halt on both nonzero classes. Wire `_shared/sync.py`, vendored files, imports, embed/manifest and relevant SKILL/beads-authoring documentation so source, embedded and installed forms agree; test them, do not deploy them live.

### Epic 3: Prove integration and produce a conditional operator handoff
- Issue 3.1: Mechanically exercise native wrapper lifecycle under sandbox HOME
  - depends-on: 2.2
  Add `skills/yf-plan/test-harness/gate-wrapper.sh`: isolated HOME/git/bd stores, explicit tool provenance, unmodified native formula, real current bd gate-wrapper pour and authentic historical task fixture/native tool control. Drive record/resolver/fidelity verbs against the modified sandbox-installed skill. Prove exact expected IDs, gates, edges, authority/refusals, zero forbidden writes, missing/tool-error controls and cleanup. Run existing Tier-1, shared sync and required Tier-2 smoke as applicable; no interactive-agent smoke substitutes. Unknown modes, zero selected tests and missing tools fail distinctly.
- Issue 3.2: Rehearse the proposed self-hosting boundary and stop on unsafe recovery
  - depends-on: 3.1
  Implement sandbox-only `skills/yf-plan/test-harness/gate-wrapper-bootstrap.sh` and emit `evidence/bootstrap-rehearsal.json`. Exercise every requirement in references/bootstrap-proposal.md with the actual manager paths and clearly labelled external-action intercepts. Begin with OLD installed intake and no preseeded new-format receipt; exercise B0 durable capture and supported actual-gate-only fallback, then convert those same captures with the newly sandbox-installed recorder after deployment and before fresh completion. Prove full actual changed-set inventory despite bookkeeping-only HEAD, exact final clean/synced/FULL-validated tree, pre/post binary/embedded/installed hashes and enumerated deployment surfaces without permission/config broadening. Reproduce repeated-failure journal regression as a refusal control and demonstrate no automatic replay or lost evidence. If safe recovery needs landing-engine code changes or an unsupported manual journal edit, STOP and escalate scope; no live exception is adopted merely because a simulation passed.
- Issue 3.3: Validate scoped deliverables and prepare the operator-owned landing and held-H0 handoff
  - depends-on: 3.2
  - resolves-upstream: #417 (include)
  Run the full compatibility matrix and repository validation against the actual changed tree; write `evidence/compatibility-acceptance.json`, `evidence/deployment-manifest.json` and `evidence/landing-handoff.md` with source/version/digest pins, test denominators, known limits, full changeset, bootstrap decision status and exact required later pre/post checks. Do not call missing deployment or PIM checks passed. Prepare fresh dry-run/independent lander/validated decision and stop for operator terminal apply only when rehearsal and separate authority permit. Reconcile #417 through yf-beads-upstream only after authorized verified delivery, not on a source-only green. No live deployment is an execution-bead prerequisite that would deadlock landing; actual installation/completion/PIM checks are explicitly later operator-owned obligations, not claimed by this bead.

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator
- Instructions: Operator in master approves the exact reviewed plan and fresh fingerprint. Execution uses a fresh cpa/claude-opus-5-5 session; planner stops before intake/execute. Plan approval alone does not accept B1 or B2.

### Capability Gate: Explicit compatibility policy and bootstrap decisions
- Type: human
- Approvers: operator
- Condition: Operator separately accepted the strict role-evidence policy, B0 old-tool intake bridge and proposed B1 promotion exception against reviewed hashes; B2 remains separately required before any live PIM receipt is added. Master drafting permission is not consent.
- Test: test -s docs/plans/plan-074-james-dixson-4b8fe0/references/operator-decisions.json
- test_class: consent
- cwd: repo-root
- Blocks: 0.1, 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 3.3
- Instructions: Frontload at execute start. Read the actual operator answer, verify decision identities, proposal hashes and scope; file existence never resolves this gate. If withheld or ambiguous, remain held and route questions through planner to master. A rehearsal failure prevents live bootstrap even with prior conditional acceptance.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Approvers: operator
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | A real Begin-titled gate is hidden | high | Receipt-bound exact roles, unique IDs, complete graph and lookalike/substitution negatives. |
| R2 | Wrapper closure is mistaken for human consent | high | Actual human gate alone resolves; re-read state; wrong-target native negative and unresolved capability-gate controls. |
| R3 | New evidence policy makes old plans silently pass or silently disappear | high | Explicit historical acceptance, documented INCONCLUSIVE boundary, genuine task native positive, no graph retrofit. |
| R4 | Repair cannot deploy itself under installed fidelity | high | UNAPPROVED B1, full disposable interrupted-lifecycle rehearsal, clean/synced exact-tree FULL validation and fresh operator decision. |
| R5 | Failed replay regresses journal and repeats outward writes | high | Snapshot phase boundaries; measured negative; stop rather than retry; separate scope decision if engine repair necessary. |
| R6 | Source-only tests miss embedded/installed drift | high | Modified sandbox install, manifest/digest comparison, live promotion only later from synchronized main. |
| R7 | Evidence touches PIM stores or rewrites history | high | Immutable bundle fixtures and disposable stores; any new live receipt separately authorized; no existing PIM writes. |
| R8 | Broader graph/landing repair escapes scope | med | Only role/gate identity and relevant edges; explicit excluded follow-ups; escalate newly required engine changes. |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | SPEC/amendment contract precedes code and tagged requirements cover this seam | manual: inspect SPEC.md plan-074 amendment, spec/phases.md, spec/data.md and spec/cli.md commit ordering plus requirement-coverage receipts; no claim of implementation from prose | 0.1 |
| SC2 | Genuine native forms classify; fabricated or incomplete identity cannot pass | `test -f _shared/test_gate_roles.py && uv run _shared/test_gate_roles.py` → exit 0 | 1.1 |
| SC3 | Native/historical role receipts are bound, validated, idempotent and refusal-safe | `test -f skills/yf-plan/scripts/test_execution_roles.py && uv run skills/yf-plan/scripts/test_execution_roles.py` → exit 0 | 1.2 |
| SC4 | Resolver never uses wrapper closure as consent and verifies actual writes | `test -f skills/yf-plan/scripts/test_gate_wrapper_resolver.py && uv run skills/yf-plan/scripts/test_gate_wrapper_resolver.py` → exit 0 | 2.1 |
| SC5 | H0 archived 3/4 mismatch is repaired without weakening real gate/edge/identity detection | `test -f _shared/test_gate_wrapper_fidelity.py && uv run _shared/test_gate_wrapper_fidelity.py` → exit 0 | 2.2 |
| SC6 | Modified sandbox-installed skill passes real native lifecycle and refusal controls | `test -f skills/yf-plan/test-harness/gate-wrapper.sh && bash skills/yf-plan/test-harness/gate-wrapper.sh gate` → exit 0 | 3.1 |
| SC7 | Conditional bootstrap is mechanically rehearsed, or explicitly blocks landing rather than fabricating recovery | `test -f skills/yf-plan/test-harness/gate-wrapper-bootstrap.sh && bash skills/yf-plan/test-harness/gate-wrapper-bootstrap.sh gate` → exit 0 | 3.2 |
| SC8 | Scope, test coverage, artifacts and later operator obligations are accurately handed off | manual: review evidence/compatibility-acceptance.json, evidence/deployment-manifest.json and evidence/landing-handoff.md with exact changed-set FULL validation receipts, hashes, unresolved decisions and no unauthorized live actions | 3.3 |
| SC9 | Actual deployment and held-H0 validation remain explicit later obligations, never evidence fabricated before they run | manual: operator reviews B1/B2, pre/post tool and surface hashes, fresh validated landing decision, actual installed fidelity success and unchanged PIM graph before separately resuming H0; lack of any required result leaves that boundary held | 3.3 |
