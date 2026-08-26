---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #226: plan_extract: a trailing declaration behind a LEADING code span yields no edge

- **Number:** 226
- **Title:** plan_extract: a trailing declaration behind a LEADING code span yields no edge
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

Measured by plan-053 (EXP-001), re-verified on the merged tree.

## The defect

A **real** trailing declaration sitting behind a leading inline code span produces no edge:

```text
- Issue 1.2: second
  `foo.py` depends-on: 1.1

  ->  depends_on = []      edges = []
```

Unchanged on both the base and the fixed tree.

## Mechanism

The two-space continuation branch tests the **masked** line. The leading mask replaces the code
span with spaces, pushing the first non-space character past column 2, so
`^ {2}(?![ \t*-])\S` no longer matches and the line never reaches `try_trailing`.

## Why it is out of scope for plan-053

Note carefully which side this is on. plan-053's Issue 2.1 changed the **capture** gate to read
the unmasked line and left every **parsing** branch reading the masked one — and that
separation is not an accident, it is `REQ-DATA-063`'s stated requirement, which exists so that
a `depends-on:` written inside a code span still produces no edge.

Fixing this defect means changing a **parsing** branch, which is exactly the class of change
that can start manufacturing phantom edges. It needs its own RED fixture and its own measured
corpus delta before it is safe to land.

## Evidence

- `docs/plans/plan-053-james-dixson-4015d3/findings/exp-001-extractor-drop-fix.md`
- `docs/plans/plan-053-james-dixson-4015d3/assets/deferred-defects.md` § D2

Filed by plan-053 Issue 7.2.

