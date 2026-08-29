---
type: Concept
okf_spec: OKF-YF-EXTENSIONS
description: "The boundary between the two structural validation layers — okf.py (container) and doc_lint.py (content) — on three axes, with the measurements that make the split non-arbitrary."
---
# The two structural validation layers, and where the boundary runs

**Status:** decision of record · **Landed:** plan-056 Issue 4.1 · **Measured:** 2026-08-28

This repository runs **two** structural validation engines over the same artifact folders. They
are not redundant, they are not layered one on the other, and neither subsumes the other. Before
plan-056 they also **did not reference each other at all** — a measured zero-cross-reference gap
that let each be described in isolation as though it were the whole story, and that is how both
came to be gates that could not fail without anyone noticing.

This document is the boundary. It is cited from
[`skills/yf-okf/SKILL.md`](../skills/yf-okf/SKILL.md) and from the `doc_lint` spec
([`skills/yf-plan/spec/data.md`](../skills/yf-plan/spec/data.md)), so a reader arriving at either
layer meets the other.

| | **`okf.py`** | **`doc_lint.py`** |
| :-- | :-- | :-- |
| Judges | the **container** | the **content** |
| Status | status-**blind** | status-**aware** |
| Coordinates | **repo-rooted** | **bundle-relative** |
| Verb | `check`, `reindex`, `migrate` | `lint`, `--classify` |
| Failure mode it prevents | a bundle whose listing lies about its own members | a document that does not have the shape its declared `type` promises |

## Axis 1 — container vs content

**`okf.py` judges the SHAPE OF THE FOLDER.** Does a bundle carry its reserved `index.md` and
`log.md`? Does every non-reserved `.md` carry frontmatter with a non-empty `type` and an
`okf_spec` member key? Does the root listing enumerate what is actually on disk? It never opens a
document to ask whether its *sections* are right.

**`doc_lint.py` judges the SHAPE OF A DOCUMENT.** Given that a file declares `type: Plan`, does it
carry the sections, the table columns, the row-id grammar and the cross-section relations that the
`plan` schema declares? It never asks whether the folder around that file is well-formed.

**The measurement that makes this non-arbitrary.** `okf.py`'s root listing enumerates **direct
children only** — 401 members across the 62 bundle roots — while those same bundles contain
**1254** `.md` files at any depth. The container layer therefore names **32%** of the corpus and is
silent about the rest *by design*: a listing is a table of contents, not an inventory. `doc_lint`
selects by path glob and reaches the other 68% without caring which folder they sit in. Merging
the two would mean either teaching the listing to enumerate 1254 entries (an index no one reads) or
teaching the content linter to reason about folder membership (a second, weaker `okf.py`).

## Axis 2 — status-aware vs status-blind

**`doc_lint` is status-AWARE**, and this is its defining property. `STATUS_SEVERITY` maps a
finding's declared severity through the bundle's `status:` — a `W` is promoted to `E` at
`review`/`ready-for-approval` (the intake gate) and demoted to `R` at every terminal status. The
rationale is that **history is not re-judged by a rule written after it**: a schema shipped today
would otherwise hard-fail 46 bundles authored before it existed.

**`okf.py` is status-BLIND.** It has no `status` concept at all. A bundle's index either agrees
with its contents or it does not, and that is equally true of a `complete` bundle and a `drafting`
one — a listing that names a file which is not there is wrong regardless of what phase the plan is
in.

**The measurement, and why the split is load-bearing.** With the terminal-status demotion
disabled, the corpus yields **197 `E` findings** over 1116 files; with it enabled, **`errors: 0`**.
Only **2 of 55** declared checks are structurally capable of producing an `E` at
`bundle_status: complete` — `R1-closeout` and `R2a-closeout`, which escape via the
`promote = false` close-out binding (`REQ-DATA-074`). So `doc_lint` past the intake gate is very
nearly a report, by deliberate design.

**That is exactly why the container layer must NOT inherit status-awareness.** If it did, the
corpus would have no structural gate that can fail after intake at all — which was the state
plan-056 was written to end. `okf.py`'s status-blindness is the property that makes the OKF drift
gate (`REQ-OKF-CHK-004`) worth wiring: it fires on a `complete` bundle, where `doc_lint` by
construction will not.

## Axis 3 — repo-rooted vs bundle-relative

**`doc_lint` reasons in REPO-RELATIVE paths.** Its `paths` and `exclude` globs are anchored at the
repo root (`docs/plans/*/findings/**/*.md`), because its job is to decide *which files in this
repository* a schema selects.

**`okf.py` reasons in BUNDLE-RELATIVE paths.** Its type map, its reserved-file rules and its §3b
exclusions are all written relative to a bundle root (`assets/fixtures/**`), because a bundle is
portable: the same rules must hold when the folder is copied into another repository.

**This is why the two exclusion lists are INDEPENDENTLY DECLARED** (plan-056 D-14). They share a
*mechanism* — both are glob lists, both are honoured at every walk site, both have a
`--no-exclude` positive control — but they cannot share a *source*, because they are written in
different coordinate systems. Deriving one from the other would miss `assets/fixtures/**`
entirely: `doc_lint` is silent there by **non-selection** (no schema's globs reach it), not by
**exclusion**, and those are different facts about the same path. The relationship is pinned by an
overlap-invariant test that also asserts **both lists are non-empty** — without that half the
invariant holds trivially when either side is empty, which is the state the concept was introduced
from.

## The one real duplicate, resolved explicitly

Both layers can report on a bundle's **frontmatter**. `okf.py`'s `REQ-OKF-003` requires a
parseable block with a non-empty `type`; `doc_lint`'s per-type schemas check individual *keys*
within that block (`identity-frontmatter`, `description`, and so on).

**The resolution is by question, not by filter.** `okf.py` owns *"is there a frontmatter block,
and does it declare a type at all?"* — a container question, answerable without knowing which type
it is. `doc_lint` owns *"given the declared type, are that type's keys present and well-formed?"* —
a content question, unanswerable until the type is known. The two never assert the same thing
about the same key: a document with no frontmatter is one `okf.py` error, not also a cascade of
`doc_lint` findings for every key of a type it never declared.

Resolving this with a **filter** — having one layer suppress the other's findings — was
deliberately rejected. A filter would make the overlap invisible rather than absent, and the next
schema added would silently re-create it.

## What each layer is NOT

Neither layer verifies that already-written artifacts **agree** across declared edges — that is
`yf-drift-check`, a prose/LLM judgement on a different axis entirely. Neither executes a repo's
build/test/lint recipe — that is `yf-change-validation`. A single `.md` edit may fire several of
these on orthogonal axes; the double-fire is expected and non-recursive.

## Where each layer is bound

| binding | layer | tier |
| :-- | :-- | :-- |
| `CHANGE-VALIDATION.md` `doclint` row | `doc_lint` | FAST + FULL |
| `CHANGE-VALIDATION.md` `okf-index-drift` row | `okf.py` (via the corpus driver) | FAST + FULL |
| `plan_manager.py` `_audit_plan` | both | intake `ready-check` / `audit` |
| `plan_manager.py` `audit-close` | both | §6.4 close, advisory |
| the on-edit rule `DOCUMENT_LINT.md` | `doc_lint` | authoring time |

Before plan-056 the second row did not exist: `okf.py reindex` appeared in **zero**
`CHANGE-VALIDATION.md` rows, **zero** CI steps and **zero** `plan_manager.py` call sites. Root-index
drift had been repaired nine days earlier and had already regressed in 9 of 30 index-bearing
bundles. A verb no gate invokes is not enforcement, whatever its exit codes say.
