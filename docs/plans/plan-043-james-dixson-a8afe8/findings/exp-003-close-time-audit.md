---
type: Finding
okf_spec: OKF-PLAN
id: exp-003-close-time-audit
plan: plan-043-james-dixson-a8afe8
created: '2026-08-16'
---

# E3 — Close-time bundle audit: fail-loud or propose-only?

**Verdict: PROPOSE-ONLY**, with a **delta refinement** that is better than either raw option.

## The blocking rate disqualifies fail-loud

Re-audited all 43 bundles. **41 reached `complete`; 31 pass, 10 fail — 24.4%.** Applying the
checks *as they existed at each plan's close date* (historically faithful): **9 of 41 —
22.0%**.

**Roughly one completed plan in four or five would have been halted at land-the-plane.**
Three findings sharpen that beyond the raw rate:

- **plan-029's failure is a proven FALSE POSITIVE.** The matched text is `s:\` inside
  `…\ntags:\n- metric\ntimestamp:…` in a quoted, escaped-newline fixture body. The
  Windows-drive-letter regex `[A-Za-z]:\\` matched `s:` + `\` from `tags:\n`. There is no
  dangling reference. This is precisely the risk a close-time audit *newly* creates:
  `findings/` and `references/` are where execute-phase agents dump verbatim fixture and
  transcript content — exactly the content that trips content heuristics.
- **plan-030's failure is self-inflicted by the close step.** `log.md` first appears in the
  "mark complete" commit; once it exists, the legacy `**Phase log:**` fallback switches off,
  and the new `log.md` holds only `- complete: plan complete` — so the review count reads 0
  against 2 real `reviews/pass-*.md`. **A fail-loud audit placed after the close step's own
  writes would block on its own output.**
- **The recovery path is a different kind from §6.4's existing fail-louds.** Cascade-close and
  complete-gate failures are resolved by acting on **beads** — close the blocker, re-run. An
  audit failure is resolved only by **authoring or rewriting bundle prose**, which is
  `/yf-plan capture`'s job — and capture explicitly *"does not advance status"*. A fail-loud
  audit strands a plan whose engineering work is finished behind a documentation task.

## The gap is real, and it is NOT legacy debt

**9 of 10 failures are class A** — execution- or close-authored, structurally invisible to the
Phase-3 gate. Only plan-001 is pure class B (its failing check postdates it by 56 days).

| bundle | offending artifact first added | class |
| :-- | :-- | :-- |
| plan-005 | `#13` row added **79 s after approval** | A |
| plan-007 | `#16` row added after approval | A |
| plan-020 | phase-log line recording the audit's own result | A |
| plan-029 | `findings/**/sources.md` — **the close commit itself** | A |
| plan-030 | `log.md` — **written by the close step** | A (+B for OKF half) |
| plan-031 / 033 / 037 / 041 | `references/` + `findings/` artifacts, all post-approval | A |
| plan-001 | `context.md`, predates the check | B |

**#140's "9 of 40" is not mostly legacy debt** — the OKF-legacy downgrade already absorbs
that: 29 of 43 bundles are `okf_native=False` and emit only `warn` across the entire OKF
surface. The residue is almost entirely class A. That validates #140's core claim while
correcting its framing.

*(Also measured: the `PORTABILITY_ACTIVATION_DATE` grandfather clause is currently **inert** —
zero bundles are date-grandfathered, because the oldest plan's first scoping is exactly the
activation date and the comparison is strict. The OKF-legacy downgrade is what is actually
load-bearing.)*

## The audit is safe to run at close

- **Mutation: none.** Whole-corpus `shasum` before/after 43 runs (663 files) → the only diff
  was a *new* file written by a concurrent sibling agent. Zero existing files modified. Code
  corroborates: only `exists()`, `read_text()`, `glob`/`rglob`, `is_dir()`.
- **Idempotent:** two runs on plan-037 → byte-identical JSON.
- **No status-conditional logic.** `_audit_plan` never reads `status`. Auditing a `complete`
  plan behaves identically to auditing a `drafting` one.
- **Cost ≤ 0.2 s** for one bundle (0.18 s for the 103-file plan-029; 0.12 s typical),
  dominated by interpreter startup. **Cost is not the variable — verdict authority is.**

## Two ordering constraints, regardless of verdict authority

1. **The audit must run BEFORE the close step's own `log.md` / status writes.** plan-030 is
   the proof-of-mechanism. Also: `status` is a dual-write field, so an audit run *between* the
   frontmatter write and the `**Status:**` line write during `set complete` would report
   `dual-write:status` as a hard fail.
2. **Grandfathering is keyed on `log.md`'s `scoping:` entries.** Any close-time `log.md` write
   that drops them silently flips `grandfathered` `True → False`, promoting warns to fails on
   a plan that passed at Phase 3. Latent today (zero grandfathered bundles) but must not be
   introduced.

## Recommendation: propose-only, plus a delta

- Run `audit --json-output` at §6.4 unconditionally, **positioned before** the cascade/log/
  status writes.
- Report findings with a recommended `/yf-plan capture` follow-up. **Do not gate
  `set complete`.**
- **Do not reuse the `FAIL-LOUD:` banner treatment** — that vocabulary belongs to bead-state
  failures the operator can act on directly.

**The delta refinement (recommended).** Record the Phase-3 audit verdict in `log.md`, and at
close report only findings **new since approval** rather than the absolute set. Measured
outcome: **all 9 class-A cases are caught; plan-001's class-B case correctly stays silent.**
This surfaces exactly the regression #140 is about while keeping pre-existing legacy noise
quiet.

**If a fail-loud carve-out is wanted**, restrict it to the **non-heuristic, non-recursive**
checks — #4 (upstream reference bodies) and #5 (review-count equality). Both are relational
and deterministic, together account for 4 of the 10 failures, and have **zero observed false
positives**. Leave #6 (dangling-refs) and #7 (OKF floor) propose-only — those are the two that
fire on execute-authored fixture content, and the only observed false positive lives there.

## Sub-root visibility (recorded; #140's other half is out of scope)

The audit **does** descend: checks #6, #7, #7b are fully recursive (`rglob`), which is how all
four plan-037 findings under `references/user-scope/yf-herdr/` — two levels below the root —
were produced. Confirmed to four levels deep on plan-029.

What it does **not** see, confirmed by synthetic fixture:

1. **Nested `index.md` / `log.md` are silently exempted at any depth** — the reserved-file
   filter matches by *bare name*, not root position. A fixture's frontmatter-less
   `references/deep/index.md` and `log.md` produced **zero** findings. This is #140's
   nested-index half — **real, measured, and out of scope for plan-043.**
2. **Non-`.md` files** are excluded from the OKF floor, and from dangling-refs unless `.txt`
   or extensionless.
3. **Checks #1–#5 never descend** — no subdirectory is ever required to have an index, a log,
   or matching review counts.

`docs/research/` is **not in scope**: `audit` hard-requires `plan.md` and refuses without it.
