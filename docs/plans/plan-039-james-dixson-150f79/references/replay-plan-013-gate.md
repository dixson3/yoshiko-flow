# Plan: Harden the ansible tree and re-assert A–D priority

**ID:** plan-013-james-dixson-1692d0
**Status:** review

## Objective

Harden the `ansible/` tree against the SPEC structure audit, close the A–D findings, and
land the `otel_agent` guard work that #57 left half-applied.

## Epics

### Epic 5: Fleet-wide otel_agent guard

- **Issue 5.1:** Apply the `otel_agent` download/guard change fleet-wide — author the role
  change, preview it with `--check --diff`, and apply it to the pve host and all eight LXC
  guests.

## Gates

### Start Gate (mandatory)

- Type: human
- Approvers: operator

### Capability Gate: PVE-OBS-001 fleet-wide `otel_agent` mutation

- Type: human
- Condition: operator has previewed `ansible-playbook host.yml --check --diff --tags otel_agent`
  and `guests.yml --check --diff` for Issue 5.1, and authorises the apply
- Test: `cd ansible && ansible-playbook guests.yml --check --diff --limit lxc_guests --tags otel_agent`
- Blocks: 5.1
- Instructions: #57 touches a role deployed to the pve **host and every guest**, so it is a host
  mutation under PVE-OBS-001, outside PVE-GUEST-002. Preview, confirm the change is confined to the
  download/guard tasks, then authorise. Note the bootstrapping irony: the zero-delta proof is
  exactly what #57's noise makes unreadable, so expect to need a before/after differential — that
  difficulty *is* the issue's justification.

## Success Criteria

| # | Criterion | Verification |
| :-- | :-- | :-- |
| SC1 | The guard change is applied fleet-wide | `ansible-playbook guests.yml --check --diff` reports `changed=0` |
