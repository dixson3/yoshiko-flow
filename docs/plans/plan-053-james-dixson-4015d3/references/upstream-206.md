---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #206: CRITICAL: plan_extract.py still silently drops detail lines — inline-code-only continuations and fenced blocks vanish with unparsed: 0 (same family as #186/#187)

- **Number:** 206
- **Title:** CRITICAL: plan_extract.py still silently drops detail lines — inline-code-only continuations and fenced blocks vanish with unparsed: 0 (same family as #186/#187)
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/206
- **State:** OPEN
- **Labels:** type::bug, priority::critical

## Body

## Summary

`plan_extract.py` still silently discards issue-detail content — the same failure family as #186 / #187, which are closed. Two line shapes are dropped **whole**, and both are reported as `unparsed: 0`, `recovered: 0`, so nothing downstream can detect the loss.

Found while re-poring `plan-001` in `dixson3/astrospike` after the #186/#187 fix shipped. The fix is real and works (titles now carry inline code; 34 of 35 details populate), but this third case survived it.

## The two drop shapes

**1. A continuation line that is *wholly* an inline-code span.**

`_collect_detail` is reachable only through the drop-through at `plan_extract.py:428`:

```python
if cur_issue is not None and re.match(r"^\s+\S", ln):
    _collect_detail(raw, False)
    continue
```

`ln` is `mask_inline_code(raw)` (assigned at :355). A line that is nothing but an indented inline-code span masks to **all spaces**, so `^\s+\S` does not match, and the line is dropped — `_collect_detail` never sees the `raw` text that was available the whole time.

**2. Any fenced code block inside an issue's continuation.**

The `## Epics` loop opens with `if i in fenced_lines: continue` (`:353`), before any detail collection, so a fenced block under an issue vanishes entirely.

## Reproduction (measured)

Real instance, from `docs/plans/plan-001-james-dixson-9153de/plan.md`:

```markdown
  - Port the markup from the ys source rather than inventing it:
    `~/workspace/ys/ys-website/themes/yoshiko/templates/page.html`
    (`<form id="contactForm" class="contact-form">`). Style it from the E3 tokens, including the
    inline success and error states.
```

Extracted `detail` for that issue:

```
- Port the markup from the ys source rather than inventing it:
(`<form id="contactForm" class="contact-form">`). Style it from the E3 tokens, including the
inline success and error states.
```

The middle line is gone. `file_refs` is `[]`, so the path is recovered nowhere. The bead instructs the executor to *"port the markup from the ys source"* and then deletes the only statement of where that source is — an instruction that reads as complete and is not.

Fenced case, sandbox-measured: an issue whose continuation contains a ```` ```bash ```` block yields `detail == '- Run this:\n- done'`.

Both report `unparsed: 0` and `recovered: 0`.

## Why this is priority::critical

Same reasoning as #186/#187: the corruption is **silent and reports success**. `--strict` gates on `unparsed[]`, which this class never populates, so there is no configuration in which the loss surfaces. A plan author has no signal, and the poured bead looks well-formed.

It is also a natural authoring shape. Putting a long path on its own line is ordinary markdown reflow, and adding a fenced command block under an issue is arguably the single most natural way to make an issue more executable — the exact edit the fixed extractor should reward.

## Suggested fix

1. Route the drop-through decision on `raw`, not `ln`. The masking is correct for *parsing* (deciding what a line is); it is wrong as the gate for *capture*. `mask_inline_code` is length-preserving by construction, so `re.match(r"^\s+\S", raw)` is a safe substitute at :428 — an indented line with any non-space content is a continuation regardless of whether that content is code.
2. Collect fenced continuation lines verbatim into the current issue's detail rather than `continue`-ing past them.
3. Failing either, **emit an `unparsed` / `recovered` record** so the loss stops being silent. A dropped line that is *reported* is a bug; a dropped line that reports `unparsed: 0` is a correctness hazard.

A regression fixture for both shapes would sit naturally alongside the #186/#187 fixtures.

## Workaround in the affected repo

`plan.md` was reflowed so the path is no longer alone on its line, and the plan's banner now warns authors never to leave an inline-code-only continuation line or add a fenced block under `## Epics`. Verified by a token-level diff of all 35 `detail` blocks against the source: 1 divergence before, **0 after**. That routes around the instance; the class remains.

