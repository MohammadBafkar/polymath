---
plugin: polymath-thinking
skill: red-team
trigger_prompts:
  - "red-team this PRD — what are the strongest objections the proposer hasn't refuted?"
  - "adversarially challenge this plan; I want the case against, not endorsement"
  - "be the harshest critic of this design and list every objection"
must_invoke:
  - polymath-thinking:red-team
allow_invoke:
  - polymath-thinking:pre-mortem
  - polymath-thinking:*
  - polymath-core:*
---

# Why this test exists

Red-team prompts vary widely. The three above span explicit (uses
"red-team"), domain ("adversarially challenge"), and colloquial
("harshest critic") phrasings. Triggering on all three is the bar.
