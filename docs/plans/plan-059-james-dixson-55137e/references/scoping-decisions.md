---
type: Reference
okf_spec: OKF-PLAN
---

# Scoping decisions — plan-059 (yf-judgement)

Recorded at Phase 1.5. These are the operator-supplied constraints that bound the design,
plus the decisions this session took under them. A cold reader needs only this file, the
three `upstream-*.md` references, and `docs/research/005-thrash-detection-and-operator-judgement/`.

## Operator-supplied constraints (verbatim intent, four, all first-class)

| # | Constraint | Consequence for this plan |
| :-- | :-- | :-- |
| S1 | **The trigger is the design.** #145's finding 4 — *"a manually-invoked skill will not be invoked"* — is proven twice in this repo (`closable` shipped and was never once run to completion; `plan_manager.py audit` never fired at the phase that mattered and four plans shipped non-conformant). A `/yf-judgement` slash command rots identically. | The automatic trigger points are decided **before** anything else. **If no reliably-firing trigger point exists, that is a finding and a reason not to build the skill.** EXP-001 is designed to be able to return that answer. |
| S2 | **Do not let the detector drive the design.** Research 005 §7.5's recommendation is: build the escalation path; treat the detector as optional and second. | The severity-vocabulary pin is a **prerequisite deliverable** and may be a separable epic worth landing on its own. The detector is downstream of it and may be descoped entirely. |
| S3 | **One-hop is supported; N-hop is a bet.** | Design the one-hop `REQ-HERDR-024` generalisation. Any N-hop content is labelled an **untested design bet** carrying the propagation budget and dedup its topology requires — never presented as a research finding. The corpus contains no N-hop data and the one supporting analogy (plan-050's seven `max-review-cycles` raises) was **withdrawn** after a direct read of that bundle's `log.md`. |
| S4 | **The honest outcome may be 'not yet'.** | An outcome of *"land the severity-vocabulary pin and the capture surface, then reassess"* is a legitimate and preferred result over shipping a 69%-PPV detector because the plan format expects a deliverable. Recall was never measured; nothing bounds how many episodes were missed; *"the agent thrashed"* and *"the reviewer was slow"* leave identical residue. |

## Operator correction, received mid-scoping (2026-08-28)

The launch prompt's constraint 2 lost a word to a shell backtick expansion. The corrected
reading, which this plan treats as authoritative:

> Shippable only under an **EXACT-MATCH** predicate: the lowercased, stripped severity cell
> must equal the literal string `high` — **not** a substring or regex search for it, and
> **NOT** any normaliser that folds `blocking` into HIGH.

Two consequences the correction carries, both adopted:

1. The substring reading silently admits `medium-high` (9 cells), `med-high` (4), `med/high` (1)
   and `medium(→high)` (1) — exactly the **downgraded-severity** cells the detector must never
   treat as HIGH. The `blocking`-folding variant **fires on `plan-026`**, whose 7-pass
   APPROVE/REVISE oscillation is deliberate re-scoping with zero recurrence. A detector that
   fires on `plan-026` is not shippable.
2. **The shippability test is one hand-picked negative control.** Three *other* control bundles
   fire under the strict predicate — `yoshiko-flow/plan-033`, `d3-pxe/plan-017`, `d3-pxe/plan-011`
   — and the 2×2 carries four false positives, **none hand-read against the re-scoping criterion**.
   Until that read is done, *"passes the shippability test"* means *"passes on `plan-026`"*.
   `Summary.md` §7.1 states this against its own interest. **Treated here as an open task, not a
   settled result** — see EXP-002.

## Decisions taken at scoping

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-1 | **Plan root: `docs/plans/`** (vault-default, no incubator). | `pwd` is outside `Incubator/`; §1.2 auto-detect resolves it without an interaction. |
| D-2 | **Dispositions: #269 `include`, #264 `partial`, #145 `partial`.** | #269 is the payload. #264's wording fix already landed and is validated separately; only the durable half (provenance-derived autonomy + one-hop generalisation) routes here. #145 is mined for synergies, not resolved — its consumer half explicitly waits on corpus accumulation. |
| D-3 | **Escalation is exercised, not merely designed.** The operator instructed this session to use the one-hop escalation mechanism deliberately and record how it feels to use. | Dogfooding is the only counterfactual arm available: research 005 §9.4 records that no such arm exists in the corpus. Each escalation this session raises (or deliberately declines to raise) is recorded in `findings/escalation-log.md` as design evidence. |
| D-4 | **Four investigations, dispatched to isolated sub-agents.** EXP-001 trigger-point survey, EXP-002 severity-vocabulary census + the un-done control read, EXP-003 the #145 synergy audit, EXP-004 the escalation-mechanism and question-artifact survey. | S1 makes EXP-001 potentially plan-terminating, so it must be able to refute the scoping decision that commissioned it (AGENTS.md "Delegation to sub-agents" — investigators carrying the drafting conversation are primed toward confirming it). |
| D-5 | **Work happens in the `yf-judgement-design` worktree, off `main`.** | Operator instruction, mid-session: three sessions shared one checkout and unrelated commits had already landed on the wrong branch. The bundle was moved before any commit existed. |
| D-6 | **"Push a milestone" means `herdr agent prompt "$YF_PARENT_PANE" …`, never `git push`.** | Settled by existing content, so not escalated: the stop list independently forbids outward-facing writes, and `--wait` — which the launch contract forbids — is a flag on `herdr agent prompt`. Recorded because a wrong reading here would have violated a stop class. |

## Scope boundaries

**In scope:** the trigger points; the question artifact and where it is written; the one-hop
resolution predicate; the severity-vocabulary pin; the carve against `yf-herdr` and
`yf-retrospective`; an explicit go / not-yet recommendation.

**Out of scope:** the `yf-retrospective` consumer half (#145 keeps it); the `yf-herdr` transport
itself (channel, not decision); N-hop propagation as a shipped default; any claim about detector
**recall**, which was never measured.
