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
