---
type: Reference
okf_spec: OKF-PLAN
---
# Draft comment for #51 (GitLab upstream tracking support)

**Disposition:** exclude — **reframed, not rejected.** This issue stays **open**.
Drafted by plan-040 Issue 5.2a. Published by 5.2b, behind the *Upstream write* gate.

---

Reframing this after **plan-040**, which changed the mechanism this issue was filed against.

`yf-beads-upstream` no longer writes through `bd <backend> push`. Writes are now **gh-direct**:
`bd` reads the bead, `gh` creates or edits the issue, and `bd update --external-ref` records the
mapping. With one writer there is nothing to dispatch on, so the `--backend` flag and the
per-backend auth table were **removed** (REQ-BUP-040).

**That removal deleted a stub, not working support.** The SPEC, `GR-BUP-004`, and
`spec/backends.md` REQ-BE-001 all already said GitLab was an *unverified config-only stub* — no
push had ever been exercised against a live GitLab instance. The stated capability was already
zero; what existed was a flag implying a choice that led nowhere.

**So this issue is now a cleaner request than it was.** It used to mean *"finish wiring a
half-present bd backend"* — inheriting whatever `bd`'s GitLab path did or didn't do. It now means
**"add a second backend to a gh-direct architecture"**: implement the `create_or_update` contract
(create vs edit keyed on `external_ref`, the REQ-BUP-054 field mapping, restrict-and-drop labels,
structural verification) against `glab` instead of `gh`. That is a well-defined surface with a
reference implementation beside it.

One measurement worth keeping from the old design, preserved in `spec/backends.md` REQ-BE-002
(marked superseded rather than deleted): **backend CLIs do not share a flag vocabulary.**
`bd jira sync` used `--push`/`--pull` and `--create-only` where GitHub/GitLab used `--push-only`.
Expect `glab`'s issue surface to differ from `gh`'s in the same way, and design the abstraction
boundary at the *operation* (create/edit/label) rather than at the flag.

Also relevant: plan-040 kept two mechanisms from coexisting on purpose. Two write paths with
different conventions is what produced #129 (a comma-joined id list matching **zero** beads while
exiting 0, after which the destructive stage tombstoned every bead). Whoever adds GitLab should
route it through the same core rather than beside it.

*Filed by plan-040 · plan folder: `docs/plans/plan-040-james-dixson-1cabe4/` · tracker: #138*
