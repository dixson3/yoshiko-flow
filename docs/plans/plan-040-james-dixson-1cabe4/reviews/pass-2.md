---
type: Review
okf_spec: OKF-PLAN
---
# Plan Red-Team: plan-040-james-dixson-1cabe4

**Pass:** 2 · **Date:** 2026-08-16

> **Independent pass** — fresh eyes, tasked with verifying pass-1's resolutions against the plan
> text rather than the resolution table, and finding defects introduced *by* those revisions.

## Verdict: REVISE

REVISE, but narrowly. Two blockers; the rest are one-line propagation misses from the revision
itself. The plan's structure, gates, findings, and both large pass-1 fixes verified correct
against the code and against `yf-plan`'s SKILL.md.

## Strengths

- **Both structural fixes are correct, verified at source.** C2's relocation: `SKILL.md:701` binds
  `${EPIC}` from the pour and `:724` runs `record-epic`, so §5.2a genuinely has the id — and §4.5
  does say *"(once poured)"* while §4.6 says *"No pour happened at intake."* §5.2b is a valid
  idempotent re-stamp site (`resume-scan` reads the `**Epic:**` field). C15's edge cut is sound:
  Epics 3 and 4 touch `upstream.py` but the coordinator serializes beads in one worktree, so
  parallel DAG position costs nothing.
- **The C6 reversal is materially correct.** `CONTAINER_TYPES` drops `{epic, molecule, gate}`, so
  3-of-991 is the real gap; the `hoist --issues <epic-id>` bypass exception is real and correctly
  stated. Issue 1.1's four-outcome table is a genuine premise check on both halves.
- **Mechanical fixes check out under command.** REQ-BUP count is exactly 35 (SC2's baseline);
  `manifest_update.py <dir> --dry-run` prints `no changes (all hashes match)`;
  `beads_hygiene.py:43/579` really does shell `upstream.py hoist`; `upstream_enabled()` is a real
  second `bd` subprocess; `upstream-triage.md` matches plan.md exactly.
- **Both capability gates are reachable**, and the plan records the v1 cycle rather than hiding it.

## Concerns

- **D1 — Issue 2.3, the issue C1 was supposed to fix, still names the wrong guardrail.** — severity: high

  Decision 2 correctly says GR-BUP-001; Issue 2.3 still reads *"Reword **GR-BUP-002** and the
  `REQ-BUP-030` family"*. It pairs a guardrail with the wrong REQ family **and collides with Issue
  2.6**, which correctly claims `REQ-BUP-031 / GR-BUP-002`. C1's fix landed in the decision table
  but not in the issue an executor reads.

- **D2 — SC4 and SC14 cannot both be satisfied.** — severity: high

  SC4 requires `grep -c 'BACKEND_AUTH\|--backend'` → 0; SC14 requires a *named* error on
  `--backend gitlab`, which needs the literal flag detected in argv. Mutually exclusive as
  written. SC14 was added from pass-1's Missing list without reconciling against SC4. Baseline: 7.

- **D3 — SC5's verification command does not run.** — severity: medium

  C9 replaced `--check` with `--dry-run` but dropped the required positional:
  `manifest_update.py --dry-run` → *"the following arguments are required: protocols_dir"*, exit 2.
  This guards R3, the plan's own high-rated risk, and pass 1 claimed it "pinned". *Verified.*

- **D4 — R6's stated mitigation is not assigned to any issue.** — severity: medium

  R6 accepts restrict-and-drop on the strength of *"2.2 specifies that a dropped label is reported,
  not silent"*. Issue 2.2's text says nothing about reporting drops; neither does 3.1 or 3.4. The
  revisit trigger has no producer — the same class as pass-1 C10. (2.2's token-scope clause is
  also vestigial: restrict-and-drop writes no labels.)

- **D5 — the C4 insertion renumbered the test issue; three references still point at the old
  number.** — severity: medium

  R2, R4 and SC3 all name "3.3" for fixture tests / the guard script, which is now the
  `yf-beads-hygiene` issue and produces neither. SC3 is unverifiable as written. #133's Resolved-By
  range also still reads `2.1–2.5, 3.1–3.3`.

- **D6 — decision 5's reversal did not propagate to the gate instructions or context.md.** — severity: medium

  The scratch-write gate still offers *"adopt ensure-label-before-use unverified"* — the reversed
  option, at the decision point. R1 still says *"Issue 2.2/2.3's ensure-label work"*. `context.md`
  still says the plan touches "two" skills and that restrict-and-drop is the *fallback* rather than
  the decision. context.md is the cold-reader artifact, so it is the copy most likely to mislead.

- **D7 — Issue 4.1 says to "delete `external_for`", which has two other live callers.** — severity: low

  Called at `upstream.py:460` and `:495` outside `closable`, and monkeypatched by three tests. The
  suite would catch it, hence low. *Verified.*

## Missing

- **Nothing establishes the `bd` version floor SC15 asks the SPEC to record.** No issue is assigned
  to *determine* it; context.md records 1.1.2 as observed, and SC15 asks it be "marked as a floor"
  — an assertion, not a measurement.
- **No issue owns SC16.** Issue 4.2 writes `closable-after.md` but its text never mentions naming
  which copy of the skill produced the run.

## Gate Assessment

**Start Gate** — well-formed. **Scratch write** — reachable; the "smoke check only / never treat a
green test as consent" relabel is exactly right, but its Instructions carry the stale ungated
alternative (D6). **Upstream write** — reachable and correctly repositioned; `Blocks: {5.2b}` with
evidence from 5.2a and 4.2, both outside the Blocks set, and the 4.2-not-4.4 provenance is now
correct. All three repo-root-relative test clauses resolve from a repo-root cwd. **Reconcile Gate**
— correct type, and now has `resolves-upstream` annotations on 3.4/4.3/4.4/5.2b to act on.

## Upstream Assessment

`upstream-triage.md` and plan.md agree line for line. #133/#117/#131 as one mechanism remains
justified. #117's partial-discharge reasoning still matches REQ-BUP-052's recorded "#117 partial".
#132 supersede is the only close, correctly gated behind draft-then-publish, with SC11b enumerating
all five drafts. R5's softening is accurate — REQ-BUP-040 and GR-BUP-004 already say only GitHub is
tested. #51/#52/#53/#111 excludes are sound and left open with SC11 asserting `OPEN`. Only defect on
this axis is D5's stale Resolved-By range.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| D1 | Issue 2.3 still names GR-BUP-002 | high | Corrected to **GR-BUP-001 / REQ-BUP-030**, plus an explicit **scope boundary with 2.6** (2.3 owns never-bare-sync; 2.6 owns the auth model) so the two cannot both edit the same guardrail. 2.3 also now fixes `SPEC.md:165`'s in-repo misreference | resolved |
| D2 | SC4 and SC14 mutually unsatisfiable | high | SC4 narrowed to what the plan actually wants: `BACKEND_AUTH` → 0 **and** no `add_argument("--backend"…)` in the argparse spec. The blanket `--backend` grep is dropped, with the reason recorded inline — SC14 needs the literal flag detectable in argv to emit a named error | resolved |
| D3 | SC5's command exits 2 without the positional | medium | Verified. SC5 now runs `manifest_update.py skills/yf-beads-upstream/protocols --dry-run` and asserts the literal `no changes (all hashes match)` | resolved |
| D4 | R6's mitigation has no producer | medium | Issue 2.2 rewritten: specifies that **a dropped label is reported, not silent**, naming bead and skipped label on the push preview; Issue 3.4 asserts it in the test suite. The vestigial token-scope clause removed | resolved |
| D5 | Stale 3.3 references after the renumber | medium | R2, R4 and SC3 re-pointed to 3.4; #133's Resolved-By range corrected to `2.1–2.7, 3.1–3.4` | resolved |
| D6 | Decision-5 reversal did not propagate | medium | Gate's ungated alternative rewritten to restrict-and-drop (with the consequence: 1.1's outcomes recorded as untested, so parity-vs-divergence stays unknown); R1 re-pointed to 2.2 only; `context.md` corrected to **three** skills and to state that **no label-write scope is needed** | resolved |
| D7 | "delete `external_for`" breaks two callers | low | Verified (`:460`, `:495`, three tests). 4.1 now says **stop calling it from `cmd_closable`**; do not delete the helper | resolved |
| — | Missing: no producer for the bd version floor | — | Issue 2.1 gains a probe step, with an explicit fallback: declare 1.1.2 a floor **because it is the only version verified**, labelled as an assertion rather than a measurement | resolved |
| — | Missing: no issue owns SC16 | — | Issue 4.2 now records which copy of the skill produced the run in `closable-after.md` | resolved |

**Final status:** all 7 concerns plus both Missing items resolved. Pass 2 frozen.
