---
plugin: polymath-streaming
scenario: kafka-order-events-topology
expect:
  invoked:
    - polymath-streaming:streaming-design
  output_matches:
    - "(partition key|partitioning)"
    - "(at-least-once|exactly-once|delivery semantic)"
    - "(consumer group|offset)"
  not_invoked:
    - polymath-data:sql-write
timeout_seconds: 120
---

# Prompt

> We're putting order events on Kafka. Multiple services consume them.
> Per-order ordering must hold, volume is ~50k events/sec, and we
> can't lose events. Help me design the topic, partitioning, and
> consumer setup.

Use polymath-streaming:streaming-design.

# Acceptance

- Partition key chosen to preserve per-order ordering while spreading load (order id), with a note that ordering is per-partition only.
- Delivery semantics stated; "can't lose events" → at-least-once with idempotent consumers (or exactly-once with the trade-off named).
- Consumer groups + offset-commit-after-processing covered.
- Retention/replay and a dead-letter / poison-message policy included.
