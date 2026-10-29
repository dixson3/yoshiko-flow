---
type: Reference
okf_spec: OKF-PLAN
description: Approved intake binds exact operator answers; B1 remains conditional, B2 external-only, and only master may launch execution.
---
# Approved intake handoff

## Authority and content
The operator explicitly approved the plan and strict compatibility policy in master. Exact answers, reviewed commit and proposal hashes are durably recorded in `references/operator-decisions.json`; the original master receipt is retained byte-for-byte under `assets/fixtures/planning-validation/operator-approval-source.json`. Later receipt permissions supersede the historical UNAPPROVED labels in the reviewed proposal and planning-readiness documents without rewriting those reviewed bytes.

Approved, stored and current content fingerprint must all equal:

`8c5b67da2c5640331746e67a1ae718c4602867079ef75a89190f848d0aa9f85c`

Only header bookkeeping and the fingerprint-excluded upstream tracker table changed in plan.md after approval. The compatibility contract SHA-256 remains `a5eeaa2288750732903b24db4de3a8804cc1bf346b01c94f0c7a351f10b80ee5`; bootstrap proposal remains `8261d0a334493f0247b9d3a723544cc9eb1a32417422aeb28ab657d5a0dcc3c0`. The reviewed plan-file SHA-256 in the receipt names the pre-intake ready-state bytes, not the later approved header serialization. Current hashes are returned in the verified handoff.

## Exact decisions and remaining boundaries
- **Plan/policy:** “Approve plan and policy (Recommended)”.
- **B0:** “Accept B0 (Recommended)”. The future fresh executor uses the reviewed old-tool intake bridge and durable prospective captures. This planner does not pour or execute.
- **B1:** “Conditionally accept B1 (Recommended)”. Successful disposable rehearsal, exact clean/synchronized FULL-validated deployment tree, full actual changed set and specified later operator manifest/install and fresh-apply confirmations remain mandatory. Conditional acceptance is not present deployment/apply authority.
- **B2:** “Accept B2 evidence policy (Recommended)”. This accepts EXTERNAL legacy-attested evidence policy only. A live PIM receipt write and H0 resumption are explicitly NOT authorized.

No fidelity waiver, graph retyping, permission broadening, landing-engine scope expansion or source-checker substitution. Unsafe rehearsal or replay stops. Any newly necessary landing-engine work needs a separate scope decision. PIM H0 remains held.

## Tracking and lifecycle linkage
- Root defect remains [#417](https://github.com/dixson3/yoshiko-flow/issues/417), mirrored by `yf-05k1`; no duplicate defect was filed.
- Single coarse plan tracker: [#456](https://github.com/dixson3/yoshiko-flow/issues/456), mirrored by `yf-kfjd`. Its creation went through installed yf-beads-upstream preview/apply; exact posted body, OPEN state and external-ref were read back and verified.
- No execution epic exists. Installed `resume-scan` returned `epic_state=none`, `epic_id=null`, `stale_approved=false`. `stamp-tracker` correctly skipped because no epic has been poured. The intake mirror is not an execution root.
- The future executor must perform the normal pour-once/resume check, retain B0 evidence and stamp #456 on the actual root immediately when it exists. Do not fabricate an Epic field during intake.

## Publication and session handoff
Intake strategy is main. Approved plan bookkeeping was committed on the development branch, then fast-forwarded locally to primary main without implementation changes. The primary untracked mirror was first preserved in an owned temporary backup and verified byte-equal to the approved branch. No unrelated file or resource was discarded.

Validation/publication results and final main/origin commit are reported separately after the actual commands run; this document does not predict success. The planner stops after verified intake. **Only master launches a fresh `cpa/claude-opus-5-5` executor.** Questions route through the planner; reviewers inherit only their narrow read-only assignment and never master-push or outer-task authority.

No install, deployment, execution pour, start resolution, implementation, land apply or PIM resumption is performed by this intake.
