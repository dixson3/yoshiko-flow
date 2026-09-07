---
type: Finding
okf_spec: OKF-PLAN
description: "73 real omissions (band 57-114; rejected upper bound 193). Ratio 53% real / 17% curation / 30% artifact. The required set must be corpus-wide, not per-page."
id: exp-003-omission-inventory
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# EXP-003 — The omission failure inventory

## Approach Tested

**measured** on `main` @ `b86f4d3` in an isolated worktree: mechanical extraction of the enumerable
half, six read-only sub-agents over the prose half under one stated definition, all six `.d2` read
against their declared sources, and plan-066's five named omissions re-verified rather than assumed.

## Result

### D2's premise confirmed: the baseline is GREEN while the omissions exist

```
check_skill_page_contract: A=20 B=20, 0 missing, 0 orphan   exit=0
check_web_counts: 47 files, 21 claims, 0 mismatches         exit=0
```

### The inventory: 73 real omissions

| Surface | REAL | CURATION | ARTIFACT |
| :-- | --: | --: | --: |
| Skill pages (20, in 4 batches) | 43 | 21 | 23 |
| `pages/*.md` — CLI + concept | 9 | 3 | 1 |
| `images/*.d2` (6) | 21 | — | 17 |
| `README.md` / `AGENTS.md` | 0 | — | — |
| **Total** | **73** | **24** | **41** |

**Ratio 53% real / 17% legitimate curation / 30% predicate artifact.** The 30% is high enough that
the rule needs a per-edge exclusion list **on day one**, not as a follow-up.

### Sensitivity — the bound is a property of the PREDICATE, not the corpus

| Reading | Total |
| :-- | --: |
| STRICT (typed verbs, flags, enumerable set-membership) | ≈ 57 |
| **Working (REAL only)** | **73** |
| LENIENT (+ ambiguous) | ≈ 114 |
| **UNBOUNDED** (every SKILL.md heading needs a page counterpart) — **the REJECTED reading** | **193** |

A 3.4× swing on prose judgment alone. **Draw the required set from enumerable sources only.**

### ~~Slash verbs are 100% covered~~ — **RETRACTED. This was a FALSE GREEN.**

> **AMENDED by main-session adjudication.** This experiment reported `MISSING_SLASH=[]` for all 20
> skills and concluded plan-066 "closed that class completely". **EXP-002 contradicted it**, naming
> `yf-change-validation infer` as a real omission. Adjudicated directly against the artifacts:
>
> ```
> skills/yf-change-validation/SKILL.md  ## Invocation
>   | Subcommand | Purpose |
>   | `infer` (bootstrap) | ... |
>   | `run --tier fast\|full` | ... |
>   | `check-drift` | ... |
>
> web/content/skills/yf-change-validation.md
>   :10  invoking `/yf-change-validation`      <- the ONLY hit; names NO sub-verb
> ```
>
> **CORRECTED AGAIN after pass-1 C15.** "names NO sub-verb" was itself an overstatement: the page
> DOES backtick-name `check-drift`, `run`, `fast` and `full`. Only `infer` is absent as a token,
> and it appears there as prose. The real gap on this page is **one verb of four** — exactly what
> EXP-002 reported. The load-bearing example is instead **`yf-beads-upstream`**: zero verb coverage
> on its page and **no `## Invocation` section at all**, which both instruments missed. Preserving
> an overstated retraction of an overstated green does not improve the record.
>
> **EXP-002 is right; this experiment was wrong.** Its extractor searched for literal
> `/<skill> <verb>` strings, but a subcommand **table** declares the verb as `` `infer` `` with no
> slash prefix — so the extractor could not see that shape and returned green over an input it
> never examined. That is the same defect class this plan exists to close, committed by one of its
> own instruments, and it is why EXP-002's finding that `## Invocation` has **≥4 incompatible
> shapes** is load-bearing rather than cosmetic.
>
> **Consequence for the plan:** slash sub-verbs are NOT 100% covered, and the class EXP-002
> identifies as the one clean, derivable signal stays in scope.

The remainder of the inventory lives in script verbs, named behaviors, and diagram set-membership.

### The structural reason omissions are invisible

`DRIFT-CHECK.md:207-209` — the three skill-page edges are `field-set-subset`: *"A curated/omitted
subset PASSes; only a contradiction FAILs."* And `e-web-cli-surface` (`:166`) is `path-resolves`
whose two declared failure directions are **both page→CLI**.

**There is no CLI→page direction anywhere in the manifest.** That is exactly why
`yf harness skills prune-private` — a live, destructive command — is documented nowhere and is
unreachable by any check:

```
grep -rn -e "prune-private" -e "prune-formulas" web/content README.md   ->  (no output)
```

### A false positive I generated myself, proving the per-page predicate is wrong

A sub-agent scoped to six files reported `yf doctor --local-only` as omitted. It is not — it is at
`web/content/skills/yf-beads-init.md:30-31`. Mechanically: 15 of 20 skills go unmentioned in
`usage.md`, 17 of 20 in `workflows.md`. **A per-page required set manufactures ~30 false failures
on those two pages alone.** "Documented somewhere on the site" is the right predicate.

### Three hypotheses tested and REFUTED (recorded so they are not rediscovered)

- *"`install-matrix.d2` mis-states the opencode/pi roots"* — **refuted**; `surface_dir` ≠
  `skills_subpath`. The diagram is correct.
- *"`tune-matrix.d2` omits the `agents` harness"* — **refuted**; `managed_block.rs:345-370` declares
  exactly 4 `RULE_TARGETS`, and `agents` has none. `tune-matrix.d2` has **0 omissions**.
- *"`architecture.d2` still omits the workflows group"* — **refuted**; `:20` carries it with correct
  membership, 3/5/8/4 = 20.

### plan-066's five, re-verified

`land`, `closable`, escalations: **repaired**. Autonomy and retrospectives: **partial** —
`--sweep-gates`, `retrospective`, `plan-retrospective` and `RE-NNN` each hit **exactly one file**.

### Two live contradictions that FAIL under the CURRENT rule and no edge covers

1. The lint subset: the web page says **seven** (correct, per `yf-markdown-lint/SKILL.md:201`);
   **four SKILL.mds say six**.
2. `yf-incubator.md:61` calls it "a beads-free utility skill"; its frontmatter declares
   `skill-group: workflows` + `depends-on-skill: [yf-beads-extra]`.

## Implications for the plan

1. **73 is plan-sized but at the top of the range** — roughly 2.8× plan-066's corrected 26.
2. **The required set must be corpus-wide, and drawn from enumerable extractions only.**
3. **`e-web-cli-surface` needs a NEW DIRECTION, not a stricter contract** — `path-resolves` is
   structurally one-way.
4. **Split at the prose/diagram seam.** The diagram half is a redesign whose "omissions" are mostly
   design decisions; the prose half is ~52 mechanical repairs against enumerable sets. One epic
   would let the diagram half's judgement calls block the prose half's clean wins.
5. **Density is uneven and schedulable** — five skill pages score zero; work concentrates in
   `yf-beads-authoring` (7), `architecture.d2` (17), and four others.

## Recommendations

1. **Adopt 73, with 57/114 as the declared band, and name 193 as the explicitly REJECTED reading** —
   naming it is what stops it being rediscovered mid-execution.
2. **Define the required set as a union of enumerable extractions** — clap paths, `/skill verb`,
   `uv run …py <verb>`, `ls agents/`, frontmatter sets, `DESCRIPTORS`, `RULE_TARGETS`, formulas.
3. **Add the CLI→page direction to `e-web-cli-surface`** with a mechanical realizer — a set
   difference with an exit code. That one check catches `prune-private`, `--prune-formulas` and both
   `--force` flags.
4. **Add `e-web-agents-set`** — `ls skills/*/agents/*.md` vs `workflows.md`'s table; currently 7 of 8.
5. **Fix the two contradictions BEFORE the rule lands**, or they pollute the new failure list.
