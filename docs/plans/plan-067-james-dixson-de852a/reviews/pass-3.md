---
type: Review
okf_spec: OKF-PLAN
description: "Red-team pass 3: APPROVE. No phantoms — all 15 pass-2 resolutions verified in the file bytes. Seven concerns, none high, none blocking."
id: pass-3
plan: plan-067-james-dixson-de852a
created: 2026-09-07
verdict: APPROVE
---
# Red-team pass 3 — plan-067-james-dixson-de852a

## Verdict: APPROVE

Cycle 3. **No phantoms this pass** — all 15 pass-2 resolutions verified against the actual bytes of
`plan.md`, `upstream-triage.md` and `index.md`. Every mechanical gate green, no criterion passes
before work, and the C3 fix is reachable. Seven concerns remain, **none high**.

## Mechanical gates (executed, fields read back)

`audit` **pass, 0 findings**, `okf_native: true` · `ready-check` not ready **only** because the last
verdict is REVISE; `audit_status: pass` · `plan_extract --strict` **7/44/58/6/32/13/7, unparsed 0,
recovered 0** · `doc_lint` **PASS, 0 E, 5 W** (exactly the derived uncovered list) ·
`gate_consistency` **PASS, 6 gates** · `recheck-criteria` **30 clause FALSE, 2 manual, 0 malformed**
· own DAG walk **0 cycles / 0 self-edges / 0 dangling / 0 duplicate ids / 0 duplicate edges** ·
uncovered list **matches the extractor exactly**, `coverage − issues = ∅` · **REQ-PORT-006: 2 ≡ 2**.

**C3 is reachable, and the exact trap was checked.** `test_negative_controls.py` has no `--require`
today (it has `--checker`/`--min-checkers`), so the gate command exits 2 — argparse rejection. Issue
1.5 explicitly builds it, 1.5 is in Epic 1, and the gate blocks `epic:2`. **Unsatisfiable now,
satisfiable by construction after 1.5** — the correct shape, not a never-passing criterion.

## Spikes (sandbox, no residue)

**SC18 is achievable — measured 6 of 6.** `render.py check-dir` treats staleness as advisory only,
so no byte-compare exists in the toolchain and SC18 could plausibly have been unreachable.
Rendering all six under `d2 v0.8.2 --theme 0 --layout elk`: every PNG byte-identical to the
committed one, two consecutive renders sharing a sha256. It also independently confirms the `elk`
pin is intact.

**The measured factual base verifies.** Issue 0.1's *scoped* grep returns exactly the **5** live
sites including the `SPEC.md:94` fifth; the unscoped form sweeps **14** — C5's fix is real. Issue
0.3's derived set is exactly the 6 named. `user-invocable` absent from exactly the 4 markdown
skills. `## Invocation` absent from 12 of 20. `lander` 0 hits in `workflows.md`. `prune-private`,
`--prune-formulas`, `owner_on_create` and `upstream.py mappings` have **0 hits** anywhere in
`web/content` or `README.md`, while both `--force` flags exist in `cli.rs` — so SC8's "a token
predicate cannot flag it" and SC14's "still an editorial omission" are both correct and not in
conflict.

## Strengths

- **The established failure mode did not recur.** All 15 pass-2 fixes present in file text.
- **Gate placement is right on all four capability gates** — each gate's evidence is produced
  entirely outside its own Blocks set, and each sits at the earliest mutating step its evidence
  permits. 3.1/3.2 are DAG roots, so the operator's read is bought as early as possible.
- **The uncovered list is derived and re-derived after each remediation**, two cycles running —
  plan-066's pass-3 C8 defect is not repeated.
- **The plan records what was REFUTED, not just what survived.** D1, D4b, D6 and R5 all carry struck
  claims with the measurement that killed them. A fourth reader can audit the reasoning rather than
  inherit it.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | medium | **Issue 1.4's source of truth is over-broad and would manufacture the false-positive burst R1/R7 exist to prevent.** `ls skills/*/agents/*.md` returns **23** files across 6 skills, but `workflows.md`'s subtitle scopes it to the yf-plan and yf-research pipelines — 16 files. Measured: a name-based extractor surfaces **4** out-of-scope agents, a path-based one **7**, against **1** real finding — an **80-87% artifact rate**. 1.4 is the only new checker with no artifact-rate statement, while 1.3 pre-measures its ~40%. | Scope to `skills/{yf-plan,yf-research}/agents/*.md`, restate the baseline as **15 of 16** with `lander` the single absence, and state the exclusion inline as Issue 0.1 now does. |
| C2 | low-medium | **C10's fix landed in Issue 0.3 but not in SC2, which still hardcodes "all 6".** 0.3 was restated as derived precisely because the six were computed under the bug 0.4 fixes. Compounding: 0.4 leaves the remedy an unresolved either/or, and the branches disagree — populate-all-20 flips `yf-markdown-format` to `true` and the set becomes **seven**. C12's class with the arrow reversed. | Restate SC2 and R2 in derived form; have 0.4 name its branch. |
| C3 | low-medium | **SC26b claims plan-066's criteria hold "on the post-plan-067 tree", but Issue 6.0 runs before Epic 5 exists** (`depends-on: 4.1, 4.2, 4.4b`). Epic 5 then adds generated diagrams and modifies `skill_pages.py` — both plausible ways to move plan-066's criteria after 6.0 declared them repaired. | Add `depends-on: 5.5, 5.6` to Issue 6.0 (no cycle). |
| C4 | low-medium | **Half of pass-2 C11's recommendation was not actioned** — and the table did not claim it, so this is an unfinished recommendation, not a phantom. The spikes README still reads "re-derivation from a specification, not speculation", the exact claim the independent rebuild refuted (9 trivial not 8, `yf-plan` 34/33 vs 26/6). `index.md` routes cold readers straight at it. | One sentence: the census is model-dependent because the finding never defines a node or an edge, which is why Issue 5.0 re-derives it. |
| C5 | low | **Three of the four pinned checker filenames are declared nowhere but the gate and SC10.** An agent implementing 1.3 against the edge name would plausibly write `check_web_cli_surface.py` and silently break the gate. | Name the script path in the text of 1.2, 1.3 and 1.4. |
| C6 | low | **`Resolved By` is `_TBD_` for #247 and #263, but neither is undetermined** — their in-scope halves are 1.3 and 1.1b, stated one column to the left. Three partials, two notations, two unfilled fields, in a plan whose review history is about unfilled fields. | Set them; reserve `—` for #317, which genuinely has no discharger here. |
| C7 | low | **Editing residue, none load-bearing.** The archify gate's Instructions contains *"Never resolve this on the agent's own read"* **twice** verbatim; no blank line before the next gate heading; Issue 1.1b has two `depends-on:` bullets straddling its `resolves-upstream:`; Epic 5 declares `5.1…5.4, 5.0, 5.5, 5.7, 5.6`. | De-duplicate, add the blank line, merge the bullets. The ordering matches the house `4.4b` convention and can stay. |

## Missing

- Nothing that blocks execution. The one genuine gap is C1's: `e-web-agents-set` is the only new
  checker whose artifact rate is neither measured nor bounded.
- No statement of what happens if Issue 5.0's threshold lands somewhere other than `nodes >= 5`.
  SC23 is correctly written to survive it, but 5.5's parenthetical and R4 still read as if 5 is the
  answer.
- `diagrams/` is empty and unreferenced by `index.md` — harmless, noted only because SC25b now
  asserts index completeness.

## Gate Assessment

Six gates, **PASS** on both arms, confirmed by hand walk. **Fail-capable** (`epic:2`) — evidence is
1.5, outside the Blocks set; no frontloading miss; C3's arithmetic trap is gone because a name list
cannot be broken by `CONTROLS` cardinality. **archify trial** (`4.1`) — evidence is 3.1/3.2/3.3, all
DAG roots; the three-outcome branch closes C8 and **no verdict strands the plan**. **Diagram human
read** (`6.4`) and **Upstream write authorization** (`6.5`) — both correctly late, their evidence
being the finished work.

## Upstream Assessment

Sound, and **sourced in two places that agree** — C2's single-file fix is genuinely double-landed.
All four `include`s have a named discharger (#373→6.5, #376→1.1b, #375→4.2, #374→5.7), each with a
matching `resolves-upstream` line, and all four appear in 6.5's reconcile list. The three partials
are correctly scoped; #317's "this plan does not close it, Issue 6.4 is the declared handoff" is
exactly the right claim. Only residue is C6's two cells.

## Resolutions

All 7 resolved by the main session, though none blocked approval.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | medium | **Fixed.** Issue 1.4 scoped to `skills/{yf-plan,yf-research}/agents/*.md` — what `workflows.md`'s own subtitle covers — with the baseline restated as **15 of 16**, `lander` the single absence, and the 80-87% artifact rate of the unscoped form recorded inline as the reason. It now matches the standard 1.3 already met. | `main-session` | `resolved` |
| C2 | low-medium | **Fixed.** SC2 and R2 restated in derived form ("every `user-invocable: true` skill lacking it at 0.4's resolution"), and **Issue 0.4 now names its branch**: populate all 20, with the consequence stated — that flips `yf-markdown-format` to `true` and makes 0.3's set seven. | `main-session` | `resolved` |
| C3 | low-medium | **Fixed.** Issue 6.0 now `depends-on: 4.1, 4.2, 4.4b, 5.5, 5.6, 5.7`, so plan-066's re-check sees the generated diagrams and the `skill_pages.py` change. Verified acyclic. | `main-session` | `resolved` |
| C4 | low-medium | **Fixed.** The spikes README now states that the *approach* is re-derivable but its **numbers are not** — the finding never defines a node or an edge, so its census is model-dependent — and points at Issue 5.0 as the remedy. The overstatement was mine and is corrected rather than defended. | `main-session` | `resolved` |
| C5 | low | **Fixed.** `check_required_set.py` and `check_cli_to_page.py` named in Issues 1.2 and 1.3; `check_agents_set.py` named in 1.4 as part of the C1 fix. The `CONTROLS` keys and the gate's `--require` list now have one declared source. | `main-session` | `resolved` |
| C6 | low | **Fixed.** #247 → `1.3 (the in-scope half)`, #263 → `1.1b (the in-scope half)`; `—` reserved for #317, which genuinely has no discharger in this plan. | `main-session` | `resolved` |
| C7 | low | **Fixed.** The duplicated gate sentence de-duplicated, the blank line added before the next gate heading, and Issue 1.1b's two `depends-on:` bullets merged into one. Epic 5's declaration order is left as-is per the reviewer's own note that it matches the house `4.4b`/`SC21b` convention. Also actioned the Missing item: R4 now records that the published-set SIZE is provisional until 5.0 re-derives the threshold. | `main-session` | `resolved` |
