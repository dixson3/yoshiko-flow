# Plan: Harden the ansible tree and re-assert A–D priority

**ID:** plan-013-james-dixson-1692d0
**Status:** review

## Objective

Harden the `ansible/` tree against the SPEC structure audit and prove the hardening changed
no live host or guest state.

## Epics

### Epic 1: Role structure conformance

- **Issue 1.1:** Bring every role's `defaults/` and `vars/` into SPEC-conformant shape.
- **Issue 1.4:** Sweep the remaining non-conformant task files.
  - depends-on: 1.1

### Epic 5: Fleet-wide otel_agent guard

- **Issue 5.4:** Land the `otel_agent` guard change in the role source.
  - depends-on: 1.4

## Gates

### Start Gate (mandatory)

- Type: human
- Approvers: operator

## Success Criteria

| # | Criterion | Verification |
| :-- | :-- | :-- |
| SC1 | Every role is SPEC-conformant | the structure audit reports no findings |
| SC7 | The hardening is a no-op against the live fleet | `ansible-playbook host.yml --check --diff` and `guests.yml --check --diff` are byte-identical to pre-change for all 8 guests + host |
| SC14 | No live host or guest state changed | a converge preview reports `changed=0` across the fleet |
