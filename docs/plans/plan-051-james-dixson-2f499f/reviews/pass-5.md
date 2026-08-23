---
type: Review
okf_spec: OKF-PLAN
id: pass-5
status: complete
---

# Red-team pass 5

## Verdict: APPROVE

Fifth independent pass, against `0908703`. **The streak breaks.** For the first time in five passes,
no blocking defect was found inside the previous pass's fix — all four of pass-4's resolutions verify
by execution and hold. One medium concern and four lows remain, all resolved below; **none blocks an
executor**, and the medium reaches back two rounds rather than one, which is a different and better
failure mode than the streak.

## Strengths

- **SC4b verified end to end, and it can now FAIL — constructed and confirmed.** The relocated command
  returns **exactly 7 paths, exit 0**, matching pass 4. Adding a tracked file carrying the phrase
  makes the hit set 8, one without a row — it fails. And post-fix the hit set is still **5 paths**
  (the captor sentences), so the **non-empty vacuity guard is satisfiable**. Neither unfalsifiable nor
  unpassable.
- **`ctl-182-spike` re-spiked under pass-4's new rules — 1 / 1 / 0 / 1 across four arms**, including
  the half-fix arm (agents reworded, spec still prose) → `pairs-found=0`, exit 1. **Arms 2 and 3 are
  SC3's two arms; SC3 is discharged as written.**
- **Both new guards fire.** A literal containing `"` → `pairs-found=1 expected=2` → **exit 2
  INCONCLUSIVE**, correctly routed to "repair the instrument". `pairs-found=0` → exit 1, never a
  vacuous pass.
- **The self-check caught the reviewer for the third consecutive pass** — its own arm-3 rewording used
  capital-`R` prose against a lowercase literal, producing `failed=1` on a genuinely fixed tree. 1.1's
  hand-fixed-copy assertion is exactly the guard for it.
- **C37 clean.** `:97` survives at three sites, all factual or inside the `NOT :97` carve-out. Grepped
  the whole plan: **only 0.1 is ever claimed to write a `Verification:` line.**
- **Zero stale citations, fifth pass running.** All re-verified at this commit, including
  `workflows.md:179` = reviewer row and `:180` = red-team row.
- **SC6 verified by running it** — section-scoped exits 1 pre-fix; whole-file `grep -c` → **3**,
  including the frontmatter `allowed-tools:` entry. The section-scoping requirement is real.
- **D-9 confirmed at source** — `DRIFT-CHECK.md` has an `agent` node and `skills/*/agents/*.md` in §6
  trigger scope, but the only agent edge is `e-agent-ref` (path-resolves). **No `spec → agent` edge.**
- All four mechanical checks green; all 11 upstream issues re-verified OPEN; #182's body carries
  SC13b's required quote verbatim.

## Concerns

| Concern | Severity | Resolution |
| :-- | :-- | :-- |
| **C41 — 0.1's mandated `Verification:` shape cannot satisfy 3.2's meta-assertion, and 3.2 is forbidden to fix it.** 0.1 fixes one shape (a greps-only command) and says *"Nothing else may rewrite those lines"*; 3.2 then requires each line to **name this test**, and SC9 discharges non-rottability by deleting the test and asserting the meta-assertion fails. A greps-only line names no test — so an executor reaches 3.2 with an unsatisfiable requirement whose only repair is rewriting a line 0.1 owns. **This is pass-2 C22's residue**: C22 reconciled Epic 1's conjunct (b) with Epic 3's *executability*, never with its *meta-assertion* | **med** | **Fixed in 0.1** — the command's **first conjunct must invoke Epic 3's pytest**, e.g. `` `uv run …<test>.py && grep -qF "<lit>" <path> && grep -qF "<lit>" <path>` ``. Verified compatible: no double quote introduced (C38's guard unaffected), `pairs-found` still equals the `grep -qF` count, the line stays a whole-line backticked command exiting 0 (SC8/3.1), **and it now names the test** (3.2, SC9). Stated in 0.1 so 3.2 never touches the line |
| C42 — **1.2 did not tell the executor to add the two NO-EDIT rows SC4b requires.** `agents/captor.md` and `spec/portability.md` were named only in SC4b's commentary; without those rows the post-fix hit set is not a subset and SC4b fails | low | **Fixed** — both added to 1.2's no-edit clause with the reason (they carry the **captor's** rule, REQ-AGENT-061, out of scope for #182) |
| C43 — **SC4b compared a path set against a site set.** Its command emits paths; 1.2 writes `file:line` rows, so a literal subset check is a type mismatch | low | **Fixed** — "subset of the **paths named by** that file's rows", with the blind spot stated: it catches a new unenumerated **file**, never a new unenumerated **line** in an enumerated file |
| C44 — **SC4b's coverage claim was overclaimed.** It said it closed `skills/yf-plan/SPEC.md:65/389-390`, `glossary.md:90` and `web/content/skills/yf-plan.md:34` — measured, those carry *"Both agents are read-only"* and no form of *"never writes files"*, so they are **not** in the hit set | low | **Fixed** — trimmed to the two paths the pattern actually reaches; the other three are stated as remaining hand-enumerated under R1 rather than presented as closed |
| C45 — **SC7's description clause is not observable from the instrument it names.** `bd cook --dry-run` emits only `step-id: Title (type)` and carries no description field | low | **Fixed** — the clause now reads from `plan-review.formula.toml` directly, with the reason recorded |

## Missing

Nothing blocking. C41 was the last live seam between two epics; C42-C45 are one-clause prose
corrections that change no command, no gate, and no DAG edge.

**Worth recording: the four-pass pattern of "the defect is inside the previous fix" did not repeat.**
Pass-4's four fixes were each verified by execution and each holds. The one medium reaches back two
rounds — to a fix passes 3 and 4 both read past — which is a different failure mode than the streak
and a better one.

## Gate Assessment

**Reachable, satisfiable, and correctly placed — verified by execution, not inspection.** Producers
`1.1/2.1/3.1` (`record-red`) and `1.2a/2.2/3.3` (`assert-distinguishes`); Blocks `{1.4, 2.4, 3.4}`;
**no producer inside the Blocks set**, no cycle. Satisfiability now measured for the second
consecutive pass, and the DAG (`1.1 ← 0.2 ← 0.1`) guarantees 1.1 records its RED against the post-0.1
tree — confirmed as a non-vacuous `pairs-found=2 failed=2`, not the degenerate `pairs-found=0`. **All
three exit codes reachable**: 1 (arms 1/2/4), 0 (arm 3), 2 (the quote guard). Count derivation sound
against a 3-line manifest. Upstream-write is correctly `human` with its grant produced outside its own
Blocks set; the Reconcile gate's predicate is well formed. No gate sits later than its evidence
requires.

## Upstream Assessment

**Sound on re-verification.** All 11 issues OPEN with titles matching verbatim. #165 genuinely
one-plan-scoped, with 0.3 recording the census **with its pathspec** — the right resolution of the
251-vs-257 delta, shipping a reproducible figure rather than picking a winner. #173/#174 each name the
sub-case closed and state the general case stays open. #150 claims two ranked classes, not the
research. #149 comment-only with the corrected premise. #177 still OPEN, so `exclude` is honest.
4.2's arithmetic is right — 5 `partial` + 2 `include` closing comments, matching `_verify_row`'s
`requires_mention: True` for both, and it runs before `verify-reconcile` at 4.4. 4.3 routes the
tracker through `/yf-beads-upstream` so the epic carries an `external_ref`, made checkable by SC12b.
Both out-of-scope defects route to 4.6 with C31's caveat recorded.
