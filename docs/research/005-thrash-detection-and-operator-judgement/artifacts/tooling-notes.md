---
type: Research Artifact
description: Measured structural variance in reviews/pass-N.md across the 7-repo corpus,
  gathered before writing the thrash-episode extractor tooling
okf_spec: OKF-RESEARCH
---

# Tooling notes — measured review-pass format variance

Gathered 2026-08-28 by direct inspection of `reviews/pass-N.md` files, at least 3 per repo,
spanning all 7 corpus repos including two non-software ones (`emacs.d`, `rc-files`). This is
the empirical basis for `scripts/finding_recurrence.py`'s parser — every claim below is a
direct observation of a cited file, not an assumption.

## Corpus census (confirmed exactly matches plan.yaml)

```
find <repo> \( -path '*/docs/plans/*' -o -path '*/Incubator/*/plans/*' \) -path '*/reviews/pass-*.md'
```

| repo | pass files found |
|:--|--:|
| yoshiko-flow | 170 |
| d3-pxe | 146 |
| evri_py | 26 |
| writing | 18 |
| pybridge | 20 |
| emacs.d | 4 |
| rc-files | 7 |
| **total** | **391** |

Matches plan.yaml's `totals.review_passes: 391` exactly — no surprise here, no missing repos.

## Frontmatter: present in 137/251 sampled (roughly half), NOT universal

`head -1 | grep '^---$'` over `docs/plans/**/reviews/pass-*.md` (a partial early sample, before
Incubator paths were added to the census) found 114/251 files with **no** YAML frontmatter at
all. Frontmatter presence correlates with repo/era, not with anything semantic:

- yoshiko-flow (current-era, e.g. `docs/plans/plan-053-james-dixson-4015d3/reviews/pass-4.md`)
  and d3-pxe (`docs/plans/plan-016-james-dixson-533fa8/reviews/pass-1.md`) mostly carry
  `---\ntype: Review\nokf_spec: OKF-PLAN\n...\n---` frontmatter (yoshiko-flow adds `id`/
  `description`; d3-pxe uses a bare `pass: N` key instead).
- writing (`docs/plans/plan-001-james-dixson-d51200/reviews/pass-1.md`), pybridge
  (`docs/plans/plan-003-james-dixson-e55a84/reviews/pass-2.md`), emacs.d
  (`docs/plans/plan-002-james-dixson-b23020/reviews/pass-1.md`) and rc-files
  (`docs/plans/plan-001-james-dixson-a7213c/reviews/pass-1.md`) carry **no frontmatter** —
  the review starts directly with an `# H1` title.

**Consequence for the parser:** frontmatter cannot be relied on for `pass` number or verdict;
both must be recoverable from the body. `pass` is always recoverable from the **filename**
(`pass-N.md`), which is 100% reliable across all 391 files — use that, not frontmatter, as the
primary pass-number source.

## Title line: two conventions, always contains the pass number redundantly

- `# Red-team pass 4` (yoshiko-flow plan-053/pass-4.md, plain — no plan id in title since the
  bundle dir already carries it)
- `# Red-team pass 1 — plan-016-james-dixson-533fa8` (d3-pxe, title carries plan id)
- `# Review Pass 1 — plan-001-james-dixson-d51200` (writing, pybridge — "Review Pass" not
  "Red-team pass")
- `# Plan Red-Team: plan-002-james-dixson-b23020 — pass 1` (emacs.d — colon form, pass number
  at the END of the title, not the start)
- `# Red-Team Review — pass 4` (evri_py plan-008/pass-4.md — yet another word order)

**Consequence:** do not regex-anchor on title wording; extract pass number from the filename
only, and treat the title line as free text / unused for structure.

## Verdict: two vocabularies observed, one dominant

Corpus-wide grep of `Verdict:` lines across all 391 files (docs/plans scope, 251 of 391 —
Incubator-scoped files not separately re-checked for this specific count but spot-checked
consistent): **190 REVISE, 80 APPROVE**, zero REJECT/BLOCK/CONDITIONAL observed in this sample.
Verdict line placement varies:

- Its own `## Verdict: REVISE` heading (yoshiko-flow, evri_py)
- A bold inline field in a metadata block: `**Verdict:** REVISE` (writing, d3-pxe, pybridge,
  rc-files, emacs.d)
- d3-pxe additionally repeats it as a **bold list item** near the top (`- **Verdict:**
  **REVISE**`) in addition to the `## Verdict: REVISE` heading — i.e. some files state the
  verdict twice, once in a metadata list and once as a heading. Do not assume exactly one match.

## Finding-id grammar: NOT one convention — at least 4 distinct shapes

Corpus-wide token scan for `[A-Z]{1,3}[0-9]{1,3}` finding-like ids found in concern text, by
frequency of the letter-prefix: `C` (2865), `SC` (1542 — mostly "success criterion" refs, not
finding ids), `M`, `R`, `N`, `D`, `H`, `P`, `L`, `F`, `E`, `G`, `ML`, `S`, `NC`, `NEW`, `J`, `I`,
`X`, `CG`. The finding-id-specific prefixes actually observed heading a concern row/bullet:

1. **Table row, `C##` id column** (yoshiko-flow plan-053/pass-4.md): a `| # | Severity |
   Concern |` markdown table, `C44`, `C45`, ... — ids are **plan-cumulative**, not reset per
   pass (pass-4's ids continue from C30 as established in pass-3, confirmed by the file's own
   "Reproduction of pass-3's 14 resolutions" section naming C30/C34/C35/... as prior-pass ids
   discussed again in the current pass — this is a DIRECT, explicit, self-reported recurrence
   signal, stronger than any fingerprint match).
2. **Table row, same `C##` shape** (d3-pxe plan-016/pass-1.md) plus a **prose elaboration**
   per id below the table (`### C1 (HIGH) — per-dataset floors vs. one invocation`) — so the
   same finding appears TWICE in one file: once as a one-line table cell, once as a full prose
   block. A naive per-line fingerprinter would double-count this as 2 findings.
3. **Numbered markdown list, no letter prefix** (writing plan-001/pass-1.md): `1. **[HIGH]
   "Copy, never move" asserted...**` — severity is inline in `[HIGH]` brackets, not a table
   column, and there is no `C1`-style id at all; only the ordinal number, which is NOT stable
   across passes (a pass-2 renumbers from 1 again even for unrelated concerns).
4. **Unlabeled prose bullet with trailing `severity: X`** (emacs.d plan-002/pass-1.md): `- **Two-
   function coexistence...** — severity: medium` — no id token whatsoever; the fingerprint MUST
   be derived from the finding text itself, there is no id to key on.
5. **`C##` prose bullet, freeform (not a table)** (rc-files plan-001/pass-1.md): `- **C1 (HIGH)
   — subprocess-isolation model may not fit `update`'s stateful sequence.**` — has a `C##` id
   AND severity in the same line, but as a bullet, not a table row.
6. **evri_py's `NC#` prefix** (plan-008/pass-4.md): "new concern" ids that are distinct from
   `C##`, apparently used when a pass wants to mark a concern as new-in-this-pass vs. carried.

**Consequence for the extractor:** finding-id tokens (`C\d+`, `NC\d+`, etc.) are a **useful but
optional hint**, never the sole join key — plenty of reviews carry no id at all (writing's
ordinals, emacs.d's unlabeled bullets), and ordinal numbers are not stable across passes. The
extractor's primary signal must be **text-shingle similarity of the finding body**, with any
recovered id treated as bonus corroborating evidence, never as ground truth.

## Explicit self-reported recurrence: a distinct, higher-confidence signal

yoshiko-flow's pass-4 (plan-053) contains an explicit **cross-pass reproduction table** —
`## Reproduction of pass-3's 14 resolutions — 7 of 14 (50%)`, classifying each of pass-3's ids
into (a) landed and correct, (b) recorded but absent, (c) landed at one site defect survives,
(d) itself a new defect. This is the review author DOING the cross-pass comparison by hand and
writing down the result. pybridge's pass-2 does the same thing in prose form ("All ten pass-1
concerns (C1–C6, M1–M3, G1, U1) verified genuinely resolved..."). evri_py's pass-4 is a clean
`APPROVE` after fixing pass-3's single carried concern.

**Consequence:** the extractor should have a distinct, higher-weight code path that looks for
these self-reported reproduction/verification sections (regex on headings like `Reproduction
of pass-\d+`, `Pass-\d+ resolution verification`, or prose like "verified genuinely resolved")
and surfaces them as **corroborated** episodes — separate from the text-similarity fingerprint
match, which is a weaker, human-unverified signal and must be reported with its similarity
score so a human can judge.

## Resolutions section: present in most files, absent in a few "still open" reviews

Most passes end with an `## Operator Resolutions` / `## Resolutions` table or prose block
mapping each concern to a `resolved` (or other) status and an actor. This is present in every
sampled file that had a resolvable REVISE verdict; it is the natural place to look for
resolution text when checking whether a later pass's recurrence is a genuine re-open vs. the
resolution simply being incomplete (as in yoshiko-flow pass-4's own finding: "found and fixed on
the verification run, not on the first edit").

## Corpus surprise: git worktrees double-count under a naive `find`

`yoshiko-flow`, `d3-pxe`, and `evri_py` each keep a `.worktrees/<branch>/` directory (used by
the plan-execution machinery to run a plan in an isolated checkout) that MIRRORS the entire
`docs/plans/` and `Incubator/*/plans/` tree for whatever branch is checked out there. A plain
`find <repo> -path '*/reviews/pass-*.md'` therefore double-counts every pass file that also
exists in an active worktree — this is almost certainly why plan.yaml's corpus table
(127 plans / 391 review passes, "measured 2026-08-28") is inflated relative to a scan that
walks only `<repo>/docs/plans` and `<repo>/Incubator/*/plans` directly. `corpus_scan.py`
deliberately does the latter (it enumerates `docs/plans` and `Incubator/*/plans` under each
repo root and never descends into `.worktrees`), and measures, on the same date:

| | plan.yaml (naive find, inflated) | corpus_scan.py (worktree-excluded) |
|:--|--:|--:|
| bundles | 127 | **114** |
| review passes | 391 | **301** |

d3-pxe alone accounts for most of the gap: its `.worktrees/plan-019-.../` checkout duplicates
73 of its 146 naive-count pass files, so its real count is 73, not 146. evri_py's worktree
duplicates roughly half its files too (13 real vs. 26 naive). The corrected 114/301 figures
should be treated as authoritative going forward for this study — cite `corpus_scan.py`'s
output, not plan.yaml's `corpus:` block, when a downstream phase needs the bundle/pass counts.

A second, smaller false-positive source in a naive `find`: yoshiko-flow's
`docs/plans/plan-029-james-dixson-75fd34/findings/okf-migration-samples/plan-bundle/{before,after}/reviews/pass-*.md`
are OKF-migration FIXTURE documents (synthetic before/after samples for testing the migration
tool), not real reviews. `corpus_scan.py` excludes these too, structurally — it only treats a
directory as a bundle if it is a direct child of `docs/plans/` or `Incubator/*/plans/`.

## Additional finding-id grammar variants found during extractor validation

Two more shapes surfaced only when running the parser against the full corpus (not the initial
7-file sample) and are recorded here for whoever revisits this parser:

- **Hyphenated/prefixed ids**: `RT-C1`, `RT-M1`, `CONF-1`, `CONF-2`
  (`docs/plans/plan-021-james-dixson-bb3558/reviews/pass-1.md`) — a table with `| ID | Severity
  | Concern | Resolution | Status |` columns whose id values carry a category prefix before
  the hyphen. The original `[A-Z]{1,3}\d{1,3}` id grammar didn't match these at all (zero
  findings extracted, a silent gap) until broadened to also accept `[A-Z]{2,6}-[A-Z]{0,3}\d{1,3}`.
- **Letter-only paragraph findings, no bullet marker**: `**A. [MEDIUM] title.** prose...`
  (`docs/plans/plan-018-james-dixson-1d39eb/reviews/pass-2.md`, concerns A–E) — a bare
  bold-lettered paragraph directly under `## Concerns`, not a `-`/`*` bullet and not a table
  row. This shape is a KNOWN, DOCUMENTED GAP in `finding_recurrence.py` as shipped — it is not
  handled, and files using it report `no findings extracted by any shape` in
  `parse_warnings`. Fixing it (paragraph-boundary splitting keyed on `**[A-Z]\.` at the start of
  a blank-line-delimited block) is a reasonable next increment if this bundle's findings turn
  out to matter to a later phase; flagged rather than silently patched over given the
  conservative-fingerprinting mandate.
- **Verdict label wording**: `**Red-team verdict:** REVISE → all concerns resolved...`
  (same file) — neither the exact label text (`Verdict:` vs `Red-team verdict:`) nor a
  hard end-of-line anchor after the verdict word can be assumed; some files trail the verdict
  value with more prose on the same line. The verdict regexes were broadened to a
  non-anchored, wording-tolerant match for this reason.

## Practical parsing decisions this drove

- Pass number: from filename only.
- Verdict: search body for the FIRST of (`## Verdict: WORD`, `**Verdict:** WORD` /
  `**Verdict:** **WORD**` on its own line or in a metadata block); do not require exactly one
  match, take the first and record if more were seen.
- Findings: extract three candidate shapes and let the caller inspect all three
  independently — (1) table rows with a leading `id` cell matching `[A-Z]{1,3}\d+`, (2) `##`/`###`
  prose subsections keyed by the same id grammar, (3) top-level `-`/`*`/`\d+.` bullets in a
  `## Concerns` section, whether or not they carry an id. Every extracted finding keeps a
  `(file, line)` pointer into the source pass file — never store text without it.
- Fingerprint: normalized-token shingle set (lowercase, strip markdown emphasis/punctuation,
  drop stopwords) over the finding's first ~40 words (the "headline"), NOT the full remediation
  prose — remediation prose describes the FIX and will spuriously match unrelated findings that
  happen to fix similarly ("added an explicit check", "verified: 0 occurrences").
- Table parsing locates the id/concern/severity columns by HEADER NAME, not fixed position —
  column order varies even within one repo (`plan-053`: `# | Severity | Concern`; `plan-019`:
  `# | Concern | Severity | Status | Resolution`). An early fixed-position implementation
  mistook the Severity column for the finding text on ~700 rows before this was caught; see
  "measured validation numbers" below.
- id-reuse across passes is NOT reliable evidence of recurrence on its own: some plans (e.g.
  `plan-026-james-dixson-6e0e2f`) reassign `C1`/`C2`/`C3` to unrelated NEW concerns on every
  pass rather than carrying an id forward. The extractor requires an id-reuse match to ALSO
  clear a low text-similarity floor (`--id-floor`, default 0.15) before counting it as a
  candidate episode; below that floor it is reported separately as `weak_id_reuse_matches`,
  never silently folded into the headline count.

## Measured validation numbers (full 7-repo corpus, 2026-08-28)

`corpus_scan.py --json` (authoritative corrected census, see the worktree-duplication note
above):

- **114 bundles**, **301 review passes**, 7/7 repos scanned OK, 0 missing/broken.

`finding_recurrence.py --census <census> --threshold 0.35 --id-floor 0.15 --json`:

- 79 bundles had >= 2 review passes (35 single-pass bundles skipped — no cross-pass recurrence
  is possible with one pass).
- **1509 findings extracted** across those 79 bundles' 301-minus-single-pass review files.
- **85 parse warnings** (66 "no findings extracted by any shape" — mostly genuine `APPROVE`
  passes with an empty Concerns section, some the letter-paragraph gap above; 18 "no `##
  Concerns` section"; 14 "no verdict found").
- **8 candidate thrash episodes** at threshold 0.35 / id-floor 0.15 — e.g.
  `plan-047-james-dixson-dec9ff` pass 3→4, "SC20's count wrong three ways again" recurring
  near-verbatim; `plan-010-james-dixson-e049e3` pass 1→2, "No READY gate on `[needs-source]`"
  recurring as "`[needs-source]` gate recall". Every episode is emitted with both findings'
  `(file, line)` pointers and its similarity score.
- **252 weak id-reuse matches** (same id token, similarity below the floor — i.e. coincidental
  id reuse, not recurrence) — reported separately, not counted as episodes.
- **51 self-reported cross-pass signals** — passes that explicitly state their own
  reproduction/verification of a prior pass's resolutions in prose (yoshiko-flow's
  "Reproduction of pass-N's resolutions" tables, pybridge's "N of M concerns verified genuinely
  resolved" prose). This is the highest-confidence recurrence signal in the corpus because a
  human reviewer already did the cross-pass comparison; it should be weighted above the
  text-similarity matches in any downstream synthesis.

`churn_signature.py --census <census> --json`:

- **114/114 bundles processed**, 0 errors.
- **5 churn-signal commits** matched a revert/redo commit-message pattern (all `actually` or
  `correct ... in place`; no literal `git revert` commits found in this corpus).
- **233 repeatedly-touched files** (>= 3 distinct commits touching one non-bundle file within a
  plan's commit window) across 53 bundles (61 bundles had none). Two outliers
  (`plan-010-james-dixson-73eebd`: 37 files; `plan-054-james-dixson-535968`: 36 files) are
  large, long-running implementation plans (25 and 47 commits in-window respectively) — checked
  and not a grep false-positive, both plans have proportionally large commit windows.
