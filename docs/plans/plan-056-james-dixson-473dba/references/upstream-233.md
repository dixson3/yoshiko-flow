---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #233: yf-plan: audit-close's OKF walk has no fixture carve-out, so pinned negative fixtures fail it

- **Number:** 233
- **Title:** yf-plan: audit-close's OKF walk has no fixture carve-out, so pinned negative fixtures fail it
- **URL:** 
- **State:** OPEN
- **Labels:** bug, priority::medium

## Body

Found at **plan-053**'s own close step, by running `audit-close`.

## Measured

```text
Counter({'fail': 26, 'warn': 19})
fail findings NOT in a pinned fixture tree: 1
```

**25 of 26 `fail` findings are pinned-fixture files** under
`docs/plans/<plan>/assets/fixtures/corpus/**` — verbatim frozen copies of real repository files
(`SKILL.md`, `SPEC.md`, `DRIFT-CHECK.md`, `web/content/*.md`), captured at a pre-fix commit so
a control can be driven RED against them:

```text
okf:assets/fixtures/corpus/ctl-214-pre-fix/SPEC.md         REQ-OKF-003: no YAML frontmatter block
okf:assets/fixtures/corpus/ctl-209-pre-fix/.../SKILL.md    REQ-OKF-003: missing or empty `type`
okf:assets/fixtures/corpus/fp-clean/.../SKILL.md           REQ-OKF-030: missing `okf_spec` member key
...
```

Every finding is **true and irrelevant**. A frozen copy of a non-OKF file is not a bundle
artifact, and **adding OKF frontmatter to one would corrupt the fixture** — its entire purpose
is to be byte-faithful to what the tree looked like at that commit.

The same applies to the single remaining `dangling-refs` finding:
`ctl-214-pre-fix/SPEC.md` contains `../` parent traversal **because the real `SPEC.md` does**.

## This class is already solved once, in the same plan

plan-053 Issue 3.6 hit exactly this and carved it out — `skills/*/scripts/fixtures/**` is
excluded from `scripts/check_skill_script_refs.py` because *"it holds corpus fixture documents
carrying arbitrary invocations by design"* (pass-4 C45). `audit-close`'s OKF walk needs the
same carve for `assets/fixtures/**`.

## Severity: noise, not an outage — but scaling noise

`audit-close` is **advisory by contract** (`REQ-PLAN-075`): it exits 0 unconditionally and
never gates `set complete`. Nothing halted.

But it is *loud* noise that will recur for **every plan that pins a negative fixture** — and
pinned negative fixtures are the standard remedy for the SPEC-first ordering inversion, where a
control grading Epic 0's work is green on the live tree from the moment it exists. Precedent is
accumulating: plan-052 Issue 0.3, and plan-053 Issues 1.6a, 1.6c, 5.4 and 6.1. The technique is
becoming common and the false positives will scale with it.

An advisory check whose output is mostly false positives is an advisory check people stop
reading — which is how a real finding gets missed.

## Suggested remedy

Exclude `assets/fixtures/**` from `audit-close`'s OKF conformance walk **and** from its
dangling-ref scan, mirroring the carve `check_skill_script_refs.py` already ships.

## Evidence

`docs/plans/plan-053-james-dixson-4015d3/assets/deferred-defects.md` § D8

Filed by plan-053 at land-the-plane.

