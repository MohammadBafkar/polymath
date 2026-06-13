---
name: aggregate-design
description: Design DDD tactical aggregates for a bounded context — aggregate roots, entities vs value objects, invariants, transaction/consistency boundaries, reference-by-id.
---

# aggregate-design

> An aggregate is a consistency boundary, not a data model. Get the invariants right and the boundaries fall out; get them wrong and you fight the database forever.

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

- A one-page aggregate model: aggregates with their roots, the invariant each enforces, entities vs value objects, by-id references, and the domain events that connect them.
- A flagged list of any invariant spanning two aggregates (a boundary that needs rethinking).

## Quality bar

- Every invariant is owned by exactly one aggregate.
- No transaction modifies more than one aggregate; cross-aggregate effects are domain events.
- Value objects are preferred over entities wherever identity does not matter.
- Aggregates are small — a god-aggregate that owns half the context is the failure mode.
