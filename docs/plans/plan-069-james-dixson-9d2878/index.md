---
okf_version: 0.2
---

# plan-069-james-dixson-9d2878

> Plan B of the landing-chain split: the --apply preamble tests, the tty-gate bypass, the executor-bookkeeping guard, the digest journal projection, and the two measurement defects

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [findings/exp-003-digest-exclusion.md](findings/exp-003-digest-exclusion.md) - [finding] Inherited from plan-068's investigation. `yf-jp7z`'s premise CONFIRMED and its remedy REFUTED: the proposed WIDE exclusion blinds the digest to all three foreign-landing classes and lets a conflicting landing validate `pass`. Real scope is five self-mutated facts across four resume points; L4 alone mutates them, not L6; and `predicted_tree` is stable across the landing's own merge, which makes it the detection-bearing field. Read before drafting the digest epic — it constrains the design.
- [findings/exp-004-preamble-coverage.md](findings/exp-004-preamble-coverage.md) - [finding] Inherited from plan-068's investigation. "Zero coverage" refuted as stated: 61.4% of the `--apply` preamble, all happy-path plus exactly one refusal, with all 17 missed statements being refusal bodies. The preamble has NINE steps, not the six `yf-acrn` lists. `#334`'s bypass and its test's vacuity are both confirmed by spike and by line data. Sizes this plan's test epic.
- [references/upstream-334.md](references/upstream-334.md) - Full body of dixson3/yoshiko-flow#334 — `_land_tty_gate(allow_list=[None])` opens the consent gate unconditionally and its test is vacuous. This plan's to fix; deferred here at the plan-068 A/B split.
- [references/upstream-349.md](references/upstream-349.md) - Full body of dixson3/yoshiko-flow#349 — the `land --apply` executor frame sits outside both REQ-LAND-030's wrapper and the test suite. **This plan closes it**; plan-068 dispositioned it `partial` (correction only) and deliberately did not.
- [references/upstream-350.md](references/upstream-350.md) - Full body of dixson3/yoshiko-flow#350 — L16 launders an unreadable unpushed count into `0`, so a failed measurement reads as success. Deferred here at the A/B split; it does not halt, which is what makes it the most dangerous of the landing hazards.
- [references/upstream-352.md](references/upstream-352.md) - Full body of dixson3/yoshiko-flow#352 — `land --dry-run` never checks that a draft body satisfies `requires_mention`, so that failure surfaces only after the writes are public. Deferred here at the A/B split.
- [references/upstream-353.md](references/upstream-353.md) - Full body of dixson3/yoshiko-flow#353 — `LAND_DIGEST_EXCLUDED` omits `resolved_target_tip` and `merge_preview`, making every resume at or after `L_VALIDATED` a guaranteed digest mismatch. **This plan closes it**; read alongside `findings/exp-003`, which refutes the remedy this issue proposes.
