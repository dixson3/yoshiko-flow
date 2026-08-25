---
type: Retrospective
okf_spec: OKF-PLAN
---
# Plan retrospective

Stops and deviations recorded during execution, newest last. Each `## RE-NNN` section is
one entry; `RE-NNN` ids are append-only and are never reused or renumbered.

`detected_by` records WHO found the entry and `evidence` records the command and output
substantiating any state claim in it, or the literal `unverified`. Both exist because an
entry's trust level is a property of who found it, and the recorder is usually the subject:
a retrospective built from an actor's own account would faithfully transcribe a false claim
rather than detect one. A state assertion with no evidence is a narration, not a finding.

## RE-001

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-08-24 |
| `stop_class` | 4 |
| `asked` | review-loop-check reached the configured max_review_cycles bound of 5 with the last red-team verdict still REVISE. Raise the bound for one confirming pass, or override the verdict and approve? |
| `answered` | PENDING — brought to the operator; not resolved by the main session |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | plan_manager.py review-loop-check --json -> {escalates: true, cycles: 5, limit: 5, stop_class: 4} |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-24 |
| `stop_class` |  |
| `asked` | Issue 1.2 declared touches: _shared/doc_lint.py, _shared/document_types/plan.toml, skills/yf-plan/scripts/doc_lint.py. Shipping the verification-clause check broke two assertions in _shared/test_doc_lint.py, which the issue does not declare. |
| `answered` | Edited the undeclared file. Both assertions were fragile by implementation, not deep invariants: one scanned the whole JSON for the literal word INCONCLUSIVE (which document content quoted back into a finding trips), the other pinned the promote=false opt-out list to exactly one entry. Leaving them red would have blocked 7.1's FULL tier. |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | uv run _shared/test_doc_lint.py -> 2 failure(s) before the edit, 'all passed' after; git stash confirmed both failures were introduced by this change and not pre-existing |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-003

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-08-24 |
| `stop_class` | 2 |
| `asked` | Issue 5.1 requires a verify-artifact aspect that weaves over all four plan-review steps via [compose] aspects. Does bd 1.1.2 support aspect weaving? |
| `answered` | No. bd classifies the formula as type=aspect and parses [compose] aspects, but weaves nothing. Six schema shapes produce zero woven steps at both formula show and mol wisp. 5.1 and 5.2 are blocked; surfaced to the operator rather than severed unilaterally. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | bd formula list --type aspect -> classifies correctly; bd formula show plan-review --json -> steps=4 unchanged across 6 shapes; bd mol wisp plan-review --json -> created=6, id_mapping has only plan-review{,.conformance,.gate,.gate-gate,.red-team,.resolve} |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-004

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-24 |
| `stop_class` | 5 |
| `asked` | The Reconcile Gate's Test was amended in plan.md DURING execution. Editing plan content mid-execution is a deviation — was it justified, and what did it change? |
| `answered` | Justified: it was a TEST/CONDITION FIDELITY defect, not a Condition change. The Condition already read 'every non-gate execution bead UNDER THIS PLAN'S EPIC', and the 7 deferred-defect beads Issue 7.3 files are parent=- so the Condition already excluded them — but the Test keyed only on metadata.plan and never looked at parentage, so it counted them. Those 7 are OPEN BY DESIGN (they track upstream #211-#217, open upstream) and never close, so the gate could never open and reconcile was unreachable. Added '.metadata.plan_issue != null'. The 'out of tree' choice was right for cascade-close, which walks the epic tree, and did nothing for this Test. Declined the alternative of stripping metadata.plan from the 7 beads: that stamp is real provenance and deleting evidence to satisfy a check inverts what this plan is for. NOTE: the Gates section IS fingerprint-covered, so this edit makes the stored fingerprint stale. |
| `frontloadable` | yes |
| `detected_by` | operator |
| `evidence` | Test run verbatim against live bd: EXIT=1, counting yf-slor yf-fnxb yf-nsm9 yf-xqj8 yf-zrtx yf-ek9a yf-ku0x (all plan_issue=NONE, parent=-) plus yf-mol-f2q.8.6. Discriminator: of 43 beads stamped plan=plan-052, 31 carry metadata.plan_issue and 12 do not (reconcile step + 7 defect beads + 4 gates). With the guard added the Test exits 1 naming ONLY yf-mol-f2q.8.6 (7.5), which is correct, and will exit 0 once 7.5 closes. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

