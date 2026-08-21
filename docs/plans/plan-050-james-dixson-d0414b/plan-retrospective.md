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
| `when` | 2026-08-20 |
| `stop_class` | 4 |
| `asked` | Continue the red-team/resolve loop until APPROVE; max-review-cycles raised 5 -> 9 for this session |
| `answered` | Stopped at cycle 9. review-loop-check returns escalates: true, stop_class 4 — a mechanical counter threshold, not a judgement call. Pass-9's C86 was resolved before stopping; a 10th review cycle would require a further operator raise. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | plan_manager.py review-loop-check --max-review-cycles 9 --json -> {escalates: true, cycles: 9, limit: 9, stop_class: 4} |
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
| `when` | 2026-08-20 |
| `stop_class` |  |
| `asked` | How should #181's silent green be fixed? Three scopes were drafted and each was refuted by an independent reviewer that BUILT it and ran the suite: unscoped (breaks test_doc_lint SC42, pass-8 C77), --path-keyed-always (breaks SC17 in the same file AND does not reach #181's titled --root scenario, pass-9 C86), and an opt-in --require-selection flag (viable, but leaves the default silent unless the always-loaded rule adopts it). |
| `answered` | Operator redirected: stop fixing at the site of the defect. Put a CLASSIFIER IN FRONT of the lint that decides ahead whether linting this path is meaningful at all (class = `selected` / `not-selected` / `no-such-path` / `empty`; exit 0 lintable, 1 degenerate, 2 could-not-run), leaving doc_lint's own lint path and verdict vocabulary UNCHANGED. All three previous attempts failed for the SAME structural reason -- each mutated the reporting of the component under test, so a shipped assertion characterising that reporting caught it. Stepping one layer upstream removes the collision surface entirely rather than negotiating with it. |
| `frontloadable` | partial |
| `detected_by` | operator |
| `evidence` | pass-8 C77 and pass-9 C86 each built the proposed fix in a sandbox and ran uv run _shared/test_doc_lint.py plus change_validation.py run --tier fast; both returned doclint-tests FAIL rc=1. The classifier design's central claim -- that test_doc_lint.py needs NO edit -- is under test at pass 10. |
| `escape_class` | review-fix-thrash |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` | GENERAL HEURISTIC, proposed for the yf-plan review loop: when N successive fixes to the same defect are each refuted, stop iterating on the fix and ask whether the defect can be addressed by a check placed IN FRONT of the failing component instead of inside it. The signal that this applies is that the refutations share a mechanism rather than being independent -- here, all three mutated the component's own reporting and collided with an assertion that pins it. A preflight classifier is cheap, additive, testable in isolation, and cannot break the characterisation tests of the thing it guards, because it changes none of its behaviour. Candidate for a red-team prompt line: 'if this is the third refuted fix for one defect, evaluate a guard placed upstream of the component before proposing a fourth.' |
| `cost` |  |

## RE-003

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-20 |
| `stop_class` |  |
| `asked` | How did #186 and #187 — both CRITICAL, both in plan_extract.py, both silently corrupting the bead DAG — survive every plan that touched or depended on that extractor? |
| `answered` | NOT a coverage gap. _shared/test_plan_extract.py exists and carries 62 assertions. Measured: ZERO of them assert that an extracted title equals its source text. Every assertion is STRUCTURAL — edges, ids, ordering, classification, recovery logging, unparsed reporting. The suite's very first assertion is 'an inline-code depends-on: is NOT read as an edge', so it covers the masking's PARSING purpose thoroughly and never notices that the same masking corrupts the payload it carries. #187 is the same blind spot: no assertion about a detail field because there is no detail field, and nothing asserts the extractor emits what SKILL.md 5.2a needs from it. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | grep -c 'check(' _shared/test_plan_extract.py -> 62; grep -n 'title' -> only id-recovery cases, no fidelity assertion. Upstream measured 4 of 35 titles blanked and 35 of 35 bead descriptions empty on a DAG reporting 0 unparsed, 53 edges, no dangling refs. |
| `escape_class` | structure-tested-payload-untested |
| `adjudication` |  |
| `origin` | test-design |
| `culpability` |  |
| `prevention` | GENERAL: these suites assert the SHAPE of a tool's output and never the FIDELITY of its content. That is the same shape as #181 (files_checked counts how many files were checked, never whether the right one was) and as this repo's recurring 'a control that reports clean while checking nothing'. A round-trip or identity assertion is the cheap countermeasure: for every extractor, assert that a field carried through unchanged EQUALS its source; for every filter, assert the selected set is non-empty on a known-positive input. Recommend a dedicated failure-mode pass over every script in _shared/ and skills/*/scripts/ — 5 of 20 script directories have NO test file at all (yf-beads-init, yf-okf, yf-optimal-instructions, yf-skill-authoring, and the untested half of yf-research) — scoped as its own plan or research project, not folded into plan-050. |
| `cost` |  |

