---
type: Finding
okf_spec: OKF-PLAN
id: exp-003-deepen-root-index
description: What does deepening the root index to enumerate nested files require of okf.py? (D-4's hinge)
---

# Finding: What does deepening the ROOT index to enumerate nested files actually require of `okf.py`?

### Approach Tested

Read `_listing_members`, `reindex_check`, `reindex_write`, `render_index`, `add_index_entry`,
`_covered_by_listed_children`, `_split_listing`, `check_markers` in `skills/yf-okf/scripts/okf.py`,
plus both producers (`plan_manager.py` `_INDEX_MEMBERS`/`seed_index`/`_ensure_index_lists_member`,
`yf-research/scripts/index_manager.py`). Ran `reindex --check` over all 61 bundles; copied the 6
nested bundles to `$(mktemp -d)` and ran `--write` against the copies. Built synthetic fixtures for
edge cases. Computed entry-count distributions for five candidate selection rules plus a K-sweep, and
a description-derivability census over 725 nested `.md`. Real corpus untouched.

### Result

**measured:** — the checker ALREADY tolerates nested entries. Zero engine change is needed to accept
them. Six bundles carry nested entries: plan-048 (6), plan-049 (10), plan-050 (24), research 002
(8), 003 (7), 004 (10). `--check` verdicts: five `clean`; plan-048 `drift` only for `missing:
assets/` and `missing: scripts/` — two directories it genuinely never listed, **not** its nested
entries. **Zero `ghost` findings corpus-wide.**

Two mechanisms already do this, and were designed for it: ghost detection has **no depth
restriction** (it resolves `bundle / target` at any depth), and `_covered_by_listed_children`
(okf.py:1338) suppresses the `missing` for a directory whose children are listed. That predicate is
already on `main` and **its docstring already cites `exp-003`**.

**measured:** — `--write` on tmp copies of all six: `changed: False` for 5 of 6. Only plan-048
changed, appending the two legitimately-missing bare dir entries. **No hand-written nested entry was
clobbered, reordered, or stripped of its description.** Migration risk to existing bundles is
measured at zero.

**measured:** — the entire depth boundary is ONE function, `_listing_members` (okf.py:1309). Both the
`missing` loop and the append loop iterate it. `add_index_entry` accepts any path string and is
**already nesting-capable**.

**measured:** — two hand formats exist. plan-048/049/050 use *grouped* (top-level dir bullet with
2-space-indented children); research 002/003/004 use *flat* with `[phase]`-tagged descriptions —
which is literally the §8 example shape.

**measured:** — the description problem has no scanner-shaped solution. Over 725 nested `.md`:
frontmatter `description:` on only **134 (18.5%)**; an H1 first line on 693 (95.6%). `reindex_write`'s
contract is explicit that "a description is never invented". So a derive-from-frontmatter generator
leaves **four in five entries bare** — and H1 quality varies sharply (`findings/*.md` H1s are rich;
`reviews/pass-1.md` H1s are near-worthless).

**measured:** — yf-research already solved this, and not with a scanner. `index_manager.py add <dir>
<phase> <artifact> <description>` takes an agent-authored description at *registration time*. That is
why research indexes have the corpus's richest nested entries and plan indexes do not. The plan
side's gap is a **missing registration verb**, not a missing scanner.

**measured:** — size, five candidate rules over 1075 files / 30 indexed bundles:

| rule | total | median | p90 | max |
| :-- | --: | --: | --: | --: |
| A: every nested file | 1045 | 24.0 | 81 | **134** |
| B: nested `.md` only | 865 | 24.0 | 50 | 101 |
| C: exclude `references/`,`reviews/`,`diagrams/` | 588 | 14.5 | 54 | 69 |
| **D: enumerate a subdir iff <=10 files, else bare dir** | **463** | **14.5** | **30** | **30** |
| E: depth-1 `.md` only, cap 12 | 523 | 14.0 | 37 | 39 |

Only the cap rules are size-invariant. Rule D turns plan-054 (135 files) into 18 entries and plan-050
into 14. K-sweep knee is at K=10-12. Rule D also collapses `references/` (391 files) and `reviews/`
(108) to bare stubs — precisely the mechanical, low-information files, and **hand-authors made the
same call**: plan-050 lists 14 `assets/` files individually and leaves `reviews/` bare.

**measured:** — v0.2 §8 permits nested targets explicitly. Verbatim: *"Entries SHOULD include the
description from the linked concept's frontmatter. Producers MAY generate `index.md`
automatically"*, with targets as `relative-url` and **no depth constraint**. §11 lists nothing about
index depth. The research bundles are the closer reading of §8 than the plan bundles are.

**measured:** — four live hazards, all in the PRODUCERS, not the engine:

- **`_ensure_index_lists_member` splices into a group.** It inserts after the last *top-level* bullet
  (plan_manager.py:803, 828). Fixture: adding a member to a grouped index made `assets/`'s children
  render as children of the new entry. **This is red today for plan-048/049/050**, not a hypothetical.
- `_INDEX_BULLET_RE` in the audit is `^- \[` with no leading whitespace — a fully-indented index would
  fail `_index_is_listing`.
- **An unlisted nested file is invisible.** Fixture: an unlisted `findings/exp-003.md` reported
  `clean`. Drift is one-directional — ghosts caught, gaps not.
- plan-050 carries a glob entry `- [references/comment-*.md](references/)`, the one entry in the
  corpus whose title is not a path.

**measured:** — no new preservation mechanism is needed. `INDEX_MARKERS` (`<!-- intro:start -->`) already
exists with a hard `MarkerImbalanceError`, but no corpus index uses them and none needs to:
`_split_listing` already carries head- and tail-prose verbatim by locating the contiguous bullet run.

### Implications for Plan

**D-4 is cheaper than scoped on the checker side and more expensive on the description side.** Zero
engine change to accept nested entries — measured, five of six round-trip byte-identically. But
widening `_listing_members` *without* a description source would add ~200 bare entries and make the
140/247 boilerplate ratio **worse**, which is the opposite of D-4's purpose.

**The insert-into-group defect is a prerequisite, not a follow-on** — it corrupts a grouped index on
the very next member added.

### Recommendations

1. **Scope the engine change to `_listing_members` gaining a selection parameter. Do not touch
   `reindex_write`'s preserve-and-append contract** — that contract is what makes the 6 existing
   bundles migrate for free. Sorting or full regeneration forfeits the measured zero-clobber result.
2. **Use rule D at K=10, recursive.** Size-invariant, max 30 entries, collapses exactly the two
   boilerplate-generating directories. Make K a constant, not a config knob.
3. **Pair the widening with an author-supplied description path** — a `plan_manager.py index-add
   <plan_dir> <path> <description>` verb mirroring `index_manager.py add`, called by the agents that
   write findings, reviews and assets. Fall back frontmatter -> H1 -> bare; **never** synthesize.
4. **Adopt the research bundles' FLAT format, not the grouped one.** It is the §8 example shape
   verbatim, cannot be corrupted by the splice defect, and cannot trip the `^- \[` audit regex.
5. **Fix `_ensure_index_lists_member` first** (insert after the last bullet of any indentation). The
   fixture is a ready-made RED observation.
6. **Add the inverse drift signal** — report `missing` for nested files the rule selects but the index
   omits, or the deepened index under-covers silently exactly as the current one does.
7. **Do not add `INDEX_MARKERS` usage.** Already enforced; adds nothing measured.
8. **Handle plan-050's glob entry explicitly** in whatever conformance work lands.
