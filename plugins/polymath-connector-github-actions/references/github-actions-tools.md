# GitHub Actions MCP tools (reference)

Workflow tools live on the same `@modelcontextprotocol/server-github` MCP
server shipped by `polymath-connector-github`. Installing this plugin gives
you focused skills + a Stop hook on top of that server.

## Tools exposed (subset relevant to Actions)

- `list_workflow_runs` — filter by branch, status, event, conclusion.
- `get_workflow_run` — single run details + the `logs_url`.
- `list_workflow_jobs` — jobs in a run, status per job.
- `get_workflow_run_logs` — raw logs (where supported by the upstream server).
- `list_workflows` — workflows defined in a repo.
- `dispatch_workflow` — trigger a `workflow_dispatch` workflow with inputs.
- `rerun_workflow_run` — re-run failed jobs.
- `cancel_workflow_run` — abort a running workflow.

## Token scopes

Same PAT as `polymath-connector-github`. Add:

- `workflows: read+write` for dispatch + rerun.
- `actions: read` for log access.

If the same PAT serves both connectors, set it once via `polymath-connector-github`'s `userConfig.githubToken`.
