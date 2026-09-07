## Fixed in plan-066 — at BOTH sites

The figure now **names its corpus**, which is the whole defect: a ratio measured in one repository
was being read as a property of the tool.

**`skills/yf-okf-hygiene/SKILL.md`** leads with the point and then gives a table with one row per
corpus:

| Corpus | Legacy bundles | Halt on objective divergence | Rate |
| :-- | --: | --: | :-- |
| `dixson3/yoshiko-flow`, historical (plan-029 era) | 31 | 7 | 7/31 |
| `dixson3/yoshiko-flow`, current (plan-064 EXP-001) | 8 | 7 | **7/8** |

with an explicit instruction to **run `audit` against your own corpus and size from that**, and
the measured consequence recorded — a real plan mis-sized **3.5x**.

**`okf_hygiene.py`'s `_objective` docstring** carried the same 31/7 against the same corpus and
was compounding it. It now names the corpus too, and repeats the do-not-size-from-this warning.

Worth keeping as the general shape: the historical rate is not the current one because the easy
bundles were transformed long ago and what remains is precisely the residue the guard fires on —
so the rate rose from 7/31 to 7/8 while the **count** of halts never moved.
