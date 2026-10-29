---
name: async-workload-design
description: Design async and background processing — queue vs stream, worker sizing, idempotency, retries and DLQ, backpressure, priority lanes.
---

# async-workload-design

> Anything the user doesn't wait for should leave the request path — but a queue only moves the failure. Design bounded depth, idempotent workers, and what happens when work arrives faster than it drains.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Offloading slow or bursty work (emails, exports, media processing, webhooks, ML jobs, third-party calls) from the request path.
- Workers fall behind, queues grow without bound, jobs run twice, or one noisy tenant starves others.
- Choosing between a task queue, a message broker, and an event stream for a workload.

Not this when: you are designing the broker topology of a high-volume event stream — `polymath-streaming:streaming-design`; or the *business* saga/choreography — `polymath-architecture:event-driven-design`.

## Inputs

- The work: what it does, duration distribution (p50/p99), CPU/IO/memory profile, side effects, and whether the caller needs a result.
- Arrival pattern: steady rate, burst size and duration, and the latency target to completion (seconds? hours?).
- Failure characteristics: transient vs permanent errors, downstream rate limits, idempotency of the work, ordering needs.
- Platform: available queue/broker (SQS, RabbitMQ, Service Bus, Kafka/Event Hubs, Celery/Sidekiq/Temporal), runtime, deployment/autoscaling.

## Procedure

1. **Decide whether to go async at all.** Async is right when the result isn't needed in the response, the work is slow/bursty/unreliable, or it must survive a restart. If the user needs the answer, keep it synchronous or return `202` + a status resource/callback and say how the client learns the outcome.
2. **Pick the primitive:**
   - **Task queue / work queue** (SQS, RabbitMQ, Service Bus queue): each message processed by one worker; no replay; per-message ack and retry. For independent jobs.
   - **Event stream / log** (Kafka, Event Hubs, Kinesis): many consumers, replay, ordering per key, retention. For facts consumed by multiple parties or needing reprocessing.
   - **Workflow engine** (Temporal, Step Functions, Durable Functions): long-running, multi-step, compensations, timers — don't hand-roll state machines in queue handlers.
   - **Scheduler / cron**: time-based; guard against overlap and missed runs (leader lock or idempotent job keyed by schedule slot).
3. **Make the message and the worker safe to repeat.** Delivery is at-least-once. Define an idempotency key per unit of work and dedupe at the side-effecting boundary (unique constraint, conditional write, provider idempotency key). Enqueue from the database transaction via an outbox so work isn't lost or enqueued for a rolled-back change. Keep messages small (ids, not payloads) so workers read fresh state.
4. **Retries, backoff, and the DLQ.** Classify errors: transient (retry with exponential backoff + jitter, capped attempts), permanent (don't retry — dead-letter immediately), poison (crashes the worker — dead-letter after N). Set visibility timeout/lease longer than p99 job time (plus heartbeat for long jobs) or work gets processed twice concurrently. A DLQ needs an alert, an owner, inspect/redrive tooling, and a retention longer than the alert-to-fix time.
5. **Size workers with Little's law.** In-flight work L = arrival rate λ × time in system W. Workers needed ≈ λ × service time ÷ target utilization (use `polymath-performance:high-load-io-design`'s calculator). Size for the burst you must absorb within the completion target, otherwise accept a queue and compute the drain time (backlog ÷ (capacity − λ)). If capacity ≤ arrival rate, the queue grows forever — no tuning fixes that.
6. **Bound everything (backpressure).** Cap queue depth or age; decide the overflow policy explicitly: block/slow the producer, reject with `429`/`503` + `Retry-After`, drop lowest priority, or spill to durable storage. Cap per-worker concurrency to what the downstream tolerates; use a token bucket for third-party rate limits (`polymath-scalability:rate-limiting-design`). Unbounded queues turn an overload into a delayed, bigger one.
7. **Isolate and prioritize.** Separate queues (and worker pools) per priority and per workload class so bulk jobs can't starve interactive ones; per-tenant fairness (weighted fair queuing, per-tenant concurrency caps, or sharded queues) so one customer's import doesn't block everyone. Don't implement priority by sorting inside one queue unless the broker supports it.
8. **Ordering.** Needed only per entity: partition/group by entity id (FIFO message groups, Kafka key) and accept lower parallelism per key. Global ordering doesn't scale; redesign to make operations commutative or versioned (last-write-wins by version, not arrival order).
9. **Autoscale on the right signal.** Queue depth or age (or lag per worker), not CPU — an IO-bound worker is idle at CPU 5% while the queue explodes. Scale-in must drain gracefully (stop pulling, finish in-flight, extend lease); set a floor for burst readiness and a ceiling matching downstream capacity.
10. **Observe and operate.** Metrics: queue depth, oldest-message age (the SLO metric), processing time, success/retry/DLQ rates, in-flight, redelivery count. Trace context carried in the message. Runbooks for DLQ redrive, pausing a queue, and replay; test the redrive path.
11. **Design the result path** for work with outcomes: status resource, webhook with signature + retries, or events; define expiry of results.

## Output

```text
Async design: report export

Decision: async — exports take p50 40 s / p99 6 min; user gets 202 + GET /exports/{id}; email + webhook on completion.
Primitive: task queue (SQS) + worker pool; long steps → Temporal workflow not needed (single stage) [VERIFY: if multi-stage PDF merge is added].
Enqueue: outbox in the orders DB → relay → SQS (message = {export_id}); worker loads state.
Idempotency: exports.id unique; worker conditional update status=queued→running; file key = export_id (overwrite-safe).
Retries: visibility timeout 15 min (p99 6 min + margin) + heartbeat; transient errors retry 5× backoff 30 s × 2ⁿ jittered; permanent (bad filter) → DLQ now; DLQ alarm on depth > 0; redrive tool in runbook.
Sizing: λ = 2/s peak, service 40 s mean → L = 80 in flight; target util 0.7 → 115 workers at burst; steady 15 min drain budget → [TBD: cost vs fewer workers + longer drain].
Backpressure: depth cap 5,000 → API returns 429 + Retry-After 60; per-tenant limit 3 concurrent exports.
Isolation: queues exports-interactive / exports-bulk (scheduled), separate pools; fair share via per-tenant cap.
Ordering: none required (exports independent).
Autoscaling: scale on ApproximateAgeOfOldestMessage > 120 s (not CPU); scale-in drains in-flight; max 150 (DB replica read limit).
SLO: 95% of exports complete < 5 min; alert on oldest-message age > 10 min.
Result: GET status; webhook signed (HMAC) with retries; result URL expires 7 d.
```

## Quality bar

- At-least-once delivery is handled: each worker's side effects are idempotent with a named key.
- Queue depth/age is bounded, with an explicit overflow policy and a backpressure signal to producers.
- Worker count follows from arrival rate × service time and a utilization target (or says the queue never drains).
- Priority and tenant isolation exist where mixed workloads share workers; DLQ has an owner, alert, and redrive path.
- Autoscaling uses queue age/depth; scale-in is graceful.

## Anti-patterns to avoid

- Unbounded queues "to absorb spikes" with no drain plan or age alert.
- Enqueue after DB commit without an outbox (lost jobs) or before commit (ghost jobs).
- One shared queue for interactive and bulk work; one tenant starving the rest.
- Visibility timeout shorter than the job — duplicates running concurrently.
- Retrying permanent errors forever; retry without jitter; no DLQ alert.
- Autoscaling IO-bound workers on CPU.
