---
type: Finding
okf_spec: OKF-PLAN
id: exp-005
description: Is a parallel-lens plan-review wisp buildable without `waits-for`, and is parallelism evidenced?
---

# EXP-005 — the review wisp: buildable, and unevidenced

## Approach Tested

Re-verified `bd dep add --type` on bd 1.1.2. Recovered the formula-step schema from all three shipped
formulas. **Built a candidate `plan-review.formula.toml` in a throwaway sandbox** (`mktemp -d`,
`git init`, `bd init` — an isolated embedded-Dolt DB, never the project DB), cooked it, poured it as a
wisp, and drove the readiness frontier step by step. Empirically tested whether `until`/`validates`
gate readiness. Tested `bd mol burn` mid-flight. Counted concern rows across every `pass-N.md` in
plan-047/048/049/050. Sandbox deleted; repo clean.

## Result

### Q1 — BUILDABLE. The named blocker was not real.

**measured:** `waits-for` does not exist — confirmed independently. And only `blocks` gates readiness:

| edge type | consumer appears in `bd ready` |
| :-- | :-- |
| `until` | **yes** — does NOT block |
| `validates` | **yes** — does NOT block |
| `tracks` | **yes** — does NOT block |
| `blocks` | **no** — blocks |

**inferred:** `until` and `validates` are **not** the join primitive under another name; they are
non-blocking semantic edges. Corroborated by `bd gate create --help`, whose gate types are
`human|timer|gh:run|gh:pr` with no `until` dep edge anywhere in the gate machinery.

**measured — the load-bearing spike.** The formula schema's `[[steps]]` carries **`needs = [...]`, an
ARRAY**, so multi-parent fan-in is first-class. A 6-step conformance → 3 lenses → join → gate formula
cooked and poured (`✓ Created wisp: 8 issues`), then driven:

| State | Ready set |
| :-- | :-- |
| fresh wisp | `conformance` only |
| conformance closed | **all 3 lenses**, reported as `⚡ Parallel Groups: group-1` |
| **2 of 3 arms closed** | only the remaining arm — **`join` ABSENT** |
| 3 of 3 arms closed | **`join` READY** |

`bd dep list <join>` → three `via blocks` edges plus one `via parent-child`. **`needs` compiles to
exactly `blocks` + `parent-child`.** The join is fully expressible today; `waits-for` would have been
a synonym for the multi-parent `blocks` set.

### Q2 — NO EVIDENCE. The cited series measures a different variable.

**measured:** independently recounted concern rows (excluding the Resolutions table, which reuses
`| C1 |` prefixes):

```
pass-1: 5   pass-2: 4   pass-3: 11  pass-4: 17  pass-5: 14  pass-6: 15  pass-7: 10
pass-8: 9   pass-9: 6   pass-10: 14 pass-11: 12 pass-12: 5  pass-13: 2
```

The cited 5 → 4 → 11 → 17 → 14 is **exact**. What each pass says about its own reviewer:

- pass-1: *"Performed in-session by the main session rather than by the `red-team` sub-agent"*
- pass-3: *"**First independent reviewer** … dispatched via the `Agent` tool"*
- pass-4 … pass-13: *"Second … Eleventh independent pass"*

**inferred:** the discontinuity at pass 3 is **exactly** the self-review → independent-reviewer
boundary. All 13 passes were **one reviewer, sequential**, and every pass from 2 onward verifies the
*previous* pass's resolutions — a chain. The series has **zero variation in reviewer count per
cycle**, so it cannot bear on parallelism. Corroborated across plan-047 (4 passes), plan-048 (7) and
plan-049 (5): **29 passes across four plans, none concurrent.**

**measured: there is no parallel-lens data in this corpus.** What exists is a *serialized* two-role
design (`SKILL.md:486` — *"Two passes, in order"*), and a **criticism** of it
(`docs/research/003-…/cluster-yf-codebase.md:295`, headed *"review is a chain, not a fan-out"*) — an
argument from structure, not a result. No pass in any plan was ever assigned a lens other than
"verify the previous pass."

### A risk the proposal did not raise

**inferred:** **parallel lenses lose the chain property.** Every pass from 2 onward exists to verify
the previous pass's *resolutions*. Concurrent arms cannot do that — they all see the same
pre-resolution artifact. Fan-out replaces *"did the fix land?"* with *"three opinions on the same
draft"*: a different, arguably weaker instrument. Nothing measured tells us which is better. Given
that **8 of 13 of plan-050's passes found a defect INJECTED by the previous pass's fix**, the chain
property is not incidental.

### A live automation hazard, independent of all of the above

**measured:** `bd mol burn <id>` on a wisp with every step open — **including an open APPROVE gate** —
prompts `Continue? [y/N]` and **exits 0 on "Canceled."** A scripted caller that ignores stdin gets a
silent no-op with a success exit code. `--force` is required to actually burn. `--dry-run` listed all
8 issues including the open gate with **no warning**.

## Implications for Plan

- The proposal's stated blocker was **not** a blocker; and the recommendation that named `waits-for`
  was written by something that had not read the schema. **Its other claims deserve the same
  scepticism** — which is why Q2 was tested rather than assumed.
- The proposal bundles two separable things: **(a)** giving Phase 3 a bead representation at all —
  mechanically sound and cheap; and **(b)** making the arms parallel and differently-lensed — **no
  supporting evidence**, sold with a series that measures a different variable.
- `bd mol burn`'s exit-0-on-cancel is a hazard for **any** wisp-based Phase 3.

## Recommendations

1. **Q1: BUILDABLE** with multi-parent `needs` (compiling to `blocks`). Drop `waits-for` entirely.
   Do not reach for `until` or `validates` — measured, neither gates readiness.
2. **Q2: NO EVIDENCE.** Decline the parallel-lens claim for plan-051; adopting it would be a
   structural change on an argument from plausibility, which the investigator contract forbids.
3. **If parallelism is wanted, run it as a MEASURED experiment in a later plan** — one cycle with
   N=3 concurrent lenses, comparing unique-concern yield and overlap against the sequential baseline
   this corpus already provides (29 passes, four plans). The baseline is unusually good and the
   mechanism demonstrably works.
4. **File the `bd mol burn` exit-0-on-cancel hazard upstream.** Any scripted burn needs `--force` and
   must check output, not the exit code.
