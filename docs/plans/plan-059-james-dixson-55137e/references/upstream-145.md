---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #145: New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

- **Number:** 145
- **Title:** New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/145
- **State:** OPEN
- **Labels:** 

## Body

> **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-retrospective`** skill that measures **escape rate** — defects that survived review — and enforces a two-part resolution contract on every defect fix: **the fix, plus a prevention that would have caught it.**

Two escape classes, deliberately separate:

| Class | Definition | Captured at |
| :-- | :-- | :-- |
| **Intra-plan** | The plan's own reviews missed something that its **own execution** then found | plan close |
| **Post-release** | An issue filed later, or a new plan written, to correct something an **earlier plan's** review could have caught | issue triage |

## Why this is worth building

`yf-plan` invests heavily in review — conformance pass, red-team passes, gates, portability audit — but **has no idea whether any of it works.** There is no measurement, so a prompt regression is invisible: a review that stops catching things looks exactly like a plan with no defects.

That was not hypothetical. plan-039's R9 filed a one-off bead (`yf-7zrd`) precisely because *"prompt regressions are silent… only a re-measure can tell."* That re-measure has now run once, by hand, and is recorded on #134. It worked — and it should not have been a one-off bead. It should be a step.

### The measurement, as it stands today

| Plan | Red-team passes | Concerns/pass | Structural escapes |
| :-- | --: | --: | --: |
| plan-013 (`d3-pxe`) | 3 | 5.0 | **1** |
| plan-039 | 5 | 7.0 | **1** |
| plan-040 | 3 | 7.3 | **0** |

Reviews are not degrading. But this took manual archaeology across two repositories to produce, and n=3 after roughly forty plans — because nothing was capturing it as it happened.

---

## What was learned building it by hand

These four findings are the real content of this issue. Each one is a design constraint discovered by doing the work, not by reasoning about it.

### 1. Defining "escape" is the hard part, and four real cases prove it

Adjudicated by hand while re-measuring:

| Case | Verdict | Reasoning |
| :-- | :-- | :-- |
| plan-039's stale baseline literal (`TP=1 FP=16`, actual `FP=17`) | **escape** | Defect in `plan.md` itself; survived five review passes; found at execution |
| plan-040's three implementation defects (an `except Exception` that would not catch `run()`'s `SystemExit`; a duplicate test name shadowing a new test; two stale bullets in an always-loaded rule) | **not an escape** | Caught by the plan's own tests and the `check_prescriptive_push` tripwire — the validation layer working, not review failing |
| plan-040's "~40 plans" backfill estimate (actual stampable: 18) | **not an escape** | The plan anticipated the uncertainty and specified the handling ("an unidentifiable tracker is recorded as such, not silently skipped"). It worked as designed |
| plan-039's eight `references/*.md` shipped without OKF frontmatter | **process escape** | No criterion covered it and **no gate existed** — categorically different from a review that had the check and missed |

**The fourth row is the discovery.** *Review escapes* (the check existed, missed it) and *process escapes* (no check existed) need separate counts. They have different fixes — one is a prompt problem, the other a gate-coverage problem — and conflating them makes the metric useless. Any taxonomy that cannot adjudicate these four is decorative.

### 2. Forensic attribution is mechanical, and portable

`yf-plan` lands every plan as a `--no-ff` merge of `<plan-id>-execute` (REQ-PLAN-055 / REQ-BRANCH-002). That is a **yf-plan-owned artifact present in any consuming repo**, independent of commit-message conventions. So: `git blame` the defective line → find the containing merge → recover the plan id.

Verified against #137:

```
$ git log -1 -S "Deliberately emit NO" -- yf/build.rs
96e4c2b  plan-019: preflight self-update offer + cache version-invalidation
$ git log --merges --ancestry-path 96e4c2b..main | tail -1
baa9379  Merge branch 'plan-019-james-dixson-eea8e7'
```

Note what is *not* relied on: this repo happens to put plan ids in 80% of commit messages, but that is a local habit. The merge-commit signal is the portable one.

### 3. Attribution ≠ blame, and the same test proves it

That probe found plan-019 authored #137's root cause. But plan-019's own code comment reads:

> *Known limit (documented, not over-promised): it still cannot observe repo-wide changes outside the `yf/` package on an incremental rebuild.*

**plan-019 knew.** It made a defensible tradeoff and wrote the limit down. The defect only materialised much later, when a different plan shipped `yf self install --from-build` (REQ-YF-SELF-004) and turned a documented limit into a promoted artifact.

A naive "which plan introduced it" metric blames plan-019's review — wrongly, and it would teach reviewers to reject documented tradeoffs, which is the opposite of the desired behaviour.

So the skill must separate:

- **Origin** — which plan the code came from. Mechanical, cheap, reliable.
- **Culpability** — which review *could* have caught it *given what was knowable then*. A judgment, and severely hindsight-prone.

**Default to "no review at fault"** unless the evidence was demonstrably available at the time. Without that guard every retrospective manufactures a guilty review, and the metric becomes a blame generator.

### 4. A manually-invoked skill will not be invoked

Two proofs, both from this repo, both recent:

- **`closable`** shipped in plan-038 and had **never once been run to completion** until two days later, when running it revealed it spawned 991 subprocesses and took over four minutes. Nothing invoked it.
- **plan-039's audit blind spot**: `plan_manager.py audit` exists and works, but runs only as a Phase-3 approval gate — so `references/` and `reviews/` files written during EXECUTE are never checked by anything. Four completed plans shipped non-conformant files. The check existed; nothing fired it at the right phase.

The retrospective's value is the **forcing function** (every fix ships a prevention). A forcing function that does not fire is decoration. **This is the constraint that should drive the design.**

---

## Proposed architecture

Follow the **`yf-change-validation` pattern** exactly — it is the established precedent in this repo for an engine that `yf-plan` delegates to without depending on:

> This is a **prose soft-dep**: present → delegate, absent → fallback. **NEVER** add `yf-change-validation` to this skill's frontmatter `depends-on-skill` — that is force-install, the wrong coupling.
> — `yf-plan` SKILL.md §6.1.5

### Ownership split

**`yf-retrospective` owns:**

- the escape taxonomy (review-escape / process-escape / not-an-escape), which must adjudicate the four cases above;
- the origin-vs-culpability split and the hindsight guard;
- the forensic attribution engine (`git blame` → `<plan-id>-execute` merge → plan id);
- the prevention-category vocabulary.

**`yf-plan` owns:**

- two delegation points (below);
- the **disposition requirement**: an `include` on a defect-class issue must name its prevention. That is a `plan.md` contract, so it belongs in `yf-plan`'s SPEC and its conformance checklist.

**A `yf-drift-check` edge** keeps the two in agreement, since the taxonomy is stated in one skill and enforced in the other.

### Trigger points

| Trigger | Fires at | Payload |
| :-- | :-- | :-- |
| **Close-time** | `yf-plan` Phase 6.4 | intra-plan escape capture, while the evidence is fresh and on disk |
| **Triage-time** | `yf-plan` Phase 1.4 | forensic attribution per candidate issue — you are already assessing it, so the check is nearly free there and pure overhead anywhere else |
| **Manual** | `/yf-retrospective` | ad-hoc issue assessment, **pre-plan**, no plan required |

The first two are what stop it rotting (finding 4). The third is what makes it usable during issue assessment before any plan exists — which `yf-plan`'s phase model has no home for, and is a large part of why this is a separate skill rather than more `yf-plan`.

### The two-part resolution contract

Constrain "prevention" to **executable or checkable** categories:

`SPEC requirement` · `phase validation` · `test case` · `process step`

*"Be more careful"* and *"reviewers should watch for X"* are **inadmissible** — neither is checkable, and admitting them is how this degenerates into ritual.

---

## Risks, stated up front

- **Goodhart.** Once escape rate is tracked, there is pressure to classify defects as non-escapes — and the four boundary cases above are exactly where that pressure lands. Mitigation: record the **adjudication and its reasoning**, not just the count, so classification is reviewable after the fact.
- **n stays small for a long time.** Three plans of history; escape rate 1 → 1 → 0. This will take a year to say anything statistically. Its near-term value is the forcing function, not the number — and it should say so, or it will be over-read.
- **Hindsight bias**, addressed by the culpability default above, but worth re-stating: the failure mode is a metric that always finds someone to blame.
- **Two homes for one taxonomy.** Stated in `yf-retrospective`, enforced in `yf-plan`. Real coupling; the `yf-drift-check` edge is the mitigation.

## Open questions for planning

1. Where exactly does intra-plan capture write — `log.md`, a `reviews/postmortem.md`, or plan.md frontmatter? It must survive `/clear` and be readable cold, like every other bundle artifact.
2. Is the disposition requirement **enforced** (conformance `INCOMPLETE` without a prevention) or **advisory**? Enforced is the forcing function; advisory is what gets ignored.
3. Does `yf-research` get the same treatment? It has the analogous question — *was a published finding later refuted, and which pass should have caught it?* One taxonomy, potentially two consumers.
4. How far back does the forensic check walk before giving up? Cost grows with history.

## Relationship to queued work

**#136** (reconcile silently skipped mapped `include` issues while the plan reported `complete`) and **#140**'s audit-at-close both want the **same missing Phase 6.4 hook** as this issue's close-time trigger. Three payloads, one absent step.

That hook's design should be settled **once** — either as a prerequisite, or as an explicit first epic here — rather than three times in three plans.

## Related

- **#134** — the manual re-measure this would automate; carries the full result and the confound analysis
- **#113** — execution-rehearsal pass; the escape-rate metric is precisely the data its re-scope now waits on
- **#136** — shares the Phase 6.4 hook
- **#140** — shares the Phase 6.4 hook (audit-at-close)
- **#135** — a defect class found four times in one plan; the kind of pattern this would surface automatically
- **#137** — the worked example for attribution-≠-blame

🤖 Generated with [Claude Code](https://claude.com/claude-code)

