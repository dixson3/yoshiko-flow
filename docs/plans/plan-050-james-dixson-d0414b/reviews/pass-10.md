---
type: Review
okf_spec: OKF-PLAN
id: pass-10
status: complete
---

# Red-team pass 10

## Verdict: REVISE

Eighth independent pass, first against the classifier redesign and Epic 7. **Five execution-blocking
concerns; four of the five were injected by this round's two unreviewed changes.**

## Strengths

- **The classifier's central claim is TRUE for Issue 2.2, and the reviewer built it to check.**
  `uv run _shared/test_doc_lint.py` → **148 `ok`, `all passed`, zero edits to that file**; FAST tier
  → `doclint pass`, `doclint-tests pass`, `uv-_shared pass`. **The first #181 scope in four attempts
  that survives contact with the suite.**
- **All four arms reachable and distinct**, including `--root <bundle copied to mktemp -d>` →
  `not-selected` where the *lint* over the same root returns the byte-identical
  `{"verdict":"PASS","files_checked":0}`. #181's titled scenario is genuinely reached.
- **SC22 is a real guard.** The reviewer reproduced #186/#187 exactly, then built 7.2 both ways: the
  offset-slice form restores titles verbatim **and** keeps a code-span `depends-on: 9.9` from
  becoming an edge; the naive `ln = raw` form **produces a spurious edge to a nonexistent target and
  drives `--strict` non-zero**. SC22 catches the exact way 7.2 could go wrong.
- Structural hygiene: 0 unparsed, 0 dangling, 0 cycles over 41 edges; audit **zero findings**;
  `Discharged-by` sound both directions; every line citation live; the 757 baseline reproduces
  (unfiltered now **828**, drifted from 820 exactly as 0.2a predicted).

## Concerns

| Concern | Sev | Detail | Resolution |
| :-- | :-- | :-- | :-- |
| C92 | **high, blocking** | **The design's central claim is false at the epic level.** `test_doc_lint.py:713-715` asserts against `DOC-LINT.md`'s **prose**, requiring the literal strings `files_checked` and `not-a-typed-document` — both live only in the section 2.2a replaces. Measured: rewriting the rule drives `doclint-tests` non-zero, and `CHANGE-VALIDATION.md:224` maps `protocols/*.md` → `doclint-tests`, so **the FAST gate fails the moment 2.2a saves the file** | Claim restated as scoped to 2.2 and **false for 2.2a**; 2.2a now explicitly must update the SC17 rule-text assertion to pin the new contract. Keeping the literal string to satisfy a text match is named as gaming the assertion |
| C93 | **high, blocking** | **`controls.txt` still enumerated four ids, so the gate could not see Epic 7.** 0.2 is its sole writer; 7.1 named `ctl-186`/`ctl-187` but never added them. The gate's `Test` enumerates from the manifest — so it returns 0 with Epic 7 unobserved while the Condition, SC2 and SC2b all say "and 7". The inverse of the defect 0.2 itself warns about | Six ids named verbatim in 0.2; `verify-all` additionally asserts the manifest's line count equals the declared red→green control count, so a future scope change that forgets it fails loudly |
| C94 | **high, blocking** | **0.1 and SC1 still demanded a REQ for "two new verdicts" the redesign deleted.** `classify` emits a `class`, not a verdict, so the stated REQ-DATA-024 breach does not occur — and landing a REQ describing verdicts no engine implements is a self-inflicted FAIL on `DRIFT-CHECK.md`'s fixed-authority `e-doclint-spec`. SC1 required a REQ no issue would write | 0.1's third id rewritten to the `classify` mode; the REQ-DATA-024 amendment **dropped** with its real reason recorded |
| C95 | **high, blocking** | **Epic 7 landed two behaviour changes with no `REQ-*`**, violating the Approach's own ordering constraint #1 and AGENTS.md's SPEC-first rule. 7.3 adds a field to the per-issue **schema** — exactly what `REQ-DATA-*` governs | Two `REQ-DATA-*` added to 0.1 (title fidelity; the `detail` field's derivation); SC1 extended four → **six** ids |
| C96 | **high, blocking** | **The silent-green fix manufactured a new silent green.** An empty selected `plan.md` is today a loud **FAIL, 6 E-severity findings, exit 1** — measured. Under "lint only on `class: selected`" it becomes a skip. `not-selected` and `no-such-path` are genuinely "linting this is meaningless"; **`empty` is not** — it is a document that fails its schema, and the schema already says so | `empty` moved to the **lintable** side (exit 0), keeping its diagnostic class without skip semantics |
| C97 | med | Branching on the **exit code** collapses the three non-`selected` classes, reinstating #181's conflation one layer up — a typo'd path treated identically to a reserved `index.md` | Callers branch on **`class`**; `no-such-path` is reported as a caller **bug**, not skipped |
| C98 | med | Epic 7 named no surfaces, while 2.2 does. `plan_extract.py` is a canonical/vendored pair and `sync.py --check` is in FAST, so editing either alone fails the on-edit gate | "Named surfaces" clause added to 7.2 and 7.3 |
| C99 | med | **My #187 relevance claim was false.** plan.md and the triage note both said "every correction nine passes bought lives in the continuation bullets". Measured: **35 bullets, 0 carrying prose** — `detail` would be empty for all 28 issues. SC24's detail arm could not fail | Corrected to "load-bearing for the CORPUS, not this plan"; SC24 restated as a **title** delta with the measured 27-of-34 expectation, and the detail arm's expected value stated as **zero — a valid negative observation**, not a pass by default |
| C100 | med | Title, Objective, Approach, R3 and index.md still said "four fixes (#178-#181)" after two more `include` rows landed. R3 is the **scope-creep risk row**, false in the document that just crept | All updated to six; **D-10** added recording the widening with the test applied (same defect class, already measured upstream, reachable by machinery the plan already builds). D-9's text left intact as the historical record |
| C101 | med | `log.md` recorded neither change, and its newest substantive entry still named the `--require-selection` flag as adopted — a cold reader takes newest-first as current state and gets the superseded design | Two drafting entries added; the pass-9 line annotated **SUPERSEDED** |
| C102 | med | **2.1's fixture drove no `selected` arm.** Two of its four "arms" return the same class, and none returns `selected` — so the gate's own fixture would be satisfied by a classifier that never returns 0, i.e. one that skips linting everything: **#181 made total** | Fixture now drives **five scenarios across four distinct classes**, with the `selected`/exit-0 positive arm **mandatory** |
| C104 | low | 2.2a's scope omitted `DOC-LINT.md`'s "Exit contract" section, leaving the protocol self-contradictory about what `1` means once `classify` adds a second `0/1/2` vocabulary | Named in 2.2a; both vocabularies must be stated, keyed by mode |
| C107 | low | "capture the title from `raw`" does not say **how**, and the two implementations differ: only offset-slicing is guaranteed by the length-preserving mask, and only it keeps SC22 holding | Offset-slice form named, with the reason and the requirement that matching continues against the masked `ln` |
| C110 | low | 2.2a stales `protocols/manifest.json`'s DOC-LINT.md sha256, and `sync.py --check` does not catch it | "re-run `manifest_update.py`" added to 2.2a |

Deferred as non-blocking and recorded here rather than silently dropped: **C103** (#181's `--root`
documentation half has no scheduled issue — either add one or downgrade #181 to `partial`),
**C105** (#181's `Resolved By` says `2.2` while its Notes say `2.2` **plus** `2.2a`), **C106** (the
SC11-SC14 gap wants the same annotation the epic gap has), **C108** (§5.2a's `_shared/` path does
not resolve in an installed skill), **C109** (D-5's re-measure range should extend to #187).

## Missing (all now closed)

REQ ids for Epic 7; Epic 7 entries in `controls.txt`; `log.md` entries for both changes; the
`selected`/exit-0 arm in the gate's fixture; named surfaces for Epic 7.

## Gate Assessment

Reachability **clean and mechanically verified** — `Blocks: {1.4, 2.4, 3.4, 7.4}`, every Condition
producer an ancestor of a blocked issue, none inside `Blocks`, no cycle over 41 edges, correctly
frontloaded. **But its `Test` enumerates from `controls.txt`, which pinned four ids — so the
Condition prose and the executable disagreed, and the executable wins** (C93). Upstream-write and
Reconcile gates fine; the Reconcile predicate's `length > 0` guard blocks the vacuous pass.

## Upstream Assessment

"The strongest part of the bundle." Every row walked against `_verify_row`'s branches: 6 `include`,
4 `partial` (all four attached to 6.2, pass-7 C71 correctly closed), 4 `deferred` (correctly relying
on plan-048's D-7 amendment), 2 `exclude` (pre-filtered), 1 `tracker` (`inconclusive` by
construction, which SC17 accounts for). #186/#187 references complete and untruncated. The one
factual error was the triage note's relevance claim (C99).

## The mechanism worth naming

Four of five blockers were injected by this round, and by a **new** mechanism — not the previous
rounds' "the fix collides with an assertion", but: **both changes edited the leaf without walking
back up to the artifacts that enumerate over it** — `controls.txt` in 0.2, the REQ list in 0.1, SC1,
and the Objective/Approach/R3/index.md scope statements. The reviewer's proposed countermeasure,
recorded for the next scope change: *for each newly added issue, does it appear in the gate's
manifest, in 0.1's REQ enumeration, in an SC, and in the Objective's count?*
