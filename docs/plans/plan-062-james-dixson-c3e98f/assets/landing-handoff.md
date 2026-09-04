---
type: Record
okf_spec: OKF-PLAN
title: 'plan-062 landing handoff — the route, the pre-landing decisions, and the halt-recovery contract'
plan: plan-062-james-dixson-c3e98f
discharges: 5.5
description: 'Issue 5.5 handoff artifact. The Phase-6 landing route for plan-062 and its halt-recovery contract, produced by the executing session for the OPERATOR to perform. Records the two decisions that must be taken before landing (the #326 frontmatter strip and the ESC-003 scope question), the exact apply command, and what to do at each halt — which now genuinely resumes, because Epic 1 landed before the seam.'
---
# plan-062 landing handoff

> **The executing session did NOT run `land --apply`, and must not.** `SKILL.md` §6.0 is
> explicit: print the command and stop. It names `dixson3/yoshiko-flow#293` — an executing agent
> closing a consent gate by asserting its own authorization. This file is the artifact; the
> **operator** performs the landing.
>
> Note the self-reference: the `--apply` path this document hands over is the one plan-062 just
> wired. Before this plan, running it did nothing at all.

## 1. Pre-landing decisions — take these BEFORE `--apply`

### 1.1 The `#326` frontmatter strip (ESC-002) — **ordering is load-bearing**

The three files at `assets/upstream-drafts/{327,266,304}.md` are posted **verbatim** by L7.
Because `#326` is unfixed, whatever is in the file is what appears in the public comment.

The operator's decision (matching plan-061) is: **strip the YAML frontmatter from those three
files as the LAST action before landing, and do not re-add it.**

| When | State | Why |
| :-- | :-- | :-- |
| During Phase 5 | frontmatter **present** | every step that reads the bundle sees a conformant tree |
| Immediately pre-land | frontmatter **stripped** | the posted comments are clean |
| After the strip | bundle carries a `REQ-OKF-003` finding on those three files | **expected, and not a blocker** |

`audit-close` is **advisory** and exits 0 unconditionally, so the finding does not gate
completion. **Do not re-add the frontmatter to make the finding go away** — that would silently
reverse this decision in order to satisfy a check.

The reason the strip must be *last* rather than *first*: **L7's read-back compares the FILE
against the POSTED comment**, so the two must match. Stripping the files keeps them matching
while making the comments clean.

The proper fix is `#326`, now labelled `deferred`, whose complete verified design is in
`findings/exp-003` and whose reserved id is `REQ-LAND-027`.

### 1.2 The ESC-003 test fix is scope beyond this plan

`skills/yf-plan/scripts/test_config_tiers.py` carries a one-line isolation fix that plan-062 did
not set out to make. It is included because the FULL tier was red without it and the defect is
real — the assertion resolved against the wrong filesystem. **If you would rather it landed
separately, drop that hunk and re-run the FULL tier**, which will go red again for that reason
alone.

## 2. The route

Phase 6 is one operation with **one informed-consent grant** (`REQ-PLAN-083`). Do not walk L1–L19
by hand — that is what plan-061 had to do, and closing that necessity is why this plan exists.

```bash
# 1. Compute the manifest. A pure read; mutates nothing (REQ-LAND-026).
uv run skills/yf-plan/scripts/plan_manager.py land --dry-run \
  docs/plans/plan-062-james-dixson-c3e98f --json

# 2. Dispatch the `lander` sub-agent over that manifest. It returns a DECISION DOCUMENT,
#    never a command. Write the decision OUTSIDE the repository tree — a decision file
#    inside the tree halts the landing at L16, past the irreversible boundary (now filed
#    as #333).
uv run skills/yf-plan/scripts/plan_manager.py land --validate-decision \
  "$TMPDIR/plan-062-decision.json" docs/plans/plan-062-james-dixson-c3e98f

# 3. THE STRIP (§1.1) — last action before the apply.

# 4. Land. Run this yourself, in your own shell.
\
  uv run skills/yf-plan/scripts/plan_manager.py land --apply \
    "$TMPDIR/plan-062-decision.json" docs/plans/plan-062-james-dixson-c3e98f
```

`land --dry-run` currently reports **`verdict: pass`, `halts: []`**.

## 3. The halt-recovery contract

**This is the part that is new.** Before plan-062, a resume after a halt re-executed **all
fifteen steps from L0** — including `l6_push_one` and `l7_reconcile_writes`, so it re-pushed and
re-posted every reconcile comment. `_land_execute` built its `done` set from journal *phases*,
named it as though it held executor *step keys*, and never read it.

So the contract is now REAL rather than aspirational:

> **On a halt: read the journal phase, fix the cause, and re-invoke the same
> `land --apply` command.** It genuinely resumes.

- Completed steps are **skipped and surfaced** with an explicit `resumed` marker in `results` —
  never a silent absence.
- The three unjournaled steps (`l3_validate_merged`, `l8_close_chain_head`, `l12_close_cascade`)
  resolve **forward**, so a halt at `l3` **re-runs validation** rather than skipping it.
- `l0_lock_acquire` **always re-executes**. The lock is released at L4, so a uniform skip would
  run unlocked and then unlink a lock it never acquired. Known asymmetry: resuming from L5 onward
  ends holding a lock nothing released, which self-heals via same-host dead-PID reclaim.

Per-state recovery is in `spec/landing.md` and plan-060's landing runbook. The four conflict
states each carry their own recovery — they are **not** uniform.

**Reading the verdict.** It is three-valued. `inconclusive` is **never** coerced: a landing can
reach `L_DONE` carrying a non-halting `inconclusive` from L8 or L12, and that reports
`inconclusive` (exit 2), not `pass`. Exit 3 is the tty refusal — a gate signal, not a verdict.

## 4. What lands

- `skills/yf-plan/scripts/plan_manager.py` — the seam, the three-valued verdict,
  `_land_resume_done()`, `LAND_RESUME_NEVER_SKIP`.
- `skills/yf-plan/scripts/test_land_apply.py` — 8 new tests (51 total).
- `skills/yf-plan/spec/landing.md` — `REQ-LAND-028`/`029`, `027` reserved, `011` retargeted.
- `SPEC.md` — the plan-062 amendment-log entry.
- `CHANGE-VALIDATION.md` — `gate-plan062-amendment` in both tiers, three Trigger Scope rows.
- `skills/yf-plan/scripts/test_config_tiers.py` — the ESC-003 fix (see §1.2).
- The plan bundle.

## 5. After the landing

`AGENTS.md` requires the redeploy to run from **local `main`, clean, in sync with `origin`** —
never from this execute branch. L19 handles it, but the precondition is the operator's to
confirm.

The five issues filed by Issue 5.1 (`#331`, `#332`, `#333`, `#334`, and the `#326` re-label) are
**already public**. They describe defects this plan deliberately did not fix, so they remain open
after the landing by design.
