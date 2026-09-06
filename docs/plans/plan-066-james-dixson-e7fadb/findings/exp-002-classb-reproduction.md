---
type: Finding
okf_spec: OKF-PLAN
description: "All six Class-B defects reproduce; three diagnoses in issue 317 are wrong and two remedies are no-ops. Defect 5 is a DISPATCH gap, not a manifest gap."
id: exp-002-classb-reproduction
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
---
# EXP-002 — Do the six Class-B defects reproduce, and do #317's remedies close them?

## Approach Tested

**measured:** every claim below was produced by executing a command and reading its real output; **inferred:** conclusions beyond direct observation are marked as such.

**Method.** `skills/yf-drift-check` contains **nine files and zero scripts** — the engine is prose
plus one LLM sub-agent. There was nothing to execute, so the agent **built a mechanical simulator**
of §1/§2/§4/§6 implementing `SKILL.md` Workflow steps 3-4 exactly (glob→edge fan-out, edge-instance
formation by shared-`*` pairing), parsed the live manifest (**48 nodes, 52 edges, 55 §6 rows, 7 §4
rows**), and mirrored the repo tree (2453 empty files) so files could be deleted and the manifest
mutated without touching the repo.

**Headline: all six reproduce in substance. Three diagnoses are wrong. Two of four remedies are
no-ops as written.**

## 1. "No §6 trigger row for images/cards/home" — REPRODUCES in substance, **literal claim FALSE**

```
web/content/cards/01-plan.md          -> e-status-values
web/content/home/hero.md              -> e-status-values
web/content/images/formulas.d2        -> e-status-values
web/content/pages/formulas.md         -> e-status-values, e-web-formula-set
```

All three paths **do** match a §6 row — `web/content/**`. The real defect is that the row fans out
to **one narrow edge**. The A/B proof still holds: 5 shipped formulas, `formulas.md:11` says five,
`images/formulas.d2:145` says three.

**The remedy is a NO-OP.** Adding §6 rows buys nothing, because **§6 rows can only name edges that
exist**, and no node covers `web/content/images/*.d2`. The two diagram-freshness edges don't help —
`DRIFT-CHECK.md:195-196` says *"diagram-vs-prose semantics remain out of scope"*. Sequence must be
**node → edge → §6 row**.

## 2. `e-web-cli-surface` excludes `harness_desc.rs` — REPRODUCES

`cli-surface` globs are `['yf/src/cli.rs', 'yf/profiles/*.json']`. Simulator lookup for
`yf/src/harness_desc.rs` → **claimed by NO node**; §6 trigger → `NO MATCHES -> engine no-ops`.
`grep` for the path strings in the source node's files → **zero output**. The node contains none of
the facts the pages state.

**The remedy is 1 of 3 required edits.** Also needed: (b) a **§6 row for `harness_desc.rs`** — it
has none, so a widened node would still never fire on its own edit; (c) a **contract rewrite**, from
`path-resolves` ("every flag and `--harness` id exists") to `value-equal` — an existence test
structurally cannot compare a **root path string** or a `name_transform` **value**.

*Incidental:* `yf/profiles/` holds 3 of the 5 shipped harness ids, so the existing contract is
already unsatisfiable for `pi` and `agents`.

## 3. `web/content/**` fans out to `e-status-values` only — REPRODUCES exactly as stated

`lifecycle.md`, `workflows.md`, `usage.md`, `glossary.md`, `managed-files.md`, `beads-concepts.md`,
`why.md` → `e-status-values` and nothing else, a plan-status-literal subset check. #317 does not
scope the remedy. **Merge this with item 1** — they are the same fact.

## 4. No coverage of the upstream-backend claim — REPRODUCES, with a natural experiment

```
images/architecture.d2:36        "upstream tracker\nGitHub / GitLab / Jira"
skills/yf-beads-upstream.md:6    **GitHub is the only supported backend**   <- CORRECT
pages/architecture.md:98         (GitHub, GitLab, or Jira)
pages/glossary.md:151            (GitHub, GitLab, or Jira)
pages/beads-concepts.md:131      (GitHub, GitLab, or Jira)
```

**The one page that is correct is the one page an edge covers.** `yf-beads-upstream.md` is a
`skill-page` under three edges; the four wrong copies are covered only by `e-status-values`. A 4-false
/ 1-true split **precisely along the coverage boundary** — the cleanest causal evidence in the set.

## 5. `e-skill-page-desc` missed defects — REPRODUCES, but **#317's DIAGNOSIS IS WRONG**

#317 asks: report-only? INCONCLUSIVE-tolerant? never dispatched? **Measured answer: never dispatched.**

Dispatching the real `drift-verifier` returned **3 FAILs with quoted evidence**, including one #317
never named (`yf-okf.md:56` "Migration is the only write path", contradicted by `REQ-OKF-011`
`reindex --write` and `scaffold`). The edge is **fully capable**. It simply never ran.

**Root cause:** `CHANGE-VALIDATION.md:6-7` — *"Executable-only: `yf-drift-check` is excluded
(prose/LLM trigger, not a runnable command)."* Its only firing surface is the always-loaded prose
trigger. Since the defect landed: **4 commits matching the §6 glob, 4 firing opportunities, 0 catches.**

**This is systemic, not confined to prose edges.** `e-web-skill-counts` is `value-equal`, in §6 scope
from both sides, mechanically decidable — **and failing right now** (19 vs 20, utility 7 vs 8).

**#317's remedy does not address this at all.** Scope item 4 lists only manifest edits. **A manifest
edit cannot fix a dispatch gap.** Closing 1-4 and 6 while leaving 5 open produces *more edges that
also never run.*

**Correction to the issue's second half.** The yf-plan `land`/escalation/retrospective/autonomy and
`closable` items are pure **omissions**. `DRIFT-CHECK.md:53-54`: *"a page that curates or omits
repo-dev detail PASSes — only an affirmative contradiction FAILs."* Those are **out of scope by
design**, not enforcement misses. Only the `assess` case was a real miss.

## 6. `optional`/`required` enforces nothing — REPRODUCES; `skill-readme` half is **STALE**

The direct token flip, byte-identical either side:

```
BASELINE (skill-page = optional)      MUTATED (skill-page = required)
  source reach=required files=20        source reach=required files=20
  derived reach=optional files=19       derived reach=required files=19
  EDGE INSTANCES (intersection): 19     EDGE INSTANCES (intersection): 19
  source-only -> NOTHING CHECKED:       source-only -> NOTHING CHECKED:
    ['yf-okf-hygiene']                    ['yf-okf-hygiene']
```

**#317 is exactly right: flipping the token changes nothing.** Deleting a `required` README produced
the same silence.

**But the structural picture is finer than #317's:**

| | `skill-readme` | `skill-page` |
| :-- | :-- | :-- |
| §1 Reachability | `required` | `optional` |
| §4 Referencers row | **YES** | **NO** |
| Inbound edge categories | includes `required-section` | all three `behavioral` |
| Mechanical gate | **`check_skill_readme_contract.py`**, gated in BOTH CV tiers | **none** |

`check_skill_readme_contract.py` → exit 0, `"missing-readme": 0`, `--min-skills 20` vacuity floor.
**STALE CLAIM:** `skills/yf-okf-hygiene/README.md` exists (added `4cf61c7`, plan-061). #317's
"has neither" is wrong — it has a README, no page.

**Engine-spec contradiction (SPEC-first item).** `spec/checks.md` REQ-CHECK-004(a) mandates a
**node-level, whole-corpus** check ("every `required` node has a live §4 referencer"), while
REQ-CHECK-005 mandates the verifier run **only edges scoped by §6**. §6 maps globs→**edges** only.
*A node-level check with no edge to be scoped by has no firing surface.*

**The remedy already exists in this repo, in the wrong artifact.** `skill_pages.py:294-305`
implements exactly this predicate, and its own comment gives the rationale: *"a skill without one
would otherwise ship an ungoverned, drift-check-less page."* Its verdict is a **build crash**, not a
drift FAIL, and it lives in Pelican rather than the manifest.

**What the check must compare** (prototype, run):

```
=== LIVE repo ===                          === MUTATED (yf-plan README deleted) ===
skill-md -> skill-page    FAIL 20/19         skill-md -> skill-page    FAIL  ['yf-okf-hygiene']
  MISSING-DERIVED=['yf-okf-hygiene']         skill-md -> skill-readme  FAIL  ['yf-plan']
skill-md -> skill-readme  PASS 20/20       exit=1
exit=1
```

- **Set A** = dirname of `glob("skills/*/SKILL.md")` (20); **Set B** = stem of
  `glob("web/content/skills/*.md")` (19); assert `A \ B == ∅`, report `B \ A` as orphans.
- The operator is **set difference**. Edge pairing computes the **intersection** — which is
  structurally why it can never see this.
- **The source-side trigger is mandatory**: an absent file is never edited and can never fire its
  own on-edit check.

## Two incidental defects found while parsing

1. `DRIFT-CHECK.md:125` gives `e-okf-version-pin` a §2 Check Category of `value-equal` — a **§3
   Contract** term, not in the declared vocabulary `{cross-ref, contract, behavioral,
   required-section}`. **That edge selects no check engine.** Another #263 vacuous-check instance.
2. `yf-okf.md:56`'s "migration is the only write path" also appears at `skills/yf-okf/SKILL.md:213`,
   making it an `e-skillspec-skillmd` finding too — fixing the page alone leaves that edge unexamined.

## Implications for Plan

1. **Defect 5 is a different KIND of thing and is the payload.** 1-4 and 6 are manifest gaps fixed by
   editing `DRIFT-CHECK.md`; **5 is a dispatch gap** — a prose-only engine with no mechanical gate,
   measured at 4 opportunities / 0 catches.
2. **Item 1's remedy is a no-op as written**; item 2's is 1 of 3 edits. Both need re-scoping.
3. **Item 6 needs "flip to required" dropped entirely** (proven inert) and its `skill-readme` half
   corrected. Cost is low — the work is **relocation**, not invention.
4. **The engine-spec contradiction must land FIRST**, per this repo's SPEC-first rule, ahead of any
   manifest change that depends on node-level checks firing.
5. **Item 5b (the yf-plan omissions) should be withdrawn or re-filed** — omission-PASS is the
   documented semantics, so those were never enforcement misses.

## Recommendations

The Implications section above is the recommendation set; each numbered item names the plan issue or decision it binds to.
