---
type: Research Artifact
description: Cross-repo interrogation (d3-pxe, evri_py, pybridge, writing, emacs.d,
  rc-files) — the external-validity test for whether findings from the self-referential
  yoshiko-flow corpus generalise to non-software, low-ceremony domains.
okf_spec: OKF-RESEARCH
---

# Cluster: herdr-repo-interrogation — cross-domain generalisation test

**Scope note (residue, not observation).** Every claim below is read from committed plan-bundle
artifacts (`reviews/pass-N.md`, `plan.md`, `context.md`, git history) — never from a live session.
Per 004's boundary, these are ARTIFACTS a session left behind, not the session loop itself. "Pass
N re-raises pass N-1's concern" means the two files' text says so; it does not mean an operator
watched the model thrash. [200]

**Scope reminder.** `yoshiko-flow` is explicitly NOT this cluster's subject — it is the
self-referential baseline other clusters characterise. This cluster covers six comparison repos:
`d3-pxe`, `evri_py`, `pybridge` (software, descending ceremony), and `writing`, `emacs.d`,
`rc-files` (non-software / config, nominally low-ceremony).

## 1. Per-repo profile table

All counts from `corpus_scan.py`'s corrected census (excludes `.worktrees/` mirrors and OKF-fixture
directories) [200]. yoshiko-flow is included as the reference row only; it is not this cluster's
target.

| repo | bundles | 1-pass | 2-pass | 3+-pass | 3+-pass rate | has `context.md` | has `log.md` | has `index.md` | median lifespan (hrs) |
| :-- | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| yoshiko-flow (baseline) | 56 | 13 | 19 | 23 | 41% | 56/56 | 27/56 | 26/56 | 53.3 |
| d3-pxe | 19 | 1 | 5 | 13 | 68% | 19/19 | 14/19 | 14/19 | 11.0 |
| evri_py | 9 | 3 | 3 | 1 | 11% | 8/9 | 1/9 | 1/9 | 1.5 |
| pybridge | 11 | 3 | 5 | 2 | 18% | 10/11 | 0/11 | 0/11 | 17.2 |
| writing | 11 | 6 | 3 | 2 | 18% | 11/11 | 0/11 | 0/11 | 0.4 |
| emacs.d | 4 | 4 | 0 | 0 | 0% | 4/4 | 0/4 | 0/4 | 0.0 |
| rc-files | 4 | 0 | 2 | 1 | 25% (of 4; 1 bundle had 0 passes) | 4/4 | 1/4 | 1/4 | 103.5 |

[200][213][214][216]

**Completed bundles.** Every bundle across all seven repos carries `context.md` except one each
in evri_py and pybridge (8/9 and 10/11) — that field is close to universal regardless of repo type.
`log.md`/`index.md` (the full OKF bundle-scaffold pair) are near-universal only in the two
heaviest-ceremony software repos (yoshiko-flow, d3-pxe) and effectively absent everywhere else,
including rc-files' one 3-pass bundle (1/4) — this is a **scaffolding-adoption gradient**, not
obviously a ceremony-vs-domain split: pybridge and writing (both non-trivial 3+-pass rates) show
0/11 for both fields, identical to emacs.d's 0/4. [214]

## 2. Process characterisation, with quotes

### d3-pxe (software, high ceremony — second-heaviest after yoshiko-flow)

d3-pxe's review convention is materially identical to yoshiko-flow's: a `C##` table with a
`Recommendation` column, `MEASURED` markers on evidence-backed findings, and an `Operator
Resolutions` table per pass. Sampling `Incubator/ansible/plans/plan-002-james-dixson-06dce8` and
`Incubator/litellm/plans/plan-010-james-dixson-49050b` (both recurrence-candidate bundles, §4)
shows the SAME residual-fix pattern twice: a concern is marked resolved in one pass's table, then
the NEXT pass's reviewer independently re-checks and finds the fix was not actually applied —
and says so explicitly:

> "Residual C7: the Approach `pve_lxc` bullet still cites `PVE-GPU-003/005/006` (GPU-003 is the
> host boot-order unit, owned by `pve_host`). Issue 3.3 + Success Criteria already dropped it."
> [208]

> "`index.md` still advertised the dropped skills gateway and CT 107." [209]

Both are genuine adversarial re-checks catching an incomplete edit, not a re-litigated disagreement
— the reviewer is not arguing with a prior decision, it is verifying an agreed fix landed and
finding it didn't.

### pybridge (software, moderate ceremony)

pybridge uses the SAME self-reported cross-pass verification convention as yoshiko-flow and
d3-pxe — an itemised "N of M concerns verified genuinely resolved" prose block:

> "All ten pass-1 concerns (C1–C6, M1–M3, G1, U1) verified genuinely resolved in the current
> `plan.md` (item-by-item below); the revisions introduced no material new risk. Load-bearing
> source claims re-confirmed against the code..." [210]

This convention is not a yoshiko-flow-specific ceremony artifact; it appears verbatim in structure
(if not exact wording) in a repo two organisations away.

### writing (non-software, nominally low ceremony)

writing's 391-file-corpus title convention differs ("Review Pass 1" not "Red-team pass"), but the
finding-table/`Operator Resolutions`/verdict-line structure is the same shape as the software repos
— this is NOT a degenerate review. The corpus's single highest-similarity recurrence candidate
(0.60, the highest score of all 8 corpus-wide) is in writing, `plan-010-james-dixson-e049e3`:

- pass-1, C4, severity **medium**: `"No READY gate on `[needs-source]`"`, resolution recorded as
  *"resolved (pending operator choice)"* — i.e. explicitly flagged incomplete at the time. [206]
- pass-2, C11, severity **low**: `"`[needs-source]` gate recall"`, resolution: *"Issue 3.3 gains
  the coverage note: guarantee is 'no flagged unresolved claim,' and READY also requires ≥1
  web-enabled footnoter pass to have run (no vacuous pass)."* [206]

Read side by side this is a **deepening**, not a re-raised objection: severity dropped medium →
low, and pass-2 closes the exact gap pass-1 had already flagged as pending rather than resolved.
This is the corpus's strongest textual-similarity match and it reads as convergence.

writing also revealed an important **parsing/measurement trap**: three of its 2-pass bundles show
a `verdict: REVISE` at the LAST recorded pass in the automated extraction, which on its face looks
like "review loop stalled without resolving." Reading the actual files shows this is wrong — the
pass-2 file's own `Operator Resolutions` table marks every row `resolved`, and the bundle's
`plan.md` frontmatter says `Status: complete`:

> pass-2 body: `"Final status: resolved — plan revised to v4."` / `plan.md`: `"**Status:**
> complete"` [207]

The bundle converged; it just never spawned a third file with the word "APPROVE" in it — the
operator or main session read the resolutions table and moved on. **This is a distinct
low-ceremony convention**: resolution is recorded inline in the same review file rather than by
issuing a confirmatory pass. A naive "last verdict field per bundle" metric would misclassify this
bundle as unresolved thrash; it is not.

### emacs.d (non-software, low ceremony — the sparsest repo, 4 bundles, all 1-pass)

emacs.d never produced a single 2+-pass bundle, so it contributes zero candidates to any
recurrence analysis. Two of its four single-pass reviews returned REVISE, and the two diverge in
what happened next:

- `plan-003` (REVISE → resolved in place): the pass-1 file's own `Operator Resolutions` table
  closes every concern via an operator decision recorded in the same document — no pass-2 file was
  ever created, and `plan.md Status: complete`. Same in-line-resolution convention as writing. [203]
- `plan-001` (REVISE → never followed up): `plan.md`'s phase log shows the plan was **reframed**
  (a transport pivot, EXP-004) and then explicitly parked:

  > "2026-06-19 drafting: v2: stdio-bridge transport (EXP-004) folded into plan body; parked
  > pending re-review" [202]

  `plan.md Status: drafting` — this bundle never converged; it was abandoned mid-review. It is
  neither a thrash episode (no repeated pass) nor a clean resolution — it is a third category the
  recurrence extractor cannot see at all, because there is no pass-2 to compare against.

emacs.d is the sharpest illustration of the study's central risk: **a 1-pass-only corpus cannot
manifest cross-pass recurrence by construction**, regardless of whether the underlying work was
troubled. Its one abandoned-mid-flight bundle would, if it existed in a heavier-ceremony repo, very
plausibly have produced a multi-pass thrash episode; here it just stops.

### rc-files (non-software, low ceremony — but its one heavy bundle rivals yoshiko-flow)

rc-files' 4 bundles are the most bimodal in the corpus: one 0-pass, two 2-pass (both converging
cleanly APPROVE), and one 3-pass bundle (`plan-004-james-dixson-f0bcc5`) that is, on inspection,
as thorough an adversarial review as anything sampled in d3-pxe or yoshiko-flow — 16 numbered
concerns in pass-1 alone, several `MEASURED` (i.e., reproduced, not asserted):

> "C4 | high | **MEASURED.** A *dangling* symlink is silently written **through**, into the repo.
> `install_renamed.rb:append_default_if_different` uses `dst.file?`, which follows symlinks:
> dangling → returns `dst` → FileUtils writes through the link to the source path. Reproduced:
> brew materialised `config.d3.yaml` (48718 bytes, `host: ""`) at the source path..." [204]

Pass-2 raises exactly ONE new concern (N1), and it is a **fresh mechanical defect introduced by
fixing pass-1**, not a re-raised one:

> "N1 | high | Risk renumbering left 12 of 14 in-prose `R<n>` references pointing at the wrong
> risk... [resolution] All 11 stale in-prose risk references corrected line-by-line (verified by
> re-grep)." [205]

This bundle converges (pass-3 APPROVE) and produces zero recurrence-fingerprint matches. It matters
for the study's confound question (§3): a config repo, tagged "low ceremony" by bundle-count alone,
produced a full-depth adversarial review indistinguishable in KIND from the software repos' heaviest
passes — ceremony intensity in a given bundle is not predicted by the repo's overall bundle volume.

### evri_py (software, lightest-ceremony software repo)

Sampled for contrast only (no recurrence candidates, §4): evri_py's 9 bundles skew toward 1-2
passes (7/9), and its `has_log_md`/`has_index_md` presence (1/9 each) is closer to the
non-software repos than to its sibling software repos d3-pxe/pybridge — another data point that
the OKF-scaffolding gradient (§1) tracks something other than software-vs-non-software.

## 3. The ceremony-vs-trouble confound — chased directly

**The confound is real and, on this corpus, dominant.** The clearest single number: repos with
higher OVERALL bundle-count and higher `has_log_md`/self-reported-signal rates ALSO have higher
3+-pass rates and higher recurrence-candidate counts — and that correlation holds regardless of
whether the repo is software or not.

| repo | bundles | 3+-pass rate | self-reported signals [215] | recurrence candidates [201] |
| :-- | --: | --: | --: | --: |
| yoshiko-flow | 56 | 41% | 29 | 4 |
| d3-pxe | 19 | 68% | 15 | 3 |
| pybridge | 11 | 18% | 4 | 0 |
| rc-files | 4 | 25% | 2 | 0 |
| writing | 11 | 18% | 1 | 1 |
| evri_py | 9 | 11% | 0 | 0 |
| emacs.d | 4 | 0% | 0 | 0 |

Reading down this table: the count of self-reported cross-pass verification signals and the count
of extracted recurrence candidates both track **repo-level review VOLUME** (total bundles × 3+-pass
rate), not the software/non-software axis. d3-pxe (software) and rc-files (non-software) both show
substantial ceremony in their heaviest bundles (§2); emacs.d (non-software) and evri_py (software)
both show almost none. **The high/low-ceremony split in plan.yaml's corpus table tracks bundle
COUNT, and bundle count is confounded with calendar time-in-service and how heavily each repo is
used for planned work — not cleanly with "software vs. non-software" or "task difficulty."**

Two consequences for the primary hypothesis (thrash correlates with under-specification, not
difficulty):

1. **Volume, not domain, predicts multi-pass rate.** A repo with 4 bundles total cannot show a
   3+-pass rate estimate with any precision — emacs.d's 0% and rc-files' 25% are each a single
   bundle's worth of signal (0/4 and 1/4). Neither number should be read as "non-software plans
   don't/do thrash"; both are point estimates from n=4.
2. **Where volume is present in a low-ceremony repo (rc-files' plan-004), the review looks exactly
   like the high-ceremony repos' reviews** — same MEASURED-evidence discipline, same table shape,
   same convergent (not re-litigating) second pass. This is evidence AGAINST "ceremony is a
   repo-level style setting that inflates thrash-looking artifacts regardless of real trouble" —
   when a bundle in a low-ceremony repo actually has enough at stake (here: credential/security
   exposure, MEASURED), the reviewer produces yoshiko-flow-grade rigor without yoshiko-flow-grade
   repo-wide ceremony. That argues the review DEPTH is responsive to the TASK, not merely
   inherited from repo convention — which is the opposite of the confound this cluster was asked
   to chase, and it is worth reporting plainly rather than forcing a single verdict: **the corpus
   supports both readings at different grain.** At the repo-aggregate level, ceremony (volume,
   scaffolding presence) and multi-pass rate move together — a real confound for cross-repo
   comparison. At the individual-bundle level, at least one clear counter-example (rc-files
   plan-004) shows depth tracking task stakes, not repo habit.

## 4. Recurrence-candidate distribution per repo (`finding_recurrence.py`, threshold 0.35, id-floor
0.15)

Corpus-wide: 79 bundles had ≥2 passes and were eligible; 1509 findings extracted; **8 candidate
thrash episodes total** [200][201].

| repo | eligible bundles (≥2 pass) | recurrence candidates | weak id-reuse (below floor) | self-reported signals |
| :-- | --: | --: | --: | --: |
| yoshiko-flow | 42 | 4 | 137 | 29 |
| d3-pxe | 18 | 3 | 105 | 15 |
| writing | 5 | 1 | 8 | 1 |
| pybridge | 7 | 0 | 1 | 4 |
| rc-files | 3 | 0 | 1 | 2 |
| evri_py | 4 | 0 | 0 | 0 |
| emacs.d | 0 | 0 | 0 | 0 |

**Every one of the 8 candidate episodes lives in exactly 3 of the 7 repos** (yoshiko-flow, d3-pxe,
writing), and **6 of the 8 are in the two highest-volume software repos**. This is a serious
external-validity limit stated plainly: this cluster CANNOT independently corroborate a
cross-domain pattern from recurrence-fingerprint matches alone — pybridge, rc-files, evri_py and
emacs.d combined contribute **zero** fingerprint-matched recurrence candidates despite 14 eligible
2+-pass bundles between them. The one non-software data point (writing's single episode, [206]) is
real, textually strong (0.60 similarity, the corpus maximum), and — as read in §2 — reads as
convergence rather than thrash. **A single convergent episode in one non-software repo cannot
license "the pattern generalises outside yoshiko-flow"; it can only fail to contradict it.**

## 5. Base rates for other clusters

Pass-count and outcome distribution per repo (bundle-level; a bundle's "final verdict" is read
from its LAST review-pass file, with the caveat from §2's writing discussion — a `REVISE`-labelled
final pass can still correspond to a `Status: complete` plan when resolutions are recorded inline):

| repo | 1-pass share | 3+-pass share | bundles ending APPROVE (of eligible ≥2-pass) | bundles ending REVISE (of eligible ≥2-pass, verdict-field only) |
| :-- | --: | --: | --: | --: |
| yoshiko-flow | 23% (13/56) | 41% (23/56) | 33/42 (79%) | 9/42 (21%) |
| d3-pxe | 5% (1/19) | 68% (13/19) | 18/18 (100%) | 0/18 |
| evri_py | 33% (3/9) | 11% (1/9) | 4/4 (100%) | 0/4 |
| pybridge | 27% (3/11) | 18% (2/11) | 6/7 (86%) | 1/7 (14%) |
| writing | 55% (6/11) | 18% (2/11) | 2/5 (40%) [see §2 caveat] | 3/5 (60%) [see §2 caveat] |
| emacs.d | 100% (4/4) | 0% (0/4) | n/a (no ≥2-pass bundles) | n/a |
| rc-files | 0% (0/4, 1 had 0 passes) | 25% (1/4) | 3/3 (100%) | 0/3 |

[200][207][213]

**Reading the writing REVISE column:** all 3 of writing's "REVISE-final" bundles are, on direct
read of `plan.md`, `Status: complete` with inline-resolved concerns (§2) — the verdict-field
metric alone overstates writing's unresolved-thrash rate. Any downstream cluster reusing this
table should either re-verify `plan.md` status per bundle or treat writing's 40/60 split as a
measurement artifact, not a real convergence-rate gap.

## 6. Plain verdict on external validity

- **Multi-pass review bundles DO exist outside yoshiko-flow**, in every repo except emacs.d, and
  the review CONVENTION (finding table, severity, Operator Resolutions, self-reported cross-pass
  verification) is materially the same shape across all seven repos regardless of domain. This
  part of the study generalises: the artifact FORM yoshiko-flow uses is not sui generis.
- **The recurrence-FINGERPRINT signal used to detect thrash episodes does not generalise on this
  corpus.** 6 of 8 candidate episodes are in the two heaviest-volume software repos; the three
  lowest-volume repos (emacs.d, rc-files, evri_py combined: 16 eligible bundles) produced zero.
  This is either because (a) low-volume repos genuinely thrash less, (b) 14 bundles is too few
  to expect even one recurrence episode at this corpus's base rate (~8/79 ≈ 10% of eligible
  bundles), or (c) some interaction of both. The data cannot distinguish (a) from (b) — **this is
  the single most important limitation for downstream synthesis to carry forward**: absence of
  detected recurrence in the low-ceremony repos is NOT evidence of absence of thrash: at the
  corpus base rate, 14 bundles would be expected to produce roughly 1-2 episodes by chance, and
  observing 0 is within noise of that expectation, not a contradiction of it.
- **The ceremony-vs-domain confound is real at the repo-aggregate level** (§3): bundle volume,
  OKF-scaffold presence, self-reported-signal count and 3+-pass rate all move together and do not
  cleanly separate on software-vs-non-software. **It does not fully hold at the individual-bundle
  level**: rc-files' one heavy bundle (plan-004) matches yoshiko-flow-grade adversarial rigor,
  arguing that review depth tracks task stakes at least some of the time, independent of repo
  habit. Both readings are supported by direct evidence in this corpus; a downstream synthesis
  claiming the confound is fully resolved in either direction would be overclaiming.
- **Net assessment:** findings from yoshiko-flow about the SHAPE of thrash artifacts (recurring
  concern text, self-reported reproduction sections, residual-fix catches) are corroborated
  qualitatively in d3-pxe, pybridge, writing and rc-files — the same textual PATTERNS appear.
  Findings about thrash FREQUENCY or about a detector's usefulness cannot yet be generalised past
  yoshiko-flow and d3-pxe with this corpus's sample sizes; the non-software repos are too sparse
  (14 bundle-eligible for cross-pass comparison total, and only 1 with a matched episode) to
  support a frequency claim either way.
