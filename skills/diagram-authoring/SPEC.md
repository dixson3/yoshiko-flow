# SPEC — Diagram Authoring (`yf-diagram-authoring`)

> **Status: DRAFT (primed).** Per-skill SPEC for the diagram skill (currently `diagram-authoring`,
> renamed to `yf-diagram-authoring` by plan-010 Issue 3.7 / `REQ-YF-RENAME-001`). Operator to
> review/edit. Composed by the root macro `SPEC.md` §4 under spec key **DIAG**.

## 1. Purpose & scope

`yf-diagram-authoring` authors diagrams as **d2** source and renders light-mode, white-background
PNGs from it, keeping the `.d2` source beside every `.png` render (never temp-and-discard). It
standardizes d2 — **not mermaid** — as the single, local, offline diagram engine, with a fixed
render contract (theme 0 light, elk layout) and a write → render → verify-by-Read workflow.

**In scope:** the d2 render wrapper (`preflight`, `render`, `render-dir`, `check-dir`), the
source-beside-render invariant, and the regeneration/orphan discipline.

**Out of scope:** non-diagram image work; mermaid-specific workflows; choosing where output goes
— the skill is **location-agnostic**, and consumers (e.g. `yf-plan`, `yf-research`,
`yf-skill-authoring`) supply their own convention (`plan_dir/diagrams`, `research_dir/diagrams`,
skill `spec/` co-resident, `docs/diagrams`).

## 2. Requirements (`REQ-DIAG-NNN`)

### 2.1 Engine & render contract

- **REQ-DIAG-001** *(testable)* the skill shall use **d2** as its only diagram engine; mermaid is
  out of scope and shall not be a render target.
- **REQ-DIAG-002** *(testable)* `render` shall invoke `d2 --theme <T> --layout <L> <src.d2>
  <src.png>`, defaulting `--theme 0` (light, white opaque background) and `--layout elk` (dagre
  selectable).
- **REQ-DIAG-003** *(testable)* `render` shall emit the PNG to a **sibling** path — `src` with its
  suffix changed to `.png` — so the `.d2` source always sits beside the render.
- **REQ-DIAG-004** *(testable)* `render` shall reject a non-`.d2` or non-existent input (exit 2)
  and report failure (exit 1) when d2 returns non-zero or the expected PNG is absent.

### 2.2 Preflight

- **REQ-DIAG-010** *(testable)* `preflight` shall be an OS-independent presence check — `command
  -v d2` (`shutil.which`) only — reporting `ok`/`missing`, the path, and `d2 --version`; it shall
  **not** probe the Chromium/playwright PNG cache (those paths are OS-specific; probing risks a
  false negative).
- **REQ-DIAG-011** *(testable)* `preflight` shall exit 0 when d2 is present and 1 when missing,
  with install guidance (`brew install d2`) in the missing case.

### 2.3 Regeneration & verification discipline

- **REQ-DIAG-020** *(testable)* `render-dir <dir>` shall (re)render every `.d2` under `<dir>`
  (recursive) to its sibling PNG and exit non-zero if any render fails.
- **REQ-DIAG-021** *(testable)* `check-dir <dir>` shall be **authoritative** on orphans — exit 1
  when any `.d2` has no matching `.png` — and **advisory only** on staleness (WARN when a `.d2` is
  newer than its `.png` in the same working tree, never failing on it, because git checkout
  normalizes mtimes so a fresh clone cannot distinguish stale from current).
- **REQ-DIAG-022** the operator/consumer shall **verify a render by reading the PNG** (white
  background, legible labels, correct structure) and fix the `.d2` and re-render on any problem —
  never hand-edit the `.png`.

### 2.4 Invocation & output

- **REQ-DIAG-030** *(testable)* every subcommand (`preflight`, `render`, `render-dir`,
  `check-dir`) shall accept `--json` for machine-readable output; `render`/`render-dir` shall
  accept `--theme` and `--layout`.
- **REQ-DIAG-031** output **location** shall be caller-supplied; the skill shall hardcode no
  destination directory (it renders beside the given `.d2`, wherever that is).

## 3. Interfaces

- **CLI / scripts:** `scripts/render.py` (run via `uv run`) — subcommands `preflight`, `render
  <file.d2>`, `render-dir <dir>`, `check-dir <dir>`; flags `--theme` (default `0`), `--layout`
  (default `elk`), `--json`. **External tool:** the script shells to **d2** (`depends-on-tool:
  [d2]`). This is a skill that shells to an external renderer, consistent with macro GUARDRAILS
  GR-004 (rendering lives in the skill, not in `yf`) and GR-011 (`yf` shells to `d2`, never vendors
  it).
- **Companion rule:** none — `user-invocable: true`, no always-loaded trigger rule.
- **Config / state:** none — no `.<skill>.local.json`, no `.yf/<skill>/` state; output paths are
  supplied per call.

## 4. Guardrails (`GR-DIAG-NNN`)

- **GR-DIAG-001** *Drift:* adopting mermaid or a second diagram engine. *Rule:* d2 is the single,
  local, offline engine; no mermaid render path. *Why:* one engine — cleaner syntax, stronger
  auto-layout, offline.
- **GR-DIAG-002** *Drift:* temp-and-discard renders, or hand-editing a `.png`. *Rule:* the `.d2`
  source always lives beside its `.png`; renders are regenerated from source, never edited.
  *Why:* the render must stay reproducible and reviewable from source.
- **GR-DIAG-003** *Drift:* hardcoding an output location or a "diagrams" convention. *Rule:* the
  skill is location-agnostic; consumers own placement. *Why:* it serves many consumers with
  different layout conventions.
- **GR-DIAG-004** *Drift:* probing OS-specific render caches in `preflight`. *Rule:* preflight
  checks only `command -v d2`. *Why:* cache-path probes are OS-specific and produce false
  negatives.

## 5. Verification

- `preflight` exit-code/status (REQ-DIAG-010/011) and `render` input validation + sibling-PNG
  emission (REQ-DIAG-003/004) are checkable with fixtures: a valid `.d2` renders to a sibling
  `.png` (exit 0); a non-`.d2` input exits 2.
- `check-dir` orphan-vs-advisory semantics (REQ-DIAG-021): a `.d2` with no `.png` yields exit 1
  with an `ORPHAN` line; a `.d2` newer than an existing `.png` yields a WARN line and exit 0.
- `--json` shape (REQ-DIAG-030) asserted per subcommand. Forward coverage per plan-010 Epic 6
  (tests naming the REQ id).

## 6. References

- `skills/diagram-authoring/SKILL.md` (workflow, output-location table, d2 authoring notes).
- `skills/diagram-authoring/scripts/render.py` (the render wrapper).
- Root `SPEC.md` §4 (DIAG) and `GUARDRAILS.md` (GR-004, GR-011).
