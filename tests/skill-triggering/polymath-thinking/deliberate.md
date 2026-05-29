---
plugin: polymath-thinking
skill: deliberate
trigger_prompts:
  - "Think through this architecture plan iteratively: inspect the context, reconsider options, trade off risks, and revise the recommendation."
  - "Review this implementation idea with an observe, options, critique, and consolidation loop before we commit."
  - "We have incomplete data. Explore alternatives, stress-test them, and produce a revised plan."
must_invoke:
  - polymath-thinking:deliberate
allow_invoke:
  - polymath-thinking:*
  - polymath-decisions:*
  - polymath-planning:*
  - polymath-core:*
---

# Why this test exists

The deliberation skill should trigger when the user asks for iterative
analysis and revision, even if they do not say "deliberate" or
"brainstorm".
