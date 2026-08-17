---
type: Research Artifact
phase: triangulate
research: 004-plan-process-defect-mining
produced: '2026-08-16'
okf_spec: OKF-RESEARCH
---

# Triangulation — cross-cluster adjudication, credibility, consensus

Inputs: `cluster-yf-corpus.md`, `cluster-cross-repo-corpus.md`, `cluster-execution-telemetry.md`,
`cluster-history-and-upstream.md`, and the 100-source merged `sources.json`. `plan.yaml` was not
read. `docs/research/003-graph-engineering-hypothesis` was not read (blind-mining rule).

All citations are by composite `uid` (`<cluster>:<id>`), because cluster-local `[N]` markers
collide across artifacts — `[1]`, `[7]` and `[13]` each denote four different sources.

---

## 0. Credibility rubric (adapted — the default web rubric does not apply)

This corpus has **no web leg**. Every source is a plan bundle, a git commit, a bead, or a GitHub
issue in the operator's own repositories. Domain authority, publication currency and author
expertise do not discriminate between any two sources here, and `credibility_scorer.py` is
URL-shaped and was not run. Four axes were used instead, and are recorded per source in
`sources.json` as `credibility_score` / `credibility_category` / `credibility_reason`:

| Axis | Stronger | Weaker |
| :-- | :-- | :-- |
| Contemporaneity | recorded at the time — a commit, a bead close reason, a dated `reviews/pass-N.md` concern, a pre-registered risk | reconstructed later — a subsequent plan's Motivation prose |
| Self-interest | self-incriminating / against interest — a review pass naming what earlier passes missed; a plan disclosing its own deliverable's gap | self-exculpating — "this plan is not fixing an oversight" |
| Mechanical vs prose | reproducible — `git log -S` pickaxe, `bd` enumeration, a verified-absence grep | prose assertion with no re-runnable basis |
| Authorship voice | the bundle's own voice (`plan.md`, `findings/`, `reviews/`) | `references/*.md`, which inlines third-party upstream issue bodies |

Categories: `high_trust` (67), `verify` (29), `questionable` (4), `avoid` (0).

**The category split is itself a finding**, and it quantifies §4.1 below:

| Cluster | high_trust | verify | questionable | dominant source type |
| :-- | --: | --: | --: | :-- |
| cross-repo-corpus | 25 | 4 | 1 | contemporaneous `reviews/pass-N.md` concerns and investigation spikes |
| history-and-upstream | 20 | 5 | 3 | git commits/pickaxe and first-party issue bodies |
| execution-telemetry | 12 | 3 | 0 | live `bd` enumeration |
| yf-corpus | 10 | 17 | 0 | **later-plan Motivation prose** |

The yf cluster is the only one whose modal source is reconstructed self-diagnosis rather than a
contemporaneous or mechanical record. That is not a criticism of the retriever — it is the
consequence of the surface it chose (§4.1).

The four `questionable` sources are `cross-repo-corpus:30` (subject-only revert search, refuted —
§4.4) and `history-and-upstream:25/26/27` (raw `remediation_pairs.py` output — evidence about the
tool, never a denominator).

---

## 1. Merged defect-class table

Retriever labels were merged, split, or renamed as the evidence dictated. "Clusters" counts
**independent clusters** supplying at least one instance; "Repos" counts distinct repositories.

| id | Merged class | Absorbs | Clusters | Repos | Confidence |
| :-- | :-- | :-- | :-: | :-: | :-: |
| M1 | Succeeds visibly while doing nothing (silent no-op / false success / fail-open / exit 0) | yf "silent no-op"; cross-repo DC-2 **"can never fail" shard only**; history #129 | 3 | 2 | high |
| M2a | Blind gate — runs, passes, cannot see the evidence it governs | yf "gate placed where it cannot see the evidence" | 1 | 1 | moderate (in-repo) |
| M2b | Unsatisfiable gate — deadlock by construction | cross-repo DC-1 | 1 | 3 | high (in-cluster) |
| M3 | Deployed artifact diverges from its source; nothing verifies parity | yf "deployed artifact diverges"; history #137 | 2 | 1 | high (in-repo); generality **[insufficient evidence]** |
| M4 | Documentation diverges from the implementation it describes — detected precisely, fixed rarely | yf "authored content drifts"; history "doc↔impl reliably detected, reliably never fixed" | 3 | 3 | detection **high**; never-fixed **moderate** |
| M5 | **Prose-only enforcement does not bind** — a stated step nothing executes is reliably skipped, and no exit code records the skip | yf "instruction file states an invariant then violates it" + F4; history #135/#129; cross-repo DC-2 convention-drop + DC-3(a); telemetry stuck-bead sweep | 4 | 5 | **high** |
| M6a | Review-induced defect / regression (a fix that reintroduces or preserves the defect) | cross-repo DC-3(b) | 1 | 3 | moderate |
| M6b | Residue and stale internal cross-reference | cross-repo DC-3(a) + DC-4; history stale-literal commits + yf #135; telemetry `yf-m78m` | 3 | 4 | high |
| M7 | A load-bearing premise carried without verification | yf "premise inherited and never verified" + "heuristic with no measured baseline"; cross-repo DC-5, DC-6, DC-7 | 2 | 3 | high at parent; sub-shapes moderate |
| M8a | `complete` covers both "delivered and proven" and "delivered, proof deferred, tracked" | cross-repo DC-8; telemetry §7 | 2 | 4 | high — **and not a defect** (§4.2) |
| M8b | Undisclosed post-completion churn, absent from the bundle by construction | history §2.2, §2.3 | 1 | 2 | moderate-high |
| M9 | **The remediation relationship exists only in prose** — no structured, machine-readable record anywhere | all four clusters' Absences sections | 4 | 5 | **high** |
| M10 | Defects filed with a precise diagnosis and never routed into work | history §3.1–3.4; yf F3; telemetry §8 | 3 | 5 | high |
| M11 | Real-target / environment reality is discoverable only by running against the real target | telemetry §3c + §7; history §4.1; cross-repo DC-2 environment shard | 3 | 4 | high |
| M12 | One-directional reconcilers — the reverse edge has no verb at all | history #142/#143/#144; yf F3 | 2 | 1 | moderate (in-repo); generality **[insufficient evidence]** |
| M13 | *(method)* Extractor identity and attribution failure | yf rejected candidates; cross-repo R-1/R-2/R-5; history §5.1–5.3 | 3 | 5 | high |
| M14 | *(method)* The corpus cannot measure its own review-escape rate | yf Absences; history §7.4 | 2 | 5 | high (as an absence) |
| — | Declining discovery rate over time | telemetry §4 | 1 | — | **[insufficient evidence]** |
| — | DC-9 "named defect shape recurs in-repo" | cross-repo (matrix rows only) | 1 | 1 | **[insufficient evidence]** |
| — | DC-2 "false pass" shard (a test that cannot observe its target) | cross-repo pybridge plan-004 | 1 | 1 | **[insufficient evidence]** |

---

## 2. Adjudications the assignment asked for, explicitly

### 2.1 yf "gate placed where it cannot see the evidence" vs cross-repo DC-1 "structurally unsatisfiable gate" — **DIFFERENT CLASSES, shared parent**

These have **inverse outcomes** and must not be pooled.

DC-1's gate **never passes**:

> "plan-013 shipped a capability gate whose condition (\"operator has previewed the diff for issue X\")
> was unreachable because the gate blocked issue X *in its entirety*, including authoring the change
> to be previewed." — `cross-repo-corpus:1`

> "The Reconcile Gate is \"auto (all execution beads closed),\" but 4.2 is blocked by an
> external-human gate an agent can never satisfy. If 4.2 stays open, the auto gate never fires and
> the plan can't complete." — `cross-repo-corpus:26`

The yf gate **passes, and is blind**:

> "`plan_manager.py audit` is a **PLAN-phase gate**. It runs at Phase 3 and in `/yf-plan capture` —
> both *before* INTAKE. But `references/` and `reviews/` are largely authored during **EXECUTE** …
> Those files are created *after* the only gate that would check them, and no later gate re-runs it.
> Re-auditing the corpus today, **9 of 40 bundles fail**." — `yf-corpus:9`

The shared parent is *gate–evidence misalignment*; the children are disjoint and have opposite
symptoms (deadlock vs. false green) and opposite remedies (relax the closure set vs. move the
trigger). Split as **M2b** and **M2a**.

**The asymmetry is a method artifact, not a finding.** M2b appears in three non-yf repos and zero
yf instances; M2a appears in yf and zero non-yf instances. Every M2b instance is sourced from a
`reviews/pass-N.md` concern — the surface the yf retriever never opened (§4.1). M2b's absence from
yoshiko-flow is **unmeasured, not absent**. The converse holds too: M2a was found by re-auditing a
corpus of *completed* bundles, which the cross-repo retriever did not do.

### 2.2 yf "silent no-op / exit 0" vs cross-repo DC-2 "verification command read, not run" — **SPLIT DC-2; merge one shard**

DC-2 is not one class. Its own text partitions it three ways, and only the first is M1:

- **"can never fail"** — same mechanism as yf's silent no-op: a check that reports success
  unconditionally. > "SC13/SC14 printed an HTTP code but asserted nothing (`-w` always exits 0) —
  the only eyeball checks in an otherwise fail-closed set." — `cross-repo-corpus:6`
- **"can never pass"** — the *opposite* failure (permanent false red). > "`curl -sf` exits 60 on TLS
  regardless of token validity. **Both prior passes *praised* this test.**" — `cross-repo-corpus:5`
  This belongs with M2b (unsatisfiable) and M11 (environment), not with M1.
- **"false pass"** — a test that runs correctly but cannot observe its target. >"A single process
  map-then-unlink can never raise it → SC#3 + Tri-Platform Green go green while the real bug
  survives." — `cross-repo-corpus:23` Adjacent to M1 in symptom, different in cause (domain
  judgment, not a suppressed error). Single instance → **[insufficient evidence]** as a class.

DC-2's *framing* ("read at review, not run") is orthogonal to all three: it is a statement about
the **detection venue**, and it belongs to **M5**, not to a defect class of its own.

M1's merged evidence spans two clusters beyond yf, and the yf and history instances are the same
mechanism in different code:

> "The reconciler **was** dispatched, **did** parse the table correctly, and then **reported success
> without performing the `gh` writes** for the three `include` rows." — `yf-corpus:6`

> "A comma-joined list is matched by bd to ZERO beads while the process still exits 0 (bd 1.1.2), so
> a comma here is silent data loss, not a formatting nit." — `history-and-upstream:4`

> "this repo has **no `validate-cmd` configured**, so the merged-state validation emitted a \"CROSS-PLAN
> REGRESSIONS NOT CHECKED\" notice and proceeded on plan-gate coverage only (a false green) … it
> **fails open**." — `yf-corpus:15`

> "The failure was **silent** — wrapped in `json-get` + capture-and-continue, so wisp tracking
> degraded to a no-op with no operator-visible error." — `yf-corpus:16`

**Confidence: high.** Three clusters, six instances, two repos. **Generality is the weak leg** — five
of six instances are yoshiko-flow, which is the self-selected corpus. The class is real; its
*frequency* outside yf is unmeasured.

### 2.3 yf "deployed artifact diverges from source" vs history "doc↔impl divergence never fixed" — **DIFFERENT CLASSES**

M3 is a **parity** failure: two copies of the *same* artifact, one stale.

> "**(1a) Embed staleness, on ADDITION only.** A file or directory *added* under `skills/` is
> invisible to an incremental release rebuild … The failure is silent and self-concealing …
> `cargo build --release` exits `0`, `yf self install` reports `{\"status\":\"ok\"}`" — `yf-corpus:11`

> "this session drafted its plan using the **stale v0.4.0 `yf-plan` skill** … The skill describing
> the process and the repo defining it disagree, and the operator is following the older one."
> — `yf-corpus:13`

M4 is a **description** failure: two *different* artifacts, one purporting to describe the other.

> "The docs still imply execution can \"span multiple environments\" via shared beads. Reality: the
> bead DB is **local** to one repo clone" — `yf-corpus:22`

> "`#55` (*\"PyBridge.status() docstring promises {pid, uptime_seconds}; actual return has no pid\"*)
> … a doc↔impl divergence — the exact axis `yf-drift-check` covers — surviving in an OPEN issue
> rather than a fix." — `history-and-upstream:22`

The yf cluster itself lists these as two separate rows in its own class table; that split is
correct and is preserved. They differ in remedy: M3 needs a build/deploy parity check, M4 needs a
cross-artifact agreement check.

**Do not let history's `#137` corroborate M3's generality.** `history-and-upstream:11` and
`history-and-upstream:12` are the *same underlying event* as `yf-corpus:11`, reached by a different
route (issue body + commit, vs. plan prose). That is strong corroboration of the **fact** and
**zero** corroboration of **generality**. M3 has no non-yoshiko-flow instance anywhere in 100
sources, and yoshiko-flow is a build-and-deploy tool, which is precisely the self-selection the yf
retriever warned about. **M3 generality: [insufficient evidence].**

M4 fares better: yf (1), pybridge #55, evri_py #60, plus telemetry's independent instance —

> `yf-m78m` ← `yf-mol-3ct.3.3`: *"yf-plan README.md stale: still lists README.md as plan-folder
> orientation file (pre-OKF), contradicts index.md/log.md in SPEC REQ-PLAN-010 + SKILL.md"*
> — `execution-telemetry:6`

Three clusters, three repos. **Detection: high confidence.** The stronger half of history's claim —
*"reliably DETECTED and reliably NOT FIXED"* (`history-and-upstream:22`) — rests on three open
issues in two repos with no denominator of doc↔impl defects that *were* fixed. **Moderate**, and
the synthesizer must not state a rate.

### 2.4 M5 — the class the merge actually produces, and the report's likely headline

Four separate retrievers, working four disjoint surfaces, each independently arrived at *a written
rule that does not bind*. None of them named it as the same class. It is.

| Cluster | Instance | Quote (uid) |
| :-- | :-- | :-- |
| yf-corpus | reconciler step 4 existed and was skipped | "Step 4 **is** the post-reconcile verification the plan intends to add. It was ignored exactly as step 3 was. **Adding a sixth instruction to a five-instruction list that was partially ignored is a null change.**" — `yf-corpus:7` |
| yf-corpus | the rule and the procedure contradict each other | "`SKILL.md` Push step §3 then documents the hand-run command as *the* procedure. An operator or agent that follows the skill violates the rule." — `yf-corpus:20` |
| history-and-upstream | a plan violated the rule it had just written | "plan-039 **diagnosed this failure mode and encoded the rule** … It then violated that rule once more, in Issue 3.1, and nothing caught it until execution. … **prose guidance inside a plan does not bind the plan's other sections.**" — `history-and-upstream:24` |
| history-and-upstream | the rule failed in the code that implements it | "the skill's own rule requires the write be *\"verified STRUCTURALLY, and an exit 0 is not proof.\"* The defect is precisely an exit-0-is-not-proof failure, in the code that implements that rule." — `history-and-upstream:4`, `history-and-upstream:5` |
| cross-repo-corpus | the repo's convention existed and the plan hand-rolled a substitute | "*the plan hand-rolled a transport that plan-008's convention deliberately does not use.*" — `cross-repo-corpus:4` |
| execution-telemetry | a mechanism specified everywhere, never once observed to fire | "A case-insensitive grep for `stuck[- ]bead` across the plan bundles of all five repos returns **only design and spec text — no log line, no close reason, no finding recording a sweep that ran or a bead it reset**" — `execution-telemetry:13` |

The generalisable statement is `yf-corpus:7`'s, and the telemetry instance is its mechanical proof
over five repos: **a step with no exit code is not a step.** Confidence **high** — four clusters,
five repos, and the telemetry and history legs are mechanical rather than prose.

**One counter-quote must travel with it**, or the claim overreaches:

> "plan-043 records that the same prose reconciled correctly for plan-040 and plan-041, so the
> variable is agent diligence, not a deterministic bug. That weakens \"the prose is broken\" into
> \"the prose is unreliable\" — a materially different claim the synthesizer must preserve."
> — `cluster-yf-corpus.md`, F4 counter-evidence

### 2.5 M7 — four retriever labels, one class

yf's "premise inherited and never verified", yf's "heuristic shipped with no measured baseline",
cross-repo's DC-5 (premise already delivered), DC-6 (premise never measured) and DC-7 (premise
inherited from prose instead of the artifact) are five shards of **a load-bearing premise carried
without verification**, differing only in *why* it was not verified:

| Sub-shape | Instance | Quote (uid) |
| :-- | :-- | :-- |
| never established | "#133 establishes that this was never justified anywhere in the repo — `SPEC.md` presupposes it (REQ-BUP-030/031) without arguing for it. It was inherited because bd 1.0.5 happened to ship the feature." | `yf-corpus:1` |
| true only in an untested mode | "That premise … only holds in dolt **server** mode. For the embedded-storage layout … the cruft-suppressed default this skill itself creates, `bd dolt stop` errors" | `yf-corpus:18` |
| no longer true | "**Epic 2 has no kernel-stability bug to fix.** Building a fix against this premise is dead work." | `cross-repo-corpus:16` |
| never measured | "plan-011 recorded this as a reason to avoid TLS but never spelled it out. Measured: … **This is materially less scary than plan-011 implied**" | `cross-repo-corpus:10` |
| never measured (shipped) | "**Current precision is 1/17, with `TN=0`** — it has never produced a correct negative." | `yf-corpus:21` |
| taken from prose, not the artifact | "## The plan-015 panel is already fleet-wide … Only its *placement* … is postgres-scoped." | `cross-repo-corpus:13` |

Two clusters, three repos, six instances. **Parent: high.** Each sub-shape individually is 1–2
instances and should be reported as an illustration, not as a rate. Note that DC-5's two instances
were **caught by the plan's own investigation spike before any epic ran** — which is M11's positive
finding, not a failure.

---

## 3. Consensus findings (3+ independent sources, cross-cluster)

### C1 — The remediation relationship exists only in prose. Nothing machine-readable records it. (M9)

**Four of four clusters. All mechanical. All independently derived.** This is the highest-confidence
finding in the triangulation and the one that bounds everything else.

> "0 of 53 `discovered-from` edges connect two plan epics … `discovered-from` in this corpus records
> *\"execution spawned new work\"*, never *\"plan B remediates plan A\"*. **A remediation pair is
> therefore not recoverable from the bead graph**" — `execution-telemetry:6`

> "d3-pxe has 423 beads and 72 epics but only **4** `discovered-from` edges, and **zero** between two
> plan epics. The machine-readable layer does not record the remediation relationship anywhere in
> this corpus; only prose does." — `cross-repo-corpus:29`

> "**No plan bundle declares its own remediation target.** Nothing in the OKF schema … has a \"fixes
> plan-NNN\" field. Every pair above was confirmed from **prose in the Motivation section**."
> — `cluster-yf-corpus.md`, Absences

> "**No commit anywhere in the corpus explicitly names a prior plan as the source of a defect it is
> fixing.** … The plan→defect→plan edge is never recorded in git … **The corpus has no
> machine-readable remediation edge.**" — `cluster-history-and-upstream.md` §6, `history-and-upstream:1`

The near-miss, recorded for accuracy: evri_py plan-004 carries `**Predecessor:**` in its frontmatter
— one bundle in 40, hand-written, and "predecessor" does not distinguish *fixes* from *follows*
(`cross-repo-corpus:27`).

**The consequence is a hard recall bound on this entire research project.** A plan whose author did
not *write down* that it was fixing a predecessor is invisible to every method used here, and the
size of that population is not estimable from this corpus. Every rate, count and "N of M repos" in
the report is a **lower bound over the recorded subset**, never a prevalence.

**Confidence: high.**

### C2 — A stated step that nothing executes is reliably skipped (M5)

Four clusters, five repos — see §2.4 for the full quote set. **Confidence: high.**

### C3 — Defects are filed with precise diagnoses and then not routed into work (M10)

> "`grep -rl '#N' docs/plans docs/research` over every yoshiko-flow bundle returns **no hits** for
> **#142, #143, #144, #147**. All four are OPEN. All four are *process* defects discovered by
> *executing* an earlier plan." — `history-and-upstream:13`

> "Folding this into #51 would let it be closed by work that never addressed it — which is exactly
> the failure mode this issue is about." — `history-and-upstream:21` (d3-pxe #76; the author
> pre-emptively defends against the process mis-absorbing the issue)

> "Three of pybridge's four open follow-ons were created in the **same second** … from one parent,
> `pybridge-hax` … a fan-out of a known-unknown into three named beads, none since actioned."
> — `execution-telemetry:6`, `cluster-execution-telemetry.md` §8

> "Honest disclosure was treated as sufficient. Nothing in the process turns a self-declared coverage
> gap into a tracked obligation with an owner — the gap lived in prose inside a `complete` plan,
> where nothing reads it." — `cluster-yf-corpus.md` F3, on `yf-corpus:3`

Three clusters, five repos, 10 of 53 `discovered-from` beads still open. **Confidence: high**, with
one mandatory caveat the retriever supplied itself: the four yoshiko-flow issues were filed within
~24h of retrieval, so "never planned" is partly a recency artifact there. The pybridge, d3-pxe and
emacs.d instances span weeks to months and do not carry it — **weight those, not the yf four**.

### C4 — Reality at the real target is not reachable by any review step (M11)

> "`0be3064` plan-003 3.1: **apply-path fixes discovered running the live converge**; `3f29a13`
> plan-008 Epic 1: **fixes found during live apply on CT 104**; `1f7feca` sign actions: **fix
> runner-environment failures found by the test build**" — `history-and-upstream:23`,
> `history-and-upstream:9`

> "The dominant subject is **environment / platform / toolchain reality** (cmake PATH, WDAC policy,
> CRLF autocrlf, MAX_PATH, PVE config canonicalization, Gatekeeper, glibc floor)"
> — `cluster-execution-telemetry.md` §3c, on `execution-telemetry:6`

> "`curl` not being installed in CT 104 is an environment fact no static rule reaches; only executing
> it … catches that." — `cluster-cross-repo-corpus.md` DC-2

Three clusters, four repos. **Confidence: high.** And it has a **positive counterpart with equal
confidence** — the corpus records the countermeasure that demonstrably worked:

> "**R1 — a v0.1.32 probe may fail** … If an Epic 0 probe fails, it is a **pybridge regression** …
> **reopen the corresponding pybridge issue** … and mark that single rewrite **blocked pending
> pybridge**" — `execution-telemetry:11`, pre-registered, then: "`2026-06-21 executing: R1 fired for
> #10 — pybridge#10 REOPENED`" — same source, dated phase log.

> "**Structurally un-previewable** … **exp-011 §6 pre-registered exactly this residual risk and it
> fired.**" — `execution-telemetry:12`

> Both pybridge DC-5 instances "were caught by the plan's own **investigation spike**, before any
> epic executed — a stated process step doing exactly its job. Neither reached execution."
> — `cluster-cross-repo-corpus.md` DC-5, on `cross-repo-corpus:16`, `cross-repo-corpus:17`

The recurring shape of what works is **a capability probe or spike placed before the dependent work,
plus a named risk with a written response**. That is the corpus's strongest prescriptive signal and
it is *not* "add another review pass".

### C5 — Residue and stale internal cross-references recur everywhere, including yoshiko-flow (M6b)

> "**Four stale SC cross-references** after the SC14 insertion: R6→SC14 (now 15), R8→`SC13a`
> (**never existed**) … Three pointed at a different *real* criterion." — `cross-repo-corpus:9`

> "Stale bead naming. `pybridge-jfc` is now **CLOSED** … **Reconcile Gate carve-out** → references a
> bead that no longer exists under that name" — `cross-repo-corpus:20`

> "`285f528` *\"fix stale AGENTS GPU fact\"*, `f68a1f9` *\"three stale rationales struck\"*, `58ed894`
> *\"correct the stale note\"*, `7ee7679` *\"correct stale 192.168.7.115 control-node references\"*"
> — `history-and-upstream:23`

> yoshiko-flow #135 reports "**four instances in one plan**, one of which escaped to execution"
> — `history-and-upstream:24`

Three clusters, four repos **including yoshiko-flow**. **Confidence: high.** Note carefully: the yf
*cluster* did not report this class at all; the yf *repo* has it, found by a different cluster. That
is direct proof that §4.1's method gap costs real recall.

Both the cross-repo retriever's remedy and its cost assessment survive triangulation:

> "**Yes, and it should not be a review step at all.** … A linter over the bundle — resolve every
> `SC\d+` / `R\d+` / `#\d+` / bead-id token against the set the bundle declares — is fully mechanical.
> That three separate repos spent a human red-team pass on this is the cost."
> — `cluster-cross-repo-corpus.md` DC-4

### C6 — The extractor's candidate set is unsound in both directions (M13)

> "**Repo-blind plan-number matching** produces cross-repo false pairs … **Detector-vs-builder
> conflation.** … Three of the pairs examined here needed redirection."
> — `cluster-yf-corpus.md`, Rejected candidates

> "pybridge reuses plan number 005 across two bundles … the matcher keys on the string `plan-005` …
> **any plan-number-keyed analysis of pybridge is unsound. Bundle hashes, not numbers, are the
> identity.**" — `cluster-cross-repo-corpus.md` R-1/R-2

> "The extractor proposes **eight** earlier plans for plan-038 … The **actual** author of the defect,
> plan-013, is not among them. Authorship is recoverable only by pickaxe … **Precision and recall
> both fail on the one pair that git can prove.**" — `history-and-upstream:27`, `history-and-upstream:3`

> "dense cross-plan reference is a **coupling** signal, not a **remediation** signal, and the two are
> indistinguishable to the extractor." — `cluster-cross-repo-corpus.md` R-3

Three clusters. **Confidence: high.** Operational consequence: **83 candidates is not a denominator**
and no "N of 83" rate may appear in the report.

---

## 4. Contradictions — surfaced and adjudicated

### 4.1 Are the yf and cross-repo clusters comparable? **NO. Verified mechanically. This is a first-class method finding.**

The cross-repo retriever's warning:

> "**The review-pass sequence, not the plan-to-plan pair, is the highest-yield evidence surface in
> this corpus.** Six of nine classes are evidenced primarily from `reviews/pass-N.md`. The extractor
> was not built to mine it. If the yf cluster's retriever did not look there, the two clusters are
> not comparable on the same axis." — `cluster-cross-repo-corpus.md` §"What the synthesizer must know"

**Verified against `sources.json` and against the repo:**

| Measure | Value |
| :-- | --: |
| cross-repo-corpus sources citing a `reviews/pass-N.md` | 16 of 30 |
| execution-telemetry sources citing a `reviews/pass-N.md` | 1 of 15 |
| history-and-upstream sources citing a `reviews/pass-N.md` | 0 of 28 |
| **yf-corpus sources citing a `reviews/pass-N.md`** | **0 of 27** |
| `reviews/pass-*.md` files that exist in yoshiko-flow `docs/plans/` | **93** |
| yoshiko-flow bundles with ≥2 review passes | **29 of 43** |

*(The last two rows are structural verification run by this triangulator to test comparability. No
new defect claim is drawn from them.)*

**Verdict: the warning is correct and understated.** The yoshiko-flow corpus contains 93 review
passes across 43 bundles — the largest such surface in the corpus, with one bundle carrying seven
passes — and the yf cluster cited exactly zero of them. Its two review-pass-derived findings (F4's
"survived three review passes", F15's pass-1/pass-2 concerns) reach the review layer **only through
a later plan's prose quoting it**, never by reading a pass file.

Three consequences the synthesizer must carry:

1. **The clusters measure different things and their counts cannot be pooled.** yf reports
   *instances per class*; cross-repo reports *repos confirmed per class*. Neither denominator is the
   other's, and neither surveys the other's surface.
2. **Every cross-repo class absent from the yf list is UNMEASURED in yoshiko-flow, not absent** —
   specifically M2b (DC-1), M6a (DC-3) and M6b (DC-4). §3 C5 proves this is not hypothetical: M6b
   *is* present in yoshiko-flow, and only a third cluster found it.
3. **Symmetrically, every yf class absent from the cross-repo list is unmeasured there** — M2a, M3,
   M12. The cross-repo retriever never re-audited completed bundles or inspected build/deploy parity.

This asymmetry is the single largest threat to any "class X generalises / does not generalise"
statement in the report. It is **not** a defect in either retriever; it is an un-reconciled scope
difference that only became visible at triangulation.

### 4.2 Is DC-8 ("closes `complete` while unproven") a defect? **NO for what DC-8 describes. But history found a genuinely different thing wearing the same name — SPLIT into M8a and M8b.**

The cross-repo argument, which I accept:

> "**No — and this is the important negative result of the cluster.** In every instance the deferral
> was deliberate, recorded in the plan, and filed upstream at the time … No stated step was violated.
> What the corpus shows is not a slip but a **missing lifecycle distinction**: `complete` is used both
> for \"delivered and proven\" and for \"delivered, proof deferred, tracked elsewhere,\" and nothing in
> the artifact distinguishes them." — `cluster-cross-repo-corpus.md` DC-8

**Execution-telemetry independently corroborates the "process held" reading**, from a different
surface (bead close reasons) and without having read the cross-repo cluster:

> "A plan closed `complete` with **4 of its ~6 work units deliberately not done** … The bundle labels
> this honestly (\"PARTIAL LANDING\", \"plan closed (partial)\"). Per the HINDSIGHT RULE this is **not**
> a preventable planning defect: the checkable step (Epic 0 capability probe + R1) existed and
> worked." — `cluster-execution-telemetry.md` §7, on `execution-telemetry:10`, `execution-telemetry:11`

> "Note the override is *self-documenting and traced*: it names the blocking cause, disclaims plan
> fault, and points at the bead that carries the deferred work … The gate mechanism degraded
> honestly." — `execution-telemetry:9`

**No cluster treats deliberate recorded deferral as a defect.** There is no contradiction to resolve
on M8a: two clusters agree, from independent surfaces, that it is a lifecycle-vocabulary gap.
**Confidence: high, as a design observation.**

**However** — history found a case that is *not* deliberate, *not* recorded, and *not* filed, and it
is not DC-8:

> "The log jumps **rc1 → rc9**. The intervening work exists only in git … Several of these defects
> are in the plan's **own test commands**, not the deliverable … `97ced85`: *The bundle itself was
> already correct; this makes the test faithful.* … Seven RC iterations' worth of defect content …
> is **absent from the bundle by construction**." — `history-and-upstream:8`, `history-and-upstream:9`

> "Between plan-010's completion commit … and plan-011's approval commit there are **14 commits, 12
> of them touching `.github/workflows/release.yml`** — the exact artifact plan-010 delivered … *none*
> of those 12 carries a `fix` prefix." — `history-and-upstream:7`

That is **M8b: undisclosed post-completion churn**, and it is a real defect of the *record* rather
than of the plan. It has a hindsight-clearing remedy history states precisely:

> "a **rule that a success criterion verifiable only by the real pipeline may not be marked met
> before that pipeline runs green.** That rule is checkable and did not exist."
> — `cluster-history-and-upstream.md` §2.3

**Confidence: moderate-high** (one cluster, two repos, but the evidence is git — mechanical and
contemporaneous). Its consequence is corroborated by two other clusters and is high-confidence in
its own right: **any escape rate computed from plan bundles alone is understated**, and understated
most for exactly the plans whose deliverable is only verifiable in CI (`history-and-upstream:8`) —
which composes with telemetry's finding that 51 of 55 plans added nothing to their own molecule
after pour (`execution-telemetry:7`).

### 4.3 emacs.d — clean, or unmeasured? **UNMEASURED. The two clusters compose into one answer; neither alone is sufficient.**

cross-repo's structural argument:

> "**There is no accreting shared artifact surface** — no SPEC, no role tree, no wire protocol, no
> release pipeline that successive plans both extend and depend on … every emacs.d bundle carries
> exactly **one** review pass … DC-1, DC-3, DC-5, DC-8 and DC-9 all require either multi-pass review
> or a shared surface that plans accrete onto. emacs.d has neither."
> — `cluster-cross-repo-corpus.md` A-1, on `cross-repo-corpus:28`

history's positive evidence:

> "emacs.d carries 178 commits, of which **27 begin `fix`**, against **4 plan bundles** and **zero**
> upstream plan-tracker issues … **no `fix` commit in the repo is attributed to any plan**. In this
> repo the plan process is a thin overlay on an otherwise unplanned fix stream."
> — `history-and-upstream:19`, `history-and-upstream:1`

> "Both cite the same upstream issue #5; the second reverses the first's `reserve-rows` default
> (`0` → `1`) … **Three commits, one symptom, ~22 hours, no plan, no red-team.**"
> — `history-and-upstream:20`

**Adjudication: these do not conflict — they compose, and history supplies the evidence cross-repo's
structural argument predicted but could not produce.** emacs.d has abundant defect activity
(27 `fix` commits; a same-symptom fix-of-a-fix inside 22 hours, which is a DC-3(b)-shaped regression
occurring entirely outside the plan process). That activity simply never enters the plan process, so
a plan-bundle method cannot see it — which is *also why* no shared surface accretes.

**emacs.d is therefore a coverage floor for the method, not a clean repo.** Two prohibitions follow:

- Do **not** write "3 of 4 repos" without the qualification. cross-repo's warning stands verbatim:
  > "Reporting it as \"3 of 4 repos\" without that qualification would misstate the evidence."
- Do **not** write or imply "emacs.d is clean" or "emacs.d's plan process produced no defects." That
  is flatly contradicted by `history-and-upstream:19` and `history-and-upstream:20`.

The honest formulation is cross-repo's, with history's addition: *these classes require a repo where
plans build on each other and are reviewed more than once; in a repo of independent one-shots whose
fix stream bypasses planning entirely, they cannot be observed.*

**Confidence: high** on "unmeasured"; **[insufficient evidence]** on the actual defect rate of
emacs.d's *plan process*, which cannot be computed from four one-pass bundles.

### 4.4 `git:revert` = 0 — **the two subject-line clusters are wrong on the count; history is right. All three are right on the conclusion.**

> "**No `git revert` anywhere in the corpus.** … `git log --grep=revert -i` returns two commits, both
> plan-033 intake/execute commits whose bodies merely contain the word." — `yf-corpus:26`

> "Exhaustive across all refs in all four repos, 767 commits. Every apparent hit was body-text
> (\"correct stale … references\", **\"restore local bundle_assets ownership\"**)."
> — `cross-repo-corpus:30`

> "the one semantic revert that exists does **not** start with \"Revert\" — evri_py `db41594`
> *\"bundler: restore local bundle_assets ownership; capture intent in SPEC\"*, whose body reads:
> *Reverts 5d03ddc's PYBRIDGE_REPO dependency* … So subject-only revert detection has **100%
> false-negative rate on the corpus's only revert.**" — `history-and-upstream:28`

**The two clusters looked at the same commit and classified it oppositely.** cross-repo saw
`db41594` in its results and dismissed it as body-text noise on the strength of its subject line;
history read the body, which says "Reverts 5d03ddc" explicitly. **History's reading is correct**, and
`cross-repo-corpus:30` is scored `questionable` in `sources.json` for this reason.

Downstream impact is nil, because all three clusters reach the same conclusion by different routes:
remediation in this corpus lands as forward fix commits, the absence of reverts is a **convention**
and carries no quality information. The method lesson does travel: **any revert-based signal must
search commit bodies**, and `git:revert = 0` must never appear in the report as a finding.

Note the adjacent, independently confirmed unsoundness of the sibling signal:

> "Prefix counts: yoshiko-flow 5, d3-pxe **0**, pybridge 26, evri_py 20, emacs.d 27. **d3-pxe scores
> zero `fix`-prefix commits while demonstrably fixing things in almost every plan** … Any cross-repo
> comparison of \"fix density\" from subject prefixes is invalid." — `history-and-upstream:1`

This also invalidates the *numeric* half of `yf-corpus:26` ("only **7** `fix`-prefixed commits in
393") as a cross-repo comparator, though its conclusion — git conventions carry no remediation
signal here — is corroborated three ways and stands.

### 4.5 The declining-discovery trend — **NOT upgraded. [insufficient evidence]. Two clusters actively support the rival explanation.**

telemetry's own verdict:

> "**Verdict: DOWNWARD-LEANING, LOW CONFIDENCE. Do not draw a line through this.** … 39 of 55 plans
> score 0. The whole signal is 24 events … The pooled 0.667 → 0.214 drop is substantially a change of
> *which repos are being measured*, not of *how plans perform*."
> — `cluster-execution-telemetry.md` §4

> "**`discovered-from` is optional and unenforced.** No manifest, gate, or checked step in any repo
> requires attaching it. This is why §4's trend cannot be trusted."
> — `cluster-execution-telemetry.md` §9.6

> "roughly half of the free-standing beads created during the window carry no `discovered-from` edge
> at all … Nothing in the corpus requires the edge, so its presence measures operator habit as much
> as it measures discovery." — `execution-telemetry:8`

**Two other clusters supply direct evidence for the instrumentation explanation**, which telemetry
could not see from the bead graph alone:

- The corpus's **largest single remediation episode** — pybridge plan-010's 12 post-completion
  `release.yml` commits — produced **zero** beads and **zero** `fix`-prefixed subjects
  (`history-and-upstream:7`). Real discovery, invisible to both instruments.
- Eight RC-fallout fix commits, including two defects in the plan's own success criteria, are
  **absent from the bundle by construction** (`history-and-upstream:9`).
- Zero of 53 edges records a remediation relationship at all (`execution-telemetry:6`,
  `cross-repo-corpus:29`), so the metric was never measuring the quantity a "process improved" claim
  would need.

**Verdict: [insufficient evidence].** The recorded discovery rate fell; whether discovery fell is
unresolved and — on this corpus — unresolvable. Any sentence of the form "the process improved over
time" is over-reading, and the falling series is at least as consistent with *the instrument being
used less* as with *there being less to find*.

---

## 5. Marked `[insufficient evidence]`

| Item | Sources | Nature | Why it stays here |
| :-- | :-: | :-- | :-- |
| Declining discovery rate over time | 1 cluster (telemetry §4) | derived rate, n=24 events over 55 plans | Retriever's own LOW-confidence label; two independent clusters supply a live rival explanation (§4.5) |
| M3 generality (deploy-parity divergence outside yoshiko-flow) | 2 clusters, **1 repo**, same underlying events | prose + issue + commit | Zero non-yf instances in 100 sources; yf is a build-and-deploy tool — textbook self-selection |
| M12 generality (one-directional reconcilers) | 2 clusters, **1 repo** | 3 open issues + 1 plan disclosure | All yoshiko-flow; all four issues filed within ~24h of retrieval (recency artifact, `history-and-upstream:13`) |
| M6a / M2b / M6b prevalence **in yoshiko-flow** | cross-repo only | review-pass concerns | yf's 93 review passes were never mined (§4.1). Absent ≠ measured-absent |
| M2a / M3 / M12 prevalence **outside yoshiko-flow** | yf only | — | cross-repo never re-audited completed bundles or checked build parity (§4.1) |
| DC-9 "named defect shape recurs in-repo" | 1 cluster, 1 repo | matrix row only | The cross-repo artifact has **no prose section for DC-9** — it appears only as two table rows, and its own recurrence table says "not assessed (single instance)" |
| DC-2 "false pass" shard (test cannot observe its target) | 1 cluster, 1 repo | one review concern | Single instance; the retriever itself records it as **not preventable by process** |
| DC-7 absence outside d3-pxe | 1 cluster | — | Retriever flags `[uncertain]`: "I also did not search for it exhaustively — it has no distinctive keyword" |
| DC-2 absence in evri_py | 1 cluster | — | Retriever flags `[uncertain]`: the CI-outcome structural explanation has "no evidence for that mechanism beyond the absence itself" |
| "doc↔impl divergence is reliably NEVER fixed" (M4's second half) | 1 cluster, 2 repos | 3 open issues | No denominator of doc↔impl defects that *were* fixed. Detection is well-evidenced; the never-fixed rate is not |
| emacs.d's actual plan-process defect rate | 2 clusters | 4 one-pass bundles | Structurally unmeasurable (§4.3) |
| Molecule↔bundle attribution for the 24 unlinkable bundles | 1 cluster | date alignment | `execution-telemetry:4`, retriever-flagged `[uncertain]`; "What was lost is the *pointer*, not the rows" is inference |
| Whether any upstream issue was closed by a plan and later reopened | 1 cluster | — | `gh` rate limit prevented timeline retrieval; explicitly `[uncertain]` |
| Bead-level reopen events anywhere in the corpus | 1 cluster | — | `bd` exposes no status history — structurally invisible, absence of evidence only |
| Review escape **rate**, corpus-wide | 2 clusters | — | "There is no artifact anywhere in the corpus that records \"this review missed X\"" (yf Absences). Compounded by M8b: bundles omit post-completion churn |
| The unrecorded-remediation population | 4 clusters | — | C1's hard bound: not estimable by any method used here |
| 31 of 45 yf candidates / the non-adjudicated remainder | — | — | Neither confirmed nor rejected; and per C6 the candidate set is not a valid denominator anyway |

**No ambiguity above was resolved by choosing a side.** Where two clusters disagreed (§4.1, §4.2,
§4.3, §4.4) the disagreement was resolved by evidence — mechanical verification, a split into two
distinct classes, or composition — not by preference.

---

## 6. What the synthesizer must NOT overclaim

1. **No prevalence, ever.** C1 makes every count a lower bound over the *recorded* subset. Write
   "confirmed in N instances", never "N% of plans".
2. **"83 candidates" is not a denominator** (C6). The extractor fails precision *and* recall on the
   one pair git can prove.
3. **Do not pool the yf and cross-repo class lists** (§4.1). They surveyed disjoint surfaces. A class
   missing from one list is unmeasured there, not absent.
4. **Do not report "3 of 4 repos" bare, and do not call emacs.d clean** (§4.3).
5. **Do not report `git:revert = 0`, `git:fix` density, or any repo ranking derived from commit
   subjects** (§4.4).
6. **Do not say the process improved over time** (§4.5).
7. **Do not call M8a (deliberate, recorded, filed deferral) a defect.** Two clusters independently
   found no violated step. It is a missing lifecycle distinction. M8b is the separate, real defect.
8. **Do not generalise M3 (deploy parity) or M12 (one-directional reconcilers) beyond yoshiko-flow.**
9. **Do not state that prose enforcement *always* fails.** The same reconciler prose worked for
   plan-040 and plan-041; the supported claim is *unreliable*, not *broken* (§2.4).
10. **Do not present review as uniformly weak.** cross-repo's calibration survives triangulation:
    review is effective on claims with a stated mechanism (`cross-repo-corpus:12`,
    `cross-repo-corpus:18`, `cross-repo-corpus:21`, `cross-repo-corpus:26`), weak on executable
    commands (`cross-repo-corpus:5`), and weak on its own prior revisions (`cross-repo-corpus:24`,
    `cross-repo-corpus:7`). Any "review lets X through" must name X.
11. **Do not use plan numbers as identity.** `plan-013` denotes three different bundles in this
    corpus; pybridge reuses `plan-005`.
12. **Do not treat later-plan self-diagnosis as ground truth.** 17 of 27 yf sources are `verify`-grade
    for this reason, and the corpus contains a worked instance of self-diagnosis being wrong:
    plan-043's E1 refuted all three of issue #136's own hypotheses about its own cause
    (`yf-corpus:6`).
13. **Do not claim any class was "caught by review" or "escaped review" for yoshiko-flow.** No yf
    source reads a review pass (§4.1), so that venue distinction is undetermined for 43 of the 83
    bundles.
