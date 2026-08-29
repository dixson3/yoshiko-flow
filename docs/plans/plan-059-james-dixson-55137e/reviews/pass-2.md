---
type: Review
okf_spec: OKF-PLAN
---
# Red-team pass 2 — plan-059-james-dixson-55137e

## Verdict: REVISE

Isolated agent. **Every claim was executed, not read** — a sandbox under `$(mktemp -d)` (removed,
repository unmodified), read-only `gh`/`git`, and an independent re-derivation of the
command-vs-obligation counts.

## Strengths

- **The escalation gate's rewrite is genuinely better, and the specific claim was verified.**
  `doc_lint --type review --path <file in $(mktemp -d)>` returns `files_checked: 1` with three real
  findings on an invalid document, versus `files_checked: 0, PASS` on a bare `--path`. Single
  physical line; fails today; self-cleaning on the failure path; `jq -e` correctly returns 1 on the
  INCONCLUSIVE shape.
- **GFM escaping is sound** — every row of the three piped tables has a consistent cell count.
- **Rows 1 and 2 of the law reproduce exactly** on independent re-derivation, with plan-048
  confirmed as the miss.
- **The SHIP / DO-NOT-SHIP judgement is correct and better supported than pass 1 concluded** — the
  obligation row moves *further* in the law's predicted direction, and the detector refusal rests on
  a control read that genuinely refuted its commissioning premise.

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| D1 | **C1 is NOT resolved — the first capability gate is still green today.** `grep -qE 'REQ-DATA-[0-9]+' skills/yf-plan/spec/data.md` exits 0 right now; the file already carries 46 such ids. It `Blocks: 1.3, 1.5`, so both are ungated. Pass 1's Resolutions table marked C1 resolved while describing only the Start Gate and the *escalation* gate — **the repair skipped one of the two gates the concern named.** | high |
| D2 | **The repaired escalation gate's load-bearing half is a TAUTOLOGY at the moment it runs.** `doc_lint`'s `STATUS_SEVERITY` demotes `{W,E} -> R` at `approved`/`executing`/`complete`. Measured on a stripped `plan.md`: status `review` -> FAIL, 8 errors; status `approved`/`executing`/`complete` -> PASS, **0 errors**, 8 report-only. The gate copies plan-059's own bundle, whose status will be `approved`/`executing` when it fires — so `.errors == 0` **cannot fail** and the gate collapses to "the escalation type has a schema", precisely the assertion the Instructions call *not* load-bearing. **SC2 carries the identical construction.** Compounding: if `escalations.toml` ships at `R` as Epic 1 deliberately does for `review.toml`, `errors` is 0 at *every* status. **Issue 2.2 never states a severity.** | high |
| D3 | **Issue 6.1 contradicts escalation E-4's resolved default, and its target file is not in this repository.** `finding_recurrence.py` exists only on the unmerged `research/005-thrash-detection` branch, not under `${SKILL_DIR}/scripts/` where SC9b's command names it. E-4's recorded outcome: *"the parser repair is scoped in **only if the detector epic survives (it does not)**."* **The plan is silently overriding a resolved escalation of its own dogfooding record — in the plan that exists to make escalations binding.** | high |
| D4 | **SC9b bakes in two literals this plan itself invalidates.** `43` is the ≥3-pass bundle count as of EXP-002, and **plan-059 will itself become a ≥3-pass bundle — this is pass 2** — so the criterion is guaranteed to break for a reason unrelated to the repair. `22` came from a *parser-free grep*, a different instrument, not ground truth; asserting the repaired parser lands exactly there pre-judges the repair and hands the executor a Goodhart incentive to tune to 22 — **in a plan whose R4 is about Goodhart.** | high |
| D5 | **C5's correction is still wrong, and it repeats the very limit it added against itself.** Row 3's denominator is **5, not 4**: the same five plans carry script-written raises (050:7, 052:1, 054:2, 055:2, **056:3**) and only 050 and 052 carry `stop_class: 4`. plan-056's log records *"loop resumed after stop class 4 at 5/5"* — its escalation is not inferential. Honest figure: **2/5 (40%)**. 056 is excludable only as not-yet-complete, but **row 1 includes 056 in both numerator and denominator** — so rows 1 and 3 use silently different populations, the same class of error C5 was filed about, one revision later. Separately the row-1 command returns **12, not 15**, in the main checkout; 15 reproduces only in another worktree, because plan-056 is on an unmerged branch. | medium |
| D6 | **SC2d and SC9c are green today, and #273 already exists unrecorded.** `gh issue list --search "command-vs-obligation"` returns `[273, 269, 264]`, and **#273 is titled "The command-vs-obligation law: …"**, created 2026-08-28. **Issue 6.4's deliverable already exists**; SC9c passes before execution. `gh issue list --search "drift-check edge retrospective taxonomy"` returns `[145]` — it matches **#145 itself**. `gh` full-text search is fuzzy, making `length >= 1` near-unfalsifiable for any plausible phrase. | medium |
| D7 | **SC4 tests the contract Issue 3.1 is instructed to PRESERVE.** `review-loop-check` already exits 3 today. SC4 asserts "exit non-zero", which the pre-existing verb satisfies — it cannot distinguish "escalation payload added" from "nothing changed". | medium |
| D8 | **C2's fix moved the vacuousness into a self-reporting verb.** `judgement-echo-check … \| jq -e '.log_gained_not_fired_line == true'` — the verb's name encodes its own answer, and a three-line implementation returning `true` satisfies it. **And no issue creates the verb.** | medium |
| D9 | **C7's fix left SC1b strictly WEAKER than the exit code it replaced.** `review.toml`'s checks are all `R`, so `errors` is structurally always 0 for that type. Worse: on INCONCLUSIVE `doc_lint` exits **2** but still prints `errors: 0`, and with no `set -o pipefail` the pipeline exit is jq's — **SC1b now passes when the linter cannot run**, which the exit-code form would have caught. SC1 is fixture-dependent (a garbage review file already yields `report_only: 3` from pre-existing `R` checks). SC2c is over-strict: `audit` on plan-050 returns `status: pass` with **26 findings**, so `.findings == []` fails on almost any real bundle. | medium |
| D10 | **The `#269 (include)` annotations were never updated when C8 changed the disposition to `partial`** — three issue bullets still read `include`, and `audit` passes silently. Separately Issue 6.4 carries `resolves-upstream: #270 (deferred)`, which is mis-wired: 6.4 files the law, not #270, and a `deferred` issue cannot be resolved by anything. | medium |
| D11 | **Four issues are outward-facing writes and no gate represents them.** `context.md` declares issue create/comment a stop class, *"operator-authorized individually, never batched"*. Issues 2.7, 6.3, 6.4 file GitHub issues and the #269 row promises a correction comment. Under the autonomous default the executor either halts four times with no gate to resolve against, or writes upstream unauthorized. | medium |
| D12 | **An unresolved escalation produces no signal anywhere — the plan's own diagnosed failure mode, one level down.** `escalations.md` is deliberately invisible to the audit; nothing gates completion on a `state: raised` entry, no criterion covers it, no risk names it. **The plan's whole thesis is that a mechanism with no failure signal rots**, and it ships a record whose open state has no failure signal. | medium |
| D13 | **Several `depends-on` edges are structural rather than real, serialising the plan behind a human gate.** Issue 4.1 `depends-on 1.1` — amending `REQ-HERDR-024` does not need the yf-plan severity vocabulary — so all of Epic 4, a self-contained `yf-herdr` change, waits on an unrelated `REQ-DATA` edit. Epic 6 is a strict chain in which 6.4 has no substantive dependency on 6.3/6.2/6.1. | medium |
| D14 | **Epic 1 and Epic 4 are separable plans and the plan half-admits it.** 15 of 32 issues in three independently landable groups — pass 1's C4, unaddressed. The coupling argument is defensible; it just isn't made. | low |
| D15 | **`jq` is load-bearing for 12 of 21 criteria and is absent from `context.md`'s tool inventory.** | low |
| D16 | **The auto gate hard-codes this plan's own bundle path and requires the repo root as cwd.** | low |
| D17 | **Issue ordering within epics is non-monotonic** (2.7 before 2.6; 3.5 before 3.4) — visible residue of review-driven appends. | low |

## Missing

An explicit severity declaration for `escalations.toml`; issues creating `judgement-echo-check`,
`escalation-report`, `test_close_contract.py --assert-invocation` and the firing-rate flag — **four
verbs that success criteria call and no issue text creates**; an Upstream Issues row for **#273**; a
close-time signal for an unresolved escalation; `set -o pipefail` on every piped verification; and a
statement reconciling Issue 6.1 with E-4's recorded resolution.

## Gate Assessment

Two capability gates remains the right count and neither creates a cycle. **The escalation gate is
materially repaired** — it fails today, for the right reason, and cleans up on both paths. But **its
load-bearing half is a tautology at the status the bundle will carry when it runs**, and **the first
capability gate was never repaired at all and is green today.** The frontloading fix is sound and the
Start Gate's Instructions are decision-grade, with one exposure: an operator who approves without
engaging the three-option choice leaves the vocabulary unratified, and the gate meant to catch that
passes regardless. **That is the same defect twice** — the human gate correctly declines to test
ratification, and the auto gate meant to test its *residue* tests nothing.

## Upstream Assessment

Dispositions are now reasonable and the triage record is filled in. Three defects remain: **#273
exists and is unrecorded**, making Issue 6.4 redundant and SC9c green before execution; the
`resolves-upstream: #269 (include)` annotations contradict the table's `partial`; and 6.4's
`#270 (deferred)` is mis-wired. #264's and #145's dispositions hold up.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| D1 first gate still green | high | Accepted. Replaced with a test that **fails today** and asserts the vocabulary check by name against a fixture carrying `med`. | `main-session` | `resolved` |
| D2 gate tautology at status | high | Accepted — the sharpest finding in the pass. The scratch copy's `status:` is now forced to `review` before linting, **and a positive control is added**: an invalid escalation must produce `errors >= 1` before the valid one is asserted clean. A gate with only a negative arm cannot discriminate. Issue 2.2 now declares its check severity explicitly. | `main-session` | `resolved` |
| D3 6.1 overrides E-4 | high | Accepted in full. **Issue 6.1 is DROPPED.** E-4's resolved default is binding: the parser repair enters only if the detector epic survives, and it does not. Epic 6 loses its code change and becomes genuinely artifact-free, which strengthens rather than weakens the plan's central claim. | `main-session` | `resolved` |
| D4 SC9b bakes in literals | high | Moot — SC9b is deleted with 6.1. The reasoning is preserved in the Approach as a recorded hazard for whoever runs the re-measurement later. | `main-session` | `resolved` |
| D5 denominator is 5, not 4 | medium | Accepted. Corrected to **2/5 (40%)**, with the population stated per row and **"population mismatch" added beside "unit mismatch"** in Limits. The row-1 15-vs-12 discrepancy and its cause are recorded. | `main-session` | `resolved` |
| D6 #273 exists; searches green | medium | Accepted. **#273 added to the Upstream Issues table**; Issue 6.4 rescoped from "file it" to "correct #273 to the 2/5 unit"; both criteria now assert on a recorded issue **number**, not a fuzzy phrase search. | `main-session` | `resolved` |
| D7 SC4 tests the preserved contract | medium | Accepted. Now asserts the payload. | `main-session` | `resolved` |
| D8 self-reporting verb | medium | Accepted. SC6 now asserts a **content delta** — hash `log.md`, run the trigger on a not-fired bundle, assert exactly one added line matching the echo pattern. Issue 5.1 names the verb. | `main-session` | `resolved` |
| D9 SC1b weaker than what it replaced | medium | Accepted. All piped verifications gain `set -o pipefail`; SC1/SC1b assert **by check name**; SC2c rescoped to "no finding when the file is ABSENT". | `main-session` | `resolved` |
| D10 stale `#269 (include)` | medium | Accepted. All three normalised to `partial`; 6.4's mis-wired `resolves-upstream` dropped. | `main-session` | `resolved` |
| D11 unauthorized upstream writes | medium | Accepted. A single human gate now covers the upstream-write batch. | `main-session` | `resolved` |
| D12 open escalation has no signal | medium | Accepted, and it is the pass's best structural catch. New Issue 5.4 emits a `W` from the close-time chain when any escalation is `state: raised`, with new SC6c. | `main-session` | `resolved` |
| D13 fabricated edges | medium | Accepted. Epic 4 is re-rooted (no dependency on 1.1); Epic 6 fans out. | `main-session` | `resolved` |
| D14 separable plans | low | Accepted — the coupling argument is now **made** rather than assumed, in the Approach. | `main-session` | `resolved` |
| D15 `jq` unlisted | low | Accepted. Added to the tool inventory with its version. | `main-session` | `resolved` |
| D16 gate hard-codes the bundle path | low | Accepted. The gate resolves its source bundle from the plan dir it is given. | `main-session` | `resolved` |
| D17 non-monotonic ordering | low | Accepted. Renumbered. | `main-session` | `resolved` |
