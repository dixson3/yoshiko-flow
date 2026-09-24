---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #298 - OKF/spec-family hygiene: ambiguous REQ ids, stale
  authority pointers, unmigrated okf_version split, phantom init verb'
---
# Upstream #298: OKF/spec-family hygiene: ambiguous REQ ids, stale authority pointers, unmigrated okf_version split, phantom init verb

- **Number:** 298
- **Title:** OKF/spec-family hygiene: ambiguous REQ ids, stale authority pointers, unmigrated okf_version split, phantom init verb
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::medium

## Body

## Four spec-family hygiene defects: ambiguous ids, stale authority, an unmigrated version split, a phantom verb

Grouped because each is a **specification artifact that no checker reads**, so all four survive every green run.

### 1. `REQ-PORT-010` resolves to TWO unrelated requirements — `yf-ne3e`

The id is declared in two different specs with different content, so any citation of it is ambiguous. Found while working #165.

Related and measured independently during plan-057: Issue 0.5 cites **`REQ-CLI-018`**, which is `verify-reconcile` — the harness contract it means is `REQ-CLI-029`. **Six red-team passes read that line** without checking the id resolved to what the sentence described (recorded as plan-057 RE-002). An id that resolves to the wrong requirement and an id that resolves to two are the same failure to check.

### 2. Two stale-authority strays in the OKF spec family — `yf-egfm`

Two statements in the `OKF-*` family assert authority that has since moved — the baseline pin and the reserved-file source table — with no pointer to the current owner. Enumerate and re-point.

Note plan-057 has now re-pinned `OKF-BASELINE.md` **by content hash** and verified live that upstream mutates content under an unchanged `Version 0.2` label. Whether that discharges the baseline half should be checked before this is worked.

### 3. The corpus splits 21-at-`okf_version` 0.1 / 11-at-0.2 — `yf-4ye0`

Of the bundles carrying a root `index.md`, `okf_version` frontmatter is split across two baseline versions with **no migration path declared and no checker that notices**. A bundle pinned to 0.1 is judged by 0.2 rules silently.

plan-057's backfill has since changed the population — re-measure before working this.

### 4. `yf-okf` advertises verbs `okf.py` does not register — `yf-9ovz`

**Partly fixed by plan-057.** `assess` is gone from `SKILL.md` (measured: 0 rows) and `check-assess-verb-gone.sh` now guards it. But `okf.py --help` registers `check migrate reindex scaffold` — **`init` is still advertised and still absent** (1 mention in `SKILL.md`).

plan-057's instrument was deliberately scoped to *engine-backed* verbs, because `init` is legitimately non-engine-backed per `SKILL.md`'s own wording. So this is now a documentation question — either `init` is real and belongs somewhere, or the operator surface should stop offering it.

## Why grouped

None of the four is a code defect. All four are assertions in specification prose that no instrument validates — the same family as **#289** and **#296**. A single id-resolution check (every cited `REQ-*` resolves to exactly one requirement whose text matches the citation) would close (1) outright and is the cheapest concrete slice of #289 identified so far.

Local beads: `yf-ne3e`, `yf-egfm`, `yf-4ye0`, `yf-9ovz`.

