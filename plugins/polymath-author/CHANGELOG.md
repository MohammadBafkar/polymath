# Changelog — polymath-author

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Added

- Style guide: **Mode contract** (deterministic / analytical / generative, with what each mode obliges), the calculator-script convention, one slug rule, two placeholder markers (`[TBD]`, `[VERIFY]`), and an unattended-run rule for confirm checkpoints.
- `bin/new-skill.sh` scaffolds `**Mode:**`, `## Inputs`, and `## Quality bar`; a unit test proves a fresh scaffold passes the shape gate.

### Changed

- Every skill declares its **Mode** — 3 analytical, 2 deterministic — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `skill-author-critic` judges mode *fit* (prose arithmetic in a deterministic skill, a generative skill that converges on its first idea).
- `validate-plugin` runs `tools/check-skill-shape.py` and the plugin's unit tests; `audit-marketplace` lists every skill's mode and checks unattended runs; its `AGENTS.md` link (dead once installed) is now a repo-root path.
- `token-budget-report`: Inputs (marketplace checkout required; heuristic-only when the CLI is absent), output sorted heaviest-first.
- `scaffold-component` keeps the root `POLYMATH.md` in sync when a component adds tools or env vars.

## [0.11.0]

### Changed

- `skill-author-critic`: a reliability lens — resolvable installed paths, missing-input behavior, side-effect gates, verification, fabrication guard, untrusted content, factual accuracy, sibling consistency.
- `references/skill-style-guide.md`: new "Reliability contract" section; frontmatter guidance reflects the agentskills.io key allowlist.
- `scaffold-component`: generators run only after confirmation (dry-run first), registration edits are additive diffs, build/test is run after scaffolding; Output shape added; shorter description (plugin back under the 400-token cap).

### Fixed

- `validate-plugin`: runs `tools/conformance.sh <plugin>` as the source of truth; removed the nonexistent `tools/link-templates.sh` / `templates.json` step; a gate that can't run is N/A, never PASS.
- `references/frontmatter-cheatsheet.md`: hook commands use the quoted `${CLAUDE_PLUGIN_ROOT}`; a blocking hook's reason comes from stderr, not stdout.
- Commands: `new-workflow` validates with `polymath-flow` on PATH instead of a `../polymath-flows` path that breaks once installed; bundled-script paths resolve under Claude Code.

## [0.10.0]

### Changed

- **/new-connector** scaffolds `mcp/servers.json` (a render template) instead of a root `.mcp.json` — plugins never auto-register MCP servers; the host agent's registered MCPs are reused first. See `docs/MCP-REUSE.md`.

## [0.9.0]

### Added

- **audit-marketplace** — adversarially audit the whole marketplace for production readiness, gaps, and over-engineering; loops every plugin/tool/workflow off the deterministic inventory, delegates per-item critique to `skill-author-critic` / `red-team` / `validate-plugin`, and emits a ranked ADD/FIX/CONSOLIDATE/REMOVE scorecard with a net-surface-delta ≤ 0 simplicity bias.

## [0.8.0]

Author craft: scaffold new plugins/skills/connectors, validate against gates, measure listing budget, review skill quality.

### Skills

- **scaffold-component** — Generate a component/service/module in the CURRENT repo per its conventions — native generator first (tool-spec handoff), canonical infra bodies from owning skills, no freehand boilerplate.
- **skill-author-critic** — Review a SKILL.md against the style guide — frontmatter, procedure, output, anti-patterns; verdict ACCEPT/REVISE/REWRITE.
- **token-budget-report** — Check listing-token cost per plugin via claude plugin details; flag over-cap plugins and the heaviest descriptions.
- **validate-plugin** — Run every Polymath gate against a plugin — claude plugin validate, lint-skills, token-budget, workflow schema.

### Commands

- **/new-command** — Generate a thin /slash-command alias file inside an existing plugin via new-command.sh; not a capability or workflow.
- **/new-connector** — Generate an integration (MCP) plugin named by capability (polymath-<concept>) with mcp/servers.json template + userConfig via new-connector.sh; not a generic plugin (new-plugin).
- **/new-pack** — Generate a defaults pack (standalone marketplace + conventions plugin + apply-defaults copy-in) for an org/team/project scope via new-pack.sh; not a generic plugin (new-plugin).
- **/new-plugin** — Generate a new top-level Polymath plugin (plugin.json, README, CHANGELOG) via new-plugin.sh; not for adding a skill or command to an existing plugin.
- **/new-skill** — Generate the SKILL.md and directories for a new skill inside an existing plugin via new-skill.sh; not a whole plugin.
- **/new-workflow** — Generate a new flows-lite workflow via the bundled new-workflow.sh; not a plugin or skill.
