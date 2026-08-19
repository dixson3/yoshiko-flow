---
type: Note
okf_spec: OKF-PLAN
---

# D-13 SPLIT PROPOSAL — the gate tripped (Issue 10.0)

**This is designed behaviour, not a failure.** D-13 declared the split point *before*
execution began rather than discovering it mid-run, and Issue 10.0 makes it a **gate rather
than a request** by exiting non-zero.

```json
{"tripped":true,"review_cycles":4,"threshold":4,"remaining_open_issues":39,"epic":"yf-mol-63g"}
```

Trip condition, **mechanical and measured**: `ls reviews/pass-*.md | wc -l` >= 4 at the end of
Epic 5 — the same signal `_audit_plan` check #5 already uses. Verified in both directions on a
scratch copy: exit 0 at 0/1/2/3 cycles, exit 1 at 4.

## What is DONE — Epics 0–5, 39 of 78 issues

The entire critical path for #113 and #174. This half is self-contained and independently
valuable: the engine exists, is gated, and is falsified.

| Epic | Issues | Delivered |
| :-- | --: | :-- |
| 0 — SPEC-first amendments | 13/13 | `REQ-DATA-018/019/024–028`, the `REQ-PORT-006` amendment, the SKILL.md template fixed and made **generated** from `_shared/plan_template.py` |
| 1 — minimal engine + schema | 4/4 | `document_types/<type>.toml`, `_shared/doc_lint.py`, known-bad fixtures, the four gate scripts recorded RED |
| 2 — carve-outs + #125 | 7/7 | vendored markers backfilled, four carve-outs declared, `update-status approved` fail-closed on a red `ready-check` |
| 3 — gate wiring | 5/5 | `doclint` rows in FAST+FULL, the #164 mis-mapping fixed, gate falsified by mutant, FULL tier green (39 commands) |
| 4 — full linter engine | 5/5 | severity tiers, status-aware promotion, path-keying, `PASS\|FAIL\|INCONCLUSIVE`, idempotency self-check |
| 5 — extractor + comparator | 5/5 | `plan_extract.py` (fails loudly), `pour_fidelity.py` (four populations), positive control in CI, `plan_issue` metadata + a halting close gate |

**Gates resolved:** `doclint row executes and fail-closes`, `carve-outs detectable`.

## What REMAINS — Epics 6–10, 39 issues

Instantiation over a finished engine, plus the corpus rewrite and the landing.

| Epic | Open | Scope |
| :-- | --: | :-- |
| 6 — instantiate the document types | 11 | one malformed fixture per type, then `findings/`, `reviews/pass-N`, `plan.md`, `references/*`, research `artifacts/`+`Summary.md`, per-skill `SPEC.md`, extract-only types, legacy `README.md`, deferrals |
| 7 — SPEC `Verification:` (#165) | 6 | classify all 226 clauses, fix the 4 false ones, restate 5 hardcoded counts, a runner, a grammar linter, record the 85% ungated bound |
| 8 — the normalizer | 11 | hash-neutral only, refusal predicate, derived protected set, `--idem-check`, orphan detector, log-region exclusion, aggregate diff, apply, rollback |
| 9 — bind remaining enforcement | 3 | `_audit_plan` linter findings, the always-on on-edit rule, three independent positive controls |
| 10 — reconcile and land | 7 | this issue, FULL validation, post-work fidelity number, upstream comments, tracker close, deploy |

**Gates still unresolved:** `normalizer aggregate diff` (human, blocks 8.8b), `Upstream write`
(human, blocks 10.4). Both are RED for the correct reason — the artefacts they gate do not
exist yet.

## Draft follow-on objective

> Instantiate the plan-047 document-conformance engine across the remaining yf artifact types,
> normalize the historical corpus hash-neutrally, bind the remaining enforcement points, and
> land the result: per-type schemas for the 8 remaining schema-bearing types, the `SPEC.md`
> `Verification:` runner and grammar linter (#165), the line-count-preserving normalizer with
> its orphan detector and rollback path, the `_audit_plan` and on-edit bindings, and upstream
> reconciliation.

Its first epic inherits two hard prerequisites already satisfied here: the engine is green on
the corpus (0 errors, 610 report-only) and the extractor's `unparsed[]` inventory (300
constructs across 33 plans) is the normalizer's actual worklist.

## Why splitting is the right call here, in one line

At 11 epics / 78 issues this is the largest plan to date (plan-045: 46), the remaining work is
**instantiation over a finished engine** rather than design, and the four review cycles the
trip condition counts are themselves evidence that the design half consumed the budget.

## Operator decision required

1. **Split** — land Epics 0–5 now, open a follow-on plan for 6–10 from the draft objective above.
2. **Continue** — carry on through Epic 10 in this plan and this session.
3. **Land and pause** — merge Epics 0–5, leave 6–10 open in this plan, resume later.

Issue 10.0 `depends-on: 5.5` and therefore **travels with the Epics-0–5 half** if the split fires.
