---
type: Reference
okf_spec: OKF-PLAN
id: upstream-175
---
# #175 — plan-047: mechanically parseable yf artifact documents — templates, linters, normalizer, extractor

**URL:** https://github.com/dixson3/yoshiko-flow/issues/175
**State:** OPEN
**Disposition:** tracker (the coarse plan-scale tracking issue; not a work row)

Filed 2026-08-19 at drafting, operator-authorized. Filed **before INTAKE** rather than at §4.5,
because `stamp-tracker` runs at the pour (§5.2a) and reads `_TRACKER_ROW_RE`
(`plan_manager.py:1383`), whose cell 1 must be `#<digits>` — so the row must already be real by
approval time. Red-team pass 3 (H3) measured the placeholder form returning
`{"status":"skipped"}`.

This is the one issue per AGENTS.md coarse granularity. Granular sub-beads are **not** pushed
upstream. Precedent: #167 (plan-046), #134 (plan-039), #115 (plan-037).

Body as filed: the objective, the measured 40% pour-defect rate (885 declared dependency edges vs
860 in `bd` — 45 dropped, 20 invented, across 17 of 43 comparable plans, with a positive control),
the enforcement-correlation control (0% drift on every enforced document type, 14–95% on every
unenforced agent-written type), the 11-epic scope, and the upstream dispositions (include #165,
#125; partial #113, #174, #149, #135, #62; exclude #173, #150, #145, #172).

Closed by Issue 10.5 at land-the-plane, after `stamp-tracker` records the `external_ref` on the
epic at the pour.
