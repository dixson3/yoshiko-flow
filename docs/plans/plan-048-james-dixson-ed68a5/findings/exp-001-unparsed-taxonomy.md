---
type: Finding
okf_spec: OKF-PLAN
id: exp-001
status: complete
---
# EXP-001 — Unparsed-construct taxonomy and hash-neutral repairability

**Question:** What are the unparsed constructs across the plan corpus, by class, and which are
repairable **hash-neutrally**?

## Approach Tested

Ran the committed `_shared/plan_extract.py` over all 47 `docs/plans/*/plan.md` and classified
every `unparsed[]` entry; mapped each to its containing `## ` section; wrote 8 trial repairs
(5 real + 3 controls), applied each to a sandbox copy, and computed the **real** fingerprint via
an `importlib`-loaded `plan_manager._plan_content_fingerprint` before and after; then applied all
repairs corpus-wide and measured residual unparsed, fingerprint movement, `stale_approved` flips,
and DAG deltas.

## Result

**plan-047's "300" is REFUTED as stated.**

- **measured:** `uv run _shared/plan_extract.py docs/plans/*/ --json` → **150 unparsed constructs
  across 33 of 47 plans**, not 300. Blocks-referent 60, column-0 bullet 37, depends-on-referent 22,
  orphan sub-key 16, gate-blocks-undeclared 7, dangling depends-on 5, non-epic H3 3.
- **inferred, corroborated:** the 300 came from a **pre-lettered-epic** extractor build. Patching
  out lettered-id support (`[0-9]+|[A-Z]` → `[0-9]+`) reproduces **327 across 33 plans**, with
  `Blocks=68` and `depends-on=20` matching plan-047's claimed numbers **exactly**. Second signal:
  plan-047's claimed components sum to **284, not 300** — internally inconsistent, mixing two
  builds.
- **Consequence:** the normalizer worklist is **~half** the size plan-047 implies.

### 1. Taxonomy

| # | Class | Count | Plans | Example | Hash-neutral repairable? | Evidence |
| :-- | :-- | --: | --: | :-- | :-- | :-- |
| A | column-0 bullet in `## Epics`, not a conformant issue bullet | 37 | 13 | plan-005 L238 `- depends-on: Epic 1` | **NO** | A1 fp `85ef5eb670ef→c6e17c0715a8`; A3 fp `bf866b678c46→d2d20906a7cf` |
| B | orphaned sub-key (no owning issue) | 16 | 6 | plan-013 L234 `  - depends-on: D.2` | **NO** (cascade of A) | 16→6 after A/D repairs; fp moved every time |
| C | `Blocks:` referent outside the REQ-DATA-019 alphabet | 60 | 25 | plan-007 L231 `- Blocks: Epic 2, Epic 3` | **NO** | C1 fp `b5298aa06802→770e34d04dc5`; C2 fp `85ef5eb670ef→77250e56b652` |
| D | `depends-on` referent not an issue id (prose tail / `Epic N` / `—` / `gate:…`) | 22 | 9 | plan-003 L72 `depends-on: start-gate` | **NO** | fp `bfd0b76078fe→4ea546c254a1` |
| E | dangling `depends-on` target | 5 | 3 | plan-015 L220 `B.4 → B.3` | **NO** (cascade of A) | 5→0 after A; fp moved |
| F | non-epic H3 inside `## Epics` | 3 | 3 | plan-008 L269 `### Capability Gate: d2 present` | **NO** — even a *verbatim* move | 7 lines moved unchanged: identical line multiset, fp `e3c87751532d→248ee089a84b` |
| G | gate `Blocks:` an undeclared issue | 7 | 6 | plan-013 L252 `D.4` | **NO** (cascade of A) | 7→0 after A; fp moved |
| — | CONTROL: trailing whitespace on 247 lines | — | — | — | **YES** (fixes nothing) | fp `85ef5eb670ef→85ef5eb670ef` |
| — | CONTROL: +259 blank lines | — | — | — | **YES** (fixes nothing) | fp unchanged |

### 2. The non-hash-neutral subset is **all 150 (100%)**

- **measured:** **83 unparsed in `## Epics`, 67 in `## Gates`, 0 elsewhere.** The only
  fingerprint-excluded regions are the pre-first-`##` preamble and `## Upstream Issues`.
  **No unparsed construct lives in an excluded region.**
- **measured:** the fingerprint is `sha256` over an *ordered* list of `section-title.lower()` plus
  every non-blank `rstrip()`ed body line. Its only degrees of freedom are trailing whitespace and
  blank lines — both confirmed neutral by control, neither able to change a parseable token.
- **Corroborated by the class-F move test:** the hash is **order- and section-sensitive**, so even
  relocation with zero character changes moves it. There is **no** content-preserving
  rearrangement that is hash-neutral.

**Blast radius (measured).** All 5 repairs corpus-wide → unparsed **150→54** (64% fixed);
**28 of 47 fingerprints move**. All 33 affected plans are `status: complete`. 17 of 33 store **no**
fingerprint; of the 16 that do, **12 become newly `stale_approved`** (0 were stale before). Because
`_fingerprint_status` computes staleness **status-independently** (#109), those 12 completed plans
would carry a permanent `⚠ STALE-APPROVED` tag in `/yf-plan list`. It blocks nothing (complete
plans never execute), so the cost is durable false-alarm noise, not a blocked pipeline.

> **Verdict on D-4: satisfiable only vacuously.** A hash-neutral normalizer with an
> abort-if-any-hash-moves postcondition aborts on **every plan it could improve** and repairs
> **0 of 150** constructs. D-4 does not shrink the epic — it deletes it.

### 3. Classes where a mechanical repair picks the WRONG fix

1. **D / `depends-on: Epic N` — highest risk, measured harm.** The "drop the prose tail" repair
   silently emptied **20 `depends-on` declarations** (`grep -c "^  - depends-on: *$"` → 20 repaired,
   **0** original). The extractor then reports them clean — manufacturing a false-clean fidelity
   number, which is the exact failure the tool exists to detect.
2. **E / dangling targets.** The extractor's own docstring cites plan-047's
   `2.5 depends-on: 2.6, 2.7` as *"correct execution order, inverted numbering"* — so
   "renumber to nearest existing id" attaches the edge to the **wrong issue**, silently inverting
   a real ordering constraint.
3. **C / `Blocks:` with a trailing qualifier.** `- Blocks: E.1 close (and therefore E.3/E.4)` —
   stripping the tail keeps one referent and **discards two real block edges**. 33 of 60 C-class
   entries are prose, not typos, with no correct mechanical rewrite at all.
4. **A / genuine prose bullets that merely look like issue bullets** (plan-045 L465, plan-018 L232).
   A converter would **fabricate issues that were never planned**.
5. **`depends-on: —`** — a fixer cannot distinguish "none" from a truncated value.

Genuinely mechanical (the 96 fixed): stripping `Issue `/`Issues ` in `Blocks:`, `Epic N`→`epic:N`
where nothing else is on the line, re-indenting a column-0 sub-key, moving a title parenthetical
past the colon.

### 4. Reproducible sequence

```bash
uv run _shared/plan_extract.py docs/plans/*/ --json > /tmp/corpus.json   # 150 / 33 of 47
uv run <scratch>/pe_noletter.py docs/plans/*/ --json                     # 327 — reproduces the 300-era build
python3 <scratch>/exp001/section_map.py /tmp/corpus.json                 # 83 Epics / 67 Gates / 0 excluded
uv run --with click --with pyyaml python <scratch>/exp001/hash_trial.py  # per-class fp before/after
uv run --with click --with pyyaml python <scratch>/exp001/move_test.py   # verbatim relocation still moves fp
uv run --with click --with pyyaml python <scratch>/exp001/corpus_trial.py # 150->54, 28/47 fp move
uv run --with click --with pyyaml python <scratch>/exp001/stale.py       # 12 newly stale_approved
grep -c "^  - depends-on: *$" <scratch>/exp001/allrepair/*/plan.md       # 20 emptied (0 in original)
```

## Implications for Plan

- **D-4 as written kills the epic.** The choice is not "how strict a normalizer" but
  **"normalizer or no normalizer"**.
- The real cost of letting the hash move is **smaller than D-4 assumes**: 17 of 33 affected plans
  store no fingerprint, all 33 are `complete`, and staleness gates only `execute`. Observable
  damage is 12 advisory tags — itself a symptom of the status-independent staleness bug (#109).
- Sizing: **~96 of 150 (64%)** are mechanically fixable via 5 small rules across 28 plans; the
  residual **54** need human judgement.
- **13 issues and 15 dependency edges are currently invisible** to every downstream consumer.
  That is what the repair buys.

## Recommendations

1. **Replace D-4.** Either (a) *hash-aware*: let the hash move and **re-stamp** in the same commit
   for `complete` plans, recording the restamp in `log.md`; or (b) **widen the extractor grammar**
   for the unambiguous forms — a **fully hash-neutral** outcome because it touches zero documents.
   **(b) recovers the same ~96 constructs at zero corpus risk and is the recommended first pass.**
2. **Never mechanically repair classes D and E.** Report them; gate to a human.
3. **Correct the number in plan-048:** the reproducible figure against the committed tool is
   **150 across 33 of 47**, not 300.
4. If any corpus rewrite proceeds, gate it on a **DAG-invariance postcondition** (issues/edges may
   only increase, never decrease), not a hash postcondition — the hash postcondition does not imply
   it, while DAG-invariance would have caught all 20 silent deletions.

## Caveats

Harness scripts live in the session scratchpad under `exp001/`; nothing was written to the repo.
The shared scratchpad root is contended — another session overwrote a file mid-run, which is why
all final artifacts are under `exp001/`.
