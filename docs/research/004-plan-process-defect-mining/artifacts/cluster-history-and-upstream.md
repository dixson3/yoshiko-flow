---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: history-and-upstream

**Method:** DIRECT (first-party only). Providers: local filesystem, `git`, `gh` CLI against the
five corpus repos' own issue trackers, and the Toolsmith's `remediation_pairs.py`. No web leg
(`plan.yaml` `exclusions`: *"No external/web leg. This corpus is entirely first-party by design."*).

**Retrieved:** 2026-08-16. **Blind to** research 003 (not read).

**Confirmation discipline:** extractor pairs are inferences. Every pair below is marked
CONFIRMED (adjudicated against both bundles and/or git authorship) or CANDIDATE. Rejected
candidates are reported as findings in §5.

---

## 1. Per-repo upstream availability

All five repos have a GitHub remote **and an issue tracker in active use**. No repo is a
"no upstream configured" no-evidence case.

| repo | remote | issues (all) | open | closed | plan-tracker issues | commits |
| :-- | :-- | --: | --: | --: | --: | --: |
| yoshiko-flow | `github.com/dixson3/yoshiko-flow` | 141 | 37 | 104 | 17 | 391 |
| d3-pxe | `github.com/dixson3/d3-pxe` | 77 | 42 | 35 | 14 | 234 |
| pybridge | `github.com/eigenvector-research-inc/pybridge` | 52 | 20 | 32 | 1 | 242 |
| evri_py | `github.com/eigenvector-research-inc/evri_py` | 47 | 16 | 31 | 3 | 113 |
| emacs.d | `github.com/dixson3/emacs.d` | 8 | 6 | 2 | **0** | 178 |

[1][2] Counts from `gh issue list --state all --limit 300` per repo and `git log --oneline | wc -l`.
"plan-tracker issues" = titles matching *"plan-NNN execution tracking"* or *"Complete execution of
plan-NNN"*.

**Observation:** the coarse-tracker convention (one upstream issue per plan) is followed in
yoshiko-flow (17/43 plans) and d3-pxe (14/16 plans), thinly in evri_py (3/9) and pybridge (1/11),
and **not at all in emacs.d (0/4)**. The plan→upstream trace is therefore repo-dependent, and any
synthesis that assumes a tracker per plan will silently drop the evri/emacs.d ends of the corpus.

---

## 2. Confirmed remediation pairs found via git/upstream

### 2.1 CONFIRMED — yoshiko-flow plan-013 → plan-038 (51-day latent data-loss defect)

`git log -S'plan_hoist'` on `skills/yf-beads-upstream/scripts/upstream.py` puts authorship of the
comma-joined bead-id list in **plan-013 wave 1**, commit `eba3638` (2026-06-24) [3]. It was fixed
**51 days later** by **plan-038**, commit `9656eb1` (2026-08-14), whose diff states the severity
verbatim [4]:

> `A comma-joined list is matched by bd to ZERO beads while the process still exits 0`
> `(bd 1.1.2), so a comma here is silent data loss, not a formatting nit.`
> — `9656eb1`, `skills/yf-beads-upstream/scripts/upstream.py`

and, in the same hunk:

> `Before this, a comma-joined id list matched ZERO beads while exiting 0, and stage 3 then`
> `tombstoned every bead with a` …

The upstream record is **#129** [5], *"yf-beads-upstream: plan_hoist emits COMMA-separated ids that
bd matches to ZERO beads — multi-bead hoist/land tombstones beads it never pushed"* (CLOSED
2026-08-14).

**Preventability (hindsight bar):** a stated, checkable step existed and did not run — the skill's
own rule requires the write be *"verified STRUCTURALLY, and an exit 0 is not proof."* The defect is
precisely an exit-0-is-not-proof failure, in the code that implements that rule. This clears the
hindsight bar: not "a smarter planner", but "the rule this file exists to enforce, applied to
itself."

### 2.2 CONFIRMED — pybridge plan-010 → plan-011 (self-declared remediation)

plan-011's own objective declares the pair [6]:

> `Capture the two operational-knowledge deliverables that plan-010's execution`
> `surfaced but did not write — a release runbook`
> — `docs/plans/plan-011-james-dixson-b0aab1/plan.md:25`

Between plan-010's completion commit `6de4bb3` (*"plan-010 complete: close epic + reconcile; status
complete"*, 2026-07-15) and plan-011's approval commit `daf28aa` (2026-07-16) there are **14
commits, 12 of them touching `.github/workflows/release.yml`** — the exact artifact plan-010
delivered [7]. Sample subjects: `d65bf66 release.yml: bump release-path notary budget 45m -> 2h`,
`7bce4df release.yml: set +e in macOS upload (GitHub bash -e aborted on first 404)`,
`a3af236 release.yml: macOS release upload via flat curl + HTTP-201 check (drop gh/functions)`.

**Note the commit-message convention gap:** *none* of those 12 carries a `fix` prefix. Any
`fix`-prefix-based churn signal misses this entire remediation episode (see §5.2).

### 2.3 CONFIRMED — evri_py plan-008: eight RC-fallout fix commits after "18/18 complete"

The plan.md phase log records completion, then a silent eight-iteration gap [8]:

> `- 2026-07-16 executing: 18/18 tasks complete + pushed (fafd1d4); #7/#50 closed, #54 filed; …`
> `- 2026-07-16 executing: v0.2.1-rc1 failed: macOS cert-secret blocker (#56 …) …`
> `- 2026-07-17 reconciling: rc9 GREEN: macOS+Windows signing validated end-to-end …`
> — `docs/plans/plan-008-james-dixson-d1f1e4/plan.md:22-24`

The log jumps **rc1 → rc9**. The intervening work exists only in git:

| sha | date (ISO) | subject |
| :-- | :-- | :-- |
| `f831f85` | 2026-07-16 | fix(bundle): resolve exe via shutil.which in run_command (Windows uv build) |
| `872c0ab` | 2026-07-16 | fix(signing): entitlements AMFI comments + Windows uv PATH (**rc2 fallout**) |
| `973c63d` | 2026-07-16 | fix(bundle): pybridge_kernel load check + py3.10 numpy + Windows MAX_PATH (**rc3 fallout**) |
| `9809bbb` | 2026-07-16 19:46 | fix(bundle): re-pin pybridge v0.1.33 + py3.10-metal TF plugin rpath (**rc4 fallout**) |
| `c8de2ac` | 2026-07-16 20:52 | fix(bundle): defer Metal + Windows load-gate extract MAX_PATH (**rc5 fallout**) |
| `7a32983` | 2026-07-16 22:07 | fix(bundle): quarantine-gate exec bit + Windows py3.12 numpy constraint (**rc6 fallout**) |
| `5845b31` | 2026-07-17 07:32 | fix(bundle): numpy constraint in _install_python_payload (the CI install path) |
| `97ced85` | 2026-07-17 08:45 | fix(ci): run Windows load-gate imports isolated (-I) — runner numpy 2.5 leaked |

[9] Several of these defects are in the plan's **own test commands**, not the deliverable. `973c63d`
labels its own provenance:

> `1. Test-command (mine): the smoke test (2.1b) and clean-machine gates (2.3 macOS,`
> `   3.2 Windows) invoked \`python -m pybridge_kernel --version\`, but the pinned`
> `   kernel CLI has no --version (only --port/--host/--debug) — and running it bare`
> `   would bind a ZMQ socket and block.`
> — `973c63d` commit body

and `97ced85` states the plan's gate was measuring the wrong thing entirely:

> `The bundle itself was already correct; this makes the test faithful.`
> — `97ced85` commit body

**Why this is the cluster's headline finding:** the plan bundle records `rc1 failed` and `rc9
GREEN`. Seven RC iterations' worth of defect content — including two defects in the plan's own
success-criteria commands — is **absent from the bundle by construction**. Clusters that mine
plan bundles cannot see it.

**Preventability (hindsight bar):** plan-008 *explicitly* declared a lesson-transfer step [10]:

> `The parallel pybridge effort (\`eigenvector-research-inc/pybridge\` #35/#38/#41) just`
> `landed signing + notarization end-to-end and shook out a long, non-obvious list of`
> — `docs/plans/plan-008-james-dixson-d1f1e4/plan.md:39-40`

The stated step ran, and nine RCs were still required. This is the *hindsight-resistant* form:
the defect class survives a stated, executed prevention. What is missing is not knowledge transfer
but a **rule that a success criterion verifiable only by the real pipeline may not be marked met
before that pipeline runs green.** That rule is checkable and did not exist.

### 2.4 CONFIRMED — yoshiko-flow #137 → plan-041 (fix landed; class self-declared recurrent)

`#137` [11] is a defect report against `yf self install --from-build` promoting a stale embedded
skills tree. Its body names the recurrence itself:

> `This is the same class of defect as plan-039's \`yf-nkgh\` (installed skill lagging the repo) —`
> `one level down, in the tool meant to fix it.`
> — issue #137 body

It was routed into **plan-041** and fixed at `c4d51e4` (2026-08-16) [12]; the plan bundle carries
`references/upstream-137.md`. `#137` is CLOSED. **This is the corpus's cleanest example of the
process working end to end**: defect filed upstream → plan → SPEC-first requirement
(`REQ-YF-EMBED-004`) → mutation-tested guard → close. It is the control case against which the
§3 never-planned defects should be read.

---

## 3. Defects that NEVER GOT A PLAN OF THEIR OWN

These are invisible to the plan-bundle clusters by construction. They are the distinctive output
of this cluster.

### 3.1 yoshiko-flow: four process-defect issues filed, OPEN, zero plan coverage

`grep -rl '#N' docs/plans docs/research` over every yoshiko-flow bundle returns **no hits** for
**#142, #143, #144, #147** [13]. All four are OPEN. All four are *process* defects discovered by
*executing* an earlier plan:

| issue | state | discovered during | in any plan bundle? |
| :-- | :-: | :-- | :-: |
| #142 `closable` proposes closing already-closed/deleted issues | OPEN | plan-040 Issue 4.4 backfill | no |
| #143 five plan.md `**Epic:**` fields are dangling refs | OPEN | plan-040 Issue 4.4 backfill | no |
| #144 bead stays open when its upstream issue closes | OPEN | plan-040 reconcile | no |
| #147 source-scorer floors non-`docs.<vendor>.com` hosts at 30 | OPEN | research 003 REFINE (critique C-7) | no |

Verbatim, #142 [14]:

> `MEASURED: after stamping 18 coarse trackers, \`upstream.py closable\` proposed 25 closures:`
> `  - 23 already CLOSED upstream`
> `  - 2 no longer exist (#139 deleted, and a bare 'gh-91' ref)`
> `  - 0 genuinely OPEN and actionable`
> …
> `Before the backfill closable proposed 7; after, 25 — so making trackers visible made the`
> `report NOISIER rather than more useful.`

#143 [15]:

> `MEASURED: plan-007, plan-009, plan-010, plan-012 and plan-017 each record an epic id with the`
> `\`beads-skills-mol-*\` prefix. \`bd list --all --json\` returns ZERO beads with that prefix (of`
> `1019) — plan-010's yf- rename did not carry the old ids into the current DB.`

#144 [16] is the sharpest, because it *predicts its own recurrence*:

> `This is the **exact mirror of #117**, one direction over. #117 was *"push is write-only …"*,`
> `and plan-040 fixed it via \`closable\` + the coarse-tracker stamp. The reverse edge — *upstream`
> `closed, local bead still open* — has no reconciler at all.`
> …
> `A second one is already predictable: **#141 supersedes #128**, and #128's mirror \`yf-ik3q\` is`
> `open — when #128 closes, \`yf-ik3q\` becomes stale the same way.`

#147 [17] documents a measurement artifact that was **disclosed rather than corrected**:

> `In research 003 that hit 31 of 90 entries, ~20 of them first-party vendor documentation …`
> `The rubric's 0-34 band is Tier 5 ('anonymous sources, content farms'), so first-party docs are`
> `scored as content farms purely on hostname shape: a ~40-point deflation on a 35%-weighted axis.`

**Class:** *one-directional reconcilers.* #142, #143 and #144 are three instances of the same
root — local and upstream state are reconciled in one direction only, and the missing direction
has no verb at all. #144 says this explicitly. **Zero of the three is in a plan.** The process
produced an exceptionally good written diagnosis and then routed none of it into work.

*(#135, #136 and #145 — three further process-defect issues from the same window — ARE covered, by
the in-progress `plan-043-james-dixson-a8afe8` bundle, which is untracked in git at retrieval time
[18]. They are not counted as never-planned.)*

### 3.2 emacs.d: 27 `fix(...)` commits, 4 plans, 0 plan-tracker issues

emacs.d carries 178 commits, of which **27 begin `fix`** [1], against **4 plan bundles**
(plan-001…plan-004) and **zero** upstream plan-tracker issues. `git log | grep 'plan-0'` returns 8
commits, all bookkeeping (`docs(plan-004): record completed …`, `chore(plan-002): mark plan
complete`) — **no `fix` commit in the repo is attributed to any plan** [19]. In this repo the
plan process is a thin overlay on an otherwise unplanned fix stream.

**Fix-of-a-fix, same issue, next day** [20]:

| sha | timestamp | subject |
| :-- | :-- | :-- |
| `254cde2` | 2026-06-23 16:01:15 -0700 | fix(ghostel): cap dingbat fallbacks to cell height; reserve-rows default 0 (**#5**) |
| `fb070cd` | 2026-06-24 12:14:48 -0700 | fix(ghostel): cap raster-overflow of symbol fallbacks; reserve 1 bottom row (**#5**) |

Both cite the same upstream issue #5; the second reverses the first's `reserve-rows` default
(`0` → `1`). Issue #5 is CLOSED (2026-06-24) [2]. A third, earlier same-day commit `5219798
fix(ghostel): stop fullscreen TUI clipping its bottom rows under the modeline` attacks the same
symptom without citing #5. **Three commits, one symptom, ~22 hours, no plan, no red-team.**

### 3.3 d3-pxe: process defects filed as OPEN issues, one explicitly guarded against absorption

d3-pxe #76 [21] is a **class**-level defect filed by plan-015 execution and left open:

> `\`postgres-dump.service\` failed on **2026-08-14, 08-15 and 08-16** — three consecutive nightly`
> `runs — and **nothing surfaced it**. … \`pool1/postgres\` is registered **precious** (SPEC`
> `PVE-STO-005). It went four days without a logical backup and the gap was discovered only`
> `because someone went looking for the cause of an unrelated symptom.`

and it pre-emptively defends against being closed by adjacent work:

> `Folding this into #51 would let it be closed by work that never addressed it — which is exactly`
> `the failure mode this issue is about.`

That defensive paragraph is itself evidence: the author expected the process to mis-absorb the
issue. d3-pxe has **42 open issues against 35 closed** — the highest open ratio in the corpus [1].

### 3.4 pybridge/evri_py: correctness defects filed post-plan, never planned

Five pybridge issues are OPEN correctness/API defects with no plan bundle referencing them
[2][22]: `#54` (*"findAvailablePort() releases the probe socket before spawnKernel binds it (TOCTOU
race -> two MATLAB sessions can share one kernel)"*), `#55` (*"PyBridge.status() docstring promises
{pid, uptime_seconds}; actual return has no pid"*), `#56`, `#57`, `#58`. `#55` is a doc↔impl
divergence — the exact axis `yf-drift-check` covers — surviving in an OPEN issue rather than a fix.
evri_py `#60` is the same shape: *"doc↔impl (CONSISTENCY §5): Windows .msi upgrades in place vs
README version-side-by-side promise"*.

**Class:** *doc↔impl divergence is reliably DETECTED and reliably NOT FIXED.* It gets filed,
carries a precise diagnosis, and stays open.

---

## 4. Recurring classes visible only from git

### 4.1 "Discovered at live apply / real target" — recurs in 3 repos

Defects that no review could reach because the artifact had never been run against the real
target. d3-pxe commit subjects name the mechanism outright [23]:

| repo | sha | subject |
| :-- | :-- | :-- |
| d3-pxe | `0be3064` | plan-003 3.1: **apply-path fixes discovered running the live converge** |
| d3-pxe | `3f29a13` | plan-008 Epic 1: **fixes found during live apply on CT 104** |
| d3-pxe | `1ee52e1` | plan-010 Issue 5.1 (part 1): fix the **silently-broken** OTel export |
| d3-pxe | `1be7ddc` | plan-013 Issue 5.3: fix the manifest drift 5.2 found (20 -> 0) |
| d3-pxe | `3204e3a` | plan-015: fix the service_name mapping (N5) |
| evri_py | `872c0ab`…`97ced85` | rc2–rc8 fallout (§2.3) |
| pybridge | `1f7feca` | sign actions: **fix runner-environment failures found by the test build** |

d3-pxe's instances land *inside* the plan (issue-numbered commits) — the plan absorbed the
discovery. evri_py's and pybridge's land *after* the plan declared complete. The same class,
handled two different ways, is itself a process signal.

### 4.2 "Stale literal / stale reference" — recurs in 2 repos, matching yf #135

d3-pxe corrected stale in-document facts in four separate plans [23]:
`285f528` *"fix stale AGENTS GPU fact"*, `f68a1f9` *"three stale rationales struck"*,
`58ed894` *"correct the stale note"*, `7ee7679` *"correct stale 192.168.7.115 control-node
references"*. yoshiko-flow #135 [24] independently names the class and reports **four instances in
one plan**, one of which escaped to execution, with the decisive observation:

> `plan-039 **diagnosed this failure mode and encoded the rule** … It then violated that rule once`
> `more, in Issue 3.1, and nothing caught it until execution. … **prose guidance inside a plan does`
> `not bind the plan's other sections.**`

**Hindsight bar: cleared, and inverted.** The checkable step *did* exist, in the same document,
and did not bind. That is stronger evidence than a missing step.

---

## 5. Rejected candidates and tool limitations (reportable findings)

### 5.1 REJECTED — extractor pair yoshiko-flow plan-013 → plan-039

`remediation_pairs.py pairs` emits this pair with signals `textual:remediation, temporal:ordered,
artifact:req, artifact:path`. Its own evidence refutes it [25]:

> `"quote": "**Reviews miss a whole class of defect.** Across \`d3-pxe\` plan-013, four real defects were"`
> `"location": "docs/plans/plan-039-james-dixson-150f79/plan.md:56"`

The referent is **d3-pxe plan-013**, not yoshiko-flow plan-013 (*"Reconcile policy — local beads =
active work only"*). **Plan numbers are not namespaced by repo**, so any cross-repo textual
reference to `plan-NNN` is silently misattributed to the same-repo bundle. Given that
yoshiko-flow plan-039 is *about* d3-pxe plan-013's defects, this is a systematic, not incidental,
false-positive source.

### 5.2 The `git:fix` signal misses the corpus's largest remediation episode

`git:fix` fires on 34 of 83 candidates [26], but is prefix/keyword-driven on commit **subjects**.
The 12 `release.yml` commits that remediate pybridge plan-010 (§2.2) carry no `fix` token in the
subject and are invisible to it. Prefix counts: yoshiko-flow 5, d3-pxe **0**, pybridge 26,
evri_py 20, emacs.d 27 [1]. **d3-pxe scores zero `fix`-prefix commits while demonstrably fixing
things in almost every plan** (§4.1) — it uses `plan-NNN Issue X.Y: …` subjects instead. Any
cross-repo comparison of "fix density" from subject prefixes is invalid.

### 5.3 The true plan-013 → plan-038 pair is ABSENT from the candidate set

The extractor proposes **eight** earlier plans for plan-038 (plan-009, plan-016, plan-018,
plan-033, plan-035, plan-036, plan-037, and research 002) [27] — six of them sharing the *same*
`git:fix` commit `9656eb1`, because the commit is attributed to the *later* plan and then paired
with every textually adjacent earlier one. The **actual** author of the defect, plan-013, is not
among them. Authorship is recoverable only by pickaxe (`git log -S<symbol> -- <path>`), a signal
the extractor does not implement. **Precision and recall both fail on the one pair that git can
prove.**

### 5.4 `git:revert` = 0 carries no information — and is also a detection artifact

Corpus-wide, `git log --grep='^Revert'` returns **0** in yoshiko-flow, d3-pxe, pybridge and
emacs.d, and **1** in evri_py [1]. Remediation in this corpus lands as forward fix commits; the
absence of reverts is a **convention**, not a quality signal, and must not be reported as one.

Further, the one semantic revert that exists does **not** start with "Revert" — evri_py `db41594`
*"bundler: restore local bundle_assets ownership; capture intent in SPEC"*, whose body reads [28]:

> `Reverts 5d03ddc's PYBRIDGE_REPO dependency. evri_py owns the assets that ship in evri_py`
> `bundles … Capture the ownership policy and the 2026-05-26 incident in docs/SPEC.md so this`
> `doesn't get re-litigated.`

So subject-only revert detection has **100% false-negative rate on the corpus's only revert**. Any
revert-based signal must search commit **bodies**.

---

## 6. Absences (no evidence found)

- **No repo lacks an upstream tracker.** The planned "record no upstream configured as
  no-evidence" case does not arise (§1). All five have a GitHub remote with issues in use.
- **No commit anywhere in the corpus explicitly names a prior plan as the source of a defect it is
  fixing.** Searched: `git log --format='%s%n%b'` across all five repos for `plan-0` co-occurring
  with fix/revert language. Attribution is always either (a) to an issue number, or (b) to the
  *current* plan. The plan→defect→plan edge is never recorded in git; every pair in §2 was
  reconstructed by pickaxe or by reading a plan's objective. **The corpus has no machine-readable
  remediation edge.**
- **No `Reverts`/`Reopened` upstream-issue events were inspected.** `gh issue list` does not carry
  reopen history and per-issue timeline calls would exceed the 10 req/min budget. Whether any
  issue was closed by a plan and later reopened is **unknown** `[uncertain]`.
- **No evidence found that any red-team or conformance pass caught a defect in §3.** No bundle
  under any repo references #142, #143, #144 or #147 [13]; nothing establishes whether those
  defects were in a reviewed plan's scope at all.

---

## 7. Limitations the synthesizer must carry

1. **`git:fix` and `git:revert` are both unsound across this corpus** (§5.2, §5.4). Commit-subject
   conventions differ per repo to the point that d3-pxe scores 0 fix-prefixes while fixing
   constantly. Do not rank repos by fix density.
2. **The extractor cannot recover authorship** (§5.3). Its plan-038 row set is 8 false positives
   and 1 false negative. Treat every non-pickaxe-confirmed pair as a candidate.
3. **Plan numbers collide across repos** (§5.1). `plan-013` means three different things in this
   corpus.
4. **Plan bundles omit post-completion churn.** evri_py plan-008's phase log jumps rc1 → rc9,
   hiding 8 fix commits and 2 defects in the plan's own success-criteria commands (§2.3). Any
   escape-rate computed from bundles alone is **understated**, and understated most for exactly the
   plans whose deliverable is only verifiable in CI.
5. **`gh` rate limit** (10/min) forced batched `issue list` queries; issue **comments and timelines
   were not retrieved**. Claims about what was discussed on an issue are out of scope here.
6. **Six of the seven never-planned yoshiko-flow issues were filed within the last 24 hours of the
   retrieval window** (2026-08-16). "Never got a plan" is therefore partly a **recency artifact**
   for #142/#143/#144/#147 `[uncertain]` — they may simply not have been triaged yet. The emacs.d
   (§3.2), pybridge (§3.4) and d3-pxe (§3.3) never-planned findings span weeks-to-months and do
   **not** have this defect; weight those higher.
