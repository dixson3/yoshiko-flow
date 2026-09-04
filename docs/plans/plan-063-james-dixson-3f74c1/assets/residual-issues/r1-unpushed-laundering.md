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
