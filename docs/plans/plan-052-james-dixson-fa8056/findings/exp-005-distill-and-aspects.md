---
type: Finding
okf_spec: OKF-PLAN
id: exp-005-distill-and-aspects
description: #197's aspects premise is CONFIRMED but its proposal does not work; #196 is refuted as scoped and reduces to ~20 lines.
---

# EXP-005 — aspects are real (#197 premise ✅, proposal ❌); distill is a skeleton (#196 reduced)

**Split verdict.** #197's premise is confirmed with a working end-to-end example, but its
*proposal* targets the one formula it cannot work on. #196 is refuted as scoped and shrinks to a
~20-line schema change.

## Part B — #197: aspects EXIST, and the decisive limit is WHERE they weave

**Confirmed by the main session against the installed binary:**

```
json:"advice,omitempty"   json:"aspects,omitempty"   json:"pointcuts,omitempty"
bd formula list --type string   Filter by type (workflow, expansion, aspect, convoy)
```

**Working example, cooked and poured.** An aspect with `[[pointcuts]] glob` and `[[advice]]
target` + `[advice.after]`, attached via **`[compose] aspects = [...]`** (a *top-level*
`aspects = [...]` is **silently ignored** — measured), took a 2-step workflow to 4:

```
write-plan                                  [from: steps[0]]
write-plan-verify     [needs: write-plan]   [from: advice]
write-context         [needs: write-plan]   [from: steps[1]]
write-context-verify  [needs: write-context][from: advice]
```

After `bd close <write-plan>`, `Verify doc-lint: write-plan` **became ready**. The obligation is a
real, blocking, closable bead — exactly what #197 asks for.

### The limit #197 did not anticipate

**Aspects weave at COOK time, over FORMULA-DECLARED steps only.** A bead created into an
already-poured molecule (`bd create --parent <mol>`) got **no** verify companion.

**yf-plan's execution beads are created exactly that way.** Confirmed by step count:

| Formula | `[[steps]]` declared | An aspect would weave over |
| :-- | --: | :-- |
| `plan-execute.formula.toml` | **1** | `start-gate` **and nothing else** |
| `plan-review.formula.toml` | **4** | `conformance`, `red-team`, `resolve`, `gate` — all of them |

`plan-execute` declares only `start-gate`; every epic and issue is injected dynamically by
`SKILL.md` §4.3 via `bd create --parent/--deps`.

**So #197's proposal — attach a verify child to every `plan-execute` step — does not work.** The
issue's own *fallback* ("the same effect is reachable at injection time in `SKILL.md` §4.3") is
not the expensive alternative; **it is the only route**, and it is a `plan_manager.py` change,
not a formula change. State this in the plan so no one spends a cycle rediscovering it.

**`plan-review` is the cheap, demonstrable win** — 4 real steps, weavable today with **zero
script change**.

## Part A — #196: distill works, and is worth much less than the issue argues

| #196 claim | Verdict |
| :-- | :-- |
| `bd mol distill` exists in bd 1.1.2 | **CONFIRMED** |
| Used ZERO times in any execution path | **CONFIRMED** |
| Referenced exactly once | **REFUTED** — two prose hits (`yf-beads-authoring/SKILL.md:252`, `yf-research/agents/coordinator.md:106`) |

**Distill produces a skeleton.** Parameterised: only `title`/`description` text where a `--var`
was supplied. Frozen: step ids (slugified from the *concrete* titles), `type`, `priority`,
`depends_on`. It cannot produce `phase`, meaningful var descriptions, gate declarations, or
comments — and the repo's hand-written formulas are 60–80% load-bearing rationale that JSON
cannot carry.

**A silent-green defect INSIDE distill** — `--var` substitution is `\b`-anchored, so a value that
does not begin *and* end with a word character substitutes **nothing** and still **exits 0**:

| `--var` value | substitutions | exit |
| :-- | --: | --: |
| `_shared` | 9 | 0 |
| `_shared/` | **0** | **0** |
| `its source.` | **0** | **0** |

Any path ending in `/`; any sentence ending in `.`. Output says `Distilled formula` either way.
**This is plan-050 RE-003's shape exactly** — a control reporting clean while doing nothing —
found inside the tool proposed to fix that class.

**Round trip is LOSSY for gates.** Pouring `plan-review` then distilling it back turned a declared
`gate` step into a plain **`task`**, plus a synthetic `gate-human` sibling carrying
`"type": "gate"` and no `[steps.gate]` block — which itself pours as a task, silently.

**The corpus is thinner than #196 implies.** plan-050: 9 entries, **2** non-empty `prevention`.
plan-051: 6 entries, **0**. `prevention` is unconstrained free text read by **0** consumers, and
both populated values read as "recommend a dedicated pass" — a *plan*, not a molecule.

## Implications

| # | Implication |
| :-- | :-- |
| I-1 | **#197 proceeds, RE-SCOPED.** (a) `[compose] aspects` on `plan-review` — zero script change, one commit. (b) For `plan-execute`, injection-time `bd create` in §4.3 — the only route, not a fallback |
| I-2 | **#196 is REFUTED AS SCOPED.** Do not build "distill the first epic that performs a remediation shape." Reduce to: add `prevention_formula` (enum-checked against `bd formula list`) + `prevention_vars` to `RETROSPECTIVE_FIELDS`, leaving `prevention` as prose. ~20 lines, and it is the actual gap |
| I-3 | **Hand-write any formula this plan ships; never distill it** — distill loses gates, freezes ids, drops every comment |
| I-4 | **Three upstream bd defects to file**, independent of #196/#197: (i) `distill --var` silently substitutes nothing and exits 0; (ii) a step with `type = "gate"` and no `[steps.gate]` pours as a plain task with no diagnostic; (iii) distill cannot reconstruct gate steps, making it non-idempotent against bd's own pour |
| I-5 | **Use `[compose] aspects`, never top-level `aspects`** — the top-level form is silently ignored |
