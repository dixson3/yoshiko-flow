---
type: Reference
okf_spec: OKF-PLAN
---
# Draft comment for #132 (`BACKEND_AUTH` has no jira entry — `--backend jira` emits `GITHUB_TOKEN`)

**Disposition:** supersede. This issue is **closed** by 5.2b — with the comment below, so the
distinction between *mooted* and *fixed* is on the record.
Drafted by plan-040 Issue 5.2a. Published by 5.2b, behind the *Upstream write* gate.

---

Closing this as **superseded by plan-040** — and stating plainly what that does and does not mean.

**The reported defect was real.** The per-backend auth table mapped only `github` and `gitlab`, so
`--backend jira` fell back to emitting a `GITHUB_TOKEN` — the wrong credential for Jira, and
silently wrong.

**It was not fixed. The surface it lived on was removed.** plan-040 changed upstream writes to
**gh-direct** (`bd` reads the bead, `gh` writes the issue, `bd update --external-ref` records the
mapping) and made GitHub the only supported backend (REQ-BUP-040). The `--backend` flag and the
`BACKEND_AUTH` table are both deleted, so the broken `jira` row **ceased to exist** rather than
being given a correct value.

This distinction matters for anyone who finds this issue closed later: **the Jira auth path was
not repaired.** There is no Jira auth path at all. Do not read this closure as "Jira auth works
now".

Two further consequences worth recording:

- **The skill now handles no token whatsoever.** Auth is delegated to `gh`'s own credential store,
  and the pre-write check is `gh auth status` rather than extracting a token (REQ-BUP-031). The
  class of bug this issue reported — the skill picking the wrong credential for a backend — is
  structurally gone, not just fixed for one row.
- **An existing `--backend` caller fails informatively.** Rather than a bare argparse
  `unrecognized arguments` error, the flag is detected and explained, naming the removal and
  pointing at #51/#52/#53 (REQ-BUP-059).

Adding Jira remains tracked at **#52**, which stays open and has been reframed: it now means "add
a Jira backend to a gh-direct architecture", and it carries this auth gap explicitly as a starting
condition.

*Superseded by plan-040 · plan folder: `docs/plans/plan-040-james-dixson-1cabe4/` · tracker: #138*
