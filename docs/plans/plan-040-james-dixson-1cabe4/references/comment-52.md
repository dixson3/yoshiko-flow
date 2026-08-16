---
type: Reference
okf_spec: OKF-PLAN
---
# Draft comment for #52 (Jira upstream tracking support)

**Disposition:** exclude — **reframed, not rejected.** This issue stays **open**.
Drafted by plan-040 Issue 5.2a. Published by 5.2b, behind the *Upstream write* gate.

---

Reframing this after **plan-040**, which changed the mechanism this issue was filed against.

`yf-beads-upstream` no longer writes through `bd <backend> push`. Writes are now **gh-direct**:
`bd` reads the bead, `gh` creates or edits the issue, and `bd update --external-ref` records the
mapping. With one writer there is nothing to dispatch on, so the `--backend` flag and the
per-backend auth table were **removed** (REQ-BUP-040).

**That removal deleted a stub, not working support** — the SPEC and `spec/backends.md` REQ-BE-001
already described Jira as an *unverified config-only stub*.

**Jira is the hardest of the three, and the removal makes that visible rather than hiding it.**
Two specifics carried forward from the deleted surface:

1. **Auth was actively broken** (#132). The per-backend auth table had **no `jira` row**, so
   `--backend jira` fell back to emitting a `GITHUB_TOKEN` — wrong for Jira, and silently so.
   #132 is now closed as **superseded**: the table ceased to exist rather than being fixed. Any
   Jira implementation starts from no auth path at all, which is at least honest.
2. **The field model genuinely differs.** GitHub/GitLab take flat labels; Jira has projects, issue
   types, and required fields. The REQ-BUP-054 field mapping (`title`→title, `description`→body,
   `issue_type`→`type::<t>`, `priority`→`priority::<word>`) is written against a label-based
   tracker. Jira needs a real mapping decision, not a translation of that one — and plan-040
   specified the GitHub mapping in writing for the first time, so there is now something concrete
   to map *from*.

Also preserved deliberately in `spec/backends.md` REQ-BE-002 (marked superseded rather than
deleted): the measured fact that **`bd jira sync` used `--push`/`--pull` and `--create-only`**
where GitHub/GitLab used `--push-only`. That divergence is why the old translation table existed;
it is kept as history so a future implementer does not have to re-derive it.

So this issue now means **"add a Jira backend to a gh-direct architecture"** — with a reference
implementation beside it, a written field mapping to diverge from, and the auth gap stated up
front instead of discovered at runtime.

*Filed by plan-040 · plan folder: `docs/plans/plan-040-james-dixson-1cabe4/` · tracker: #138*
