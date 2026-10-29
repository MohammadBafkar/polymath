---
plugin: polymath-database
skill: index-strategy
trigger_prompts:
  - "which indexes should I add to the orders table for this query workload"
  - "we have too many indexes and writes are slow — which can we drop"
  - "composite index column order for WHERE customer_id = ? ORDER BY created_at DESC"
must_invoke:
  - polymath-database:index-strategy
allow_invoke:
  - polymath-data:sql-optimize
  - polymath-backend:migration-plan
  - polymath-core:*
---

# Why this test exists

Confirms the description routes these natural phrasings to `polymath-database:index-strategy` rather than to its sibling skills.
