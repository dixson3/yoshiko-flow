**Recorded by plan-063 at its own pass-3 review (C35). The check plan-063 built does not cover
the axis that was load-bearing in plan-063.**

`scripts/checks/check_mock_fidelity.py` binds every monkeypatched stub against
`inspect.signature` of its target. It caught `#340` (`_worktree_teardown` faked with one
parameter instead of two) and would have caught it before the first real `land --apply`.

It binds the **argument** axis only. It is **structurally blind to return shapes** — and the return
shape is the divergence that mattered most in the plan that added it:

- `_worktree_teardown` returns `{"status", "path", "branch", "steps"}` and **never** an `"action"`
  key.
- All four shipped stubs returned `{"action": "removed"}`.
- plan-063's `REQ-LAND-031` makes L18 **branch on `wt["status"]`**.

So a stub that binds perfectly on arity can still drive L18 down the wrong branch — and did. The
`"action"` key was consumed by `wt.get("action") or wt`, which always took the fallback and made
the divergence invisible for as long as nothing read `status`.

`check_mock_fidelity.py` records this limitation in its own docstring and in its `--json`
`not_covered` field rather than claiming the class is closed. This issue is the other half of that
honesty.

**Why it is hard, stated rather than hand-waved.** A return-shape check has no `inspect.signature`
equivalent: Python return annotations are `dict` at best, and the real contract is the **key set**.
The tractable forms are (a) annotate the real functions with `TypedDict` and check stub literals
against it, or (b) a runtime contract — record the key sets a function actually returns across the
suite and diff the stubs against that.

**Scope note.** This is the second axis of one class. The first (arity) is closed by
`check_mock_fidelity.py`; the third (assignments to non-callables) has no observed instance yet.
