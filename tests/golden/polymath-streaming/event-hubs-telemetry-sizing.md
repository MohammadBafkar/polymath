---
plugin: polymath-streaming
scenario: event-hubs-telemetry-sizing
expect:
  invoked:
    - polymath-streaming:azure-event-hubs-design
  output_matches:
    - "(throughput unit|TU|processing unit)"
    - "(partition)"
    - "(Capture|checkpoint)"
timeout_seconds: 120
---

# Prompt

> Size an Azure Event Hubs namespace for 18 MB/s and 22k events/s of vehicle telemetry with four independent consumer groups. How many partitions, which tier, and how do we handle checkpointing and long-term storage?

Use polymath-streaming:azure-event-hubs-design.

# Acceptance

- Counts egress per consumer group in the unit math.
- Partition count reasoning including that it is fixed on Standard.
- Idempotent processing, batched checkpoints, Capture to the lake.
