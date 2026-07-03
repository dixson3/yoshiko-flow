# Review Pass 1 — plan-021-james-dixson-bb3558

**Conformance:** INCOMPLETE → resolved. The draft left duplicate template stub sections
(`## Epics/Gates/Risks/Success Criteria` = "_To be determined._") after the real content; deleted.
"Resolved By" column filled. Re-run expected PASS.

**Red-team verdict:** REVISE → all concerns resolved in-place; ready to re-present for approval.

## Strengths
- SPEC-first enforced by the DAG, not just asserted (every code issue edges to its SPEC issue).
- Root cause confirmed to one line + one prose site; Epic 2 pins **both** ambient deps (base + merge target).
- Guard-collapse well-scoped; reconcile gate/step relocation correctly accounted for inside the moved §4.2–4.6 range.
- Cross-clone fingerprint works by construction (content-embedded field, committed before any push).

## Concerns & Operator Resolutions
| ID | Severity | Concern | Resolution | Status |
|:---|:---------|:--------|:-----------|:-------|
| RT-C1 | high | Self-hosting ordering hazard named but not operationalized — a mid-execution skill edit changes the running protocol | Added **Epic 0**: plan-021 runs in-place (worktree off), pinned pre-edit skill snapshot, no resume across a landing boundary; wired as a Start-Gate instruction. Strengthened the risk entry | resolved |
| RT-C2 | high | Fingerprint self-trigger via `## Upstream Issues` "Resolved By" cells, filled at the relocated pour | Excluded `## Upstream Issues` from the hashed span in Issue 5.1 + REQ-PORT-04x (1.4); added test in 6.2 | resolved |
| RT-C3 | medium | Fingerprint-write vs auto-commit ordering unsequenced — a plan could commit/push without a fingerprint | Added `depends-on: 5.1` to Issue 4.2; added the explicit "write Fingerprint at APPROVE" step to the Approach flow | resolved |
| RT-C4 | medium | Default-branch guard robustness (main vs master, detached HEAD) unspecified | Issue 4.1 specifies resolution: `symbolic-ref origin/HEAD` → `init.defaultBranch` → `main`/`master`; detached/empty = fail-closed refuse; testable REQ in 1.3; test in 6.2 | resolved |
| RT-C5 | medium | `README.md` (§Execute/§Reconcile) hardcodes the old model, omitted from docs epic | Added README.md to Issue 6.3 surface list | resolved |
| RT-C6 | low | Capability smoke gates only Epic 6 — Epics 3–5 land unvalidated | Tightened `Blocks:` to also cover Epic 3 close; noted per-epic `test_worktree.py` (6.1) as the interim guard | resolved |
| RT-M1 | note | Teardown branch-resolution under the named-branch scheme unspecified per strategy | Added acceptance to Issue 2.3: feature-branch strategy preserves feature `<plan-id>`, deletes only `<plan-id>-execute` | resolved |
| CONF-1 | — | Duplicate trailing stub sections (also a fingerprint-boundary ambiguity with two `## Success Criteria`) | Deleted | resolved |
| CONF-2 | — | "Resolved By" column = "Epics TBD" | Filled with resolving epics | resolved |

## Missing sections
None — all required portability sections present (single copy each after stub removal).

## Gate Assessment
Start Gate (human/operator) correct. Capability Gate (scratch-repo dogfood) is the right mitigation
for the self-hosting hazard; `Blocks:` tightened to Epic 3 + reconcile (RT-C6). Reconcile Gate (auto)
standard; note it now pours at execute (relocated with §4.6 under Epic 3.1). Epic 0 adds the binding
self-hosting execution constraint.

## Upstream Assessment
#47/#63/#64 = include, coarse single-tracker each (matches AGENTS.md). #62 = defer (operator decision,
stays open). SPEC-first carve-out (GR-PLAN-003) correctly sequenced ahead of Epic 4. "Resolved By"
column now names resolving epics.

**Final status:** all concerns resolved; frozen.
