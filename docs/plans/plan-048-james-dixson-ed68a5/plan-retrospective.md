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
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Capability gate 'grammar widening is non-vacuous' RED: residue 81 vs approval-fixed target 54. Escalated to operator rather than re-deriving the target. |
| `answered` | Operator RE-BASED the target to 81 with corrected derivation recorded. The 54 was MISDERIVED, not missed: it inherited EXP-001's '~96 of 150 mechanically recoverable' (which counted a construct recoverable if a rule COULD produce an edge) while Issues 1.4/1.4a, written later in response to EXP-001's OWN warning about wrong fixes, REFUSE several of those same classes. Seven red-team cycles all checked the target was FIXED AT APPROVAL; none checked it was DERIVABLE FROM WHAT THE PLAN PERMITS. That is a real gap in the review process. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | gate-run.sh gate-grammar.sh -> exit 1, 'residue 81 exceeds the approval-fixed target of 54'; after re-base -> exit 0. Falsifiability mutant (class A disabled): residue 81->98, gate exit 1. |
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
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Issue 1.4a's all-or-nothing refusal cost two real edges in plan-033 (depends-on: 6.2, 1.5, gate:pi-rule-target-verified). Is that acceptable? |
| `answered` | Yes, and the reason is easy to miss: the value-level refusal and REQ-DATA-043's document-level INCONCLUSIVE gate are the same conservatism applied twice. plan-033 has unparsed[] != [], so pour_fidelity returns INCONCLUSIVE (exit 2), not FAIL, and the apparent divergence can never be consumed as a verdict. WITHOUT Issue 1.2 LANDING FIRST, THIS REFUSAL WOULD HAVE MANUFACTURED A FALSE FAIL ON plan-033. Sequencing 1.2 before 1.4a was load-bearing, not incidental. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | pour_fidelity before/after: plan-033 plan_edges 35->33, edge_set_match true->false, 2 invented edges. With --strict: exit 2 (INCONCLUSIVE) because extractor_unparsed=2. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-003

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | pour_fidelity before/after showed plan-048 losing 62 edges. Is the widening regressing its own plan? |
| `answered` | No. It is an ADDRESS-SPACE ARTIFACT. The 'before' run executes in the primary checkout and the 'after' run in the execute worktree; record-epic writes plan-048's **Epic:** field primary-side per the SKILL.md 5.3 address-space model, and pour_fidelity SKIPS a plan with no **Epic:** field. plan-048 was simply absent from the 'after' population and its whole edge count read as a loss. THIS IS EXACTLY THE CLASS OF THING THAT GETS MISTAKEN FOR DATA. Corrected net delta excluding plan-048: +11 edges across 6 plans, -2 in plan-033. |
| `frontloadable` | yes |
| `detected_by` | self-report |
| `evidence` | fid-after skipped: [{'plan':'plan-048-james-dixson-ed68a5','reason':'no **Epic:** field'}]; comparable 45->44. |
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
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | SC5 requires each newly instantiated type's bad.md to drive doc_lint to exit 1. D-10/REQ-DATA-045 forbids any E-severity check on a path outside a plan bundle unless the corpus already passes it. For five types these are mutually unsatisfiable. Which wins? |
| `answered` | D-10 wins; SC5 is PARTIALLY UNDISCHARGEABLE and that is recorded rather than papered over. Affected types: research-summary, research-artifact, research-sources (docs/research/** - bundle_status is null there, so an E can NEVER be softened and would hard-fail the research corpus permanently), and reference-comment (its one check is W). Two further types, reference-tracker and reference-authored, declare NO checks by design - 3 and 12 heterogeneous files with no producer and no template - so there is nothing to fail. A W does not change the exit code, so none of these can reach exit 1 without an E that D-10 forbids. Resolution: ship the strongest available assertion - the bad fixture FIRES a finding and the conforming control fires none - and record the deviation in the test block. Faking an E to satisfy SC5's literal wording would break D-10 and hard-fail the research corpus, a worse outcome than a scoped recorded deviation. THIS IS A SUBSTANTIVE SCOPE CALL, not a detail: a success criterion is partially undischargeable because a declared decision forbids the severity it needs. |
| `frontloadable` | yes |
| `detected_by` | self-report |
| `evidence` | doc_lint --type research-artifact --path <bad fixture>: verdict PASS errors 0 warnings 1 findings 1, exit 0. The finding fires; the exit code cannot. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-005

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Epic 2 instantiated ten document types. Did any of the new checks ship unable to do what they claimed? |
| `answered` | Three defects, all found by MEASUREMENT rather than review. (a) BLAST-RADIUS FINDING: doc_lint loads every schema EAGERLY, so ONE malformed schema - a code-generated type missing derive_from - made EVERY instantiated type report INCONCLUSIVE with files_checked 0, not just its own. The failure is fail-SAFE (INCONCLUSIVE, never a false PASS) but its blast radius is the whole type set, and a silent files_checked=0 across all types is indistinguishable from a linter that is working. Guard test added. (b) doc_lint.sections() returns only H2/H3 and NEVER an H1, so plan-retrospective's title check via headings-any-level could ONLY EVER FAIL - the mirror image of R4's check-that-cannot-fail. Caught by SC6, now pinned by a test. (c) The nested-reach fixture existed to prove the findings glob is RECURSIVE, and it proved it by driving exit 1. When Issue 2.9 moved the finding content checks to R, the fixture stopped failing and the recursion proof went SILENT while still appearing to pass. Re-pointed at the check that still has teeth. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | doc_lint --type upstream-triage --json -> reason 'plan-retrospective.toml: code-generated type must set derive_from', files_checked 0 for ALL types. sections('# Title Only') -> []. finding bad.md exit 0 after 2.9, restored to 1. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-006

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Operator reported that plan-retrospective.md did not exist after the agent had claimed three times that entries were recorded, verifying with retrospective-report --json returning {present: false, count: 0}. |
| `answered` | The file DID exist with 3 entries (RE-001..003), written by the verb at 16:19:46, before the correction was sent. The disagreement is itself an ADDRESS-SPACE ARTIFACT - the same class as the 62-edge 'regression' recorded in RE-003. retrospective-append, record-epic and update-status all write PRIMARY-SIDE by the SKILL.md 5.3 model, while the execution worktree carries only code changes. A retrospective-report run against the WORKTREE copy of the bundle correctly reports present:false, because that file genuinely is not there. Run against the primary checkout it reports present:true count:3. LESSON THAT GENERALISES: under worktree execution, a bundle-state verification is meaningless unless the address space is named. The agent's reports should state WHERE an artifact landed, not just that it landed - 'recorded' is ambiguous across two trees and the ambiguity looks exactly like a false claim. THE OPERATOR'S UNDERLYING CONCERN WAS STILL CORRECT AND FOUND A REAL RISK: the file was UNTRACKED on main and absent from the execute branch, so the Phase 6 merge would never have carried it. Only the primary-side commit at land time saves it. |
| `frontloadable` | yes |
| `detected_by` | operator |
| `evidence` | primary: retrospective-report -> {present:true, count:3, by_kind:{deviation:3}}; ls -la shows plan-retrospective.md 4.0KB Aug 19 16:19:46. worktree: no such file. git status primary: '?? docs/plans/plan-048-james-dixson-ed68a5/plan-retrospective.md' (untracked). |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

