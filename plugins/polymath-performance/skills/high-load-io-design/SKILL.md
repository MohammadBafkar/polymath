---
name: high-load-io-design
description: Design high-throughput IO-bound services — concurrency model, pool sizing (Little's law), batching, backpressure, load shedding.
---

# high-load-io-design

> An IO-bound service spends most of its life waiting. Throughput comes from keeping many requests in flight without exhausting a pool, a socket, or a downstream — and from refusing work you can't finish.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A service handling thousands of concurrent connections or requests (proxy, gateway, ingest, chat, streaming, file/object transfer) must hit a throughput and latency target.
- Latency climbs under load while CPU is low (queueing on pools, locks, or sockets), or throughput plateaus below hardware limits.
- Choosing a concurrency model (threads, event loop, async/await, actors, virtual threads) or sizing pools.

Not this when: you are chasing one route's P99 with traces and profiles — `polymath-performance:backend-tail-latency`; or CPU-bound hot spots — `polymath-performance:app-profiling`. Sizing a design's capacity before building — `polymath-scalability:capacity-estimation`.

## Inputs

- Throughput and latency targets (peak requests/s, concurrent connections, p99) and payload sizes.
- Per-request profile: CPU time vs time waiting on IO (database, HTTP, disk, queue); fan-out per request.
- Runtime and framework, current pool/thread/connection settings, limits (file descriptors, ephemeral ports, downstream max connections/rate limits).
- Measurements: in-flight count, queue/wait time per pool, CPU utilization, socket/FD counts, GC/allocation rate. Missing → `[TBD: measure]` and proceed on the model.

## Procedure

1. **Characterize the work**: CPU ms vs wait ms per request. Wait ≫ CPU ⇒ IO-bound: concurrency (not more cores) is the lever. CPU-bound ⇒ parallelism up to cores, then profile (`app-profiling`).
2. **Size concurrency with Little's law — via the calculator, not by feel.** In-flight work L = λ × W. Pool/worker size = L ÷ target utilization; for blocking threads, cores × util × (1 + wait/cpu):

   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/high-load-io-design/scripts/concurrency.py" \
     --rate 800 --latency-ms 45 --target-util 0.7 --cpu-ms 5 --cores 8
   ```

   Add `--capacity N --backlog M` to compute queue drain time (or "never drains"). Run per scenario; exit 2 = bad input.
3. **Choose the concurrency model** by connection count and blocking behavior: thread-per-request (simple; ~thousands of threads is the practical ceiling because of memory and scheduling), virtual/green threads (Java 21 virtual threads, Go goroutines — blocking-style code with cheap concurrency; beware pinning and unbounded spawning), event loop/async (Node, asyncio, Netty, Tokio — highest connection density, but one blocking call or CPU burst stalls everyone: offload to a bounded worker pool), actors/message passing. Mixing models needs explicit boundaries (blocking calls off the event loop).
4. **Bound every queue and pool — and make the bounds line up.** The order should narrow toward the scarce resource: accepted connections ≥ in-flight requests ≥ DB/HTTP client pool ≥ DB `max_connections` share. Total client pool across all instances must fit the downstream (instances × pool ≤ target share of `max_connections`; use a pooler). An unbounded queue turns overload into unbounded latency and OOM.
5. **Reuse connections.** Keep-alive/HTTP/2 multiplexing to downstreams, connection pools with max-lifetime and idle-timeout shorter than the server's/LB's (avoid using a connection the peer already closed), TLS session resumption, DNS caching with re-resolution. Watch ephemeral port and `TIME_WAIT` exhaustion on high-churn clients; fix with pooling, not kernel knobs first.
6. **Cut round trips and bytes:**
   - **Batch**: bulk inserts/`COPY`, multi-get, producer batching (size + linger), coalescing identical in-flight requests (request collapsing / single-flight).
   - **Pipeline/parallelize** independent downstream calls with a deadline; sequential awaits are the commonest hidden latency.
   - **Compress** when CPU is cheaper than bytes (and measure); **stream** large bodies instead of buffering; use `sendfile`/zero-copy for static and large objects; hand big payloads to object storage with signed URLs.
   - **Avoid N+1** across services as well as in the ORM.
7. **Timeouts and deadlines everywhere**: connect, request, and total; propagate the remaining deadline downstream; set timeouts from the dependency's measured p99, below the caller's. No timeout means a stuck dependency eventually consumes every worker.
8. **Load shedding and backpressure.** Admission control at the edge: concurrency limit per instance (static from step 2, or adaptive, e.g. gradient/AIMD), reject early with `503`/`429` + `Retry-After` when saturated, prioritize critical traffic, and propagate backpressure (bounded channels, pull-based consumers, TCP flow control, reactive streams demand) instead of buffering. Pair with resilience patterns — `polymath-architecture:resilience-design`, `polymath-scalability:rate-limiting-design`.
9. **Tune the OS/runtime only after the design is right**: file-descriptor limits, `somaxconn`/accept backlog, TCP buffers, `SO_REUSEPORT` for multi-process accept, epoll thread counts, GC choice and heap for latency, CPU pinning/NUMA for extreme cases. Each change needs a before/after measurement.
10. **Prove it under load**: test with realistic payloads, connection counts, slow clients, and downstream latency injected (`polymath-test-automation:load-test`); use open-loop load (fixed arrival rate), not closed-loop, so coordinated omission doesn't hide queuing; watch in-flight, queue wait, saturation of each pool, and the knee of the latency curve. Set autoscaling on in-flight/queue age, not CPU.

## Output

```text
High-load IO design: image-upload gateway — 4,000 req/s peak, p99 < 300 ms, avg 45 ms (5 ms CPU, 40 ms waiting on storage + metadata DB)

Profile: IO-bound (wait 40 ms vs CPU 5 ms).
Sizing (concurrency.py, rate 800/s per instance × 5 instances):
  in flight 36 per instance; pool/worker 52 at util 0.7; blocking-thread model would need 51 threads on 8 cores.
Model: async event loop (Netty); blocking image-hash step on a bounded pool of 8 (CPU 50% at 800/s).
Bounds: accept backlog 1,024 → max in-flight 120/instance → storage client pool 64 → metadata DB pool 20 × 5 instances = 100 ≤ 40% of max_connections (250) through PgBouncer.
Connections: HTTP/2 to storage; pool max-lifetime 5 min < LB idle 10 min; TLS resumption on.
Round trips: metadata writes batched (50 rows / 20 ms linger); thumbnails via async queue (not on the request path); uploads streamed to storage (no buffering).
Timeouts: storage 400 ms (p99 280 ms) retry once idempotent PUT; DB 150 ms; total deadline 300 ms propagated.
Shedding: per-instance concurrency limit 120 → 503 + Retry-After 1 s; premium tenants reserved 20%.
Load test: open-loop 1.5× peak with 5% slow clients, storage +100 ms injected; success = p99 < 300 ms, zero pool-wait > 20 ms, graceful 503 at 2×.
Open: [VERIFY: storage per-prefix request limit — shard key prefixes if hit].
```

## Quality bar

- Pool and worker sizes follow from rate × latency and a utilization target (calculator output), and are consistent end to end with downstream limits.
- Every queue and pool is bounded, with a stated overload behavior (shed/reject/backpressure).
- Timeouts and a propagated deadline exist for every remote call.
- The concurrency model matches the workload, and blocking work is isolated from event loops.
- The validation plan uses open-loop load with slow-client and slow-dependency injection.

## Anti-patterns to avoid

- "Just add threads / bigger pool": it moves the queue to the downstream and often worsens the tail.
- A blocking call (DNS, file IO, JDBC, `requests`) on an event-loop thread.
- Unbounded executors, channels, or in-memory buffers.
- Instance count × pool size above the database's connection limit.
- Closed-loop benchmarks that slow down when the server does, hiding queueing.
- Kernel tuning as the first move, or copying `sysctl` blocks without a measurement.
