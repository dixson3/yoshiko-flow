---
type: Review
okf_spec: OKF-PLAN
id: pass-3
plan: plan-042-james-dixson-98631b
created: '2026-08-17'
verdict: APPROVE
status: resolved
---

# Review pass 3 — adversarial (red-team)

## Verdict: APPROVE

1 medium, 3 low. **Both cycle-2 highs and all four mediums verified landed in the body** — by
grep, not from the resolutions table, per the standing instruction this bundle earned after
three instances of a resolution asserted but never applied.

> *"C1 is a one-sentence edit and should be made before intake, but it does not warrant a fourth
> review cycle — the gate's authoritative fields are correct and internally consistent."*

## Verification of cycle-2 claims

**H1 — the superseded predicate: LANDED.** Nine `permissions` occurrences remain in `plan.md`,
**all nine deliberate**: `~~D-C1~~`'s strikethrough, D-R's rationale, three instances of the
D-N *flag name* `--allow-permissions-write`, the E4 finding, Issue 3.0's literal JSON paths, the
gate Instructions describing the danger, and Issue 3.1's explicit *"Do NOT use a `permissions.*`
key-path test"*. Issue 3.1 now reads *"the computed change set contains no entry declaring
`consent_required: true`"*; 3.6 covers all three profiles; the gate Condition keys on
`consent_required`; Scope and `context.md` both name D-R.

**H2 — D-R unimplementable: LANDED, all five sub-claims verified.** Issue 0.6 amends
`REQ-YF-TUNE-001` quoting its exhaustive-enumeration language; Issue 3.0 sets the flag on the
four entries; `3.1 → 3.0`, `0.5 → 0.6`; Issue 0.3 names `REQ-YF-TUNE-012`; SC11 lists all five
SPEC items.

**M1–M4, L1–L6: LANDED.** Issue 3.8 exists as the sole flip off `--rules-only`; `--prune`
orphans cleared (remaining hits all historical); `3.3 → 3.1, 2.1`; the 22→24 arithmetic stated;
SC numbering has no duplicate; the gate test lost its `2>/dev/null`.

## Graph verification

All 25 issues, all `depends-on` lines enumerated. **Every edge resolves; the graph is acyclic**
— the only backward-looking edge, `1.3 → 2.1`, terminates at `2.1 → 0.3`, which reaches nothing
in Epic 1. 0.1 is the sole root, no node orphaned.

**Gate ancestry ∩ Blocks = ∅**, verified transitively: 3.6's full ancestry is
`{3.2, 3.1, 0.4, 3.0, 0.6, 0.2, 0.3, 0.1}` against `Blocks = {3.8, 3.3, 4.1}`. *"The 3.6/3.7
split does exactly what it claims."* And *"nothing else can write config"* holds — the exec
string stays `--rules-only` until 3.8 flips it.

## Strengths (verbatim)

- *"The gate's `Condition` is now a property of the profile schema (`consent_required`), so it is
  falsifiable per-profile rather than per-key-prefix — and 0.6 makes that field exist in SPEC
  before 3.0 writes it and 3.1 reads it. That is a correctly ordered SPEC-first chain, not an
  assertion."*
- *"Isolating the dangerous flip into a one-line issue (3.8) is the right structural move: it
  makes the Epic-2-independence claim mechanically true rather than rhetorical, and shrinks the
  gate's blast radius from 'an epic' to 'one line'."*
- *"D-P's refusal to claim the scope shrank, and R5's admission that the risk was previously
  false with its severity inverted, are unusually honest self-corrections for a plan under
  revision pressure."*

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| C1 | **R5's mitigation still said the gate blocks Issue 2.2**, contradicting `Blocks:` and the Instructions, which name 2.2 as explicitly *not* blocked. *"This is the M1 fix propagated to the Gate section but not to the risk table — the same partial-propagation pattern that produced pass-2's H1."* Not an execution blocker (the machine-consumed `Blocks:` field is self-consistent), but an executor reading risks first could gate the wrong issue. | medium |
| C2 | **The gate's `-ge 3` threshold under-counts its own Condition.** Issue 3.6 specifies four scenario classes, one of which must hold on each of three profiles — a faithful implementation is ≥ 6 tests, so a 3-test partial passes the non-emptiness check. | low |
| C3 | **The issue count is 25, not the 24 D-P states.** The 22→24 arithmetic was right when pass-2's M4 was written; adding 3.8 for M1 made it 25 and the sentence was not updated. | low |
| C4 | **Issue 2.3 (`--no-sync`) had no edge forcing it before 2.2.** Its text says *"lands with or before 2.2/1.3"* and D-E requires the opt-out never trail the wiring, but nothing enforced it. Bounded (2.2 emits `--rules-only`, so the unguarded window cannot write config), hence low. | low |

## Gate Assessment

*"Reachable and correctly placed."* The deadlock pass-1 flagged is genuinely resolved by the
3.6/3.7 split, *"and the Instructions now record why the split exists so a future editor cannot
re-merge them innocently."* The `Blocks` set is *"minimal and correct"* — 3.8 (the only config
write), 3.3 (config-half behavior), 4.1 (documents the path).

## Upstream Assessment

Unchanged and sound. #154, #155, #156 excluded with reasons that distinguish *routing around*
from *fixing* and *raising frequency* from *creating*. The `_to file_` tracker is correct for
Phase 4.5 intake, not a gap.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | R5 said the gate blocks 2.2 | medium | Fixed and **grep-verified** (`grep -c "blocks Issue 2.2"` → 0). R5 now names **Issue 3.8** — *"the single issue that flips the exec off `--rules-only`"*. Fourth instance of partial propagation in this bundle; grep verification is now applied to every edit rather than to the ones that look risky. | resolved |
| C2 | Test threshold under-counts | low | Raised to `-ge 6`, and the gate now states explicitly that **the count is a floor against the empty-filter trap, not a coverage measure** — profile coverage is verified by reading 3.6's module. | resolved |
| C3 | Count is 25, not 24 | low | Corrected to 22 → **25**, noting 3.8 arrived from pass-2 M1 after the earlier count was written. | resolved |
| C4 | 2.3 not forced before 2.2 | low | Fixed: `Issue 2.2 depends-on: 1.3, 2.3`, making D-E's "never trailing" requirement machine-enforced rather than prose. Re-verified: 25 issues, no dangling edges, still acyclic. | resolved |
