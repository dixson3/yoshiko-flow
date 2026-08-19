# `document_types/` — per-type document schemas (REQ-DATA-024)

One `<type>.toml` per in-scope yf artifact document type, read by the single linter engine
`_shared/doc_lint.py`. The schema is **data**; the engine is the only code.

## Two flavours, split by producer class (plan-047 D-8)

The split is measured, not stylistic: every **enforced code-generated** type measures **0%**
drift across the corpus, and every **unenforced agent-written** type measures **14–95%**.

| Flavour | `producer_class` | Required structure comes from | Example |
| :-- | :-- | :-- | :-- |
| code-generated | `"code-generated"` | `derive_from` — a Python dotted path the engine imports and reads | `plan.toml` (`plan_template.PLAN_SECTIONS`) |
| agent-written | `"agent-written"` | the inline `[[checks]]` in the file itself | `finding.toml` |

A code-generated type **must** set `derive_from`, so its required-section list cannot diverge
from the function that writes the type. An agent-written type has no producer function to
derive from, so it declares a standalone schema its producing agent file references. One
uniform format for both would re-introduce, at the template layer, the hand-maintained-duplicate
problem `_shared/sync.py` exists to eliminate.

## File keys

| Key | Required | Meaning |
| :-- | :-- | :-- |
| `type` | yes | the type's name; must equal the filename stem |
| `producer_class` | yes | `code-generated` \| `agent-written` |
| `derive_from` | code-generated only | `<module>.<ATTR>` — imported from `_shared/`, must be a list of section names |
| `paths` | yes | glob list selecting instances. **Path-keyed, never filename-keyed** (REQ-DATA-024) |
| `exclude` | no | glob list of carved-out regions |
| `description` | no | prose, for the report |

## `[[checks]]`

Each check is a table with `id`, `severity` (`E` structural \| `W` completeness) and `kind`.
Only `E` sets a non-zero exit code.

| `kind` | Extra keys | Passes when |
| :-- | :-- | :-- |
| `headings-present` | `value` (list), or omitted to use `derive_from` | every named `## ` heading is present, in order |
| `frontmatter-keys` | `value` (list) | the file opens with a YAML block carrying every key |
| `table-columns` | `section`, `value` (list) | the first GFM table under `## <section>` has exactly those column headers |
| `regex-absent` | `pattern` | the pattern does **not** match |
| `regex-present` | `pattern` | the pattern matches at least once |
| `row-id-grammar` | `section`, `pattern` | every data row's first cell matches `pattern` and no id repeats |

## Verdict and exit contract (REQ-DATA-024)

`PASS | FAIL | INCONCLUSIVE`. `INCOMPLETE` is the *reviewer agent's* vocabulary and never
appears here. Exit **0** = no error-severity finding, **1** = at least one, **2** = the linter
could not run (the only thing `INCONCLUSIVE` means). "Not finished yet" is a `W` **inside a
PASS**, so the exit contract stays binary at every binding point.

Status-aware promotion (plan bundles only): `scoping|investigating|drafting` → `W` is
informational; `review|ready-for-approval` → `W` is promoted to `E`; `complete` →
**report-only, never an error**.
