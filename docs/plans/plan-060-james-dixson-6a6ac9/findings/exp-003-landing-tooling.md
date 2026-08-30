---
type: Finding
okf_spec: OKF-PLAN
description: 'EXP-003 — inventory of the tooling a `land` verb must call: yf-beads-upstream''s engine, the reconcile contract, the FULL validation tier, the redeploy consent gate, herdr teardown''s absent contract, and the strongest prior art for a JSON-decision-driven gated executor.'
---
# EXP-003: The tooling a `land` verb must compose

## Approach Tested

**Question.** For each of the six landing steps, what already exists, what does it guarantee, and
what would `land` have to invent?

**Method.** Read-only survey of `skills/yf-beads-upstream/scripts/upstream.py` (2042 lines),
`skills/yf-plan/agents/reconciler.md`, `plan_manager.py verify-reconcile` / `grant`,
`CHANGE-VALIDATION.md`, `skills/yf-change-validation/scripts/change_validation.py`,
`yf/src/cmd/harness/consent.rs`, `skills/yf-herdr/SKILL.md`, and
`skills/yf-okf-hygiene/scripts/okf_hygiene.py`.


## Result

## F1 — `upstream.py`: eleven verbs, and three that do not exist

Verbs actually registered (`upstream.py:1930-1994`): `enumerate`, `mappings`, `granularity`,
`config`, `followons`, `closable`, `reconcile`, `push`, `hoist`, `land`, `unhoist`.

> **`init`, `status` and `pull` do NOT exist as verbs.** They are prose-only flows in the skill's
> `SKILL.md`, executed by the LLM with raw `bd config set` / `gh issue list`. Any `land` design that
> assumed it could shell out to `upstream.py status` is wrong.

**Importability:** it is a PEP-723 `uv run --script` CLI with `dependencies = []`, guarded by
`if __name__ == "__main__"`. It **is** side-loadable — `test_upstream.py:21-26` does so via
`importlib.util.spec_from_file_location` — but there is no package, so a plain
`import upstream` from `skills/yf-plan/scripts/` fails. `land` should shell out.

**A name collision to resolve: `upstream.py` already has a `land` verb**
(`land --parent --intake --dest [--apply]` — follow-on detection + hoist). `plan_manager.py land`
is a different, larger operation. The plan must state the distinction explicitly or the two will be
confused in prose forever.

## F2 — The gh-direct write sequence, and why its verification is structural

`apply_write` (`upstream.py:1078-1122`) is `gh issue create/edit`, then `bd update --external-ref`.
Its create path refuses to proceed without a returned URL:

```python
url = parse_issue_url(out)
if not url:
    raise WriteError(
        f"{plan['id']}: gh issue create returned no issue URL — treating as "
        f"UNVERIFIED and halting (REQ-BUP-057). Output: {out!r}")
```

and the `external_ref` failure carries hand-written remediation because a re-run would duplicate:

```python
raise WriteError(
    f"{plan['id']}: issue created at {url} but recording external_ref FAILED "
    f"({exc}). Re-running would create a DUPLICATE — record it by hand: "
    f"bd update {plan['id']} --external-ref {url}") from exc
```

The rationale recorded at `:1155-1162`: `bd github push --dry-run` printed `✓ Pushed 1 issues` when
nothing was pushed, so evidence is now *"a returned issue URL on create, which cannot be produced by
a no-op"*.

> **Important limit:** this is a **write-response** check, not a `gh issue view` re-read. #301
> demands read-back verification on every `gh` write (*"`gh` returned exit 0 on a wrong body this
> session — #292 carried uppercase `BLIND` against a case-sensitive test"*). **`upstream.py` does not
> provide that.** `land` must add re-read verification itself, or delegate to `verify-reconcile`.

**Fail-closed core:** `create_or_update` re-raises the first `WriteError`, so the destructive
follow-on stage (`hoist_close_commands`) is unreachable on an unverified write. Callers render
`FAIL-CLOSED: {exc}\n  No bead was closed.` and return 1.

**Gotcha:** `cmd_push` treats `upstream_state() == "undetermined"` as **exit 1**, deliberately
distinct from `disabled` (exit 0 no-op) — `upstream.py:1436-1451`.

## F3 — The reconcile contract is a single shared table, and `grant --check` is the existing consent primitive

`UPSTREAM_REQUIREMENTS` (`plan_manager.py:2676-2721`) is read by **both** `verify-reconcile` and
`grant`:

| disposition | end_state | state_reason | requires_mention | report_only |
| :-- | :-- | :-- | :-- | :-- |
| `include` | CLOSED | — | yes | no |
| `partial` | **OPEN** | — | yes | no |
| `supersede` | CLOSED | `NOT_PLANNED` | no | no |
| `deferred` | **OPEN** | — | no | no |
| `tracker` | — | — | no | **yes -> always `inconclusive`** |
| `exclude` | filtered out before verification | | | |

**This table is the mechanical refutation of #301's adjudication case 2.** The operator's
instruction *"close the upstream issues"* was wrong for plan-057 because every row was `partial` /
`deferred` / `exclude`, and `partial`/`deferred` require **OPEN**. `land` does not need an agent to
discover that — it needs an agent to *explain* it, and the table to *enforce* it.

**`verify-reconcile` check order** (`:2755-2784`): an unrecognised disposition literal is **`fail`
before any network call** ("a typo in the table, not a valid state"); then `gh issue view` bounded
by `_GH_TIMEOUT_S = 30`, where any failure/timeout is `inconclusive`, **never** `fail`; then state,
then `stateReason`, then plan-id mention (normalized alphanumerics, deliberately **not**
time-windowed). Aggregate: any `fail` -> exit 1 (halts); else any `inconclusive` -> exit **0**.

**`grant --check <file>`** (`plan_manager.py:2918`, `_grant_coverage` at `:3020`) is *"the only
operator-consent-file primitive in the repo"*: it derives the required actions from the same table
and verifies an operator authorization file covers **every action, per action — not per issue**,
because *"plan-048's omission was a close on an issue the grant already mentioned, which a per-issue
check would have passed."* Exit 1 on any uncovered action.

> **`grant --check` is the strongest existing candidate for `land --apply`'s consent gate and should
> be reused rather than reinvented.**

## F4 — Pre-authored comment bodies: an ad-hoc convention that nothing reads

Three incompatible shapes exist across three plans:

- `plan-049/assets/upstream-drafts/{135,140,149,113,174}.md` + `tracker.md`
- `plan-057/assets/upstream-drafts/{140,170,171,189}.md`
- `plan-059/assets/upstream-drafts/reconcile-264.body.txt`, `issue-*.body.txt` + a hand-written
  `RUNBOOK.md` carrying literal `gh issue comment 264 --body-file - < …` lines

**No code greps for `upstream-drafts`.** `grant --check` reads one path you hand it and knows
nothing about the directory. If `land` is to consume pre-authored bodies, **the path convention has
to be invented by this plan** — it does not exist to be reused.

## F5 — The FULL tier: 57 rows, no recorded wall-clock, and a timeout trap

`CHANGE-VALIDATION.md` §0 is `approved: yes`. §1 `full` = **57 rows** (~18 with blank ids, which is
legal); `fast` = 59 rows. *(Corrected from 58 after red-team pass 1 re-measured; `fast` was right.)* FULL omits `harness-e2e`, which is FAST-only. §3 has 118 glob rows; the
ones plan-060 fires include `skills/yf-plan/scripts/**` (20 fast ids),
`skills/yf-plan/scripts/plan_manager.py` (`uv-recheck-criteria`, `uv-index-members`,
`uv-yf-cli-enum`, `uv-yf-intake-lint`), and `skills/yf-beads-upstream/scripts/**`.

`change_validation.py run` emits
`{"tier","status","commands":[{id,cmd,ok,returncode,status,output_tail}],"first_failure"}`, **breaks
on first failure**, and exits `EXIT_OK` / `EXIT_FAIL` / `EXIT_INCONCLUSIVE` / `EXIT_REFUSED`.
`inconclusive` means *the first token of the command is not on `PATH`*. `--changed` scoping applies
**only to `fast`**.

**Timing: no wall-clock figure is recorded anywhere.** What is recorded is the constraint:

- `protocols/CHANGE-VALIDATION-TRIGGER.md:35` — *"FULL is the multi-minute gate paid once per land."*
- `plan-053/assets/checks/check-full-tier-record.sh:18-24` — *"`recheck-criteria` converts a
  `TimeoutExpired` into `status: inconclusive` and **continues** … while the FULL tier far exceeds
  its 300 s default"*, so the plan's broadest criterion *"would have timed out, recorded
  inconclusive, and let completion proceed at exit 0."*
- Measured row counts: **51/51 pass** (plan-053, 2026-08-26); **45/45 pass** (plan-050).

> **Direct design consequence.** `validate-merged` shells `change_validation.py run --tier full
> --json` with **no timeout** (`plan_manager.py:4643`). Both prior plans solved the >300 s problem by
> running the tier **once** and writing a dated record file a later criterion reads, rather than
> re-running inside a timeout-bounded checker. `land` must do the same, and its own success criteria
> must not embed a FULL-tier run inside a 300 s `recheck-criteria` bound — that is a criterion that
> **cannot fail** (#224's class).

Note also that `_validate_merged` maps engine `inconclusive` -> **`fail`** — issue **#262** live
inside the exact helper `land` must call.

## F6 — Redeploy: the consent gate is profile-declared, and rollback is asymmetric

`yf self install --from-build --build` (REQ-YF-SELF-004/005/008) promotes the binary, writes
`~/.config/yf/yf-from-build.json`, then execs the **freshly promoted** copy once per detected
harness to deploy skills + rules aggregate + config. Harness selection is by **existing config home
directory**, not by a binary on `PATH`.

`yf/src/cmd/harness/consent.rs`:

```rust
pub const CONSENT_FLAG: &str = "--allow-permissions-write";
```

*"Deliberately distinct from `--yes`… Two gates that authorize materially different things must not
share one token: an operator passing `--yes` to silence a fan-out prompt would otherwise silently
authorize a `bypassPermissions` write."* (`consent.rs:41-49`)

The config half auto-applies **only if** the target file already exists **by read
classification, not `path.exists()`** — empty/whitespace-only/malformed counts as **Absent**
(`:24-30`) — **and** the change set contains no profile entry declaring `consent_required: true`.
Otherwise it prints the per-key delta and refuses. `ConsentReason` carries **every** reason, not the
first. Only *mutating* changes count.

**Rollback is asymmetric** (`AGENTS.md:130-136`): `harness tune --revert` restores config precisely,
but the rules-aggregate revert **deletes** `YOSHIKO_FLOW.md` rather than restoring it (#154).
*"That is why the consent gate is the primary control rather than a backstop."*

**Hard constraint:** `AGENTS.md:42` — *"The one real constraint: no `yf skills install` /
`yf self install` mid-execution."* Redeploy is legitimate **only** as the last landing step, after
the merge is pushed.

**"Did the landed change touch `skills/`?"** — no purpose-built detector exists. `SKILL.md:1662`
already computes `CHANGED=$(git diff --name-only "${MERGE_TARGET}"...HEAD)` for
`classify-deliverable`. A one-line predicate `… | grep -q '^skills/'` is sound and conflicts with no
prior art.

## F7 — herdr teardown: the contract is ABSENT, and provenance does not exist

`skills/yf-herdr/SKILL.md` has **no `## Teardown` section**. The single close-related line is a
prohibition (`:234`): *"Do not close tabs or panes you did not create, and do not `herdr server
stop`."*

| Phase | Status |
| :-- | :-- |
| Launch | Mandatory contract `REQ-HERDR-015`, mechanically enforced by `test_launch_contract.py` |
| Observe | Specified `REQ-HERDR-026` |
| **Teardown** | **Absent** |

**Provenance of which session created a tab does not exist as a durable artifact.** The three
available handles are all inadequate:

- `--env YF_PARENT_PANE="$HERDR_PANE_ID"` seeded at `tab create` — **child-to-parent**, so a
  subordinate can push back; it does **not** let a parent enumerate its children.
- *"Record the delegation in the conversation"* (`SKILL.md:118`) — conversational memory, not an
  artifact.
- Token stamps written by `plan_manager.py escalation-push` (`:7228`) — the nearest thing to durable
  provenance, but keyed on plan id for the escalation backstop, not designed as a teardown handle.

> **Scope consequence.** #301's step 5 says *"close the herdr tab **only if this session created
> it**"* — and **that predicate is currently unanswerable**. `land` can either (a) restrict itself to
> a tab whose id the operator supplies explicitly, (b) build the provenance record #204 asks for, or
> (c) propose the close and never perform it. Options (a) and (c) are in reach; (b) is a yf-herdr
> deliverable.

#204's harvest-before-prune preconditions are mechanical and directly usable:
`git ls-tree -r origin/main -- <plan_dir>` non-empty and including `plan.md`/`log.md`/`reviews/`/
`findings/`/`assets/`; plan status `complete`; retrospective non-empty; `git status --porcelain`
clean; `git rev-list --count origin/main..main` = 0. Plus: verify the close **structurally** by
reading back the agent list, because *"the close returned `type: ok` while the surrounding shell
command exited 1."*

## F8 — Prior art for a JSON-decision-driven gated executor

**Strongest: `skills/yf-okf-hygiene/scripts/okf_hygiene.py backfill` (771 lines).** It has all four
properties `land` needs.

- **Dry-run/apply split with ONE decision path.** `backfill_one(tree, bundle, *, apply, skill)`
  (`:492`); without `--apply` it returns `{"action": "would-backfill", "steps": [...]}` and touches
  nothing. Classification, halt-check and member resolution run **identically** on both paths, so
  *the preview is the real plan*, not a parallel code path. **This is the property `land --dry-run`
  must have** — a dry run computed by different code is not a preview.
- **Pre-flight halt classes AND a post-condition assertion.** `unclassifiable` -> skip, *"never
  transformed blind"* (`:517`). On the way out (`:585-595`), if the transform left a legacy index
  beside a new `index.md`, it reports `manufactured-hybrid` — *"creating it would be strictly worse
  than not running — so it is asserted on the way out, not merely avoided on the way in."*
- **Crash-recovery journal.** `Journal` (`:285-325`), five enumerated states:

  ```python
  STATES = {"S0": "nothing staged", "S1": "staged, before rename 1",
            "S2": "after rename 1 — the bundle is ABSENT",
            "S3": "after rename 2 — the original is stashed",
            "S4": "after rename 2, before the journal is unlinked"}
  ```

  written with `_fsync_write` (`O_CREAT|O_TRUNC` + `fsync(fd)` + `fsync(dirfd)`) because *"the
  journal must survive the crash it exists to describe."* `recover()` is *"Keyed on the JOURNAL's
  recorded phase, never on directory presence — which is exactly the distinction that makes S1 and
  S4 separable at all."* Staging lives **inside the repo tree**, never `mktemp -d`, because
  cross-filesystem staging turns `os.rename` into a copy and *"voids every durability claim the
  journal makes."*
- **Record-driven reversal.** `backfill --record <path>` writes per-bundle before/after;
  `restore --record <path> [--apply]` computes a **per-path operation kind** — `git-checkout` for
  tracked files, `unlink` for files the transform created — because *"`git checkout` ALONE CANNOT
  UNDO THIS TRANSFORM… A restore that only checks out leaves every created file behind and reports
  success."*

**Second: `upstream.py push/hoist/land --apply`** — best fail-closed model, **no journal at all**.
If `apply_write` succeeds for beads 1–3 and dies on 4, nothing records it; recovery is a
hand-written remediation string plus idempotency-on-`external_ref`. `plan_land_hoist` (`:1235`) is
the one place a consent *policy* is a pure function: default `propose` puts everything in
`requires_confirm` with `auto_eligible` empty.

**Third: `escalation-push`** (`plan_manager.py:7133`) contributes the delivery-verification idiom:
*"`herdr agent prompt` returns `agent_not_found` **at exit 0**, so `$?` is not evidence of
anything"* — parse the payload, and *"FAIL-CLOSED: do NOT stamp. An unstamped escalation is retried
on the next boundary; a stamped-but-undelivered one is lost forever and looks sent."*

**Not prior art:** `skills/yf-beads-init/scripts/beads_init.py` is a **46-line shim**; there is no
`repair` executor there.

## F9 — Assembled call inventory

| Step | Tooling | Halting? |
| :-- | :-- | :-- |
| document-close chain (12 steps) | the existing §6.4 verbs; enumerable at runtime via `test_close_contract.py --list-steps` | mixed |
| reconcile writes | `grant [--check]` -> `gh issue comment/close` -> `verify-reconcile` (exit 1 halts) | yes |
| bead close-out + mirroring | `upstream.py closable --json` (propose-only), `reconcile --apply` (local only), `land`/`push --apply` | fail-closed, exit 1 |
| merge + FULL + push | `landing-lock acquire` (exit 3 = held) -> `git checkout/pull/merge --no-ff` -> `validate-merged` (exit 3; engine >300 s) -> `git commit` -> `landing-lock release` -> authorized push, guarded on `bd config get dolt.local-only` | yes |
| prune | `worktree teardown --json` (exit 3; `--force`); herdr tab close has **no contract** | partial |
| redeploy | `yf self install --from-build --build [--allow-permissions-write]`; detect via `git diff --name-only <target>...HEAD` ∩ `skills/` | fail-soft |

## Absence findings

- **No `upstream.py init` / `status` / `pull` verbs** — prose only.
- **No read-back (`gh issue view`) verification on upstream writes** in `upstream.py`; only a
  write-response URL check. #301's read-back requirement is new work.
- **No convention any code reads for pre-authored comment bodies**; three plans, three shapes.
- **No recorded FULL-tier wall-clock time** anywhere in the repo.
- **No detector for "the landed change touched `skills/`."**
- **No herdr tab-provenance record**, so "a tab this session created" is currently unanswerable.
- **No journal, no crash recovery, and no `--record`/reverse path anywhere in `yf-plan`.** The one
  good model is in a different skill (`okf_hygiene.py`).

## Implications for Plan

**measured:** three capabilities #301 assumes exist do not — `gh` read-back verification, a
convention any code reads for pre-authored comment bodies, and herdr tab provenance. Each is new
work or a deliberate narrowing, and the plan says which.

**measured:** the FULL tier exceeds `recheck-criteria`'s 300 s default, which converts a timeout to
`inconclusive` and continues. A success criterion that re-runs the tier inside that bound cannot
fail — which would be #224's defect authored into the plan whose subject is checks that cannot fail.

**inferred:** `okf_hygiene.py backfill` is the only adequate model in the repository for a
decision-driven gated executor, and it lives in a different skill. Copying its journal and
`--record`/`restore` shape is cheaper and safer than inventing one.

## Recommendations

1. Shell out to `upstream.py`; do not import it (no package, and the test suite side-loads it only
   via `importlib`).
2. Reuse `grant --check` as the upstream-write consent gate rather than reinventing one.
3. Add `gh issue view` read-back on top of `upstream.py`'s write-response check.
4. Name the distinction from `upstream.py land` wherever both appear.
5. Record the FULL tier's duration once, to a dated file, and cite the file.
