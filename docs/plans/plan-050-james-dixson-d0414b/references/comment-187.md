---
type: Reference
okf_spec: OKF-PLAN
id: comment-187
description: Drafted upstream comment for #187 (include, close)
---

# Draft comment → #187 (`include`; closes with this comment)

> **Fixed in `plan-050-james-dixson-d0414b`.**
>
> `REQ-DATA-063` — each issue `plan_extract.py` emits now carries a **`detail`** field: its
> continuation lines, **minus** the `depends-on:` / `resolves-upstream:` sub-key bullets the
> parser already consumes (in both the two-space-indented and recovered column-0 forms, and
> including a trailing-inline declaration stripped off the line it was read from).
>
> This is the issue's **framing 1** — make the extractor honest — rather than framing 2,
> weakening `SKILL.md` §5.2a to match. §5.2a instructs an executor to derive the bead DAG
> mechanically and pass `--description=${issue_detail}`; there was no such field, so a
> mechanical pour produced beads with empty descriptions on a DAG that was otherwise perfect.
>
> ## The sub-key exclusion is what makes it a schema field
>
> The same bytes must not be reachable **both** as a structured edge and as prose. Without
> that exclusion it would be a raw-text dump, and `depends-on: 1.1` would appear in every bead
> description alongside the edge it already produced. The control asserts the exclusion
> explicitly, in both directions: the prose must arrive, the sub-keys must not, and the edges
> must still be read.
>
> ## An empty `detail` is a valid value
>
> An issue whose only continuation was its sub-key bullets carries an empty `detail`. That is
> the field working, not failing — and it is the measured case on the fixing plan itself:
> **0 of 28** of `plan-050`'s issues carry non-empty `detail`, because every one of its
> continuation bullets is a sub-key.
>
> That figure was predicted before execution and recorded as a **negative observation** rather
> than passed over. It also corrected the plan's own note: an earlier draft claimed this issue
> was load-bearing for that plan. It is not. **That plan's exposure was `#186`**; this issue
> matters for every plan that writes substantive continuation prose — which is what the control
> `ctl-187-empty-detail`'s fixture plan does, and where the behaviour is actually proven. A
> criterion phrased as "`detail` is non-empty" would have been unfalsifiable on the fixing plan
> and quietly satisfied by the fixture alone.
>
> ## Also repointed
>
> `SKILL.md` §5.2a's invocation named `_shared/plan_extract.py` — a path inside the source
> repository, and **not** one of the `SKILL_DIR` resolver's six roots, so an operator following
> it verbatim anywhere else got a file-not-found. It now names
> `${SKILL_DIR}/scripts/plan_extract.py`, the vendored copy `_shared/sync.py` keeps
> byte-identical (and which `CHANGE-VALIDATION.md` enforces in the FAST tier, so editing either
> alone fails the on-edit gate).
>
> Measured: `ctl-187-empty-detail` 1 → 0 (pre-fix: no `detail` field exists at all). Recorded
> in `docs/plans/plan-050-james-dixson-d0414b/assets/red-prework.md`.
