---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #240: codex budget check models ONE AGENTS.md; codex concatenates several against the same cap

- **Number:** 240
- **Title:** codex budget check models ONE AGENTS.md; codex concatenates several against the same cap
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

The codex block-size budget check (`CodexBudgetCheck`, #120) models codex's
`project_doc_max_bytes` cap against **one file** — the user-scope `~/.codex/AGENTS.md`. Codex
concatenates **multiple** `AGENTS.md` files (user scope plus project scope, and up the
directory tree), and the cap applies to the **concatenation**.

## Why it matters

The check can report "under the cap" for a user-scope file while the effective concatenated
document is over it — at which point codex silently truncates, and the always-loaded rules the
whole cross-harness design rests on are partially absent with nothing saying so.

`REQ-YF-TUNE-027` records the single-file scope as a **chosen limitation**, so this is a known
gap being filed rather than a contradiction. plan-054's EXP-005 specifically re-examined
whether #120 had a multi-file residual and concluded the *issue as scoped* did not — this files
the residual as its own item instead of quietly widening a closed issue.

## Scope

- Enumerate the `AGENTS.md` files codex would actually concatenate for a given cwd.
- Budget the concatenation, not the single file.
- Amend `REQ-YF-TUNE-027` when the limitation is lifted.

Discovered by plan-054 (release-readiness pass), out of scope for that plan.

