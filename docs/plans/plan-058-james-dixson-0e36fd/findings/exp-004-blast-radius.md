---
type: Finding
okf_spec: OKF-PLAN
id: EXP-004
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# EXP-004: Blast radius of the one-call rewrite

**Question.** What breaks if `collect_parent_edges` stops shelling out per bead?

## Approach Tested

1. Repo-wide grep for `collect_parent_edges` / `deps_for_show` across all file types.
2. Read the call sites, `_shared/sync.py`'s vendoring manifest, `DRIFT-CHECK.md`,
   `CHANGE-VALIDATION.md`, `SPEC.md` and `test_upstream.py`.
3. Empirical equivalence on a **stratified 73-bead sample** (with/without parents, epics,
   molecules, closed beads, 20 of the 122 rows missing the `dependencies` key) plus an independent
   **random 300-bead sample**.
4. Sandbox spike: imported the real `upstream.py`, served cached `bd show` payloads, and compared
   the shipped `collect_parent_edges` against a rows-based derivation over 357 beads. Sandbox
   removed; repo untouched.

## Result

Very little breaks — it is a **one-function, ZERO-call-site** change. The main risk is not
breakage but a **coverage gap**: nothing in the suite exercises the function at all today.

### Callers: two, and neither needs a signature change

`collect_parent_edges` has exactly two production callers — `cmd_enumerate` (`:603`) and
`owner_claim_warning_lines` (`:1178`) — and both build their argument identically:

```python
beads = {r["id"]: r for r in rows if r.get("id")}
```

**measured: the dict values ARE the raw rows**, `dependencies[]` included. So the body can read
`beads[bid].get("dependencies")` with **no signature change and no call-site edit**. A `(rows,
beads)` signature is possible but strictly worse: it edits 2 call sites and 3 test monkeypatches
for no gain.

The edges are consumed only by `classify_active` (`:328`), which reads `dep_type`, `blocked` and
`blocker` — never `Edge.target` on this path. Nothing `bd show` returns is needed.

**`deps_for_show` (`:550`) becomes dead code** — `collect_parent_edges` is its only caller in the
entire repo. The similarly-named `deps_for` closures in `cmd_followons` (`:1001`) and `cmd_land`
(`:1065`) are a *different* function over `bd dep list` and are deliberately untouched.

### No vendoring hazard

`find . -name upstream.py` → exactly one file. `_shared/sync.py:300` vendors **one region** of it,
the `active-set classifier` fenced at `:250`-`:388`. Every function this plan touches —
`collect_parent_edges` (524), `deps_for_show` (550), `cmd_enumerate` (600),
`owner_claim_warning_lines` (1168) — is **outside** that fence. So `_shared/sync.py --check` and
the `e-active-set-copy-upstream` drift edge are unaffected, and no re-vendoring is needed.

**The fence is a hard constraint for execution:** do not edit `:250`-`:388`.

FAST-tier rows that fire on `skills/yf-beads-upstream/scripts/**`: `uv-with` (pytest),
`bup-prescriptive-push`, `bup-gh-direct`.

### The real risk: there is no test to break

| test | line | how it stubs |
| :-- | --: | :-- |
| `test_enumerate_warns_on_nonzero_candidates_with_exclusions` | 1099 | `monkeypatch.setattr(up, "collect_parent_edges", lambda _b: edges)` |
| `test_enumerate_json_stdout_stays_a_pure_array` | 1120 | same |
| `test_enumerate_silent_when_nothing_owner_excluded` | 1136 | same |
| `test_owner_claim_exclusions_*` (4) | 1066-1091 | pure; pass `Edge`s directly |

**No test calls `collect_parent_edges` or `deps_for_show` for real** — all three that touch it
monkeypatch it away. Nothing in the suite would catch a regression in the new derivation. The
`make_enumerate_universe()` fixture (line 903) builds bead dicts with **no `dependencies` key**,
so it cannot drive a rows-based implementation as written.

The three existing stubs survive unchanged **only because** the signature stays `lambda _b:` —
which is a second, independent reason not to change it.

### Directly reusable precedent for the guard

`test_closable_issues_one_bd_list_and_zero_bd_show` (line 685) and
`test_closable_bd_show_count_does_not_grow_with_universe_size` (line 719) already implement
exactly the invariant this fix needs, one verb over: a `_counting_run` fixture asserting
`len(lists) == 1` and `shows == []`, plus `count_for(10) == count_for(1000)`. Model the new tests
on these rather than inventing a shape.

## Implications for Plan

- No plan issue should propose a signature change; doing so is avoidable work that churns three
  test monkeypatches for no gain.
- The **coverage gap is the real finding**. A change with no test covering it is not made safe by
  being small, so the plan must add the missing tests rather than rely on the suite staying green.
- **inferred:** since all three tests that touch the function monkeypatch it away, the suite would
  have stayed green through *any* rewrite, correct or not. Green is not evidence here.
- The vendored-region fence is a hard constraint that must be written into the plan, because it is
  invisible when reading `upstream.py` alone.
- Sampling covered ~21% of the universe; EXP-002's full-universe run supersedes it, so the
  "optional landing gate" this experiment suggested is no longer needed.

## Recommendations

1. Rewrite in place with **no signature change**: replace `for dep in deps_for_show(bid):` with
   `for dep in (beads[bid].get("dependencies") or []):`.
2. Delete `deps_for_show` — no other caller exists repo-wide. Note in the commit that the
   `deps_for` closures at `:1001`/`:1065` are a different function over `bd dep list`.
3. Add a **direct** unit test of `collect_parent_edges` over a rows-shaped fixture (dependencies
   present, absent, and non-parent-child), and extend `make_enumerate_universe()` to carry
   `dependencies` arrays.
4. Model the scale-independence guard on `test_closable_issues_one_bd_list_and_zero_bd_show`
   (line 685) rather than inventing a shape.
5. **Do not touch `upstream.py:250`-`:388`** — the vendored `active-set classifier` region.

## Evidence

- `skills/yf-beads-upstream/scripts/upstream.py:524`, `:534`, `:550`, `:601-603`, `:1176-1178`, `:328`, `:347-348`
- `_shared/sync.py:300`; `upstream.py:250` / `:388` (the vendored fence)
- `skills/yf-beads-upstream/scripts/test_upstream.py:685`, `:719`, `:903`, `:1066-1136`
- `CHANGE-VALIDATION.md:191` (trigger scope), `DRIFT-CHECK.md:174` (`e-active-set-copy-upstream`)
