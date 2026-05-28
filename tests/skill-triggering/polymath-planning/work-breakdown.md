---
plugin: polymath-planning
skill: work-breakdown
trigger_prompts:
  - "break this feature down into PR-sized chunks"
  - "decompose this epic into leaf tasks"
  - "I have a 6-week initiative; help me carve it into bite-sized work items"
must_invoke:
  - polymath-planning:work-breakdown
allow_invoke:
  - polymath-planning:estimate
  - polymath-thinking:*
  - polymath-core:*
---

# Why this test exists

"Work breakdown" and "decompose into PR-sized chunks" are the canonical
phrasings. The third is more idiomatic ("carve into bite-sized work
items") and catches descriptions that depend too heavily on the literal
"work breakdown" phrase.
