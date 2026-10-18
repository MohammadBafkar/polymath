# Changelog — polymath-core

<!-- markdownlint-disable MD024 -->

## [0.9.0]

### Skills

- **mcp-bridge** — Detect MCP servers already registered in the CURRENT host agent (Claude Code, Cursor, Gemini CLI, OpenCode, Codex, VS Code) and reuse them for Polymath connectors instead of installing duplicates; scan/match/render/doctor via the bundled `mcp-registry` script. Host-only: a server registered in a different agent is never a substitute.

### Hooks

- **SessionStart** now runs `build-mcp-resolution.py` after project-context load: detects the current host from in-session env markers, scans ONLY that host's MCP config (`tools/mcp-registry.py` + the `.polymath/project.yaml` `mcp:` policy), resolves every kind=mcp binding's provider, and persists `mcpResolution` into `project-context.json`; surfaces a one-line note only when the current host's server is reused. Skills bind via the snapshot (`source: host | plugin | none`, `toolPrefix` per host). Undetectable host → plugin fallback everywhere, never another host's server.
- Fixed a pre-existing bash syntax error in `session-start.sh` (apostrophe inside a heredoc body within `$( )` unterminated quote scanning — the hook had been failing to parse since 0.8.0).

### Schemas

- `project.schema.json` gains the `mcp:` block: `policy` (`reuse-host` default / `prefer-plugin`), `serverOverrides` (per-provider pin or `plugin`).

## [0.8.0]

Foundation: route prompts, load conventions/project context, report plugin budgets, and run SessionStart hooks.

### Skills

- **conventions** — Read Polymath project conventions (commit style, PR shape, plugin layout) when starting a task that touches the marketplace.
- **doctor** — Check the Polymath environment — required and optional tools, and validate any .polymath/project.yaml — reporting PASS/WARN/FAIL and fix hints.
- **glossary** — Define shared vocabulary for Polymath plugins (PRD, ADR, RFC, mustPass, flows-lite); use when terms need disambiguating.
- **initialize-project** — Map a repository to .polymath/project.yaml — capability mapping and onboarding notes for Polymath-aware agents.
- **project-context** — Read .polymath/project.yaml — language, framework, conventions, external skills, skill overrides — so a skill can adapt to this project instead of giving generic guidance.
- **route** — Choose the right Polymath workflow, skill, connector, agent, or external catalog for a user prompt; returns JSON with confidence, evidence, and alternatives.

### Commands

- **/doctor** — Run the doctor preflight on your Polymath environment before first init or when it misbehaves; alias for polymath-core:doctor.
- **/init-project** — Run the initialize-project skill from the CLI to bootstrap a repo's Polymath setup in one command.
- **/plugin-budget** — List current Polymath always-on listing-token cost per plugin and totals; flags overruns vs the ≤400/plugin and ≤1,500 MVP targets.
- **/route** — Run a Router Report before work starts; command entry point for the selector, not the canonical routing procedure.
