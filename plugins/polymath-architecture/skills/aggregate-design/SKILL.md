---
name: aggregate-design
description: Design DDD tactical aggregates for a bounded context — aggregate roots, entities vs value objects, invariants, transaction/consistency boundaries, reference-by-id.
---

# aggregate-design

> An aggregate is a consistency boundary, not a data model. Get the invariants right and the boundaries fall out; get them wrong and you fight the database forever.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- You have a bounded context (see `bounded-context-map`) and need its internal object model.
- Transactions are touching too many rows, or two requests keep corrupting the same invariant.
- A workflow invokes `polymath-architecture:aggregate-design`.

Not this when: you are choosing cross-node consistency (eventual vs strong across services) — that is `distributed-consistency`. For the persistence DDL, hand off to `polymath-backend:db-schema`.

## Inputs

- The bounded context and its core business rules ("a refund can't exceed the captured amount").
- Known concurrency hotspots.

## Procedure

1. **List the true invariants** — rules that must hold at every commit. Each invariant must live inside exactly one aggregate; that is what defines the boundary.
2. **Classify each concept**: *entity* (has identity + lifecycle), *value object* (defined wholly by its attributes, immutable — prefer these), *domain event* (something that happened).
3. **Pick the aggregate root** — the single entity that guards the invariant and is the only entry point. Outside code references the root, never its internals.
4. **Set the boundary**: include only what must be transactionally consistent. Keep aggregates *small* — a large aggregate serializes unrelated writes.
5. **Reference other aggregates by id, not by object.** Crossing an aggregate boundary in one transaction is the most common design smell — flag it.
6. **Decide cross-aggregate consistency**: between aggregates use *eventual* consistency via domain events, not a bigger transaction. Name the event and who reacts.
7. **Check concurrency**: each aggregate gets an optimistic-concurrency version. Two writers to one aggregate is a real conflict; to two aggregates is not.

## Output

```text
Aggregate model: Refunds context

Refund (root)                     invariant: Σ refunds ≤ captured amount of the payment
  RefundLine        entity        (identity: line id; lifecycle: requested → issued → settled)
  Money             value object  (amount, currency) — immutable
  references Payment by id (PaymentId), never by object
  version: optimistic concurrency column `version`

Payment (root, Payments context)  invariant: captured ≤ authorized
  emits PaymentCaptured → Refunds caches capturedAmount per PaymentId

Domain events
  RefundIssued(refundId, paymentId, amount) → Ledger posts the reversal (eventual)

Invariants spanning two aggregates (rethink):
  - "a refund cannot exceed the *remaining* capture" needs Payment + all Refunds → keep a
    RefundAllowance on Refund, fed by PaymentCaptured / RefundIssued, not a two-aggregate transaction.
```

Inline by default; when a workflow step or the user wants it kept, write it to `docs/architecture/<slug>-aggregates.md` (slug from the system or context name, lowercased, non-`a-z0-9` runs → `-`).

## Quality bar

- Every invariant is owned by exactly one aggregate.
- No transaction modifies more than one aggregate; cross-aggregate effects are domain events.
- Value objects are preferred over entities wherever identity does not matter.
- Aggregates are small — a god-aggregate that owns half the context is the failure mode.
