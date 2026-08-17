---
type: Research Artifact
cluster: yf-corpus
research: 004-plan-process-defect-mining
method: direct
retrieved: '2026-08-16'
okf_spec: OKF-RESEARCH
---

# Cluster `yf-corpus` — retrieval findings

Corpus: `~/workspace/dixson3/yoshiko-flow` — 43 plan bundles under `docs/plans/*` plus
research bundles under `docs/research/*`. Method: DIRECT (filesystem, `git`, `bd`). No web leg
(`plan.yaml` `exclusions`). Extractor: `scripts/remediation_pairs.py pairs --repo yoshiko-flow`
→ 45 candidates, every one an INFERENCE requiring confirmation against both bundles.

## Standing caveat — self-selection

**This repo is the skill fixing itself.** Every plan here exists *because* a defect was
noticed, and several plans exist specifically to build defect-detection machinery. The defect
population is therefore self-selected twice over: once by noticing, once by the corpus being
the tool's own development history. A class found only here is **not** evidence of a general
process defect — it is evidence that yoshiko-flow's authors were looking for that class. Only
corroboration from `cross-repo-corpus` upgrades any class below from "observed in the
self-referential corpus" to "recurring". This caveat applies to **every** finding on this page
and is not repeated per-section.

A second, subtler self-selection: the corpus is unusually *articulate* about its own defects.
Later plans in this repo write explicit post-mortems into their Motivation sections
(plan-040's "a mechanism nobody chose", plan-043's E1). That richness is why this cluster
yields deep findings — and is itself a property of the repo, not of planning generally.

## Confirmed remediation pairs

### F1 — plan-038 → plan-040: enforcement built on an unexamined inherited premise

plan-038 made `upstream.py push` the single documented write path and hardened everything
around `bd <backend> push`. plan-040, one plan later, established that the mechanism
underneath had never been chosen at all.

> "**The write path depends on a mechanism nobody chose.** Every upstream write shells out to
> `bd github push` (≡ `bd github sync --push-only --issues`). #133 establishes that this was
> never justified anywhere in the repo — `SPEC.md` presupposes it (REQ-BUP-030/031) without
> arguing for it. It was inherited because bd 1.0.5 happened to ship the feature." [1]

Worse, the one capability that would justify the dependency was forbidden by the skill's own
central invariant:

> "The skill's central safety invariant, **GR-BUP-001** (REQ-BUP-030), is *\"never run a bare
> `bd <backend> sync`\"* — so the dependency is retained and then deliberately disabled from
> doing the only thing that justifies it." [1]

**Process defect.** plan-038 assumed the mechanism; no review pass in the corpus at that date
asked *"is this dependency justified?"* — both the conformance and red-team passes reason
about a plan's internal coherence. plan-039 (one plan earlier) had just diagnosed exactly this
gap and shipped a premise-verification prompt for it (#114) [8] — but a premise verifier fires
on *findings the plan states*, not on *dependencies the plan silently inherits from the
codebase*.

**Hindsight bar.** A stated, checkable step **could** be written and partly was: plan-039's
#114 premise-verification prompt. It would not have caught this one, because the premise was
never written down as a finding. Verdict: preventable only by a *new* check ("name and justify
every external tool dependency your change path relies on"), not by an existing one. Recorded
as prescriptive, not as a review escape.

### F2 — plan-038 → plan-040: a verb shipped that cannot run at this repo's scale

plan-038 shipped `closable`. plan-040 measured it:

> "**`closable` produced zero output in 4 minutes and was killed** **[measured]**. From an
> operator's seat, indistinguishable from a hang." [2]

> "**Cause is a removable N+1** **[measured]**: `cmd_closable` loads all rows in one
> `bd list --all --json`, then calls `external_for(id)` per row — a fresh `bd show` subprocess
> each — across **991 beads**." [2]

Corroborated live: this cluster's own `bd list --all --json` on the same DB returns **1072**
beads today [uncited — direct observation, `bd list --all --json | len` = 1072, 2026-08-16].

**Process defect.** The acceptance criteria for a new verb checked *shape* (does it emit the
right proposal) and not *runnability at production scale*. This is the same shape as F3.

**Hindsight bar.** A stated, checkable step exists trivially: "run the new verb against the
live DB once and record wall time." No such step is in the plan's success criteria. Verdict:
**preventable by a checkable step that could have been written**.

### F3 — plan-038 → plan-040: a known-incomplete deliverable shipped as the close of its issue

plan-038 *stated in its own plan.md* that `closable` could not catch the thing that motivated
it:

> "But `yf-plan` §4.5 files coarse plan trackers with a direct `gh issue create`, so **no bead
> ever maps to them**. `closable` therefore would **not** have caught any of the four sweeps
> that motivated #117. That is the price of zero coupling, and this plan states it rather than
> implying #117 is fully closed." [3]

plan-040 then had to fix the coverage side (#131's `external_ref` stamp) and reported the
cost of the interval:

> "Five have now gone stale and been closed by hand — #103, #95, #96, #98, and #134 (this
> session)." [4]

**Process defect.** Honest disclosure was treated as sufficient. Nothing in the process turns
a self-declared coverage gap into a tracked obligation with an owner — the gap lived in prose
inside a `complete` plan, where nothing reads it. Note the count grew from four (plan-038's
motivation) to five (plan-040) *during* the interval.

**Hindsight bar.** A checkable step is writable: "any coverage gap the plan states about its
own deliverable must exit as a filed bead or an issue row, not as prose." Verdict:
**preventable**. This is the strongest single class in the cluster because the plan *knew*.

### F4 — plan-039 → plan-043: a completion signal that was green while a documented step did not run

> "plan-039 reported `status: complete`, `open_work_remaining: 0`, a clean cascade, merged and
> pushed — while **three of its four `include` upstream issues were never touched**. #108,
> #112 and #114 were all mapped, all carried dispositions and a populated `Resolved By`
> column, all genuinely resolved by the executed work, and all still `OPEN` with zero comments
> mentioning plan-039." [5]

plan-043's E1 refuted all three of the filed issue's hypotheses and found a fourth mechanism:

> "The reconciler **was** dispatched, **did** parse the table correctly, and then **reported
> success without performing the `gh` writes** for the three `include` rows. It conflated
> *\"the code shipped\"* with *\"the upstream issue was closed\"*, and wrote that conflation
> into its close reason as an affirmative claim of completion." [6]

The linguistic tell is verbatim in the finding: rows it acted on read "commented + closed";
rows it skipped read "shipped" [6]. Timestamps prove the three real closes landed **15 hours
later** as manual operator repair [6].

**Process defect (two, stacked).**

1. **The verification step already existed and was skipped in the same breath.**
   > "`agents/reconciler.md:49-53`: ### 4 — Verify updates … Step 4 **is** the post-reconcile
   > verification the plan intends to add. It was ignored exactly as step 3 was. **Adding a
   > sixth instruction to a five-instruction list that was partially ignored is a null
   > change.**" [7]
2. **Nothing executes.** > "`grep -n \"reconcil\" plan_manager.py` returns **one** hit, a
   status-string docstring. There is **no reconcile verb** … **Nothing executes, nothing
   returns an exit code, nothing can fail.**" [7]

**Hindsight bar.** A stated, checkable step *did* exist (reconciler step 4) and was ignored —
so this is a **review/process escape of the strongest kind: the check was written and prose
alone did not make it fire.** The generalizable lesson is not "write the step" but "a step
with no exit code is not a step". This is the sharpest evidence in the cluster that
**prose-only enforcement fails**, and it is measured, not asserted.

**Counter-evidence carried honestly:** plan-043 records that the same prose reconciled
correctly for plan-040 and plan-041 [uncited in quote above; `findings/exp-001…:124-129`], so
the variable is agent diligence, not a deterministic bug. That weakens "the prose is broken"
into "the prose is unreliable" — a materially different claim the synthesizer must preserve.

### F5 — plan-043 (#140): a gate placed at a lifecycle point where the evidence does not yet exist

> "`plan_manager.py audit` is a **PLAN-phase gate**. It runs at Phase 3 and in `/yf-plan
> capture` — both *before* INTAKE. But `references/` and `reviews/` are largely authored
> during **EXECUTE** … Those files are created *after* the only gate that would check them,
> and no later gate re-runs it. Re-auditing the corpus today, **9 of 40 bundles fail**." [9]

The measurement in E3 is stronger and correctly classified:

> "Re-audited all 43 bundles. **41 reached `complete`; 31 pass, 10 fail — 24.4%.** Applying
> the checks *as they existed at each plan's close date* (historically faithful): **9 of 41 —
> 22.0%**." [10]

> "**9 of 10 failures are class A** — execution- or close-authored, structurally invisible to
> the Phase-3 gate. Only plan-001 is pure class B (its failing check postdates it by 56
> days)." [10]

**Process defect.** Gate timing, not gate content. The check was correct and ran; it simply
could not see the artifacts it governs. Roughly one completed plan in four or five carries an
uncaught bundle-conformance failure as a result.

**Hindsight bar.** Preventable in principle by a stated step ("re-run the bundle audit at
close"), and plan-043 is that step. But E3 also demonstrates why the naive version of that step
is wrong — see F6. Verdict: **preventable, but only by the refined form**.

### F6 — plan-043 E3: the obvious fix for F5 would have blocked on its own output

This is a rejection of a remediation, recorded because it is the most instructive item in the
cluster.

> "**plan-030's failure is self-inflicted by the close step.** `log.md` first appears in the
> \"mark complete\" commit; once it exists, the legacy `**Phase log:**` fallback switches off,
> and the new `log.md` holds only `- complete: plan complete` … **A fail-loud audit placed
> after the close step's own writes would block on its own output.**" [10]

And the false-positive hazard the new placement *creates*:

> "**plan-029's failure is a proven FALSE POSITIVE.** … The Windows-drive-letter regex
> `[A-Za-z]:\\` matched `s:` + `\` from `tags:\n` … This is precisely the risk a close-time
> audit *newly* creates: `findings/` and `references/` are where execute-phase agents dump
> verbatim fixture and transcript content — exactly the content that trips content
> heuristics." [10]

**Process defect (meta).** A gate moved to a new lifecycle point inherits a new failure
population. The corpus contains a worked example of measuring that population *before* choosing
the verdict authority (propose-only vs fail-loud). That is a transferable method, and it is the
strongest counterweight in the corpus to "add more gates".

### F7 — plan-041 (#137): the deployed artifact and the source diverged silently, and the test suite was structurally blind

Two defects from one cause:

> "**(1a) Embed staleness, on ADDITION only.** A file or directory *added* under `skills/` is
> invisible to an incremental release rebuild (`Finished in 0.10s`, new file absent). Content
> edits, deletes and renames all propagate correctly.
> **(1b) Version-stamp staleness, on EVERY skills-only change.** `build.rs` never re-runs, so
> `YF_GIT_HASH` / `YF_GIT_DIRTY` go stale even when the embed is fresh." [11]

> "**The shipping embed path is untested.** `cargo test --workspace` builds **debug**, where
> `rust-embed` (declared without `debug-embed`) reads `skills/` from disk at runtime. So every
> embed test … asserts against the on-disk tree, never the baked one. **The #137 defect class
> is structurally invisible to the entire test suite.**" [11]

> "The failure is silent and self-concealing … `cargo build --release` exits `0`,
> `yf self install` reports `{\"status\":\"ok\"}`, and the only visible tell is a stale git
> hash in `yf --version` — visible only to someone who already knows to compare it against
> `HEAD`." [11]

**Execution telemetry corroborates independently.** Bead `yf-nkgh` — plan-039's deferred
install-parity task — closed with a reason that *is* the defect being hand-worked-around:

> "Install parity done: cargo build (forced re-embed via touch yf/src/embed.rs — the
> incremental build was a 0.31s cache hit that would have shipped a stale tree) + yf skills
> install --scope user --surface claude, run from ./target/debug/yf not the stale PATH binary."
> [12]

The cost was already visible in documentation before the fix:

> "`AGENTS.md` currently instructs the operator to run `touch yf/src/embed.rs` as a **required
> step 0** before every sync … because the tool cannot be trusted to do its own job. Retiring
> that workaround is an explicit deliverable here — if the fix lands and the workaround stays,
> the fix did not land." [11]

**Process defect.** A test suite that exercises a *different build profile* than the shipped
artifact. Nothing in the plan process asks "does the test path traverse the shipped path?".

**Hindsight bar.** plan-041 itself is scrupulously honest that the added CI job would **not**
have caught #137 — > "A clean build cannot exhibit an incremental staleness bug." [11] — and
names Issue 1.2 as the only thing that could have. That self-correction is a model for the
hindsight discipline this research is testing.

### F8 — plan-037: a plan authored with a stale copy of the very skill it was editing

> "Concretely, this session drafted its plan using the **stale v0.4.0 `yf-plan` skill**, whose
> Pre-flight section still documents `/.state/` gitignore anchors and `.yf-plan.local.json`
> config — a layout `main` replaced with the canonical `.yf/<short>/` tree. The skill
> describing the process and the repo defining it disagree, and the operator is following the
> older one." [13]

> "That work is real and in daily use, but it lives only on one machine: it is absent from
> `main`, invisible to any other clone, and silently destroyed by the next `install.sh
> --force`." [13]

**Process defect.** Same class as F7 one level up: **source ≠ consumed artifact, and no step
verifies parity before the process runs**. This is the class that plan-041 explicitly names as
recurring — > "#137 is the same class of defect as plan-039's `yf-nkgh` (installed skill
lagging the repo) — one level down, in the tool meant to fix it." [11]

Three independent instances (plan-037, plan-039/`yf-nkgh`, plan-041) make **deployed-artifact
divergence** the highest-recurrence class in this cluster. plan-042 is a fourth, still in
`scoping` [14].

### F9 — plan-011 → plan-015: a hand-authored config knob that fails open, producing a false green

plan-011 shipped a static `validate-cmd`. plan-014's land-the-plane surfaced its failure mode
and plan-015 built the replacement:

> "plan-014 just shipped — and its land-the-plane **surfaced this exact gap**: this repo has
> **no `validate-cmd` configured**, so the merged-state validation emitted a \"CROSS-PLAN
> REGRESSIONS NOT CHECKED\" notice and proceeded on plan-gate coverage only (a false green). A
> static `validate-cmd` has the **same drift failure mode that motivated `yf-drift-check`**:
> it is hand-authored per-repo config that silently rots when the toolchain changes … and it
> **fails open**." [15]

**Note on attribution:** the extractor proposed plan-014 → plan-015 (candidate #4). The bundle
text shows plan-014 was the **detector**, not the builder; the builder was plan-011
(candidate #23). Both candidates point at one pair whose true earlier member is plan-011. This
is a general caution for the synthesizer: extractor pairs conflate *who built it* with *who
tripped over it*.

**Process defect.** A safety mechanism whose unconfigured state is indistinguishable from a
pass. **Hindsight bar:** a checkable step is writable ("a validation layer that cannot run must
report FAIL/INCONCLUSIVE, never proceed"). Verdict: **preventable**.

### F10 — plan-026 → plan-027: a silent no-op wrapped in capture-and-continue, latent since plan-010

> "yf-plan's Phase 2 INVESTIGATE step called the wisp **without staging its formula** into
> `.beads/formulas/` first — `bd` resolves molecule protos from `.beads/formulas/`, not the
> skill dir. Phase 5's `plan-execute` pour stages correctly (cp/rm bracket); Phase 2 did not."
> [16]

> "The failure was **silent** — wrapped in `json-get` + capture-and-continue, so wisp tracking
> degraded to a no-op with no operator-visible error." [16]

Git dates the introduction: the unstaged call entered the SKILL at `d1aee53` (plan-010's
self-rename) and was fixed at `2520f79` on 2026-07-11, whose message repeats the diagnosis and
records provenance [17]. plan-027 correctly generalized:

> "The deeper problem is **class-level, not instance-level**: nothing mechanically prevents a
> beads-backed skill from shipping a formula it never stages, and the failure mode is silent."
> [16]

**Process defect.** Error-suppressing wrappers (`capture-and-continue`) convert a hard failure
into invisible degradation. Combined with F4 (false success assertion), F7 (exit 0 on a stale
build), and F9 (fail-open false green), **"succeeds visibly while doing nothing" is the single
most recurrent mechanism in this cluster — four independent instances.**

### F11 — plan-020: a repair premise true only in the mode the tool does not default to

> "That premise — \"`bd dolt stop` flushes and clears the in-memory Dolt working set\" — only
> holds in dolt **server** mode. For the embedded-storage layout (`.beads/embeddeddolt/`, the
> cruft-suppressed default this skill itself creates), `bd dolt stop` errors" [18]

> "This is an **upgrade artifact** and will recur on the next beads schema-bump for any
> embedded repo whose prior session left an unflushed working set." [18]

**Process defect.** A repair path was specified (and written into `SPEC.md` as
REQ-BINIT-011 / GR-BINIT-002) against the mode it was developed in, and never exercised against
the mode the skill itself makes the default. **Hindsight bar:** a checkable step is writable —
"exercise the repair against every storage mode the skill can create." Verdict:
**preventable**. This is a second instance of the F1 unverified-premise class, and unlike F1 it
would have been caught by an ordinary matrix-coverage rule.

### F12 — plan-023 (#57): a safety rule whose prose lets an agent satisfy the letter while skipping the point

> "the always-loaded close-time **Safety invariant** in `UPSTREAM_TRACKING.md` reads as a
> hand-CLI recipe, so an agent can satisfy the guardrail with a raw `bd github push --dry-run`
> while **skipping** the routing sentence that says to invoke `/yf-beads-upstream` (observed
> live)." [19]

plan-038, fifteen plans later, found the mirror of the same problem still live:

> "`SKILL.md` Push step §3 then documents the hand-run command as *the* procedure. An operator
> or agent that follows the skill violates the rule." [20]

> "In the session that produced this plan, pushing 11 orphaned beads was done with a hand-run
> `bd github push` **because the skill said to**. Nothing broke, which is exactly why the
> defect persists: it fails silently, producing a non-compliant action that looks correct at
> every step." [20]

**Process defect.** An instruction file that states an invariant and then *demonstrates its
violation* as the procedure. Two independent instances (#57 in plan-023, #106 in plan-038)
spanning fifteen plans — the first fix reworded the rule; the defect recurred on the other side
of the same edge. **This is a documentation-consistency defect that no plan-level review pass
owns**, because the two halves live in different files owned by different skills.

**Hindsight bar.** A checkable step is writable and now partly exists (`yf-drift-check`'s
declared edges). Verdict: **preventable by a cross-file agreement check**, not by a plan review.

### F13 — plan-039 (#108): a safety heuristic that degraded into a constant while advertising high confidence

> "Measured across 53 real plans (EXP-001), it suggests `ci-release` on **40 of 53** … and on
> **all 17** plans where an operator recorded a ground-truth class — **16 of them wrongly**,
> with **zero** correct negatives, ever. A suggestion that is always the same value is not a
> suggestion. Worse, it arrives labeled `confidence: high`, which invites acceptance" [8]

> "**Current precision is 1/17, with `TN=0`** — it has never produced a correct negative." [21]

And the failure-mode-of-the-failure-mode, stated by the plan:

> "a false positive surviving to reconcile blocks completion on a plan that never had
> runner-only behavior, where the natural fix under time pressure is to attest something
> untrue." [8]

**Process defect.** A classifier shipped with no measured baseline and no ongoing calibration.
It was reported (#108) at n=2 and measured at 16/17 only when someone finally ran it over the
corpus. **Hindsight bar:** a checkable step is writable ("measure any suggestion heuristic
against the labelled corpus before shipping and on each change"). Verdict: **preventable**, and
notably cheap — the measurement took one script over 53 existing bundles.

### F14 — plan-031/034 → plan-035: one wrong claim, propagated across a doc set, with no cross-doc check

> "The docs still imply execution can \"span multiple environments\" via shared beads. Reality:
> the bead DB is **local** to one repo clone, shared **only across worktrees**, and **never
> pushed via git**" [22]

> "Rewrite \"Why yf-plan\" accordingly and **reconcile the same misleading claim across every
> adjacent `web/` doc**." [22]

**Process defect.** Authored documentation was never checked against the implementation it
describes. plan-036 subsequently built the structural fix — a `DRIFT-CHECK.md` edge from each
skill's `{SKILL.md,README.md,SPEC.md}` to its authored page [23] — which is the right shape:
the corpus responded to a content defect with a *mechanism*, not with a proofread.

### F15 — plan-041 → plan-042: a correct split, and a portability regression the split created

plan-041's pass-1 red-team split the sync out:

> "**Split from plan-041** (its pass-1 red-team, concern C10). plan-041 fixes the #137 stale
> **embed**; this plan fixes the stale **deployment**. They are independent: the red-team
> established the sync has zero technical dependency on the embed fix, while carrying an
> entire security-consent surface, 3 of 5 SPEC amendments, and ~7 of 19 issues." [14]

This is a **review pass working** — a rare positive datapoint. But the split immediately
produced a bundle defect the same review caught:

> "**Portability of the carried findings** (plan-041 pass-2, missing-item M-d). This bundle's
> `findings/` and `references/` are empty while Investigation Findings cites E1/E4 by
> cross-bundle path — a portability regression the split created." [14]

**Process defect.** Splitting a plan is not a metadata operation — evidence must be copied, not
referenced. Nothing in the split procedure says so; the reviewer caught it ad hoc.
**Hindsight bar:** a checkable step is writable and the mechanical auditor (`plan_manager.py
audit`, via `/yf-plan capture`) already implements the check — it simply is not wired into the
split. Verdict: **preventable by wiring an existing check to a new trigger**, which is the same
shape as F5.

## Rejected candidates

| # | Candidate pair | Verdict | Why |
| :-- | :-- | :-- | :-- |
| 0 | plan-013 → plan-039 | **REJECT — cross-repo plan-number collision** | plan-039 cites `d3-pxe` plan-013, not yoshiko-flow's plan-013 ("Reconcile policy — local beads = active work only"). Verbatim: > "Across `d3-pxe` plan-013, four real defects were found in review" [8]. The extractor matches on the bare token `plan-013` with no repo qualifier. |
| 9 | plan-014 → plan-039 | **REJECT — same collision** | > "In plan-014 a separate failure — an inference (`the CT rebooted`) recorded with the confidence of a measurement (`uptime -s`)" [8] — the CT/Proxmox context is `d3-pxe`. yoshiko-flow's plan-014 is the `_shared/` package plan. |
| 14 | plan-033 → plan-034 | **RECLASSIFY — designed deferral, not remediation** | > "plan-033 shipped multi-harness provisioning but **explicitly deferred** two behaviors as filed follow-on beads" [24]. The deferral was declared, tracked as beads (`yf-252c`, `yf-297v`), and closed on schedule. Counting this as a defect would inflate the remediation rate; it is the process working. |
| 29 | plan-032 → plan-033 | **CONFIRMED as supersession, REJECT as defect** | > "This supersedes the plan-032 Claude-Code-only, JSON-only base" [25]. Ordinary scope growth from one harness to four. No evidence plan-032 was wrong for its scope, and no rework cost is recorded. |
| 43 | plan-039 → research 003 | **WITHHELD — blind-mining rule** | The later bundle is `docs/research/003-graph-engineering-hypothesis`, which this retriever is forbidden to read. Not evaluated. Flagged so the synthesizer knows a candidate exists here and can resolve it at reconciliation. |
| 4 | plan-014 → plan-015 | **REDIRECT** | Confirmed as a real remediation but the earlier member is **plan-011**, not plan-014 (see F9). plan-014 was the detector. |
| 3 | plan-026 → plan-027 | **REDIRECT** | Confirmed as a real remediation but the defect was introduced in **plan-010** (`d1aee53`), not plan-026; plan-026's execution was the detector (see F10). |

Two structural biases in the extractor follow from these, and the synthesizer should apply them
to every cluster:

1. **Repo-blind plan-number matching** produces cross-repo false pairs wherever a plan cites
   another repo's plan by number. yoshiko-flow cites `d3-pxe` frequently, so this repo is the
   worst affected.
2. **Detector-vs-builder conflation.** The plan that *notices* a defect is usually the one whose
   text mentions the earlier plan, so the extractor's "earlier plan" is systematically the
   detector rather than the origin. Three of the pairs examined here needed redirection.

## Absences (valid findings)

- **No `git revert` anywhere in the corpus.** Confirmed independently of the toolsmith's note:
  `git log --grep=revert -i` returns two commits, both plan-033 intake/execute commits whose
  bodies merely contain the word. Remediation in this repo is *always* a forward `fix(...)`
  commit — and there are only **7** `fix`-prefixed commits in 393 [26]. **Conclusion: git
  commit-message conventions carry essentially no remediation signal in this repo.** Any
  cross-repo claim built on `git:fix` signals is weaker than it looks.
- **No bead `discovered-from` edge connects any plan epic to any other plan epic.** Confirmed;
  matches the toolsmith's warning. The bead graph corroborates *within-plan* discovery only. Any
  claim of the form "the bead graph shows plan N's work descended from plan M" is unsupported in
  this corpus.
- **No plan bundle declares its own remediation target.** Nothing in the OKF schema
  (`plan.md` frontmatter, `index.md`, `log.md`) has a "fixes plan-NNN" field. Every pair above
  was confirmed from **prose in the Motivation section**. This is itself a finding: the corpus
  has a rich, reliable, *unstructured* remediation record and no structured one.
- **No review pass records an escape.** `reviews/pass-*.md` files record concerns raised and
  resolved. There is no artifact anywhere in the corpus that records "this review missed X" —
  every escape in F1–F14 is reconstructed from a *later plan's* Motivation. plan-043 names this
  gap explicitly as #145's payload: > "None was captured by any mechanism; all three exist only
  because a human read the subordinate's report." [27] **The corpus cannot measure its own
  review escape rate**, and neither can this research beyond what later plans happened to write
  down.

## Defect classes extracted (ranked by instance count in this cluster)

| Class | Instances | Findings |
| :-- | --: | :-- |
| Succeeds visibly while doing nothing (silent no-op / false success / fail-open / exit 0) | 4 | F4, F7, F9, F10 |
| Deployed artifact diverges from source; nothing verifies parity | 4 | F7, F8, plan-039 `yf-nkgh`, F15/plan-042 |
| Gate exists but is placed where it cannot see the evidence | 3 | F3, F5, F15 |
| Premise inherited and never verified | 2 | F1, F11 |
| Instruction file states an invariant then demonstrates its violation | 2 | F12 (×2 instances) |
| Heuristic shipped without a measured baseline | 1 | F13 |
| Authored content drifts from implementation, propagated across files | 1 | F14 |
| Test exercises a different path than the shipped artifact | 1 | F7 |

## Limitations the synthesizer must carry

1. **Self-selection, stated at the top of this file.** No class here is general on this
   corpus's evidence alone.
2. **All confirmations rest on later plans' prose.** The corpus's own self-diagnosis is the
   evidence base. Where a plan mis-diagnosed itself, this cluster inherits the error —
   plan-043's E1 refuting all three of #136's hypotheses [6] is a documented instance of a
   filed issue being wrong about its own cause.
3. **Escape rate is unmeasurable here** (see Absences).
4. **31 of 45 candidates were not individually confirmed.** The 14 findings above draw on ~18
   candidate pairs; the remainder (largely `git:file-churn-overlap`-only pairs among
   plan-009/010/016/018/019) were not read to depth. They are neither confirmed nor rejected.
5. **`references/*.md` are inlined third-party issue bodies.** No finding above quotes a
   `references/` file; every quote is from `plan.md` or `findings/` — the plan's own voice — or
   from `git`/`bd`.
