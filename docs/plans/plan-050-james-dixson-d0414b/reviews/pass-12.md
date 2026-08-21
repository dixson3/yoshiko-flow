---
type: Review
okf_spec: OKF-PLAN
id: pass-12
status: complete
---

# Red-team pass 12

## Verdict: REVISE

Tenth independent pass (cycle 12 of 12 — the declared bound), against `f8b0da1`. Every pass-11
resolution was verified **by execution** in a sandbox clone. **Eleven of twelve hold exactly as
claimed and were reproduced.** One fix — C119's — injected a defect that made the capability gate
unsatisfiable as literally specified, by a genuinely new mechanism: the remedy was a **derivation
rule**, and the plan text specifying that rule is itself inside the corpus the rule scans. All five
concerns resolved below; none deferred.

## Strengths

- **Issue 7.2 was BUILT and it works, at both sites.** Applying `raw[m.start(2):m.end(2)]` (epic
  name) and `raw[m.start("rest"):m.end("rest")]` (issue title) to a synthetic plan: before,
  `'Fix               masking'`; after, the code span restored verbatim. C116's two-site claim, its
  group references, and `raw`'s scope at each are all exactly right.
- **SC22 holds under the prescribed fix, measured in isolation.** An issue whose title carries a
  `depends-on:` inside a code span still yields `depends_on: []`, `unparsed: []`, exit 0 — parsing
  keeps the masked `ln`, exactly as 7.2 requires. The fix does not trade one silent corruption for
  another.
- **SC24's figures reproduce to the digit**: 34 titles, **27** corrupted; 35 continuation bullets,
  **0** carrying prose.
- **SC7's baseline reproduces exactly at 757** while the unfiltered figure drifted again
  (829 → **830**) inside this session — the self-exclusion is doing real work, for the third
  consecutive pass.
- **C106's corrected annotation is right**, verified against `d40e1a3^`: SC11/SC12 were Epic 4's,
  SC13/SC14 Epic 5's. The correction I made after writing it wrong holds.
- **C120's claim verified against live code** rather than prose — `plan_manager.py:4047`'s own
  comment states the plan document is type-FORCED so it stays checkable wherever the bundle lives.
- **Mechanically clean**: 28 issues, 41 edges, `unparsed: []`, no cycles; `doc_lint` over all 72
  bundle files → 0 `E`-severity, with `index.md`/`log.md` correctly `files_checked: 0`; portability
  audit zero findings; FAST tier green on all four rows.
- **8 of 9 line citations resolve exactly** — `_verify_row` at `plan_manager.py:2012`,
  `UPSTREAM_DISPOSITIONS` at `:3911`, `SKILL.md:1440`, `test_doc_lint.py:713-715` and `:722-743`
  (boundaries exact), `CHANGE-VALIDATION.md:224`, `plan_extract.py:142`, `red-team.md:63`.
- All four satellite corrections from pass 11 verified in place (C113, C114, C115, C121).

## Concerns

| Concern | Severity | Resolution |
| :-- | :-- | :-- |
| C123 — **C119's fix made the capability gate permanently unsatisfiable.** 0.2 specified the manifest-count assertion as "derived by grepping `plan.md` for `ctl-[a-z0-9-]*` ids". Measured: that returns **7**, not 6 — Issue 0.2's own text contains the literal pattern, from which `grep -o` extracts the bare prefix `ctl-`. `verify-all` would compare 6 manifest lines against 7, exit 1, and block 1.4/2.4/3.4/7.4 while the gate's Instructions send the executor hunting a record that does not exist | high | **Fixed.** The **anchored** form is now stated verbatim in 0.2 — `grep -oE 'ctl-[0-9]{3}-[a-z-]+' plan.md \| sort -u \| wc -l` → **6**, re-measured after the edit, with `neg-179-open-wrapper` still correctly excluded. The failure mode is recorded in the issue itself, since an executor copies whatever the issue prints |
| C124 — **the `REQ-DATA-024` amendment C117 added has three live restatements outside `spec/data.md`**, and 0.1 amended only the spec: `_shared/doc_lint.py:17`, its vendored copy, and `_shared/document_types/README.md:52`. `DRIFT-CHECK.md:184`'s fixed-authority `e-doclint-spec` edge names **the engine's own module banner** explicitly | med | **Fixed.** All three named in 0.1 as moving with the amendment; 2.2's Named surfaces now call out the banner at `:17` in both copies **and** add `_shared/document_types/README.md`, which was a surface of no issue. Verified by `grep -rn` that these are the only three restatements outside test fixtures |
| C125 — **the amendment had no discharging criterion.** SC1's Verification is an enumerated list of six NEW ids and names no amendment, so 0.1 could close with it silently skipped and SC1 still pass — an obligation added at cycle 11 with nothing scoring it, in the plan whose thesis is that an unexecuted rule is a null change | med | **Fixed.** SC1's Verification extended to require the amendment **and its three out-of-spec restatements** in the same SPEC commit. The enumerated count stays **six**, since an amendment adds no id |
| C126 — stale line citation: 0.1 cited `spec/data.md:181-184` for the "binary at every binding point" sentence; measured at **187**, with 181-184 being the plan-049 `R`-severity note. Ninth appearance of the stale-citation class, injected by the same cycle-11 edit as C123/C124/C125 | low | **Fixed** to `skills/yf-plan/spec/data.md:185-188` — and the path corrected too, which the concern did not flag: the bare `spec/data.md` does not resolve from the repo root |
| C127 — `context.md` was internally inconsistent about the descoped M9 material: one bullet correctly said the stamping change left with plan-051, while the portability bullet still listed "26 `discovered-from` edges, 0 attributed" among measurements this plan fixes expectations against | low | **Fixed.** The clause is removed from the measurement list and recorded as plan-051's |

## Missing

- Nothing structurally absent. Every issue has a producer and a discharging criterion
  (plan-relations clean in both directions), every gate Condition is reachable, and the portability
  audit is clean.
- The one real coverage gap found was C125's — an added obligation with no criterion. That was a gap
  in *verification*, not in *work*: 0.1's text was already explicit enough to execute.

## Gate Assessment

Structurally sound, and now satisfiable. `Blocks: {1.4, 2.4, 3.4, 7.4}`; every named producer is a
`depends-on` ancestor of a blocked issue, none sits inside `Blocks`, verified across all 41 edges —
no cycle, and the gate is frontloaded to the earliest legal position. The 0/1/2 contract and the
honest "no engine executes this `Test`" disclosure remain intact. C123's defect was confined to one
clause of the `verify-all` count assertion and left the reachability argument untouched; the
anchored pattern is now measured, not asserted. Upstream-write and Reconcile gates unchanged.

## Upstream Assessment

Unchanged and still the strongest part of the bundle. Disposition counts re-walked against the live
table: 6 `include` / 4 `partial` / 4 `deferred` / 2 `exclude`, plus the one `tracker` row 6.3 adds —
matching SC10's "five of the six are REAL rows, only `supersede` is synthetic". `#183`'s exclusion is
correctly argued on `_TRACKER_ROW_RE.search()`'s first-match behaviour. Nothing in this pass touches
the reconcile path.

## The mechanism, round nine

Two distinct failures this round, and only one is the familiar class.

**The familiar one:** pass 11 named the countermeasure — *when a fix changes what an issue CLAIMS,
grep the bundle for the claim's own words* — and then did not apply it to its own C117. The claim
`binary at every binding point` is restated in three files **outside the bundle**, and the drift edge
that would catch it names one of them by description. The countermeasure was scoped to the bundle;
the claim was not.

**The new one, and it is worth naming precisely:** C119's remedy was a **derivation rule**, and the
plan text that specifies the rule is itself inside the corpus the rule scans. Writing the pattern
into the issue changed what the pattern matches. This is not "the fix injected a defect elsewhere" —
it is *the fix invalidating itself by being written down*.

The generalisation: **a derivation whose input includes the document that specifies it must be RUN
against that document before it is trusted.** C123 was found in one command. Reading the prescribed
grep would never have found it; running it once always would.
