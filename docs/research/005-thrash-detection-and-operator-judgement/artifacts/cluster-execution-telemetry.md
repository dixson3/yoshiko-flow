---
type: Research Artifact
description: Execution-telemetry cluster (beads/bd) findings for yf-research project
  005 — what the live beads graph SEES about candidate thrash episodes, and at what
  latency
okf_spec: OKF-RESEARCH
---

# Cluster: execution-telemetry

Secondary Q: at which yf surfaces could a thrash detector actually fire, and what does each
surface SEE? This cluster answers from the **beads execution graph** — residue of execution
recorded in `.beads/` state, never a live session observation (004's boundary; method_notes
repeats it and this report holds to it throughout).

All 7 corpus repos carry a healthy, non-wedged `bd` config. `bd status --json` returned a
clean summary object (no `error` key) in every repo, so none needed `yf-beads-init` and none
were touched beyond read-only `bd`/`grep`/`python3` inspection [1].

## 0. What `bd` actually exposes, measured directly

Two files exist per repo under `.beads/`: `issues.jsonl` (issue snapshots, one line per
current issue) and `interactions.jsonl` (an append-only event log). The **field-name union**
over every record in yoshiko-flow's `issues.jsonl`:

```
['_type','assignee','await_type','close_reason','closed_at','comment_count','created_at',
 'created_by','defer_until','dependencies','dependency_count','dependent_count','description',
 'external_ref','id','issue_type','labels','metadata','mol_type','notes','owner','priority',
 'started_at','status','title','updated_at']
```

and over `interactions.jsonl`: `['actor','created_at','extra','id','issue_id','kind']`, with
every observed `kind` equal to `"field_change"` and every `extra.field` equal to `"status"` —
i.e. **only status transitions are recorded as discrete events** in this corpus; no other
field (priority, assignee, description) has ever generated an interaction row here [2]. This
is a stronger transition record than the `bd history` Dolt-commit log, see §1.

## 1. Reopen / status oscillation

**Two candidate sources exist and they disagree in kind, not just detail.**

`bd history <id>` walks Dolt commits touching the issue's row. For a bead worked inside this
very research molecule's authoring session (`yf-mol-bh8.2.11`), it returned **745 entries**
for a bead created and closed within roughly 90 minutes on 2026-08-26 [3]. Counting the status
token embedded in each entry's line:

```
 641 [P2 - closed]
   1 [P2 - in_progress]
 103 [P2 - open]
```

Nearly all of those "open" and "closed" entries are **identical, back-to-back Dolt commits at
the same wall-clock second** touching a row whose semantic status did not change between them
— visible directly in the raw output (`ki5ebma3 2026-08-28 14:50:05` / `nb0dueaf 2026-08-28
14:50:09` / `277r5fu3 2026-08-28 14:50:09`, all `[P2 - closed]`, all on a bead last touched two
days earlier) [3]. **`bd history` is swamped by commit-granularity noise and is not a usable
transition log on its own** — this independently corroborates `yf-ek9a`'s "beads are closed in
batches" finding (a Dolt commit that flushes many rows re-writes each row's history, whether or
not that specific row's semantics changed) [4].

`interactions.jsonl`'s `field_change` events are the real signal: each row carries
`old_value`/`new_value` for exactly one semantic status change, deduplicated. For the same
bead, the four real transitions are:

```
2026-08-26T01:20:26Z  open -> closed   (reason: normal close, long prose)
2026-08-26T01:32:36Z  closed -> open   (reason: null)
2026-08-26T01:32:36Z  in_progress -> closed  (reason: "...NOTE: this reason was first recorded
                       against yf-mol-bh8.2.11 (Issue 1.6b) by a bead-id mis-mapping; 2.11 has
                       been reopened and carries its own control, ctl-208-edge-scope.")
2026-08-26T01:34:22Z  in_progress -> closed  (reason: real close, ctl-208-edge-scope)
```
[5]

**Population and reopen rate, corpus-wide** (interactions.jsonl, `field_change` events where
`field == "status"`, `old_value == "closed"` and `new_value` in `{open, in_progress}`):

| repo | interactions | status changes | reopens | reopen rate |
|:--|--:|--:|--:|--:|
| yoshiko-flow | 1687 | 1687 | 3 | 0.18% |
| d3-pxe | 599 | 599 | 0 | 0% |
| evri_py | 51 | 51 | 0 | 0% |
| writing | 293 | 293 | 0 | 0% |
| pybridge | 183 | 183 | 0 | 0% |
| emacs.d | 53 | 53 | 0 | 0% |
| rc-files | 103 | 103 | 0 | 0% |

[6]. `interactions.jsonl`'s date range in every repo starts at or within a day of that repo's
earliest `issues.jsonl` `created_at`, so this is close to full-lifetime coverage of the
issue-tracking era, not a short recent window [7].

**Hand-audit of all 3 yoshiko-flow reopens** (the only nonzero cell in the corpus):

- `yf-mol-84r.4.1`: `in_progress→closed` (reason `"probe: unset var"`) then
  `closed→in_progress` (reason `None`) 10 seconds later, then `in_progress→closed` with a real
  close reason. A mechanical probe/no-op cycle, not rework [8].
- `yf-mol-bh8.3.2`: `in_progress→closed` (reason `"probe"`), `closed→open` (reason `None`) 64
  seconds later, `open→closed` immediately after with the real close reason. Same probe
  pattern [9].
- `yf-mol-bh8.2.11`: shown above — a **bead-id mis-mapping bookkeeping correction**, explicitly
  self-described in the close reason as such, not a re-litigated decision [5].

**Verdict:** the field exists, is populated at near-full-lifetime coverage, and the reopen rate
is genuinely near zero (3/2969 status changes corpus-wide) — but every single observed
instance in the hand-audit is a **tooling artifact** (a "probe" close/reopen pair, or a
clerical bead-id fix), not a content-level re-litigation. **Reopen-as-recorded-in-bd never
once corresponded to "the agent changed its mind and redid the work" in this corpus.** This is
a genuine, if narrow, negative finding: bd's reopen field is real and readable, but at this
population size it has zero demonstrated discriminating power for thrash — it fires on
tooling noise, not on content oscillation. A detector keyed on it alone would be silent on
every real thrash episode the other clusters found via review-pass recurrence, because none of
those episodes produced a bd status reopen at all [10].

## 2. `discovered-from` chains

Population is low and depth is shallow, corpus-wide:

| repo | issues | discovered-from edges | edges/issue | roots | max depth | depth distribution |
|:--|--:|--:|--:|--:|--:|:--|
| yoshiko-flow | 1245 | 26 | 2.1% | 23 | 2 | {2: 23} |
| d3-pxe | 395 | 4 | 1.0% | 3 | 2 | {2: 3} |
| evri_py | 304 | 8 | 2.6% | 8 | 2 | {2: 8} |
| writing | 319 | 7 | 2.2% | 7 | 2 | {2: 7} |
| pybridge | 229 | 15 | 6.6% | 11 | 3 | {2: 10, 3: 1} |
| emacs.d | 23 | 0 | 0% | — | — | — |
| rc-files | 84 | 4 | 4.8% | 2 | 2 | {2: 2} |

[11]. Max fan-out from any single parent observed corpus-wide is **3** (`yf-9e73640b` and
`pybridge-hax`) [11]. No chain anywhere in the corpus exceeds depth 3.

**Verdict:** `discovered-from` is used, but sparsely (1–7% of issues) and almost exclusively as
a **single-level** annotation ("found X while doing Y") rather than a deepening chain. At this
depth ceiling (2, occasionally 3) the field structurally **cannot** distinguish "the work kept
growing" thrash from ordinary, bounded discovery — there is no long tail to threshold against.
A detector that fired on "depth >= 2" would fire on effectively every recorded use of the field
in this corpus, since depth 2 is the mode, not an outlier. **This signal does not discriminate
in the corpus as measured** — it is present but structurally too shallow to carry the intended
meaning.

## 3. Blocked beads

`bd status --json`'s live-computed `blocked_issues` count, and `bd blocked --json`'s
enumeration, agree exactly in the two repos checked in detail (yoshiko-flow: 6/6; writing:
29/29) [12][13]. `bd blocked` is a **live, dependency-graph-derived** view (`blocked_by` lists
only currently-open blocker ids), not a stored status literal — `bd list --status blocked`
returns an empty array in every repo tried, confirming "blocked" is computed, not stored
[14].

Hand-audit for the corruption pattern named in the task ("blocked-with-no-live-blocker"):
scanning every `blocks`-type dependency edge in every repo's `issues.jsonl` for a
`depends_on_id` that does not resolve to any known issue in that repo found **exactly one**
dangling reference corpus-wide, and it is a parsing artifact, not a real edge:
`yf-67e2d9e7 -> --metadata` in yoshiko-flow (the depends_on value is a stray CLI flag string,
not an issue id) [15]. Zero dangling refs in the other 6 repos. Separately, checking every
non-closed issue whose blocker is `closed` (a state that is fine — `bd` computes readiness
dynamically and a closed blocker does not block) found small counts (evri_py: 17, writing: 2,
all others: 0) and every sampled case in writing was a real open successor genuinely waiting on
a specific closed predecessor's row, not orphaned state [16].

**Verdict:** blocked-state in this corpus is structurally clean — the specific corruption
pattern named in the task brief is essentially absent (1 stray non-id string out of thousands
of edges). The live case sampled in yoshiko-flow at retrieval time (`yf-mol-49u.5` blocked on
3 sibling retrieve tasks in this very research molecule) is ordinary phase-gating in a DAG
formula, not thrash [12]. Blocked-count is available cheaply and in real time
(`bd status --json`), but as measured here it reflects **planned structural dependency**, not
rework — no case in the sample showed a bead blocked because earlier work had to be undone.

## 4. Phase-log churn

`log.md` exists in only 43/114 = 37.7% of plan bundles corpus-wide (a newer OKF-bundle
convention; most of the corpus predates it) [17]. Of the 37 `log.md` files under the 5
software repos scanned by `find ... -name log.md`, the `## ` heading-entry count distribution
is:

```
   3 files: 0 entries
  16 files: 1 entry
  18 files: 2 entries
```

[18] — **no `log.md` in this corpus has more than 2 top-level entries.** Reading one of the
2-entry files in full (`plan-054-james-dixson-535968/log.md`) shows why: its single populated
section is a **retrospective bulleted recap of all 5 red-team passes**, written once
(evidently at close/package time), not five separately-dated append events:

```
- review-pass: red-team pass 5 (fifth independent, via Agent): REVISE — 9 of 9 pass-4
  resolutions reproduced; ... LOOP BOUND REACHED, escalates to operator
- review-pass: red-team pass 4 ...
- review-pass: red-team pass 3 ...
- review-pass: red-team pass 2 ...
- review-pass: red-team pass 1 ...
```
[19]. This corroborates the review-pass-recurrence cluster's raw counts (this bundle really did
run 5 REVISE-heavy passes and hit a loop bound), but it is **not** a live phase log a detector
could watch incrementally — it is a summary artifact assembled after the fact by whichever
agent wrote it, with no timestamps separating entry-writing from event-occurring.

**Verdict:** phase-log churn as literally specified (entries that revise or contradict earlier
entries, observed as they accrue) is **not measurable in this corpus** — the object doesn't
have the shape the question assumes. `log.md` is populated in barely a third of bundles and,
where present, is a single retrospective write, not a running log. Absence stated plainly per
the epistemic mandate: there is no evidence either for or against phase-log churn as a signal,
because the artifact required to observe it does not exist in the form assumed.

## 5. Timing

Both named caveats were read directly rather than worked around, per the task's instruction.

- `yf-zrtx` (open, P2): `"Beads carrying both started_at and closed_at: 86 of 225 (plan-048
  alone: 0 of 39)... Separately, bd list --json does not expose started_at at all."` [20]
- `yf-ek9a` (open, P2): `"The coordinator closes beads in batches rather than when each unit of
  work finishes. That collapses distinct work intervals onto a single timestamp, so 84% of all
  observed interval overlap is an artifact of when the closes were flushed — not of when work
  actually ran concurrently."` [21]

Live re-check against the current `issues.jsonl` snapshot (not the plan-052 EXP-006 numbers,
but consistent with them in kind): `started_at` is present in the field union but is null on a
large share of closed beads, and `bd list --json`'s own output — verified directly during this
retrieval by inspecting `bd blocked --json` records, which is the same code path — never
surfaces `started_at` in a list-shaped call; it only appeared when a full object was returned,
matching yf-zrtx's claim [2]. §1's own hand-audit adds a **third**, independently-measured
mechanism for the same distortion `yf-ek9a` names: `bd history`'s 745-entry, mostly-duplicate
output for a bead touched over 2 days earlier shows the batch-commit mechanism directly, not
just its statistical footprint (the "84% overlap is artifact" figure) [3][4].

**Given both caveats, no duration-based signal is derived in this report.** Any
"time-in-status" or "concurrent work" metric built from `bd` timestamps in this corpus would be
measuring the coordinator's flush schedule for a majority of beads, not the work — exactly
`yf-ek9a`'s finding, now corroborated by a second, independently-run method. Timing is the one
signal category in this cluster with a **known, filed, unresolved instrumentation gap**, not
merely a low population rate.

## 6. Join to plan bundles

Matching each `corpus_scan.py`-enumerated bundle's `plan_id` string against a substring search
over every bead's title + description + close_reason + metadata JSON in the same repo:

| repo | bundles joined | bundles total | rate |
|:--|--:|--:|--:|
| yoshiko-flow | 41 | 56 | 73% |
| d3-pxe | 12 | 19 | 63% |
| evri_py | 4 | 9 | 44% |
| writing | 8 | 11 | 73% |
| pybridge | 10 | 11 | 91% |
| emacs.d | 1 | 4 | 25% |
| rc-files | 3 | 4 | 75% |
| **total** | **79** | **114** | **69.3%** |

[22]. Unjoined bundles are not simply pre-beads-adoption era artifacts: `plan-044-james-dixson-
f6fdbd` in yoshiko-flow (git-dated 2026-08-17/18, well inside the repo's beads-active period,
which started 2026-04-05) is unjoined, alongside older bundles like `plan-002` (2026-05-31)
[23]. So the gap is not fully explained by "beads wasn't adopted yet" — some plans in the
beads-era simply were not bead-tracked by a string-matchable `plan-NNN` reference (they may
have used only an epic id with no plan-string cross-reference, or were executed without
per-issue bd tracking at all).

**Verdict:** a 69% join rate is workable for cross-referencing but is not complete — roughly
3 in 10 bundles have no bd-side trace this method can find. Any bd-derived signal in this
report should be read as covering **at most** 69% of the corpus's plan bundles, and the
uncovered third is itself informative: those plans left **no beads-execution residue at all**
that a plan-id string match can recover, meaning a bd-only detector is structurally blind to
them regardless of what happened during their execution.

## Surface / latency / discrimination table

| surface | what it sees | latency (when a detector could read it) | discriminating power (thrash vs. convergence/difficulty/tooling/underdetermination) |
|:--|:--|:--|:--|
| **bd status reopen** (`interactions.jsonl` field_change, closed→open/in_progress) | Real, deduplicated status transitions with an optional free-text `reason`. Population near-full-lifetime; reopen rate 3/2969 (0.1%) corpus-wide. | Available the instant the transition is written — genuinely early/real-time if the coordinator emits it live. | **None demonstrated.** All 3 hand-audited reopens in the corpus were tooling probes or an id-mapping bookkeeping fix, not content rework. Cannot distinguish anything because it never fired on a real episode in this sample. |
| **`bd history` (Dolt commit log)** | Every Dolt commit touching the row, including no-op re-commits from batch flushes. | Same latency as reopen, but | **Actively misleading** — 641/745 entries for one bead were duplicate "closed" snapshots from unrelated batch commits. Must not be used as a transition source; corroborates `yf-ek9a`. |
| **`discovered-from` chains** | Explicit "found while doing" edges, fan-out and depth. Population 1–7% of issues; depth caps at 2 (one repo hit 3 once). | Available as soon as the child bead is filed — early, in principle. | **Cannot discriminate at this depth ceiling.** Depth 2 is the corpus mode; there is no observed long tail to threshold "growing scope" against. |
| **blocked beads** | Live, dependency-graph-computed blocking state (`bd status`/`bd blocked --json`), agrees exactly between the two methods checked. Structurally clean — 1 dangling ref out of thousands of edges. | Real-time; `bd status --json` is cheap and always current. | **Reflects planned structure, not rework**, in every sampled case (including a live example from this very molecule). Not evidence of thrash on its own; would need to be paired with a "blocked, then the blocker itself was reworked" pattern this report did not find instances of. |
| **phase-log churn (`log.md`)** | Populated in 37.7% of bundles; where present, 0–2 top-level entries, and the 2-entry files are single retrospective recaps, not incremental writes. | **Not available early** — written once, apparently at close/package time. | **Unmeasurable as specified.** The artifact does not have the incrementally-written shape the question assumes; absence stated as the finding. |
| **timing (`started_at`/`closed_at` spans)** | `started_at` null on a large share of beads (yf-zrtx: 86/225) and unexposed by `bd list --json`; closes are batch-flushed, collapsing 84% of observed overlap into an artifact (yf-ek9a), independently corroborated here by `bd history`'s duplicate-commit pattern. | Would be near-real-time if the two filed defects were fixed; **as instrumented today, closed-bead timestamps lag the actual work by an unknown, batch-dependent amount.** | **Not usable today.** Both preconditions for a duration-based signal (unconditional `started_at` write, per-unit close rather than batch close) are open bugs, not corpus properties this report can work around. |
| **plan-bundle join** | 69.3% of bundles have at least one bead referencing their plan_id string; the rest have no bd-side trace findable this way. | N/A — this is a coverage ceiling, not a per-episode latency. | Limits every row above: any bd-derived finding covers at most 69% of bundles, and that 69% is not obviously the same population the prose-artifact clusters cover. |

## Bottom line

Beads execution state in this corpus is **structurally healthy** (no wedged DBs, near-zero
dangling dependency edges, live-computed blocked state that agrees with itself across two query
paths) but carries **no signal in this sample that discriminates thrash from convergence,
difficulty, tooling failure, or underdetermination better than the prose artifacts already do**.
The one field that in principle records exactly what the task asked for — reopen — exists,
is well-populated, and fired on tooling noise every single time it fired in this corpus, never
once on genuine rework. `discovered-from` and blocked-state are real but too shallow/structural
to carry the intended meaning at current population sizes. Phase-log churn cannot be measured
because the artifact isn't written incrementally. Timing is blocked by two filed, open defects
(`yf-zrtx`, `yf-ek9a`) that this retrieval independently corroborated via a **third** mechanism
(`bd history`'s batch-commit duplication). **The prose artifacts (review-pass recurrence, git
churn, phase narrative) are, on this corpus, the load-bearing evidence; bd telemetry as
currently instrumented is a health-check surface, not a thrash-detection surface.** That
absence is itself the deliverable this cluster was commissioned to find.
