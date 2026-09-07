---
type: Finding
okf_spec: OKF-PLAN
description: "20 per-skill diagrams are sound only if GENERATED. Hand-authored they are 20 new drift surfaces. 8 of 20 are trivial; the wrappers relation derives at 85%."
id: exp-004-per-skill-diagram-model
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# EXP-004 — Generation model for 20 per-skill diagrams

## Approach Tested

**measured:** all claims below were produced by parsing the 20 `SKILL.md` frontmatter blocks,
running three independent extractors for the "wrappers" relation, building a two-stage prototype
(`build_model()` → toolchain-neutral dict; `to_d2()` → source) over all 20 skills, and rendering
every output under the pinned `d2 v0.8.2`. **inferred:** conclusions beyond direct observation are
marked.

## Result

### The verdict: GENERATE. Hand-authored, D3 is self-defeating.

Maintenance cost per model:

| Event | Hand-authored | Generated |
| :-- | :-- | :-- |
| skill adds a `depends-on-*` | edit 1-3 `.d2`, re-render → **CAN DRIFT** | re-run → **CANNOT DRIFT** |
| skill adds/removes a script | invisible to every current edge → **DRIFTS SILENTLY** | re-run → **CANNOT DRIFT** |
| new skill added | someone must remember a 21st file → **CAN DRIFT** | appears automatically |
| skill removed | orphan `.d2`+`.png` linger → **CAN DRIFT** | disappears |
| `_shared` vendoring changes | nobody would notice | edge redraws from `sync.py` |

**The measured cost of SIX hand-authored diagrams** is already on record:
`check_web_counts.py:11-16` records plan-066 finding **7 live mismatches across 4 files** that
three well-specified DRIFT-CHECK edges all missed, plus the corrected-count-wrong-membership
defect (`beads group (5)` listing the *workflows* skills). Going 6 → 26 hand-authored multiplies
exactly that.

**Second-order:** you cannot omit a cluster or an edge from a diagram you did not write — so
generation makes this surface immune to plan-067's own Half-2 omission problem.

### 8 of 20 are TRIVIAL — the census

```
RICH 5 · moderate 7 · TRIVIAL 8
  yf-plan 26 nodes/6 edges · yf-research 16/6 · yf-beads-upstream 12/5 · yf-beads-extra 9/8
  ...
  yf-drift-check 3 nodes / 0 EDGES   <- literally zero
```

Eight are a box plus at most two tool arrows. Generation makes the *count* free, but 8
near-identical single-box PNGs are still a reader cost.

**And the top end fails too:** `yf-plan` renders **3104×4532** — a single-column stack of 22
sub-boxes, visually a bulleted list rather than a graph. A layout problem (grid-nesting fixes
it), not a data problem, but "one diagram per skill" does not automatically yield a *legible* one.

### The "wrappers" relation IS derivable — 85%, 100% with one field

```
HIT RATE  scripts/ on disk : 16/20        UNIQUE     11/20
HIT RATE  invoked in SKILL.md : 14/20     NONE        6/20  (all CORRECT — ship no scripts)
EXACT MATCH disk & invoked : 14/20        AMBIGUOUS   3/20  (yf-plan[4], yf-research[5], yf-markdown-format[2])
```

The two signals fail in **opposite** directions — disk over-reports (CI helper scripts), invocation
under-reports (`beads_init.py` is invoked only from its `protocols/` rule). **The missing datum is
not the SET but the RANK.** One optional `engine:` field is needed for exactly 3 skills; the other
17 derive correctly. Do **not** add a field enumerating all wrappered scripts — a hand-listed set
goes stale.

### `_shared/sync.py` is an unexploited machine-readable graph

Its `REGION_ASSETS`/`WHOLE_FILE_ASSETS` tables (`_shared/sync.py:299-414`) declare which skill
scripts are byte-vendored copies and which embed a marker-fenced shared region. Verified:
`md5 skills/*/scripts/okf.py` → all five identical. This is content the operator's "wrappers" view
wants and that no hand-author would keep straight.

### A LIVE FALSE CLAIM on the published site, found incidentally

`yf/src/frontmatter.rs:61` types it `user_invocable: Option<bool>` (absent = unknown), but
`web/plugins/skill_pages.py:133` coerces `bool(fm.get("user-invocable", False))`. **Four markdown
skills omit the key** while their own descriptions read `TRIGGER when: /yf-markdown-lint invoked` —
so the live site renders them **"auto (fires from its description conditions)"**, which is false.

Generation does not create this bug; it **propagates** it into a second place. It must be fixed
SPEC-first or the new diagrams ship a false claim on day one — the exact class plan-067 exists to
close.

## Implications for Plan

1. **D3 survives only in generated form.** 20 hand-authored diagrams would be 20 new drift
   surfaces, which is the opposite of this plan's purpose.
2. **Publishing all 20 is a separate question from generating all 20.** Generation is free;
   publication has a reader cost for the 8 trivial ones.
3. **The model→emitter split matters for D1** — EXP-001's archify outcome would change only
   `to_d2()`, not the model.
4. **`user-invocable` must be fixed before any generation lands.**

## Recommendations

1. **Generate** `web/content/images/skills/<name>.d2` from a shared model reading frontmatter, the
   reverse dependency graph, `scripts/`, `_shared/sync.py`'s asset tables, and `agents/`,
   `formulas/`, `protocols/` listings. Factor `_read_skills()` out of `skill_pages.py:120` into a
   shared module so the site page and the diagram provably read one source.
2. **Add `--check` to the generator and wire it into CHANGE-VALIDATION FAST.** Without it the
   generator is a convenience, not a guarantee. Precedent: `_shared/sync.py --check`.
3. **Gate publication on a computed threshold** (`nodes >= 5`), so the threshold cannot drift and a
   skill that grows past it gains a diagram automatically.
4. **Add one optional `engine:` field** for the 3 ambiguous skills only.
5. **Fix `user-invocable` first, SPEC-first.**
6. **Grid-nest sub-boxes** — a one-line emitter fix for the `yf-plan` 4532px column.
