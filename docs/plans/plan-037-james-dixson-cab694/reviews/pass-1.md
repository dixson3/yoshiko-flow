---
type: Review
okf_spec: OKF-PLAN
---
## Plan Red-Team: plan-037-james-dixson-cab694

## Verdict: REVISE

### Strengths

- The three-bucket classification is **evidence-based, not asserted**. The "safe to
  refresh" claim rests on exact blob matching against every historical version of each
  file, which is the right standard for a decision that authorizes overwriting.
- The `v=0.4.0`-is-not-the-tag trap is identified and documented. A reviewer repeating the
  work naively would have concluded 22 files were locally edited.
- Scope discipline on the adjacent `.yf/` issues is good: #102 excluded with a reason, and
  only its *question* (commit semantics) cross-referenced into Issue 2.1.
- The #100-before-#107 sequencing is correctly derived rather than assumed, and the reason
  (a verbatim port would add a third reader on the deprecated surface) is stated.
- Issue 1.2 + its capability gate correctly identify the single irreversible step.

### Concerns

- **The plan cannot satisfy its own Success Criterion 1** — severity: **high**
  Epic 1 refreshes user scope from `main` *before* Epics 2 and 3 have landed. The moment
  they merge, user scope is stale again — missing the new `#107` feature and `yf-herdr`
  entirely. There is no second refresh anywhere in the plan, so criterion 1 ("a fresh
  install reproduces the operator's setup; no differences") is false at plan completion.
  Recommendation: add a final issue after Epics 2 and 3 that re-installs from merged `main`
  and re-runs the `exp-01` three-pass verification. Reframe Epic 1's refresh as the
  *baseline*, and make the final re-install the actual criterion-1 gate.

- **Self-modification hazard: the plan overwrites the skill that is executing it** —
  severity: **high**
  Issue 1.3 re-runs the installer, which replaces `~/.claude/skills/yf-plan/scripts/plan_manager.py`
  and `SKILL.md` — the exact artifacts the running coordinator calls for `update-status`,
  `resume-scan`, `landing-lock`, and `close_cascade`. Epic 2 compounds it by moving
  `STATE_DIR` from `.yf/yf-plan/` to `.yf/plan/`, which relocates `landing.lock` — the lock
  Phase 6 acquires. Swapping the manager mid-execution risks a state-path change between
  lock acquisition and release.
  Recommendation: state an explicit self-modification policy. Either (a) exclude `yf-plan`
  from Issue 1.3's refresh and fold it into the final re-install after RECONCILE, or (b)
  require that any refresh touching `yf-plan` happens only at a phase boundary with no lock
  held. Name which, and record it in the plan rather than leaving it to execution-time
  judgment.

- **Repo policy requires Tier-2 testing that the plan omits** — severity: **medium**
  Epic 2 modifies `plan_manager.py`, a manager script. `TESTING.md` mandates Tier-1 unit
  tests **plus** a Tier-2 mechanical drive of the modified skill under a sandboxed `HOME`,
  and warns explicitly *"never trust the installed copy — it is the old, `rust-embed`-baked
  skill."* Issue 2.5 specifies Tier-1 only. That warning is doubly pointed here, since this
  plan's whole subject is a stale installed copy.
  Recommendation: extend Issue 2.5 to cover the Tier-2 sandboxed-`HOME` drive of the config
  precedence and root-configurability paths.

- **The capability gate's test command is not runnable** — severity: **medium**
  It references `$BACKUP` with no definition anywhere in the plan. A gate whose `Test:` cannot
  be executed as written is not a gate.
  Recommendation: pin a concrete backup path in Issue 1.2 and use it literally in the test.

- **Issue 1.1 has no defined branch behavior** — severity: **medium**
  It resolves whether the concatenated rules bundle is intentional or drift, and blocks 1.3 —
  but the plan says nothing about what happens in either outcome. If the answer is "drift,"
  fixing it is unscoped work of unknown size (installer change? new issue?).
  Recommendation: state both branches. Suggested: intentional → refresh in place, no further
  work; drift → file a follow-up issue and keep this plan's scope unchanged.

- **No issue updates #110, though Success Criterion 4 requires it** — severity: **medium**
  The criterion promises #110 is updated to record that the skill surface landed while the
  `herdr agent *` integration stays open. Reconcile handles dispositions generically, but a
  `partial` disposition needs specific in/out wording that no issue owns.
  Recommendation: give Issue 3.6 (or a new 3.7) explicit ownership of the #110 update, with
  the in-scope/out-of-scope split stated.

- **Verification will false-fail on `__pycache__`** — severity: **low**
  The `exp-01` comparison surfaced `__pycache__` directories differing between repo and user
  scope. These are build artifacts that will always differ. Criterion 1's "no differences
  other than the install stamp" would fail on them.
  Recommendation: exclude `__pycache__` (and `.DS_Store`) from the verification, in both
  Issue 1.4 and Criterion 1.

- **`#110` Resolved-By is a placeholder** — severity: **low**
  The Upstream Issues table says "Issue 3.x (partial)". Placeholder cell in a table that the
  reconciler reads.
  Recommendation: name the real issue once the #110-ownership concern above is resolved.

- **Issue 3.1 does not name the REQ id scheme** — severity: **low**
  "Bring to repo REQ-* discipline" without specifying the prefix leaves an executor guessing.
  Recommendation: specify `REQ-HERDR-*`, consistent with the other per-skill SPECs.

### Missing

- A post-merge re-install + re-verify step (the Criterion 1 gap above).
- An explicit self-modification policy for refreshing `yf-plan` while `yf-plan` is executing.
- Tier-2 test coverage mandated by `TESTING.md`.

### Gate Assessment

Three gates, and the count is right — no gate proliferation. The Start Gate and Reconcile
Gate are conventional and correctly typed. The two capability gates guard genuinely
irreversible or genuinely blocking decisions, which is the correct use.

But the "un-upstreamed work preserved" gate — the most important one in the plan, since it
guards the only unrecoverable step — has a `Test:` that cannot run (`$BACKUP` undefined).
The "config-tier semantics decided" gate is well-placed but has no `Test:` at all; for a
human decision gate that is acceptable, though a check that the decision file exists would
make it mechanical.

### Upstream Assessment

Dispositions are sound. #107/#100/#101 as `include` is correct and the dependency reasoning
(#100 supplies the reader the other two consume) is the right justification for pulling #101
in rather than scope creep. #102 and #109 are properly excluded with reasons.

The `partial` on #110 is the right call — importing the skill genuinely does not deliver the
`herdr agent *` fan-out investigation — but per the red-team rule that partials must be
specific about what is in and out, it currently is not, and no issue owns writing that split.
That is the medium concern above.

No supersedes claimed, correctly.

### Operator Resolutions

| # | Concern | Severity | Status | Resolution |
|:--|:--|:--|:--|:--|
| 1 | Cannot satisfy Success Criterion 1 (no post-merge re-install) | high | resolved | Added **Epic 4** (Issues 4.1–4.3): re-install all 19 skills from merged `main`, re-run the `exp-01` verification as the mechanical test of Criterion 1, then prove the backup redundant before retiring it. Criterion 1 rewritten to name Issue 4.2 as its measurement. |
| 2 | Self-modification: refresh overwrites the executing skill | high | resolved | Added an explicit **Self-modification policy** to Approach: `yf-plan` is excluded from Epic 1's refresh (Issue 1.3 now covers 18 skills) and reinstalled only in Issue 4.1, after RECONCILE, with no landing lock held. The accepted consequence — executing on the stale manager throughout — is recorded as a risk row rather than left implicit. |
| 3 | Tier-2 testing omitted (TESTING.md) | medium | resolved | Added **Issue 2.6**: Tier-2 mechanical drive under a sandboxed `HOME`, citing the "never trust the installed copy" warning and noting it binds doubly here. Criterion 5 now requires both tiers green. |
| 4 | Capability gate test references undefined `$BACKUP` | medium | resolved | Backup path pinned to `~/yf-preserve-plan-037/` in Issue 1.2; the gate's `Test:` is now a concrete runnable block covering all three artifacts. |
| 5 | Issue 1.1 branch behavior undefined | medium | resolved | Both branches specified: intentional → refresh in place, no follow-up; drift → refresh in place anyway, file a follow-up issue, installer explicitly out of scope. |
| 6 | No issue owns the #110 update | medium | resolved | Added **Issue 3.7**, owning the #110 update with the in/out split stated and #110 left open. Criterion 4 updated to match. |
| 7 | Verification false-fails on `__pycache__` | low | resolved | Issues 1.4 and 4.2 and Criterion 1 all now exclude `__pycache__/`, `*.pyc`, and `.DS_Store`. |
| 8 | #110 Resolved-By placeholder | low | resolved | Table cell now reads Issue 3.7, and the Notes cell carries the explicit in-scope/out-of-scope split. |
| 9 | Issue 3.1 REQ prefix unspecified | low | resolved | Specified `REQ-HERDR-*` plus the living-amendment log. |

**All 9 concerns resolved.** Per REQ-PLAN-030 a REVISE verdict requires a fresh red-team cycle
before the plan can reach `ready-for-approval`; see `pass-2.md`.
