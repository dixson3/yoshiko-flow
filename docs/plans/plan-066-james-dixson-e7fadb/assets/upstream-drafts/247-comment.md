---
type: Asset
okf_spec: OKF-PLAN
description: "Posted comment for upstream #247 (manifest gap) — POSTED 2026-09-07; issue LEFT OPEN as a partial."
---
<!-- THE POSTED BODY IS EVERYTHING BELOW THIS COMMENT. The frontmatter above is
     bundle metadata (OKF REQ-OKF-003) and was NOT part of the upstream write:
     posted; #247 stays open. -->

## Partially addressed by plan-066 — this issue STAYS OPEN

`plan-066-james-dixson-e7fadb` closed the **four Class-B coverage gaps #317 enumerates**, which
are a subset of this issue's manifest gap. Recording what moved, so the remainder is legible.

### Closed here

- **`web-diagram-src`** node (`web/content/images/*.d2`) with edges to the frontmatter contract,
  `harness_desc.rs` and the formula set — the `.d2` files were previously unreachable by any edge,
  because the three existing count edges were scoped to two `.md` pages.
- **`e-web-cli-surface` widened**, all three edits: `yf/src/harness_desc.rs` added to the source
  node, a **§6 trigger row for that path** (it had none, so a widened node would still never have
  fired on its own source edit), and the contract rewritten from `path-resolves` to `value-equal`.
- **`upstream-backend-truth`** node + two edges for the backend claim.
- **`web-content-prose`** node + `e-web-prose-status`, replacing a `web/content/**` fan-out that
  reached `e-status-values` **alone** — a plan-status-literal subset check, so seven content pages
  had no coverage at all.
- **`e-okf-version-pin`'s §2 Check Category was `value-equal`** — a §3 *Contract* term outside the
  §2 vocabulary, so **that edge selected no check engine and was vacuous**. Corrected to
  `contract`.

### Also relevant to this issue's framing

The plan's Epic 0 found and repaired a contradiction in the engine's own spec: `REQ-CHECK-004(a)`
mandated a node-level whole-corpus check while `REQ-CHECK-005` confined the verifier to §6-scoped
**edges**, and §6 mapped globs to edges only — so that check had **no firing surface at all**.
`REQ-CHECK-008` now allows a **node-keyed** §6 row, and `REQ-SCHEMA-002` was widened so such a row
passes referential closure. Two node-keyed rows now exist.

### Why it stays open

This plan took the four gaps its own scope named. **#247's manifest gap is broader**, and a
follow-on plan is expected to add a `DRIFT-CHECK.md` amendment making **omissions FAIL** rather
than pass by design — which is a change to the manifest's semantics, not another node.
