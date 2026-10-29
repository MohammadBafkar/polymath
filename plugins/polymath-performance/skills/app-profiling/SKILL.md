---
name: app-profiling
description: Profile CPU, memory and allocation hot spots — flame graphs, N+1, serialization, GC; one measured fix. Not tail latency (backend-tail-latency).
---

# app-profiling

> Measure, don't guess. A profile shows where the time and bytes actually go; the fix is almost never where intuition points.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A service burns more CPU or memory than expected, throughput is below target, or a hot path "feels slow".
- Cost reduction: shrink the fleet by cutting CPU or memory per request.
- A latency regression appeared between releases and you need a diff of where time moved.

Not this when: the symptom is P99/P999 spikes explained by waiting (GC pauses, locks, queues, downstreams) — `polymath-performance:backend-tail-latency`; or the database is the suspect — `polymath-database:db-performance-triage`.

## Inputs

- The workload to profile: a specific endpoint/job and a reproducible load (a production-like replay, a load test, or live sampling).
- Language/runtime and deployment (JVM, Go, Node, Python, .NET, Rust/C++; container limits).
- The metric to move (CPU per request, p95, allocations/s, RSS) and a baseline measured the same way.

**Production safety.** Prefer low-overhead sampling profilers (continuous profiling, `perf`, async-profiler, `pprof`, py-spy, Pyroscope/Parca/Datadog profiler); instrumenting profilers and heap dumps can pause or slow a production process — run them on a canary or replica, with the owner's OK, and mind PII in dumps.

## Procedure

1. **Define the question and baseline**: "reduce CPU/request of `POST /orders` at 500 rps" with a measured starting point (CPU%, ms/request, allocations/request). Warm up first (JIT, caches), run long enough for stable samples, and keep the environment fixed across runs.
2. **Choose the profile kind to match the symptom:**
   - **CPU** (on-CPU sampling): high CPU%, throughput-bound.
   - **Wall-clock / off-CPU**: low CPU but slow — time spent blocked on IO, locks, sleeps (async-profiler `wall`, `perf` off-CPU, `pprof` block/mutex profiles, Go trace).
   - **Allocation / heap**: GC pressure, high alloc rate, memory growth (allocation profile for churn; heap snapshot diff for leaks — retained size by type and GC roots).
   - **Lock contention**: threads parked, scalability flat with cores.
   - **Traces/spans** to see cross-service structure first (`polymath-observability:trace-investigate`), then profile the service that owns the time.
3. **Capture and read the flame graph** (width = share of samples, not time order): find the widest frames at the top of the stack (self time) and the wide plateaus (inclusive time). Look for *surprising* width: serialization (JSON/proto encode), logging/formatting, regex, reflection, ORM hydration, crypto/hashing, compression, string concatenation, GC threads, `memcpy`/allocator, lock wait, DNS or TLS handshakes, per-request object construction. Diff two profiles (before/after, good/bad release) when comparing.
4. **Classify the hot spot and pick the fix class:**
   - **Wasted work**: N+1 queries/calls, repeated computation, redundant serialization, deserializing then re-serializing, logging at debug in hot paths, loading whole objects for one field → remove or cache (`polymath-performance:caching-tradeoffs`).
   - **Algorithmic**: quadratic loops, wrong data structure, repeated linear scans, sorting to find a max → fix the complexity first; constant-factor tuning cannot beat it.
   - **Allocation/GC**: allocation in hot loops, boxing, short-lived large objects, unbounded collections → reuse buffers/pools, stream instead of materialize, preallocate, change data representation; then GC tuning (collector, heap sizing) with GC logs as evidence.
   - **Concurrency**: coarse locks, false sharing, synchronized singletons, thread pools too small/large → shrink critical sections, shard state, use lock-free/immutable structures (see `high-load-io-design`).
   - **IO**: chattiness, unbatched calls, sync IO on a hot path → batch, pipeline, async.
   - **Runtime/config**: debug builds, missing compiler/JIT flags, container CPU limits throttling (check CFS throttling metrics), wrong GC for the heap, interpreted vs compiled paths.
5. **Pick ONE change** whose estimated share of samples is largest (Amdahl: removing a frame that is 40% of CPU can win at most 40%; a 5% frame can't pay for a risky rewrite). State the expected gain from the profile, e.g. "`jsonEncode` = 31% of CPU; switching the encoder should recover about a third of that [VERIFY]".
6. **Verify by re-measurement**: same load, same environment, same metric; repeat enough runs to see variance; confirm the frame shrank in the new profile, and check for regressions elsewhere (memory, tail latency, correctness). Keep the benchmark/profile as a regression guard (`polymath-performance:perf-budget`).
7. **Stop when the budget is met**, not when the profile is flat. Record what you tried and rejected.

## Output

```text
Profile: POST /orders (JVM 21, 8 vCPU container, 500 rps replay) — goal: CPU/request −25%

Baseline: 62% of 8 vCPU @ 500 rps = 0.62 × 8 ÷ 500 ≈ 9.9 ms CPU/request; GC ≈ 6% of CPU; allocation rate [TBD: from the allocation profile].
Profile kinds run: CPU (30 s ×3, async-profiler), allocation; wall not needed (CPU-bound, no waiting).

Top self-time frames (CPU)
  31%  jackson ObjectMapper.writeValueAsString  ← serializing the full Order graph twice (response + audit event)
  14%  Hibernate entity hydration (N+1: 11 SELECTs/request seen in trace)
  9%   G1 concurrent GC threads (allocation churn from the above)
  6%   Logback pattern formatting at INFO in the hot path
Diagnosis: wasted work — duplicate serialization + N+1 account for ≈ 45% of CPU.

Change (ONE): serialize the audit payload from the already-encoded response bytes (drop the second encode).
Expected: about −15% CPU/request (half of the 31% frame) [VERIFY].
Follow-ups (not now): fetch-join the order lines (N+1); lower log level.
Verification: same replay, 3 runs; expect CPU/request ≤ ~8.4 ms, p95 unchanged or better, GC share down; flame graph shows the second writeValueAsString gone.
```

## Quality bar

- The profile type matches the symptom (CPU vs wall vs allocation vs contention) and the baseline is measured the same way as the verification.
- Findings cite frames and shares from an actual profile, not intuition; expected gain is bounded by the frame's share.
- One change per iteration, verified by a repeat measurement with variance considered.
- Production profiling uses low-overhead tools and respects data sensitivity.
- The fix class is named (wasted work / algorithmic / allocation / concurrency / IO / config).

## Anti-patterns to avoid

- Micro-optimizing a frame that is 2% of samples.
- Profiling a cold process, a debug build, or a different workload than production.
- Reading the flame graph x-axis as time order.
- Tuning the GC before reducing allocation.
- Changing several things and attributing the win to the favorite one.
- Benchmarking in a loop that the JIT or compiler eliminates, or on a noisy shared laptop.
