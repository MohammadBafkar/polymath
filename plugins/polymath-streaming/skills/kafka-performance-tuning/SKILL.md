---
name: kafka-performance-tuning
description: Tune Kafka throughput, latency and consumer lag — producer batching, acks, fetch, rebalances, broker IO. Not topology (streaming-design).
---

# kafka-performance-tuning

> Kafka is fast when it does large sequential IO in batches and slow when you make it do small, synchronous, or skewed work. Find which of producer, broker, or consumer is the limit before turning any knob.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Producers are throttled or high-latency, consumers lag, or the cluster is saturated (disk, network, request handlers).
- Planning a throughput increase (10× events) and needing to know which limit hits first.
- Consumer groups rebalance constantly or process unevenly.

Not this when: you are designing topics, keys, and delivery semantics — `polymath-streaming:streaming-design`. For stateful stream jobs — `stream-processing`. Azure's managed equivalent — `polymath-streaming:azure-event-hubs-design`.

## Inputs

- Target: peak MB/s and events/s in, fan-out (consumer groups), end-to-end latency goal, durability needs (acks/replication).
- Cluster: Kafka version, broker count/size/disks/network, replication factor, `min.insync.replicas`, partition counts, managed (MSK, Confluent Cloud, Aiven) or self-run.
- Evidence: broker and client metrics (request rate, bytes in/out, request latency percentiles, `RequestHandlerAvgIdlePercent`, network processor idle, ISR shrinks, under-replicated partitions, disk util/IO wait, consumer lag per partition and its trend). Without metrics, say what to collect first.
- Event size, key distribution, compression ratio, consumer processing time per record.

**Production caution.** Config changes to brokers can cause rolling restarts and leader movement; client changes are lower risk. Recommend, stage, and measure one change at a time; the owner applies.

## Procedure

1. **Locate the bottleneck by comparing rates.** Producer send rate vs broker bytes-in vs consumer fetch rate vs lag growth. Producer-side latency with idle brokers ⇒ client batching or network; high request-queue time or low handler idle ⇒ broker CPU/threads; saturated disk or page-cache misses ⇒ storage; lag growing with idle brokers ⇒ consumers.
2. **Producer tuning (throughput ↔ latency):**
   - Batch: raise `batch.size` (64–256 KB for high volume; default 16 KB is small) and set `linger.ms` (5–50 ms) so batches fill; trade a few ms latency for large throughput gains and fewer requests.
   - `compression.type` `lz4` (fast) or `zstd` (higher ratio) — batch compression multiplies effective network and disk throughput; measure CPU.
   - Durability: `acks=all` with `replication.factor=3`, `min.insync.replicas=2` for no-loss; `acks=1` trades safety for latency (document the loss window). `enable.idempotence=true` (default in recent clients) gives per-partition ordering and dedup with up to 5 in-flight; transactions only if you need exactly-once across topics.
   - `buffer.memory`, `max.block.ms`, `delivery.timeout.ms` sized so back-pressure surfaces as a handled error, not an unbounded stall; many small producers → shared producer instance per process (a producer is thread-safe).
   - Partitioner: sticky/uniform for null keys (fills batches); skewed keys concentrate load on one partition — fix the key, not the batch.
3. **Broker tuning:**
   - **Disk and page cache**: Kafka relies on the OS page cache and sequential IO; give brokers RAM beyond the JVM heap (heap small, e.g. 6–8 GB), dedicated disks (XFS), avoid noisy neighbours; consumers reading old data (not in cache) hit disk — a catch-up consumer can degrade producers.
   - **Threads**: `num.network.threads`, `num.io.threads`, `num.replica.fetchers` when handler idle percent is low and CPU is available; check request-queue time before raising.
   - **Replication**: follower fetch lag and ISR shrinks reveal slow disks/network; `replica.lag.time.max.ms`; keep `unclean.leader.election.enable=false` for durable topics; rack-aware placement for AZ fault tolerance (cross-AZ replication traffic has a cost).
   - **Partitions per broker**: each partition costs file handles, memory, and leader-election time; stay within recommended limits for your version (KRaft raises the ceiling) and rebalance leaders (`auto.leader.rebalance.enable`, Cruise Control) to avoid hot brokers.
   - **Segments and retention**: `log.segment.bytes`/`log.retention.*` tuned for delete cost and compaction; tiered storage (KIP-405, production-ready in recent versions) for long retention with cheap storage; limits listed in `polymath-database:data-retention-archiving`.
   - Quotas (`producer_byte_rate`, `consumer_byte_rate`, request quotas) protect the cluster from one noisy client.
4. **Consumer tuning and lag diagnosis:**
   - Lag in *time* (oldest unprocessed age) matters more than offset count. Split causes: (a) too slow per record (processing, downstream calls — profile and batch writes, parallelize within the partition by key if ordering allows), (b) too few consumers/partitions (parallelism ≤ partitions; consumers beyond that idle), (c) skew (one hot partition), (d) rebalances/pauses, (e) broker/fetch limits.
   - Fetch: `fetch.min.bytes` + `fetch.max.wait.ms` for fewer, bigger fetches; `max.partition.fetch.bytes`; `max.poll.records` sized so processing fits within `max.poll.interval.ms` (exceeding it kicks the consumer out → rebalance loop).
   - Rebalances: cooperative sticky assignor (`CooperativeStickyAssignor`), static membership (`group.instance.id` + longer `session.timeout.ms`) for rolling deploys, fast shutdown with commit; don't do long work inside the poll thread without heartbeats.
   - Commits: `enable.auto.commit=false`, commit after processing, batched (sync per batch or async with a final sync) — commit frequency is a hidden throughput cost.
   - Scaling out: add partitions first if consumers ≥ partitions — changing partition counts breaks key→partition mapping for keyed topics, so plan it (`streaming-design`).
5. **Network and cross-AZ**: compression, `replica`/`follower` fetching from nearest replica (KIP-392) for consumers to cut cross-AZ cost, and sizing NICs (broker out-bandwidth = replication + consumers × bytes-in).
6. **Capacity math** (use `polymath-scalability:capacity-estimation` for sizing): per-broker ingress = produce MB/s × RF ÷ brokers; egress = ingress × (RF − 1)/RF replication + consumer groups × produce MB/s; keep disks and NICs under ~60–70% at peak so a failed broker's load fits on the rest.
7. **Change one thing, then measure** end-to-end: producer p99 send latency, request-queue time, ISR stability, consumer lag/age; define the rollback.

## Output

```text
Kafka tuning review: clickstream (Kafka 3.7, 9 brokers m5.2xlarge, RF 3, min.insync 2)

Symptom: consumer group "sessionizer" lag 18 min and growing; producers fine.
Evidence: bytes-in 140 MB/s steady; broker handler idle 62%, disk util 35%; sessionizer has 24 consumers on a 24-partition topic; partition 17 holds 31% of messages (key = country, "US"); per-record processing 4.1 ms with one DB call each.
Bottleneck: consumer — skewed partition + per-record DB round trips. Not brokers.

Changes (in order)
  1. Consumer: batch DB writes per poll (max.poll.records 500) → est. ≥ 5× records/s per consumer [VERIFY: measure]; commit after each batch.
  2. Key: change key from country to session_id (new topic version + dual-publish window, see streaming-design); until then isolate partition 17 with a dedicated consumer instance.
  3. Rebalance: CooperativeStickyAssignor + group.instance.id, session.timeout 45 s (rolling deploys currently cause 90 s full stalls).
Producer (optional, cost): linger.ms 5→20, batch.size 16 KB→128 KB, compression lz4 → ~40% less network [VERIFY: measured ratio].
Broker: no change — handler idle 62%, disk 35%.
Verify: lag age < 1 min, p99 per-batch time, partition-level lag evenness, rebalance count/day.
Unknowns: [TBD: consumer GC/heap behavior at 500-record batches]
```

## Quality bar

- The limiting component (producer/broker/consumer) is identified with rate and utilization evidence before any tuning.
- Each change names the metric that will show its effect, and durability changes (`acks`, replication, `min.insync.replicas`) state the loss window.
- Lag is reasoned in time and per partition, and consumers ≤ partitions is checked.
- Partition-count and key changes carry the keyed-ordering caveat.
- Changes are applied one at a time with rollback.

## Anti-patterns to avoid

- Raising partitions to "fix" lag that is per-record processing time or key skew.
- `acks=0/1` or `min.insync.replicas=1` for speed on data that must not be lost, without a documented loss window.
- Enormous `max.poll.records` with slow processing — rebalance storm.
- Tuning broker threads or JVM heap before checking page cache and disk behavior.
- Doing synchronous per-record side effects in the consumer loop.
- Treating total offset lag as the SLO instead of consumer lag age.
