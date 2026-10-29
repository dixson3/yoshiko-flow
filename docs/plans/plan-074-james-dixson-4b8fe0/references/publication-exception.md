---
type: Reference
okf_spec: OKF-PLAN
description: Operator permits only approved plan-bundle publication after artifact checks; FULL remains INCONCLUSIVE and all implementation/deployment gates remain intact.
---
# Plan-only publication exception

## Exact authority
The operator answered in master: **“Allow plan-only publication exception (Recommended)”**.

The exact master receipt is retained in `references/publication-exception.json`. It binds plan-074, master-checked clean HEAD `f1f381b7ed6fbf326d1d3693f5b63fc1040136d5`, and 188 unpublished paths, all within this plan bundle. This is a later bounded publication decision, not an alteration of the approved plan or its proposal hashes.

Only approved plan bookkeeping may be published. The planner must rerun applicable artifact, affected FAST, readiness, fingerprint and proposal-hash checks, then verify the complete unpublished path set including this exception bookkeeping, clean state and remote freshness immediately before push. Unrelated changes, failed checks or remote divergence require stopping. No validation manifest change or costly FULL rerun is authorized now.

## Actual FULL outcome — INCONCLUSIVE, never PASS
The first delegated invocation erroneously included a trailing positional dot. The runner rejected it at argument parsing with exit 2 and `unrecognized arguments: .`; zero recipe commands executed. This was an invocation error, not a repository test failure.

The corrected invocation was:

```sh
uv run "$HOME/.agents/skills/yf-change-validation/scripts/change_validation.py" run --tier full --json
```

It ran against clean main `f1f381b7ed6fbf326d1d3693f5b63fc1040136d5`. The execution tool timed out after 1,800 seconds during `trigger-eval`, before final JSON or the process exit code was captured. The recipe has 53 configured rows; completed/pass/fail counts are unavailable. Empty stdout is not success. The runner exit is unknown, and no repository-command failure is established.

`CHANGE-VALIDATION.md`'s trigger-eval row declares `--deadline-seconds 25200` and timeout `28800`. The delegated tool bound was insufficient for that declared budget. The validator subsequently found no matching runner or trigger-evaluation process. HEAD was unchanged and git status clean before and after. No automatic costly retry occurred.

The exact stdout, stderr, exit/timeout, HEAD, status and SHA-256 receipts are preserved under bundle-relative `assets/fixtures/intake-publication/invocation-error/` and `assets/fixtures/intake-publication/full-timeout/`. Empty `.json` stdout captures intentionally remain empty historical bytes; they are not valid structured verdicts and must not be repaired into fabricated JSON. Original source copies remain retained locally as well.

## Non-waivers
This exception does **not** waive implementation or merged-tree FULL validation, B1's exact deployment-tree FULL requirement, any semantic criterion, consent check or pour-fidelity check. FULL remains INCONCLUSIVE regardless of artifact/affected FAST results.

B1 remains conditional on its required successful disposable rehearsal and later explicit operator install-manifest and fresh-apply confirmations. B2 still approves external legacy-attested evidence policy only: no live PIM receipt write or H0 resumption. No graph retyping, permission broadening, landing-engine scope expansion or source-checker substitution is authorized.

Only master launches the fresh Opus executor after verified publication. This planner does not self-execute, pour, deploy or apply. H0 remains held.
