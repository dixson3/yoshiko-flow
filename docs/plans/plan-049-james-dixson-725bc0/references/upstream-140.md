---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #140: yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model

- **Number:** 140
- **Title:** yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`yf-plan` and `yf-research` bundles are OKF-shaped **only at the root**. `index.md` / `log.md` exist at the bundle root and nowhere below it, so every subdirectory requires a full content scan to learn what it holds.

Enforcing structure further down is worth doing — but it creates an index-drift problem the moment it lands, and `yf-okf` has no way to generate or drift-check a listing. A second, more capable take on exactly that already exists in `~/workspace/bookpipe/bp/skills/okf-lint` and is worth evaluating as the model.

Reconciling `yf-okf` to **OKF v0.2** is filed separately as #141 — independent work with its own breaking changes.

---

## The gap, measured

Measured on `plan-039` (a completed, audit-passing bundle):

```
plan-039-james-dixson-150f79/
  index.md          ← the only listing in the bundle
  log.md
  plan.md, context.md, upstream-triage.md
  findings/     3 files, no index.md, no log.md
  references/  12 files, no index.md, no log.md
  reviews/      5 files, no index.md, no log.md
```

Corpus-wide: **zero** `index.md` below the bundle root across `docs/plans/` and `docs/research/` — the only nested ones are inside `plan-029`'s *test fixtures*. `docs/research/*/` has the same shape (`artifacts/`, `diagrams/`, `scripts/` all unlisted).

So `references/` in plan-039 holds four replay fixtures, five upstream snapshots, two drafted comments and a residuals record, and the only way to learn that is to open all twelve.

### This is a navigability gap, not a conformance failure — state it correctly

**OKF does not require nested index files.** v0.2 §8: *"An `index.md` file MAY appear in any directory."* §9: *"A `log.md` file MAY appear at any level."* §11 is explicit that consumers **MUST NOT** reject a bundle for *"Missing `index.md` files."* `yf-okf`'s own `OKF-BASELINE.md` already records `log.md` as *"optional and unexercised"* — a recursive scan of the reference repo finds zero.

So enforcing this is a **yoshiko-flow extension decision** (`OKF-YF-EXTENSIONS.md`), not a fix to a conformance defect. Filing it as "we're non-conformant" would misstate the rationale.

**The justification is OKF's own stated motivation for index files** (§8): *"to support **progressive disclosure**: letting a human or agent see what is available before opening individual documents."* That is precisely the cost being paid today — and it is paid hardest by the agents that read these bundles, since a cold reader with no listing must open everything or guess.

### Open design questions

- **What does a per-directory `log.md` contain?** For `reviews/` a chronological history is meaningful. For `references/` — regenerated wholesale on every re-triage — a log is plausibly noise. Nested `index.md` and nested `log.md` should be decided **separately**; they are not one feature.
- **Which directories?** Every directory with concept documents, or only those exceeding some size? `diagrams/` with one `.d2` + one `.png` may not earn a listing.
- **Retroactive or forward-only?** ~40 completed plan bundles exist. A backfill is mechanical if generated, unreviewable if hand-written.

---

## `bp`'s okf-lint is a different model, and solves the drift half

`~/workspace/bookpipe/bp/skills/okf-lint/scripts/okf-lint.py` (483 lines) takes a different approach from `yf-okf`'s:

| | `yf-okf` | `bp/okf-lint` |
| :-- | :-- | :-- |
| Verbs | `check`, `migrate`, `scaffold` | check, **`--fix`** |
| Index handling | `render_index` / `add_index_entry`, **root only** | **coverage + drift across every folder**, with regeneration |
| Posture | conformance report, propose-only | validate **and repair** |
| Prose safety | — | preserves hand-written prose between `<!-- intro:start -->` markers |

**Its central check is the one this issue needs:** *"Every folder containing concept documents needs an `index.md`, and that index must list **every** concept in the folder, with **no** entries for files that no longer exist. **Drift is the main thing this catches** — a file added or deleted without the listing being regenerated."*

That matters because **§1 creates a drift problem the moment it lands.** Four listings per plan bundle × ~40 bundles, hand-maintained, is not viable — and a stale index is worse than no index, because it asserts something false. Generation + drift detection is what makes the enforcement sustainable.

Two caveats, from reading it:

- **It is not liftable as-is.** It hard-depends on `chapter-intake` and `okf-issue-tracker` for `--fix` delegation, and on an `AGENTS.md` root sentinel. The *approach* transfers; the code does not.
- **It also carries vault-specific rules** (chapter and character conventions merged in from a retired `validate-vault.py`) that have no analogue here.

Worth noting it independently arrived at the same reserved-name discipline — its SKILL.md argues at length against renaming `index.md` to `_index.md`, on the grounds that OKF reserves the name at every level and a rename forces a choice between two non-conformant outcomes.

---

## Suggested shape

Not prescriptive:

- Decide nested `index.md` and nested `log.md` **separately**, as `OKF-YF-EXTENSIONS.md` decisions with the progressive-disclosure rationale stated — not as conformance fixes.
- **Add a `reindex` / `--fix` verb to `yf-okf` before enforcing anything**, so the corpus can be generated and drift-checked rather than hand-maintained. Enforcement without generation is the failure mode: a stale index asserts something false, which is worse than no index.
- Decide retroactive vs forward-only for the ~40 existing plan bundles. Mechanical if generated; unreviewable if hand-written.

## Related

- #141 — reconcile `yf-okf` to OKF v0.2 (independent; changes the frontmatter these indexes would surface, so sequence deliberately)
- plan-029 — introduced `yf-okf` and the current root-only bundle shape

🤖 Generated with [Claude Code](https://claude.com/claude-code)

