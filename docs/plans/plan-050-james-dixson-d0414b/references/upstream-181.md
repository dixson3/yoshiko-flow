---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #181: doc_lint: a bundle copied outside docs/plans/ returns a silent green, indistinguishable from clean

- **Number:** 181
- **Title:** doc_lint: a bundle copied outside docs/plans/ returns a silent green, indistinguishable from clean
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Copying a bundle outside `docs/plans/` to verify it yields a silent green

A natural way to test "would this bundle pass at `status: review`?" is to copy it to a scratch
directory, force the status, and run `doc_lint`. **That instrument is invalid and returns a
pass.**

Every `document_types/*.toml` keys on a directory prefix (`docs/plans/*/…`,
`docs/research/*/…`, `skills/*/…`) — deliberately, because path-keying is what makes the engine
inert in a repo with no yf documents. A bundle copied to `/tmp/probe/` matches no glob, so:

```json
{"verdict": "PASS", "files_checked": 0, "errors": 0, "findings": []}
```

— **byte-identical to the result for a path that does not exist.**

### Measured

plan-049's conformance reviewer was explicitly asked to use a scratch-root copy and refused,
reporting the instrument invalid and falling back to the in-place run. plan-048's EXP-004 measured
the same object for `--path` on an unselected file. The correct instruments are either an in-place
run (when the bundle already carries the status under test) or a scratch root that **reproduces the
`docs/plans/` prefix**.

### Proposed fix

Two options, not exclusive:

1. Document the trap in `_shared/document_types/README.md` and in `TESTING.md`, with the working
   form (`<scratch>/docs/plans/<bundle>/`).
2. Better: make `files_checked: 0` **loud**. A `--require-selection` flag, or a distinct
   `not-a-typed-document` verdict, so a caller cannot mistake "selected nothing" for "checked and
   clean". plan-049's Issue 4.3 already requires the on-edit rule to assert `files_checked > 0`;
   this generalizes it to every caller.

### Related

- plan-048 Motivation (the `docs/research/**` instance of the same object)
- plan-049 `reviews/pass-1.md` (the reviewer refusing the instrument)

