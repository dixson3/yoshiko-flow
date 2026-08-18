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
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | plan-044 gate Instructions were stale relative to the gate's own condition |
| `answered` | operator caught it during plan-044 execution |
| `frontloadable` | partial |
| `detected_by` | operator |
| `evidence` | unverified |
| `escape_class` | stale-artifact |
| `adjudication` | recorded from the planning session's account and NOT re-measured during execution — the bare `unverified` is deliberate so the mechanical check counts it |
| `origin` | plan-044 authoring |
| `culpability` | process |
| `prevention` | gate structuring at creation (plan-045 Issue 3.1) |
| `cost` | one operator interruption |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | did plan-045's bundle get committed and pushed? |
| `answered` | plan-044 reported the bundle 'uncommitted and untracked'; in fact 15 files / ~1180 lines were committed under a plan-044 commit message and pushed to origin/main |
| `frontloadable` | no |
| `detected_by` | operator |
| `evidence` | git log / git show on origin/main — independently verified during the planning session (exp-007) |
| `escape_class` | self-report-vs-verification |
| `adjudication` | content intact; attribution and publication state were not |
| `origin` | plan-044 execution |
| `culpability` | agent reporting |
| `prevention` | detected_by + evidence fields (D-6a); verify-before-close (plan-045 Issue 2.7) |
| `cost` | an in-flight, unfingerprinted, unapproved bundle published to a shared branch |

## RE-003

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | does this plan rewrite the skill executing it, creating a self-modification hazard? |
| `answered` | no — TESTING.md:14 already said so, and the SKILL_DIR resolver cannot reach the repo's skills/ dir |
| `frontloadable` | yes |
| `detected_by` | operator |
| `evidence` | TESTING.md:14 verbatim; the six SKILL_DIR search roots contain no repo-relative skills/ path |
| `escape_class` | reasoned-past-a-documented-fact |
| `adjudication` |  |
| `origin` | plan-045 drafting |
| `culpability` | process |
| `prevention` | promote the three-artifact invariant into AGENTS.md (plan-045 Issue 6.2a) |
| `cost` | a wrong hazard claim in a draft plan |

## RE-004

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | did the planning session's own resolutions table state what it verified? |
| `answered` | no — three separate over-claims, one caught by each of red-team passes 2, 3 and 4 |
| `frontloadable` | no |
| `detected_by` | operator |
| `evidence` | reviews/pass-2.md, pass-3.md, pass-4.md concern rows |
| `escape_class` | self-report-vs-verification |
| `adjudication` |  |
| `origin` | plan-045 planning |
| `culpability` | agent reporting |
| `prevention` | the actor column + an actor-agnostic resolver (plan-045 Issue 2.5) |
| `cost` | three review cycles spent on the plan's own bookkeeping |

## RE-005

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | is REQ-CLI-006 consistent with the source after the final sweep? |
| `answered` | no — third drift in one plan: grep gave 25, spec asserted 24, retrospective-report was unenumerated |
| `frontloadable` | no |
| `detected_by` | operator |
| `evidence` | grep -c '^@cli.command' skills/yf-plan/scripts/plan_manager.py -> 25; spec/cli.md asserted 24 |
| `escape_class` | verification-that-does-not-execute |
| `adjudication` | survived a 33/33 FULL-tier sweep because the REQ's Verification line was prose shaped like a command — nothing ran it |
| `origin` | plan-045 Epic 4 (added retrospective-report in the same epic that fixed the previous count drift) |
| `culpability` | process |
| `prevention` | restate the REQ as a set-equality invariant AND register test_cli_enumeration.py so the check executes (uv-yf-cli-enum) |
| `cost` | an operator catch at the push gate; #149's own thesis reproduced inside the spec of the plan citing #149 |

## RE-006

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | how many files did the plan-045 merge touch? |
| `answered` | I reported 31 files / +2813; the merge itself was 29 files / +2806 |
| `frontloadable` | no |
| `detected_by` | operator |
| `evidence` | git merge output: '29 files changed, 2806 insertions'; the 31/+2813 figure was git diff --stat origin/main..main, which also counts the separate bookkeeping commit |
| `escape_class` | self-report-vs-verification |
| `adjudication` | both numbers were real but I attributed the wrong one to 'the merge' — the exact substitution class exp-007 documents |
| `origin` | plan-045 §6.1 merge report |
| `culpability` | agent reporting |
| `prevention` | quote the command whose output is being reported, not a nearby command's |
| `cost` | a wrong figure in a status report to the operator |

## RE-007

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | was the push-authorization prompt delivered? |
| `answered` | no — the session sat 'blocked' on its own consent dialog, which swallows an injected prompt; the operator cancelled with Esc rather than risk keystrokes with an irreversible push at option 1 |
| `frontloadable` | partial |
| `detected_by` | operator |
| `evidence` | operator report at the push gate; matches the REQ-HERDR-022 trap this plan documented in Epic 5 |
| `escape_class` | blocked-agent-swallow |
| `adjudication` | a live instance of the blocked-agent hazard on the CHILD side — Epic 5 added the symmetric parent-side case but the child-side consent dialog is the same mechanism |
| `origin` | plan-045 §6.2 push gate |
| `culpability` | tooling |
| `prevention` | the 5.4 token side-channel is the standing mitigation; consider whether a consent dialog should stamp a token before blocking |
| `cost` | one cancelled dialog; no work lost |

