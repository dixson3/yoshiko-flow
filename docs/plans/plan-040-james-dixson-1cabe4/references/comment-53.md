---
type: Reference
okf_spec: OKF-PLAN
---
# Draft comment for #53 (Linear upstream tracking support)

**Disposition:** exclude — **reframed, not rejected.** This issue stays **open**.
Drafted by plan-040 Issue 5.2a. Published by 5.2b, behind the *Upstream write* gate.

---

Reframing this after **plan-040**, which changed the mechanism this issue was filed against.

`yf-beads-upstream` no longer writes through `bd <backend> push`. Writes are now **gh-direct**:
`bd` reads the bead, `gh` creates or edits the issue, and `bd update --external-ref` records the
mapping. The `--backend` flag and the per-backend auth table were **removed** (REQ-BUP-040) —
GitHub is the only supported backend.

**Linear is affected differently from #51/#52, and it is worth being precise about it.** GitLab
and Jira had config-only stubs that were deleted; **Linear never had one** — `bd`'s upstream sync
covered github/gitlab/jira only. So nothing was removed here.

What changed is the *shape of the work*. Previously, adding Linear meant waiting on (or
contributing) a `bd linear` backend, since the skill could only write through whatever `bd`
implemented. Under gh-direct the skill owns the write path itself, so **the skill is no longer
gated on `bd` gaining a backend**. Adding Linear now means implementing the `create_or_update`
contract — create vs edit keyed on `external_ref`, the REQ-BUP-054 field mapping,
restrict-and-drop labels, structural verification — against Linear's API or CLI.

That is a larger job than #51 in one respect: Linear has no `gh`-equivalent first-party CLI in the
same shape, so it likely means an API client rather than shelling out. But it is a **smaller** job
in the respect that mattered most — it no longer depends on an upstream project's roadmap.

If Linear is picked up, route it through the same `create_or_update` core rather than beside it.
Two write paths with different conventions is exactly what produced #129.

*Filed by plan-040 · plan folder: `docs/plans/plan-040-james-dixson-1cabe4/` · tracker: #138*
