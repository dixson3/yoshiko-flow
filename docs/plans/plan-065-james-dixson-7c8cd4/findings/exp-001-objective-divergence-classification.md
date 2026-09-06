---
type: Finding
okf_spec: OKF-PLAN
description: 'exp-001 - does adopting plan.md H1 discard real information across the 7 objective-divergence bundles'
---

# exp-001: Objective-divergence classification across the 7 backfill-halting bundles

## Approach Tested

For each of the 7 bundles that halt on `objective-divergence`, read the legacy `README.md`
`> ` blockquote objective and the `plan.md` `# Plan:` H1 **verbatim**, then read each plan's
Objective, Motivation, Scope/Out-of-scope, Upstream Issues table, Epic headings and phase log to
establish **what the plan actually delivered**. Classified against delivery, not length.

Issue #295 (plan-057's decision D-5) was read **after** the classification was formed, so its
agreement is a corroboration rather than an input.

## Result

**measured:** classification counts — `plan-md-authoritative` **5**, `readme-richer` **2**,
`equivalent` **0**, ambiguous **0**.

| Bundle | Classification | What adopting plan.md H1 loses |
| :-- | :-- | :-- |
| plan-010 | **readme-richer** | the CLI's purpose and delivery: skill install/upgrade lifecycle, Homebrew distribution, retirement of `install.{sh,py}` |
| plan-012 | plan-md-authoritative | nothing — H1 is a strict superset (adds #30, E, F) |
| plan-013 | **readme-richer** | the policy's second half and the entire two-skill delivery decomposition |
| plan-014 | plan-md-authoritative | nothing — README is **stale pre-rescope scope** |
| plan-021 | plan-md-authoritative | nothing — the only extra (`+ yf-spec skill`) was **deferred out of scope** |
| plan-023 | plan-md-authoritative | nothing — README lists the **triage input** set; #60 was `defer`, #65 `supersede` |
| plan-026 | plan-md-authoritative | nothing — H1 is a strict superset (adds #85 / yf-markdown-format) |

### The two merged H1s

**plan-010:**

> Rename skills to `yf-` prefix and build the `yf` Rust CLI — skill install/upgrade lifecycle, Homebrew distribution, replacing `install.{sh,py}`

The README's `'yflow'` is the **rejected** name (plan-010 Approach, decision NAME: dropped due to
an active same-domain PyPI `yflow`). The merge imports only the three live facts, not the name.

**plan-013:**

> Reconcile policy — local beads = active work only; non-active work lives upstream until pulled via a plan (yf-beads-hygiene reconcile pass + yf-beads-upstream land-the-plane hoist-and-remove)

**measured:** `gh issue view 295` records D-5 as finding the README richer in **plan-010 and
plan-013**. This investigation derived the **same two bundles** independently, before reading the
issue. The mechanism of loss differs per bundle (plan-010 loses delivery-mechanism nouns;
plan-013 loses the two-skill decomposition), so the agreement is not an artifact of how README
lines happen to be written.

## Implications for Plan

`--reconcile-objective`'s unconditional adopt-plan.md is **correct for 5 of 7** and lossy for 2.
The loss is not cosmetic: plan-013 would lose its entire delivery decomposition.

**But a blanket prefer-README rule would be strictly worse.** It would regress plan-012 and
plan-026 (README is a proper subset there) and re-install dead scope into plan-014, plan-021 and
plan-023.

**No mechanical rule separates the two groups.** plan-014 and plan-021 are longer-README **stale**
cases; plan-010 and plan-013 are longer-README **rich** cases. They are indistinguishable from
outside the plan body — which is why length, issue-number count and superset tests all fail. The
per-bundle human decision #295 describes is genuinely required, and the tool is right to keep
failing closed.

**A second instance of the plan-014 trap was found unprompted.** The brief named only plan-014;
plan-021 is the same stale-scope shape. Stale-scope READMEs are the **common** case here (3 of 7),
not the exception.

## Recommendations

1. Adopt plan.md's H1 unchanged for **plan-012, plan-014, plan-021, plan-023, plan-026** — nothing is lost.
2. Pre-merge the H1s above into **plan-010** and **plan-013** before running the backfill, so `--reconcile-objective` then loses nothing on any bundle.
3. Do **not** generalize this into an engine heuristic. plan-014 / plan-021 are the counterexample any length- or richness-based rule gets wrong.
