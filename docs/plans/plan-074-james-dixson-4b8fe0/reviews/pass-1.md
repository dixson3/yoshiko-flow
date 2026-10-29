---
type: Review
okf_spec: OKF-PLAN
description: REVISE — old-tool intake and receipt transition for the repair itself must be explicitly allocated.
---
# Plan Red-Team: plan-074-james-dixson-4b8fe0

## Verdict: REVISE
**Mode:** reading

## Strengths
- The proposed classifier distinguishes **role identity, structural fidelity and human consent**. It does not mistake wrapper closure, a receipt hash or a matching title for authorization.
- Both native wrapper forms have retained positive evidence. The required adversaries include copied topology without provenance, conflicting mappings, count-preserving gate substitution, incomplete acquisition and closed-wrapper/open-human-gate states.
- The repair preserves issue/epic/dependency checks while strengthening gate comparison beyond counts.
- Historical PIM evidence is honestly classified as executor-authored, not native pour output. Supplemental attestation and live PIM changes remain separately authorized.
- B1/B2 are explicitly **UNAPPROVED**. The proposal does not convert drafting permission, ordinary plan approval or an AST probe into deployment authority.
- SPEC-first ordering, sandbox-only integration, source/embedded/installed separation, and stop-on-unsafe-replay boundaries are clear.
- Reviewer scope is correct: independent reviewers return findings; the parent writes artifacts. I performed no repository writes, live beads operations, upstream writes or Herdr actions.

## Concerns

| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | measured: M1 `rg -n 'record-execution-roles' …/plan_manager.py` → exit 1; M2–M4 → exit 0, commands and observations below | **The self-hosting proposal specifies the deployment/completion transition but leaves this repair’s own old-tool intake and receipt transition unallocated.** The installed recorder does not exist; installed intake keeps pour output in a shell variable and pipes capability/reconcile creation through ID extraction. The proposed normal lifecycle requires receipt finalization before start resolution, while Issue 1.2 implements that recorder only after execution begins. Bootstrap step 1 begins with implementation; step 6 assumes the same role receipt already exists. Neither B1 nor B2 specifies how plan-074 gets safely from old-tool intake to that receipt. B2 is expressly PIM-specific. This is a missing bootstrap precondition, not a demand that future rehearsal already have run. | Add a **plan-074-specific intake bridge** to the bootstrap proposal before approval: specify durable raw pour/create capture under the old installed workflow; exact ownership, paths, binding and refusal checks; the supported actual-human-gate start procedure and wrapper postconditions; and when/how the newly installed recorder converts those retained inputs into the default finalized receipt before completion. Explicitly distinguish initial raw evidence from the not-yet-available new receipt. If retrospective attestation or another deviation is necessary, name its separate authority rather than borrowing B2. Extend Issue 3.2’s rehearsal to start with the old installed intake, without a preseeded new-format receipt, and carry it through fresh completion. |

## Measurements

Paths below abbreviate:
- `SD=$HOME/.agents/skills/yf-plan`
- `PD=docs/plans/plan-074-james-dixson-4b8fe0`

Commands were run with absolute paths expanded; subprocess exit statuses were explicitly recorded. Parent normalized only the displayed path aliases for portability, not command semantics or returned findings.

| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| M1 — installed recorder | `rg -n 'record-execution-roles' "$SD/scripts/plan_manager.py"` | 1 | No recorder command/reference in the installed manager. |
| M2 — installed intake | `rg -n 'RESULT=\|CAP_GATE=\|RECONCILE_GATE=\|resolve-start-gate' "$SD/SKILL.md"` | 0 | Located pour at 1007, capability creation at 1175, reconcile creation at 1225 and resolver at 1254. Direct reads show shell-variable pour retention and create-output ID extraction. |
| M3 — planned receipt ordering | `rg -n 'Record native start\|before resolution\|Require finalized\|Add `record-execution-roles`' "$PD/plan.md"` | 0 | Lines 45, 77 and 85 require early receipt finalization, allocate implementation to Issue 1.2 and require finalized receipts for completion. |
| M4 — proposed bootstrap authority/sequence | `rg -n '^[1-7]\. \|Proposed exception B1\|Proposed decision B2' "$PD/references/bootstrap-proposal.md"` | 0 | B1 covers promotion timing; B2 covers PIM attestation. Sequence starts with implementation and later assumes the repair’s receipt exists. |

Additionally, I executed only the installed `_find_start_gate_pair` AST body with in-memory lookups over the archived PIM snapshot. Even with gate-inclusive children, it returned **“no start-gate wrapper task”**. This was an isolated function probe, not manager execution, native-bd experimentation or a landing rehearsal.

The native positive/control findings were reviewed as retained evidence; I did **not** rerun their native pours. No implementation or future sandbox rehearsal is claimed to exist.

## Missing
- An explicit old-intake → retained evidence → new default receipt bridge for **plan-074 itself**, including its start-resolution boundary.
- A rehearsal requirement that rules out accidentally proving only a new-tool-created execution or a manually preseeded receipt.

Missing future implementation/test artifacts are expected and are not independently counted as concerns.

## Gate Assessment
The start and capability gates frontload actual operator decisions. B1 can be accepted conditionally before rehearsal without a dependency cycle: later rehearsal still determines whether live use is permissible. File existence is expressly insufficient consent.

B2 correctly remains separate from development authorization. C1 needs a similarly explicit treatment of this repair’s own intake; it must not silently acquire authority through either existing decision.

The reconcile gate and later operator-owned deployment/PIM obligations are distinguished from implementation-bead completion. Bootstrap feasibility remains conditional—not established by this reading review.

## Upstream Assessment
Reusing #417 is appropriately bounded. The triage now records its inclusion and Issue 3.3 linkage. Excluding #445’s standing override and #414’s broader landing changes avoids importing unrelated authority or scope.

No additional upstream issue is needed for C1: it is a planning correction within this blocker. Any landing-engine change discovered during rehearsal should remain a stop-and-rescope decision, not an implicit expansion of #417.

## Resolutions
| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | Added explicitly UNAPPROVED B0: durable old-tool raw capture, exact role/root/fingerprint checks, supported actual-human-gate fallback, no preseeded receipt, and newly installed recorder conversion before fresh completion. Issue 3.2 rehearses that full bridge. Content evidence: `rg -n 'B0\|OLD installed intake\|NO preseeded\|newly installed recorder' docs/plans/plan-074-james-dixson-4b8fe0/references/bootstrap-proposal.md docs/plans/plan-074-james-dixson-4b8fe0/plan.md` → exit 0; gate_consistency → exit 0. This resolves missing planning allocation, not live feasibility or consent. | main-session | resolved |
