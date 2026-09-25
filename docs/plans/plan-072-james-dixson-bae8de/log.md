# Log

## 2026-09-25
- executing: OPERATOR DECISION: D9 dev spend ceiling raised $200 → $600 CC list-rate via assets/spend-ceiling.txt (plan text keeps $200 as the approved default). Reason: 'we have not come close to reaching the subscription limit on token spend' — the incident was a request-rate limit, not spend. All Epic 3 runs now pass --budget-usd 600
- executing: 3.2 incident: baseline tripped the shared model-account RATE limit (~381 runs/h for 1.6h; pi reaches the same account via cliproxyapi); last 14 CC runs were 0-token rate-limited and mis-scored; kill() PermissionError aborted the run, nothing recorded. OPERATOR DECISION: 'throttle the runs — there are always other sessions active' → REQ-SKAUTH-062 amended (0-token/429 INCONCLUSIVE, global --max-runs-per-hour default 150, adaptive backoff, --results/--resume); baseline resumed, not restarted
- executing: start gate resolved
- intake: epic yf-mol-t42s poured

- approved: operator approved

## 2026-09-24
- intake: tracker #416 filed; plan landed on local main at d32708d (not pushed); deliverable class standard; fingerprint dcbd16e3
- ready-for-approval: ready-check green — pass-5 (execution) APPROVE + audit pass
- review: post-APPROVE mechanical edit. SC3/SC5/SC6/SC9/SC10 prefixed `test -f <script> &&` so ready-check's smoke run sees a clean exit 1, not uv's unparseable spawn error ('cause: No such file', misread as path `cause`). Criterion semantics are unchanged, and each is still red pre-work
- review-pass: 5 (execution) — APPROVE, zero measured findings; all 35 prior resolutions re-verified by running their evidence
- review-pass: 4 (execution) — REVISE, 3 low concerns: CC spend misses subagent transcripts + 2 price classes; false-FAIL formula vs figures; FULL-row issue ordering. All 32 prior resolutions re-verified
- review-pass: 3 (execution) — REVISE, 8 concerns (0 high): all 24 prior resolutions re-verified; ledger USD source undercounts killed runs; 5.5 fails SPEC-first checkers; SC5/6/9/10 flags absent from Epics; SC4 pre-green
- review-pass: 2 (reading) — REVISE, 10 concerns (2 high): CC init lists only user-invocable skills, so the ⊇ check would make every candidate run INCONCLUSIVE; a streamed row could corrupt --json and land a red FULL as pass
- review-pass: 1 (reading) — REVISE, 14 concerns (4 high): FULL row would test the old installed text; FULL near-certain to fail as specified; unnamed rating state; SC4 fixtures absent
- review: plan v1 presented
- drafting: plan v1 synthesized from EXP-001..005
- investigating: EXP-003 baseline complete (cc 59/63, pi 57/63); EXP-002 partial — D3 cost needs operator re-decision
- investigating: 4 experiments identified (EXP-001..004); scoping decisions D1-D8 recorded

- scoping: initial scope captured

