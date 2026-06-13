---
workflow: dataPipelineBuild
trigger_prompts:
  - "build a data pipeline from"
  - "set up the etl into our warehouse"
  - "ingest this source into the lakehouse"
  - "design and build the pipeline and tables"
must_propose:
  - dataPipelineBuild
forbidden_prompts:
  - "format my markdown"
  - "what time is it"
---

Naive prompts that must surface the `dataPipelineBuild` workflow via the detect → propose contract (run-workflow/SKILL.md). It models the target tables, designs the idempotent pipeline, then verifies the load and data-quality gates.
