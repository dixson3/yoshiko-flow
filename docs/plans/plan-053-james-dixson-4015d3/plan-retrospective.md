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
| `kind` | deviation |
| `when` | 2026-08-25 |
| `stop_class` |  |
| `asked` | Three review passes each resolved every concern; passes 2 and 3 then measured only 9/14 and 9/15 of those resolutions reproducing. |
| `answered` | RE-002 named against the RESOLUTION PROCESS rather than the plan: the main session repairs a scope at the site the reviewer names and does not sweep for the same property elsewhere. Remedy adopted at pass 3: DELETE the drifting count literals rather than correct them, and let the controls enumerate. Four literals removed (D-8's site count, 3.7's '8 rows', 5.1's '16 sites', D-13's '0 of 41'). |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | pass-2 9/14=64%, pass-3 9/15=60%; three of pass-3's five (c)-class failures were re-broken by pass-2's own remedies |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-25 |
| `stop_class` |  |
| `asked` | Pass 4 measured the pass-3 structural remedy (delete drifting count literals) as itself applied site-by-site: 1 of 4 literals actually removed. |
| `answered` | Remedy changed AGAIN, this time procedurally rather than textually: apply the fix, then RUN the reviewer's own verification command and re-sweep on failure. On this pass that caught three literals the first edit pass missed (C50, C51, C52) and pushed two fixes beyond the concern's stated scope (C46 also corrected exp-003 and a section heading nobody named). |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | reproduction rate 64% -> 60% -> 50%; all six pass-4 verification commands now return the required value |
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
| `when` | 2026-08-25 |
| `stop_class` |  |
| `asked` | Issue 1.1(b) required exit 2 to be made UNRECORDABLE rather than merely rejected: move the rc check ahead of _append in redcheck.sh's cmd_record_red, because a record-time guard cannot un-write a record. Was that fix worth making, or was it a theoretical hardening of a path that never fires? |
| `answered` | It fired on its FIRST REAL USE, before any control had been recorded. Recording the RED for ctl-206-dropped-continuation, the fixture exited 2 (HARNESS) because redcheck.sh's INHERITED YF_TREE default -- ': ${YF_TREE:=${REPO_ROOT}/.worktrees/${PLAN_ID}}' -- assumed the assets live in the PRIMARY checkout, which was plan-050's layout. plan-053 keeps its assets in the EXECUTION WORKTREE, so REPO_ROOT already WAS the worktree and the default produced the doubled path '<worktree>/.worktrees/<plan-id>/_shared/plan_extract.py', which does not exist. The hardened cmd_record_red REFUSED the observation and wrote nothing. Under the harness exactly as adopted from plan-050, _append ran BEFORE the rc check, so this would have printed 'RED observed', returned 0, and banked a permanent 'record-red, ctl-206-dropped-continuation, ..., 2, ...' line -- which _has_record 'nonzero' matches -- certifying a RED for a fixture that never executed a single assertion. YF_TREE now RESOLVES (probe for .worktrees/<plan-id>/_shared, else use REPO_ROOT) instead of assuming. This is R3's exact failure mode -- a control written so it cannot go RED -- occurring INSIDE the instrument built to grade silent greens, and it is the second time this harness has caught that shape in itself (plan-050's own self-spike caught the command-substitution subshell bug in _run_fixture). |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | COMMAND: bash redcheck.sh record-red fixtures/ctl-206-dropped-continuation.sh ctl-206-dropped-continuation | OUTPUT (verbatim): 'ctl-206: HARNESS - no extractor at /Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3/.worktrees/plan-053-james-dixson-4015d3/_shared/plan_extract.py' followed by 'redcheck: FAIL - ctl-206-dropped-continuation fixture exited 2 (INCONCLUSIVE): the fixture could not run at all. ... NOTHING WAS RECORDED. Repair the fixture, then re-run.' Exit code 1. VERIFICATION THAT NOTHING WAS WRITTEN: 'grep -c ctl-206 red-prework.md' -> file did not yet exist (0 records), and 'bash redcheck.sh verify-red-all' still returned rc=1 with all 11 controls unobserved. WHAT WOULD HAVE BEEN RECORDED WITHOUT THE GUARD: the line 'record-red, ctl-206-dropped-continuation, fixtures/ctl-206-dropped-continuation.sh, 2, `YF_TREE=... bash fixtures/ctl-206-dropped-continuation.sh`, <utc>, <git-describe>' -- rc=2, which the pre-fix _has_record 'nonzero' predicate matches, so verify-all would later have certified this control red->green. INDEPENDENTLY CONFIRMED by a deliberate spike against a fixture whose entire body is 'exit 2': refused, rc 1, zero records on disk. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-004

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-25 |
| `stop_class` |  |
| `asked` | Verifying SC6 by hand -- test -f skills/yf-plan/scripts/pour_fidelity.py && grep -q '${SKILL_DIR}/scripts/pour_fidelity.py' skills/yf-plan/SKILL.md -- returned NON-ZERO even though the literal was verifiably present in the file. Is SC6's verification command defective? |
| `answered` | NO. The criterion is sound; the MEASUREMENT ENVIRONMENT was not. The interactive session's `grep` is a SHELL FUNCTION wrapping ugrep, installed by a Claude Code shell snapshot (~/.claude/shell-snapshots/snapshot-zsh-*.sh), not /usr/bin/grep. ugrep's default matcher treats the unescaped { } in ${SKILL_DIR} differently and reported 0 matches, while /usr/bin/grep and grep -F both report 1. Verified: 'grep -c' -> 0, 'grep -cF' -> 1, '/usr/bin/grep -c' -> 1, and the same command under 'bash -c' (where grep resolves to /usr/bin/grep) -> rc 0. SC4, SC6 and SC6b are all GREEN when run with the system binary. CONSEQUENCE FOR THE REST OF THIS PLAN: every grep-based criterion must be verified through 'bash -c' or /usr/bin/grep, never through the interactive shell's grep, or a TRUE criterion reports FALSE. recheck-criteria at SS6.4 runs its commands via subprocess rather than through this shell function, so the automated re-check is unaffected -- but a hand-verification is not, and this session had already hand-verified several grep-based assertions. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | COMMANDS AND OUTPUTS: 'type grep' -> 'grep is a shell function from /Users/james/.claude/shell-snapshots/snapshot-zsh-1787705623143-ft9k73.sh' wrapping 'ARGV0=ugrep $_cc_bin -G --ignore-files ...'; 'grep --version' -> 'ugrep 7.5.0 aarch64-apple-macosx'; 'grep -c -- ${SKILL_DIR}/scripts/pour_fidelity.py skills/yf-plan/SKILL.md' -> 0; 'grep -cF -- <same>' -> 1; '/usr/bin/grep -c -- <same>' -> 1; 'bash -c type grep' -> 'grep is /usr/bin/grep'. Final verification of all three affected criteria through bash -c: SC4 rc=0, SC6 rc=0, SC6b rc=0. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-005

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-25 |
| `stop_class` |  |
| `asked` | The bead ledger disagreed with the completion reports: 32 closed / 12 in_progress, where the in_progress set was issues inside epics already reported COMPLETE. An outside observer measured the closed count DECREASING across the run (35 -> 40 -> 42 -> 32) and asked whether beads had been reopened deliberately, whether closes simply had not been issued, or whether something reopened them unintentionally. |
| `answered` | NEITHER a deliberate correction NOR an unintentional reopen. NOTHING WAS EVER REOPENED -- eleven closes NEVER TOOK EFFECT, via TWO stacked silent-failure mechanisms, and the apparent 'decrease' was an artifact of comparing counts that included beads whose closes had already silently no-opped. MECHANISM 1: 'bd close' HAS NO --notes FLAG (verified: bd close --help lists only -f/--force, -r/--reason, --reason-file). Five closes (2.2, 3.1, 3.3, 3.4, 4.3) were issued as 'bd close <id> --notes ... --reason ...' and errored outright. MECHANISM 2, THE SERIOUS ONE: 'bd close' on a bead BLOCKED BY AN OPEN DEPENDENCY REFUSES AND EXITS 0 -- it prints 'cannot close <id>: blocked by open issues [<id>] (use --force to override)' on stdout and returns success. So the six downstream closes (2.3, 3.2, 4.4, 4.5, 5.0, 7.1) silently no-opped once mechanism 1 left their predecessors open. MY OWN CONTRIBUTING ERROR, stated plainly: every close was issued as '-q >/dev/null 2>&1', which discarded the message, and the exit code was never read -- so BOTH mechanisms were invisible to me. That is the same 'a step with no exit code is not a step' defect this plan exists to close, committed by me while executing the plan that closes it. REPAIRED: all eleven re-closed in DEPENDENCY ORDER with their real reasons via --reason-file, each result verified by matching the success line rather than the exit code. Ledger now 43 closed (all with reasons), 3 non-closed = 7.2/7.3/7.4, which is correct. CAUGHT BY THE PARENT SESSION FROM OUTSIDE, not by me and not by any check in this plan -- the Reconcile Gate would have caught it, but only AFTER 7.2's upstream filings had gone out. |
| `frontloadable` | yes |
| `detected_by` | operator |
| `evidence` | ROOT CAUSE COMMANDS: 'bd close --help' -> flags are only '-f, --force', '-r, --reason string', '--reason-file string'; there is no --notes. 'bd close yf-mol-bh8.3.3 --reason TEST' -> 'cannot close yf-mol-bh8.3.3: blocked by open issues [yf-mol-bh8.3.2] (use --force to override)' with rc=0 -- a REFUSAL AT EXIT ZERO, measured directly. 'bd close yf-mol-bh8.3.2 --reason probe' immediately afterwards -> 'Closed' (so 2.2 was the head of the cascade, blocked by nothing, and had failed on mechanism 1 alone). LEDGER BEFORE: Counter({'closed': 32, 'in_progress': 12, 'open': 2}) of 46, in_progress = 2.2 2.3 3.1 3.2 3.3 3.4 4.3 4.4 4.5 5.0 7.1 7.2. LEDGER AFTER repair: Counter({'closed': 43, 'open': 2, 'in_progress': 1}) of 46, with 43 of 43 carrying a close_reason, and the only non-closed being 7.2 (in progress), 7.3 and 7.4. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-006

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-26 |
| `stop_class` |  |
| `asked` | SC19's Verification command, as written in plan.md, is: bd show "$(uv run skills/yf-plan/scripts/plan_manager.py json-get epic < docs/plans/plan-053-james-dixson-4015d3/plan.md)" --json | jq -e '.[0].external_ref | startswith("https://github.com/")'. Run verbatim at 7.3 it FAILED. Is the end state wrong? |
| `answered` | NO -- the END STATE is correct and the COMMAND is defective. json-get is a JSON extractor and plan.md is MARKDOWN, so 'json-get epic < plan.md' returns 'ERROR: key epic not found in path epic', the command substitution yields that error text as the bead id, and jq then fails with 'Cannot index object with number'. Exit 5. The epic DOES carry the ref: 'bd show yf-mol-bh8 --json | jq -e '.[0].external_ref | startswith("https://github.com/")'' returns true, with external_ref = https://github.com/dixson3/yoshiko-flow/issues/231. This is the THIRD criterion-command defect this plan has hit (SC6's ugrep artifact, SC16's wrong path measured at exit 2 during planning, and now SC19), which is itself the finding: plan-053 spent five review passes on criterion SEMANTICS and the residual defects are all in criterion MECHANICS -- commands that were written but never EXECUTED before being committed to. SC19's own text says it asserts 'on the END STATE, never on the route', and the end state is what was verified; the correct reader is 'bd show <epic> --json'. Note this defect could NOT have been caught earlier by construction: before 7.3 there was no tracker to stamp, so the command had nothing to return either way. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | AS WRITTEN: 'bd show "$(uv run skills/yf-plan/scripts/plan_manager.py json-get epic < docs/plans/plan-053-james-dixson-4015d3/plan.md)" --json | jq -e ...' -> stderr 'ERROR: key epic not found in path epic'; then 'jq: error (at <stdin>:4): Cannot index object with number'; exit 5. CORRECTED READER: 'bd show yf-mol-bh8 --json | jq -e '.[0].external_ref | startswith("https://github.com/")'' -> true, rc 0; 'bd show yf-mol-bh8 --json | jq -r .[0].external_ref' -> https://github.com/dixson3/yoshiko-flow/issues/231. STAMP VERB OUTPUT: {"status": "stamped", "epic": "yf-mol-bh8", "tracker": "https://github.com/dixson3/yoshiko-flow/issues/231", "reason": "epic is now visible to upstream.py closable"}. SC18 alongside: verify-reconcile exit 0, 8 of 9 rows pass, the single inconclusive being the tracker row itself which is report-only BY CONSTRUCTION (REQ-CLI-018) and explicitly does not block completion. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

