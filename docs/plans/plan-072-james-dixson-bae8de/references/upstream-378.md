---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #378 - Investigate incorporating okf-memory/okf-agent-memory
  into the yf-okf-* skills'
---
# Upstream #378: Investigate incorporating okf-memory/okf-agent-memory into the yf-okf-* skills

- **Number:** 378
- **Title:** Investigate incorporating okf-memory/okf-agent-memory into the yf-okf-* skills
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::high

## Body

Investigation spike. `okf-memory/okf-agent-memory` (https://github.com/okf-memory/okf-agent-memory) is a third-party, MIT-licensed, pure-Go implementation of Google OKF v0.2 — the same baseline `yf-okf` pins as `spec/OKF-BASELINE.md` (`okf_version: 0.2`). It is worth evaluating as a component of, or a conformance oracle for, the `yf-okf-*` skill family.

## What it is

- Git-native memory: a `knowledge/` OKF bundle of plain Markdown + YAML frontmatter, version-controlled, no external DB.
- Zero-dependency Go toolchain, single binary (`okf`), <5ms cold start.
- In-memory BM25 concept search (<300us) and bundle/graph validation (~4ms for 50+ concepts, bidirectional link graph).
- Embedded MCP server (`okf mcp`).
- Progressive disclosure via hierarchical `index.md` files and a link graph.
- Supports OKF provenance (`sources`), trust tiers (`generated` vs `verified`), and lifecycle metadata (`status`, `stale_after`).

## Why it is relevant here

The overlap with our OKF surface is direct:

- `yf-okf` composes OKF-BASELINE u OKF-YF-EXTENSIONS u per-skill OKF-EXTENSION and runs `check` (report-only conformance) and `migrate` (per-folder, in-place). Our BASELINE layer and their validator are checking the *same* v0.2 rules.
- `yf-okf-hygiene` does corpus-level discovery, classification, and the legacy BACKFILL. Their graph validation and bundle parse operate at the same corpus scale.
- Our bundles already use the reserved `index.md` + `log.md` + frontmatter+`type` model — the same progressive-disclosure shape they build on.

## Questions to answer

1. **Conformance oracle.** Can `okf validate` serve as an independent second opinion on OKF-BASELINE conformance, catching baseline drift our own `okf.py` misses? Do our plan/research/incubator bundles pass it today, and if not, is the gap ours or a divergent reading of v0.2?
2. **Engine reuse vs. duplication.** Is any part of `okf.py`'s baseline checking worth replacing with a shim over the Go binary — or does the extra dependency (a Go binary on PATH) cost more than the ~200 lines it would save? Note the yf toolchain is Rust + Python/uv today; adding a third runtime is a real cost.
3. **Search / retrieval.** BM25 over a bundle corpus is something we do not have. Is there a use for it in `yf-plan` / `yf-research` (finding prior plans and reports by concept rather than by grep)?
4. **MCP surface.** Does `okf mcp` offer anything our skills would want to expose, or does it duplicate what the skills already do natively?
5. **Spec divergence.** Their extension layer ("Agent Memory Convention") is a peer of our OKF-YF-EXTENSIONS. Are the two compatible, or would a bundle valid under one be invalid under the other? That answer determines whether interop is even meaningful.
6. **Memory tier.** This repo's AGENTS.md forbids Claude Code memory and defines a two-tier model (`bd remember` ephemeral / AGENTS rules + beads durable). Does a git-native `knowledge/` bundle belong as a third tier, or does it collide with the existing two?

## Expected output

A recommendation, not an implementation: adopt / adopt-partially (naming which layer) / reject, with the reasoning recorded. If the answer is adopt, a `/yf-plan` follows.

## Non-goals

- No vendoring or dependency addition as part of the investigation itself.
- No change to the pinned `okf_version: 0.2` baseline without a separate SPEC-first change.
