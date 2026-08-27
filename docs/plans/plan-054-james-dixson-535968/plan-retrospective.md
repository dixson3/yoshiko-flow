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
| `when` | 2026-08-26 |
| `stop_class` |  |
| `asked` | yf-herdr SKILL.md Launch step: resolve the current agent kind via 'herdr agent list --json | jq -r ...' |
| `answered` | The command is INVALID — herdr emits JSON by default and 'agent list --json' exits 2 with a usage error. Piping into jq swallowed the error, so KIND resolved to the empty string and the next step would have run 'herdr agent start --kind ""'. Recovered by re-reading without the flag. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | herdr agent list --json >/dev/null; echo $? -> 2. Prescribed at skills/yf-herdr/SKILL.md:65 and in the installed copy at ~/.claude/skills/yf-herdr/SKILL.md:66. |
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
| `when` | 2026-08-26 |
| `stop_class` |  |
| `asked` | Does 'herdr tab create' support --no-focus, as yf-herdr SKILL.md:73 prescribes? |
| `answered` | I reported it did NOT and that the skill was wrong. That was FALSE. --no-focus is a real flag; I had read 'herdr tab create --help' truncated at head -20 and the flag sits at line 21. The skill is correct here. Cost: a false defect claim relayed to the operator, plus a stray tab created while testing it (cleaned up). |
| `frontloadable` | partial |
| `detected_by` | self-report |
| `evidence` | herdr tab create --help | grep -n -i focus -> 18: --focus, 21: --no-focus. Direct invocation exits 0. |
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
| `when` | 2026-08-26 |
| `stop_class` |  |
| `asked` | Epic-3 milestone claimed 'All 5 Epic-3 controls red->green' |
| `answered` | FALSE at the time it was asserted. ctl-203-exit-discipline had a record-red row but NO assert-distinguishes row: Issue 3.6's body carries the SC2b obligation to run it on completion, and the issue was closed without it. The FIX was correct (the fixture exits 0 against the worktree) — the missing artifact was the GREEN RECORD, so redcheck.sh verify-all exited 1 while the milestone reported green. Detected by the parent session running verify-all independently from the primary checkout; confirmed here by measurement (verify-all REAL EXIT = 1 before, 0 after). This is the plan's own thesis defect reproduced in my own reporting: an issue closed reporting success while its postcondition was unverified. Issue 0.8a exists to catch exactly this and is now unblocked, so it WOULD have caught it at completion — but a milestone asserted it four issues early, which is the actual error. Remedy applied: ran assert-distinguishes for ctl-203, then AUDITED ALL EIGHT controls for a zero-exit assert-distinguishes row (all 8 now present) rather than fixing only the one reported. Standing correction: a milestone that names a mechanical verb must quote that verb's MEASURED exit code, never a summary claim derived from having run the underlying fixture. |
| `frontloadable` | yes |
| `detected_by` | operator |
| `evidence` | bash assets/redcheck.sh verify-all -> exit 1 (stderr: FAIL — ctl-203-exit-discipline: no assert-distinguishes observation with a ZERO exit); after assert-distinguishes -> exit 0, 'all 8 control(s) distinguished RED from GREEN' |
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
| `when` | 2026-08-26 |
| `stop_class` | 5 |
| `asked` | §6.1.5 validate-merged FULL tier on the merged tree |
| `answered` | FAIL on first run: clippy items-after-test-module in yf/src/cmd/harness/revert.rs — remove_rule_target had been APPENDED to the end of the file at Issue 2.2, placing it after mod tests. Invisible to every pre-merge check in this plan because cargo build and cargo test both accept it; only the FULL tier runs clippy with -D warnings. Fixed by moving the function above the test module; FULL then passed 51 commands, 0 failures, and the merge was committed. Recorded rather than silently repaired because it is evidence FOR the merge-back-first ordering plan-009 INV-4 introduced: a pre-merge validation would not have caught it either, but a post-merge one did, before anything was pushed. |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | change_validation.py run --tier full --json -> status fail, first_failure cargo clippy --workspace --all-targets -- -D warnings, returncode 101; after the fix -> status pass, 51 commands |
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
| `when` | 2026-08-26 |
| `stop_class` |  |
| `asked` | Parent verification instructed: 'DO NOT amend REQ-PORT-001/REQ-STRUCT-001/REQ-BAUTH-001 — amending them would write a false statement INTO the fixed-authority surface. There is NOTHING to amend.' |
| `answered` | THE VERIFICATION ITSELF WAS THE DEFECT, and complying would have shipped a genuine SPEC-first violation. Re-measured before acting: REQ ids are PER-SKILL NAMESPACED, so REQ-PORT-001 and REQ-STRUCT-001 EACH EXIST TWICE. The parent measured yf-plan/spec/portability.md:19 (index.md listing) and yf-optimal-instructions/spec/structure.md:6 (AGENTS.md primary); the ones under amendment were yf-research/spec/portability.md:6 and yf-beads-authoring/spec/structure.md:8. REQ-BAUTH-001, claimed not to exist, is at yf-beads-authoring/SPEC.md:29. The refuting grep returned no matches and I REPRODUCED that exactly — but it searched for the SHELL LITERAL while all three specs pin the idiom in PROSE ('the SKILL_DIR find idiom'), so the pattern could not match. Parent re-measured and withdrew the call in full. THE GENERAL LESSON: a verification that returns a clean negative is indistinguishable from an instrument that cannot see the thing. Reproducing the parent's own command and getting their result, THEN asking what that command could not match, is what separated the two. Compliance would have been the failure mode here, not the safe choice. |
| `frontloadable` | no |
| `detected_by` | self-report |
| `evidence` | git show HEAD:skills/yf-research/spec/portability.md | grep -n REQ-PORT-001 -> line 6, 'SKILL_DIR resolves via find over the root list ~/.claude/skills ...'; enumeration over git ls-files 'skills/*/spec/*.md' 'skills/*/SPEC.md' shows 5 distinct REQ-(PORT|STRUCT|BAUTH)-001 definitions across 5 files; parent's pattern 'find ~/\.claude/skills|SKILL_DIR=\$\(find' -> 0 matches (reproduced); 'SKILL_DIR.{0,40}find|find idiom' -> 3 matches |
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
| `asked` | Recurring class across this plan: when is an ENUMERATED set wrong where a DERIVED one would be right? |
| `answered` | SIX measured instances in one plan, which is why it is recorded as a class rather than six bugs. (1) Issue 1.5's hardcoded-path count was wrong twice before being derived (14, then 16; measured 32 across 8 files). (2) Issue 5.3's file set was 7, not the 4 drafted — the three extras included a GENERATOR and a diagram SOURCE. (3) check-glossary-terms carried an INVENTED ten-term list while asserting it was the measurement; the real ten came from EXP-005's table. (4) check-bd-dep-types carried a hardcoded type vocabulary, making it vacuous by construction — a doc naming a type outside the list was invisible to it. (5) SC6 ENUMERATED its scope as 'SKILL.md or skill README.md', so three hardcoded .claude/skills paths in the PROJECT README — a real functional bug for pi/opencode users — sat outside the criterion written to prevent exactly that. (6) The parent's refuting grep: A GREP PATTERN IS ITSELF AN ENUMERATION OF THE FORMS YOU EXPECT. It enumerated the shell-literal form and could not see the prose form, and it enumerated one REQ-id spelling ('^REQ-X-001:') where the repo also uses a bullet-bold form. The sixth is the sharpest because the instrument looked like a measurement rather than a list. REMEDY APPLIED: SC6's wording and its check widened to every instruction surface a reader may copy from, with a mutation test proving the widened check fails on a planted violation. |
| `frontloadable` | yes |
| `detected_by` | operator |
| `evidence` | SC6 pre-widening matched 0 of the 3 project-README sites; post-widening it matched them and a planted violation drove it to exit 1, restored to 0. Parent's own re-measurement confirmed instances (6): grep -rh -A4 without filenames, ^REQ-X-001: line-anchored colon form, and the shell-literal search. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-007

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-26 |
| `stop_class` |  |
| `asked` | Did the backgrounded check-harness-smoke.sh run, and was its output trustworthy? |
| `answered` | I reported to the operator that it 'did not run'. WRONG on both counts. It DID start (transcript header timestamped 03:44:43Z), TRUNCATED the hand-recorded transcript - the script rewrites the file on every invocation - wrote a partial pi section, and was killed by the 600s timeout mid-run. I then COMMITTED the resulting 19-line stub at 3c8a966 without noticing, and the full transcript had never been committed, so the original was lost and had to be rewritten from the conversation. Two distinct failures: (a) a background job with a destructive first action, whose partial completion I did not check before committing; (b) reporting 'did not run' from the absence of a completion notification rather than from reading the artifact. The artifact was on disk the whole time and said otherwise. Also surfaced a real script defect: the transcript recorded 'resolved tree: <unresolved>' for every harness, because the script called bare  and the PATH copy is the PRE-RELEASE binary with no such subcommand - so SC35's entire point (name the tree) degraded to a placeholder that still satisfied nothing. Fixed to resolve with the tree-under-test's binary. REMEDY: the rewritten transcript carries an explicit provenance note stating it is hand-recorded and that the script truncates on each run, so the next reader is not misled about which is authoritative. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | check-deployed-tree.sh exit 1 with 'does not cover opencode'; wc -l on the transcript = 19; git log on the path shows 3c8a966 as its ONLY commit, so the full version was never committed; transcript header timestamp 2026-08-27T03:44:43Z proves the run started |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

