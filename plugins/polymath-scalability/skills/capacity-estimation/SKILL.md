---
name: capacity-estimation
description: Do back-of-envelope sizing — QPS, bandwidth, storage, cache load, node count — via a script. Not a growth forecast (capacity-plan).
---

# capacity-estimation

> Before arguing about architecture, size the problem. Order-of-magnitude numbers — with the assumptions written down — decide whether you need one box, a cache, a queue, or a shard.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Starting a system design and needing QPS, bandwidth, and storage to pick components (`polymath-scalability:system-design`).
- Checking whether a proposal's scale claims are plausible, or what "10× growth" means in machines and dollars.
- Turning a product number (users, events/day) into engineering numbers.

Not this when: you have utilization history and need a date to act — that is `polymath-sre:capacity-plan` (and `demand-forecast` for seasonality). This skill sizes a *design*; those skills project a *running system*.

## Inputs

- Users or event volume (DAU, devices, events/day), actions per user per day, read/write ratio.
- Payload sizes (bytes per read, per stored write), retention, replication factor.
- Peak-to-average factor (default 3 if unknown — mark it an assumption; diurnal consumer traffic is often 2–5×, event-driven spikes more), cache hit ratio if a cache is planned, and per-node throughput *if measured*.

Anything not provided is an assumption: label it `[VERIFY]` with the source of the guess. Never present a per-node throughput as fact without a benchmark or vendor number cited.

## Procedure

1. **Write the assumptions as a table** before computing: each input, its value, and where it came from (product forecast, existing metric, industry rule of thumb, guess). Guesses get a range, and you compute the low and high case.
2. **Run the calculator — never multiply by hand.** It applies one fixed set of formulas, so two runs on the same inputs agree:

   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/capacity-estimation/scripts/estimate.py" \
     --dau 5000000 --actions-per-user-day 20 --read-ratio 0.9 --peak-factor 3 \
     --read-bytes 5000 --write-bytes 2000 --retention-days 365 --replication 3 \
     --cache-hit 0.8 --per-node-qps 2000 --target-util 0.6
   ```

   Exit 2 means bad input; fix it rather than guessing a value. Run it once per scenario (low / expected / high).
3. **Interpret in terms of components** (the point of the exercise):
   - **Peak QPS and read/write split** → one primary can do roughly thousands of simple indexed ops/s; tens of thousands of writes/s or a read-heavy skew points to replicas, caching, or partitioning (`polymath-database:db-scaling-strategy`). Use measured numbers for the engine, not folklore.
   - **Origin QPS after cache** → whether the cache is mandatory or merely helpful; a hit-ratio assumption this large needs evidence (`polymath-performance:caching-tradeoffs`).
   - **Bandwidth** → compare egress to a single NIC and to CDN need (`polymath-performance:http-edge-caching`); fan-out multiplies it.
   - **Storage × retention × replication** → single node or distributed store; tiering and archival (`polymath-database:data-retention-archiving`); add indexes (often 30–100% on top of data) and backup copies, which the script does not include.
   - **Node count** with the stated utilization target and N+1 → a floor for the fleet, before zonal redundancy (×1.5 for N+1 across 3 zones is a common check; state it).
4. **Sanity-check against a known reference**: compare to an existing system's real throughput, or cross-check with a second derivation (e.g. bytes/day ÷ 86,400 against the network figure). If the answer is off by 10×, an assumption is wrong — find it.
5. **Name the dominant uncertainty** — the one input whose range changes the architecture — and what measurement would resolve it (a load test: `polymath-test-automation:load-test`).
6. **State the decisions the numbers support or kill**, in one line each ("single Postgres primary is enough for writes; reads need a cache; storage needs tiering after year 2").

## Output

```text
Capacity estimate: feed service

Assumptions
  dau 5 M            product forecast (launch plan)           range 3–8 M
  20 actions/user/d  existing app analytics [VERIFY: web ≠ mobile]
  read ratio 0.9     assumption — similar products
  peak factor 3      assumption (no peak data yet)
  read 5 KB / write 2 KB, retain 365 d, ×3 replication, cache hit 0.8 [VERIFY: needs measurement]

(calculator output)
Requests:  100.00M/day → avg 1,157 QPS → peak 3,472 QPS
           reads 3,125/s · writes 347/s
Origin:    972 QPS reach the data tier (625 read misses + 347 writes)
Network:   ingress 0.69 MB/s (5.6 Mbit/s) · egress 15.62 MB/s (125.0 Mbit/s)
Storage:   10.00M writes/day → 21.90 TB over 365 d at ×3 replication
Nodes:     ceil(3,472 ÷ (2000 × 0.6)) + 1 (N+1) = 4

Reading
  Writes (347/s) fit a single primary; reads need a cache (3,125 → 625/s at hit 0.8 — if hit ratio is 0.5 origin is 1,910 QPS).
  Egress 125 Mbit/s is trivial for the fleet but argues for a CDN on media later.
  Storage 21.9 TB incl. replication: needs a partitioned/tiered store by year 2; indexes and backups come on top [TBD: index overhead].
Dominant uncertainty: cache hit ratio (changes origin load 3×) → measure with a replay of production keys.
Decisions supported: primary + 2 replicas + cache; no sharding at this scale. Revisit if DAU > 8 M or actions/user > 40.
```

## Quality bar

- Every number comes from the calculator or from a stated input; no hand arithmetic.
- Assumptions are listed with their source and a range; guesses are marked `[VERIFY]`.
- The output ends in architectural decisions, not just numbers, and names the one uncertainty that matters most.
- Peak, not average, drives the sizing; replication, retention, and N+1 are included.
- Results are cross-checked against a reference or a second derivation.

## Anti-patterns to avoid

- Sizing for average load, or applying a made-up peak factor without saying so.
- Quoting per-node throughput from memory instead of a benchmark or vendor figure.
- Forgetting write amplification: indexes, replication, backups, and derived copies.
- False precision — "3,472 QPS" from a guessed DAU; round the conclusion, keep the range.
- Treating the estimate as a forecast of a running system (use `polymath-sre:capacity-plan`).
