---
name: design-patterns-apply
description: Review a design sketch against SOLID, GoF, and architectural patterns; flag anti-patterns at design time; not line-level code review (code-review).
---

# design-patterns-apply

> Patterns are a vocabulary for trade-offs, not a checklist to maximize. The skill is choosing the one that removes the most pain — and refusing the ones that only add indirection.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A design sketch or module structure needs a second pass: which pattern fits, what's over-engineered, where SOLID is being violated.
- A class/module is hard to test or change and you suspect a structural cause.
- A workflow invokes `polymath-architecture:design-patterns-apply`.

Not this when: you are reviewing a concrete diff for bugs and line-level quality — that is `polymath-engineering:code-review`. This skill works at design time on structure, before/around the code.

## Inputs

- The design sketch, class/module responsibilities, and the change or pain that prompted the review.

## Procedure

1. **Check SOLID at the seams** — most value, least ceremony:
   - *SRP* — one reason to change per module; a class touched by every feature is the smell.
   - *OCP* — extend without editing; if every new case edits a switch, consider strategy/polymorphism.
   - *LSP* — subtypes honor the base contract (no "throws NotSupported").
   - *ISP* — clients depend only on what they use; split fat interfaces.
   - *DIP* — depend on abstractions; the domain should not import infrastructure.
2. **Name the pain precisely** (rigid? duplicated? hard to test? shotgun-surgery?) — the pain selects the pattern, not the reverse.
3. **Select a pattern only if it removes that pain**:
   - *Creational* (factory, builder) — when construction is complex or varies.
   - *Structural* (adapter, facade, decorator) — when integrating, simplifying a surface, or layering behavior.
   - *Behavioral* (strategy, observer, state, command) — when behavior varies or must be swapped/queued/observed.
4. **Reject over-engineering**: a pattern that adds an interface with one implementation, speculative generality, or indirection without a current need. Recommend the simpler shape.
5. **Flag anti-patterns**: god object, anemic domain model, circular dependencies, leaky abstraction, primitive obsession, service locator hiding dependencies.
6. **State the trade-off** of each recommendation: what it buys, what it costs in indirection/complexity. Hand a genuinely contested choice to `polymath-decisions:tradeoff-matrix`.

## Output

```text
Design review: notification module

Pain: every new channel edits NotificationService.send() (a 9-branch switch) — shotgun surgery.

SOLID
  OCP  NotificationService.send()           — switch on channel → Strategy per channel
  DIP  notifications/domain imports twilio  — domain depends on infrastructure → port + adapter
  SRP  ok · LSP ok · ISP ok

Recommend
  Strategy (ChannelSender per channel)  removes the switch · cost: one interface, 4 small classes
  Adapter (TwilioSmsSender)             isolates the vendor · cost: one indirection layer

Don't add
  Abstract factory for senders — one construction path today; a dict of senders is enough
  Observer bus — no second subscriber exists yet

Anti-patterns: god object NotificationService (templates + routing + sending) → split routing out
```

Inline by default; when a workflow step or the user wants it kept, write it to `docs/architecture/<slug>-patterns.md` (slug from the system or context name, lowercased, non-`a-z0-9` runs → `-`).

## Quality bar

- Every recommended pattern is justified by a named, present pain — no speculative patterns.
- At least one "don't add this" appears, or the design is genuinely minimal (say so).
- SOLID findings point at concrete modules, not generic advice.
- The recommendation stays at design level; line-level bugs are routed to code-review.
