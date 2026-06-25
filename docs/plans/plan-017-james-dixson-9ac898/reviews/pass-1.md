# Review pass 1 — plan-017

**Reviewer:** red-team (adversarial)
**Date:** 2026-06-24
**Verdict:** REVISE

## Strengths
- Findings genuinely de-risk the hard parts. E1 validated the full d2→PDF / csv→table /
  pcall-degrade / glyph path in a real xelatex build (exit 0, vector Form XObject, zero
  missing-character warnings). The d2→PDF-not-SVG adaptation and absolute-temp-path
  requirement are empirically pinned.
- Registry/vendoring approach matches the existing `_shared/sync.py` machinery exactly;
  the `json-extract` precedent (canonical → vendored region + `value-equal` edge +
  `sync.py --check`) is a working template. No install/Rust changes — verified.
- `field-set-equal` is a real DRIFT-CHECK contract (used by `e-formula-vars`,
  `e-readme-layout`), so the registry↔Lua-mirror edge is structurally sound.
- Graceful degradation is a first-class design property, verified for missing d2.

## Concerns
| # | Severity | Concern | Recommendation |
|:--|:---------|:--------|:---------------|
| 1 | high | REQ-CLI-006 realignment under-scoped — the stale `check` subcommand also poisons **REQ-CLI-007** (`check --json-output`) and the REQ-CLI-006 verification line (`grep -c '@cli.command' == 2`). Fixing only REQ-CLI-006 leaves the spec internally inconsistent; `research_manager.py` has exactly one command (`json-get`) today. | Expand E.2 to audit **all** of REQ-CLI-006/007/008 against the actual click CLI; repoint REQ-CLI-007's `check --json-output` to the `yf preflight` kernel that replaced it, or descope explicitly. Operator approval must cover the fuller spec edit. |
| 2 | medium | The lint "recognize renderable fences as valid" work is largely a no-op — `markdown_lint.py` already `continue`s over all fenced interiors, so d2/csv blocks are already valid/invisible. The only new behavior is the optional d2-compile rule; the registry's value to lint is thinner than implied. | Reframe A.3 around the new optional ML rule (its actual new behavior) and the registry-membership it needs. Confirm the vendored region is actually referenced by new code (no dead-weight vendoring + drift cost). |
| 3 | medium | d2→PDF temp-file path is a real cleanup/security surface — E1's filter uses hand-rolled `os.time()+random` names in world-readable `$TMPDIR` and `os.execute` string-concats paths into a shell. Cleanup/leak-freedom is unspecified; B.3 tests output correctness, not leaks. | Specify temp discipline in B.1/B.2: `pandoc.system.with_temporary_directory` (pandoc 3.x), arg-vector exec / `pandoc.pipe` not `os.execute` concat, deterministic reaping via `md2pdf.py`'s `finally`. Add a no-temp-leak assertion to B.3. |
| 4 | medium | Glyph fallback validated only on the operator's macOS machine — the result depends on `Arial Unicode MS` being mainfont, which `md2pdf.py` forces to `None` off-macOS. `\newunicodechar{✅}{\symbol{"2714}}` assumes the active font has U+2714 (false under Latin Modern). "No font install needed" is machine-local. | Decide explicitly: macOS-only-best-effort vs cross-platform. State the accepted limitation ("monochrome glyph parity is macOS+Arial-Unicode-MS-specific; off-macOS degrades to xelatex warnings"). Make the "zero missing-character warnings" success criterion not silently machine-bound; B.3 covers an off-macOS graceful-degradation path. |
| 5 | low | Epic ordering: B.1 hand-writes the Lua class list (depends A.1), C.1 later retro-fits it into a generated region — a transient unguarded-manual-copy drift window inside the plan's own execution. | Note in C.1 it must land in the same change-set as B.1 (or add a `field-set-equal` check to B.3); gate the Reconcile auto-gate on `sync.py --check` green. |

## Missing
- No mention that the **existing** CLI-vs-SKILL drift edges (not just the new registry
  edges) must stay green when adding `record-epic` / `embed` / `lift` / `inline` — should
  be an explicit success-criterion line.
- No rollback/disable story for `blocks.lua` on the **default** md2pdf path — every existing
  user now renders d2/csv unconditionally. Consider a `--no-render-fences` opt-out (e.g. to
  document d2 itself verbatim) or document always-on.
- The "`bd remember`/_shared install assumptions" risk bullet is boilerplate — the plan
  never uses `bd remember`. Clean up or remove.

## Gate Assessment
Reasonable: one human Start Gate + auto Reconcile gate fits a multi-skill change touching a
fixed-authority spec. "No capability gates" is sound on the operator's machine but
environment-specific (ties to concern 4). Strengthen the Reconcile auto-gate to additionally
require `sync.py --check` green + new DRIFT-CHECK edges passing, since the plan's integrity
rests on the generated-not-hand-maintained invariant.

## Upstream Assessment
Dispositions sound; all three `include` with clear epic mappings (#33→A/C/D, #34→B, #37→E).
Coarse-granularity reconciliation correctly follows `AGENTS.md`. #37 correctly flagged as
riding along. Only gap: the #37 operator approval must cover the fuller spec edit
(REQ-CLI-006 **and** 007 + verification line), per concern 1.

## Operator Resolutions
| # | Resolution | Status |
|:--|:-----------|:-------|
| 1 | Expanded E.2 to audit all of REQ-CLI-006/007/008 against the live CLI and repoint/descope REQ-CLI-007's removed `check`; operator approval scoped to the whole CLI spec section. | resolved |
| 2 | Reframed A.3 around the new optional d2-compile ML rule (the actual new behavior) + the registry-membership it consumes; vendored region is referenced by that rule, not dead weight. | resolved |
| 3 | B.1/B.2 specify `pandoc.system.with_temporary_directory` + arg-vector exec (no `os.execute` concat) + deterministic reaping; B.3 adds a no-temp-leak assertion. | resolved |
| 4 | Glyph scope declared macOS+Arial-Unicode-MS best-effort; off-macOS degrades to warnings (documented limitation); success criterion + B.3 made not machine-bound. | resolved |
| 5 | C.1 must land in the same change-set as B.1; Reconcile auto-gate strengthened to require `sync.py --check` green + new drift edges passing. | resolved |
| M1 | Added success-criterion line: existing CLI↔SKILL drift edges stay green for new subcommands. | resolved |
| M2 | Added `--no-render-fences` opt-out to B.2 (default-on rendering, explicit escape hatch). | resolved |
| M3 | Removed the boilerplate `bd remember` risk bullet. | resolved |

**Final status:** all concerns resolved in plan v2 (see phase log). Presented to operator for approval.
