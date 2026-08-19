---
type: Review
okf_spec: OKF-PLAN
id: pass-4
---
# Red-team pass 4 — plan-047-james-dixson-dec9ff

## Verdict: APPROVE

**Date:** 2026-08-19 · **Status:** all concerns resolved · **Brief:** verify pass-3's claimed
resolutions.

All three pass-3 blockers (H1, H2, H3) are **genuinely resolved, verified by execution**. Two
pass-3 mediums were **falsely marked resolved** (M1, M4 — the claimed replacement text was simply
absent from the file), and the H2 fix introduced one new medium. No high-severity concern remains,
so the rubric yields APPROVE with four mechanical edits to land before the pour.

## Resolution verification

**Genuinely resolved:** H1 (full re-parse: 11 epics, 77 issues, 0 duplicates, 0 dangling, 0 cycles,
0 backward-epic edges, **0 cut violations**, 0 uncovered issues, 0 phantom dischargers) · H2 (all
four `jq -e` expressions executed against good JSON, `{}`, `null`, missing keys, empty stdout and
non-JSON — **an empty script cannot satisfy any of the four gates**; `.commands | length > 0 and
(.[0].output_tail | length > 0)` confirmed valid jq) · H3 (`_TRACKER_ROW_RE` matches, returns
`175`; `stamp-tracker` skips for the *correct* reason; `gh issue view 175` → OPEN;
`references/upstream-175.md` satisfies the audit) · M2, M3, M5, M6, L1–L7.

**Falsely marked resolved:** M1 (`plan.md` said "six new ids" seven lines below "seven" — both
inside Issue 0.9), M4 (SC20 still said "10 Epic-6 issues"; Epic 6 has 11, dischargers list 9,
schema-bearing types are 8).

## Strengths

- **Whole-bundle stale-reference sweep is clean** — `plan.md`, `context.md`, `index.md`, `log.md`,
  `upstream-triage.md`, all 13 `references/*.md` and all 6 `findings/*.md`. Every hit legitimate.
  Pass-3's M3 gap closed corpus-wide, not just in `plan.md`.
- **43 of 44 criteria genuinely fail against the pre-work tree.** Executed: `assets/` and `scripts/`
  empty; `_shared/doc_lint.py` absent; no `sync.py` fence in `SKILL.md`; `REQ-DATA-018/019/024–028`
  **all free** (live set `001–007, 010–017, 020–023, 030, 031, 040–042`); `grep plan_issue skills/`
  → zero hits; FAST on `docs/plans/**` → `commands: []`; `CHANGE-VALIDATION.md:170` still maps
  `skills/*/SPEC.md → uv-herdr-launch`; `verify-reconcile` → 7 of 8 rows fail.
- **The #125 enforcement hole re-verified on a scratch copy**: `ready-check` → exit 3, then
  `update-status approved` → **exit 0** and wrote `status: approved`.
- **All 8 spot-checked `file:line` citations resolve**, including `plan_manager.py:1312` (docstring
  literally says "free-form"), `:1616` (F1 section-scoped as claimed), `:3871` (docstring does
  enumerate (1)–(8)), `:3701` (confirms the REQ-PORT-006 conflation premise), `coverage.rs:182`.
- Gate reachability sound; no `Condition` depends on evidence inside its own `Blocks` set; no
  frontloading miss.

## Concerns

| # | Severity | Concern | Resolution |
| :-- | :-- | :-- | :-- |
| P1 | med | **"six new ids" vs "seven"**, seven lines apart inside Issue 0.9. An executor obeying the second greps six of seven, leaving one unverified — inside the sweep installed to prevent the `REQ-DATA-020`–`023` collision. **Fourth consecutive cycle of a stale count surviving inside its own fix** | resolved — Issue 0.9 rewritten; the duplicate tail sentence left by the M6 split was the cause. Verified by grep: 0 occurrences of "six", 1 of "seven" |
| P2 | med | **SC20 still said "10 Epic-6 issues"** — wrong three ways again | resolved — "8 schema-bearing types (Issues 6.1–6.8)" |
| P3 | med | **"Each Epic-6 issue carries its own criterion" is false** — 6.1–6.8 are all discharged by SC20 alone. The fix (Issue 6.0's per-type fixtures) made SC20 non-vacuous, a real improvement, but the *claim* about it was over-stated the same way the original was | resolved — reworded to state SC20 is **per-type rather than aggregate**, discharged eight separate times against eight committed fixtures |
| P4 | med | **NEW, introduced by the H2 fix.** Every gate `Test:` runs `bash <script> \| jq -e '…'` with **no `pipefail`**, so the pipeline reports jq's status alone. Two consequences: the archived pre-work evidence describes a different command than the gate executes, and a script exiting non-zero while printing satisfying JSON resolves the gate **green** | resolved — `set -o pipefail` added to all four Tests; Issue 1.4(4) re-scoped to record the **gate `Test:` string's** pre-work run, not the bare script's |
| P5 | low | `plan.md:26` cited `SKILL.md:395-412` while D-7/Issue 0.1 cite `365-420` for the same artifact; the fenced block is 365–421 | resolved |
| P6 | low | `references/comment-113.md` — `ML004` broken same-file anchor | resolved — absolute URL |
| P7 | low | Gate `Test:` paths are repo-root-relative while the coordinator may run in the worktree address space | accepted — the bundle is committed before the pour, so this resolves; noted rather than left implicit |

## Missing

**Pass-3's Missing #2 — the recurring root cause — is now addressed.** Three cycles produced a gate
failing for a reason unrelated to what it measures (`KeyError` → `exit 127` → stub exits 0), and
piping through `jq -e` made the signal *worse* by erasing the script's own exit code. Issue 1.4 now
carries an explicit discipline: **0 = capability present · 1 = capability absent · 2 = the harness
could not run**, under `set -o pipefail`, mapping onto the `INCONCLUSIVE` vocabulary Issue 4.4
already defines. **A gate is only allowed to be red for reason 1.**

No unmet precondition found anywhere: every artifact, tool and capability an issue's text assumes
is produced by a declared predecessor or established by a gate.

## Gate Assessment

All four gates **BROKEN today** (scripts absent → `bash` exits 127, empty stdout → `jq -e` exits 4),
**correctly placed**, and **stub-resistant by construction** — verified by executing each expression
against six input shapes. `Blocks:` sets reference only existing issues. No cycles, no frontloading
miss.

## Upstream Assessment

5 `partial` (#113, #174, #149, #135, #62), 2 `include` (#165, #125), 4 `exclude`, 1 `tracker`
(#175). `verify-reconcile` executed: 7 of 8 rows correctly fail pre-work; #175 returns
`inconclusive` (trackers carry no end-state contract), so pass-1's warning that SC38 stays green
with a broken tracker holds structurally — but with #175 real and `_TRACKER_ROW_RE`-matching, that
failure mode can no longer occur silently. `upstream-triage.md` omits a #175 section, matching
plan-046's precedent (#167 is likewise absent); not a defect.

## Operator note — the split still fires, and that is by design

D-13's trip condition is `ls reviews/pass-*.md | wc -l >= 4`, evaluated **at the end of Epic 5 by
Issue 10.0**, which exits non-zero and halts. Writing this pass makes that count 4. **APPROVE does
not mean "proceeds whole"** — it means the plan proceeds under its own mechanical split gate, which
will trip at the end of Epic 5 and render the split proposal. That is what D-13 was designed to do,
and it is a better outcome than a fifth review cycle.

**Had this pass returned REVISE:** the concerns are **concentrated in Epics 0–5** (P1 → Issue 0.9 in
Epic 0; P4 → Issue 1.4 in Epic 1; only P2/P3's wording touches Epic 6). A split at Epic 5 would
**not** have helped — it would have carried three of the four mediums into the first half and
orphaned the fourth. Epics 0–5 alone would be APPROVE-able standalone on the same grounds, but
splitting buys nothing here.
