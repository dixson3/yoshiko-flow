---
type: Reference
okf_spec: OKF-PLAN
id: comment-181
description: Drafted upstream comment for #181 (include, close)
---

# Draft comment → #181 (`include`; closes with this comment)

> **Fixed in `plan-050-james-dixson-d0414b`**, by the fourth design — the first three were
> each refuted by measurement, and all three for the same reason.
>
> ## What shipped
>
> `REQ-DATA-061` — a **preflight classifier** on `doc_lint.py`. `--classify --path <p>` runs
> **before** any lint and decides whether linting that path is meaningful at all:
>
> | `class` | meaning | classify exit |
> | :-- | :-- | --: |
> | `selected` | selected by a schema's globs, non-empty | `0` (lintable) |
> | `empty` | selected but empty | `0` (lintable) |
> | `not-selected` | exists, but no schema's globs claim it | `1` |
> | `no-such-path` | does not exist | `1` |
>
> plus `2` for "the classifier could not run". `protocols/DOC-LINT.md`'s on-edit rule now
> **calls it and branches on the `class`** — that rule change is what actually closes this
> issue; a classifier nothing calls would have been a rule with no exit code, which is the
> class of defect the plan exists to end.
>
> ## Why a preflight rather than a fix inside the lint
>
> Three earlier scopes were built and measured, and each was refuted:
>
> - a general `files_checked == 0` form → breaks `_shared/test_doc_lint.py`'s SC42;
> - a `--path`-keyed-always form → breaks the same file's SC17 block, which pins an unselected
>   `--path` to `PASS`/rc 0 *and identical to a nonexistent path*;
> - an opt-in `--require-selection` flag → viable, but leaves the default silent.
>
> All three mutated **the reporting of the component under test**, and a shipped assertion
> pinning that reporting caught each one. `doclint-tests` runs in both CI tiers, so each would
> have failed the on-edit gate for every `doc_lint.py` edit.
>
> Stepping one layer upstream removes the collision surface instead of negotiating with it,
> and the design's central claim held under measurement: **`test_doc_lint.py` required zero
> edits for the engine change** (`git diff` empty at that commit, `all passed`), and the
> corpus figure was **unmoved at 757** against a baseline captured before the change. SC17 and
> SC42 remain *literally true*, because the behaviour they characterise is not modified.
>
> ## Two decisions worth stating
>
> - **`empty` is on the LINTABLE side, deliberately.** A selected-but-empty `plan.md` fails
>   its schema and the lint already says so loudly (measured: 6 `E` findings, exit 1). Skipping
>   it would have manufactured a new silent green *inside the fix for a silent green*. The
>   control asserts the **exit** on that arm, not just the class, because a classes-only
>   assertion is satisfied by a classifier that exits 1 on `empty`.
> - **Callers branch on the `class`, never on the exit code alone.** `not-selected` and
>   `no-such-path` share exit `1` and are different facts — an ordinary skip versus a caller
>   bug. Collapsing them would reinstate this issue's own conflation one layer up.
>
> ## The titled scenario is covered
>
> A plan bundle **copied outside `docs/plans/`** — the `--root` form, this issue's headline —
> returns `not-selected`. The control drives five scenarios across the four classes and
> **asserts, separately, that the lint's own reporting is still byte-identical** for an
> unselected and a nonexistent path. That is deliberate: if that arm ever goes false, the
> classifier has leaked into the lint and the corpus figure is invalid.
>
> Measured: `ctl-181-silent-green` 1 → 0 (pre-fix: `unrecognized arguments: --classify`).
> `REQ-DATA-024`'s "binary at every binding point" sentence was amended in the same SPEC
> commit, along with its three restatements outside the spec, because the same executable now
> carries two exit vocabularies keyed by mode.
