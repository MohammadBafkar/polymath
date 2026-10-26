---
name: streaming-design
description: Design a streaming topology (Kafka/Pulsar/Kinesis) — topics, partitioning key, delivery semantics, consumer groups, retention/compaction, ordering, and backpressure.
---

# streaming-design

> A stream is a durable, partitioned, replayable log — not a queue. The partition key decides ordering, parallelism, and hot-spots all at once, so choose it first.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Standing up or reshaping a Kafka/Pulsar/Kinesis topic and its producers/consumers.
- Deciding delivery semantics, partition count/key, or retention for an event stream.
- A workflow invokes `polymath-streaming:streaming-design`.

Not this when: you are designing the *business* event flow (saga, choreography, outbox) — that is `polymath-architecture:event-driven-design`. For windowed/stateful computation over the stream, `polymath-streaming:stream-processing`.

## Inputs

- The events, their volume/throughput, ordering needs, and consumer count.
- Durability/replay and retention requirements.

## Procedure

1. **Topic design**: one topic per event type/bounded purpose; name and own it. Decide schema + a registry with a compatibility rule (backward/forward).
2. **Partition key** — the central decision: pick a key that (a) co-locates events that must stay ordered (e.g. per-entity id), (b) spreads load evenly (avoid a hot key), (c) supports the consumer parallelism you need. Ordering is per-partition only — there is no global order.
3. **Partition count**: `partitions = max(peak MB/s ÷ measured per-partition MB/s, peak consumer parallelism) × growth headroom`, rounded up — show the arithmetic with its inputs (measured, or `[TBD]` when not). Repartitioning later breaks key→partition mapping, so size for the planning horizon, not today.
4. **Delivery semantics**: at-least-once (default; consumers must be idempotent), at-most-once (lossy, rare), or exactly-once (transactions/idempotent producer — costs throughput; use only where dupes are unacceptable). Name the choice and the dedup mechanism.
5. **Consumer groups**: one group per independent consumer concern; within a group, partitions divide across members. Plan rebalancing behavior and offset-commit strategy (commit after processing, not before).
6. **Retention / compaction**: time/size retention for event logs; log compaction for changelog/“latest state per key” topics. State replay expectations.
7. **Backpressure & lag**: monitor consumer lag; decide what happens when consumers fall behind (scale out, pause producers, or shed) — never silently unbounded.
8. **Failure handling**: dead-letter topic for poison messages, and a retry/skip policy.

## Output

```text
Streaming topology: order events (Kafka)

Topics
  orders.order-events.v1   owner: ordering   schema: Avro in the registry, BACKWARD compatible
  orders.order-events.dlq  owner: ordering   poison messages + error header
Partition key: order_id — keeps one order's events in order; 2.1 M distinct ids/day spreads load; no hot key
Partition count: max(peak 24 MB/s ÷ 2 MB/s measured per partition = 12, peak consumers 16) × 1.5 headroom = 24
Delivery: at-least-once; idempotent producer on; consumers dedupe on event_id (processed_events table, 7 d)
Consumer groups
  fulfillment-svc   commits offsets after the DB write succeeds (never before)
  analytics-sink    separate group — its lag never slows fulfillment
Retention: 7 days delete; changelog topic orders.order-state compacted (latest state per order)
Lag: alert when fulfillment-svc lag > 5 min; response = scale consumers to 24 (one per partition), then page
DLQ: 3 retries with backoff → DLQ; DLQ alert on any message; replay tool documented in the runbook
```

## Quality bar

- The partition key is justified against ordering, load spread, and parallelism together.
- Delivery semantics are stated, and at-least-once is paired with idempotent consumers.
- Offsets commit after successful processing; a DLQ exists for poison messages.
- Consumer lag is monitored with a defined behavior when consumers fall behind.
