---
name: azure-event-hubs-design
description: Design and size Azure Event Hubs — tier, throughput units, partitions, consumer groups, checkpointing, Capture, Kafka endpoint.
---

# azure-event-hubs-design

> Event Hubs is a partitioned log with managed capacity. The partition count (fixed early) caps consumer parallelism; the tier and throughput units cap bytes per second. Size both from the numbers, and checkpoint with care.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Ingesting telemetry, logs, clickstream, or domain events on Azure with Event Hubs (AMQP or Kafka protocol).
- Hitting `ServerBusy`/throttling, uneven partition load, or consumers that lag or reprocess after restarts.
- Choosing between Event Hubs, Service Bus, and Kafka (self-managed/Confluent) on Azure, or planning Capture to ADLS.

Not this when: the platform is Kafka outside Azure — `polymath-streaming:kafka-performance-tuning` and `streaming-design`. For the enterprise-message (commands, sessions, DLQ, transactions) pattern — Service Bus is the fit; see `polymath-architecture:integration-design`. For the Azure landing zone — `polymath-cloud:design-azure-pattern`.

## Inputs

- Peak ingress (MB/s and events/s), average event size, fan-out (number of independent consumer groups) and egress, retention/replay needs, ordering key.
- Consumers: Azure Functions, Stream Analytics, Databricks/Spark, Flink, custom `EventProcessor`, Kafka clients.
- Availability: zonal/regional requirements, RPO/RTO, networking (private endpoints, firewall), identity (Entra ID/managed identity vs SAS).
- Limits: current Event Hubs quotas for the chosen tier — **verify against the Microsoft Learn quotas page**; numbers, regions, and features change by tier and over time.

## Procedure

1. **Is Event Hubs the right primitive?** Event Hubs: high-volume ordered-per-partition streaming, replay within retention, many readers (log semantics). Service Bus: per-message processing, DLQ, sessions, scheduled delivery, transactions. Event Grid: discrete reactive notifications. If you need per-message ack/redelivery, ordering by session, or small command volumes, use Service Bus.
2. **Pick the tier from requirements**: Standard (throughput units, up to short retention, Kafka endpoint, Capture, auto-inflate) for most workloads; Premium (processing units, resource isolation, longer retention, more partitions/consumer groups, dynamic partition scaling) for predictable latency, isolation, and larger scale; Dedicated (capacity units) for very high throughput and single-tenant clusters. Basic lacks consumer-group, Capture, and Kafka features. Confirm current feature matrix.
3. **Size throughput.** Standard throughput unit (TU) ≈ 1 MB/s or 1,000 events/s ingress, whichever first, and 2 MB/s or 4,096 events/s egress [VERIFY: current numbers]. TUs needed = max(peak ingress MB/s, peak events/s ÷ 1,000, peak egress ÷ 2). Egress includes every consumer group reading the full stream. Enable auto-inflate with a ceiling for bursts (it scales up, not down); in Premium, size processing units and test. Small events hit the events/s limit before MB/s — batch on the producer.
4. **Choose partition count carefully.** Parallelism ceiling = partitions (one active reader per partition per consumer group). Partitions can't be changed after creation on Basic/Standard (only added in Premium/Dedicated; never reduced) — plan for the planning horizon: `partitions ≥ max(peak consumers needed, peak MB/s ÷ safe per-partition MB/s)` with headroom, within tier limits. Per-partition throughput is bounded; hot keys concentrate on one partition.
5. **Partitioning and ordering.** Ordering is per partition. Use a partition key (hashed to a partition; the same key lands on the same partition) for per-entity ordering — and check key skew. Don't set partition IDs explicitly unless you must; an unavailable partition then fails the send, while a key/round-robin lets the service balance. Don't use a key at all when ordering is irrelevant.
6. **Producer practices.** Batch sends (`EventDataBatch`, up to the max batch size) rather than one send per event; reuse the client/connection (AMQP connections are expensive); async with retries; handle `ServerBusy` with backoff (it signals a throttle — raise TUs/PUs or reduce rate); consider compression in the payload. Max event size is limited — large payloads go to Blob storage with a pointer.
7. **Consumer groups and checkpointing.** One consumer group per independent consuming application (never share a group between apps; `$Default` is for quick tests). With `EventProcessorClient`, state lives in Blob Storage (checkpoint + partition ownership): use a storage account in the same region, avoid frequent checkpoints (checkpoint per batch or every N events/seconds, not per event — each is a storage write), and make processing **idempotent** — checkpoint after processing gives at-least-once, so after a restart or rebalance you reprocess since the last checkpoint. For Azure Functions Event Hubs trigger, tune `maxEventBatchSize`/`prefetchCount` and watch for batch redelivery on failures; poison events need an explicit dead-letter strategy (Event Hubs has no DLQ — write failures to a side Event Hub/Blob/Service Bus).
8. **Capture to the lake.** Enable Capture to ADLS Gen2/Blob (Avro) with time and size windows (smaller windows → more, smaller files; compact later — `polymath-streaming:data-lake-layout`). Capture is the long-term record; keep Event Hubs retention short (the replay window you really need). Downstream: Databricks Auto Loader / Synapse / Fabric over the Capture path.
9. **Kafka protocol option.** Standard+ exposes a Kafka-compatible endpoint (SASL, port 9093): existing Kafka clients work with config changes (event hub = topic, namespace = cluster). Limits differ from Apache Kafka (no log compaction on all tiers, feature gaps) — verify feature needs (transactions, compaction, Kafka Streams) before committing.
10. **Resilience and DR.** Zone redundancy (on by default in supported regions). Geo-disaster recovery (metadata/namespace pairing, no event data) vs geo-replication (replicates data, Premium/Dedicated) — state the RPO each really gives; consumers must tolerate duplicates and offset/sequence differences after failover (`polymath-scalability:multi-region-design`). Alert on throttled requests, server errors, and consumer lag.
11. **Security and networking.** Entra ID RBAC with managed identities over SAS keys; private endpoints and firewall rules; customer-managed keys if required; separate namespaces per environment/blast radius.
12. **Monitor** the metrics that matter: incoming/outgoing bytes and messages vs the throughput limit, throttled requests, server errors, per-partition skew (via captured metrics/logs), consumer lag (checkpoint position vs last sequence number), Capture backlog.

## Output

```text
Event Hubs design: vehicle telemetry (Azure, West Europe)

Choice: Event Hubs (log semantics, replay, 4 independent consumers). Not Service Bus (no per-message ack workflow).
Tier: Standard with auto-inflate [TBD: move to Premium if private-link isolation/latency SLO required].
Load: peak 18 MB/s, 22,000 events/s (≈ 0.8 KB each) → TUs = max(18, 22, egress (4 groups × 18 = 72 MB/s ÷ 2 = 36)) = 36 TU, egress-bound. That sits close to the Standard auto-inflate ceiling [VERIFY: current TU cap], leaving little burst headroom → Premium (size PUs from a load test) or cut egress by feeding cg-search and cg-replay from the Capture files instead.
Partitions: 32 [VERIFY: tier max]; ≥ max(24 consumers, 18 MB/s ÷ 1 MB/s per partition) = 24; round to 32; vehicle_id as partition key (fleet 2 M vehicles → even; top vehicle < 0.001%).
Producers: batched EventDataBatch (≈ 100 events), shared client, backoff on ServerBusy.
Consumer groups: cg-alerts (Functions), cg-stream (Databricks Structured Streaming), cg-search (indexer), cg-replay (ad hoc).
Checkpointing: Blob checkpoint every 500 events or 10 s; processors idempotent on (vehicle_id, event_seq).
Capture: Avro to ADLS Gen2, 5 min / 100 MB windows; Event Hubs retention 3 d; compaction job hourly → Delta bronze.
DR: zone-redundant; geo-replication to North Europe [VERIFY: tier support]; consumers dedupe across failover.
Security: managed identity RBAC, private endpoints, no SAS in apps.
Alerts: ThrottledRequests > 0, ServerErrors, lag age > 2 min, Capture backlog.
```

## Quality bar

- Tier, TUs/PUs, and partitions are computed from stated rates and flagged `[VERIFY]` against current Microsoft limits.
- The partition count decision accounts for being fixed (Standard) and for key skew.
- Consumer groups are one-per-application, checkpoints are batched, and processing is idempotent.
- Capture/retention split is explicit: short retention for replay, lake for history.
- Failure handling (no DLQ in Event Hubs, throttling, DR duplicates) is designed, not assumed.

## Anti-patterns to avoid

- Sharing one consumer group across applications, or leaving everything on `$Default`.
- Underestimating egress: each consumer group reads the whole stream.
- Checkpointing every event, or checkpointing before processing.
- One `send` per event over a new connection each time.
- Picking a low partition count "for now" on Standard and discovering it can't be raised.
- Using Event Hubs where per-message redelivery, DLQ, or sessions are required.
