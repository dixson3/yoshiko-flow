---
type: Reference
okf_spec: OKF-PLAN
id: exp-004-changelog-reconstruction
description: EXP-004 — can the v0.5.0 CHANGELOG be reconstructed mechanically from the plan bundles?
---

# EXP-004: changelog reconstruction feasibility

**Verdict: D-2 CONFIRMED — and the spine is NOT the one scoping assumed.** The SPEC amendment
log is unusable as a spine; the bundles' own `index.md` summary line is.

## Approach Tested

Read-only inspection at `HEAD`. Enumerated `docs/plans/plan-026..plan-053` (28 bundles) and grepped each for `## Objective`, `## Upstream Issues`, `## Success Criteria`, and each bundle root for `index.md` / `log.md` / `README.md` / frontmatter. Ran the shipped extractor `plan_extract.py --json` over all 28. Counted amendment-log bullets across the **whole** root `SPEC.md`, all 19 `skills/*/SPEC.md`, and `skills/*/spec/*.md`. Ran `git log v0.4.0..HEAD --name-only --grep=plan-0NN` per plan, and `git log --oneline | grep -v plan-` for the non-plan commits. Read the three `gen_handoff.py` copies and `scripts/`.

## Result

## The spine that works

| Signal | Coverage over plan-026..053 |
| :-- | --: |
| `## Objective` | **28 / 28** |
| **`index.md` one-line summary blockquote** | **28 / 28** |
| `## Upstream Issues` heading | 28 / 28 |
| …with ≥1 table row | 24 / 28 |
| `## Success Criteria` machine-readable as `SC<n>` | 14 / 28 |
| `plan-retrospective.md` | **9 / 28** (plan-045 onward only) |

`plan_extract.py` parsed **all 28 with exit 0**, yielding **183 structured upstream rows**.

## The SPEC amendment log is NOT usable as a spine — three independent reasons

1. **It misses 9 plans, not 7.** Scoping named 031, 035, 036, 045, 046, 048, 052. Measured, the
   set also includes **049 and 053** — and those two *did* edit root `SPEC.md` (053 added
   `REQ-YF-EMBED-005`) without writing a log bullet. **That is a process defect worth its own
   issue.** The other seven are legitimate: 031/035/036 touched no SPEC at all (they are the
   `web/` plans), and 045/046/048/052 amended only *per-skill* SPECs.
2. **It is fragmented and non-chronological.** The log is **not** confined to `SPEC.md:8-439`;
   bullets continue in later blockquote regions at lines **464, 501, 538, 620, 633**. Reading
   only 8–439 silently drops plan-042, 044, 047, 050, 051. Order is not chronological either —
   plan-051 (08-23) precedes plan-047 (08-19) and plan-050 (08-20).
3. **It is written in REQ-id voice**, not user-facing voice. Some entries state the visible fact
   (plan-042's is excellent); others are bare id lists (plan-047 is `REQ-DATA-018`..`-028` with
   no user-facing sentence).

**The per-skill SPECs do not close the gap.** Of 19 `skills/*/SPEC.md`, **exactly one**
(`yf-herdr`) has an amendment log; the other 18 carry plan attribution only as inline
parentheticals — unordered, undated, not enumerable.

**The decisive point:** the three plans with **zero SPEC signal anywhere** (031, 035, 036) are
the entire **docs-site theme** — the single most user-facing item in the release.

The amendment log remains the right source for **per-theme REQ citations**, just not for the
theme list or its ordering.

## The ten themes

| # | Theme | Plans | Class |
| :-- | :-- | :-- | :-- |
| T1 | **Multi-harness provisioning** — `yf harness tune` / `harness skills` across claude-code, codex, opencode, pi; `AGENTS.md` rule blocks; `--revert`; per-harness doctor drift axis | 032, 033, 034 | user-facing |
| T2 | **Install-time sync + consent gate** — `self install --from-build` / `self update` deploy skills + rules + gated config; `--allow-permissions-write`; `--no-sync` | 042, 041 | user-facing |
| T3 | **Four new skills** — `yf-okf`, `yf-herdr`, `yf-markdown-format`, `yf-markdown-html` | 029, 037, 026 | user-facing |
| T4 | **Markdown lint & format** — ML003 fix, new ML010/ML011, lint made validate-only with the aligner split out | 026 | user-facing |
| T5 | **Public docs site — yoshikoflow.sh** — Pelican, S3+CloudFront, per-skill pages, `VOICE.md`; retired the Docusaurus scaffold | 031, 035, 036 | user-facing |
| T6 | **Upstream tracking rebuilt on `gh`** — `bd` reads, `gh` writes, `external_ref` maps; `push` and `closable` verbs | 038, 040 | user-facing |
| T7 | **Autonomous execution + a real review contract** — self-resolving review cycles, non-stopping coordinator, gate sweep, herdr delegation, red-team as sub-agent | 045, 039, 051, 052 | user-facing |
| T8 | **Machine-readable artifacts + OKF v0.2** — `plan_extract.py`, `doc_lint.py`, OKF v0.1→v0.2, generated `index.md` | 047, 048, 049, 046 | mixed |
| T9 | **The silent-success / silent-data-loss class** — Dolt local-only, `YOSHIKO_FLOW.md` two-writer, reconcile close-wrong-bead, extractor drops, unshipped `pour_fidelity.py` | 044, 053, 050, 043 | user-facing |
| T10 | **Kernel & lifecycle hygiene** — preflight owns formula staging, doctor FormulaCheck + `--prune-formulas`, parked-plan visibility, ci-release completion | 027, 028, 030 | user-facing |

All 28 plans assigned exactly once. Every anchor named at scoping lands: 033→T1, 032→T1,
042→T2, 029/037→T3, 044/050/053→T9.

## Five things NOT recoverable from bundles

1. **The release number.** No bundle records it. `e-changelog-version` will fire.
2. **39 non-plan commits**, of which ~8 are user-facing and appear in **no** bundle — notably
   the `workflows` install group (`3c7eecf`), the `.beads/proxieddb/` gitignore (`f2a811d`), the
   `#105` fail-loud (`030745b`/`3fb5367`), and the web theme redesign (`9030544`, `d83d426`).
   **Budget one narrowly-scoped commit read — 39 commits, not 411.**
3. **The disposition trap.** Of 183 upstream rows only **59 are `include`**. A naive generator
   would emit 37 `exclude` and 30 `deferred` as *shipped work*. `partial` (36) is worse — it
   needs prose to say which half shipped. **This is the highest-probability defect in a
   mechanical pass.**
4. **Plan-time promise vs shipped reality.** `Resolved By` is written at intake; mid-execution
   descopes live only in prose. `plan-retrospective.md` covers only 9 of 28.
5. **Deprecations.** `yf skills`→`yf harness skills` and `--surface`→`--harness` exist in
   `REQ-YF-CLI-002` prose only; no table column carries "breaking".

## Tooling: scaffold, do not build a generator

`scripts/` has **no** changelog tooling. `gen_handoff.py` exists in **three** bundles, each
rewritten from scratch and hard-bound to its own `PLAN_DIR` — and its own docstring records that
plan-051's version **passed `--check` while reporting 0 where 6 existed**. Not a reusable base,
and a fourth rewrite is not warranted.

The real asset is the shipped, tested `plan_extract.py` — though it emits **no `objective` and
no `summary` field**, the two a changelog needs most.

**Recommendation: a ~40-line throwaway scaffolder** over `plan_extract.py --json` + the 28
`index.md` summary lines, emitting per-theme headings with summaries and `include`-only issue
rows. Roughly 60–70% of the typing with zero recall risk. Then curate by hand.

The existing 43-line `Unreleased` section is **correct** and should be folded into **T10 and
T1**, not discarded.

## Implications for Plan

- The mechanical spine that actually exists is **`index.md`'s one-line summary (28/28)** plus **`plan_extract.py --json`'s `upstream[]` with dispositions**. Both are on disk and tested.
- **Neither SPEC amendment log is usable as a spine.** The root log misses 9 plans — including all three docs-site plans, which have *zero* SPEC signal anywhere — is fragmented across five blockquote regions, and is non-chronological.
- **A generator cannot produce prose, and should not be built.** A ~40-line throwaway scaffolder gets 60–70% of the typing with zero recall risk.
- **The disposition filter is the highest-probability defect** in any mechanical pass: only 59 of 183 rows are `include`.
- The existing 43-line `Unreleased` content is **correct** and folds into T10 and T1.

## Recommendations

1. **Do not use the SPEC amendment log as the spine.** Use it for per-theme REQ citations only. File an issue for the two plans that amended root `SPEC.md` without a log bullet, and for the log's fragmentation across five regions.
2. **Adopt the ten-theme table above as the execution target.** All 28 plans are assigned exactly once.
3. **Write a ~40-line throwaway scaffolder, not a maintained generator.** Do not invest in a fourth `gen_handoff.py`.
4. **Filter on `disposition == "include"` and route `partial` to a manual queue.**
5. **Budget one narrowly-scoped commit read** — the 39 non-plan commits, not 411.
6. **Bump `yf/Cargo.toml` in the same change-set** as the heading rename, or `e-changelog-version` fires.

## Confidence

**measured:** all coverage counts, the extractor run over 28 bundles, the disposition histogram, the amendment-log bullet enumeration and its five fragmented regions, the per-skill SPEC survey, the non-plan commit list, and the OKF transition points.

**inferred:** the theme grouping and the user-facing versus internal split.
