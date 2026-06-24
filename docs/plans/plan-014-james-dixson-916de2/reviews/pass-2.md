# Review pass-2 — plan-014 (re-review, cycle 2)

**Verdict:** REVISE (conditional APPROVE — "pin the shape and this is APPROVE")
**Date:** 2026-06-24
**Reviewer:** red-team (adversarial), after the #15-only re-scope

## Strengths

- C1 fully resolved — the "extract from drift-check"/generic-lib fiction is gone; `_shared/` =
  classifier only; drift-check-is-prose acknowledged.
- C5 split clean (3 epics, #15-only, #27+#25 deferred with recorded dependency direction).
- C2 enforcement point pinned precisely to the yf-drift-check on-edit trigger; `--check` demoted
  to CI/manual backstop.
- Missing items addressed (authority inversion + full nodes↔edges↔§3↔§6 consistency in B.3/B.4).
- C3/C4/C6 correctly deferred with owner — verified none leaked back in.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| N1 | high | "import/include the vendored `active_set`" spans two incompatible shapes: (a) true `import` (works at script runtime but breaks the single-file `spec_from_file_location` test loaders + relaxes the one-script-one-file convention) vs (b) regenerate the inlined fenced block in-place (matches the `e-classifier-copy` precedent, keeps scripts self-contained, tests untouched). Unpinned. | Pin to **(b)**: the sync tool overwrites the fenced region in each consumer from canonical; `value-equal` compares the region; no `import`. |
| N2 | medium | Under shape (a) a new `scripts/active_set.py` file would be a new generic `script` node → must be added to both skill README layout fences (`e-readme-layout`) + scoped by `e-skill-script-cli`/`e-json-contract`. B.3 only budgets classifier edges. | Adopting (b) makes this vanish (no new file). State explicitly no new `script` node is created. |
| N3 | low | The existing `classifier-canonical` node points at the hygiene file; migration must **re-point/replace** it and **delete** the old pairwise `e-classifier-copy`, not just add copies. | B.3 reworded to explicit delete + re-point, then add 2 derived copy edges. |

## Missing

- One line that `_shared/sync.py` itself follows the repo `uv run --script` + PEP-723 convention.
- One line that vendored copies are committed source (not gitignored) — the thing install copies verbatim.

## Gate Assessment

Start (human) + Reconcile (auto → C.2) sufficient for a 3-epic mechanical plan; no capability
gate needed now the runner/inference work is deferred. Dependency chain coherent. N1 is a
plan-level fix, not a gate.

## Upstream Assessment

Dispositions sound (coarse one-plan-tracker). Nit: prefer **annotate-and-narrow** over close on
#15 (only one helper delivered, by vendoring not import-sharing) so the follow-on keeps the #15
thread.

## Operator Resolutions

| # | Resolution | Status |
| :-- | :-- | :-- |
| N1 | Pinned to shape **(b)** — regenerate the inlined fenced block in-place from canonical; no `import`; scripts stay self-contained; `value-equal` compares the fenced region (as today). Approach + A.2 + B.1 reworded. | resolved |
| N2 | Vanishes under (b): no new `scripts/active_set.py` file, so no new `script` node, no README-layout fallout. Stated explicitly in B.3. | resolved |
| N3 | B.3 now explicit: re-point/replace `classifier-canonical` to `_shared/active_set.py`, **delete** the old pairwise `e-classifier-copy`, then add 2 derived copy edges. | resolved |
| Missing | A.2 notes `sync.py` follows `uv run --script` + PEP-723; glossary/A.2 note vendored copies are committed source. | resolved |
| Upstream nit | C.2 reworded to **annotate-and-narrow** #15 (not close), preserving the follow-on thread. | resolved |

**Status:** resolved — shape pinned to (b), N2/N3/Missing folded in. Plan ready for portability audit + INTAKE.
