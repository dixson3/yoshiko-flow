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

