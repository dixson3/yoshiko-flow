---
type: Plan
okf_spec: OKF-PLAN
description: 'Diagram set redesign (#373): restack architecture as a layered marketecture
  with per-skill and per-formula diagrams, combine phase-model+lifecycle and install+tune,
  evaluate archify vs d2->png as the rendering toolchain, and amend DRIFT-CHECK so
  omissions FAIL'
id: plan-067-james-dixson-de852a
author: james-dixson
created: '2026-09-07'
status: executing
deliverable_class: standard
fingerprint: c89397ff5cb6cc27990db15cc85f81d584b15401b0fa091815902e4118a25754
epic: yf-mol-gtcy
---
# Plan: Diagram set redesign (#373): restack architecture as a layered marketecture with per-skill and per-formula diagrams, combine phase-model+lifecycle and install+tune, evaluate archify vs d2->png as the rendering toolchain, and amend DRIFT-CHECK so omissions FAIL

**ID:** plan-067-james-dixson-de852a
**Author:** james-dixson
**Created:** 2026-09-07
**Status:** executing
**Deliverable-class:** standard
**Epic:** yf-mol-gtcy
**Fingerprint:** c89397ff5cb6cc27990db15cc85f81d584b15401b0fa091815902e4118a25754

## Objective
Diagram set redesign (#373): restack architecture as a layered marketecture with per-skill and per-formula diagrams, combine phase-model+lifecycle and install+tune, evaluate archify vs d2->png as the rendering toolchain, and amend DRIFT-CHECK so omissions FAIL

## Motivation

**Split from plan-066 at its Diagram human-read gate.** The operator read the six regenerated
PNGs and did not accept them — not because any diagram makes a false claim, but because the set
needs restructuring and because several real relationships are **absent**.

That distinction is the whole reason this plan has two halves.

`DRIFT-CHECK.md:207` holds that a page which **"curates or omits repo-dev detail PASSes — only an
affirmative contradiction FAILs"**. Under that rule an omission is invisible *by construction*.
The measured cost: `land`, retrospectives, the escalation surface, autonomy levels and `closable`
went undocumented across multiple releases and **nothing ever complained**; `architecture.d2`
omitted the entire `workflows` skill group while passing every check. plan-066 repaired those as
editorial work precisely because no edge could have flagged them.

**So a redesign alone re-drifts.** The rule change is what keeps the new diagrams complete.

The six diagrams plan-066 landed are **factually correct and mechanically checked** — the
`beads group` membership bug (count 8 while listing the *workflows* skills), the retired
`lowercase-hyphen,max64` annotation, the absent workflows group and the three-vs-five formula
count are all repaired. This plan is not a correction to them. It is a better set.

**plan-066 is parked in `executing` with its diagram gate shut** and #317 open pending a
retrospective that is gated behind that read. This plan owns the handoff that unblocks it.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #373 | Diagram set redesign + make DRIFT-CHECK omissions FAIL | include | The plan of record. Pass-1 C8 caught two named deliverables silently dropped; both restored (4.4b per-formula diagrams, 4.2 land-the-plane), so `include` is now earned rather than asserted. | 6.5 |
| #376 | check_web_counts: group membership NOT CHECKED where a bullet enumerates no ids | include | **Re-scoped from adjacent to precondition** (pass-1 C6). It is the stated limit in the exact function Issue 1.1 modifies, and it is what would let an omission stay invisible under the new rule. | 1.1b |
| #375 | lifecycle.d2 labels a preflight status `deps-missing` | include | Assigned to Issue 4.2, which merges `lifecycle.d2` — without this the wrong literal is carried forward into the combined diagram. | 4.2 |
| #374 | skill_pages.py authored-page guard is EXISTENCE-only (a zero-byte page builds green) | include | Interacts directly with Epic 5's generated pages and with SC24; a generator emitting an empty page would build green. | 5.7 |
| #317 | Plan 3/3: regenerate user-facing docs | partial | plan-066's tracker, parked behind its Diagram human-read gate. This plan does not close it — Issue 6.4 is the declared handoff that lets the operator open that gate. | — |
| #247 | Drift findings no declared edge covers | partial | In scope: the CLI→page direction (D4b) and the `web-diagram-src` coverage. Out of scope: the remainder of #247's manifest gap. | 1.3 (the in-scope half) |
| #263 | META: "two facts, one signal" | partial | In scope: `not_checked` conflating "no ids enumerated" with "checked and clean" (1.1b). Out of scope: the META class. | 1.1b (the in-scope half) |

## Scoping Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D1 | **KEEP d2 as the committed source of truth. archify is NOT rejected — it is retained for EXPLORATION, and Epic 3 TRIES it on the architecture diagram before any wider decision.** | *(Revised twice: after EXP-001, then again after pass-1 C3 refuted three of the four grounds the first revision rested on. Pass-2 C1 then found this row had never actually been rewritten — the fix was claimed in the resolutions table and applied only to the surrounding prose.)* **THREE OF THE ORIGINAL FOUR GROUNDS ARE STRUCK, recorded rather than deleted, because a plan that rejects an operator's explicit ask must show which claims held:** ~~no headless raster export~~ (**false** — `archify visual-check <html> --json` drives headless Chrome and writes PNGs); ~~unvendorable dev-channel dependency~~ (**false** — MIT, **zero runtime dependencies**, pure ESM; `private: true` blocks only `npm publish`; the self-update manifest has **no call sites**; `cp -R` is the whole procedure); ~~the `--quality showcase` gate pressures deleting member ids~~ (**false** — the constraint fires byte-identically at `standard`, which is the **default, not a demotion**). **THE TWO SURVIVING GROUNDS, which carry the decision alone: (1) CHECKABILITY** — archify's `.html` loses membership (`4 declared unchecked, EXIT=0`), its `.json` throws false-positive FAILs through `check_web_counts`'s region logic, and it has **no d2 input path at all**, so SC10's byte criterion has no clean equivalent; **(2) ORTHOGONALITY** — the omission fix is ~2 lines of checker logic, so no toolchain change buys it. |
| D2 | **Land the omissions-FAIL rule FIRST; its failures become the redesign's work inventory.** | D1's precedent from plan-066, where a checker-derived inventory found 4 defect sites the source issue never listed and corrected an undercount from ~4 to 26. The inverse order lands the rule green by construction, proving nothing about whether it would have caught the omissions it was written for. |
| D3 | **All 20 per-skill diagrams**, one per skill. | Uniform and complete; every skill page can embed its own. Accepts the larger artifact count and maintenance surface as the cost of not having to adjudicate which skills "earn" a diagram. |
| D4 | **REVISED after EXP-002. The v1 required set is SLASH SUB-VERBS ONLY, and it is preceded by a SPEC-first epic normalising `## Invocation` into one parseable shape.** A blanket subset→equal flip is rejected; so is a broad frontmatter-derived set. | EXP-002 measured a required set over the *derivable* classes newly FAILing **17-18 of 20** currently-green pages with **every failure an artifact** — `skill-group` and `depends-on-tool` are emitted by `skill_pages.py:203-217` into the generated "At a glance" block, which `DRIFT-CHECK.md:207` already declares unable to drift. That is a 24-failure false-positive burst that would discredit the check on its first run. **Only slash sub-verbs give a clean signal** (0 generated-data artifacts; the negative control fires and names the removed verb). But `## Invocation` is **not a schema**: absent from 12 of 20 skills, and the 8 that have it use **≥4 incompatible shapes** — so a check keyed on it is silently vacuous for 60% of the corpus. Normalising it is a **prerequisite, not a follow-on**, and it is cheaper and more honest than predicate engineering. **Script-verb coverage is irreducibly editorial** and the plan says so rather than claiming a derived set: `plan_manager.py` carries 40 flat verbs with **zero** visibility metadata, and `spec/cli.md` REQ-CLI-006 frames the entire set as internal delegation. |
| D4b | **Add the missing CLI→page DIRECTION to `e-web-cli-surface`, with a set-difference realizer.** | EXP-003: both of that edge's declared failure directions are page→CLI, so **no check anywhere can see a shipped command that no page documents**. Measured consequence: `yf harness skills prune-private` — live and destructive — is documented nowhere. One new direction catches `prune-private` and `--prune-formulas`. ~~and both `--force` flags~~ — **struck (pass-2 C12)**: `--force` is already documented (`install.md:132`, `README.md:75`), so a corpus-wide token predicate cannot flag it, and a pair-level predicate would contradict the corpus-wide rule. SC8 disowns the claim; this row now agrees with it. |
| D6 | **WITHDRAWN. The `elk` pin STAYS.** Epic 3 instead trials **archify** on the architecture diagram and reports, per the operator's redirect. | *(Originally: re-pin `elk`→`dagre`, gated on an operator read.)* **Pass-1 C1 refuted it by measurement** — all six rendered under both engines gave hard text-on-text collisions on **2 of 6**, larger output on **6 of 6** (+4% to +25%, independently re-measured), semantic ordering discarded on **3**, and dagre **worse on `architecture`**, the diagram the objection was about. EXP-001's recommendation came from **one** sample, `lifecycle` — the single case where the engines are equivalent. **The lesson, recorded because it generalises: a layout judgement needs the whole corpus, not a representative.** The dagre render is kept at `assets/spikes/exp001-dagre-sample.png` as a negative artifact so the sampling error stays inspectable. |
| D7 | **One plan; the mechanical PROSE epics are sequenced AHEAD of the diagram redesign.** | EXP-003: the diagram half's "omissions" are largely design decisions (which of 7 `yf` verbs belongs on a canvas); the prose half is ~52 mechanical repairs against enumerable sets. Holding them in one epic would let the judgement-heavy half block the clean wins. |
| D5 | **This plan unblocks plan-066 at the end.** A dedicated issue hands off: redesigned diagrams land → operator reads → plan-066's gate opens → its 8.1/8.3 run → plan-066 completes and #317 closes. | Leaving plan-066 parked with no declared route to closure is the shape that produced five stale trackers in this repo (#103, #95, #96, #98, #134). |

## Investigation Findings

### Planned experiments (pre-investigation checkpoint)

| # | Question | Why it can change the plan |
| :-- | :-- | :-- |
| EXP-001 | Build the **marketecture restack** in BOTH archify and d2. Are the factual claims (skill counts, group membership, tool dependencies) **mechanically extractable** from each artifact? Is output **deterministic** enough for a byte or structural criterion? What would `check_web_counts` have to become for each? | **This experiment decides D1 and can refute it in either direction.** If archify output is not greppable or not deterministic, adopting it silently undoes plan-066's diagram coverage. If d2 cannot express the layered stack legibly, the redesign is blocked on toolchain regardless of checkability. |
| EXP-002 | What exactly must the **declared required set** contain, and is it derivable rather than hand-maintained? Enumerate the user-facing surfaces a page must document — slash verbs, shipped commands, `skill-group` clusters — and determine whether each has a machine-readable source of truth. | If the set must be hand-authored, D4 reintroduces the hand-maintained-list weakness `check_amendment_log`'s own docstring calls its soundness limit. That changes what the rule can honestly claim. |
| EXP-003 | Run the proposed rule against the CURRENT corpus. How many pages and diagrams fail, and what is the actual work inventory? | D2 makes this inventory the plan's work list. If it is enormous the scope must change; if it is empty the rule is vacuous and does not do what it is for. |
| EXP-004 | For 20 per-skill diagrams: what is the **generation** model — hand-authored, generated from `SKILL.md` frontmatter (`depends-on-tool`, `depends-on-skill`), or hybrid? What does each cost to keep current? | D3 commits to 20 artifacts. If they are hand-authored they become 20 new drift surfaces, which is what this plan exists to reduce. Generated-from-frontmatter would make them incapable of drifting — a materially different plan. |

| Exp | Verdict | The result that changed the plan |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-archify-vs-d2.md) | **Keep d2 — but on TWO grounds, not four** | Pass-1 C3 refuted three of the original four (raster export, vendorability, the quality gate). What survives: archify's HTML **loses membership**, its JSON breaks the region logic, and it has **no d2 input path**. **The decisive result is orthogonality** — the omission fix is ~2 lines of checker logic, so no toolchain change buys it. Its dagre recommendation came from ONE sample and pass-1 C1 refuted it across six. |
| [EXP-002](findings/exp-002-required-set-derivability.md) | **D4 refuted as scoped** | A required set over derivable classes newly FAILs **17-18 of 20** pages with **every failure an artifact**. Only slash sub-verbs give a clean signal — and `## Invocation` is absent from 12 of 20 skills with **≥4 incompatible shapes**, so normalising it is a prerequisite. Script-verb coverage is **irreducibly editorial**: 40 verbs, **zero** visibility metadata. |
| [EXP-003](findings/exp-003-omission-inventory.md) | **73 real omissions** (band 57-114; **193 rejected**) | Ratio 53% real / 17% curation / **30% artifact**. `prune-private` is documented nowhere and unreachable because **no CLI→page direction exists**. Its own slash-verb extractor produced a **false green**, retracted by amendment. |
| [EXP-004](findings/exp-004-per-skill-diagram-model.md) | **Generate, do not hand-author** | 20 hand-authored diagrams would be 20 new drift surfaces; **8 of 20 are trivial**, one has zero edges. The wrappers relation derives at **85%**. Found a **live false claim on the published site** — four skills render "auto-fires" while their descriptions declare a slash trigger. |

**Two of this plan's own instruments returned false greens** (EXP-003's extractor; EXP-001's
one-sample layout recommendation), and pass-1 caught a third defect of the same class in Issue
0.1's hardcoded count. That is why every new checker is gated behind a **code-side** negative
control with a raised vacuity floor.

## Approach

**Order: fix contradictions → normalise the schema → land the rule → repair prose → redesign diagrams → hand back to plan-066.**

The rule lands **before** the repairs (D2), so its failure list *is* the work inventory rather than
a hand-written one — plan-066's D1 precedent, which found 4 defect sites its source issue never
listed. But two live contradictions are fixed **first**, because they FAIL under the *existing*
rule and would otherwise pollute the new failure list with pre-existing noise.

**The required set is drawn from ENUMERABLE sources only.** EXP-003 measured a 3.4× swing —
57 / 73 / 114 / 193 — driven purely by how "documented behavior" is read. The 193 figure (every
`SKILL.md` heading needs a page counterpart) is named here as the **explicitly rejected** reading so
it is not rediscovered mid-execution.

**The predicate is corpus-wide, never per-page.** EXP-003 generated its own false positive proving
this: a page-scoped agent reported `yf doctor --local-only` omitted when it sits at
`yf-beads-init.md:30`. Mechanically, 15 of 20 skills go unmentioned in `usage.md` — a per-page set
would manufacture ~30 false failures on two pages alone.

**Diagrams are GENERATED where they can be.** EXP-004 measured that 20 hand-authored per-skill
diagrams would be 20 new drift surfaces; generated from frontmatter they cannot drift at all, and
`skill_pages.py` already builds the same model.

## Epics

### Epic 0: SPEC-first — schema, semantics, and the instrument
- Issue 0.1: Fix the two live contradictions that FAIL under the CURRENT rule, so they do not pollute the new failure list: the lint-subset count (the web page's **seven** is correct per `yf-markdown-lint/SKILL.md:201`; **every site carrying the 6-element subset string, DERIVED by `grep -rl` **SCOPED TO `skills/**` AND `web/content/**`.** The scope is mandatory, not tidiness (pass-2 C5): an unscoped grep also matches `docs/plans/plan-053-*/assets/fixtures/corpus/ctl-208-vocab-pre-fix/`, `ctl-209-pre-fix/` and `ctl-214-pre-fix/` — **plan-053 pre-fix negative-control fixtures whose entire purpose is to stay broken** — plus three historical plan-026 documents. Repairing those would destroy another plan's controls. Pass-1's C9 fix traded a hardcoded undercount for a derived overcount; the scope is what makes the derivation correct.**. Pass-1 C9 measured **five** sites, not four: the fifth is `yf-skill-authoring/SPEC.md:94`, missed because the phrasing scoped to "SKILL.mds" so a `SPEC.md` fell outside the search shape - **the third instance of this defect class in this plan's own intake**), and `yf-incubator.md:61`'s "beads-free utility skill" against its own `skill-group: workflows` + `depends-on-skill: [yf-beads-extra]`.
- Issue 0.2: **Normalise `## Invocation` into ONE parseable shape** across all skills — the bullet form `- \`/skill verb\` — purpose`, which `yf-plan` already uses and which is the only shape with a single unambiguous parser. Measured: 12 of 20 skills have no such section, and the 8 that do use ≥4 incompatible shapes.
  - depends-on: 0.1
- Issue 0.3: Add `## Invocation` to every `user-invocable: true` skill lacking it. **The set is DERIVED (`user-invocable: true` ∖ has-`## Invocation`), not the six names** — pass-2 C10: those six were computed under the very coercion bug Issue 0.4 fixes, and if `yf-markdown-format` (key absent, no section) becomes `true` the set is **seven**. Currently six: `yf-beads-hygiene`, `yf-beads-init`, `yf-beads-upstream`, `yf-diagram-authoring`, `yf-herdr`, `yf-research`.
  - depends-on: 0.2, 0.4
- Issue 0.4: Fix the `user-invocable` coercion defect, SPEC-first, under **`REQ-CHECK-012`**. `frontmatter.rs:61` types it `Option<bool>` (absent = unknown) while `skill_pages.py:133` coerces absent to `False`, so four markdown skills render as "auto (fires from its description conditions)" while their own descriptions read `TRIGGER when: /yf-markdown-lint invoked`. **This is a live false claim on the published site.** **Take the populate-all-20 branch** and state it: making the reader fail-closed would leave the frontmatter ambiguous, and Issue 0.3's set cardinality depends on which branch is taken (pass-3 C2) — populating flips `yf-markdown-format` to `true`, so 0.3's derived set becomes **seven**, not six.
- Issue 0.5: Amend the drift-engine spec for the required-set semantics and the new CLI→page direction — **Name the ids explicitly - `REQ-CHECK-010` (declared required set: slash-sub-verb scope + vacuity floor) and `REQ-CHECK-011` (the CLI→page direction), `REQ-CHECK-013` (the omission rule itself — Epic 1's headline behavior change), `REQ-CHECK-014` (the `e-web-agents-set` edge)** - plus a root `SPEC.md` amendment-log entry and a tagged test in the same change-set, ahead of code. Pass-1 C10: `check_amendment_log` returns **INCONCLUSIVE - "the derived id set is empty"** when no id is named, making SC4 vacuous.
  - depends-on: 0.2
- Issue 0.6: Author `scripts/checks/plan067_checks.py` — one subcommand per Success Criterion, `argparse(choices=sorted(SUBCOMMANDS))` so an unknown verb exits **2**, plus a `verbs-match` subcommand asserting the table's verb set equals the subcommand set. Never pipe pelican; do not hardcode `web/.venv`.
- Issue 0.7: Record the DECLARED BAND in the plan and in the checker's own output: 57 strict / 73 working / 114 lenient, with **193 named as the rejected reading**.
  - depends-on: 0.6

### Epic 1: The rule — make omissions FAIL
- Issue 1.1: Add the omission check to `check_web_counts.py` (spec: `REQ-CHECK-013`) — `missing = [s for s in truth if s not in members]` beside the existing `wrong` at `:179`. EXP-001 measured the current pipeline exiting **0** on a two-member deletion with the count unchanged.
  - depends-on: 0.5
- Issue 1.1b: Close the `members is None` path (**#376**). Pass-1 C6: `wrong` sits inside the `else` of `if members is None`, so the new check lands in the same branch and a group **enumerating no member ids** goes to `not_checked`, where the omission check never runs. Epic 4 rebuilds every diagram into a shape with *fewer* enumerated labels - the easiest possible way to evade the new rule.
  - depends-on: 1.1, 0.5
  - resolves-upstream: #376 (include)
  - depends-on: 0.5
- Issue 1.2: Implement the slash-sub-verb required set as `scripts/checks/check_required_set.py`, with a **vacuity floor**, so a shape change cannot silently zero it. Scope: every sub-verb a skill's normalised `## Invocation` declares must be named on its web page.
  - depends-on: 0.3, 0.5
- Issue 1.3: Add the **CLI→page direction** to `e-web-cli-surface`, realized by `scripts/checks/check_cli_to_page.py` — a set-difference realizer (`check_skill_page_contract.py`'s shape — an exit code, not a prose edge). **State the predicate explicitly as corpus-wide TOKEN presence**, and exclude **positional arguments**: pass-1 C5 built the realizer and measured clap deriving long flags from *field names*, so a naive extractor missed `--prune-formulas` and a corrected one returned 12 'missing' of which **5 were positionals** - a **~40% artifact rate**. Report that rate before Epic 1 lands.
  - depends-on: 0.5
- Issue 1.4: Add an `e-web-agents-set` edge realized by `scripts/checks/check_agents_set.py` — **scoped to `skills/{yf-plan,yf-research}/agents/*.md`**, which is what `workflows.md`'s own subtitle covers ("the yf-plan and yf-research pipelines and the subagents that run them"). **The scope is mandatory** (pass-3 C1): the unscoped `ls skills/*/agents/*.md` returns **23** files across 6 skills, and a name-based extractor over it surfaces 4 out-of-scope agents while a path-based one surfaces 7 — an **80-87% artifact rate** against 1 real finding. In-scope baseline is **15 of 16**, with `lander` the single absence.
  - depends-on: 0.5
- Issue 1.5: Give every new checker a **code-side negative control** — mutate the source of truth under passing docs, assert non-zero. Register each under its own name in `CONTROLS` and expose a `--require <names>` mode, so the gate pins **specific checkers by name** rather than a count (pass-2 C3).
  - depends-on: 1.1, 1.2, 1.3, 1.4
- Issue 1.6: Declare the `not_checked` classes explicitly — script-verb coverage is **irreducibly editorial** (40 verbs, zero visibility metadata) and generated "At a glance" data is out of scope by construction. State it in the checker's own voice, not only in prose.
  - depends-on: 1.5
- Issue 1.7: Wire the new checks as `CHANGE-VALIDATION.md` rows with §3 globs naming BOTH the doc side and the **source of truth** — `skills/*/SKILL.md`, `yf/src/cli.rs`, `yf/src/harness_desc.rs`. A doc-side-only trigger would not fire on the commit that creates the omission.
  - depends-on: 1.5

### Epic 2: The failure list, and the prose repairs it produces
- Issue 2.1: Run the landed rule over the corpus and record the produced failure list as `findings/omission-inventory.md`. **This list, not EXP-003's table, is what Epic 2 repairs.**
  - depends-on: 1.7
- Issue 2.2: NEGATIVE CONTROL on the inventory — assert every omission EXP-003 named appears in it. An EXP-003 item the rule misses is an **instrument defect**, not an absent defect.
  - depends-on: 2.1
- Issue 2.3: Repair the highest-value omissions — the readers actually blocked today: `yf harness skills prune-private` (destructive, zero docs), `yf self install --force` / `self uninstall --force`, `yf doctor --prune-formulas`, `custom.upstream.owner_on_create`, `upstream.py mappings`.
  - depends-on: 2.2
- Issue 2.4: Repair the partial-coverage items plan-066 left one-page-deep: `--sweep-gates`, `retrospective` / `plan-retrospective` / `RE-NNN`, and the `lander` + `land --dry-run → operator STOP → --apply` mechanic, each currently hitting exactly one file.
  - depends-on: 2.2
- Issue 2.5: Repair the remaining skill-page omissions the inventory reports, concentrated in `yf-beads-authoring` (7), `yf-beads-extra` (5), `yf-beads-upstream` (5), `yf-okf-hygiene` (5), `yf-herdr` (4), `yf-plan` (4).
  - depends-on: 2.2
- Issue 2.6: Re-run every checker; all must exit 0 over the repaired prose.
  - depends-on: 2.3, 2.4, 2.5

### Epic 3: The archify trial on ONE diagram
> **REPLACES the dagre re-pin, which pass-1 C1 REFUTED by measurement.** All six rendered under
> both engines: hard text-on-text collisions on **2 of 6** (`phase-model` stamps `consent` across
> `PHASE 4 INTAKE`; `formulas` strikes a label through `AUTHORED`), larger output on **6 of 6**
> (+4% to +25%, independently re-measured), semantic ordering discarded on **3**, and dagre
> **worse on `architecture`** - the diagram the "too busy" objection was about. EXP-001's
> recommendation came from **one** sample, `lifecycle`, the single case where the engines are
> equivalent. **The pin stays `elk`.** Busyness is addressed by decomposition, which #373 already
> prescribes. Epic 3 has **no dependency on Epic 2** (pass-1 C12) - it reads nothing Epic 2
> produces, so it runs early and the operator's answer arrives before the redesign commits to it.
- Issue 3.1: Build the layered marketecture as an **archify `architecture` spec** — **at Issue 4.1's full declared content load**, not the sparse `exp001-architecture-stack.d2` draft (pass-2 C9): the tool layer, the 12 `yf` subcommand paths, the 12 `depends-on-skill` edges. A legibility verdict on a sparse draft would repeat D6's own sampling error one level up, and archify's `--quality` constraint solver is precisely what pressure-tests under density. Deliver to `assets/archify-trial/architecture.html` and produce a raster via `archify visual-check` — noting inline that this yields a **full-page viewer screenshot including the title bar and Export button**, not a clean render.
  - no-req-required: Epic 3 is a TRIAL that reports a comparison; it amends no requirement. The gate's own text records that *adopt* does not proceed inside this plan — a toolchain migration is filed upstream as its own plan.
- Issue 3.2: Build the **same** diagram in d2 under the current `elk` pin, at the same content load, to `assets/archify-trial/architecture.d2` + `.png`. **This output is the starting point for Issue 4.1**, not a throwaway.
  - no-req-required: builds a comparison artifact under the UNCHANGED `elk` pin. It changes no pin and asserts no new requirement; SC18 asserts exactly that.
- Issue 3.3: Report the comparison for the operator - legibility, whether the enumerated member ids survive, and what a committed archify artifact would cost in checkability. State plainly that archify has **no d2 input path**, so adopting it means either a second authored source or generating both from one model. Write the report to `findings/archify-trial.md`.
  - depends-on: 3.1, 3.2
  - no-req-required: writes a findings report for a human gate. A report is evidence, not a behavior change.

### Epic 4: The diagram redesign
- Issue 4.1: Rebuild `architecture.d2` as a layered marketecture — tool dependencies (`bd`, `gh`, `pandoc`, `d2`, `uv`, `git`, `xelatex`, `herdr`) at the bottom, beads + utility + markdown skills in the middle, workflow skills on top. Measured gaps to close: **5 of 8 declared tool deps absent**, **7 of 12 `yf` subcommand paths absent**, and **0 of 12 `depends-on-skill` edges drawn** *(the plan drafted this as 10; re-measured from frontmatter during Epic 3 it is **12** — the two the count missed are `yf-okf-hygiene → yf-okf` and `yf-optimal-instructions → yf-skill-authoring`. The checker derives the set mechanically, so the criterion was never at risk; the prose was) — including the workflows→utility relationship #373 names.
  - depends-on: 2.6
- Issue 4.2: Combine `phase-model.d2` + `lifecycle.d2` into one. **Fix #375's literal in the same pass** — `lifecycle.d2` labels a preflight status `deps-missing` where the real literal is `system_deps_missing`; merging without fixing carries the wrong literal into the combined diagram. Add adding the red-team review **cycle**, capability gates during EXECUTE, escalations, retrospectives, autonomy tokens, `capture`, **execution**, and **land-the-plane** - the last measured by pass-1 C8 as having **zero hits** anywhere in the draft despite being one of #373's three named additions.
  - depends-on: 2.6
  - resolves-upstream: #375 (include)
- Issue 4.3: Combine `install-matrix.d2` + `tune-matrix.d2`. Note `tune-matrix` measured **0 omissions** — it is correct and is being merged, not repaired. Preserve its `surface_dir` vs `skills_subpath` distinction, which is right and which a naive pass would break.
  - depends-on: 2.6
- Issue 4.4: Add the skills/agents → formulas map #373 asks for.
  - depends-on: 2.6
- Issue 4.4b: Author **one diagram per shipped formula** - `plan-execute`, `plan-investigate`, `plan-review`, `verify-artifact`, `yf-research` - and **remove the meta-diagram** `formulas.d2`, per #373's literal ask. Pass-1 C8: the draft kept it and added only the map, silently dropping a named deliverable while claiming `resolves-upstream: #373 (include)`.
  - depends-on: 2.6
- Issue 4.5: Fix `install-matrix`'s `SkillsCommand` gap — 5 verbs declared, only `install` shown.
  - depends-on: 4.3

### Epic 5: Per-skill diagrams, GENERATED
- Issue 5.1: Factor `_read_skills()` out of `web/plugins/skill_pages.py:120` into a shared model module, so the site page and the diagram provably read one source.
  - depends-on: 0.4
- Issue 5.2: Author the generator — `build_model()` (toolchain-neutral) → `to_d2()` (emitter), reading frontmatter, the reverse dependency graph, `skills/<n>/scripts/`, `_shared/sync.py`'s `REGION_ASSETS`/`WHOLE_FILE_ASSETS` tables, and `agents/`/`formulas/`/`protocols/` listings.
  - depends-on: 5.1
- Issue 5.3: Add one optional `engine:` frontmatter field naming the primary wrappered script — needed for exactly **3** skills (`yf-plan`, `yf-research`, `yf-markdown-format`); the other 17 derive correctly. Do NOT add a field enumerating all wrappered scripts: derivable at 85%, and a hand-listed set goes stale.
  - depends-on: 5.2
- Issue 5.4: Add `--check` to the generator (byte-compare emitted source against committed) and wire it into CHANGE-VALIDATION FAST. **Without this the generator is a convenience, not a guarantee.** Precedent: `_shared/sync.py --check`.
  - depends-on: 5.3
- Issue 5.0: **Rebuild EXP-004's census and re-derive the threshold before any constant is fixed** (pass-2 C11). The prototype is lost, and an independent rebuild from the written finding got **9 trivial not 8**, **no zero-edge skill**, and `yf-plan` at **34/33 against the reported 26/6** — the finding never defines what counts as a node or an edge, so its numbers are model-dependent and the model is gone. **State the node/edge definition in the plan**, then re-derive. `nodes >= 5` currently sits on a **three-way tie** (`yf-change-validation`, `yf-incubator`, `yf-markdown-pdf`), so a one-node definitional difference reclassifies three skills.
  - depends-on: 5.1
- Issue 5.5: Gate publication on a **computed** threshold (re-derived by 5.0, provisionally `nodes >= 5`) so the threshold itself cannot drift and a skill that grows past it gains a diagram automatically. Measured: 8 of 20 are a box plus ≤2 arrows; `yf-drift-check` has zero edges.
  - depends-on: 5.4, 5.0
- Issue 5.7: Fix #374 — `skill_pages.py`'s authored-page guard is **existence-only**, so a zero-byte page builds green with zero warnings. Epic 5's GENERATED pages are exactly the artifacts that could be emitted empty and pass. Make the guard assert non-trivial content.
  - depends-on: 5.2
  - resolves-upstream: #374 (include)
- Issue 5.6: Grid-nest sub-boxes in the emitter — `yf-plan` at 13 scripts currently renders 3104×4532, a single-column stack that reads as a bulleted list rather than a graph.
  - depends-on: 5.2

### Epic 6: Verification, retrospective, and the plan-066 handoff
- Issue 6.0: Re-run plan-066's `recheck-criteria` against the post-plan-067 tree and repair whatever this plan's restructuring broke - amending plan-066's criterion PROSE in the same change-set where the change is legitimate (its SC23/SC24 reference `formulas.d2`, which Issue 4.4b removes). Pass-1 C13: no issue asserted plan-066's criteria survive.
  - depends-on: 4.1, 4.2, 4.4b, 5.5, 5.6, 5.7
- Issue 6.1: Full verification sweep — every checker exits 0, pelican builds clean under `--fatal warnings` unpiped, `render.py check-dir` clean, generator `--check` clean.
  - depends-on: 2.6, 4.1, 4.2, 4.4, 4.5, 5.5, 5.6
- Issue 6.2: Enumerate each Class-B item as CLOSED or FILED WITH AN OWNER, by name — never implied by a green build.
  - depends-on: 6.1
- Issue 6.3: Write `plan-retrospective.md` distinguishing content defects from process defects, with counts, and recording the two instrument false-greens this plan's own experiments produced.
  - depends-on: 6.2
- Issue 6.4: **THE plan-066 HANDOFF.** Present the redesigned diagrams to the operator for the plan-066 Diagram human-read gate. On acceptance plan-066's gate opens, its 8.1/8.3 run, it reaches `complete`, and #317 closes. This issue does NOT resolve that gate — only the operator can.
  - depends-on: 6.1
- Issue 6.5: Reconcile upstream — **#373, #374, #375, #376** per disposition; leave **#247, #263, #317** open as partials (#317 closes only when plan-066 completes, via the Issue 6.4 handoff).
  - depends-on: 6.3, 6.4
  - resolves-upstream: #373 (include)

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Checkers are fail-capable
- Type: auto
- Condition: every new checker has been OBSERVED to fail against a code-side mutation
- Test: uv run scripts/checks/test_negative_controls.py --require check_web_counts.py,check_required_set.py,check_cli_to_page.py,check_agents_set.py
- Blocks: epic:2
- Instructions: Mutate the SOURCE OF TRUTH under passing docs. A doc-side control is insufficient — measured twice in plan-066, and once again in this plan's own EXP-003, whose slash-verb extractor returned green over an input it could not see.

### Capability Gate: archify trial decision
- Type: human
- Condition: the operator has seen the archify and d2 builds of the same diagram side by side, and has decided whether archify is adopted, kept for exploration, or dropped
- Test: manual
- Blocks: 4.1
- Instructions: Present both artifacts plus Issue 3.3's report — legibility, whether the enumerated member ids survive, and the checkability cost of committing an archify artifact. **State the known blocker plainly: archify has NO d2 input path**, so adopting it means either a second authored source or generating both from one model. **Three outcomes, and the plan can act on all three (pass-2 C8).** The gate's evidence is produced entirely by Issues 3.1, 3.2 and 3.3 — none of which this gate blocks. *Drop* and *keep-for-exploration* both proceed with d2 unchanged. *Adopt* does **NOT** proceed inside this plan: every downstream artifact keys on `*.d2` (the `web-diagram-src` node, the CHANGE-VALIDATION §3 globs, the generator's `to_d2()`), and archify has no d2 input path — so adoption is a **toolchain migration to be filed upstream as its own plan**, and the redesign continues in d2 regardless of which of the three the operator picks. Issue 3.3 records the verdict. An inconclusive outcome is also legitimate: record it and proceed. **Never resolve this on the agent's own read** — the operator asked to try archify, and only they can judge the result.
### Capability Gate: Diagram human read
- Type: human
- Condition: each redesigned diagram has been read by a human for the semantic residue no extractor catches
- Test: manual
- Blocks: 6.4
- Instructions: Agent reads are evidence, never a discharge. plan-066 measured a corrected diagram whose count was right and whose membership was wrong.

### Capability Gate: Upstream write authorization
- Type: human
- Condition: the operator has authorized the reconcile writes and any follow-on filings
- Test: manual
- Blocks: 6.5
- Instructions: Present drafted bodies composed with `--body-file -` and a quoted heredoc; verify by reading back, never by exit 0. Never self-authorize.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | The new rule produces a **false-positive burst** that discredits it on first run. **Measured:** a required set over derivable classes newly FAILs 17-18 of 20 pages, every failure an artifact. | high | D4 narrows v1 to slash sub-verbs only (0 generated-data artifacts). Issue 1.6 declares the excluded classes explicitly. |
| R2 | The check is **silently vacuous** — keyed on a section 12 of 20 skills lack, in ≥4 shapes. | high | Issues 0.2/0.3 normalise the schema and add it to **every `user-invocable: true` skill lacking it**, BEFORE the check lands (1.2 depends on 0.3, which depends on 0.4). Vacuity floor in 1.2. |
| R3 | An instrument returns green over input it cannot see. **Measured three times**: plan-066's checker B, and this plan's own EXP-003 slash-verb extractor. | high | Code-side negative controls (1.5), gated. Issue 2.2 asserts every EXP-003 item appears in the produced inventory. |
| R4 | 20 hand-authored per-skill diagrams become 20 new drift surfaces. **And the published-set SIZE is not fixed** — Issue 5.0 re-derives the threshold, so `nodes >= 5` is provisional and the publication set may be larger or smaller than the 12 EXP-004 implied. | high | Epic 5 GENERATES them; 5.4's `--check` is what makes it a guarantee rather than a convenience. |
| R5 | **RETIRED - the dagre re-pin is removed (pass-1 C1).** Kept as a record: a one-diagram sample produced a recommendation a six-diagram measurement refuted. The generalisable lesson is that a layout judgement needs the whole corpus, not a representative. | - | Epic 3 now trials archify on one diagram and **reports**, rather than re-pinning anything. |
| R6 | The inventory is unbounded — the predicate, not the corpus, sets the size (57 → 193). | med | Required set drawn from enumerable sources only; 0.7 records the band and names 193 as REJECTED. |
| R7 | A per-page predicate manufactures ~30 false failures on `usage.md`/`workflows.md` alone. **Self-demonstrated in EXP-003.** | med | The predicate is corpus-wide: "documented somewhere on the site". |
| R8 | Script-verb coverage is claimed as derived when it is editorial. **Measured:** 40 verbs, zero visibility metadata. | med | 1.6 states the limitation in the checker's own voice. The plan claims visibility-in-review, not mechanisation. |
| R9 | The diagram half's judgement calls block the prose half's clean wins. | med | D7: Epics 1-2 precede Epics 3-5; Epic 6.1 depends on both. |
| R10 | A naive "repair all retired paths" pass breaks `tune-matrix`, which is CORRECT. | med | 4.3 states the `surface_dir` vs `skills_subpath` distinction inline; EXP-003 refuted three such hypotheses before they became work. |
| R11 | The `user-invocable` coercion ships a false claim into the generated diagrams too. | med | 0.4 fixes it SPEC-first; 5.1 depends on 0.4. |
| R12 | Fixing the two contradictions late lets them pollute the new failure list. | low | 0.1 is first in the DAG. |
| R13 | plan-066 stays parked with no route to closure — the shape that produced five stale trackers. | med | D5 / Issue 6.4 is the declared handoff. |

## Success Criteria

Every Verification cell is an executable clause discharged by `scripts/checks/plan067_checks.py` (Issue 0.6), except the two marked `manual:` which no command can decide.

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | The two live contradictions are fixed — the lint subset reads seven at **every site the derived set-difference finds** (not a hardcoded four), and `yf-incubator.md` no longer calls a `workflows` skill "beads-free utility" | `uv run scripts/checks/plan067_checks.py contradictions` → exit 0 | 0.1 |
| SC2 | `## Invocation` parses under ONE shape across every skill that declares it, and **every `user-invocable: true` skill lacking it at Issue 0.4's resolution now has it** — stated in the derived form, not as a literal 6, because 0.4's branch can change the cardinality (pass-3 C2) | `uv run scripts/checks/plan067_checks.py invocation-schema` → exit 0 | 0.2, 0.3 |
| SC3 | The `user-invocable` coercion defect is fixed — no skill renders "auto-fires" while its description declares a slash trigger | `uv run scripts/checks/plan067_checks.py user-invocable` → exit 0 | 0.4 |
| SC4 | The drift-engine spec carries the new `REQ-*` ids, a root `SPEC.md` amendment-log entry, and a tagged test | `uv run scripts/check_amendment_log.py --plan plan-067-james-dixson-de852a` → exit 0 | 0.5 |
| SC5 | The criteria table's verb set equals the script's subcommand set | `uv run scripts/checks/plan067_checks.py verbs-match` → exit 0 | 0.6 |
| SC6 | `check_web_counts.py` FAILS on an omission — the two-member deletion that exits 0 today - **and `not_checked == 0` over the corpus**, so a group with no enumerated ids cannot evade the rule | `uv run scripts/checks/plan067_checks.py omission-fails` → exit 0 | 1.1, 1.1b |
| SC7 | The slash-sub-verb required set is live, carries a vacuity floor, and is non-vacuous for every skill declaring `## Invocation` | `uv run scripts/checks/plan067_checks.py required-set` → exit 0 | 1.2 |
| SC8 | The CLI→page direction exists and catches what its **stated predicate** can reach - `prune-private` and `--prune-formulas`. It does **not** claim the `--force` flags: pass-1 C5 measured `--force` as already documented (`install.md:132`, `README.md:75`), so a corpus-wide token predicate cannot flag it, and a pair-level predicate would contradict the corpus-wide rule and reopen R7 | `uv run scripts/checks/plan067_checks.py cli-to-page` → exit 0 | 1.3 |
| SC9 | `e-web-agents-set` exists and the `lander` agent is documented | `uv run scripts/checks/plan067_checks.py agents-set` → exit 0 | 1.4 |
| SC10 | Every checker this plan touches was OBSERVED to fail against a code-side mutation, **pinned BY NAME** — `check_web_counts.py` (modified by 1.1/1.1b), `check_required_set.py` (1.2), `check_cli_to_page.py` (1.3), `check_agents_set.py` (1.4). **A name list, not a count** (pass-2 C3): the `--min-checkers 8` floor pass-1 introduced was **unreachable** — `CONTROLS` holds 4 registered scripts, 1.1 only *modifies* one of them, so the maximum is **7** and the criterion could never pass. Pass-1's C4 fix replaced an always-passing criterion with a never-passing one; a name list cannot be satisfied by inheritance nor broken by arithmetic | `uv run scripts/checks/test_negative_controls.py --require check_web_counts.py,check_required_set.py,check_cli_to_page.py,check_agents_set.py` → exit 0 | 1.5 |
| SC11 | The `not_checked` classes are declared in the checker's own output, not only in prose | `uv run scripts/checks/plan067_checks.py notchecked-declared` → exit 0 | 1.6 |
| SC12 | CHANGE-VALIDATION rows name BOTH the doc side and the source of truth | `uv run scripts/checks/plan067_checks.py cv-rows` → exit 0 | 1.7 |
| SC13 | The produced inventory contains every omission EXP-003 named — an absence is an instrument defect | `uv run scripts/checks/plan067_checks.py inventory-control` → exit 0 | 2.1, 2.2 |
| SC14 | The highest-value omissions are documented — `prune-private`, `--prune-formulas`, both `--force` flags, `owner_on_create`, `mappings` | `uv run scripts/checks/plan067_checks.py high-value` → exit 0 | 2.3 |
| SC15 | The one-page-deep items reach the concept pages — `--sweep-gates`, retrospectives, `lander` | `uv run scripts/checks/plan067_checks.py partial-coverage` → exit 0 | 2.4 |
| SC16 | Every checker exits 0 over the repaired prose | `uv run scripts/checks/plan067_checks.py checkers-green` → exit 0 | 2.5, 2.6 |
| SC17 | The operator was shown both builds of the same diagram and returned a decision on archify — adopt, keep for exploration, or drop | manual: a human must look at two rendered artifacts and judge which communicates better; no command can decide it | 3.3 |
| SC18 | The d2 side of the archify comparison was built under the **unchanged `elk` pin**, and every committed PNG remains byte-identical to a fresh render under it — i.e. the trial changed no pin and left the corpus renderable | `uv run scripts/checks/plan067_checks.py render-bytes-match` → exit 0 | 3.2 |
| SC19 | `architecture.d2` shows the tool layer, the `yf` subcommand paths, and the `depends-on-skill` edges including workflows→utility - **with `not_checked == 0`**, so the redesign cannot pass by dropping enumerated ids | `uv run scripts/checks/plan067_checks.py architecture-complete` → exit 0 | 4.1 |
| SC20 | The two combinations landed; the combined lifecycle carries red-team cycles, gates, escalations, retrospectives, autonomy, `capture`, execution and land-the-plane; **and it uses the real literal `system_deps_missing`, not `deps-missing`** (#375) | `uv run scripts/checks/plan067_checks.py combined-diagrams` → exit 0 | 4.2, 4.3, 4.5 |
| SC21 | The skills/agents → formulas map exists | `uv run scripts/checks/plan067_checks.py formulas-map` → exit 0 | 4.4 |
| SC21b | One diagram per shipped formula exists and the meta-diagram `formulas.d2` is REMOVED, per #373's literal ask | `uv run scripts/checks/plan067_checks.py per-formula-diagrams` → exit 0 | 4.4b |
| SC21c | The archify trial produced a like-for-like comparison and a reported verdict — both artifacts exist and the report names the checkability cost | `uv run scripts/checks/plan067_checks.py archify-trial` → exit 0 | 3.1, 3.2, 3.3 |
| SC22 | Per-skill diagrams are GENERATED, and `--check` proves the committed set matches a fresh generation | `uv run scripts/checks/plan067_checks.py generator-check` → exit 0 | 5.2, 5.4 |
| SC23 | Publication is gated on a computed threshold **whose node/edge definition is stated in the plan and whose value was re-derived by Issue 5.0**, not a hand-maintained list or an inherited constant | `uv run scripts/checks/plan067_checks.py publication-threshold` → exit 0 | 5.5 |
| SC24 | The site builds clean and every generated diagram renders legibly — no single-column stacks | `uv run scripts/checks/plan067_checks.py build-and-render` → exit 0 | 5.6, 6.1 |
| SC24b | A zero-byte generated page can no longer build green — the authored-page guard asserts non-trivial content (#374) | `uv run scripts/checks/plan067_checks.py page-guard` → exit 0 | 5.7 |
| SC25 | Each Class-B item is CLOSED or FILED WITH AN OWNER, enumerated by name | `uv run scripts/checks/plan067_checks.py classb-disposition` → exit 0 | 6.2 |
| SC26 | The retrospective distinguishes content from process defects, with counts, and records the instrument false-greens | `uv run scripts/checks/plan067_checks.py retro-classes` → exit 0 | 6.3 |
| SC25b | The bundle's `index.md` lists every artifact a cold reader needs — findings, references, reviews and spikes — not just the four scaffold files | `uv run scripts/checks/plan067_checks.py index-complete` → exit 0 | 6.3 |
| SC26b | **plan-066's criteria still hold on the post-plan-067 tree.** Epic 4 rebuilds `architecture.d2` (plan-066 SC9) and removes `formulas.d2` (its SC23), and plan-066 re-runs all 26 criteria at close-out | `uv run scripts/checks/plan067_checks.py plan066-still-green` → exit 0 | 6.0 |
| SC27 | The redesigned diagrams were presented to the operator for plan-066's gate | manual: the handoff is an act of presentation, and only the operator can resolve that gate | 6.4 |

**Declared `no-req-required` set — {3.1, 3.2, 3.3}, the whole of Epic 3.** This is the MUTABLE
half of `check_amendment_log.py`'s A2 exemption, and it is declared here (the reviewed artifact)
rather than hardcoded in the instrument, so the comparison is not a constant against itself. Epic
3 is an operator-facing **trial**: it builds two renders of one diagram and reports. The gate it
feeds says in its own text that *adopt* does **not** proceed inside this plan, so there is no
requirement for Epic 3 to amend, and manufacturing a `depends-on` into Epic 0 to satisfy a
reachability check would be exactly the false green this plan exists to close. Each of the three
issues carries its reason inline.

**Deliberately uncovered issues — MECHANICALLY DERIVED, and must match the extractor.** Currently
exactly five: `0.7, 5.0, 5.1, 5.3, 6.5`. plan-066's pass-3 C8 caught a list that disagreed with the
extractor by two while asserting coverage that did not exist, so this list is checked rather than
written — and pass-1 of THIS plan grew it to seven before the missing criteria were added, which is
the same drift caught one cycle earlier. `0.7` (record the band) and `5.1` (factor out the shared
model) are bookkeeping whose effect is asserted by the criteria that execute against them; `5.0` re-derives a census whose
output SC23 then asserts; `5.3` adds an optional field whose absence is legal for 17 of 20 skills; `6.5` is discharged by the
reconcile gate and the §6.4 `verify-reconcile` chain, not by a plan criterion.
