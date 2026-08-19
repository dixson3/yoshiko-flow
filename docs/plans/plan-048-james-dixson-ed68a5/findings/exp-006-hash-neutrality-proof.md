---
type: Finding
okf_spec: OKF-PLAN
id: exp-006
status: complete
---
# EXP-006 — Is a hash-neutral-only normalizer satisfiable, and is it useful?

**Question:** Which transforms are provably fingerprint-preserving; does an abort-if-any-hash-moves
predicate hold; and is D-4 useful or merely satisfiable?

## Approach Tested

Imported `plan_manager.py` in-process, verified an in-memory fingerprint reimplementation against
the real `_plan_content_fingerprint` on a live bundle, then ran **17 synthetic + 7 real** transforms
over the full 47-plan corpus, computing the fingerprint before and after each. Built a 3-phase
prototype normalizer (stage → verify → commit) with the abort predicate and drove it with a
hash-neutral transform, a hash-moving mutant, and a hash-neutral-but-non-idempotent mutant. Temp
copies only; `git status` clean.

## Result

### 1. The exclusion set, verbatim from code

`plan_manager.py:2145` — `FINGERPRINT_EXCLUDE_SECTIONS = {"upstream issues"}`; the hashed span is
`:2181-2186`, and `_plan_content_sections` (`:2148-2168`) accumulates only after the **first**
`^## `.

| # | Excluded | Mechanism | Site |
| :-- | :-- | :-- | :-- |
| E1 | every file except `plan_dir/plan.md` | function reads only that path | `:2178` |
| E2 | everything above the first `## ` — frontmatter, all `**Field:**`, `**Phase log:**` | `cur_title is None` | `:2160-2168` |
| E3 | `## Upstream Issues` — **exact lowercased title match only** | `FINGERPRINT_EXCLUDE_SECTIONS` | `:2145`, `:2183` |
| E4 | blank / whitespace-only lines | `if ln.strip()` | `:2185` |
| E5 | trailing whitespace | `ln.rstrip()` | `:2185` |
| E6 | `\r` in CRLF, EOF newline count | `str.splitlines()` | `:2160`, `:2185` |
| E7 | heading *case* | `title.strip().lower()` | `:2184` |

**Contradicting the prose:** `reviews/` and the Resolutions tables are excluded only *because they
are not in `plan.md`* (E1), by no rule. Nothing is `##`-level-aware beyond `^## ` — `###`/`####`
are hashed as ordinary body lines. Section **order** is hashed. There is **no status gate**.

**Callers:** `_fingerprint_status` (`:2220`) and `fingerprint write` (`:2254`) only.
**measured:** `grep -rn fingerprint yf/src/` → 0; `close_cascade.py` → 0.

**Fragility:** E3 is an *exact* string match. **measured** on plan-001: renaming to
`## Upstream Issues & Reconciliation` moves the hash `c2d850dd18da… → f891fe8fd6c5…`. A heading
normalizer must hard-blacklist it.

### 2. Measured transform table (47 plan.md)

Hash-neutral: trailing-whitespace strip (touches 0), blank-line collapse, EOF newline normalization,
LF→CRLF, tabs→spaces (touches 0), **add YAML frontmatter (touches 29)**, add a `**Field:**` line,
edit `## Upstream Issues` cells (touches 23), list marker `*`→`-` (touches 0), `####`→`###`
(touches 0).

Hash-moving: GFM table re-alignment (**30 moved**), heading `&`→`and` (47), bolding issue bullets
(36), appending a section (47), smart quotes→ASCII (47), wiki-link→GFM (1).

**The decisive table — the *actual* normalizer worklist (T1–T7):**

| Transform | Hash-neutral? | moved | touches | sections the changed lines live in |
| :-- | :-- | --: | --: | :-- |
| T1 unwrap bold issue lines | **NO** | 4 | 4 | Epics:84 |
| T2 letter epics → numeric | **NO** | 6 | 6 | Epics:27 |
| T3 inline `(#N)` → `resolves-upstream:` | **NO** | 1 | 1 | Epics:112, Gates:36, SC:21 |
| T4 gate `Test (paren):` → `Test:` | **NO** | 2 | 2 | Gates:2 |
| T5 `- Blocks:` referent grammar | **NO** | 5 | 5 | Gates:5 |
| T6 Risks bullets → table rows | **NO** | 2 | 2 | Risks:14 |
| T7 Success Criteria ids | **NO** | 21 | 21 | Success Criteria:174 |

**7 of 7 — 100% — of the real worklist moves the hash.** Every target line lives in `## Epics`,
`## Gates`, `## Risks & Mitigations` or `## Success Criteria`: all fingerprinted. **inferred:**
structural, not incidental — the fingerprint hashes exactly the sections a normalizer wants to
restructure. Corroborated by independent section attribution and by the synthetic probe (every
neutral transform is pure-whitespace or pure-preamble).

### 3. The refusal predicate, and the mutant that proves it fires

**(a) Eligibility gate (pre-write, per file):** path under a plans root, not under
`skills/**/fixtures/**` or `docs/plans/*/findings/**`; `status == "complete"`; a stored fingerprint
that equals the current one.

**(b) Neutrality postcondition — evaluated over the WHOLE batch before any byte is written:**
`if any(fp(staged) != fp(original)): ABORT — write nothing`.

**measured** on a temp copy of the real corpus:

```
A. hash-neutral transform → staged-changes=0  COMMIT ok — 0 files written, 0 fingerprints moved
B. MUTANT: T7 (SC ids)    → staged-changes=13 ABORT — fingerprint moved on 13; NOTHING written
corpus after all runs: 0 files differ from pristine
```

**The eligibility population — plan-047's "inert on today's corpus" note is wrong. measured:**
`status {complete: 47}`; `stored fingerprint present 26 / absent 21`; **ELIGIBLE 25/47**
(ineligible: no-stored-fp 21, already-stale 1). The `status` conjunct is inert; the
`stored == current` conjunct **rejects 22 of 47 (47%)**.

**And it rejects them backwards.** The 21 excluded are a strict subset of the *least-migrated*
plans — the population that most needs normalizing — and it buys nothing, because a plan with **no**
stored fingerprint cannot go stale-approved. **Split the conjunct:** `stored is None` → eligible
even for hash-moving transforms; `stored != current` → skip; `stored == current` → hash-neutral only.

### 4. Verdict on D-4

**Satisfiable: trivially. Useful on `plan.md`: essentially not.**

- **7 of 7** real transforms move the hash → **0 of 7** may run on an eligible plan.
- Hash-neutral transforms with *any* work to do: rstrip 0/47, tabs 0/47, list markers 0/47, heading
  levels 0/47, EOF newline 0/47. Only blank-line collapse (2/47) — and it shifts line numbers,
  which D-2a forbids on cited plans.
- **Run A wrote 0 files.** That is the honest yield on `docs/plans/*/plan.md`: **zero**.
- 30 of 47 plans have T1–T7 work; **all 30** move a hash. **0 of 30 get normalized.**

> **On `plan.md`, D-4 does not narrow the normalizer — it deletes it.**

**The counterweight, and it is real.** The fingerprint covers **1 file per bundle**. **measured:**
`docs/plans` = **699** `.md`, of which **47** are fingerprint-bearing (6.7%); `docs/research` = 41
and the SPEC family = 52, **0 fingerprinted**. So **~92% of the corpus is unconstrained by D-4** —
the normalizer keeps full value on `index.md`, `log.md`, `README.md`, findings, reviews, research
bundles and SPECs. **measured** counter-example with real work: adding YAML frontmatter is
hash-neutral, applies to 29/47 (8 eligible) → `COMMIT ok — 8 files written, 0 fingerprints moved`.

**On the OKF precedent — inversion confirmed, and there is NO reusable predicate.**
`skills/yf-okf/SPEC.md:244` (REQ-OKF-MIG-003) requires the fingerprint stay **stable** — D-4's
discipline, not its opposite. But **measured:** `grep -c fingerprint skills/yf-okf/scripts/okf.py`
→ **1**, and it is a *comment* (`okf.py:1173`). `okf.py` never computes a fingerprint; neutrality
is achieved **by construction** (writes land above the first `## `) and asserted externally in one
test line (`test_worktree.py:1512-1513`). Issue 8.1 must build the predicate from scratch; only the
*test shape* is inheritable.

### 5. Atomicity, rollback, `--idem-check`

The postcondition must be a **pre-write batch gate**, not a post-write check — a per-file
check-then-write leaves the corpus half-normalized on abort at file *k*. Three phases: **STAGE**
(transform in memory, retain originals), **VERIFY** (no fingerprint moved; `transform(out) == out`;
line-count preserved on the derived cited set), **COMMIT** (`write tmp` + `os.replace` per file,
then re-read and re-verify; drift → restore originals). Per-file replace is atomic; the *batch* is
not, so retained originals are the rollback. Git is the outer net — one commit +
`.git-blame-ignore-revs` makes `git revert <sha>` the whole-run undo, **so never commit
incrementally**.

**`--idem-check` is independent and the postcondition cannot subsume it.** Proved with a
hash-neutral-but-non-idempotent mutant (appends a trailing space to every `- Issue` line — absorbed
by E5, so the hash never moves, but bytes grow every run):

```
D. hash-neutral BUT non-idempotent → IDEM-CHECK FAILED on 21
```

Zero fingerprints moved; 21 files would grow without bound. So: every transform needs a
**recognizer for its own output**; fixpoint is checked on the **composed pipeline** (ordering bugs
are invisible per-transform); it runs in STAGE so a non-idempotent transform never reaches disk;
and it must **abort**, not warn.

## Implications for Plan

- **On `plan.md`, D-4 as written deletes the epic** — 0 of 7 worklist transforms may run, and the
  prototype wrote 0 files. The choice is not "how strict a normalizer" but "normalizer or none".
- **But D-4 constrains only 6.7% of the corpus.** 47 of 699 `docs/plans` `.md` are fingerprint-bearing;
  research and SPEC carry none. The normalizer retains full value elsewhere.
- **The eligibility predicate rejects backwards** and must be split per D-4a.
- **There is no reusable OKF predicate.** `okf.py` never computes a fingerprint.

## Recommendations

Keep D-4 as an invariant **on `plan.md` only**, and either (a) scope the write phase to
non-`plan.md` documents with `plan.md` report-only, filing the hash-moving sweep as a follow-on
(the corrected eligibility split alone unlocks 21 plans safely), or (b) accept that the epic ships
a linter-with-a-writer whose `plan.md` diff is empty. **Do not ship it believing the current
framing normalizes 30 plans.**

## Honest limits

T1–T7 are faithful *approximations* of EXP-002's transforms, not its implementation; instance
counts differ slightly. The neutrality verdict does not depend on the counts — it follows from
*where the target lines live*, measured independently via section attribution. `okf.py migrate` was
not executed end-to-end; the no-reusable-predicate finding rests on grep + source read, corroborated
by the external test assertion being the only fingerprint check in the codebase.
