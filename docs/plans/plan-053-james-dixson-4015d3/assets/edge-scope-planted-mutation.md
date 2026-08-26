---
type: Reference
okf_spec: OKF-PLAN
id: edge-scope-planted-mutation
description: The MANUAL planted-mutation dispatch for e-status-values (Issue 1.6b) — an honest artifact, not a faked shape check
---

# `e-status-values` — the planted-mutation dispatch (MANUAL)

## Why this is a manual record and not a test

There is **no runnable drift verifier**. `skills/yf-drift-check/` ships no `scripts/`
directory, and `CHANGE-VALIDATION.md` excludes yf-drift-check as a prose/LLM trigger rather
than an executable recipe row. The verifier is an **LLM sub-agent dispatch**, so its result is
a judgement, not an exit code.

Recording that honestly is the point. The alternative — writing a shape check and calling it a
verifier run — is the "process rule that nothing executes" defect this plan exists to close.
The **mechanical** half of this control lives in
[`fixtures/ctl-208-edge-scope.sh`](fixtures/ctl-208-edge-scope.sh), which asserts the edge's
declared scope; this file records the half no exit code reaches.

## Safety: run on a COPY in `$(mktemp -d)`, never in-place-with-revert

An in-place mutation reverted afterwards leaves a modified `skills/` file behind on **any**
abort — a crash, a interrupt, a failed revert. A copy cannot.

```bash
WORK=$(mktemp -d)
cp -R skills/yf-plan/agents "$WORK/agents"
printf '\n\nStatus check: a plan may be `wibble-not-a-status` at this point.\n' \
  >> "$WORK/agents/coordinator.md"
# dispatch the drift-verifier over e-status-values with $WORK as the agent node root
```

## The planted literal

`wibble-not-a-status` — outside REQ-STATUS-001's vocabulary by construction, and chosen so it
cannot collide with any real word in the corpus.

## Observation, 2026-08-26

| Field | Value |
| :-- | :-- |
| Planted into | `$WORK/agents/coordinator.md` (a copy; `git status` on `skills/yf-plan/agents/` stayed clean) |
| Literal | `wibble-not-a-status` |
| Live tree modified | **no** — verified by `git status --short skills/yf-plan/agents/` returning empty |
| Verifier dispatched | **no** — there is nothing to dispatch (see above) |

## What the mutation demonstrates, and what it does not

**Does:** the planted literal lands in a file the *current* target node (`agent` =
`skills/*/agents/*.md`) selects, so the edge's own `field-set-subset` check has the input it
needs and would report the drift **if it ran**.

**Does not:** prove anything about the sites that actually matter. `plan_manager.py`,
`_shared/doc_lint.py`, `skills/yf-herdr/**` and `web/content/**` all restate the vocabulary
and **none** is inside the current target set — which is the defect Issue 5.4 fixes and
`ctl-208-edge-scope.sh` asserts mechanically. Planting into an agent file is the *easy* case;
it is recorded here precisely so that it is not mistaken for the hard one.

**And the edge would still pass on it.** `complete` and every other real status is *in* the
vocabulary, so the subset check holds. The edge is weak not because its target set is empty —
pass-2 C17 measured that claim false — but because nothing the agent files contain can violate
a subset check against the vocabulary they are drawn from.
