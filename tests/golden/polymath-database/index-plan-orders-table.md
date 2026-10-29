---
plugin: polymath-database
scenario: index-plan-orders-table
expect:
  invoked:
    - polymath-database:index-strategy
  output_matches:
    - "(customer_id, created_at|composite)"
    - "(partial|WHERE status)"
    - "(drop|unused|duplicate)"
timeout_seconds: 120
---

# Prompt

> The orders table has 214M rows and 9 indexes. Our hot query is WHERE customer_id = ? ORDER BY created_at DESC LIMIT 20, plus a sweeper on status='pending'. Propose the index set and tell me what to drop.

Use polymath-database:index-strategy.

# Acceptance

- Composite index with equality column first then the sort column.
- Partial index for the pending sweeper.
- Drop candidates with the stats-window caveat.
- Write-cost and rollout (CONCURRENTLY) noted.
