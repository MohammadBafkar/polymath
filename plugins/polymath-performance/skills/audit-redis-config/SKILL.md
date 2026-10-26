---
name: audit-redis-config
description: Audit a live Redis instance's config — maxmemory + eviction, persistence (RDB/AOF), replication, slow-log, ACL, TLS. Audits existing settings; not cache design (design-cache-layer).
---

# audit-redis-config

> Sanity-check a Redis deployment against the workload. Output: parameter findings + concrete changes.

## When to use

- A Redis instance is evicting unexpectedly, running out of memory, slow, or about to take more load.
- A security review needs the instance's auth/TLS/exposure posture.

## Inputs

- Effective settings: `CONFIG GET *` and `INFO` (`memory`, `persistence`, `replication`, `clients`), plus the version. Managed services (ElastiCache, Memorystore, Azure Cache) often disable or rename `CONFIG` — read their parameter group / console instead.
- The workload role: pure cache, session store, queue, or primary store.

**Read-only.** Never run `CONFIG SET`, `CONFIG REWRITE`, `FLUSH*`, `DEBUG`, or `KEYS *` against a live instance — recommend; the owner applies.

## Procedure

1. **Memory.**
   - `maxmemory` set explicitly, not "no limit". Without a cap, Redis OOMs the host.
   - `maxmemory-policy` matches the workload: `allkeys-lru` (pure cache), `volatile-lru` (mixed), `noeviction` (queue / store).
2. **Persistence.**
   - RDB snapshots — point-in-time + fast load. Lose up-to-snapshot-interval on crash.
   - AOF — append-only log; choose `appendfsync everysec` (1s window) or `always` (sync per write, slow).
   - For caches: persistence often off (just warm up from origin).
   - For queues / sessions: AOF + RDB hybrid is the usual.
3. **Replication.**
   - `replicaof` master:port if a replica.
   - `replica-read-only yes` — replicas should not accept writes.
   - `repl-diskless-sync yes` for big setups (avoids the disk-write during full sync).
4. **Slow log.**
   - `slowlog-log-slower-than 10000` (10 ms, in µs) — logs every command slower than the threshold (a fixed cutoff, not a percentile).
   - `slowlog-max-len 1024` — small ring buffer.
5. **Client connections.**
   - `maxclients` should match the connecting application's connection pool.
   - `timeout` (idle client disconnect) — 0 by default; set 300s in shared environments.
6. **ACL.**
   - Default user disabled or non-default password.
   - Per-application ACLs with command + key-prefix scoping.
   - `requirepass` (legacy) is single-user; ACLs are the modern way.
7. **Exposure.**
   - `protected-mode yes` and `bind` limited to private interfaces — never `0.0.0.0` on a reachable network without auth.
   - Dangerous commands (`FLUSHALL`, `FLUSHDB`, `KEYS`, `CONFIG`, `DEBUG`) denied to application users via ACL categories (`-@dangerous`), or renamed on older versions.
8. **TLS.**
   - `tls-port` enabled in any non-trusted network.
   - `tls-cert-file` / `tls-key-file` + `tls-auth-clients` for mTLS.
9. **Cluster vs single.** Cluster mode (`cluster-enabled yes`) shards across nodes; consumers must use cluster-aware clients (no `KEYS *` across slots).

## Output

```text
audit-redis-config

Host:    cache-1.refund-prod
Version: 7.2

Memory
  ✓ maxmemory = 8gb
  ⚠ maxmemory-policy = noeviction; workload is cache. Recommend allkeys-lru.

Persistence
  RDB: snapshots every 1h.
  AOF: off.
  ✓ Acceptable for pure cache.

Replication
  ✓ Two replicas, replica-read-only = yes.

Slow log
  ⚠ slowlog-log-slower-than = -1 (disabled). Set to 10000.

ACL
  ✗ default user enabled with empty password.
    Fix: disable default; create per-app users with key-prefix scoping.

TLS
  ✗ TLS not configured; cluster on a private VPC may still benefit.

Recommendation: 3 changes (eviction policy, slow-log, ACL hygiene).
```

## Anti-patterns to avoid

- `noeviction` on a workload that exceeds maxmemory. Writes start failing instead of evicting.
- AOF disabled + RDB at 24h interval on a session store. Up to 24h of session loss on crash.
- Single shared password across all clients. Compromise of one client compromises all.
- `KEYS *` recommended anywhere. Blocks the server; use `SCAN` for iteration.
