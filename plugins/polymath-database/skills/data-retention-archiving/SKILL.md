---
name: data-retention-archiving
description: Design retention and archiving — tiers, partition-drop purges, legal hold, deletion requests, restore tests — for DBs, event logs, lakes.
---

# data-retention-archiving

> Data you keep forever costs forever — in storage, backup time, query speed, and legal exposure. Decide per data class how long it lives, where it sits as it ages, and how it dies.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A table, topic, log index, or lake zone is growing without bound, or storage/backup/restore time is hurting performance and cost.
- Defining or auditing retention for events (Kafka/Event Hubs topics, event stores), operational databases, logs, and analytical data.
- A compliance, privacy, or legal requirement (GDPR erasure, financial records, litigation hold) touches stored data.

Not this when: you're choosing broker partitioning or compaction mechanics only — `polymath-streaming:streaming-design`. For compliance control mapping — `polymath-security:compliance-mapping`.

## Inputs

- Inventory of data classes: what it is, where it lives, size and growth, who reads it and how often, and age at which reads fall off (read-age histogram if available).
- Obligations: legal/regulatory minimums and maximums (tax, financial, healthcare, privacy), contractual terms, and the owner who may state them. Retention periods come from the owner or counsel — never invent one; mark `[TBD: owner/legal]`.
- Technical: engine/storage tiers, backup scheme, replication and downstream copies (CDC targets, lake, search index, caches), and deletion mechanisms available.

## Procedure

1. **Classify the data.** For each class: purpose, sensitivity (PII, financial, secrets), authoritative copy vs derived copies, and the *business reason* to keep it. Data without a purpose is a deletion candidate.
2. **Set retention per class** with a floor and a ceiling: the legal/contract minimum, the business-value horizon, and the privacy maximum (storage limitation). Record the owner and the date of the decision. Where requirements conflict (keep 7 years vs erase on request), name the resolution — usually erase identifiers, retain the minimum record.
3. **Tier by age and access.** Typical shape: **hot** (primary DB / SSD, low latency, recent window) → **warm** (read replica, cheaper volume, or compressed partitions) → **cold** (object storage, Parquet/ORC, queryable via the lake) → **archive** (infrequent-access/glacier-class storage with retrieval delay and cost) → **delete**. Choose each boundary from the read-age histogram and the restore-time the business can tolerate, not a round number. Count minimum-storage-duration and retrieval fees of the cold tiers.
4. **Pick the mechanism that scales:**
   - **Relational**: partition by time and detach/drop partitions (`polymath-database:partitioning-sharding`) — O(1) and no bloat — instead of massive `DELETE` (bloat, WAL, replica lag). If unpartitioned, delete in bounded batches with throttling, an index on the age column, and vacuum headroom; archive-then-delete in the same job with verification.
   - **Event logs/streams**: topic retention by time/size (`retention.ms`, Event Hubs retention) for replay windows; compaction for latest-state-per-key; tiered storage for long Kafka retention; **sink to the lake** (Kafka Connect, Event Hubs Capture, Auto Loader) as the long-term record rather than extending broker retention. State what replay needs, and what breaks if a consumer is offline longer than retention (`polymath-streaming:kafka-performance-tuning` for lag).
   - **Lakes/warehouses**: table-format retention (snapshot expiry, `VACUUM` in Delta, `expire_snapshots` in Iceberg), partition lifecycle, object-store lifecycle rules, and compaction before archival (`polymath-streaming:data-lake-layout`).
   - **Logs/metrics/traces**: index lifecycle management with rollover, sampling and downsampling for old data.
   - **NoSQL**: TTL attributes (`polymath-database:nosql-partition-design`), mind asynchronous deletion and tombstones.
5. **Archive so it can be read back.** Self-describing format with schema and version, the encryption keys retained as long as the data (key deletion is a deletion mechanism — `polymath-security:crypto-review`), immutable/WORM storage when required, a catalog entry (what, when, where, how to restore), and a **restore test** on a schedule — an untested archive is a hope.
6. **Deletion must reach every copy.** Enumerate derived copies (replicas, CDC sinks, search indexes, caches, analytics tables, backups, logs). For erasure requests define the path and SLA: delete from the primary, propagate tombstones/events, and let backups age out within a stated window (or use crypto-shredding per subject). Event streams with immutable history need a design (tokenize PII, per-subject keys, compaction with tombstones) — not a promise.
7. **Legal hold.** A hold overrides purge for the affected records: a flag/scope that the purge job honors, an audit trail of who set it and when, and a release path. Test that the purge job actually skips held data.
8. **Make it operable.** The purge/archive job is idempotent, resumable, rate-limited, observable (rows/bytes moved, lag behind policy, failures), runs off-peak, supports dry-run, and has a kill switch. Alert when data older than policy exists (policy drift) and when a purge deletes anomalously much (guard against a bad predicate).
9. **Quantify the payoff.** Storage and backup-window reduction, query/IO improvement, restore-time improvement, and cost by tier — computed from sizes and rates, with unknowns marked.

## Output

```text
Retention & archiving plan: payments platform

Class                 Where                 Floor (why)                    Ceiling   Tiering / mechanism
payment_events        Postgres ledger       7 y (financial records)  [TBD: confirm w/ finance]  10 y   hot 13 mo (partitions) → cold Parquet on S3 → IA after 3 y → delete at 10 y
order_events (Kafka)  orders.order-events   replay window 7 d              7 d      broker retention 7 d; sink to lake (Connect) = long-term record; compacted orders.order-state
app logs              OpenSearch            30 d (incident analysis)       90 d     ILM: hot 7 d → warm 30 d → delete 90 d; sample DEBUG
user PII (profile)    users DB + CDC        life of account                +30 d after closure   erase on request ≤ 30 d; backups age out ≤ 35 d; lake copies tokenized
Archive: Parquet + schema file + manifest (catalog table `archive_catalog`); SSE-KMS key retained while data retained; restore test quarterly (last: [TBD]).
Deletion propagation: DB → CDC tombstone → lake MERGE delete + search index delete; caches expire ≤ 24 h.
Legal hold: `legal_hold` table checked by purge job; test "held rows survive purge" in CI.
Purge job: monthly partition detach → verify row count + checksum in archive → drop; dry-run flag; alert if > 2× expected rows.
Payoff: ledger shrinks ≈ [TBD: from size histogram]; backup window and restore time follow.
Open: [TBD: legal minimum for chargeback evidence], [VERIFY: Kafka tiered storage availability on current cluster version].
```

## Quality bar

- Every data class has an owner-stated retention floor and ceiling; none is invented by the skill.
- Deletion covers all derived copies and backups with a stated mechanism and SLA.
- Archives are restorable: format, catalog, keys, and a scheduled restore test are named.
- Legal hold is enforced in code and tested, not left to policy text.
- The mechanism is O(partition), not row-by-row `DELETE`, wherever volume is large.

## Anti-patterns to avoid

- "Keep everything, storage is cheap" — until restore, backup, and query times aren't.
- Giant `DELETE FROM … WHERE created_at < …` on a hot table.
- Extending broker retention to months instead of sinking to a lake.
- Archiving without a restore test or without the key/schema needed to read it.
- Honoring an erasure request in the primary DB while the lake, search index, and logs keep the data.
- A purge job with no dry run, no row-count guard, and no hold check.
