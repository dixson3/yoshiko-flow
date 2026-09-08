---
type: Retrospective
okf_spec: OKF-PLAN
description: "plan-067's retrospective: 14 content defects and 11 process defects, counted and separated, plus the three instrument false-greens this plan's own experiments and instruments produced."
id: plan-retrospective
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# Plan retrospective — plan-067-james-dixson-de852a

## Why the two classes are counted separately

A **content defect** is a false or absent claim in an artifact: a page saying six where the truth
is seven, a diagram omitting a group. A **process defect** is a defect in the thing that was
supposed to *catch* the content defect: a checker that reads past its subject, a criterion that
cannot fail, a review resolution that was never applied.

They are counted apart because they have different remedies and different failure modes. A
content defect is found by looking; a process defect is found only by making the instrument fail
on purpose. Merging the counts would let a plan report "25 defects fixed" while saying nothing
about whether anything would catch the 26th.

## Counts

| Class | Count | What it means |
| :-- | --: | :-- |
| **Content defects** | 14 | false or absent claims in shipped artifacts |
| **Process defects** | 11 | defects in the instruments that should have caught them |
| **Instrument false-greens** | 3 | an instrument that reported PASS over input it could not see |

The process count being nearly as large as the content count is the plan's own thesis restated:
the corpus was **green** while every content defect below existed.

## Content defects (14)

| # | Defect | Where |
| :-- | :-- | :-- |
| C1 | the lint subset stated as six rules where the truth is seven | 5 derived sites under `skills/**` |
| C2 | `yf-incubator` called "a beads-free utility skill" against its own `workflows` group and `depends-on-skill` | `web/content/skills/yf-incubator.md` |
| C3 | four skills rendered "auto (fires from its description conditions)" while their descriptions declare a slash trigger | the published site |
| C4-C9 | six declared slash sub-verbs documented nowhere on the site | `restore`, `status`, `pull`, `infer`, `migrate`, `reindex` |
| C10 | `yf harness skills prune-private` — live and **destructive** — documented nowhere | the whole corpus |
| C11 | seven shipped flags documented nowhere | `--prune-formulas`, `--also-quarantine`, `--quarantine-dir`, `--shared-root`, `--no-skills`, `--rules-only`, `--path` |
| C12 | the `lander` agent named nowhere on the page whose subtitle covers it | `workflows.md` |
| C13 | `architecture.d2` omitted 5 of 8 tool deps, 7 of 12 CLI paths, and **all 12** skill→skill edges | `web/content/images/` |
| C14 | `lifecycle.d2` labelled a preflight status `deps-missing`; the literal is `system_deps_missing` (#375) | `web/content/images/` |

## Process defects (11)

| # | Defect | Why it is a PROCESS defect |
| :-- | :-- | :-- |
| P1 | a set-membership claim FAILed on a wrong member but not a MISSING one | an omission was invisible **by construction**; deleting two members with the count unchanged exited 0 |
| P2 | the `members is None` branch routed an unenumerated group to the CLEAN population (#376) | made "state a count, list nothing" the cheapest possible evasion of the new rule |
| P3 | both of `e-web-cli-surface`'s declared failure directions ran page→CLI | no check anywhere could see a shipped command no page documents |
| P4 | no edge covered the pipeline agent set at all | the `lander` gap had nothing to find it |
| P5 | a tri-state frontmatter key read as two-valued by a default argument | both sides were internally consistent; the falsehood lived where neither declared anything |
| P6 | the authored-page guard was existence-only (#374) | `touch` satisfied a check whose purpose is that a **governed** page exists |
| P7 | `## Invocation` used ≥4 incompatible shapes across 8 skills and was absent from 12 | any check keyed on it was silently vacuous for 60% of the corpus |
| P8 | `render-bytes-match` used `glob`, not `rglob` | re-rendered 4 of 9 diagrams while reporting "all identical" |
| P9 | `run_cmd` passed `cwd` positionally | a caller needing another directory got a `TypeError` surfaced as INCONCLUSIVE |
| P10 | SC24b's predicate matched neither spelling the guard uses | reported INCONCLUSIVE about code that was right there |
| P11 | one constant served both "the site plan-066 repaired" and "the current subject" | repointing it fixed one criterion and broke another; rewriting it would have falsified the historical record |

**P8 through P11 were committed by THIS plan, in its own instruments, while it was fixing the
others.** They are recorded here rather than quietly corrected because that is the honest rate:
an instrument-building plan produces instrument defects, and a retrospective that showed only the
ones inherited from elsewhere would misreport the difficulty.

## The three instrument false-greens

A false green is worse than a red: it is an instrument reporting PASS over input **it could not
see**. Each of these was caught only because something else contradicted it.

### FG1 — EXP-003's slash-verb extractor

It reported `MISSING_SLASH=[]` for all 20 skills and concluded the class was "closed completely".
**EXP-002 contradicted it**, naming `/yf-change-validation infer`. Adjudicated against the
artifacts: the extractor searched for literal `/<skill> <verb>` strings, but a subcommand **table**
declares the verb as `` `infer` `` with no slash prefix — so it returned green over a shape it
never examined. The finding carries an amendment retracting it, and that amendment was itself
corrected once more after pass-1 measured the retraction as overstated.

**What it cost:** nothing, because EXP-002 existed. **What it would have cost alone:** the plan
would have scoped out its one clean signal class on the grounds it was already solved.

### FG2 — EXP-001's layout recommendation

It recommended re-pinning `elk → dagre` on the strength of **one** sample. Pass-1 re-measured
across all six diagrams: hard text-on-text collisions on 2, larger output on 6, semantic ordering
discarded on 3, and dagre **worse on `architecture`** — the diagram the objection was about. The
one sample was the single case where the engines are equivalent.

**The generalisable lesson, recorded because it recurs:** a layout judgement needs the whole
corpus, not a representative. The dagre render is kept as a negative artifact so the sampling
error stays inspectable.

### FG3 — this plan's own negative-control harness

While writing `check_user_invocable.py`'s controls, `relative_to()` raised on an out-of-repo
`--skills-root`. The traceback exited 1 — and the control was checking for exit 1. **The control
passed for the wrong reason**, reporting a fail-capable checker on the strength of a crash.

**This is the class the whole plan is about, committed inside the plan's own verification.** It
was caught by reading the *output* rather than the exit code — which is the same discipline
`ctl_counts` already documents and which this repository has now needed five times.

## What the plan changed about how it is caught next time

- Every new checker is **observed to fail against a CODE-SIDE mutation under passing docs**, and
  the gate pins the four **by name** rather than by a count. A count floor can be satisfied by
  inheritance and broken by arithmetic; measured, pass-1's `--min-checkers 8` was **unreachable**
  because the maximum was 7.
- Every checker declares its `not_checked` classes **in its own output**, not only in prose.
- The three-valued exit contract is enforced everywhere: **2 IS NOT 1**. An instrument that could
  not look is not a document that is wrong.
- The prose that contradicted the new rule — "an omission is not drift" — was **amended at all
  four sites** rather than left standing beside it.

## Epic 7 — a SECOND fully-green set failed a human read

**This is the plan's highest-value process finding, and it was unrecorded until now** (pass-4 C9).

The 20-diagram set that Epic 6 presented was green on every axis this plan built: every checker
at 0, all 20 PNGs sha256-identical to a fresh render, 6 negative controls observed to fail, 29 of
32 criteria holding. **The operator rejected it.** Not for a false claim — for being too wordy,
and for `architecture.d2` not reading as a layered stack.

### What that measures

| | Claim | Verdict |
| :-- | :-- | :-- |
| First set | mechanically complete | **accurate, and rejected** |
| plan-066's set | mechanically complete | **accurate, and rejected** |

Two consecutive plans produced fully-green diagram sets that a human read turned down. **The
mechanical gates were not wrong either time.** They were answering a different question from the
one that decides acceptance, and no amount of additional checking would have closed the gap —
which is exactly why the Diagram human-read gate is `gate_type: human` and why an agent read is
declared evidence rather than a discharge.

The generalisable finding: **"green" and "good" are different predicates, and this plan can now
demonstrate that with two independent measurements rather than assert it.**

### What the restyle then found

Epic 7 was not only cosmetic. Changing the DOCUMENT reopened a defect in the CHECKER:

- `GROUP_RE` required a parenthetical count to **find** a group at all, and D8 forbids
  parenthetical counts. **Measured:** after the restyle, `architecture.d2` yielded **zero**
  detected groups, and deleting a member box left `check_web_counts` at exit 0 with
  `not_checked_groups: 0` — Issue 1.1's exact two-member-deletion defect, reintroduced without
  touching the checker.
- Three further instrument defects surfaced in Epic 7 and are counted in the process class
  below: container detection anchored at column 0 (five claims vanished, caught by the claim
  floor added hours earlier); the sublabel transform matching the literal id `label`; and a
  control-registry suffix that passed a label to `argparse` as a subcommand.

**A style change is a checker test.** That is the lesson worth carrying: the instruments were
tuned to one document shape, and only a change of shape could reveal it.

### The one place the restyle made something WORSE

**`lifecycle.png` went from 11602px tall to 13362px.** Recorded because it is a measured
regression on the exact dimension the first read objected to, and because the mechanism
generalises:

> **The fix for wordiness worked against the aspect ratio.** Expanding 95 sublabels into child
> boxes is what removed the wordiness — and child boxes are *vertical structure*, so the diagram
> with the most sublabels got the most new height. The nodes are no longer wordy; the artifact is
> taller than ever.

Nothing in Epic 7 could have caught this, and that is the point: **`build-and-render`'s legibility
check is a 3:1 single-column threshold, and 1.56:1 passes it comfortably.** The check is not
wrong — it detects a *column masquerading as a graph*, which this is not. It simply does not
measure "is this too big to take in", because no threshold does.

The two plausible remedies — split the `phase-model` + `lifecycle` combination back apart, or
restructure horizontally — are **deliberately not started**. Which is right depends on what a
reader objects to, and guessing would repeat the error the whole Epic exists to correct: acting
on a mechanical signal where the deciding question is a human one.

### Updated counts

| Class | Was | Now | Added by Epic 7 |
| :-- | --: | --: | :-- |
| Content defects | 14 | **17** | the wordy node set; `architecture.d2` not reading as a stack; `lifecycle.png` growing to 13362px under the fix for the first two |
| Process defects | 11 | **15** | count-blind group detection; column-0 container anchor; the `label` collision; the `::` suffix collision |
| Instrument false-greens | 3 | **4** | `sc_architecture_complete` passing while `architecture-deps.d2` did not exist — a criterion satisfied by the ABSENCE of its subject |

The fourth false green is the sharpest of the four. `SC27c` reported PASS against a file that had
never been created, because the function still read the old path. It was caught by *looking*
before changing it, which is the only reason it is in this table rather than in the shipped plan.

## The rate to carry forward

Fourteen content defects, eleven process defects, three false greens — and the corpus was green
throughout. The number worth remembering is not 14 or 11. It is **3**: the number of times, in
one plan, that an instrument said PASS about something it had not read.

## RE-001

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-07 |
| `stop_class` | 2 |
| `asked` | The archify trial decision gate blocks Issue 4.1 and every downstream issue. Adopt, keep for exploration, or drop? |
| `answered` | KEEP FOR EXPLORATION. d2 remains the committed, checked source of truth; adoption stays open as a separate upstream plan. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | bd ready returned zero ready TASK beads: every remaining task was downstream of Issue 4.1, blocked by gate yf-mol-gtcy.9. A genuine DAG stall, not a judgement call. |
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
| `when` | 2026-09-07 |
| `stop_class` |  |
| `asked` | Did this plan's own negative-control harness prove what it claimed? |
| `answered` | No. check_user_invocable's control passed for the WRONG REASON: relative_to() raised on an out-of-repo --skills-root and the traceback's exit 1 was read as the assertion firing. Fixed, then re-observed. |
| `frontloadable` | partial |
| `detected_by` | self-report |
| `evidence` | uv run scripts/checks/check_user_invocable.py --skills-root $T/skills -> ValueError traceback, exit 1. Caught by reading the OUTPUT, not the exit code. |
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
| `when` | 2026-09-07 |
| `stop_class` |  |
| `asked` | Did the criteria instrument this plan authored contain defects of the class it was built to catch? |
| `answered` | Yes, four: render-bytes-match used glob not rglob (4 of 9 diagrams re-rendered while reporting 'all identical'); run_cmd passed cwd positionally; SC24b's predicate matched neither spelling the guard uses; and sc_combined_diagrams asserted a GUESSED SkillsCommand verb set. |
| `frontloadable` | no |
| `detected_by` | self-report |
| `evidence` | Each found by RUNNING the verb rather than reading it: render-bytes-match reported 4 diagrams where 9 exist; build-and-render raised TypeError; page-guard reported INCONCLUSIVE against a guard present in the file. |
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
| `when` | 2026-09-07 |
| `stop_class` |  |
| `asked` | Were the retrospective entries written AS THE WORK HAPPENED, as the skill prescribes? |
| `answered` | No. They were written at Issue 6.3, from the bead close reasons and the session record. The narrative plan-retrospective.md is complete and accurate; the RE-NNN machine-readable corpus is reconstructed rather than accumulated. |
| `frontloadable` | yes |
| `detected_by` | self-report |
| `evidence` | retrospective-report returned count 0 at Issue 6.3, which is what surfaced the gap. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-005

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-07 |
| `stop_class` | 2 |
| `asked` | Two capability gates remain — Diagram human read (blocks 6.4) and Upstream write authorization (blocks 6.5). Both are gate_type: human. |
| `answered` | PENDING. Not resolved, and not resolvable by this session: an agent read is evidence, never a discharge, and an outward-facing write needs authorization a green test cannot supply. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | bd ready returns zero ready TASK beads; the only open tasks are 7.5 and 7.6, each behind a human gate. 27 of 28 criteria PASS; the one FALSE is plan-066's diagram-reads, reported as the DECLARED HANDOFF rather than a regression. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-006

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-07 |
| `stop_class` | 2 |
| `asked` | The restyled set is presented. Does the Diagram human-read gate accept it? |
| `answered` | HELD a SECOND time — the operator is reading it themselves. Gate 3 remains sequenced after it. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | bd ready returns zero ready TASK beads; the only open tasks are 6.4 and 6.5, each behind a human gate. 36 of 40 criteria hold; the one FALSE is the declared handoff. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-007

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-09-07 |
| `stop_class` |  |
| `asked` | Did the restyle make anything worse? |
| `answered` | Yes, one thing: lifecycle.png grew from 11602px to 13362px tall — a regression on the exact dimension the first read objected to. Expanding 95 sublabels into child boxes removed the wordiness, and child boxes are vertical structure. No remedy started; which one is right is the operator's call. |
| `frontloadable` | no |
| `detected_by` | self-report |
| `evidence` | PNG header read: 4364x11602 before, 8556x13362 after. build-and-render's 3:1 legibility threshold passes it at 1.56:1 and is not wrong to — it detects a column masquerading as a graph, not 'too big to take in'. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

