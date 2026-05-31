---
plugin: polymath-product
skill: groom-backlog
trigger_prompts:
  - "these backlog items are vague and huge — get them ready for sprint planning"
  - "groom the backlog before our refinement session"
  - "are these stories ready to pull, or do they need work"
must_invoke:
  - polymath-product:groom-backlog
allow_invoke:
  - polymath-product:*
  - polymath-planning:*
  - polymath-core:*
forbidden_prompts:
  - "rank these stories by value and effort"
  - "break this epic into a user story map"
---

# Why this test exists

Refinement / ready / DoR phrasings route here. Forbidden prompts guard
against `polymath-prioritize:prioritize` (ranking) and
`polymath-product:decompose-epic` (epic story-mapping).
