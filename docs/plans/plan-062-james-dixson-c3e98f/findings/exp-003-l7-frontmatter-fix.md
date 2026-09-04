---
type: Finding
okf_spec: OKF-PLAN
description: 'DEFERRED at pass 4 by operator decision — #326 is no longer in plan-062 scope; this finding is retained so a later plan starts from a solved design. Designs and spike-proves the #326 fix: strip frontmatter via the existing okf.read_frontmatter, materialize to a temp file, and compare the STRIPPED text in the read-back — the strip and the comparison must change together. 7/7 spike cases pass. Also surfaces an independent L7 defect: the success envelope omits `failed`, so dropped writes are silently discarded and L7 returns pass on a landing that posted nothing.'
---
# EXP-003 — The minimal correct fix for #326

**Question.** How do we stop `land` L7 posting YAML frontmatter into public GitHub comments,
without breaking the read-back verification or the OKF audit?

## Approach Tested

Read `_land_l7_reconcile_writes` and the read-back in full, plus `_land_upstream_facts`,
the `body_sha256` check and the audit walk that types drafts. Searched all six vendored `okf.py`
copies and `doc_lint.py` for a frontmatter splitter. Copied the scripts to `$(mktemp -d)`, applied a
candidate patch, and ran the existing suite plus a new 7-case spike using the repo's own
`FakeRunner` / `LandingContext(runner=...)` injection point. Nothing was posted to GitHub.

## Result

## Both claims in the brief CONFIRMED, quoted

The post (`plan_manager.py:9038-9044`) — no strip anywhere on the path:

```python
        if action == "comment":
            if not body_path or not Path(body_path).is_file():
                failed.append({"issue": issue, "reason": f"body_path {body_path} missing"})
                continue
            r = ctx.run("gh", ["issue", "comment", issue, "--body-file", body_path], cwd=ctx.root)
```

The read-back (`:9055-9063`) — `want` is re-read **from the file**:

```python
                    want = Path(body_path).read_text(encoding="utf-8").strip()
                    bodies = [c.get("body", "") for c in (seen.get("comments") or [])]
                    ok = any(want[:200] in b for b in bodies)
```

The fail-closed return at `:9073-9079` runs **after** `gh issue comment` has executed. So a
strip-only fix flips `ok` to `False` *post-publication*. The trap is real.

**Both sides of the collision, measured** on a sandbox copy of plan-057's bundle:

| Draft state | `audit` |
| :-- | :-- |
| as committed (frontmatter present) | `pass`, zero `upstream-drafts` findings |
| stripped (plan-061's workaround) | **`fail`** — `REQ-OKF-003: no YAML frontmatter block` ×4 |

## The fix: (a) and (b) are not alternatives — the answer is their union

`ctx._dispatch` (`:8766`) takes **no stdin**, so `--body-file -` is unavailable: any strip must
be materialized to a temp file. And a temp file that is a verbatim copy still posts the YAML.
So: **strip → temp file → post → compare the stripped text.**

**A reusable helper already exists.** `okf.read_frontmatter` (`okf.py:135`) returns
`(frontmatter_dict, body)`; `plan_manager.py` already imports `okf` (`:33`) and calls it at
`:227`, `:5842`, `:5683`. Its documented contract — *"A file with no frontmatter yields `({},
full_text)`"* — is exactly the no-op #326 needs. **Do not write a new splitter.**

## Spike: 7/7 pass

Cases proven: frontmatter stripped with read-back green (`okf_spec` absent from posted text,
archival file still opens `---`); **no-frontmatter byte-exact no-op** (`posted_text == file
text`); wrong body still halts; truncated body still halts; frontmatter-only draft refused
*before* any `gh` call; malformed YAML posted verbatim; helper is a pure identity across four
no-frontmatter shapes including a mid-document `---` rule.

The pre-existing suite is unchanged — the same 5 environment-only failures occur **before and
after** the patch.

## An independent L7 defect the spike surfaced (measured, not in the brief)

The first spike run failed with `KeyError: 'failed'`. The success `_step(...)` at `:9080`
passes `performed` and `refused` but **not `failed`** — so `continue`-path failures (today: a
missing `body_path`) are appended to a list and then **silently discarded**. *L7 returns `pass`
on a landing that posted nothing.*

That is the vacuous-check class (`#263`) inside the landing's own verification step, and it is
what makes the new empty-body refusal observable at all.

## Constraints that must hold

- **`body_sha256` must NOT move.** The `--validate-decision` digest (`:8177`) is
  `sha256(f.read_bytes())` over the **archival** file — that is what the operator consented to,
  and the strip is deterministic from it. `agents/lander.md:88` needs no change.
- **`REQ-OKF-003` and `OKF-EXTENSION.md` §3b are both satisfied untouched** — no exclusion row,
  no stripped committed file. The bundle member keeps its frontmatter; the public comment never
  sees it.
- **SPEC-first.** `REQ-LAND-019` (`spec/landing.md:302`) says writes are verified by read-back;
  it must be amended to say the read-back compares **the text posted**, not the file, or the fix
  contradicts the SPEC. Add `REQ-LAND-027` (next free id) for the strip and its no-op guarantee.

## Rejected alternative

Renaming drafts to `.body.txt` (plan-059's convention) dodges `rglob("*.md")`, but removes the
drafts from `doc_lint` and OKF typing entirely — **silencing the check by renaming rather than
by an exclusion row, which is what §3b forbids, one layer down.** It also requires changing the
hardcoded `.md` at `_land_upstream_facts:7948`.

## Implications for Plan

**measured:** every quantitative claim above came from a runnable spike or an AST read, not
from reading prose. **inferred:** the judgements about agent behaviour and about what a
future reader would conclude are reasoning, not measurement, and are labelled as such where
they appear.

The consequences for the plan are carried in the sections above and in `plan.md`'s Approach.

## Recommendations

1. Adopt **strip + temp-file + compare-stripped-text** as one change-set, SPEC edit first.
2. Reuse `okf.read_frontmatter`; catch `OKFParseError` and post verbatim — never guess at a
   `---` block the OKF engine itself rejects.
3. **Include the empty-stripped-body refusal.** Without it the fix opens a new hole: `want ==
   ""` makes `any(want[:200] in b ...)` **vacuously true**, so a comment that said nothing
   reports verified.
4. Fold in the `failed=failed` / halt-on-`failed` envelope correction — one line, and it is what
   makes the refusal observable.
5. Add the 7 spike cases to `test_land_apply.py` (they reuse its `repo`, `FakeRunner`, `_R`,
   `_ctx` fixtures unmodified).

Touch points, all in one function: `import tempfile` (`:22`); a `_land_comment_body` helper
above `_land_l7_reconcile_writes`; the comment branch (`:9038-9043`); `want = posted.strip()`
(`:9059`); an `if failed:` guard before the pass envelope (`:9080`).
