---
type: Finding
okf_spec: OKF-PLAN
---
# Finding: What does gh-direct actually have to reimplement, and is "~20 lines" right?

**Experiment:** EXP-001 · **Date:** 2026-08-16 · **Issue:** [#133](https://github.com/dixson3/yoshiko-flow/issues/133)

Marked **[measured]** (a command ran, this was its output) or **[inferred]** (a conclusion drawn
from it), per REQ-AGENT-021.

## Approach Tested

#133 estimates the reimplementation at **~20 lines**: create-or-update on `external_ref`, label
mapping, and `--parent` subtree walking. The label-mapping item is the one with a hidden
dependency — it is currently `bd`'s job, and nothing in this repo specifies it. Two questions:

1. Where is the label mapping defined in this repo?
2. Does the repo's label set actually cover the bead space that would be pushed?

Commands: `grep` over `upstream.py` / `SKILL.md` / `SPEC.md`; `gh label list`; `bd list --all`
aggregated by `issue_type` and `priority`.

## Result

### The label mapping does not exist in this repo, anywhere **[measured]**

```
$ grep -n "priority::\|type::\|_PRIORITY\|def.*label" skills/yf-beads-upstream/scripts/upstream.py
(no matches)
$ grep -n "type::\|priority::" skills/yf-beads-upstream/SKILL.md skills/yf-beads-upstream/SPEC.md
(no matches)
```

`upstream.py` never constructs a label. Neither the SKILL nor the SPEC documents the convention.
The `type::<t>` / `priority::<level>` scheme #133 describes is inferred **from observed output**
(bead `yf-1656` → issue #132), not from any local specification.

**[inferred]** So "keep the existing convention so already-pushed issues stay consistent" is not
a matter of copying a mapping — the mapping has to be **reverse-engineered and then specified for
the first time**. That is a SPEC-first deliverable, not a code line.

### The repo's label set does not cover the bead space **[measured]**

Bead types and priorities actually present in the local DB (1,000+ beads):

```
types:    {'task': 753, 'epic': 182, 'molecule': 42, 'feature': 9,
           'chore': 2, 'bug': 2, 'decision': 1}
priority: {1: 163, 2: 812, 3: 15, 4: 1}
```

Labels that exist on `dixson3/yoshiko-flow`:

```
type::bug  type::epic  type::feature  type::task
priority::high  priority::low  priority::medium
```

> **⚠ Corrected at review (pass-1 C6).** The census below is accurate, but its *implication* was
> overstated ~5×. `upstream.py:346` defines `CONTAINER_TYPES = {epic, molecule, gate}` and
> `candidate_filter` drops them from the push candidate set — so the 42 `molecule` and 182 `epic`
> beads are **structurally excluded from the write path** and never need a label. The real
> uncovered population is **`chore` (2), `decision` (1), and the single P4 bead — 3 of 991**.
> Exception: an explicit `hoist --issues <epic-id>` bypasses `candidate_filter`, so epics *can*
> reach the write path; `type::epic` already exists, so that case stays covered.
>
> This changed the plan's decision: **ensure-label-before-use → restrict-and-drop**. Paying a
> label-write token scope and an API call per unseen label to preserve labels on 0.3% of beads
> was not justified once the population was correct.

| Needed | Exists? |
| :-- | :-- |
| `type::task`, `type::epic`, `type::feature`, `type::bug` | yes |
| **`type::molecule`** (42 beads) | **no** |
| **`type::chore`** (2 beads) | **no** |
| **`type::decision`** (1 bead) | **no** |
| `priority::high` / `medium` / `low` (P1/P2/P3, presumed) | yes |
| **P4** (1 bead) — no `priority::` label of any name is unaccounted for | **no** |

Three type labels and at least one priority level have no corresponding label.

### Why this matters more under gh than under bd **[inferred]**

`gh issue create --label X` **fails** when `X` does not exist on the repo; it does not create
labels on demand. `bd` evidently does create them — the repo carries `upstream-followup` and
`plan-033-followon`, which are bd-side conventions, not hand-made.

**⚠ This specific claim is [inferred], not [measured].** Verifying it requires a real
`gh issue create` against a nonexistent label, which is an outward-facing write; it was not run.
The label-space gap above **is** measured. **Falsification test, to run as the first execution
step:** `gh issue create --label type::molecule` on a scratch issue — if it succeeds, this whole
concern collapses and the ensure-label step is unnecessary.

If it holds, gh-direct must either **ensure-label-before-use** (an extra API call per unseen
label, plus write permission on labels) or **restrict the emitted set** to labels known to exist
and silently drop the rest — which is a behavior change from bd, and a decision to make
deliberately rather than discover on a failed push.

### `closable` does not complete in 120s on this repo **[measured]**

```
$ uv run skills/yf-beads-upstream/scripts/upstream.py closable --json
(no output after 120s; moved to background)
```

**[inferred]** With 1,000+ beads, the per-bead scan is likely doing an `bd`/API call per bead.
Not a blocker for this plan, but it means the `closable` sweep #131 aims to make useful is
currently too slow to run casually — worth confirming and possibly bounding in scope.

## Implications for Plan

0. **The gap is 3 beads, not ~45** — see the correction banner above. The label *policy* still
   needs deciding; its *stakes* are much lower than this finding first implied.
1. **"~20 lines" understates the work.** The label mapping is unspecified and its target label
   space is incomplete. Reimplementing it means: reverse-engineer bd's mapping, **specify it**
   (SPEC-first), decide the missing-label policy, and implement it. That is an epic, not a line.
2. **The missing-label policy is a real decision** with three defensible answers (ensure-create,
   restrict-and-drop, or fail-loud), and it changes the required GitHub token scope.
3. **This is an argument *for* the swap, not against it.** #133's Measurement 4 says the mapping
   is "opaque" and that `notes`/`design` silently do not sync — documented as a gotcha because we
   do not own it. The label gap is the same defect: behavior we depend on, never specified, and
   incomplete in a way nobody noticed. Owning it makes it fixable.
4. **The `gh`-fails-on-unknown-label claim must be tested first**, before any implementation
   depends on it.

## Recommendations

- Add a SPEC-first epic that **specifies** the bead→issue field mapping (title, body, type,
  priority, labels, `external_ref`) as `REQ-BUP-*` before any code.
- Make the missing-label policy an explicit, operator-confirmed decision.
- Run the `gh --label` falsification test as the first execution issue; record the result.
- Scope-check `closable` performance separately — do not let it silently become this plan's
  problem.
