---
type: Finding
okf_spec: OKF-PLAN
description: 'Post-repair halt profile over all 8 legacy bundles: 8/8 halting becomes 7/8 clearing under --reconcile-objective, with plan-030 alone still blocked by a real phase-log-loss guard; plus the three surfaces EXP-001 never tested'
---
# EXP-004: the post-repair halt profile, and the three untested surfaces

**Issues:** 4.5, 4.6 · **Discharges:** SC17 · **Feeds:** Issue 5.4's follow-on transform issue

This is the measurement the follow-on transform plan starts from. Every number below is a **dry
run**. `backfill --apply` was never run against the repository corpus — that is the follow-on's
work, not this plan's.

## 1. The halt profile, before and after

Run over `docs/plans` + `docs/research`, `--maxdepth 2`, on the merged post-repair tree.

| Run | bundles checked | would-backfill | halted | halt profile |
| :-- | --: | --: | --: | :-- |
| default | 69 | 0 | **8** | `objective-divergence` ×7, `phase-log-loss` ×1 |
| `--reconcile-objective` | 69 | **7** | **1** | `phase-log-loss` ×1 |

**8/8 halting became 7/8 clearing.** The one bundle still blocked is
`docs/plans/plan-030-james-dixson-65526e`, on `phase-log-loss` — a guard protecting the single
measured data-loss mode, so it is correctly blocking and must not be waved through.

**`plan-030` is also the proof that REQ-OKFH-011 landed.** EXP-001 measured that plan-030
*cleared the dry run* and then halted under `--apply`, because `phase-log-loss` was computed
inside `if apply:`. The dry run above now reports that halt **without applying anything**. The
dry run's claim and apply's behaviour are the same claim for the first time.

## 2. The three surfaces EXP-001 did not test

### 2a. The `_index.md` legacy-variant route — a **real defect**, routed to the follow-on

**Measured, both before and after this plan's changes:**

| legacy index | dry run | apply |
| :-- | :-- | :-- |
| `README.md` | `would-backfill` | `backfilled` |
| `_index.md` | `halt` *(after 4.1)* / `would-backfill` *(before)* | **`halt` — `manufactured-hybrid`** |

`okf.migrate` is member-driven and OKF-PLAN's `index_source` is `README.md`. For a bundle whose
legacy index is `_index.md`, migrate finds no `README.md`, **scaffolds a fresh `index.md`, and
leaves `_index.md` beside it** — manufacturing the exact `hybrid-partial` state the tool refuses
to create. The post-condition catches it and halts.

So `REQ-OKFH-010`'s two-variant equivalence is **classified** correctly but **not transformed**
correctly. This was invisible before Issue 4.1 because only the apply path evaluated it; it is a
second instance of the very defect `REQ-OKFH-011` closes, found by closing it.

**It blocks nothing in this corpus:** all 8 remaining targets are `legacy-readme` (§2b). Repairing
it means changing `okf.migrate`'s `index_source` resolution across **six** vendored engine copies,
which is outside every epic of plan-064 — so it is **recorded and filed**, not absorbed.
`test_two_variant_equivalence` now asserts the measured behaviour of each variant, so the
divergence cannot be re-hidden, and that arm **fails** if the routing is ever repaired.

### 2b. Does any target classify `hybrid-partial`? — **No**

Measured over all 69 enumerated bundles: `{conformant: 61, legacy-readme: 8}`. **Zero**
`hybrid-partial`, **zero** `legacy-underscore-index`, **zero** `unclassifiable`. The remaining
population is homogeneous, which removes one of R8's named unknowns.

### 2c. The record contents of a partially-halted batch — **mutated bundles only**

A run that mutates *N* and halts on *M* now reports `mixed_run: true`, the counts separately, and
both bundle lists by name. **The record contains entries only for the mutated bundles**: a halted
bundle was never touched and has nothing to reverse. Asserted by
`test_mixed_run_exit_is_legible`, which also asserts the two lists are disjoint and that a halted
bundle never appears in the record as reversible.

## 3. Why the audit verdict stayed `warn` → `warn` (Issue 4.6)

**Because `warn` is a SATURATING LABEL, not a measure.** `audit_verdict` returns `warn` when the
status is `pass` **and the report contains at least one `[warn]` line**. One residual finding
produces the same label as fifty.

Measured on a sandbox copy of three targets, `--apply --reconcile-objective`:

| bundle | warn findings before | after | cleared |
| :-- | --: | --: | --: |
| `plan-010` | 13 | 2 | **-85%** |
| `plan-012` | 17 | 2 | **-88%** |
| `plan-013` | 52 | 33 | **-37%** |

**The transform clears exactly what it is responsible for, and nothing it is not.** Every
`index.md: missing or empty` finding and every `okf:<file>: REQ-OKF-003: no YAML frontmatter
block` finding is gone — those are the backfill's remit. What remains is:

- **`doc-lint/*`** — the plan document's own schema conformance (`R1b`, `required-sections`,
  table columns, criterion ids). These are properties of `plan.md`'s **content**, which the
  backfill neither touches nor claims to fix. On `plan-013` they are 33 of the 33 residual
  findings.
- **`epic-ref`** — an artifact of the sandbox, where `bd` is unreachable. It does not fire
  in-repo.

**So EXP-001's "the audit verdict does not improve" was true and misleading in the same breath.**
The verdict genuinely did not change; the *bundle* improved by 85-88% on two of three targets. The
verdict was reporting a boolean and being read as a measure — the corpus-level instance of the
"two facts, one signal" class this repository has now recorded a dozen times.

**Consequence for the follow-on:** `verdict: pass` is not the acceptance signal (D4), and neither
is `verdict: warn` a failure signal. The actionable numbers are `legacy: N` and the per-bundle
**finding count**, before and after.

## 4. Residue

Both corpus dry runs left **no** `.okf-hygiene-staging` or `.okf-hygiene-journal` directories and
**no** modification to any bundle (`git status --porcelain` clean apart from this plan's own
files). The dry run stages into a throwaway copy, removes it on both exit paths, and writes no
journal.
