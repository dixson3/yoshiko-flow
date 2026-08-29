---
type: Finding
okf_spec: OKF-PLAN
---

# EXP-003 — Audit of #269's six claimed `yf-judgement` <-> `yf-retrospective` synergies

## Finding: Do #269's six claimed yf-judgement <-> yf-retrospective synergies hold against what actually landed?

### Approach Tested

Verify against **landed artifacts, not issue text** — #269's claims were written from
#145's *proposal*, and plan-045 landed only part of it. Plus a corpus measurement: all 13
non-worktree `plan-retrospective.md` files across 3 repos, 96 `## RE-NNN` entries, per-field fill
rates; and a re-implementation of `test_close_contract.py`'s §6.4 enumerator.

### Result

**measured:** every figure below is reproduced from the commands named inline; **inferred:** claims are marked as such where no command establishes them.

**Question.** The operator's instruction was to treat #269's six synergies as *"a starting
hypothesis to test and extend, not a finished list"* — to find ones that were missed, and **to say
plainly if any of the six do not hold.**



#### Verdict table

| # | Claim | Verdict |
| :-- | :-- | :-- |
| 1 | Finding 4 ("a manually-invoked skill will not be invoked") is the hardest constraint | **HOLDS — and is proved a third time, inside the artifact #269 wants to inherit** |
| 2 | Independent convergence on the self-report problem | **HOLDS** |
| 3 | `plan-retrospective.md` is a ready-made capture surface | **HOLDS WITH QUALIFICATION** — stronger than claimed on capture, **materially weaker on lifecycle** |
| 4 | The §6.4 step contract already permits `yf-judgement`'s exact shape | **HOLDS WITH QUALIFICATION** — the words are exact, but it is a **close-time** contract and `yf-judgement` fires mid-review |
| 5 | Complementary in time, on the same axis | **DOES NOT HOLD as stated** |
| 6 | Both data-starved by the same shortfall; #145's risks transfer wholesale | **DOES NOT HOLD on "data-starved"; HOLDS on risk transfer** |

#### Claim 5 does not hold, and this is the most consequential result

**The two skills are not complementary in time. They are competing for adjacent hooks in the same
loop — and there is already a landed incumbent occupying `yf-judgement`'s trigger.**

`plan_manager.py review-loop-check` (REQ-CLI-023) **already fires during review cycles** and
already escalates to the operator: exit 3, `stop_class: 4`. Its count is
`len(glob('reviews/pass-*.md'))` (`plan_manager.py:6139`) — **a pure review-pass count, which is
exactly the signal research 005 measures at ρ = 0.739 with plan size.** `yf_attempts >= N` in the
coordinator is a second incumbent, same stop class.

So `yf-judgement` is not entering an empty slot. It is proposing to **replace, wrap, or coexist
with two existing count-based escalators** — one of which research 005 already audited (plan-050's
seven raises, six at cycle ≥ 9, ceremonial not thrash, `Summary.md:1095-1100`).

**#145 said #136, #140 and #145 all wanted "the same missing Phase 6.4 hook." `yf-judgement` makes
it four only if it is close-time — and #269 says it is not.** The honest statement:
`yf-retrospective` competes for the **§6.4 hook**, which has a settled contract;
`yf-judgement` competes for the **§3 review-loop and §5.3 coordinator hooks**, which have **no
settled contract** — REQ-COMPLETE-003 does not reach them.

**And the measured 15 `stop` entries straddle both**: stop classes 2/3/4/5 are raised
mid-execution and recorded at the same site. The two skills touch **the same rows**, not different
phases.

**Consequence for this plan: the real first scoping decision is one #269 does not contain** — does
`yf-judgement` replace, wrap, or coexist with `review-loop-check` and `yf_attempts`?

#### Claim 6's "data-starved" half is stale — the corpus is no longer empty

#145's *"a consumer built now would read an empty corpus; the corpus has to accumulate first"* was
true at **7** backfilled entries. **Measured today: 96 entries across 13 bundles in 3 repos** — 15
of kind `stop` with verbatim asks, 81 `deviation`.

**This materially weakens constraint S4's "not yet" reasoning as applied to the capture surface**
(though not as applied to the detector, which is a separate question). What *is* still starved is
the **adjudication** half:

| field | filled | share |
| :-- | --: | --: |
| `asked` / `answered` / `frontloadable` | 96/96 | **100%** |
| `escape_class` | 9/96 | 9% |
| `prevention` | 9/96 | 9% |
| `origin` | 8/96 | 8% |
| `culpability` | 7/96 | 7% |
| `adjudication` | 5/96 | 5% |

Goodhart and the origin-vs-culpability split transfer as stated. The emptiness claim does not.

#### Claim 3, probed hardest — reuse the FILE, but the lifecycle is missing

**The schema does have a place for an unanswered question, and it was used exactly once.**
`plan-049/plan-retrospective.md:35-51`:

```
| `stop_class` | 1 |
| `asked`      | Authorize the upstream write: 5 comments, CLOSE #135, and create the coarse tracker |
| `answered`   | (pending) |
```

`grep -rn "pending" docs/plans/*/plan-retrospective.md` → **1 hit, corpus-wide. That entry still
reads `(pending)` today.**

The surface can **raise** a question but cannot **close the loop**. `append_retrospective`
(`plan_manager.py:688`) is strictly append-only — a new `## RE-NNN` or the existing id on identity
match. **There is no update path and no `retrospective-update` verb**, and `RE-NNN` ids are
documented as *"append-only and never reused or renumbered."* An escalation's
**`raised → answered → resolved` lifecycle has no representation.**

**Two things #269 understates in the other direction.** (a) `asked` / `answered` / `frontloadable`
are filled **96/96**, and **64/96 `asked` values contain a `?`**. Research 005's *"the corpus
currently records only the answer"* (`Summary.md:1073`) — the basis for calling "record the ask"
the cheapest available instrumentation — **is already ~⅔ discharged by the landed emit side, which
the research did not credit.** (b) `escape_class`, `adjudication`, `origin`, `culpability`,
`prevention`, `cost` **already exist as columns** (`RETROSPECTIVE_FIELDS`, `plan_manager.py:656-660`).

**But those six columns are unvalidated free text**, and drift is already measurable: 9 filled
`escape_class` values yield **8 distinct strings** — one reuse in nine. `kind` and `detected_by`
are `click.Choice`; the other six are `default=""`. **The surface is ready; the vocabulary is not.**

**The class-1 exclusion argument does not transfer, and is already violated in its own corpus.**
`SKILL.md:1888` says stop class 1 is empty *"by construction, not by omission"* because every
class-1 stop is a designed consent gate. The plan-049 entry quoted above **is a class-1 designed
consent gate, recorded anyway** — post-plan-045. More importantly the logic **inverts**: class 1 is
excluded because those asks are *designed and must not be optimised away*. **`yf-judgement`'s
payload is the opposite — an *undesigned* ask arising because the system failed to anticipate
something.** The exclusion is therefore not an obstacle, but neither is it an inherited principle,
and this plan must not present it as one.

#### Claim 1 holds, and is now proved a THIRD time — inside the machinery both skills inherit

Both original proofs verified. `closable`: `skills/yf-beads-upstream/scripts/upstream.py:483-484` —
*"Measured on this repo (991 beads): `closable` produced zero output in 4 minutes and was killed;
only 20 beads had a mapping at all."*

**The new instance is the cleanest one yet.** `skills/yf-plan/scripts/retrospective_fields.py` (the
`prevention_formula` closed-domain checker, plan-052 Issue 5.3 / #196) has a test file, a
`CHANGE-VALIDATION.md` row (`uv-yf-retro-fields`, line 98), a README line, and a
`_shared/document_types/plan-retrospective.toml` check — **and zero callers.**
`grep -n "retrospective_fields\|prevention_formula" plan_manager.py SKILL.md` returns nothing, and
`prevention_formula` appears in **0 of 96** corpus entries. **It is CI-validated,
README-documented, schema-referenced, and never invoked** — finding 4 recurring inside the artifact
#269 proposes to build on.

#### A defect in the "mechanical teeth" #269 inherits uncritically

#145's first comment asserts *"a new escape-capture step that ignores the envelope will fail CI."*
**True only for a step written as `uv run ${SKILL_DIR}/scripts/*.py`.** `test_close_contract.py:98-102`'s
`_INVOKE_RE` requires the literal `${SKILL_DIR}`. Re-implementing the enumerator over the live §6.4
block returns exactly 11 invocations, all `plan_manager.py` / `close_cascade.py` /
`pour_fidelity.py`. **`upstream.py closable` — a real close-time step mandated by
`UPSTREAM_TRACKING.md` — is invisible to it**, because it lives in another skill.

So a `yf-judgement` step following the repo's own cross-skill pattern is enumerated **only if
fronted by a `plan_manager.py` wrapper verb**, the way `yf-change-validation` is fronted by
`validate-merged`. A direct `${JUDGEMENT_DIR}/scripts/…` line **passes CI silently.** #145's "will
fail CI" guarantee is false for exactly the architecture #145 proposes.

#### Six synergies #269 MISSED

1. **The taxonomy has FOUR homes, not two, and the announced mitigation is vapour.** #145 flags
   "two homes for one taxonomy" mitigated by a `yf-drift-check` edge. **That edge does not exist**:
   `grep -i "retrospective\|taxonomy" DRIFT-CHECK.md` returns nothing, and no `e-*` edge in the
   40-edge table covers it. `retrospective_fields.py` is home #3. `yf-judgement` would be home #4.
2. **`yf-herdr` SPEC §3 is a fifth, already-populated deviation taxonomy** — five seed classes with
   cited provenance (`SPEC.md:128-136`), maintained under REQ-HERDR-030/031/033. Its *"Premise
   refuted at execution"* and the corpus's `reasoned-past-a-documented-fact` are **the same concept
   under two strings**. `yf-judgement` is downstream of `yf-herdr`, so this is a direct, unmanaged
   collision.
3. **The batching boundary is already a landed REQUIREMENT, not a new design constraint.**
   REQ-HERDR-026 (`SPEC.md:100-102`) already fixes it to three trigger classes — *"epic completion,
   a blocker/failed gate/halt, and plan completion or abort"* — with an explicit *"shall not push
   per bead."* Research 005's "batch to a boundary; never interrupt per question" **is already
   shipped.**
4. **Forensic attribution is reusable but overkill for live work.** The `bd` epic ↔ plan linkage
   from `record-epic` + `stamp-tracker` (REQ-PLAN-073) answers "which controller owns this content"
   in one lookup. Reserve #145's `git blame → merge-commit` engine for cold, already-landed content.
5. **`yf-research` needs this and has nothing** — and the evidence is **stronger** for
   `yf-judgement` than for `yf-retrospective`. `research_manager.py` exposes exactly **two**
   commands; `grep -ril retrospective skills/yf-research/` returns **zero files**. And #264
   documents that research 005's own subordinate **stalled twice at phase boundaries** — a stop
   event with no surface to record it on. **`yf-judgement` firing in `yf-research` would have
   caught exactly that.** Cheapest place to prove the escalation path works: no legacy to reconcile.
6. **`_shared/document_types/review.toml` is the missing severity anchor for constraint 4.** It is
   already the schema for `reviews/pass-N.md` and already regex-pins the **Verdict** line
   (`APPROVE|REVISE|INVESTIGATE-MORE`) at `R` severity — with a documented, measured rationale for
   why a review-pass schema **cannot** carry a promotable severity (it is authored while the plan
   sits at `review`, where `STATUS_SEVERITY` promotes `W → E`). **A finding-severity check belongs
   here, at `R`, and inherits a settled answer to a question that would otherwise be re-litigated.**

#### Five ANTI-synergies — where building both creates a problem

1. **Two skills, one write verb, no update path.** Both emitting `## RE-NNN` share one append-only,
   non-updatable stream. `retrospective-report`'s aggregation (`by_kind`, `by_stop_class`) has no
   way to exclude open escalations from an escape count — **an unanswered question would be counted
   as a recorded event.**
2. **`review-loop-check` vs a `yf-judgement` detector is a direct trigger conflict.** Both fire in
   §3 on review-pass accumulation. `max_review_cycles` defaults to 5, so under the incumbent a plan
   escalates at 5 passes anyway. **`yf-judgement`'s detector buys 2 passes at best, on a signal
   silent on 68% of the corpus.**
3. **Goodhart compounds asymmetrically, and the new pressure is NEW rather than inherited.** #145's
   actor has no escape hatch. **`yf-judgement`'s does** — an agent that can escalate instead of
   finishing has an incentive to reclassify difficulty as under-specification. #269 names the risk
   but calls it inherited; it is not.
4. **`EXEMPT_VERBS` is a closed 3-name frozenset guarded by `test_exempt_list_has_no_dead_entries`.**
   Two skills each adding a §6.4 step means two edits and two hard CI events. Sequence it (one skill
   lands the hook, the other attaches) rather than discovering it.
5. **`plan-retrospective.md` is presence-optional and its absence *"is never an audit finding"***
   (`plan_manager.py:645`). **A `yf-judgement` that treats it as a durable escalation queue builds
   on a surface the audit is contractually forbidden to require.**

#### Absence findings

- **"Four completed plans shipped non-conformant files"** (#145 finding 4's second proof): the
  mechanism is verified and the fix landed as `audit-close`, but **no repo artifact states the
  number four.** Uncorroborated.
- **Whether the 96 entries reflect compliance or a same-repo author effect.** All 11 yoshiko-flow
  bundles plan-045..plan-055 carry a retrospective; d3-pxe plans 016/017/018 landed the same day as
  `18f3959` with none, the first appearing eight days later. **Confound not removable:** skill-deploy
  timing to that clone is unknown, so this may be a deploy artifact rather than a compliance one.
- **Whether `yf-judgement` fires at §3, §5.3, or both.** #269 says "during review cycles", which are
  §3 (pre-pour, no beads exist) and §5.3 (post-pour, beads exist). These have **structurally
  different instrumentation** — `plan_manager.py:6134-6136` says the bd-metadata route *"structurally
  cannot reach"* the glob-count route. **The answer changes claim 5 materially and #269 does not
  contain it.**
- **Recall of any detector** — never measured, as #269 itself states.

### Implications for Plan

**The real first scoping decision is one #269 does not contain**: does `yf-judgement` replace,
wrap, or coexist with `review-loop-check` and `yf_attempts`? Claim 5's failure makes that
unavoidable.

**`plan-retrospective.md` is reusable as a capture surface and unusable as an escalation queue.** The
distinction decides whether this plan adds an entry kind or a sibling file.

**The taxonomy problem is larger than #145 states** — four homes, and the promised mitigation edge
does not exist.

### Recommendations

1. **Restate claim 5 honestly, or drop it.** The two skills compete for adjacent hooks.
2. **Reuse the file, but ship an update verb** — or route escalations elsewhere.
3. **Make "pin the vocabulary" the first epic, for four homes rather than two**, and give
   `escape_class` a `click.Choice` the way `detected_by` has one.
4. **Wire or delete `retrospective_fields.py` in the same change-set.** Leaving it is worse than
   either.
5. **Fix the enumerator's cross-skill blind spot before adding a cross-skill step**, or mandate the
   `plan_manager.py` wrapper-verb pattern.
6. **Add `yf-research` to scope as a stated hypothesis** — #264's twice-stalled subordinate is the
   concrete instance and there is no legacy to reconcile.
