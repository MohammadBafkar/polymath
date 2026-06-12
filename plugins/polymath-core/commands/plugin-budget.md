---
name: plugin-budget
description: Report current Polymath always-on listing token cost per plugin and totals; flags overruns vs the ≤ 400/plugin and ≤ 1,500 MVP targets.
---

# /plugin-budget

Run the marketplace token-budget reporter and surface the table.

## What to do

1. Locate the marketplace root (the directory containing `.claude-plugin/marketplace.json`).
2. Execute `tools/token-report.py budget` from that root.
3. Display the table to the user.
4. If any plugin exceeds 400 tokens, or the total exceeds 1,500, recommend the most likely culprit (long descriptions, too many components).

This is a read-only report. It does not modify any files.
