---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: cross-repo-corpus

Retrieval over the four **non-yf** repos in the corpus — `d3-pxe` (16 plans), `pybridge` (11),
`evri_py` (9), `emacs.d` (4). Method is `direct` per `plan.yaml`: providers are the local
filesystem, `git`, and `bd`. **No web leg.**

This cluster carries the **generality** signal. yoshiko-flow is the skill fixing itself; a defect
class that also appears in an Ansible homelab, a MATLAB/Python FFI bridge, and a Python
distribution repo is evidence about the *process*, not about the skill's self-selected defect
population.

## Method and scope

The Toolsmith's `remediation_pairs.py` proposed **38 candidate pairs** across these four repos
(d3-pxe 19, pybridge 11, evri_py 8, emacs.d 0). Candidates are inferences from textual, temporal,
artifact-overlap and git signals — nothing in a bundle declares "this fixes plan-013". I adjudicated
by reading both bundles for the higher-signal candidates and by direct grep across all four repos'
`reviews/`, `findings/` and `plan.md` surfaces.

Two deliberate method extensions beyond the candidate list:

1. **Within-bundle review chains.** The single richest defect evidence in this corpus is not the
   plan-to-plan pair at all — it is the `reviews/pass-N.md` sequence *inside* one bundle, where
   pass N names exactly what passes 1..N-1 missed or broke. That is a self-dated, self-attributed
   record of review failure, and it is far stronger than any inferred cross-plan pair. Several
   findings below rest on it.
2. **Absence checks** run directly (emacs.d cross-references, `git revert`, bead edges) rather than
   inherited from the tool.

### Limitations carried from the Toolsmith (verified, not assumed)

- **Bead corroboration is unavailable.** d3-pxe has 423 beads and 72 epics but only **4**
  `discovered-from` edges, and **zero** between two plan epics [29]. The machine-readable layer does
  not record the remediation relationship anywhere in this corpus; only prose does.
- **`git revert` never fires.** Exhaustive search of all refs in all four repos (767 commits) found
  no `Revert "..."` commit [30]. Remediation lands as forward `fix(...)` commits. Its absence carries
  no information.
- **`references/*.md` is quoted third-party text** (inlined upstream issue bodies). I have cited it
  only where the plan's own voice restates the same claim.
- **Artifact-path overlap is regex-mined from prose**, never resolved against the filesystem. I have
  not used it as independent evidence for any finding.

### Terminology

I distinguish two detection venues throughout, because they carry different weight:

- **Caught by review** — a `reviews/pass-N.md` concern. The process worked, though possibly late.
- **Caught by execution** — the defect survived every review pass and was found by running the
  thing. This is the population that matters for "which review pass should have caught it".

---

## Defect classes

### DC-1 — Structurally unsatisfiable gate

A plan declares a gate whose stated precondition cannot be produced, or an AUTO completion gate
whose closure set includes a bead that no agent can close. The plan is internally consistent
sentence by sentence and deadlocked as a whole.

**d3-pxe, plan-013 → plan-014 (CONFIRMED).** The strongest single pair in the cluster, because both
sides are first-party and self-incriminating. plan-014 names the defect:

> "plan-013 shipped a capability gate whose condition (\"operator has previewed the diff for issue X\")
> was unreachable because the gate blocked issue X *in its entirety*, including authoring the change
> to be previewed. It survived all three review passes and is filed upstream as
> [yoshiko-flow#112](https://github.com/dixson3/yoshiko-flow/issues/112)."
> — `Incubator/ansible/plans/plan-014-james-dixson-763edc/plan.md:143-147` [1]

plan-013 records the same event in its own amended text, adding the detection venue:

> "Gating this step made the gate's own precondition unreachable — the preview could never be
> produced, so the gate could never be satisfied. That deadlock was found mid-execution on
> 2026-08-12 after three review passes missed it, and is filed upstream as yoshiko-flow#112/#113."
> — `Incubator/ansible/plans/plan-013-james-dixson-1692d0/plan.md:345-349` [2]

plan-014's own review confirms the correction landed: the fix "is exactly the right correction of
plan-013's defect" [3].

**pybridge, plan-006 (CONFIRMED, caught by review pass 1).**

> "**M2** — Reconcile gate folds in `runAllTests.m` green, but `testArrayTransferMultiDim` is
> known-failing on main (`pybridge-jfc`) → gate can never go green."
> — `docs/plans/plan-006-james-dixson-8f91b1/reviews/pass-1.md:32` [21]

**evri_py, plan-007 (CONFIRMED, caught by review pass 1).**

> "The Reconcile Gate is \"auto (all execution beads closed),\" but 4.2 is blocked by an
> external-human gate an agent can never satisfy. If 4.2 stays open, the auto gate never fires and
> the plan can't complete."
> — `docs/plans/plan-007-james-dixson-8d1b13/reviews/pass-1.md:53-58` [26]

**evri_py, plan-008 (CONFIRMED, and review-induced — see DC-3).** Pass 3 found that the pass-2
revision made the Reconcile Gate block a bead that the Windows App Control gate can block
indefinitely [24].

**Generality:** three of four repos, in three unrelated domains (Ansible/Proxmox, MATLAB FFI, Python
packaging), with a **shared shape**: an automatic completion condition defined over a set that
contains a human- or externally-blocked element. Two of the four instances are specifically the
*reconcile/completion* gate.

**Preventable by a stated, checkable step?** **Yes.** The check is mechanical and writable today:
*for each gate, enumerate the beads/issues it blocks and assert that none of them is (a) required to
produce the gate's own precondition, or (b) itself blocked by a gate of a stricter kind.* The
d3-pxe instance is exactly (a); the pybridge and both evri_py instances are exactly (b). This is a
graph property of the plan's own declared structure, not a judgment call — so this passes the
HINDSIGHT bar without appeal to a smarter planner.

---

### DC-2 — Verification commands are read at review, not run

Plans author shell one-liners as success criteria and gate tests. Reviewers read them for intent.
Nobody executes them until execution, so a command that can never pass — or can never fail —
survives review, and can even be *praised* by it.

**d3-pxe, plan-010 (CONFIRMED; the densest instance in the cluster).** Four distinct sub-instances
across passes 3 and 4 of one bundle:

> "**The traces gate could not execute** — third consecutive pass for this one gate. […] Root cause
> named precisely: *the plan hand-rolled a transport that plan-008's convention deliberately does
> not use.*" — `.../plan-010-.../reviews/pass-4.md:53` [4]

> "**The PVE-token gate curl would always fail** — […] `curl -sf` exits 60 on TLS regardless of token
> validity. **Both prior passes *praised* this test.**" — `.../reviews/pass-3.md:53` [5]

> "SC13/SC14 printed an HTTP code but asserted nothing (`-w` always exits 0) — the only eyeball
> checks in an otherwise fail-closed set." — `.../reviews/pass-4.md:58` [6]

> "**The traces gate curl could never pass.** […] plan-008's own gate said \"a **bounded** SQL query\" —
> the signal dropped in translation." — `.../reviews/pass-3.md:52` (read in full; same table as [5])

The last line also names DC-2's cross-plan mechanism: the *convention* existed in the repo
(plan-008's `ansible.builtin.uri` shape), the later plan hand-rolled a substitute, and the substitute
was wrong three times running. The pass-4 fix was "adopting the convention instead of patching the
one-liner" [4].

**pybridge, plan-004 (CONFIRMED; the false-pass variant).** Here the command runs fine — it just
cannot observe the defect:

> "A single process map-then-unlink can never raise it → SC#3 + Tri-Platform Green go green while
> the real bug survives." — `docs/plans/plan-004-james-dixson-14d3b5/reviews/pass-1.md:20` [23]

**evri_py: NOT FOUND.** A targeted search of all evri_py `reviews/*.md` for unexecutable- or
non-discriminating-criterion language returned nothing. evri_py's success criteria are mostly CI-job
outcomes rather than hand-authored one-liners, which is a plausible structural explanation, but I
have no evidence for that mechanism beyond the absence itself. **[uncertain]**

**emacs.d: ABSENT.** No gate or criterion concerns of this shape in its four pass-1 reviews.

**Preventable by a stated, checkable step?** **Partly, and the partition is sharp.**

- *Yes* for the "can never fail" sub-class [6]: `curl -w` with no `-f`/comparison, a `[ … ]`-less
  print, an `-o /dev/null` with no exit assertion — all detectable by static inspection of the
  command string against a short deny-list. A stated rule ("every criterion must be an expression
  whose exit code varies with the property under test") would have caught SC13/SC14.
- *Partly* for "can never pass" [4][5]: `curl -sf` against a known self-signed endpoint is
  catchable by a stated rule ("a criterion's transport must match the repo's existing convention
  for that endpoint — cite the file it copies") — and that rule is exactly what the pass-4 fix
  amounted to. But `curl` not being installed in CT 104 is an environment fact no static rule
  reaches; only executing it, or a stated "dry-run every gate command in its declared venue before
  approval" step, catches that.
- *No* for the pybridge false-pass [23]: recognising that a single-process simulation cannot raise a
  cross-process lock error is a domain judgment. No checkable step gets there. I record this
  sub-instance as **not preventable by process**.

---

### DC-3 — Review-induced defects and incomplete remediation

The most consistent class in the cluster, and the only one confirmed in **all three** repos that run
multi-pass review. It has two sub-shapes:

**(a) Residue — a fix applied at the cited location but not at all locations.**

> "NEW (C1 residue) | Risks section (197-199) still says \"coordinate 3.2 with plan-005 … **land
> after plan-005** or guard by identity.\" plan-005 is merged; \"land after\" is meaningless."
> — pybridge `.../plan-006-.../reviews/pass-2.md:32` [19]

> "Success Criteria says \"#38 closed as a dup of #34\" — the exact reversal C6 fixed (table and
> Issue 1.6 correctly say close #34 as dup of #38). Executed literally, closes the wrong
> asset-referenced issue." — pybridge `.../plan-010-.../reviews/pass-2.md:30` [22]

**(b) Regression — the fix reintroduces the defect through a different mechanism, or preserves the
property that made it a defect.**

> "One new medium (NC5), introduced by the pass-2 revision itself: the Reconcile Gate now blocking
> `4.2` re-entangles the #7 macOS close with the indefinitely-blockable Windows gate — the exact
> contradiction NC2 removed, **reintroduced through the gate instead of the edge**."
> — evri_py `.../plan-008-.../reviews/pass-3.md:9-11` [24]

> "pass-3 replaced `/24` with six CIDRs \"verified to cover `.100–.149` exactly\" — **which is exactly
> what keeps SC9 unpassable.** The fix removed the `/24` while preserving the property that made the
> criterion false." — d3-pxe `.../plan-010-.../reviews/pass-4.md:55` [7]

evri_py plan-008 shows a **three-generation chain inside one bundle**: pass-2's revision introduced
NC5 [24]; the NC5 fix left a stale risk-table reference, found as NC6 at pass 4 [25]. pybridge
plan-010 pass-2's verdict line states the pattern outright: "the revisions introduced/left three
technical-correctness defects (N2/N3 would fail at execution) plus a re-introduced C6
contradiction" [22].

**A related structural limit, confirmed once:** review passes check their own concerns, never the
cross-product of previously accepted fixes.

> "A genuinely *new* interaction: pass-2's N5 hardening met EXP-003's scrape recipe, and neither pass
> looked at them together. Unaddressed, the scrape 401s […] and **SC16 and SC18 fail silently** on
> the plan's highest-blast-radius change." — d3-pxe `.../plan-010-.../reviews/pass-4.md:54` [8]

**Generality:** d3-pxe, pybridge, evri_py — all three multi-pass repos. **Absent in emacs.d**, and
the absence is structurally explained rather than meaningful: every emacs.d bundle has exactly one
review pass (`reviews/pass-1.md` only), so there is no pass-2 in which a pass-1 fix could regress.
The class requires N>1 passes to be observable at all.

**Preventable by a stated, checkable step?** **Sub-shape (a): yes.** "When resolving a concern, grep
the whole bundle for the corrected string/claim and list every site changed" is stated, checkable,
and would have caught [19], [22] and [25] — all three are the same string surviving in an
uncorrected third location. **Sub-shape (b): no.** Recognising that a gate-level constraint
re-imposes a dependency you just cut at the edge level [24], or that a narrowed CIDR set preserves
the containment property [7], is a semantic judgment about the revision. The best available stated
step is weaker and is a *targeting* rule, not a detector: "a pass that revises a gate or a
dependency edge must re-run the gate-reachability check from DC-1." That would have caught [24] and
plausibly [7]; it would not catch (b) in general.

---

### DC-4 — Stale internal cross-references after renumbering

Purely mechanical, appears in all three multi-pass repos, and is repeatedly found by a *human* at
pass 3 or 4 rather than by a tool.

> "**Four stale SC cross-references** after the SC14 insertion: R6→SC14 (now 15), R8→`SC13a`
> (**never existed**), R13→SC16 (now 17), Rollback→SC14 (now 15). Three pointed at a different
> *real* criterion." — d3-pxe `.../plan-010-.../reviews/pass-3.md:54` [9]

> "Stale bead naming. `pybridge-jfc` is now **CLOSED** […] plan.md still says `jfc` at line 131,
> 163-165, 177-178 (**Reconcile Gate carve-out** → references a bead that no longer exists under
> that name)" — pybridge `.../plan-006-.../reviews/pass-2.md:31` [20]

> "Risk-table row labeled the App-Control-blockable close-out `(4.2)` — stale after the NC5 fix"
> — evri_py `.../plan-008-.../reviews/pass-4.md:28` [25]

The d3-pxe instance carries the sharpest cost signal: three of four stale pointers resolved to a
*different real criterion*, so the plan read as coherent while pointing at the wrong thing. The
pybridge instance is load-bearing — a gate carve-out referencing a bead id that no longer resolves.

**Preventable by a stated, checkable step?** **Yes, and it should not be a review step at all.**
Every instance is a reference-resolution failure over identifiers the bundle itself defines
(`SC<n>`, `R<n>`, issue numbers) or that `bd` can resolve (bead ids). A linter over the bundle —
resolve every `SC\d+` / `R\d+` / `#\d+` / bead-id token against the set the bundle declares — is
fully mechanical. That three separate repos spent a human red-team pass on this is the cost.

---

### DC-5 — Plan scopes work an earlier plan already delivered

**pybridge, twice, against the same earlier plan (CONFIRMED).**

> "**Epic 2 has no kernel-stability bug to fix.** Building a fix against this premise is dead work."
> — `.../plan-006-.../findings/exp-002-spike-b-27-mechanism.md:48` [16]

The premise had been eliminated by two prior commits, one of them plan-002's (`05c903b`) and one
plan-003's (`a28b7f7`) [16]. Four months later, in a different plan:

> "**Verdict: B1 already exists in full (plan-002 Epic 4).** The plan should *reconcile*, not
> rebuild." — `.../plan-009-.../findings/exp-002-macos-gatekeeper.md:3` [17]

**Detection venue matters here, and it is good news.** Both instances were caught by the plan's own
**investigation spike**, before any epic executed — a stated process step doing exactly its job.
Neither reached execution. The residual defect is that the *intake / upstream-triage* pass, which
had already read the issue and the repo, did not check whether the issue was still live.

**d3-pxe and evri_py: PRESENT BUT CORRECTLY TRIAGED, not a defect.** Both repos show the same
situation resolved at intake instead of by a spike — d3-pxe plan-012 dispositions issue #10 as
"exclude | Already resolved by plan-011", and evri_py plan-003 dispositions `evri_py#3` as
"**supersede** | Done in plan-002". I therefore score DC-5 as **confirmed in pybridge only**, with
the other two repos providing the counterexample that the intake step *can* catch it.

**emacs.d: ABSENT** (no shared surface — see DC-8).

**Preventable by a stated, checkable step?** **Yes.** "For every upstream issue admitted to scope,
state the evidence that its premise still reproduces on today's `main`, or mark it unverified." Both
pybridge instances would have been caught, and d3-pxe/evri_py show the step is practicable because
their intake already does it informally.

---

### DC-6 — Unmeasured claim used as a decision rationale

A plan declines or shapes scope on a hazard it never characterises; a later plan measures it and
finds it smaller or different.

**d3-pxe, plan-011 → plan-012 (CONFIRMED).**

> "plan-011 recorded this as a reason to avoid TLS but never spelled it out. Measured: […] **This is
> materially less scary than plan-011 implied**, because the group and membership already exist and
> are recreated by the `ssl-cert` package on any rebuild."
> — `.../plan-012-.../findings/exp-001-002-acme-client-and-pg-tls.md:66,78` [10]

A second, independent rationale of plan-011's also failed, though not through anyone's error:

> "Which **invalidated the \"LAN-internal traffic\" rationale plan-011 gave for `ssl = off`**."
> — `.../plan-012-.../context.md:142` [11]

**I am deliberately not scoring [11] as a defect.** The same context.md states the widening was done
"deliberately, with a SPEC amendment, and with the trade-off recorded at the time," and that "This
plan is not fixing an oversight; it is paying a debt that was taken on knowingly." That is a
rationale correctly invalidated by a later, deliberate change — the process working. Only the
unspelled hazard [10] is the defect.

**Counter-evidence in the same bundle — review caught a finding's overreach.** plan-012's own EXP-002
concluded "so use the group"; its review overturned that:

> "**Superseded in part by D2 (review).** The measurement is correct, but the conclusion \"so use the
> group\" does not survive D1 […] The de-escalation of plan-011's vague hazard stands; the proposed
> mechanism does not." — `.../plan-012-.../plan.md:189-193` [12]

This is worth carrying to synthesis: review is demonstrably effective on **claims with a stated
mechanism** and demonstrably weak on **executable commands** (DC-2) and **its own prior revisions**
(DC-3).

**pybridge, adjacent variant (CONFIRMED).** The unverified-assertion-about-the-codebase form:
plan-006's review pass 1 records "**\"No kill/taskkill anywhere\" is false.** `PyBridge.m:165` already
does `kill -9 %d` inside `reinitialize()` (plan-002 E3.5)"
(`.../plan-006-.../reviews/pass-1.md:23`, read in full). Same root — a load-bearing claim asserted
without measurement — but caught at pass 1, not by a later plan.

**evri_py, emacs.d: NOT FOUND.**

**Preventable by a stated, checkable step?** **Yes, weakly.** "Any risk cited as the basis for
excluding or reshaping scope must name its mechanism and cite the observation, or be explicitly
marked unmeasured." That is stated and checkable by inspection. It would not have made plan-011
measure the hazard — but it would have forced the `[unmeasured]` label, which is what plan-012
actually needed and did not get.

---

### DC-7 — A later plan's claim about an earlier plan's artifact is wrong

**d3-pxe, plan-015 → plan-016 (CONFIRMED).** plan-016's `plan.md:83` states that plan-015 "proved the
signal and pinned the field (`body_unit`, **not** `body__systemd_unit`) but shipped a
**postgres-scoped** panel." Its own experiment then contradicts it:

> "## The plan-015 panel is already fleet-wide […] So it would **already render a pve backup-unit
> failure today**. Only its *placement* — on a dashboard titled \"PostgreSQL — CT 107\" — is
> postgres-scoped."
> — `.../plan-016-.../findings/exp-006-backup-observability.md:74,83` [13]

The finding reframes the work: "#76 partial is therefore about discoverability and app-level signal,
not about a broken query," and warns that the naive fix would have been "redundant noise."

**Confirmed only in d3-pxe.** I did not find this shape in the other three repos, but I also did not
search for it exhaustively — it has no distinctive keyword. **[uncertain]** on absence elsewhere.

**Preventable by a stated, checkable step?** **Yes.** "A claim about a prior plan's shipped artifact
must cite the artifact, not the prior plan's prose." plan-016 inherited the description from
plan-015's own summary rather than reading the panel's SQL; the experiment read the SQL and the claim
collapsed. This one is cheap and mechanical.

---

### DC-8 — A plan closes `complete` with its deliverable unproven or its scope unfinished

Confirmed in **three of four** repos. It is a lifecycle-policy property, not an execution slip —
every instance is deliberate and recorded.

**d3-pxe, plan-002 → plan-003.**

> "plan-002 formalized the `pve` host + Plex guest into Ansible roles but stopped at `--check --diff`
> (reconcile only, no converge). Three things were therefore **authored but never proven**"
> — `.../plan-003-.../plan.md:26-30` [15]

The unproven items were load-bearing: "Until the apply path is proven, **no guest in the backlog
(GH #6–#18) can actually be provisioned**" (same passage, read in full).

**evri_py, plan-003 → plan-004.** A whole plan exists solely as a carrier:

> "**Status:** approved (lightweight rollup; no review cycle) […] Complete the three work items
> deferred from plan-003 execution. […] This plan exists as a tracking surface so the items don't
> drift after plan-003 closed." — `.../plan-004-.../plan.md:6,16-18` [27]

Two secondary observations on this bundle: it has **no `reviews/` directory at all** — the
"lightweight rollup" path bypasses review entirely — and it is the only evri_py plan of nine in that
state.

**pybridge, plan-010 → plan-011.** plan-011's title is itself the evidence: "…and light
reconciliation of the plan-010 Windows-signing follow-ups (#35/#41/#45 deferred, #4 progress, file
enforcement anomaly)". Its scope table records "plan-010 is `complete`, but its tracking issue stays
open until the deferred Windows persistent-enforcement confirmation (via #45) lands"
(`.../plan-011-.../plan.md:81`).

**evri_py, plan-008 → plan-009** is a second instance in the same repo: "#54 | Stapleable .dmg […] —
defer from plan-008" (`.../plan-009-.../plan.md:46`).

**emacs.d: ABSENT.**

**Preventable by a stated, checkable step?** **No — and this is the important negative result of the
cluster.** In every instance the deferral was deliberate, recorded in the plan, and filed upstream at
the time (d3-pxe as GH #4/#5, evri_py as #13/#14/#15 and #54, pybridge as #35/#41/#45). No stated
step was violated. What the corpus shows is not a slip but a **missing lifecycle distinction**:
`complete` is used both for "delivered and proven" and for "delivered, proof deferred, tracked
elsewhere," and nothing in the artifact distinguishes them. A reader of plan-002's status field
cannot tell that its central mechanism was never executed. That is a design observation for
synthesis, not a preventable defect, and any "should have caught it" framing here would be hindsight.

---

## Presence / absence matrix

Scoring is per-repo and evidence-backed. `yes` = at least one candidate confirmed against both
artifacts. `not found` = searched, no instance located (a weaker claim than `absent`). `absent
(structural)` = absent with an identified structural reason.

| Defect class | d3-pxe | pybridge | evri_py | emacs.d |
| :-- | :-: | :-: | :-: | :-: |
| DC-1 Structurally unsatisfiable gate | yes [1][2] | yes [21] | yes [26][24] | absent |
| DC-2 Verification command read, not run | yes [4][5][6] | yes [23] | not found | absent |
| DC-3 Review-induced defect / residue | yes [7][8] | yes [19][22] | yes [24][25] | absent (structural: 1 pass) |
| DC-4 Stale internal cross-reference | yes [9] | yes [20] | yes [25] | absent |
| DC-5 Scopes already-delivered work | triaged, no defect | yes [16][17] | triaged, no defect | absent (structural: no shared surface) |
| DC-6 Unmeasured claim as rationale | yes [10] | yes (pass-1 C2) | not found | not found |
| DC-7 Wrong claim about a prior artifact | yes [13] | not found | not found | absent |
| DC-8 Closes `complete` while unproven | yes [15] | yes | yes [27] | absent (structural: no successors) |
| DC-9 Named defect shape recurs in-repo | yes [14] | not found | not found | absent |

Recurrence across repos, most general first:

| Defect class | repos confirmed | preventable by a stated, checkable step? |
| :-- | :-: | :-- |
| DC-3 Review-induced defect / residue | 3 of 3 eligible | (a) residue: **yes**; (b) regression: **no** |
| DC-4 Stale internal cross-reference | 3 of 3 eligible | **yes** — and it should be a linter, not a review pass |
| DC-1 Structurally unsatisfiable gate | 3 of 4 | **yes** — a graph property of the plan's own declarations |
| DC-8 Closes `complete` while unproven | 3 of 4 | **no** — no step was violated; the lifecycle lacks the distinction |
| DC-2 Verification command read, not run | 2 of 4 | **partly** — "can never fail" yes; "can never pass" partly; false-pass no |
| DC-6 Unmeasured claim as rationale | 2 of 4 | **weakly** — forces a label, not a measurement |
| DC-5 Scopes already-delivered work | 1 of 4 | **yes** |
| DC-7 Wrong claim about a prior artifact | 1 of 4 | **yes** |
| DC-9 Named defect shape recurs in-repo | 1 of 4 | not assessed (single instance) |

---

## Rejected candidates

A rejected candidate is a finding. Six rejections, in three groups.

### R-1, R-2 — pybridge plan-005 identifier collision (candidates 24 and 29)

The extractor emitted `plan-005-james-dixson-b3d15c → plan-006` and `plan-005-james-dixson-b3d15c →
plan-008` with **textual evidence byte-identical** to the corresponding `-7cfecd` candidates. Cause:
pybridge reuses plan number 005 across two bundles (the Toolsmith's declared warning), and the
matcher keys on the string `plan-005`.

**Rejected.** Every `plan-005` reference in plan-006 and plan-008 resolves unambiguously to
`-7cfecd`. plan-006's review pass 1 pins the referent to a specific merge — "**plan-005 is MERGED to
main** (`4356f52` + `739b33d`)" [18] — and its context.md:21 names the subject: "its inbound
object-semantics work — auto-registered `$handle` returns and identity-dedup (`_id_to_handle`,
kernel.py:56-95) — is already live". That is `-7cfecd`'s subject ("Inbound MATLAB→Python object-semantics", 2026-06-19).
`-b3d15c` is "Fix Windows Runner Issues & Create Platform Validation Workflows", dated 2026-03-29,
and shares no subject matter. Candidate 24 additionally reports "Artifact overlap: none detected"
and no git correlation — it rests on the collided string alone.

**Consequence for the synthesizer:** any plan-number-keyed analysis of pybridge is unsound. Bundle
hashes, not numbers, are the identity.

### R-3 — d3-pxe plan-010 → plan-011 as a *remediation* pair (candidate 2)

Highest quote count in d3-pxe (7 signals, 50+ mentions) and **not a remediation pair**. plan-011's
plan.md describes a deliberate, forward-looking split — "**011 lands first.** plan-010 takes a hard
dependency on it" (`.../plan-011-.../plan.md:57`), "plan-010 then becomes its first *client*, not its
owner" (:46). This is co-designed sequencing, not one plan fixing another.

**Generalisable warning:** dense cross-plan reference is a **coupling** signal, not a **remediation**
signal, and the two are indistinguishable to the extractor. The tool's `remediation` term list
(`follow-up`, `deferred`, `does not`, `stale`) fires on ordinary planning prose.

### R-4 — d3-pxe plan-011 → plan-012, the "LAN-internal traffic" half (part of candidate 11)

The rationale-invalidation [11] is real but was **not** a defect: the invalidating change was
deliberate, SPEC-amended, and recorded, and plan-012 says so explicitly. Only the unspelled hazard
[10] survives as DC-6. Rejecting half a candidate matters — an automated reading of candidate 11
would have double-counted.

### R-5 — d3-pxe plan-003 → plan-009 (candidate 5), git evidence

The pair is confirmable on textual grounds (plan-009 inherits plan-003's destroy+recreate runbook
because `raw_conf.yml` does not prune stale lines). But its sole git citation, `1be7ddcf4` "plan-013
Issue 5.3: fix the manifest drift 5.2 found", belongs to **plan-013** and is unrelated to either
member.

**Rejected as evidence, not as a pair.** The git signal matches commits *touching files that both
plans touched*, which for an infrastructure monorepo is nearly everything. Treat `git:fix` in this
corpus as co-location, not causation.

### R-6 — the `textual:split` signal on d3-pxe candidates 12 and 13

Both fire on `references/upstream-73.md:15`, "Split out of plan-014 (Issue 1.5) by operator
decision" — inlined **upstream issue body text**, i.e. the third-party quoted layer the Toolsmith
warned about, and it appears identically in two bundles because both reference the same issue. It
evidences an operator scoping decision, not a defect in plan-014.

---

## Absences

### A-1 — emacs.d: zero remediation pairs, verified genuine

Independently reproduced. Recursive grep for `plan-0[0-9][0-9]` in each of the four bundles,
excluding each bundle's own id, returned **zero** hits across all four [28]. This is not a tool
failure and not a small-N artifact.

The cause is structural and visible in the titles: "Bespoke agent-shell MCP editor-tools server",
"Enhance markdown-xwidget preview CSS", "Universal SPC leader, with evil confined to text-editing
modes", "Render CriticMarkup in the markdown-xwidget live preview". Four topically disjoint one-shot
changes to a personal Emacs config. **There is no accreting shared artifact surface** — no SPEC, no
role tree, no wire protocol, no release pipeline that successive plans both extend and depend on.

Two further structural facts compound it: every emacs.d bundle carries exactly **one** review pass,
and all four use the legacy `README.md` layout with no `index.md`/`log.md`.

**This is load-bearing for the generality claim.** emacs.d is not evidence that the defect classes
are absent from ordinary repos. It is evidence about their **precondition**: DC-1, DC-3, DC-5, DC-8
and DC-9 all require either multi-pass review or a shared surface that plans accrete onto. emacs.d
has neither. The honest statement is *"these classes need a repo where plans build on each other; in
a repo of independent one-shots they cannot arise"* — not *"these classes do not generalise."*

### A-2 — no `git revert` anywhere

Exhaustive across all refs in all four repos, 767 commits [30]. Every apparent hit was body-text
("correct stale … references", "restore local bundle_assets ownership"). Remediation is uniformly
forward `fix(...)`. **The absence carries no information** and must not be read as "few defects."

### A-3 — the bead graph records no cross-plan remediation

d3-pxe: 423 beads, 72 epics, **4** `discovered-from` edges, none between two plan epics [29]. I
verified this directly rather than inheriting it.

The consequence is a scope limit on this whole research project: **the remediation relationship
exists only in prose.** Every finding above rests on a human-written sentence in a `plan.md`,
`context.md`, `findings/*.md` or `reviews/pass-N.md`. Nothing machine-readable corroborates any of
them. A plan whose author did not *write down* that it was fixing a predecessor is invisible to this
method, and there is no way to estimate how large that population is.

### A-4 — no plan bundle declares a remediation relationship in a structured field

Consistent with the plan.yaml method note, verified across all four repos: no frontmatter key, no
`index.md` field, no reserved section names a predecessor-being-fixed. evri_py plan-004 comes
closest — `**Predecessor:** [plan-003-james-dixson-e2667b](../plan-003-james-dixson-e2667b/plan.md)`
at `plan.md:7` — but this is one bundle out of 40 in this cluster, it is hand-written prose in the
frontmatter block, and "predecessor" does not distinguish *fixes* from *follows*.

---

## What the synthesizer must know

1. **The review-pass sequence, not the plan-to-plan pair, is the highest-yield evidence surface in
   this corpus.** Six of nine classes are evidenced primarily from `reviews/pass-N.md`. The
   extractor was not built to mine it. If the yf cluster's retriever did not look there, the two
   clusters are not comparable on the same axis.
2. **DC-3 and DC-4 recur in every eligible repo and are the cheapest to fix** — one is a linter, the
   other is a grep-the-bundle discipline. DC-1 is nearly as general and is a pure graph check.
3. **The `complete` status is overloaded (DC-8)**, and I found no process violation behind it.
   Framing it as a defect would be hindsight; framing it as a missing lifecycle distinction is
   supported.
4. **Review is not uniformly weak.** It is effective on claims with a stated mechanism [12][18][21]
   [26] and weak on executable commands [5] and on its own prior revisions [24][7]. Any synthesis
   claiming "review lets X through" must say which X.
5. **Do not use plan numbers as identity** — pybridge reuses 005 (R-1/R-2), and d3-pxe splits plans
   across `Incubator/<slug>/plans/` and `docs/plans/` roots, so number order does not track either
   directory or dependency order.
6. **emacs.d's zero is about preconditions, not about generality** (A-1). Reporting it as
   "3 of 4 repos" without that qualification would misstate the evidence.
7. **`git:fix` and `artifact:path` signals are co-location, not causation** in monorepo-shaped repos
   (R-5). Neither should carry weight in a ranking.
8. **Nothing here is machine-corroborated** (A-3). Every finding is a first-party prose claim. They
   are mostly *self-incriminating* prose claims, which is the strongest available class — but the
   population of unrecorded remediations is unmeasured and unmeasurable by this method.
