---
name: new-workflow
description: Generate a new flows-lite workflow via the bundled new-workflow.sh; not a plugin or skill.
---

# /new-workflow

Scaffold a new flows-lite workflow via `${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/bin/new-workflow.sh <workflow-name> [target-plugin]`. Defaults to placing the workflow under `polymath-flows/workflows/`. The scaffolder uses the bundled `templates/Workflow.yaml` first, falling back to the legacy `tools/scaffolder-templates/Workflow.yaml` for in-tree usage. After scaffolding, run `polymath-flow validate <path>` on the new workflow (polymath-flows' `bin/` is on the shell `PATH` while that plugin is enabled; in a marketplace checkout use `plugins/polymath-flows/bin/polymath-flow`), then `tools/build-workflow-index.py` to refresh the routing index.
