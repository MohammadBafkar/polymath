# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Polymath is an open-source Claude Code marketplace: 36 work-shaped plugins covering the full SDLC, 26 YAML-driven workflows that compose plugins into end-to-end scenarios, and strict per-plugin token budgets (≤400 tokens always-on). Skills are authored in [agentskills.io v1.0](https://agentskills.io) format, making them portable across Claude Code, Cursor, Codex, Goose, Gemini CLI, and JetBrains Junie.

## Local validation commands

Run these before opening a PR (CI enforces all of them):

```bash
tools/validate-all.sh                  # plugin.json validity + frontmatter discipline
tools/lint-skills.sh                   # description ≤200 chars, SKILL.md ≤500 lines
tools/token-budget.sh                  # per-plugin always-on cost ≤400 tokens
tools/conformance.sh --all             # MANIFEST/SKILL/TEMPLATE/WORKFLOW/CONNECTOR/FIXTURE checks
tools/bakeoff.py check                 # parses bakeoff cases without running a judge
tools/skill-triggering.py check        # validates skill-triggering test frontmatter
tools/workflow-triggering.py check     # workflow-triggering frontmatter + trigger drift guard
tools/build-workflow-index.py --check  # workflow routing index in sync with workflow YAML
tools/build-surface-index.py --check   # deterministic route-signals table in sync with per-surface routing.yaml
tools/build-capability-index.py --check # capabilities.json providerPlugins in sync with per-provider bindings
tools/lint-descriptions.py --strict    # no two descriptions token-collide (disambiguation floor)
tools/check-description-confusion.py check   # confusion-matrix frontmatter (sibling routing) is valid

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

Hand-run analysis tools (not CI gates — measurement/diagnostics, run manually):

```bash
tools/route-eval.py                    # held-out routing measurement (precision/reach vs tests/route-eval/heldout.jsonl); reports, always exits 0 — NOT the tests/route-triggering gate
tools/analyze-token-usage.py <file>    # break down a `claude -p --output-format stream-json` transcript by token consumption
tools/check-mcp-packages.py --online  # re-verify connector .mcp.json packages against npm (the offline MCP-PKG gate runs in conformance)
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
.mcp.json                      # Integration plugins only (vcs/chat/observability/…)
bindings/<provider>/binding.json  # Capability provider wiring (integration/infra plugins)
bin/                           # Executables (polymath-flow, scaffolders)
tests/                         # Unit tests, golden fixtures, skill-triggering cases
README.md, CHANGELOG.md        # Both required (DOCS-1 conformance check)
```

The token-budget script measures only the `name` + `description` frontmatter fields from every SKILL.md, command, and agent in the plugin. Long procedure bodies don't count against the cap, but they still must stay ≤500 lines.

Default to **skill-only**: a skill earns a command only when it is a frequent direct user entry point, and a workflow only when ≥2 skills chain with data dependencies or gates. Because command descriptions count against the per-plugin budget, a thin shim is not free. See [docs/PLUGIN-AUTHORING.md § 5.1](docs/PLUGIN-AUTHORING.md) for the promotion policy; `tools/check-command-overlap.py` and `tools/check-workflow-invokes.py` enforce it.

## Conformance criteria enforced by CI

| ID | Rule |
| --- | --- |
| MANIFEST-1 | `claude plugin validate --strict` passes |
| MANIFEST-2 | plugin.json has `name`, `version`, `description`, `license` |
| MANIFEST-3 | Plugin has a `status` in `registry/polymath-catalog.json` (`stable` / `beta` / `experimental` / `deprecated`) |
| SKILL-1 | SKILL.md description ≤200 chars, body ≤500 lines |
| TEMPLATE-1 | Templates whose name matches `registry/schemas/artifacts/*.schema.json` must have frontmatter |
| WORKFLOW-1 | Workflow YAML validates against `registry/schemas/workflow.schema.json` |
| WORKFLOW-INDEX | `plugins/polymath-flows/data/*.json` routing index matches a fresh `tools/build-workflow-index.py` build (diff-guard + injected-index token ceiling) |
| SURFACE-INDEX | `plugins/polymath-core/data/route-signals.json` + `surface-index.json` match a fresh `tools/build-surface-index.py` build (diff-guard); `--strict` (SURFACE-2) requires every intent / url / regex pattern to be globally unique across all surfaces |
| CAPABILITY-INDEX | `registry/schemas/capabilities.json` `providerPlugins{}` matches a fresh `tools/build-capability-index.py` build from per-provider `bindings/<provider>/binding.json` (diff-guard); `--strict` (BINDING-1) requires every binding's provider to be in its capability's `providers[]`, forbids two plugins claiming one `(capability, provider)`, and requires each `mcp` binding's `server` + `userConfigKeys` to exist in the plugin's `.mcp.json` / `plugin.json` |
| TOOL-1 | every `tools/<name>/tool.json` validates against `registry/schemas/tool.schema.json` (enforced by `build-surface-index.py`, i.e. SURFACE-INDEX) |
| TRUST-1 | a `routing.yaml` `trust` value is `propose` (default) or `auto-headless` — enforced by the `registry/schemas/surface-routing.schema.json` `trust` enum (`build-surface-index.py` validates every sidecar against it). Unconditional `auto` is intentionally not in the enum until per-surface write-scope analysis exists |
| WORKFLOW-2 | `build-workflow-index.py --strict`: every workflow declares `whenToUse` + `triggers`, and no trigger phrase is shared across workflows |
| WORKFLOW-TRIGGER | `tests/workflow-triggering/*.md` frontmatter is valid and its `trigger_prompts` are a superset of the workflow's own `triggers` |
| DESC-1 | `tools/lint-descriptions.py --strict`: no two always-on descriptions (skill/command/agent) token-collide without a distinguishing proper noun (the disambiguation floor; `scope_boundary` is advisory) |
| DESC-2 | `tools/check-description-confusion.py check`: `tests/forbidden_prompts.yaml` cases are well-formed (referenced skills exist). Behavioural `run` mode is opt-in under `CLAUDE_CODE_OAUTH_TOKEN` |
| INTEGRATION-1 | Integration plugins (those that ship a `.mcp.json`) need `references/*.md` and `userConfig` with `title`+`description` per key — unless they delegate to a connector dependency or declare keyword `polymath-cli-only`. Detected by `.mcp.json` presence, not name |
| INTEGRATION-2 | Every integration plugin (`.mcp.json` or `bindings/`) and infra plugin must be audited in `docs/INTEGRATION-POLICY.md` and carry the synced policy block. Detected by artifact, not name prefix |
| MCP-PKG | `tools/check-mcp-packages.py`: every connector `.mcp.json` package is confirmed to resolve on npm or disclosed as a placeholder (`<!-- mcp-package-status -->`) in its README — no dead-on-install connector ships silently. Offline; `--online` re-verifies vs npm |
| AGENT-1 | `tools/check-agents.py`: every `plugins/*/agents/<name>.md` has a baseline-beating golden fixture at `tests/golden/<plugin>/agent-<name>.md` (frontmatter `agent: <name>` + an `expect` trace), and no agent name/description collides with a workflow name or trigger phrase (the role-as-agent guard, PLUGIN-AUTHORING §6/§6.1) |
| FIXTURE-1 | At least one golden fixture under `tests/golden/<plugin-name>/*.md` |
| DOCS-1 | Both `README.md` and `CHANGELOG.md` present in plugin root |

When adding a new integration/infra plugin (one with a `.mcp.json` or `bindings/`), populate its `polymath_value` row in [docs/INTEGRATION-POLICY.md](docs/INTEGRATION-POLICY.md) before the PR can merge. Concept plugins are named by capability (`polymath-vcs`, `polymath-chat`, …) and map multiple vendor providers via `bindings/<provider>/binding.json`; the `registry/schemas/capabilities.json` vocabulary lists each capability's providers (some aspirational until a real MCP package ships).

## Workflow YAML architecture

Workflows live in `plugins/polymath-flows/workflows/*.yaml` and are executed by `plugins/polymath-flows/bin/polymath-flow` — a deterministic state machine with resume and `mustPass` validation. The schema is `registry/schemas/workflow.schema.json`.

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

Workflows also declare a routing surface — `whenToUse` (a terse, always-on hint), `triggers` (naive user phrasings, unique across workflows), and `detectionSignals` (file globs / intents). `tools/build-workflow-index.py` compiles these into `plugins/polymath-flows/data/` and the polymath-flows SessionStart hook injects the compact index so the agent can detect and **propose** a matching workflow (the detect → propose → confirm → run contract lives in `run-workflow/SKILL.md`). Re-run the builder after editing any workflow; the `WORKFLOW-INDEX` gate fails on drift, and `WORKFLOW-2` (`--strict`) requires `whenToUse` + `triggers` on every workflow with globally-unique triggers.

## Deterministic surface routing (route-signals)

Any surface — skill, workflow, or tool — can opt into the deterministic prompt-time route hint (the `polymath-core` `route-hint` `UserPromptSubmit` hook) by dropping a `routing.yaml` sidecar declaring hard signals (`url` / `regex` / `paths` / `diff`) and soft `intents`. Skills declare it next to `SKILL.md` (`skills/<skill>/routing.yaml`); workflows declare it in `plugins/polymath-flows/routing/<name>.yaml` (kept outside the `workflows/*.yaml` glob so the flows validator never sees it). **Tools** are a first-class unit too: a `tools/<name>/tool.json` manifest (validated by [`registry/schemas/tool.schema.json`](registry/schemas/tool.schema.json), `TOOL-1`, enforced by the SURFACE-INDEX gate) plus an optional `routing.yaml` — added like a skill and dispatched through the same registry. This replaced the per-connector bash "detect-and-hint" scripts: detection signals now live in `routing.yaml`, and the MCP tool detail in `tool.json`.

Three further dispatch facets build on this registry: a surface may declare `trust: auto-headless` so the agent MAY run it without confirmation in a non-interactive session (unconditional `auto` is not an allowed value — the surface-routing schema enum permits only `propose`/`auto-headless`, `TRUST-1`); a workflow may declare `chainsTo: [<workflow>...]` so the runner proposes the natural next arc on completion (never auto-runs; dangling targets fail `build-workflow-index --strict`); and a `PostToolUse` event-trigger hook (`polymath-core/hooks/scripts/event-trigger.py`) proposes a surface from what just happened (e.g. a failed test run → `bugTriage`), the general form of the per-connector `Stop` nudges. `tools/build-surface-index.py` is the **single producer** that compiles every sidecar into `plugins/polymath-core/data/route-signals.json` (formerly hand-maintained) plus a `surface-index.json` catalog, validating each against [`registry/schemas/surface-routing.schema.json`](registry/schemas/surface-routing.schema.json) and enforcing globally-unique intent/url/regex patterns (`SURFACE-2`). Re-run the builder after editing any `routing.yaml`; the `SURFACE-INDEX` gate fails on drift.

## Project localization

A project can customize skill behavior by creating `.polymath/project.yaml` (resolution order: project → user `$CLAUDE_CONFIG_DIR/polymath/project.yaml` → `~/.polymath/project.yaml`). The `polymath-core` SessionStart hook parses it and writes a resolved snapshot to `$CLAUDE_PLUGIN_DATA/polymath-core/project-context.json`. Skills read that snapshot to apply per-project overrides (stack, test commands, PR templates, commit style).

See [docs/PROJECT-LOCALIZATION.md](docs/PROJECT-LOCALIZATION.md) for the full schema and resolution rules, and [.polymath/examples/](.polymath/examples/) for starter files.

## Marketplace registration

Every plugin must appear in [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) (Claude's catalog manifest) AND in [registry/polymath-catalog.json](registry/polymath-catalog.json) (Polymath's own catalog, where `status` lives). Update both when adding or renaming a plugin. `status` cannot live in `marketplace.json` or `plugin.json` — Claude Code's `--strict` validator rejects unknown fields in both, and `MANIFEST-3` enforces presence in the Polymath catalog. `tools/check-catalog.py` rejects divergent plugin sets between the two files.

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
| [docs/INTEGRATION-POLICY.md](docs/INTEGRATION-POLICY.md) | Adding/auditing a connector or infra plugin |
| [docs/PROJECT-LOCALIZATION.md](docs/PROJECT-LOCALIZATION.md) | `.polymath/project.yaml` schema |
| [docs/CAPABILITIES.md](docs/CAPABILITIES.md) | Capability → provider mapping vocabulary |
| [docs/QUALITY-SCORECARD.md](docs/QUALITY-SCORECARD.md) | Promotion bar and proof loop |
| [registry/schemas/](registry/schemas/) | JSON schemas for workflows, project, capabilities, artifacts |
