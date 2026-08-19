---
type: Finding
okf_spec: OKF-PLAN
id: exp-005-enforcement-wiring
---
# EXP-005 — Can per-type linters bind as real exit-code gates at intake, in CHANGE-VALIDATION, and always-on on-edit?

**Status:** complete · **Date:** 2026-08-18 · **Verdict:** all three binding points are
feasible; one of them does not currently exist in any form.

## Question

Operator decision D-3 binds linters at three points: fail-closed at INTAKE, a
`CHANGE-VALIDATION.md` recipe row, and an always-on on-edit trigger with **no opt-out**.
Determine for each: where it attaches, what it costs, and what it breaks.

## Headline — MEASURED, and it is not what the experiment was sent to find

**There is no code-level gate between a failing audit and `status: approved`.**

Driven against the real verbs in a scratch repo, on a plan whose `audit` had just returned
`status: fail` (4 findings) and whose `ready-check` had just returned exit **3**:

```
$ plan_manager.py update-status <dir> approved -m "deliberate bypass test"
{"status": "approved", "date": "2026-08-18", ...}
STATUS_EXIT=0
```

`update-status` is a **free-form writer**. Its own docstring says so (`plan_manager.py:1312`):
*"The writer is free-form — it accepts any status string and does not validate against an enum."*

> The only thing standing between a failing audit and `approved` is **the agent obeying
> SKILL.md prose**. There is no gate in code.

This is #149's M5 one level up from where it has been discussed: a gate whose enforcement is an
LLM reading a shell snippet has no exit code either. It also makes github issue **#125**
(status-enum hardening) considerably more load-bearing than its one-line filing suggests —
the missing enum guard and the missing readiness guard are the same hole.

## Correction to a claim carried into this plan from plan-046

The prior session's claim *"the audit blocks intake"* was falsified during plan-046 and
attributed to `_OKF_PORT050_REQS` (`plan_manager.py:3594`, applied at `:4036`). **That
attribution was wrong, though the falsification was right.**

`_OKF_PORT050_REQS` filters only the **OKF `check_conformance` error findings** (check #7)
down to four requirement ids. Every other check — context.md sections, motivation, upstream
refs, review counts, dual-write, epic-ref — appends findings unfiltered, and those *do* produce
`status: fail`. The allowlist was never the reason intake is unblocked. The reason is the
paragraph above: nothing consumes the verdict.

## Result

### (a) INTAKE binding

**Attachment point:** `_audit_plan(plan_dir)` — `plan_manager.py:3871`. Returns
`{status, findings[], report}`; `status == "fail"` iff any finding is `status="fail"`. A linter
finding appended to `findings` propagates automatically. `ready_check` (`:4700`) calls it at
`:4750` and exits **3**; the `audit` CLI (`:4184`) exits **1**; `audit-close` (`:4310`) wraps
the same engine and **exits 0 unconditionally** by design.

Call sites: `SKILL.md:492` (Phase 3 audit), `:515` (ready-check), `:553` (Phase 4.1 INTAKE
re-check), `:1308` (close-time advisory), `:1436` (`capture`).

**Positive control — the harness can observe a block:**

| Case | Result |
| :-- | :-- |
| Fresh `init`, ready-check | exit **3**, 2 reasons (blocked) |
| Made fully conformant, ready-check | `READY`, exit **0** (green) |

**The disjointness measurement.** Starting from the *green* plan, six document-linter-class
defects were injected: a table with **no delimiter row** and a 7-cell row under a 3-column
header; deletion of the entire `## Success Criteria` section; a duplicate `## Approach`
heading; an Obsidian `[[wiki-link]]`; a broken relative link; an h2→h4 heading skip.

```
audit          → status: pass   "All checks passed."
ready-check    → READY          exit 0
update-status  → approved       exit 0
```

The existing intake gate is **structurally blind** to every rule plan-047 proposes. The linter
is not redundant with the audit — it is **disjoint** from it.

Corroborating signal: `yf-markdown-lint` on the same file caught only 2 of the 6 (ML001
wiki-link, ML003 broken link) and **missed the malformed table entirely** — ML005/ML008 never
fired, because a table with no delimiter row is not recognized as a table at all.

**Blast radius on existing plans:**

| Measurement | Value |
| :-- | :-- |
| Plans at `**Status:** complete` | **46 / 46** |
| Plans the *existing* audit already fails | **10 / 46 (21.7%)** — 001, 005, 007, 020, 029, 030, 031, 033, 037, 041 |
| Plans a plausible type linter would flag | **33 / 46 plan.md (72%)**; 41/46 bundles |
| Automatic paths that re-audit a `complete` plan | **none** |

The 21.7% figure is independently corroborated by the `audit_close` docstring
(`plan_manager.py:4326`), derived separately: *"a fail-loud close-time audit would have blocked
22% of plans that legitimately completed."*

→ **A hard linter gate at INTAKE breaks zero existing plans.** The 72% is a hazard for binding
point (c) only.

### (b) CHANGE-VALIDATION row

Executed against the real engine in a scratch repo. A row plus `docs/plans/**` §3 globs
**selected and actually ran** (`commands[].id == "doclint-plan"`, non-empty `output_tail`), in
both FAST and FULL.

**Both decorative-row traps reproduced:**

| Trap | Reproduction |
| :-- | :-- |
| **#164 class** — zero commands reports green | `run --tier fast --changed some/unmatched.txt` → `{"status":"pass","commands":[]}`, exit **0** |
| **#149 class** — linter prints findings but exits 0 | engine reported `"status": "pass"` while the linter printed `errors=4`. Only `sys.exit(1 if errors else 0)` produced `"status":"fail"` + `first_failure` |

**Two live defects in this repo's manifest, measured:**
- `CHANGE-VALIDATION.md` §3 contains `| skills/*/SPEC.md | uv-herdr-launch |` — the #164
  mis-mapping is present.
- **`docs/plans/**` appears in NO §3 glob**, so every plan-bundle edit in this repo today
  produces the vacuous green above.

**Cost — MEASURED, and it is a non-constraint:**

| Scope | Files | Wall (warm) |
| :-- | --: | --: |
| `docs/plans` | 659 | 0.097 s |
| `docs/research` | 41 | 0.019 s |
| `skills/**` (incl. 52 spec files) | 154 | 0.034 s |
| **full corpus** | **854** | **0.135 s** in-process · **0.17–0.18 s** via `uv run` (3 runs) |

Cold first run 0.274 s. Three orders of magnitude below any `cargo test` row. **Drop all
incremental-scoping complexity from the design** — lint the whole corpus every time.

### (c) ALWAYS-ON on-edit — the risky decision

**False-fire surface, measured on real files:**

| Surface | Measurement |
| :-- | :-- |
| Non-bundle `plan.md` | **17** outside `docs/plans/` in this repo (`skills/yf-plan/scripts/fixtures/classify/*/plan.md`) → **62 errors** from a filename-keyed trigger |
| Vendored-verbatim `references/` | 193 files, 10 findings — including `plan-046/references/okf-spec-v0.1.md` and `-v0.2.md`, **verbatim external spec copies**. Fixing a finding there would corrupt the reference |
| Repo with no `docs/plans/` | Path-glob trigger inert; filename-keyed is not |

**The decisive measurement — "not finished" and "malformed" separate cleanly.** A freshly
`init`'d plan (status `scoping`):

```
files=4  findings=5  errors=0  warnings=5
  plan.md:28 W030 unfilled placeholder '_No investigations yet._'
  plan.md:31 W030 '_To be determined after scoping and investigation._'
  plan.md:34/42/45 W030 '_To be determined._'
```

**The seeded template is structurally perfect — `errors=0`.** Every defect in a legitimately
incomplete plan is a *completeness* defect, and all five are the template's own placeholder
strings. The deliberately-malformed plan produced the mirror image: structural `E010`/`E040`/
`E041` errors and **zero** placeholder warnings.

Corroborated by: `_audit_plan` already draws exactly this line for `context.md`/`motivation`
via `_CONTEXT_PLACEHOLDERS` marker matching, and the freshly-init'd plan failed *only* those
placeholder checks.

### Interaction with existing triggers

On an edit to `docs/plans/<id>/plan.md` **today**:

| Trigger | Fires? | Evidence |
| :-- | :-- | :-- |
| `yf-markdown-lint` | **yes** | `.markdown-lint-on-edit` marker present at repo root; fired ML001+ML003, exit 1 |
| `yf-drift-check` | **no** | `DRIFT-CHECK.md` §6 has no `docs/plans/**` glob |
| `yf-change-validation` | **vacuously green** | no `docs/plans/**` in §3 → `commands: []`, exit 0 |

No recursion is constructible: change-validation runs §1 subprocesses only, drift-check
dispatches a report-only sub-agent, markdown-lint is a leaf script. A fourth trigger is an
expected multi-fire on an orthogonal axis, exactly as `YOSHIKO_FLOW.md` already declares for the
change-validation ↔ drift-check pair.

**The new axis:** markdown-lint = *is it valid GFM*; drift-check = *do artifacts agree across
edges*; change-validation = *does the tree behave*; doc-lint = **does this document have the
shape its type declares**. Overlap with ML005/ML008 on tables is real but **incomplete in
markdown-lint's favour** — resolve by subtraction, and fix markdown-lint's missing-delimiter
blind spot rather than re-implementing tables in the type linter.

## Recommendations

**(a) INTAKE — wire it, but fix the enforcement hole first.**
1. Append linter findings inside `_audit_plan` (`:3871`) after check #9 via `_audit_finding`.
   `ready-check`'s exit-3 and `audit`'s exit-1 then work unchanged — **zero call-site edits** —
   and `audit-close` stays advisory by construction.
2. Map severity to the existing grandfather machinery: structural → `okf_missing_level` (hard
   `fail` on OKF-native, `warn` on legacy); completeness → `warn` always.
3. **Add a real code gate to `update-status`:** refuse `approved` unless `ready-check` is green,
   with an explicit `--force` writing the existing logged-deviation bullet (`SKILL.md:1535`
   already blesses `--force` as a logged stop-class deviation). **Without this, (a) is not
   fail-closed no matter what the linter returns.** Own bead; likely its own epic.

**(b) CHANGE-VALIDATION — one row, whole corpus, and prove it runs.** FAST and FULL identical
(0.18 s). §3 globs `docs/plans/**`, `docs/research/**`, `skills/*/SPEC.md`, `skills/*/spec/*.md`.
Two executable acceptance criteria:
- **Non-vacuity:** assert `len(commands) > 0` and non-empty `output_tail` — **never** on
  `status == "pass"`.
- **Exit-code fidelity:** seed a known-bad fixture, assert `returncode: 1` and
  `first_failure.id == "doclint"`.
- Fix the `skills/*/SPEC.md → uv-herdr-launch` mis-mapping (#164) in the same change; the
  doclint row is its natural replacement.

**(c) ALWAYS-ON — "no opt-out" holds, via four mechanisms; none alone suffices.**
1. **Key on PATH, never filename** — `docs/plans/**/*.md`, `Incubator/*/plans/**/*.md`,
   `docs/research/**/*.md`. Immunizes the 17 fixtures (62 errors avoided) and makes the trigger
   a silent no-op in a repo with no plans.
2. **Two severities, one of which is an error.** `E` structural, `W` completeness. Justified by
   the pristine-template measurement: a freshly-init'd plan is structurally valid **by
   construction**, so errors-only is never hostile to a plan being written.
3. **Status-aware promotion.** `scoping|investigating|drafting` → `W` informational;
   `review|ready-for-approval` → promote `W` to `E` (the threshold `ready-check` already
   enforces); `complete` → **report-only, never error** (the 72%).
4. **Exclude `references/**` from structural rules** — 10 findings there, two of them verbatim
   vendored spec copies that must not be edited.

**Verdict shape: `PASS | FAIL | INCONCLUSIVE`**, not `PASS | INCOMPLETE`. CHANGE-VALIDATION
consumes an exit code and already has this vocabulary, with `INCONCLUSIVE` meaning *a required
tool is absent* — which a doc linter genuinely hits. `_audit_plan` consumes
`status ∈ {pass, fail, warn}`; map `FAIL→fail`, `INCONCLUSIVE→warn` (the existing `epic-ref`
bd-unavailable precedent). `INCOMPLETE` is the **reviewer agent's** vocabulary
(`agents/reviewer.md:33`) because it is an LLM judgement fed back for iterative repair; a linter
is not that. Express "not finished yet" as **warning severity inside a PASS**, keeping the exit
contract binary at all three binding points and reserving exit 2 for "the linter could not run."

## Honest limits

- The linter used throughout is a ~110-line **prototype**, not the deliverable. Its 72%
  non-conformance figure depends on rules that plan-047 has not yet chosen; treat it as an
  order-of-magnitude signal, not a target.
- The 0.18 s cost is for a prototype doing frontmatter + section + table checks. A schema-driven
  linter over ~15 types will be slower — but it has three orders of magnitude of headroom.
- **Not measured:** whether `update-status --force` semantics as recommended would conflict with
  the existing stale-approval `--force` path, which uses the same flag name for a different
  purpose. Plan-047 must check this before implementing (a)(3).

## Reproduction

Scratch artifacts only (`scratchpad/exp005/`), not committed: `s1.sh`–`s8.sh`, `protolint.py`,
`protolint_gate.py`, and a scratch repo with its own `CHANGE-VALIDATION.md`. Worktree
`git status --porcelain` empty — nothing in the repo was modified.
