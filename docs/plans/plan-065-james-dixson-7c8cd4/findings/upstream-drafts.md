---
type: Finding
okf_spec: OKF-PLAN
description: 'Issue 5.6 — the six drafted upstream issue bodies and the exact close set, so the
  Epic 6 operator gate has evidence to authorize against'
---
# Upstream drafts — plan-065

**Nothing here has been filed.** Filing and closing are outward-facing writes gated on
`yf-mol-e7k4.10` (*Upstream write authorization*), which is the operator's alone. This file is
the evidence that gate authorizes against.

**SIX defects, not four.** SC10 and Issue 6.1 were amended mid-execution (ESC-001): four were
scoped at drafting, and two more were found by *running* the plan. The pre-amendment text said
"All FOUR" and named the fourth explicitly, so as written it would have **passed while silently
dropping (5) and (6)**.

**Composing the bodies** (AGENTS.md, Upstream Tracking): always `--body-file -` fed by a
**quoted** heredoc (`<<'EOF'`), never `--body '...'`. These bodies are full of backticks and
braces; a single-quoted `--body` passes backslashes through literally and an unquoted one lets
the shell expand `` ` `` and `$`. Verify each posted body by reading it back
(`gh issue view N`), never by trusting exit 0.

---

## Part 1 — six issues to FILE

### (1) `restore --root` refuses 100% of the time: the record stores absolute paths, the guard queries `HEAD:{rel}`

**Labels:** `bug`
**Severity:** medium — **fail-safe** (it refuses rather than destroys), but it makes the
documented `--root` workflow unusable.

```
`okf_hygiene.py restore` is unusable under `--root`. `_tracked_at_head`
(okf_hygiene.py:1185) asks git whether a path exists at HEAD:

    subprocess.run(["git", "-C", str(tree), "cat-file", "-e", f"HEAD:{rel}"], ...)

`HEAD:{rel}` requires `rel` to be REPOSITORY-RELATIVE. But under `--root` the record's
operation paths are stored ABSOLUTE, so the query becomes `HEAD:/Users/.../docs/plans/...`,
which never resolves. Refusal condition 2 therefore fires for every path, and `restore`
declines the whole batch — 100% of the time, in that mode only.

**Why it matters even though it is fail-safe.** `--root` is the documented way to run the
engine against a tree other than `cwd`, and it is the natural way to rehearse a backfill in a
sandbox. An operator who rehearses with `--root` proves nothing about the reversal path,
because the reversal path cannot run there at all.

**Workaround, used throughout plan-065:** `cd` into the target tree and pass no `--root`.
Measured: the round-trip is byte-identical that way (see (4) for the case where it is not).

**Fix:** normalise operation paths to repo-relative when writing the record, or resolve them
against the record's own root when reading. The record is versioned
(`RECORD_SCHEMA_VERSION`), so a normalising change can be gated on the version.
```

---

### (2) The phase-log guard is one-sided, and `src_bul` / `dst_bul` are dead

**Labels:** `bug`
**Severity:** medium — produces a **false halt**, blocking a transform that would lose nothing.

```
`okf_hygiene.py` computes bullet signatures and then never uses them:

    src_bul, src_dates = _log_signature(plan_before)          # :786
    dst_bul, dst_dates = _log_signature(...)                  # :788
    lost_dates = src_dates - dst_dates                        # :790

`src_bul` and `dst_bul` are assigned and never read. The guard compares **dates only**, which
is wrong in both directions:

- **False negative.** A bullet lost under a date that survives on another bullet is invisible.
  Measured: a synthesized log carrying nine of plan-030's ten bullets — the dropped one's date
  still present — passes the guard. plan-065 had to build a separate bullet-level check
  (`plan065_checks.py phaselog-bullets`) precisely because the engine's own guard could not be
  reused for the verification.

- **False positive.** The guard compares `plan.md`'s dates against a **staged `log.md` the
  transform did not write** — see (3). For plan-030 it reported `phase-log-loss` for a loss
  that cannot occur, halting 1 of 8 bundles for a detector artifact.

**Fix:** compare the bullet signatures that are already computed, and fix (3) so the comparison
is against the log the transform actually produces.
```

---

### (3) `migrate`'s log reconciliation is skipped entirely when `log.md` already exists

**Labels:** `bug`
**Severity:** medium

```
`okf.py:1292` guards the whole log-reconciliation block:

    if not (d / "log.md").exists():
        ...extract **Phase log:** -> log.md, then strip the block from plan.md...

So for a bundle that already carries a `log.md`, the transform **never moves the phase log and
never strips it**. The bundle is left with the phase log in BOTH places — or, more precisely,
still only in `plan.md`, with `log.md` untouched.

This is not hypothetical: `plan_manager`'s close-time `append_log` writes a `log.md` into an
otherwise-legacy bundle, so the state arises normally. Measured on plan-065's corpus: exactly
one of eight bundles (plan-030) was in it.

**Interaction with (2) is what made it visible.** The guard compares `plan.md`'s dates against
the staged `log.md` — which, because of this skip, the transform did not write. It reported a
loss that could not occur, and halted.

**The correct behaviour is the move, not the skip:** merge the phase log into the existing
`log.md` (newest-first, preserving existing entries) and delete the `**Phase log:**` block,
reaching the same end state the other seven bundles reach mechanically. plan-065 performed
exactly that by hand for plan-030 and the bundle then transformed cleanly.

**Note for the fix:** a naive replay of `append_log` oldest-first is NOT correct when a
`log.md` already exists. `append_log` prepends a new `## <date>` block whenever the date
differs from the heading at position 0, so replaying against an existing `## 2026-07-20`
emits a SECOND `## 2026-07-20` block above the older one — duplicated heading, not
newest-first, which `_check_reserved_log` then flags.
```

---

### (4) `restore --apply` on a COMMITTED backfill is a SILENT TOTAL LOSS — the `git checkout` return code is never checked

**Labels:** `bug`
**Severity:** **HIGH — data loss.** Reports `verdict: pass` and exits 0 while destroying the
bundle.

**Reproduction:** `docs/plans/plan-065-james-dixson-7c8cd4/findings/exp-003-post-commit-restore-loss.md`

```
Measured sequence: commit a base, `backfill --apply --record`, **commit the backfill**, then
`restore --record <r> --bundle <one> --apply`.

Result: `verdict: pass`, `exit: 0`, and the bundle left with **no README.md, no index.md and
no log.md**. The control — the same sequence WITHOUT the commit — restores byte-identically.

Mechanism, at okf_hygiene.py:1363-1373:

    for op in item["operations"]:
        if op["kind"] == "created":
            (tree / op["path"]).unlink(missing_ok=True)     # :1368  ALWAYS RUNS
    paths = [... "modified"/"deleted" ...]
    if paths:
        subprocess.run(["git", "-C", str(tree), "checkout", "--", *paths],
                       capture_output=True)                  # :1371-1372  RETURN CODE DISCARDED

Committing the backfill removes `README.md` from the working tree AND from `HEAD`'s successor
commit, so the `git checkout` that should restore it fails. Its return code is captured into a
`CompletedProcess` that is thrown away. Meanwhile the `created` unlink pass has already deleted
`index.md` and `log.md`. Net effect: the delete half succeeds, the restore half fails silently,
and the verdict is computed without reference to either.

**This is a FOURTH data-loss path in `restore`, distinct from the three repaired by plan-064**,
and it is reachable by an ordinary, sensible operator sequence.

**Fix (two parts, both needed):**
1. **Check the return code.** A failed `git checkout` must make the verdict `fail`, and must
   do so BEFORE — or instead of — the `created` unlink pass, so a restore that cannot restore
   does not first delete.
2. **Refuse up front.** `_tracked_at_head` already exists and already answers the right
   question. If the paths the record marks `deleted` are absent from `HEAD`, the backfill has
   been committed and the record-driven reversal is not applicable: refuse, and say that
   `git revert` is the verb.
```

---

### (5) `backfill --apply` generates a NON-CONFORMANT `index.md` with no member listing

**Labels:** `bug`
**Severity:** medium — every freshly transformed bundle is immediately non-conformant.
**Found during plan-065's own corpus apply.**

```
`backfill --apply` renames `README.md` -> `index.md` and then strips the README's prose
(step `delete-renamed-README.md-prose`), including its `## File map`. What it emits is a
header, an objective blockquote, and a portability sentence — with NO member listing.

So every bundle it transforms immediately FAILS `scripts/checks/check_okf_index_drift.py`.

**Measured on all 8 bundles of plan-065's corpus apply**, with missing-member counts of
9, 13, 9, 11, 12, 12, 18 and 6 — 90 missing entries in total. Before the apply the corpus
reported `no_index: 8, drifting: 1`; immediately after it reported `no_index: 0, drifting: 9`.

**The generated artifact refutes itself on its face.** plan-010's `index.md` was 368 bytes
reading:

    This bundle is **portable** — a cold reader understands its purpose, environment and
    history from the files below alone, without the drafting conversation.

...followed by no files. An index that promises a listing and omits it is worse than an absent
one, because it passes a presence check.

**Repaired post-hoc** by `reindex --apply` on each of the 8 (which derives real descriptions
from each member's frontmatter — not bare bullets). But that repairs the SYMPTOM in one corpus:
the engine will reproduce this for every future backfill in every repo that installs the skill.

**Fix:** call the reindex path as the final step of `backfill_one`'s apply branch, so a
transformed bundle is conformant when the transform returns. `render_index` /
`reindex_write` already exist and already do the right thing.
```

---

### (6) `reindex`'s dry run reports `verdict: clean` while proposing nine changes

**Labels:** `bug`
**Severity:** low — but it is the saturating-label failure in a new place.

```
    $ uv run okf_hygiene.py reindex docs/plans/plan-010-... --json
    { "verdict": "clean", "changed": true, "changes": [ ...9 add-missing ops... ], "exit": 0 }

A dry run that proposes nine repairs is not `clean`. The `verdict` here describes whether the
reindex OPERATION succeeded, while every consumer reads a `verdict` as a statement about the
BUNDLE — which is what `reindex_check` correctly reports as `drift`.

`changed: true` alongside `verdict: clean`, at exit 0, means a caller that branches on the
verdict (or on the exit code) sees green on a bundle that needs nine repairs. This is the same
shape as `audit`'s saturating `warn` and `check_okf_index_drift`'s `no_index`-does-not-affect-
the-verdict: a label that cannot report what its consumers read it to mean.

**Fix:** in `--json` dry-run mode, report the BUNDLE's verdict (`drift` when `changes` is
non-empty), or rename the field so the two questions are not answered by one word.
```

---

## Part 2 — the exact close set

**No issue below is closed until `yf-mol-e7k4.10` is resolved by the operator.** Verify every
one by reading it back with `gh issue view N`, never by trusting an exit 0.

| # | Action | Body / comment | Why |
| :-- | :-- | :-- | :-- |
| **#359** | **CLOSE** | Comment: the corpus backfill ran on the repaired engine — 8 transformed, 0 halted, 70 checked, `legacy: 0`, and `restore` exercised on a real bundle (plan-030) with a byte-identical round-trip verified by per-file sha256. Link commits `17a9445`, `250aace`, `31a6fe3`. | Every acceptance criterion it carries is discharged |
| **#316** | **CLOSE** | Comment: superseded-and-completed by #359, which carried its criteria verbatim. Same evidence. | Parent; both close together |
| **#295** | **UPDATE, LEAVE OPEN** | Comment: **SC19 only** — the 8 unresolved backfill halts are resolved; all 8 bundles now carry the reserved `index.md` + `log.md`. **SC24 (4 ungranted reconcile comments) is untouched and out of plan-065's scope**, and this issue stays OPEN for it. | Partial disposition |
| new ×6 | **FILE** | The six bodies in Part 1 | Every defect this plan found is filed, not fixed (SC12) |

**Do not add a `Closes:` keyword to any commit.** plan-065's backfill commit initially carried
`Closes #359, closes #316`; it was amended to `Refs` before any push, because a close keyword
fires on push and would bypass this gate entirely.

**`dolt.local-only` is true for this repo.** The propagation step is `git push` **alone** —
never `bd dolt push`.
