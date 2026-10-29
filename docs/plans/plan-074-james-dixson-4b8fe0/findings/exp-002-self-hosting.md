---
type: Finding
okf_spec: OKF-PLAN
description: Self-hosting needs explicit operator bootstrap authority and a disposable recovery rehearsal; a session boundary alone is insufficient.
---
# EXP-002 — Self-hosting landing boundary

## Finding: No fully supported self-deploying sequence established

### Approach Tested
Independent read-only investigator `bootstrap` inspected installed yf-plan SKILL, landing spec and manager, repository AGENTS.md and TESTING.md. It ran AST-extracted pure logic with in-memory subprocess/journal stubs, not a real land or database. The first stub probe had an argument-count error; the corrected probe succeeded. No repository or real tracker writes occurred.

### Result
**measured:** Installed manager SHA-256 `1b1cd81c86234121c32a3bcfdb2f66b315dff299881825d6ac356524aa643085` matches source at `8c97581e85fd48ebdfac45866b03fd213b9a783a`. Installed/source landing spec SHA-256 is `fd45959cf3db3336f0b371b6616868c6a6ed5b12a27dce3021644069b087e8a7`.

**measured:** `spec/landing.md:54–80` orders FULL validation and implementation push before fidelity, while deployment is L19, after fidelity L14 and complete L15. Installed manager lines 9476–9540 selects `pour_fidelity.py` beside itself and halts on exits 1 and 2. Editing source alone cannot affect that call.

**inferred:** The repair can publish validated implementation and remain unable to complete/deploy itself. Corroborated by normative ordering and executable path selection; the future real landing has not been run.

**measured:** Repository AGENTS.md prohibits mid-execution installation and requires clean synchronized main, FULL merged-tree validation and deployment last. TESTING.md likewise places promotion last. Ending a session removes mixed old-prose/new-script risk but does not retire the landing-order constraint.

**measured (investigator's AST stub probe):** `_land_resume_done("L_RECONCILED")` skips L1–L7, but re-executes L0 and L8–L19. No L14-specific journal phase exists. Re-preview/revalidation is required when decision facts change; apply-time digest binding is at manager lines 8330–8364 and 8850–8891.

**measured (investigator's AST stub probe, not live landing):** Starting from L_RECONCILED, successful L0 then failing L11 yielded `halted_at=l11_recheck_criteria`, `journal_phase=L_LOCKED`, `journal_writes=['L_LOCKED']`. L0's phase can overwrite earlier recovery progress. This is a bootstrap hazard, not authority to implement an unrelated landing repair.

**measured:** Landing halt can write the plan log (manager 6382–6396). Preserving/publishing bookkeeping to regain clean main changes HEAD; changed-file inference uses HEAD first-parent range (7679–7715). Do not assume the old decision or L19 change detector remains valid.

### Implications for Plan
No exception is currently authorized. A first-push → halt → terminate executor → clean/sync → install → fresh completion sequence needs an explicit plan-specific ordering exception and disposable rehearsal. It must never imply fidelity success before actually passing. A failed replay must stop for assessment rather than blindly retrying a regressed journal.

### Recommendations
Ask master to obtain a separate operator decision before adopting early promotion: permit only the fully validated published compatibility repair to deploy between terminated executor and fresh completion sessions, before this plan's L14–L18, without fidelity waiver, graph mutation, consent substitution or general landing-order change. Require mechanical rehearsal of bookkeeping, exact deployment-tree validation, changed-set behavior, and repeated-failure recovery. If additional landing-code changes are necessary, stop and request separate scope. Safe no-answer default: remain blocked, no installation or landing.
