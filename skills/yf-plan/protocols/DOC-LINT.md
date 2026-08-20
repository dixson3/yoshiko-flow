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

## On-edit trigger

After any create or modify of a `.md` file under one of the typed roots — `docs/plans/**`,
`Incubator/*/plans/**`, `docs/research/**` — run the linter over the changed file:

```bash
uv run "<skill-dir>/scripts/doc_lint.py" --path "<changed.md>" --json
```

Resolve any `E`-severity finding in the same pass. `W` and `R` are informational.

## Reading the result: `files_checked` is NOT optional

**Parse `files_checked` from the `--json` output and report `not-a-typed-document` when it is
0.** An exit code cannot carry this, and that is the whole reason the rule says so explicitly:

| `files_checked` | `verdict` | exit | What it actually means |
| --: | :-- | --: | :-- |
| `>= 1` | `PASS` | 0 | the document was checked and is clean |
| **`0`** | **`PASS`** | **0** | **nothing was checked** — no schema's globs select this path |

The two rows are **identical at the exit-code level**. A caller that branches on the exit code
alone reports a green for a file the engine never opened, which is indistinguishable from a
green for a file that passed. `--path` on an unselected file returns the same object as
`--path` on a **nonexistent** file, so the failure is silent in both directions.

So the correct report for `files_checked: 0` is **`not-a-typed-document`** — a statement that
no type claims this path — and never `PASS`. Two reserved OKF files (`index.md`, `log.md`) sit
in this category inside every plan bundle, so the condition is ordinary, not exceptional.

## Exit contract

`0` = no `E`-severity finding · `1` = at least one · `2` = **INCONCLUSIVE**, the linter could
not run (a missing schema directory, an unreadable document). A `2` is a statement about the
*instrument*, not the document: repair the harness rather than reading it either way. At the
intake binding an INCONCLUSIVE maps to `warn`, **never** `fail` (`REQ-DATA-057`) — the linter's
own breakage must not become an intake outage.

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
