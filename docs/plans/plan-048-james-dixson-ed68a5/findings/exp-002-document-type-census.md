---
type: Finding
okf_spec: OKF-PLAN
id: exp-002
status: complete
---
# EXP-002 — Document-type census and required schemas

**Question:** Which artifact types exist, in what counts, and what must each schema require?

## Approach Tested

Walked the corpus mechanically over `docs/plans/**`, `docs/research/**`, `skills/**`; ran a probe
script per candidate type asserting concrete checks and reporting pass rates over every instance;
traced each candidate requirement to a **consumer** (parser, gate, or Rust code) by grep rather than
accepting "the recent files all do it"; ran three live experiments against the real engine.

**measured:** baseline `doc_lint.py --json` → `PASS, 174 files, 0 errors, 610 report-only`. Only 3 of ~30
distinct types have schemas; 174 of **744** in-scope `.md` are reachable (the denominator is the union of `docs/plans/**`, `docs/research/**` and `skills/**` markdown, excluding vendored `references/user-scope/**`).

## Result

### 1. The type table (abridged to the load-bearing rows)

| Type | n | schema today? | proposed required (E) | consumer that makes it load-bearing |
| :-- | --: | :-- | :-- | :-- |
| `plan` | 48 | yes | — | shipped |
| `finding` | 123 | yes | — | shipped |
| `reference` (vendored) | 3 | yes | — | shipped |
| **`review`** | **112** | no | `^## Verdict: (APPROVE\|REVISE\|INVESTIGATE-MORE)`; five body H2s | **`_latest_review_verdict` → `ready-check` → the approval gate (REQ-PLAN-071/072, #116).** Unparseable = plan silently cannot be approved |
| **`skill`** | 19 | no | frontmatter `name, description, skill-group, depends-on-tool, depends-on-skill` | **`yf/src/frontmatter.rs` parses exactly these 5**; drives `yf skills install` |
| **`upstream-reference`** | 194 | no | code-generated H1/`## Body`/5 bullets | `_write_upstream_reference` is the sole producer |
| **`context`** | 48 | no | 5 sections (derived) | **already hard-enforced by `_audit_plan`** — consolidation, no behavior change |
| `upstream-triage` | 30 | no | H1 + `**Disposition:**` | `seed_upstream_triage`; operator-edited gate input |
| `plan-retrospective` | 3 | no | H1 + `RE-\d+` H2 grammar | `test_retrospective.py` |
| `agent` | 23 | no | frontmatter `name, role, model, description` | weak — well-formedness already guarded |
| research `Summary`/`artifact`/`sources` | 4/25/4 | no | frontmatter + H1 stem + citation linkage | REQ-DATA-003, REQ-PORT-007 — **spec-declared, unenforced today** |
| `skill-readme`, `protocols/*`, `assets/*` | 19/8/14 | no | **none justified** | **none — unjustified** |
| `skills SPEC.md` | 19 | no | **OUT OF SCOPE (D-1)** | censused only |
| `index.md` / `log.md` | 37 / 6 | no | **do not instantiate — duplicate** | already enforced by `okf.py check_conformance` + `_audit_plan` |
| legacy `README.md` | 30 | no | **do not instantiate — normalizer target** | no producer exists |

**measured:** drift. `review`: `## Verdict:` parses in **88/112 (79%)** — but the load-bearing
number is per-plan: **16 of 47 plans (34%) have a *latest* `pass-N.md` whose verdict does not
parse**, and all 16 predate the #116 parser fix; post-plan-024 it is 100%. *plan-047's
enforcement-not-recency thesis, reproduced exactly.* Resolutions table in the mandated shape:
**5/112 (4%)**. `context` **48/48 (100%)**. `skill` **19/19** on four keys, 18/19 on the fifth.
`agent` 23/23; `plan-retrospective` 3/3; `upstream-triage` 30/30.

**A live producer gap:** only research-001's artifacts carry `](sources.md#` links. **002/003/004's
21 artifact files carry ZERO** — `003/artifacts/triangulation.md` still holds bare `[CE-1]`, never
link-normalized.

### 2. Three engine constraints that size the epic (all measured)

- **Status-aware promotion does not apply outside plan bundles.** A probe schema on
  `docs/research/*/Summary.md` returned `bundle_status: null` for every file → `FAIL`, exit 1; on
  `skills/*/SKILL.md` → `FAIL`, **19 errors**. `bundle_status()` walks up to the nearest `plan.md`,
  so `mapping = STATUS_SEVERITY.get("", {})` → `{}` → `E` stays `E`. **Every `E` check on a research
  or skills type is a hard, un-softened error the instant it is declared.** This is the single
  largest hidden cost in the epic and plan-047 does not mention it.
- **`derive_from` resolves only modules in `_shared/`.** `derive_from = "plan_manager._CONTEXT_REQUIRED_SECTIONS"`
  → `INCONCLUSIVE, "no module 'plan_manager' in _shared/"`, exit 2. Every code-generated type whose
  producer lives in `plan_manager.py` needs its constant hoisted into `_shared/` first
  (`_shared/plan_template.py` is the established home). One small refactor per type, not an engine change.
- **`skills/*/SKILL.md` and `skills/*/agents/*.md` map only to the `frontmatter` recipe**, not
  `doclint` — a `skill`/`agent` type needs a new §3 trigger row or it never fires on edit.
- `tests/fixtures/doclint/` has `plan/bad.md` and `finding/bad.md` but **no `reference/bad.md`** —
  the shipped third type already lacks its fixture.

### 3. Splits required

**`references/*` → 4 types, not 1:** `upstream-reference` (194, generated, strict),
`reference-comment` (13, agent-written), `reference-tracker`, `reference-authored` (14 residual —
arguably declare nothing). **Correction:** plan-047 says 13 tracker refs; measured, **4** carry a
`tracker` disposition and 15 carry any `**Disposition` — the 13 is the `comment-*` count, conflated.
Only **3/14** residual authored refs carry `source+retrieved`, so extending the vendored-marker
check beyond `user-scope/**` would fire **11 false positives**.

**research `sources.md` cannot be strictly schema'd** — two incompatible producer modes
(per-source-ID vs per-cluster headings); require `# Sources` and nothing else.
**research `artifacts/*` → 3 sub-types** whose H2 sets are 100% distinct (17 distinct sequences over
17 cluster files); a frontmatter + H1-stem + citation-linkage schema is the honest ceiling.
**`reviews/pass-N.md` needs no split** (0 non-`pass-N` files) but needs two tiers: verdict `E`, body
sections `E`, Resolutions table `W` (4% conformance).

### 4. Absence findings

- **`Incubator/` does not exist in this repo at all.** Every `Incubator/*` glob in the three shipped
  schemas is permanently inert here. plan-048 must not count them as coverage.
- **`scope-answers.md`: ZERO instances**, despite `seed_scope_answers()` producing it. No schema.
- **Issues 6.1, 6.3 and part of 6.4 are already DONE** — shipped with plan-047's Epics 0–5.
  plan-048 must not re-schedule them.
- **Corrections to plan-047's numbers:** `review` is 112 files (not 108) and the load-bearing drift
  is 34% per-plan (not 13.9%); research `artifacts/` is 25 `.md` (the "39" counted 14 JSON sidecars).
- **Types Epic 6 omits entirely:** `skills/*/SKILL.md` (hard Rust consumer — the biggest omission),
  `agents/*.md`, `assets/*.md`, `skills/*/README.md`, `OKF-EXTENSION.md`, `protocols/*`, research
  `index.md`/`log.md`.
- **A live defect:** `docs/research/001-okf-compliance-delta/` still carries a legacy `_index.md`
  with **no `index.md` and no `log.md`** — un-migrated.

## Implications for Plan

- The epic is smaller than plan-047's list once duplicates are dropped, but each **new-surface**
  type (research, skills) carries a remediation cost the plan-bundle types do not, because
  status-softening does not reach them. Budget it explicitly.
- **`derive_from` hoisting is a prerequisite, not a detail** — four of the five code-generated
  types cannot be declared until their constants move into `_shared/`.
- `reviews/pass-N.md` is the highest-value target by consumer hardness: the only candidate whose
  failure mode has **already happened in production** (#116), and whose current tests check the
  parser and the template but **never the 112 artifacts**.
- The `SPEC.md` census (18/19 conformant) makes D-1's deferral a **scheduling** choice, not risk
  avoidance.

## Recommendations

**Instantiation order:** (0) hoist producer constants into `_shared/`, add the `SKILL.md` → doclint
trigger row, backfill `reference/bad.md` — *blocking prerequisite*; (1) **`review`** (112) — the only
candidate with a hard, already-broken consumer, and remediation is optional because every affected
bundle is `complete`; (2) `upstream-reference` (194) — largest count, code-generated, 0% drift;
(3) `skill` (19) — hardest machine consumer, 0% drift, declare-and-done; (4) `context` (48) — pure
consolidation; (5) batch `upstream-triage` + `plan-retrospective` + `agent`; (6) research types —
**declare every check `W`** or fix the 21 unlinked artifacts in the same commit; (7) reference
variants.

**Do not instantiate:** `index.md`/`log.md` (okf duplicates), legacy `README.md` (normalizer
target), `skills/*/README.md`, `protocols/*`, `assets/*`, `reference-authored` (no consumer),
`SPEC.md` (D-1).

**Two constraints to write into the plan:** (a) **no `E`-severity check on any `docs/research/**` or
`skills/**` path unless the whole corpus already passes it** — there is no status escape hatch
there; (b) one `tests/fixtures/doclint/<type>/bad.md` per new type is non-negotiable.

**Note on D-1:** the `SPEC.md` census is 18/19 conformant, which makes the deferral a *scheduling*
choice, not risk avoidance — worth stating so it is not re-litigated.
