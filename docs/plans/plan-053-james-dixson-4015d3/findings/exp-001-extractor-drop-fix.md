---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-extractor-drop-fix
description: #206's fix is clean, the parse/capture split already exists structurally, and the corpus delta is zero edges — but the indent guard is load-bearing
---

# EXP-001: can #206 be fixed without breaking the masking invariant?

**Verdict: YES, cleanly. The parse/capture split the fix needs ALREADY EXISTS structurally, so
no restructuring is required. Corpus delta is ZERO edges and ZERO counts. But the fix
introduces one new silent-corruption shape if written naively, and the guard against it is
load-bearing.**

## Reproduced exactly — and #206's line numbers are stale

The fixture reproduces the astrospike output byte-for-byte: the inline-code-only line vanishes,
the whole fenced block vanishes, `unparsed: 0`, `recovered: 0`, `edges: []`.

**The mechanism is exactly as #206 describes. The line numbers are not.** Current tree: the
drop-through is at **`:473`** (#206 says 428), `ln = mask_inline_code(raw)` at **`:398`** (says
355), the fence skip at **`:396`** (says 353) — a uniform ~+43 offset, so #206 was written
against a pre-#193 revision. `_shared/` and the vendored copy are byte-identical.

## The invariant holds — because the split is already there

The `:473` branch is **capture-only**: it calls `_collect_detail(raw, False)` and nothing else.
It never calls `try_trailing` and never matches `SUBKEY` / `COL0_SUBKEY` / `ISSUE` / `EPIC`.
Every *parsing* branch above it still tests `ln`.

> **So changing this one gate's operand widens capture and CANNOT widen parsing.** The code
> already keeps parsing on the masked line and capture on the raw line; the fix makes that
> split correct rather than creating it.

Adversarial cases, measured under the fix:

| Case | Result |
| :-- | :-- |
| continuation line entirely `` `depends-on: 1.1` `` | `detail` carries it as prose; `depends_on: []`, `edges: []` — REQ-DATA-062's guarantee intact |
| fence containing `- Issue 9.9:`, `- depends-on: 9.9`, `` - touches: `nope.py` `` | `depends_on: []`, `touches: []`, `edges: []`, issue count unchanged — **no phantom 9.9** |

A fence is opaque by construction, so it reaches the same answer masking does, by a different
route.

## The indent guard is LOAD-BEARING — a naive fix creates a new corruption

What terminates an issue's continuation: an epic `###`, any other `###`, a column-0 `- `
bullet, or the end of `## Epics`. **A column-0 fence terminates nothing.**

Measured with a naive "collect every fenced line" variant, against a fence written after the
last issue but still inside `## Epics`:

```
NAIVE 1.1 '```bash\n# A COLUMN-0 FENCE that belongs to the plan body, not to issue 1.1.\n…'
```

The plan-body fence lands in the last issue's **bead description**. The guarded variant leaves
`detail: ''`.

The rule that works is **CommonMark's own**: an *indented* opening fence is list-item
continuation; a *column-0* fence is document content. The opening indent must also be stripped
so internal indentation survives.

**Fixing #206 naively would introduce a new silent-corruption shape while fixing an old one.**

## The corpus delta: two live instances, zero regressions

```
corpus: 53 plans
  plan-001-james-dixson-c88e7a: 1 issue gains detail (+8 lines): ['4.3']
  plan-040-james-dixson-1cabe4: 1 issue gains detail (+4 lines): ['4.4']
plans with recovered detail: 2/53; +12 detail lines
```

Zero edge deltas, zero `counts` deltas, identical issue-id lists on all 53. **plan-001 issue
4.3's `detail` was entirely EMPTY at base and is now the whole `plan_manager.py audit` bash
block** — a live instance of #206 in this repo's own corpus, not just astrospike's.

**Absence of evidence, reported:** this corpus contains **no** instance of drop shape 1 (the
code-only continuation line). That shape is evidenced only from astrospike.

Test suites on base vs fixed: `test_plan_extract.py` `all passed`; `ctl-186` and `ctl-187` both
exit 0; `test_dag_guard`, `test_okf` (59), `test_sync` (27) all pass. `test_doc_lint.py` shows
**2 failures identical on base and fixed** — pre-existing, corpus-driven, not this change.

## Two more family members, both out of scope

1. **The column-0 paragraph** inside `## Epics` under an open issue is still dropped silently
   with `unparsed: 0` — a **third** member of #206's family, measured on both base and fixed.
   Do not widen this fix to cover it: a column-0 line is not a continuation under CommonMark,
   so the right answer is likely `unparsed`, not `detail`. **File as a follow-on.**
2. **A separate latent gap:** `` `foo.py` depends-on: 1.1 `` — a real trailing declaration
   behind a leading code span — yields `depends_on=[]` on **both** base and fixed. The
   two-space branch tests `ln`, which the leading mask pushes past column 2. Unchanged by this
   fix; flagged, not fixed.

## Shape of the work

**Two independent changes, not one** — shape 1 is a one-token operand change; shape 2 needs a
`_fence_indents` helper and a guard. Split into two execution issues so each earns its own RED
observation.

**SPEC-first is required and the requirement is currently unstated.** `REQ-DATA-063`
(`spec/data.md:735`) defines `detail` as the continuation lines minus sub-keys. It does not say
which line the **capture gate** reads, nor that a fenced block is a continuation, nor that a
column-0 fence is not. Both facts are load-bearing. Amend it to state: (a) the capture gate
reads the **unmasked** line while every parsing branch reads the masked line — *the split is
the requirement, not an implementation detail*; (b) an **indented** fence is continuation,
collected verbatim minus the opening indent; a **column-0** fence is plan body.

**Fixture home:** `docs/plans/plan-050-james-dixson-d0414b/assets/fixtures/` — `ctl-186-masked-title.sh`,
`ctl-187-empty-detail.sh`, `corpus/ctl-18{6,7}-plan.md`, with `assets/redcheck.sh` and
`assets/controls.txt`. A ready `ctl-206-dropped-continuation.sh` was written in `ctl-187`'s
exact style and measured **RED (exit 1, 6 failures) → GREEN (exit 0)**.

It asserts **five** things, not two: both recoveries, both adversarial no-edge cases, and the
column-0 fence boundary. **Do not reuse `ctl-187`'s blanket `"depends-on:" not in detail`
assertion** — the adversarial issue legitimately carries that text as prose.
