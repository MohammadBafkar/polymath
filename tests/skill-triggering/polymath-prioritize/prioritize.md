---
plugin: polymath-prioritize
skill: prioritize
trigger_prompts:
  - "rank this backlog and tell me what to build first"
  - "help me prioritize these features — we can't do them all this quarter"
  - "should we do A or B first, and why"
must_invoke:
  - polymath-prioritize:prioritize
allow_invoke:
  - polymath-planning:*
  - polymath-product:*
  - polymath-thinking:*
  - polymath-core:*
forbidden_prompts:
  - "estimate how long this feature will take"
  - "break this epic into user stories"
---

# Why this test exists

"Rank / prioritize / what first" are the canonical phrasings. The third
("A or B first, and why") is the idiomatic gut-feel ask that should still
route here. The forbidden prompts guard the boundary against
`polymath-planning:estimate` (sizing, not ranking) and
`polymath-product:decompose-epic` (slicing, not ranking).
