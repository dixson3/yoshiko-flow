---
type: Review
okf_spec: OKF-PLAN
plan: plan-046-james-dixson-aabefa
pass: 2
verdict: REVISE
created: '2026-08-18'
status: resolved
---

# Red-Team Pass 2 — plan-046-james-dixson-aabefa

## Verdict: REVISE

5 high, 8 medium, 6 low. Of pass 1's five HIGH rows marked `resolved`: **H3 fully resolved; H5 substantively resolved with a drafting residue; H1 and H4 partial; H2 NOT resolved.**

## Strengths

- **H3 is fully and correctly resolved.** 4.3a is explicitly ungated with the reason stated, 4.3b carries the gate, `Blocks: Issue 4.3b` points at the mutating step. The cycle is gone.
- **The D-12 correction is substantively right, independently re-verified** — the frozenset at `:3525`, the filter at `:3967`, the "deliberately excluded" comment at `:3522-3524`, and `_shared/okf.py:804` emitting under REQ-OKF-001.
- **The exp-003 correction block is model conduct** — quotes the wrong sentence verbatim, states *how* it happened, scopes what survives. Recording rather than editing away is right.
- **M6/M7 cleanly resolved**, underlying numbers re-verified (50 bundles, 19 root indexes, 5 `okf.py` copies, `REQ-OKF-034` referenced once and never defined, `emit_conformant_copy` zero callers).
- **M8's fallback is specific about what degrades**, not just "don't block".

## Concerns

### HIGH

**H2-R — The rewritten engine gate is STILL vacuous, and unrunnable as written. Measured both ways.** `plan.md:233`.
*(a)* `${CV_SKILL_DIR}` is defined nowhere — one occurrence in the repo, `plan.md:233` itself:
```
$ uv run "${CV_SKILL_DIR}/scripts/change_validation.py" run --tier fast --changed skills/yf-okf/scripts/okf.py --json
error: Failed to spawn: `/scripts/change_validation.py`
```
*(b)* With the path corrected it **exits 0 today**, before Epic 1:
```
{"tier":"fast","status":"pass","commands":[],"first_failure":null}   EXIT=0
```
`coordinator.md:182` resolves a gate on **exit 0**. The "pass iff `commands` is non-empty and contains `uv-okf`" clause is prose in the `Test:` field; nothing parses it. `test_class: probe` means §5.2b runs it **unattended** at execute start and resolves it. The vacuity just moved from the command to the predicate.

**H1-R — A stale version of the retracted claim survives in four places, one of them the executable instruction.** `findings/exp-003:212` (*"`audit` blocks everything"*, two lines below its own retraction), `exp-003:253`, `exp-004:78`, and — critically — **`plan.md:178`, Issue 3.6**, which restates the retracted causal mechanism as its rationale. Worse, *"explicitly outside `_OKF_PORT050_REQS`"* is not an action: the set is a literal frozenset, so a new REQ is outside it **by construction**. An executor will look for something to exclude and find nothing.

**H4-R — The `n/a` requirement the pass-1 table says is "specified in Issue 3.3" is not in Issue 3.3, or anywhere in Epic 3.** `grep -n "n/a" plan.md` → three hits: D-11, Issue 4.4, SC6. Issue 3.3 specifies only `missing`/`ghost`/`empty-dir` and `exit 0/1`. Issue 3.1 does not mention it either. SC6 and 4.4 assert a behavior no issue builds and no requirement specifies — and implementing it in 3.3 without a 3.1 requirement is a fixed-authority CONFLICT. **Third instance of the over-stated-resolutions defect.**

**H-NEW-1 — Issue 3.2's premise is measurably false, and the falsification is a live backfill hazard.** `plan.md:167` says *"all 23 current indexes happen to be roots."* Measured: **four of the 23 are nested**, all under `plan-029/findings/okf-migration-samples/*/after/`, and `incubator-bundle/after/index.md` opens with `okf_version: '0.1'` — a non-root index carrying exactly the frontmatter v0.2 §8 forbids, **in the tree right now**. Consequences: (i) 3.2's justification is *stronger* than stated but its premise reproduces the read-not-measured pattern; (ii) **Issues 4.1 and 4.3a say "corpus-wide" without defining the corpus** — a `docs/**/index.md` glob would regenerate plan-029's frozen migration fixtures, destroying the recorded evidence of a completed plan.

**H-NEW-2 — #92's first carve-out is filed by nobody, and a count coincidence hides it.** Three sites name the carve-outs as projection delivery mode / gate for yf-research+yf-incubator / round-trip. Issue 5.5 files the gate, round-trip, and the **D-9 deferral** — **projection delivery mode is absent.** Because pass 1 added a third item, the count reads "three" and matches while the contents do not. Compounded: Issue 5.2 deletes `emit_conformant_copy` citing *"reviving it is what the #92 carve-out issue (5.5) tracks"* — 5.5 tracks no such thing. And SC9 still says *"two carve-out issues"*.

### MEDIUM

**M-NEW-1 — R2's mitigation is assigned to no issue, and Issue 1.3 names no ids.** R2 claims *"Epic 1 wires `uv-_shared` to all four copies' globs"*; no issue does. Measured: `uv-_shared` fires on **none** of the four vendored copies. R2's *"currently two of them match nothing"* conflates "matches no glob" (2) with "does not fire `uv-_shared`" (4). Since SC1 and the gate require only `uv-okf`, Epic 1 can close green with R2 unmitigated. *(Glob resolution confirmed to be a union, not first-match — so adding rows is additive and safe.)*

**M-NEW-2 — Issue 3.8 does not test what D-12 claims; it tests D-10.** The filter is `if cf.level != "error" or cf.req not in _OKF_PORT050_REQS`. Issue 3.6 lands the finding at **warning**, so 3.8's synthetic finding is discarded by the **first** clause and never reaches the allowlist test. Falsifiable — against the wrong hypothesis.

**M-NEW-3 — Issue 3.8 is a graph leaf; the measurement gates nothing.** Nothing depends on 3.8, so Epic 4 can complete whether or not it ran, and a 3.8 that *falsified* D-12 would arrive after the backfill it should have re-scoped. *(The rest of the graph was traced: all `depends-on` resolve, acyclic, nothing orphaned by the 4.3 split or 3.8 insertion.)*

**M-NEW-4 — Issue 4.2 fixes one producer; three of the 19 indexes come from another.** The template being fixed is `_INDEX_MEMBERS` at `plan_manager.py:622-631` — **yf-plan only**. `docs/research/002/003/004` are produced by `index_manager.py`/`okf.add_index_entry`, and exp-003 measured *their* missing entries (`plan.yaml`, `sources.json` — 3 of the 15). Epic 4 would hand-fix those three and leave the producer that re-breaks them — the same backfill-without-generation ordering the plan's spine forbids.

**M-NEW-5 — Two undecided either/ors survive, and one is self-contradictory.** 4.2(c)'s *"or have `scaffold` create them"* would generate empty `diagrams/`/`assets/` in every bundle, which (i) collides with Issue 3.3's own `empty-dir` finding and (ii) **git does not track empty directories**, so they vanish on clone and the ghost returns. 3.3's *"exempt declared-optional entries"* branch requires the **baseline** engine to know a yf-plan-specific optionality list (`RETROSPECTIVE_FILE` lives in `plan_manager.py:635`) — a layering inversion the plan's own baseline/extensions discipline forbids.

**M-NEW-6 — Epic 3's REQ ids are unallocated.** Issue 2.2 allocates ids for *"this epic"* (Epic 2); 3.1 says *"against the ids allocated in 2.2"*; 3.6 needs *"a new REQ"* named nowhere. Under fixed-authority SPEC-first this is a CONFLICT-and-halt — which is exactly why Issue 1.1 exists.

**M-NEW-7 — The Backfill Review gate's `cwd` does not match where its evidence lives.** Gate is `cwd: repo-root`; 4.3a produces the diff *"in the execution worktree"*. And 4.3b says *"apply and commit"* without saying where — 4.3a already wrote the files, so R3's `git checkout` revert only makes sense under one reading.

**M-NEW-8 — Issue 4.5 points at the in/out list rather than carrying it.** The pass-1 H5 row promised it *in* 4.5. *(The in/out content itself was checked and IS consistent across `plan.md:69` and `upstream-triage.md:28`.)*

### LOW

**L1** — Risks run R1…R5, **R9**, R6, R7, R8. R9 inserted mid-table.
**L2** — Issue 3.2 names `write_index`, which does not exist. The functions at the cited lines are `scaffold_bundle` (`:293`/`:320`), `_read_index` (`:340`/`:344`), `render_index` (`:347`/`:356`). Line numbers right, function name wrong.
**L3** — D-6's *"on a tree where `sync.py --check` exits 1"* reads as the live tree. Measured live: **EXIT=0**, all five byte-identical. exp-001 is honest (it means its scratch tree); D-6's compression drops that.
**L4** — `log.md` had no entry for the pass-1 resolution cycle.
**L5** — `1.2 depends-on 1.1` is spurious serialization.
**L6** — Issue 1.1 edits a **fixed-authority** SPEC on *"almost certainly a typo"*. By this plan's own standard, hedged language should not ground an authority edit.

## Missing

- No issue makes the engine gate's exit code carry its predicate; SC1 has the same shape.
- No definition of "corpus-wide", and no exclusion for the four plan-029 fixture indexes.
- No `n/a` state in Issue 3.1 or 3.3, though SC6 and 4.4 assert it.
- No issue files the #92 projection carve-out.
- No treatment of the yf-research index producer.
- No REQ-id allocation for Epic 3.
- No positive control in Issue 3.8 — a green result is indistinguishable from a broken harness.

## Gate Assessment

| Gate | Reachable? | Pass-2 status |
| :-- | :-- | :-- |
| Start Gate | yes | unchanged |
| Engine gate green | Reachable, **STILL VACUOUS and unrunnable**. Measured: EXIT=2 as written; EXIT=0 with the path fixed and `commands: []`. `probe` class means §5.2b auto-resolves it before Epic 1. | **H2 NOT resolved** |
| Backfill review | **yes — cycle broken.** | **H3 resolved.** Residual: `cwd` mismatch (M-NEW-7) |
| Reconcile Gate | yes | unchanged |

## Upstream Assessment

| Issue | Assessed |
| :-- | :-- |
| #141 | **Sound**, unchanged. |
| #140 | **Disposition now honest.** IN/OUT verified consistent across `plan.md:69` and `upstream-triage.md:28`. Residual: M-NEW-8. |
| #92 | **Now the weakest row, and it regressed** — see H-NEW-2. |
| #118 | **Sound.** The `SKILL.md:245 → :262` fix is now present. |

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H2-R gate still vacuous + unrunnable | high | **Upheld — I re-ran both myself.** As-written: `error: Failed to spawn: /scripts/change_validation.py`. Path-corrected: `commands: []`, EXIT=0. Test replaced with a repo-relative path piped through a `python3 -c` predicate that **exits non-zero unless `uv-okf` is in `commands`**. Issue 1.4 now additionally requires running the gate command **today** and confirming it exits **non-zero** — the same standard 1.4 already applied to the manifest. SC1 reworded to the exit code, not prose. | `main-session` | resolved |
| H1-R stale claim in 4 places | high | **Upheld.** Issue 3.6 rewritten to drop the false rationale and state the real one. Correction notes appended to `exp-003:212` and `:253`; `exp-004:78` caveated with the four-req scope. | `main-session` | resolved |
| H4-R `n/a` never specified | high | **Upheld — third instance of this defect.** `no-index` added to Issue 3.1's SPEC text (with its exit code) and to Issue 3.3's report vocabulary. | `main-session` | resolved |
| H-NEW-1 false premise + fixture hazard | high | **Upheld — verified.** Four nested indexes exist under `plan-029/findings/okf-migration-samples/*/after/`; `incubator-bundle/after/index.md` carries `okf_version: '0.1'`. 3.2's premise corrected to cite the **live** violation. "Corpus-wide" pinned in 4.1/4.3a to `docs/plans/*/index.md docs/research/*/index.md`, with an explicit fixture exclusion and the reason. | `main-session` | resolved |
| H-NEW-2 projection carve-out unfiled | high | **Upheld.** Issue 5.5 now files **four**, projection delivery mode named first and carrying the `emit_conformant_copy` deletion as its provenance. SC9's count corrected. 5.2's cross-reference now resolves. | `main-session` | resolved |
| M-NEW-1 R2 unassigned | medium | Issue 1.3 now states the id mapping per row (`uv-okf` **and** `uv-_shared` on all four vendored-copy rows). R2's count corrected to four. | `main-session` | resolved |
| M-NEW-2 3.8 tests the wrong hypothesis | medium | 3.8 now emits the synthetic finding at **error** level under the new REQ (temporary, reverted — same shape as 1.4's mutant), plus a **positive control** with an allowlisted req proving the harness can observe a non-zero audit. | `main-session` | resolved |
| M-NEW-3 3.8 is a leaf | medium | `4.1 depends-on 3.8` added. | `main-session` | resolved |
| M-NEW-4 second producer | medium | Issue 4.2 extended to the yf-research producer with its own throwaway-bundle verification; SC7 reworded to "both producers". | `main-session` | resolved |
| M-NEW-5 two either/ors | medium | Both pre-decided. 4.2(c) → **emit-only-if-exists** (the scaffold-creates branch is self-defeating: git does not track empty dirs). 3.3 → **fix the producer**, exempt branch dropped with the layering reason recorded. | `main-session` | resolved |
| M-NEW-6 Epic 3 ids unallocated | medium | Issue 2.2 widened to allocate for Epics 2 **and** 3, naming the `reindex` and drift-finding ids. | `main-session` | resolved |
| M-NEW-7 gate cwd mismatch | medium | Gate `cwd: worktree`; 4.3b states explicitly that it commits the worktree changes 4.3a wrote. | `main-session` | resolved |
| M-NEW-8 4.5 points not carries | medium | IN/OUT bullets inlined in 4.5. | `main-session` | resolved |
| L1 R9 mid-table | low | R9 moved to the end. | `main-session` | resolved |
| L2 `write_index` does not exist | low | Corrected to `scaffold_bundle` / `_read_index` / `render_index`. | `main-session` | resolved |
| L3 D-6 "exits 1" scoping | low | Reworded to name the scratch tree. Live tree is EXIT=0, all five byte-identical. | `main-session` | resolved |
| L4 log.md gap | low | The pass-2 `review:` line is now recorded. | `main-session` | resolved |
| L5 spurious 1.2 dep | low | `depends-on: 1.1` dropped from 1.2. | `main-session` | resolved |
| L6 hedged authority edit | low | Issue 1.1 now requires confirming from `git log`/`git blame` on that line, and recording the uncertainty in the edit if it cannot be confirmed. | `main-session` | resolved |
