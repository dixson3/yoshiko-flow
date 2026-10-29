---
type: Reference
okf_spec: OKF-PLAN
description: Proposed receipt-bound gate roles distinguish native wrappers from real gates and reject ambiguous lookalikes without inferring consent.
---
# Proposed compatibility contract

This is a proposal for SPEC-first implementation, not shipped behavior or operator consent. EXP-001 establishes the native shapes; EXP-003 establishes the held historical input. Native graph fields alone cannot distinguish a deliberately copied lookalike.

## Role identity and provenance

Introduce a small shared pure module `_shared/gate_roles.py`, vendored into yf-plan by `_shared/sync.py`. Its inputs are an extracted plan, expected plan ID/fresh approved content fingerprint, recorded molecule root, complete normalized graph, and a versioned role receipt. Its output is `pass`, `fail` or `inconclusive`, identified wrapper/real-gate IDs, evidence source and diagnostics. It performs no writes, resolves no gates and grants no consent.

Proposed receipt location: `references/execution-roles.json` within a plan bundle. Schema version 1 carries plan ID, approved fingerprint, repo-relative bundle identity, root ID, formula SHA-256, bd version, evidence kind, evidence file SHA-256, the three native role keys (`plan-execute`, `plan-execute.start-gate`, `plan-execute.gate-start-gate`), and a one-to-one map of exact extracted gate declaration names to bead IDs. Start Gate maps to the actual human gate, never its wrapper. Duplicate declaration names or IDs are invalid. Gate declaration names exclude line numbers so formatting changes do not invent new identity.

The new manager `record-execution-roles` verb reads explicitly named capture inputs and validates before writing. At pour it saves a start-only receipt immediately after root linkage, retaining original native output; after capability/reconcile creation it finalizes the complete declaration map before execute-start resolution. Incomplete receipts cannot pass completion fidelity. Re-running with identical evidence is a no-op; conflicting evidence refuses without overwriting. Persist using atomic replace, report exactly which paths were written, read them back, and never update the graph to fit the receipt. Future native-create outputs are retained as the source of gate IDs. No IDs are guessed from titles, prefixes or array order.

The receipt is an auditable identity binding, NOT cryptographically authenticated native output. An agent able to forge the graph and all evidence is outside what this checker can prove. Evidence digests prove bytes, not authorship or operator consent. Bound plan/root/fingerprint, exact source captures and independent review are required; tests must not call a fabricated same-topology graph native evidence.

## Historical evidence, including PIM

Historical native task-wrapper snapshots with genuine pour mappings are supported, not excluded by version. Existing runs with no trustworthy receipt are INCONCLUSIVE, never silently promoted by matching a Begin title. This stricter compatibility boundary must be explicit in the amended SPEC and release documentation; it is not a claim that every old plan can be automatically migrated.

PIM's retained `execution-epic-mapping.json` is executor-authored historical evidence, not the original raw three-key native output. The importer may accept a separate `legacy-attested` receipt ONLY after the operator explicitly accepts the binding of its existing wrapper/actual-gate/capability/reconcile IDs to the reviewed plan fingerprint and unchanged root. Capture the evidence digest and exact human provenance decision separately from execution/start consent. Unknown fields, missing role evidence, stale fingerprint, wrong root, conflicting maps, or absent acceptance refuse. No formula-source fields are fabricated on historical nodes.

During this planning effort all such importing is confined to copies under owned scratch. A future PIM live supplemental receipt is a NEW file requiring separate master/operator authorization; no existing PIM consent record, graph, plan text or frozen evidence may be overwritten. Until authorized and verified, PIM live fidelity/landing remains held. A `--roles PATH` override on read-only comparator/diagnostic commands allows independent verification of a supplemental receipt without writing PIM. Normal landing uses only the default reviewed bundle receipt; do not introduce environment-based silent overrides or substitute a source checker.

## Normalized structural predicates

Accept node `issue_type` with a checked `type` alias only where unambiguous. Normalize list edges (`depends_on_id`, `type`) and show edges (`id`, `dependency_type`); reject conflicting aliases. Validate unique node IDs, explicit root membership, parent-field versus parent-child consistency, no containment cycles, and sufficient input closure. Never use default `bd children`, which omits gates. Live acquisition uses `bd list --all --include-gates --limit 0 --json`, checks process status and JSON/error envelopes, and verifies required IDs by explicit show where needed. A failed or incomplete read is INCONCLUSIVE, not an empty graph.

Require three distinct mapped IDs, root matching plan's recorded molecule and plan-dir binding, wrapper and actual gate direct siblings under that root, wrapper type task or gate with no await semantics, actual gate type gate with `await_type=human`, and exactly the native wrapper-to-actual-gate `blocks` edge. Parent-child, related or reverse edges do not substitute. Reject extra wrapper blocking dependencies, competing role claims or an unmapped competing wrapper pair. Titles/descriptions corroborate but never authorize exclusion. Structural roles do not change when statuses close.

Every declared gate maps to exactly one observed real gate; every observed gate other than the one proven wrapper must map to a declaration. Reject missing, extra, duplicated and count-preserving substituted gate identities. A task-typed mapped real gate is not silently dropped. Preserve issue IDs/counts, duplicate detection, epic counts and issue-to-issue dependency comparison. Also validate the start wrapper edge and entry-issue gating, and capability/reconcile blocking relations declared by the plan. Extra unrelated edge types stay distinct, not invented prerequisites. No existing nonzero completion result becomes success merely because a wrapper was found.

## Consent and resolver behavior

Role recognition is not gate authorization. The caller must establish fresh approval, correct plan/root and fresh-session execute authority using the existing lifecycle. `resolve-start-gate` targets ONLY the validated actual human gate. It re-reads gate state after resolving, then uses ordinary `bd close` on the wrapper, never `bd gate resolve` on the wrapper and never `--force`. Finally re-read both nodes and report actual state, not subprocess exit alone.

A preclosed wrapper with an open actual gate must not short-circuit as success. Without execute authorization, do not resolve either. With valid execute authorization, resolve the actual gate and verify it before reporting the pair discharged. Open human capability gates remain unresolved regardless of structural fidelity, and completion must continue to halt on them. Structural fidelity may pass a correctly poured open graph at diagnostic time; this is expressly not completion or consent success.

Partial failure preserves the exact state and reports recovery instructions keyed to explicit IDs. No fallback to a generic Gate-titled child. Ambiguous/incomplete resolver input yields a nonzero INCONCLUSIVE result without mutations; a definite inconsistent graph yields nonzero failure. Amend CLI expectations and callers together so exit 0 with `passed=false` cannot advance execution silently. Keep comparator exit 0/1/2 = pass/divergence/inconclusive and preserve installed landing's halt on both nonzero classes.

## Required proof matrix

Genuine positives: native 1.1.0 task wrapper and native 1.3.1 gate wrapper, list/show shapes, open and resolved states, saved exact mapping and complete plan/root binding. PIM immutable snapshot must progress from recorded 3-versus-4 red to three actual mapped gates under the approved historical-evidence policy, with 8 issues, 7 issue edges and 4 epics unchanged.

Synthetic adversaries, explicitly labelled: arbitrary Begin title; copied topology without receipt; altered receipt digest; foreign or stale plan/root/fingerprint; swapped or repeated IDs; conflicting parents; gate masquerading as task; await semantics on wrapper; wrong actual await type; missing, extra, reversed or containment-only wrapper dependency; multiple candidate pairs; missing/extra/duplicate/count-preserving substituted actual gates; dropped/invented issue and gate-blocking edges; unavailable CLI, error JSON, malformed/truncated input, unknown schema and partial receipt. Closed wrapper/open human gate is a mandatory false-consent control. Verify zero writes on every refusal and real successful writes on authorized positive resolver controls.

No new backend, universal graph ontology, retry-default change or general landing recovery engine belongs here.
