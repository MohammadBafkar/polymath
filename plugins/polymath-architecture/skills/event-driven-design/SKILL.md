---
name: event-driven-design
description: Design an event-driven flow — event catalog, choreography vs orchestration, saga + compensation, the outbox pattern for dual-writes, idempotent consumers, and CQRS read models.
---

# event-driven-design

> Events decouple services in space and time — and move every hard problem to delivery semantics. Design the failure paths first; the happy path is the easy 10%.

## When to use

- A business process spans services and you are choosing between synchronous calls and events.
- A write must update the database *and* publish a message and you are about to do both in one block (the dual-write trap).
- A workflow invokes `polymath-architecture:event-driven-design`.

Not this when: the integration is two services and request/response is fine — that is `integration-design`. For the broker's partitioning/throughput tuning, that is `polymath-streaming:streaming-design`.

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

- A one-page design: event catalog (name, owner, schema, version rule), the choreography/orchestration decision, a saga table (step → compensation), the outbox + idempotency mechanism, and the ordering/partitioning key.

## Quality bar

- No dual-write survives — every publish is outbox-backed or explicitly justified.
- Every saga step has a compensating action or a documented "cannot fail here" reason.
- Consumers are idempotent and tolerate reordering; the dedup key is named.
- Events are business facts, not table change-logs.
