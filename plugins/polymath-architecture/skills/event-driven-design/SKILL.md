---
name: event-driven-design
description: Design an event-driven flow — event catalog, choreography vs orchestration, saga + compensation, the outbox pattern for dual-writes, idempotent consumers, and CQRS read models.
---

# event-driven-design

> Events decouple services in space and time — and move every hard problem to delivery semantics. Design the failure paths first; the happy path is the easy 10%.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A business process spans services and you are choosing between synchronous calls and events.
- A write must update the database *and* publish a message and you are about to do both in one block (the dual-write trap).
- A workflow invokes `polymath-architecture:event-driven-design`.

Not this when: the integration is two services and request/response is fine — that is `integration-design`. For the broker's partitioning/throughput tuning, that is `polymath-streaming:streaming-design`.
For event schema compatibility and versioning, `polymath-streaming:event-schema-evolution`; for worker/queue sizing, retries, and DLQs, `polymath-scalability:async-workload-design`.

## Inputs

- The end-to-end process and its steps, with which service owns each.
- Consistency and ordering requirements; what "must never happen".

## Procedure

1. **Catalog the events** — past-tense, business-meaningful (`OrderPlaced`, `PaymentCaptured`), not CRUD (`OrderRowUpdated`). Each has an owner, a schema, and a versioning rule.
2. **Choreography vs orchestration**: choreography (services react to events) for loose, simple flows; orchestration (a coordinator/saga drives steps) when the process is long, needs status, or has complex compensation. State the choice and why.
3. **Design the saga** for any multi-step process that can fail midway: list each step and its *compensating action* (refund, release, cancel). There is no distributed rollback — only compensation.
4. **Kill the dual-write** with the *transactional outbox*: write the event to an outbox table in the same DB transaction as the state change; a relay publishes it. Never write DB + broker in two separate commits.
5. **Make consumers idempotent**: dedupe on event id / idempotency key; assume at-least-once delivery and out-of-order arrival. Define what a duplicate must do (nothing).
6. **Decide ordering**: if order matters, partition by aggregate id so one entity's events are serialized; do not assume global ordering.
7. **(CQRS)** if reads and writes diverge sharply, derive a read model from the events and state its staleness budget and rebuild path.
8. **Name the observability**: a correlation id threaded through every event so a flow can be traced end to end.

## Output

```text
Event-driven design: order fulfillment

Events (past tense · owner · schema · version rule)
  OrderPlaced        Ordering    orders.v3    additive-only; breaking → OrderPlaced.v4 dual-published 90 d
  PaymentCaptured    Payments    payments.v2  additive-only
  ShipmentCreated    Fulfillment fulfil.v1    additive-only

Coordination: orchestration — a fulfillment saga (needs status + multi-step compensation)

Saga
  step                 compensation
  reserve stock        release stock
  capture payment      refund payment
  create shipment      cancel shipment (cannot fail after carrier pickup → manual review queue)

Dual-write: transactional outbox in each service DB; Debezium relay → Kafka
Idempotency: consumers dedupe on event_id (processed_events table, 7 d)
Ordering: partition key = order_id (one order's events in order; no global order assumed)
Correlation: correlation_id on every event, propagated to traces
```

Inline by default; when a workflow step or the user wants it kept, write it to `docs/architecture/<slug>-events.md` (slug from the system or context name, lowercased, non-`a-z0-9` runs → `-`).

## Quality bar

- No dual-write survives — every publish is outbox-backed or explicitly justified.
- Every saga step has a compensating action or a documented "cannot fail here" reason.
- Consumers are idempotent and tolerate reordering; the dedup key is named.
- Events are business facts, not table change-logs.
