---
type: Finding
okf_spec: OKF-PLAN
id: exp-003-reindex-and-corpus-backfill
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
---

# exp-003 — Is a generated nested-`index.md` backfill mechanically sound?

**Question:** Is a generated nested-`index.md` backfill across the existing corpus sound, and what should the `reindex` verb be?
**Method:** enumerated the corpus with `find`/`git log`; parsed frontmatter and H1s of all 423 nested `.md`; read OKF v0.2 §3.1/§8/§9, `_shared/okf.py`, `plan_manager.py`'s `audit`/`audit-close`, and `bp/okf-lint` plus its delegated generator; ran `okf.py check` over all 50 bundles; ran `markdown_lint.py --rules ML003` over every root index; prototyped generation on 7 real directories; exercised `render_index`/`add_index_entry` against a nested dir. Repo untouched; all prototyping in scratch.

## Verdict

> **The backfill half of D-3 does not survive contact with the corpus.** Build `reindex` — but point it at the **root** indexes, where real, measurable drift already exists. Do not generate nested `index.md`. Do not build nested `log.md` at all.

The *ordering principle* in D-3 ("green before enforcement") is right. Only the **tier** is wrong.

## 1. Corpus shape

```
plan bundles: 46   research bundles: 4   Incubator/: does not exist
```

**142 nested subdirectories, 457 files.** Bundles carrying each kind:

```
46 reviews   34 findings   33 references   13 diagrams   7 assets   4 scripts   4 artifacts   1 decisions
```

File-count histogram (`filecount → #subdirs`):

```
0→15   1→30   2→41   3→22   4→10   5→6   6→5   7→4   8→1  10→1  11→1  12→2  15→1  18→1  30→1  35→1
```

- **45/142 (32%) hold ≤1 file** — 15 empty, 30 single-file. An `index.md` in a one-file directory is longer than the thing it indexes.
- **86/142 (61%) hold ≤2 files.**
- Only **24/142 (17%)** hold ≥5, and they are concentrated: `plan-038/references` (35), `plan-037/references` (30), `plan-040/references` (18), `plan-039/references` (15).
- `assets/` is 7 dirs / **1 file total**; `diagrams/` is 13 dirs / 15 files with 6 empty; `scripts/` is 4 dirs / 3 files.

**Zero nested `index.md` corpus-wide — the issue's claim CONFIRMED.** The only four are plan-029 test fixtures; same for nested `log.md`. Root level: 19 `index.md`, 20 `log.md` across 50 bundles.

## 2. The index-entry input is ABSENT — the central finding

OKF v0.2 §8, verbatim (`references/okf-spec-v0.2.md:515`):

> An `index.md` file **MAY** appear in any directory, including the bundle root. […] Index files contain **no frontmatter**, with one exception: a bundle-root `index.md` MAY carry an `okf_version` key (§12). […] Entries **SHOULD include the description from the linked concept's frontmatter**.

Measured over all 423 nested `.md`:

```
with frontmatter:            246/423 (58.2%)
  with 'description':          0/423 (0.0%)
  with 'title':                0/423 (0.0%)
  with 'type':               246/423 (58.2%)
```

Every frontmatter key that exists anywhere in the corpus:

```
type 246, okf_spec 246, plan 48, id 46, created 45, status 20, verdict 18,
research 4, pass 3, phase 3, produced 3, produced_in 2, retrieved 2,
cluster 2, date 1, source 1, okf_version 1, method 1
```

> **The gap is not 70% — it is 100%.** A generated backfill has literally no source for the field §8 says an entry SHOULD carry.

Fallbacks measured: H1 present **411/423 (97.2%)**; a synthesizable first-paragraph description **43/423 (10.2%)**; H1 *informative beyond the filename* (≥3 novel tokens):

```
findings      98/108 (91%)
references   179/186 (96%)
reviews       39/103 (38%)
artifacts      4/ 25 (16%)
TOTAL        321/423 (76%)
```

## 3. Prototype output, verbatim

`plan-044/findings/` — **useful**:

```markdown
# findings

* [exp-001 — The YOSHIKO_FLOW.md rules-aggregate write path (#154, #156)](exp-001-rules-aggregate-write-path.md) - *description pending*
* [exp-002 — The Dolt-remote / local-only two-layer model (#159, #160)](exp-002-dolt-remote-local-only.md) - *description pending*
* [exp-007 — The #160 init-ordering hypothesis: CONFIRMED](exp-007-160-init-ordering-probe.md) - *description pending*
```

`plan-045/reviews/` — **worthless**:

```markdown
# reviews

* [Red-Team Pass 1 — plan-045-james-dixson-9899e1](pass-1.md) - *description pending*
* [Red-Team Pass 2 — plan-045-james-dixson-9899e1](pass-2.md) - *description pending*
```

Degenerate cases:

```markdown
# assets            ← plan-046/assets/: a heading, nothing else

# diagrams          ← research/004/diagrams/
* [defect-class-taxonomy.d2](defect-class-taxonomy.d2) - *description pending*
* [defect-class-taxonomy.png](defect-class-taxonomy.png) - *description pending*
```

**By directory count: `reviews/` (46) + `diagrams/` (13) + `assets/` (7) + `scripts/` (4) + `artifacts/` (4) = 74 of 142 (52%) low-or-zero value**, versus 67 (47%) with usable titles. And *every* entry corpus-wide reads `*description pending*`.

## 4. The ROOT index already does this job, better

`plan-045/index.md`, verbatim:

```markdown
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded
  Upstream Issues row. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers
  flagged and how it was resolved.
```

**16 of 19 root indexes carry described subdirectory entries.** For research it is stronger:

```
research root index: entries pointing INTO subdirs = 8, 7, 10   (per bundle)
plan    root index:  entries pointing INTO subdirs = 0 for all 16
```

`research/004/index.md` already enumerates individual files *inside* `artifacts/`, `diagrams/`, `scripts/` with phase-tagged descriptions a generator cannot match:

```markdown
- [artifacts/triangulation.md](artifacts/triangulation.md) - [triangulate] 18 merged defect classes,
  3 overlap candidates split not merged, 5 contradictions adjudicated, 16 insufficient-evidence
  items; 100 sources scored (67 high_trust)
```

**Inferred:** for **yf-research** bundles a nested index is strictly duplicative and strictly lower quality. For **yf-plan** bundles it would add a per-file listing that genuinely does not exist — but only `references/` and `findings/` produce something worth reading.

## 5. The existing helpers emit an OKF-NON-CONFORMANT nested index

`render_index` against a scratch nested `references/`:

```
---
okf_version: '0.1'
---

# references

- [upstream-56.md](upstream-56.md)
```

Three defects at once: (a) emits `okf_version` frontmatter, which **§8 forbids on a non-root index**; (b) link text is the raw filename, not the H1; (c) no description slot. `_shared/okf.py:340` hardcodes `{"okf_version": okf_version}` and always prepends frontmatter. And `_check_reserved_index` (`:820`) only rejects `type`/`okf_spec` — so a nested index with `okf_version` would **pass yf's own check while violating OKF §8**.

## 6. `bp/okf-lint` — approach transferable, code not

**Transferable.** The set algebra: a folder is in scope if it holds ≥1 non-reserved `.md`; `missing = have - listed`, `ghost = listed - have`. `listed_in_index` strips preserved-prose blocks first, then accepts both relative and bundle-absolute links, URL-decodes, drops `http`/`#` targets.

**The best idea in it — prose preservation.** `PRESERVED_MARKERS = ("intro","notes","charter")`; regeneration keeps `<!-- intro:start -->…<!-- intro:end -->` verbatim. Two guards worth lifting wholesale: `check_markers()` **hard-errors on an unbalanced marker** (a `:start` with no `:end` silently discards prose — unrecoverable), and `discarded_prose()` warns on dropped non-generated lines. **Live case here:** `plan-045/index.md` carries a hand-written `## Note on scope-answers.md` section a naive regenerator would delete.

Also: exit `0`/`1`, `--fix` **re-checks drift after regeneration**, `--dry-run` returns 0 early, and a failed delegation is a hard error *before* the report.

**Not liftable.** `--fix` shells out to `chapter-intake` / `okf-issue-tracker` generators; root resolution needs an `AGENTS.md` sentinel; `FOLDER_TYPES`/`REFERENCE_TREES`/`SPEC` are the vault's Characters/Creatures/Places map; the chapter and character rules have no analogue; and **it targets OKF v0.1** (cites §6/§7 for what v0.2 numbers §8/§9). Its `d.get("description","")` fallback works because that vault *has* descriptions; here it fires 100% of the time.

## 7. Enforcement blast radius

Baseline today, `okf.py check` over all 50 bundles: **PASS=14 FAIL=36** (legacy bundles missing root `index.md`/`log.md`/frontmatter).

Simulating "every dir containing a non-reserved `.md` needs an `index.md`":

```
bundles that would gain >=1 finding: 50/50
total new findings: 128
of the 14 currently-PASSING bundles, newly broken: 14/14
```

**Every bundle in the corpus, without exception, would gain findings the moment the rule lands.**

> ### CORRECTION (red-team pass 1, 2026-08-18) — the escalation claim in this section was WRONG
>
> This section originally continued: *"Because `_audit_plan` step 7 folds `okf.check_conformance`
> **error**-level findings into `_OKF_PORT050_REQS`, this propagates into `plan_manager.py audit`,
> which exits non-zero… **It would block new plans, not merely flag old ones.**"*
>
> **That is false.** `plan_manager.py:3967` reads:
>
> ```python
> if cf.level != "error" or cf.req not in _OKF_PORT050_REQS:
>     continue
> ```
>
> against `_OKF_PORT050_REQS = frozenset({"REQ-OKF-003","REQ-OKF-030","REQ-OKF-031","REQ-OKF-071"})`
> (`:3525`) — an **allowlist of four named reqs, not a fold**. The source comment above it states
> the reserved-file presence errors are *"deliberately excluded"* to avoid double-reporting.
> Missing `index.md` is emitted under `REQ-OKF-001` (`_shared/okf.py:804`), which is **not** in the
> set — so these 128 findings would have been filtered out **at any level**, and `audit` would not
> have blocked a single new plan.
>
> **How it happened, and why it is recorded rather than edited away.** This finding's own Method
> section lists *reading* `plan_manager.py`'s `audit`/`audit-close`; **no `audit` run was ever
> executed.** The claim was an inference from source, presented in a section otherwise full of
> measurements — the precise defect class this plan is written against. plan-046 Issue 3.8 now
> measures it by execution.
>
> **The retargeting conclusion is UNAFFECTED.** It rests on the measured grounds — `description`
> at 0/423, 74/142 low-value directories, and root indexes already carrying better descriptions —
> not on this escalation. But `audit-close` going 100% noisy (below) is the real consequence, and
> it is smaller than what was claimed.

`audit-close` (plan-043's shipped half of #140) wraps the *same* engine but re-frames the verdict as advisory and `sys.exit(0)` unconditionally. Its docstring records why: *"a fail-loud close-time audit would have blocked 22% of plans that legitimately completed."* So `audit-close` goes 100% noisy but does not block. **`audit` would NOT have blocked either** — this sentence originally read *"`audit` blocks everything"* and is retracted by the correction block above: the allowlist filters a `REQ-OKF-001` finding at **any** level.

**And this is a yf-local strengthening, not conformance.** yf's own REQ-OKF-001 scopes the requirement to *"each **dir-form bundle**"*, and OKF §8 says nested index files **MAY** appear.

## 8. Nested `log.md` — kill it permanently

- `references/upstream-<N>.md` is **170 of 191 references files (89%)**, and `yf-plan/SKILL.md:279` states they are *"regenerated on every re-triage; operator hand-edits will be clobbered."* A log there records "regenerated" forever.
- Churn measured across 8 bundles × 3 subdirs: **distinct commit dates = 1 for 20 of 24, = 2 for the other 4.** §9's date-grouped, newest-first format has nothing to group.
- **Nothing would populate it:** every `okf.append_log` call site in `plan_manager.py` (562, 1287, 1487, 1772) targets the bundle **root**. No producer event is scoped to a subdirectory.

## 9. The real drift is at the ROOT, and it exists today

```
$ uv run skills/yf-markdown-lint/scripts/markdown_lint.py docs/*/*/index.md --rules ML003
docs/plans/plan-032-james-dixson-6cb87b/index.md:14: ML003 broken link target: references/
docs/plans/plan-032-james-dixson-6cb87b/index.md:16: ML003 broken link target: findings/
docs/plans/plan-046-james-dixson-aabefa/index.md:19: ML003 broken link target: plan-retrospective.md
25 violation(s): ML003=25
```

Missing-entry half over the 19 root indexes:

```
plan-031: missing=['upstream-triage.md']
plan-037: missing=['REDEPLOY-HANDOFF.md', 'upstream-triage.md']
plan-038/039/040/043/044/045: missing=['upstream-triage.md']
plan-046: missing=['upstream-triage.md'] ghost=['plan-retrospective.md']
002/003: missing=['plan.yaml', 'sources.json']       004: missing=['plan.yaml']

root indexes examined: 19; ROOT-LEVEL files unlisted: 15; ghost entries: 1
```

`upstream-triage.md` is unlisted in **8 of 19** — a systematic producer bug the scaffold template never covers. `plan-046` links a `plan-retrospective.md` that does not exist. **That is an index asserting something false, in production, right now** — and `okf.py check` does **no link resolution at all**, so it is invisible to the current gate.

## The proposed `reindex` verb

| | |
| :-- | :-- |
| **Scope** | Bundle **root** `index.md` only, in v1 |
| `reindex --check <bundle>` | Report `missing` (present, unlisted), `ghost` (entry whose target does not resolve), `empty-dir`. Exit `0` clean / `1` drift. **No "stale metadata" check** — with `description` at 0/423 there is no metadata to go stale |
| `reindex --write <bundle>` | Regenerate, preserving hand prose between `<!-- intro:start/end -->`. Port `check_markers()` and `discarded_prose()`. **Never invent a description** — preserve an existing one, emit a bare `- [title](path)` for a new entry rather than `*description pending*` |
| `okf.py check` integration | Add ghost/missing as **`warning`**-level findings under a new REQ. *(Corrected: this originally read "deliberately outside `_OKF_PORT050_REQS`, so step 7 cannot promote them to `fail` and block intake". A new REQ is outside that four-element frozenset **by construction** — there is nothing to do — and the block-intake mechanism does not exist. See the correction block above.)* Promote to `error` only after `--write` has run corpus-wide and `--check` is green — D-3's own ordering, applied to the root |

Fixing the 25 + 15 real root defects is a green-able ~40-item backlog with genuine correctness value, versus a 128-finding nested backfill whose every entry reads `*description pending*`.

## Implications

1. **D-3's backfill half must be retargeted** from the nested tier to the root tier.
2. **D-3's generation + drift-check half is sound and should ship** — root-scoped, warning-level, non-gating, before enforcement.
3. **D-4 resolves asymmetrically and per-producer.** Nested `log.md`: **no**, permanently. Nested `index.md`: **no** for yf-research (root index already does it better), **not yet** for yf-plan.
4. **Prerequisite if nested is ever revisited:** make producers stamp `description:` in frontmatter. Then nested indexes are worth generating **forward-only**, and the backfill question dissolves.
5. **Do not reuse `render_index`/`add_index_entry` for nested dirs** — they emit frontmatter §8 forbids.

## Honest limits

- **Git churn is understated.** Merge/squash commits collapse in-session iteration, so "1–2 distinct dates" is a lower bound. The conclusion holds — committed history is what a `log.md` would record — but reflogs and unmerged branches were not inspected.
- **"Informative title" is a heuristic**, sensitive to its stoplist: unfiltered scored `reviews/` at 95%, filtered at 38%. The filtered number is reported because the plan-045 sample verifies it; treat ±10pp as noise.
- **Frontmatter parsing was regex-based**, not YAML — it would miss a multi-line `description:`. Given the count is exactly 0, a false zero is unlikely, but this was not cross-checked with `okf.read_frontmatter` on all 423 files.
- The plan-029 fixture indexes were **not** run through the prototype to compare against its hand-built "after" samples — a useful independent corroboration, not done.
- **Incubator bundles are unmeasured** — `Incubator/` does not exist here. If the corpus is meant to include an Obsidian vault, that population could have very different frontmatter coverage.
- **The 128-finding simulation assumes one rule shape** ("any dir with a non-reserved `.md`"). A narrower rule — only dirs with ≥5 files — would break **24 dirs instead of 128**. That variant was not simulated, and is the obvious lever if a nested tier is to be rescued.
