# Finding: plan_manager.py coupling to README.md + in-plan.md phase log

**Experiment:** Map how deeply `yf-plan`'s `plan_manager.py` is coupled to the `README.md`
filename and the phase-log-inside-`plan.md`, to size the full-native-OKF rework.

## Result

### README.md coupling — a rework, not a rename

Five code sites plus spec/prose. Functional breakers:

| Site | file:line | Class |
|:--|:--|:--|
| `seed_readme()` | `plan_manager.py:368-411` writes `README.md` with `## File map` / `## Reading order` | hard (filename + headings) |
| `_README_REQUIRED_SECTIONS` | `:2186` = `("File map", "Reading order")` substring check | hard |
| `_audit_plan()` check #1 | `:2322-2337` requires `README.md` present + both section strings, else hard `fail` | hard |

The OKF `index.md` format (no frontmatter, `#`-heading + `- description` bullet list,
progressive disclosure) is **structurally incompatible** with the `File map`/`Reading order`
heading check. So README→index requires: rewrite `seed_readme` to emit OKF-format content,
drop/replace `_README_REQUIRED_SECTIONS` with an OKF-structure check, reword REQ-PORT-001.
Spec/prose refs to update: `spec/portability.md` REQ-PORT-001, `spec/data.md`
REQ-DATA-002, `SPEC.md:39`, `SKILL.md:235,1078`, `protocols/PLANS.md:24`, `agents/captor.md:44`,
`spec/agents.md` REQ-AGENT-060.

### Phase-log coupling — the deepest & riskiest axis

Phase log = `**Phase log:**` block in plan.md's **preamble before the first `## `**. Consumers
keying on the literal marker + `- ` lines:

- `update_status` (`:819-860`), `record_epic` (`:863-926`) — append log lines; **silently no-op**
  if the marker isn't in plan.md.
- `_plan_review_line_count` (`:2216-2221`, regex `- \d{4}-\d{2}-\d{2} review:`) → **REQ-PORT-006
  count-equality** (audit #5). Returns 0 if log leaves plan.md → hard `fail`.
- `_plan_first_scoping_date` (`:2207-2213`, regex `- (date) scoping:`) → **grandfather clause**
  (`:2316-2320`). Returns `None` → `grandfathered=False` → every migrated plan loses warn-downgrade
  and gets hard fails.

### Fingerprint is SAFE (the reassuring finding)

`_plan_content_sections` (`:944-964`) drops everything before the first `## ` heading;
`_plan_content_fingerprint` (`:967-983`) hashes only `## ` bodies (minus Upstream Issues). The
phase-log exclusion is **positional/implicit**, not a phase-log strip. Therefore:

- Moving the phase log OUT to `log.md` is **hash-neutral by construction**.
- Adding YAML frontmatter is **also hash-neutral**, *provided it sits above the first `## `*.

No fingerprint code needs to learn about `log.md`. The invariant "frontmatter above first `##`"
must be enforced by the shared engine (and covered by a test).

### Frontmatter — greenfield

`plan_manager.py` parses/emits **zero** YAML frontmatter (no `import yaml`; `plan.yaml` is a
line-scanned research artifact). Six `**Field:**`-line parsers (`ID/Author/Created/Status/Epic/
Fingerprint`) would need migrating only if header fields move INTO frontmatter — **recommend
keeping `**Field:**` lines and adding only `type:`** to minimize churn.

### Audit checks (6) reclassified

| # | Check | REQ | Under OKF |
|:--|:--|:--|:--|
| 1 | README + File map/Reading order | PORT-001 | needs-rework (rename + structure check) |
| 2 | context.md 5 sections | PORT-002 | +add `type` frontmatter check |
| 3 | Motivation present | PORT-004 | unaffected |
| 4 | references/upstream-*.md count | PORT-005 | +add `type` frontmatter check |
| 5 | pass-*.md == phase-log review lines | PORT-006 | **needs-rework (HIGH RISK)** — source moves to log.md |
| 6 | no dangling external refs | PORT-007 | unaffected (rglob covers new files) |
| gate | grandfather (first scoping date) | PORT-ACT | needs-rework — read date from log.md |
| new | every non-reserved .md has non-empty `type` | — | new global check |

### Migration surface (`yf-okf migrate <plan-dir>`)

1. README.md → index.md (rename + rewrite body to OKF listing + bundle-root `okf_version`).
2. **Extract phase-log → log.md** (oldest-first bullets → newest-first date headings). **CRITICAL:**
   preserve the first `scoping:` date into log.md in a machine-readable form, or the grandfather
   clause flips to `fail` and hard-fails every legacy plan. Single most dangerous step.
3. Keep `**Field:**` header lines; add only `type: plan` frontmatter above the first `## `.
4. Add `type` frontmatter to every non-reserved `.md` (findings/*, reviews/pass-*, context.md,
   references/upstream-*).
5. Fingerprint stays stable (content `##` sections unchanged) — assert with a test so migrated
   approved plans don't go stale-approved (REQ-PORT-041).

## Implications for Plan

- README→index and the phase-log move are **two distinct rework axes**; the phase-log move is
  high-risk (3 parsers, REQ-PORT-006 + grandfather).
- Fingerprint stability is guaranteed by positional exclusion — de-risks migration, but depends
  on the "frontmatter above first `##`" invariant.
- Frontmatter is pure new code (the shared engine's job).

## Recommendations

1. Scope the phase-log move as its own epic; gate on a test that a migrated plan preserves
   grandfather status + REQ-PORT-006 count-equality.
2. SPEC-first: REQ-PORT-001, -006, -040 (make exclusion explicit/frontmatter-aware), -ACT/
   REQ-DATA-012 (log format+location), new `type`-frontmatter REQ. Land before touching code.
3. Keep `**Field:**` lines; add only `type:`.
4. Add a fingerprint-stability test (phase-log removal + frontmatter-above-`##` are hash-neutral).
5. Migration preserves the first-scoping date into log.md as top priority.
