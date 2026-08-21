---
type: Reference
okf_spec: OKF-PLAN
id: comment-186
description: Drafted upstream comment for #186 (include, close)
---

# Draft comment → #186 (`include`; closes with this comment)

> **Fixed in `plan-050-james-dixson-d0414b`.**
>
> `REQ-DATA-062` — every title `plan_extract.py` emits now equals its source line's span
> **verbatim**, inline code spans included.
>
> ## The fix, and why the obvious one is wrong
>
> The title is captured from the **unmasked** line by **offset-slicing** the match
> (`raw[m.start(g):m.end(g)]`), which `mask_inline_code`'s documented length preservation
> guarantees correct. Everything else — `ISSUE`, `EPIC`, `SUBKEY`, `try_trailing` — keeps
> matching against the **masked** line, because that masking is *correct for parsing*: a
> `depends-on:` written inside a code span is documentation, not a declaration.
>
> The naive repair (`ln = raw`) was built and measured, and it produced a **spurious edge to a
> nonexistent target** and drove `--strict` non-zero, because a code-span `depends-on:` becomes
> visible to `try_trailing` again. That is why the requirement names the offset form
> specifically rather than "read `raw`".
>
> ## Both capture sites — this issue's own scope was understated
>
> The fix changes **two** sites: the `ISSUE` title *and* the `EPIC` name. The plan carried a
> "single call site" claim for several cycles; a reviewer **spiked** a synthetic plan and
> measured an epic name blanking identically, and the control then reproduced it on a real
> fixture:
>
> ```
> issue 1.1  want 'Ship the `classify` mode on `doc_lint.py`'
>            got  'Ship the            mode on'
> epic 1     want 'Fix `plan_extract.py` and its `mask_inline_code` helper'
>            got  'Fix                   and its                    helper'
> ```
>
> A one-site fix would have shipped half of this issue.
>
> ## Measured on a real 28-issue plan
>
> Re-extracting `plan-050`'s own bundle before and after:
>
> | | epics | issues | edges | `unparsed` | `--strict` |
> | :-- | --: | --: | --: | --: | --: |
> | before | 6 | 28 | 41 | 0 | 0 |
> | after | 6 | 28 | 41 | 0 | 0 |
>
> **27 titles restored**, DAG identical. The unchanged edge count is the load-bearing half:
> had it moved, the title fix would have perturbed parsing, which is exactly what the naive
> repair did.
>
> Note what the pre-fix output looked like — not an error, not an `unparsed[]` entry, not a
> non-zero exit. Just runs of spaces where a term used to be, written straight into a bead
> `title` by `SKILL.md` §5.2a's mechanical pour, with `--strict` reporting `unparsed: []` and
> exit **0** throughout.
>
> A companion assertion pins the other direction (`SC22`): a `depends-on:` written inside a
> code span — in a title **and** in a continuation line — still produces **no edge**. The fix
> must not trade one silent corruption for another.
>
> Measured: `ctl-186-masked-title` 1 → 0. Recorded in
> `docs/plans/plan-050-james-dixson-d0414b/assets/red-prework.md`; the before/after extraction
> delta is in that bundle's `assets/extraction-delta-050.md`.
