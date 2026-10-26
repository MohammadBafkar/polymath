# Changelog — polymath-core

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Changed

- `project-context`: resolution order is snapshot (only if `_meta.source` is this repo) → raw `.polymath/project.yaml` (+ local overlay) → defaults, so localization works on hosts without SessionStart and never applies another repo's context.
- `mcp-bridge`: tool list first; bundled `mcp-registry` `scan` everywhere, `match`/`render`/`doctor` only from a marketplace checkout — an installed copy's `0/0 provider(s)` is reported as "bindings not visible", not "nothing to reuse".
- `conventions` / `glossary`: catalog token target is 250 × plugin count (was ≤ 1,000 / ≤ 1,500); ADRs are owned by `polymath-writing`; never ship a same-named command.

### Fixed

- Bundled-script paths in skills used `${POLYMATH_PLUGIN_ROOT}`, which Claude Code never sets in the Bash tool — every call resolved to `/skills/...`. Skills now use `${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}` (Claude Code substitutes the inner variable; other hosts set the outer one).
- `mcp-bridge`: the scan command quoted `scan` into the script path.
- `initialize-project`: validates with the bundled loader in a throwaway data dir instead of a marketplace-only `plugins/...` path.
- SessionStart: under Claude Code the hook wrote the snapshot under `CLAUDE_PLUGIN_DATA`, which skills (Bash tool) never see — the loader now also mirrors it to `~/.polymath/data`; `build-mcp-resolution.py` resolved a different directory than the loader (split snapshot); paused runs written by the runner under `~/.polymath/data` were never surfaced; a minimal project file triggered the "not initialized" nudge.
- `/plugin-budget`: stale 1,500-token target; says it needs a marketplace checkout.

### Removed

- The `/doctor` and `/route` commands — the skills are already `/polymath-core:doctor` and `/polymath-core:route`; the shims only duplicated always-on listing entries (plugin back under the 400-token cap).

## [0.10.1]

### Changed

- `route`, `mcp-bridge` and `glossary` describe `mcpResolution` as advisory; the session's tool list is authoritative for connector skills.

## [0.10.0]

### Changed

- **MCP servers are no longer auto-registered by plugins.** The connector server definitions moved from `.mcp.json` to `mcp/servers.json` — a render template for the opt-in install path (`mcp-registry render`), never an auto-registered config. `reuse-host` stays the default resolution: the current host agent's matching MCP server wins; with no match the provider resolves to `source: none` and the skill degrades gracefully (the silent plugin fallback is gone — `detectedHost: null` now resolves to `none`, never to a plugin server). `prefer-plugin` / `serverOverrides: {provider: plugin}` now pin the template's server name and only take effect once that server is registered in the host.

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
