---
type: Plan
okf_spec: OKF-PLAN
id: plan-039-james-dixson-150f79
author: james-dixson
created: '2026-08-14'
status: reconciling
deliverable_class: standard
fingerprint: 1682d28f0130dc79fb823365e766d881a9df4780452e57d04ac77744c6ca0392
epic: yf-mol-mzj
---
# Plan: Raise yf-plan review quality: gate reachability, premise verification, and deliverable-class classifier accuracy

**ID:** plan-039-james-dixson-150f79
**Author:** james-dixson
**Created:** 2026-08-14
**Status:** reconciling
**Deliverable-class:** standard
**Epic:** yf-mol-mzj
**Fingerprint:** 1682d28f0130dc79fb823365e766d881a9df4780452e57d04ac77744c6ca0392

## Objective

Close the review-quality gap in `yf-plan` along three axes measured against real plans:

1. **Structural** — a plan's review passes never check whether a step's stated preconditions
   are actually available when it runs, or whether a gate's condition is reachable given what
   the gate blocks ([#112](https://github.com/dixson3/yoshiko-flow/issues/112),
   [#113](https://github.com/dixson3/yoshiko-flow/issues/113)).
2. **Factual** — no pass re-tests the findings a plan is built on, so a plan can be perfectly
   coherent and rest on a false premise ([#114](https://github.com/dixson3/yoshiko-flow/issues/114)).
3. **Mechanical** — the `ci-release` deliverable-class classifier suggests `ci-release` on
   essentially every plan, so its output carries no information at the point it is read
   ([#108](https://github.com/dixson3/yoshiko-flow/issues/108)).

Plus one in-flight repair discovered while reading `agents/reviewer.md` for this plan's own
conformance pass: that file's YAML frontmatter is corrupted (`:--` for `---`), so the conformance
agent's metadata does not parse. Unrelated to the three axes, too small to warrant its own plan,
and carried here with a guard so the class cannot recur (Epic 4).

Out of scope, deliberately: the topological DAG-walk engine and the `requires:` schema change
(#113's expensive branch — see EXP-002), and the `bd`→`gh` upstream mechanism swap
([#133](https://github.com/dixson3/yoshiko-flow/issues/133), which gets its own plan).

**Which copy of the code this plan edits.** `yf-plan` is installed user-globally at
`~/.claude/skills/yf-plan` and *also* lives in this repo at `skills/yf-plan/`. They are separate
artifacts. This plan edits the **repo copy only**; the installed copy is unchanged until
reinstalled, so every verification command below is pinned to the repo path. Install parity is
deliberately **out of scope** — see the note under Success Criteria.

## Motivation

`yf-plan`'s value proposition is that a reviewed plan is a *trustworthy* plan. Two independent
lines of evidence say that guarantee is weaker than it reads.

**Reviews miss a whole class of defect.** Across `d3-pxe` plan-013, four real defects were
found in review and a fifth escaped every pass. All five are the same shape: *a claim about
execution-time state that was never checked against what will actually be true at that point in
the DAG.* One of them was an unsatisfiable capability gate that survived conformance and **two**
red-team cycles. In plan-014 a separate failure — an inference (`the CT rebooted`) recorded with
the confidence of a measurement (`uptime -s`) — propagated into five plan artifacts, one of which
would have restarted a production database to test a bug that did not exist. Both passes reason
about a plan's *internal coherence*; neither walks it forward in time, and neither re-tests the
facts underneath it.

**A safety mechanism has degraded into a constant.** The `ci-release` deliverable class drives
`complete-gate`, which fail-louds a plan lacking a validation attestation. #108 reported the
classifier false-positiving on two Proxmox plans. Measured across 53 real plans (EXP-001), it
suggests `ci-release` on **40 of 53** (measured 2026-08-14; the count moves as plans are added,
including this one), and on **all 17** plans where an operator recorded a ground-truth class —
**16 of them wrongly**, with **zero** correct negatives, ever. A suggestion that is always the same
value is not a suggestion. Worse, it arrives labeled `confidence: high`, which invites acceptance;
and a false positive surviving to reconcile blocks completion on a plan that never had
runner-only behavior, where the natural fix under time pressure is to attest something untrue.

Who is affected: every operator of every `yf-plan`-using repo. What triggered the work: a
prior session's review of the d3-pxe plan-013/014 defect set, plus the #108 report, both of
which this plan re-verified against the primary artifacts rather than taking on trust.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#112](https://github.com/dixson3/yoshiko-flow/issues/112) | red-team should check gate REACHABILITY, not just well-formedness | include | Lands in red-team `Evaluate`, per operator decision; migrates to a post-DAG pass if #113 ever justifies one | 2.2 |
| [#114](https://github.com/dixson3/yoshiko-flow/issues/114) | verify the PREMISES a plan rests on (measurement vs inference) | include | Two prompt additions, exactly as proposed — investigator + red-team | 2.3, 2.4 |
| [#108](https://github.com/dixson3/yoshiko-flow/issues/108) | deliberate-class heuristic false-positives ci-release on ordinary infra plans | include | All four suggested fixes adopted; EXP-001 measured the defect at 16/17, far above the reported n=2 | 3.1–3.6 |
| [#113](https://github.com/dixson3/yoshiko-flow/issues/113) | add an execution-rehearsal review pass (topological DAG walk) | partial | **In:** the prose precondition cross-check (2.4), which EXP-002 shows catches ≥3 of the 5 observed defects with no schema change. **Out:** the DAG-walk engine and the `requires:` schema — unjustified on one plan's evidence. Issue stays open, re-scoped | 2.4, 5.2a, 5.2b |
| [#109](https://github.com/dixson3/yoshiko-flow/issues/109) | stale_approved computed status-independently | supersede | Does not reproduce: 0/38 completed plans display the tag (EXP-003). The mechanism claim is code-true but the path is unreachable — closed with that distinction recorded, not silently | 5.1a, 5.1b |
| [#134](https://github.com/dixson3/yoshiko-flow/issues/134) | plan-039 execution tracking | tracker | The coarse plan-level tracking issue for this plan, filed at intake per the repo's one-issue-per-plan convention. Not a work item — Issue 5.3 updates it | — |
| [#133](https://github.com/dixson3/yoshiko-flow/issues/133) | replace `bd <backend> push` with gh-direct issue creation | exclude | Materially different surface (yf-beads-upstream mechanism swap) with four unresolved design decisions. Gets its own plan | — |

## Investigation Findings

Three experiments, all against primary artifacts available locally. Per the convention this
plan adopts in #114, each finding separates **measurement** from **inference**.

### EXP-001 — classifier corpus measurement ([findings](findings/exp-001-classifier-corpus.md))

Ran the unmodified `_classify_deliverable` over 53 real plans (39 `yoshiko-flow`, 14 `d3-pxe`,
including both plans #108 cites), scored against the 17 plans carrying an operator-confirmed
`deliverable_class`.

- **Current precision is 1/17, with `TN=0`** — it has never produced a correct negative.
  Full corpus: **40/53** suggested `ci-release`.
- **All fixes together: `TP=1 FP=2 TN=14 FN=0`**, full corpus 13/53. **No recall cost** — `FN=0`
  holds after every individual fix, not just at the end.
- **F3 (require a high signal) is the dominant fix.** Re-measured in this plan's implementation
  order (F3 → F1 → F2 → F5 → F4): F3 alone takes the corpus 40→22 and false positives 16→8;
  F1 is second (22→15, FP 8→3). **F2 removes zero labeled-set false positives** and is the
  weakest — it ships only with a stop rule.
- **F5 (strip code spans and fenced blocks) was added during review** — a quoted token is not a
  claim. Reduces per-plan signal counts across the corpus without changing `FN`.
- **The two residual false positives are one class** — plan text *consuming or referencing* a
  release (`pinned release binary`, `kept until the next major release of yf`) rather than
  producing one. The distinguishing feature is the verb, not the noun, which is why a keyword
  blocklist keeps chasing it.
- **F4 makes `confidence` constant at intake**: the path marker is the only non-prose signal and
  `changed` is empty at §4.1.5, so every intake classification reports `low`. F4 correctly stops
  the field overstating, but leaves it carrying no information where it is actually read.

### EXP-002 — is a `requires:` schema change needed? ([findings](findings/exp-002-precondition-inferability.md))

Read the as-landed `d3-pxe` plan-013 — source of all four defects #113 tabulates — to test
#113's own open question.

- **Every observed remedy was expressible in today's schema**: `depends-on` edges (3 cases), a
  capability gate (1), an issue split (1). No `requires:` key was needed for any of them.
- **The missing artifact was the edge, not the declaration.** In all five cases the precondition
  was written out in plain English in the issue body; only the machine-readable dependency was
  absent. A prose-vs-DAG cross-check therefore has enough information to catch them.
- **2 of the 5 are not reachability failures at all** — one capability gap, one semantic
  conflict (an issue's output failing a check an earlier issue installs). Neither is found by a
  graph walk, which weakens #113's "mechanical, pass/fail, therefore conformance" framing and
  supports the operator's decision to put this in red-team.
- **The corpus is still one plan deep.** #113's own `n=1` caveat survives this experiment intact.

### EXP-003 — does #109 reproduce? ([findings](findings/exp-003-109-nonreproduction.md))

- **Mechanism claim is code-true**: `plan_manager.py:1023` and `:1069` compute and render
  `stale_approved` with no status filter.
- **Symptom does not reproduce: 0/38** completed plans report `stale_approved: true`.
- **Why** (inferred): the fingerprint excludes `**Field:**` header lines and `log.md`, so
  completion cannot perturb it; `stored == current` always holds and the branch is unreachable.
  Latent, not absent — a post-completion `--force`d content edit would surface it.

## Approach

**Prompt changes over machinery.** Four of the five structural defects and the entire premise
defect are addressed by additions to two agent prompts totaling well under a page. EXP-002
establishes that the expensive alternative — a DAG-walk engine plus a `requires:` schema —
buys nothing on the available evidence. Build the cheap thing, measure a second plan, revisit.

**Measurement-backed classifier changes, sequenced by measured impact.** #108's four fixes are
all adopted, but sequenced F3 → F1 → F2 → F4 (largest correction first) rather than in the
order the issue lists them. The 17 operator-labeled plans become a fixture corpus, and the
regression harness is built **before** the fixes so each one's effect is measured rather than
asserted — the "prove the check actually catches" pattern.

**SPEC-first**, per the repo mandate: every behavior change lands as a `REQ-*` amendment ahead
of its implementation, with a living-amendment-log entry, then code and a tagged test against it.

**This plan is its own adversarial fixture — for signal *honesty*, not for a `standard` verdict.**
Its text is dense with `release`, `sign`, `deploy`, `pipeline`, and `workflow`, in prose *about*
the classifier. It will still classify `ci-release`, and that is the **correct** outcome: a plan
whose subject *is* releases and signing falls in the **self-reference class**, a structural limit
of prose keyword matching that no blocklist can close (Issue 3.4b). What Epic 3 must deliver here
is an honest report — `evidence: prose-only`, `confidence: low`, and every residual signal
traceable to genuine subject-matter prose. That is SC6.

A hard signal count was asserted here twice and falsified by measurement twice (pass-2 H1,
pass-3 C1), because the document being measured is the document being edited. The criterion now
asserts stable properties instead.

## Epics

### Epic 1: SPEC amendments (SPEC-first)

- **Issue 1.1:** Land the **complete REQ set for Epic 2, atomically** — one file
  (`skills/yf-plan/spec/agents.md`) plus one amendment-log entry. It is deliberately not split:
  the three new REQs and the REQ-AGENT-021 amendment are a single coherent contract for the
  review passes, and a partially-landed REQ set would leave Epic 2 implementing requirements
  that do not exist. Add to `skills/yf-plan/spec/agents.md`:
  **REQ-AGENT-046** (red-team gate reachability — a gate whose `Condition` depends on evidence
  produced by an issue in its own `Blocks` set is unsatisfiable; gate the mutating step, not the
  step producing the evidence); **REQ-AGENT-047** (red-team precondition cross-check — for each
  issue, the artifacts/tools/capabilities its text assumes are either produced by a declared
  `depends-on` predecessor or established by a gate); **REQ-AGENT-048** (red-team premise check —
  for each finding an epic/gate/success-criterion depends on, is it measured or inferred; if
  inferred, is it independently corroborated; what would falsify it and was that checked).
  Amend **REQ-AGENT-021** so the investigator finding format marks load-bearing conclusions
  `measured` or `inferred` and requires corroboration for any inference the plan will build on.
  Add the living-amendment-log entry to root `SPEC.md`.
- **Issue 1.2:** Amend **REQ-CLI-015** in `skills/yf-plan/spec/cli.md` for the corrected
  classifier contract: the scan region is the Epics / Upstream Issues / Success Criteria sections
  (not the whole file); a `ci-release` suggestion requires a **high** signal, with low-only
  matches reported as informational; the reported evidence basis distinguishes path-backed from
  prose-only rather than labeling prose-only matches `high`; and code spans / fenced blocks are
  excluded from the scan (F5 — a quoted token is not a claim). Amendment-log entry in root
  `SPEC.md`.
- **Issue 1.3:** Add a **frontmatter-integrity** requirement to **root `SPEC.md`**: every
  `skills/*/agents/*.md` and `skills/*/SKILL.md` carries a well-formed, terminated YAML
  frontmatter block. Root `SPEC.md`, not `skills/yf-plan/spec/cli.md`, because the invariant is
  **repo-wide across all 20 skills** — a cross-skill rule filed under the yf-plan CLI key would
  be undiscoverable from the 19 skills it constrains (pass-3 C4).

  **Match the file's actual conventions** (pass-4: an earlier draft proposed a bare
  `REQ-YF-230`, which fits nothing in root `SPEC.md` — that file has **zero** line-anchored
  `REQ-` lines; every requirement is a bullet `- **REQ-YF-<SUBKEY>-NNN** *(testable)* …` homed in
  a numbered §3.x section whose heading declares the subkey). Home it in **§3.2 Embedding
  (`REQ-YF-EMBED`)** — the section governing the shape of the embedded `skills/` tree, which is
  exactly what this invariant constrains — as the **next free** `REQ-YF-EMBED-NNN`. Do not
  hardcode a number here; SC1 verifies the pattern, not a specific id, so the two cannot
  disagree. Amendment-log entry alongside. Implemented by Issue 4.2.

### Epic 2: Review-prompt hardening (#112, #114, #113-partial)

Issues 2.2–2.4 all edit `skills/yf-plan/agents/red-team.md` and are sequenced serially to keep
the edits conflict-free; 2.1 edits a different file and is independent.

- **Issue 2.1:** `skills/yf-plan/agents/investigator.md` — extend the finding format so each
  load-bearing conclusion is tagged **measured** (a command ran, this was its output) or
  **inferred** (what the author concluded from it), and require any inference the plan will build
  on to be corroborated by a second independent signal. Cite the plan-014 case in the rationale:
  four independent signals each settled it and any one would have prevented the error.
  Implements REQ-AGENT-021 as amended (#114 change 1).
  - depends-on: 1.1
  - resolves-upstream: [#114](https://github.com/dixson3/yoshiko-flow/issues/114) (include, with 2.3)
- **Issue 2.2:** `red-team.md` Evaluate — add **Gate reachability** under the existing
  **Gates** item: for each capability gate, can its `Condition` be satisfied given what it
  `Blocks`? A condition depending on evidence produced inside its own `Blocks` set is a cycle.
  Implements REQ-AGENT-046 (#112).
  - depends-on: 1.1
  - resolves-upstream: [#112](https://github.com/dixson3/yoshiko-flow/issues/112) (include)
- **Issue 2.3:** `red-team.md` Evaluate — add **Premise check**: for each finding an epic,
  gate, or success criterion depends on, is it a measurement or an inference? If inferred, is it
  corroborated by an independent signal? **What would falsify it, and was that checked?** The
  falsification prompt is the load-bearing part — answerable in seconds, askable with no domain
  expertise. Implements REQ-AGENT-048 (#114 change 2).
  - depends-on: 2.2
  - resolves-upstream: [#114](https://github.com/dixson3/yoshiko-flow/issues/114) (include, with 2.1)
- **Issue 2.4:** `red-team.md` Evaluate — add **Precondition cross-check**: for each issue, are
  the artifacts, tools, and capabilities its text assumes either produced by a declared
  `depends-on` predecessor or established by a gate? Report each unmet precondition with the node
  that needed it. This is #113's cheap branch, scoped by EXP-002; it explicitly does **not**
  introduce a DAG-walk engine or a `requires:` key. Implements REQ-AGENT-047.
  - depends-on: 2.3
  - resolves-upstream: [#113](https://github.com/dixson3/yoshiko-flow/issues/113) (partial)
- **Issue 2.5:** Verify the amended red-team prompt against known-defective source material —
  both that the **new** items fire and that the **existing** items still do.

  Reproduce four fixtures under `references/`:

  | Fixture | Source | Must be flagged by |
  | :-- | :-- | :-- |
  | `replay-plan-013-gate.md` | plan-013's **pre-fix** gate (`Blocks: 5.1`, condition requires a preview of 5.1's own output) | new: gate reachability (2.2 / REQ-AGENT-046) |
  | `replay-plan-014-premise.md` | plan-014's `EXP-001` reboot finding, stated as a measurement | new: premise check (2.3 / REQ-AGENT-048) |
  | `replay-plan-013-epic6.md` | plan-013's **pre-fix** Epic 6 — "re-audits the hardened tree" with **no** `depends-on` on Epics 1–5. Pre-fix text is quoted verbatim in d3-pxe `reviews/pass-0-conformance.md`; `findings/exp-002` quotes the as-landed remedy | new: precondition cross-check (2.4 / REQ-AGENT-047) |
  | `replay-plan-013-capability.md` | plan-013's **pre-fix** success criteria requiring SSH to 9 hosts + a secret env no gate declared | **existing**: the checks that already caught this |

  The third fixture exists because pass-2 H3 found that **2.4 — the item discharging #113's
  `partial` disposition, which 5.2b announces upstream as shipped — had no evidence it fires at
  all.** The fourth is a **regression fixture**: a defect the *current* prompt catches, guarding
  the dilution R2 names. Line count (SC10) proxies for this badly and is demoted to advisory.

  **The replay runs in a fresh session with no access to this plan, its findings, or this
  conversation** — given only the amended `red-team.md` and one fixture at a time. A replay that
  already knows the expected answer proves nothing; this is the independence standard pass-1 of
  this plan's own review failed to meet, recorded there as a caveat. Record verbatim output in
  `references/replay-results.md`, one `- FLAGGED` line per fixture caught. All four must be
  flagged.

  **Source of the pre-fix text.** Three fixtures need plan-013/014 text *as it was before review
  fixed it*. `findings/exp-002` records the **as-landed** remedies, not the pre-fix bodies, so
  the primary source is the `d3-pxe` bundles' own `reviews/pass-N.md` (which quote the defects
  verbatim), falling back to `git log -p` on those plan.md files. **If neither is available**,
  reconstruct from the defect descriptions in #112/#113 — which state each one precisely — and
  record in `replay-results.md` that the fixture is a reconstruction, not a verbatim capture.

  **On a miss.** If a fixture is not flagged, that is a **finding, not a tuning signal**. Record
  it verbatim and bring it to the operator. At most **one** revision cycle per fixture; a second
  miss escalates rather than iterates. Tune-until-green would reproduce exactly the
  confirmation-bias failure this issue exists to avoid.

  A fifth fixture is available for free: this plan's own **pre-fix** `Gate: Upstream write`,
  which blocked the two upstream-publish issues (`4.1, 4.2` in the v1 numbering; now `5.1b,
  5.2b`) while requiring their output — the same cycle as fixture 1, independently reproduced
  during this plan's conformance pass.
  - depends-on: 2.4

### Epic 3: Deliverable-class classifier accuracy (#108)

Fixture-and-harness first, so every subsequent fix is measured rather than asserted.

- **Issue 3.1:** Build `skills/yf-plan/scripts/test_classify_deliverable.py` plus a fixture
  corpus under `skills/yf-plan/scripts/fixtures/classify/` derived from the 17 operator-labeled
  plans (reduced to their scanned sections + recorded ground-truth class; no verbatim copying of
  unrelated plan content). Assert the **current** behavior as the baseline — `TP=1 FP=16 TN=0
  FN=0` — so the harness is known to reproduce EXP-001 before anything changes. The fixtures are
  **vendored into this repo**: once 3.1 lands, no later issue and no CI run may depend on the
  `d3-pxe` checkout being present.
  - depends-on: 1.2
  - resolves-upstream: [#108](https://github.com/dixson3/yoshiko-flow/issues/108) (include, with 3.2–3.6)
- **Issue 3.2:** **F3 — require a high signal.** A `ci-release` suggestion requires at least one
  high-tier signal; low-only matches are reported in `signals` as informational with
  `suggested_class: standard`. Largest measured correction, smallest change.

  **Harness expectations are per-step, in this plan's implementation order** (F3 → F1 → F2 →
  F5 → F4), re-measured after pass-2 H2 caught the original figures being the *cumulative*
  F1+F2+F3 numbers from a different ordering:

  | After | Labeled set | Full corpus |
  | :-- | :-- | --: |
  | current (baseline, 3.1) | `TP=1 FP=16 TN=0 FN=0` | 40/53 |
  | **F3 (3.2)** | `TP=1 FP=8 TN=8 FN=0` | 22/53 |
  | F3+F1 (3.3) | `TP=1 FP=3 TN=13 FN=0` | 15/53 |
  | F3+F1+F2 (3.4) | `TP=1 FP=2 TN=14 FN=0` | 13/53 |
  | +F5 (3.4b) | `TP=1 FP=2 TN=14 FN=0` | 13/53, per-plan signal counts reduced |

  The harness asserts the **invariants** at every step — `FN=0`, and `FP` non-increasing — and
  the exact tuple only after 3.5. Corpus counts are re-derived by the harness, never
  transcribed (pass-2 M3: the figures drift as plans are added, including this one).
  - depends-on: 3.1
  - resolves-upstream: [#108](https://github.com/dixson3/yoshiko-flow/issues/108) (include, with 3.1–3.6)
- **Issue 3.3:** **F1 — section-scoped scan.** Restrict `hay` to the Epics, Upstream Issues, and
  Success Criteria sections, honoring the function's existing docstring. Removes the title-verb
  class (`# Plan: Deploy …`) and risk-table-cell matches. Include a fixture whose H1 contains
  `Deploy` and whose scanned sections do not.
  - depends-on: 3.2
  - resolves-upstream: [#108](https://github.com/dixson3/yoshiko-flow/issues/108) (include, with 3.1–3.6)
- **Issue 3.4:** **F2 — negative context guards** for the demonstrated collisions: `self-signed`,
  `signed certificate`, upstream release cadence (`release notes|cycle|cadence`),
  `(metrics|logs|traces) pipeline`, `deployed by`.

  **Retained on an operator re-decision made *after* EXP-001**, which measured F2's labeled-set
  contribution at **zero** false positives removed. It ships for the corpus-wide effect and the
  documentation value, not as a general fix — and it carries a **stop rule**, written into the
  code comment beside the pattern list:

  > No keyword is added to this list without a corpus re-measurement showing it moves `FP`.
  > This list is a known-incomplete blocklist, not a general solution. It structurally cannot
  > cover the residual class — plan text that *consumes or references* a release rather than
  > producing one (measured examples: a pinned upstream release binary; a deprecation horizon
  > phrased as "kept until the next major release") — where the distinguishing feature is the
  > verb, not the noun.

  The stop rule is what bounds R3's unbounded-growth risk; without it F2 is a liability.
  - depends-on: 3.3
  - resolves-upstream: [#108](https://github.com/dixson3/yoshiko-flow/issues/108) (include, with 3.1–3.6)
- **Issue 3.4b:** **F5 — quoted tokens are not claims.** Strip fenced code blocks and inline code
  spans from the scan region before matching. A plan that writes a trigger word inside a command,
  a regex, or a quoted example is not thereby announcing that it ships releases.

  Structural rather than a blocklist entry, so it is exempt from 3.4's stop rule and does not
  grow. Measured on stable documents: plan-012 2→1, plan-016 3→2, plan-030 5→4, plan-031 4→2,
  with `FN=0` preserved. **This plan is deliberately not in that list** — it is still being
  edited, so its signal count is a moving target (5→3 at the time of writing, and it rose as the
  H1 remedy added prose about releases). Re-derive at execution; never transcribe.

  **Known structural limit, recorded here so it is not re-derived.** F5 does not — and no
  keyword approach can — fix the **self-reference class**: a plan whose *subject* is releases,
  signing, or the deliverable class itself will match in ordinary prose. This plan is the
  demonstration (see SC6). The honest remedy is F4's evidence basis, not another pattern.
  - depends-on: 3.4
  - resolves-upstream: [#108](https://github.com/dixson3/yoshiko-flow/issues/108) (include, with 3.1–3.6)
- **Issue 3.5:** **F4 — honest confidence.** Reserve `confidence: high` for the
  `.github/workflows/` path marker. Because `changed` is empty at intake, this makes the field
  constant there (EXP-001), so additionally report an explicit `evidence` basis
  (`path-backed` | `prose-only`) and surface it in SKILL.md §4.1.5 so the operator sees *why* a
  suggestion is weak rather than a severity word that is always `low`.
  - depends-on: 3.4b
  - resolves-upstream: [#108](https://github.com/dixson3/yoshiko-flow/issues/108) (include, with 3.1–3.6)
- **Issue 3.6:** Wire `test_classify_deliverable.py` into `CHANGE-VALIDATION.md` fast and
  full tiers, and update SKILL.md §4.1.5 / §6.4 prose for the new output shape.
  - depends-on: 3.5
  - resolves-upstream: [#108](https://github.com/dixson3/yoshiko-flow/issues/108) (include, with 3.1–3.4b, 3.5)

### Epic 4: Repair a corrupted review-agent file

- **Issue 4.1:** **The repair, alone.** `skills/yf-plan/agents/reviewer.md` line 7 closes its
  YAML frontmatter with `:--` instead of `---`, so the block is unterminated and the agent's
  `name` / `role` / `stance` / `description` metadata does not parse. The damage matches a GFM
  table-alignment autofix (`:--` is an alignment marker) applied to a frontmatter delimiter.
  Restore the delimiter. One character; no new enforced behavior, so no SPEC amendment is owed.
  Discovered while reading `reviewer.md` for this plan's own conformance pass; pre-existing and
  unrelated to the three tracked axes.
- **Issue 4.2:** **The guard.** Add `scripts/check_frontmatter.py` — asserting that every
  `skills/*/agents/*.md` and `skills/*/SKILL.md` carries a well-formed, terminated YAML
  frontmatter block — and wire it into `CHANGE-VALIDATION.md` fast and full tiers, so the class
  cannot silently return. Audited during review across all 20 skills: `reviewer.md` is the **only**
  offender across all 20 skills, so the guard lands green on the rest of the tree once 4.1 is
  applied.

  This is a **new enforced behavior**, so it is SPEC-first: the new **`REQ-YF-EMBED-NNN`** frontmatter-integrity
  requirement plus its amendment-log entry land in Issue 1.3 — root `SPEC.md`, not the yf-plan
  CLI spec, because the invariant is **repo-wide** across all skills (pass-3 C4). It also edits
  `CHANGE-VALIDATION.md`, which Issue 3.6 edits too — sequenced after it for the same
  conflict-avoidance reason Epic 2's issues are serialized.
  - depends-on: 4.1, 1.3, 3.6

### Epic 5: Upstream reconciliation of deferred and non-reproducing issues

Authoring the comment text is **ungated**; only publishing is gated (see `Gate: Upstream write`).

- **Issue 5.1a:** Draft the closing comment for
  [#109](https://github.com/dixson3/yoshiko-flow/issues/109) from the EXP-003 evidence, stating
  the mechanism/symptom split explicitly: the status-independence is code-true, the display path
  is unreachable because completion cannot perturb the fingerprint, 0/38 completed plans
  reproduce it, and the residual exposure is a post-completion `--force`d content edit. Write the
  text to `references/close-109.md`. No `gh` call. Not a silent close.
  - depends-on: 3.6, 2.5
- **Issue 5.1b:** Publish `references/close-109.md` — `gh issue comment 109` then
  `gh issue close 109`.
  - depends-on: 5.1a
  - resolves-upstream: [#109](https://github.com/dixson3/yoshiko-flow/issues/109) (supersede)
- **Issue 5.2a:** Draft the re-scoping comment for
  [#113](https://github.com/dixson3/yoshiko-flow/issues/113) from the EXP-002 finding, narrowing
  it to the DAG-walk engine only: record that the prose cross-check shipped as its cheap
  precursor (Issue 2.4), that no observed defect required a `requires:` schema change, that 2 of
  the 5 defects are not reachability failures at all, and that its `n=1` caveat still stands.
  Write the text to `references/rescope-113.md`. No `gh` call.
  - depends-on: 3.6, 2.5
- **Issue 5.2b:** Publish `references/rescope-113.md` — `gh issue comment 113`. Leave the issue
  **open**.
  - depends-on: 5.2a, 2.5
  - resolves-upstream: [#113](https://github.com/dixson3/yoshiko-flow/issues/113) (partial, with 2.4)
  - Note: gated behind 2.5 per pass-2's upstream assessment — this comment announces that the
    precondition cross-check has shipped, so it must not publish before the fixture proves the
    check fires.
- **Issue 5.3:** File the coarse plan-level **tracking issue** for plan-039 against
  `dixson3/yoshiko-flow` — routed through `/yf-beads-upstream`, never a hand-run `bd <backend>`
  push (the repo's `UPSTREAM_TRACKING.md` safety invariant) — and file two deferred follow-on
  beads, both labelled exactly **`plan-039-followon`**: (a) R9's **re-measure checkpoint** —
  after the next two plans complete, compare defects-found-per-review against the plan-013
  baseline (**4 found, 1 escaped**) and record the result on the tracking issue; (b) **install
  parity** — re-bake (`cargo build`) and `yf skills install yf-plan`, then verify the running
  skill matches the repo. Both are pass-2 findings (M5, H4). The re-measure is also the
  second-plan evidence #113 asks for.
  - depends-on: 5.1b, 5.2b

## Gates

### Start Gate (mandatory)

- Type: human
- Approvers: operator

### Capability Gate: Evidence corpus

- Type: human
- Condition: the `d3-pxe` plan corpus is readable — by Issue 3.1, for the 17 operator-labeled
  plans, **and by Issue 2.5**, for the pre-fix plan-013/014 replay text.
- Test: `test -d "$HOME/workspace/dixson3/d3-pxe/Incubator" && [ "$(ls "$HOME"/workspace/dixson3/d3-pxe/Incubator/*/plans/*/plan.md 2>/dev/null | wc -l)" -gt 0 ]`
- Blocks: 3.1, 2.5
- Instructions: The corpus lives in a **sibling repository on this machine**, not in this repo —
  an execution-time capability no other step establishes. Degraded fallbacks, both acceptable:
  Issue 3.1 proceeds with the 8 `yoshiko-flow`-only labeled plans at reduced statistical power
  (record the reduction in the fixture README); Issue 2.5 reconstructs its fixtures from the
  defect descriptions in #112/#113 and marks them as reconstructions. Once 3.1 vendors the
  fixtures and 2.5 writes its replay fixtures into `references/`, the dependency is discharged
  and **no CI run** reaches outside the repo.
- Note: pass-2 M1 found the original test could not fail (BSD `wc -l` pads with spaces, so
  `grep -qv '^0$'` always succeeded) and pass-2 M2 found 2.5's dependency un-gated while the
  instructions claimed it was discharged. Both are defect classes this plan adds checks for,
  found in this plan.

### Capability Gate: Upstream write

- Type: human
- Condition: operator has read `references/close-109.md` and `references/rescope-113.md`
  (produced by Issues 5.1a/5.2a, which this gate does **not** block) and authorizes publishing
  them against `dixson3/yoshiko-flow`.
- Test (paths are plan-dir-relative; run from `${plan_dir}`): `gh auth status >/dev/null 2>&1 && gh repo view dixson3/yoshiko-flow --json name -q .name && test -s references/close-109.md && test -s references/rescope-113.md`
- Blocks: 5.1b, 5.2b
- Instructions: Gated on the **mutating** step only. The evidence the condition needs is produced
  by 5.1a/5.2a, which are outside the `Blocks` set — so the condition is reachable from the state
  the gate creates (REQ-AGENT-046, dogfooded). The earlier draft of this plan blocked the two
  upstream-publish issues (numbered `4.1, 4.2` in the v1 draft; now `5.1b, 5.2b`) while requiring
  their output, reproducing the exact plan-013 cycle #112 reports; the conformance pass caught it. Pass-2 L5 added the artifact-existence checks so the test is responsive to its
  own condition rather than only proving auth.

### Reconcile Gate

- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **Prompt additions are unfalsifiable.** Three new review items could be added and simply never fire, with no way to tell. | high | Issue 2.5 replays **four** fixtures — one per new item, plus a no-regression fixture for the existing checks — in a **fresh session with no access to this plan**, and requires each to be flagged, with a one-revision-cycle cap so it cannot become tune-until-green. A review item never seen to fire is not known to work. |
| R2 | **Review-prompt bloat.** `red-team.md` is 60 lines; three additions plus rationale could dilute the whole prompt and degrade the checks that already work. | medium | Each addition is one Evaluate bullet, phrased as a question. Rationale and evidence live in the SPEC and in `findings/`, not in the prompt. The real check is 2.5's no-regression fixture; SC10's line count is advisory only. |
| R3 | **F2's blocklist grows unboundedly.** EXP-001 measured its labeled-set contribution at zero and identified a residual class it structurally cannot cover. | medium | Ship it documented as known-incomplete with the measured counter-examples recorded in-code, plus the 3.4 **stop rule** (no keyword without a corpus re-measurement showing it moves `FP`). F5 (3.4b) is the structural alternative and is exempt. |
| R4 | **Fixture corpus over-fits.** The 17 labeled plans are from two repos and one operator; tuning to a low `FP` on them may not generalize. | medium | Assert `FN=0` as the hard invariant and `FP` non-increasing as the trend; the exact tuple is asserted only after 3.5. `FP<=2` has no principled basis — it is the measured all-four result, recorded so a regression is visible, not a target to tune toward. Recall, not precision, is the safety-critical direction: a false positive costs an operator ten seconds at intake, a false negative silently disables a completion gate. |
| R5 | **#113 partial-close ambiguity.** Shipping the cheap precursor could read upstream as "#113 is done", losing the DAG-walk proposal. | low | Disposition is `partial`, not `include`; Issues 5.2a/5.2b explicitly re-scope and leave it open, and 5.2b is gated behind 2.5 so nothing is announced before it is observed to fire. Reconciler comments without closing (REQ-AGENT-031). |
| R6 | **The classifier lives in the user-global skill install.** Changes affect every consuming repo, and a regression could block completion fleet-wide. | medium | `FN=0` invariant plus CHANGE-VALIDATION rows (3.6). The failure direction that matters — a genuine `ci-release` plan classified `standard` — is measured at zero across the corpus. Install parity is a separate follow-on (5.3), so this plan cannot silently ship a regression to the running skill. |
| R7 | **Whatever corrupted `reviewer.md`'s frontmatter may still be live.** The `:--` substitution is a GFM alignment marker applied to a `---` delimiter; if a table-alignment autofix still treats frontmatter as a table, Epic 4's repair will be undone on the next run. | medium | Issue 4.2 ships a guard, not just a repair, so recurrence fails CI loudly. If the guard fires again after the fix, the autofix itself is the defect and gets its own issue — this plan does not chase it. |
| R8 | **The evidence corpus is a sibling repo, not a dependency this repo can assert.** Issues 3.1 and 2.5 read `d3-pxe` at authoring time. | low | Declared as an explicit capability gate covering **both** issues, with a documented degraded fallback for each. Fixtures are vendored, so the reach-outside-the-repo happens at authoring time only and CI never depends on it. |
| R9 | **Prompt regressions are silent.** If the amended review passes make reviews *worse* in practice, nothing surfaces it — a review that stops catching things looks identical to a plan with no defects. | medium | Two-part: (a) the Epic 2 changes are additive bullets in two files, so `git revert` of the Epic 2 commits is a clean rollback with no schema or data migration; (b) an explicit **re-measure checkpoint**, filed as a deferred bead by Issue 5.3 (not a prose promise) carrying the plan-013 baseline. |
| R10 | **This plan's own review found defects in this plan on every cycle — including defects introduced by the previous cycle's fixes.** Pass 1: a gate-reachability cycle. Pass 2: a falsified success criterion, a 4×-wrong harness expectation, a missing fixture, a nonexistent command. Pass 3: the SC6 fix falsified again by the prose its own remedy added. Pass 4: that fix landing in the criterion but not in the Approach paragraph naming it, and a REQ id that fit no convention in its target file. The plan is dense, self-referential, and its own measurement subject. | medium | Every review artifact is retained in full with verbatim concerns and resolutions, and several found defects became replay fixtures. Two structural lessons are now encoded rather than re-learned: **assert properties, not counts**, against a document still being edited (SC6, 3.2, 3.4b); and **verify an id or command against the real target file**, not against its assumed shape (SC1, SC1b). The pattern argues for running the independent red-team again if Epic 2 or 3 is materially rescoped during execution. |

## Success Criteria

| # | Criterion | Verification |
| :-- | :-- | :-- |
| SC1 | Epic 1's REQ set exists and the amendment log records it | `grep -c '^REQ-AGENT-04[678]:' skills/yf-plan/spec/agents.md` returns `3` (anchored — pass-2 L1: unanchored also counts sibling cross-references in Rationale lines); the new frontmatter REQ matches root `SPEC.md`'s **actual** bullet form and is verified **id-agnostically** — `grep -qE '^- \*\*REQ-YF-EMBED-[0-9]+\*\*' SPEC.md && grep -qi 'frontmatter' SPEC.md` (two greps rather than one, so a **wrapped** bullet — root `SPEC.md` wraps at ~100 chars — still passes; pass-5 noted the single-line form was satisfiable but brittle) (pass-4: an anchored `^REQ-YF-230:` grep was unsatisfiable by a conforming edit, since root `SPEC.md` has zero line-anchored `REQ-` lines, and it also contradicted 1.3's licence to pick the next free number); `grep -q 'plan-039' SPEC.md` |
| SC1b | Issue 1.2's REQ-CLI-015 amendment landed | `grep -q 'evidence' skills/yf-plan/spec/cli.md && grep -q 'code span' skills/yf-plan/spec/cli.md`. Added per pass-3 C4 — 1.2 was previously the one SPEC issue with no verification, in a plan whose discipline is SPEC-first |
| SC2 | The red-team prompt carries all three checks | `for s in 'gate reachability' 'premise check' 'precondition cross-check'; do grep -qi "$s" skills/yf-plan/agents/red-team.md \|\| exit 1; done`. **Presence only** — SC7 is the behavioral check |
| SC3 | The investigator prompt requires the measured/inferred split | `grep -qi 'measured' skills/yf-plan/agents/investigator.md && grep -qi 'inferred' skills/yf-plan/agents/investigator.md`. Presence only |
| SC4 | The classifier regression suite passes, with `FN=0` at every step | `uv run ./skills/yf-plan/scripts/test_classify_deliverable.py` exits `0` — **repo path, never `~/.claude/skills/`** |
| SC5 | No labeled `ci-release` plan regresses to `standard` | The suite's `FN` assertion is `0` at every step and `plan-031` classifies `ci-release` after all fixes |
| SC5b | **F5 is pinned directly.** A trigger word inside a fenced block or an inline code span produces no signal | A dedicated fixture in the suite: two documents identical except that one wraps `release` in backticks; the wrapped one yields no `release` signal. Added per pass-3 (Missing) — F5's only prior trace in the criteria was SC6's signal count, which twice proved unstable |
| SC6 | **Self-test, stated as stable properties rather than a count** | `uv run ./skills/yf-plan/scripts/plan_manager.py classify-deliverable docs/plans/plan-039-james-dixson-150f79 --json` reports `evidence: prose-only` and `confidence: low`, and **every** residual signal is genuine subject-matter prose (enumerate them at execution time in `references/sc6-residuals.md`, one line each, quoting the matched text). This plan is **not** expected to classify `standard`: its subject *is* releases and signing, the self-reference limit recorded in 3.4b. Twice now a hard signal count was asserted here and twice measurement falsified it (pass-2 H1, pass-3 C1) — because the document being measured is the document being edited. Assert what is stable |
| SC7 | Every replay fixture has a recorded, honest outcome | `references/replay-results.md` contains **four** outcome lines, each `- FLAGGED` or `- MISS`, one per fixture. A `- MISS` is satisfying **only** if accompanied by a filed follow-on bead carrying the verbatim output. Pass-3 C2: requiring 4 × `FLAGGED` while 2.5 forbids tuning-until-green made "the check honestly did not fire" an unreachable state — the only route to completion would have been the confirmation bias 2.5 exists to prevent |
| SC8 | Both suites run in CI | `grep -q test_classify_deliverable CHANGE-VALIDATION.md && grep -q check_frontmatter CHANGE-VALIDATION.md` |
| SC9 | #109 closed with evidence; #113 commented and left open | `gh issue view 109 --json state -q .state` is `CLOSED` with a non-empty closing comment; `gh issue view 113 --json state -q .state` is `OPEN` |
| SC10 | _(advisory, not blocking)_ `red-team.md` stays legible | `wc -l < skills/yf-plan/agents/red-team.md` under `80`. Demoted per pass-1 C3: line count proxies badly for dilution — SC7 is the real check |
| SC11 | `reviewer.md` frontmatter parses | `uv run --with pyyaml python3 -c "import yaml,pathlib;yaml.safe_load(pathlib.Path('skills/yf-plan/agents/reviewer.md').read_text().split('---')[1])"` exits `0`. Verified discriminating: exit `1` before the repair, `0` after |
| SC12 | The tracking issue and both follow-on beads exist | Issue 5.3's tracking issue is open against `dixson3/yoshiko-flow`; `bd list --label plan-039-followon` shows **two** open beads (re-measure, install parity), the first carrying the plan-013 baseline |

**Install parity is deliberately out of scope.** Pass-2 H4 found the original SC12 named
`install.sh --force`, which does not exist here — skills are `rust-embed`-baked into the `yf`
binary at `cargo build` time and deployed by `yf skills install`, so reinstalling against a stale
binary would restore the *old* skill and fail the check even on perfect work. Re-baking and
redeploying depends on a binary release cycle this plan does not otherwise touch, so it is filed
as a follow-on bead by Issue 5.3 rather than gated here. Everything above is measured against the
**repo copy**; the installed skill is unchanged by this plan.

**Declined, explicitly: the pre-existing false-positive audit.** Plans that already carry an
operator-confirmed `deliverable_class: ci-release` accepted from a false-positive suggestion
still have `complete-gate` armed on them. Raised in pass-2's Missing and again in pass-3; it is
a **non-goal of this plan**, declined rather than dropped. Rationale: the corpus shows exactly
one such plan (`plan-031`) and its label is a **true** positive, so the population this audit
would serve is currently empty; and re-labelling completed plans mutates approved, fingerprinted
artifacts, which is a materially different and riskier operation than fixing the classifier. If
a genuine mislabelled plan is ever found, it is a one-line `set-deliverable-class` fix, not a
sweep.
