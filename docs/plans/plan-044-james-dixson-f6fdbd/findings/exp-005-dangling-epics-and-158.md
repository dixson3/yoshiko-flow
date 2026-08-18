---
type: Finding
okf_spec: OKF-PLAN
id: exp-005-dangling-epics-and-158
plan: plan-044-james-dixson-f6fdbd
created: '2026-08-17'
---

# exp-005 — Dangling `**Epic:**` refs (#143) and the #158 verdict

**Date:** 2026-08-17
**Method:** `bd show` over every distinct `**Epic:**` value in all 44 plan bundles; `.beads/issues.jsonl` `metadata.plan_dir` correlation; source read of `plan_manager.py` and `yf/src/cmd/self_cmd/sync.rs` at `0d900b1`.

## PART A — #143 is 14 dangling refs, not 5

```
DANGLING beads-skills-mol-{14o,2bi,3ee,5tv,806,bjf,g0b,glo,itd,mqa,nxk,r8z,s3x,yvv}   # 14
RESOLVES yf-mol-*                                                                     # 26
```

Affected: **plan-004 through plan-017**, contiguous. All 14 are OKF-legacy — `epic:` frontmatter
exists only from plan-030 onward, so all 14 are body-only `**Epic:**` on plan.md line 7.
Frontmatter/body agreement is a non-question *today* — but the repair **creates** the second
surface (see A4).

**Why #143 said five.** Its source (`plan-040/references/tracker-backfill-map.md`) was scoped to
plans with an identifiable upstream tracker. Five of the 14 (007, 009, 010, 012, 017) had
trackers; the other nine landed in its "No tracker found (17)" table — which lists their
`beads-skills-mol-*` epics right there. The title counted only the tracker-bearing subset.

### The defect is worse than filed: a silent false success, not `found: false`

#143 says `resume-scan` would report `found=false`. **It does not:**

```
$ plan_manager.py resume-scan docs/plans/plan-007-... --json
{ "epic_id": "beads-skills-mol-s3x", "epic_source": "plan_md", "found": true,
  "counts": {}, "total": 0, "stuck": [], "open_work_remaining": 0 }
```

`_resume_scan` (`:3025-3050`) resolves plan.md **first** and falls back to `metadata.plan_dir`
only when the field is *absent*. A dangling-but-**present** field therefore yields
`found: true` with zero descendants — **a resumed execute session reads "no open work" and skips
everything.** (Compare plan-018, good ref: `total: 26`.)

### A2 — all 14 recoverable, high confidence

The mapping channel is `metadata.plan_dir`, and it is exactly 1:1 — every plan_dir in
`.beads/issues.jsonl` has precisely one `issue_type: molecule` bead.

| Plan | Dangling | Proposed new id | Plan | Dangling | Proposed new id |
| :-- | :-- | :-- | :-- | :-- | :-- |
| plan-004 | `…-nxk` | `yf-5e06c253` | plan-011 | `…-r8z` | `yf-9e73640b` |
| plan-005 | `…-5tv` | `yf-4128b0a0` | plan-012 | `…-2bi` | `yf-e2e24239` |
| plan-006 | `…-g0b` | `yf-576712a7` | plan-013 | `…-glo` | `yf-909569c3` |
| plan-007 | `…-s3x` | `yf-9c09122b` | plan-014 | `…-mqa` | `yf-23173bc0` |
| plan-008 | `…-14o` | `yf-af5bbf86` | plan-015 | `…-itd` | `yf-bfdedcfa` |
| plan-009 | `…-bjf` | `yf-e3e04a51` | plan-016 | `…-3ee` | `yf-0d67a1e5` |
| plan-010 | `…-yvv` | `yf-036717e7` | plan-017 | `…-806` | `yf-34321543` |

**Unrecoverable: none.** Corroboration independent of plan_dir: every candidate is
`issue_type: molecule`, `title: "plan-execute"`, `status: closed`, `created_at` matching the
plan's scoping date, non-zero `dependent_count`, and a `close_reason` naming the plan by number
on the four spot-checked (e.g. plan-010's *"…Epic 7 hoisted to #28"* matches its plan.md).

**Why prior probes missed it:** they searched for **suffix preservation** (`yf-mol-nxk`) and a
`beads-skills` prefix census — both correctly returned zero, because the rename **regenerated ids
into an 8-hex form** (`yf-<8hex>`), not `yf-mol-<3>`. The plan_dir channel was never checked.

**The repair surface is two lines per plan**, not one: plan.md also carries
`- <date> intake: epic beads-skills-mol-<x> poured` in its phase log.

### A3 — validator placement

| Verb | Model |
| :-- | :-- |
| `audit` (`:3694` → `_audit_plan:3422`) | findings + `status ∈ {pass,fail}`, **exits 1** — a PLAN-phase gate. Entirely **offline**, no `bd` call. |
| `audit-close` (`:3824-3900`) | same `_audit_plan`, advisory, **always exit 0** (REQ-PLAN-075) |
| `resume-scan` (`:3105-3181`) | pure report, no severities, always exit 0 |

**Recommendation: add it to `_audit_plan` as check #9** — one implementation yields both the hard
approval gate (`audit`) and the advisory close report (`audit-close`), which is exactly the split
the codebase already designed. **Additionally** add an `epic_resolves: bool` to `resume-scan`'s
output, because that is where the defect actually bites and it is the only verb the execute path
consults.

**Design cost to flag:** `_audit_plan` is currently 100% filesystem-local; a `bd show` makes it
depend on a live DB and a subprocess. Mitigation exists in-tree (`_bd_list`/`_parse_bd_json`
`:2957-3004` return `[]` defensively). **Emit `warn`, not `fail`, when `bd` is unavailable** —
otherwise a portable plan bundle checked out on a beads-less machine hard-fails its own audit. A
real INCONCLUSIVE-vs-FAIL distinction.

**Grandfathering would NOT suppress these — use the right lever.** Two downgrades exist:
`missing_level` (warn iff first scoping < `PORTABILITY_ACTIVATION_DATE` = 2026-04-05 — all 14
scoped **June 2026** → `grandfathered: false`) and `okf_missing_level` (warn iff not OKF-native —
all 14 → **warn**). Measured on plan-007: `grandfathered: false, okf_native: false`. **Use
`missing_level`;** `okf_missing_level` would silently downgrade all 14 to `warn`.

### A4 — `record-epic` is the WRONG repair tool

`record-epic` (`:1312-1373`) delegates to the single dual-writer `_write_plan_fields`
(`:167-206`), which builds one in-memory model and lands **both** surfaces — there is no path
that writes one without the other, and audit check #8 (`:3619-3637`) enforces agreement as an
unconditional `fail`. Good invariant; wrong tool here. Running it on these 14 would:

1. **Create frontmatter** where none exists → flips OKF-legacy → `okf_native: true` →
   `okf_missing_level` flips `warn` → `fail`, converting ~9 existing warns per bundle into hard
   failures.
2. **Create `log.md`** (`okf.append_log`, `okf.py:396-416`). None of the 14 has one. Once it
   exists, `_plan_review_line_count` (`:3287-3306`) switches off the legacy in-plan.md phase-log
   fallback and counts `- review:` bullets in `log.md` → **0**, while `reviews/pass-*.md` still
   exists → **new hard fail**.
3. **Append a duplicate intake line** — its idempotency check matches on the *epic id*, so a new
   id appends a second `intake:` line beside the surviving old one.

**Recommended repair shape:** a purpose-built one-shot that rewrites the `**Epic:**` body line and
the phase-log `intake:` line in place, leaving OKF-legacy bundles legacy. (Alternative: use the
dual-writer *and* fully OKF-migrate all 14 — much larger.) Either way the sync invariant holds by
construction, because there is only one writer.

## PART B — #158 verdict: FULLY FIXED, safe to verify-and-close

- **`refresh_user_skills` and `present_user_surfaces` no longer exist** — repo-wide grep returns
  only doc comments explaining what replaced them (`sync.rs:56`, `:377`).
- **All 5 descriptors spanned:** `SYNC_PRESENCE` (`sync.rs:71-95`) has rows for claude-code,
  agents, codex, opencode, pi. A test pins full coverage against `DESCRIPTORS` itself
  (`sync.rs:362-372`); `harness_desc.rs:185` pins `DESCRIPTORS.len() == 5`.
- **`--surface` is not emitted on the vendor path** — `install_args_with` (`:156-175`) emits
  `--harness`. The CLI alias still exists as a user-facing deprecated flag that warns when a
  *human* passes it; that is the intended deprecation, not the defect.
- **Signal split is as described:** claude-code/agents use `YfSurface` (a yf-written dir);
  codex/opencode/pi use `ConfigHome`. `sync_harnesses` takes **no `PATH`** (REQ-YF-INSTALL-009).
- **Tests pin both hazards and the new reachability:** `sync.rs:362,380,404,442,469,489,499`
  plus e2e `install_sync_e2e.rs:519 codex_is_reachable_and_writes_its_own_rule_target`.

**No scope change to the plan.** Two footnotes, neither reopening the issue:

1. **Not executed** — the verdict rests on source reading plus the presence of pinning tests, not
   a green run. `cargo test -p yf sync` is the one command if a hard gate is wanted before closing.
2. **Cosmetic:** `install_args_are_explicit_per_harness` (`:499-509`) asserts `--harness` is
   present but never asserts `--surface` is absent. No code path could emit it — a robustness nit.
