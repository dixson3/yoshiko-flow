---
type: Research Artifact
description: Retrieval findings for the git-churn-signatures cluster of yf-research
  005 — base rates, widened commit-message pattern audit, revert audit, file-re-touch
  hand audit, timing shape, and confounders, answering whether git history carries
  a thrash signature visible earlier or more reliably than review-pass residue.
okf_spec: OKF-RESEARCH
---

# Git churn signatures — retrieval findings

Corpus: 114 plan bundles / 301 review passes across 7 repos, per
`scripts/corpus_scan.py --json` (`corpus_corrected` in `plan.yaml`), retrieved 2026-08-28.
`scripts/churn_signature.py --census <census.json> --json` is the tool of record; its
author-reported validation run (114/114 bundles, 0 errors, 5 churn-signal commits, 233
repeatedly-touched files across 53 bundles) is reproduced identically here — I re-ran it
myself rather than trusting the number [1].

## 1. Base rates

**Total commits per repo** (`git log --oneline | wc -l`, all branches' current HEAD, run
2026-08-28) [2]:

| repo | total commits | commits inside plan-bundle windows (sum, may overlap) | bundles w/ window |
| :-- | --: | --: | --: |
| yoshiko-flow | 697 | 727 | 56 |
| d3-pxe | 323 | 344 | 19 |
| evri_py | 113 | 56 | 9 |
| writing | 117 | 44 | 11 |
| pybridge | 242 | 141 | 11 |
| emacs.d | 178 | 12 | 4 |
| rc-files | 374 | 35 | 4 |
| **total** | **2044** | **1359** | **114** |

Source: `churn_signature.py --census`'s `total_commits_in_window` field, summed per repo [3].

**yoshiko-flow's in-window sum (727) exceeds its total commit count (697).** This is not a
counting bug — a bundle's "window" is `[first commit touching the bundle dir or mentioning
`plan-NNN`, last such commit]`, and overlapping/adjacent plan windows both claim the same
intervening commits. This is the tool's own documented design (`churn_signature.py --help`:
"the union of (a) commits whose path-scoped `git log` touches the bundle directory... and (b)
commits... whose message mentions the plan's short id") [4]. **Consequence for every number
below:** "commits in window" is not "commits about this plan" — it is contaminated by whatever
else landed on the branch between the plan's first and last touch. This is documented further
in §6.

**Base rate of revert-ish commit messages across ALL history, not just windows.** I ran a
deliberately *broad* regex over full commit messages (subject + body) in every repo — `revert`,
`redo`, `take 2`/`take two`, `actually`, `fix the fix`, `oops`, `undo`, `wrong`, `incorrect`,
`correct.*in place` — case-insensitive, unanchored:

```
git -C <repo> log --oneline -E --regexp-ignore-case --grep='revert' --grep='redo' \
  --grep='take 2' --grep='take two' --grep='actually' --grep='fix the fix' --grep='oops' \
  --grep='undo' --grep='wrong' --grep='incorrect' --grep='correct.*in place'
```

| repo | total commits | broad-pattern hits | rate |
| :-- | --: | --: | --: |
| yoshiko-flow | 697 | 75 | 10.8% |
| d3-pxe | 323 | 49 | 15.2% |
| evri_py | 113 | 6 | 5.3% |
| writing | 117 | 2 | 1.7% |
| pybridge | 242 | 8 | 3.3% |
| emacs.d | 178 | 10 | 5.6% |
| rc-files | 374 | 13 | 3.5% |
| **total** | **2044** | **163** | **8.0%** |

[5]. This broad pattern is **not** window-scoped — it is the whole-history base rate, and it
is roughly **32x higher** than `churn_signature.py`'s 5 window-scoped hits taken at face value
(before accounting for the narrower pattern — see §2). That gap is the headline of this
retrieval: the low count is mostly the regex, not the world, but the *broad* count is also
mostly noise (see below), so the honest number sits well below either extreme.

## 2. Interrogating the regex — original vs widened

**The single largest false-positive source: `git log --grep` matches the FULL commit body, but
`--oneline` only displays the subject.** A "wrong" or "incorrect" hit's matched word is
frequently buried in body prose describing what a *first-time* fix corrected, not a redo of the
plan's own prior work. Example — `yoshiko-flow` commit `5b7edb9` ("Simplify to Claude Code
only, inline phases, add consistency rule and spec") matches `wrong` only via a buried bullet:

```
git -C ~/workspace/dixson3/yoshiko-flow log -1 5b7edb9 --format="%B" | grep -in 'wrong'
```
> `- Fix check-prereqs.sh: wrong beads URL, missing git check, stale comment`

[6]. That is a first-pass bug description in a changelog-style bullet, not evidence the plan
redid its own prior work. `churn_signature.py`'s design explicitly anticipated this — its
docstring notes "wrong"/"incorrect" are only counted "as a correction admission, not just a
description" [1], which the tool's actual pattern implements far more conservatively than my
broad grep. **Widening the search myself thus mostly demonstrates why the narrow pattern is
narrow, not that it is missing signal.**

**`revert` isolated:** literal `^Revert` (the exact prefix `git revert`'s porcelain generates)
appears **0 times as a true `git revert` commit** across all 2044 commits in all 7 repos — the
1 yoshiko-flow, 1 evri_py, and 3 rc-files matches for `--grep='^Revert'` are all body lines that
happen to start with the word "Revert" as prose ("Revert is `git checkout` on the affected
index paths"; "Reverts 5d03ddc's PYBRIDGE_REPO dependency"; "Reverts the removal from f27d2fa")
[7]. This confirms `churn_signature.py`'s reported "no literal `git revert` commits found in
this corpus" [1] and demonstrates that **hand-authored semantic reverts exist but are rare and
essentially always OUTSIDE plan-bundle windows** (see §3).

**Vocabulary this repo's commit convention actually uses for correction, that the pattern's own
design anticipates and largely catches:** `plan-NNN Issue X.Y` retry framing dominates — a
retrospective/self-correction shows up as *prose inside a normal Issue-numbered commit*, not as
a separate revert-flavored commit. The clearest true positive found by re-reading, not by
regex, is yoshiko-flow `18f3959`:

> "Third drift of one REQ inside one plan: grep gave 25, the spec asserted 24, and
> retrospective-report was unenumerated." — commit `18f3959e1daf1b429799671068dc8d1162722b15`,
> subject "plan-045: make REQ-CLI-006 self-consistent and actually executed" [8]

This is a genuine, self-reported, same-day recurrence (the plan's spec drifted from its own
implementation three separate times within one execution), caught by the narrow `actually`
pattern, and it is the **strongest single artifact this retrieval found**. It sits in the same
commit burst as four Epic-numbered commits earlier that day (§5).

**Words the corpus uses that a naive detector could add, spot-checked as genuinely
correction-flavored rather than noise:** "correct ... in place" (already in the tool's pattern
— `d3-pxe`'s `07d1bfb`, "correct plan-016's 440 MB figure in place, at all four sites" [9]),
and "amend"/"reconcile"/"drift" as used in `18f3959`'s body above. I checked "for real this
time", "second attempt", "properly", "rework", "supersede", "back out" against all 7 repos'
full history and found **zero matches** for any of them — these phrasings are simply not this
operator's or these repos' idiom; the corpus's actual retry vocabulary is `actually`,
`correct...in place`, and prose self-admission ("third drift", "survived a sweep because...").
Widening the pattern to include them would add nothing measurable here [10].

**Bottom line for §2:** the original 5-hit count is a **precision-optimized undercount**, not a
broken regex — every one of the 5 hits verified as a true positive on inspection (§ below), and
a maximally broad widening (163 hits) is dominated by body-text false positives from unrelated
first-time bug descriptions. The real, defensible number for "genuine within-plan-window
correction/redo commits" in this corpus is closer to **5–10**, not 163, and not 0.

## 3. Revert / reset / force-push residue

Actual `git revert`-generated commits: **0** across all 2044 commits, all 7 repos [7]. Hand-
authored commits whose body explicitly frames themselves as undoing prior work ("Reverts
X's..."): **4**, found via the `^Revert` body-line check —

- `evri_py` `db41594`: "Reverts 5d03ddc's PYBRIDGE_REPO dependency. evri_py owns the assets
  that..." [11]
- `rc-files` `8b05e8b`: "Reverts the 5440463 vendoring of yf-beads/naba skill markdown and
  the..." [12]
- `rc-files` `50060b7`: "re-add CodeGraphContext to curated uv tool list" / body: "Reverts the
  removal from f27d2fa. Supports Python 3.10–3.14 per upstream, no pin needed." [13]
- `rc-files` `dbbded4`: "re-add serena to curated uv tool list (pinned to Python 3.13)" / body:
  "Reverts the removal from f27d2fa. Same Python 3.13 pin as before..." [14]

All four are **genuine semantic reverts** — real undo-a-prior-decision commits — but none of
them fall inside a plan-bundle commit window that `corpus_scan.py` tracks: `rc-files` has only
4 plan bundles total, and these commits are ordinary repo-hygiene work outside any tracked
plan's window; `evri_py`'s is likewise outside its 9 windowed bundles. **This is a real limit
on git as a plan-scoped thrash detector**: the one class of commit that is unambiguously
"redo," in this corpus, systematically occurs in *un-planned* maintenance work, not inside the
planned, reviewed executions the rest of this study is about. I did not find a single
bundle-window-scoped semantic revert in any of the 7 repos.

I diffed one sample (`d3-pxe` `07d1bfb1ba643f03e8255a82489cc151a07890ef`, the "correct...in
place" hit) against its stated predecessor to check whether it substantially undoes prior work:
its diff is **not** an undo — it is an *annotation* ("Annotated rather than silently rewritten:
plan-016 is a historical record, so each site now carries a dated correction block explaining
WHY the number is wrong, not just that it is" [9]) added across a different plan (`plan-017`)
correcting a documentation error discovered in `plan-016`'s closed record. This is **cross-plan
correction, not intra-plan thrash** — a later plan catching an earlier plan's number, appended
rather than reverted. It would not read as "thrash" to a human reviewer; it reads as normal
quality control at a plan boundary.

## 4. File re-touch hand audit

`churn_signature.py` reports **233 repeatedly-touched files across 53 of 114 bundles** (61 had
none) at the default `--min-file-touches 3` [1]. I hand-audited 20 samples spanning all 5
non-trivial repos (yoshiko-flow, d3-pxe, evri_py, pybridge, rc-files — writing and emacs.d had
zero bundles with any repeatedly-touched file, discussed below), reading each touching commit's
subject via `git log -1 --format='%h %ai %s' <sha>` for every listed SHA.

| # | repo | bundle | file | touches | commit subjects (abridged) | verdict |
| --: | :-- | :-- | :-- | --: | :-- | :-- |
| 1 | yoshiko-flow | plan-010 | `yf/src/main.rs` | 9 | spans the whole plan; CLI entrypoint every feature wires into | NORMAL (hot file) |
| 2 | yoshiko-flow | plan-010 | `SPEC.md` | 6 | SPEC-first mandate — every Issue amends spec first | NORMAL (mandated hot file) |
| 3 | yoshiko-flow | plan-010 | `Cargo.toml`/`Cargo.lock` | 5–6 | dependency bumps per feature | NORMAL (build metadata) |
| 4 | yoshiko-flow | plan-054 | `yf/tests/harness_cross_e2e.rs` | 4 | Issues 1.6-1.8, 2.2-2.4, 2.1, 2.5-2.6 — sequential distinct Issues [15] | DECOMPOSITION |
| 5 | yoshiko-flow | plan-054 | ~30 `skills/*/SKILL.md`, `README.md` files | 3 each, **same 3 SHAs** (`ac56bb0`,`7d656b2`,`9d1f653`) | a single mechanical bulk operation (skills-root collapse) touching dozens of files identically, not per-file back-and-forth [16] | NORMAL (mechanical bulk edit) |
| 6 | yoshiko-flow | plan-044 | `yf/src/coverage.rs` | 7 | 5 SHAs are `plan-044` Epics/Issues (same day, 2026-08-17); **2 SHAs (`4380c74`,`6d12a8e`) are `plan-054` commits from 2026-08-26**, 9 days later [17] | **WINDOW-CONTAMINATED** — 5/7 genuine decomposition, 2/7 belong to a different plan entirely, caught inside plan-044's window only because the window runs to the bundle's last-touch date |
| 7 | yoshiko-flow | plan-018 | `yf/src/cmd/self_cmd/mod.rs` | 6 | Issues 3.1→3.2→3.3→3.4a→3.5→4.1, all same day (2026-06-30) [18] | DECOMPOSITION |
| 8 | yoshiko-flow | plan-045 | `CHANGE-VALIDATION.md` | 5 | Epics 1→2→3→4, then the `18f3959` "actually executed" fix (§2) — same day, tight then a 71-min gap [19] | DECOMPOSITION + 1 genuine correction |
| 9 | d3-pxe | plan-016 | `ansible/roles/pve_backup/defaults/main.yml` | 7 | Issues 1.2+1.4→1.6→Epic2→Epic3→4.1-4.4→5.2→a later SPEC correction, spanning weeks [20] | DECOMPOSITION |
| 10 | d3-pxe | plan-010 | `ansible/roles/litellm/defaults/main.yml` | 7 | Issues 3.1→3.2→3.3→3.4→3.6→5.1→an operator-decision redaction commit [21] | DECOMPOSITION |
| 11 | d3-pxe | plan-011 | `ansible/inventory/host_vars/postgres.yml` | 4 | 3 plan-011 commits + **1 `plan-010` commit** (`7a45c98`) [22] | **WINDOW-CONTAMINATED** (cross-plan) |
| 12 | evri_py | plan-002 | `scripts/create_bundle.py` | 4 | 1 `plan-002`, 1 `plan-003`, 2 unlabeled bundler commits [23] | **WINDOW-CONTAMINATED** but content is still additive feature work, not redo |
| 13 | pybridge | plan-005 | `src/matlab/+pybridge/PyObject.m` | 3 | Issues 1.1→1.3→1.4, sequential same plan [24] | DECOMPOSITION |
| 14 | rc-files | plan-001 | `AGENTS.md` | 5 | 4 same-week plan-001 commits + **1 commit from 5 weeks later** (`9041f56`, an unrelated markdown-lint fix) [25] | **WINDOW-CONTAMINATED** |
| 15 | rc-files | plan-001 | `doctor.md` | 4 | same pattern as #14 | **WINDOW-CONTAMINATED** |
| 16 | rc-files | plan-003 | `.beads/interactions.jsonl` | 3 | bead-DB export, touched by every `bd` write | NORMAL (auto-generated export) |
| 17 | (corpus-wide) | — | `.beads/issues.jsonl` | appears in 14 different bundles | same reason as #16 | NORMAL |
| 18 | (corpus-wide) | — | `SPEC.md` | appears in 11 different bundles | SPEC-first mandate (yoshiko-flow's own AGENTS.md: "SPEC changes always happen first") | NORMAL (mandated) |
| 19 | (corpus-wide) | — | `SKILL.md` (any) | 34 file-instances corpus-wide | mix of #5's bulk-edit pattern and per-skill decomposition | mostly NORMAL/DECOMPOSITION |
| 20 | (corpus-wide) | — | `README.md` | 18 file-instances corpus-wide | typically a "keep the top-level doc in sync" trailing edit per Issue | NORMAL (hot doc) |

**Aggregate name-frequency check** (every repeatedly-touched file's basename, corpus-wide, from
the tool's own JSON [1]): the top 7 basenames — `SKILL.md` (34), `SPEC.md` (24), `README.md`
(18), `main.yml` (17, ansible role-default decomposition), `issues.jsonl` (14),
`interactions.jsonl` (7), `plan_manager.py` (6) — account for **120 of 233 (51.5%)** of all
repeatedly-touched-file instances, and every one of those seven is either a structurally
mandated hot file (SPEC.md, issues.jsonl, interactions.jsonl), a routinely-updated top-level
doc (README.md, SKILL.md), or a file under legitimate incremental feature decomposition
(main.yml, plan_manager.py) [26].

**Verdict ratio (n=20 hand-audited samples, weighted by the corpus-wide name-frequency check
above):** roughly **8 DECOMPOSITION, 7 NORMAL (hot file), 5 WINDOW-CONTAMINATED** (cross-plan
commits misattributed by window overlap) out of 20, and **zero classified as genuine intra-plan
THRASH** — the closest thing to a thrash-flavored file re-touch (`CHANGE-VALIDATION.md` in
plan-045, sample #8) is decomposition-plus-one-correction, not back-and-forth on the same
purpose. **The file-re-touch signal is dominated by ordinary development rhythm and a specific
tooling artifact (window contamination), not by thrash.** This matches the research plan's own
warning: "if most are hot files, the signal is mostly noise and you must say so" [research plan
§4] — say so: it is.

## 5. Timing shape

Within `plan-045`'s `CHANGE-VALIDATION.md` window (the one genuine correction case found),
commit timestamps are:

```
11:32:24  plan-045 Epic 1: close the validation blind spot
11:46:34  plan-045 Epic 2: the autonomy core            (+14 min)
11:53:16  plan-045 Epic 3: gates -- structure, sweep...   (+7 min)
12:00:36  plan-045 Epic 4: retrospective emit             (+7 min)
13:11:37  plan-045: make REQ-CLI-006 self-consistent...  (+71 min — the correction commit)
```

[27]. This is the one example in the entire retrieval where a burst (4 commits, 7–14 min
apart) is followed by a visible gap (71 min) before a self-correcting commit — consistent with
"discovery happened in the gap." **This is n=1.** I looked for the same shape around the other
4 tool-detected churn signals and did not find a comparably clean burst-gap-correction pattern
in any of them (the `d3-pxe` and `evri_py` hits are cross-plan corrections landing weeks apart,
not same-session bursts) [9][10]. **Honest conclusion: the corpus is underpowered to say
whether burst-then-gap-then-correction is a reliable timing shape** — one clean instance is
suggestive, not a pattern, and I did not attempt to fit this shape against the 233 file-retouch
list because §4 already established most of that list is not thrash to begin with.

## 6. Confounders

- **Squash-merge**: NOT used in this corpus. All 7 repos merge feature work with an explicit
  merge commit while preserving every intermediate Issue-numbered commit (e.g. yoshiko-flow has
  89 merge commits out of 697 total, and the `plan-NNN Issue X.Y: ...` commits are visible
  individually alongside each `Merge plan-NNN: ...` commit) [28]. This is *favorable* to git as
  a detector surface here, but it is a workflow property of this specific corpus, not a
  guarantee — a squash-merging team would destroy essentially all of the intra-branch churn this
  retrieval measured, including the one genuine correction case in §5.
- **Rebase**: not directly measured (would require comparing author-date vs commit-date
  divergence, which I did not do), but `.worktrees/<branch>/` mirrors exist in 3 of 7 repos
  (yoshiko-flow, d3-pxe, evri_py) per `artifacts/tooling-notes.md`'s corpus-correction note,
  meaning some plan work happens on isolated branches later merged in. If any of that work were
  rebased before merge, the linear timestamps this section relies on (§5) would not reflect the
  true authoring order — this is a real, unverified risk for any timing-shape claim, and is a
  further reason §5's single clean example should not be over-read. `[uncertain]`
- **Worktree branches / window construction**: this is the single largest confound this
  retrieval surfaced, and it is not hypothetical — §4 samples #6, #11, #14, #15 are all directly
  measured cases where `churn_signature.py`'s window (`[first commit, last commit]` touching a
  bundle or mentioning its plan id) silently absorbed commits belonging to a *different* plan or
  to unrelated later maintenance. 5 of 20 hand-audited samples (25%) were window-contaminated.
  Any downstream synthesis using `churn_signature.py`'s raw touch counts must discount for this;
  the tool reports every touching SHA, so a consumer *can* re-filter by grep-matching the
  commit's own subject for the specific plan id, but the shipped counts do not do this
  themselves.
- **Commit granularity is a style choice, not a difficulty measure**: every DECOMPOSITION
  verdict in §4 (samples #4, #7, #9, #10, #13) is an agent or operator choosing to commit once
  per Issue/Epic — a deliberate, repo-wide convention (`plan-NNN Issue X.Y: ...`), not a signal
  that the file was hard to get right. A team that batches five Issues into one commit would
  produce a *lower* re-touch count for identical underlying work, and a team that commits every
  file save would produce a much higher one. **File re-touch count is confounded with commit
  granularity by construction**, and this corpus's granularity is unusually fine (nearly one
  commit per sub-issue), which likely explains why 233 files clear the `>=3 touches` bar at all
  — a coarser-committing team might show near-zero re-touches for the identical amount of real
  iteration.
- **Task difficulty / missing tooling / context exhaustion / domain underdetermination**: none
  of the signals in this cluster distinguish these from thrash. A file legitimately touched 7
  times because it accretes one Ansible role's config across 7 sequential features (sample #9)
  is indistinguishable, by touch-count alone, from a file rewritten 7 times because the
  operator kept changing their mind — the *only* thing that discriminates the two in this
  retrieval is reading the commit subjects and bodies by hand, which is not a scalable detector
  input. **A signal that requires per-instance human judgment to separate decomposition from
  thrash is not, by itself, a usable detector — it is a candidate that still needs the review-
  pass-style human-verification step research 004 already established.**

## 7. Plain verdict

**Git carries a real but sparse and mostly-precision-limited thrash signal, and it is not
earlier or more reliable than the review-pass residue.**

- The commit-message pattern (widened or not) finds genuine, high-confidence signal at **very
  low recall** — 5 window-scoped hits corpus-wide (114 bundles), all 5 verified as true
  positives on inspection, but they are needles: **~0.4% of bundles**, and 3 of the 5 are
  cross-plan documentation corrections rather than within-plan thrash. Widening the pattern
  trades recall for precision catastrophically (163 hits, dominated by unrelated body-text
  matches for "wrong"/"incorrect").
- File re-touch is **dominated by ordinary development rhythm** (decomposition, mandated hot
  files, mechanical bulk edits) and by a **measured tooling artifact** — 25% of hand-audited
  samples were contaminated by a different plan's commits falling inside the window. Zero of
  20 hand-audited samples were genuine intra-plan thrash.
- The one clean burst-then-gap-then-correction timing shape found (§5) is a single data point,
  not a pattern; I could not replicate it against the other 4 tool-detected signals.
- git's ONE unambiguous "undo" class — hand-authored semantic reverts (§3) — exists (n=4) but
  occurs **outside every tracked plan-bundle window** in this corpus, meaning it is invisible to
  a plan-scoped detector by construction, not merely rare.

**On latency specifically**: where git *does* carry a genuine signal (the `18f3959` "third
drift" commit, §2/§5), the correction is a **residue that already happened** — the operator's
own commit message narrates that the drift occurred three times before the fix landed. Git
records that the fix eventually happened; it does not surface the drift any earlier than the
fix commit itself, and the fix commit is, definitionally, after the thrash is already over. Git
is not an early-warning surface for this corpus — it is, at best, a low-recall confirmation
surface for episodes that already resolved themselves, which is a strictly weaker position than
review-pass residue (research 005's `finding_recurrence.py`, per `artifacts/tooling-notes.md`,
already found 8 candidate episodes and 51 higher-confidence self-reported recurrence signals
from the same corpus using review-pass text alone [1] — an order of magnitude more usable signal
than git's 5, with earlier visibility, since a REVISE-verdict review pass records the concern
*before* the fix commit exists at all).
