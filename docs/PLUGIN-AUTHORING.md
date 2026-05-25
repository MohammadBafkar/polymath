# Plugin authoring guide (v0.1)

This guide is scoped to the MVP. It describes how to create, structure, and submit a Polymath plugin. See [`docs/WORKFLOW-SCHEMA.md`](WORKFLOW-SCHEMA.md) for the workflow YAML schema.

## 1. Component decision matrix

| Need                                                            | Component                              |
| --------------------------------------------------------------- | -------------------------------------- |
| Event-driven gate (block secrets, format on save, push reminder) | Hook                                   |
| External service tool calls (GitHub, Jira, Datadog, …)           | MCP server                             |
| Persistent background watcher (logs, CI, deploy status)          | Monitor                                |
| Per-language code intelligence                                   | LSP plugin (compose official)          |
| Specialist isolated context (deep audit, panel critique, research) | Agent                                 |
| Quick alias / flow orchestrator / no supporting files            | Command (flat `.md` in `commands/`)    |
| Procedure with templates, scripts, examples, or references       | Skill (directory with `SKILL.md`)      |

Polymath does not ship output styles — tone control lives in reference-content skills (e.g. `tone-terse`).

## 2. Plugin layout

```text
plugins/polymath-<name>/
├── .claude-plugin/
│   └── plugin.json
├── skills/<skill>/
│   ├── SKILL.md
│   ├── references/            # optional
│   └── scripts/               # optional
├── templates/                 # plugin-owned artifact templates (PRD.md, etc.)
├── commands/<cmd>.md
├── agents/<role>.md
├── hooks/
│   ├── hooks.json
│   └── scripts/
├── monitors/monitors.json     # rare
├── .mcp.json                  # connector plugins only
├── workflows/*.yaml           # polymath-flows only
├── tests/
├── README.md
└── CHANGELOG.md
```

## 3. plugin.json

```jsonc
{
  "name": "polymath-thing",
  "version": "0.1.0",
  "description": "Short, ≤ 200 chars, trigger phrase first.",
  "license": "Apache-2.0",
  "dependencies": {
    "plugins": ["polymath-core"]
  },
  "metadata": {
    "category": "engineering",
    "tags": ["tdd", "review"]
  }
}
```

Do **not** add unknown top-level fields (including `status`). Claude Code's
`plugin validate --strict` treats unknown fields as warnings, and conformance
runs the validator with `--strict`. Plugin-level metadata that doesn't fit
the official manifest schema lives in `.claude-plugin/marketplace.json` —
see § 3.1.

## 3.1. Maturity tier (`status`)

Every plugin declares a maturity tier in `marketplace.json`. The tier is a
contract with users about how much to trust the plugin.

| Tier | Meaning |
| --- | --- |
| `stable` | Proven shape. Has skills + tests + a fixture, and the plugin's workflows (if any) have at least one strong-deterministic blocking gate. Breaking changes go through a deprecation cycle. |
| `beta` | Structurally valid + has skills, but value not yet proven. Shape may shift; depend on it with caution. |
| `experimental` | Scaffolded but unproven. May change shape, be renamed, be merged into another plugin, or be removed. Most `polymath-connector-*`, `polymath-lang-*`, and `polymath-infra-*` plugins live here until a real workflow + fixture proves the shape. |
| `deprecated` | Scheduled for removal. The plugin's README must name the replacement and the removal date. |

A plugin promotes to `stable` only when it has: (a) at least one strong-gated workflow that exercises its primary skill, (b) a golden fixture that runs against a live Claude model in CI, and (c) at least one external user beyond the maintainer. Promotion is a CHANGELOG entry, not just a status flip.

Add the entry in `marketplace.json`:

```jsonc
{
  "name": "polymath-thing",
  "source": "./plugins/polymath-thing",
  "description": "…",
  "version": "0.1.0",
  "category": "engineering",
  "tags": ["tdd", "review"],
  "status": "experimental"
}
```

`tools/conformance.sh` rejects a plugin whose `marketplace.json` entry is missing `status` or sets it to an unknown value.

## 4. Skill frontmatter rules

- `name`: bare kebab-case slug.
- `description`: ≤ 200 chars, trigger phrase first, present tense.
- `SKILL.md` body ≤ 500 lines. Spill to `references/`.
- Reference the plugin's templates via relative path from the skill (e.g. `[\`PRD.md\`](../../templates/PRD.md)`).

Example:

```markdown
---
name: prd
description: Draft a PRD from a problem statement plus user/context inputs; populates docs/prds/<slug>.md.
---

# prd

## When to use

- The user says "draft a PRD" or "we need a spec for X".
- A workflow step invokes `polymath-product:prd`.

## Procedure

1. …
```

## 5. Commands vs skills

Both produce `/name` invocations. Choose by directory shape:

- **Command** (`commands/foo.md`): single flat file, ≤ 20 lines, ideal for aliases.
- **Skill** (`skills/foo/SKILL.md`): directory, bundles templates, scripts, references.

If both exist for the same name, the command must be a thin alias pointing to the skill; the skill holds canonical content.

## 6. Agent rules

Agents are reserved for:

- Panels of critics running in parallel.
- Heavy research / audit that would flood the main context.
- Distinct named roles the user explicitly addresses.

Three structural constraints (verify against current Claude Code docs before relying):

1. Plugin-shipped subagents **cannot** ship their own hooks, MCPs, or `permissionMode`.
2. Subagents **cannot** spawn subagents.
3. Subagent execution is synchronous from the caller's view.

A new agent must ship with a golden fixture showing it finds something a **no-agent baseline** misses. The baseline is the same input handed to the same Claude lead without any subagent — *not* a skill running in the parent context. The earlier "outperform a skill" framing made the comparison structurally rigged: a skill in the parent context can never lose on tokens, so an agent could not prove its worth even when it should. The actual question an agent has to answer is "does forking context (independent priors, fresh window, parallel critique) catch something the same lead misses without it?" The fixture trace + the no-agent trace are both checked in and reviewed together.

Agent evidence lives under `tests/agent-evidence/<plugin>/<agent>.md` and is
checked by `tools/check-agent-evidence.py` as part of conformance. Required
frontmatter:

```yaml
plugin: polymath-thinking
agent: architecture-critic
scenario: adr-cache-store
baseline_prompt: "Review this ADR without using a subagent."
baseline_misses:
  - "Failure mode the same-context lead often misses."
agent_expected_findings:
  - "Finding the forked-context agent must surface."
decision_relevance: "Why the delta changes the decision."
```

`tools/check-agent-evidence.py` also rejects forbidden plugin-shipped subagent
fields (`permissionMode`, `hooks`, `mcpServers`) and requires a matching golden
fixture under `tests/golden/<plugin>/`.

## 7. Hooks

- `PreToolUse(Write|Edit)` for secret-scan or format checks.
- `PostToolUse(Edit|Write)` for formatter or lint runs.
- `SessionStart` for printing active plugins or paused workflows.
- `Stop` for end-of-turn nudges.

Hooks live in `hooks/hooks.json`; helper scripts live in `hooks/scripts/`.

## 8. Token-budget discipline

- Per-plugin always-on listing ≤ 400 tokens.
- MVP total ≤ 1,500 tokens measured.
- Run `tools/token-budget.sh` locally before PR.

CI fails ≥ 50-token regressions without an explicit `expected-cost:` override.

## 9. Templates

Each plugin owns its artifact templates under `plugins/<plugin>/templates/`. Skills reference templates by relative path; workflows validate the frontmatter via `mustPass: artifactValid` against the matching JSON schema in `shared/schemas/artifacts/`.

Run `tools/conformance.sh <plugin>` to check that template + frontmatter + schema agree.

## 10. Tests

Each plugin should ship at least one golden fixture under `tests/golden/<plugin>/<scenario>.md`. Fixtures contain a goal prompt plus expected component invocations. CI runs `claude -p` against these when `ANTHROPIC_API_KEY` is configured.

## 11. Submitting a plugin

1. `tools/new-plugin.sh <name>` to scaffold.
2. Author components.
3. `tools/validate-all.sh && tools/lint-skills.sh && tools/token-budget.sh` must pass.
4. Add a golden fixture to `tests/golden/<plugin>/`.
5. Register the plugin in `.claude-plugin/marketplace.json`.
6. Open a PR. CI runs all gates.
