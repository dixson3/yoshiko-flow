---
type: Finding
okf_spec: OKF-PLAN
id: exec-003-sc3-unsatisfiable
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
---

# exec-003 — SC3's mechanical check is unsatisfiable as written (plan-046, Epic 2)

**Verdict: the plan contradicts itself here.** Reported rather than quietly reinterpreted, because
"an artifact asserting something nothing checks" is the defect class this plan exists to fix — and a
criterion that cannot pass is the same failure wearing the opposite sleeve.

## The conflict

**SC3** requires:

> `grep -rniE "okf_version.*0\.1|OKF v0\.1" skills/ _shared/` … returns **zero** hits.

**But Issues 2.1, 2.3 and 2.4 require the opposite**, in `skills/`:

- **2.1** vendors v0.1 verbatim and 2.3 links it from `OKF-BASELINE.md`'s References — the link text
  must name v0.1.
- **2.3** requires a v0.1→v0.2 **section map**, and requires recording the pre-existing `(§5)`
  citation error, whose statement *is* a measurement about v0.1.
- **2.4** requires a **§13-verification subsection** quoting v0.1's clause beside v0.2's.
- **2.2**'s `REQ-OKF-FAM-005` rationale quotes §13's *"supersedes OKF v0.1"*.

A document that reconciles v0.1→v0.2 **must** mention v0.1. The pattern cannot distinguish a stale
claim ("yf is pinned to OKF v0.1") from a correct historical reference ("v0.2 supersedes OKF v0.1").

This is structurally the same defect pass 4 already caught in **SC9** — a criterion that named the
forbidden variants literally inside itself and so became its own counter-example. SC3 is the same
shape: it forbids a string that the work it grades is required to produce.

## What was actually achieved

### SC3 clauses 1 and 2 — DISCHARGED, and they are the substance

| clause | result | evidence |
| :-- | :-- | :-- |
| `okf_version` reads `0.2` in **all five copies** | **PASS** | `grep -rn "^okf_version" _shared/okf.py skills/*/scripts/okf.py` → 5/5 read `"0.2"` |
| `sync.py --check` exits `0` | **PASS** | executed; exit `0`. Also verified in the negative: it exited **1** (`DIVERGED` on all four copies) before the re-vendor, so the check is non-vacuous |

**Every stale claim is fixed.** 23 sites changed across 17 files: the constant in all five `okf.py`
copies, four test assertions/fixtures, and 14 prose sites (`SKILL.md` ×3, `README.md` ×2, `SPEC.md`
×2, `OKF-YF-EXTENSIONS.md` ×3, three `OKF-EXTENSION.md` files, `captor.md`, plus the three
fixed-authority pin sites from Issue 2.4a).

### Clause 3 — the enumerated allowlist (6 residual hits)

**The count moved from 5 to 6 during Epic 2, and the delta is accounted for, not a miscount.** The
first measurement was taken at Issue 2.5; hit **#2** below was written afterwards by **Issue 2.7**,
which corrected the third *"OKF is silent on log ordering"* site. Re-measured on the completed tree
the count is **6**.

**One of the six is a REGEX FALSE POSITIVE, not a historical reference** — a distinction worth
keeping, because it is the pattern misfiring rather than the corpus carrying a v0.1 mention:

| # | site | text | classification |
| :-: | :-- | :-- | :-- |
| 1 | `skills/yf-okf/SPEC.md:155` | quotes §13's *"supersedes OKF v0.1"* | historical — `REQ-OKF-FAM-005`'s stated rationale (Issue 2.2) |
| 2 | `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md:96` | *"OKF v0.1 reserved `log.md` … but demonstrated no format and no ordering"* | historical — the retired-claim record (Issue 2.7) |
| 3 | `skills/yf-okf/spec/OKF-BASELINE.md:31` | *"The primary v0.1 source was…"* | historical — §0 provenance (Issue 2.3) |
| 4 | `skills/yf-okf/spec/OKF-BASELINE.md:153` | the measured `okf_version`-at-§11 correction | historical — the pre-existing-citation-error record (Issue 2.3) |
| 5 | `skills/yf-okf/spec/OKF-BASELINE.md:462` | the link to the vendored v0.1 spec | historical — Issue 2.1's deliverable, cited from References |
| 6 | `skills/yf-plan/spec/portability.md:19` | *"…MAY carry `okf_version: 0.2` (… reconciled from `0.1` by plan-046 Epic 2)"* | **REGEX FALSE POSITIVE** — the line states the pin as **`0.2`**; `okf_version.*0\.1` matches across ~90 chars of unrelated text to reach the parenthetical `0.1`. Not a v0.1 reference at all |

Hit 6 is the clearest evidence that the pattern cannot discriminate: the one line that states the
**new** pin correctly is flagged, because `.*` spans the whole line.

### The `(§5)` correction, independently corroborated

The operator re-measured this finding against the upstream spec and **confirmed** it: v0.1 §5 is
*Cross-linking*, and the sole `okf_version` mention sits under §11 *Versioning*.

> **Line-number note, reconciled:** this finding cites `okf/SPEC.md:393`; the operator's measurement
> reads `:414`. **These are the same line.** The vendored copy at `references/okf-spec-v0.1.md`
> carries a 21-line yf provenance header above the verbatim upstream text (`393 + 21 = 414`). Cite
> `:393` for the upstream file and `:414` for the vendored copy. No discrepancy.

v0.1 §10 *"Relationship to other formats"* having no v0.2 counterpart was likewise independently
confirmed (0 hits).

## Proposed replacement criterion## Proposed replacement criterion

SC3's first two clauses stand as written and **both pass**:

- `okf_version` reads `0.2` in all five copies — **verified**;
- `sync.py --check` exits `0` — **verified**.

The grep clause should read: the widened pattern returns **only** historical references — mechanically,
every hit is in the enumerated allowlist above, and no hit **asserts** a current pin. As a command:

```bash
grep -rniE "okf_version.*0\.1|OKF v0\.1" skills/ _shared/ \
  | grep -vE "supersedes OKF v0\.1|primary v0\.1 source|okf-spec-v0\.1\.md|v0\.1 mentions|reconciled from"
# expected: no output
```

Verified: **no output**. This is a real check (it would catch a reintroduced stale claim) rather
than one that cannot pass.

**Not applied unilaterally, and now formally declined.** SC3 lives in `plan.md`'s fingerprinted
content, so rewriting a success criterion mid-execution to match the result is both the move this
plan's findings condemn *and* a mechanical hazard.

> **OPERATOR RULING (2026-08-18): accept the allowlist; do NOT amend SC3.**
> Success Criteria is **fingerprint-included**, so amending it mid-execution would make the plan
> **stale-approved** and force a fresh conformance → red-team → audit cycle before Epic 3 could
> continue. That cost is not worth paying for a criterion already correctly worked around. Clauses 1
> and 2 are discharged above; the 6-row allowlist is the auditable discharge of clause 3. The
> replacement command is recorded for a **future** plan, not applied here.

`plan.md` is therefore **unmodified**, and `resume-scan` was re-run afterwards to confirm
`stale_approved: false`.
