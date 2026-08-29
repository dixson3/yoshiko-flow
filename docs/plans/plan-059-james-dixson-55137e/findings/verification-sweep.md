---
type: Finding
okf_spec: OKF-PLAN
---
# Verification sweep — every gate `Test:` and every non-`manual:` criterion, executed

## Finding: Do this plan's own instruments discriminate, and are any of them green before the work begins?

### Approach Tested

Red-team pass 3's closing recommendation, executed: **run every gate `Test:` and every
non-`manual:` Success Criterion as written, in the tree they execute in, and record the exit code
beside each.** Each command run verbatim from `plan.md`, from the repo root of the
`yf-judgement-design` worktree, `PLAN_DIR=docs/plans/plan-059-james-dixson-55137e`. Exit codes
unmodified. `manual:` criteria are excluded by definition.

**This is the SECOND run.** Red-team pass 4 audited the first and found two of its rows misread; both
corrections are below, and the machine-readable block was added so a future run is diffable rather
than re-transcribed.

### Result

**measured:** 16 of 17 executable checks are RED (SC2 was removed as redundant at red-team pass 5; its row is deleted here rather than left stale) before the work begins. **inferred:** the one green
is a genuine invariant, and establishing that took a query repair pass 4 forced.

```
RC GATE1 1
RC GATE2 1
RC SC0 1
RC SC1 1
RC SC1b 1
RC SC2b 1
RC SC2c 0
RC SC3 2
RC SC4 1
RC SC4b 1
RC SC5 4
RC SC6 4
RC SC6b 5
RC SC6c 1
RC SC8b 2
RC SC9b 1
RC SC10 4
```

| Check | rc | Reading |
| :-- | --: | :-- |
| GATE 1 severity vocabulary recorded | 1 | correctly red — the `Ratified severity vocabulary:` marker does not exist yet |
| GATE 2 escalation schema round-trips | 1 | correctly red — `escalations.toml` does not exist |
| SC0 sweep re-run green at intake | 1 | correctly red — 17 of 18 rows are non-zero, which is the point |
| SC1 vocabulary check fires by name | 1 | correctly red — `cell-vocabulary` and its fixture do not exist |
| SC1b check reports at `R` on history | 1 | correctly red |
| SC2b `escalations.md` routes by path | 1 | correctly red |
| **SC2c absent file yields no finding** | **0** | **GREEN — a genuine invariant, see below** |
| SC3 lifecycle without a second entry | **2** | red — `click` "no such command" |
| SC4 trigger carries a payload | 1 | correctly red — `review-loop-check` exits 3 today but emits no `escalation` key |
| SC4b `--assert-invocation` rejects unknown verbs | 1 | correctly red |
| SC5 escalations batch to one push | **4** | red — `click` usage error, verb missing |
| SC6 not-fired echo is a content delta | **4** | red — verb missing |
| SC6b close contract enumerates by name | **5** | red — `--list-steps` missing |
| SC6c open escalation produces a signal | 1 | correctly red |
| SC8b herdr channel test | 2 | correctly red — `test_herdr_channel.py` exists nowhere |
| SC9b #273 carries the corrected unit | 1 | correctly red — #273 still carries the withdrawn framing |
| SC10 cost-ratio instrumentation | **4** | red — verb missing |

### What run 1 got wrong, recorded rather than replaced

**Run 1 reported `SC2c -> rc=0, GREEN, correctly so`. Red-team pass 4 measured `rc=5` and called the
row false. Both were right about different things, and the distinction matters.**

- Run 1's exit code was **accurate for the command as run** — against *this* bundle, whose audit
  emits an **empty** `findings` array, so `select(.message | ...)` never evaluates and `jq` returns
  true vacuously. The sweep did not misreport its measurement.
- Pass 4 ran it against bundles that **have** findings and got `rc=5`, because
  **`plan_manager.py` findings are `{item, status, detail}` — there is no `.message` key at all.**
  The criterion was malformed and would have errored on every real bundle.
- **So run 1's number was true and its READING was wrong**: it recorded a green produced by an empty
  array and interpreted it as a verified invariant.

**The repair produced the stronger result.** SC2c now asks `(.item + " " + .detail)` and is measured
against `plan-050`, a bundle carrying **26 real findings, none about escalations** — `rc=0`. SC2c is
now a **genuinely verified** green invariant rather than an accidentally-green vacuous one.

Run 1 also recorded `SC3 -> rc=2` where pass 4 measured `rc=4`. Both are `click` usage codes and the
difference is invocation context; **which is itself the defect run 1 flagged and did not act on.**

### The polarity distinction, now with a measured instance

| kind | before the work | after the work | example |
| :-- | :-- | :-- | :-- |
| **progress criterion** | **must be RED** | green | 17 of 18 |
| **invariant criterion** | **must be GREEN** | still green | **SC2c**, alone |

A green progress criterion is the defect passes 1–4 each caught. **A red invariant would be an
equally real defect in the other direction, and nothing in the plan would detect one** — no check's
polarity had ever been stated before this sweep.

### The exit-code class problem, now acted on rather than noted

**Four rows (`SC5`, `SC6`, `SC10` = 4; `SC6b` = 5) are `click`/`jq` USAGE errors, not assertion
failures.** An exit code alone cannot distinguish *"the assertion is false"* from *"the verb does not
exist"* or *"the query is malformed"* — the same two-facts-one-signal conflation this repo has filed
three times (`doc_lint` #181, `resume-scan` #207, `pour_fidelity`).

**Run 1 wrote this down as a recommendation and did not implement it, and that omission is exactly
what let SC2c's malformed query survive.** SC0 now asserts it: no recorded code may be `4` or `5`
after execution. Implementing it in run 1 would have caught the `.message` defect mechanically.

### Cross-validation against `recheck-criteria` — and a correction to red-team pass 5

**After the placeholder fix, two independent instruments agree exactly.**

| | `recheck-criteria` (the landed §6.4 verb) | this sweep |
| :-- | :-- | :-- |
| holds / green | **`SC2c` only** | **`SC2c` only** |
| false / red | 17 | 17 |
| not evaluated | 5 (`manual:` rows) | excluded by definition |

Neither instrument knew about the other. **That agreement is the strongest evidence in the bundle
that the criteria are well-formed** — a malformed clause errors rather than evaluating, and errors
would not have matched.

**It also corrects red-team pass 5's B1, whose defect was real and whose consequence was not.** The
placeholder defect is genuine: a `<token>` is a bash **redirection**, so the clause **errors (exit 4)
instead of evaluating**. But *"the plan as written cannot reach `complete`"* does not follow from
`recheck-criteria` returning FAIL **at drafting time** — it is a **completion-time** step, and 17
progress criteria are *supposed* to be false before the work is done.

Two controls settle it:

- **`plan-052`, a `complete` plan, returns the same `rc=1` FAIL.** So the verdict is not unique to
  this bundle and did not prevent that plan from closing.
- **`plan-050`, also complete, returns `rc=2` INCONCLUSIVE** — the unmigrated-criteria case §6.4
  explicitly tolerates.

**What the fix actually bought is worth stating plainly: it converted 15 clauses from UNRUNNABLE to
HONESTLY FALSE.** That is a real and necessary gain — an unrunnable clause can never turn green —
but it is a different claim from the one this session relayed upward, and the correction is recorded
here rather than quietly dropped.

### Implications for Plan

**The plan's instruments discriminate**, and that is now measured rather than assumed.

**Epic 0 is justified by its own output, twice.** Run 1 found two defects three adversarial passes
reading the same document missed. Run 2, forced by pass 4, found a malformed query that had been
green for the wrong reason — in the criterion the sweep itself had singled out as its headline.

**The polarity table and the machine-readable `RC` block are plan artifacts, not review notes.** After
execution the before-state is unrecoverable, and a future reader checking *"did this plan's criteria
test anything?"* needs it.

### Recommendations

1. **Re-run at intake and diff the `RC` block** (Issue 0.1). Every progress row must be `0`; SC2c
   must still be `0`; **no row may be `4` or `5`.**
2. **Assert on the exit-code CLASS, not just the value** — a `4`/`5` after execution means the verb
   or query is broken, not that the assertion failed.
3. **Check every asserted literal against the issue that produces it** — REQ marker, check id, CLI
   flag, log-line prefix. Pass 4 found five that no issue named; this is mechanically checkable and
   belongs in the sweep.
4. **Do not treat SC2c's green as a defect.** The reflex to "fix" it into failing today would invert
   a correct regression guard — but do verify the query is well-formed, because run 1's green came
   from an empty array rather than from the property it claimed to test.
