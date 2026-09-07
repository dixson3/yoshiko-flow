---
type: Review
okf_spec: OKF-PLAN
description: "Red-team pass 1: REVISE, 17 concerns (7 high). D6 refuted by a six-diagram measurement; three of D1's four archify grounds refuted."
id: pass-1
plan: plan-067-james-dixson-de852a
created: 2026-09-07
verdict: REVISE
---
# Red-team pass 1 — plan-067-james-dixson-de852a

## Verdict: REVISE

17 concerns (7 high, 2 medium-high, 5 medium, 3 low-medium/low). **Two are decisions the operator
made on information this review refutes.**

## Mechanical gates (executed, fields read back)

`audit` **pass** (8 warns) · `plan_extract --strict` 7/38/48/6/27, **0 unparsed** · `doc_lint`
exit 0, **0 E** · `gate_consistency` **PASS, 6 gates** · DAG 0 cycles / 0 self-edges / 0 dangling ·
uncovered list matches the extractor **exactly** · `recheck-criteria` 24 FALSE, **0 malformed**.

**Both `manual:` rows are correctly formed** — SC17 and SC27 match `\Amanual:\s*\S`. plan-066's
`**manual**:` defect is NOT repeated.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **D6 is REFUTED by measurement.** All six rendered under both engines (24 renders). dagre produces **hard text-on-text collisions on 2 of 6** (`phase-model`: `consent` stamped across `PHASE 4 · INTAKE`; `formulas`: a label struck through `AUTHORED`), is **larger on 6/6**, **discards semantic ordering on 3**, and is **worse on `architecture`** — the diagram that drew the operator's objection (1.6× canvas, backwards snaking). The one diagram where dagre ≈ elk is `lifecycle`, almost certainly EXP-001's single sample. | Drop Epic 3, or reduce it to `lifecycle` only. **A human gate cannot mitigate a change the evidence already says to reject.** Determinism is not the issue — both engines are byte-stable. |
| C2 | high | **The dagre gate is a cliff, not a checkpoint.** 20 of 38 issues depend transitively on `3.2`. If the operator declines (C1 predicts they will), the entire diagram redesign is stranded and plan-066 stays parked forever — R13's exact failure mode, reintroduced by R5's mitigation. No declined branch exists. | Re-point `4.1-4.4` and `5.1` at `2.6`. The layout pin is orthogonal to the redesign's content and must not be able to block it. |
| C3 | high | **Three of D1's four archify disqualifiers are refuted or overstated — and archify is what the operator asked for.** (a) "no CLI raster export" — **refuted**: `archify visual-check <html> --json` is a documented verb driving headless Chrome, writing PNGs. (b) "unvendorable" — **refuted**: MIT, **zero runtime dependencies**, pure ESM; `private: true` blocks only `npm publish`; the self-update manifest is **inert** (no call sites). `cp -R` is the whole procedure. (c) "`--quality showcase` pressures deleting member ids" — **refuted**: the constraint fires **byte-identically at `standard`**, which is the **default, not a demotion**, and archify's own SKILL.md *forbids* shortening labels first. Only (d) the font reference verifies, and even it overstates. | **Keep the conclusion; replace the rationale.** The two surviving claims are strong alone: **orthogonality** (the omission fix is checker logic) and **checkability** (archify's HTML loses membership — `4 declared unchecked, EXIT=0`; its JSON throws two false-positive FAILs; it has **no d2 input path**; `visual-check` PNGs are full-page viewer screenshots including title bar and Export button, so SC10 has no clean equivalent). Reinstate EXP-001's recommendation 5 — archify scoped to exploration — which D1 killed on grounds that have collapsed. **A plan that rejects an operator's explicit ask should do it on claims that hold.** |
| C4 | high | **SC10 and the fail-capable gate are already satisfied before any work.** `--min-checkers 4` is met by **plan-066's** four checkers; registering **zero** new controls still passes. The criterion cannot distinguish done from not-done. | Raise the floor to 8, or pin the gate to the four new checkers by name — in both the gate `Test:` and SC10. |
| C5 | high | **SC8 is unsatisfiable under the plan's own predicate.** The plan declares it corpus-wide ("documented somewhere on the site"), but `--force` **is** documented (`install.md:132`, `README.md:75`). What is undocumented is the *verb-flag pair*. A pair-level predicate contradicts the corpus-wide rule and reopens R7. Separately, a built realizer returned **12 "missing" flags of which 5 are positional arguments** — a ~40% artifact rate. D4b is the one direction adopted **without** a measured false-positive rate. | State 1.3's predicate explicitly; rewrite SC8 to name only what the chosen predicate catches; add positional-vs-flag exclusion with a measured rate before Epic 1 lands. |
| C6 | high | **Issue 1.1 inherits #376's blind spot verbatim.** The proposed `missing = …` lands inside the `else` of `if members is None`, so a group enumerating **no member ids** goes to `not_checked` and the check never runs. Epic 4 rebuilds every diagram into a shape with *fewer* enumerated labels — the easiest way to evade the new rule. No criterion bounds `not_checked`. | Add `not_checked == 0` to SC6 and SC19; give 1.1 an explicit sub-task for the `members is None` path. **Triage #376 as `include`** — it is a precondition of Epic 1. |
| C7 | high | **`upstream-triage.md` is entirely unfilled** — every Disposition and Notes field blank across all seven issues, and `## Upstream Issues` has **zero rows** — yet Issue 6.5 asserts dispositions that exist nowhere. `audit` passes regardless. | Fill the triage and the table before approval. #375's literal must be assigned — 4.2 merges `lifecycle.d2` without mentioning it. |
| C8 | medium-high | **Two of #373's explicit asks are silently dropped.** (a) the **five per-formula diagrams** — 4.4 adds only the map and explicitly keeps `formulas.d2`; (b) **land-the-plane** — zero hits across the whole plan. Yet `resolves-upstream: #373 (include)`. | Add both, or record explicit scoping decisions and downgrade #373 to `partial`. Closing `include` while dropping named deliverables is the stale-tracker shape D5 exists to prevent. |
| C9 | medium-high | **Issue 0.1 undercounts, in the same way plan-066 did.** "Four SKILL.mds say six" — measured, there are **five** sites; the fifth is `yf-skill-authoring/SPEC.md:94`, missed because the phrasing scoped to "SKILL.mds". Third instance of this defect class in this plan's own intake. | Restate as "every site carrying the 6-element subset string" and make SC1 a **derived** set-difference over `grep -rl`, not a hardcoded four. |
| C10 | medium | **SC4 is vacuous and the tool says so** — `check_amendment_log` returns INCONCLUSIVE: "the derived id set is empty". Issue 0.5 says "new/revised `REQ-*` ids" without naming one; plan-066's SC3 was non-vacuous because it named them. | Name the concrete `REQ-*` ids in 0.5 and 0.4 before approval. |
| C11 | medium | **The elk-pin blast radius is undercounted** — the pin is restated at **13+ sites** including `yf-diagram-authoring/SKILL.md:5`'s frontmatter `description` (which triggers a `yf` rebuild+redeploy), and the repo holds **21** `.d2`/`.png` pairs, not 6. | Moot if C1 is accepted; otherwise 3.2 must decide global flip vs `web/`-scoped override, and SC18 must name the archival PNGs in or out. |
| C12 | medium | **Frontloading miss.** `3.1` re-renders existing sources and has **no technical dependency** on Epic 2, yet sits behind all ~52 prose repairs — pushing the operator's read to the back half and lengthening plan-066's parked time by Epics 0-2. | Move `3.1` and its gate to the front, ideally as intake evidence. That is also what C1's measurement wants: the answer before 38 issues commit to it. |
| C13 | medium | **Cross-plan hazard, in the unchecked direction.** No deadlock — but plan-066 will re-run **all 26 criteria** at its close-out over a tree plan-067 restructured. 3.2 mutates `plan066_checks.py`'s `D2_FLAGS`, and plan-066's SC10 prose **hardcodes `--theme 0 --layout elk`**; Epic 4 rebuilds `architecture.d2` (plan-066 SC9) and merges four `.d2` files (SC23/SC24). | Add a criterion asserting plan-066's `recheck-criteria` is green on the post-plan-067 tree, and amend plan-066's SC10 prose in the same change-set. |
| C14 | medium | **The investigations' executable artifacts were not preserved.** `assets/` and `diagrams/` are empty. Lost: EXP-004's generator prototype (the strongest feasibility evidence for Epic 5), EXP-001's archify spike, and **EXP-003's slash-verb extractor — the instrument that produced the false green.** | Commit the three spikes under `assets/`. The EXP-003 extractor should become a **fixture** for 1.2's vacuity floor — a known-blind input is exactly what a floor needs testing against. |
| C15 | low-medium | **The EXP-003 amendment is directionally right but overstates.** The core claim holds. But "names NO sub-verb" is **false** — the page backtick-names `check-drift`, `run`, `fast`, `full`; only `infer` is absent, and it appears as prose. The real gap is one verb, exactly what EXP-002 reported. `yf-beads-upstream` — zero verb coverage, no `## Invocation` at all — is the better example. | Correct to "named one of four sub-verbs" and cite `yf-beads-upstream`. Preserving an overstated retraction of an overstated green does not improve the record. |
| C16 | low-medium | **`## Investigation Findings` is empty** and `## Upstream Issues` has no rows. A cold reader of `plan.md` alone gets none of the four experiments' results. | One summary line per experiment, linked into `findings/`. |
| C17 | low | The fail-capable gate declares `Blocks: epic:2, epic:4`; `epic:4` is already transitively blocked. Three findings use non-schema headings and `exp-003` puts the colon outside the bold, causing 8 audit warns. | Drop `epic:4`; normalize the headings and the marker. |

## Missing

- **No decision on what Epic 1 is worth.** 0.2/0.3 normalize `## Invocation` across 20 files to make live a check whose measured current yield is **one omission**. The required set after 0.3 is derived from a document **the plan itself writes**, so its size is a choice, not a measurement. State the expected yield, or say plainly the value is future-proofing.
- **No criterion asserts the six PNGs are re-rendered and committed** — 3.1 renders into a *review set*, 3.2 only changes flags.
- **No `pages/*.md` owner** for EXP-003's 9 real omissions there.
- **Epic 5 is defensible as an epic only because EXP-004 built and ran the prototype** — the evidence C14 says was discarded.

## Gate Assessment

`gate_consistency` **PASS, 6 gates**; all four capability gates formally reachable, none depending
on evidence inside its own Blocks set. The dagre gate is **correctly placed** between 3.1 and 3.2.
The gate *instructions* are the strongest part of the plan. The problems are placement (C12), an
already-satisfied test (C4), and **the absence of a declined branch** (C2) — not reachability.
**No cross-plan deadlock**; the hazard runs the other way (C13).

## Upstream Assessment

**Not assessable — and that is the finding (C7).** Seven issues, every disposition blank, zero
table rows. #373 `include` is **not earned as written** (C8). **#376 is mis-scoped as adjacent** —
it is the stated limit in the exact function 1.1 modifies (C6). #375 has no owning issue. #374
is undispositioned and interacts with Epic 5. #317 is undispositioned despite being the plan's
entire motivation.

## Resolutions

All 17 resolved. C1 and C3 were **operator decisions** — both were put to the operator with the
refuting measurements, and both were re-decided on the corrected information.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Accepted and independently re-measured.** I rendered all six under both engines myself: dagre is larger on **6/6** (+4% to +25%), worst on `architecture` (**+23%**) — the diagram the objection was about. **Epic 3 is replaced entirely**: the dagre re-pin is gone, the pin stays `elk`, and Epic 3 now trials **archify on one diagram** per the operator's redirect. R5 is retired with the sampling lesson recorded: a layout judgement needs the corpus, not a representative. **AMENDED — this resolution was initially a PARTIAL PHANTOM.** It claimed "Epic 3 is replaced entirely" while leaving **three** artifacts behind: D6 still declared the re-pin, the "dagre re-pin acceptance" gate still existed (blocking a `3.2` that no longer meant what it did), and SC17 still asserted the operator had accepted it. Caught by a self-administered phantom check **before pass 2 ran** — in the very cycle that resolved a concern about phantom resolutions. D6 is now **WITHDRAWN** with its rationale preserved, the gate is replaced by an **archify trial decision** gate, and SC17 asserts the archify verdict. | `main-session` | `resolved` |
| C2 | high | **Accepted.** Every `depends-on: 3.2` re-pointed to `2.6`, so no issue depends on a gate that can be declined. Epic 3 is now a leaf that reports; nothing is stranded by its outcome. | `main-session` | `resolved` |
| C3 | high | **Accepted, and the operator was told.** I verified all three refutations myself — `visual-check` exists, the package is MIT with **zero** runtime deps and no self-update call sites, and `standard` is the default. D1's rationale is rewritten to the **two surviving grounds** (checkability, orthogonality) with the three struck claims **retained struck-through** rather than deleted, because a plan rejecting an operator's ask must show which claims held. **The operator re-decided on the corrected information** and chose to trial archify on the architecture diagram; D1 now scopes archify to exploration rather than rejecting it. | `main-session` | `resolved` |
| C4 | high | **Accepted.** Floor raised to `--min-checkers 8` (plan-066's four inherited + the four Issue 1.5 registers) in **both** the gate `Test:` and SC10, so registering zero new controls can no longer pass. | `main-session` | `resolved` |
| C5 | high | **Accepted.** SC8 rewritten to claim only what a corpus-wide token predicate can reach (`prune-private`, `--prune-formulas`) and to state explicitly that it does **not** claim the `--force` flags, with the measurement (`install.md:132`, `README.md:75`). Issue 1.3 now states the predicate and requires a positional-argument exclusion with the measured ~40% artifact rate reported before Epic 1 lands. | `main-session` | `resolved` |
| C6 | high | **Accepted.** New Issue 1.1b closes the `members is None` path, and **#376 is re-triaged from adjacent to `include`** — it is the stated limit in the exact function 1.1 modifies. SC6 and SC19 now assert `not_checked == 0`, so the redesign cannot pass by dropping enumerated ids. | `main-session` | `resolved` |
| C7 | high | **Accepted.** The Upstream Issues table is populated with all seven rows and real dispositions: #373/#376/#375/#374 `include`, #317/#247/#263 `partial` with the in/out line drawn on each. #375 is assigned to Issue 4.2, #374 noted against Epic 5. | `main-session` | `resolved` |
| C8 | medium-high | **Accepted.** Both dropped asks restored: new Issue 4.4b authors the **five per-formula diagrams** and REMOVES `formulas.d2` per #373's literal wording, and Issue 4.2 gains **execution** and **land-the-plane**. New SC21b covers 4.4b. `resolves-upstream: #373 (include)` is now earned rather than asserted. | `main-session` | `resolved` |
| C9 | medium-high | **Accepted.** Issue 0.1 restated as *every site carrying the 6-element subset string, DERIVED by `grep -rl`*, with the fifth site (`yf-skill-authoring/SPEC.md:94`) named and the search-shape error recorded. SC1 now asserts the derived set-difference, not a hardcoded four. | `main-session` | `resolved` |
| C10 | medium | **Accepted.** Concrete ids named in the plan text: `REQ-CHECK-010` (required set), `REQ-CHECK-011` (CLI→page direction), `REQ-CHECK-012` (the `user-invocable` coercion fix), with the INCONCLUSIVE-on-empty-set mechanism recorded inline. | `main-session` | `resolved` |
| C11 | medium | **Moot, as the reviewer predicted.** C1 removed the re-pin, so the 13-site blast radius and the 21-pair archival question do not arise. Recorded rather than silently dropped: if a layout change is ever revisited, that scope is the starting point. | `main-session` | `resolved` |
| C12 | medium | **Accepted.** Epic 3 has **no dependency on Epic 2** — the dependency is removed and the reason stated inline (it reads nothing Epic 2 produces). The operator's answer now arrives before the redesign commits to it. | `main-session` | `resolved` |
| C13 | medium | **Accepted.** New Issue 6.0 re-runs plan-066's `recheck-criteria` against the post-plan-067 tree and amends plan-066's criterion prose where this plan legitimately invalidates it (its SC23/SC24 reference `formulas.d2`, which 4.4b removes). New SC26b asserts it. | `main-session` | `resolved` |
| C14 | medium | **Partially accepted — and the gap is recorded rather than papered over.** Recovered and committed under `assets/spikes/`: EXP-001's marketecture `.d2` draft plus its elk and dagre renders (the dagre one kept deliberately as a **negative artifact** — it is the single sample that produced the refuted D6). **NOT recovered:** EXP-004's generator prototype, EXP-001's archify spec, and EXP-003's slash-verb extractor — their sub-agent scratch did not survive. `assets/spikes/README-plan.md` states this and its consequence: Issue 5.2 re-derives the generator from EXP-004's written specification, and 1.2's vacuity floor must be tested against a **reconstructed** known-blind input rather than the original failing instrument. | `main-session` | `resolved` |
| C15 | low-medium | **Accepted.** The EXP-003 amendment overstated: the page does backtick-name `check-drift`, `run`, `fast` and `full`; only `infer` is absent as a token. Correcting to "named one of four sub-verbs" and citing `yf-beads-upstream` — zero verb coverage, no `## Invocation` at all — as the load-bearing example. Preserving an overstated retraction of an overstated green does not improve the record. | `main-session` | `resolved` |
| C16 | low-medium | **Accepted.** `## Investigation Findings` now carries a four-row summary with each experiment's verdict and the result that changed the plan, linked into `findings/`, plus a note that two of this plan's own instruments returned false greens. | `main-session` | `resolved` |
| C17 | low | **Accepted.** `epic:4` dropped from the fail-capable gate's Blocks (it was already transitively blocked). The findings-heading and epistemic-marker normalisation is folded into the C15 amendment pass. | `main-session` | `resolved` |
