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
| `kind` | deviation |
| `when` | 2026-08-29 |
| `stop_class` |  |
| `asked` |  |
| `answered` |  |
| `frontloadable` |  |
| `detected_by` | mechanical-check |
| `evidence` | Four consecutive reviews list it under '## Missing': grep -c 'instrument-output diff' docs/plans/plan-057-james-dixson-9ecf1c/reviews/pass-{2,3,4,5}.md -> 1 each. Concretely at pass 5: Issue 3.1 said ~144, SC20 said ~147, and grep -ro 'knowledge-catalog' . --exclude-dir=.git | wc -l -> 152. |
| `escape_class` | stale-figure: a measured number written into plan.md drifts from what its own instrument prints, and no instrument compares them |
| `adjudication` | Named as Missing in FOUR consecutive red-team passes (2, 3, 4, 5) and never closed. It cost at least one defect in every pass: pass-2 C3/C12/C14 (SC3's unreproducible triple, SC1's figures, 58->59 and 63->64), pass-3 C8 (SC1's quote went stale from pass 2's own deletion, in the same pass that pinned it), pass-4 C9/C10 (Issue 1.0's five/four leftovers, in the issue that owns the anti-off-by-one arithmetic; the assess census 9 vs measured 11), pass-5 C3 (~144 vs ~147 vs measured 152, two approximations three lines apart). |
| `origin` | Every criterion and issue that cites a measurement is hand-transcribed from a command run at authoring time. Nothing re-runs the command and diffs the stated value, so a figure is correct only until the corpus changes — which it does on every plan that lands. |
| `culpability` | Process, not executor. Five independent reviewers each re-measured by hand and each found a different stale figure; the defect survived because catching it depends on a human re-running a command and comparing, which is exactly the class of check this repo mechanizes everywhere else. |
| `prevention` | An instrument that re-runs each cited command and diffs the stated value against its output. The plan already carries the two halves this needs: the Verification column gives the command, and the criterion cell gives the claimed figure. This was deliberately NOT added to plan-057 at pass 5 — inventing a sixth new instrument after an APPROVE would restart the review cycle on unreviewed text — so it belongs upstream as its own effort, not as a late amendment here. |
| `cost` | Five review passes, each spending part of its budget re-measuring figures by hand; one defect per pass reached the plan and had to be repaired in the next. |

