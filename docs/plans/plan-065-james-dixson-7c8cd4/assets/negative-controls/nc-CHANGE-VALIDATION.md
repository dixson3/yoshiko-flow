# NC CHANGE-VALIDATION.md

> Prose mentioning `uv run scripts/checks/plan065_checks.py audit-strict` — a substring
> grep would match this line and report the script registered.

## 0. Status

approved: yes

## 1. Tiers

### fast

| id | cmd | cwd | timeout |
|:--|:--|:--|--:|
| `plan065-audit` | `uv run scripts/checks/plan065_checks.py audit-strict` |  |  |

### full

| id | cmd | cwd | timeout |
|:--|:--|:--|--:|
| `cargo` | `cargo test --workspace` |  |  |

## 2. Signal Fingerprint

## 3. Trigger Scope
