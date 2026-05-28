# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Polymath is an open-source Claude Code marketplace: 43 work-shaped plugins covering the full SDLC, 15 YAML-driven workflows that compose plugins into end-to-end scenarios, and strict per-plugin token budgets (≤400 tokens always-on). Skills are authored in [agentskills.io v1.0](https://agentskills.io) format, making them portable across Claude Code, Cursor, Codex, Goose, Gemini CLI, and JetBrains Junie.

## Local validation commands

Run these before opening a PR (CI enforces all of them):

```bash
tools/validate-all.sh                  # plugin.json validity + frontmatter discipline
tools/lint-skills.sh                   # description ≤200 chars, SKILL.md ≤500 lines
tools/token-budget.sh                  # per-plugin always-on cost ≤400 tokens
tools/conformance.sh --all             # MANIFEST/SKILL/TEMPLATE/WORKFLOW/CONNECTOR/FIXTURE checks
tools/bakeoff.py check                 # parses bakeoff cases without running a judge
tools/skill-triggering.py check        # validates skill-triggering test frontmatter

# Single-plugin conformance during authoring:
tools/conformance.sh plugins/polymath-<name>

# If the `claude` CLI is on PATH, conformance also runs:
claude plugin validate --strict plugins/polymath-<name>
```

Scaffold new components with the bundled author skills:

```bash
# These invoke the scripts in plugins/polymath-author/bin/ — run from any depth
polymath-author:new-plugin <name>
polymath-author:new-skill <plugin> <skill>
polymath-author:new-command <plugin> <command>
polymath-author:new-connector <name>
polymath-author:new-workflow <name>
```

## Plugin anatomy

Every plugin lives under `plugins/polymath-<name>/` and follows this layout:

```text
.claude-plugin/plugin.json     # Required: name, version, description, license
skills/<name>/SKILL.md         # YAML frontmatter (name, description) + body ≤500 lines
skills/<name>/references/      # Overflow material that would push SKILL.md past 500 lines
skills/<name>/scripts/         # Shell/Python helpers bundled with the skill
commands/<cmd>.md              # Thin aliases ≤20 lines — no scripts, no templates
agents/<role>.md               # Forked-context specialists (use sparingly)
hooks/hooks.json + scripts/    # Deterministic gates (secret-scan, format-on-save)
templates/                     # Artifact templates owned by this plugin
workflows/*.yaml               # polymath-flows only
.mcp.json                      # Connector plugins only
bin/                           # Executables (polymath-flow, scaffolders)
tests/                         # Unit tests, golden fixtures, skill-triggering cases
README.md, CHANGELOG.md        # Both required (DOCS-1 conformance check)
```

The token-budget script measures only the `name` + `description` frontmatter fields from every SKILL.md, command, and agent in the plugin. Long procedure bodies don't count against the cap, but they still must stay ≤500 lines.

## Conformance criteria enforced by CI

| ID | Rule |
| --- | --- |
| MANIFEST-1 | `claude plugin validate --strict` passes |
| MANIFEST-2 | plugin.json has `name`, `version`, `description`, `license` |
| MANIFEST-3 | Plugin has a `status` in marketplace.json (`stable` / `beta` / `experimental` / `deprecated`) |
| SKILL-1 | SKILL.md description ≤200 chars, body ≤500 lines |
| TEMPLATE-1 | Templates whose name matches `shared/schemas/artifacts/*.schema.json` must have frontmatter |
| WORKFLOW-1 | Workflow YAML validates against `shared/schemas/workflow.schema.json` |
| CONNECTOR-1 | Connector plugins need `.mcp.json`, `references/*.md`, and `userConfig` with `title`+`description` per key — unless they delegate to a connector dependency or declare keyword `polymath-cli-only` |
| CONNECTOR-2 | `polymath-connector-*` and `polymath-infra-*` must be audited in `docs/CONNECTOR-POLICY.md` |
| FIXTURE-1 | At least one golden fixture under `tests/golden/<plugin-name>/*.md` |
| DOCS-1 | Both `README.md` and `CHANGELOG.md` present in plugin root |

When adding a new connector, populate the `polymath_value` row in [docs/CONNECTOR-POLICY.md](docs/CONNECTOR-POLICY.md) before the PR can merge.

## Workflow YAML architecture

Workflows live in `plugins/polymath-flows/workflows/*.yaml` and are executed by `plugins/polymath-flows/bin/polymath-flow` — a deterministic state machine with resume and `mustPass` validation. The schema is `shared/schemas/workflow.schema.json`.

A workflow step looks like:

```yaml
- id: prd
  invoke: polymath-product:prd       # plugin:skill reference
  prompt: "..."
  artifacts:
    - docs/prds/${workflow.slug}.md
  needs: [acceptance]                # dependency graph for ordering
```

The `requires.capabilities` block in a workflow is resolved against `.polymath/capabilities.yaml` at run time — workflows declare *what* they need (issue tracker, observability); the project file declares *which* provider supplies it.

## Project localization

A project can customize skill behavior by creating `.polymath/project.yaml` (resolution order: project → user `$CLAUDE_CONFIG_DIR/polymath/project.yaml` → `~/.polymath/project.yaml`). The `polymath-core` SessionStart hook parses it and writes a resolved snapshot to `$CLAUDE_PLUGIN_DATA/polymath-core/project-context.json`. Skills read that snapshot to apply per-project overrides (stack, test commands, PR templates, commit style).

See [docs/PROJECT-LOCALIZATION.md](docs/PROJECT-LOCALIZATION.md) for the full schema and resolution rules, and [.polymath/examples/](/.polymath/examples/) for starter files.

## Marketplace registration

Every plugin must appear in [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) with a `status` field. Update this file when adding or renaming a plugin. The `status` field is the only place maturity tier is tracked — `plugin.json` itself does not carry it (Claude Code's `--strict` validator rejects unknown top-level fields there).

## Commit and PR conventions

- Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, …)
- PR titles mirror the headline commit
- PR descriptions follow [`plugins/polymath-release/templates/PR-description.md`](plugins/polymath-release/templates/PR-description.md)
- CHANGELOG must be updated for every non-trivial change

## Key reference docs

| Doc | When to read |
| --- | --- |
| [docs/PLUGIN-AUTHORING.md](docs/PLUGIN-AUTHORING.md) | Authoring a new plugin or skill |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Full contribution workflow |
| [docs/CONNECTOR-POLICY.md](docs/CONNECTOR-POLICY.md) | Adding/auditing a connector or infra plugin |
| [docs/PROJECT-LOCALIZATION.md](docs/PROJECT-LOCALIZATION.md) | `.polymath/project.yaml` schema |
| [docs/CAPABILITIES.md](docs/CAPABILITIES.md) | Capability → provider mapping vocabulary |
| [docs/QUALITY-SCORECARD.md](docs/QUALITY-SCORECARD.md) | Promotion bar and proof loop |
| [shared/schemas/](shared/schemas/) | JSON schemas for workflows, project, capabilities, artifacts |
