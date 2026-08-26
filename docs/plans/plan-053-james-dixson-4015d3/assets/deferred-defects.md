---
type: Reference
okf_spec: OKF-PLAN
id: deferred-defects
description: The out-of-scope defects plan-053's investigation measured, each with its evidence (Issue 7.2)
---

# Deferred defects — measured by plan-053, deliberately NOT fixed here

Each row was **measured on the merged tree**, not inferred from a finding. Each is filed
upstream with that evidence.

**The `yf-markdown-*` stale README paths are NOT here.** Issue 3.6's widened `§3` globs pulled
`skills/*/README.md` into the check's scope and Issue 3.7 fixed all ten, so they are *fixed*,
not deferred. A plan must not both fix and defer the same defect (pass-4 C45).

---

## D1 — the COLUMN-0 PARAGRAPH drop: #206's third family member

A column-0 paragraph inside `## Epics` under an open issue is dropped **silently**, with
`unparsed: []` and exit 0 — the same silent-loss signature #206 is about, in a shape neither
Epic 2 fix reaches.

**Measured on the merged tree** (i.e. *after* both #206 fixes landed):

```text
unparsed: []
any issue detail carrying the column-0 paragraph: False
```

**Why plan-053 did NOT widen the fix to cover it** (EXP-001, and it is a real reason rather
than a scoping convenience): a column-0 line is **not a continuation under CommonMark**, so
collecting it into `detail` would be wrong. The right answer is probably `unparsed[]` — which
makes it a *different* change with a different risk profile, not a bigger version of this one.

## D2 — the LEADING-CODE-SPAN trailing declaration is not read

A real trailing declaration sitting behind a leading inline code span yields **no edge**, on
both the base and the fixed tree.

**Measured on the merged tree:**

```text
- Issue 1.2: second
  `foo.py` depends-on: 1.1     ->  depends_on = []   edges = []
```

**Mechanism:** the two-space continuation branch tests the **masked** line, and the leading
mask pushes the first non-space character past column 2, so `^ {2}(?![ \t*-])\S` no longer
matches. Note this is the *parsing* side, which Issue 2.1 deliberately did **not** touch —
2.1 widened **capture** only, and that separation is REQ-DATA-063's stated requirement. Fixing
D2 means changing a parsing branch, which is exactly the class of change that needs its own
RED fixture and its own corpus delta.

## D3 — `yf-incubator`'s `STATUS_VALUES` is DEAD CODE: #208's defect one skill over

`skills/yf-incubator/scripts/incubator-index.py:47` defines a `STATUS_VALUES` set and
**never reads it** — one occurrence in the whole file, the definition itself.

**Measured on the merged tree:**

```text
grep -c STATUS_VALUES skills/yf-incubator/scripts/incubator-index.py  ->  1
```

This is #208's shape exactly, one skill over: a status vocabulary that *looks* enforced and
enforces nothing. plan-053 fixed the `yf-plan` instance (REQ-CLI-026 warns, REQ-DATA-072 fails
closed) and deliberately did not reach into another skill's runtime.

**Note it already contains `abandoned`** — so the fix is to *read* the set, not to extend it.

## D4 — TITLE-BORNE citations (D-13)

`#209`'s provenance header reaches a bead's **description**. It does not reach citations that
migrated into bead **titles**, which is where this repo's newest bundles actually put them.

**Measured:** this repository's four newest bundles carry **zero** non-empty `detail`, and
**plan-053 is itself such a bundle** — 0 of its 46 issues carried non-empty `detail` at pour
time. So plan-053 hit #209 during its own execution and Epic 6 did not reach it.

Recorded rather than papered over: the header still makes a bundle findable from a bead, which
is a real gain on an otherwise-blank description. It is simply not the larger class.

## D5 — `redcheck.sh`'s `YF_TREE` default is a PORTABILITY defect (#210's class)

The adopted plan-050 harness computes

```bash
: "${YF_TREE:=${REPO_ROOT}/.worktrees/${PLAN_ID}}"
```

which is correct **only** when the plan's assets live in the PRIMARY checkout, as plan-050's
did. plan-053 keeps its assets in the EXECUTION WORKTREE — so that fixtures and the fixes they
grade land on the same branch — and there `REPO_ROOT` already *is* the worktree, producing the
doubled path `<worktree>/.worktrees/<plan-id>/`.

**This is #210's class**: an assumption about layout baked into a default that no other layout
satisfies. It is filed because **the harness will be copied by the next plan too**.

**Evidence:** `plan-retrospective.md` RE-003 — the verbatim command, output and exit code, and
the `rc=2` record that would have been banked without the Issue 1.1(b) guard. The guard caught
it on its FIRST REAL USE.

plan-053 fixed its own copy by RESOLVING rather than assuming (probe for
`.worktrees/<plan-id>/_shared`, else use `REPO_ROOT`); the fix belongs upstream in whatever
becomes the canonical harness.
