---
plugin: polymath-product
skill: prd
trigger_prompts:
  - "draft a PRD for rate-limiting /login"
  - "we need a product requirements doc for the new refund flow"
  - "write a one-pager PRD covering goals, acceptance criteria, and rollout for the dashboard redesign"
must_invoke:
  - polymath-product:prd
allow_invoke:
  - polymath-thinking:*
  - polymath-core:*
---

# Why this test exists

A "PRD"/"product spec" request is the canonical trigger for
polymath-product:prd. If the skill's `description:` ever drifts away
from those phrases, this test catches it before the user does.
