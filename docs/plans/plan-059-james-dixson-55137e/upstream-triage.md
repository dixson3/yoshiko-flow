---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: yf-judgement escalation design

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #269 — New skill: yf-judgement — detect when a plan needs OPERATOR JUDGEMENT and escalate a question, rather than attempting another fix

> > **Written to be read cold.** The empirical basis is `yf-research` 005 (PR #267,
> `docs/research/005-thrash-detection-and-operator-judgement/`), a deep-mode study over **114 plan
> bundles and 301 r...

**Disposition:** partial
**Notes:** **IN:** the escalation path, shipped as a capability inside `yf-plan` and `yf-herdr`. **OUT (1):** the severity-decay detector — answered **NO** on evidence. EXP-002 finished the control hand-read research 005 left undone and the strict `high` predicate **fails its own shippability standard**, firing on `plan-029` and `plan-033`, both deliberate re-scoping by their own phase logs. `plan-026` was not the exception; it is the one bundle whose reviewer wrote `medium (blocking)`. **OUT (2):** the `skills/yf-judgement/` directory — deliberately not created, because a new manually-invoked surface is precisely what this issue's own cited finding 4 predicts will never be invoked. Was `include` in the first draft; corrected at red-team pass 1 because only one of three halves ships.

## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:** partial
**Notes:** **Not resolved here — mined for synergies, and two of the six claimed DO NOT HOLD.** Claim 5 ('complementary in time') fails: the two skills compete for adjacent hooks in the same loop and touch the same retrospective rows. Claim 6's 'data-starved' half is stale — the corpus is 96 entries across 13 bundles, not the 7 the issue records. **IN:** the decision that `plan-retrospective.md` is **rejected** as the escalation surface (append-only, no update verb, and the corpus's one `(pending)` answer is still pending), so `escalations.md` is a sibling rather than an entry kind; and filing the `yf-drift-check` edge #145 announced and never landed. **OUT:** the escape-rate consumer, the forensic attribution engine, and the prevention-category vocabulary — all stay with #145.

## #264 — yf-herdr: AUTONOMY clause does not survive a phase boundary — subordinate goes idle after pushing

> ## Summary

The mandatory launch contract's **AUTONOMY** element (REQ-HERDR-015a) is insufficient to keep a
subordinate running across a **phase boundary**. Observed live during `yf-research` 005: the...

**Disposition:** partial
**Notes:** **IN:** the durable half its own follow-up routed here — the one-hop `REQ-HERDR-024` generalisation (gaining a third arm, *look*, measured in this session's own dogfooding) and provenance-derived autonomy. Plus three undocumented channel facts EXP-004 measured. **OUT:** the AUTONOMY wording fix, which already landed and is validated separately by the three-boundary natural experiment; and **N-hop, declined as an untested bet** — EXP-004 measured the live topology at depth 1, fan-out 2, and established that N-hop state is *not representable* in what `YF_PARENT_PANE` seeds, since a child spawning a grandchild silently overwrites the chain.

## #270 — yf-plan: `plan-review.formula.toml` has NEVER been poured

> Filed during this plan's investigation, from escalation E-3. The only structurally-mechanical mid-burn review gate in yf; zero matching beads across all 1,245; 27 review passes added to git since it landed (`57a21e3`, 2026-08-24).

**Disposition:** deferred
**Notes:** Filed from this plan's escalation E-3 and scoped out by operator decision. Retained here because it is load-bearing: Issue 3.4 and SC7 keep the escalation payload movable onto the `plan-review` wisp gate without redesign, and fixing #270 upgrades this plan's trigger for free.
