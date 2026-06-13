---
plugin: polymath-ai
scenario: agent-design-support-triage
expect:
  invoked:
    - polymath-ai:agent-design
  output_matches:
    - "(ReAct|plan-execute|plan-and-execute|control)"
    - "(stop condition|max steps|budget)"
    - "(tool contract|side-effect|read-only|confirm)"
  not_invoked:
    - polymath-ai:prompt-engineer
timeout_seconds: 120
---

# Prompt

> Design an agent that triages support tickets: it can search our
> knowledge base, look up the customer's orders, and either draft a
> reply or escalate. It keeps looping and sometimes issues refunds it
> shouldn't.

Use polymath-ai:agent-design.

# Acceptance

- A control pattern is chosen with a reason (ReAct or plan-execute fits multi-step tool use).
- Explicit stop conditions (max steps, token/cost budget, no-progress) are defined — the infinite loop is addressed.
- The tool contract marks side-effect class; the refund (mutating/irreversible) requires confirmation, not model-only authorization.
- Memory/context-budget plan and failure-recovery paths are included.
