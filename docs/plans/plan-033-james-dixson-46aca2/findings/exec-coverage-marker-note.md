# Execution note — coverage-gate marker convention for plan-033 REQs

`yf/src/coverage.rs::testable_reqs()` enforces ONLY the exact substring `*(testable)*`.
The Epic-1 SPEC amendment marked all new/revised plan-033 REQs as `*(testable, plan-033)*`
/ `*(testable, revised plan-033)*` (annotated), matching the pre-existing `#67`/`plan-027`
convention — so those REQs are EXCLUDED from the enforced coverage set (the build does not
force a tagged test for them).

**Decision (coordinator):** keep the annotated convention during build-out (avoids red
builds mid-execution as REQs land incrementally). Each implementation issue MUST add tagged
tests for its REQs (verified per-issue). **Final-validation checklist item:** reconcile
coverage — confirm every new plan-033 REQ has ≥1 tagged test in the suite; decide whether to
flip markers to plain `*(testable)*` (enforced) at that point. Two stale allowlist entries
(CLI-001/002) were removed by Issue 2.1 when the markers were annotated.
- verify_agreement (minimize.rs) is test-only -> clippy -D warnings dead_code. Wire it into the tune rule-deploy path (runtime agreement guard) OR annotate, during final cleanup (before merge-back validation). Not in the CHANGE-VALIDATION recipe (fmt+test+pytest), so not a current gate.
