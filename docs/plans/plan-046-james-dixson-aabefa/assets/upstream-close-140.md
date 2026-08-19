Closing as **partial**. plan-046 built the root tier and deliberately did not build the nested tier.

**IN (delivered):**
- Root-scoped `reindex --check` / `reindex --write` (SPEC `REQ-OKF-011`), with a three-way verdict — `clean` (exit 0) / `drift` (exit 1) / `no-index` (exit 2) — so a bundle with no root `index.md` can never be counted green.
- The drift model: `ghost` (an entry whose relative target does not resolve — dead files *and* dead directories), `missing`, `empty-dir`; surfaced in `okf check` at **warning** level under `REQ-OKF-CHK-002`.
- The root backfill: 19 root indexes regenerated, **36 ghost entries removed**, 16 members added, with prose preservation (`REQ-OKF-072`) and a human consent gate on the aggregate diff.
- The two extension decisions, recorded with their measurements in `spec/OKF-YF-EXTENSIONS.md`.
- Both **producers** fixed (`plan_manager.py` `_INDEX_MEMBERS`, `index_manager.py`), so the corpus is not re-broken after the sweep — generation before enforcement was the ordering constraint this plan was built around.

**OUT (deliberately not built):**
- **Nested `index.md` — deferred (D-9)**, behind a producer change that stamps `description:`. Measured: `description` present on **0 of 423** nested files, so every generated nested entry would carry no description, and **74 of 142 (52%)** of subdirectories would receive a listing of no value. Filed as a follow-on.
- **Nested `log.md` — dropped permanently (D-4).** Measured 1–2 distinct commit dates per subdirectory, and every `okf.append_log` call site targets the bundle **root** — no producer event is scoped below it, so nothing would populate it.
- **Promotion to error-level enforcement — recorded, not executed.** The precondition is met (19/19 clean, 31/31 `no-index`, ML003 clean), but landing it in the same pass would enforce against a corpus whose greenness was established minutes earlier by the same session. The follow-up steps are recorded in `skills/yf-okf/SPEC.md` under `REQ-OKF-CHK-002`.

The `audit-close` half of this issue already shipped in plan-043 (#148).

*Correction to this issue's own framing:* the nested tier was the originally-approved target. exp-003 refuted it by measurement and the plan was retargeted to the root tier, where real drift existed **today** — invisible because `okf.py check` did no link resolution at all until this change.

Plan: `docs/plans/plan-046-james-dixson-aabefa/`. Tracker: #167.
