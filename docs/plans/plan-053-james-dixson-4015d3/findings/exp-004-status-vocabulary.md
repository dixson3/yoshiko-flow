---
type: Finding
okf_spec: OKF-PLAN
id: exp-004-status-vocabulary
description: The 16-site change-set for adding a plan status, why `incomplete` is disqualified, and the vacuous drift edge that was supposed to protect it
---

# EXP-004: what must move to add a status, and what the status should be

**Verdict: D-1's DECISION survives; D-1's STATED RATIONALE does not. The `e-status-values`
drift edge that the rationale named as the reason "everything must move together" is
CURRENTLY VACUOUS — it cannot fail. The 16-site change-set is real; the safety net named for
it is not.**

## The correction to my own scoping note

I recorded D-1's cost as *"the vocabulary is a declared `DRIFT-CHECK` authority edge
(`e-status-values`), so SPEC, the Phase Model line, `STATUS_SEVERITY`, `_is_parked` and the
§5.1 execute filter must move together."*

The edge exists. It does not do that.

`DRIFT-CHECK.md:146` defines it as `field-set-subset`, `skill-md` → `agent`, and its §6 trigger
scope (`:228,230`) is **only** `skills/*/SKILL.md` and `skills/*/agents/*.md`. ~~Measured: **no `skills/yf-plan/agents/*.md` file contains a status literal or an
`update-status` call**, so the target-side set is empty and the subset check passes
trivially.~~

> **CORRECTED at pass 2 (C17). This finding's central premise was WRONG.**
> `agents/coordinator.md:238` and `agents/reconciler.md:64` both carry `` `complete` ``, so the
> target-side set was **never empty**. The edge is vacuous for a *different* reason: `complete`
> **is in** the declared vocabulary, so the subset check passes because the subset genuinely
> holds — not because there is nothing to check.
>
> **The conclusion survives; the mechanism does not**, and the difference is load-bearing: a
> control built on the empty-set premise is unsatisfiable (measured 2 of 23 agent files, and
> *worse* — 6 of 33 — after the widening the finding recommends). Issue 1.6b was re-derived
> from the corrected mechanism: what the edge must catch is a status literal **outside** the
> declared vocabulary. Issue 5.4 was likewise narrowed to one branch, because the widening
> branch this finding recommends makes the ratio worse rather than better.

The edge's scope reaches none of `spec/*.md`, `SPEC.md`, `plan_manager.py`,
`_shared/doc_lint.py`, or `_shared/document_types/*.toml` — which is the part of this section
that stands unchanged.

**The edge named as the guardrail for this change is the one edge that cannot detect the
change failing.** That is worth an issue in this plan on its own.

## The change-set, and the failure direction of each

> **The "16 sites" count in this section's original heading is WITHDRAWN** (pass-3 C35, pass-4 C52): the table below enumerates ~18 rows, and a fourth `web/content/**` site was found after it was written. `ctl-208-vocabulary-sites` enumerates; no count is recorded.

| Site | On unknown status |
| :-- | :-- |
| `plan_manager.py:1287` `update_status` | **silent, exit 0** — the #208 defect |
| `plan_manager.py:2969` `_is_parked` | fails **open → invisible** |
| `_shared/doc_lint.py:114-131` `STATUS_SEVERITY` | **fails OPEN** — declared severity survives → spurious `PASS` |
| `document_types/plan.toml:125`, `upstream-triage.toml:57`, `plan-relations.toml:106,113` | **fail OPEN** — check silently skipped |
| `doc_lint.py:684` `stale-measured-literal` | fails **closed** (accidental) |
| `skills/yf-plan/scripts/{doc_lint.py,document_types/*.toml}` | byte-identical sync'd mirrors |
| `SKILL.md:161` (source of truth), `:829` §5.1, `:1661` parked nudge | prose |
| `yf-herdr/SKILL.md:44` | a second skill restating the rule |
| `web/content/**` × 4 | published lifecycle tables, no edge covers them |

**Non-consumers, measured:** `yf/` (Rust) carries **zero** plan-status literals. ~~All seven
`skills/yf-plan/agents/*.md` carry none.~~ **CORRECTED (pass-2 C17): two of the seven do** —
`coordinator.md:238` and `reconciler.md:64`. `plan_extract.py`, `pour_fidelity.py`, `okf.py`,
`gate_consistency.py` and every `formulas/*.toml` carry none.

**Three SPEC counts break, not one.** `REQ-STATUS-001` (`spec/phases.md:27`) states *"Exactly
**9** status values exist"* with `Verification: grep 'Status values:' SKILL.md lists all 9`;
`REQ-STATUS-002` pins `grep -c 'py update-status' SKILL.md` at **9**; `REQ-CLI-024`'s rationale
says *"writes **nine** different statuses"*. All three are grep-verifiable and all three go
stale.

**A scope REDUCTION, though:** #208's "ineligible for `execute`" consequence is enforced by
**prose only** (`SKILL.md:829`). `_resume_scan` reads the fingerprint and never the status. So
adding a status needs **no execute-path code change** — cheaper than D-1's framing implied.

## Fail-closed is free — but only in its narrow form

Strictest profile = `{WARN: ERROR}`. Two variants, run over the whole repo:

```
BASELINE  PASS  files=917  errors=0   warnings=636
NARROW    PASS  files=917  errors=0   warnings=636      ← status present AND unrecognised
BROAD     FAIL  files=917  errors=31  warnings=605      ← `.get(status or "", STRICTEST)`
```

Corpus status census: `{complete: 52, investigating: 1}` — **zero out-of-vocabulary statuses
today**, so the narrow mapping changes **0 of 917** documents.

The **broad** one-liner — the obvious implementation — breaks **31 documents**, all with
`bundle_status: None` (22 research artifacts, 2 `sources.md`, 2 `Summary.md`, 5 `SKILL.md`),
and turns the repo's own `doclint` FAST-tier row permanently red. That is plan-048 D-10's
warning: `bundle_status` is null off the plan axis, so there is no status escape hatch there.

**So the fix is a two-line predicate, not a one-line `.get()` default**, and it needs a
**two-armed** success criterion — arm 1: an unrecognised status flips `PASS`→`FAIL`; arm 2: a
null-`bundle_status` document is **unchanged**. Without arm 2 the naive fix ships.

Positive control on a copied bundle:

| `status:` | baseline | narrow fail-closed |
| :-- | :-- | :-- |
| `investigating` | PASS E=0 W=1 | PASS E=0 W=1 |
| `approved` / `complete` | PASS E=0 W=0 | PASS E=0 W=0 |
| `incomplete` | **PASS** E=0 W=1 | **FAIL** E=1 W=0 |
| `parked-do-not-resume` | **PASS** E=0 W=1 | **FAIL** E=1 W=0 |

## The name: `abandoned`, and `incomplete` is disqualified

**`incomplete` — the operator's own coinage in #208 — must not be adopted.** It collides
head-on with the **reviewer agent's verdict vocabulary** (`agents/reviewer.md:6`,
`SKILL.md:488`: `Verdict: PASS | INCOMPLETE`), and `doc_lint.py`'s module docstring already
carries a disambiguation line written specifically to keep that word out of the linter's
namespace: *"`INCOMPLETE` is the reviewer agent's vocabulary and never appears here."*
Promoting it to a status reinstates the ambiguity that line exists to remove. It also *reads*
as "not finished yet" rather than "stopped".

`parked` is disqualified harder — it is already a derived boolean **and** a subcommand, so
`{"status":"parked","parked":false}` would be a legal record. `cancelled/canceled` carries a
US/UK spelling split, fatal for an exact-match enum.

**`abandoned` has a direct in-repo precedent.** `yf-incubator` already ships
`incubating | scoping | exploring | converging | concluded | parked | abandoned`
(`SPEC.md:35`) — with `parked` and `abandoned` as **distinct** values, exactly the distinction
yf-plan needs. Zero collision with doc_lint severities (`E|W|R`), verdicts
(`PASS|FAIL|INCONCLUSIVE`), red-team verdicts, or bd bead statuses.

## The design: (c), with (d) as its diagnosis

Option (d) — *"the real gap is that `executing` has no exit but `complete`"* — is **correct as
diagnosis and fails as a conclusion**. REQ-PLAN-002 pins the machine with no abandonment edge
anywhere. But an edge needs a destination node, and `status` is the only durable
machine-readable lifecycle signal in the system. You cannot add the missing exit without
adding the node.

Today an abandoned plan must either **lie** (`complete`, which also fires the completion gate
and cascade close) or **sit in `executing` forever** — where it is not `parked`, never surfaces
in the land-the-plane nudge, and sits under `{WARN: REPORT, ERROR: REPORT}` **permanently
unjudgeable** by the linter.

Option (a), "deliberately not resumable", is **refuted by the incident that motivated it**:
#208 says astrospike plan-001 *"could not be brought back without hand-editing"* — the operator
wanted it back. A status that forbids revival makes the reported problem worse.

**Contract:** IN from any non-`complete` status. OUT by **exactly one edge, → `drafting`** — a
revival re-earns `ready-check`/`approved` through the normal path. Explicitly **no
→ `complete`** edge, which would launder an abandon into a success. Not execute-eligible; not
`parked` (the nudge text is literally *"run /yf-plan execute"*, exactly wrong here — give
`list` its own `⏹ ABANDONED` tag); `STATUS_SEVERITY` profile `{WARN: REPORT, ERROR: REPORT}`,
same row as `complete`, because frozen history is not re-judged (REQ-DATA-025); **deliberately
excluded** from all three schema `statuses` lists, stated rather than inherited.

## Tests

`test_update_status_gate.py` is the home for warn-on-unknown — but note
`test_the_gate_is_scoped_to_approved_only:111` loops over known statuses asserting **exit 0**,
so **the warn must be stderr-only, exit 0**, and `abandoned` must be added to that tuple.
`_shared/test_doc_lint.py:443` already has the parallel `promote = false` block for the
fail-closed test.

**Absence of evidence:** no test anywhere asserts anything about an unrecognised status.

## Two issues this plan should add

1. **Make `e-status-values` non-vacuous** — widen its §6 trigger scope to `skills/*/spec/*.md`,
   `plan_manager.py` and `_shared/doc_lint.py`, or replace the ~~empty~~ `agent` target node with
   the real restatement set. As written it cannot fail.
2. **Follow-on:** `skills/yf-incubator/scripts/incubator-index.py:47` defines `STATUS_VALUES`
   as a set literal that is **never referenced anywhere else in the file** — grep returns
   exactly one hit. The sibling skill declares an enum and enforces nothing: #208's defect
   class, one skill over, unfiled.
