---
type: Reference
okf_spec: OKF-PLAN
id: comment-175-draft
disposition: tracker
target: https://github.com/dixson3/yoshiko-flow/issues/175
status: DRAFTED — NOT POSTED (operator gated)
---

# Draft comment for #175 — plan-047 coarse tracker

**plan-047 is COMPLETE for a REDUCED scope. This tracker should stay OPEN for the follow-on.**

## Delivered — Epics 0–5 plus Issue 10.0 (40 of 78 issues)

- **Epic 0** — `REQ-DATA-018/019/024–028` and a `REQ-PORT-006` amendment; the `yf-plan`
  `SKILL.md` plan.md template (measured the most-drifted artifact in the investigation) fixed
  and made **generated** from `_shared/plan_template.py` through `sync.py`'s marker fence, so it
  cannot drift from `seed_plan_md` again.
- **Epic 1** — `_shared/doc_lint.py`, the `document_types/<type>.toml` schema format, committed
  known-bad fixtures, and four gate scripts each recorded failing **RED for the reason they
  claim to measure**.
- **Epic 2** — vendored-content markers backfilled, four carve-out regions declared, and #125's
  enforcement hole closed.
- **Epic 3** — `doclint` wired into `CHANGE-VALIDATION.md` FAST and FULL, the #164 mis-mapping
  fixed, and the gate falsified by an injected mutant. FULL tier green: 39 commands, 0 failing.
- **Epic 4** — severity tiers, status-aware promotion, path-keying, a three-valued verdict with
  a binary exit contract, and an idempotency self-check.
- **Epic 5** — `plan_extract.py` (fails loudly; 300 unparsed constructs enumerated across 33
  plans) and `pour_fidelity.py` with its positive control running in CI.

## Descoped to a follow-on — Epics 6–10 (38 issues)

D-13's split gate tripped mechanically at 4 review cycles and the operator chose to split. All
38 remaining issues were closed with an explicit descope reason rather than left silently open.

**The follow-on must not copy them verbatim.** Epic 5 refuted a measurement they were planned
against: the **20 invented edges were a parser artifact** — 0 in any cleanly-parsed plan, with
all 127 in documents the grammar cannot read. The honest worklist is the extractor's 300
unparsed constructs, a number that did not exist when those epics were drafted.

## The finding worth carrying forward

Six controls in this execution were vacuous or misclassifying, and **every one was invisible to
inspection and visible only to execution**. The remediation is not more careful authoring — that
produced all six — but a precondition: **a control must mechanically demonstrate it can fail
before it is trusted to pass.**
