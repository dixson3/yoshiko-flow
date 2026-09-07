---
type: Finding
okf_spec: OKF-PLAN
description: "D4 refuted as scoped. A declared required set over derivable classes newly FAILs 17-18 of 20 pages and EVERY failure is an artifact. Exactly one class has a clean signal."
id: exp-002-required-set-derivability
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# EXP-002 — Is the declared required set derivable?

## Approach Tested

**measured:** every claim was produced by running a real extraction command per surface class,
building a prototype that computes required-set coverage, running a corpus census over all 20 skill
pages, and running a negative control that redacts a documented surface and confirms the check
flips. **inferred:** marked where stated.

## Result — D4 IS REFUTED AS SCOPED

**A naive declared required set over the derivable frontmatter classes newly FAILs 17-18 of 20
currently-green pages, and EVERY ONE of those failures is an artifact.**

```
class                 reqset  missing  pages FAILing   adjudication
skill-group               20       13        13        ALL artifacts — generated block
depends-on-tool           34       12        11        ALL artifacts — generated block
formula                    5        5         2        ALL artifacts — curated out legitimately
script-verb (SKILL-named) 60       26         5        ~25 artifacts, ~1 real
slash-verb                19        0         0        clean
```

The `skill-group` and `depends-on-tool` data is **emitted by `skill_pages.py:203-217`** into the
generated "At a glance" block — `DRIFT-CHECK.md:207` already declares it out of scope because it
*cannot drift*. Requiring it of the authored prose would produce a **24-failure false-positive
burst that discredits the check on its first run**. (9 of the 12 `depends-on-tool` misses are the
token `uv`.)

## The decisive finding: NO mechanical predicate exists for script verbs

Q3 asked what separates the ~5 verbs a page owes a reader from the ~41 it does not. Measured:

```
grep -cE 'hidden\s*=\s*True|deprecated\s*=|short_help=' plan_manager.py   -> 0
grep -nE '@cli\.command\([^)]*,' plan_manager.py                          -> no output
```

**Every one of the 40 registrations is `@cli.command("<name>")` or bare. There is no bit in the
source to read.** And `spec/cli.md` REQ-CLI-006 frames the *entire* set as *"the mechanical
operations SKILL.md delegates"* — no user-facing partition is declared anywhere.

| Predicate | Selects | Verdict |
| :-- | --: | :-- |
| P1 every `@cli.command` verb | 48 | 58 missing, 6/20 pages FAIL — WRONG |
| P2 verb named in `SKILL.md` | 30 | ~20 false positives on `yf-plan.md` alone |
| P3 per-verb visibility attribute | **0** | does not exist |
| P4 verb named in `README.md` | 7 | closest — **but README is hand-authored prose** |

**So the required set for script verbs is irreducibly editorial.** P4 is nearest-correct and is
obtainable only by reading a document a human maintains — which is exactly
`check_amendment_log.py:20-23`'s stated soundness limit, reintroduced.

## Exactly one class has a clean signal

**Slash sub-verbs.** Required-set 24, **1 newly-failing page** (`yf-change-validation infer`),
**0 generated-data artifacts**, and the negative control fires specifically:

```
redacted 6 'land' and 3 'capture' occurrences; readback confirms 0 of each
BEFORE: MISSING 25    AFTER: MISSING 27
  MISSING  [slash-verb]                capture
  MISSING  [script-verb(SKILL-named)]  land
```

It names **exactly** the two redacted surfaces. The check has been observed to fail, and to fail
specifically.

## The real blocker is upstream: `## Invocation` is NOT a schema

```
12 of 20 skills have NO '## Invocation' section at all
the 8 that do use >= 4 INCOMPATIBLE shapes:
  bullet list · fenced + subcommand table · fenced free-form lines · a bare `uv run` fence
```

Six of the twelve are `user-invocable: true` — `yf-beads-hygiene`, `yf-beads-init`,
`yf-beads-upstream`, `yf-diagram-authoring`, `yf-herdr`, `yf-research`. A required-set check keyed
on this section is **silently vacuous for 60% of the corpus** — the same silent-green failure mode
plan-066 measured.

Corroborated independently: a widened scan found `SKILL.md` documents `/yf-beads-upstream init`
while its web page contains **zero** `/yf-beads-upstream <verb>` strings — a real omission that
today PASSes *and* that the `## Invocation`-scoped predicate also cannot see.

## Implications for the plan

1. **D4 must narrow to one class in v1** — slash sub-verbs. Everything else is either generated
   (artifact) or editorial (underivable).
2. **Normalising `## Invocation` into one parseable shape is a PREREQUISITE, not a follow-on** —
   and it is a cheaper, more honest epic than any predicate engineering.
3. **The plan must state the script-verb limitation rather than claim a derived set.** The rule
   makes script-verb coverage *visible in review*; it does not mechanise it.
4. **Side finding for the manifest epic:** `e-skill-page-sections` (`DRIFT-CHECK.md:140`) is nearly
   vacuous — §5 carries exactly one `skill-page` row, an existence-of-a-non-trivial-body check.
   That row is the natural home for the new required set.

## Recommendations

1. **v1 required set = slash sub-verbs only.** Contract: every sub-verb the skill's `## Invocation`
   declares must be named on its web page.
2. **SPEC-first epic normalising `## Invocation`** to the bullet form (`yf-plan` already uses it),
   adding it to the 6 `user-invocable: true` skills that lack it — converting 6 vacuous checks into
   live ones. Add a **vacuity floor** so a shape change cannot silently zero the required set.
3. **Do NOT require generated data** (`skill-group`, `depends-on-tool`, `depends-on-skill`).
4. **If script-verb coverage is wanted, make the list a DECLARED artifact** — a
   `user-facing-verbs:` frontmatter key, or a `public=True` marker on `@cli.command`. That turns a
   hand-maintained list into one a machine can read and a drift edge can guard. Code change to 6
   manager scripts: its own plan.
5. **Do not extend the set to formula names** — all 5 are on `formulas.md` and already guarded.
