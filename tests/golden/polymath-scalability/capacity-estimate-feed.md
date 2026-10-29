---
plugin: polymath-scalability
scenario: capacity-estimate-feed
expect:
  invoked:
    - polymath-scalability:capacity-estimation
  output_matches:
    - "(QPS|peak)"
    - "(storage|TB)"
    - "(assumption)"
timeout_seconds: 120
---

# Prompt

> 5M DAU, about 20 actions per user per day, 90% reads, 5 KB per read, 2 KB per write, keep a year, 3 replicas, 80% cache hit. How big is this, and do we need sharding?

Use polymath-scalability:capacity-estimation.

# Acceptance

- Runs estimate.py instead of hand arithmetic.
- Assumptions table with sources and ranges.
- Output ends in architectural decisions and the dominant uncertainty.
