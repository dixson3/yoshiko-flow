---
type: Finding
okf_spec: OKF-PLAN
id: exp-005-backfill-and-hygiene-skill
description: The backfill is mechanical but `okf migrate` gets it wrong — it introduces a hard audit failure on 30/30. And the corpus is 514 bundles across 41 repos, not ~100.
---

# Finding: Is the legacy `README.md` -> `index.md` backfill mechanical, and what should `yf-okf-hygiene` do?

### Approach Tested

Enumerated every bundle under `docs/plans/**` and `docs/research/**`; hashed all 30 legacy READMEs
with H1 + objective stripped to count boilerplate variants; read `okf.py`'s `migrate`/`reindex`/
`render_index`; ran `migrate` on **copies** of all 30 legacy bundles in two `mktemp -d` trees,
measuring `okf check`, `reindex --check`, `plan_manager audit`, `fingerprint check`, `doc_lint` and
phase-log count-equality before and after; simulated the correct backfill via `seed_index`; read
`yf-beads-hygiene` end to end; delegated a read-only cross-repo survey. Real repo untouched.

### Result

**measured:** — the 30 legacy READMEs are pure boilerplate: exactly TWO distinct variants. 22 files
hash `1fd228d7` (plan-009..030, with a `diagrams/` bullet), 8 hash `826c28a3` (plan-001..008,
without). Byte-identical below line 3. **Zero per-bundle authored prose.** The variance tracks
template evolution, not authorship. The union of paths named across all 30 File maps is 9 entries — a
**subset** of `_INDEX_MEMBERS`. The READMEs are strictly *thinner* than the current template.

**measured:** — the one real exception: line 3 (the objective blockquote) differs from `plan.md`'s H1
in **7 of 30** bundles. In plan-010/013 the README is *richer*. Regenerating from `plan.md` silently
discards a 23%-of-corpus difference.

**measured:** — `okf migrate` makes the plan audit STRICTLY WORSE. On all 30 legacy bundles: 324
changes; fingerprint **30/30 byte-identical**; phase-log count-equality **29/30**; but

| checker | after migrate |
| :-- | :-- |
| `okf check` | index-listing warnings on **30/30** |
| `reindex --check` | `drift` on **30/30** |
| `plan_manager audit` | a **NEW hard `fail`** on **30/30** |

The cause: `okf_missing_level` is `fail` when `okf_native` (= "plan.md has frontmatter"), and
`migrate` *adds* that frontmatter while leaving legacy prose in `index.md` — flipping `warn` to
`fail`. `reindex --write` does not repair it: it appends bare bullets **below** the retained "File
map" prose, with no descriptions and no `okf_version`, then reports `verdict: clean`.

**measured:** — plan-030 loses history. Its `log.md` already existed, so `migrate`'s
`if not (d/"log.md").exists()` skips `extract-log` entirely, stranding **10 bullets across 2 dates**
in `plan.md` while `log.md` keeps 1. The hybrid case is the only one here — and exactly the shape a
partially-migrated foreign corpus will have.

**measured:** — the CORRECT backfill is fully mechanical, end to end. `migrate` -> **delete** the
renamed index -> `seed_index`, on plan-020:

```
okf check    ok=True, 0 findings   (was ok=False, 9 errors)
reindex      clean                 (was drift, 6 findings)
plan audit   fail:1 warn:4         (was fail:1 warn:29 — the surviving fail is a
                                    pre-existing reviews/ count mismatch)
```

Indistinguishable from a born-OKF bundle. **So the backfill is three steps, not one, and step 2 is
what `okf migrate` gets wrong**: renaming README -> index.md is *worse than deleting it*, because it
manufactures a non-conformant reserved file that `reindex --write` cannot repair.

**measured:** — `plan_manager.py` exposes NO CLI verb that regenerates `index.md`. `seed_index` is
reachable only from `init`. The correct backfill is currently unreachable from any command line.

**measured:** — two advertised verbs do not exist. `SKILL.md` and the skill `description` advertise
`init | check | migrate | assess`; the parser offers `check, migrate, reindex, scaffold`. `assess` is
documented as exactly D-2's `audit`.

**measured:** — `doc_lint` does not motivate the backfill at all. Zero references to `index.md` or
`README` across all 17 schemas. So D-3's tension was stated on the wrong surface (see below).

**measured:** — CROSS-REPO REACH IS 5x THE SCOPING ESTIMATE: 514 bundles across 41 git repos.
yoshiko-flow holds only **61 (12%)**.

| | bundles | index.md | README-only | `_index.md` |
| :-- | --: | --: | --: | --: |
| byid/byid-obsidian | 268 | 0 | 24 | **227** |
| dixson3/yoshiko-flow | 61 | 30 | 30 | 1 |
| dixson3/d3-pxe | 21 | 14 | 5 | 2 |
| dixson3/writing | 17 | 0 | 11 | 4 |
| ~37 others | ~147 | 10 | ~64 | 9 |
| **TOTAL** | **514** | **54 (10.5%)** | **134 (26%)** | **243 (47%)** |

**`_index.md` is the DOMINANT legacy shape corpus-wide (47%), not `README.md` (26%).** A backfill
scoped to README-only handles a quarter of the problem.

**measured:** — root detection needs more than the four known roots. They miss a live modern bundle at
`d3-meetings/yf/meeting-pipeline/plans/plan-001-...`. Other roots found: `<repo>/plans/`,
`<repo>/research/`, `docs/archive/research/`. `.yf/research/` must be **excluded** (it holds
`preflight.json`). 50 bundle dirs live under `.worktrees/`, `.claude/worktrees/` or inside `.git/` —
real double-counting hazards.

### Implications for Plan

**D-2's "backfill" is not a rename**, and any plan step saying "run `yf-okf migrate`" is wrong.

**The D-3 tension partly dissolves and partly does not.** It *dissolves* where it was stated —
`doc_lint` has no index/README check, so "complete -> report-only" is not the rule the backfill
violates. It *does not* dissolve on the real surface: `_audit_plan`'s `okf_missing_level` and
`okf check`'s REQ-OKF-001/002 both judge completed bundles, and their grandfather is `okf_native`,
not status. Backfill flips that bit, **so a half-done backfill is worse than none.**

**The strongest reconciliation is measured, not rhetorical: the backfill is provably
content-preserving** — 30/30 fingerprints byte-identical, 29/30 log count-equality, index prose
demonstrably two variants of boilerplate. "History is not re-judged" bars *changing a verdict on
frozen content*; this changes no content the verdict is computed over. The honest residue is the 7/30
objective lines and plan-030's 10 stranded bullets — both handleable, not acceptable losses.

### Recommendations

1. **`yf-okf-hygiene` absorbs the unimplemented `assess`** rather than adding a fourth name.
2. **Verb set** mirroring `beads_hygiene.py`: `audit` (read-only, classifies into `conformant |
   legacy-readme | legacy-underscore-index | hybrid-partial | unclassifiable`; exit 0/1/2) ·
   `backfill [--apply] [--yes] [--record]` (the three-step transform) · `reindex` (drift repair, and
   it must **refuse** on a legacy prose index — that is backfill's job) · `restore --record`.
3. **Hard preconditions on `backfill`, fail-closed:** fingerprint before == after (assert, don't
   assume), phase-log bullet *and* distinct-date equality (catches plan-030), clean git tree unless
   `--allow-dirty`. On objective divergence, **halt and require `--objective plan|readme`** rather
   than picking silently.
4. **Route by detected member, not by filename** — `_index.md` is 47% of the corpus.
5. **Root detection is a config-driven glob list**, not four hard-coded paths, with hard exclusions
   for `.git/**`, `.worktrees/**`, `.claude/worktrees/**`, `.yf/**`, and archives behind
   `--include-archives`. Repo attribution by nearest-ancestor `.git`.
6. **Ship `--record`, and implement `restore` as `git checkout` DRIVEN BY the record** — the record
   supplies *scope*, git supplies *content*. Git alone is byte-exact but has no cross-repo
   enumeration; a manifest alone is a second source of truth. This gets both.
7. **Tests** (`test_okf_hygiene.py`), each traceable to a measurement: two-variant equivalence; the
   **plan-030 hybrid** case named for the incident; fingerprint invariance asserted; `reindex` refuses
   on legacy prose; objective divergence halts; root detection finds `yf/<slug>/plans/` and skips
   `.worktrees/`/`.yf/`; `audit` never writes (assert mtimes).
8. **Two upstream beads, defects in shipped code rather than gaps this skill fills:** `okf migrate`'s
   hybrid-bundle log loss, and the missing `assess`/`init` verbs both `SKILL.md` and the skill
   `description` advertise.
