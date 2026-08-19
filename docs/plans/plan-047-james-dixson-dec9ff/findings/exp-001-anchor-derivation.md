---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-anchor-derivation
---
# EXP-001 — Canonical grammar for `plan.md`, derived from the 47-plan corpus + declared templates

**Status:** complete · **Date:** 2026-08-18 · **Verdict:** a canonical grammar exists and is
derivable. The operator's "natural evolution" hypothesis holds on **3 of 11** axes — and all
three are axes where an **engineering change forced the move**. **Convergence tracks
enforcement, not recency.**

## Question

Field by field, what is the canonical grammar for `plan.md`? Does variance decrease over time
(validating "anchor on the most recent form"), or not?

## Method note

Plan number is a valid time axis — **MEASURED**: `plan-number vs created-date monotone? YES`.
Three templates were read: `SKILL.md` L370–425 (prose), `spec/data.md` REQ-DATA-010…016, and the
*code* template `seed_plan_md` (`plan_manager.py:508-566`). Corpus parsed fence-aware.

## Result

### Sections

All nine REQ-DATA-011 sections appear in **47/47** plans. Section order is the declared order in
**45/47**; plans **37 and 38** swap Investigation Findings before Upstream Issues.

**Non-template sections: 15 distinct spellings across 26 occurrences in 25 plans (53%)** — five
`## Scope`, three `## Scoping Decisions`, two `## Scope Decisions`, and ten more one-offs
including six date-stamped variants of "Scope decisions (operator-confirmed, YYYY-MM-DD)".

> A `## Scope Decisions` section is **de facto required** — a majority of plans invent one — and
> the template does not declare it. Leaving it undeclared forces the normalizer to drop or guess.

### Epics and issues

**`### Epic <N>:` — N is not always an integer.** Of 218 `###` headings inside `## Epics`:
188 integer, **27 letter-indexed** (plans 12–17 only, a contiguous window, never recurring),
2 non-epic headings misfiled under `## Epics`, 1 missing its colon. **`Epic 0` is legitimate** —
plans 21, 41–45 use it as the SPEC-first pre-epic.

**Issue-line variants — 855 top-level bullets, exact counts:**

| Variant | n | Plans |
| :-- | --: | :-- |
| **V1** `- Issue <id>: text` | **672** | 2–11, 13–16, 18–36, 41–46 |
| V3 `- **Issue <id>:** text` | 41 | 39, 40 |
| V2 `- **Issue <id>: Title.** body` | 39 | 37, 38 |
| V7 `- <id>: text` (no `Issue` keyword) | 38 | 12, 17 |
| V5 `- Issue <id> (#NN\|note): text` | 8 | 7, 13–16 |
| V4 `- **Issue <id> (#NN): Title.** body` | 4 | 37, 38 |
| V6 no colon after id | 2 | 15, 38 |
| V0 not an issue line | 51 | **plan-001 (27)**, 5(6), 8(6), 10(3), 12(6), 18(1), 45(2) |

plan-001 uses a wholly separate syntax: `- **1.1**: text`, no `Issue` keyword, id bolded, colon
outside the bold. Id alphabet in the wild: `(<int>|<UPPER>) "." <int> [a-z]` — `4.3b`, `3.7b`,
`4.1a`, `5.1b`, `A.1`…`E.4`.

**The decisive corollary — the DAG is already semantically perfect:**

```
issue id prefix != enclosing epic id:      0
duplicate issue ids within a plan:         0
depends-on targets with no matching id:    0
sub-bullet indent depths:               {2: 776}   (never drifted)
```

> **Only the lexical surface varies. A normalizer is a pure rewrite with no semantic
> reconciliation required.**

**Sub-bullet keys** (776 sub-bullets): 720 key-shaped, **56 free prose (7.2%)**. 638
`depends-on`, 69 `resolves-upstream`, and 13 one-offs (`Gated by`, `gated-by`,
`soft-order-after`, `IN`, `OUT`, `Note`, …). `depends-on` values are canonical in **620/638
(97.2%)**; `resolves-upstream` in 46/69 (plan-039 alone uses full markdown links, 17×).

Free-prose sub-bullets are **flat at 0 for plans 19–36 and rising recently**: 37(4), 40(4),
43(5), 44(3), 45(2), **46(9)**.

### Gates

`### Start Gate (mandatory)` is **byte-identical in 47/47** plans — zero variants, from plan-001.
38 Capability Gates (10 carrying a parenthetical), 33 Reconcile Gates across **6 spellings**.

**Field lines — your measurement confirmed exactly:**

| Field | Clean | Annotated (parenthetical before colon) |
| :-- | --: | --: |
| Type | 120 | 0 |
| Approvers | 57 | 0 |
| Condition | 43 | 1 |
| **Test** | **38** | **3** |
| Blocks | 72 | 0 |
| Instructions | 37 | 0 |

Plus two parser hazards the first pass missed: **plan-040 L360's parenthetical wraps across two
physical lines**, putting the colon on a continuation line; and **4 plans (37, 38, 42, 46) put
the `Test:` value in a following fenced block**. The `*(none — …)*` sentinel exists exactly once
(plan-046).

> A parser reading one physical line silently mis-reads 5+ gates.

**`Blocks:` — 72 values, ten referent shapes.** 20 are the bare sentinel `reconcile step`; only
**12 (16.7%) parse as a pure id list**; 40 are something else, including wildcards
(`Issue 2.x / 3.x`, plan-008) and pure prose.

> **CORRECTION to this plan's earlier measurement:** a **bare integer `3` never appears as a
> whole `Blocks:` value.** Bare integers occur only as *continuation tokens* inside `Epics 2, 3,
> 4`. This matters directly: a comma-splitting parser must not treat `3` as a standalone
> referent — it inherits the `Epics ` prefix.

### Success Criteria and Risks

**367 criterion items across plans 1–46:**

| Property | n | % |
| :-- | --: | --: |
| carries a stable id (`SC1`, `SC5b`) | **31** | **8.4%** — plans **39 and 40 only** |
| names an Issue/Epic id | 22 | 6.0% |
| contains a backtick (command/path) | **275** | **74.9%** |

> **CORRECTION to this plan's earlier measurement:** "6 of 47 plans give criteria stable ids" was
> wrong — that grep counted plans *mentioning* `SCn` anywhere, including prose cross-references.
> The true figure is **2 of 47 plans**, 31 of 367 items.

Form by plan: numbered 21 · bullets 23 · **table 2 (plans 39, 40)** · empty 1.

> The 039/040 table form (`| # | Criterion | Verification |`) is the **only machine-usable form in
> the corpus** — the only one assigning stable ids and the only one separating criterion from
> verification command. Within those two plans the id rate is **31/31 = 100%**; elsewhere 0/336.

The **74.9% backtick rate is the good news for #174**: the *verification* half of its falsification
rule is already present as prose and only needs lifting into a column. The *attribution* half is
entirely absent.

**Risks table header is itself unstable — 7 variants**, and cycling: `Risk|Mitigation` (15 plans)
→ `#|Risk|Mitigation` (5) → `#|Risk|Severity|Mitigation` (39–43) → **back to `Risk|Mitigation`
(44, 45)** → `#|Risk|Mitigation` (46).

## The hypothesis test — 3 of 11 axes

| Axis | Trend | Verdict |
| :-- | :-- | :-- |
| frontmatter + `log.md` | **monotone** — absent 1–29, present 30–47, zero relapse | **supports** |
| epic heading `Epic <int>:` | **monotone** — letters only in window 12–17 | **supports** |
| Risks: is-it-a-table | **monotone** — table continuously 25–46 except 30 | **supports** |
| Risks: which columns | cycling | refutes |
| Issue-line form | **cycling** — V1 → V7(12,17) → V2/V4(37,38) → V3(39,40) → V1 (41–46) | refutes |
| Section order | flat, broken only *recently* (37, 38) | refutes |
| Free-prose sub-bullets | flat at 0, **recently rising** (46: 9) | refutes |
| `Blocks:` grammar | flat/random; last 6 plans use prose, not bare ids | refutes |
| Success Criteria form | cycling; table appears only at 39/40 then is abandoned | refutes |
| Extra-section naming | random — 4 different spellings in the last 7 plans | refutes |
| Gate field keys | never drifted | supports (weakly) |

**All three supporting axes were forced by an engineering change** — plan-029's OKF adoption
(written by `seed_plan_md`), the epic-letter retirement, and risks-as-table.

**Two corroborating signals:**
1. The most uniform section in the corpus is `## Upstream Issues` — **45/47 byte-identical header
   rows** — and it is the **only** section with both a seeded skeleton *and* a real parser
   (`parse_upstream_rows:3809`, whose docstring says it is "deliberately the ONLY parser of this
   table in the codebase").
2. `## Success Criteria` and `## Risks & Mitigations` are seeded as the bare string
   `_To be determined._` with **no parser anywhere** — and they are the two sections with the
   most competing forms.

> **Consequence for the proposed remedy.** "Anchor on the most recent form" is valid only on the
> three monotone axes. On the issue-line axis it gives the right answer **by luck** — plan-046 is
> canonical. **Run this at plan-040 and "most recent" would have selected V3, a two-plan
> fashion.** The safe rule is: anchor on the **modal form of the post-excursion window (41–46),
> cross-checked against the whole-corpus mode**.

## The anchor, per section

| Section | Normative reference |
| :-- | :-- |
| header / frontmatter | **`seed_plan_md` (code) + REQ-DATA-015** — *not* SKILL.md |
| Objective, Motivation, Approach, Findings | **no anchor exists** — declare "free prose, ≥1 non-empty paragraph"; do not invent structure (Approach has 12 competing shapes, none >30%) |
| Upstream Issues | SKILL.md template + `parse_upstream_rows` (they agree; 45/47 exact) |
| Epics | **plans 044–046** (V1, 124 issue lines, 0 deviations) |
| Gates — Start | SKILL.md template, 47/47 exact |
| Gates — Capability/Reconcile | **plan-046** (`gate_type` / `test_class` / `cwd` keys, fenced `Test:`, the `*(none)*` sentinel) |
| `Blocks:` | **no anchor exists — must be legislated** (12/72 canonical) |
| Risks | **plans 039–043**: `\| # \| Risk \| Severity \| Mitigation \|` |
| Success Criteria | **plans 039/040**: `\| # \| Criterion \| Verification \|` + a new `Discharged-by` column |

## Where the declared template and the corpus DISAGREE

1. **`**Phase log:**` — the template is stale and contradicts its own spec.** `SKILL.md:372`
   still teaches it; **REQ-DATA-012 says `log.md` replaces it**, and `seed_plan_md` writes no such
   block. 32 plans have it, the last 13 do not. **The SKILL.md fenced template is the single
   most-drifted artifact in this experiment.**
2. **YAML frontmatter is absent from the SKILL.md template** yet required by REQ-DATA-015 /
   REQ-PORT-050 and present in 18/18 recent plans.
3. `### Capability Gate: <name> (if needed)` — `(if needed)` is an authoring annotation leaking
   into the grammar; 0/38 gates carry it.
4. `### Reconcile Gate (when upstream issues incorporated)` — this exact string appears **0
   times**; the corpus uses 6 other spellings.
5. Risks and Success Criteria are declared as bare headings with **no body** — and the corpus
   consequently invented 7 and 4 forms.

## What must be ADDED (not codified)

1. **Stable criterion ids** — precedent 31/367 items in 2/47 plans. `SC<int>[<a-z>]`, unique,
   **insertable without renumbering** (plan-039 shows criteria are added mid-review; the `SC5b`
   suffix form is the right device).
2. **`discharged-by:` criterion → issue link** — **this edge does not exist in the corpus in any
   form.** Recommended as a 4th table column, with two linter rules: every SC has ≥1 discharger,
   and every issue is named by ≥1 SC (or explicitly `discharges: none`). This is the exact join
   #174 needs.
3. **Machine-checkable `Blocks:`** — a closed referent alphabet (`issue-id` and explicit
   `epic:<N>`), retain the `reconcile step` sentinel but forbid its trailing parenthetical (6
   uses → move to `Instructions:`), forbid wildcards and prose. A linter rule that every referent
   resolves is symmetric with the `depends-on` check that already passes 100%.
4. **Three the corpus did not ask for but the parser needs:** a closed sub-bullet key set (13
   one-offs; free prose 7.2% and rising); a **multi-line value rule** for gate fields; and a
   declared `## Scope Decisions` section.

## Implications

- **The normalizer's job is smaller than D-2 assumes and its risk is low.** The concrete rewrite
  set is bounded: plan-001 (27 lines), plans 12/17 (38 lines + epic renumbering), plans 37/38 (43
  lines + section reorder), plans 39/40 (41 lines), ~18 stragglers. **≈190 of 855 issue lines
  (22%).**
- **The extractor is tractable today for Epics/Issues/`depends-on`** (3 regexes cover 620/638 dep
  values; post-normalization 855/855 issue lines) and **is not tractable for `Blocks:`** (16.7%)
  without the legislated grammar.
- **The biggest single risk to this plan is the SKILL.md template itself.** Codifying "the
  declared template" would codify a document that contradicts REQ-DATA-012 and 18 of the last 18
  plans. **Fix the template before deriving anything from it.**

## Recommendations

1. **Fix the SKILL.md `plan.md structure` block first** (SPEC-first): delete `**Phase log:**`, add
   frontmatter, drop the `(if needed)` / `(when upstream issues incorporated)` annotations, add
   bodies for Risks and Success Criteria. **Make it byte-identical to `seed_plan_md` and add a
   test asserting that equality** — the two templates are already drifted and nothing detects it.
2. Adopt the EBNF grammar verbatim, with the anchors tabled above.
3. Legislate the additions as new REQ ids and **say in the amendment log that they are additions**,
   not codifications.
4. **Do not anchor on "the most recent plan" as a rule.** Record the 37–40 window as a measured
   counter-example to the recency heuristic.
5. **Ship the extractor and the linter together, and gate intake on the linter.** The measured
   evidence is that structure survives exactly as long as something reads it.
