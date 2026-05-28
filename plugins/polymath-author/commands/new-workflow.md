---
name: new-workflow
description: Scaffold a new flows-lite workflow via the bundled new-workflow.sh.
---

# /new-workflow

Scaffold a new flows-lite workflow via `${CLAUDE_PLUGIN_ROOT}/bin/new-workflow.sh <workflow-name> [target-plugin]`. Defaults to placing the workflow under `polymath-flows/workflows/`. The scaffolder uses the bundled `templates/Workflow.yaml` first, falling back to the legacy `tools/scaffolder-templates/Workflow.yaml` for in-tree usage. After scaffolding, run `${CLAUDE_PLUGIN_ROOT}/../polymath-flows/bin/polymath-flow validate <path>` on the new workflow.
