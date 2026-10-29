---
plugin: polymath-streaming
scenario: lakehouse-merge-small-files
expect:
  invoked:
    - polymath-streaming:lakehouse-performance
  output_matches:
    - "(small files|OPTIMIZE|compaction)"
    - "(cluster|partition)"
    - "(skew|MERGE.{0,40}(condition|prune))"
timeout_seconds: 120
---

# Prompt

> Our nightly Databricks MERGE into silver.orders went from 55 minutes to over 3 hours. DESCRIBE DETAIL shows 380k files averaging 9 MB, partitioned by order_id, and one task runs 7 minutes while the median is 2 seconds.

Use polymath-streaming:lakehouse-performance.

# Acceptance

- Fixes layout before cluster size.
- MERGE gets a pruning predicate; skewed key handled.
- Verification by files scanned and task skew ratio.
