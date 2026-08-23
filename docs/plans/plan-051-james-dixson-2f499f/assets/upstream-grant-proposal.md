---
type: Reference
okf_spec: OKF-PLAN
id: upstream-grant-proposal
description: The full upstream write grant for plan-051 — every issue, every comment body verbatim, every close
---

# Upstream write grant — plan-051

**Generated from `plan_manager.py grant`'s enumeration**, not from a prose list. Reconciled
against `plan.md`'s Upstream Issues table **before** the gate is presented:

| | |
| :-- | :-- |
| grant rows **with actions** | `149, 150, 165, 173, 174, 182, 184` |
| table rows `include`/`partial` | `149, 150, 165, 173, 174, 182, 184` |
| **reconciled** | **yes — exact match** |
| grant rows with **no** actions | `145, 177, 188, 190` (`exclude` / `deferred` — no upstream action) |

All five `partial` rows get a comment. That is not stylistic: `_verify_row` maps `partial` →
`requires_mention: True` and returns `fail: "no comment mentions <plan_id>"` otherwise, and
`verify-reconcile` runs at **4.4 — after the outward writes have begun**.

**Total: 7 comments, 2 closes. Nothing else.**

---

## 1. `gh issue comment 182` — then `gh issue close 182`

> **plan-051 lands this — as a narrowing, not as the issue framed it.**
>
> **The issue's premise is not what the tree said.** The body states the rule "is drawn as
> *`never write, edit, or create any file`*". `skills/yf-plan/agents/red-team.md:63` said only:
>
> > Read-only — never writes files.
>
> It never forbade building something in a scratch directory and running it. The prohibition was
> a *reasonable reading of silence* — so the defect is **under-specification, not a wrong rule**,
> and the fix is a clarification rather than a reversal. Recording that matters: closing this as
> if the stronger framing were accepted would leave the next attempt rebuilding from a premise
> the tree does not support.
>
> **What landed.** `REQ-AGENT-043` and `REQ-AGENT-045` now scope read-only to **the repository
> under review** and explicitly authorize a sandbox spike outside it, leaving no residue.
> `reviewer.md` is in scope alongside `red-team.md`: it carried the identical sentence, and
> rewording only one would leave the two agents contradicting each other on one constraint.
>
> **The edit set was 7 files, not one.** An investigation measured the minimum consistent set at
> **7** (8 with the reviewer sibling) against the "one line in one file" estimate. Three of those
> sites have **nothing mechanical** behind them — measured directly: the FAST validation tier runs
> **zero** commands for all three `web/content/**` paths. Every site is enumerated with a stated
> disposition, including five explicit **NO-EDIT** rows, in the plan's `assets/edit-set-182.md`.
>
> **The dangling-pointer state is now catchable.** Rewording an agent file while the spec still
> pins the old string was invisible to every engine in the repo — the FAST tier returned
> `pass, first_failure None` on it. Two things fix that: a new `DRIFT-CHECK.md` edge
> **`e-spec-agent`** (`spec` → `agent`, spec is fixed authority), and a `CHANGE-VALIDATION.md`
> row **`uv-yf-review-agent`** registered on **both** sides of the pair, so amending either
> without the other fails at the point of change.
>
> **Verified:** the retired literal survives at **zero** tracked sites
> (`git grep -c 'Read-only — never writes files' -- ':!docs/plans' ':!docs/research'` → no
> matches). A control, `ctl-182-spike`, was observed **RED before the fix and GREEN after**, with
> both observations on record.
>
> Closed by plan-051-james-dixson-2f499f (Issues 1.2, 1.2a).

**Close command:** `gh issue close 182`

---

## 2. `gh issue comment 184` — then `gh issue close 184`

> **plan-051 lands this.**
>
> **The RED was measured before the fix.** `Agent` appeared **0 times across all 7
> `skills/yf-plan/agents/*.md`**, and the section-scoped check
>
> ```bash
> awk '/^### Review$/{f=1} f&&/^### Portability audit/{f=0} f' skills/yf-plan/SKILL.md | grep -q 'Agent'
> ```
>
> exited **1** on the pre-fix tree and **0** after. The scoping is load-bearing: the **whole-file**
> form `grep -q 'Agent' skills/yf-plan/SKILL.md` exits **0 on the unfixed tree**, because `Agent`
> sits at `SKILL.md:21` in the frontmatter `allowed-tools:` list — so a whole-file control would
> have shipped **unable to fail**.
>
> **What landed.** A new **`REQ-AGENT-049`**: the adversarial pass **shall be dispatched as a
> sub-agent**, not performed by the main session. `SKILL.md` §3 step 2 now spawns a sub-agent
> reading `agents/red-team.md`, mirroring the §2 INVESTIGATE form; the REVISE path re-**dispatches**.
> "Two passes, in order" is unchanged — the conformance → adversarial ordering is the same; what
> changed is *who runs* the adversarial pass. The main session remains the sole writer of
> `reviews/pass-N.md` and the `log.md` `review-pass:` bullet.
>
> **What this does NOT claim.** The requirement constrains the **text** that specifies dispatch,
> never reviewer conduct. That a pass was genuinely dispatched has no exit code, and the control
> does not pretend to verify it — a text-presence control is in principle gameable by the token it
> checks for. The control's value is that it **distinguishes before from after**. It is hardened
> against the two obvious gaming vectors: measured, a bare-token check is green on both
> `<!-- Agent -->` and *"Do NOT use the Agent tool here"*, so the check additionally requires the
> imperative dispatch form.
>
> **Counter-evidence, recorded rather than omitted.** Eleven independent red-team passes on
> plan-050 found **none** of the three defects that *running a control* found during its execution.
> Independent review is a large improvement over self-review; it is not the strongest lever
> measured. This ships the improvement the evidence supports and does not overclaim it.
>
> Closed by plan-051-james-dixson-2f499f (Issue 2.2).

**Close command:** `gh issue close 184`

---

## 3. `gh issue comment 149` — stays OPEN (`partial`)

> **plan-051 corrects the record on M9. The issue's premise is refuted; M9 itself stays open.**
>
> **Re-measured against the live bead DB for this comment, not quoted from a prior plan:**
>
> | Figure | Value |
> | :-- | --: |
> | `discovered-from` edges | **26** |
> | of those, attributed on **either** endpoint | **0** |
>
> So **the relationship exists and only the attribution is missing.** The issue's framing — that
> remediation edges "exist only in prose" — is wrong in the direction that matters: the edges are
> real and machine-readable; what no edge carries is *why* the work was discovered.
>
> **The "one seam" recommendation does not survive measurement either.** `--deps
> discovered-from:` is instructed by **prose in 12 sites across 10 files in 4 skills**
> (`yf-beads-authoring`, `yf-beads-extra`, `yf-plan`, `yf-research`), and **no script creates
> one** — every script-side hit is *reading* or classifying an existing edge. So there is no
> single seam to stamp at, and a stamping rule added to prose would be **M5 vacuity inside the
> fix for M5**.
>
> **And the host cannot express the detector's contract.** M9's designed remediation was an
> exit-2 `INCONCLUSIVE` row in `CHANGE-VALIDATION.md`. Measured at source —
> `skills/yf-change-validation/scripts/change_validation.py`, `run_command` — that engine emits
> `inconclusive` **only** when the command's first token is absent from `PATH`; a command's own
> return code maps `0 -> pass` and **everything else -> `fail`**. An exit-2 row therefore reports
> `fail`, not `inconclusive`. Since the row's `cmd` starts with `uv`, a clone or CI runner without
> `.beads/` breaks the tier outright. So M9 is not merely unbuilt: the host it was to be wired into
> **structurally cannot carry its contract** — which is why this needs a different shape rather
> than a patch (**plan-050's pass-5 C40**, re-verified at source by plan-051).
>
> **Scope:** this is a correction comment only. M9's substance is **out of scope** for plan-051
> and this issue stays open.
>
> — plan-051-james-dixson-2f499f (Issue 4.2)

**⚠ OPERATOR DECISION — see "One open question" below.**

---

## 4. `gh issue comment 165` — stays OPEN (`partial`)

> **plan-051 delivers this narrowly: its own new/amended `Verification:` lines are executable.
> The corpus-wide sweep stays open.**
>
> **The census, recorded with its verbatim pathspec** — because the figure is meaningless without
> the command, and two prior reconstructions (251, 257) disagreed with no way to resolve them:
>
> ```bash
> # from the repo root
> git grep -h '^Verification:' -- '*.md' ':!docs/plans' ':!docs/research'    # -> 221
> ```
>
> The earlier 251/257 divergence is now **explained**: the recursive `grep` form that includes
> **untracked** files returns **256** and drifts run to run. `git grep` removes that instability.
>
> **A definitional correction to the "1 of 251" figure.** Under the definition that matters here —
> *the whole `Verification:` line is a single runnable command* — the pre-plan corpus count is
> **0**, not 1. The known instance (`REQ-CLI-006`) closes the loop by **naming a CV-registered
> test**, while the clause itself is prose containing inline code spans. Both figures are correct
> under their own definitions; the disagreement is definitional, not an error in either.
>
> **Two `Verification:` commands are FALSE today in a FULL-tier-green tree** — hand-run from the
> repo root:
>
> | Site | Command | Exit |
> | :-- | :-- | --: |
> | `skills/yf-optimal-instructions/spec/integration.md:51` | `ls skills/optimal-instructions/protocols/` | **2** — stale path; the real one is `skills/yf-optimal-instructions/protocols/` |
> | `skills/yf-research/spec/prerequisites.md:42` | `grep -r 'docs.astral.sh\|gastownhall/beads' .agents/skills/yf-research/` | **2** — `.agents/skills/yf-research/` does not exist |
>
> These are evidence for this issue, not work items in plan-051.
>
> **What landed.** Three `Verification:` lines — `REQ-AGENT-049`, `REQ-AGENT-043`, `REQ-AGENT-045`
> — are now whole-line backticked commands that **exit 0 from the tree root**, each conjoining a
> real test with `grep -qF` literal/path pairs. They are the corpus's first whole-line-executable
> clauses. The test is registered as `uv-yf-review-agent` on **both** sides of the spec↔agent pair.
>
> **Non-rottability is demonstrated, not asserted.** On a throwaway tree: **renaming** the test
> makes all three REQ cases fail; **deleting** it makes the `Verification:` command exit 2;
> **rewording one** REQ's line fails **exactly that one** case. This works only because the test's
> self-reference is *derived* from its own filename rather than hardcoded — a hardcoded literal
> would stay green after a rename, asserting that the spec names a test that no longer exists.
>
> **Honest limitation.** Because the SPEC-first step fixed the line's *shape* first, this control
> never observes the "prose shaped like a command" defect in the wild; it observes the absence of
> the named test. The corpus-wide sweep — the other 218 clauses — remains this issue's.
>
> — plan-051-james-dixson-2f499f (Issues 3.1–3.3)

---

## 5. `gh issue comment 173` — stays OPEN (`partial`)

> **plan-051 closes two worked instances; the general cross-check stays open.**
>
> `#182`'s and `#184`'s requirements are now checked against the surface that enforces them, in
> both directions: `CHANGE-VALIDATION.md`'s `uv-yf-review-agent` row fires on **both**
> `skills/yf-plan/spec/agents.md` and `skills/yf-plan/agents/*.md`, and a new `DRIFT-CHECK.md`
> edge `e-spec-agent` declares the spec fixed authority over the agent prose it quotes.
>
> Verified as **two separate single-path invocations**, never one two-path run — a single run over
> both paths demonstrates only the *union* and is satisfied when just one glob matched.
>
> **What stays open:** the general mechanism — criteria and dispositions checked against the
> engine that enforces them, across the corpus. These are two instances, not the rule.
>
> **One datum for this issue, found by executing this plan.** A criterion of plan-051's own
> (`SC4b`) was measured green at the issue that discharged it and was **false by two epics later**:
> a file added downstream matched its pattern. Nothing re-checked it — the plan's end-state
> mandate covered only the criteria that had *fixtures*. It was caught by an operator
> re-measurement, not by any mechanism the plan shipped. **A criterion is only as good as the last
> time something re-ran it**, which is close to the substance of this issue.
>
> — plan-051-james-dixson-2f499f (Issue 4.2)

---

## 6. `gh issue comment 174` — stays OPEN (`partial`)

> **plan-051 closes a named sub-case; the general falsification pass stays open.**
>
> `#182` is the sub-case: **the spike is the technique that catches what reading cannot.**
> `REQ-AGENT-043`/`-045` now authorize a sandbox spike explicitly, so the technique that produced
> the evidence for this issue is no longer forbidden by a reading of silence.
>
> Executing the plan produced three first-party instances of the same principle:
>
> - a fixture's own guards were spiked before any RED was recorded, and the spike proved the
>   fixed/dangling arms both behave — one arm alone is satisfied by a control that is
>   unconditionally non-zero;
> - a vacuity guard **failed on the very first run** of a new test and caught a real parser defect
>   that made every spec block parse **empty** — the three parameterized cases would have been
>   asserting against empty strings;
> - a rename-arm spike showed a hardcoded self-reference keeps a meta-assertion green after the
>   file is renamed.
>
> All three were found by *running* something, and none by reading it.
>
> **What stays open:** the general review-phase pass that falsifies **every** criterion.
>
> — plan-051-james-dixson-2f499f (Issue 4.2)

---

## 7. `gh issue comment 150` — stays OPEN (`partial`)

> **plan-051 delivers two more ranked classes as worked instances.**
>
> - **M5 — process rules that nothing executes.** Three `Verification:` clauses are now whole-line
>   commands that run, registered in the validation manifest on both sides of the pair they check.
>   Measured: under that definition the pre-plan corpus count was **0**, against a census of
>   **221** clauses (pathspec recorded).
> - **The self-reference class.** A checker became a member of the set it measured: a new test
>   file quoted the very phrase its criterion greps for, taking the hit set out of subset. Resolved
>   by *enumerating* it as an explicit NO-EDIT row with a stated "quote-to-forbid" disposition —
>   the same distinction this repo already ratified in `REQ-BUP-053`/`GR-BUP-005`. Narrowing the
>   pathspec to make the criterion pass was considered and **rejected**.
>
> **What stays open:** M9, the M11 probe mechanism, and the remaining ranked classes.
>
> — plan-051-james-dixson-2f499f (Issue 4.2)

---

## The C40 question — ANSWERED by the operator, folded in

Issue 4.2's *"plus C40"* referent is **plan-050's pass-5 C40**, not this bundle's. plan-051's own
`reviews/pass-4.md` C40 is an unrelated path-qualification nit; plan-050's is a **high, injected
concern explicitly deferred to plan-051**, named in `handoff-051.md` §5 as this plan's starting
evidence. It is folded into comment 3 above.

**It is cited path-qualified — "plan-050's pass-5 C40"** — never as a bare `C40`. An unqualified
id in a comment that outlives both bundles reproduces exactly the ambiguity that cost a gate stop
here. This plan's own pass-1 **C18** established the path-qualification rule for `SPEC.md`
citations; this is the same class on a different axis.

**Re-verified at source before publication** rather than taken on the review record:
`change_validation.py` `run_command` sets `inconclusive` **only** under `if not tool_on_path(tok)`
(:781–783), and the normal path is `"status": "pass" if proc.returncode == 0 else "fail"` (:797).
Exit 2 → `fail`. Confirmed.
