---
type: Research Artifact
phase: retrieve
research: 004-plan-process-defect-mining
cluster: yf-corpus-reviews
produced: '2026-08-16'
okf_spec: OKF-RESEARCH
---

# Cluster: yf-corpus-reviews

Supplementary retrieval over the **one surface the `yf-corpus` retriever never opened**:
yoshiko-flow's 93 `reviews/pass-N.md` files. Method is `direct` — local filesystem and `git`
only, no web leg. Findings are reported against the **merged class labels** from
`triangulation.md` §1 (M1, M2a, M2b, M5, M6a, M6b, M7, M11, M13, M14), not against the
cluster-local DC-* or yf-* labels.

**Why this cluster exists.** `triangulation.md` §4.1 established mechanically that the two
primary clusters are not comparable: 16 of 30 cross-repo sources cite a `reviews/pass-N.md`;
**0 of 27** yf-corpus sources do, against a yoshiko-flow surface of 93 passes. Three merged
classes — **M2b**, **M6a**, **M6b** — were marked `[insufficient evidence] in yoshiko-flow`
purely because nobody looked here. This cluster resolves that. It does **not** re-mine
candidate remediation pairs; those are `cluster-yf-corpus.md`'s 15 findings and are cited, not
restated.

**Self-selection caveat, carried into every finding below.** yoshiko-flow is the skill fixing
itself. Its defect population is self-selected and it is unusually articulate about its own
defects — several passes below are *about* review quality because the plan under review is
*about* review quality. A class confirmed only here is **not** thereby general. Where a class
is already confirmed in three other repos by `cluster-cross-repo-corpus.md`, a yf instance adds
a fourth repo and closes an unmeasured gap; where a class appears only here, it is an
in-repo observation.

---

## 1. Surface quantification

Counted mechanically over `docs/plans/*/reviews/` on 2026-08-16.

| Measure | Value |
| :-- | --: |
| Plan bundles in `docs/plans/` | 43 |
| `reviews/pass-*.md` files | 93 |
| Bundles with ≥1 review pass | 42 |
| Bundles with ≥2 review passes | 29 |
| Bundles with **0** passes (`plan-042`, empty `reviews/`) | 1 |
| Maximum passes in one bundle (`plan-026`) | 7 |
| Mean passes per reviewed bundle | 2.21 |

Distribution — note the file naming is uniformly `pass-N.md`; no legacy variant exists, unlike
d3-pxe's `pass-0-conformance.md`.

| Pass number | Files at that depth |
| :-- | --: |
| pass-1 | 42 |
| pass-2 | 29 |
| pass-3 | 10 |
| pass-4 | 5 |
| pass-5 | 4 |
| pass-6 | 2 |
| pass-7 | 1 |

**Verdicts.** Every pass records an explicit verdict.

| Population | APPROVE | REVISE |
| :-- | --: | --: |
| pass-1 (n=42) | 1 | 41 |
| pass-2..7 (n=51) | 29 | 22 |
| All passes (n=93) | 30 | 63 |

Two numbers matter. **41 of 42 first passes returned REVISE** — the first pass essentially never
approves. And **22 of 51 later passes still returned REVISE**, with 13 of those carrying at least
one `high`-severity concern, at depths up to pass 5 (`plan-029/reviews/pass-5.md`) [1]. Review
depth in this repo is not ceremonial padding: passes 2–7 keep finding blocking defects.

**M6a's signature — a pass naming a defect in a prior pass of the same bundle — fires in 8 of the
51 later passes, across 5 bundles** (`plan-026`, `plan-037`, `plan-039`, `plan-041`, `plan-043`).
The concentration is in the four most recent multi-pass bundles, which is itself discussed in §5.

---

## 2. Per-class presence / absence in yoshiko-flow

Scored against the merged labels. `yes` = at least one instance quoted verbatim below with a
`path:line`. `not found` = searched with the stated queries, no instance located (weaker than
`absent`). "Prior status" is what `triangulation.md` recorded for **yoshiko-flow specifically**.

| Merged class | Prior status in yf | This cluster | Instances |
| :-- | :-: | :-: | :-- |
| M1 Succeeds visibly while doing nothing | yes (other surface) | **yes** — corroborated on a new surface | [2] [3] [11] |
| M2a Blind gate — runs, passes, cannot see its evidence | yes | **yes** — independent instance | [4] |
| M2b Unsatisfiable gate — deadlock by construction | **[insufficient evidence]** | **RESOLVED → yes** | [5] [6] |
| M3 Deployed artifact diverges from source | yes | **yes** — independent instance | [7] |
| M4 Docs diverge from implementation | yes | not found *as a review concern* | — |
| M5 Prose-only enforcement does not bind | yes | **yes** — strongest recurrence here | [8] [9] [10] |
| M6a Review-induced defect / regression | **[insufficient evidence]** | **RESOLVED → yes** | [12] [13] [14] |
| M6b Residue and stale internal cross-reference | **[insufficient evidence]** | **RESOLVED → yes** | [15] [16] [17] [18] |
| M7 Load-bearing premise carried without verification | yes | **yes** — independent instances | [19] [20] |
| M8a `complete` overloaded | yes (other surface) | not found — structurally out of scope | — |
| M8b Undisclosed post-completion churn | yes (other surface) | absent (structural — reviews precede execution) | — |
| M9 Remediation relationship exists only in prose | yes | **corroborated** — reviews add no structured edge | §6 A-2 |
| M10 Precise diagnosis, never routed into work | yes | **yes** | [21] |
| M11 Real-target reality only reachable by running | yes | **yes** | [22] [23] |
| M12 One-directional reconcilers | yes | not found | — |
| M13 *(method)* extractor identity failure | yes | n/a — no extractor used | — |
| M14 *(method)* corpus cannot measure its escape rate | yes | **widened** — see [24] and §5 | [24] |
| **NEW — M6c** Resolution asserted but not landed | — | **new class** | [25] [26] [27] |
| **NEW — M14b** Conformance findings leave no artifact | — | **new class** | [24] |

Two "not found" rows deserve a word so they are not read as absences of the defect. **M4** and
**M12** are real in yoshiko-flow (`cluster-yf-corpus.md` and `cluster-history-and-upstream.md`
evidence both) — they simply are not the kind of thing a *plan* review is looking at, because a
plan review reads a plan, not the shipped docs. **M8b** is structurally invisible here: every
review pass is written before or during approval, and M8b is by definition post-completion.

---

## 3. Resolving the three `[insufficient evidence]` items

### 3.1 M2b — Unsatisfiable gate. **RESOLVED: present in yoshiko-flow.**

Two independent instances, both `high`/blocking, both caught at review.

The cleanest is `plan-030` pass 1 — and it is the *same shape* as the cross-repo instances
(`cross-repo-corpus:26`, `cross-repo-corpus:21`): an automatic completion condition defined over
a set that contains an element another mechanism holds open.

> "Option (b) deferred-validation bead contradicts the cascade-close step that runs *before*
> complete-gate: `close_cascade.cascade()` fail-louds (exit 2) on any container with any open
> child, so an open bead *inside* the plan tree halts completion before complete-gate runs.
> Reconcile Gate (\"all execution beads closed\") has the same conflict. **Option (b) is
> unreachable as written.**"
> — `docs/plans/plan-030-james-dixson-65526e/reviews/pass-1.md:20` [5]

Note the recommendation is *exactly* the graph check `cluster-cross-repo-corpus.md` DC-1 proposed
— relocate the blocked element out of the gate's closure set: *"Require the deferred-validation
bead to live **outside** the plan molecule tree (a standalone/upstream-tracked bead the cascade
never visits)"* (same line).

The second is a *success criterion* rather than a bead gate, and it is review-induced (so it is
also [12] below):

> "2.5 says a missed fixture \"is a finding, not a tuning signal… a second miss escalates rather
> than iterates\". SC7 required 4 × `FLAGGED`. If a fixture legitimately does not fire and the
> operator accepts that, **SC7 can never be satisfied** — so the only route to completion is to
> tune until it flags, exactly the confirmation bias 2.5 exists to prevent. **Both were added by
> the same resolution; neither noticed the other.**"
> — `docs/plans/plan-039-james-dixson-150f79/reviews/pass-3.md:52-58` [6]

**Consequence for triangulation.** M2b is now confirmed in **4 repos** (d3-pxe, pybridge,
evri_py, yoshiko-flow), and §2.1's stated asymmetry ("M2b appears in three non-yf repos and zero
yf instances") is dissolved exactly as §4.1 predicted it would be: it was a method artifact.
Both yf instances were **caught by review**, matching pybridge and evri_py; only d3-pxe's reached
execution.

### 3.2 M6a — Review-induced defect / regression. **RESOLVED: present, and self-attributed.**

The strongest instance in the whole cluster, because the reviewer names the author — the previous
pass's own operator:

> "**The high concern is a defect I introduced in the pass-1 revision**, not a pre-existing one."
> — `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-2.md:18` [12]

and the operator's own resolution row concurs:

> "**My error, introduced when Epic 2 was renumbered after dropping the delta** — the gate's
> targets did not shift with the issues."
> — `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-2.md:82` [13]

The **regression** sub-shape — a fix that reintroduces the defect it fixes — is confirmed too,
and yoshiko-flow's instance is sharper than any cross-repo one because it is measured:

> "Three do not fully land, and one — the H1 fix — **reintroduces the exact defect class H1
> named, inside its own remedy**." … "**C1 — SC6 is falsified by measurement, again. The H1 fix
> reproduces the H1 defect.** … The new matches come from text the H1 resolution itself added:
> 3.4's stop-rule blockquote, 3.4b's own prose, and \"redeploying\" in the SC trailer."
> — `docs/plans/plan-039-james-dixson-150f79/reviews/pass-3.md:16,40-48` [14]

A third, milder instance: *"SC3 contradicts R2a's own mitigation … **A contradiction introduced
by the C4 fix.**"* — `plan-041-.../reviews/pass-2.md:44`.

**Counter-evidence, which must travel with the finding.** Review-induced defects are not
inevitable here. `plan-039` pass 5, run on the same bundle two passes later, reports the clean
outcome:

> "**No defect introduced by the pass-4** [revisions]"
> — `docs/plans/plan-039-james-dixson-150f79/reviews/pass-5.md:17`

So the supported claim is that the revision step is a **defect-introducing step with a nonzero
rate**, not that it always regresses. In this bundle the rate was 2 of 4 revision cycles.

### 3.3 M6b — Residue and stale internal cross-reference. **RESOLVED: present, four instances, and renumbering is the dominant cause.**

`triangulation.md` C5 already proved M6b exists in yoshiko-flow via a third cluster (issue #135,
four stale literals in one plan). This cluster finds it **natively in the review surface**, four
times, and identifies the mechanism.

**Renumbering residue — the machine-readable field and its prose drift apart:**

> "**The Capability Gate's `Blocks` set was not renumbered when Epic 2 lost its old 2.1.** …
> the gate still said `Blocks: 1.3, 2.3`, and its Instructions still named 2.2 as a verb. Net
> effect: **Issue 2.2 could wire the audit into §6.4 while `REQ-COMPLETE-001` still read \"fixed
> three-step order\"** — precisely the outcome the gate exists to prevent."
> — `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-2.md:50` [15]

This is the load-bearing variant `cluster-cross-repo-corpus.md` DC-4 flagged in pybridge (a gate
carve-out pointing at a bead that no longer resolves) — a **stale pointer inside a gate**. The
adjacent C17 makes the cost explicit: *"`Resolved By` is the column `reconciler.md` reads, and a
mismatched mapping in this exact table is the mechanism behind #136 — the defect this plan exists
to fix"* (`pass-2.md:51`).

**Same-string-surviving-elsewhere residue — the classic DC-3(a) shape, in its *third* location:**

> "The C1 resolution repaired the criterion but not the sentence naming it, so the plan claimed
> and denied the same thing … An executor taking it literally concludes Epic 3 failed …
> **Same defect class as H1 and C1, in its third location.**"
> — `docs/plans/plan-039-james-dixson-150f79/reviews/pass-4.md:41-49` [16]

**Fix-not-propagated-to-the-criterion residue, with a stated cost:**

> "**C18's fix did not propagate to SC2 or D10.** … An implementer building capture-only
> enumeration would **satisfy SC2 and D10 while violating Issue 0.3**, leaving R8 unmitigated by
> the exact mechanism C18 identified."
> — `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-3.md:57` [17]

**Bundle-level residue after a plan split — the cold-reader cost, named:**

> "**Stale artifacts the split left behind (aggregate).** `index.md`'s summary still describes the
> moved sync deliverable — **the first thing a cold reader sees**. `log.md` has no entry for the
> split and `status:` was still `review`. The Experiments table justifies E1/E4 in the present
> tense against decisions that left"
> — `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-2.md:47` [18]

The companion C16 records the *reader-facing* half — "Epics jump 0→1→3→4; risks run R2, R2a, R3,
R5, R7, R9 with R1/R4/R6/R8 silently gone. **A reader cannot distinguish \"moved to plan-042\"
from \"lost in editing\"**" (`pass-2.md:48`).

**M6b is now confirmed in 5 of 5 eligible repos**, and yoshiko-flow supplies the sharpest
statement of the mechanism: **renumbering is the trigger, and the machine-authoritative field and
its prose restatement are two locations that must be updated together.** `plan-043` pass 3 says
so directly: *"renumbering errors clustering is exactly why it matters"* (`pass-3.md:56`).

**Preventable by a stated, checkable step?** **Yes, and yoshiko-flow independently reached
`cluster-cross-repo-corpus.md` DC-4's answer.** The remedy that finally worked in `plan-043` was
mechanical resolution, not a further review pass — see §4.2. Every instance above is a
reference-resolution failure over identifiers the bundle itself defines (`Issue N.M`, `SC<n>`,
`R<n>`, `D<n>`, `#<n>`), which a linter resolves. This passes the HINDSIGHT bar.

---

## 4. What review CAUGHT — testing the cross-repo calibration against 93 passes

`triangulation.md` §6.10 records the cross-repo calibration as surviving: review is **effective on
claims with a stated mechanism**, **weak on executable commands**, and **weak on its own prior
revisions**. Tested here, that calibration is **two-thirds confirmed and one-third refuted.**

### 4.1 Effective on claims with a stated mechanism — CONFIRMED, strongly

This is the modal yoshiko-flow review concern. The reviewer re-derives the plan's premise from
the source and reports the delta. Selected:

> "**Epic 4 premise factually wrong for md2pdf**: it **already** has `check_deps()`
> (REQ-MDPDF-003) exiting with a named-tool message. 4.3's run-guard is redundant for md2pdf."
> — `docs/plans/plan-026-james-dixson-6e0e2f/reviews/pass-1.md:20` [19]

> "**Epic 0 amends a requirement that does not contain what the plan says it contains.**
> `REQ-YF-PRE-009` (`SPEC.md:634-646`) is entirely about the preflight **self-update offer**;
> `grep -n \"rerun-if\|build\\.rs\" SPEC.md` returns **nothing**. … **The plan promoted a code
> comment into a SPEC requirement.**"
> — `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-2.md:43` [20]

> "**Issue 2.1/2.2 use the wrong artifact paths — would miss the vault's entire plan+research
> corpus.** The vault's plans/research live at `docs/plans/`, `docs/research/`, AND
> incubator-scoped `Incubator/<slug>/plans/` … not top-level `plans/`/`research/` as 2.2 says."
> — `docs/plans/plan-029-james-dixson-75fd34/reviews/pass-5.md:22-28` [1]

All three are **M7** (a load-bearing premise carried without verification) caught *before* any
epic ran, by a reviewer who read the cited artifact instead of the plan's description of it.
`plan-041` [20] is the strongest: the reviewer ran the disconfirming grep and quoted its empty
result. That is `cluster-cross-repo-corpus.md` DC-7's remedy ("a claim about an artifact must
cite the artifact, not the prose") being executed unprompted.

### 4.2 Weak on executable commands — **REFUTED for yoshiko-flow. Reviewers here run them.**

This is the cluster's most consequential divergence from the cross-repo finding. In d3-pxe, a
`curl` gate test was **praised by two passes** before pass 3 found it could never pass
(`cross-repo-corpus:5`). In yoshiko-flow, reviewers execute the criterion and report the exit
code. 17 passes across 12 bundles contain explicit execution evidence. The canonical form:

> "**M1 — `Gate: Evidence corpus`'s Test cannot fail.** … corpus the pipeline still exits 0. The
> gate's test passes unconditionally." … resolved as: "**Verified (BSD `wc -l` pads).** Replaced
> with `test -d … && [ \"$(ls … | wc -l)\" -gt 0 ]`"
> — `docs/plans/plan-039-james-dixson-150f79/reviews/pass-2.md:93,97,221` [2]

That is a textbook **M1** ("can never fail") caught by *running* it — the exact sub-class
`cluster-cross-repo-corpus.md` DC-2 said review reliably misses. The next pass then confirmed the
fix **with a negative control**:

> "**M1 is a real fix, verified with a negative control** — the new gate test passes against the
> live corpus and *fails* against a nonexistent one. **The old form could not fail.**"
> — `docs/plans/plan-039-james-dixson-150f79/reviews/pass-3.md:24` [3]

The discipline is stated as a reviewer instruction, not left to chance:

> "REVISE only for defects that would break execution, make a deliverable unverifiable, or
> mislead upstream — **verified by running a command** or quoting contradicting text."
> — `docs/plans/plan-040-james-dixson-1cabe4/reviews/pass-3.md:10` [28]

And the vacuous-pass check runs in the *other* direction too — a criterion that passes because it
matches nothing:

> "**SC11 and SC1b are both discriminating, verified live.** `evidence` and `code span` occur zero
> times in `spec/cli.md` today, **so SC1b cannot pass vacuously**."
> — `docs/plans/plan-039-james-dixson-150f79/reviews/pass-4.md:31-32` [29]

The one shape yoshiko-flow's review does **not** reliably close is the **never-shown-RED** test —
`triangulation.md`'s `[insufficient evidence]` "false pass" shard. It was *identified* here, which
upgrades that shard's evidence from one repo to two:

> "**The Capability Gate's test is never shown RED before the fix.** `1.2 depends-on 1.1`, so the
> test is authored after the fix and only ever observed passing. **A test green because it does
> not exercise the addition path is indistinguishable from one green because the fix works.** The
> plan shows it understands the trap … **but does not close it.**"
> — `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-2.md:45` [11]

Note this was found at **pass 2**, one pass after the same reviewer had found the same gate wrong
in both directions at once (*"**False pass:** editing `build.rs` is itself a watched-file change
… **False fail:** `git commit` moves `HEAD` without touching a watched file"* —
`plan-041-.../reviews/pass-1.md:52`). The pass-1 catch is the strongest single anti-DC-2 datum in
the corpus: a reviewer reasoning about a gate command's behavior in **both** failure directions,
before execution.

**Revised calibration statement.** "Review is weak on executable commands" is a property of a
*review practice that reads*, not of review as such. A review practice that **runs the command and
demands a negative control** catches the M1 shard reliably. yoshiko-flow demonstrates the
countermeasure; d3-pxe demonstrates its absence. Both are in the corpus.

### 4.3 Weak on its own prior revisions — CONFIRMED, and yoshiko-flow shows the fix and its limit

The failure is real and repeated here (§3.2, §3.3). What is *new* is that this repo evolved an
explicit countermeasure — **verify the resolution against the plan body, not against the
resolutions table** — and the corpus records both its adoption and its residual failure rate.

Adoption is visible from `plan-022` onward and is stated in the pass banner:

> "Cycle 2 verified each pass-1 concern was actually resolved in `plan.md` (**not merely asserted
> in** the pass-1 table)"
> — `docs/plans/plan-022-james-dixson-14b3dd/reviews/pass-2.md:9`

> "All 10 pass-1 resolutions **genuinely applied (verified line-by-line, not just the resolution
> table)**."
> — `docs/plans/plan-026-james-dixson-6e0e2f/reviews/pass-2.md:13`

It works — it catches things:

> "The reviewer verified each pass-1 resolution landed in `plan.md` rather than merely being
> asserted in the resolutions table — **and caught one that had not (C18)**."
> — `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-2.md:18-19` [25]

And it is *still* not sufficient, which is §5's new class.

### 4.4 The deepest passes still catch blocking defects

Against the intuition that review saturates, `plan-026` — the 7-pass bundle — found **two mediums
at pass 4 that three prior passes missed**:

> "**Two medium concerns three prior passes missed**, both verified against real code: a
> SPEC-first guardrail conflict introduced by #85, and an Epic-2 reader directive that would
> regress `md2pdf`."
> — `docs/plans/plan-026-james-dixson-6e0e2f/reviews/pass-4.md:9` [24]

The stated cause is a **scope difference, not diligence**: pass 3 was delta-scoped to the #85
addition; pass 4 was *"operator-requested full, fresh, whole-plan adversarial review (not
delta-scoped) … **Supersedes the delta-only pass-3** for readiness purposes"* (`pass-4.md:3-6`).
That is a checkable structural lesson: **a delta-scoped pass does not discharge whole-plan
review**, and a bundle whose scope changed after approval needs a full re-pass.

The same bundle then demonstrates the M6b remedy working end to end. Pass 6 found an incomplete
residue list — *"**the Issue 5.3 de-list list is materially incomplete** — it enumerates three
lint surfaces and misses ≥3 more in-repo references"* (`pass-6.md:11`) — and pass 7 closed it
**by exhaustive grep**:

> "**Grep-complete coverage, verified.** All 7 in-repo references (excluding the script,
> `__pycache__`, `docs/plans/`) are explicitly de-listed"
> — `docs/plans/plan-026-james-dixson-6e0e2f/reviews/pass-7.md:13` [30]

That is `cluster-cross-repo-corpus.md` DC-3(a)'s prescribed step ("grep the whole bundle for the
corrected string and list every site changed"), independently arrived at, and it worked.

---

## 5. New classes the pair-mining missed entirely

### 5.1 M6c — A resolution is asserted in the resolutions table but did not land in the plan body

**This is distinct from M6a and M6b and should be a separate class.** M6a is a fix that
*regresses*; M6b is a fix applied at one site but not all sites. M6c is a fix **that was never
applied at all**, while the bundle's own bookkeeping records it as `resolved`. The artifact that
is wrong is the *review record*, not the plan.

Three instances, all self-incriminating, all in the last three bundles:

> "**M3's resolution did not land.** pass-1 marks it `resolved — falsifier recorded in the E2
> block`, but `grep -rn \"falsif\"` across the bundle hits **only `reviews/pass-1.md`**. **A
> resolution row asserting something the plan does not contain is the failure mode this cycle
> exists to catch.**"
> — `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-2.md:50` [25]

> "N1 | Approach said \"Three active workstreams\" while naming four epics — **C16's claimed
> reconciliation had not landed**"
> — `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-3.md:49` [26]

The third is the most important finding in this cluster, because it names a **mechanism** that
generalises well beyond plan bundles:

> "**C22 caught a resolution asserted in pass-2's table that did not land in the plan body.** …
> The cause was mundane and worth recording: **the target string wrapped across a line break, so
> two successive replacements silently matched nothing while the resolutions table was updated as
> if they had.** **The lesson is that a resolution is not resolved until it is grepped**, and that
> is now how this bundle's fixes are verified."
> — `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-3.md:21-26` [27]

and the operator's resolution row:

> "The two prior replacements failed because the string wraps across a line break — **a silent
> no-op that pass-2's table nonetheless recorded as resolved.**"
> — `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-3.md:88` [27]

**M6c is M1 wearing review clothing.** A search-and-replace that matches zero occurrences returns
success; the operator reads success and writes `resolved`. It is the same "succeeds visibly while
doing nothing" mechanism as `yf-corpus:6`'s reconciler and `history-and-upstream:4`'s comma-joined
bd list — **applied to the process's own bookkeeping**. That is why the pair-mining could never
find it: the defect never reaches a later plan, because the bundle catches it internally and the
Motivation prose of the next plan has no reason to mention it.

**Preventable by a stated, checkable step? Yes, unambiguously, and the repo has already stated
it.** `plan-043` pass 4 is the demonstration — an APPROVE reached by verifying every claimed
resolution mechanically rather than by reading:

> "All four cycle-3 concerns verified **by grep against `plan.md`**, not by reading the
> resolutions table — the discipline this bundle earned after two instances of a resolution
> asserted but not landed." … "C22 | `grep -c '1\\.1/2\\.2'` → **0**; exactly one `1.1/2.1` at
> L428. **Line-wrapped variants also checked** — none. | LANDED"
> — `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-4.md:19-24` [31]

The step is: **every resolution row must carry the grep and its count.** It is mechanical, it has
an exit code, and it directly satisfies M5's "a step with no exit code is not a step."

**Generality: [uncertain].** All three instances are yoshiko-flow, and all three are in bundles
written after the practice of resolution-verification was adopted — so the class is visible here
*because* this repo started looking for it. The cross-repo corpus contains one structurally
identical instance that its retriever classified as DC-3(a) residue rather than as this class
(pybridge `plan-010` pass-2's "Success Criteria says '#38 closed as a dup of #34' — the exact
reversal C6 fixed", `cross-repo-corpus:22`). Whether that is M6b or M6c is not resolvable from the
quote. **Do not report M6c as general on this evidence.**

### 5.2 M14b — The conformance pass produces no artifact, so its findings are unrecoverable

yoshiko-flow runs **two** reviews per cycle: a mechanical conformance pass and an adversarial
red-team pass. Only the second writes a file.

> "Conformance pass ran first and returned **PASS** (**after two INCOMPLETE rounds**: an
> uncompleted `upstream-triage.md`, an Upstream Issues note that contradicted the revised D1/D2,
> a double-deliverable Issue 2.6, two success criteria with no verification handle, and a
> dangling `2.6` edge left by the split). **Conformance is mechanical and produces no
> `pass-N.md`**; this file records the adversarial pass."
> — `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-1.md:17-21` [24]

Five defects — including a **dangling dependency edge** (M6b) and **two success criteria with no
verification handle** (M1-adjacent) — exist in the corpus only because one reviewer happened to
summarise them in a parenthesis. Across the other 92 passes the conformance layer surfaces only as
a one-word banner: `**Conformance:** PASS`, `**Reviewers:** conformance (PASS), red-team
(REVISE)`, `**Conformance (pre-pass):** PASS (after Capability-Gate `Approvers:` fix)`
(`plan-009/reviews/pass-1.md:3`, `plan-006/reviews/pass-1.md:3`,
`plan-008/reviews/pass-2.md:5`). The parenthetical in the last of those is a defect record too —
and it is all that survives of it.

**This is a direct, quantified widening of M14** ("the corpus cannot measure its own review-escape
rate"). It is worse than M14 states: the corpus cannot measure the **conformance** layer's find
rate *at all*, because that layer is a gate whose output is discarded on success and summarised in
prose on failure. Every escape-rate figure in this research is therefore missing an unknown number
of mechanically-detected defects that were fixed and never written down.

**Preventable by a stated, checkable step? Yes — trivially.** The conformance reviewer already
emits a `PASS|INCOMPLETE` contract (specified at `plan-005/reviews/pass-2.md:26`); it simply is
not persisted. Writing it to `reviews/conformance-N.md` is a one-line change. d3-pxe already does
this — `cluster-cross-repo-corpus.md` cites `pass-0-conformance.md` as a real file in a d3-pxe
bundle — so the artifact form exists in the corpus and yoshiko-flow does not use it.

---

## 6. Absences

### A-1 — No review pass names a defect in a *different* plan bundle. The review surface is bundle-local.

Recursive grep for `plan-0[0-9][0-9]` across every bundle's `reviews/`, excluding each bundle's
own id, returns 63 hits — but **every one is a scoping, sequencing or precedent reference, not a
defect attribution**. The distribution is dominated by `plan-042` (23 hits, all inside
`plan-041`'s reviews, referring to the plan `plan-041` was *split into* — a co-design pointer,
exactly `cluster-cross-repo-corpus.md` R-3's "coupling not remediation" signal) and `plan-013` (10
hits, cited as a *fixture source*: *"d3-pxe plan-013 carries `reviews/pass-0-conformance.md`
quoting the pre-fix Epic 6 defect verbatim"*, `plan-039/reviews/pass-3.md:33`).

**Consequence: the review surface cannot produce remediation pairs.** It is a *within-bundle*
instrument only. This is not a limitation of my search — it follows from when reviews are written
(before execution of the bundle they review, hence before any later bundle exists). Anyone reading
this cluster alongside `cluster-yf-corpus.md` should understand the two as **non-overlapping by
construction**, not as two attempts at the same thing.

### A-2 — Reviews add no machine-readable remediation edge either. **C1 (M9) holds.**

No review pass carries a structured field naming a defect's author, a prior pass's concern id in a
parseable form, or a link to a bead. Concern ids (`C1`, `M3`, `RT-2`, `F5`, `N1`, `P2`, `H1`) are
**bundle-local and non-uniform across bundles** — seven different prefix conventions appear across
the 93 files. Even *within* a bundle the cross-pass reference is prose (`"the H1 fix"`,
`"C18's fix"`). The `[insufficient evidence]` verdict on machine-corroboration is unchanged by
this cluster; if anything the review surface makes it worse, since it is the densest defect record
in the corpus and the least structured.

### A-3 — No review pass records "a previous review pass was wrong to approve"

Searched for language admitting an APPROVE was mistaken. **No evidence found.** Passes freely
record that a prior pass *missed* something ([24]) or that a prior *revision* broke something
([12][14]), but no pass revisits an APPROVE verdict. `plan-026` comes closest — pass 4 states it
*"Supersedes the delta-only pass-3 for readiness purposes"* (`pass-4.md:6`), which supersedes a
**scope**, not a judgment.

The absence is structurally explained and carries no information about review quality: a plan that
was approved leaves the review phase, so there is no venue in which a later pass could contradict
the approval. **Any defect that escaped a final APPROVE is invisible to this surface** — which is
precisely M14, and precisely why `cluster-history-and-upstream.md`'s git and issue evidence is not
substitutable by more review mining.

### A-4 — M8a / M8b are not observable here

No review pass discusses a `complete` status, a deferred proof, or post-completion churn. This is
structural: every pass is written at `review` status, before `complete` exists. Recorded so that
their absence from the table in §2 is not misread.

### A-5 — plan-042 has an empty `reviews/` directory

One bundle of 43 carries zero passes. `plan-042-james-dixson-98631b/reviews/` exists and is empty.
This bundle is the **split-off half of plan-041** (`plan-041/reviews/pass-2.md:47` records the
split), so it inherited its content from a reviewed plan. I did **not** determine whether it was
reviewed under another mechanism or approved unreviewed; that is a question for the synthesizer if
it matters. **[uncertain]** — flagged rather than inferred.

---

## 7. What the synthesizer must know

1. **The three `[insufficient evidence] in yoshiko-flow` items are resolved, all positive.** M2b,
   M6a and M6b are all **present** in yoshiko-flow. `triangulation.md` §4.1's prediction — that
   their absence was "unmeasured, not absent" — is confirmed exactly. M2b is now 4 repos; M6b is
   5 of 5 eligible repos; M6a is 4 repos.

2. **The yf and cross-repo clusters are now comparable on the review-pass axis.** Both have mined
   `reviews/pass-N.md` on the same axis with the same evidentiary standard. The counts still are
   not poolable — cross-repo reports *repos per class*, this cluster reports *instances per class*
   in one repo — but the **surface** gap §4.1 identified is closed.

3. **Revise the "review is weak on executable commands" calibration.** It is a property of a
   review practice that *reads*, not of review. yoshiko-flow reviewers **run** gate tests and
   demand negative controls ([2][3][29]), and they caught the "can never fail" M1 shard doing it.
   The corpus contains both the failure (d3-pxe) and the countermeasure (yoshiko-flow). The
   calibration that survives unchanged is **"review is weak on its own prior revisions"** — that
   one is confirmed here, repeatedly, and by self-attribution.

4. **Two new classes, both about the process's record of itself, both HINDSIGHT-clearing.** M6c
   (a resolution asserted but not landed — caused by a silent-no-op string replacement) and M14b
   (conformance findings leave no artifact). Both have a stated, checkable, mechanical remedy;
   one of them (M6c) is **already implemented** in `plan-043` pass 4 and demonstrably worked.
   M6c's generality is `[uncertain]` — all three instances are yoshiko-flow.

5. **M6c is M1 applied to the process's own bookkeeping.** This is the strongest structural
   observation available: the same "exit 0 while doing nothing" mechanism that appears in the
   reconciler (`yf-corpus:6`), in `bd`'s comma-joined list (`history-and-upstream:4`), and in
   d3-pxe's `curl -w` criterion (`cross-repo-corpus:6`) also appears **in the edit that records a
   review fix**. M1 and M5 are not separate stories from M6c; M6c is where they meet.

6. **Review depth here is not padding.** 41 of 42 pass-1s REVISE; 22 of 51 later passes still
   REVISE; 13 later passes carry a `high`. A `high` was found at pass 5. Any recommendation to cap
   review passes must contend with this.

7. **A delta-scoped pass does not discharge whole-plan review** ([24]). `plan-026`'s pass 4 found
   two mediums three prior passes missed, and named the reason as scope, not diligence. That is a
   checkable structural rule with a worked instance.

8. **The review surface is bundle-local and produces no remediation pairs** (A-1). It complements
   `cluster-yf-corpus.md` rather than overlapping it; neither is a substitute for the other, and
   the union is still bounded by C1 (M9).

9. **Carry the self-selection caveat.** Several of the sharpest quotes above are from plans whose
   *subject* is the review process (`plan-039` on classification, `plan-043` on reconciliation,
   `plan-041` on embed staleness). A repo that plans about its own planning will produce reviews
   that are unusually articulate about review defects. The *classes* are corroborated elsewhere;
   the *articulacy* is not general, and the apparent concentration of M6a/M6c in bundles 039–043
   is at least as consistent with **the repo having recently started looking for them** as with
   any change in defect rate. Do not read a trend into it.

10. **Do not treat the resolution tables as ground truth.** This cluster's own central finding is
    that they are unverified self-reports which have been wrong at least three times ([25][26][27]).
    Where I quote a `resolved` row above I am quoting a *claim*, and I have marked the two cases
    ([27], [31]) where a later pass independently verified it by grep.
