---
type: Review
okf_spec: OKF-PLAN
id: pass-4
description: "Red-team pass 4 — REVISE. Fourth recurrence: SC0 omits the one script it exists to guard, and is itself a guaranteed-green row that launders INCONCLUSIVE into PASS."
---

# Red-team pass 4: plan-056-james-dixson-473dba

## Verdict: REVISE

> **All 9 concerns resolved.** C32 and C33 changed the design: the backstop moved from a criterion to a
> capability gate, because a gate halts outside `recheck-criteria`'s verdict arithmetic and a criterion
> cannot. C36 required correcting a pass-3 resolution row that was false when written.

Four of five findings were produced by executing the plan's own machinery. **The vacuity recurred a
fourth time, inside the mitigation pass 3 commissioned for the third.**

## Strengths

- **34 issues, 21 criteria, zero dangling `depends-on`, zero cycles, zero backward cross-epic edges**,
  every issue named by >=1 criterion, every criterion naming an existing issue. Coverage is bidirectional.
- **C28 is genuinely fixed.** Re-deriving the instrument set mechanically from the Verification column
  yields exactly 10 instruments, and **every one has a creating issue** (1.8, 1.9, 3.1).
- `gate_consistency` PASS. `doc_lint` PASS. `ready-check` correctly blocks on pass 3's REVISE.
- **The split lost nothing.** plan-057 exists, carries all six findings verbatim, carries D-1..D-12 with
  original evidence, gates on plan-056 completion, and covers old Epics 4/5/6 as its 1/2/3. 34 + 25 = 59
  issues from a 54-issue predecessor.

## Concerns

### C32 — THE FOURTH RECURRENCE. SC0 omits the one script it exists to guard, and is itself a guaranteed-green row. [HIGH]

The criteria invoke **7** shell instruments. **SC0's `test -x` chain lists 6.** The omission is
`harness-selftest.sh` — the instrument for **SC35**, the RED-fixture control that exists specifically to
close pass 3's hole. Sandbox reproduction against the real engine:

```
SC0 holds · SC35 inconclusive (127) · SC2 holds
verdict: PASS — "all 2 evaluated criterion/criteria hold"
```

**Second, worse shape:** SC0 tests the x-bit, not runnability. Give the six listed scripts a bad shebang:

```
SC0 holds (0) · SC35 inconclusive (126) · SC2 inconclusive (126)
verdict: PASS — "all 1 evaluated criterion/criteria hold"
```

That is the sharp point. **SC0 always holds once the files exist, so it guarantees `evaluated >= 1`.**
Pass 3 named SC11b as the laundering step that converts `evaluated == 0 -> INCONCLUSIVE` into `PASS`.
SC0 does the same thing **by construction, on every run**. In the broken-shebang world, pre-SC0 the plan
reported INCONCLUSIVE exit 2 (visible); with SC0 it reports **PASS exit 0**. The backstop is a net
regression in that branch.

*Rec:* add `harness-selftest.sh` to SC0; make SC0 assert **runnability** (`bash -n`), not the x-bit; and
either exclude SC0 from the `evaluated` denominator or state plainly that it is a guaranteed-green row
and cannot be the backstop it is billed as.

### C33 — Issue 1.10's engine fix cannot protect plan-056's own close. [HIGH]

`SKILL.md:1655` runs `recheck-criteria` from `${SKILL_DIR}`, which resolves to the **installed** skill,
never the working tree — AGENTS.md states this and forbids `yf skills install` mid-execution, with
deploy at land-the-plane *after* validation. §6.4 **is** the validation. So Issue 1.10's
`harness_incomplete` fix lands in the repo copy and is **not in effect for this plan's own close-check**.
SC36 proves a pytest test passes in the repo; it does not prove the engine adjudicating this plan has the
fix. R13 presents SC0 and 1.10 as two layered defences; against *this plan* there is one, and C32 holes
it.

*Rec:* state this in R13/R11, and add a mechanism that does not route through `recheck-criteria` at all.

### C34 — The Motivation was not trimmed at the split; the Objective promises work no epic performs. [HIGH]

The plan asserts "What remains is exactly the Motivation". It is not — the Motivation is now strictly
larger than the plan:

- **Title and Objective** still read "…realign to the relocated upstream, and add a cross-repo
  `yf-okf-hygiene` skill", while the Approach says the plan "does not build the hygiene skill, and does
  not touch the OKF baseline." They contradict each other on the same page.
- **Motivation ¶4** — the entire baseline-relocation / unversioned-`v0.2` thread — is plan-057's item 3.
- **Motivation's closing sentence** promises both.

Separately: the *first* Motivation bullet is closed by documentation, not mechanism. D-1 retains
`STATUS_SEVERITY`'s `complete` demotion and no issue touches it, so after this plan **46 of 48 checks
remain structurally incapable of failing a completed bundle**. What ships is #246's amendment and SC9
freezing the erosion at 2/48. Defensible, but "makes the structure able to fail" over-claims.

*Rec:* rewrite Title, Objective, ¶4 and the closing sentence to the enforcement gap only; say what the
doc_lint half actually gets.

### C35 — Issue 4.3 omits #265, so SC26 is guaranteed FALSE at close. [HIGH]

`#265` is `include`, which `verify-reconcile` requires to end CLOSED. Live: `"#265 is OPEN; a include row
must be CLOSED"`. Issue 4.3 names #165, #171, #247, #233, #246, #140, #170 — **not #265**. It was added
by pass 3; 4.3 was rewritten at the split; the two edits did not meet.

### C36 — Split wreckage: five dangling references. [MEDIUM-HIGH]

| Location | Dangler |
| :-- | :-- |
| D-1 basis | "**Epic 5's** backfill flips `okf_native` … and **SC15c** bounds it" — both moved, and line 168 says the opposite |
| Approach spine 3 | "makes the **Epic 5** backfill's third step reachable" |
| SC1 | "Every **Epic 1-6** issue…" — and it is the criterion `check-req-coverage.py` is written against |
| D-17 / R12 | Both say "**33 issues**"; mechanically counted **34**. Fourth occurrence of the class R12 tracks |
| **M8's pass-3 resolution** | Claims "1088 files, 1642 findings, 392 demoted" are "now written into D-1's Basis cell". `grep`: **none of the three appears anywhere.** Recorded `resolved` and is not |

### C37 — The split moved four criteria to plan-057 without their creating issue. C28 verbatim, in the successor. [MEDIUM — high for plan-057]

All 8 of plan-057's instruments have **zero** creating issue, and 4 are new to that plan:
`check-index-boilerplate-ratio.py`, `check-baseline-pin-contract.sh`, `check-skill-classified.sh`,
`check-backfill-audit-delta.py`. **plan-057 has no analogue of Issue 1.9.** And its SC0 has the *same*
omission as plan-056's — `check-skill-classified.sh` is invoked by SC19b and absent from the chain.

### C38 — Upstream rows whose Notes and Disposition disagree after the split. [MEDIUM]

- **#140** — `deferred` (which `verify-reconcile` passes precisely because it requires no mention), yet
  the Notes say "Root-tier enforcement + drift model **IN**" — which is what Epic 3 ships. Delivered and
  recorded nowhere. Should be `partial` with 3.1/3.2.
- **#170** — `deferred`, but the Notes argue at length "**`partial`, not `include`**". Self-contradictory.
- **#189** — `deferred` with a non-empty `Resolved By: 1.9`.

### C39 — SC1 is a self-fulfilling definition. [MEDIUM]

SC1 says every Epic 1-6 issue "**names** the `REQ-*` it implements or is marked a bug fix". Read
literally, ~17 issues name none — they carry a `depends-on` to the Epic 0 issue that adds the REQ. And
`check-req-coverage.py`, written by Issue 1.9, will be written to whatever rule makes SC1 pass.

*Rec:* restate to the rule actually intended, so the script implements a criterion rather than defining one.

## Missing

- **No capability gate on the harness.** After a four-time recurrence, the frontloading move is a gate
  whose Condition is "the harness scripts exist and each returns non-zero on its RED fixture", blocking
  Epic 3. `harness-selftest.sh` is producible from Epic 1 alone; the gate sits later than its evidence
  requires — a frontloading miss.
- **SC35 has no non-vacuity floor.** The plan invented exactly the right pattern (`--min-roots N` on
  Issue 3.1's driver) and did not apply it to its own harness. A selftest checking 2 of 8 scripts is
  indistinguishable from one checking 8.
- **The plan's own `index.md` does not list `reviews/`, `findings/` or `references/`** — `reindex --check`
  reports `drift`, 3 missing. A cold reader cannot reach the four review passes from the index. The
  plan's own thesis, reproducing in its own bundle while under review.
- **`log.md` records no split entry.** A cold reader sees "review: plan v1 presented — 7 epics, 46
  issues" and no record of how it became 5 epics / 34 issues.
- **Issue 3.4's "9 drifting bundles" is a stale SET, not just a count.** Re-measured: still 9, but a
  different 9 — `docs/research/005-*` is now clean and **plan-057, created today by the split, is already
  drifting.** The producer defect reproduced in real time during this review cycle.

## Assessment of the plan's own admission

**SC35's residual-circularity admission is honest but incomplete, and the gap is exactly C32.** Both
clauses describing *existence* are false for the one script the sentence is about: SC0 does not
establish `harness-selftest.sh`'s existence, and existence is not the only failure mode — 126 defeats
`test -x` for all six. The residue is not "one script's behaviour is unverified"; it is "one script's
absence or unrunnability is invisible to the verdict, and the other six's unrunnability is too."

## Gate Assessment

`gate_consistency` PASS, 2 gates, 0 findings. Both sound. plan-057's four gates are also sound. The gap
is the **absent** harness gate, not a defective present one.

## Upstream Assessment

`verify-reconcile` fails 6 of 11 for the correct pre-execution reason. **#265 will still fail at close**
(C35). Three rows are internally inconsistent post-split (C38). #165's residual survives correctly as an
Issue 4.2 filing item.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C32 SC0 omits its own guard; guaranteed-green | high | Reproduced and accepted in full. SC0 now covers **all seven** shell instruments including `harness-selftest.sh`, and asserts **runnability via `bash -n`** rather than the x-bit, which closes the 126 branch. The deeper point — that SC0 always holds once the files exist and therefore guarantees `evaluated >= 1` — is now stated in SC0's own cell and in R13: **SC0 is a floor, not a backstop.** The actual backstop is the new capability gate. | `main-session` | `resolved` |
| C33 engine fix cannot reach this plan's close | high | Accepted; this is the finding that changed the design. A new **Capability Gate: Verification harness ready** (`Test: harness-selftest.sh --require 8`, `Blocks: epic:3`) is the one defence that reaches this plan, because a gate's Test is executed by the coordinator and halts on exit code, entirely outside `recheck-criteria`'s verdict arithmetic. R11 was raised low->med and now states plainly that Issue 1.10's engine fix is **inert for this plan's own close** — `${SKILL_DIR}` resolves to the installed skill, and installing mid-execution is forbidden. The successor plan inherits the fixed engine and does not have the gap. | `main-session` | `resolved` |
| C34 Objective/Motivation not trimmed at split | high | Title and Objective rewritten to the enforcement gap. Motivation ¶4 (the whole baseline-relocation thread) deleted — it is plan-057's. The closing sentence rewritten, and it now says explicitly what the doc_lint half actually gets: D-1 retains the `complete` demotion, so 46 of 48 checks remain incapable of failing a completed bundle, and what ships **freezes the erosion at 2 of 48** rather than reversing it. The over-claim was real and is now stated as a scope decision rather than papered over. | `main-session` | `resolved` |
| C35 4.3 omits #265; SC26 guaranteed FALSE | high | #265 added to Issue 4.3's close list. It was filed by pass 3 while 4.3 was being rewritten at the split, and the two edits did not meet — exactly the class the plan's own #173 exclusion was rationalised away as being a different axis. | `main-session` | `resolved` |
| C36 five dangling references incl. a false ledger entry | medium-high | All five fixed. D-1's Epic-5/SC15c note replaced (this plan now modifies no completed bundle on any axis); the Approach spine's Epic-5 reference re-aimed at the successor; SC1 rescoped to Epic 1-4; the 33/34 miscount corrected in both D-17 and R12. **And the false ledger row was corrected rather than quietly fixed:** pass-3's M8 resolution claimed figures were 'now written into D-1's Basis cell' when they were not — the row now carries `[CORRECTED at pass 4 — this row was FALSE when written.]`, and the measured 1088/1642/392 are genuinely in D-1 with their date. | `main-session` | `resolved` |
| C37 plan-057 harness unowned | medium | plan-057 gains Issue **1.0** owning its four additional harness scripts plus its selftest entry, under Issue 0.5's extension of `REQ-CLI-018`, with new SC0b as the RED-fixture control and its own harness capability gate. Its SC0 was rewritten to include `check-skill-classified.sh`, which had the identical omission this pass found in plan-056's. | `main-session` | `resolved` |
| C38 upstream rows self-contradictory | medium | #140 corrected `deferred` -> **`partial`** with `Resolved By: 3.1, 3.2, 4.3` — the row was passing `verify-reconcile` precisely because deferred rows require no mention, so root-tier enforcement would have shipped and been recorded nowhere. #170's note rewritten to match its `deferred` disposition (carried whole to plan-057, which owns both halves). #189's stray `Resolved By` cleared. | `main-session` | `resolved` |
| C39 SC1 self-fulfilling | medium | SC1 restated as the three-way rule actually intended — names a REQ, **or** `depends-on` an Epic 0 issue that adds one, **or** is marked a bug fix — with the measurement (~17 issues carry the dependency form) in the cell, so `check-req-coverage.py` implements a criterion rather than defining one. | `main-session` | `resolved` |
| M10 harness gate, SC35 floor, index drift, log entry, stale set | medium | Harness capability gate added (above). SC35 now requires `--require 8`, applying the `--min-roots` non-vacuity pattern the plan invented for Issue 3.1 and had not applied to itself. Issue 3.4 rewritten to name the **enumeration** rather than a count, recording that the drifting set moved during this review cycle and that **plan-057, created hours earlier by this plan's own split, is already drifting** — the producer defect reproducing in real time. Both bundles' `index.md` repaired by hand with real descriptions (not `reindex --write`'s bare bullets, per R4); both now report `clean`. `log.md` backfilled with the split, the pass-4 entry, and the #265 filing. | `main-session` | `resolved` |
