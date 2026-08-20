---
type: Reference
okf_spec: OKF-PLAN
id: free-req-ids
description: Free REQ-* id list, derived by grepping the live set (Issue 0.1)
---

# Free `REQ-*` id list (plan-049, Issue 0.1)

Measured at `HEAD = 458092d` on 2026-08-20 by grepping the live set
across `*.md`, `*.py`, `*.rs` and `*.toml` in the repository. Regenerate with the command in
the [Provenance](#provenance) section below.

**Allocation rule.** No issue in plan-049 may allocate a `REQ-*` id before this file lands —
Issue 0.1 is a declared ancestor of every id-allocating issue. Allocate from the **Next free**
column, which is `max + 1` within the family.

**Do not back-fill a gap.** The families are laid out in **decade blocks** (`0x0` opens a
sub-topic), so most apparent gaps are block boundaries, not free ids. The *In-block gaps*
column below reports only gaps with an allocated id **on both sides inside the same decade** —
the only shape that could plausibly be a retired id. Even those are not reusable: a retired
id reused silently rebinds every historical reference to it.

## Live families

| Family | Count | Max allocated | Next free | In-block gaps (do NOT back-fill) |
| :-- | --: | --: | --: | :-- |
| `REQ-AGENT-*` | 30 | 064 | **065** | — |
| `REQ-APPLY-*` | 6 | 006 | **007** | — |
| `REQ-BAUTH-*` | 21 | 041 | **042** | — |
| `REQ-BE-*` | 5 | 005 | **006** | — |
| `REQ-BINIT-*` | 19 | 027 | **028** | — |
| `REQ-BRANCH-*` | 4 | 004 | **005** | — |
| `REQ-BUP-*` | 42 | 064 | **065** | — |
| `REQ-CHECK-*` | 7 | 007 | **008** | — |
| `REQ-CHGVAL-*` | 21 | 024 | **025** | — |
| `REQ-CLI-*` | 26 | 025 | **026** | — |
| `REQ-COMPLETE-*` | 4 | 003 | **004** | — |
| `REQ-DATA-*` | 36 | 050 | **051** | — |
| `REQ-DIAG-*` | 15 | 043 | **044** | — |
| `REQ-DOC-*` | 3 | 003 | **004** | — |
| `REQ-DRIFT-*` | 14 | 030 | **031** | — |
| `REQ-ENGINE-*` | 10 | 010 | **011** | — |
| `REQ-EPIST-*` | 6 | 006 | **007** | — |
| `REQ-FORMULA-*` | 5 | 005 | **006** | — |
| `REQ-HERDR-*` | 22 | 041 | **042** | — |
| `REQ-HYG-*` | 16 | 016 | **017** | — |
| `REQ-INCUB-*` | 18 | 043 | **044** | — |
| `REQ-INFER-*` | 5 | 005 | **006** | — |
| `REQ-INT-*` | 5 | 005 | **006** | — |
| `REQ-JSON-*` | 4 | 004 | **005** | — |
| `REQ-MDFMT-*` | 13 | 021 | **022** | — |
| `REQ-MDHTML-*` | 16 | 031 | **032** | — |
| `REQ-MDLINT-*` | 11 | 020 | **021** | — |
| `REQ-MDPDF-*` | 19 | 051 | **052** | — |
| `REQ-OKF-*` | 20 | 072 | **073** | 033 |
| `REQ-OP-*` | 15 | 015 | **016** | — |
| `REQ-OPTINST-*` | 16 | 030 | **031** | — |
| `REQ-ORCH-*` | 14 | 014 | **015** | — |
| `REQ-PHASE-*` | 7 | 007 | **008** | — |
| `REQ-PLAN-*` | 44 | 078 | **079** | 004 |
| `REQ-PORT-*` | 23 | 053 | **054** | — |
| `REQ-PREREQ-*` | 13 | 023 | **024** | — |
| `REQ-RESEARCH-*` | 14 | 040 | **041** | — |
| `REQ-RESUME-*` | 5 | 005 | **006** | — |
| `REQ-SAFE-*` | 5 | 005 | **006** | — |
| `REQ-SCHEMA-*` | 8 | 008 | **009** | — |
| `REQ-SESSION-*` | 3 | 003 | **004** | — |
| `REQ-SKAUTH-*` | 17 | 060 | **061** | — |
| `REQ-STATUS-*` | 3 | 003 | **004** | — |
| `REQ-STRUCT-*` | 5 | 005 | **006** | — |
| `REQ-YF-*` | 1 | 230 | **231** | — |

## Ids allocated by plan-049

| Issue | Id | Subject |
| :-- | :-- | :-- |
| 0.2 | `REQ-DATA-053` | the `promote = false` schema key: bypass `STATUS_SEVERITY` in both directions |
| 0.4 | `REQ-DATA-051` | the four-layer DAG postcondition — L1 issues, L2 edges, L3 raw referent tokens, L4 gate content — under set/multiset containment |
| 0.5 | `REQ-DATA-052` | the widened trailing-inline `depends-on:` grammar and its refusal cases |
| 3.1 | `REQ-DATA-054` | the `cell-non-empty` check kind, incl. the zero-row table and the two carve-outs |
| 3.2 | `REQ-DATA-055` | the `gate-completeness` check kind, all-three-absent predicate |
| 4.1 | `REQ-DATA-056` | vendor the linter with its transitive closure; explicit root resolution |
| 4.2 | `REQ-DATA-057` | bind the linter into `_audit_plan`; `Inconclusive` -> `warn`, never `fail` |
| 4.7 | `REQ-DATA-058` | the `statuses` schema key: which bundle statuses a check applies to |
| 5.1 | `REQ-DATA-059` | `--exclude <glob>` on both engines; a plan self-excludes from its own corpus counts |
| 5.2 | `REQ-DATA-060` | the in-flight stale-measured-literal rule, at `W`, gated on `status != complete` |

## Provenance

```bash
grep -rhoE 'REQ-[A-Z]+-[0-9]+[a-z]?' \
  --include='*.md' --include='*.py' --include='*.rs' --include='*.toml' . | sort -u
```
