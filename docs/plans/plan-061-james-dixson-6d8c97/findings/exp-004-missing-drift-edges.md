---
type: Finding
okf_spec: OKF-PLAN
description: 'Designs for the missing drift edges from issues 291 and 247, the measurement that install.sh does not exist while 17 READMEs and DRIFT-CHECK.md itself cite it, and a sweep for other artifacts no declared edge covers. The install.sh half lands here, the manifest half in issue 317.'
---
# EXP-004 — Designing the missing #291 and #247 edges, and other uncovered artifacts

## Part A — #291: the escape/stop taxonomy

**Five homes exist, not four.** #291 undercounts by one and mischaracterizes a second.

| # | Home | Vocabulary |
| :-- | :-- | :-- |
| 1 | `yf-plan/spec/portability.md:124` (REQ-PORT-052) | declares `stop_class`, `escape_class`, `adjudication` — free-text, **no enum** |
| 2 | `yf-plan/SKILL.md:1361-1369` (REQ-AGENT-064) + `:2002-2038` | the actual closed set: **five numbered stop classes** |
| 3 | `plan_manager.py:692-696,7027-7028` | `RETROSPECTIVE_FIELDS` + `--stop-class`/`--escape-class` — **plain `default=""` strings, NOT `click.Choice`**, so nothing enforces the domain at write time |
| 4 | `yf-herdr/SPEC.md:185-196` | a **different, unnumbered** prose deviation taxonomy |
| 5 | `plan_manager.py:802-808` (`ESCALATION_FIELDS`) + `portability.md:134-138` | plan-059's new home — a `state` lifecycle vocabulary |

**#291's claim about home 3 is REFUTED.** `retrospective_fields.py` validates only
`prevention_formula` against `bd formula list`; it contains **zero** references to `escape_class`
or `stop_class`. It is *not* "the executable domain check over those fields" — **no such check
exists anywhere in the repo.**

**The homes already disagree — so this edge is a bug report, not a preventative.** Measured
across the corpus:

- `stop_class` values are cleanly `{1..5}` — consistent, but **unenforced**.
- `escape_class` is **free prose**: 20+ unique values, no two identical
  (`reasoned-past-a-documented-fact`, `stale-figure`, `vacuous-check / green-on-broken`, …).

So "the taxonomy" is **two different objects wearing one name**: a genuinely closed enum
(`stop_class`) and an open narrative tag (`escape_class`). That distinction should drive the
design, and it is why one edge cannot cover both.

**The demonstrated collision:** `plan-045/plan-retrospective.md:66` records
`escape_class: reasoned-past-a-documented-fact`; `yf-herdr/SPEC.md:191` independently names the
same concept `"Premise refuted at execution"`. plan-059 found this **by hand, after the fact**.

**Design — split by mechanizability:**

- **`e-stop-class-domain` — MECHANICAL.** `field-set-subset`: every `stop_class` literal in
  `plan_manager.py`, escalation payloads, and every `plan-retrospective.md` is a subset of
  `{1,2,3,4,5}`, with `SKILL.md` as source of truth. Routes to the checker.
- **`e-escape-taxonomy-overlap` — PROSE.** Semantic paraphrase detection; no script can decide
  that "Premise refuted at execution" ≡ "reasoned-past-a-documented-fact". Routes to LLM
  dispatch. Needs the node split into `deviation-taxonomy-herdr` → `retrospective-escape-corpus`
  if the schema disallows self-edges.

REQ-DATA-076's severity vocabulary is confirmed **distinct** and out of scope for both.

## Part B — #247: the manifest's own diagram

**Re-derived today — the gap has GROWN since #247 was filed:**

| | #247 as filed | Today |
| :-- | --: | --: |
| `DRIFT-CHECK.md` §2 edges | 52 | **52** |
| `.d2` edges | 30 | **27** |
| Missing from diagram | 22 | **25** |
| Extra in diagram | — | 0 |

Five edges were added to the manifest since #247; none to the diagram. **Confirmed:**
`drift-check-artifact-graph.d2:69` still draws `skillmd -> agent: e-status-values`, the pre-#208
edge plan-053 D-6 replaced with `status-restatement` — the diagram never introduces a
`status-restatement` node at all.

**Why a freshness edge cannot catch this — the general principle, which generalizes to (c):**

> A freshness edge proves only **internal** consistency between a source artifact and its own
> derived rendering. It structurally cannot detect that the *source* has drifted from a **third**
> artifact it claims to represent.

`e-docs-diagram-fresh` PASSES because the PNG really is a faithful render of the stale `.d2`.
This is the **same shape** as `skill-page`'s `optional` reachability (#263): *a check whose only
failure mode is that the thing which would have caught it never ran* reports clean **by
construction, not by verification**.

**Design — MECHANICAL, and prototyped working against the live repo:**

```python
md_edges = set(re.findall(r"^\|\s*`(e-[a-z0-9-]+)`", section_2, re.M))
d2_edges = set(re.findall(r":\s*(e-[a-z0-9-]+)\s*\{", d2_text))
verdict = "PASS" if md_edges == d2_edges else "FAIL"
```

New node `drift-manifest` (source) → `e-drift-manifest-diagram-sync` (`field-set-equal`) →
`docs-diagram-src`. Endpoint agreement (e.g. `e-status-values`'s source/target pair) is a
stronger, still-mechanical follow-on once the id-set check ships. Routes to the checker.

## Part C — `install.sh` / `install.py` do not exist

**Confirmed absent** at repo root. `README.md:39` documents a **hosted vendor** installer at
`yoshikoflow.sh/install.sh` — a genuinely different artifact. `yf/src/parity.rs:2,5` explicitly
calls `install.py` "retired" (deleted at plan-010).

Yet **17 skill READMEs** still reference "the repo-level `install.sh`/`install.py`" — **and so
does `DRIFT-CHECK.md` itself, twice** (`:219`, `:225`, §5 Required-Section Contracts), naming
"repo-level `install.sh` reference" and "`install.sh` actual flags" as the required source.

**The manifest names a nonexistent authority for its own required-section check** — precisely the
error class its §7 conflict policy exists to catch, committed in itself. `e-install-url` does not
help: it checks byte-identity of a URL duplicated between SKILL.md and README, **not that the
mechanism named is real.**

The real path today is `yf self install --from-build --build` or `yf skills install`.

## Part C — other artifacts no edge covers

1. **`spec` → `script`**: nothing connects `spec/portability.md`'s REQ-PORT-052/053/054 field
   lists to `plan_manager.py`'s `RETROSPECTIVE_FIELDS`/`ESCALATION_FIELDS` tuples. Only
   `spec → skill-md` (prose) exists, so a field added to one and not the other is invisible.
2. **Per-skill `OKF-EXTENSION.md`** (3 exist) carry **no node at all** in §1.
3. **`e-formula-name` asserts its own unchecked agreement** (`:147`: "same extraction contract as
   `yf doctor`'s `FormulaCheck`"). Nothing checks the Rust implementation against the Python
   extraction it claims to mirror — **the same announced-but-unbuilt shape as #291 and #247**, in
   the manifest's own prose.

## Implications for the plan

- Both requested edges are designable; both land per the operator's FULL-scope election.
- The #247 edge and `e-stop-class-domain` route to the **mechanical checker**;
  `e-escape-taxonomy-overlap` routes to **LLM dispatch**. Do not force them into one.
- **`DRIFT-CHECK.md:219,225` needs fixing independently of any new edge** — 17 READMEs plus the
  manifest itself cite a file that does not exist.
