---
type: Finding
okf_spec: OKF-PLAN
description: "The failure list the LANDED rule produced. 15 mechanical omissions across three checkers, plus 6 one-page-deep partials. This list, not EXP-003's table, is what Epic 2 repairs."
id: omission-inventory
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# The omission inventory — produced by the rule, not by hand

## Why this file exists and EXP-003's table does not replace it

D2 sequences the rule **before** the repairs precisely so that the work list is **derived**
rather than written. The precedent is plan-066's D1, where a checker-derived inventory found 4
defect sites the source issue never listed and corrected an undercount from ~4 to 26. The inverse
order lands a rule green by construction and proves nothing about whether it would have caught the
omissions it was written for.

**measured** on branch `plan-067-james-dixson-de852a-execute` at the close of Epic 1, by running
every checker over the corpus and recording its exit code and named findings verbatim.

## The baseline, before this plan

```
check_web_counts:          47 files, 21 claims, 0 mismatches        exit=0
check_skill_page_contract: A=20 B=20, 0 missing, 0 orphan           exit=0
```

Both green — while the omissions below all existed. That is D2's premise, confirmed a second
time.

## Population A — MECHANICAL, produced by the landed rule (15)

Each row is a checker's own finding, quoted. These FAIL today and are what Epic 2 repairs.

| # | Surface | Checker | Class |
| :-- | :-- | :-- | :-- |
| A1 | `/yf-beads-hygiene restore` | `check_required_set.py` | declared slash sub-verb, documented nowhere |
| A2 | `/yf-beads-upstream status` | `check_required_set.py` | declared slash sub-verb, documented nowhere |
| A3 | `/yf-beads-upstream pull` | `check_required_set.py` | declared slash sub-verb, documented nowhere |
| A4 | `/yf-change-validation infer` | `check_required_set.py` | declared slash sub-verb, documented nowhere |
| A5 | `/yf-okf migrate` | `check_required_set.py` | declared slash sub-verb, documented nowhere |
| A6 | `/yf-okf-hygiene reindex` | `check_required_set.py` | declared slash sub-verb, documented nowhere |
| A7 | `prune-private` | `check_cli_to_page.py` | shipped subcommand, **destructive**, documented nowhere |
| A8 | `--prune-formulas` | `check_cli_to_page.py` | shipped flag, documented nowhere |
| A9 | `--also-quarantine` | `check_cli_to_page.py` | shipped flag, documented nowhere |
| A10 | `--quarantine-dir` | `check_cli_to_page.py` | shipped flag, documented nowhere |
| A11 | `--shared-root` | `check_cli_to_page.py` | shipped flag, documented nowhere |
| A12 | `--no-skills` | `check_cli_to_page.py` | shipped flag, documented nowhere |
| A13 | `--rules-only` | `check_cli_to_page.py` | shipped flag, documented nowhere |
| A14 | `--path` | `check_cli_to_page.py` | shipped flag, documented nowhere |
| A15 | `yf-plan/lander` | `check_agents_set.py` | in-scope pipeline agent, unnamed on `workflows.md` |

**A4 is EXP-002's named example** and the one EXP-003's own slash-verb extractor returned green
over — the false green that experiment retracted by amendment. The rule now sees it.

**A7 is D4b's headline.** It is live, it is destructive, and no check anywhere could reach it
before the CLI→page direction existed, because both of `e-web-cli-surface`'s declared failure
directions ran page→CLI.

## Population B — PARTIAL COVERAGE, each hitting exactly ONE file (6)

plan-066 repaired these to a single site. One file is not coverage: a reader who does not open
`yf-plan.md` cannot reach any of them.

| # | Token | Files carrying it | Only site |
| :-- | :-- | --: | :-- |
| B1 | `--sweep-gates` | 1 | `web/content/skills/yf-plan.md` |
| B2 | `retrospective` | 1 | `web/content/skills/yf-plan.md` |
| B3 | `plan-retrospective` | 1 | `web/content/skills/yf-plan.md` |
| B4 | `RE-NNN` | 1 | `web/content/skills/yf-plan.md` |
| B5 | `lander` | 1 | `web/content/skills/yf-plan.md` |
| B6 | `checkpointed` | **0** | — (the autonomy level's own name is absent site-wide) |

`land --dry-run` scores **0** as a phrase, and `closable` and `escalation` score 2 each — the two
plan-066 called repaired are genuinely repaired, and the two it called partial genuinely are.

## Population C — NAMED BY THE PLAN, not reachable by any current checker (2)

Recorded so they are not mistaken for absent defects:

| # | Surface | Why no checker reaches it |
| :-- | :-- | :-- |
| C1 | `custom.upstream.owner_on_create` | a config key, not a CLI surface or a declared sub-verb; no source-of-truth extractor exists for the `custom.upstream.*` namespace |
| C2 | `upstream.py mappings` | a SCRIPT verb, which `REQ-CHECK-010` excludes **by name** as irreducibly editorial (40 registrations, zero visibility metadata) |

**C2 is the honest limit, stated rather than quietly repaired into invisibility.** The rule makes
script-verb coverage visible in review; it does not mechanise it. Both are still repaired by Issue
2.3 — the point is that their repair is EDITORIAL, and nothing will catch them regressing.

## What the rule did NOT produce, and why that is a result

`check_web_counts` reports **0 mismatches and 0 unenumerated groups** over the real corpus. That
is not a vacuous green: the code-side controls show it exits 1 when a member is moved between
groups, when two enumerated members are deleted with the count left unchanged, and when a group
states a count while listing no ids at all. plan-066 had already repaired the group memberships,
so this surface is genuinely clean — which is exactly the distinction between a rule that lands
green **honestly** and one that lands green **by construction**.

## Against the declared band

The band is 57 strict / **73 working** / 114 lenient, with 193 named as the REJECTED reading.
This inventory holds **23** items (15 + 6 + 2) because it counts only what an ENUMERABLE
extraction can name. The gap to 73 is the prose half EXP-003 adjudicated by reading — real, but
not mechanically derivable, which is `REQ-CHECK-010`'s declared scope working as designed rather
than a shortfall.
