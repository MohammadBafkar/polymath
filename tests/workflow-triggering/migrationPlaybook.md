---
workflow: migrationPlaybook
trigger_prompts:
  - "plan the migration off the old system"
  - "strangler-fig migration playbook"
  - "migrate consumers to the new service safely"
  - "phased migration plan and rollout"
must_propose:
  - migrationPlaybook
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `migrationPlaybook` workflow via the detect → propose contract (run-workflow/SKILL.md). It assesses seams + a strangler sequence, plans the phases, writes the consumer migration guide, then rolls out gated by usage.
