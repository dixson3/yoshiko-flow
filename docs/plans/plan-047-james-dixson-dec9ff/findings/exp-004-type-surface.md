---
type: Finding
okf_spec: OKF-PLAN
id: exp-004-type-surface
---
# EXP-004 — The definitive document-type surface, its producers, and the carve-outs

**Status:** complete · **Date:** 2026-08-18 · **Verdict:** D-1's "everything" resolves to **15
markdown types + 2 hard carve-outs**. The EXP-001 pattern — *a correct template that nothing
executes* — **repeats in 6 of 15 types**; 3 more have no template at all.

## The scoping inventory was wrong in five places

Measured with `git ls-files` (so untracked noise cannot inflate counts), at HEAD `7fc38d0`:

| Type | Scoping said | **Measured** | Cause |
| :-- | --: | --: | :-- |
| `findings/*` | 162 | **205** | **87 are a nested vendored fixture corpus** |
| `references/*` | 191 | **194** | +2 nested in that corpus |
| `plan.md` / `context.md` | 47 | **46** | plan-047 not in the worktree |
| `assets/*` | 11 | **14** | — |
| spec family | 53 | **53** (+`SPEC-TEMPLATE.md` = 54) | template excluded |

**`findings/` is not one type.** 118 files are flat; **87 sit under
`plan-029/findings/okf-migration-samples/`** — a before/after migration diff fixture containing
whole nested bundles (`plan.md`, `index.md`, `log.md`, `sources.md`, `references/upstream-3.md`,
`check-before.json`, `migrate-dry-run.json`).

> This is a **second carve-out as large as the vendored-spec one** and was invisible at scoping.
> Linting a fixture's `plan.md` against the live template would generate 87 false findings **and
> break the fixture**, whose entire purpose is to preserve a pre-migration shape.

## The type table

| # | Type | n | Producer (exact) | Class | Template? | Enforced? | **Measured drift** |
| --: | :-- | --: | :-- | :-- | :-- | :-- | :-- |
| 1 | `findings/*.md` (excl. fixtures) | 117 | `agents/investigator.md` L24-36 fenced block | agent | **yes** | **no** | **111/117 = 94.9%** |
| 2 | spec `Verification:` clauses | 226 | hand-authored across 25 files | authored | partial | **no** | 13 runnable; **4 of 12 executed are FALSE** |
| 3 | `reviews/pass-N.md` | 108 | `SKILL.md:461-472`, written by the **main session** (red-team is read-only) | agent | **yes** | count only | **15/108 = 13.9%** |
| 4 | `references/upstream-<N>.md` | 167 | `plan_manager.py:_write_upstream_reference` L935-975 | code | **yes** | no | 13/167 = 7.8% |
| 5 | `plan.md` | 46 | `seed_plan_md` L508-566 | mixed | **yes** | **no** | 0/46 |
| 6 | `context.md` | 46 | `seed_context_md` L822-915 | mixed | yes | **YES** (`_audit_plan` #2) | **0/46** |
| 7 | `upstream-triage.md` | 28 | `seed_upstream_triage` L977-1035 | mixed | yes | no | 0/28 |
| 8 | `index.md` | 16 | `seed_index` + `okf.add_index_entry` | code | yes | **YES** | **0/16** |
| 9 | `log.md` | 20 | `okf.append_log` / `index_manager.py` | code | yes | partial | **0/20** |
| 10 | `README.md` (legacy) | 30 | **no producer** — every grep hit is a comment saying "legacy" | frozen | no | n/a | normalizer target only |
| 11 | research `Summary.md` | 4 | `agents/synthesizer.md` step 9 | agent | **no body template** | frontmatter only | emergent: 3/4 |
| 12 | research `artifacts/*.md` | 39 | `triangulator.md` / `red-team.md` / `retriever.md` | agent | **no — none of the 8 research agents has an `## Output` section** | none | **no `##` heading repeats >2×** |
| 13 | research `sources.md` | 4 | `link_normalizer.py:render_sources_md` L86-135 | code | yes | idempotent regen | **0** |
| 14 | per-skill `SPEC.md` | 19 | `skills/SPEC-TEMPLATE.md` (a real checked-in file) | authored | **yes, standalone** | **no** | 1/19 (`yf-herdr`) |
| 15 | `plan-retrospective.md` | 2 | `retrospective-append` | code | yes | CLI flags | 0/2 |
| — | **vendored `references/`** | 6 md + 3 sidecars | third parties | **vendored** | n/a | n/a | **CARVE OUT** |
| — | **`okf-migration-samples/**`** | 87 | fixture | fixture | n/a | n/a | **CARVE OUT** |

## The control that validates the whole thesis

> Every **enforced** type measures **0% drift** (#6, #8, #9, #13). Every **unenforced
> agent-written** type measures **14%–95%**.

`context.md` is the control: it is the one plan-bundle type with a real audit check, and it is
46/46 conformant. That correlation is this plan's justification.

## The `references/` carve-out — and it is not detectable today

| Subset | n | Verdict |
| :-- | --: | :-- |
| `upstream-<N>.md`, generator-shaped | 154 | **LINT strictly** — the template is already executable code |
| `upstream-<N>.md` coarse trackers | 13 | **LINT as a second declared variant** (`Disposition: tracker`) — forcing them into the generated shape would delete the disposition line |
| `comment-<N>.md` | 5 | LINT, thin template |
| hand-authored one-offs | 16 | **LINT LOOSELY** — H1 + provenance frontmatter only |
| vendored-verbatim | 6 md + 3 sidecars | **CARVE OUT, hard** |

**Only 2 of the 6 vendored files carry a machine-detectable marker** (`source:` + `retrieved:`
frontmatter — `okf-spec-v0.1.md`, `okf-spec-v0.2.md`). The three vendored `yf-herdr` copies and
`salvaged-docusaurus.md` carry **nothing**; the latter's only vendoring signal is the English
phrase *"Verbatim capture of the six reusable `website/docs/*.md` files"*.

> **The carve-out cannot be detected today. This plan must INTRODUCE the marker, not honor one.**
> Backfilling it onto the 4 unmarked files is a **prerequisite epic**, not a nice-to-have.

## The SPEC family and #165 — the issue is UNDERSTATED

53 spec files, 736 `REQ-*` ids, **312 `*(testable)*` markers**, **226 `Verification:` clauses**.

| Class | n | % |
| :-- | --: | --: |
| prose citing a file/REQ in backticks | 152 | 68.5% |
| prose, no backticks | 53 | 23.9% |
| **runnable — the clause IS a literal command** | **13** | **5.9%** |
| command embedded mid-sentence | 4 | 1.8% |

**Nothing reads a `Verification:` line.** Grepping all code outside `docs/plans/` returns **3
hits, all in `test_cli_enumeration.py`**, which asserts that **REQ-CLI-006 alone** names an
executing test. The only executing spec gate is `yf/src/coverage.rs`, which parses the **root
`SPEC.md` only** — 47 ids of 312.

> **265 of 312 testable requirements (85%) sit under no executing gate whatsoever, and 0 of 226
> `Verification:` clauses execute.**

Corroborated independently: only **25 of 222** clauses even *name* a test file, and all 25 are
under `skills/yf-plan/`. **Every one of the other 17 skills has zero.**

### 12 runnable clauses executed — 6 of 12 do not pass

| Clause | Result |
| :-- | :-- |
| `yf-optimal-instructions/spec/integration.md:51` | **FALSE** — exit 2, path predates the `yf-` rename |
| `yf-plan/spec/agents.md:7` | **FALSE as written** — the clause hedges *"(except the prohibition itself)"* in prose, an **unencodable exception**. Any mechanical runner marks it FAIL |
| `yf-research/spec/prerequisites.md:42` | **FALSE** — names the *installed* path, absent from this repo |
| `yf-research/spec/portability.md:44` | **FALSE** — 3/4 bundles exit 0; `docs/research/001-…` exits **2** (`no-index`, still carries legacy `_index.md`) |
| `yf-research/spec/cli.md:34`, `agents.md:12` | **cwd-dependent** — fail from repo root, pass with the real path |
| the other 6 | PASS |

**The #135 drift class appears in 5 clauses** (hardcoded counts: `7`, `9`, `9`, `== 2`, `exactly
these 8`). All 5 pass today; **all 5 are one file-addition away from being false**, exactly as
REQ-CLI-006 was.

> **#165 is understated, not overstated.** It framed this as "some literal commands nobody runs".
> The measurement is that only 5.9% are even *shaped* like commands, **50% of those are already
> false**, and the remaining 94% are prose a linter cannot promote at all — they need
> **restating**, not executing.

`test_cli_enumeration.py:188-204` already encodes this exact lesson as a hand-written single-REQ
guard (*"a spec Verification must not be prose shaped like a command"*). Its existence proves the
pattern is right; **its scope — 1 REQ of 736 — proves it was never generalized.**

## Implications

1. **The two carve-outs are 19% of the plan-bundle corpus** and both are now enumerated.
2. **The carve-out marker must land before any linter binds fail-closed**, or the first INTAKE
   after this plan hard-fails on `salvaged-docusaurus.md`.
3. **D-3's fail-closed INTAKE binding would hard-fail 140 existing files on day one**
   (111 findings + 15 pass-N + 13 upstream + 1 SPEC). **The normalizer is a hard prerequisite of
   the linter binding — the ordering is not optional.**
4. **The `Verification:` work is a different kind of thing** and needs its own epic family: the
   other 14 types ask *does this document have the right shape*; this one asks *does this
   sentence's claim hold when executed*. It needs a runner, a recipe row, and a **restatement pass
   over 213 prose clauses** — authoring work no linter can do.
5. **`_shared/` is the right home for the extractor.** `_shared/sync.py` already regenerates
   marker-fenced vendored regions with a `--check` mode and is already a `CHANGE-VALIDATION.md`
   fast row. `scripts/check_frontmatter.py` is the exact precedent for a repo-level doc linter
   bound as a recipe row — and it currently covers `skills/*/SKILL.md` and `skills/*/agents/*.md`,
   i.e. **zero** of `docs/plans/` or `docs/research/`.

## Priority ranking (epic ordering should follow this; all types still get instantiated)

| Rank | Type | Why here |
| --: | :-- | :-- |
| **P0** | vendored-content marker + carve-out globs | blocking — D-3 would read 9 files it must never read |
| **P0** | normalizer for the 140 currently-failing files | blocking — D-3 is fail-closed, there is no soft landing |
| 1 | `findings/*.md` | **best ratio by an order of magnitude** — 117 files, 94.9% drift, template already a verbatim fenced block, and **only 2/117 carry the mandated `**measured:**` marker the whole investigator epistemics contract rests on** |
| 2 | spec `Verification:` (#165) | only type where the defect **actively lies in a green sweep**. Split: (a) runner + recipe row for the 13 runnable; (b) restate the 5 hardcoded counts as self-consistency assertions; (c) a grammar linter for the rest |
| 3 | `reviews/pass-N.md` | 108 files, 13.9% drift, template already written in prose |
| 4 | research `artifacts/*.md` | no template exists in any of the 8 research agents; research is young, so fixing it now is cheap |
| 5 | research `Summary.md` | codify the emergent shape; add `## Sources` to 001 |
| 6 | `references/*` | value is the carve-out + the 13 tracker variants |
| 7 | `plan.md` | 0% drift today but zero enforcement — pure regression prevention |
| 8 | per-skill `SPEC.md` | nearly free, `SPEC-TEMPLATE.md` already exists; fix `yf-herdr` in the same pass |
| 9–12 | `upstream-triage.md`, `plan-retrospective.md`, `context.md`, `index.md`/`log.md` | formalize / extract only, no remediation |
| 13 | legacy `README.md` (30) | **normalizer target, not a linter target** — no producer exists, no template should be authored |
| 14 | `DECISION.md`, `decisions/*`, `REDEPLOY-HANDOFF.md` | **defer** — 3 files do not justify 3 templates |
| 15 | non-md sidecars | out of scope; `diagrams/` already owned by `yf-diagram-authoring` |

## One structural recommendation beyond the ranking

The corpus splits cleanly into **code-generated** types (0% drift wherever a check exists) and
**agent-written** types (14–95% drift). The template format should reflect that split:

- **code-generated** → derive the template **from the producer function** so it cannot diverge;
- **agent-written** → a **standalone declared artifact** the agent file references.

Writing one uniform template format for both would re-introduce, at the template layer, exactly
the hand-maintained-duplicate problem `_shared/sync.py` exists to eliminate.
