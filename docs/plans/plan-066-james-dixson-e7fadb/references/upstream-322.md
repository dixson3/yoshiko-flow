---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #322 - docs yf-okf-hygiene SKILL.md: the "31 legacy,
  7 halt" figure reads as repo-agnostic and mis-sized a real plan 3.5x'
---
# Upstream #322: docs yf-okf-hygiene SKILL.md: the "31 legacy, 7 halt" figure reads as repo-agnostic and mis-sized a real plan 3.5x

- **Number:** 322
- **Title:** docs yf-okf-hygiene SKILL.md: the "31 legacy, 7 halt" figure reads as repo-agnostic and mis-sized a real plan 3.5x
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## docs — `SKILL.md`'s "31 legacy bundles, of which 7 halt" reads as repo-agnostic and mis-sized a real plan 3.5x

Measured 2026-08-30 (plan-012, EXP-004).

### The defect

`yf-okf-hygiene/SKILL.md:189-191` states:

> *"Measured over this repo: **31** legacy bundles, of which **7** halt"*

"this repo" means **yoshiko-flow**, the skill's home repo. But `SKILL.md` is read by an operator working in whatever repo the skill is *installed into*, where the sentence parses as a property of the tool. `okf_hygiene.py:432-442`'s `_objective` docstring records the same 31/7 against the same corpus, compounding it.

### The measured consequence

The `dixson3/writing` corpus:

```
bundles_checked: 15   transformed: 13   halted: 2   verdict: fail   exit: 1
```

**2 halts, not 7.** Both were `objective-divergence` and neither was a real contradiction — the legacy README `>` line was a longer restatement of the `plan.md` H1, and remediation was one editorial judgment each. A plan sized off `SKILL.md` would have budgeted 3.5x the manual work it actually needed. `bundles_checked: 15` is also arithmetically incompatible with 31, which is what made the mismatch findable at all.

### Suggested fix

Scope the figure explicitly — "measured over the yoshiko-flow corpus (31 legacy, 7 halting) as of \<date\>; your corpus will differ, run `audit` to size yours" — in both `SKILL.md` and the `_objective` docstring.

### Second, smaller item: the default-roots literal is duplicated

`roots = a.root or ["docs/plans", "docs/research"]` appears **verbatim at both `okf_hygiene.py:606` and `:642`**, once for `audit` and once for `backfill`. The two verbs can drift independently, and a caller who passes `--root` to one and not the other silently transforms a narrower set than it audited. Worth collapsing to one constant.

Related but not duplicated: **there is no config surface at all.** `os.environ` / `os.getenv` appear zero times in `okf_hygiene.py` or the vendored `okf.py`, and `yf` has no `config` subcommand — so a repo whose bundles live outside the two default roots has no durable way to record that, and must commit a wrapper script instead. Filing that as a feature request is out of scope here, but it is the reason the duplicated literal matters.

Source: `dixson3/writing` `docs/plans/plan-012-james-dixson-c324be/findings/exp-004-backfill-dry-run.md` and `exp-003-durable-root-coverage.md`.

