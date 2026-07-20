# Upstream #89: yf-plan: for CI/infra/release plans, require one green end-to-end execution before 'complete'

- **Number:** 89
- **Title:** yf-plan: for CI/infra/release plans, require one green end-to-end execution before 'complete'
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement, type::task, priority::medium

## Body

**Lesson from a real plan (pybridge plan-010, CI code signing).**

The plan was marked `complete` when its code merged — but the behavior it *delivers* (code signing running on self-hosted macOS/Windows runners) had never actually executed. Validating it afterward surfaced **~a dozen distinct runner-environment bugs** across 13 release-candidate iterations (bash 3.2 empty-array/functions, GitHub `shell: bash` injecting `-e`, MSYS arg mangling, CRLF, `set -e`+unzip, pretty-printed-JSON parsing, non-ASCII in shell, Azure dlib x86-vs-x64, gh-release-upload silent no-op, softprops asset-wipe, blob-storage upload stalls, a notarization-propagation Gatekeeper modal, and a version/tag collision).

None of these were catchable at merge time — CI config that runs on (flaky, self-hosted) runners **cannot be validated locally**, and 'merged' is not 'works'.

## Proposal

For plans whose primary deliverable is **CI/infra/release configuration** (i.e. its correctness is only observable when it runs on the target), yf-plan's reconcile / land-the-plane should either:
- require **one green real execution** of the deliverable (e.g. a `workflow_dispatch` no-publish 'test build', or an actual release run) before allowing status `complete`; or
- record an explicit **deferred-validation bead** (open, upstream-tracked) so the plan doesn't read as 'done' while its central behavior is unverified.

This is a completion-criterion nuance, not a new phase: 'the code is merged' vs 'the thing the code does has been observed to work at least once'.

## Related pattern worth codifying alongside

A **`workflow_dispatch`, no-publish 'test build'** (guard the publish job on `github.event_name != 'workflow_dispatch'`) is the mechanism that made iterative validation possible without cutting real releases — worth mentioning as the recommended way to satisfy the criterion for release pipelines.
