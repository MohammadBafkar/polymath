# Changelog — polymath-tracker

<!-- markdownlint-disable MD024 -->

## [0.8.0]

Issue-tracker connector: Jira + Linear MCP + ticket-key detection (PROJ-123 / TEAM-123 / browse URLs); triage + provider-agnostic file-bug-from-incident.

### Skills

- **file-bug-from-incident** — File tracker bug tickets from a postmortem's action items — one per action, severity/priority mapped from incident sev, postmortem updated with the keys. Provider-agnostic (Jira or Linear).
- **jira-triage** — Triage a Jira issue — fetch via MCP, classify type/priority/component, ask for missing repro, transition state, route owner. Jira only — not other trackers.
- **linear-triage** — Triage a Linear issue — classify type/priority/state, ask for missing repro, transition through the workflow state machine, route to the right team. Linear only — not other trackers.

### Integrations

- Ships a Model Context Protocol (MCP) connector. The server definition is portable; configure credentials and client registration per host.
