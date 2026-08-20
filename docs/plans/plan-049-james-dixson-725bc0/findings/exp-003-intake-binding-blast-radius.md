---
type: Finding
okf_spec: OKF-PLAN
id: exp-003
status: complete
---
# EXP-003 — Is a fail-closed `_audit_plan` binding safe to land today?

**Question:** Verify — do not inherit — plan-048's claim that findings conform by construction, and
re-measure whether a fail-closed intake binding still wedges.

## Approach Tested

All by execution. Scratch roots each with a real `docs/plans/` root (path-keying respected — a
bundle outside such a root selects zero files and silent-greens). Copied 6 bundles, forced
`status: review` in **both** frontmatter and the `**Status:**` line, ran `doc_lint --root`. Re-ran
for plan-047 and plan-048 reconstructed **at their own INTAKE commits** via `git archive`. Ran a
fresh `init` through five states. Diffed installed vs repo `investigator.md` and both against
`finding.toml`. Used `git merge-base --is-ancestor` to order the prompt rewrite against the findings
it supposedly governs.

## Result

**1. Per-bundle errors at `status: review`**

| Bundle | errors | breakdown |
| :-- | --: | :-- |
| plan-001 | 43 | R1b×27, risk-ids×11, frontmatter, table-columns … |
| plan-002 | 15 | R1b×8, R2c, … |
| plan-003 | 12 | risk-ids×6, … |
| **plan-047** | **0** | — |
| **plan-048** | **4** | R1b×4 |
| **plan-049** | **3** | R2b×3 — `#140/#149/#135: disposition include but Resolved By names no issue` |

**measured:** 6-bundle sweep `exit=1 FAIL files=100 errors=77`. At their own intake commits:
plan-047 @ `4cedb40` → **1 error**; plan-048 @ `12fe37d` → **4**, the same R1b×4.

**2. plan-047's historical 11 reproduce exactly — but at `R`, not `E`.**

- **measured:** `--type finding` over the review-forced corpus → `exit=0 PASS, errors=0,
  report_only=13`, of which plan-047 contributes the **identical 11**.
- **inferred:** plan-047 passes today **solely because plan-048 Issue 2.9 demoted the two checks
  `E → R`** — not because any file was fixed. Corroborated: the offending files are byte-identical,
  and `R` is exempt from promotion.

**3. plan-048's SC6 claim is FALSE as stated.** *"A copy of a real completed bundle at `review`
produces zero error-severity findings"* holds for **plan-047 only**. 5 of 6 produce 3–43 errors.

**4. "Findings conform by construction" is UNVERIFIED (n=0), not verified.**

- **measured:** `investigator.md` last changed in `e1c3102` (16:33:20). plan-048's six findings were
  committed in `12fe37d` (15:50:43); `git merge-base --is-ancestor 12fe37d e1c3102` → **YES**.
- **measured:** plan-049's `findings/` was **empty** at measurement time.
- **measured:** live corpus — 129 finding files, **117** violate `required-sections`, **122**
  violate `epistemic-marker`.
- **inferred:** **not one finding in the corpus was written under the new contract.** plan-048's
  6/6 clean findings **predate the prompt rewrite**, so they are evidence about the *old* prompt.

**5. Fresh-plan results.** `init` as-created → 0 errors. Forced `review`, template untouched →
**1 E `motivation-filled`**. Motivation filled → 0. Plus a conforming finding → 0. Plus a
plan-047-shaped non-conforming finding → **0 E, 2 R**. Plus a headingless finding → **1 E
`has-heading`**.

- **inferred:** a badly-shaped agent finding **cannot** fail intake; only one with no heading at all.

**6. `investigator.md` ↔ `finding.toml` now AGREE, string for string.** Installed and repo copies
byte-identical; sections, order, and the epistemic-marker regex all match exactly. plan-048's
EXP-004 mismatch is closed. Two nits: `finding.toml`'s comment cites a `## Output` heading that does
not exist, and `sections()` **skips fenced code**, so a finding pasting the template inside a fence
scores zero sections.

**7. The three `_audit_plan` call sites** (definition at `plan_manager.py:3999`)

| Site | Binding | Exit | Blast radius |
| :-- | :-- | :-- | :-- |
| `:4319` `audit` | **FAIL-CLOSED** | **1** | Phase-3 APPROVE; halts intake |
| `:4468` `audit_close` | **ADVISORY by construction** — exits 0 unconditionally | **0** | `set complete` never blocks |
| `:4860` `_ready_check_result` | **FAIL-CLOSED** | **3** | the Phase-3 gate and the approval re-check |

Sites 1 and 3 are the same verdict twice; a binding at `_audit_plan` lands at both. Site 2 is
structurally immune.

## Implications for Plan

- **The findings axis is no longer the blocker** — but what changed is **severity, not content**.
  The gate-precedes-its-subject paradox that motivated plan-047's deferral is genuinely dissolved.
- **A fail-closed binding landed today still blocks plan-049 at its own intake** — 3 `R2b` errors
  from `_tbd_` in Resolved By. Three table cells, but it *will* fire.
- **`R1b` is the real residual hazard**, not the finding schema: plan-048 tripped it 4× at its own
  intake, plan-001 27×.
- **SC6 as written cannot be certified** — it is 1-of-6, not general.
- **INCONCLUSIVE must not become FAIL.** With `only_paths` set, `doc_lint` **re-raises** rather than
  degrading, so a per-path binding turns a missing `document_types/` into a hard intake wedge.

## Recommendations

1. **Land fail-closed** — but after fixing plan-049's own 3 `R2b` rows.
2. **Bind at `_audit_plan` (:3999) only.** Sites 1 and 3 inherit; site 2 stays advisory for free.
3. **Map `Inconclusive` → `warn`, never `fail`**, and prefer the corpus-sweep form over per-`--path`.
4. **Strike "conform by construction" from plan-049's premises** — an unfalsified prediction with
   n=0. Re-measure after 5–10 findings are written under the new prompt.
5. Consider a one-shot `R1b` sweep before enforcement.
6. Two cheap `finding.toml` repairs: the stale `## Output` cross-reference, and the fenced-template trap.
