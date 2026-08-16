---
type: Reference
okf_spec: OKF-PLAN
---
# Draft comment for #111 (Investigate `br` / `ticket-rs` as beads alternatives)

**Disposition:** exclude — a different question. This issue stays **open**.
Drafted by plan-040 Issue 5.2a. Published by 5.2b, behind the *Upstream write* gate.

---

Not acting on this — it is a different question from **plan-040**, which only changed *how*
`yf-beads-upstream` writes upstream. But plan-040 moved one input to this investigation, so
noting it here rather than leaving it to be rediscovered.

**gh-direct narrows the `bd` surface a replacement would have to match.** Upstream writes no
longer go through `bd <backend> push` / `bd <backend> sync` at all. `bd` is now **read-only on the
write path**: it supplies bead content and receives one field back. Concretely, the upstream
mirror needs a candidate tracker to provide only:

- read bead fields — `title`, `description`, `issue_type`, `priority`, `labels`, `status`
- read them **in bulk** (`bd list --all --json`), including closed beads
- store and return one **arbitrary string per bead** (`external_ref`), with a bulk read
- an idempotent write of that field (`bd update --external-ref`)

That is a much smaller contract than "must implement a GitHub/GitLab/Jira sync engine with
conflict resolution". A candidate that has any external-reference field, or could carry one in
generic metadata, now clears this bar.

**Two caveats, so this is not read as more encouraging than it is:**

1. **This is one surface of several.** yf's dependency on `bd` also covers molecules
   (`bd mol pour`), gates, dependency graphs, the active-set classifier, and Dolt-backed
   versioning. plan-040 shrank the *upstream-tracking* surface only, and that was never the
   hardest part to match.
2. **plan-040 also raised a version floor.** The skill now records **bd 1.1.2** as its floor for
   `--external-ref` and for `bd list --all --json` carrying `external_ref` (REQ-BUP-055) — stated
   as an *assertion*, since it is the only version verified, not a version below which failure was
   demonstrated. A replacement must match that field's semantics, including that it is serialized
   **omitempty** (the key is absent, not null, on unmapped beads — measured on 998 of 1019 rows).

Net: mildly *informative* for this investigation, not a reason to start or drop it.

*Noted by plan-040 · plan folder: `docs/plans/plan-040-james-dixson-1cabe4/` · tracker: #138*
