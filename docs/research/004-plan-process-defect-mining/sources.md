---
type: Reference
research: 004-plan-process-defect-mining
produced: '2026-08-16'
okf_spec: OKF-RESEARCH
---

# Sources — 004-plan-process-defect-mining

136 sources across six clusters — the five retrieval clusters plus one
single-source verification cluster added at REFINE. Every source is first-party: a plan bundle, a review pass, a git
commit, a bead, or a GitHub issue in the operator's own repositories. **There is no web leg by
design** (`plan.yaml` `exclusions`), so the default web credibility rubric does not apply; the four
axes actually used are recorded in `artifacts/triangulation.md` §0 (contemporaneity, self-interest,
mechanical-vs-prose, authorship voice).

## Citation-id mapping

`sources.json` keys every source by a cluster-prefixed composite `uid` (`<cluster>:<n>`), because
cluster-local `[N]` markers collide — `[1]`, `[7]` and `[13]` each denote four different sources.
`Summary.md` and this ledger use the following short forms, one heading per source:

| Cluster (`uid` prefix) | Short form | Count | Dominant source type |
| :-- | :-- | --: | :-- |
| `cross-repo-corpus` | `XR<n>` | 30 | contemporaneous `reviews/pass-N.md` concerns, investigation spikes |
| `yf-corpus` | `YF<n>` | 27 | later-plan Motivation prose |
| `yf-corpus-reviews` | `YFR<n>` | 35 | yoshiko-flow `reviews/pass-N.md` concerns |
| `execution-telemetry` | `ET<n>` | 15 | live `bd` enumeration |
| `history-and-upstream` | `HU<n>` | 28 | git commits / pickaxe, first-party issue bodies |
| `refine-verification` | `RF<n>` | 1 | primary artifact read at REFINE to test a critique item |

So `cross-repo-corpus:12` is cited as `XR12` and anchors at `sources.md#xr12`.

## Credibility categories

Assigned in `sources.json` as `credibility_score` / `credibility_category`. The first four clusters
(100 sources) were scored at triangulation. The 35 `yf-corpus-reviews` sources were originally
prose-graded by their own retriever — all 35 `high_trust`, none scored — and were **rescored at
REFINE** on the same four axes; nine moved to `verify`, principally on the self-interest axis (a
review pass reporting favourably on review practice, inside the self-selected repo, is self-serving,
not against-interest). `refine-verification:1` was scored on retrieval.

| Category | Count (of 136) | Meaning here |
| :-- | --: | :-- |
| `high_trust` | 94 | contemporaneous and/or mechanically reproducible |
| `verify` | 38 | reconstructed later-plan self-diagnosis, single-observer inference, or self-serving on the self-interest axis |
| `questionable` | 4 | refuted method output, or evidence about the extractor rather than the corpus |
| `avoid` | 0 | — |

The nine `yf-corpus-reviews` sources moved to `verify` at REFINE are `YFR2`, `YFR3`, `YFR28`, `YFR29`
(the four carrying the review-quality reversal — a review pass reporting favourably on review
practice, in a bundle whose subject is review practice); `YFR30`, `YFR31` (favourable-to-self
demonstrations that the repo's own remedy worked, partly offset by being mechanically re-runnable);
`YFR33` (a favourable absence with no described search); `YFR22` (its own finding is `[uncertain]`);
and `YFR24` (the single source for M14b, and structurally a later reviewer's parenthetical summary
of the conformance artifact that does not exist). The first-person self-attributed regressions
`YFR12` / `YFR13` / `YFR14` clear the against-interest bar and remain `high_trust`.

The four `questionable` sources are `XR30` (subject-only revert search, refuted by `HU28`) and
`HU25` / `HU26` / `HU27` (raw `remediation_pairs.py` output — evidence about the tool, never a
denominator).


---

## cross-repo-corpus (XR) — 30 sources

### XR1

**plan-014 Decision D2 — author and apply are separate issues, and only the apply is gated**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:1` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/ansible/plans/plan-014-james-dixson-763edc/plan.md:143-147` |
| Credibility | 70 / verify |

> "plan-013 shipped a capability gate whose condition ("operator has previewed the diff for issue X") was unreachable because the gate blocked issue X *in its entirety*, including authoring the change to be previewed. It survived all three review passes and is filed upstream as [yoshiko-flow#112](https://github.com/dixson3/yoshiko-flow/issues/112). **That mistake is not repeated here:**"

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### XR2

**plan-013 Issue 5.1a — Deliberately UNGATED (post-hoc amendment)**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:2` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/ansible/plans/plan-013-james-dixson-1692d0/plan.md:345-349` |
| Credibility | 90 / high_trust |

> "**Deliberately UNGATED.** Authoring and `--check --diff` are read-only and mutate nothing. PVE-OBS-001 governs the *apply* (5.1b). Gating this step made the gate's own precondition unreachable — the preview could never be produced, so the gate could never be satisfied. That deadlock was found mid-execution on 2026-08-12 after three review passes missed it, and is filed upstream as yoshiko-flow#112/#113."

*Note:* Contemporaneous SELF-INCRIMINATING amendment: plan-013 records its own deadlock, in its own bundle, naming the detection date and the review-pass failure. An admission against interest, and it independently corroborates cross-repo-corpus:1 from the opposite side of the pair.

### XR3

**plan-014 red-team pass 1 — endorsement of the D2 correction**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:3` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/ansible/plans/plan-014-james-dixson-763edc/reviews/pass-1.md:135` |
| Credibility | 90 / high_trust |

> "is exactly the right correction of plan-013's defect, with the reasoning inline where an"

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR4

**plan-010 red-team pass 4, concern P1 — traces gate could not execute, third consecutive pass**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:4` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-4.md:53` |
| Credibility | 90 / high_trust |

> "**The traces gate could not execute** — third consecutive pass for this one gate. Two independent defects: **`curl` is not installed in CT 104**, and `pct exec 104 -- curl …` execs with no shell in the guest, so `$OO_ROOT_USER_*` expands on the *pve host* where they are unset (they are control-node vars). Root cause named precisely: *the plan hand-rolled a transport that plan-008's convention deliberately does not use.*"

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR5

**plan-010 red-team pass 3, concern N8' — PVE-token gate curl would always fail; both prior passes praised it**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:5` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-3.md:53` |
| Credibility | 90 / high_trust |

> "**The PVE-token gate curl would always fail** — PVE presents a self-signed cert; the repo's own README uses `curl -sk` and `pve_lxc` sets `validate_certs: false`. `curl -sf` exits 60 on TLS regardless of token validity. Both prior passes *praised* this test."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR6

**plan-010 red-team pass 4, concern P6 — success criteria that assert nothing**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:6` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-4.md:58` |
| Credibility | 90 / high_trust |

> "SC13/SC14 printed an HTTP code but asserted nothing (`-w` always exits 0) — the only eyeball checks in an otherwise fail-closed set."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR7

**plan-010 red-team pass 4, concern P2 — a pass-3 fix that preserved the defect**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:7` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-4.md:55` |
| Credibility | 90 / high_trust |

> "Traced honestly: pass-1 asserted the control node was outside (false); pass-3 replaced `/24` with six CIDRs "verified to cover `.100–.149` exactly" — **which is exactly what keeps SC9 unpassable.** The fix removed the `/24` while preserving the property that made the criterion false."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR8

**plan-010 red-team pass 4, concern P3 — no pass looked at two prior fixes together**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:8` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-4.md:54` |
| Credibility | 90 / high_trust |

> "A genuinely *new* interaction: pass-2's N5 hardening met EXP-003's scrape recipe, and neither pass looked at them together. Unaddressed, the scrape 401s, no `litellm_*` series arrive, and **SC16 and SC18 fail silently** on the plan's highest-blast-radius change."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR9

**plan-010 red-team pass 3, concern M1 — four stale success-criterion cross-references**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:9` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-3.md:54` |
| Credibility | 90 / high_trust |

> "**Four stale SC cross-references** after the SC14 insertion: R6→SC14 (now 15), R8→`SC13a` (**never existed**), R13→SC16 (now 17), Rollback→SC14 (now 15). Three pointed at a different *real* criterion."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR10

**plan-012 EXP-002 — plan-011's hazard was never spelled out and was overstated**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:10` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/postgres/plans/plan-012-james-dixson-abea8d/findings/exp-001-002-acme-client-and-pg-tls.md:66,78` |
| Credibility | 86 / high_trust |

> "plan-011 recorded this as a reason to avoid TLS but never spelled it out. Measured: […] **This is materially less scary than plan-011 implied**, because the group and membership already exist and are recreated by the `ssl-cert` package on any rebuild."

*Note:* Execution-phase experiment record: a measurement made at the time, in a corpus where these repeatedly OVERTURN the plan's own prose. Mechanical where it reports an observation; treat any conclusion it draws as one step weaker.

### XR11

**plan-012 context — plan-011's stated rationale was invalidated by a later change**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:11` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/postgres/plans/plan-012-james-dixson-abea8d/context.md:142` |
| Credibility | 65 / verify |

> "Which **invalidated the "LAN-internal traffic" rationale plan-011 gave for `ssl = off`**."

*Note:* The same context.md is SELF-EXCULPATING on this point ('not fixing an oversight; paying a debt taken on knowingly'). The retriever correctly declined to score it as a defect. Usable as a record of the decision, not as evidence of a defect.

### XR12

**plan-012 EXP-002 — its own conclusion superseded by its own review**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:12` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/postgres/plans/plan-012-james-dixson-abea8d/plan.md:189-193` |
| Credibility | 86 / high_trust |

> "> **Superseded in part by D2 (review).** The measurement is correct, but the conclusion "so use the group" does not survive D1 […] The de-escalation of plan-011's vague hazard stands; the proposed mechanism does not."

*Note:* A finding OVERTURNED BY ITS OWN BUNDLE'S REVIEW, recorded in place. Evidence both for the claim and for the (rarer) case of review working on mechanism-bearing claims.

### XR13

**plan-016 EXP-006 — plan-016's own claim about plan-015's panel was wrong**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:13` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `docs/plans/plan-016-james-dixson-533fa8/findings/exp-006-backup-observability.md:74,83` |
| Credibility | 86 / high_trust |

> "## The plan-015 panel is already fleet-wide […] So it would **already render a pve backup-unit failure today**. Only its *placement* — on a dashboard titled "PostgreSQL — CT 107" — is postgres-scoped."

*Note:* An experiment that CONTRADICTS ITS OWN PLAN'S stated claim about a predecessor's artifact, by reading the artifact instead of the predecessor's prose. Self-incriminating and mechanically grounded.

### XR14

**plan-016 EXP-006 — the plan-015 absence-blindness weakness reproduces exactly**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:14` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `docs/plans/plan-016-james-dixson-533fa8/findings/exp-006-backup-observability.md:114` |
| Credibility | 86 / high_trust |

> "The plan-015 weakness reproduces exactly: a `GROUP BY body_unit … WHERE body_message LIKE 'Finished %'` lists only units that *did* run."

*Note:* Execution-phase experiment record: a measurement made at the time, in a corpus where these repeatedly OVERTURN the plan's own prose. Mechanical where it reports an observation; treat any conclusion it draws as one step weaker.

### XR15

**plan-003 Motivation — plan-002 shipped roles that were authored but never proven**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:15` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/ansible/plans/plan-003-james-dixson-a81dfc/plan.md:26-30` |
| Credibility | 70 / verify |

> "plan-002 formalized the `pve` host + Plex guest into Ansible roles but stopped at `--check --diff` (reconcile only, no converge). Three things were therefore **authored but never proven**: (a) `unsafe_writes: true` on `/etc/pve` pmxcfs writes (PVE-ANS-005), (b) the `community.proxmox.proxmox` CT lifecycle module (`check_mode: none` — un-previewable), and (c) idempotency (PVE-ANS-007)."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### XR16

**plan-006 EXP-002 — Epic 2's premise was already fixed by plan-002**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:16` |
| Repo | pybridge |
| Type | plan-bundle |
| Locator | `docs/plans/plan-006-james-dixson-8f91b1/findings/exp-002-spike-b-27-mechanism.md:48` |
| Credibility | 86 / high_trust |

> "**Epic 2 has no kernel-stability bug to fix.** Building a fix against this premise is dead work."

*Note:* Investigation-spike finding: a measurement made BEFORE any epic executed, which killed the epic's premise. Contemporaneous and prospective.

### XR17

**plan-009 EXP-002 Leg B — B1 already exists in full from plan-002**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:17` |
| Repo | pybridge |
| Type | plan-bundle |
| Locator | `docs/plans/plan-009-james-dixson-7e1c92/findings/exp-002-macos-gatekeeper.md:3` |
| Credibility | 86 / high_trust |

> "**Verdict: B1 already exists in full (plan-002 Epic 4).** The plan should *reconcile*, not rebuild."

*Note:* Investigation-spike finding, same shape as cross-repo-corpus:16 four months later in the same repo. Contemporaneous.

### XR18

**plan-006 red-team pass 1, concern C1 — plan drafted against a stale sibling baseline**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:18` |
| Repo | pybridge |
| Type | plan-bundle |
| Locator | `docs/plans/plan-006-james-dixson-8f91b1/reviews/pass-1.md:22` |
| Credibility | 90 / high_trust |

> "**plan-005 is MERGED to main** (`4356f52` + `739b33d`), not executing in parallel. context.md and Epic 3.2 risk describe it as concurrent with "land after plan-005" mitigation."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR19

**plan-006 red-team pass 2, concern C-NEW-3 — residue of the pass-1 C1 fix**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:19` |
| Repo | pybridge |
| Type | plan-bundle |
| Locator | `docs/plans/plan-006-james-dixson-8f91b1/reviews/pass-2.md:32` |
| Credibility | 90 / high_trust |

> "NEW (C1 residue) | Risks section (197-199) still says "coordinate 3.2 with plan-005 … **land after plan-005** or guard by identity." plan-005 is merged; "land after" is meaningless."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR20

**plan-006 red-team pass 2, concern C-NEW-2 — stale bead identifiers throughout the plan**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:20` |
| Repo | pybridge |
| Type | plan-bundle |
| Locator | `docs/plans/plan-006-james-dixson-8f91b1/reviews/pass-2.md:31` |
| Credibility | 90 / high_trust |

> "Stale bead naming. `pybridge-jfc` is now **CLOSED** (folded into `pybridge-2yp`, upstream **#31**); `pybridge-8fv` is already upstream (**#32**). plan.md still says `jfc` at line 131, 163-165, 177-178 (**Reconcile Gate carve-out** → references a bead that no longer exists under that name)"

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR21

**plan-006 red-team pass 1 — reconcile gate can never go green**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:21` |
| Repo | pybridge |
| Type | plan-bundle |
| Locator | `docs/plans/plan-006-james-dixson-8f91b1/reviews/pass-1.md:32` |
| Credibility | 90 / high_trust |

> "**M2** — Reconcile gate folds in `runAllTests.m` green, but `testArrayTransferMultiDim` is known-failing on main (`pybridge-jfc`) → gate can never go green. Carve it out or fix it."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR22

**plan-010 red-team pass 2 — revisions introduced defects and re-introduced a fixed contradiction**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:22` |
| Repo | pybridge |
| Type | plan-bundle |
| Locator | `docs/plans/plan-010-james-dixson-06eefa/reviews/pass-2.md:10,30` |
| Credibility | 90 / high_trust |

> "the revisions introduced/left three technical-correctness defects (N2/N3 would fail at execution) plus a re-introduced C6 contradiction (N1). […] Success Criteria says "#38 closed as a dup of #34" — the exact reversal C6 fixed (table + Issue 1.6 correctly say close #34 as dup of #38). Executed literally, closes the wrong asset-referenced issue."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR23

**plan-004 red-team pass 1, concern C1 — a test that cannot detect the bug it targets**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:23` |
| Repo | pybridge |
| Type | plan-bundle |
| Locator | `docs/plans/plan-004-james-dixson-14d3b5/reviews/pass-1.md:20` |
| Credibility | 90 / high_trust |

> "The xplat suite is a **single-process** Python simulation; the WinError-32 leak is by construction **cross-process** […] A single process map-then-unlink can never raise it → SC#3 + Tri-Platform Green go green while the real bug survives."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR24

**plan-008 red-team pass 3 — NC5 introduced by the pass-2 revision itself**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:24` |
| Repo | evri_py |
| Type | plan-bundle |
| Locator | `docs/plans/plan-008-james-dixson-d1f1e4/reviews/pass-3.md:9-11` |
| Credibility | 90 / high_trust |

> "One new medium (NC5), introduced by the pass-2 revision itself: the Reconcile Gate now blocking `4.2` re-entangles the #7 macOS close with the indefinitely-blockable Windows gate — the exact contradiction NC2 removed, reintroduced through the gate instead of the edge."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR25

**plan-008 red-team pass 4, concern NC6 — stale cross-reference created by the NC5 fix**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:25` |
| Repo | evri_py |
| Type | plan-bundle |
| Locator | `docs/plans/plan-008-james-dixson-d1f1e4/reviews/pass-4.md:28` |
| Credibility | 90 / high_trust |

> "Risk-table row labeled the App-Control-blockable close-out `(4.2)` — stale after the NC5 fix (4.2 is now the macOS #7 close, no longer Windows-blockable; the Windows-gated close-out is 4.3)."

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR26

**plan-007 red-team pass 1, concern C5 — reconcile gate structurally unreachable**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:26` |
| Repo | evri_py |
| Type | plan-bundle |
| Locator | `docs/plans/plan-007-james-dixson-8d1b13/reviews/pass-1.md:53-58` |
| Credibility | 90 / high_trust |

> "### C5 (MEDIUM) — Epic 4 reconcile gate structurally unreachable; completion self-contradicts The Reconcile Gate is "auto (all execution beads closed)," but 4.2 is blocked by an external-human gate an agent can never satisfy. If 4.2 stays open, the auto gate never fires and the plan can't complete — contradicting the risk claim that it "can complete … with #15 left partial.""

*Note:* Contemporaneous, dated, self-attributed record of REVIEW FAILURE: pass N naming what passes 1..N-1 missed or broke, written before the outcome was known and against the reviewing process's own interest. The highest-yield source type in this corpus.

### XR27

**plan-004 — a whole plan whose only purpose is to carry plan-003's deferred items**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:27` |
| Repo | evri_py |
| Type | plan-bundle |
| Locator | `docs/plans/plan-004-james-dixson-81bfcd/plan.md:6,16-18` |
| Credibility | 70 / verify |

> "**Status:** approved (lightweight rollup; no review cycle) […] Complete the three work items deferred from plan-003 execution. None require new investigation — each has a clear definition of done in its bead. This plan exists as a tracking surface so the items don't drift after plan-003 closed."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### XR28

**emacs.d — zero cross-plan references across all four bundles (verified absence)**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:28` |
| Repo | emacs.d |
| Type | plan-bundle |
| Locator | `docs/plans/{plan-001-james-dixson-30e722,plan-002-james-dixson-b23020,plan-003-james-dixson-667e0b,plan-004-james-dixson-ed20f6}` |
| Credibility | 88 / high_trust |

> "[no matching text] — recursive grep for `plan-0[0-9][0-9]` in each bundle, excluding each bundle's own id, returned zero hits in all four."

*Note:* Verified ABSENCE by reproducible recursive grep across all four emacs.d bundles. Mechanical and re-runnable. Note it establishes absence of cross-plan REFERENCES only, not absence of defects (see history-and-upstream:19/20).

### XR29

**d3-pxe bead graph carries almost no cross-plan remediation signal**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:29` |
| Repo | d3-pxe |
| Type | bead |
| Locator | `bd list --all --json (d3-pxe/.beads) — 423 beads, 72 epics, 4 discovered-from edges` |
| Credibility | 90 / high_trust |

> "types: Counter({'task': 332, 'epic': 72, 'molecule': 19}) / discovered-from edges on beads: 4 / epics: 72"

*Note:* Direct bd enumeration, independently reproduced by execution-telemetry:6 over all five repos. Mechanical.

### XR30

**No `Revert "..."` commits exist in any of the four repos**

| Field | Value |
| :-- | :-- |
| uid | `cross-repo-corpus:30` |
| Repo | d3-pxe, pybridge, evri_py, emacs.d |
| Type | commit |
| Locator | `git log --all --grep=revert -i across all four repos (767 commits total)` |
| Credibility | 40 / questionable |

> "[no matching text] — every hit was a body-text mention (e.g. 'plan-015 Issue 4.5: correct stale 192.168.7.115 control-node references'); no commit subject matches git's generated `Revert "..."` form."

*Note:* MEASUREMENT ARTIFACT. Subject/keyword-scoped revert search. history-and-upstream:28 shows the corpus's one genuine semantic revert (evri_py db41594) does not begin with 'Revert' and is detectable only in the commit BODY — this source saw that commit and dismissed it as body-text noise. The stated CONCLUSION (the absence carries no information) survives; the COUNT does not. Do not cite the count.


---

## yf-corpus (YF) — 27 sources

### YF1

**plan-040 — Replace bd-backend push with gh-direct issue creation (Motivation)**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:1` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-040-james-dixson-1cabe4/plan.md:43-53` |
| Credibility | 70 / verify |

> "**The write path depends on a mechanism nobody chose.** Every upstream write shells out to `bd github push` (≡ `bd github sync --push-only --issues`). #133 establishes that this was never justified anywhere in the repo — `SPEC.md` presupposes it (REQ-BUP-030/031) without arguing for it. It was inherited because bd 1.0.5 happened to ship the feature. ... The skill's central safety invariant, **GR-BUP-001** (REQ-BUP-030), is *"never run a bare `bd <backend> sync`"* — so the dependency is retained and then deliberately disabled from doing the only thing that justifies it."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF2

**plan-040 EXP-002 — closable does not complete**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:2` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-040-james-dixson-1cabe4/plan.md:111-117` |
| Credibility | 86 / high_trust |

> "**`closable` produced zero output in 4 minutes and was killed** **[measured]**. From an operator's seat, indistinguishable from a hang. ... **Cause is a removable N+1** **[measured]**: `cmd_closable` loads all rows in one `bd list --all --json`, then calls `external_for(id)` per row — a fresh `bd show` subprocess each — across **991 beads**."

*Note:* Explicitly tagged [measured] by the plan itself: a wall-clock observation (zero output in 4 minutes, killed) plus a named mechanism (removable N+1 across 991 beads). Measurement, not assertion.

### YF3

**plan-038 — closable with the chosen per-bead signal is forward-looking only**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:3` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-038-james-dixson-1ce25a/plan.md:112-117` |
| Credibility | 88 / high_trust |

> "But `yf-plan` §4.5 files coarse plan trackers with a direct `gh issue create`, so **no bead ever maps to them**. `closable` therefore would **not** have caught any of the four sweeps that motivated #117. That is the price of zero coupling, and this plan states it rather than implying #117 is fully closed."

*Note:* AGAINST INTEREST: plan-038 discloses, in its own plan.md, that its own deliverable cannot catch the four sweeps that motivated it. Self-incriminating disclosure in a shipping plan is the strongest prose class in this corpus.

### YF4

**plan-040 — five coarse trackers gone stale and closed by hand**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:4` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-040-james-dixson-1cabe4/plan.md:62-67` |
| Credibility | 70 / verify |

> "Meanwhile coarse plan trackers are structurally invisible to it, because `yf-plan` files them with a bare `gh issue create` and records the URL on no bead. Five have now gone stale and been closed by hand — #103, #95, #96, #98, and #134 (this session)."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF5

**plan-043 — plan-039 reported complete while three include rows were never touched**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:5` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/plan.md:43-49` |
| Credibility | 70 / verify |

> "Concretely (#136): plan-039 reported `status: complete`, `open_work_remaining: 0`, a clean cascade, merged and pushed — while **three of its four `include` upstream issues were never touched**. #108, #112 and #114 were all mapped, all carried dispositions and a populated `Resolved By` column, all genuinely resolved by the executed work, and all still `OPEN` with zero comments mentioning plan-039. Reconciliation ran, handled `supersede` and `partial` correctly, then silently did nothing for the third disposition. Nothing prompted anyone to look."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF6

**plan-043 E1 — Why plan-039's reconcile skipped three include upstream issues**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:6` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/findings/exp-001-reconcile-skip-cause.md:14-23,37-68,124-129` |
| Credibility | 88 / high_trust |

> "**Verdict: none of the three.** A fourth mechanism: The reconciler **was** dispatched, **did** parse the table correctly, and then **reported success without performing the `gh` writes** for the three `include` rows. It conflated *"the code shipped"* with *"the upstream issue was closed"*, and wrote that conflation into its close reason as an affirmative claim of completion. ... At the moment the reconcile bead closed claiming all six handled, **zero `gh` writes had touched those three issues**. The three closes landed in a 5-second batch 15 hours later — the operator's manual repair, not the reconciler's work."

*Note:* Execution-phase experiment with timestamp evidence and a verbatim linguistic tell. Double-edged and important: it is simultaneously the best evidence for F4 AND the corpus's proof that first-party self-diagnosis is fallible (it refuted all three of issue #136's own hypotheses). Cite it, and cite that property.

### YF7

**plan-043 E1 — reconcile is pure prose; the verification step already existed**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:7` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/findings/exp-001-reconcile-skip-cause.md:88-117` |
| Credibility | 88 / high_trust |

> "`grep -n "reconcil" plan_manager.py` returns **one** hit, a status-string docstring. There is **no reconcile verb** ... **Nothing executes, nothing returns an exit code, nothing can fail.** ... **The verification step already exists as prose, and was skipped in the same breath.** ... Step 4 **is** the post-reconcile verification the plan intends to add. It was ignored exactly as step 3 was. **Adding a sixth instruction to a five-instruction list that was partially ignored is a null change.**"

*Note:* Mechanical within a prose finding: 'grep -n reconcil plan_manager.py returns ONE hit' is reproducible, and the conclusion (nothing executes, nothing returns an exit code) follows from it directly rather than from assertion.

### YF8

**plan-039 — Motivation: reviews miss a class of defect; a safety mechanism degraded into a constant**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:8` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-039-james-dixson-150f79/plan.md:56-74` |
| Credibility | 70 / verify |

> "**Reviews miss a whole class of defect.** Across `d3-pxe` plan-013, four real defects were found in review and a fifth escaped every pass. All five are the same shape: *a claim about execution-time state that was never checked against what will actually be true at that point in the DAG.* One of them was an unsatisfiable capability gate that survived conformance and **two** red-team cycles. ... Measured across 53 real plans (EXP-001), it suggests `ci-release` on **40 of 53** ... and on **all 17** plans where an operator recorded a ground-truth class — **16 of them wrongly**, with **zero** correct negatives, ever. ... a false positive surviving to reconcile blocks completion on a plan that never had runner-only behavior, where the natural fix under time pressure is to attest something untrue."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF9

**plan-043 — the audit is a PLAN-phase gate that cannot see execution-authored artifacts**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:9` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/plan.md:51-60` |
| Credibility | 70 / verify |

> "Concretely (#140): `plan_manager.py audit` is a **PLAN-phase gate**. It runs at Phase 3 and in `/yf-plan capture` — both *before* INTAKE. But `references/` and `reviews/` are largely authored during **EXECUTE**: replay fixtures, drafted comments, backfill maps, residuals records. Those files are created *after* the only gate that would check them, and no later gate re-runs it. Re-auditing the corpus today, **9 of 40 bundles fail** ... Both defects share one shape: **the close step is where the evidence is complete, and it is the one place nothing looks.**"

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF10

**plan-043 E3 — Close-time bundle audit: fail-loud or propose-only**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:10` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/findings/exp-003-close-time-audit.md:15-57` |
| Credibility | 88 / high_trust |

> "Re-audited all 43 bundles. **41 reached `complete`; 31 pass, 10 fail — 24.4%.** Applying the checks *as they existed at each plan's close date* (historically faithful): **9 of 41 — 22.0%.** ... **plan-029's failure is a proven FALSE POSITIVE.** ... The Windows-drive-letter regex `[A-Za-z]:\\` matched `s:` + `\` from `tags:\n`. ... **plan-030's failure is self-inflicted by the close step.** ... **A fail-loud audit placed after the close step's own writes would block on its own output.** ... **9 of 10 failures are class A** — execution- or close-authored, structurally invisible to the Phase-3 gate."

*Note:* Re-measured the whole corpus (43 bundles) two ways, including a historically-faithful re-run, and reported a PROVEN FALSE POSITIVE in its own results plus a case where the proposed fix would block on its own output. Self-correcting measurement; the strongest methodological source in the yf cluster.

### YF11

**plan-041 — embed addition blind spot, version-stamp staleness, and an untested shipping path**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:11` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-041-james-dixson-a9d837/plan.md:47-105` |
| Credibility | 88 / high_trust |

> "**(1a) Embed staleness, on ADDITION only.** A file or directory *added* under `skills/` is invisible to an incremental release rebuild (`Finished in 0.10s`, new file absent). Content edits, deletes and renames all propagate correctly. **(1b) Version-stamp staleness, on EVERY skills-only change.** ... **The shipping embed path is untested.** `cargo test --workspace` builds **debug** ... So every embed test — including the `REQ-YF-EMBED-003` frontmatter integrity check — asserts against the on-disk tree, never the baked one. **The #137 defect class is structurally invisible to the entire test suite.** ... The failure is silent and self-concealing ... `cargo build --release` exits `0`, `yf self install` reports `{"status":"ok"}` ... `AGENTS.md` currently instructs the operator to run `touch yf/src/embed.rs` as a **required step 0** before every sync ... because the tool cannot be trusted to do its own job."

*Note:* AGAINST INTEREST: plan-041 states that the CI job it is adding would NOT have caught the defect it is fixing ('a clean build cannot exhibit an incremental staleness bug'). A plan disclosing the inadequacy of its own remedy is high-credibility by construction.

### YF12

**Bead yf-nkgh — plan-039 install parity**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:12` |
| Type | bead |
| Locator | `bd:yf-nkgh (close_reason, closed 2026-08-16T16:14:51Z)` |
| Credibility | 90 / high_trust |

> "Install parity done: cargo build (forced re-embed via touch yf/src/embed.rs — the incremental build was a 0.31s cache hit that would have shipped a stale tree) + yf skills install --scope user --surface claude, run from ./target/debug/yf not the stale PATH binary."

*Note:* Bead close reason, written at close time. Contemporaneous and unedited; it records the hand workaround (touch yf/src/embed.rs) that IS the defect, months before the defect was named.

### YF13

**plan-037 — Motivation: the plan was drafted with a stale copy of the skill it edits**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:13` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-037-james-dixson-cab694/plan.md:47-56` |
| Credibility | 70 / verify |

> "That work is real and in daily use, but it lives only on one machine: it is absent from `main`, invisible to any other clone, and silently destroyed by the next `install.sh --force`. Meanwhile the repo has moved ahead of the install, so the operator is running skills whose behavior no longer matches their own SPECs. Concretely, this session drafted its plan using the **stale v0.4.0 `yf-plan` skill**, whose Pre-flight section still documents `/.state/` gitignore anchors and `.yf-plan.local.json` config — a layout `main` replaced with the canonical `.yf/<short>/` tree."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF14

**plan-042 — Install-time sync (split from plan-041)**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:14` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-042-james-dixson-98631b/plan.md:28-42,98-102` |
| Credibility | 68 / verify |

> "`AGENTS.md` documents a three-step land-the-plane ritual (`self install` → `skills install` → `harness tune`) whose steps 2 and 3 are silently optional: nothing warns when they are skipped ... **Split from plan-041** (its pass-1 red-team, concern C10) ... **Portability of the carried findings** (plan-041 pass-2, missing-item M-d). This bundle's `findings/` and `references/` are empty while Investigation Findings cites E1/E4 by cross-bundle path — a portability regression the split created."

*Note:* plan-042 is status `scoping` — an unexecuted, in-flight bundle. Adequate evidence that the split occurred and that a review caught the portability regression; NOT evidence about outcomes.

### YF15

**plan-015 — Motivation: the static validate-cmd fails open, producing a false green**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:15` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-015-james-dixson-cb2ef4/plan.md:33-40` |
| Credibility | 70 / verify |

> "plan-011 added a static `validate-cmd` string to `.yf-plan.local.json` ... plan-014 just shipped — and its land-the-plane **surfaced this exact gap**: this repo has **no `validate-cmd` configured**, so the merged-state validation emitted a "CROSS-PLAN REGRESSIONS NOT CHECKED" notice and proceeded on plan-gate coverage only (a false green). A static `validate-cmd` has the **same drift failure mode that motivated `yf-drift-check`**: it is hand-authored per-repo config that silently rots when the toolchain changes ... and it **fails open**."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF16

**plan-027 — Motivation: unstaged formula, silent degradation, class-level problem**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:16` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-027-james-dixson-a59656/plan.md:26-43` |
| Credibility | 70 / verify |

> "While executing plan-026, `bd mol wisp plan-investigate` failed with `proto not found`. Root cause: yf-plan's Phase 2 INVESTIGATE step called the wisp **without staging its formula** into `.beads/formulas/` first ... Phase 5's `plan-execute` pour stages correctly (cp/rm bracket); Phase 2 did not. The failure was **silent** — wrapped in `json-get` + capture-and-continue, so wisp tracking degraded to a no-op with no operator-visible error. ... The deeper problem is **class-level, not instance-level**: nothing mechanically prevents a beads-backed skill from shipping a formula it never stages, and the failure mode is silent."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF17

**fix(yf-plan): stage plan-investigate wisp formula + --force the burn**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:17` |
| Type | commit |
| Locator | `2520f79368bfd4d3d93e1c242587c56b6bc27c3c (2026-07-11) and d1aee53 (introduction)` |
| Credibility | 92 / high_trust |

> "Phase 2 INVESTIGATE called `bd mol wisp plan-investigate` without first staging the formula into `.beads/formulas/`, so bd failed `proto not found` and wisp tracking silently degraded to a no-op (json-get + capture-and-continue swallowed it). ... Discovered during plan-026 execution. Interim correctness fix; plan-027 moves staging ownership into the yf kernel (preflight) and removes this cp/rm dance fleet-wide. Satisfies plan-027 Epic 5.1."

*Note:* Mechanical, contemporaneous git record (sha + subject/diff/body), reproducible by re-running the query. Not prose, not self-serving, and not reconstructed later.

### YF18

**plan-020 — Motivation: the repair premise holds only in dolt server mode**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:18` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-020-james-dixson-81785d/plan.md:26-38` |
| Credibility | 70 / verify |

> "That premise — "`bd dolt stop` flushes and clears the in-memory Dolt working set" — only holds in dolt **server** mode. For the embedded-storage layout (`.beads/embeddeddolt/`, the cruft-suppressed default this skill itself creates), `bd dolt stop` errors ("not supported in embedded mode (no Dolt server)") ... This is an **upgrade artifact** and will recur on the next beads schema-bump for any embedded repo whose prior session left an unflushed working set."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF19

**plan-023 — #57: the safety invariant reads as a hand-CLI recipe**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:19` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-023-james-dixson-b618bb/plan.md:45-47` |
| Credibility | 70 / verify |

> "**#57** — the always-loaded close-time **Safety invariant** in `UPSTREAM_TRACKING.md` reads as a hand-CLI recipe, so an agent can satisfy the guardrail with a raw `bd github push --dry-run` while **skipping** the routing sentence that says to invoke `/yf-beads-upstream` (observed live)."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF20

**plan-038 — the skill documents the command its own rule forbids; #129 matches zero beads at exit 0**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:20` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-038-james-dixson-1ce25a/plan.md:54-61,96-110` |
| Credibility | 88 / high_trust |

> "`SKILL.md` Push step §3 then documents the hand-run command as *the* procedure. An operator or agent that follows the skill violates the rule. ... In the session that produced this plan, pushing 11 orphaned beads was done with a hand-run `bd github push` **because the skill said to**. Nothing broke, which is exactly why the defect persists: it fails silently, producing a non-compliant action that looks correct at every step. ... The fixture tests missed it because they assert the *shape* of the emitted command against an expected string that itself contains the commas: a test documenting the implementation rather than the contract."

*Note:* AGAINST INTEREST and contemporaneous: plan-038 records that the very session which produced it violated the rule, 'because the skill said to'. Self-incriminating.

### YF21

**plan-039 EXP-001 — classifier corpus measurement**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:21` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-039-james-dixson-150f79/plan.md:103-119` |
| Credibility | 86 / high_trust |

> "**Current precision is 1/17, with `TN=0`** — it has never produced a correct negative. Full corpus: **40/53** suggested `ci-release`. ... **F4 makes `confidence` constant at intake**: the path marker is the only non-prose signal and `changed` is empty at §4.1.5, so every intake classification reports `low`. F4 correctly stops the field overstating, but leaves it carrying no information where it is actually read."

*Note:* Corpus-scale measurement over 53 real plans with a stated confusion matrix (1/17 precision, TN=0). Mechanical and re-runnable.

### YF22

**plan-035 — web docs imply execution can span multiple environments (resolves #97)**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:22` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-035-james-dixson-74d7ae/plan.md:32-40` |
| Credibility | 70 / verify |

> "The docs still imply execution can "span multiple environments" via shared beads. Reality: the bead DB is **local** to one repo clone, shared **only across worktrees**, and **never pushed via git** ... Rewrite "Why yf-plan" accordingly and **reconcile the same misleading claim across every adjacent `web/` doc**."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF23

**plan-036 — authored skill pages guarded by a DRIFT-CHECK edge**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:23` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-036-james-dixson-461061/plan.md (Motivation)` |
| Credibility | 62 / verify |

> "The risk of authored pages is the inverse of the current design's strength: authored prose can **drift** from the skill's actual behavior as the skill evolves. The repo already runs `yf-drift-check` (an `approved: yes` root `DRIFT-CHECK.md`), so the fix is to add a source-of-truth edge from each skill's `{SKILL.md,README.md,SPEC.md}` to its authored page."

*Note:* Motivation prose with NO line anchor ('plan.md (Motivation)'). Citation precision is below the rest of the cluster; the claim is plausible and uncorroborated mechanically.

### YF24

**plan-034 — closing plan-033's declared deferrals**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:24` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-034-james-dixson-ac6633/plan.md (Motivation)` |
| Credibility | 62 / verify |

> "plan-033 shipped multi-harness provisioning but **explicitly deferred** two behaviors as filed follow-on beads: the per-harness `yf doctor`/drift axis for non-Claude harnesses (`yf-252c`, the 008/009 analog ...) and the codex block-size-budget check (`yf-297v`, Risk R8/F7 ...)."

*Note:* Motivation prose with no line anchor. Used to RECLASSIFY a candidate as designed deferral rather than defect — the conservative direction, which limits the harm of its imprecision.

### YF25

**plan-033 — supersedes the plan-032 Claude-Code-only base**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:25` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-033-james-dixson-46aca2/plan.md:25` |
| Credibility | 70 / verify |

> "This supersedes the plan-032 Claude-Code-only, JSON-only base and the narrower "extend tune to codex/opencode" framing."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### YF26

**Git remediation-signal density in yoshiko-flow**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:26` |
| Type | commit |
| Locator | `git log (repo-wide, 2026-08-16): --grep='^fix' → 7; total → 393; --grep=revert -i → 2 (fe6eab9, 500aa35, both plan-033 intake/execute)` |
| Credibility | 60 / verify |

> "fe6eab9 plan-033: yf multi-harness provisioning (execute) / 500aa35 plan-033-james-dixson-46aca2: INTAKE approved (awaiting /yf-plan execute)"

*Note:* Two unsound sub-signals in one source. (a) The revert count uses --grep=revert -i on subjects, the same defect as cross-repo-corpus:30. (b) The 'only 7 fix-prefixed commits in 393' density figure does not travel: history-and-upstream:1 shows d3-pxe scores ZERO fix-prefixes while fixing constantly. The source's own conclusion — that git commit conventions carry no remediation signal here — is correct and is corroborated three ways; the numbers must not be reused.

### YF27

**plan-043 — three plan-041 execution deviations captured by no mechanism**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus:27` |
| Type | plan-bundle |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/plan.md:62-68` |
| Credibility | 70 / verify |

> "plan-041 completed an hour before this plan was scoped, and its execution surfaced three process deviations — a tracking issue auto-closed at intake by a `close #137` merge-commit keyword before any work ran, a `--no-ff` merge flattened by an automatic `pull --rebase`, and an unrelated directory swept into a commit by a `bd`-side hook. None was captured by any mechanism; all three exist only because a human read the subordinate's report."

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.


---

## yf-corpus-reviews (YFR) — 35 sources

### YFR1

**plan-029 pass 5 — wrong artifact paths would miss the entire corpus (high, at pass 5)**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:1` |
| Type | review-pass |
| Locator | `docs/plans/plan-029-james-dixson-75fd34/reviews/pass-5.md:22-28` |
| Credibility | 85 / high_trust |

> "Issue 2.1/2.2 use the wrong artifact paths — would miss the vault's entire plan+research corpus. severity: high The vault's plans/research live at `docs/plans/`, `docs/research/`, AND incubator-scoped `Incubator/<slug>/plans/`, `Incubator/<slug>/research/` — the two-root model the skills actually use — not top-level `plans/`/`research/` as 2.2 says."

*Note:* high_trust — contemporaneous, dated, first-party review concern; verified against the repo's actual two-root layout, which is independently documented in the project's PLANNING rule. Evidence that a high-severity blocking defect was still being found at pass 5.

### YFR2

**plan-039 pass 2 — M1: gate test cannot fail (always exits 0), found by executing it**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:2` |
| Type | review-pass |
| Locator | `docs/plans/plan-039-james-dixson-150f79/reviews/pass-2.md:93,97,221` |
| Credibility | 65 / verify |

> "**M1 — `Gate: Evidence corpus`'s Test cannot fail.** — severity: medium … corpus the pipeline still exits 0. The gate's test passes unconditionally. … | M1 | `Gate: Evidence corpus` test always exits 0 | medium | Verified (BSD `wc -l` pads). Replaced with `test -d … && [ "$(ls … | wc -l)" -gt 0 ]` | resolved |"

*Note:* high_trust — the reviewer names the platform-specific cause (BSD wc -l padding), which is only knowable by running the command. Directly refutes the cross-repo claim that review reads rather than runs verification commands.

### YFR3

**plan-039 pass 3 — M1 fix confirmed with a negative control**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:3` |
| Type | review-pass |
| Locator | `docs/plans/plan-039-james-dixson-150f79/reviews/pass-3.md:24` |
| Credibility | 65 / verify |

> "**M1 is a real fix, verified with a negative control** — the new gate test passes against the live corpus and *fails* against a nonexistent one. The old form could not fail."

*Note:* high_trust — mechanical, reproducible, and self-limiting (states both the positive and negative result). The negative control is the strongest single piece of evidence that this repo's review practice executes rather than reads.

### YFR4

**plan-024 pass 1 — M2a: audit gate runs before the fingerprint it would validate**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:4` |
| Type | review-pass |
| Locator | `docs/plans/plan-024-james-dixson-76cee9/reviews/pass-1.md:67-70` |
| Credibility | 85 / high_trust |

> "fingerprint-write timing across the new `ready-for-approval → approved` split is unspecified — the audit runs at `ready-check` (before approval) while `**Fingerprint:**` is written at approval (REQ-PLAN-034). A content edit between the two could let a stale-but-audited plan be approved."

*Note:* high_trust — an independent M2a (blind gate: passes, cannot see its evidence) instance found on the review surface, corroborating yf-corpus:9 which reached the same class by re-auditing completed bundles. Two disjoint surfaces, same class.

### YFR5

**plan-030 pass 1 — M2b: completion gate unreachable by construction**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:5` |
| Type | review-pass |
| Locator | `docs/plans/plan-030-james-dixson-65526e/reviews/pass-1.md:20` |
| Credibility | 88 / high_trust |

> "Option (b) deferred-validation bead contradicts the cascade-close step that runs *before* complete-gate: `close_cascade.cascade()` fail-louds (exit 2) on any container with any open child, so an open bead *inside* the plan tree halts completion before complete-gate runs. Reconcile Gate ("all execution beads closed") has the same conflict. Option (b) is unreachable as written."

*Note:* high_trust — resolves the M2b [insufficient evidence] flag for yoshiko-flow. Contemporaneous, high-severity, cites the exact mechanism (close_cascade.cascade exit 2) rather than asserting the deadlock. Same shape as cross-repo-corpus:26 and :21 (auto completion gate over a set containing a blocked element).

### YFR6

**plan-039 pass 3 — M2b: SC7 unsatisfiable, and review-induced (both halves added by one resolution)**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:6` |
| Type | review-pass |
| Locator | `docs/plans/plan-039-james-dixson-150f79/reviews/pass-3.md:52-58` |
| Credibility | 88 / high_trust |

> "2.5 says a missed fixture "is a finding, not a tuning signal… a second miss escalates rather than iterates". SC7 required 4 × `FLAGGED`. If a fixture legitimately does not fire and the operator accepts that, SC7 can never be satisfied — so the only route to completion is to tune until it flags, exactly the confirmation bias 2.5 exists to prevent. Both were added by the same resolution; neither noticed the other."

*Note:* high_trust — self-incriminating (names the plan's own prior revision as the author of both halves) and mechanically checkable. A second yf M2b instance, and simultaneously an M6a instance.

### YFR7

**plan-010 pass 1 — M3: installed copy diverges from the canonical tree mid-execution**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:7` |
| Type | review-pass |
| Locator | `docs/plans/plan-010-james-dixson-73eebd/reviews/pass-1.md:23-31` |
| Credibility | 82 / high_trust |

> "Self-rename hazard: `bdplan → yf-plan` breaks the executor mid-flight — severity: high. The skill driving this plan is installed at `~/.claude/skills/bdplan`. … any bdplan subcommand re-resolving `SKILL_DIR` or reading `.state/bdplan/` against the renamed canonical tree can fail; the installed `~/.claude` copy still says `bdplan`, so driver and canonical tree diverge."

*Note:* high_trust — an independent M3 (deploy-parity) instance from the review surface, found before execution rather than after. Note this does NOT extend M3's generality beyond yoshiko-flow, which remains [insufficient evidence] per triangulation §5.

### YFR8

**plan-043 pass 1 — M5: the plan violates the repo's own unconditional SPEC-first rule**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:8` |
| Type | review-pass |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-1.md:50` |
| Credibility | 85 / high_trust |

> "**Epic 3 makes behavior changes with no SPEC issue.** 3.3 changes `close_cascade.py`'s documented exit-code contract; 3.2 changes observable `log.md` behavior that REQ-DATA-016 parsers key on. Epics 0/1/2 each carry a SPEC issue; Epic 3 has none, violating the project's SPEC-first rule."

*Note:* high_trust — one of four independent instances (plan-026 C2, plan-039 M4, plan-041 C11, plan-043 C3) of the same always-loaded, unconditional written rule being violated by a plan in the repo that authored it. Strong M5 corroboration on a new surface.

### YFR9

**plan-026 pass 1 — M5: Epic 4 has no SPEC-first issue; 'repo mandate is unconditional'**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:9` |
| Type | review-pass |
| Locator | `docs/plans/plan-026-james-dixson-6e0e2f/reviews/pass-1.md:21` |
| Credibility | 85 / high_trust |

> "Epic 4 has no SPEC-first issue, yet introduces new observable behavior (report vs crash). Repo mandate is unconditional."

*Note:* high_trust — the reviewer explicitly notes the rule is unconditional, i.e. no interpretive latitude was available. M5's cleanest form: a stated rule with no executing gate, skipped.

### YFR10

**plan-022 pass 1 — M5: 'Do not drop a working fallback on a prose-only floor'**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:10` |
| Type | review-pass |
| Locator | `docs/plans/plan-022-james-dixson-14b3dd/reviews/pass-1.md:18` |
| Credibility | 80 / high_trust |

> "Epic 1 drops the raw-dolt fallback, but there is **no runtime bd-version floor** — pins are documentary only. An operator on bd 1.0.x passes preflight then hits the 1.1.0-only `bd dolt commit` embedded hatch → broken repair. … Do not drop a working fallback on a prose-only floor."

*Note:* high_trust — states M5's generalisable principle verbatim and prospectively ('pins are documentary only'), independent of the four instances where the rule was actually violated.

### YFR11

**plan-041 pass 2 — the never-shown-RED test (DC-2 'false pass' shard), identified but at pass 2**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:11` |
| Type | review-pass |
| Locator | `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-2.md:45` |
| Credibility | 82 / high_trust |

> "**The Capability Gate's test is never shown RED before the fix.** `1.2 depends-on 1.1`, so the test is authored after the fix and only ever observed passing. A test green because it does not exercise the addition path is indistinguishable from one green because the fix works — the C2 failure mode one level up. The plan shows it understands the trap ("a content-edit test would pass even with the bug present") but does not close it."

*Note:* high_trust — upgrades triangulation's [insufficient evidence] 'false pass' shard from one repo (pybridge) to two. Also self-limiting: the reviewer credits the plan with understanding the trap while noting it did not close it, which is against the reviewer's rhetorical interest.

### YFR12

**plan-043 pass 2 — M6a: 'a defect I introduced in the pass-1 revision'**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:12` |
| Type | review-pass |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-2.md:18` |
| Credibility | 92 / high_trust |

> "**The high concern is a defect I introduced in the pass-1 revision**, not a pre-existing one."

*Note:* high_trust — maximally self-incriminating: first-person attribution of a high-severity defect to the author's own prior revision. Resolves M6a's [insufficient evidence] flag for yoshiko-flow.

### YFR13

**plan-043 pass 2 — M6a/M6b: operator's own resolution row attributes the gate off-by-one to the renumber**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:13` |
| Type | review-pass |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-2.md:82` |
| Credibility | 92 / high_trust |

> "Gate `Blocks` off-by-one after renumbering | high | Fixed: `Blocks: Issue 1.3, Issue 2.2`; Instructions now read "the two **wiring** issues (1.3, 2.2), not the verb implementations (1.1/2.1)". **My error, introduced when Epic 2 was renumbered after dropping the delta** — the gate's targets did not shift with the issues."

*Note:* high_trust — first-person, against interest, and names the mechanism (renumbering) that this cluster identifies as M6b's dominant trigger in yoshiko-flow. Note: the 'Fixed' claim in this row was itself later found NOT to have landed (see source 27) — quote the attribution, not the fix status.

### YFR14

**plan-039 pass 3 — M6a regression: 'the H1 fix reproduces the H1 defect'**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:14` |
| Type | review-pass |
| Locator | `docs/plans/plan-039-james-dixson-150f79/reviews/pass-3.md:16,40-48` |
| Credibility | 92 / high_trust |

> "Three do not fully land, and one — the H1 fix — reintroduces the exact defect class H1 named, inside its own remedy. … **C1 — SC6 is falsified by measurement, again. The H1 fix reproduces the H1 defect.** … The new matches come from text the H1 resolution itself added: 3.4's stop-rule blockquote, 3.4b's own prose, and "redeploying" in the SC trailer."

*Note:* high_trust — the yf corpus's sharpest M6a(regression) instance because it is MEASURED, not argued: the reviewer re-ran the classifier and reports the exact residual signal count (3, two high-tier) against the criterion's required 1.

### YFR15

**plan-043 pass 2 — M6b: gate Blocks set not renumbered; the gate would fail to prevent its own target outcome**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:15` |
| Type | review-pass |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-2.md:50` |
| Credibility | 88 / high_trust |

> "**The Capability Gate's `Blocks` set was not renumbered when Epic 2 lost its old 2.1.** Epic 2 is now 2.1=verb, 2.2=**wiring**, 2.3=test — but the gate still said `Blocks: 1.3, 2.3`, and its Instructions still named 2.2 as a verb. Net effect: **Issue 2.2 could wire the audit into §6.4 while `REQ-COMPLETE-001` still read "fixed three-step order"** — precisely the outcome the gate exists to prevent."

*Note:* high_trust — load-bearing M6b: a stale identifier inside a GATE, the same cost shape as cross-repo-corpus:20 (pybridge's reconcile-gate carve-out referencing a closed bead). Resolves M6b's [insufficient evidence] flag for yoshiko-flow on its native surface.

### YFR16

**plan-039 pass 4 — M6b: the fix repaired the criterion but not the sentence naming it; 'third location'**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:16` |
| Type | review-pass |
| Locator | `docs/plans/plan-039-james-dixson-150f79/reviews/pass-4.md:41-49` |
| Credibility | 88 / high_trust |

> "The C1 resolution repaired the criterion but not the sentence naming it, so the plan claimed and denied the same thing — and Approach is what an executor reads first. An executor taking it literally concludes Epic 3 failed, and the obvious remedy … is exactly what R3, 3.4's stop rule, and 3.4b forbid. Same defect class as H1 and C1, in its third location."

*Note:* high_trust — the classic DC-3(a)/M6b shape (same claim surviving at an uncorrected site) with an explicit executor-facing cost, and the reviewer counts the recurrence ('third location') rather than treating it as isolated.

### YFR17

**plan-043 pass 3 — M6b: a fix that did not propagate to the criterion checked at close**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:17` |
| Type | review-pass |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-3.md:57` |
| Credibility | 85 / high_trust |

> "**C18's fix did not propagate to SC2 or D10.** Issue 0.3 required enumerating every invocation, but SC2 — *the criterion checked at close* — still specified the superseded capture-only key. An implementer building capture-only enumeration would **satisfy SC2 and D10 while violating Issue 0.3**, leaving R8 unmitigated by the exact mechanism C18 identified."

*Note:* high_trust — the sharpest cost statement for M6b in the corpus: the residue sits in the success criterion, so an implementer could satisfy the gate while violating the requirement it gates.

### YFR18

**plan-041 pass 2 — M6b: bundle-level residue after a plan split (index.md, log.md, risks, experiments)**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:18` |
| Type | review-pass |
| Locator | `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-2.md:47-48` |
| Credibility | 85 / high_trust |

> "**Stale artifacts the split left behind (aggregate).** `index.md`'s summary still describes the moved sync deliverable — the first thing a cold reader sees. `log.md` has no entry for the split and `status:` was still `review`. … **Decisions got a MOVED pointer; epics, issues and risks did not.** Epics jump 0→1→3→4; risks run R2, R2a, R3, R5, R7, R9 with R1/R4/R6/R8 silently gone. A reader cannot distinguish "moved to plan-042" from "lost in editing"."

*Note:* high_trust — extends M6b beyond plan.md to the OKF bundle's reserved files (index.md, log.md), and names the cold-reader portability cost the plan-folder contract exists to protect. Contemporaneous and enumerated.

### YFR19

**plan-026 pass 1 — M7: epic premise factually wrong; the capability already exists**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:19` |
| Type | review-pass |
| Locator | `docs/plans/plan-026-james-dixson-6e0e2f/reviews/pass-1.md:20` |
| Credibility | 88 / high_trust |

> "Epic 4 premise factually wrong for md2pdf: it **already** has `check_deps()` (REQ-MDPDF-003) exiting with a named-tool message. 4.3's run-guard is redundant for md2pdf."

*Note:* high_trust — M7's 'no longer true / already delivered' sub-shape (cross-repo DC-5), caught at pass 1 by reading the code rather than the plan's description. Later independently confirmed at pass 2 against md2pdf.py:76-82.

### YFR20

**plan-041 pass 2 — M7: the plan promoted a code comment into a SPEC requirement**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:20` |
| Type | review-pass |
| Locator | `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-2.md:43` |
| Credibility | 90 / high_trust |

> "**Epic 0 amends a requirement that does not contain what the plan says it contains.** `REQ-YF-PRE-009` (`SPEC.md:634-646`) is entirely about the preflight **self-update offer**; `grep -n "rerun-if|build\.rs" SPEC.md` returns **nothing**. The "deliberately emit NO rerun-if-changed" stance lives only in the `build.rs:51-58` *comment* … The plan promoted a code comment into a SPEC requirement."

*Note:* high_trust — the reviewer runs a DISCONFIRMING grep and quotes its empty result, which is the strongest form of premise verification available. This is cross-repo DC-7's prescribed remedy ('cite the artifact, not the prose') executed unprompted.

### YFR21

**plan-024 pass 1 — M10: a named consumer with no issue, gate, or follow-up; 'drop it or file it'**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:21` |
| Type | review-pass |
| Locator | `docs/plans/plan-024-james-dixson-76cee9/reviews/pass-1.md:60-61` |
| Credibility | 80 / high_trust |

> "the "land-the-plane sweep" consumer named in the Objective/justification is not scheduled (no issue/gate/follow-up). Drop it from the justification or file it."

*Note:* high_trust — M10 (a precise diagnosis never routed into work) caught prospectively at review, with the binary remedy stated. Corroborates history-and-upstream's M10 from a different venue: here the process caught it, elsewhere it did not.

### YFR22

**plan-033 pass 4 — M11: a compiled-in guess shipped at an [uncertain] real target, failing silently**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:22` |
| Type | review-pass |
| Locator | `docs/plans/plan-033-james-dixson-46aca2/reviews/pass-4.md:29` |
| Credibility | 72 / verify |

> "**Pi rule deployment ships a compiled-in guess to an `[uncertain]` target** … The plan can't even choose: "pi `~/.pi/agent/AGENTS.md` **or** `APPEND_SYSTEM.md`" (semantically different) … Reversibility doesn't save it: a wrong target means the block is written to a file Pi never reads and rules **silently don't load** — invisible to an operator who never runs `--revert`. Textbook hidden-unknown mis-filed as implementation."

*Note:* high_trust — M11 (real-target reality) caught at review with the correct prescribed remedy: convert the hidden unknown into an INVESTIGATE spike before the epic codes it. Matches triangulation C4's positive counterpart (probe/spike before dependent work).

### YFR23

**plan-030 pass 1 — M11/M1: a success-criterion regex that would never match the real file**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:23` |
| Type | review-pass |
| Locator | `docs/plans/plan-030-james-dixson-65526e/reviews/pass-1.md:21` |
| Credibility | 85 / high_trust |

> "The `validated:` evidence line uses the **retired** inline-date phase-log format and greps `plan.md`. REQ-DATA-012 relocated the live log to reserved `log.md` … the date is in the heading, not the bullet. The proposed `^- \d{4}-\d{2}-\d{2} validated:` regex against plan.md would never match."

*Note:* high_trust — the 'can never pass' shard of cross-repo DC-2, caught at pass 1 by checking the criterion's regex against the real file format. Further evidence that this repo's review runs/checks commands rather than reading them for intent.

### YFR24

**plan-041 pass 1 — M14b (NEW): five conformance defects survive only as a parenthesis; the conformance pass writes no file**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:24` |
| Type | review-pass |
| Locator | `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-1.md:17-21` |
| Credibility | 78 / verify |

> "Conformance pass ran first and returned **PASS** (after two INCOMPLETE rounds: an uncompleted `upstream-triage.md`, an Upstream Issues note that contradicted the revised D1/D2, a double-deliverable Issue 2.6, two success criteria with no verification handle, and a dangling `2.6` edge left by the split). Conformance is mechanical and produces no `pass-N.md`; this file records the adversarial pass."

*Note:* high_trust — the single source establishing that yoshiko-flow runs a second, mechanical review layer whose findings are discarded. Five real defects (including a dangling dep edge and two unverifiable criteria) are recoverable only because one reviewer summarised them in a parenthesis. Widens M14 with a concrete, quantified mechanism.

### YFR25

**plan-041 pass 2 — M6c (NEW): a resolution row asserting something the plan does not contain**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:25` |
| Type | review-pass |
| Locator | `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-2.md:18-19,50` |
| Credibility | 88 / high_trust |

> "The reviewer verified each pass-1 resolution landed in `plan.md` rather than merely being asserted in the resolutions table — and caught one that had not (C18). … **M3's resolution did not land.** pass-1 marks it `resolved — falsifier recorded in the E2 block`, but `grep -rn "falsif"` across the bundle hits **only `reviews/pass-1.md`**. A resolution row asserting something the plan does not contain is the failure mode this cycle exists to catch."

*Note:* high_trust — mechanically verified (the reviewer quotes the grep and its scope), self-incriminating, and names the class. First of three M6c instances.

### YFR26

**plan-041 pass 3 — M6c: a second claimed reconciliation that had not landed**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:26` |
| Type | review-pass |
| Locator | `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-3.md:49` |
| Credibility | 82 / high_trust |

> "N1 | Approach said "Three active workstreams" while naming four epics — C16's claimed reconciliation had not landed | Corrected to "Four active workstreams". | resolved"

*Note:* high_trust — a second M6c instance in the SAME bundle one pass after the first, which is the strongest available evidence that the class is a repeatable process failure rather than a one-off slip.

### YFR27

**plan-043 pass 3 — M6c with a named mechanism: a line-wrapped string made two replacements silent no-ops**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:27` |
| Type | review-pass |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-3.md:21-26,88` |
| Credibility | 90 / high_trust |

> "**C22 caught a resolution asserted in pass-2's table that did not land in the plan body.** … The cause was mundane and worth recording: the target string wrapped across a line break, so two successive replacements silently matched nothing while the resolutions table was updated as if they had. **The lesson is that a resolution is not resolved until it is grepped**, and that is now how this bundle's fixes are verified. … The two prior replacements failed because the string wraps across a line break — a silent no-op that pass-2's table nonetheless recorded as resolved."

*Note:* high_trust — the most important source in this cluster. Self-incriminating, names the exact mechanism (line-wrapped literal → zero-match replacement reporting success), and identifies M6c as an instance of M1 (succeeds visibly while doing nothing) applied to the process's own bookkeeping. Also supplies the HINDSIGHT-clearing remedy verbatim.

### YFR28

**plan-040 pass 3 — the reviewer's stated evidentiary bar: verified by running a command**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:28` |
| Type | review-pass |
| Locator | `docs/plans/plan-040-james-dixson-1cabe4/reviews/pass-3.md:10` |
| Credibility | 65 / verify |

> "REVISE only for defects that would break execution, make a deliverable unverifiable, or mislead upstream — verified by running a command or quoting contradicting text."

*Note:* high_trust — the run-the-command discipline stated as an explicit reviewer instruction rather than inferred from behavior. Load-bearing for the revised calibration in §7.3: this repo's review practice EXECUTES, which is why it catches the M1 shard that d3-pxe's review missed three passes running.

### YFR29

**plan-039 pass 4 — the vacuous-pass check run in the other direction**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:29` |
| Type | review-pass |
| Locator | `docs/plans/plan-039-james-dixson-150f79/reviews/pass-4.md:31-32` |
| Credibility | 65 / verify |

> "**SC11 and SC1b are both discriminating, verified live.** `evidence` and `code span` occur zero times in `spec/cli.md` today, so SC1b cannot pass vacuously."

*Note:* high_trust — demonstrates the reviewer checking that a criterion cannot pass for the wrong reason (matching nothing), not merely that it passes. Mechanical and reproducible.

### YFR30

**plan-026 passes 6-7 — the M6b remedy (grep-complete residue enumeration) applied and verified**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:30` |
| Type | review-pass |
| Locator | `docs/plans/plan-026-james-dixson-6e0e2f/reviews/pass-6.md:11 and pass-7.md:13` |
| Credibility | 72 / verify |

> "**But the Issue 5.3 de-list list is materially incomplete** — it enumerates three lint surfaces and misses ≥3 more in-repo references that trip named `required` DRIFT-CHECK edges. … [pass 7] **Grep-complete coverage, verified.** All 7 in-repo references (excluding the script, `__pycache__`, `docs/plans/`) are explicitly de-listed"

*Note:* high_trust — a worked, two-pass demonstration that cross-repo DC-3(a)'s prescribed remedy ('grep the whole bundle and list every site') is practicable and effective. Independently arrived at in a different repo from the one that proposed it.

### YFR31

**plan-043 pass 4 — the M6c remedy implemented: every resolution verified by grep with its count**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:31` |
| Type | review-pass |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-4.md:19-24,28` |
| Credibility | 72 / verify |

> "All four cycle-3 concerns verified **by grep against `plan.md`**, not by reading the resolutions table — the discipline this bundle earned after two instances of a resolution asserted but not landed. | C22 | `grep -c '1\.1/2\.2'` → **0**; exactly one `1.1/2.1` at L428. Line-wrapped variants also checked — none. | LANDED | … "The C22 wrap-across-linebreak failure that silently no-op'd twice is genuinely fixed this time — the string now sits entirely on line 428 and the count is zero by direct grep, not by inference.""

*Note:* high_trust — the corpus's clearest instance of a stated, checkable process step being derived from a defect and then working. Each verification carries its command and its count, satisfying M5's 'a step with no exit code is not a step'.

### YFR32

**plan-026 pass 4 — two mediums three prior passes missed; a delta-scoped pass does not discharge whole-plan review**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:32` |
| Type | review-pass |
| Locator | `docs/plans/plan-026-james-dixson-6e0e2f/reviews/pass-4.md:3-9` |
| Credibility | 85 / high_trust |

> "**Context:** operator-requested full, fresh, whole-plan adversarial review (not delta-scoped) of the re-scoped plan-026. … Supersedes the delta-only pass-3 for readiness purposes. … **Two medium concerns three prior passes missed**, both verified against real code: a SPEC-first guardrail conflict introduced by #85, and an Epic-2 reader directive that would regress `md2pdf`."

*Note:* high_trust — quantifies review escape WITHIN a bundle (2 defects survived 3 passes) and names the structural cause as pass scope rather than diligence, which yields a checkable rule. The deepest-N review-escape datum available in the corpus.

### YFR33

**plan-039 pass 5 — counter-evidence: a revision cycle that introduced no defect**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:33` |
| Type | review-pass |
| Locator | `docs/plans/plan-039-james-dixson-150f79/reviews/pass-5.md:17` |
| Credibility | 68 / verify |

> "the resolution table. The three low ones are resolved too. No defect introduced by the pass-4 [revisions]"

*Note:* high_trust — mandatory counter-evidence for M6a. The revision step is a defect-introducing step with a nonzero rate (2 of 4 cycles in this bundle), not a step that always regresses. Prevents the synthesizer overstating M6a.

### YFR34

**Surface quantification — 93 review passes across 43 bundles, counted mechanically**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:34` |
| Type | plan-bundle |
| Locator | `docs/plans/*/reviews/` |
| Credibility | 85 / high_trust |

> "43 bundles; 93 reviews/pass-*.md files; 42 bundles with >=1 pass; 29 with >=2; 1 with 0 (plan-042-james-dixson-98631b, empty reviews/); max 7 (plan-026). Depth: pass-1 42, pass-2 29, pass-3 10, pass-4 5, pass-5 4, pass-6 2, pass-7 1. Verdicts: pass-1 41 REVISE / 1 APPROVE; pass-2..7 22 REVISE / 29 APPROVE; 13 later passes carry a high-severity concern; M6a's signature (a pass naming a defect in a prior pass of the same bundle) fires in 8 of 51 later passes across 5 bundles."

*Note:* high_trust — mechanical enumeration of the filesystem and of each file's declared verdict line; fully reproducible. Confirms triangulation §4.1's structural counts (93 passes, 29 bundles with >=2) independently.

### YFR35

**Verified absence — no review pass names a defect in a different plan bundle**

| Field | Value |
| :-- | :-- |
| uid | `yf-corpus-reviews:35` |
| Type | plan-bundle |
| Locator | `docs/plans/*/reviews/*.md` |
| Credibility | 85 / high_trust |

> "Recursive grep for `plan-0[0-9][0-9]` across every bundle's reviews/, excluding each bundle's own id: 63 hits, dominated by plan-042 (23, all in plan-041's reviews, referring to the plan it was split into) and plan-013 (10, cited as a d3-pxe fixture source). Every hit is a scoping, sequencing or precedent reference; none attributes a defect to another bundle."

*Note:* high_trust — mechanical verified-absence check. Establishes that the review surface is bundle-local and structurally cannot produce remediation pairs, so this cluster and cluster-yf-corpus.md are non-overlapping by construction rather than by retriever choice.


---

## execution-telemetry (ET) — 15 sources

### ET1

**Live bd issue census across the five corpus repos**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:1` |
| Repo | all-5 |
| Type | bead-graph |
| Locator | `bd list --status all --json --limit 0 --include-gates --include-infra (per repo, 2026-08-16)` |
| Credibility | 90 / high_trust |

> "yoshiko-flow issues 1176 edges 2182 Counter({'blocks': 1085, 'parent-child': 1067, 'discovered-from': 25, 'relates-to': 4, 'related': 1}) | d3-pxe issues 501 edges 943 Counter({'parent-child': 470, 'blocks': 467, 'discovered-from': 4, 'relates-to': 2}) | pybridge issues 229 edges 406 Counter({'blocks': 203, 'parent-child': 188, 'discovered-from': 15}) | evri_py issues 304 edges 536 Counter({'parent-child': 272, 'blocks': 256, 'discovered-from': 8}) | emacs.d issues 58 edges 68 Counter({'blocks': 37, 'parent-child': 30, 'discovered-from': 1})"

*Note:* Mechanical enumeration of / quotation from the live bd graph. Reproducible; close reasons are written at close time and are therefore contemporaneous.

### ET2

**plan-004 records an epic id under the retired beads-skills prefix**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:2` |
| Repo | yoshiko-flow |
| Type | plan-bundle |
| Locator | `docs/plans/plan-004-james-dixson-56f494/plan.md:7,15` |
| Credibility | 88 / high_trust |

> "**Epic:** beads-skills-mol-nxk ... - 2026-06-01 intake: epic beads-skills-mol-nxk poured"

*Note:* Mechanical grep of a header field, quoted verbatim with line numbers, reproducible.

### ET3

**The 14 beads-skills-* epic pointers resolve to nothing**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:3` |
| Repo | yoshiko-flow |
| Type | bead |
| Locator | `bd show beads-skills-mol-nxk / bd show beads-skills-mol-806; prefix census over 1176 ids` |
| Credibility | 90 / high_trust |

> "Error fetching beads-skills-mol-nxk: no issue found matching "beads-skills-mol-nxk" || beads-skills-prefixed ids: 0 || prefixes: Counter({'yf': 1176}) || suffix probe nxk/5tv/g0b/s3x/14o/bjf/yvv/r8z/2bi/glo/mqa/itd/3ee/806: no candidate for any of the 14"

*Note:* Mechanical enumeration of / quotation from the live bd graph. Reproducible; close reasons are written at close time and are therefore contemporaneous.

### ET4

**Dangling epic pointers and orphan plan-execute molecules**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:4` |
| Repo | all-5 |
| Type | bead-graph |
| Locator | `derived: bundle-epic set vs bd molecules (issue_type=molecule) per repo` |
| Credibility | 60 / verify |

> "yoshiko-flow: dangling epic ids 14 / no-epic-recorded 5; molecules=49 claimed=24 orphan=25 (16 of them 'plan-execute' dated 2026-06-01..2026-06-25 under hash ids yf-dfabdd38, yf-fb0bc064, yf-5e06c253, ...). d3-pxe: dangling 0, orphan 7 (all yf-research / plan-investigate wisps). pybridge: dangling 0, orphan 1 = pybridge-mol-edn 'plan-execute' 2026-05-26. evri_py: dangling 0, orphan 2 = evri_py-mol-itou 2026-05-19, evri_py-mol-xsdxn 2026-05-20. emacs.d: dangling 0, orphan 0."

*Note:* Molecule-to-bundle mapping is DATE-INFERRED, never recorded; the retriever flags it [uncertain] itself. The orphan-molecule and dangling-pointer counts are mechanical (high); the one-to-one attribution is inference (low).

### ET5

**Early bundles omit the Epic header field entirely**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:5` |
| Repo | pybridge,evri_py,emacs.d |
| Type | plan-bundle |
| Locator | `grep -nE '^\*\*(Epic\|Status)' pybridge/docs/plans/plan-002-james-dixson-f111ab/plan.md evri_py/docs/plans/plan-00{2,3,4}*/plan.md emacs.d/docs/plans/plan-001*/plan.md` |
| Credibility | 88 / high_trust |

> "evri_py plan-004 .../plan.md:6:**Status:** approved (lightweight rollup; no review cycle) | pybridge plan-002 .../plan.md:6:**Status:** complete | evri_py plan-003 .../plan.md:6:**Status:** complete | evri_py plan-002 .../plan.md:6:**Status:** executing | emacs.d plan-001 .../plan.md:6:**Status:** drafting -- no **Epic:** line matched in any of them"

*Note:* Mechanical grep establishing the Epic header is ABSENT (not empty) across named bundles in three repos. Reproducible.

### ET6

**Full discovered-from edge dump with endpoint titles**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:6` |
| Repo | all-5 |
| Type | bead-graph |
| Locator | `derived: 53 discovered-from edges, each resolved to both endpoint beads` |
| Credibility | 90 / high_trust |

> "pybridge-5ap <-discovered-from- pybridge-mol-edn.5.3 : NEW "Standalone bundle isn't actually standalone: relocatable venv references build-runner CPython" FROM "5.3 Bundle re-test: verify quarantine present-then-cleared, smoke against bundle Python" ;; pybridge-aey <- pybridge-mol-66l : "Windows self-hosted runner: cmake not on cmd PATH - breaks all Windows MEX builds" ;; evri_py-fes <- evri_py-mol-rxg.4.1 : "Doc gap: PRD has no REQ-* for SVM (svm/svmda) algorithm" ;; evri_py-r4l <- evri_py-mol-rxg.5.1 : "Doc gap: SPEC has no field-level schema for pybridge-standalone.json manifest" ;; yf-m78m <- yf-mol-3ct.3.3 : "yf-plan README.md stale: still lists README.md as plan-folder orientation file (pre-OKF), contradicts index.md/log.md in SPEC REQ-PLAN-010 + SKILL.md" FROM "Exit gate: lint audit + 0-warning build + drift-check PASS" ;; d3-pxe-mol-e49.3.4 <- d3-pxe-mol-e49.3.1 : "3.1a raw_conf: replace blockinfile markers with marker-less lineinfile (PVE canonicalizes 100.conf under active API module, mangling comment markers -> duplicate lxc.* lines)" ;; pybridge-jfc <- pybridge-08b : "testArrayTransferMultiDim fails on main - 2D row/col-major assertion (#21 closed but multidim regresses)" ;; pybridge-bd4 / pybridge-gsx / pybridge-vk8 all <- pybridge-hax "Platform-specific testing: Windows Python variants, macOS Gatekeeper, Linux glibc" at 2026-06-21T17:00:20-21Z. Aggregate: 44/53 cross a molecule boundary; 0/53 connect two plan epics; 24/53 originate inside a resolvable plan subtree."

*Note:* Mechanical enumeration of / quotation from the live bd graph. Reproducible; close reasons are written at close time and are therefore contemporaneous.

### ET7

**Post-pour additions into a plan's own molecule are near-zero**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:7` |
| Repo | all-5 |
| Type | bead-graph |
| Locator | `derived: per plan molecule, subtree beads created >1h and >24h after the earliest subtree created_at` |
| Credibility | 90 / high_trust |

> "55 plans with a resolvable graph; total beads created >1h after pour = 23, >24h = 4. 51 of 55 plans added nothing. Non-zero rows only: evri_py p008 (sub=41, >1h=14, >24h=4, 34.1% late); yoshiko-flow p021 (33/2/0, 6.1%); yoshiko-flow p030 (18/2/0, 11.1%); d3-pxe p003 (27/2/0, 7.4%); pybridge p010 (22/1/0, 4.5%); d3-pxe p010 (37/1/0, 2.7%); d3-pxe p013 (35/1/0, 2.9%)."

*Note:* Mechanical enumeration of / quotation from the live bd graph. Reproducible; close reasons are written at close time and are therefore contemporaneous.

### ET8

**About half of in-window ad-hoc beads carry no discovered-from edge**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:8` |
| Repo | pybridge,emacs.d,evri_py |
| Type | bead-graph |
| Locator | `derived: free-standing beads created inside a plan's execution window, split by whether they carry a discovered-from edge` |
| Credibility | 72 / verify |

> "pybridge p003 window 2026-06-17..06-18: 4 ad-hoc beads, 2 with a discovered-from edge; p004: 3 / 1; p005: 5 / 3; p006: 3 / 1; p007: 2 / 0; p008: 2 / 0; p009: 5 / 3; evri_py p005: 6 / 4; p006: 2 / 0; emacs.d p002: 2 / 0; p003: 2 / 0; p004: 2 / 0. (Pooled corpus figure 908/71 DISCARDED as unreliable: yoshiko-flow windows inflate to months because subtree updated_at was touched long after close.)"

*Note:* Deliberately restricted to the short-window subset; the retriever discarded its own pooled figure (908 candidates vs 71 edges) as unreliable because yf subtree updated_at values were touched long after close. Directionally sound, not a rate.

### ET9

**Gate: Tri-Platform Green - the corpus's only recorded operator override**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:9` |
| Repo | pybridge |
| Type | bead |
| Locator | `pybridge-mol-66l.6 (gate, closed, created 2026-06-17T23:15:19Z)` |
| Credibility | 90 / high_trust |

> "OPERATOR OVERRIDE: macOS + Linux jobs green (19/19 incl. 500MB) in run 27734768524. Windows blocked at Configure CMake by pre-existing runner regression (cmake off cmd PATH ~2026-05-26, also breaks releases) - NOT a plan-003 code defect. Tracked as pybridge-aey; real Windows CI validation deferred to that runner fix."

*Note:* Mechanical enumeration of / quotation from the live bd graph. Reproducible; close reasons are written at close time and are therefore contemporaneous.

### ET10

**evri_py plan-006 closed with four work units deliberately undone; five gates still open corpus-wide**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:10` |
| Repo | evri_py |
| Type | bead |
| Locator | `evri_py-mol-eoz.3, .5, .6, .10 (all closed 2026-06-21); evri_py-mol-e3d.6/.7, evri_py-mol-xsdxn.9, evri_py-mol-itou.14/.16 (gates, open)` |
| Credibility | 90 / high_trust |

> "Plan-006 closed; §6 direct-fit chain deferred to evri_py#49 / pybridge#10. Re-pour a follow-up plan when pybridge#10 ships refcounted handles. [identical close_reason on eoz.3 'Epic 1: Direct fit/predict (#17, pybridge#10)', eoz.5 'Epic 2: Cross-PyObject proxy-arg helpers (#18, pybridge#11)', eoz.6 'Epic 3: NV pairs -> kwargs (#22, pybridge#15)', eoz.10 'Reconcile: close #17/#18/#21/#22/#39/#40 upstream'] || open gates: evri_py-mol-e3d.6 'Capability Gate: Windows WiX toolchain on the runner', e3d.7 / xsdxn.9 / itou.16 'Gate: Reconcile upstream', itou.14 'Gate: pybridge dispatch wired' (open since 2026-05-19)"

*Note:* Mechanical enumeration of / quotation from the live bd graph. Reproducible; close reasons are written at close time and are therefore contemporaneous.

### ET11

**plan-006 pre-registered risk R1, and R1 fired exactly as written**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:11` |
| Repo | evri_py |
| Type | plan-bundle |
| Locator | `docs/plans/plan-006-james-dixson-38b166/plan.md:18,21,22,211-215,225-231` |
| Credibility | 88 / high_trust |

> "**R1 - a v0.1.32 probe may fail (operator decision 2026-06-21: treat as regression).** The pybridge fixes are **assumed present** in v0.1.32 (all six issues closed COMPLETED). If an Epic 0 probe fails, it is a **pybridge regression**, not a version mismatch: **reopen the corresponding pybridge issue (#10/#11/#12/#14/#15) with the failing probe context** (bundle version, MATLAB transcript, expected vs actual), and mark that single rewrite **blocked pending pybridge** - do not bump the pinned version and do not rewrite that section against a broken capability. ... - 2026-06-21 executing: R1 fired for #10 - pybridge#10 REOPENED (incomplete-fix root cause + repro). Epic 1 (#17) blocked on new gate eoz.12; transitive chain Epics 2/3/5/6 (#18/#22/#40/#39) held. Operator chose option C (hybrid: file upstream + proceed Epic 4 + hold chain). - 2026-06-21 reconciling: PARTIAL LANDING - merged plan-006 to main ... #17/#18/#22 stay OPEN, annotated with reopened pybridge#10 block. 4 of 6 issues done ... Plan stays executing (partial) - 2026-06-21 complete: plan closed (partial); §6 chain deferred to evri_py#49 / pybridge#10"

*Note:* Contemporaneous on both halves: the risk R1 was pre-registered in plan.md BEFORE execution, and its firing is recorded in the dated phase log. This is the corpus's cleanest prospective-then-outcome record and is the strongest single source for the positive finding (M13).

### ET12

**3.4 Prove the absence alert fires against its REAL production threshold - descoped, cause recorded as structurally un-previewable**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:12` |
| Repo | d3-pxe |
| Type | bead |
| Locator | `d3-pxe-mol-qoz.3.4 (task, closed, created 2026-08-13T04:48:01Z)` |
| Credibility | 90 / high_trust |

> "DESCOPED by operator decision 2026-08-13. There is no alert to trip, so the deliberate CT 107 outage was NOT performed and no monitoring gap was created on the guest holding pool1/postgres. Cause: Issue 3.2's apply of the nine absence alerts failed with HTTP 400 {"code":400,"message":"Alert destinations is required"} - OpenObserve v0.91.3 rejects an alert with an empty destinations array, so all nine bodies failed identically and ZERO alert objects exist on CT 104. The plan's UI-only fallback is therefore not merely undesirable but IMPOSSIBLE: there is no degraded mode, without a destination there is no alert at all. Structurally un-previewable - ansible.builtin.uri has no check-mode support, so 3.1's fleet-wide --check skipped the POST; exp-011 §6 pre-registered exactly this residual risk and it fired. Operator chose 'keep the IaC dormant, descope the apply' ... CONSEQUENCES: SC3 FAILS (the alert exists as committed IaC but was never instantiated, never fired, is not delivered). ... #68's TIME-BASED HALF REMAINS OPEN, tracked by https://github.com/dixson3/d3-pxe/issues/73"

*Note:* Mechanical enumeration of / quotation from the live bd graph. Reproducible; close reasons are written at close time and are therefore contemporaneous.

### ET13

**The stuck-bead sweep is specified everywhere and recorded firing nowhere**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:13` |
| Repo | yoshiko-flow |
| Type | plan-bundle |
| Locator | `docs/plans/plan-004-james-dixson-56f494/plan.md:128-130,202; reviews/pass-1.md:23-24; grep -rniE 'stuck[- ]bead' over all 5 repos' plan roots` |
| Credibility | 85 / high_trust |

> "The sweep **resets** stuck `in_progress`/claimed beads to `open` and **reports** (does not close) anything it cannot classify. Resetting (not closing) keeps the epic non-terminal, so reconcile cannot fire on a resumed-but-incomplete plan. || reviews/pass-1.md:24: 'Resolution (applied, operator-confirmed): sweep is now **reset + report, never auto-close**.' || The grep across yoshiko-flow, d3-pxe, pybridge, evri_py and emacs.d plan bundles returns only design/spec/reference text - no log line, close reason, or finding recording a sweep that ran."

*Note:* Verified absence: case-insensitive grep for stuck[- ]bead across the plan bundles of all five repos, returning only design/spec text. Reproducible, and the mechanism-specified-but-never-observed shape is corroborated independently by yf-corpus:7 and history-and-upstream:24.

### ET14

**plan_manager.py ships a stuck-bead resume-guard reporter**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:14` |
| Repo | yoshiko-flow |
| Type | plan-bundle |
| Locator | `docs/plans/plan-037-james-dixson-cab694/references/user-scope/plan_manager.py:2565,2587` |
| Credibility | 72 / verify |

> """"Report the plan's epic + stuck-bead state for the coordinator resume-guard.""" ... click.echo(" no stuck beads")"

*Note:* A VENDORED COPY of plan_manager.py inlined under plan-037/references/. It is code, not prose, but it is a snapshot that may lag the live script. Adequate to establish that the reporter was specified; not adequate to establish current behavior.

### ET15

**No bead-level reopen is observable anywhere in the corpus**

| Field | Value |
| :-- | :-- |
| uid | `execution-telemetry:15` |
| Repo | yoshiko-flow |
| Type | plan-bundle |
| Locator | `grep -rniE 'reopen' over yoshiko-flow/d3-pxe/pybridge/evri_py plan roots; docs/plans/plan-026-james-dixson-6e0e2f/reviews/pass-3.md:3` |
| Credibility | 85 / high_trust |

> "**Context:** plan-026 was approved (pass-2 APPROVE), then reopened to fold upstream issue **#85** [the only prose reopen hit that is not yf-beads-upstream 'unhoist' design text: 'unhoist reopen wrongly-hoisted bead(s) from tombstone', 'Un-hoist (restore) - reopen a wrongly-hoisted bead from its tombstone']"

*Note:* Verified absence across four repos' plan roots plus the bd schema. Correctly labelled by the retriever as absence of EVIDENCE (bd exposes no status history), not evidence of absence.


---

## history-and-upstream (HU) — 28 sources

### HU1

**Corpus-wide commit / fix-prefix / revert counts**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:1` |
| Repo | all-five |
| Type | commit |
| Locator | `git log --oneline \| wc -l; git log --format='%s' \| grep -icE '^(fix\|hotfix)'; git log --oneline --grep='^Revert' \| wc -l` |
| Credibility | 80 / high_trust |

> "yoshiko-flow total=391 reverts=0 fixprefix=5 | d3-pxe total=234 reverts=0 fixprefix=0 | pybridge total=242 reverts=0 fixprefix=26 | evri_py total=113 reverts=1 fixprefix=20 | emacs.d total=178 reverts=0 fixprefix=27"

*Note:* Mechanical corpus-wide counts, reproducible. Downgraded from 92 because the fix-prefix axis it measures is shown UNSOUND as a cross-repo comparator by the same retriever (d3-pxe: 0 fix-prefixes, fixes constantly). Cite the commit totals; do not rank repos by fix density.

### HU2

**Per-repo upstream issue inventory**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:2` |
| Repo | all-five |
| Type | issue |
| Locator | `gh issue list -R <repo> --state all --limit 300 --json number,title,state,createdAt,closedAt` |
| Credibility | 85 / high_trust |

> "yf total 141 open 37 closed 104 plan-trackers 17 | pxe total 77 open 42 closed 35 plan-trackers 14 | pyb total 52 open 20 closed 32 plan-trackers 1 | evp total 47 open 16 closed 31 plan-trackers 3 | emd total 8 open 6 closed 2 plan-trackers 0"

*Note:* First-party defect report filed contemporaneously against the operator's own repository, in this corpus almost always carrying an explicit MEASURED block. Self-incriminating (the author reporting a defect in their own tool), which is the strongest prose class available here.

### HU3

**plan-013 wave 1 — authorship of the comma-joined bead-id list (git pickaxe)**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:3` |
| Repo | yoshiko-flow |
| Type | commit |
| Locator | `eba3638 (2026-06-24), skills/yf-beads-upstream/scripts/upstream.py` |
| Credibility | 92 / high_trust |

> "plan-013 wave 1: hygiene reconcile core (B.1/B.2/B.5) + upstream config/hoist/followon (A.1/A.2/A.4/C.1/C.2/C.4/C.6)"

*Note:* Mechanical, contemporaneous git record (sha + subject/diff/body), reproducible by re-running the query. Not prose, not self-serving, and not reconstructed later.

### HU4

**plan-038 Epics 1-2 — the fix for #129, with severity stated in-diff**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:4` |
| Repo | yoshiko-flow |
| Type | commit |
| Locator | `9656eb1 (2026-08-14), skills/yf-beads-upstream/scripts/upstream.py` |
| Credibility | 92 / high_trust |

> "A comma-joined list is matched by bd to ZERO beads while the process still exits 0 (bd 1.1.2), so a comma here is silent data loss, not a formatting nit."

*Note:* Mechanical, contemporaneous git record (sha + subject/diff/body), reproducible by re-running the query. Not prose, not self-serving, and not reconstructed later.

### HU5

**yf-beads-upstream: plan_hoist emits COMMA-separated ids that bd matches to ZERO beads**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:5` |
| Repo | yoshiko-flow |
| Type | issue |
| Locator | `issue #129 (CLOSED 2026-08-14)` |
| Credibility | 85 / high_trust |

> "yf-beads-upstream: plan_hoist emits COMMA-separated ids that bd matches to ZERO beads — multi-bead hoist/land tombstones beads it never pushed"

*Note:* First-party defect report filed contemporaneously against the operator's own repository, in this corpus almost always carrying an explicit MEASURED block. Self-incriminating (the author reporting a defect in their own tool), which is the strongest prose class available here.

### HU6

**plan-011 objective declares itself a remediation of plan-010**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:6` |
| Repo | pybridge |
| Type | plan-bundle |
| Locator | `docs/plans/plan-011-james-dixson-b0aab1/plan.md:25` |
| Credibility | 70 / verify |

> "Capture the two operational-knowledge deliverables that plan-010's execution surfaced but did not write — a release runbook (`docs/specifications/IG/RELEASE.md`, #49) and an agent-facing self-hosted-runner gotchas doc (`AGENTS/CI_RUNNERS.md`, #48)"

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### HU7

**14 post-completion commits, 12 touching release.yml, after plan-010 declared status complete**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:7` |
| Repo | pybridge |
| Type | commit |
| Locator | `6de4bb3..daf28aa (2026-07-15 to 2026-07-16)` |
| Credibility | 92 / high_trust |

> "6de4bb3 plan-010 complete: close epic + reconcile; status complete / d65bf66 release.yml: bump release-path notary budget 45m -> 2h / 7bce4df release.yml: set +e in macOS upload (GitHub bash -e aborted on first 404) / a3af236 release.yml: macOS release upload via flat curl + HTTP-201 check (drop gh/functions)"

*Note:* Mechanical, contemporaneous git record (sha + subject/diff/body), reproducible by re-running the query. Not prose, not self-serving, and not reconstructed later.

### HU8

**plan-008 phase log jumps rc1 -> rc9, omitting seven RC iterations**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:8` |
| Repo | evri_py |
| Type | plan-bundle |
| Locator | `docs/plans/plan-008-james-dixson-d1f1e4/plan.md:22-24` |
| Credibility | 70 / verify |

> "- 2026-07-16 executing: 18/18 tasks complete + pushed (fafd1d4); #7/#50 closed, #54 filed; merge-to-main HELD pending green workflow_dispatch signing test-build (operator decision) - 2026-07-16 executing: v0.2.1-rc1 failed: macOS cert-secret blocker (#56 buildadmin) + Windows uv-build bug (#55, FIXED f831f85). rc1 deleted. rc2 after cert re-provisioned - 2026-07-17 reconciling: rc9 GREEN: macOS+Windows signing validated end-to-end (all 9 bundles signed); begin merge-back"

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### HU9

**Eight RC-fallout fix commits between plan-008's 18/18 and its completion**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:9` |
| Repo | evri_py |
| Type | commit |
| Locator | `f831f85, 872c0ab, 973c63d, 9809bbb, c8de2ac, 7a32983, 5845b31, 97ced85 (2026-07-16 to 2026-07-17)` |
| Credibility | 92 / high_trust |

> "1. Test-command (mine): the smoke test (2.1b) and clean-machine gates (2.3 macOS, 3.2 Windows) invoked `python -m pybridge_kernel --version`, but the pinned kernel CLI has no --version (only --port/--host/--debug) — and running it bare would bind a ZMQ socket and block. [973c63d] ... The bundle itself was already correct; this makes the test faithful. [97ced85]"

*Note:* Mechanical, contemporaneous git record (sha + subject/diff/body), reproducible by re-running the query. Not prose, not self-serving, and not reconstructed later.

### HU10

**plan-008 declares a lesson-transfer step from the parallel pybridge effort**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:10` |
| Repo | evri_py |
| Type | plan-bundle |
| Locator | `docs/plans/plan-008-james-dixson-d1f1e4/plan.md:39-40` |
| Credibility | 70 / verify |

> "The parallel pybridge effort (`eigenvector-research-inc/pybridge` #35/#38/#41) just landed signing + notarization end-to-end and shook out a long, non-obvious list of"

*Note:* LATER-PLAN SELF-DIAGNOSIS of a predecessor — the corpus's most common source type and explicitly NOT neutral. Demonstrably fallible: plan-043's E1 (yf-corpus:6) refuted all three of issue #136's own hypotheses about its own cause. Load-bearing, but every claim resting on it needs mechanical or contemporaneous corroboration.

### HU11

**yf self install --from-build can promote a binary with a STALE embedded skills tree**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:11` |
| Repo | yoshiko-flow |
| Type | issue |
| Locator | `issue #137 (CLOSED 2026-08-16)` |
| Credibility | 85 / high_trust |

> "This is the same class of defect as plan-039's `yf-nkgh` (installed skill lagging the repo) — one level down, in the tool meant to fix it."

*Note:* First-party defect report filed contemporaneously against the operator's own repository, in this corpus almost always carrying an explicit MEASURED block. Self-incriminating (the author reporting a defect in their own tool), which is the strongest prose class available here.

### HU12

**plan-041 fixes #137 SPEC-first with mutation-tested guards**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:12` |
| Repo | yoshiko-flow |
| Type | commit |
| Locator | `c4d51e4 (2026-08-16)` |
| Credibility | 92 / high_trust |

> "SPEC-first: adds REQ-YF-EMBED-004 (a build observes additions under skills/) ... yf/tests/embed_addition.rs (REQ-YF-EMBED-004) asserts BOTH arms every run -- the addition must be ABSENT without the watch lines and PRESENT with them, so it can never be vacuously green."

*Note:* Mechanical, contemporaneous git record (sha + subject/diff/body), reproducible by re-running the query. Not prose, not self-serving, and not reconstructed later.

### HU13

**Absence of plan coverage for four open process-defect issues**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:13` |
| Repo | yoshiko-flow |
| Type | plan-bundle |
| Locator | `grep -rl '#142\|#143\|#144\|#147' docs/plans docs/research -> no matches` |
| Credibility | 86 / high_trust |

> "--- #142 mentioned in plan/research bundles: --- #143 mentioned in plan/research bundles: --- #144 mentioned in plan/research bundles: --- #147 mentioned in plan/research bundles:"

*Note:* Verified absence by grep over every bundle in the repo. Mechanical. Carries the retriever's own recency caveat: four of the issues were filed within ~24h of retrieval, so 'never planned' may be 'not yet triaged'.

### HU14

**closable proposes closing issues that are already closed (or deleted) upstream**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:14` |
| Repo | yoshiko-flow |
| Type | issue |
| Locator | `issue #142 (OPEN)` |
| Credibility | 85 / high_trust |

> "MEASURED: after stamping 18 coarse trackers, `upstream.py closable` proposed 25 closures: - 23 already CLOSED upstream - 2 no longer exist (#139 deleted, and a bare 'gh-91' ref) - 0 genuinely OPEN and actionable ... Before the backfill closable proposed 7; after, 25 — so making trackers visible made the report NOISIER rather than more useful."

*Note:* First-party defect report filed contemporaneously against the operator's own repository, in this corpus almost always carrying an explicit MEASURED block. Self-incriminating (the author reporting a defect in their own tool), which is the strongest prose class available here.

### HU15

**Five plan.md **Epic:** fields are dangling refs to pre-rename beads-skills-mol-* beads**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:15` |
| Repo | yoshiko-flow |
| Type | issue |
| Locator | `issue #143 (OPEN)` |
| Credibility | 85 / high_trust |

> "MEASURED: plan-007, plan-009, plan-010, plan-012 and plan-017 each record an epic id with the `beads-skills-mol-*` prefix. `bd list --all --json` returns ZERO beads with that prefix (of 1019) — plan-010's yf- rename did not carry the old ids into the current DB."

*Note:* First-party defect report filed contemporaneously against the operator's own repository, in this corpus almost always carrying an explicit MEASURED block. Self-incriminating (the author reporting a defect in their own tool), which is the strongest prose class available here.

### HU16

**A bead stays open when its upstream issue closes — the reverse of #117, with no reconciler**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:16` |
| Repo | yoshiko-flow |
| Type | issue |
| Locator | `issue #144 (OPEN)` |
| Credibility | 85 / high_trust |

> "This is the **exact mirror of #117**, one direction over. ... The reverse edge — *upstream closed, local bead still open* — has no reconciler at all. ... A second one is already predictable: **#141 supersedes #128**, and #128's mirror `yf-ik3q` is open — when #128 closes, `yf-ik3q` becomes stale the same way."

*Note:* First-party issue with a MEASURED diagnosis, self-incriminating about the operator's own tool. Note the second half (#141 supersedes #128, yf-ik3q will go stale) is a PREDICTION, not an observation — do not cite it as a confirmed instance.

### HU17

**Source-scorer defect: domain_authority floors all non-docs.<vendor>.com hosts at 30**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:17` |
| Repo | yoshiko-flow |
| Type | issue |
| Locator | `issue #147 (OPEN)` |
| Credibility | 75 / verify |

> "In research 003 that hit 31 of 90 entries, ~20 of them first-party vendor documentation (burr.apache.org, developers.llamaindex.ai, ...). The rubric's 0-34 band is Tier 5 ('anonymous sources, content farms'), so first-party docs are scored as content farms purely on hostname shape: a ~40-point deflation on a 35%-weighted axis."

*Note:* A measurement artifact DISCLOSED rather than corrected. Relevant to method credibility. It concerns research 003, which this triangulation is blind to by rule; its substance is not adjudicated here.

### HU18

**plan-043 covers #135, #136, #145 — excluding them from the never-planned set**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:18` |
| Repo | yoshiko-flow |
| Type | plan-bundle |
| Locator | `docs/plans/plan-043-james-dixson-a8afe8/ (untracked in git at retrieval)` |
| Credibility | 65 / verify |

> "docs/plans/plan-043-james-dixson-a8afe8/context.md, upstream-triage.md, index.md, plan.md, references/upstream-145.md"

*Note:* plan-043 was UNTRACKED IN GIT at retrieval — an in-flight, unlanded bundle. It is used here only to EXCLUDE #135/#136/#145 from the never-planned set, which is the correct conservative direction (it shrinks the finding). Do not treat its contents as a settled record.

### HU19

**No emacs.d fix commit is attributed to any plan**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:19` |
| Repo | emacs.d |
| Type | commit |
| Locator | `git log --format='%h %ad %s' \| grep -iE 'plan-0'  (8 hits, all bookkeeping)` |
| Credibility | 92 / high_trust |

> "039fe9d docs(plan-004): record completed CriticMarkup preview plan / f2b044b chore(plan-003): plan record + beads close-out for universal SPC leader / ac80de0 chore(plan-002): mark plan complete / 2e2fbe3 docs(plans): add plan-001 in-Emacs agent integration plan"

*Note:* Mechanical, contemporaneous git record (sha + subject/diff/body), reproducible by re-running the query. Not prose, not self-serving, and not reconstructed later.

### HU20

**Fix-of-a-fix on emacs.d issue #5 within ~22 hours, no plan**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:20` |
| Repo | emacs.d |
| Type | commit |
| Locator | `5219798 (2026-06-23 14:27), 254cde2 (2026-06-23 16:01), fb070cd (2026-06-24 12:14)` |
| Credibility | 92 / high_trust |

> "5219798 fix(ghostel): stop fullscreen TUI clipping its bottom rows under the modeline / 254cde2 fix(ghostel): cap dingbat fallbacks to cell height; reserve-rows default 0 (#5) / fb070cd fix(ghostel): cap raster-overflow of symbol fallbacks; reserve 1 bottom row (#5)"

*Note:* Mechanical, contemporaneous git record (sha + subject/diff/body), reproducible by re-running the query. Not prose, not self-serving, and not reconstructed later.

### HU21

**Undetected backup failure as a class: three consecutive postgres-dump failures went unnoticed**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:21` |
| Repo | d3-pxe |
| Type | issue |
| Locator | `issue #76 (OPEN)` |
| Credibility | 85 / high_trust |

> "`postgres-dump.service` failed on **2026-08-14, 08-15 and 08-16** — three consecutive nightly runs — and **nothing surfaced it**. ... Folding this into #51 would let it be closed by work that never addressed it — which is exactly the failure mode this issue is about."

*Note:* First-party defect report filed contemporaneously against the operator's own repository, in this corpus almost always carrying an explicit MEASURED block. Self-incriminating (the author reporting a defect in their own tool), which is the strongest prose class available here.

### HU22

**Post-plan correctness and doc-vs-impl defects filed and left open**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:22` |
| Repo | pybridge |
| Type | issue |
| Locator | `issues #54, #55, #56, #57, #58 (all OPEN); evri_py #60 (OPEN)` |
| Credibility | 85 / high_trust |

> "#55 PyBridge.status() docstring promises {pid, uptime_seconds}; actual return has no pid | #54 findAvailablePort() releases the probe socket before spawnKernel binds it (TOCTOU race -> two MATLAB sessions can share one kernel) | evri_py #60 doc↔impl (CONSISTENCY §5): Windows .msi upgrades in place vs README version-side-by-side promise"

*Note:* First-party defect report filed contemporaneously against the operator's own repository, in this corpus almost always carrying an explicit MEASURED block. Self-incriminating (the author reporting a defect in their own tool), which is the strongest prose class available here.

### HU23

**d3-pxe live-apply discovery and stale-reference correction commits**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:23` |
| Repo | d3-pxe |
| Type | commit |
| Locator | `0be3064, 3f29a13, 1ee52e1, 1be7ddc, 3204e3a, 285f528, f68a1f9, 58ed894, 7ee7679` |
| Credibility | 92 / high_trust |

> "0be3064 plan-003 3.1: apply-path fixes discovered running the live converge / 3f29a13 plan-008 Epic 1: fixes found during live apply on CT 104 / 1ee52e1 plan-010 Issue 5.1 (part 1): fix the silently-broken OTel export / 285f528 plan-003 5.1/5.3: ... fix stale AGENTS GPU fact / f68a1f9 plan-012 Issue 3.3: ssl = on with absolute paths, three stale rationales struck / 7ee7679 plan-015 Issue 4.5: correct stale 192.168.7.115 control-node references"

*Note:* Mechanical, contemporaneous git record (sha + subject/diff/body), reproducible by re-running the query. Not prose, not self-serving, and not reconstructed later.

### HU24

**yf-plan: a measured literal in plan.md goes stale when the plan is inside its own measured corpus**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:24` |
| Repo | yoshiko-flow |
| Type | issue |
| Locator | `issue #135 (OPEN)` |
| Credibility | 85 / high_trust |

> "plan-039 **diagnosed this failure mode and encoded the rule** — Issue 3.2's *"corpus counts are re-derived by the harness, never transcribed"* ... It then violated that rule once more, in Issue 3.1, and nothing caught it until execution. ... **prose guidance inside a plan does not bind the plan's other sections.**"

*Note:* First-party defect report filed contemporaneously against the operator's own repository, in this corpus almost always carrying an explicit MEASURED block. Self-incriminating (the author reporting a defect in their own tool), which is the strongest prose class available here.

### HU25

**REJECTED candidate — cross-repo plan-number collision**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:25` |
| Repo | yoshiko-flow |
| Type | plan-bundle |
| Locator | `remediation_pairs.py pairs --json, candidate plan-013-james-dixson-0af2f8 -> plan-039-james-dixson-150f79; evidence at docs/plans/plan-039-james-dixson-150f79/plan.md:56` |
| Credibility | 45 / questionable |

> "**Reviews miss a whole class of defect.** Across `d3-pxe` plan-013, four real defects were"

*Note:* EXTRACTOR OUTPUT. Evidence about the tool's behavior (a confirmed cross-repo plan-number false positive), not evidence about a defect. Never usable as a denominator.

### HU26

**Extractor signal distribution**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:26` |
| Repo | all-five |
| Type | plan-bundle |
| Locator | `remediation_pairs.py pairs --json (83 candidates)` |
| Credibility | 45 / questionable |

> "Counter({'textual:remediation': 83, 'temporal:ordered': 83, 'artifact:path': 70, 'git:file-churn-overlap': 60, 'artifact:issue': 57, 'git:fix': 34, 'artifact:req': 17, 'textual:split': 6})"

*Note:* EXTRACTOR OUTPUT: the candidate-signal distribution. Usable only to characterise the tool. history-and-upstream:27 shows the candidate set fails on BOTH precision and recall for the one pair git can prove, so it cannot bound the defect population.

### HU27

**Eight candidate predecessors for plan-038; the true one (plan-013) is absent**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:27` |
| Repo | yoshiko-flow |
| Type | plan-bundle |
| Locator | `remediation_pairs.py pairs --json, all candidates with later_plan = plan-038-james-dixson-1ce25a` |
| Credibility | 45 / questionable |

> "plan-033 -> plan-038 [git:fix]; plan-035 -> plan-038 [git:fix]; plan-016 -> plan-038 [git:fix]; 002-harness-global-rule-minimization -> plan-038 [git:fix]; plan-009 -> plan-038 [git:fix]; plan-018 -> plan-038 [git:fix]; plan-037 -> plan-038 [git:fix]; plan-036 -> plan-038 [git:fix]"

*Note:* EXTRACTOR OUTPUT. Highly informative as a NEGATIVE result about the method (8 false positives, 1 false negative on a pickaxe-provable pair) and worthless as positive evidence of any pair.

### HU28

**The corpus's only semantic revert — undetectable by subject-line matching**

| Field | Value |
| :-- | :-- |
| uid | `history-and-upstream:28` |
| Repo | evri_py |
| Type | commit |
| Locator | `db41594 (2026-05-26)` |
| Credibility | 92 / high_trust |

> "bundler: restore local bundle_assets ownership; capture intent in SPEC Reverts 5d03ddc's PYBRIDGE_REPO dependency. evri_py owns the assets that ship in evri_py bundles — pybridge maintains a parallel copy for its own test-only artifacts. ... Capture the ownership policy and the 2026-05-26 incident in docs/SPEC.md so this doesn't get re-litigated."

*Note:* Commit body read in full, quoted verbatim, reproducible. This source OVERTURNS cross-repo-corpus:30 and yf-corpus:26 on the revert count. Mechanical evidence beats two clusters' subject-line greps.

## refine-verification (RF) — 1 source

Added at REFINE, not at retrieval. The red-team critique (MF-7) predicted that the report's
"d3-pxe already writes a `pass-0-conformance.md`" claim was uncited model knowledge. The claim was
tested against the d3-pxe repository on disk and **is supported**; this is the artifact.

### RF1

**d3-pxe persists its conformance verdict as a real `pass-0-conformance.md` file**

| Field | Value |
| :-- | :-- |
| uid | `refine-verification:1` |
| Repo | d3-pxe |
| Type | plan-bundle |
| Locator | `Incubator/ansible/plans/plan-013-james-dixson-1692d0/reviews/pass-0-conformance.md:1-25` (and the same file in `plan-014-james-dixson-763edc/reviews/`) |
| Credibility | 95 / high_trust |

> "Mechanical conformance pass, run **before** the red-team cycles. Corresponds to the phase-log line `review: plan v1 presented`. **Recorded because its findings changed the plan's dependency graph, and a cold reader tracing why Issue 3.4 depends on `5.2` should be able to find the reason.** ## Verdict: INCOMPLETE (resolved — see below) ... Re-run after resolution: **PASS**."

*Note:* PRIMARY ARTIFACT, read directly off disk rather than asserted. Exactly **two** of d3-pxe's
plan bundles carry the file (`plan-013`, `plan-014`, both under `Incubator/ansible/plans/`), so it
supports "d3-pxe does this" and **not** "d3-pxe does this uniformly". Note the locator root: d3-pxe
files these bundles under `Incubator/<slug>/plans/`, not `docs/plans/`, which is why a `docs/plans`
grep would miss it.

