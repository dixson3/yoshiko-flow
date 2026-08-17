---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: execution-telemetry

**Question this cluster answers:** what did EXECUTION hit that PLANNING did not anticipate?

**Method.** DIRECT retrieval only (`plan.yaml` sets `method: direct`, `exclusions: "No
external/web leg"`). Providers: local filesystem, `bd` (read-only), `git`. No web leg was run.
All bead data was pulled live from each repo's `bd` DB on 2026-08-16 via `bd list --status all
--json --limit 0 --include-gates --include-infra` plus chunked `bd dep list ... --json`, parsed
defensively (first `[`, `raw_decode`). Bundle inventory came from the Toolsmith's
`scripts/remediation_pairs.py inventory --detail`. `bd` was never mutated.

**Blind-mining compliance.** `docs/research/003-graph-engineering-hypothesis` was not opened.

---

## 1. `bd` availability per repo

All five corpus repos have a queryable `bd` DB. This is *availability*, not *corroboration* —
see §3 and §9.

| repo | `.beads/` present | `bd list` returns | issues (incl. gates/infra) | dep edges | `discovered-from` edges |
| :-- | :-: | :-: | --: | --: | --: |
| yoshiko-flow | yes | yes | 1176 | 2182 | 25 |
| d3-pxe | yes | yes | 501 | 943 | 4 |
| pybridge | yes | yes | 229 | 406 | 15 |
| evri_py | yes | yes | 304 | 536 | 8 |
| emacs.d | yes | yes | 58 | 68 | 1 |
| **total** | 5/5 | 5/5 | **2268** | **4135** | **53** |

Edge-type mix (all repos): `blocks` 2048, `parent-child` 2027, `discovered-from` 53,
`relates-to` 6, `related` 1. `bd` version 1.1.2 (Homebrew) [1].

**Zero repos are "no evidence".** Every repo answered. Where a claim below is absent for a
repo, that is a measured absence, not a tool failure.

---

## 2. The plan-to-bead linkage is broken for 24 of 83 bundles

Before any telemetry can be attributed to a plan, the bundle's recorded `**Epic:**` id must
resolve to a live bead. It does not, for **24 of 83 bundles (29%)**, in **two distinct ways**.

### 2a. Dangling epic pointer — 14 bundles, yoshiko-flow only

Plans 004–017 record epic ids under a **retired repo prefix**. `plan-004`'s header reads
verbatim:

> `**Epic:** beads-skills-mol-nxk` — `docs/plans/plan-004-james-dixson-56f494/plan.md:7`
> `- 2026-06-01 intake: epic beads-skills-mol-nxk poured` — same file, line 15 [2]

`bd show beads-skills-mol-nxk` returns:

> `Error fetching beads-skills-mol-nxk: no issue found matching "beads-skills-mol-nxk"` [3]

All 1176 yoshiko-flow bead ids now carry the `yf-` prefix; **zero** carry `beads-skills` [3].
Nor did the ids survive a rename: probing each of the 14 short suffixes (`nxk`, `5tv`, `g0b`,
`s3x`, `14o`, `bjf`, `yvv`, `r8z`, `2bi`, `glo`, `mqa`, `itd`, `3ee`, `806`) against every yf
id — as `yf-mol-<sfx>`, as a suffix match, and as a subtree prefix — returned **no candidate
for any of the 14** [3].

The bead *data* almost certainly survived: yoshiko-flow holds **16 orphan `plan-execute`
molecules** dated 2026-06-01 → 2026-06-25 under hash-style ids (`yf-dfabdd38`, `yf-fb0bc064`,
`yf-5e06c253`, …) that no bundle claims, and which line up by date with the 14 dangling
bundles [4]. What was lost is the *pointer*, not the rows. **[uncertain]** on the exact
one-to-one mapping — nothing records it, and no bundle was rewritten to repair it.

**Scope:** yoshiko-flow only. d3-pxe, pybridge, evri_py and emacs.d have **zero** dangling
epic pointers [4]. This is a local slip, not a recurring class.

### 2b. No epic recorded at all — 10 bundles, all four other repos included

| repo | bundles with no `**Epic:**` | bundle ids | benign (still pre-pour)? |
| :-- | --: | :-- | :-- |
| yoshiko-flow | 3 | plan-001, plan-002, plan-003 | plan-042 (`scoping`), plan-043 (`review`) also lack one — expected |
| d3-pxe | 1 | plan-016 | yes — status `review` |
| pybridge | 2 | plan-002, plan-005-…-b3d15c | no — both `complete` |
| evri_py | 5 | plan-001, -002, -003, -004, -007 | no — statuses `complete`/`executing`/`approved` |
| emacs.d | 1 | plan-001 | yes — status `drafting` |

The header field is **absent**, not empty: `grep -nE "^\*\*(Epic\|Status)"` over
`pybridge/plan-002`, `evri_py/plan-002..004`, `emacs.d/plan-001` returns only `**Status:**`
lines and no `**Epic:**` line at all [5].

Yet the beads exist. pybridge holds one orphan `plan-execute` molecule `pybridge-mol-edn`
(2026-05-26 — pybridge plan-002 is dated 2026-05-26); evri_py holds two,
`evri_py-mol-itou` (2026-05-19 = plan-002) and `evri_py-mol-xsdxn` (2026-05-20 = plan-003)
[4]. Date alignment is exact but the linkage is **inferred, not recorded** — flag
**[uncertain]**.

**This half of the class is cross-repo** (4 of 5 repos, excluding emacs.d whose single case is
a pre-pour draft). Execution telemetry for those plans is orphaned from the plan that produced
it in *both* directions: the bundle cannot name its beads, and the molecule cannot name its
bundle.

**Net:** only **55 of 83 bundles (66%)** have a bead graph this cluster could attribute.
Every rate below is over that denominator, and understates the corpus.

---

## 3. `discovered-from` edges: what execution found that planning did not

53 edges corpus-wide. Only **24** of the 53 originate inside a resolvable plan subtree; the
other 29 originate from non-plan molecules, research molecules, or free-standing beads [6].

**44 of 53 edges cross a molecule boundary** [6]. And the Toolsmith's finding replicates
exactly: **zero of the 53 connect two plan epics.** Every edge runs from a task or molecule to
a *newly filed* bead — never plan-A-epic → plan-B-epic. `discovered-from` in this corpus
records *"execution spawned new work"*, never *"plan B remediates plan A"*. **A remediation
pair is therefore not recoverable from the bead graph** — an absence the synthesizer must
carry into any claim about remediation-pair provenance.

### 3a. Rate per plan (plans with a resolvable bead graph, n=55)

| repo | plans w/ graph | `discovered-from` originating | mean per plan | plans with ≥1 |
| :-- | --: | --: | --: | --: |
| yoshiko-flow | 24 | 9 | 0.38 | 6 |
| d3-pxe | 15 | 3 | 0.20 | 2 |
| pybridge | 9 | 6 | 0.67 | 5 |
| evri_py | 4 | 5 | 1.25 | 2 |
| emacs.d | 3 | 1 | 0.33 | 1 |
| **all** | **55** | **24** | **0.44** | **16 (29%)** |

**71% of plans with a bead graph recorded zero discovered-from edges.**

### 3b. The 16 non-zero plans

| repo | plan | created | plan.md issues | beads at pour | tasks | gates | `discovered-from` out |
| :-- | :-- | :-- | --: | --: | --: | --: | --: |
| pybridge | plan-003 | 2026-06-17 | 16 | 25 | 17 | 3 | 2 |
| pybridge | plan-004 | 2026-06-18 | 12 | 20 | 13 | 3 | 1 |
| pybridge | plan-005 | 2026-06-19 | 5 | 9 | 6 | 1 | 1 |
| evri_py | plan-005 | 2026-06-19 | 13 | 23 | 14 | 3 | 4 |
| pybridge | plan-006 | 2026-06-19 | 14 | 21 | 15 | 1 | 1 |
| evri_py | plan-006 | 2026-06-21 | 1 | 13 | 8 | 3 | 1 |
| emacs.d | plan-002 | 2026-06-23 | 4 | 6 | 4 | 0 | 1 |
| yoshiko-flow | plan-018 | 2026-06-30 | 16 | 25 | 17 | 2 | 1 |
| yoshiko-flow | plan-021 | 2026-07-02 | 20 | 33 | 23 | 2 | 2 |
| yoshiko-flow | plan-023 | 2026-07-05 | 11 | 17 | 12 | 1 | 1 |
| yoshiko-flow | plan-024 | 2026-07-07 | 10 | 16 | 11 | 2 | 1 |
| d3-pxe | plan-001 | 2026-07-12 | 19 | 30 | 19 | 5 | 1 |
| pybridge | plan-010 | 2026-07-15 | 14 | 22 | 15 | 2 | 1 |
| d3-pxe | plan-003 | 2026-07-18 | 16 | 27 | 18 | 3 | 2 |
| yoshiko-flow | plan-035 | 2026-07-23 | 17 | 28 | 19 | 7 | 3 |
| yoshiko-flow | plan-036 | 2026-07-24 | 9 | 13 | 9 | 3 | 1 |

### 3c. What the edges actually say

Representative verbatim titles, with the parent they were discovered from [6]:

- `pybridge-5ap` ← `pybridge-mol-edn.5.3`: *"Standalone bundle isn't actually standalone:
  relocatable venv references build-runner CPython"* discovered from *"5.3 Bundle re-test:
  verify quarantine present-then-cleared, smoke against bundle Python"*. A verification step
  found the deliverable did not meet its own name.
- `pybridge-aey` ← `pybridge-mol-66l` (`plan-execute`): *"Windows self-hosted runner: cmake not
  on cmd PATH — breaks all Windows MEX builds"*. Environment defect, not code.
- `evri_py-fes` ← `evri_py-mol-rxg.4.1`: *"Doc gap: PRD has no REQ-\* for SVM (svm/svmda)
  algorithm"*; and `evri_py-r4l` ← `…rxg.5.1`: *"Doc gap: SPEC has no field-level schema for
  pybridge-standalone.json manifest"*. Implementing against a spec revealed the spec was
  silent. This is the **SPEC-first** failure mode observed empirically, twice in one plan.
- `yf-m78m` ← `yf-mol-3ct.3.3` (*"Exit gate: lint audit + 0-warning build + drift-check
  PASS"*): *"yf-plan README.md stale: still lists README.md as plan-folder orientation file
  (pre-OKF), contradicts index.md/log.md in SPEC REQ-PLAN-010 + SKILL.md"*. An earlier plan's
  own migration left an inconsistency that a later plan's exit gate found.
- `d3-pxe-mol-e49.3.4` ← `d3-pxe-mol-e49.3.1`: *"3.1a raw_conf: replace blockinfile markers
  with marker-less lineinfile (PVE canonicalizes 100.conf under active API module, mangling
  comment markers -> duplicate lxc.\* lines)"*. Platform behaviour unknowable at plan time.
- `pybridge-jfc` ← `pybridge-08b`: *"testArrayTransferMultiDim fails on main — 2D row/col-major
  assertion (#21 closed but multidim regresses)"* — the one edge in the corpus whose text
  asserts an **incomplete prior fix**, and even it points at a GitHub issue, not a plan.

The dominant subject is **environment / platform / toolchain reality** (cmake PATH, WDAC
policy, CRLF autocrlf, MAX_PATH, PVE config canonicalization, Gatekeeper, glibc floor), then
**doc/spec gaps found while implementing**, then **plumbing chores** (register a new test in
`CHANGE-VALIDATION.md`, regenerate a golden, bump a version). Comparatively few are design
errors.

---

## 4. Trend assessment — declining rate, but I cannot rule out declining instrumentation

**Raw series, all repos pooled, ordered by bundle creation date (n=55, quartiles of 13):**

| window | n | `discovered-from` total | mean/plan | plans with ≥1 |
| :-- | --: | --: | --: | --: |
| 2026-06-17 → 06-30 | 13 | 12 | 0.92 | 8 |
| 2026-07-02 → 07-15 | 13 | 6 | 0.46 | 5 |
| 2026-07-15 → 07-23 | 13 | 5 | 0.38 | 2 |
| 2026-07-24 → 08-14 | 13 | 1 | 0.08 | 1 |
| 2026-08-16 (tail) | 3 | 0 | 0.00 | 0 |

Halves: H1 (n=27) mean 0.667, 13 plans non-zero; H2 (n=28) mean 0.214, 3 plans non-zero.

**The decline survives controlling for repo** — every repo's own first half exceeds its second:

| repo | n | H1 mean | H2 mean |
| :-- | --: | --: | --: |
| yoshiko-flow | 24 | 0.42 (p018–p029) | 0.33 (p030–p041) |
| d3-pxe | 15 | 0.43 | 0.00 |
| pybridge | 9 | 1.25 | 0.20 |
| evri_py | 4 | 2.50 | 0.00 |
| emacs.d | 3 | 1.00 | 0.00 |

**Verdict: DOWNWARD-LEANING, LOW CONFIDENCE. Do not draw a line through this.** Reasons:

1. **n is tiny and the series is mostly zeros.** 39 of 55 plans score 0. The whole signal is
   24 events. yoshiko-flow — the only repo with enough plans to see a shape — moves 0.42 →
   0.33, which is **one edge of difference** and is noise.
2. **The pooled decline is confounded by repo composition.** pybridge and evri_py (the two
   highest-rate repos) are almost entirely in H1; d3-pxe and late yoshiko-flow (the two
   lowest) are almost entirely in H2. The pooled 0.667 → 0.214 drop is substantially a change
   of *which repos are being measured*, not of *how plans perform*.
3. **A declining rate is equally consistent with declining instrumentation.** Two independent
   checks, both pointing that way:
   - **Post-pour additions into a plan's own subtree are near-zero and always were.** Across
     all 55 resolvable plans, only **23 beads** were created inside a plan molecule more than
     an hour after its pour, and **13 of those 23 are one plan** (evri_py plan-008: 41 beads,
     14 late, 4 of them >24h later). 51 of 55 plans added **nothing** to their own molecule
     after pour [7]. So the molecule is treated as *frozen at pour* corpus-wide; unplanned
     work necessarily exits the plan, which is exactly why 44/53 edges cross a molecule
     boundary (§3). This behaviour is **flat across the whole timeline** — it does not
     decline — so it cannot explain a declining discovery rate, but it does mean the only
     surviving record of discovery is the optional `discovered-from` edge.
   - **That optional edge is inconsistently attached.** In the plans whose execution window is
     short enough to measure cleanly, roughly half of the free-standing beads created during
     the window carry no `discovered-from` edge at all (e.g. pybridge plan-003: 4 beads in
     window, 2 with an edge; plan-006: 3 in window, 1 with an edge; emacs.d plan-002/003/004:
     2 beads each, **0** with an edge) [8]. Nothing in the corpus requires the edge, so its
     presence measures operator habit as much as it measures discovery.

I found **no artifact that distinguishes these two explanations**, and I do not think the
corpus contains one. The honest statement is: *the recorded discovery rate fell; whether
discovery fell is unresolved.* **[uncertain]**

**Caveat on the window measure.** An attempt to count "ad-hoc beads created during a plan's
execution window" over all 55 plans produced 908 candidates against 71 edges, but the yf
windows are inflated to weeks or months because subtree `updated_at` values were touched long
after the plan closed. I am reporting only the short-window subset above and discarding the
pooled figure as unreliable. Recorded here so it is not re-derived and trusted.

---

## 5. Plan-as-written vs plan-as-poured

Comparing `plan.md` issue-bullet count (`^\s*[-*]\s+(\*\*)?Issue\s`) to bead `task` count in
the poured molecule, over the 55 plans with a resolvable graph:

- **Mean delta = +1.15 tasks.** The pour is a faithful, near-mechanical translation of the
  written plan plus a small fixed overhead (the formula's `Reconcile:` / land steps).
- Median behaviour is `tasks = plan.md issues + 1`. 41 of 55 plans sit at delta 0 or +1.
- Only two outliers, both parse artefacts or genuine expansion worth flagging:
  **evri_py plan-008** (18 issues → 32 tasks, delta +14) and **evri_py plan-006** (1 → 8;
  plan-006 writes its epics as `### Epic N` headings with no `- Issue` bullets, so the parser
  under-counts — **not** a real gap).
- No plan poured *fewer* tasks than it wrote.

**Finding:** the pour step is not where plans lose fidelity. Whatever divergence exists between
plan and reality enters *after* the pour, and — per §4 — leaves almost no trace inside the
molecule.

---

## 6. Gates: 236 in the corpus, exactly one recorded override

| repo | gates | closed | still open |
| :-- | --: | --: | --: |
| yoshiko-flow | 103 | 103 | 0 |
| d3-pxe | 75 | 75 | 0 |
| pybridge | 29 | 29 | 0 |
| evri_py | 25 | 20 | **5** |
| emacs.d | 3 | 3 | 0 |
| **total** | **236** | **231** | **5** |

**One gate in 236 records being satisfied by override rather than by evidence** [9]:

> `pybridge-mol-66l.6` — *Gate: Tri-Platform Green* — close reason:
> **"OPERATOR OVERRIDE: macOS + Linux jobs green (19/19 incl. 500MB) in run 27734768524.
> Windows blocked at Configure CMake by pre-existing runner regression (cmake off cmd PATH
> ~2026-05-26, also breaks releases) — NOT a plan-003 code defect. Tracked as pybridge-aey;
> real Windows CI validation deferred to that runner fix."**

Note the override is *self-documenting and traced*: it names the blocking cause, disclaims
plan fault, and points at the bead (`pybridge-aey`) that carries the deferred work — and
`pybridge-aey` is itself a `discovered-from` child of the same molecule (§3c). The gate
mechanism degraded honestly.

The 5 open gates are **all in evri_py** and all belong to plans that never finished:
`evri_py-mol-e3d.7` *Gate: Reconcile upstream* and `evri_py-mol-e3d.6` *Capability Gate:
Windows WiX toolchain on the runner* (plan-009, status `executing` since 2026-07-27, with 14
open beads in its subtree); `evri_py-mol-xsdxn.9` *Gate: Reconcile upstream*; and
`evri_py-mol-itou.16` *Gate: Reconcile upstream* + `evri_py-mol-itou.14` *Gate: pybridge
dispatch wired* — the latter open since **2026-05-19**, on the molecule that date-matches
evri_py plan-002, whose bundle still reads `**Status:** executing` [5][9][10].

**No gate anywhere in the corpus is closed with a "could not be satisfied" verdict.** Gates
either close on evidence, stay open forever on an abandoned plan, or (once) close on a
documented override. There is no recorded *failed* gate.

---

## 7. The two cases where a pre-registered risk fired — and the process held

Both are **counter-examples to a naive "planning gap" reading**, and both meet the HINDSIGHT
bar in reverse: a *stated, checkable step existed*, it fired, and the outcome was a controlled
degradation rather than a defect.

**evri_py plan-006.** The plan pre-registered the exact failure that occurred:

> **"R1 — a v0.1.32 probe may fail (operator decision 2026-06-21: treat as regression).** The
> pybridge fixes are **assumed present** in v0.1.32 (all six issues closed COMPLETED). If an
> Epic 0 probe fails, it is a **pybridge regression**, not a version mismatch: **reopen the
> corresponding pybridge issue (#10/#11/#12/#14/#15) with the failing probe context** … and
> mark that single rewrite **blocked pending pybridge**"
> — `evri_py/docs/plans/plan-006-james-dixson-38b166/plan.md:225-231` [11]

It fired, exactly as written:

> `- 2026-06-21 executing: R1 fired for #10 — pybridge#10 REOPENED (incomplete-fix root cause
> + repro). Epic 1 (#17) blocked on new gate eoz.12; transitive chain Epics 2/3/5/6
> (#18/#22/#40/#39) held. Operator chose option C (hybrid: file upstream + proceed Epic 4 +
> hold chain).`
> — same file, line 18 [11]

Three of its epics then closed **undone**, with an identical, explicit reason:

> `evri_py-mol-eoz.3` *Epic 1: Direct fit/predict (#17, pybridge#10)*, `…eoz.5` *Epic 2:
> Cross-PyObject proxy-arg helpers*, `…eoz.6` *Epic 3: NV pairs -> kwargs*, `…eoz.10`
> *Reconcile* — all four closed with: **"Plan-006 closed; §6 direct-fit chain deferred to
> evri_py#49 / pybridge#10. Re-pour a follow-up plan when pybridge#10 ships refcounted
> handles."** [10]

A plan closed `complete` with **4 of its ~6 work units deliberately not done**, blocked on a
dependency in a *different repo*. The bundle labels this honestly ("PARTIAL LANDING", "plan
closed (partial)", line 21-22). Per the HINDSIGHT RULE this is **not** a preventable planning
defect: the checkable step (Epic 0 capability probe + R1) existed and worked.

**d3-pxe plan-014** (`d3-pxe-mol-qoz.3.4`), the corpus's most detailed close reason, says the
same thing in its own words [12]:

> **"DESCOPED by operator decision 2026-08-13.** … Cause: Issue 3.2's apply of the nine
> absence alerts failed with HTTP 400 `{"code":400,"message":"Alert destinations is
> required"}` … **Structurally un-previewable** — `ansible.builtin.uri` has no check-mode
> support, so 3.1's fleet-wide `--check` skipped the POST; **exp-011 §6 pre-registered exactly
> this residual risk and it fired.** … CONSEQUENCES: SC3 FAILS … #68's TIME-BASED HALF REMAINS
> OPEN, tracked by https://github.com/dixson3/d3-pxe/issues/73"

"Structurally un-previewable" is the plan's own verdict on preventability, recorded at the
time and not in hindsight.

**Pattern worth ranking:** in both cases the surviving artifact is a **spike / capability-probe
gate placed before the dependent work**, plus a **named risk with a written response**. Where
that pair was present, an unplanned reality became a documented partial landing. Where it was
absent (the §3c environment defects: cmake PATH, WDAC, CRLF, MAX_PATH), the same class of
reality became a mid-execution `discovered-from` bead.

---

## 8. Deferred / open follow-on backlog

Beads *created by* a `discovered-from` edge that are still not closed:

| repo | beads created via `discovered-from` | still open/deferred | ids |
| :-- | --: | --: | :-- |
| yoshiko-flow | 25 | 4 | `yf-m78m` (open), `yf-ybri` (open), `yf-mrv9` (open), `yf-uz5k` (**deferred**) |
| pybridge | 15 | 4 | `pybridge-8fv`, `pybridge-bd4`, `pybridge-gsx`, `pybridge-vk8` |
| evri_py | 8 | 2 | `evri_py-tmq`, `evri_py-56q` |
| d3-pxe | 4 | 0 | — |
| emacs.d | 1 | 0 | — |
| **total** | **53** | **10 (19%)** | |

Three of pybridge's four open follow-ons were created in the **same second**
(`2026-06-21T17:00:20–21Z`) from one parent, `pybridge-hax` *"Platform-specific testing:
Windows Python variants, macOS Gatekeeper, Linux glibc"* — a fan-out of a known-unknown into
three named beads, none since actioned [6]. `pybridge-hax` is itself still open.

Corpus-wide non-closed beads: yoshiko-flow 27 (21 open, 5 in_progress, 1 deferred), evri_py
15 open, pybridge 6, d3-pxe 4, emacs.d 1 [1].

---

## 9. Absences (measured, not inferred)

1. **No `discovered-from` edge in the corpus connects two plan epics.** 53/53 checked. The
   bead graph cannot evidence a remediation pair. Replicates the Toolsmith's finding
   independently [6].
2. **No stuck-bead sweep has any recorded firing.** The mechanism was designed in
   yoshiko-flow plan-004 — *"The sweep **resets** stuck `in_progress`/claimed beads to `open`
   and **reports** (does not close) anything it cannot classify"*
   (`plan-004…/plan.md:128-130`) [13] — and `plan_manager.py` ships a resume-guard reporter
   (*"Report the plan's epic + stuck-bead state for the coordinator resume-guard"*, `"no stuck
   beads"`) [14]. A case-insensitive grep for `stuck[- ]bead` across the plan bundles of all
   five repos returns **only design and spec text — no log line, no close reason, no finding
   recording a sweep that ran or a bead it reset** [13].
3. **No gate is recorded as unsatisfiable.** 236 gates: 231 closed, 5 open on abandoned plans,
   1 closed by documented override. Zero "gate failed" verdicts (§6).
4. **No bead carries a recorded reopen event.** `bd list --json` exposes no status history, and
   a grep for `reopen` across all bundles returns only *design* text about the `unhoist`
   feature plus one prose note (*"plan-026 was approved (pass-2 APPROVE), then reopened to fold
   upstream issue #85"*, `plan-026…/reviews/pass-3.md:3`) [15]. Reopens of *upstream GitHub
   issues* are recorded in close reasons (e.g. *"pybridge#10 reopened"*) — reopening a **bead**
   is not observable in this dataset at all. Absence of evidence, not evidence of absence.
5. **No bundle records a repair of the §2a dangling epic pointers.** 14 bundles have pointed at
   nothing for weeks and nothing detected it.
6. **`discovered-from` is optional and unenforced.** No manifest, gate, or checked step in any
   repo requires attaching it. This is why §4's trend cannot be trusted.

---

## Limitations the synthesizer must carry

- **Denominator is 55, not 83.** 28 bundles have no attributable bead graph (§2). All rates
  are over the 66% that do, and are therefore optimistic about coverage.
- **The trend in §4 is not a finding, it is an observation with a live rival explanation.** If
  the report says "the process improved", it will be over-reading this cluster.
- **Repo composition confounds every pooled time series** — the repos entered the corpus at
  different dates with different rates.
- **Molecule↔bundle mappings in §2 are date-inferred**, never recorded. Treat as
  **[uncertain]**.
- **`bd` has no status history**, so reopen/blocked *transitions* are structurally invisible;
  only terminal state and prose close reasons are observable.
- **yoshiko-flow is self-referential** (plan.yaml's own caveat) and supplies 24 of the 55
  measurable plans — 44% of the denominator.

---

## Sources

See `sources-execution-telemetry.json` (ids `[1]`–`[15]`).
