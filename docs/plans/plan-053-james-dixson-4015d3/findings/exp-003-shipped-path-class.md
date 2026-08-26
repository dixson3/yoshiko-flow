---
type: Finding
okf_spec: OKF-PLAN
id: exp-003-shipped-path-class
description: Sizing the unshipped-script-path class and designing the check that closes it
---

# EXP-003: how big is the "SKILL.md names an uninstalled script path" class?

> ## ⚠ THIS FINDING'S CLASS-(c) COUNT IS WRONG. The predicate survives; the scope does not.
>
> **Refuted at pass 3 (C33) and widened again at pass 4 (C45).** The "**8** `yf-diagram-authoring`
> rows" figure was an artifact of the prototype scanning exactly four doc kinds
> (`SKILL.md`, `agents/*.md`, `protocols/*.md`, `reference/*.md`). Re-measured:
>
> | Claim | Measured |
> | :-- | :-- |
> | 8 rows, `yf-diagram-authoring/SKILL.md` | **9** in `SKILL.md`, plus **8 more in its `README.md`** |
> | class (c) is 9 rows total | also `yf-beads-hygiene/README.md` (7), `yf-beads-init/README.md` (4), three `yf-markdown-*/README.md` (10 stale) |
> | "FP surface measured to zero" | did not cover `skills/*/scripts/fixtures/**`, corpus documents carrying arbitrary invocations — now carved out explicitly |
>
> **This is the finding's own headline argument turned on itself**: a scope set by a
> prototype's convenience and never widened. `skills/*/README.md` is now in the check's globs
> and every affected file is in Issue 3.7's `touches`; the plan records **no count literal**
> for this class at all.
>
> The **predicate** (§"The predicate") is unaffected and remains the specification Issue 1.0
> rebuilds from.

**Verdict: on the `_shared/` axis the class is EXACTLY ONE live break — #210 — and the honest
report is to say so rather than to sell the class fix as a sweep. Its justification is a
mutation result, not a volume count. But the same predicate catches NINE adjacent breaks #210
never names, and #210's own fix needs TWO edits, not the one it proposes.**

## The measurement

A prototype checker over every `.py`/`.sh` invocation in every skill-owned instruction doc
(`skills/*/SKILL.md`, `agents/*.md`, `protocols/*.md`, `reference/*.md`) — **133 invocations,
0.17s**:

| Class | n | Where |
| :-- | --: | :-- |
| **(a) ok** — rooted at a skill-dir root, file exists in `skills/<owner>/` | **112** | 72× `plan_manager.py`, 9× `upstream.py`, the markdown-* family, yf-research, yf-herdr |
| **(b) repo-only `_shared/`** | **1** | `skills/yf-plan/SKILL.md:1578` → `uv run _shared/pour_fidelity.py` — **this is #210, and nothing else** |
| **(c) unresolvable, other** | **9** | 8× `yf-diagram-authoring/SKILL.md` bare `scripts/render.py` (cwd-relative, fails from any cwd but the skill dir); 1× `yf-incubator/SKILL.md:138` → an `obsidian-lint` skill this repo does not ship |
| illustrative (carved out) | 1 | `yf-skill-authoring/SKILL.md:152` `uv run script.py <args>` — a generic example |

Corroboration: `grep -rn --include='*.md' '_shared/' skills | wc -l` → **43** mentions, of which
**exactly 1** is an invocation. The other 42 are prose — including plan-050's own note
*explaining* this defect, which a naive grep would have flagged.

## Why the class fix is justified anyway — the mutation

Volume is the wrong argument. The right one is that the check **catches the first instance
too**. Appending a fence with `uv run _shared/plan_extract.py "$d" --json` — plan-050 Issue
7.3's original bug, verbatim — produced:

```
repo-only  skills/yf-demo/SKILL.md:21  _shared/plan_extract.py     RC=1
```

That is plan-052's `RE-002` remedy stated correctly: *put a check in front of the component*
rather than fixing the instance a third time.

## The predicate

> For every invocation `<runner> [flags] <PATH>` in a **shell-info fence** or **inline code
> span** of an instruction doc owned by `skills/<S>/`: `<PATH>` must begin with a recognised
> skill-dir root (`${SKILL_DIR}/`, `<skill-dir>/`, `<yf-NAME>/`, `[~/].{claude,agents}/skills/<name>/`),
> and the remainder must name an existing file at `skills/<name>/<rest>`.

This is a faithful **repo-side** re-expression of "resolves under `SKILL_DIR`" because install
is a verbatim embed→deploy of `skills/<S>/` (`REQ-YF-EMBED-001`): `skills/<owner>/<rest>` exists
at repo time **iff** `<SKILL_DIR>/<rest>` exists at run time. Absence of a recognised root fails
by construction — `_shared/`, `skills/…/` and bare `scripts/` are all cwd-dependent.

**False-positive surface, measured to zero.** A fixture with five prose `_shared/` mentions
(including plan-050's note verbatim), a `python` fence containing a commented invocation, and
one deliberately-external reference returned `2 invocations checked, 0 violations`, RC **0**.
The carves that achieve this: fences+code-spans only, a required runner token, an
`illustrative` class for paths with no directory component, and an explicit inline opt-out
marker for the intentional external case.

`SPEC.md` / `spec/*.md` are **excluded from scope** — they cite repo test paths as verification
commands, which are correct repo-time citations, not runtime instructions. Widening to them
adds 5 rows, all false.

## #210's fix is TWO edits, not one

`_shared/sync.py` vendors `doc_lint.py`, `manifest_update.py`, `okf.py`, `plan_extract.py` and
`plan_template.py`. **`pour_fidelity.py` has no vendored copy at all** — it is the only
`_shared` script a SKILL.md invokes that `sync.py` does not carry.

So rewriting `SKILL.md:1578` alone lands in the checker's `missing-in-repo` class. The order is:
add the `sync.py` whole-file map entry → regenerate → commit `skills/yf-plan/scripts/pour_fidelity.py`
→ rewrite the line → add a `§3` glob so the `pour-fidelity` recipe fires on the vendored copy.

## Wiring

`scripts/check_skill_script_refs.py` — a **repo-level guard, not a shipped skill script**. It
polices `skills/` from outside; shipping it inside a skill would make it self-referential and
put a repo-time tool on the install path. Exact precedent: `scripts/check_frontmatter.py`.

`CHANGE-VALIDATION.md` §1 **fast and full** (0.17s, no toolchain deps), §3 globs on
`skills/*/{SKILL.md,agents/*.md,protocols/*.md,reference/*.md,scripts/**}` plus a self-glob —
a *deleted* script must fire it.

SPEC-first anchor: a new **`REQ-YF-EMBED-005`** in `SPEC.md` §3.2, modelled on
`REQ-YF-EMBED-003`.

## Two decisions this forces on the plan

1. **The 8 `yf-diagram-authoring` rows.** They are real breaks in the adjacent class. The check
   **goes red until they are resolved or suppressed**, so the plan must decide explicitly:
   in scope, or a follow-on bead with a temporary suppression? Scoping the check to `_shared/`
   only would miss all 9 — the predicate is what earns the catch.
2. **`README.md` carries 10 genuinely stale paths** (`.claude/skills/markdown-{pdf,lint,format}/…`,
   pre-`yf-` rename). Not #210's class. Recommend a separate bead, optionally a WARN-only scope
   so it stays visible without gating.

## Also worth ADOPTING

The prototype already carries the 0/1/2 contract, `--json`, an `--all` measurement mode, and
passes both the FP fixture and the plan-050 mutation. It has **no unit tests** — seed
`test_check_skill_script_refs.py` from the two sandbox fixtures (FP-clean, plan-050 mutant).
