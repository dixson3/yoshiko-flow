---
type: Review
okf_spec: OKF-PLAN
description: "Red-team pass 2: REVISE, 15 concerns. Two phantom resolutions, and pass-1's --min-checkers 8 floor measured UNREACHABLE — an always-passing criterion replaced by a never-passing one."
id: pass-2
plan: plan-067-james-dixson-de852a
created: 2026-09-07
verdict: REVISE
---
# Red-team pass 2 — plan-067-james-dixson-de852a

## Verdict: REVISE

15 concerns (5 high, 3 medium-high, 5 medium, 2 low-medium). **Two are phantom resolutions.**
**One makes the plan uncompletable by construction.**

> The artifact moved mid-review; three self-inflicted dagre phantoms (D6, the gate, SC17) were
> repaired by the main session between the reviewer's first and second read. **SC18 was not**, and
> is C6 below.

## Mechanical gates (executed, fields read back)

`audit` **pass, 0 findings** · `ready-check` not ready (REVISE, pass 1) · `plan_extract --strict`
**7/42/52/6/30, 0 unparsed** · `doc_lint` **PASS, 0 E** · `gate_consistency` **PASS, 6 gates** ·
own DAG walk **0 cycles / 0 self-edges / 0 dangling / 0 duplicate ids** · uncovered list **matches
the extractor exactly** · `recheck-criteria` **28 FALSE, 2 manual, 0 malformed**.

**Nothing passes before work, and the C4 fix was measured effective:** `--min-checkers 4` exits 0
today (pass-1's defect reproduced); at 8 it exits 1. Both `manual:` rows parse.

## Strengths

- The mechanical surface is genuinely green and the uncovered list is **derived, not asserted** —
  plan-066's pass-3 defect is not repeated.
- **C4's fix is real, not cosmetic** — the reviewer reproduced both sides of the floor.
- Issue 0.3's six skills verify exactly (11 `user-invocable: true` ∖ 5 with `## Invocation`).
- EXP-004's incidental find verifies precisely: `user-invocable` absent from exactly four skills,
  and they are exactly the four markdown skills.
- The new archify gate's instructions are the strongest prose in the plan.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **PHANTOM — pass-1 C3 never touched D1.** It still reads *"archify is REJECTED entirely — not adopted, and not retained for exploration"* with all four disqualifiers intact. It therefore contradicts **D6**, **Epic 3 in its entirety**, and the **EXP-001 summary row three rows below it**. A cold reader hits the flat rejection first and never reaches the reversal. | Rewrite D1 to the two surviving grounds, strike the three refuted claims in place, and state archify is retained for the Epic 3 trial. |
| C2 | high | **PHANTOM — `upstream-triage.md` is still entirely unfilled.** All seven Disposition and Notes fields blank. C7's resolution claimed the triage was populated; only `plan.md`'s table was. `index.md` names that file as *"the triage record behind plan.md's table"*, so the dispositions are unsourced. | Fill all seven. A fix applied to one document and claimed across two is the plan-066 pattern this pass exists to catch. |
| C3 | high | **The `--min-checkers 8` floor is UNREACHABLE, so Epic 2 is permanently blocked.** `CONTROLS` is keyed by script filename, 4 entries. A floor of 8 needs four NEW scripts — but 1.1 **modifies `check_web_counts.py`, already one of the four**. Maximum reachable is **7**. Pass-1's C4 fix replaced an always-passing criterion with a never-passing one. | Pin the gate to the new checkers **by name** — a name list cannot be satisfied by inheritance nor broken by arithmetic. |
| C4 | high | **#374 and #375 are `include` with nothing resolving them.** #375's Notes assign it to Issue 4.2, whose text never mentions the literal and which carries no `resolves-upstream`; #374 has **no owning issue at all** and is omitted from 6.5's reconcile list. `doc_lint` flags both at `W`. C8's defect class reintroduced by C7's fix, on two issues. | Give #375 a sub-task in 4.2 with a clause in SC20; give #374 an owning issue; add it to 6.5; fill the four `_TBD_` cells. |
| C5 | high | **Issue 0.1's derived `grep -rl` is unscoped and sweeps six files that must not be edited.** Three are **plan-053 pre-fix negative-control fixtures whose purpose is to stay broken** (`ctl-208-vocab-pre-fix`, `ctl-209-pre-fix`, `ctl-214-pre-fix`); three are historical plan-026 documents. A green SC1 would require rewriting all eleven. C9 traded a hardcoded undercount for a derived overcount that breaks another plan's controls. | Scope the grep to `skills/**` and `web/content/**`, excluding `docs/plans/**` and `**/fixtures/**`, and state the exclusion in the issue. |
| C6 | medium-high | **SC18 is stale dagre residue and now unsatisfiable** — *"The pin changed at every site"*, discharged-by 3.2, which now builds under the **unchanged** pin. Worse, it makes 3.2 look covered, hiding it from the uncovered list. | Rewrite SC18 to what 3.2 delivers, and re-derive the uncovered list. |
| C7 | medium-high | **Issue 4.4 lost its dependency entirely.** Every other Epic 4 issue was re-pointed `3.2 → 2.6`; 4.4 was left with **no `depends-on` at all** and is now a DAG root — buildable before the rule lands. Its sibling 4.4b correctly depends on 2.6, so the two halves of one deliverable sit on opposite sides of the plan. | Add `depends-on: 2.6`. |
| C8 | medium-high | **The archify gate offers three outcomes and the plan can execute two.** There is no branch for *adopt*: 4.1 rebuilds `architecture.d2`, SC19 greps it, the node and globs key on `*.d2`, and 3.3 itself states archify has no d2 input path. An adopt verdict strands Epics 4 and 5. | Declare adoption out of scope (trial reports; adoption filed upstream), or add the branch. As written the gate can return an answer the plan cannot act on. |
| C9 | medium | **Epic 3 can repeat D6's own sampling error one level up.** The comparison uses the sparse `exp001` draft, which carries none of SC19's load — the tool layer, 12 `yf` paths, 10 skill edges. The plan just recorded "a layout judgement needs the whole corpus" then commissioned a one-sample judgement. Also unstated: whether 3.2's output feeds 4.1 or is discarded. | Build at 4.1's declared content load, or scope the verdict explicitly. Say what happens to 3.2's output. |
| C10 | medium | **Issue 0.3's set is computed under the very bug 0.4 fixes, and does not depend on it.** If `yf-markdown-format` becomes `user-invocable: true`, the set is **seven**, not six — and `1.2 → 0.3` inherits the stale set into the checker. | Add `depends-on: 0.4` and restate the set as derived. |
| C11 | medium | **Epic 5's threshold constants are not reproducible from EXP-004's written spec.** An independent rebuild got **9 trivial not 8**, **no zero-edge skill**, and `yf-plan` at **34/33 vs the reported 26/6** — the finding never defines a node or an edge. `nodes >= 5` sits on a **three-way tie**. The approach survives the artifact loss; the measured justification does not. | Add an Issue 5.0 that rebuilds the census and re-derives the threshold, and state the node/edge definition. Amend the spikes README — "re-derivation from a specification" overstates what the specification contains. |
| C12 | medium | **D4b contradicts SC8 and Issue 1.3** — it still claims the direction catches "both `--force` flags", the exact claim C5 refuted. Same half-landed pattern as C1: the criterion was fixed, the decision record was not. | Strike the claim and cite the measurement. |
| C13 | medium | **`index.md` omits every artifact a cold reader needs** — no entry for the 4 findings, 7 references, `reviews/`, or `assets/spikes/`, while its own boilerplate promises them. | Add them with answer-carrying descriptions, matching plan-066. |
| C14 | low-medium | **SPEC-first applied to three changes, skipped for two** — nothing covers Epic 1's headline omission rule or 1.4's new edge. `check_amendment_log` derives its id set from what the plan names, so SC4 passes while two behavior changes go untagged. | Name `REQ-CHECK-013` and `-014`; add `depends-on: 0.5` to 1.1. |
| C15 | low-medium | **Epic 3 names no output paths, so SC21c cannot be written.** Also, 3.1's raster comes from `visual-check`, which is a **full-page viewer screenshot including the title bar and Export button** — worth saying inline. | Name the paths; note the caveat. |

## Missing

- No branch for an "adopt archify" verdict (C8) — the outcome the operator's redirect makes most likely to matter.
- No issue for #374; no criterion for #375's literal (C4).
- **No record of the pass-1 remediation in `log.md`** — 38→42 issues left no trace.
- No statement of the node/edge model Epic 5 generates over (C11).
- 26 of 28 clause criteria exit 2 by design (0.6 authors them), but no subcommand has been proven writable; SC5's `verbs-match` is the only thing binding 26 names to 26 implementations.

## Gate Assessment

`gate_consistency` **PASS, 6 gates**; no gate depends on evidence inside its own Blocks set, and
C12's frontloading fix is real — 3.1/3.2 are now DAG roots. Two problems remain, **neither
reachability**: the fail-capable gate's test **can never pass** (C3, an arithmetic error inside a
script's registry), and the archify gate **admits a verdict the plan cannot execute** (C8).
`gate_consistency` sees neither.

## Upstream Assessment

Better than pass 1, but **confined to one file**. `plan.md`'s table is a genuine fix; beneath it
`upstream-triage.md` is untouched (C2), all four `include` rows carry `_TBD_`, and only **two of
four** `include`s are discharged by an issue. The three partials are well-scoped and correct.

## Resolutions

All 15 resolved by the main session.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Fixed — and this was a phantom my own self-check missed.** I tested "Epic 3 = archify trial" and "elk retained" but never tested D1 itself; the C3 substitutions were dropped when I restructured the remediation script and nothing asserted they landed. D1 is now rewritten to the two surviving grounds with the three refuted claims **struck in place**, and states archify is retained for the trial. | `main-session` | `resolved` |
| C2 | high | **Fixed.** All seven dispositions and notes written into `upstream-triage.md`, so `plan.md`'s table is sourced rather than free-standing. Verified: 0 blank Disposition fields, 7 filled. | `main-session` | `resolved` |
| C3 | high | **Fixed, and the arithmetic verified.** `CONTROLS` holds 4 entries; 1.1 only *modifies* `check_web_counts.py`, so the maximum reachable is **7** and the floor of 8 could never pass. The gate and SC10 now pin **four checkers by name** (`--require check_web_counts.py,check_required_set.py,check_cli_to_page.py,check_agents_set.py`), and Issue 1.5 requires each to register under its own name. A name list cannot be satisfied by inheritance nor broken by arithmetic. | `main-session` | `resolved` |
| C4 | high | **Fixed.** #375 gets an explicit sub-task in Issue 4.2 plus `resolves-upstream`, and SC20 now asserts the real literal `system_deps_missing`. #374 gets a new owning Issue 5.7 (the guard must reject a zero-byte page — Epic 5's *generated* pages are exactly what could be emitted empty) plus new SC24b. Both added to 6.5's reconcile list; all four `Resolved By` cells filled. | `main-session` | `resolved` |
| C5 | high | **Fixed, and the sweep verified.** I ran the unscoped grep: it matches the three plan-053 `ctl-*-pre-fix` fixtures and three plan-026 historicals alongside the five live sites. Issue 0.1 now scopes the derivation to `skills/**` and `web/content/**` with the exclusion and its reason stated inline, so an executing agent cannot rediscover it by destroying another plan's controls. | `main-session` | `resolved` |
| C6 | medium-high | **Fixed.** SC18 rewritten to what 3.2 actually delivers — the d2 side built under the **unchanged** pin, with the corpus still byte-identical to a fresh render. The uncovered list was re-derived afterwards and grew to five. | `main-session` | `resolved` |
| C7 | medium-high | **Fixed.** `depends-on: 2.6` added to Issue 4.4. The edge had been deleted rather than re-pointed. | `main-session` | `resolved` |
| C8 | medium-high | **Fixed.** The gate now states all three outcomes explicitly: drop and keep-for-exploration proceed with d2 unchanged; **adopt is out of scope for this plan** and is filed upstream as a toolchain migration, because every downstream artifact keys on `*.d2` and archify has no d2 input path. The redesign continues in d2 whichever the operator picks, so no verdict can strand it. | `main-session` | `resolved` |
| C9 | medium | **Fixed.** Issue 3.1 now builds **at 4.1's full declared content load** — the tool layer, 12 `yf` paths, 10 skill edges — with the reason stated: a sparse-draft verdict would repeat D6's sampling error one level up, and archify's `--quality` solver is what pressure-tests under density. 3.2's output is declared the starting point for 4.1, not a throwaway. | `main-session` | `resolved` |
| C10 | medium | **Fixed.** Issue 0.3 now `depends-on: 0.2, 0.4` and its set is stated as **derived** (`user-invocable: true` ∖ has-`## Invocation`), with the six current names given as the present value rather than the definition. | `main-session` | `resolved` |
| C11 | medium | **Fixed.** New Issue 5.0 rebuilds the census and re-derives the threshold **before** 5.5 fixes a constant, and requires the node/edge definition be stated in the plan. SC23 asserts the definition is stated and the value re-derived. The reviewer's independent rebuild (9 trivial, no zero-edge skill, `yf-plan` 34/33) is recorded as the reason. | `main-session` | `resolved` |
| C12 | medium | **Fixed.** D4b's "and both `--force` flags" is struck in place with the measurement cited, so the decision record now agrees with SC8 and Issue 1.3. | `main-session` | `resolved` |
| C13 | medium | **Fixed.** `index.md` extended with findings, reviews, references and spikes sections, each carrying an answer rather than a filename — including the explicit record of which spike artifacts were lost. New SC25b asserts it stays complete. | `main-session` | `resolved` |
| C14 | low-medium | **Fixed.** `REQ-CHECK-013` (the omission rule) and `REQ-CHECK-014` (the agents-set edge) named in Issue 0.5; Issue 1.1 now carries the spec reference and `depends-on: 0.5`. | `main-session` | `resolved` |
| C15 | low-medium | **Fixed.** Epic 3's three output paths named (`assets/archify-trial/architecture.html`, `.d2`+`.png`, `findings/archify-trial.md`), and the `visual-check` full-page-screenshot caveat stated inline in 3.1 so the comparison is not read as a clean render. | `main-session` | `resolved` |
