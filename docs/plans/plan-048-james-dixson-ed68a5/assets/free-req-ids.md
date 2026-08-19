# Free `REQ-*` id list (Issue 0.1)

**Derived mechanically**, not by counting forward — plan-047 allocated four ids that were
already live because it counted forward instead of grepping.

## Method — and the correction it forced

A first pass grepped the whole worktree, `docs/plans/**` included, and reported `REQ-DATA-050`
as the highest live id. That was **wrong**: historical plan documents cite ids they *propose*,
and a proposal is not a declaration. The live set has to distinguish two populations:

```bash
# DECLARED — the authoritative set. Line-start, in the spec dir only.
grep -rhoE '^REQ-(DATA|PORT|CLI)-[0-9]+[a-z]?' skills/yf-plan/spec/ | sort -u

# REFERENCED — anywhere outside docs/plans. A superset; catches dangling citations.
grep -rhoE 'REQ-(DATA|PORT|CLI)-[0-9]+[a-z]?' . --exclude-dir=docs --exclude-dir=.git | sort -u
```

**Allocate strictly above the maximum of BOTH sets.** A referenced-but-undeclared id is not
free: some file already points at it, and rebinding it silently redirects that citation.

## Measured live sets (2026-08-19)

| Family | Declared in `spec/` | Max declared | Referenced but NOT declared | Max referenced |
| :-- | :-- | :-- | :-- | :-- |
| `REQ-DATA-*` (`spec/data.md`) | 001–002, 010–028, 030–031, 040–042 | `042` | `003`–`007` | `042` |
| `REQ-PORT-*` (`spec/portability.md`) | 001–008, 010–012, 020, 030–033, 040–041, 050–052 | `052` | `009` | `052` |
| `REQ-CLI-*` (`spec/cli.md`) | 001–024 | `024` | — | `024` |

Two pattern matches are prose fragments, not ids, and are excluded: `REQ-PORT-04x` and
`REQ-CLI-0`.

**Interior gaps are not free for reuse.** `REQ-DATA-029` and `032`–`039` are declared nowhere
and referenced nowhere, but a retired id must stay retired: a stale external reference must
never silently rebind to new text.

## Free ids — allocate from the top of each family

- `REQ-DATA-043` and upward
- `REQ-PORT-053` and upward
- `REQ-CLI-025` and upward

## Allocations made by plan-048

| Id | Issue | Subject |
| :-- | :-- | :-- |
| `REQ-DATA-043` | 0.3 | extractor `unparsed[]`-gating contract — every consumer returns INCONCLUSIVE, never FAIL |
| `REQ-DATA-044` | 0.7 | the `plan-relations` check kind |
| `REQ-DATA-045` | 0.5 | no `E`-severity check on a path outside a plan bundle unless the corpus already passes |

No other issue in this plan may allocate an id without appending a row here first.
