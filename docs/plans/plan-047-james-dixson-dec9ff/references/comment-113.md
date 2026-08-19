---
type: Reference
okf_spec: OKF-PLAN
id: comment-113
---
## Re-scoped to sit BEHIND a common extractor — and this issue's own data trigger is still unmet

Two separate updates. Taking them in order, because the second is the one that changes what
happens next and the first is a correction that argues *against* acting.

### 1. plan-046's escapes were NOT this issue's class

The disposition set in [the previous comment](https://github.com/dixson3/yoshiko-flow/issues/113#issuecomment-5309052196) was a **data trigger**:
revisit *"if two consecutive plans show structural escapes the prose cross-check missed."*

plan-046 has since completed, burning its full five-cycle review budget and producing **two
escapes that survived every cycle**. It would be easy to read that as the trigger firing. It is
not:

| Escape | Class | Would a topological walk against running state catch it? |
| :-- | :-- | :-- |
| SC3 required `grep -rniE "OKF v0\.1"` to return zero hits, while Issues 2.1 / 2.3 / 2.4 *mandate* v0.1 references | criterion ↔ issue contradiction | **No.** No ordering defect — every precondition was satisfied at the point it was needed |
| Issue 4.5 instructed "close #140 as `partial`"; the engine at `plan_manager.py:2023` requires a `partial` row to stay OPEN | plan claim vs enforcing-code contract | **No.** Nothing in the plan graph disagrees with anything else in the plan graph |

Both are **claims-class**, not ordering-class. The structural escape count for *this issue's*
class across the four measured plans is now **1 → 1 → 0 → 0**.

So: the trigger has not fired, and the honest reading of plan-046 is that it supplies **no new
evidence for building the DAG walk**. Recording that explicitly because the surface reading —
"we just had two escapes that survived five review cycles" — points the opposite way.

### 2. What *has* changed is the price, and it changes the build order

This issue was costed against zero existing infrastructure: the walk is "a new script." That
costing is wrong in both directions, and #174 identified why while proposing the claims-half
counterpart:

> They likely want to be **one pass with two checks**, because both need the same prerequisite:
> **the plan's assertions extracted into a machine-readable list.** That extraction is the real
> work; once it exists, both checks are cheap. Worth deciding deliberately rather than building
> two extractors.

Measuring that prerequisite produced a sharper result than expected.

**Nothing machine-reads the plan's primary payload.** `plan_manager.py` is 4779 lines and
contains **zero** parses of `### Epic N:` or `- Issue N.M:` — every apparent match is a code
comment citing a plan issue by number. The epic/issue DAG is read by exactly one consumer: an
LLM at SKILL.md §5.2a freehanding `bd create` calls. Pour fidelity — bead count and edge set
versus what `plan.md` declares — is verified by nobody. `yf-herdr`'s deviation table already
lists the mismatch as something for a human observer to watch for, which is an admission that a
human is the only checksum.

Meanwhile **six partial readers** of the other sections already exist, each with its own slicing
rule: `_plan_content_sections` (fingerprint), `parse_upstream_rows`, `_CI_RELEASE_SCAN_SECTIONS`
(classify-deliverable), `_read_plan_field` / `_read_field_line`, `_TRACKER_ROW_RE`, and `audit`'s
section-presence check.

That third one is instructive on its own: `classify-deliverable` **already wants** structured
access to the Epics section and settles for prose keyword matching, with the accuracy caveat
written down next to it — `spec/cli.md:73` scopes the region and `SKILL.md:599` grades the signal
**"weak — check the quoted signals before accepting."** An extractor-shaped hole with a
documented accuracy disclaimer already attached.

So it was never "two extractors." It is one LLM extractor doing the load-bearing work, six
partial ones doing the rest, and two proposed checks that would have made eight.

### 3. The corpus is messier than the template, and the template is fine

Before assuming a grammar exists to extract against, all 47 plans were measured:

| Section | Declared template (`SKILL.md:395-412`) | Corpus reality |
| :-- | :-- | :-- |
| Epics / Issues | fully specified | conformant in 041–046; **4 legacy variants** in 002–040 (`Issue A.1`, `- **Issue 1.1: Title.**`, `- **Issue 1.1:**`, `- **Issue 2.2 (#100):**`) |
| Gate `Test:` | `- Test: <bash command>` | 38 clean · **3 with a parenthetical before the colon** · 1 fenced multi-line · 1 `*(none)*` sentinel |
| Gate `Blocks:` | `<issue refs>` — **no grammar** | **10 distinct shapes** across 72 values, incl. `reconcile step` (20), `Epics 2, 3, 4`, `D.1`, `4.3b`, and the wildcard `Issue 2.x / 3.x`. Only **12 (16.7%) parse as a pure id list** |
| Risks & Mitigations | **empty** | 28 table · 18 bullet |
| Success Criteria | **empty** | 23 bullet · 21 numbered · 2 table · 1 none |
| Criterion ids | unspecified | **2 of 47** plans declare them (31 of 367 items). Six *more* reference undeclared positional ids |

Two things fall out.

**The `Test:` row is a fail-open trap for #174's falsification rule specifically.** A parser
anchored on `^- Test:` silently drops 7% of gate tests and picks up one false positive
(`- Testing is sandboxed-HOME per…`). A harness that *silently skips* the gates it exists to
falsify reproduces the vacuous-gate defect it was built to catch.

**The criterion-id row is what blocks #174 Part 2**, and the deeper measurement is worse. Its
cross-check matrix is bidirectional, and **45 of 47 plans have no key to join on**. Worse, the
criterion→issue edge **cannot be recovered from the existing text**: only 13.3% of the 367
criteria mention an issue id at all, and hand-adjudicating the strongest signal gives ~73%
precision — a combined yield of **~10%**. The failure is structural rather than tunable: *a
mention is not a discharge*. plan-039's SC1 infers to `1.3` purely because a parenthetical reads
"it also contradicted 1.3's licence to pick the next free number"; the actual discharger is 1.1.

So the honest position is that #174's matrix **starts empty and fills forward**. Backfilling it
would mean ~330 human decisions, and shipping *inferred* edges would be worse than shipping none —
mostly-absent, partly-wrong, and indistinguishable downstream.

**The template itself is not the problem.** `SKILL.md:395-412` already declares exactly the form
plans 041–046 use. Where it is specific, plans drifted away and came back. Where it is silent —
Risks, Success Criteria — there was never anything to drift from. This is not a missing standard;
it is a standard that nothing executes, which is precisely #149's M5 (*a step with no exit code is
not a step*), on the plan document itself.


### 3b. And the extractor's first consumer is already failing — measured

Prototyping the extractor produced the finding that actually pays for it, and it has nothing to do
with either review pass. Joining the extracted DAG against the live bead graph across 43 comparable
plans:

| Axis | `plan.md` declares | `bd` has | Divergence |
| :-- | --: | --: | :-- |
| epics | 189 | 188 | 1 never poured |
| issues | 781 | 752 | 31 unmatched |
| **dependency edges** | **885** | **860** | **45 dropped · 20 invented** |
| gates | 116 | 114 | 4 plans disagree |

**17 of 43 plans carry at least one divergence — a 40% per-plan pour-defect rate.** A dropped
`blocks` edge is not cosmetic: it means the coordinator marked a bead ready **before its declared
predecessor**. plan-019's Issue 4.1 declares `depends-on: 2.3, 3.4`; the bead has no 3.4 edge.
plan-016's A.3 declares `depends-on: A.1`; the bead blocks on **A.2** instead.

Three plans — 006, 007, 036 — have **no recoverable plan↔bead mapping at all**: no task bead title
carries its issue id, so the mapping is unreconstructable by any tool.

**Positive control, because a comparison that cannot fail proves nothing.** Against an unmutated
copy of plan-046 the comparator reports `clean: True` on all six axes. Deleting one `- Issue 3.5:`
line, then additionally dropping one `depends-on` and one whole gate block, made the issue-set,
edge-set, and gate-count axes fail in turn.

**The consequence for this issue specifically: #113's DAG walk cannot be built on the bead graph
alone, because the bead graph is one of the two things under test.** The walk needs the document
and the graph, and it needs to know which one is wrong.

Encouragingly, the last six plans (041–046) measure **0 dropped, 0 invented** across 215 edges —
so this is a legacy-and-drift problem, not an ongoing one. But nothing detects it either way.

### 4. Disposition

Filed as **plan-047**, triaged with this issue as `partial` — it stays **open**. That plan builds
the substrate and deliberately does **not** build this walk:

1. formal templates per document type (plans, research, and the `SPEC.md` family), adding the
   structure #174's consumers require — stable criterion ids, a `discharged-by:` link per
   criterion (**mandatory for new plans, backfilled for none**), a grammar for `Blocks:`;
2. a per-type **linter** engine, binding fail-closed at INTAKE, as a `CHANGE-VALIDATION.md`
   recipe row, and always-on on-edit;
3. a **normalizer** for the historical corpus, in the shape of the OKF `migrate` path plan-046
   shipped;
4. the **common extractor**, whose first consumer is the pour-fidelity comparator above — not
   either review pass.

The extractor is justified on its own merits by (4). If it needed #113 or #174 to pay for itself
it would not be worth building, and the honest reading in §1 above is that this issue currently
cannot pay for anything.

**Trigger unchanged, cost changed.** Revisit when two consecutive plans show structural escapes
the prose cross-check missed. If that happens *after* plan-047 lands, the walk is a reader over
an existing JSON structure rather than a new parser — which is the whole point of sequencing it
this way.

**Cross-references:** #174 (the claims half, same substrate, also `partial`) · #149 (M5/M9 — the
general form of "a written rule that nothing executes") · #165 (the same defect on `SPEC.md`
`Verification:` lines, `include` in plan-047) · #135 (measured literals in plan.md going stale).
