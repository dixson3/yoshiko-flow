---
type: Finding
okf_spec: OKF-PLAN
---

# EXP-001 — Does a reliably-firing automatic trigger point exist?

## Finding: Does a reliably-firing automatic trigger point for `yf-judgement` exist?

### Approach Tested

Enumeration of every candidate firing surface; direct inspection of the runtime hook
surface (`~/.claude/settings.json`, `.claude/settings*.json`, `.git/hooks/`,
`git config core.hooksPath`, `.beads/hooks/`, `.github/workflows/`); two natural experiments; a
sandbox spike over a copy of plan-048 in `$(mktemp -d)` (log verified byte-identical after, no
residue); a query over all 1,245 beads in `.beads/issues.jsonl`; and a machine-readability
measurement over all 175 `reviews/pass-*.md` files.

### Result

**measured:** every figure below is reproduced from the commands named inline; **inferred:** claims are marked as such where no command establishes them.

**Question.** Constraint S1 says the trigger is the design, and that "no reliable trigger exists"
is a legitimate plan-terminating answer. This experiment was dispatched to an isolated agent
precisely so it could return that answer against the interest of the session that commissioned it.



#### Verdict

**No reliably-firing automatic trigger point exists — and the plan does not terminate anyway.**

Both halves are load-bearing.

**The negative half is absolute.** The yf system contains **zero** `PostToolUse` / `PreToolUse` /
`FileChanged` hooks, **zero** installed git hooks (`.git/hooks/` is `.sample`-only,
`core.hooksPath` empty), and exactly one Claude Code hook on the machine — a `SessionStart` shim
that self-gates on `HERDR_ENV=1` and does nothing yf-related. `yf-beads-init` is an **anti-surface**:
it *deliberately removes* hooks (`skills/yf-beads-init/SKILL.md:174-176` — "repair **never installs**
beads git hooks … Repair only ever *removes* hooks"). The three GitHub Actions workflows are
genuinely mechanical but run `cargo fmt/clippy/test` only — they never invoke
`change_validation.py`, `doc_lint.py`, or any `uv` row.

**So every on-edit, pre-push and close-time trigger in this system is prose an agent must choose to
obey — including the four that read as mechanical.** `yf-change-validation`'s FAST tier and
`yf-drift-check`'s on-edit dispatch are not a second class *distinct from* the prose rules; **they
are the prose rules.** Both root manifests are `approved: yes` with large precise glob tables,
which makes the surface look mechanical on paper. Nothing in the runtime reads those globs on an
edit. `DRIFT-CHECK.md:23` claims *"The engine enforces this manifest"* — **there is no enforcement
mechanism.**

**The positive half is a distinction nobody in this plan's premise had drawn.**

#### The measured discriminator is NOT prose-vs-mechanical

It is **"prose that names a command" vs "prose that names an obligation."** Measured on the *same
event, same session, same author* — `review-loop-check` escalating at the bound, which is recorded
twice, once by the script itself (`okf.append_log` inside `plan_manager.py:6172`) and once by a
prose instruction (SKILL.md's "Write sites" table):

> **THE NUMBERS IN THE TABLE BELOW ARE SUPERSEDED.** Five red-team passes corrected them: the two
> prose rows compared different **units**, then different **populations**, and the population
> sentence was then stated falsely. **The current derivation is 12/12, 4/5, 2/5 over the five
> post-plan-045 plans exceeding the bound** — see `findings/finding-command-vs-obligation.md`, which
> records all four drafts rather than replacing them. The rows below are kept as this experiment
> reported them, because a correction is only legible against what it corrected.
>
> *This banner failed to land three times before it was verified against the file rather than
> against the bookkeeping — which is the defect it annotates, committed while annotating it.*

| Recorder | Rate | Evidence |
| :-- | --: | :-- |
| **Script writes it itself** | **15 / 15 (100%)** | `grep -h "autonomy: max-review-cycles raised" docs/plans/*/log.md` → 15, across plan-050 (7), 055 (2), 052 (1), 054 (2), 056 (3) |
| **Prose instructs an agent to RUN A COMMAND** | **5 / 6 (83%)** | of the 6 post-plan-045 plans that crossed the default bound of 5, five ran `review-loop-check`; plan-048 did not |
| **Prose instructs an agent to HONOUR AN OBLIGATION** | **2 / 12 (17%)** | 12 escalations in completed plans → 2 `stop_class: 4` retrospective entries. plan-054 had 2 escalations and wrote 7 entries, **none** with `stop_class: 4`; plan-055 had 2 escalations and 2 entries, neither one |

**A factor of five, on one event, with the confound of author, session and task removed.** This is
the single most useful number the experiment produced and it is not in research 005.

The skipped case is dated: **plan-048 ran 7 review cycles on 2026-08-19 with zero echoes — one day
after `review-loop-check` landed** (`2bc2228`, 2026-08-18). The spike confirms what it would have
returned:

```
$ uv run plan_manager.py review-loop-check <copy-of-plan-048> --json
{"escalates": true, "cycles": 7, "limit": 5, "stop_class": 4, "autonomy": "autonomous", ...}
EXIT=3
```

That escalation was available at cycle 6 and was never asked for.

#### The corpus's own verdict on prose, quoted

`docs/plans/plan-043-james-dixson-a8afe8/findings/exp-001-reconcile-skip-cause.md:105-117`:

> **The verification step already exists as prose, and was skipped in the same breath.** … Step 4
> **is** the post-reconcile verification the plan intends to add. It was ignored exactly as step 3
> was. **Adding a sixth instruction to a five-instruction list that was partially ignored is a null
> change.**

`docs/plans/plan-052-james-dixson-fa8056/references/upstream-197.md:25-35` — first-party, and it
names this plan's three most attractive candidate surfaces **by name**:

> - doc_lint: classify -> lint -> resolve every E finding, on any edit under the typed roots
> - yf-change-validation: FAST tier on any path matching an approved manifest's §3 globs
> - yf-drift-check: report-only dispatch on any path matching an approved manifest's §6 globs
>
> Each is a paragraph. **None is a thing that must be CLOSED.**
> … a verification bead is a thing that must be closed; **a prose instruction is a thing that can
> be believed to have been followed.**

`docs/research/004-plan-process-defect-mining/Summary.md:41-52`: *"a written rule that nothing
executes is **unreliably** obeyed, and no exit code records the skip … **a step with no exit code
is not a step**."*

**Evidence in the other direction — prose is unreliable, not broken.** plan-040 and plan-041,
*"same prose and same table shape, reconciled correctly … Same instructions, different outcomes —
**the definition of an unenforced contract**"* (`plan-043/findings/exp-001:124-131`). And
plan-048's retrospective records a prose authorization boundary **obeyed at cost**: a subordinate
*"refused … and halted, blocking completion. … The refusal was CORRECT."*

#### The concerns table cannot carry the trigger

Measured over all 175 `reviews/pass-*.md`:

| Signal | Availability | Note |
| :-- | :-- | :-- |
| pass-file **count** | **175/175 (100%)** | it is a glob; cannot fail |
| `## Verdict:` line | 151/175 (86%) corpus-wide, **100% from plan-024 onward** | all 24 misses predate `REQ-PLAN-071` |
| `## Concerns` section | 160/175 (91%) | |
| a parseable concerns **table** | **80/175 (46%)**, in **5 incompatible header shapes** | |
| severity vocabulary | **unnormalised** | `low` 208, `high` 193, `medium` 169, **`med` 110**, plus `low-medium`, `high, blocking`, `medium-high`, `med-high`, `low-med`, and 40+ free-text strings where column 2 is not a severity at all |

This independently reproduces research 005's `[104]` (severity vocabulary unnormalised) and `[105]`
(8 multi-pass bundles extract zero findings, invisible to the detector by construction), from a
different direction and a different measurement.

**Consequence: any predicate reading concern severities reads a 46%-coverage, 5-schema,
unpinned-vocabulary surface.** The verdict line (100% modern) and the pass-file count (100% by
construction) do not. **Build on those two; do not build on the findings table.**

#### Stop class 4 is not redundant with yf-judgement — it is exactly #264's defect

The review-loop boundary already halts mechanically-enough (5/6 *(superseded — now 4/5; see the banner above)*). **What is missing is not
detection. It is that the halt does not ASK.** The `remediation` string the script emits offers two
options and names no upstream party. What turned plan-052's escalation into a *question* was a human
writing `asked:` into a retrospective afterwards — 2 times out of 12.

The shape this plan wants already exists once, at
`docs/plans/plan-052-james-dixson-fa8056/plan-retrospective.md:23`:

> `| asked | review-loop-check reached the configured max_review_cycles bound of 5 with the last
> red-team verdict still REVISE. Raise the bound for one confirming pass, or override the verdict
> and approve? |`

**The mechanism reliably stops; the asking is prose, and the asking is the 17% half.** That is the
silent-idle defect precisely: an agent that halts at 5/5 and waits, with the question living only
in the drafting conversation.

#### Two surfaces the plan's premise did not have

**1. `plan-review.formula.toml` — the only structurally mechanical mid-burn boundary in yf, and it
has never been used.** `skills/yf-plan/formulas/plan-review.formula.toml:63-70` carries a
`type = "gate"` step with `type = "human", approvers = ["operator"]` — a bd gate that *structurally
holds* until an operator resolves it, at the end of **every** cycle, not only at cycle 5.

Measured against all 1,245 beads: **zero** beads titled "Conformance review", "Adversarial review",
"Resolve concerns" or "Review verdict gate". The formula landed 2026-08-24 (`57a21e3`, plan-052
Issues 5.1/5.3) and **not one wisp has been poured since.**

**State the counting basis with the number.** This experiment reported **33** — pass files *present
in the working tree*, including bundles still untracked at measurement time. The operator
independently measured **27** — review passes *added to git* (`git log --diff-filter=A`). Both are
correct on their own basis and **the claim is unaffected at either**; the plan uses **27 (git-added)**
as the citable figure. A third figure, 552, was produced by an mtime-based count and is **wrong** —
creating three worktrees that day reset every file's mtime, so it measured the measurer's own action.

**This experiment's scope decision:** escalation E-3 resolved — making the wisp pour is **out of
scope for plan-059**, filed as **#270**. This plan binds to `review-loop-check` and designs the
escalation payload so it can move onto the wisp later **without redesign**; #270 records that
fixing the formula upgrades this trigger for free, which is why the weaker trigger is acceptable
now. **That seam must stay clean and named.**

**This is #145 finding 4 recurring on the very mechanism that would fix it** — and the formula's own
comment anticipates the wrong failure, declining to put the counter in the wisp because *"a wisp is
EPHEMERAL AND BURNABLE"*. It worried about the counter; it did not worry about whether anyone would
pour it.

**2. `yf-herdr`'s token stamp is the C3-clean execution-side signal.** A stamp that has not advanced
across N epic-boundary polls is second-party residue about a stuck subordinate, with no self-report
involved, and `REQ-HERDR-026` already batches it to a boundary (*"Never per bead — a plan-sized DAG
would emit tens of messages and flood the parent's context"*). The repo already learned the push
itself is an unverified claim: `SKILL.md:149` — *"`agent_prompted` acknowledges INJECTION, NOT
SUBMISSION. One measured push returned success and was never submitted."* The **stamp** is the
verification.

#### `yf_attempts` is struck from the candidate list

Measured: 13 distinct metadata keys are exported across 1,245 beads. **`yf_attempts` is not among
them — zero occurrences.** Its only hits anywhere in `.beads/` are 4 lines in `interactions.jsonl`
from the plan-045 development conversation *describing the design*. Metadata export demonstrably
works, so this is not an export artifact. **Stop class 4's execution arm has never fired in the
recorded history of the repo.**

It is disqualified three ways: **(a)** it is prose — `coordinator.md:83-88` instructs the *agent* to
write the key; no script does. **(c)** it is a **controller self-report**, forbidden by consensus
C3 — `coordinator.md:98` says *"Increment ON DETECTED FAILURE"*, and an agent that does not detect
its failure does not increment. This is the unreliable narrator counting their own mistakes.
**And on evidence:** it has never been written.

#### Aggregate `detected_by` across all 81 retrospective entries

| `detected_by` | count | share |
| :-- | --: | --: |
| `mechanical-check` | 47 | 58% |
| `operator` | 22 | 27% |
| `self-report` | 12 | 15% |

Self-report is the smallest bucket — consistent with C3 rather than a refutation of it. **Caveat:
11 of 57 bundles carry a retrospective at all, all from plan-045 onward, so this is a
post-mechanisation rate, not a corpus-wide one.**

#### Absence findings

- **Whether the on-edit prose triggers actually fire, and at what rate, cannot be determined.** They
  leave no durable per-invocation artifact, so there is nothing to count. This is an absence of
  *record*, not a demonstrated absence of firing. `review-loop-check` was measurable **only because
  the script writes its own echo — an accident of design, not a general property.**
- **Why plan-048 skipped the check is unrecorded.** That it did not run is established; the cause
  (session boundary, operator instruction, agent omission) is not.
- **Why the `plan-review` wisp has never been poured is unrecorded.**
- **Whether the coordinator's step-6 FAIL branch has ever executed cannot be distinguished** from
  "no bead ever failed its postcondition" on this evidence.
- **Whether escalating one cycle earlier would have changed any outcome** is the counterfactual
  research 005 §8.4 already marks *"untestable from this corpus."* This experiment did not test it
  either.
- **Whether prose-trigger reliability differs between the main session and sub-agents** — nothing in
  the artifacts distinguishes who skipped.

### Implications for Plan

**The premise "the trigger points ARE the design" is correct, and stronger than stated.** No
mechanical trigger exists anywhere in yf, so whatever `yf-judgement` binds to, it binds to prose —
the only question is *which* prose, invoking *what*.

**The plan does not terminate, but it must design for a measured 17% failure mode rather than assume
it away.** `review-loop-check` is the best available surface at 5/6 *(superseded — now 4/5; see the banner above)*, and plan-048 is the
counterexample, one day old relative to the mechanism.

**Two candidate surfaces are struck** — `yf_attempts` (never fired, prose, self-report) and the
concerns table (46% coverage, 5 schemas). **Two are added** — the `plan-review` wisp gate (out of
scope, #270) and `yf-herdr`'s token stamp (the only execution-side candidate passing all four
discriminators).

### Recommendations

1. Answer the trigger question as **"no — but a measurably best one exists, at 83%, and its 17%
   failure is a design input."**
2. **Extend `review-loop-check`** rather than adding a slash command: an existing path at 5/6 *(superseded — now 4/5; see the banner above)* versus
   a fresh path at 0.
3. **Build the predicate on the verdict line and the pass-file count**, never on the concerns table.
4. **Make the raised question a bead or a script-written artifact, never a paragraph.**
5. Add `yf-herdr`'s token stamp as the execution-side signal.
6. **Pin the severity vocabulary regardless of what the plan decides about the detector.**
