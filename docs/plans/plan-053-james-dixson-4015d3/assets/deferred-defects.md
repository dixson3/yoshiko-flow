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

## D6 — `bd close` REFUSES AND EXITS 0 on a bead blocked by an open dependency

`bd close <id>` on a bead with an open blocking dependency prints

```text
cannot close <id>: blocked by open issues [<other-id>] (use --force to override)
```

**and returns exit code 0.** The refusal is real and correct; reporting it as success is not.

**Measured directly, on this repository:**

```console
$ bd close yf-mol-bh8.3.3 --reason "TEST"
cannot close yf-mol-bh8.3.3: blocked by open issues [yf-mol-bh8.3.2] (use --force to override)
$ echo $?
0
```

**This is exactly the defect class plan-053 exists to close**, in the tool the plan is tracked
with: an operation that declines to act and reports success. Every consumer that branches on
the exit code — which is every non-interactive consumer — records a close that never happened.

**Measured blast radius, in this plan's own execution.** Six of plan-053's issue beads
(`2.3`, `3.2`, `4.4`, `4.5`, `5.0`, `7.1`) silently failed to close. The divergence was caught
from *outside* the session by an observer comparing the ledger against the completion reports;
nothing inside the run detected it. The Reconcile Gate would eventually have caught it — but
only **after** the upstream filings had already gone out, which is the worst possible ordering
for an outward-facing write.

**Suggested remedy:** exit non-zero on a refusal. `2` would fit an INCONCLUSIVE reading
("the instrument declined to act"), `1` a FAIL reading; either is enormously better than `0`.

**A second, lesser finding alongside it:** `bd close` accepts no `--notes` flag (only
`-f/--force`, `-r/--reason`, `--reason-file`), which is fine — but the combination of an
unknown flag and a caller suppressing output is what created the head of the cascade above.
That half is a caller error, recorded honestly in `plan-retrospective.md` rather than blamed
on the tool.

## D7 — Success-Criterion COMMANDS are never executed before approval (the residual finding)

Not a code defect — a **process** one, and the most valuable thing plan-053 produced about
itself.

### The measurement

plan-053 ran **five red-team passes** over **53 concerns**, heavily focused on its Success
Criteria. Three criterion defects survived into execution. **All three were in criterion
MECHANICS — the command as typed. None was in criterion SEMANTICS.**

| | Defect | Caught | By what |
| :-- | :-- | :-- | :-- |
| SC16 | wrong command path | planning (pass-2 C19) | someone **ran** it: exit 2 `Failed to spawn` |
| SC6 | `grep` resolves to a ugrep shell function, not `/usr/bin/grep` | Epic 3 | **running** it — reported a TRUE criterion FALSE |
| SC19 | `json-get epic < plan.md` — a JSON extractor reading markdown | Issue 7.3 | **running** it — `Cannot index object with number` |

### The asymmetry that IS the evidence

- **11 of 11 controls** carried **zero** mechanics defects into execution.
- **3 of 23 verifiable criteria** carried one.

The difference is not care or attention — it is **D-4**. Every `ctl-` fixture had to be
**observed RED before its fix existed**, so no control could reach execution with a command
that does not run. **No such discipline applies to criteria.**

### The structural point

A Success Criterion is a **claim plus an instrument**. A review that audits only the claim
leaves the instrument unexamined. This plan's thesis is *"a step with no exit code is not a
step"*; the corollary it discovered about itself is:

> **A criterion whose command was never executed is not a criterion.**

### The remedy, and it is cheap

At the end of PLAN, before `ready-check`, **execute every criterion command once and record the
exit code.**

Most will fail — correctly, since the work has not been done. That is fine, because **all three
defects above are distinguishable from an honest not-done-yet failure**: `Failed to spawn` (2),
a false negative on a condition already true, and a `jq` type error. None resembles "not done
yet".

This is simply **extending D-4's existing discipline from controls to criteria**.

## D8 — `audit-close`'s OKF check has no fixture carve-out, so pinned fixture corpora fail it

Found at plan-053's own close step, by running `audit-close`.

### Measured

```text
Counter({'fail': 26, 'warn': 19})
fail findings NOT in a pinned fixture tree: 1
```

**25 of 26 `fail` findings are pinned-fixture files** under
`docs/plans/<plan>/assets/fixtures/corpus/**` — verbatim frozen copies of real repository files
(`SKILL.md`, `SPEC.md`, `DRIFT-CHECK.md`, `web/content/*.md`) captured at a pre-fix commit so a
control can be driven RED against them.

They are reported as:

```text
REQ-OKF-003: no YAML frontmatter block
REQ-OKF-003: missing or empty `type`
REQ-OKF-030: missing `okf_spec` member key
```

All true, and all irrelevant: **a frozen copy of a non-OKF file is not a bundle artifact.**
Adding OKF frontmatter to them would *corrupt the fixture*, because the fixture's whole purpose
is to be byte-faithful to what the tree looked like.

The same applies to the one remaining `dangling-refs` finding: `ctl-214-pre-fix/SPEC.md`
contains `../` parent traversal because **the real `SPEC.md` does**.

### Why this is a known class, already solved once in this same plan

Issue 3.6 hit precisely this and carved it out — `skills/*/scripts/fixtures/**` is excluded
from `check_skill_script_refs.py` because *"it holds corpus fixture documents carrying
arbitrary invocations by design"* (pass-4 C45). `audit-close`'s OKF walk needs the same carve
for `assets/fixtures/**`.

### Why it did not halt anything

`audit-close` is **advisory by contract** (`REQ-PLAN-075`) — it exits 0 unconditionally and
never gates `set complete`. So this is noise, not an outage. But it is *loud* noise that will
recur for **every** plan that pins a negative fixture, and pinned negative fixtures are the
standard remedy for the SPEC-first ordering inversion (plan-052 Issue 0.3, plan-053 Issues 1.6a
/ 1.6c / 5.4 / 6.1). The technique is becoming common; the false positives will scale with it.

### Suggested remedy

Exclude `assets/fixtures/**` from `audit-close`'s OKF conformance walk and from its
dangling-ref scan, mirroring the carve `check_skill_script_refs.py` already ships.

### A second, much smaller note

One finding is genuine and deliberately left: `plan-retrospective.md` quotes an absolute
`/Users/...` path. That path is **verbatim evidence** in an RE-entry — the whole value of the
entry is that the command and its output are reproduced exactly — so genericising it would
weaken the record to satisfy a portability rule aimed at something else.
