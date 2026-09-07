`scripts/checks/check_web_counts.py` verifies a group's **count** always, but its **membership**
only when the group's label or bullet actually enumerates member ids. Where none are enumerated it
emits:

```
NOT-CHECKED web/content/images/architecture.d2:22: group `markdown` enumerates no member ids
            (count checked, MEMBERSHIP NOT CHECKED)
```

This is a **declared limit, not a defect** — `REQ-CHECK-009` (added by plan-066) requires a
mechanical gate to state what it does not cover, and this is that statement working as intended.
It is filed so a future reader does not mistake the silence for a pass.

### The reason it matters

Count and membership are two facts. plan-066 measured `architecture.d2`'s `beads group` carrying
the count **8** while listing the three *workflows* skills — right shape, wrong contents. Wherever
a bullet enumerates no ids, that failure mode is currently invisible.

### Options

- Rewrite the remaining non-enumerating bullets to list backticked ids, as plan-066 did for
  `architecture.md`'s `utility` and `markdown` bullets — after which the check covers them
  automatically; or
- accept the limit permanently and keep it declared.

Filed from plan-066 under D5.
