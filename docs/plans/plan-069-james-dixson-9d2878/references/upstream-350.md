---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #350 - A measurement that failed is reported as a green
  number (L16 laundered unpushed count, check_amendment_log under-counted n_impl)'
---
# Upstream #350: A measurement that failed is reported as a green number (L16 laundered unpushed count, check_amendment_log under-counted n_impl)

- **Number:** 350
- **Title:** A measurement that failed is reported as a green number (L16 laundered unpushed count, check_amendment_log under-counted n_impl)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Shared cause

Two instances of one defect class: **an emitted number that is not the measured number.** One launders an *unreadable* count into the literal `0`, so a failed measurement reads as green; the other under-counts, so a true measurement reads as a smaller one. Both are report-line fidelity, and both belong to the vacuous-check family this repository has been closing plan by plan (see #263). Grouped so the fix is stated once as **never emit a number you did not measure**, rather than as two unrelated arithmetic patches.

Grouped per the coarse-granularity convention in AGENTS.md. Recorded during plan-063 and deliberately not fixed there.

---

## L16 launders an unreadable unpushed-commit count into `0` (bead `yf-2atf`)

**Found by plan-063 (EXP-003) and deliberately not fixed there.**

`_land_l16_commit_and_push_two`'s post-condition reads the unpushed-commit count as:

```python
unpushed = ctx.run("git", ["rev-list", "--count", f"origin/{ctx.target}..{ctx.target}"],
                   cwd=ctx.root).stdout.strip() or "0"
```

The trailing `or "0"` **launders a failure into a green**. `git rev-list --count` writes nothing
to stdout when it fails — an absent `origin/<target>` ref, a detached HEAD, a broken repo — so an
empty stdout and a genuinely-zero count are indistinguishable, and the `or "0"` resolves both to
"nothing unpushed".

This is the same **two facts, one signal** class as `doc_lint`'s `not-selected` vs `no-such-path`
(#181) and `resume-scan`'s `found` (#207).

**Why it matters here specifically.** This is L16's post-condition — the assertion that runs *on
the way out* of the only step that pushes after the irreversible boundary. A laundered green
there means "the landing verified that nothing is unpushed" when what actually happened is "the
verification could not run".

**Proposed fix.** Read the return code. A non-zero `rev-list` is `inconclusive`, not `0`:

```python
rv = ctx.run("git", ["rev-list", "--count", f"origin/{ctx.target}..{ctx.target}"], cwd=ctx.root)
if rv.returncode != 0:
    return _step(..., "inconclusive", "the unpushed count could not be measured: ...", halting=True)
```

Note the verdict is `inconclusive` and **halting** — the measurement failed, which is a different
claim from the tree being dirty, and REQ-LAND-012 forbids coercing it to `fail`.

---

## `check_amendment_log`'s success line under-counts `n_impl` (bead `yf-6xqf`)

**Found by plan-063 while running the check on itself. Cosmetic, but it misreports a count.**

`scripts/check_amendment_log.py`'s success line:

```python
n_impl = sum(1 for e in epic_of.values() if e != spec_epic) - len(exempt)
```

subtracts `len(exempt)` unconditionally, but `exempt` is the **declared or baseline
no-req-required set** — whose members need not exist in the plan under check. The baseline is
`{"4.6", "4.7"}`; plan-063 has neither, so the check reported:

> all **19** non-exempt implementation issues reach a REQ-naming Epic-0 issue

when the true count is **21**. The *assertion* is correct — reachability was genuinely verified for
all 21 — only the reported number is wrong.

**Why it is still worth fixing.** The success line is the only human-readable evidence the check
produces. A number that silently differs from reality trains readers to skim it, and a check
nobody reads is a check that certifies nothing (`#263`).

**Proposed fix.**

```python
impl = {i for i, e in epic_of.items() if e != spec_epic}
n_impl = len(impl - exempt)
```

Subtract the *intersection*, not the cardinality of the exemption list.

---

<sub>Filed from plan `plan-063-james-dixson-3f74c1` (bundle: `docs/plans/plan-063-james-dixson-3f74c1`). Beads: `yf-2atf`, `yf-6xqf`.</sub>

