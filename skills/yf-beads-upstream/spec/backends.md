# Spec: Backends & trigger split

## Requirements

- **REQ-BE-001 (revised plan-040):** GitHub is the **only supported backend**. The `--backend` flag
  and the `BACKEND_AUTH` table are removed; the write path is `gh`-only with no backend dispatch.
  — *Rationale:* honesty about coverage, carried to its conclusion. This requirement **already
  said** GitLab and Jira were config-only stubs that must not be presented as tested, so the
  *stated* capability was already zero — what remained was a flag implying a choice that led
  nowhere. This **deletes a stub surface; it does not withdraw support.** Keeping a half-wired
  dispatch alongside the real one is also the two-mechanisms-with-different-conventions condition
  that produced #129. #51/#52/#53 stay **open**, reframed as "add a backend to a gh-direct
  architecture" — a cleaner request than "finish wiring a half-present bd backend". — *Verify:*
  SKILL.md "Backend generalization" §; absence of `BACKEND_AUTH` and of an
  `add_argument("--backend"…)` registration in `upstream.py`; SPEC.md REQ-BUP-040.

- **REQ-BE-002 (superseded plan-040):** The backend-generic scoped-push **translation table is
  dead** — under gh-direct there is no `bd <backend>` sync call to translate, and per REQ-BE-001 no
  backend to dispatch on. Retained as **history, not a live requirement**: the divergence it records
  was real and measured (`--issues`/`--parent`/`--dry-run` on `bd github|gitlab|jira sync`, with
  Jira using `--push`/`--pull` and `--create-only` instead of `--push-only`), and a future "add a
  backend" needs to know that backend CLIs do not share a flag vocabulary. — *Rationale:* deleting
  the entry would discard a measurement that a later backend author would have to re-derive.
  Nothing shall be implemented against it. — *Verify:* n/a (historical).

- **REQ-BE-003 (revised plan-040):** The backend states are now **two** — `github` and `none` — and
  both are first-class; `none` remains fully disabled and re-enableable. — *Rationale:* disabling is
  a supported configuration, not an error state. The `gitlab`/`jira` states are removed with the
  dispatch surface (REQ-BE-001); `none` is unaffected, and the default-deny short-circuit
  (REQ-BUP-010) is unchanged. — *Verify:* SKILL.md Backends table; REQ-OP-003.

- **REQ-BE-004 (trigger split):** Intent triggers (`init`, `status`/pull, "set up upstream tracking",
  "push beads upstream") live in the SKILL `description`; the procedural close-time/land-the-plane
  push trigger lives only in the always-loaded companion rule, never in the description. — *Rationale:*
  a description cannot reliably catch "wrapping up"; an always-loaded rule can. — *Verify:* SKILL.md
  frontmatter description + "Trigger split" §; protocols/UPSTREAM_TRACKING.md.

- **REQ-BE-005:** This is a utility skill — no formula, `bd mol pour`, or coordinator loop. — *Rationale:*
  the work is config + scoped CLI calls, not a multi-bead DAG. — *Verify:* absence of `formulas/`,
  `bd mol pour` in SKILL.md.
