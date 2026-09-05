**Found by plan-063 (EXP-003) and deliberately not fixed there.**

Every subprocess the landing close chain launches passes `cwd=ctx.root` — **except one**. L14's
pour-fidelity `bd list`:

```python
bl = subprocess.run(["bd", "list", "--all", "--include-gates", "--limit", "5000", "--json"],
                    capture_output=True, text=True)
```

has no `cwd`, so it inherits the process's ambient working directory. The `uv run pour_fidelity.py`
call three lines below it *does* pass `cwd=ctx.root`, which makes the omission look like an
oversight rather than a decision.

**Why it is not currently visible.** `land --apply` already refuses to run outside the primary
checkout (`_land_assert_primary_checkout`, REQ-LAND-010), so in practice the ambient cwd *is*
`ctx.root` today. The defect is that nothing in the call itself establishes that — it is correct
by a precondition enforced elsewhere, which is exactly the kind of coupling that breaks silently
when the precondition moves.

`bd` resolves its database by walking up from the cwd, so under any future call path that does not
already guarantee the primary checkout, this reads a **different beads database** — or none — and
`pour_fidelity` then judges the wrong DAG.

**Proposed fix.** Add `cwd=ctx.root`, matching every sibling call. Consider a mechanical check
that no `subprocess.run` in the landing path omits `cwd`.
