---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #182: yf-plan red-team: the read-only rule forbids the sandbox spike that catches specification defects

- **Number:** 182
- **Title:** yf-plan red-team: the read-only rule forbids the sandbox spike that catches specification defects
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## The rule as written forbids the one technique that catches specification defects

`skills/yf-plan/agents/red-team.md` makes the reviewer read-only (REQ-AGENT-043), and the
dispatching prose in `SKILL.md` reinforces it. The intent is right: **a reviewer must not fix what
it is asked to judge.** But the rule is drawn as *"never write, edit, or create any file"*, and that
prohibits a **sandbox spike** — building a throwaway prototype of one issue's deliverable, outside
the repository, to test whether the specification is sound.

### Measured evidence that the current wording costs real defects

plan-049 red-team pass 4 built a prototype of its own Issue 4.1 — "vendor `doc_lint.py` and
`document_types/` under `skills/yf-plan/scripts/`" — and ran the vendored copy against a real typed
`plan.md`:

```json
{"verdict": "PASS", "files_checked": 0, "errors": 0, "findings": []}
```

Cause: `_shared/doc_lint.py:47` computes `REPO_ROOT = Path(__file__).parent.parent`, so a vendored
copy resolves the repo root to the **skill directory** and every path glob matches nothing. Two
transitive imports were also missing from the issue's list.

**Four prior review passes read that issue and saw nothing wrong.** The fifth ran it. Without the
spike, plan-049 would have landed a green enforcement binding that enforces nothing — the precise
defect the plan exists to close. And no criterion caught it: `SC15` asserted only that the file
existed, and `SC17`'s expected `not-a-typed-document` is exactly what the broken copy emits.

This is the same class plan-047 measured six times: **a control invisible to inspection and visible
only to execution.** A purely-reading reviewer is structurally unable to find it.

### Proposed change to `red-team.md`

Replace the blanket prohibition with a scoped one plus an explicit authorization:

> **You may not modify the repository under review.** No writes, edits, deletes, or `git`
> mutations to the checkout you were given — including its `docs/`, `skills/`, `_shared/`,
> `tests/`, or bead database. The plan and its bundle are the main session's to change; a
> reviewer that edits what it judges has destroyed the independence that makes the review worth
> anything.
>
> **You MAY build a spike in a sandbox, and you are encouraged to when a specification's
> soundness cannot be established by reading.** A spike is a throwaway prototype of the smallest
> part of one issue's deliverable, built **outside the repository under review** — under the
> session scratchpad or a `mktemp -d` — run once to answer a specific question, and abandoned.
> It is evidence, not work.
>
> **Worked example.** An issue reads *"vendor `doc_lint.py` and `document_types/` under
> `skills/<name>/scripts/` so a deployed rule can invoke them."* Reading it establishes nothing
> about whether the vendored copy resolves its paths. So:
>
> ```bash
> SPIKE=$(mktemp -d)
> cp -Rf "$REPO/_shared/doc_lint.py" "$REPO/_shared/document_types" "$SPIKE/scripts/"
> uv run "$SPIKE/scripts/doc_lint.py" --path "$REPO/docs/plans/plan-047-*/plan.md" --json
> # -> {"files_checked": 0, ...}   the specification is unsound; report it
> rm -rf "$SPIKE"
> ```
>
> Report what you ran and what it returned, so the main session can reproduce it. **Never spike
> inside the repository under review, and never leave residue** — the main session must be able
> to run `git status` after your review and see nothing you did.

### Why the scoped form is safe

The prohibition's purpose — a reviewer must not edit what it judges — is fully preserved by
"may not modify the repository under review". What the blanket form additionally forbids is
building evidence somewhere else, which serves no purpose and costs the defect class above.

### Related

- plan-049 `reviews/pass-4.md` (the finding)
- plan-047's six vacuous controls, all invisible to inspection

