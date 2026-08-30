---
type: Reference
okf_spec: OKF-PLAN
description: 'Operator authorization for plan-060''s own upstream reconcile writes, granted 2026-08-30 — nine comments, and NO issue closures. Records what was withheld as deliberately as what was granted.'
---
# Upstream write authorization — plan-060

**Granted by the operator on 2026-08-30**, relayed through the controlling session. This
authorization is not mine and I did not grant it.

## What was authorized

**Reconcile COMMENTS on every non-exclude row of the plan's Upstream Issues table.** Nine
actions, enumerated here per action rather than per issue, because `_grant_coverage` checks per
action — a per-issue check is exactly what let plan-048's `#172` closure slip through
unauthorized.

| # | Issue | Disposition | Action | Authorized |
| --: | :-- | :-- | :-- | :-- |
| 1 | `#301` | include | comment | **yes** |
| 2 | `#293` | partial | comment | **yes** |
| 3 | `#263` | partial | comment | **yes** |
| 4 | `#222` | partial | comment | **yes** |
| 5 | `#204` | partial | comment | **yes** |
| 6 | `#230` | partial | comment | **yes** |
| 7 | `#302` | partial | comment | **yes** |
| 8 | `#303` | partial | comment | **yes** |
| 9 | `#304` | partial | comment | **yes** |

## What was WITHHELD, and why it is recorded here rather than omitted

| # | Issue | Disposition | Action | Authorized |
| --: | :-- | :-- | :-- | :-- |
| 10 | `#301` | include | **close** | **NO — deliberately withheld** |

**`#301` STAYS OPEN.** Its disposition is `include`, whose contract
(`UPSTREAM_REQUIREMENTS`) requires end state `CLOSED` — so this authorization is deliberately
**narrower than the plan's own dispositions require**. The operator's reason: the work is
**landed-in-branch but not merged and not deployed**, so "done" is false. Closing it would be an
outward statement that is not true.

**This is recorded as a WITHHOLDING, not as an omission.** plan-048's grant file missed `#172`'s
close and its own amendment names the cause — *"Its omission from the original list was an
oversight in THIS FILE, not a decision to withhold."* The distinction only survives if the file
says which one it is. This one is a decision.

## The consequence, stated rather than hidden

**The gate's own `Test` will NOT pass against this file**, because `_grant_coverage` checks per
action and action 10 is uncovered. That is the correct behaviour and must not be worked around:

- the check is right that the plan's declared dispositions are not fully authorized;
- the operator is right that `#301` must not be closed today;
- and `verify-reconcile` will later report `#301` as not reaching its required end state.

**That disagreement is the honest signal and is to be left standing.** The precedent is plan-057
Issue 3.5, where closing a bead as deferred made a gate's mechanical condition read true while its
four comments were unposted — `verify-reconcile`'s exit 1 was the only honest signal in the room.
A grant file edited to silence the check would reproduce that defect exactly.

## Scope limits carried forward

- **No issue is closed by this authorization** — not `#301`, not any other.
- It authorizes **plan-060's own** reconcile writes only. The per-landing grant that
  `land --apply` requires at runtime for OTHER plans is a separate precondition
  (`REQ-LAND-021`), unaffected by this file.
- It is **not** authorization to merge, to push, or to redeploy. **G3 (redeploy) is DEFERRED —
  neither granted nor denied** — and G4 remains open.
