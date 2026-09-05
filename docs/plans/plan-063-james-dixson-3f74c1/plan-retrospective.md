---
type: Retrospective
okf_spec: OKF-PLAN
---
# Plan retrospective

Stops and deviations recorded during execution, newest last. Each `## RE-NNN` section is
one entry; `RE-NNN` ids are append-only and are never reused or renumbered.

`detected_by` records WHO found the entry and `evidence` records the command and output
substantiating any state claim in it, or the literal `unverified`. Both exist because an
entry's trust level is a property of who found it, and the recorder is usually the subject:
a retrospective built from an actor's own account would faithfully transcribe a false claim
rather than detect one. A state assertion with no evidence is a narration, not a finding.

## RE-001

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-04 |
| `stop_class` | 1 |
| `asked` | May this session file the eight residual findings upstream as GitHub issues? |
| `answered` | Not asked — a class-1 outward-facing write is a DESIGNED consent gate, so the session drafted the bodies, filed them as LOCAL beads (reversible), and proposed the exact gh commands instead of running them. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | Issue 6.1 / SC16: 'filing is an outward-facing write and cannot be self-certified from inside the plan'. 8 drafts at assets/residual-issues/, 8 local beads yf-2atf yf-i127 yf-9yb0 yf-f7lq yf-6xqf yf-acrn yf-pyqn yf-gdx4. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-04 |
| `stop_class` | 1 |
| `asked` | May this session run land --apply for plan-063? |
| `answered` | Not asked, and not run. SKILL.md 6.0 declares this stop-class-1: the session prints the command and stops. The route and its full halt-recovery contract are handed over at records/landing-handoff.md. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | land --dry-run: verdict pass, halts [], 6/6 upstream drafts present, merge_preview conflicts []. FULL tier: 68/68 pass. The apply_command is printed in the handoff verbatim; REQ-LAND-014's exit-3 tty gate is detection not prevention, and herdr pane run was NOT used to bypass it. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-003

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-09-04 |
| `stop_class` |  |
| `asked` | n/a — no operator interaction |
| `answered` | The session ran 'close-reconcile-step' while intending only to PREVIEW whether its gate-before-close precondition was satisfied, and labelled the output 'NOT run for real'. The verb has no dry-run mode: it closed yf-mol-3wtq.12 before the landing's L7 had performed any reconcile write. Detected immediately and reverted with 'bd update yf-mol-3wtq.12 --status open'; the bead is open again and the landing's close chain will close it after L7. |
| `frontloadable` | no |
| `detected_by` | self-report |
| `evidence` | close-reconcile-step returned {verdict: pass, bead: yf-mol-3wtq.12, already_closed: false, reason: 'closed reconcile bead yf-mol-3wtq.12'}. After revert, bd show yf-mol-3wtq.12 reports status: open. No upstream write occurred at any point; the error was local and reversible. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


## RE-004

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-05 |
| `stop_class` | 1 |
| `asked` | `verify-reconcile` halted the landing: all six issues carried a posted, read-back-verified comment, but none satisfied `requires_mention`. Closing the gap needed six further outward-facing writes. |
| `answered` | Operator chose to append a short addendum comment per issue naming the full plan id, leaving the original detailed comments untouched. Six posted and verified by read-back; the landing then resumed and `verify-reconcile` passed. |
| `frontloadable` | **yes** |
| `detected_by` | mechanical-check (`verify-reconcile`, exit 1, during `land --apply`) |
| `evidence` | L7 reported `11 upstream write(s) posted and verified by read-back`, every row `body match=True`. `verify-reconcile` then failed on all six: `#340 is CLOSED but no comment mentions plan-063-james-dixson-3f74c1`. Cause: `_mentions_plan_id` (`plan_manager.py:2621`) normalizes and searches for the FULL plan id; the drafts said only "plan-063", which normalizes to `plan063` and does not contain the needle `plan063jamesdixson3f74c1`. After the addenda: each of 340/342/343/341/333 `CLOSED` and 331 `OPEN`, each `comments=2 mentions=1`; resumed run recorded `verify-reconcile pass, exit_code 0`. |
| `escape_class` | vacuous-adjacent — a check that verified the WRONG PROPERTY. `land --dry-run` verifies `draft_present: true` for every row, and L7 verifies the posted body matches the draft. Neither verifies the one property the draft must have: that it satisfies `requires_mention`. The drafts were checked for EXISTENCE and for FIDELITY-TO-THEMSELVES, and the check that would have failed them ran only AFTER the writes were already public. |
| `adjudication` | The halt is correct behaviour and `verify-reconcile` did its job. The defect is upstream of it: the property is knowable at dry-run time, when it is still free to fix, and is instead discovered after six irreversible writes. |
| `origin` | plan-063 authored the drafts; the missing pre-write check predates it. |
| `culpability` | process — no actor error; the checking order is wrong. |
| `prevention` | `land --dry-run` should evaluate each draft body against `_mentions_plan_id` for rows where `requires_mention` is true, and report a row as failing BEFORE any write occurs. The predicate already exists; only the binding point is missing. |
| `cost` | one halt mid-landing, six additional public comments, one re-adjudication cycle. |

## RE-005

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-09-05 |
| `stop_class` | 5 |
| `asked` | n/a — halted mechanically on resume |
| `answered` | The resume after RE-004 halted with `halt_class 5`, a DIGEST MISMATCH: `resolved_target_tip` moved `eb0d859 -> 567f342`. The mover was THIS LANDING'S OWN L4 merge and L6 push. Remediated per the envelope's own instruction — fresh `land --dry-run`, re-dispatch of the `lander`, re-validate — never by editing the digest, which the envelope states is "a HALT, never an override". |
| `frontloadable` | **yes** |
| `detected_by` | mechanical-check (`land --apply`, `halt_class 5`) |
| `evidence` | `manifest_digest MISMATCH — decision carries 'sha256:4d8976f4…', re-derived reality is 'sha256:dd3dd31a…'`. Fact diff between the two manifests showed EXACTLY ONE changed field: `resolved_target_tip: eb0d859df0615b… -> 567f342050fbcc…`, plus `merge_preview.changed_paths` collapsing 13 -> 0 because the merge had already happened. Re-minted decision validated `digest_ok: true`; resumed run reached `L_DONE`. |
| `escape_class` | an incomplete disjunction in an exclusion set's membership predicate. |
| `adjudication` | A real defect, but **the exclusion set is the wrong place to fix it** (lander, second adjudication). `LAND_DIGEST_EXCLUDED` excludes the two `execute_worktree_*` fields because L18 mutates them mid-landing; it omits `resolved_target_tip`, which L4/L6 mutate in the same chain. The reason it cannot simply be added: the tip drifts from TWO causes — a foreign landing (must halt; this is the digest's entire purpose) and this landing's own chain (must not) — so the exclusion predicate is written over the FIELD while the correct discriminator is the CAUSE. `execute_worktree_*` could be excluded safely only because L18 is their sole writer, so field and cause coincide there. Excluding the tip would trade a nuisance halt for a silent one — the vacuous-check class this plan exists to remove. |
| `origin` | REQ-LAND-036's exclusion-set rationale, authored by this plan; discovered by this plan's own landing. |
| `culpability` | process |
| `prevention` | Record the self-mutated tip (and post-merge preview shape) into the journal `detail` at L4/L6; on resume, compare the re-derived tip against the journal's recorded self-mutation FIRST — equal means self-inflicted, proceed with the original digest intact; unequal means foreign drift, halt exactly as today. Foreign-drift detection is fully preserved. Scope is wider than one field: `merge_preview.predicted_tree` and `changed_paths` are self-mutated by the same chain. |
| `cost` | one guaranteed-to-recur halt on EVERY resume at or after `L_VALIDATED`; here, one full re-adjudication cycle. |

## RE-006

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-09-05 |
| `stop_class` |  |
| `asked` | n/a — decided at re-adjudication, no operator interaction |
| `answered` | On the re-adjudication the lander moved `l7_reconcile_writes` from `enable` to `skip`, on the ground that the step is NOT IDEMPOTENT and the resume guard that would normally protect it is a single point of failure. Recorded because it is a near-miss, not a fault: the harm did not occur. |
| `frontloadable` | no |
| `detected_by` | agent (lander, second dispatch); independently verified by the observing session |
| `evidence` | `_land_l7_reconcile_writes` calls `gh issue comment` unconditionally at `plan_manager.py:9438` — no already-posted check — and `gh issue comment` APPENDS. A re-execution would have posted six duplicate public comments. The journal at `L_RECONCILED` places L7 in `_land_resume_done`'s set and that check precedes `ctx.step_enabled`, so the resume would not have re-entered it; but the journal is an untracked file, and a lost or cleared journal makes `recover()` return `action: start` with an EMPTY done set. Outcome: final run recorded `l7_reconcile_writes` as `resumed: true, skipped: true` and every issue still reads `comments=2`. |
| `escape_class` | single-guard dependency on a non-durable artifact |
| `adjudication` | Correct call. Two independent mechanisms where one was load-bearing and fragile. The skip cost nothing — its branch journals `L_RECONCILED`, already the recorded phase, and no downstream step reads L7's `performed` list. |
| `origin` | pre-existing in the L7 implementation |
| `culpability` | none — near-miss, prevented |
| `prevention` | Make L7 idempotent at the source: before posting, read back and skip any comment whose body already matches. Then correctness does not depend on the journal surviving. |
| `cost` | none realised. |
