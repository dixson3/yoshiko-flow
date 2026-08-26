---
type: Reference
okf_spec: OKF-PLAN
id: exp-005-stale-issue-verification
description: EXP-005 — do the six apparently-delivered issues' deliverables actually satisfy their asks?
---

# EXP-005: verifying the six "already delivered" issues

**Verdict: D-5's METHOD is vindicated; its EXPECTED OUTCOME was wrong.** Scoping assumed six
clean closes. Measured: **four** clean closes, **one** close gated on a doc fix, and **one**
that must NOT be closed.

## Approach Tested

Read each issue body verbatim (`gh issue view N`), then read the claimed deliverable end to end. For #119/#120 additionally read the governing SPEC requirements, the production registration sites in `yf/src/cmd/doctor/checks.rs` and `yf/src/cmd/harness/mod.rs`, and **ran `yf doctor`** to observe the axes live rather than trusting the tests. For #122/#127 enumerated the on-disk agent files and the repo's actual recurring vocabulary and diffed them against the pages. Then swept the six most plausible remaining already-delivered candidates against the tree.

## Result

## Why this experiment earned its cost

Two of the six would have been mis-dispositioned by the scoping guess — one in each direction.
That is the exact failure D-5 was written to prevent, and it fired twice.

## Results

| Issue | Verdict | Residual |
| :-- | :-- | :-- |
| #120 | **CLOSE** | None. The suspected residual did **not** survive scrutiny |
| #122 | **CLOSE** | None. Survived the skeptical read |
| #123 | **CLOSE** | Cosmetic only; not worth holding |
| #124 | **CLOSE after a one-word fix** | A factual miscount in the page |
| #119 | **CLOSE-WITH-COMMENT, gated on a doc fix** | A shipped doc asserts the deferral the close retires |
| #127 | **RESCOPE — do NOT close** | Its stated success criterion is measurably unmet |

## The two that scoping got wrong

### #120 — the suspected residual was NOT real

Scoping suspected the codex budget check was incomplete because it covers a single file while
codex concatenates several. Measured: **the issue itself scopes to one file** — *"a yf managed
rule block in `~/.codex/AGENTS.md` [competing] with operator content"* — and `REQ-YF-TUNE-027`
records the single-file scope as a **chosen** limitation.

The delivery is real and was observed live, not read from tests:

```
[ok  ] codex-budget  projected ~/.codex/AGENTS.md 14663 bytes, under the 65536-byte cap
```

It reads the **effective on-disk** `project_doc_max_bytes` with the documented 32768 fallback
(not the profile's tuned 65536), warns at ≥90%, and never truncates.

**Holding #120 open on the multi-file basis would be the mirror-image error** of closing an
unmet issue. Multi-file concatenation is real engineering and deserves its **own** issue.

### #127 — must NOT be closed

The ask is *"a glossary **a cold reader can use to decode the docs**"*. All three named
exemplars are present and all 10 inbound `/glossary/#anchor` links resolve — but the stated
criterion is unmet. Measured frequency of **undefined** vocabulary (files under `skills/`
carrying the term vs. glossary hits):

| Term | Files | Glossary |
| :-- | --: | --: |
| `preflight` | 50 | **0** |
| `OKF bundle` | 48 | **0** |
| `worktree` / execute branch | 29 | **0** |
| `fail-closed` | 28 | **0** |
| `silent no-op` | 25 | **0** |
| `discovered-from` | 23 | **0** |
| `epistemic rules` | 11 | **0** |
| `session boundary` | 11 | **0** |
| `stuck-bead sweep` | 10 | **0** |
| `descope` | 5 | **0** |

A cold reader hitting `managed-files.md`'s own use of *"silent no-op"* and *"OKF bundle"* gets
nothing. The residual is **bounded**: roughly 8–10 entries, ~30 lines. Priority is `low`, so
deferring is defensible — **closing it untouched is not.**

## #119 is gated on a doc fix that must land in the SAME change-set

The axes are delivered and were observed live:

```
[ok  ] settings:claude-code   aligned with the recommended profile
[ok  ] settings:codex         aligned with the recommended profile
[ok  ] settings:opencode      aligned with the recommended profile
[ok  ] managed-block:codex    managed rule block current
[ok  ] managed-block:opencode managed rule block current
[ok  ] managed-block:pi       managed rule block current
```

No `settings:pi` axis — correct; pi ships no profile.

But `docs/recommended-settings.md:269-271` still reads:

> *"(A per-harness `yf doctor`/drift axis — the codex/opencode/pi analog of the Claude-Code
> drift check — is deferred to a follow-on; there is no automated drift gate for these
> harnesses yet.)"*

`git log` shows that file's last touch was `fe6eab9` (plan-033); **plan-034 shipped the axis and
never updated it.** `SPEC.md:1386-1392` marks the analog **Delivered (plan-034)**, so the doc
already contradicts the SPEC.

**Closing #119 first would ship a contradiction into published docs** — and that file is the
*checked artifact* in the `REQ-YF-TUNE-008` doc↔profile oracle, i.e. precisely the surface the
repo has decided must not drift.

Two further points for the close comment:

- The **-008 half was never built and was deliberately retired**: `SPEC.md:1389-1391` rules the
  per-harness reference-baseline gate **out of scope** — those harnesses carry prose only, with
  no baseline block for `drift.rs` to parse.
- **pi's settings axis is not delivered** and rides on **#121**, which stays open.

## #124 — one-word fix before closing

The heading reads *"How the **six** yf-beads-\* skills divide the work"*, but only **five**
`skills/yf-beads-*` exist; the sixth list item is `beads`, which is not a `yf-beads-*` skill.

## Sweep of the rest of the backlog: no further candidates

Six other plausible already-delivered issues were checked and **all six are genuinely open**:
#102 (no `.yf/` variant exists), #104 (`devserver` is a bare `pelican -lr`, no teardown target),
#90 (zero occurrences of actionlint/shellcheck in the skill), #166 (no matching prose), #145 and
#62 (neither skill dir exists).

## Amendment to D-5

D-5 stands as written — *verify each deliverable, then close* — but the plan must budget for
**three outcomes, not one**: close, close-after-fix, and rescope. The upstream dispositions for
**#119** and **#127** change accordingly.

## Implications for Plan

- Four of six are clean closes. **Two carry work that must land in the same change-set as the close, not after it.**
- **#119 is gated on a doc fix.** `docs/recommended-settings.md:269-271` asserts the deferral the close retires — and that file is the *checked artifact* in the REQ-YF-TUNE-008 doc-to-profile oracle, exactly the surface the repo has decided must not drift.
- **#127 must not be in the close batch as-is.** It is the one issue whose stated success criterion is measurably unmet, and the gap is concrete and cheap.
- **The suspected residual on #120 did not survive scrutiny.** Holding it open on the multi-file basis would be the mirror-image error of closing an unmet issue.
- No further sweep candidates: six other plausible issues were checked and all six are genuinely open.

## Recommendations

- **Close now, no changes:** #122, #123.
- **Close now, after a one-word fix:** #124.
- **Close now, with a comment:** #120 — record the delivered mechanism and that multi-file concatenation is an explicit, SPEC-recorded scope choice. File a separate issue if that case is wanted.
- **Fix the doc, then close with a comment:** #119 — correct `recommended-settings.md`, and record that the -008 analog is retired as out of scope and that pi's settings axis rides on #121.
- **Keep #127 open, rescoped** to the bounded residual, or fold the ~30-line addition into this release and close it properly. Closing it untouched is not defensible.
- **No additional sweep candidates.**

## Confidence

**measured:** the live `yf doctor` output, the 15/15 subagent coverage in `workflows.md`, the glossary frequency counts, the `recommended-settings.md` text and its `git log`, the `beads-concepts.md` miscount, and all six sweep candidates.

**inferred:** that the stale deferral paragraph is now false against shipped behaviour — corroborated by the SPEC amendment contradicting it.
