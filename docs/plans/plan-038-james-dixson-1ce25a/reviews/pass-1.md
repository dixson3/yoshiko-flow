---
type: Review
okf_spec: OKF-PLAN
---
## Plan Red-Team: plan-038-james-dixson-1ce25a

## Verdict: REVISE

### Strengths

- **The prescriptive/descriptive split is the right central insight**, and it is carried
  consistently: it appears in the finding, the Approach, the risk table, and — crucially — in
  Issue 4.1's instruction that the check must be section-scoped. A plan that identified the
  distinction but then specified a global grep would have shipped the bug it diagnosed.
- **The scope correction is recorded rather than quietly applied.** The finding states plainly
  that an earlier reading claimed the executor was missing and that this was wrong. That keeps a
  future reader from re-deriving the larger scope.
- **The #117 limitation is stated where it will actually be read** — in the disposition table, in
  the SPEC requirement (1.2), and in the operator-facing prose (3.3) — not buried in a finding.
  Disposition is correctly `partial` with #117 left open.
- **Issue 3.5 is well-judged.** It files the follow-up that would genuinely close the gap and
  explicitly does not implement it, keeping the coupling decision intact.
- **The enforcement-boundary section is honest.** Stating that nothing can stop an operator typing
  the command directly is the kind of claim-limiting that makes the rest of the plan credible.

### Concerns

- **The plan never verifies its own central premise** — severity: **high**
  Everything rests on "there is no in-skill wrapper for the push step." That was established by
  reading the verb list and §3. But `hoist --issues <csv>` already ensures an upstream issue per
  bead under `granularity: granular`, dry-runs first, and pushes scoped — which is *very close* to
  what `push` is specified to do. If `hoist` (or `hoist` with a flag) already covers the plain-push
  case, then #106's fix is a **prose change plus possibly a flag**, not a new verb, and Epic 2
  shrinks by more than half.
  Recommendation: add an issue at the head of Epic 2 that diffs the specified `push` behavior
  against existing `hoist`/`land`, and states explicitly why a new verb is needed rather than a
  parameter on an existing one. If the answer is "hoist also closes the bead locally and push must
  not," that is a one-line justification worth writing down — and if it is *not* the answer, the
  epic should collapse.

- **"Six prescriptive sites" is a count from one grep, treated as exhaustive** — severity:
  **medium**
  The classification came from `grep -n 'bd github\|bd gitlab\|bd jira\|bd <backend>'`. That
  pattern misses a prescriptive instruction phrased without the literal backend token — e.g. the
  §3 parenthetical "(For a whole subtree: `bd github sync --push-only --parent <id>`)" is caught,
  but a line saying "run the scoped sync form" would not be. Success Criterion 2 asserts "all six"
  and "all fourteen" as if the partition is complete and verified.
  Recommendation: have Issue 2.3 re-derive the site list from the *sections* (read §3, §4, §6, and
  the backend table end to end) rather than trusting the grep, and soften the criterion to the
  sections rather than a fixed count.

- **Issue 4.1's check is specified by what it must not do, not by what it does** — severity:
  **medium**
  "Section-scoped, not a global grep" rules out the wrong implementation but does not say how
  sections are delimited. `SKILL.md` has no machine-readable section markers; an executor could
  reasonably implement this as a line-range check, which silently rots the moment the file is
  edited — and this plan edits it heavily.
  Recommendation: specify the mechanism. A workable option: check only fenced ```bash blocks
  within the operator-facing procedure, since every prescriptive site is inside one and every
  descriptive mention is prose or a blockquote. State whatever is chosen in the SPEC guardrail
  (1.3) so the check has a declared contract.

- **No issue updates #117, though Success Criterion 5 requires it** — severity: **medium**
  The criterion says #117 stays open "updated with the coarse-tracker gap." Issue 3.5 files a
  *new* `yf-plan` issue; nothing owns commenting on #117 itself. This is the identical gap
  plan-037's review caught for #110, which suggests the `partial` disposition reliably produces an
  unowned update step.
  Recommendation: give Issue 3.5 (or a new 3.6) explicit ownership of the #117 update with the
  in/out split, and note the recurrence — if `partial` keeps producing this, the reconciler or the
  plan template should require an owning issue.

- **Epic 3 has no gate, but writes the operator-facing claim that most invites misreading** —
  severity: **low**
  Issue 3.3 documents `closable` including its limitation. If that sentence is dropped or softened
  during execution, a clean `closable` run reads as "nothing needs closing" — which is false for
  every hand-filed tracker. Nothing checks that the caveat survives.
  Recommendation: make it a success-criterion-level check, or have Issue 3.4's tests assert the
  limitation string is present in SKILL.md. Cheap insurance on the plan's most misreadable output.

- **`--dry-run|--apply` duplicates a flag pair the existing verbs express differently** —
  severity: **low**
  `cmd_hoist` uses `apply: bool` where absent means dry-run; there is no `--dry-run` flag. Issue
  1.1 specifies `[--dry-run|--apply]`, introducing a second idiom in the same script.
  Recommendation: match the existing `--apply`-only convention unless there is a reason to differ,
  and if there is, state it in the SPEC.

### Missing

- A justification for `push` as a **new verb** rather than an extension of `hoist` (the high
  concern above). This is the plan's load-bearing unexamined assumption.
- An owner for the #117 update.
- A concrete mechanism for the 4.1 check.

### Gate Assessment

Three gates: Start, one capability gate, Reconcile. The count is right — no proliferation.

The capability gate ("`push` verb exists before the prose points at it") is well-conceived: it
guards a real ordering hazard and its `Test:` is genuinely runnable
(`upstream.py push --help >/dev/null 2>&1`). It is also the *inverse* of the bug being fixed —
documentation referencing a non-existent verb — which is a thoughtful touch.

One gap: it blocks 2.3 and 2.4 but **not** 2.5, which also depends on `push` existing (it adds
inline warning output to the verb). 2.5's `depends-on: 2.2` covers the ordering, so this is not a
correctness bug, but the gate's `Blocks:` list is inconsistent with its own rationale.

Epic 3 and Epic 4 have no capability gates, which is appropriate — 4.3 is a validation step, not a
gate needing operator authority.

### Upstream Assessment

Five issues; dispositions sound.

`#106 include` is the core. `#105 include` as a rider is legitimate — it is a genuine residual of
already-shipped work, it lands in the same file, and the plan explains *why* the new verb is the
right place for it (the routed path is where an agent will actually look).

`#117 partial` is correctly typed and, unlike plan-037's first attempt at #110, the in/out split
is specific from the start. The unowned-update gap is a process defect, not a disposition error.

`#102` and `#60` excluded with reasons; `#60` in particular is a good exclusion call — same skill,
genuinely different axis, no shared code path.

### Operator Resolutions

| # | Concern | Severity | Status | Resolution |
|:--|:--|:--|:--|:--|
| 1 | Premise unverified: does `hoist` already cover plain push? | high | resolved | **Measured rather than argued** (`findings/exp-03`). `plan_hoist` is three stages — dry-run push, real push, **`bd close` per bead**. The third stage is the difference: `hoist` removes the bead locally; a plain push must not. Premise holds; `push` is stages 1–2. Measuring it also uncovered **#129**, a silent data-integrity defect, now folded in as Epic 2 ahead of all routing work. |
| 2 | "Six sites" from one grep, treated as exhaustive | medium | resolved | Issue 3.3 re-derives the site list by reading the Push step and Backend generalization **end to end** rather than trusting the grep. Success Criterion 3 restated against the sections, not a fixed count. |
| 3 | Issue 4.1 check specified negatively, no mechanism | medium | resolved | Issue 1.4 now defines the boundary mechanically in the SPEC — **fenced ```bash blocks inside the Push step and Backend generalization sections** are procedure; prose, tables, and blockquotes are explanation. Issue 5.1 implements against that declared contract. |
| 4 | No issue owns the #117 update | medium | resolved | Issue 4.5 explicitly owns commenting on #117 with the in/out split and leaving it open, *and* filing the `yf-plan` epic-stamping follow-up. Noted as a recurrence of the same gap plan-037's review found for #110. |
| 5 | Nothing guards the `closable` limitation caveat surviving | low | resolved | Issue 4.4 asserts the caveat string is present in SKILL.md, so softening or dropping it fails a test. |
| 6 | `--dry-run\|--apply` diverges from existing `--apply` idiom | low | resolved | Issue 1.2 now specifies `--apply`-only, matching `cmd_hoist` (absent `--apply` *is* the dry run). No second idiom introduced. |

**All 6 concerns resolved**, and the high one materially changed the plan: it grew from four epics
to five, with #129 sequenced ahead of the routing work. Per REQ-PLAN-030 a REVISE requires a fresh
red-team cycle before `ready-for-approval`; see `pass-2.md`.
