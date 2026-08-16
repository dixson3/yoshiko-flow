# Plan: Harden the ansible tree and re-assert A–D priority

**ID:** plan-013-james-dixson-1692d0
**Status:** review

## Objective

Harden the `ansible/` tree against the SPEC structure audit, close the A–D findings, and
re-prioritise what remains.

## Epics

### Epic 1: Role structure conformance

- **Issue 1.1:** Bring every role's `defaults/` and `vars/` into SPEC-conformant shape.
- **Issue 1.4:** Sweep the remaining non-conformant task files.
  - depends-on: 1.1

### Epic 2: Inventory and group_vars hardening

- **Issue 2.1:** Normalise `group_vars/` layout.
- **Issue 2.3:** Remove the duplicated host definitions.
  - depends-on: 2.1

### Epic 3: Playbook tagging

- **Issue 3.4:** Apply the standard tag set to every play.

### Epic 4: Secrets handling

- **Issue 4.2:** Move the remaining plaintext values into vault.

### Epic 5: Fleet-wide otel_agent guard

- **Issue 5.4:** Land the guard change and record the result.

### Epic 6: Re-audit and re-assert A–D priority

- **Issue 6.1:** Re-run the full `ansible/`-vs-SPEC structure audit against the hardened tree,
  using the new gates' actual output as evidence rather than reading by eye.
- **Issue 6.2:** Write `Incubator/ansible/audit-2026-08-A-D-reassessment.md` — the A–D verdict
  against the re-audited tree, with each finding's cost re-estimated.
  - depends-on: 6.1
- **Issue 6.3:** File or update the upstream issues for whatever A–D work survives
  re-prioritisation.
  - depends-on: 6.2

## Gates

### Start Gate (mandatory)

- Type: human
- Approvers: operator

## Success Criteria

| # | Criterion | Verification |
| :-- | :-- | :-- |
| SC1 | The re-audit reports a clean structure verdict | `audit-2026-08-A-D-reassessment.md` records an A–D verdict against the hardened tree |
