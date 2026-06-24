# exp-001: yf-beads-upstream & yf-beads-hygiene current architecture

## yf-beads-upstream

- **`scripts/upstream.py` is a read-only helper** — it does NOT push. Verbs:
  - `enumerate [--json]` — `bd list --status open,blocked,deferred --json`, drops
    `epic`/`molecule`/`gate`, resolves each bead's `External:` mapping. `CANDIDATE_STATUSES = "open,blocked,deferred"`.
  - `mappings --issues <csv> [--json]` — per-bead `External:` URL or null.
- **Push is operator/SKILL-driven:** `bd github push <ids>` (≡ `bd github sync --push-only --issues <ids>`); subtree variant `--parent <id>`. Mandatory `--dry-run` first (REQ-BUP-013/REQ-SAFE-001). Inline auth `GITHUB_TOKEN=$(gh auth token) bd github push …` — never `bd config set *.token`. Never a bare `bd <backend> sync` (REQ-BUP-030).
- **Linkage format** (bd-managed, surfaced in `bd show` text, parsed by `EXTERNAL_RE = ^\s*External:\s*(https?://\S+)`):
  `External: https://github.com/<owner>/<repo>/issues/<N>`. This mapping suppresses duplicate creation on re-push. Only the bead `description` syncs to the issue body — `notes`/`design` do NOT sync.
- **Config keys:** `custom.upstream.enabled` (literal `"true"` enables; default-deny otherwise), `custom.upstream.backend` (`github|gitlab|jira|none`), `github.owner`, `github.repo`. **No granularity key implemented** — REQ-BUP-043 specifies `coarse|granular` but it is unimplemented; clean extension point.
- **Close-time/land-the-plane trigger** lives in the always-loaded companion rule `protocols/UPSTREAM_TRACKING.md` (NOT the description; REQ-BUP-042). Procedure lives in SKILL.md.
- **SPEC IDs:** `REQ-BUP-*` (043 = unimplemented granularity), `REQ-OP-*`, `REQ-SAFE-*`, `REQ-BE-*`, `GR-BUP-*`. Manifest bump: `uv run scripts/manifest_update.py protocols [--minor|--major]` after editing the rule; commit rule + manifest.json together.
- **No test file for upstream.py** (unlike hygiene) — adding `test_upstream.py` means factoring pure parts (`parse_json_array`, `external_for`, candidate filter) with the resolver-injection pattern hygiene uses.

## yf-beads-hygiene

- **`scripts/beads_hygiene.py` verbs:** `audit [--json]`, `repair [--apply] [--yes] [--record <file>]`, `restore --record <file> [--apply]`. Dispatch via `set_defaults(func=...)`.
- **Audit data-flow (live layer vs pure core):**
  1. `db_is_wedged()` — preflight; honors false-negative invariant; wedged → `_route_to_init()` exits 2 (REQ-HYG-010).
  2. `load_universe()` — `bd list --all --json` **plus** `bd list --all --type gate --json` (gates hidden + 50-row truncation). REQ-HYG-003.
  3. `collect_edges(universe, resolver=show)` — per-bead `bd show --json` `dependencies[]` → `Edge(blocked, blocker, dep_type, target)`; target resolved via universe then `bd show` (never `bd list` membership). `resolver` injected for tests.
  4. Pure core: `Edge.classify()` → `TRUE_ORPHAN|TRULY_DANGLING|SATISFIED_GATE|LIVE_GATE|healthy`. #29 invariant: open gate = LIVE_GATE (never dangling). `classify_edges()` → `AuditReport` (`findings`, `.removable`).
- **Repair gating:** dry-run without `--apply`; interactive `_confirm()` unless `--yes`; mutates via `bd dep remove`; `--record` writes round-trip JSON; post-mutation `bd dep cycles` + prints land-the-plane sequence (`bd dolt commit && bd dolt push && git push`). `restore` re-adds via `bd dep add`.
- **SPEC IDs:** `REQ-HYG-001..010`, `GR-HYG-001..004`.
- **Tests** (`test_beads_hygiene.py`): pytest, `importlib` loads PEP-723 script, pure/fixture-driven (`gate()`, `task()` helpers, injected `resolver` lambdas), grouped under `# --- section ---` comments naming the REQ. No live bd. Match this style for new coverage.
