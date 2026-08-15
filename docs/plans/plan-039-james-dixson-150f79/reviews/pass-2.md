---
type: Review
okf_spec: OKF-PLAN
---
# Plan Red-Team: plan-039-james-dixson-150f79

**Pass:** 2 · **Date:** 2026-08-14

> **Independent pass.** Performed by a fresh-eyes sub-agent with no access to the drafting
> conversation, addressing the reviewer-independence caveat recorded in `pass-1.md`. The reviewer
> re-ran the plan's own experiment harness rather than assessing internal coherence only.

## Verdict: REVISE

## Strengths

- The findings are re-runnable and most replicate exactly: `current TP=1 FP=16 TN=0 FN=0` →
  `all four TP=1 FP=2 TN=14 FN=0`, with `FN=0` at every stage and `plan-031` surviving as a true
  positive.
- The C4 bias control is real, not asserted — independently reproduced 8/8 `ci-release` on plans
  031–038 against a ground truth of 1.
- **Deferring #113's DAG-walk engine is justified, not rationalized.** EXP-002's two legs each
  independently undercut the expensive branch, and the finding retains #113's own `n=1` caveat
  rather than burying it.
- Fixture-and-harness before fixes is the correct shape, and the `FP=16` baseline still
  reproduces.
- `Gate: Upstream write` is genuinely reachable — the plan's strongest self-application of its
  own new rule.

## Concerns

- **H1 — SC6 is falsified by measurement: this plan still classifies `ci-release` after all four
  fixes.** — severity: high

  Measured: `plan-039 → ci-release, conf=low, signals=['release','sign','deploy','pipeline','workflow']`.
  Cause: the high pattern is `\brelease` and `-` is a non-word character, so **`\brelease`
  matches inside the literal token `ci-release`**, which this plan's `## Epics` and
  `## Success Criteria` sections — the exact F1 scan region — contain repeatedly. Independently
  confirmed: `re.search(r'\brelease', 'the ci-release deliverable class')` is `True`.

  Exposes a residual FP class EXP-001 never identified: **any plan discussing the
  deliverable-class feature self-flags** — distinct from the "consumes/references a release"
  class the finding documents. `plan-033` is the same phenomenon.

  Recommendation: (a) add a term-of-art exclusion (`ci-release`, `deliverable class`) to F2 as a
  *measured* entry — it moves corpus FP, satisfying the 3.4 stop rule — and re-verify SC6; or
  (b) restate SC6 as "classifies with `evidence: prose-only`, residual class recorded as a known
  limit". Do not ship SC6 as written.

- **H2 — Issue 3.2's harness expectation was never measured and is wrong by 4×.** — severity: high

  3.2 states F3's result as `FP=2` / `29→12`, but those are the **cumulative F1+F2+F3** figures.
  EXP-001 only measured the cumulative sequence F1 → F1+F2 → +F3 → +F4, which is **not** the
  implementation order the plan chose (F3 → F1 → F2 → F4). Measured in the plan's actual order:

  ```
  F3 only    TP=1 FP=8 TN=8  FN=0   corpus=22/53
  F3+F1      TP=1 FP=3 TN=13 FN=0   corpus=15/53
  all four   TP=1 FP=2 TN=14 FN=0   corpus=13/53
  ```

  An executor writing 3.2's harness to the stated expectation gets a red suite with no way to
  tell whether F3 is broken or the number is.

  Recommendation: use the per-step figures above, or assert only the invariants that hold at
  every step (`FN=0`, monotonically non-increasing `FP`), with the exact tuple asserted after 3.5.

- **H3 — no fixture exercises REQ-AGENT-047, the entire #113-partial deliverable.** — severity: high

  Issue 2.5's three fixtures cover 2.2, 2.3, and the existing capability check. There is **no**
  fixture for the **precondition cross-check** added by 2.4 — the item that discharges #113's
  `partial` disposition and that 5.2b announces upstream as shipped. The C2 gap survives its own
  resolution.

  Recommendation: add a fourth fixture from EXP-002's own table — "Epic 6 re-audits the hardened
  tree with no `depends-on` on Epics 1–5", whose pre-fix and as-landed text EXP-002 already
  quotes — and raise SC7 to 4 flags.

- **H4 — SC12, the C1 remediation, names a command that does not exist in this repo.** — severity: high

  There is **no `install.sh`** in this repo (verified: no `*.sh` at root; the `install.sh` in
  `README.md:39` is the hosted cargo-dist installer for the `yf` **binary**). Per `README.md`
  and `TESTING.md`, skills are **`rust-embed`-baked into `yf` at `cargo build` time** and
  deployed by `yf skills install`. Reinstalling against a stale binary would restore the **old
  baked skill**, failing SC12 even when Epic 3 is perfectly done — and silently regressing the
  operator's installed skill. C1 is not resolved; one wrong-copy error was substituted for
  another.

  Recommendation: SC12 → `cargo build` (re-bake) then `yf skills install yf-plan`, then diff; or
  drop install parity to a follow-on, since it depends on a binary release cycle this plan does
  not otherwise touch.

- **M1 — `Gate: Evidence corpus`'s Test cannot fail.** — severity: medium

  `ls … | wc -l | grep -qv '^0$'` — BSD `wc -l` emits `"       0"` with leading padding, which
  does not match `^0$`, so `grep -v` succeeds. Independently confirmed: against a nonexistent
  corpus the pipeline still exits 0. The gate's test passes unconditionally. Red-team's
  *existing* "Test commands valid?" item should have caught this in pass 1 — a data point
  against self-review.

  Recommendation: `test -d … && [ "$(ls …/plan.md 2>/dev/null | wc -l)" -gt 0 ]`.

- **M2 — Issue 2.5 has an ungated sibling-repo precondition.** — severity: medium

  2.5's fixtures need plan-013's **pre-fix** text, which is not in this plan's `findings/`
  (EXP-002 records as-landed remedies) — so 2.5 needs the `d3-pxe` checkout and plausibly its git
  history. `Gate: Evidence corpus` blocks 3.1 only, and 2.5 has no `depends-on: 3.1`. The gate's
  "discharged permanently … no later issue reaches outside the repo" is therefore **false**.
  This is exactly the #112/#113 defect class the plan exists to fix, present in the plan.

  Recommendation: extend `Blocks` to `3.1, 2.5`; state where the pre-fix text comes from, plus a
  fallback if history is unavailable.

- **M3 — EXP-001's headline figures no longer reproduce.** — severity: medium

  Re-run today: `current 40/53` (finding says 39), `F1 only 32/53` (31), `all four 13/53` (12).
  The delta is `plan-039` itself, which now appears in the survivor list. The corpus was scanned
  when this plan's `plan.md` was a stub — **the self-test case was never in the measured
  corpus**, which is why H1 went unnoticed.

  Recommendation: date/commit-stamp the figures, note the in-flight plan is now included, and
  re-run the corpus at Issue 3.1 rather than transcribing.

- **M4 — Epic 4 adds an enforced CI check with no SPEC amendment, and collides with 3.6.** — severity: medium

  Issue 4.1 introduces a new frontmatter guard wired into `CHANGE-VALIDATION.md` — a new enforced
  behavior — with no `REQ-*`, no amendment-log entry, and no `depends-on` on Epic 1, violating
  the repo's SPEC-first mandate. Separately 4.1 and 3.6 both edit `CHANGE-VALIDATION.md` with no
  ordering edge, while Epic 2 was deliberately serialized to avoid exactly that.

  Recommendation: scope 4.1 to the one-character repair (guard → follow-on with its own REQ), or
  add the REQ to Epic 1 and a `depends-on`; add an ordering edge between 4.1 and 3.6.

- **M5 — R9's re-measure checkpoint has no owner and cannot run inside this plan.** — severity: medium

  R9 is prose: no issue, no bead, no criterion, and it fires after this plan closes. It refers to
  "the plan-039 tracking issue", which does not exist and which no issue creates.

  Recommendation: file a deferred bead/issue carrying the plan-013 baseline (4 found, 1 escaped);
  name the tracking issue as a land-the-plane deliverable.

- **M6 — EXP-002 measures expressibility, not detectability.** — severity: medium

  "A prose-vs-DAG cross-check therefore has enough information to catch them" is an **inference**
  about LLM detection presented one line from `[measured]` rows. Whether a prompt bullet actually
  finds a missing `depends-on` in a 400-line plan is untested — a mild instance of the
  conflation #114 exists to prevent.

  Recommendation: same remedy as H3 (the 2.4 fixture converts it to a measurement); soften the
  wording to `[inferred]`.

- **L1 — SC1's `grep -c` can fail on correct work.** — severity: low
  `grep -c` counts lines; the spec's house style cross-references sibling REQs in Rationale lines
  (`spec/agents.md:90` cites "REQ-AGENT-043/045"). Recommendation: `grep -c '^REQ-AGENT-04[678]:'`.

- **L2 — `upstream-triage.md` has every Disposition and Notes field blank.** — severity: low
  Real dispositions live only in plan.md's table; a cold reader opening the triage artifact sees
  an untriaged plan. Recommendation: back-fill, or delete and let plan.md be the single source.

- **L3 — stale internal cross-references.** — severity: low
  R5 cites "Issue 4.2" (now 5.2a/5.2b); R1 says 2.5 replays "both" artifacts (there are three,
  four with H3); SC12 is listed before SC11. Recommendation: mechanical sweep.

- **L4 — `index.md` links non-existent directories.** — severity: low
  `diagrams/` and `assets/` do not exist; `references/upstream-133.md` exists though #133 is
  `exclude`. Recommendation: prune or create.

- **L5 — `Gate: Upstream write`'s Test does not test its Condition.** — severity: low
  Test proves auth, never that the operator read the drafts. Recommendation: add
  `test -s references/close-109.md && test -s references/rescope-113.md`.

## Missing

- **No criterion covers what Epic 2 actually buys.** SC2/SC3 are `grep`s for words in a prompt —
  they pass if the bullets are pasted in, whatever they say. SC7 is the only behavioral check and
  it omits 2.4 (H3). Nothing covers 2.1's investigator change beyond "the file contains the word
  `measured`".
- **No remedy path when a replay fixture does not flag.** Nothing says what happens on a miss —
  revise and re-run (unbounded), or record and proceed. Without a rule this becomes
  tune-until-green, the confirmation-bias failure C2 raised.
- **No pre-existing-FP audit.** Plans already carrying an operator-confirmed
  `deliverable_class: ci-release` accepted from a false-positive suggestion are not enumerated or
  re-checked. `complete-gate` is still armed on them.
- **`FP<=2` remains without principled basis** — R4 says so honestly, then 3.2 encodes `FP=2` as
  a hard harness expectation (H2). Pick one.

## Gate Assessment

Four gates, all declaring required fields. **Reachability:** both capability gates are reachable;
the `Gate: Upstream write` split is the plan's strongest self-application of REQ-AGENT-046.
**Test validity:** one gate test is broken (M1 — always exits 0, so it cannot detect the absent
corpus it exists to detect) and one is non-responsive to its condition (L5). The gate *structure*
is sound; the gate *instrumentation* is not. **Coverage:** one genuine capability precondition is
un-gated (M2 — Issue 2.5's `d3-pxe` dependency), which also falsifies the Evidence-corpus gate's
"discharged permanently" instruction. Applying the plan's own REQ-AGENT-047 to itself finds this;
pass-1 asserted no such gap exists.

## Upstream Assessment

Dispositions are sound and each is justified by a finding rather than by the issue's own framing.
#108 `include` — correct, and EXP-001 raises severity well above the report; all six issues carry
`resolves-upstream`. #113 `partial` — the strongest judgment in the plan: expensive branch
declined on evidence, issue stays open, 5.2b comments without closing (REQ-AGENT-031) — **but**
the shipped half (2.4) has no evidence it works (H3), so `rescope-113.md` would announce a check
never observed to fire. Land H3 before 5.2b. #114 and #112 `include` — faithful to the issues;
EXP-002 independently supports the red-team placement. #109 `supersede` — defensible, with the
mechanism/symptom split preserved in the comment text rather than the close reason. #133
`exclude` — right.

Gaps: `upstream-triage.md` records none of this (L2), and the coarse plan-level tracking issue
the repo convention requires — which R9 depends on — is not a deliverable of any issue (M5).

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | `\brelease` matches inside `ci-release`; SC6 falsified | high | Confirmed independently. The operator-chosen term-of-art guard was **measured and did not work** — this plan still flagged, on Issue 3.4's own stop-rule prose. Adopted instead: new **Issue 3.4b (F5)** — strip code spans and fenced blocks, a structural fix measured to cut plan-039 5 signals → 1 and to help across the corpus — and **SC6 restated** to assert `evidence: prose-only` rather than `standard`. The **self-reference class** is recorded in 3.4b as a structural limit of prose keyword matching | resolved |
| H2 | 3.2's harness expectation is cumulative, not per-step | high | Re-measured in the plan's actual implementation order and replaced with a **per-step table** (F3 alone: `FP=8`, corpus 22/53). Harness now asserts **invariants** (`FN=0`, `FP` non-increasing) at every step, exact tuple only after 3.5, and re-derives corpus counts rather than transcribing them | resolved |
| H3 | No fixture for REQ-AGENT-047 (2.4), the #113-partial deliverable | high | Added a fourth fixture `replay-plan-013-epic6.md` (plan-013's pre-fix Epic 6, no `depends-on` on Epics 1–5) targeting 2.4 specifically; SC7 raised to 4 flags; **5.2b now `depends-on: 2.5`** so #113 is never told the check shipped before it was observed to fire | resolved |
| H4 | SC12 names a nonexistent `install.sh`; skills are rust-embed baked | high | Verified: no `*.sh` at repo root. Install parity **removed from scope** and filed as a follow-on bead by Issue 5.3, with the reason (a `cargo build` + redeploy cycle this plan does not touch) recorded under Success Criteria. SC12 reused for the tracking-issue/bead deliverable | resolved |
| M1 | `Gate: Evidence corpus` test always exits 0 | medium | Verified (BSD `wc -l` pads). Replaced with `test -d … && [ "$(ls … \| wc -l)" -gt 0 ]` | resolved |
| M2 | Issue 2.5's `d3-pxe` precondition is un-gated | medium | Gate `Blocks` extended to `3.1, 2.5`; the false "discharged permanently" claim corrected to "no **CI run** reaches outside the repo"; 2.5 now states its pre-fix text source (d3-pxe `reviews/`, then `git log -p`) and a reconstruct-from-#112/#113 fallback | resolved |
| M3 | EXP-001 figures drifted; plan-039 was not in the measured corpus | medium | Figures updated to 40/53 and date-stamped; Motivation and Investigation Findings note the count moves as plans are added, including this one; the harness re-derives rather than transcribes | resolved |
| M4 | Epic 4 guard has no REQ (SPEC-first) and collides with 3.6 | medium | Split: **4.1** is the one-character repair only (no new behavior, no REQ owed); **4.2** is the guard, with its REQ added to Issue 1.2's scope and `depends-on: 4.1, 1.2, 3.6` — the ordering edge against 3.6's `CHANGE-VALIDATION.md` edit | resolved |
| M5 | R9's re-measure checkpoint has no owner | medium | New **Issue 5.3** files the coarse tracking issue plus deferred beads for the re-measure (carrying the plan-013 baseline: 4 found, 1 escaped) and install parity. R9's mitigation now points at the bead, not at prose. Covered by SC12 | resolved |
| M6 | EXP-002 measures expressibility, states detectability | medium | Converted from inference to measurement by H3's `epic6` fixture — the cross-check must be *observed* finding the missing `depends-on`, not assumed to | resolved |
| L1 | SC1's `grep -c` can fail on correct work | low | Anchored to `'^REQ-AGENT-04[678]:'`, with the reason recorded inline | resolved |
| L2 | `upstream-triage.md` dispositions blank | low | All six dispositions and notes back-filled to match plan.md's table | resolved |
| L3 | Stale internal cross-references | low | Swept: R5 → 5.2a/5.2b, R1 → four fixtures, SC order corrected, EXP-001 bullets updated | resolved |
| L4 | `index.md` links non-existent dirs | low | `diagrams/` and `assets/` were empty (hence untracked by git and invisible to a cold reader); added `.gitkeep` to both. Corrected the `references/` description — it holds all rows, including excluded #133 | resolved |
| L5 | `Gate: Upstream write` test does not test its condition | low | Test extended with `test -s references/close-109.md && test -s references/rescope-113.md` | resolved |

**Final status:** all 15 concerns resolved. Pass 2 frozen.

**Note on process.** H1's resolution changed the operator's earlier decision because the chosen
fix was measured and found not to work. That is the plan's own thesis applied to itself: the
term-of-art guard was a plausible inference, and one command falsified it.
