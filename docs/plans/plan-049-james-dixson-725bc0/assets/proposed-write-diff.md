---
type: Reference
okf_spec: OKF-PLAN
id: proposed-write-diff
description: Dry-run diff of the two corpus-write target documents (Issue 3.2a / SC35)
---

# Proposed write diff (plan-049 Issue 3.2a)

**Criterion:** SC35 · **Produced:** 2026-08-20, as a **dry run into a scratch tree** — the
repository was not touched to make this file.

## Why this file exists at all

The corpus-write gate is the only place plan-049 asks an operator to authorize a change to a
document it did not write. SC35 requires the evidence for that decision to come from an
**ancestor** of the gated issue rather than from the issue the gate blocks: Issue 3.2a produces
this diff, Issue 3.3 performs the write, and 3.2a is deliberately outside the gate's `Blocks`
set. An operator asked to authorize a write should be reading a diff that already exists, not
one that will be generated after they say yes.

## Scope: exactly two documents

| Document | Change | Lines |
| :-- | :-- | --: |
| `docs/plans/plan-008-james-dixson-382e8a/plan.md` | relocate the `Capability Gate: d2 present` block out of `## Epics` and into `## Gates`, replacing the bare `(see above)` stub | 7 moved, 1 stub replaced |
| `docs/plans/plan-015-james-dixson-cb2ef4/plan.md` | de-bold the title parenthetical on `Issue B.3` | 1 |

No other file in `docs/plans/` is touched. Every other recovery in this plan came from widening
the **reading** grammar, which modified zero documents.

## Measured effect, per document

| Document | Issues | Edges | Residue (`unparsed[]`) |
| :-- | :-- | :-- | :-- |
| `plan-008` | 13 → 13 | 15 → 15 | **8 → 3** |
| `plan-015` | 15 → **16** | 15 → **16** | **4 → 1** |

`plan-008` does **not** clear. Three refusals remain after the relocation, which the plan
predicted and which are recorded rather than hidden.

`plan-015`'s single edit cascades to three residue rows: de-bolding the parenthetical makes
`Issue B.3` parse, which simultaneously fixes the "column-0 bullet is not a conformant issue
bullet" row, the "sub-key bullet with no owning issue" row beneath it, and the
`depends-on target 'B.3' is not a declared issue` row on `Issue B.4` that referenced it.

## The DAG guard verdict on this exact write

```
$ uv run _shared/dag_guard.py verify --pre <post-widening>.json \
    --post <dry-run>.json --upper-bound --json
{ "verdict": "PASS", "failing_layers": [], "losses": 0, "over_upper_bound": [],
  "removed_empty_gates": [ { "plan": "plan-008-…", "gate": "Capability Gate: d2 present (see above)" } ],
  "hash_note": { "moved": [ "plan-008-…", "plan-015-…" ] } }
```

Three things in that verdict are worth reading deliberately:

- **`losses: 0` with a NON-EMPTY L4 population.** This is SC11's requirement. L1–L3 show zero
  delta on a relocation (EXP-002 mutant C measured it), so a guard asserting only those would be
  a no-op over exactly the write it brackets. L4 carries `Capability Gate: d2 present` with all
  four of its fields — `type`, `condition`, `test`, `blocks` — before and after, so the
  relocation is verified content-preserving rather than merely assumed to be.
- **`removed_empty_gates` is a NOTE, not a loss.** The `(see above)` stub is a heading with no
  declared fields; removing it is the very thing `gate-completeness` (REQ-DATA-055) reports as a
  vacuous gate. It is reported so the removal is visible, and does not fail the write.
- **`hash_note.moved` lists both documents, and the verdict is still PASS.** A hash-moving,
  DAG-preserving write is what a legal relocation *is* (SC4). The predecessor postcondition
  gated on exactly this and was therefore all-or-nothing.

## The diffs, verbatim

### `plan-008-james-dixson-382e8a/plan.md`

```diff
@@ -265,6 +265,11 @@
   broken reference (FAIL/INCONCLUSIVE per the manifest). The positive case guards against a
   verifier that flags everything (or nothing). Remove the fixtures.
   - depends-on: 3.2
+
+## Gates
+### Start Gate (mandatory)
+- Type: human
+- Approvers: operator
 
 ### Capability Gate: d2 present
 - Type: human
@@ -273,14 +278,7 @@
 - Test: `command -v d2 && d2 --version`
 - Blocks: Issue 1.5 (self-verify renders), Issue 2.x / 3.x verification (need rendered PNGs)
 - Instructions: `brew install d2` (already done on the dev machine; v0.7.1).
-
-## Gates
-### Start Gate (mandatory)
-- Type: human
-- Approvers: operator
 
-### Capability Gate: d2 present (see above)
-
 ## Risks & Mitigations
 - **First-run Chromium download (~140MB, network).** d2-native PNG silently fetches a
   playwright Chromium (+ playwright-go driver) on first render. *Mitigation:* the warm-up is
```

### `plan-015-james-dixson-cb2ef4/plan.md`

```diff
@@ -207,7 +207,7 @@
   exit non-zero on fail; mark **INCONCLUSIVE** (via an inlined ~10-line `tool_on_path`) when a
   required tool is absent (never a false green).
   - depends-on: B.1
-- Issue B.3 **(staged — the self-maintaining tier, red-team C2)**: `check-drift` subcommand —
+- Issue B.3 (staged — the self-maintaining tier, red-team C2): `check-drift` subcommand —
   re-read signals, diff against the recorded §2 fingerprint, emit a JSON **re-proposal**
   (added/removed/changed signals + the proposed tier delta); **never auto-rewrites** the manifest.
   Sequenced after the MVP (A–D, dogfood E.1) proves out; independently reviewable and deferrable to
```

## Reversibility

The write runs on a clean git worktree, so `git checkout -- docs/plans` restores both documents
exactly. The guard brackets the write: a FAIL means revert, and nothing downstream of Issue 3.3
proceeds.

## To authorize

Record authorization in the file the gate's `Test:` names, then re-run the gate:

```bash
echo "authorized: <name>, <date>, having reviewed assets/proposed-write-diff.md" \
  > docs/plans/plan-049-james-dixson-725bc0/assets/write-authorization.txt
```

The gate is `Type: human`. It is never resolved on the operator's behalf, and a green test
elsewhere can never substitute for it.
