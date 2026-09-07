---
type: Finding
okf_spec: OKF-PLAN
description: "Every Class-B (instrument / pipeline) defect this plan touched, dispositioned BY NAME — CLOSED with the artifact that closes it, or FILED with an owner. Never implied by a green build."
id: classb-disposition
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# Class-B disposition — fourteen items, each named

## Approach Tested

**measured:** each row names the artifact that closes the item and the command that demonstrates
it, or the bead it is filed as. **A green build is not a disposition.** The whole Class-B thesis
is that coverage and detection are different things, so "everything passes" is precisely the
evidence that does not settle these — a checker that was never observed to fail and a checker
that has nothing to find produce the same green.

Class-A is a **content** defect (a page says something false). Class-B is an **instrument**
defect (nothing could have told you). This plan is mostly Class-B by construction: its premise is
that the corpus was green while the omissions existed.

## Result

| Item | Disposition | Owner / closing artifact |
| :-- | :-- | :-- |
| B1 — a set-membership claim FAILs on a wrong member but not a MISSING one | CLOSED | `REQ-CHECK-013`; `check_web_counts.py` computes `missing` beside `wrong`. Control: two members deleted with the count unchanged exited 0 before, exits 1 now |
| B2 — the `members is None` branch let a group evade the rule entirely (#376) | CLOSED | Issue 1.1b; an unenumerated group is now a FINDING with its own `not_checked_groups` count. Control: a `beads (5)` claim listing no ids exits 1 |
| B3 — `e-web-cli-surface`'s two failure directions were BOTH page→CLI | CLOSED | `REQ-CHECK-011`; `check_cli_to_page.py`, a set difference with an exit code. Reaches `prune-private`, which was documented nowhere |
| B4 — no edge covered the pipeline agent set | CLOSED | `REQ-CHECK-014`; `e-web-agents-set` + `check_agents_set.py`, SCOPED. Baseline 15/16, `lander` the single absence, now 16/16 |
| B5 — `user-invocable` read as two-valued from a tri-state source | CLOSED | `REQ-CHECK-012`; populated at all 20 producers, `check_user_invocable.py` asserts it, and the consumer now warns instead of asserting a falsehood |
| B6 — the authored-page guard was EXISTENCE-only (#374) | CLOSED | Issue 5.7; the guard measures renderable prose. Control observed end to end: a zero-byte page makes the build exit 1 |
| B7 — `## Invocation` was not a schema, so a required-set check keyed on it was silently vacuous for 60% of the corpus | CLOSED | Issues 0.2/0.3; one bullet shape, present on all 15 user-invocable skills, with `REQ-CHECK-010`'s vacuity floor |
| B8 — 20 hand-authored per-skill diagrams would be 20 NEW drift surfaces | CLOSED | Epic 5; generated from a shared model, with `--check` in FAST and FULL. You cannot omit an edge from a diagram you did not write |
| B9 — two readers of one frontmatter (page vs diagram) | CLOSED | Issue 5.1; `web/plugins/skill_model.py` is the one reader. Two grammars disagree exactly where it matters — which is B5's own cause |
| B10 — `render-bytes-match` used `glob`, not `rglob` | CLOSED | Found while verifying Epic 3: it re-rendered 4 of 9 while reporting "all identical". The per-formula subdirectory was structurally invisible to it |
| B11 — `plan067_checks.run_cmd` passed `cwd` positionally | CLOSED | A caller needing to run inside `web/` got a `TypeError`, reported as INCONCLUSIVE. `cwd` is now an overridable default |
| B12 — SC24b's own predicate matched NEITHER spelling the guard uses | CLOSED | It searched for `os.path.exists` / `.is_file()` against a guard using `os.path.isfile`, and reported INCONCLUSIVE about code that was right there |
| B13 — `plan066_checks.FORMULAS_D2` conflated the site plan-066 REPAIRED with the current subject | CLOSED | Issue 6.0; split into `FORMULAS_D2_HISTORICAL` and `FORMULAS_DIAGRAM`. Repointing the single constant would have falsified the historical record |
| B14 — `check_web_counts`'s region logic is SHAPE-SPECIFIC (one `is_d2` switch) | FILED | bead `yf-w57p`, owner: **operator decision at the Upstream write authorization gate**. Filed on its own merits, independent of archify |

## The one item deliberately NOT closed, and why

**B14 is filed, not fixed.** It is latent rather than live: `DEFAULT_CORPUS` expands only `.md`
and `.d2`, so nothing in the shipped recipe reaches the defect today. It bites the moment anyone
points `--corpus` at a third shape, and the failure mode is a burst of confident false FAILs —
the shape most likely to get a checker distrusted and then disabled. Twice observed, on two
different third shapes: plan-066 EXP-001 recorded it as a latent hazard, and this plan's Epic 3
measured it directly (7 false mismatches on a `.json`, 63 on an `.html`).

It is filed as a **local bead only**. The operator chose *exploration*, not adoption, so no
migration issue was created; whether `yf-w57p` goes upstream is theirs to decide at the Upstream
write authorization gate.

## What is DECLARED rather than dispositioned

**Script-verb coverage is not a Class-B item to close — it is a stated limit.** Measured:
`plan_manager.py` carries 40 flat `@cli.command` registrations with **zero** visibility metadata,
and `spec/cli.md` `REQ-CLI-006` frames the entire set as internal delegation. There is no bit in
the source to read. `REQ-CHECK-010` excludes the class **by name** and every relevant checker
says so in its own `not_checked` output. Recording it as "open" would imply a fix exists that
nobody has done; recording it as "closed" would be false. It is neither — it is declared.
