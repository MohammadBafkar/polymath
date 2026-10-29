---
plugin: polymath-scalability
skill: capacity-estimation
trigger_prompts:
  - "back-of-envelope: 5M daily users, how many QPS and how much storage"
  - "estimate peak QPS, bandwidth and storage for 100M events a day with 3x replication"
must_invoke:
  - polymath-scalability:capacity-estimation
allow_invoke:
  - polymath-sre:capacity-plan
  - polymath-scalability:system-design
  - polymath-core:*
---

# Why this test exists

Confirms the description routes these natural phrasings to `polymath-scalability:capacity-estimation` rather than to its sibling skills.
