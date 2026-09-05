---
type: Finding
okf_spec: OKF-PLAN
description: 'EXP-003 - whether the 3 per-skill OKF-EXTENSION.md files need DRIFT-CHECK.md nodes, and whether that work belongs in this plan. Verdict - route it to 247 and take a 2-line slice here.'
---
# EXP-003: OKF-EXTENSION.md drift nodes — measure before deciding

**Question (from #316 scope item 4):** per-skill `OKF-EXTENSION.md` files "carry no node in
`DRIFT-CHECK.md` §1 at all and nothing checks them against their skill's behavior; decide in
scoping whether that belongs here or in the drift-manifest work."

**Verdict: route the node work to #247. Take only the 2-line CHANGE-VALIDATION slice here.**

## Approach Tested

**measured:** Read-only audit of the repository at HEAD, plus one throwaway identifier/path-resolution
probe run from the scratchpad and deleted. Steps: enumerate `OKF-EXTENSION.md`; grep `DRIFT-CHECK.md`
and `CHANGE-VALIDATION.md` for coverage; read `_shared/okf.py`'s `parse_extension` /
`resolve_extension` to establish what the files actually are; execute `resolve_extension()` on all
three and dump the parsed ruleset; probe every backticked code identifier and repository path in each
file against its named implementation; `git log` / `git log -S` for historical drift; and
`gh issue list --search`, `bd list`, and a grep of the plan corpus for a recorded deferral.

**inferred:** executing the parser rather than reading the documents is what exposed the two
document-vs-parser disagreements; neither is visible from the prose.

Residue: none. `git status --porcelain` empty afterward.

## Result

### The premise is directionally right but materially overstated

| #316 claim | Measured |
| :-- | :-- |
| "no node in `DRIFT-CHECK.md` §1 at all" | **True, 3/3.** `grep -i extension DRIFT-CHECK.md` returns nothing — the substring does not appear. All 48 §1 node globs read; nearest are `skills/*/spec/*.md` and `skills/*/SPEC.md`. `OKF-EXTENSION.md` sits at the **skill root** — unglobbed by both. |
| "nothing checks them against their skill's behavior" | **False for `yf-plan`.** `CHANGE-VALIDATION.md:268` wires it to `okf-index-drift` + `uv-okf`, and `_shared/test_okf.py` asserts against the real file twice (`resolve_extension("yf-plan")`, and a `>= 2` §3b glob count). Wired into **both** FAST and FULL. **True for `yf-research` and `yf-incubator`** — no trigger row anywhere, no test reads them. |

**Restate as: 0/3 noded · 1/3 behaviorally covered · 2/3 uncovered on every axis.** A plan that
repeats #316's wording verbatim loses a red-team exchange over `CHANGE-VALIDATION.md:268` for no
gain.

### These files are configuration, not prose

`_shared/okf.py:659` `parse_extension()` machine-reads seven sections by heading substring and
table column: `member`, `bundle_form`, `type_vocab`, `required_keys`, `reserved_subdirs`,
`exclude_globs`, `type_map`/`index_source`/`log_source`/`field_labels`. Every one of the three
makes checkable claims; none is narrative.

Executing `resolve_extension()` on all three surfaced two live parser/document disagreements:

- **`yf-plan bundle_form: both`** contradicts its own §0 (`**dir-form**` … `never single-file`).
  The parser is a naive substring test (`okf.py:670`), so the phrase *"never single-file"* flips
  the value to its opposite. Harmless **today** only because the field is consumed by nothing —
  the same vacuity plan-056 measured for `reserved_subdirs`.
- **`yf-research field_labels: ['research_project','research_project','phase','date']`** — a
  duplicate entry and four values that are none of the frontmatter keys §4 declares. The parser
  harvests the wrong column.

### What a node would catch: not zero, but modest

Real, live, ~48-day-old drift:

- **All three still carry plan-029 `Status: DRAFT … Proposal only`** banners while plan-029 is
  `status: complete` and the engine ships them in production.
- **Two dangling symbols.** `yf-research` cites `HEADER_TEMPLATE`; it is gone from
  `index_manager.py` entirely. `yf-plan` cites `seed_readme`; the function is `seed_index`
  (`plan_manager.py:1168`). Probe totals: yf-plan 12 claims/1 unresolved · yf-research 7/1 ·
  yf-incubator 5/0.
- **Two shipped decisions still posed as open.** `yf-research` §5 calls the `index.md` table-vs-
  bullet question a "decision to lock in Issue 4.1" — `INDEX_FILENAME = "index.md"` and all 5
  research bundles already have it.

**The drift shipped in its own birth commit.** `HEADER_TEMPLATE` was deleted from
`index_manager.py` in `aaf2b6c`, *the same commit that created the extension file citing it*.
It then survived **plan-054's full 52-edge drift sweep** — the one that produced #247 — because
no node covers it, so the sweep could not look.

**Counter-evidence on value:** the last week produced #319/#320/#321 (two P0, one P1), all
located *inside* an `OKF-EXTENSION.md`, all found by manual audit. A cheap `cross-ref`/`contract`
edge would have caught the **stale-symbol/stale-status** class (2 confirmed) and almost certainly
**not** those three, which are engine-semantics defects. This is an instrument for documentation
hygiene, not for the P0 class.

### Cost: the rows are trivial; the tail is not

The manifest edit is **6 lines added + 1 amended in `DRIFT-CHECK.md`, 2 lines in
`CHANGE-VALIDATION.md`** — one `okf-extension` §1 node, two edges (`e-okf-extension-parse`
contract, `e-okf-extension-symbols` cross-ref), their §3 contract rows, a §6 trigger row. No
diagram cost.

**The cost is the FAIL those rows produce on day one:** 2 dangling symbols, 3 false DRAFT
banners, 2 shipped-but-"open" decisions, 2 mis-parsed fields. Fixing that is documentation
correctness across 3 files — and the `bundle_form`/`reserved_subdirs` vacuity is a **SPEC
question**, so by this repo's SPEC-first rule a `skills/yf-okf/SPEC.md` amendment lands *ahead*
of it, pulling in the 6 `okf.py` copies. That is an epic-sized tail hanging off a one-line row.

### Why not here

1. **Disjoint subject matter.** This plan transforms 8 legacy **bundles** under `docs/plans/`
   with a journaled, reversible engine run. `OKF-EXTENSION.md` files are engine **configuration**
   under `skills/`; the backfill neither reads them at bundle scope nor rewrites them. Sharing
   the word "OKF" is the whole of the overlap.
2. **A live-fire hazard.** #318 (`--skill` before the subcommand silently dropped — data loss),
   #320 and #321 are open P0/P1s **in the `--skill` / member-resolution path this backfill
   exercises**. Editing the member files mid-backfill changes the inputs to an engine with three
   open severity-1 defects in exactly that path.
3. **#247 is the correct home and is already open** — titled "Drift findings no edge covers",
   its item 1 is a manifest-completeness gap of identical shape, with a `**Suggested edge:**`
   already drafted. Same file, same class, same reviewer.

### Adjacent gap found while measuring (not in #316)

A **fifth** vendored `okf.py` exists with no node and no edge: `skills/yf-okf-hygiene/scripts/
okf.py`. §1 declares four `okf-copy-*` nodes; there are five copies. All six files are
byte-identical today (`md5 -q` agree), so it is an uncovered copy that *happens* to be in sync.
Belongs with #247 in the same pass.

### Was it deliberate?

**No — an unfinished commitment.** 0 beads and 0 issues propose or defer it. plan-029's
`reviews/pass-4.md:17-19` records the design intent: the `.md` docs "kept in agreement by a
`yf-drift-check` edge". What landed is `e-okf-version-pin`, which pins the **version string
only**, on `OKF-BASELINE.md` only. The omission is structurally accidental: both
`skills/*/spec/*.md` and `skills/*/SPEC.md` are noded; only the root-located spec-family file is
unglobbed.

### Recommendations taken into this plan

| # | Recommendation | Disposition |
| :-- | :-- | :-- |
| 1 | Do not make the node work an epic here; route to #247 with the literal rows + the fifth-copy gap. | **Accepted** → Epic 5 |
| 2 | Correct #316's premise in plan text; close scope item 4 with a recorded "routed to #247", never silence. | **Accepted** → Epic 5 |
| 3 | Take the 2 `CHANGE-VALIDATION.md` §3 rows for `yf-research`/`yf-incubator` here — 2 lines, closes the real 2/3 gap, produces no red run. | **Accepted** → Epic 5 |
| 4 | File a follow-on bead for the documentation remediation (DRAFT banners, dead symbols, shipped-as-open decisions), linked to #247. | **Accepted** → Epic 5 |

## Implications for Plan

1. **#316's premise as written will not survive a red-team pass.** If the plan restates "nothing
   checks them" verbatim, a reviewer produces `CHANGE-VALIDATION.md:268` and the plan loses
   credibility on a scope item it did not need to overstate.
2. **The manifest edit is ~8 lines and would fit anywhere. The remediation is what does not fit.**
   Adding the edges turns them red on day one, and the `bundle_form` / `reserved_subdirs` vacuity is a
   SPEC question — so a `skills/yf-okf/SPEC.md` amendment lands first, pulling in the `okf.py` copies.
   That is an epic-sized tail hanging off a one-line node row.
3. **The subject matter is genuinely disjoint from this plan's deliverable** — bundles under
   `docs/plans/` versus engine configuration under `skills/`. Sharing the word "OKF" is the whole of
   the overlap.
4. **There is a real live-fire hazard in doing it here.** #318, #320 and #321 are open P0/P1s in the
   `--skill` / member-resolution path the backfill exercises. Editing the member files mid-repair
   changes the inputs to an engine with three open severity-1 defects in exactly that path.
5. **#247 is the correct home and it is already open**, with a `**Suggested edge:**` of the identical
   shape already drafted in its body.

## Recommendations

1. **Do not make the node work an epic here.** Route it to #247 with the literal §1/§2/§3/§6 rows,
   and let #247 absorb the fifth-copy (`skills/yf-okf-hygiene/scripts/okf.py`) gap in the same pass.
2. **Correct the premise in the plan text**, and close #316 scope item 4 with an explicit, recorded
   "routed to #247" — a scope item that simply disappears is indistinguishable from one forgotten.
3. **Do take two things, because they are two lines and genuinely in scope.** Add the `yf-research`
   and `yf-incubator` `CHANGE-VALIDATION.md` §3 rows: they close the 2/3 behavioral-coverage gap #316
   actually identified, cost 2 lines in a file the plan already edits, and produce no red run.
4. **File one follow-on bead** for the documentation remediation — 3 stale `Status: DRAFT` banners, 2
   deleted symbols (`HEADER_TEMPLATE`, `seed_readme`), 2 shipped decisions posed as open — so the
   finding survives whichever plan does not take the work. Link it to #247.
5. **If the plan owner overrules and keeps it here, sequence it last** and scope it to the manifest
   rows plus the stale-banner/stale-symbol fixes only, explicitly deferring the SPEC question where
   the size actually lives.
