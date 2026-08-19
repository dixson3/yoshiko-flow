---
type: Reference
okf_spec: OKF-PLAN
id: comment-62-draft
disposition: deferred
target: https://github.com/dixson3/yoshiko-flow/issues/62
status: DRAFTED — NOT POSTED (operator gated)
---

# Draft comment for #62 — propose a `yf-spec` skill

**Disposition: DEFERRED — the spec-linter half was Issue 7.5, in the descoped Epic 7. #62 stays OPEN.**

plan-047 delivered the general document-conformance engine (`_shared/doc_lint.py` plus
per-type `document_types/<type>.toml` schemas) that a spec linter would be an instance of, and
wired `skills/*/SPEC.md` and `skills/*/spec/*.md` into its trigger scope. The
`Verification:`-grammar linter itself was not built.

Incidentally fixed on the way: `skills/*/SPEC.md` was routed to `uv-herdr-launch` in
`CHANGE-VALIDATION.md` §3, so every skill's SPEC.md edit ran yf-herdr's launch-contract test
(#164). It now routes to the document linter.
