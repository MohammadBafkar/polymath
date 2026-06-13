---
workflow: evalDrivenDevelopment
trigger_prompts:
  - "build this llm feature eval-first"
  - "set up evals before we change the prompt"
  - "eval-driven development for this agent"
  - "define the eval suite then implement"
must_propose:
  - evalDrivenDevelopment
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `evalDrivenDevelopment` workflow via the detect → propose contract (run-workflow/SKILL.md). It defines the eval harness + regression set first, implements against it, then measures pass/fail before shipping.
