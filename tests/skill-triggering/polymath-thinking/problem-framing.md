---
plugin: polymath-thinking
skill: problem-framing
trigger_prompts:
  - "before we build this, are we even solving the right problem"
  - "help me frame the actual problem here, not jump to a solution"
  - "what problem are we really trying to solve for whom"
must_invoke:
  - polymath-thinking:problem-framing
allow_invoke:
  - polymath-thinking:*
  - polymath-research:*
  - polymath-product:*
  - polymath-core:*
forbidden_prompts:
  - "brainstorm a bunch of solution ideas for this"
  - "run a 5-whys on last night's outage"
---

# Why this test exists

Problem-before-solution phrasings route here. Forbidden prompts guard against
`brainstorm` (options) and `5-whys` (incident root-cause).
