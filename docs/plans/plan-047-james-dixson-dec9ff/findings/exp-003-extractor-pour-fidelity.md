---
type: Finding
okf_spec: OKF-PLAN
id: exp-003-extractor-pour-fidelity
---
# EXP-003 — Prototype extractor, and the first measurement of pour fidelity

**Status:** complete · **Date:** 2026-08-18 · **Verdict:** the pour is **measurably unfaithful in
40% of plans** — 45 dropped and 20 invented dependency edges. A positive control proves the
comparison fires on injected defects. This, not either review pass, justifies the extractor.

## Premise confirmed

`plan_manager.py` is 4779 lines. `grep -n '### Epic'` → **zero output**. A wider grep returns 30
hits, **every one inside a comment or docstring**. Nothing in the toolchain reads the epic/issue
DAG out of `plan.md`.

## THE HEADLINE — pour fidelity

46 plan folders; 3 (plan-001/002/003) predate the `**Epic:**` field and cannot be joined.

> **Of the 43 comparable plans, 26 are clean and 17 carry at least one divergence — a 40%
> per-plan pour-defect rate.**

| Axis | plan.md | bd | Divergence |
| :-- | --: | --: | :-- |
| epics | 189 | 188 | 1 never poured (plan-041) |
| issues | 781 | 752 | 31 unmatched |
| **dependency edges** | **885** | **860** | **45 dropped · 20 invented** |
| gates | 116 | 114 | 4 plans disagree |

Restricted to the 40 joinable plans: 2 dropped / 20 invented edges, 26/40 clean → 35%.

**The six most recent (041–046): 184 issues / 185 beads, 215/215 edges, 21/21 gates — 0 dropped,
0 invented.** The two flagged are plan-041's deliberately-not-poured epic and plan-045's bead
`6.4` added during execution.

### Representative defects, each re-verified with a direct `bd` call

- **Dropped edge, plan-019.** `plan.md:248` declares `depends-on: 2.3, 3.4`. `bd show
  yf-mol-99w.4.1` returns dependencies on `2.3` and its parent only. **The 3.4 edge does not
  exist — the task was executable before its declared predecessor.**
- **Corrupted edge, plan-016.** `plan.md:175` declares `depends-on: A.1`. The bead blocks on a
  *gate* and on **A.2**, and not on A.1. The pour substituted a different predecessor.
- **Work in bd, absent from plan.md.** plan-045 bead `6.4` ("REQ-CLI-006 self-consistency") exists
  and was executed — `git log` shows commit `18f3959` doing it — but `plan.md` Epic 6 lists only
  6.1, 6.2, 6.2a, 6.3. Same shape in plan-035 (`2.2b`).
- **Gate declared, never poured.** plan-019 and plan-027 each declare a `### Reconcile Gate` with
  no corresponding gate bead. plan-008 is the inverse: 3 gate beads, 2 gate headings, the third
  written *inside* the Epics section.
- **Identity destroyed.** In plans **006, 007, 036 no task bead title carries its issue id at
  all**. All 31 "issues with no bead" come from these three. The beads exist; the **mapping** was
  discarded, so no downstream tool can ever reconstruct it.
- **Body fidelity.** Across 750 joined pairs the median `len(bead.description) / len(plan.body)`
  is **0.68**; **32% of beads carry under half** the plan text; 63 carry a pointer only
  (*"See docs/plans/…/plan.md (Epics section) for the full instruction"*); 8 are empty.

## POSITIVE CONTROL — the comparison can observe a defect

Run against a **copy** of plan-046, which is clean on the live tree and is therefore the correct
negative baseline.

| Run | Result |
| :-- | :-- |
| unmutated copy | `clean: True` — all six axes true, 39/39 issues, 38/38 edges, 4/4 gates |
| delete one `- Issue 3.5:` line | `clean: False` — `extra_beads: ['3.5']`, 2 edges `in_bd_not_plan`, per-epic count mismatch |
| additionally drop a `depends-on` and delete a whole gate block | edges 36/38, **gates 3/4**, `gate_count_match: False` |

**All three axes fire on injected defects and are silent on the unmutated original.** The 40%
figure is a measurement, not an artifact of a comparison that cannot fail. The control was re-run
after every extractor change and still passes on the final version.

## Extractor failure modes (honest)

All **46/46** plans yield ≥1 epic, ≥1 issue, ≥1 gate, ≥1 criterion — working unmodified back to
plan-001. But only after **four widenings forced by measurement, each of which had been silently
corrupting the fidelity number**:

| # | Construct | Verdict |
| --: | :-- | :-- |
| 1 | `- **Issue 2.2 (#100): …**` — parenthetical between id and colon | too naive; **before the fix it reported 3 phantom "extra beads" in plan-037** |
| 2 | `- Issue B.3 **(staged — …)**:` — bolded parenthetical | too naive |
| 3 | `depends-on: 6.1, 6.2, 6.3 (consolidates with Issue 4.3)`, `depends-on: G1, 4.4` | **genuinely ambiguous** — free text after a machine field. Naive id-scraping *invented* a `6.4→4.3` edge; strict list-parsing *dropped* 4 real ones. Any rule here is a guess |
| 4 | Success Criteria in **three** spellings (ordered, bullet ×25, table ×2) | **genuinely ambiguous** — three grammars for one section |

**Constructs it reports rather than guesses at** (`unparsed`), all genuinely ambiguous:
`### Epic 6 (follow-on, NOT built in this plan):` — a heading whose prose negates its own
structure; `### Epic 2: … — MOVED to plan-042` — **the sole epic-count divergence in the corpus,
where bd is right, the document is right, and only prose reconciles them**; and two non-epic
`###` headings inside `## Epics`.

**Where the extractor beats grep:** 6 plans carry `### Epic N` headings *outside* `## Epics` —
plans 026 and 027 restate the full epic list in Approach, so a naive `grep -c '^### Epic'`
double-counts. The fence-aware section splitter gets these right. **This structurally confirms
`classify-deliverable`'s "weak" self-grade**: whole-file keyword matching double-weights those two
documents, and a section-scoped extractor removes that class outright.

## `bd list` hides gates — #166 reproduced

```
bd list --all --limit 0 --json                  ->  1290 beads,   0 gates
bd list --all --include-gates --limit 0 --json  ->  1411 beads, 121 gates
```

Any consumer omitting `--include-gates` sees a graph with **121 nodes and every gate edge
missing, with no error.**

## Implications

1. **The pour is unverified and measurably unfaithful.** A dropped `blocks` edge means the
   coordinator marked a bead ready **before its declared predecessor**. Critically: **#113's DAG
   walk cannot be built on the bead graph alone, because the bead graph is one of the two things
   under test.**
2. **Three plans have no recoverable plan↔bead mapping.** Any pour must preserve the issue id —
   and a **metadata key (`plan_issue: "3.5"`) is strictly better than a title convention**,
   because titles get rewritten.
3. **Bead descriptions are not the plan text.** #174 must read `plan.md`, never the bead body.
4. **367 criteria, 116 carrying a runnable command.** #174's input corpus exists today — in three
   incompatible section grammars.
5. **`depends-on` is the weakest link** — the only machine-consumed field routinely written with
   prose tails, bold, and gate references, and where every silent-defect instance landed.

## Recommendations

1. **A schema-driven extractor is the right shape — but only above a normalized corpus.**
   Everything that defeated the prototype was *lexical* and every fix was a regex widening in a
   per-type table, never bespoke logic. But each fix was driven by an *observed* failure and had
   been silently corrupting the number until found — so ship the extractor **with** the normalizer
   and linters, and make it **fail loudly (`unparsed`) rather than degrade**. The prototype does;
   keep that property.
2. **Two constructs need a document decision, not a parser.** (a) A `depends-on` carrying prose —
   forbid it in the linter, move rationale to the body. (b) A structurally-present but
   deliberately-not-poured epic (plan-041's "MOVED to plan-042") — needs an explicit `status:
   moved` marker, or the extractor reports a false pour defect forever.
3. **Ship the comparator as a gate, not a report.** 184 lines, one `bd list --all --include-gates`
   call. Run at plan close it would have caught all 65 edge divergences. **Its positive control
   must ship with it and run in CI** — that control is the entire reason this measurement is
   trustworthy.
4. **Every bead-graph consumer must pass `--include-gates`** (#166).
5. **Do not treat "extra bead" as a pure defect.** plan-045's `6.4` and plan-035's `2.2b` are real
   executed work the document never learned about. The fix is a **write-back path** (execution
   amends `plan.md`), not a prohibition.

## Reproduction

`exp003/extract_plan.py` (362 lines), `exp003/pour_fidelity.py` (184 lines), in the agent
worktree. No bead created, closed, or modified; no `bd dolt push`.
