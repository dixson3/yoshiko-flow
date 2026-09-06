---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #295 - plan-057 follow-on: 8 unresolved backfill halts
  (SC19) and 4 ungranted reconcile comments (SC24)'
---
# Upstream #295: plan-057 follow-on: 8 unresolved backfill halts (SC19) and 4 ungranted reconcile comments (SC24)

- **Number:** 295
- **Title:** plan-057 follow-on: 8 unresolved backfill halts (SC19) and 4 ungranted reconcile comments (SC24)
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::medium

## Body

## Deferred from plan-057: two criteria left FALSE by operator decision

plan-057 is `status: complete` at 28 of 30 criteria. The two outstanding are **not defects** — each needs an operator judgement the plan deliberately reserved. Filing so they are not lost in a completed plan's retrospective.

### SC19 — eight fail-closed backfill halts, unresolved

`backfill --apply` transformed 23 of 31 legacy bundles and **halted on 8**, which is exactly decision **D-5**'s prediction. The halted bundles are **untouched**:

| Class | Count | Bundles |
| :-- | --: | :-- |
| `objective-divergence` | 7 | plan-010, 012, 013, 014, 021, 023, 026 |
| `phase-log-loss` | 1 | plan-030 |

**`objective-divergence`** — the legacy `README.md`'s objective differs from `plan.md`'s H1, and D-5 records that the README is *richer* in plan-010 and plan-013. Resolving each is a human decision about which text is canonical; a tool cannot pick.

**`phase-log-loss`** — plan-030 carries `README.md` (9 phase-log bullets) **and** `log.md` (1 bullet). D-5 named it as stranding 10 bullets, and the fail-closed check that caught it runs only in the apply path, after staging — so the dry run could not predict it. This is the guard working on the one case the plan said it would.

`SC19` (`--require-legacy 0`) stays FALSE until these are resolved.

### SC24 — upstream reconcile comments, ungranted

Four `gh` comment bodies are **pre-written and `doc_lint`-clean** at `docs/plans/plan-057-james-dixson-9ecf1c/assets/upstream-drafts/`, for the `partial` rows: **#140**, **#170**, **#171**, **#189**. Each records what shipped and what remains, and leaves the issue OPEN — which is what `partial` means.

`verify-reconcile` stays non-zero until they are posted. No upstream write was authorized during execution, and the executor correctly parked rather than writing.

### Also carried forward

- **RE-002** — Issue 0.5 cites `REQ-CLI-018`, which is `verify-reconcile`; the harness contract it means is `REQ-CLI-029`. Work was done against the correct requirement and `plan.md` was left unedited to avoid staling an approved fingerprint over a typo. Six red-team passes read that line without checking the id resolved to what the sentence described — an instance of #289.
- **RE-006** — the Issue 2.9 backfill was applied without operator authorization; the operator subsequently accepted it. Mechanism defect filed as **#293**.

### Not blocking anything

plan-057 is complete and merged (`a667865`); the corpus is repaired; `FULL` tier is 57/57. These are follow-on work items, not regressions.

