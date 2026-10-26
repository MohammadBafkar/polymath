---
name: plugin-budget
description: Show each Polymath plugin's always-on listing-token cost vs the 400/plugin cap; marketplace checkouts only.
---

# /plugin-budget

Run the marketplace token-budget reporter and surface the table.

## What to do

1. Locate the marketplace root (the directory containing `.claude-plugin/marketplace.json`). If there is none, say this command only works in a Polymath marketplace checkout and stop.
2. Execute `tools/token-report.py budget` from that root.
3. Display the table to the user, including the catalog target it prints (250 × plugin count).
4. If any plugin exceeds 400 tokens, or the total exceeds the printed target, name the longest descriptions in that plugin as the likely culprit. For the authoritative per-component numbers, use `polymath-author:token-budget-report`.

This is a read-only report. It does not modify any files.
