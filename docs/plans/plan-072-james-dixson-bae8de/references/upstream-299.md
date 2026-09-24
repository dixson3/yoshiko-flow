---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #299 - yf harness: consolidate DESCRIPTORS + RULE_TARGETS
  into one table with an explicit rules-surface column'
---
# Upstream #299: yf harness: consolidate DESCRIPTORS + RULE_TARGETS into one table with an explicit rules-surface column

- **Number:** 299
- **Title:** yf harness: consolidate DESCRIPTORS + RULE_TARGETS into one table with an explicit rules-surface column
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::medium

## Body

## The per-harness surface description is split across two tables that must agree and are not checked

Both from plan-044; grouped because the second is the **structural cause** of the first.

### 1. `skills remove` prunes the skills-sibling `rules/` dir — `yf-pzsv`

plan-044 D-10 **residual**, recorded honestly rather than claimed fixed. Issue 2.1 made `skills upgrade` rules-neutral (`REQ-YF-FLOW-008`) but deliberately **kept** `skills remove`'s rules write per `REQ-YF-FLOW-002`. The consequence is that its section-drop is effective on **claude-code only** — the other harnesses do not get the same treatment.

### 2. Two tables independently describe per-harness surfaces — `yf-va8x`

plan-044 D-12 follow-on (exp-001 rec 5), and named there as the **structural cause of both #156 and the `agents` rules gap**:

- `harness_desc::DESCRIPTORS` — skills subpaths + name translation
- `managed_block::RULE_TARGETS` — rules-surface destinations

Nothing asserts the two agree, and nothing declares which harnesses have a rules surface at all. Consolidating them into one table with an **explicit rules-surface column** removes the class rather than the instance.

## Why grouped

(1) is a per-harness inconsistency; (2) is why per-harness inconsistencies are the default. Fixing (2) makes (1) a one-line change and prevents the next one. Working (1) alone would patch a symptom of a table split that will keep producing them.

Both are Rust-side (`yf/`), so they are outside the reach of every Python instrument this repo has built for the same class of defect.

Local beads: `yf-pzsv`, `yf-va8x`.

