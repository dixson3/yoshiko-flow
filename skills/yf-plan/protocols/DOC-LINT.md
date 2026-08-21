# Document-Lint Trigger Protocol

Always-loaded firing surface for the yf artifact **document linter** (`doc_lint.py`). The
engine is a script with no skill of its own, so no `description` can fire it; this rule binds
the on-edit trigger. The schema model, the check kinds and the severity semantics live in the
`yf-plan` spec (`spec/data.md`, `REQ-DATA-024` / `REQ-DATA-043`–`REQ-DATA-057`); this rule binds
only *when the engine runs* and *how to read what it returns*.

## No marker file. Inertness is STRUCTURAL.

This rule carries **no opt-in marker**, unlike `yf-markdown-lint`'s
`.markdown-lint-on-edit`. It does not need one: the engine is **path-keyed**, so in a repository
with no `docs/plans/**`, `Incubator/*/plans/**` or `docs/research/**` documents, **no schema
selects anything** and the trigger below never has a changed path to act on. A marker would be
a second, weaker restatement of a condition the path globs already enforce exactly — and a
marker that can be absent while the paths exist is a way to silently disable the check.

## On-edit trigger — CLASSIFY FIRST, then branch on the `class`

After any create or modify of a `.md` file under one of the typed roots — `docs/plans/**`,
`Incubator/*/plans/**`, `docs/research/**` — run the **preflight classifier** over the changed
file, then act on the `class` it returns:

```bash
uv run "<skill-dir>/scripts/doc_lint.py" --classify --path "<changed.md>" --json
```

| `class` | classify exit | What to do |
| :-- | --: | :-- |
| `selected` | `0` | **lint it** (below) |
| `empty` | `0` | **lint it** — an empty document fails its schema and the lint says so loudly |
| `not-selected` | `1` | **skip and report** `not-a-typed-document` — ordinary, not an error |
| `no-such-path` | `1` | **report as an ERROR** — a caller naming a file that does not exist is a caller bug |

On `selected` or `empty`, lint it:

```bash
uv run "<skill-dir>/scripts/doc_lint.py" --path "<changed.md>" --json
```

Resolve any `E`-severity finding in the same pass. `W` and `R` are informational.

**Branch on the `class`, never on the classify exit code alone.** The two non-lintable classes
share exit `1` and are *different facts*: `not-selected` is an ordinary skip, `no-such-path` is
a caller bug. Collapsing them reinstates #181's conflation one layer up — the same defect this
step exists to remove, one level higher.

**The `--root` form answers the copied-bundle case.** A plan bundle **copied outside**
`docs/plans/` is #181's titled scenario, and it is a *root* question rather than a *path* one:

```bash
uv run "<skill-dir>/scripts/doc_lint.py" --classify --root "<other-root>" --path "<bundle>/plan.md" --json
```

It returns `not-selected` — correctly, and now *legibly*, where the lint alone returned a green.

**`not-selected` means *not selected by PATH ROUTING*.** A `--type`-forced lint is unaffected:
`plan_manager.py` deliberately re-lints a bundle's `plan.md` with the type forced, so the plan
document stays checkable wherever the bundle lives. A path this step skips *is* lintable by
that route.

## What replaced the "`files_checked` is NOT optional" section

This section used to be **prose instructing an agent to parse a field and reinterpret it**. It
is now an **executed step with an exit code**, because a step with no exit code is not a step.

The `files_checked` field still means what it meant — it is simply no longer the caller's
decision procedure:

| `files_checked` | `verdict` | lint exit | What it means | Which `class` predicted it |
| --: | :-- | --: | :-- | :-- |
| `>= 1` | `PASS` | 0 | the document was checked and is clean | `selected` |
| `>= 1` | `FAIL` | 1 | the document was checked and has `E` findings | `selected` or `empty` |
| **`0`** | **`PASS`** | **0** | **nothing was checked** | `not-selected` **or** `no-such-path` |

The bottom row is why the classifier exists. Those two rows are **identical at the exit-code
level and identical in the JSON**: `--path` on an unselected file returns the same object as
`--path` on a **nonexistent** file, so the failure was silent in both directions. Reading
`files_checked` distinguished *checked* from *not checked*, but it could never distinguish
*not claimed by any type* from *not there at all* — no field in the lint's output carries that.

Two reserved OKF files (`index.md`, `log.md`) sit in the `not-selected` class inside every plan
bundle, so that class is **ordinary, not exceptional** — they are skipped and reported, never
failed. `no-such-path`, by contrast, is always worth an error.

## Exit contract — TWO vocabularies, KEYED BY MODE

The same executable carries two exit vocabularies. Which one applies is decided by the mode,
and a caller that reads the wrong one reads a number that means something else.

**LINT mode** (the default): `0` = no `E`-severity finding · `1` = at least one · `2` =
**INCONCLUSIVE**, the linter could not run (a missing schema directory, an unreadable
document). A `2` is a statement about the *instrument*, not the document: repair the harness
rather than reading it either way. At the intake binding an INCONCLUSIVE maps to `warn`,
**never** `fail` (`REQ-DATA-057`) — the linter's own breakage must not become an intake outage.

**CLASSIFY mode** (`--classify`, `REQ-DATA-061`): `0` = **lintable** (`selected`, `empty`) ·
`1` = **not lintable** (`not-selected`, `no-such-path`) · `2` = the classifier could not run.

The two are not the same contract, and the difference is observable: a `classify` run over a
selected-but-**empty** document exits **0**, while a `lint` run over that same document exits
**1** on its `E` findings. `REQ-DATA-024`'s "binary at every binding point" wording was amended
for exactly this reason.

The **verdict** vocabulary is unchanged and closed — `PASS | FAIL | INCONCLUSIVE`. `classify`
emits a `class`, never a verdict.

## Where else the engine runs

Two other bindings exist and neither replaces this one:

- **intake** — `_audit_plan` folds the linter into the portability audit, so `ready-check`
  (exit 3) and `audit` (exit 1) gate on it and `audit_close` stays advisory (`REQ-DATA-057`).
- **`CHANGE-VALIDATION.md`** — the `doclint` recipe row runs it over changed paths in the FAST
  tier and over the tree in FULL.

This rule is the **authoring-time** surface: it fires on the edit, long before either.

## Scope boundary

`doc_lint` checks that a **typed yf artifact** has the shape its type declares — sections,
frontmatter, table columns, row-id grammar, and the cross-section `plan-relations` rules. It
never authors, reformats or fixes.

- generic GFM validity (links, embeds, tables) → `yf-markdown-lint`
- cross-edge content **agreement** (docs ↔ spec ↔ implementation) → `yf-drift-check`
- executing a repo's build/test/lint recipe → `yf-change-validation`

A single `.md` edit may fire several of these on orthogonal axes; that is expected and
non-recursive.
