---
plugin: polymath-core
skill: route
trigger_prompts:
  - "Given this prompt and repo context, tell me which Polymath workflow or skill should handle it before doing any work."
  - "Route this request to the right Polymath surface: review this PR for correctness, security, and missing tests."
  - "Which Polymath plugin, skill, connector, or workflow should I use for a vague architecture decision?"
must_invoke:
  - polymath-core:route
allow_invoke:
  - polymath-core:*
  - polymath-flows:*
---

# Why this test exists

Routing prompts do not ask for the underlying work yet. They ask the
agent to choose the right Polymath surface, expose confidence, and ask
when the signal is ambiguous instead of silently loading a sibling skill.
