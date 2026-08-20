---
type: Review
okf_spec: OKF-PLAN
id: pass-3
status: complete
---

# Red-team pass 3

## Verdict: REVISE

**First independent reviewer.** Passes 1 and 2 were performed by the main session — the drafter
reviewing its own draft. This pass was dispatched via the `Agent` tool at the operator's explicit
request, ran in an isolated context, built a sandbox spike (`mktemp -d`), and left the repository
unchanged.

The reviewer's own note, recorded because it is evidence for #182: *"I read `red-team.md:63`
('Read-only — never writes files') and would have declined the spike had the operator not
explicitly authorized it. This review is itself an instance of the defect #182 describes."*

## Strengths

- **Four of six findings reproduce byte-exactly** under independent re-derivation: the 49/49
  hand-closed wrappers, the 26 `discovered-from` edges with 0 attributed (162 of 1481 beads carry
  `metadata.plan`), the byte-identical `doc_lint` verdicts (`cmp` reports IDENTICAL), and
  `_verify_row`/`red-team.md:63`. EXP-002's mechanism claim verified at source: `${START_GATE}`
  wired at `SKILL.md:862/909/933`, `${START_GATE_BEAD}` resolved at `:1056`, and **nothing
  anywhere closes the wrapper**.
- Pass 1's C1 restructure **genuinely fixed the cycle** for four of five gate members, derived
  from the DAG rather than prose.
- `plan_extract`: 7 epics, 25 issues, 32 edges, 4 gates, 20 criteria, `unparsed: 0`; every
  `Discharged-by` resolves; no issue unnamed by a criterion; `audit` pass; `doc_lint` PASS.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C10 | **high** | **Epic 4 (M9) has no producer seam.** Every `discovered-from` code hit is a *consumer* (`active_set.py`, `beads_hygiene.py`, `upstream.py`); the only producers are prose — `coordinator.md:279` and `yf-research/spec/phases.md:24`. So Issue 4.2's only implementation is adding `--metadata` to a prose instruction, which the Approach explicitly forbids. **SC11 cannot fail**: whoever writes "create one; assert the field is present" creates it stamped — R4's class, inside the epic D-4 was written for. Issue 4.3's detector is mechanical but the plan names no file, gate or validation row that runs it, and D-7 leaves it an empty input set on day one | Either (a) relocate enforcement to a real seam — `beads_hygiene.py` reports unstamped post-cutoff beads, wired into a named runnable surface, making 4.3 the deliverable — or (b) declare M9's producer half **unenforceable prose under D-8**, as #182 already is. What must not stand is a claimed "producer change at one seam" that does not exist |
| C11 | **high** | **EXP-001's forward recommendation is falsified.** A repaired scanner finds **163** SC rows (not 101 — a 61% undercount) and **does** find SC31 and SC23, so the recall failure was a regex defect, not undecidability. Worse: the recommended citation-resolution check **would have PASSED both** — SC23 carries an inline derivation, SC31 says "the derived post-write target". SC16/Issue 6.2 would publish that recommendation upstream | Correct EXP-001 before 6.2 drafts. **D-6 survives and is strengthened** — the better argument for dropping #177 is that the successor design green-lights the very cases it was built for |
| C12 | medium | **`_verify_row` cannot supply a grant.** It returns `{detail, disposition, issue, verdict}` — no `required_action`; the requirement lives in branch conditions and f-string prose. It is network-bound (`gh issue view` per row). Called directly with an `exclude` row it returns **`fail`: "unrecognised literal"** — for a literal that *is* in `UPSTREAM_DISPOSITIONS`. `tracker` returns `inconclusive` unconditionally; `deferred` is a declared non-action. SC8's import assertion cannot detect any of this, and R6's "structurally impossible" is untested inference | Extract the per-disposition *requirement* into a shared table both generator and verifier consume; make SC8 assert on that table, not on an import. Handle `exclude` explicitly. Correct R6's wording |
| C13 | medium | **The gate blocks 5.2, outside its own Condition.** `5.2 producers-in-ancestors: []` — Epic 5's parity check has no RED/GREEN fixture and no producer ancestor, yet the Condition reads "for each control shipped by **Epics 1-4**". Pass 2 asserted "every producer is an ancestor of what it unblocks" as universal; it is false for 5.2 | Drop `5.2` from `Blocks` → `1.4, 2.4, 3.4, 4.3` |
| C14 | medium | **SC7 has no baseline.** `--exclude` is sound (817 → 757 files_checked, confirming the self-inflation was real), but SC7's only `Discharged-by` is 2.3, which runs *after* 2.2 lands. No issue captures the "before" figure | Capture the pre-change corpus figure in 2.1 (or 0.2) with the exact `--exclude` invocation, and add it to SC7's `Discharged-by` |
| C15 | medium | **Eight stale issue references survived the pass-1 renumbering** — 4 in `plan.md` (gate Instructions, R2, R5, R6), 4 in `context.md` (Epic 5→6 twice, Issue 4.1→4.2, 5.6→6.6). Sharpest: **R5 cites a mitigation no issue performs** ("Issue 1.3's RED fixture asserts the cascade still fails on a genuinely open child" — 1.1 owns the fixtures, 1.3 is the ordering assertion). Nothing mechanical catches this | Renumber all eight; then confirm the open-child assertion is actually in 1.1's text |
| C16 | medium | **The Reconcile Gate has neither Condition nor Test** (`condition: null, test: null`) — a regression against plan-049, in a plan whose thesis is *a step with no exit code is not a step* | Copy plan-049's Reconcile Gate Condition and `jq -e` test, retargeted |
| C17 | medium | **context.md's network claim is false for Epic 3.** It says "network required for `gh` only, in Epic 5; Epics 0-4 are entirely local" — but 3.2's grant verb calls `_verify_row` → `gh issue view`, and 3.1 drives that path | Correct context.md and add the `gh` precondition to 3.1 — or take a pre-fetched payload so it genuinely can be local, which also addresses C12's point 2 |
| C18 | low | The Objective cites **"0 of 53"** as a bare local measurement, contra D-5, R4 and EXP-004's own warning; the local figure is **26**. Separately the title and Objective still say "**six** … #177–#182" after D-6 dropped #177, while `index.md` says "five … #178-#182" | Attribute the 53 to research 004, add the local 26/0, and change six→five / #177→#178 in the title and Objective |
| C19 | low | **Pass 2's C7 rationale is factually wrong.** The missing harness exits **127**, not 2 — `SKILL.md:1140`'s INCONCLUSIVE carve-out covers a gate with no runnable test, not a command that ran and exited 127. plan-049 solved this with a `gate-run.sh` normalising wrapper; plan-050 inherits none of it, and declares no `test_class` | Adopt the `gate-run.sh` wrapper and declare `test_class: probe` |
| C20 | low | EXP-002 says "a different bespoke sentence each time" — measured **29 distinct across 49**, not 49. 49/49 hand-closed is exact and remains the strongest evidence in the plan | Say "49 of 49 closed by hand, with 29 distinct improvised reasons" in the finding and the #179 comment |

## Missing

- No issue captures SC7's pre-change baseline (C14).
- No named host for Issue 4.3's detector (C10).
- R5's stated mitigation is implemented by no issue (C15).

## Gate Assessment

Four gates. The driven-red gate is the plan's best structural idea; pass 1's restructure fixed the
cycle for four of five members, and every producer sits at depth 2 (`0.1 → 0.2 → x.1`) so it
cannot be hoisted earlier — no frontloading miss. **5.2 is the exception** (C13). Two mechanical
defects remain: no 0/1/2 normalising wrapper (C19) and no `test_class`. The **Reconcile Gate** has
neither Condition nor Test (C16). The **Upstream-write gate** dogfoods this plan's own #178 fix —
good design — but cites the wrong issue (C15) and depends on the verb with C12's design gap.

## Upstream Assessment

12 rows; every `include` names a resolving issue and every `Resolved By` resolves in the DAG. The
`partial` IN/OUT splits for #149 and #150 are "the clearest I have seen in this corpus". Two
problems: **#177's `partial` is discharged only by SC16, which would publish a claim measured to
be false** (C11); and **#149's `partial` is discharged by 4.2/4.3, whose mechanical half does not
exist** (C10) — closing #149's M9 half on a prose change would be the precise failure this plan
was written to end. This plan's table carries **no `tracker` row** for its own coarse tracker, so
Issue 3.3's `tracker` path has synthetic coverage only.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C10 | high | **Epic 4 re-scoped onto a real seam** (operator decision): the deliverable is now the detector in `beads_hygiene.py audit` plus a named `CHANGE-VALIDATION.md` §1 caller; the producer prose ships as explicitly supporting, not load-bearing. SC11 replaced with a two-sided fixture that can fail; SC12b/c/d added for the caller, the mechanical cutoff, and the honest prose status | `operator` | resolved |
| C11 | high | `exp-001` rewritten with the sandbox re-derivation: 163 rows not 101, the miss was a regex defect, and the citation check **passes SC23 and SC31**. D-6 retained and strengthened; 6.2 must publish the corrected result | `main-session` | resolved |
| C12 | medium | Issue 3.2 now extracts a shared requirement table both generator and verifier consume; 3.2a ships the verb on top of it. SC8 asserts on the table, not an import. SC10 names `exclude`. R6 raised low→med and its "structurally impossible" wording corrected | `main-session` | resolved |
| C13 | medium | `5.2` dropped from the gate's `Blocks`; now `1.4, 2.4, 3.4, 4.3`, consistent with its own "Epics 1-4" Condition | `main-session` | resolved |
| C14 | medium | New Issue **0.2a** captures the pre-change baseline with the exact `--exclude` invocation; added to SC7's `Discharged-by` | `main-session` | resolved |
| C15 | medium | All eight stale references renumbered (4 in `plan.md`, 4 in `context.md`). R5 now cites **1.1's** open-wrapper fixture, which is a real node | `main-session` | resolved |
| C16 | medium | Reconcile Gate given a Condition and a runnable `bd list ... \| jq -e` Test | `main-session` | resolved |
| C17 | medium | `context.md` corrected — Epic 3 requires network and `gh`; the earlier "Epics 0-4 are entirely local" claim is named as refuted | `main-session` | resolved |
| C18 | low | Title and Objective now say **five** / **#178-#182**, matching `index.md`; the 53 attributed to research 004 with the local 26/0 alongside | `main-session` | resolved |
| C19 | low | Adopted plan-049's `gate-run.sh` 0/1/2 normalising wrapper (shipped by Issue 0.2) and declared `test_class: probe` | `main-session` | resolved |
| C20 | low | `exp-002` now says **49 of 49 hand-closed, 29 distinct reasons**; the #179 comment inherits the precise form | `main-session` | resolved |

## Consequence beyond this plan

This pass is the measured case for **[#184](https://github.com/dixson3/yoshiko-flow/issues/184)**,
filed during its resolution and folded into this plan as Issues 5.3/5.4: `SKILL.md` §3 never
dispatches the red-team as a sub-agent, so following it literally produces the main-session
self-review that passes 1 and 2 were. The repo's `AGENTS.md` gained a `## Delegation to
sub-agents` section in the same change.
