---
type: Asset
okf_spec: OKF-PLAN
description: "Surviving executable artifacts from the plan-067 investigations. EXP-004's generator prototype was NOT recovered; this file records that honestly."
id: spikes
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# Investigation spikes — what survived, and what did not

Pass-1 C14 required the investigations' executable artifacts be preserved rather than discarded.
This is a **partial** recovery and the gap is stated rather than glossed.

## Preserved

| File | From | What it is |
| :-- | :-- | :-- |
| `exp001-architecture-stack.d2` | EXP-001 | the first cut at #373's layered marketecture — tools bottom, beads+utility middle, workflows top, with the workflows→utility edge. Issue 4.1's starting point. |
| `exp001-elk-sample.png` | EXP-001 | that source rendered under the current pin (`--layout elk`) |
| `exp001-dagre-sample.png` | EXP-001 | the same source under `dagre` — the single sample that produced the now-refuted D6 |

**The dagre sample is retained deliberately as a negative artifact.** It is `lifecycle`-adjacent in
character — the one shape where dagre reads well — and it is why a one-diagram sample produced a
recommendation that a six-diagram measurement then refuted (pass-1 C1). Keeping it makes the
sampling error inspectable rather than merely described.

## NOT recovered

- **EXP-004's `build_model()` / `to_d2()` generator prototype**, which ran over all 20 skills and
  rendered every output. It lived in a sub-agent scratch directory that did not survive.
- **EXP-001's archify spec and delivered HTML.**
- **EXP-003's slash-verb extractor** — the instrument that produced the false green.

**Consequence, stated plainly.** Issue 5.2 must re-derive the generator rather than adapt a working
one. `findings/exp-004-per-skill-diagram-model.md` documents the approach in detail — the inputs
(`SKILL.md` frontmatter, the reverse dependency graph, `skills/<n>/scripts/`, `_shared/sync.py`'s
`REGION_ASSETS`/`WHOLE_FILE_ASSETS` tables), the measured hit rates, and the full 20-skill triviality
census — so this is re-derivation from a specification, not speculation. But pass-1 noted that Epic 5
is defensible as an epic *because* a prototype had been built and run, and that evidence is now
prose rather than code.

**For EXP-003's extractor specifically:** it cannot be preserved as the fixture pass-1 wanted. Issue
1.2's vacuity floor must therefore be tested against a **reconstructed** known-blind input — a
subcommand-table `## Invocation` whose verbs carry no slash prefix — rather than against the original
failing instrument.
