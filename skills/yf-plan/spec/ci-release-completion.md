# CI/infra/release completion criterion (REQ-PLAN-069)

Guidance for the `ci-release` deliverable-class completion gate: how to satisfy it, and the
recommended `workflow_dispatch` no-publish "test build" pattern for exercising a release pipeline
without cutting a real release.

## Why this gate exists

CI/infra/release configuration — a GitHub Actions workflow, a release/signing/notarization
pipeline, an infra/deploy config — is only correct when it **runs on the target**. `merged` is not
`works`: the merged-state validation (REQ-PLAN-060) runs the repo's build/test suite on the landing
machine, which cannot observe a workflow that only executes on push/dispatch/release against real
(often self-hosted, flaky) runners. The lesson driver is upstream #89 (pybridge plan-010 CI code
signing): the plan read `complete` at merge, but the signing behavior it delivered had never
executed — validating it afterward surfaced ~a dozen distinct runner-environment bugs across 13
release-candidate iterations, none catchable at merge time.

So for a `ci-release` plan, `complete-gate` (REQ-PLAN-069) hard-gates `complete` on **one** of:

1. **Green-execution attestation** — a `log.md` `- validated: <run URL/id> — <note>` bullet
   (REQ-PLAN-069b / REQ-DATA-016) recording one observed green run. Record it with
   `plan_manager.py attest-validation "${plan_dir}" "<run-url>" --note "<what ran>"`, or write the
   bullet by hand.
2. **Open deferred-validation bead** — carry the unverified behavior forward as tracked debt (below).

Ordinary (`standard`) plans are never gated — the criterion is a strict no-op unless the plan's
`**Deliverable-class:**` is `ci-release`.

## The `workflow_dispatch` no-publish "test build" pattern

The recommended way to satisfy the green-execution criterion for a release pipeline **without
cutting a real release**: add a `workflow_dispatch` trigger and **guard the publish/release job** on
`github.event_name != 'workflow_dispatch'`. A manual dispatch then exercises the full build on real
runners (proving the runner-only behavior works) but publishes nothing.

```yaml
name: release
on:
  push:
    tags: ["v*"]        # real release path
  workflow_dispatch: {}  # manual "test build" — exercises the pipeline, publishes nothing

jobs:
  build:
    runs-on: [self-hosted, macOS]   # the runner-only-observable environment
    steps:
      - uses: actions/checkout@v4
      - name: Build + sign + notarize
        run: ./scripts/build-and-sign.sh   # the behavior that must actually run

  publish:
    needs: build
    # PUBLISH GUARD: skip the release/upload job on a manual test-build dispatch
    if: github.event_name != 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - name: Upload release assets
        run: ./scripts/publish-release.sh
```

Dispatch the workflow manually, confirm the `build` job is green on the real runner, then attest:

```bash
plan_manager.py attest-validation "${plan_dir}" \
  "https://github.com/<owner>/<repo>/actions/runs/<id>" \
  --note "workflow_dispatch test build — build+sign+notarize green, publish guarded off"
```

## Deferring validation (option 2)

When a real green run is not yet achievable (e.g. runners unavailable at land time), file a
**standalone, out-of-tree** deferred-validation bead — **not** a child of the plan epic, or
`close_cascade` (REQ-PLAN-067) would fail-loud on it first:

```bash
bd create "Deferred validation: <plan-id> <deliverable> not yet run green" \
  -t task -p 1 \
  --label deferred-validation \
  --metadata '{"plan":"<plan-id>"}'
# then push it individually upstream (a deliberate per-bead exception to coarse granularity)
```

`complete-gate` finds it by `bd list --label deferred-validation` filtered on the `plan` metadata,
so the plan can reach `complete` while its central behavior stays visibly unverified upstream.

## References

- SPEC.md REQ-PLAN-069 / 069a / 069b; `spec/phases.md` REQ-COMPLETE-001/002; `spec/data.md`
  REQ-DATA-016; `spec/cli.md` REQ-CLI-015/016/017.
- Upstream #89 (the lesson driver).
