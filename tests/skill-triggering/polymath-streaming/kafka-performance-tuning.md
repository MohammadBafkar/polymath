---
plugin: polymath-streaming
skill: kafka-performance-tuning
trigger_prompts:
  - "our kafka consumer group lag keeps growing, how do we tune it"
  - "tune kafka producer batching and compression for higher throughput"
must_invoke:
  - polymath-streaming:kafka-performance-tuning
allow_invoke:
  - polymath-streaming:streaming-design
  - polymath-core:*
---

# Why this test exists

Confirms the description routes these natural phrasings to `polymath-streaming:kafka-performance-tuning` rather than to its sibling skills.
