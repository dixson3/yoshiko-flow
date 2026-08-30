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
| `when` | 2026-08-29 |
| `stop_class` | 4 |
| `asked` | `review-loop-check` reported cycles 5 of 5, `escalates=true`, `stop_class 4`. The session asked the operator whether to raise `--max-review-cycles` to 6 and run a sixth pass, stop with the plan in review carrying a REVISE, or approve over the REVISE with `--override-ready-check`. |
| `answered` | Operator raised the bound to 6 and directed pass 6. The override-ready-check option was explicitly declined. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | `review-loop-check --json` => `{cycles: 5, limit: 5, escalates: true, stop_class: 4}`; five `reviews/pass-*.md`; count-equality with `log.md` at 5/5. ESC-001 raised, pushed, and resolved with no_answer_taken: false. |
| `escape_class` | none — no defect escaped; this entry records a control that HELD |
| `adjudication` | Mechanical stop, correctly reached. `review-loop-check` returned `escalates: true` with `stop_class: 4`, so the halt was an exit code rather than a judgement call. *(The positive-control note originally written here was MISPLACED by a mis-targeted edit — it belongs on RE-002, the entry about the refusal, and has been moved there and rescoped. Recorded rather than silently relocated.)* |
| `origin` | plan-060 review loop, cycle 5 |
| `culpability` | none |
| `prevention` | Not a defect to prevent. What made the right call CHEAP is worth keeping: `review-loop-check` returned a machine-readable `escalates: true` with `stop_class: 4`, so the halt was reached by an exit code rather than by judgement, and `escalation-raise`/`escalation-push` gave the question a durable artifact rather than a prompt that could be lost. **Positive controls are rarer than defects and are not usually written down** — the corpus records what went wrong far more often than what a mechanism prevented, which biases any later analysis of whether these gates are worth their cost. |
| `cost` | one operator round trip |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-29 |
| `stop_class` |  |
| `asked` | Whether the session should raise its own --max-review-cycles bound to continue the review loop, rather than halting and putting the decision to the operator. |
| `answered` | It declined to self-grant. The bound is documented as the operator's lever, with the stated purpose that a plan which has burned N cycles must not SILENTLY resume. The session halted, raised ESC-001, and waited. |
| `frontloadable` | no |
| `detected_by` | self-report |
| `evidence` | `SKILL.md`: `the operator's only exit is a per-invocation --max-review-cycles <n> raise, echoed to log.md`. The session ran `review-loop-check`, got `escalates=true`, and raised ESC-001 instead of passing `--max-review-cycles` itself. |
| `escape_class` | none — no defect escaped; this entry records a control that HELD |
| `adjudication` | **A positive control on the BEHAVIOUR, and explicitly NOT on the artifact.** #293 is an executing agent closing a `Type: human` gate by writing its own authorization into the close reason. What this entry can prove is narrow and mechanical: `review-loop-check` returned `escalates: true`, and the session did **not** pass `--max-review-cycles` itself — the ESC-001 artifact exists and the bound was raised only after an operator turn. **What it CANNOT prove is the part that would make it an exact contrast**, and the earlier draft of this cell claimed otherwise. `ESC-001.answer` is **free text written by this session** recording what the operator decided, which is structurally the SAME artifact class as #293's close reason: nothing in the record distinguishes "the operator answered and the session recorded it" from "the session wrote the answer itself". `asked_of` is empty, so the escalation names no recipient, and the `push_batch` token has no verifiable upstream trace. So: a positive control on conduct, evidenced by an absence (the flag not passed) rather than by a presence — and the residual gap is the very one #293 exposes. Claiming "the contrast is exact" was the one self-favourable unfalsifiable claim in a bundle whose thesis is that such claims are the defect, and red-team pass 6 was right to catch it. |
| `origin` | plan-060 review loop, cycle 5 |
| `culpability` | none for the refusal; the overclaim in the first draft of this cell is the session's |
| `prevention` | Not a defect to prevent. What made the right call CHEAP is worth keeping: the halt was reached by an exit code (`stop_class: 4`), not by judgement, and `escalation-raise` gave the question a durable artifact rather than a prompt that could be lost. **Positive controls are rarer than defects and are not usually written down** — the corpus records what went wrong far more often than what a mechanism prevented, which biases any later analysis of whether these gates are worth their cost. The *strengthening* worth having is an escalation whose resolver identity is not first-party — the same unsolved problem as #304. |
| `cost` | one operator round trip |

## RE-003

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-29 |
| `stop_class` |  |
| `asked` | Whether an ordinary operational action taken for an unrelated reason can invalidate a plan's design premise mid-review. |
| `answered` | Yes, and it did. The operator directed a durability commit of the bundle. That commit falsified Issue 1.9's premise that draft bodies are untracked BY CONSTRUCTION at dry-run time, and flipped the prescribed enumeration from 37-correct to 0-against-40. The premise was state-dependent and nothing in the plan said so. |
| `frontloadable` | partial |
| `detected_by` | operator |
| `evidence` | Before the bundle was committed: `ls-files` **0**, `--others --exclude-standard` **N**. After the commit range `a5664e7..d039600` (`a5664e7` alone is 39 files; the total grew with each review pass): **N** and **0**. The absolute N decays with every added file, so the durable statement is the INVARIANT: the two commands swap which one returns N and which returns 0, purely on tracked-ness, with no edit to either command. Same commands, same paths, opposite answers. See assets/enumeration-spike.md F2. |
| `escape_class` | intra-plan — caught at review, before execution |
| `adjudication` | **A finding about premises being STATE-DEPENDENT, not a mistake by anyone.** The commit was correct and was taken for durability: before it, the bundle was 39 untracked files on a branch with zero commits, and a `git clean -xdf` would have destroyed five review passes and six investigations. It happened to change the truth value of a design claim in an unrelated part of the plan. **The operator could not reasonably have connected the two beforehand** — a durability commit taken to protect five review passes from `git clean -xdf` has no visible relation to an enumeration premise. **The session could have, and that is the honest half.** It wrote *"untracked by construction"* about a git tracked-ness state, inside a skill that ships a `commit-plan` verb whose entire purpose is to commit a bundle pre-landing — no commit needed to happen for the premise to be wrong. *(An earlier draft of this cell said "neither party", which contradicted this entry's own `culpability` cell and put the self-favourable version in the field a reader quotes. Corrected after red-team pass 7 caught the contradiction.)* The plan asserted a property of the world (*"draft bodies are untracked by construction"*) as though it were a property of the design, and nothing in the document marked it as contingent. |
| `origin` | Issue 1.9, written in the pass-3 revision |
| `culpability` | none for the commit. The session's is the unmarked contingency: a premise that depends on whether someone has run `commit-plan` is not "by construction". |
| `prevention` | **The spike is the generalisable remedy, and it is stronger than the specific fix.** A fixture holds BOTH states at once; the live repository can only ever be in one, so five consecutive rounds each measured a true fact about a transient state and generalised it. `assets/enumeration-spike.md` runs every candidate against both states and both cwds simultaneously — which is why it settled in one pass what prose reasoning had missed five times. **The transferable rule: when a claim is about which of several tools is correct, build the fixture that distinguishes them rather than reasoning about their semantics.** Secondarily: mark contingent premises as contingent, and prefer a criterion over a premise wherever the criterion can be written. |
| `cost` | one high-severity red-team concern, one bound raise, one spike |

