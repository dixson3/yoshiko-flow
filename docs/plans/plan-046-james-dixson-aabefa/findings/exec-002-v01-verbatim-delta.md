---
type: Finding
okf_spec: OKF-PLAN
id: exec-002-v01-verbatim-delta
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
---

# exec-002 — The v0.1↔v0.2 delta, measured against BOTH verbatim specs (plan-046 Issue 2.1)

**Why this exists.** Risk R1: v0.1's §1/§2/§6/§7 bodies were never quoted in-repo, so further
undeclared v0.2 changes could not be ruled out — and one *was* already found inside the verified
subset, which is evidence §13 is not exhaustive. Issue 2.1 fetched v0.1 verbatim; this file is the
diff that closes R1.

**No fallback was needed.** v0.1 is fully recoverable: `okf/SPEC.md` @ `ee67a5ca` (2026-06-12), the
last revision before `780fe9d3` (2026-07-24) migrated it to v0.2. Vendored at
[`references/okf-spec-v0.1.md`](../references/okf-spec-v0.1.md), 451 upstream lines,
`**Version 0.1 — Draft**`.

> **Date note.** The plan states upstream shipped v0.2 on 2026-08-15. The upstream *commit* that
> migrated the path is dated **2026-07-24**. Recorded, not reconciled — it changes no conclusion.

## 1. The section map — MEASURED, not inferred (feeds Issue 2.3, checked by SC4)

| v0.1 | v0.2 | note |
| :-- | :-- | :-- |
| §1 Motivation | §1 Motivation | body differs (prose) |
| §2 Terminology | §2 Terminology | body differs |
| §3 Bundle Structure | §3 Bundle structure | body differs |
| §4 Concept Documents | §4 Concept documents | body differs |
| §5 Cross-linking | **§6** Cross-linking and paths | renumbered |
| §6 Index Files | **§8** Index files | renumbered |
| §7 Log Files (optional) | **§9** Log files | renumbered; "(optional)" dropped from the title |
| §8 Citations | **— removed** | declared breaking change B-2 |
| §9 Conformance | **§11** Conformance | renumbered |
| §10 Relationship to other formats | **— removed** | **UNDECLARED** (see §2 below) |
| §11 Versioning | **§12** Versioning | renumbered |
| — | §5 Provenance, trust, and lifecycle | new (declared additive) |
| — | §7 Actor convention | new (declared additive) |
| — | §10 Attested computations concept | new (declared additive) |
| — | §13 Changes from v0.1 | new (the changelog itself) |

**Correction to exp-002.** exp-002's map recorded *"versioning §5→§12"*. Measured: versioning is
v0.1 **§11** → v0.2 §12; v0.1 **§5** is *Cross-linking* → v0.2 §6. The `index §6→§8`,
`log §7→§9` and `conformance §9→§11` entries in exp-002 are correct as written.

## 2. §13's omissions — THREE, not two

§13.2 closes with: *"Everything else (bundle structure, reserved filenames, the required `type`,
recommended `title`/`description`/`resource`/`tags`, cross-linking, index files, log files,
permissive conformance) is carried forward unchanged."*

1. **`SHOULD NOT` → `MUST NOT` on the extension clause** (exp-002's B-3). Now confirmed against
   upstream v0.1 itself rather than three in-repo copies:
   - v0.1 `okf/SPEC.md:161-162` — *"SHOULD preserve unknown keys when round-tripping and **SHOULD
     NOT** reject documents with unrecognized fields."*
   - v0.2 `okf/SPEC.md:219-220` — *"SHOULD preserve unknown keys when round-tripping and **MUST
     NOT** reject documents with unrecognized fields."*
2. **The renumbering is not flagged anywhere in §13.** Seven sections moved; every `(§N)` citation
   in a v0.1-derived document is now a wrong pointer, silently — v0.2 uses identical `(§N)` syntax,
   so no grep can distinguish a surviving v0.1 reference from a correct v0.2 one. This is why SC4 is
   checked row-by-row against the table above rather than by grep.
3. **v0.1 §10 "Relationship to other formats" was removed entirely** — a whole section, undeclared,
   while §13 asserts everything else carried forward unchanged. *(New in this finding; exp-002 did
   not have v0.1's §10 body to observe its absence.)*

### A fourth nuance — conformance gained CONDITIONAL MUSTs

exp-002's *"single most important non-change"* **holds**: v0.1 §9's three numbered MUSTs are
byte-identical in v0.2 §11 apart from the `§6`/`§7` → `§8`/`§9` cross-references, and the permissive
"MUST NOT reject a bundle because of" list is byte-identical.

But v0.2 §11 **adds** a paragraph absent from v0.1 §9, carrying two new MUSTs gated on the new
families being present (*"MUST treat a bare `verified` mapping as a one-element list"*; *"MUST NOT
reject a concept for missing any optional family"*). **These do not bind yf** — it emits none of the
trust/lifecycle/provenance/computation families — and they are arguably covered by §13.2's blanket
"new optional keys". Recorded as a nuance rather than a fourth omission, because the reading is
genuinely arguable and this plan's standard is to record rather than silently resolve.

v0.1 §9 also **lost** a closing rationale sentence (*"This permissive consumption model is
intentional…"*). Prose only; no normative force.

## 3. A pre-existing citation error, distinct from the renumbering

`OKF-BASELINE.md` cites `(§5)` for the `okf_version` key at **L96** and **L166**. Measured: v0.1
mentions `okf_version` exactly once, at `okf/SPEC.md:393`, which falls inside **§11 Versioning**
(§11 starts at line 382) — *not* §5 (Cross-linking, line 233).

**So those two citations were already wrong against v0.1.** They are not renumbering casualties, and
Issue 2.3 must not "correct" them as if they were: the v0.2-correct target is **§12 Versioning**,
reached by fixing an error, not by applying the map. Recorded because silently rewriting `(§5)` to
`(§6)` via the map would have produced a *confidently wrong* citation in a fixed-authority document.
