---
plugin: polymath-engineering
skill: code-review
trigger_prompts:
  - "review this diff for correctness and missing tests"
  - "code-review the current branch and flag anything missing"
  - "look at this change and tell me what's wrong, what's missing, what's over-built"
must_invoke:
  - polymath-engineering:code-review
allow_invoke:
  - polymath-engineering:read-code
  - polymath-engineering:verify-change
  - polymath-thinking:*
  - polymath-core:*
---

# Why this test exists

Code review is the highest-volume skill invocation. The triggers above
are deliberately phrased without the literal word "review" in one case
to catch over-fitting to the skill name.
