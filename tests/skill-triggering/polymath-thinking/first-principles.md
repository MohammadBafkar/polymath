---
plugin: polymath-thinking
skill: first-principles
trigger_prompts:
  - "let's reason about this from first principles instead of how it's usually done"
  - "strip this problem down to fundamentals and rebuild the approach"
  - "everyone assumes this cost is fixed — is it actually, or just convention"
must_invoke:
  - polymath-thinking:first-principles
allow_invoke:
  - polymath-thinking:*
  - polymath-core:*
forbidden_prompts:
  - "brainstorm ten ideas for the landing page"
  - "frame the problem we're solving before we start"
---

# Why this test exists

First-principles / fundamentals / question-the-assumption phrasings route here.
Forbidden prompts guard against `brainstorm` and `problem-framing`.
