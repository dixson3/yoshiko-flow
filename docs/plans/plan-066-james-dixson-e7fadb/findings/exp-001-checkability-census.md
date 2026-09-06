---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-checkability-census
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
---
# EXP-001 — Are #317's Class-A defects mechanically checkable, or irreducibly prose?

**Question.** This experiment was commissioned to be able to **refute D1** ("re-derive the
inventory mechanically"). If most claim classes are prose-only, D1 buys a thin checker plus a
manual sweep wearing a checker's clothes.

**Answer: D1 is corroborated, with a bounded scope.** 12 of 14 rows have a machine-readable
source of truth. Two are irreducibly prose.

## Class census

| # | Claim class | Verdict | Source of truth | Rows |
| :-- | :-- | :-- | :-- | --: |
| 1 | **Counted-set** — "19 skills", "utility (7)", "three shipped formulas" | **CHECKABLE** | `skills/*/SKILL.md` `skill-group:`; `skills/*/formulas/*.formula.toml` | 4 |
| 2 | **Path/identifier** — harness install roots, `name_transform` | **CHECKABLE** | `yf/src/harness_desc.rs` `DESCRIPTORS` | 3 |
| 3 | **Artifact existence** — the missing page (the P0) | **CHECKABLE** | `ls skills/*/SKILL.md` vs `ls web/content/skills/*.md` | P0 |
| 4 | **Enumerated-verb** — page command table vs the real verb set | **PARTIAL** | `SKILL.md` `## Invocation`; argparse tables | 3 |
| 5 | **Removed-feature** — `assess <corpus>`, GitLab/Jira backends | **PARTIAL** | code-derived denylist + legitimate-mention allowlist | 2 |
| 6 | **Conditional-behavior prose** — "removal is unconditional" vs a sha256 guard | **PROSE-ONLY** | `revert.rs:466-521` | 1 |
| 7 | **Omission / site-wide silence** | **PROSE-ONLY** | — | 1 |
| 8 | **Unverifiable — no in-repo truth** (`why.md` competitor table) | **PROSE-ONLY** | none | flagged |
| 8b | **Environment-dependent** (`bd` version currency) | **CHECKABLE vs the MACHINE** | `bd --version` → measured **1.2.2** vs page's 1.0.5/1.1.0 | flagged |

**Bucket count of the 14 tabled rows: CHECKABLE 7 · PARTIAL 5 · PROSE-ONLY 2.**

## Checker A — counted-set, live repo

```
CENSUS: {'skills': 20, 'group:beads': 5, 'group:markdown': 4, 'group:utility': 8,
         'group:workflows': 3, 'formulas': 5}
scanned 44 files, 12 counted-set claims
FAIL images/architecture.d2:18: 'skills (18)'                  -> claims 18, census 20
FAIL images/architecture.d2:20: 'beads group (8)'              -> claims 8,  census 5
FAIL images/architecture.d2:21: 'utility group (6)'            -> claims 6,  census 8
FAIL images/formulas.d2:145: 'three shipped standard formulas' -> claims 3,  census 5
FAIL images/formulas.d2:147: 'three shipped standard formulas' -> claims 3,  census 5
FAIL pages/architecture.md:59: '19 skills'                     -> claims 19, census 20
FAIL pages/architecture.md:65: 'utility (7)'                   -> claims 7,  census 8
VERDICT: FAIL (7 mismatches)   EXIT=1
```

It correctly stayed **silent** on `workflows (3)`, `beads (5)`, `markdown (4)` — which are right.

**Three controls, all passed.** Doc-side positive (repair all 7 → `PASS, EXIT=0`); doc-side
negative (`markdown (4)`→`(11)` on the green copy → `FAIL`); **code-side negative** (add a
fictional 21st skill + a 6th formula, docs untouched and previously green → `FAIL (7)`, census
shifts to 21/9/6).

## Checker B — path/identifier, live repo

```
DESCRIPTORS (truth), yf/src/harness_desc.rs:
  claude-code  user=.claude/skills  project=.claude/skills  name_transform=None
  codex        user=.agents/skills  project=.agents/skills  name_transform=None
  opencode     user=.agents/skills  project=.agents/skills  name_transform=None
  pi           user=.agents/skills  project=.agents/skills  name_transform=None
  agents       user=.agents/skills  project=.agents/skills  name_transform=None
scanned 44 files, 34 path/identifier claims
VERDICT: FAIL (15 mismatches)   EXIT=1
```

**15 defect sites across 3 files.** #317 implies ~4. The real count is **9 wrong path cells**
(both user *and* project columns) and **3** `name_transform` assertions.

### The negative control earned its keep — it caught a FALSE GREEN

On its first run checker B returned `PASS (0 mismatches), EXIT=0` — against a tree with 15 real
defects. Cause: the shared root `.agents/skills` **contains the harness id `agents`**, so a
repaired `pi` row scanned as `{pi, agents}`, was judged ambiguous, and was silently skipped.

Stripping path tokens before attributing the line fixed it and raised live coverage from 27 to
34 claims. **The checker was wrong in exactly the direction that looks like success** — the case
a doc-side-only control cannot catch.

## Row-by-row status vs #317

- **STILL TRUE: 13 of 14.**
- **CHANGED: 1** — row 11 (`harness-tune.md:156`). #317's "contradicts `install.md` on the same
  site" is **no longer true, and was already untrue at filing** (`web/content` is byte-identical
  to 2026-08-26). The narrower defect remains: the bullet is unconditional while `revert.rs`
  applies a sha256 guard with three outcomes.
- **ALREADY FIXED: 0.** Nothing was repaired since the snapshot.

## Four defect sites #317 does NOT list

| Site | Claim | Class |
| :-- | :-- | :-- |
| `images/architecture.d2:36` | `"upstream tracker\nGitHub / GitLab / Jira"` | **4th** site of the removed-backend claim |
| `skills/yf-plan.md:90` | *"`/yf-plan` scans GitHub **or GitLab**"* | **5th** site — on a page #317 counts as clean |
| `pages/install.md:204-207` | a whole prose bullet on the `pi` transform | **3rd** site of the `name_transform` regression |
| `install.md:191`, `architecture.md:47` | wrong in the **project** column too | doubles the path-cell count |

## The Class-B thesis is STRONGER than #317 states

`DRIFT-CHECK.md` already declares **three edges for exactly the counted-set class** —
`e-web-skill-counts` (`:189`), `e-web-formula-set` (`:155`), `e-web-skill-groups` — and they
missed **all 7** mismatches. Their nodes (`:73`, `:76`) are scoped to `pages/architecture.md`
and `pages/formulas.md` only, so the `.d2` files are structurally out of reach.

`e-web-formula-set`'s own text says *"the page asserted three formulas while five shipped — a
claim nothing checked"*. **The diagram still asserts three, at two lines, today.**

So the gap is not merely *missing §6 rows*. It is that three existing, well-specified edges were
assigned to an **LLM prose judge** over a **narrowed node set**, for a claim class that is pure
integer equality. A prose judge over `architecture.md` can never see `architecture.d2`.

## Implications for the plan

1. **D1 stands, scoped to classes 1-3.** Two ~70-line deterministic checkers covered 7 of 14
   rows plus the P0, and found 4 sites #317 misses.
2. **A design choice the plan must make.** #317's Scope §4 says *add* `images/**` §6 rows. The
   stronger fix is to **retire** the three prose-judged count edges and replace them with one
   deterministic checker whose corpus is `**/*.{md,d2}` — no node list to hand-maintain, so the
   diagram-exclusion defect cannot recur. Adding rows leaves the judge prose and the node lists
   hand-maintained.
3. **Every checker ships with a code-side negative control**, not just a doc-side one. Mutate the
   source of truth under passing docs — that is the direction that catches a checker which has
   quietly stopped attributing anything.
4. **Rows 11 and 14 are editorial, not automatable.** Budget them as prose work.
5. **`land` is NOT a `/yf-plan` slash verb** (`SKILL.md:137-143`). Documenting it as a command
   would manufacture a false claim — the same trap #317 flags for `yf-judgement`.
6. **Fix rows 4-6 from checker B's 15-site list, not #317's 4.** A partial fix re-greens the
   issue while leaving three sites wrong — violating #317's own "repair at all sites together".

**Limit of this experiment:** the agent could not run `pelican` (no `.venv` in its worktree), so
its P0 claim is structural inference. EXP-003 reproduced the build independently.
