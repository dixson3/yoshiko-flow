---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 4 on plan-061 — verdict APPROVE. Gate 2 green-reachability proven by exhaustive enumeration (all 25 matched files authorized by an issue); six residual concerns C23-C28 folded in, including a shipped always-loaded rule the gate scope had omitted.'
---
# Review pass 4 — adversarial (red-team)

## Verdict: APPROVE

**six residual concerns (C23-C28) folded in before this pass was recorded**
**Date:** 2026-08-30

## Part A — pass 3's four resolutions

**C19, C20 LANDED in full.** C20 verified across all four sub-parts, including `4.4 → [4.2, 4.2b,
4.3, 4.5]` **in the extracted DAG**, and confirmation that `:164` really is in §3 while `:219,225`
are in §5 — so Issue 4.3's section attribution is correct.

**C21 enumeration correct, count off by one** (14 lines, not 13) — see C27.
**C22 mostly landed**, one truncated `index.md` bullet survived — see C28.

Harness: `plan_extract --strict` exit 0 / `unparsed: []`; `audit` **pass**; `recheck-criteria`
`class_a 10, evaluated 10` with SC9/SC10 `manual`. **SC7 now evaluates `holds` (exit 0) — the
repo's FULL tier is green**, which C22's reindex fixed.

## Part B — Gate 2 green-reachability: ENUMERATED, not counted

| Files | Count | Authorizing issue |
| :-- | --: | :-- |
| skill `README.md` (17 skills) | 17 | **4.2** |
| skill `SKILL.md` (6 skills) | 6 | **4.2b** |
| `DRIFT-CHECK.md` (`:164,:219,:225`) | 1 | **4.3** |
| `README.md` (`:42`, its only matching line) | 1 | **4.5** |

**17 + 6 + 1 + 1 = 25. No unauthorized file. Gate 2 IS green-reachable.**

4.2's population split verified exactly: the four runnable-command-block READMEs are
`yf-beads-authoring:24`, `yf-beads-extra:22`, `yf-plan:59-62`, `yf-research:28-31`; the other 13
are prose-only. All 24 non-`README.md:42` hits were read individually — every one names the repo
installer as a live mechanism. **No further reword-would-be-wrong case exists.**

## Concerns (all resolved before recording)

| # | Severity | Concern | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| C23 | medium | **Gate 2's Condition asserted more than its Test checked, and the gap contained a SHIPPED always-loaded rule.** `skills/yf-research/protocols/RESEARCH.md:4` is installed verbatim to `~/.<surface>/rules/RESEARCH.md` — an always-loaded rule telling every user to run a script deleted at plan-010 — and sat outside the four path globs. Gate 2 would have reported green over a false Condition: the vacuous-check class (#263, R1) the plan exists to close. | **RESOLVED, both halves.** `skills/*/protocols/*.md` added to the Gate-2 Test, SC5 and Issue 4.2b (path set 25 → **26**). The Condition is also narrowed to name exactly what it measures, so `skills/*/spec/` — internal design prose, not reader-facing instruction — is **deliberately and visibly** out of scope rather than silently unmeasured. | `main-session` | `resolved` |
| C24 | low-medium | **Issue 4.4 was unsatisfiable as literally written** — "sweep repo-wide and assert zero" matches **108** tracked files, 63 under `docs/plans/`, contradicting the very gate it discharges. Same defect class as C19: prose an executor can read literally and get stuck on. | **RESOLVED.** 4.4 now names the Gate-2 path set explicitly and states why *not* repo-wide, with the 108/63 measurement. | `main-session` | `resolved` |
| C25 | low | **Stale numeral in Gate 2's Instructions** — "26 files, 8 archived", invalidated by C3's own pattern-broadening. Measured today: broad+unscoped → 108/63; narrow → 23/8. The "26" matched neither pattern. | **RESOLVED.** Restated as 108/63. | `main-session` | `resolved` |
| C26 | low | **Motivation's enumeration contradicted Issue 4.3** — said "three times" but cited two line numbers plus *the section they live in*, omitting the real third hit `:164`. | **RESOLVED.** Now cites `:219`/`:225` (§5, Install-section source) and `:164` (§3, the `e-frontmatter` source of truth) as the distinct things they are. | `main-session` | `resolved` |
| C27 | low | `13 lines` vs an enumeration of **14**. | **RESOLVED.** 14. | `main-session` | `resolved` |
| C28 | low | `index.md:15` truncated mid-sentence at "Deferred to" — C22's "every member carries a real description" was not fully true. | **RESOLVED.** Tail restored. | `main-session` | `resolved` |

## Gate Assessment

| Gate | Reachable | Verdict |
| :-- | :-- | :-- |
| Start Gate | yes | Fine. |
| Capability: checker is sensitive | **yes** | Re-confirmed; *"Nothing further."* |
| Capability: no install.sh reference | **yes** | C20 fix complete and verified by exhaustive enumeration; C23/C25 close the Condition-vs-Test gap. |
| Reconcile Gate | yes | Standard. |

## Portability

**Executable by a cold session holding only this bundle.** Every command is inline; `context.md`,
`upstream-triage.md`, four findings and eight upstream references are present; `index.md`/`log.md`
are reserved-file conformant; 10 of 12 criteria parse to executable clauses.

## Premise check — the through-line of four passes

Each pass falsified an inference the previous one had left standing, and they form one sequence:

1. **Pass 1:** *"a checker exiting 1 proves it is sensitive"* — falsified; three harness faults all exit 1.
2. **Pass 2:** *"a declared gate will run"* — falsified; absent `test_class`, the sweep runs nothing.
3. **Pass 3:** *"the files a gate matches are all defects"* — falsified; `README.md:42` is true.
4. **Pass 4:** *"the gate's path set covers the surfaces its Condition names"* — falsified; a shipped rule sat outside it.

Every one is the same shape — **a check believed to be measuring more than it measures** — which is
the exact defect class this plan exists to close. The plan is stronger for having had it applied to
itself four times.
