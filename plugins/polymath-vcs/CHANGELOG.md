# Changelog — polymath-vcs

<!-- markdownlint-disable MD024 -->

## [0.9.0]

### Changed

- Skills now carry an MCP-binding preamble: the agent resolves which server backs github/vcs/ci from the SessionStart `mcpResolution` snapshot (host-registered server first, per the `reuse-host` policy) instead of assuming the plugin-shipped `.mcp.json` server. See `docs/MCP-REUSE.md`.

## [0.8.0]

Version-control integration: GitHub PR/issue/CI MCP + PR-URL detect + unpushed-commits nudge (GitLab/Azure DevOps/Bitbucket in the capability vocab).

### Skills

- **diagnose-ci-failure** — Diagnose a failed GitHub Actions run — fetch logs via MCP, identify the failing step, classify (flake / real / config), propose next action.
- **open-pr** — Open a GitHub PR via the github MCP server — push current branch, draft from polymath-release:pr template, set base, add reviewers, never force-push.
- **triage-issue** — Triage an inbound GitHub issue — label, severity, area, ask for missing repro details if needed, route to the right team. GitHub issues only — not other trackers.

### Integrations

- Ships a Model Context Protocol (MCP) connector. The server definition is portable; configure credentials and client registration per host.
