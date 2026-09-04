---
type: Escalation
okf_spec: OKF-PLAN
description: Open questions raised to the upstream controller during execution, with
  alternatives, a recommended default, and what happens if no answer arrives.
---
# Escalations

Questions this plan raised to its upstream controller, newest last. Each `## ESC-NNN` section
is one entry; `ESC-NNN` ids are append-only and are never reused or renumbered.

**The architecture is WRITE-THEN-NOTIFY, never ask-and-await.** The herdr channel has no
answer-return primitive, so the escalation IS this artifact and any push is merely a
notification about it. That is why `on_no_answer` is required on every entry: an escalation
that omits its own default pretends to a round-trip the transport cannot deliver.

`recommended` is stored SEPARATELY from `answer`, and the separation is the point. The
dominant operator input across the corpus is a choice among stated alternatives, and a schema
that records only the resolution destroys the default it was chosen against.

An escalation whose recommended default was taken **without an answer arriving** is
`resolved`, not `raised` — with `answer` recording the default that was taken. Leaving it
`raised` would make every fire-and-forget escalation trip the close-time open-escalation
warning, which would train a reader to ignore it.

## ESC-001

| Field | Value |
| :-- | :-- |
| `question` | SC13c (check_amendment_log --plan plan-062) fails assertion A2: every implementation issue must have a depends-on path to a REQ-naming Epic-0 issue, but ALL 17 of them hang off 0.7 (branch creation), which names no REQ. The plan's Approach asserts SPEC-first ordering; its depends-on graph does not express it. Fixing it requires editing plan.md's ## Epics section on an already-approved, already-poured plan. |
| `alternatives` | A: Add 0.5 to 1.1's depends-on and 0.4 to 2.0's depends-on (the two implementation entry points), add the matching bd dep edges so pour fidelity holds, and leave the fingerprint STALE rather than rewriting it.; B: Declare a no-req-required set in plan.md covering all 17 issues — same plan.md edit, but semantically false (these issues do implement REQ-LAND-028/029).; C: Halt and hand SC13c back to the operator unresolved. |
| `recommended` | A: Add 0.5 to 1.1's depends-on and 0.4 to 2.0's depends-on (the two implementation entry points), add the matching bd dep edges so pour fidelity holds, and leave the fingerprint STALE rather than rewriting it. |
| `on_no_answer` | Take A. It is the smallest edit, it is what the plan's own Approach already says in prose ('SPEC-first, then the RESUME FIX, then the seam'), and 1.1 genuinely implements REQ-LAND-029 while 2.0 genuinely tests REQ-LAND-028. The fingerprint is deliberately NOT rewritten: the content did change, so the stale-approved signal is CORRECT and erasing it would launder an unreviewed edit. A crash-resume will need /yf-plan execute --force with this entry as the reason. |
| `detected_by` | mechanical-check |
| `evidence` | uv run scripts/check_amendment_log.py --plan plan-062-james-dixson-c3e98f -> exit 1; 'FAIL - implementation issue(s) with no depends-on path to a REQ-naming Epic-0 issue, and not in the declared no-req-required set [4.6, 4.7]: [1.1, 1.2, 2.0, 2.1, 2.2, 2.3, 4.1, 4.2, 4.3, 4.4, 5.1, 5.1b, 5.1c, 5.2, 5.3, 5.4, 5.5]'. A1 (amendment-log coverage) passes. |
| `asked_of` |  |
| `state` | resolved |
| `answer` | Alternative A taken as the on-no-answer default. plan.md Issue 1.1 depends-on is now '0.5, 0.7' and Issue 2.0's is '0.4, 0.7'; the two matching bd edges (yf-mol-tm2d.2.1->1.5, 3.1->1.4) were added so pour fidelity holds. check_amendment_log now reports '4 amended id(s) all carry an amendment-log bullet; all 16 non-exempt implementation issues reach a REQ-naming Epic-0 issue', exit 0. The **Fingerprint:** was deliberately NOT rewritten — the plan's content genuinely changed, so the stale-approved signal is correct; a crash-resume needs /yf-plan execute --force citing ESC-001. |
| `raised_when` | 2026-09-03 |
| `resolved_when` | 2026-09-03 |
| `no_answer_taken` | yes |
| `push_batch` |  |

## ESC-002

| Field | Value |
| :-- | :-- |
| `question` | The three assets/upstream-drafts/ bodies are caught in #326 directly. OKF (REQ-OKF-003) requires YAML frontmatter on every bundle file, but _land_upstream_rows posts these files VERBATIM as GitHub comments — so frontmatter present means three public comments on #327/#266/#304 that open with a raw YAML block, and frontmatter absent means the bundle FAILS its own portability audit with three [fail] findings. #326 is the fix and was deferred out of this plan's scope at pass 4. |
| `alternatives` | A: Add the frontmatter — the bundle stays audit-clean, and the handoff (Issue 5.5) records LOUDLY that L7 will post a raw YAML header into three public comments unless the operator fixes #326 first or edits the comments after.; B: Omit the frontmatter — the posted comments are clean, but the bundle ships failing its own audit with three [fail] findings, which is a declared stop-class-5 mechanical check failing.; C: Fix #326 now, stripping frontmatter at post time per findings/exp-003's completed design — correct, but it is scope the operator explicitly cut at pass 4, and it would land an unreviewed change in the L7 write path. |
| `recommended` | A: Add the frontmatter — the bundle stays audit-clean, and the handoff (Issue 5.5) records LOUDLY that L7 will post a raw YAML header into three public comments unless the operator fixes #326 first or edits the comments after. |
| `on_no_answer` | Take A. A failing portability audit is a mechanical check failing, which this plan's own contract treats as a halt condition, whereas a cosmetically ugly comment header is legible and repairable after the fact by anyone reading it. Crucially A keeps the decision REVERSIBLE and in the operator's hands at land time — they hold the landing anyway, so they can fix #326 first, strip the headers by hand, or accept them. B ships a defect that no later reader can distinguish from carelessness. |
| `detected_by` | mechanical-check |
| `evidence` | plan_manager.py audit --json-output -> status fail, with three [fail] okf:assets/upstream-drafts/{266,304,327}.md REQ-OKF-003 'no YAML frontmatter block' plus three [warn] doc-lint/asset-type-declared. land --dry-run confirms all three rows now report draft_present=true and requires_mention=true, so all three WILL be posted by L7. #326 is OPEN and labelled deferred (re-labelled by Issue 5.1 this session). |
| `asked_of` |  |
| `state` | resolved |
| `answer` | Alternative A taken as the on-no-answer default. YAML frontmatter (type: Record, okf_spec: OKF-PLAN, description) added to all three of assets/upstream-drafts/{327,266,304}.md. The bundle audit returns to pass and reindex --check exits 0. THE CONSEQUENCE IS NOT DISCHARGED, only made the operator's to decide: because #326 is unfixed, L7 will post those three files VERBATIM, so the comments on #327, #266 and #304 will each open with a raw YAML block. Issue 5.5's handoff carries this as a named pre-landing decision with three options — fix #326 first using the completed design in findings/exp-003, strip the three headers by hand before landing, or accept the headers and edit the comments afterwards. |
| `raised_when` | 2026-09-03 |
| `resolved_when` | 2026-09-03 |
| `no_answer_taken` | yes |
| `push_batch` |  |

## ESC-003

| Field | Value |
| :-- | :-- |
| `question` | Issue 5.3's FULL tier is RED — 1 of 21 commands fails, and it is NOT this plan's code. test_config_tiers.py::test_no_config_yields_defaults asserts _bootstrap_config() == {} but calls it OUTSIDE the _in_cwd helper, so it resolves against the REAL repo cwd and reads the plan-mandated .yf/plan/config.local.json, getting {'execute.worktree': False}. The file is UNTRACKED and gitignored (.gitignore:25), so it is absent from the merged tree and CI would never see this. Fix the test, or record the red and move on? |
| `alternatives` | A: Fix the one-line isolation defect — wrap the call in _in_cwd, the pattern the same file already uses correctly at lines 150, 161 and 168. Minimal, makes the test correct regardless of local config, and lets SC15 be measured honestly.; B: Record the red as environmental and proceed — argue SC15 says 'on the merged tree' and the merged tree has no such file. True, but it leaves a test that passes or fails depending on an untracked file nobody will remember.; C: Delete or move the config file to make the tier green — rejected outright. Gate 1's Instructions say remediation is a RESTART not a toggle, and it would silently re-decide the execution mode mid-run. |
| `recommended` | A: Fix the one-line isolation defect — wrap the call in _in_cwd, the pattern the same file already uses correctly at lines 150, 161 and 168. Minimal, makes the test correct regardless of local config, and lets SC15 be measured honestly. |
| `on_no_answer` | Take A. The defect is real and one line — the test file demonstrates the correct pattern three times immediately below the broken call. B would have me certify SC15 by argument rather than measurement, which is the vacuous-check habit this whole plan exists to attack. C is unsafe. A is scope beyond plan-062 and that is stated plainly rather than hidden, but a red FULL tier is a declared stop-class-5 halt and fixing the instrument is the cheapest honest route past it. |
| `detected_by` | mechanical-check |
| `evidence` | change_validation.py run --tier full -> status fail, 21 commands, first_failure uv run skills/yf-plan/scripts/test_config_tiers.py returncode 1, '1 failed, 30 passed'. Assertion: 'assert {"execute.worktree": False} == {}' at test_config_tiers.py:107. git ls-files --error-unmatch on the config -> 'Did you forget to git add?' (untracked). git check-ignore -v -> .gitignore:25 /.yf/*/*. Lines 150/161/168 of the same file wrap their calls in _in_cwd; line 107 does not. |
| `asked_of` |  |
| `state` | resolved |
| `answer` | Alternative A taken as the on-no-answer default. test_config_tiers.py:107 now calls _in_cwd(repo, pm._bootstrap_config) instead of pm._bootstrap_config(), matching the pattern the same file already uses at lines 150, 161 and 168, with a comment recording the measured symptom. That file alone: 31 passed. Stated plainly — this is scope beyond plan-062. It is taken because a red FULL tier is a declared stop-class-5 halt and because certifying SC15 by argument rather than measurement would be the vacuous-check habit this plan exists to attack. |
| `raised_when` | 2026-09-03 |
| `resolved_when` | 2026-09-03 |
| `no_answer_taken` | yes |
| `push_batch` |  |

