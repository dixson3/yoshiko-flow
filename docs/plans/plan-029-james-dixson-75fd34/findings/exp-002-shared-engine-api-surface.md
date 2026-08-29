---
type: Finding
okf_spec: OKF-PLAN
experiment: Define the shared-engine API a `yf-okf` skill must expose so yf-research
  /
---
# Finding: yf-okf shared-engine API surface + where it lives

**Experiment:** Define the shared-engine API a `yf-okf` skill must expose so yf-research /
yf-incubator / yf-plan can delegate folder construction+management; map current construction
code and the `_shared/` vendoring precedent.

## Result

### Current construction models

- **yf-research** — `mkdir -p {scripts,artifacts,diagrams}` + `index_manager.py init` writes
  `_index.md` (underscore), an H1 + **4-column timestamped GFM table** (Timestamp/Phase/Artifact/
  Description). `add` appends rows oldest-first, auto-linkifies `.md`. No log file. **No
  frontmatter.** (`index_manager.py:17-100`, `SKILL.md:245-256`.)
- **yf-incubator** — agent writes a verbatim template (no scaffold script). Dir-form
  `Incubator/<kebab>/README.md` or single-file `Incubator/<kebab>.md`. **The one skill that emits
  frontmatter** (7 keys: `title/created/tags/status/last_reviewed/priority/aliases`), read by
  `incubator-index.py:parse_frontmatter` (`:26-40`; needs `status`+`last_reviewed`). Per-bundle
  listing = `## Files` body section; repo-level triage index = `Incubator/INDEX.md` (generated,
  not per-bundle). Change log = `## Decision log` free-prose body section.
- **yf-plan** — `plan.md` IS the manifest (no index file). Phase log inside plan.md (see exp-001).
  `**Field:**` bold-label header block. `reviews/` + `references/upstream-N.md`.

### Proposed yf-okf API (shared operations)

```python
scaffold_bundle(dir, *, subdirs, reserved=True) -> dict   # mkdir + reserved index.md/log.md
write_frontmatter(path, *, type, meta) -> None            # OKF: non-empty type + arbitrary meta
read_frontmatter(path) -> dict | None                     # generalize incubator parse_frontmatter
render_index(dir) -> str ;  add_index_entry(dir, path, desc, *, phase, ts)
append_log(dir, entry, *, date=None) -> None              # newest-first ISO-8601 date headings
check_conformance(dir) -> Report                          # reserved-file rules + type-on-every-.md
emit_conformant_copy(dir) -> Path
migrate(dir, *, dry_run=True) -> Plan                     # opt-in `yf-okf migrate`
```

- **Genuinely shared (≥2 skills):** `scaffold_bundle`, `write/read_frontmatter`, `append_log`,
  `check_conformance`, `migrate`.
- **Per-skill adapters needed:** index/log *rendering* — the three current models genuinely
  differ. Skill-specific and staying put: research's `plan.yaml`/`sources.json`/link-normalizer/
  credibility-scorer; plan's `reviews/`+beads wiring; incubator's repo-level `INDEX.md`+`## Resume`.

### Where it lives — `_shared/` vendoring (NOT import)

`_shared/` exists at repo root (`active_set.py`, `json_extract.py`, `manifest_update.py`,
`sync.py`, ...), deliberately outside `skills/` so `yf` doesn't enumerate it. **Skills cannot
import each other** (independent installability) — sharing is by **vendoring** via `_shared/sync.py`:
(a) fenced canonical region regenerated in-place (e.g. the defensive json extractor in
`research_manager.py:24-61` / `plan_manager.py:39-76`), or (b) whole-file copy (e.g.
`manifest_update.py` vendored byte-identical into 5 skills). Enforced by `yf-drift-check`
`value-equal` edges + `_shared/sync.py --check`.

**Recommendation:** yf-okf = **skill** (`skills/yf-okf/SKILL.md` + `scripts/okf.py`) for the user
surface (`/yf-okf migrate`, conformance check) **+ canonical `_shared/okf.py` whole-file-vendored**
into each consumer's `scripts/okf.py` (same pattern as `manifest_update.py`). Consumers shell out
(`uv run ${SKILL_DIR}/scripts/okf.py …`, as research already does with `index_manager.py`) or import
the co-located sibling. Add drift `value-equal` edges per vendored copy; register the canonical→copy
map in `_shared/sync.py`. Cross-skill `uv run ${OKF_SKILL_DIR}/…` is rejected — a skill can't assume
another is installed.

### Divergences that resist a uniform model

1. **Index filename/shape** — research `_index.md` timestamped table vs OKF `index.md` listing;
   plan has none; incubator's `## Files` section + repo-level `INDEX.md` don't fit per-bundle.
2. **Log model** — 3 incompatible (research none; plan in-file oldest-last **load-bearing** for
   status transitions; incubator free-prose section) vs OKF newest-first `log.md`.
3. **Single-file incubators** (`Incubator/<kebab>.md`) — no dir, no room for reserved index.md/log.md
   → OKF must exempt single-file form or force promotion to dir-form.
4. **Non-`.md` files** — research `plan.yaml`/`sources.json` must be explicitly excluded from the
   "frontmatter+type on every `.md`" conformance check.
5. **Frontmatter asymmetry** — only incubator emits it today; net-new for research + plan.

## Implications for Plan

- Engine = canonical `_shared/okf.py` + whole-file vendored `scripts/okf.py` per consumer + thin
  yf-okf SKILL for the migrate/conformance user surface. Preserves independent-installability.
- Shared for scaffold/frontmatter/log/conformance; index+log **rendering** need per-skill adapters.
- Highest-risk migrations: plan's load-bearing in-file phase log → `log.md`; research's `_index.md`
  table → `index.md` listing. incubator single-file needs an explicit exemption/promotion rule.

## Recommendations

- Lock the OKF `index.md` listing schema early; write research's migrate adapter first (closest
  analog).
- `append_log` newest-first from day one; give plan a compatibility shim (write both legacy in-file
  marker AND `log.md`) until the legacy reader is retired, since status transitions read the log.
- `check_conformance` skips non-`.md`; special-cases single-file incubators.
- Add drift `value-equal` edges per vendored `okf.py`, mirroring the `manifest_update.py` fan-out;
  register in `_shared/sync.py`.
