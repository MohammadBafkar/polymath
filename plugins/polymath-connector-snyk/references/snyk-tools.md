# Snyk MCP tools (reference)

Default server: `@snyk/mcp-server` (or any community server speaking the same tool shape).

Auth: `SNYK_TOKEN` + optional `SNYK_ORG` from `userConfig`.

## Tools exposed (subset)

### Read

- `list_projects` — Snyk projects in the org.
- `list_issues` — vulns / license / IaC findings, filterable by severity, project, identifier.
- `get_issue` — single finding with reachability + remediation info.
- `list_targets` — repos/images monitored.

### Write

- `test` — run a one-off scan (project must exist or be scannable from a path).
- `monitor` — register a target for ongoing monitoring.
- `ignore_issue` — add an `.snyk` policy entry (require expiration + reason).

## Token scope

- Project-scoped tokens preferred over account-wide.
- Rotate when triage staff change.
- For CI use, prefer Snyk's first-party service-account tokens.

## Anti-patterns

- Auto-ignoring criticals from the model.
- `snyk test` without an org context (results may map to the wrong org).
