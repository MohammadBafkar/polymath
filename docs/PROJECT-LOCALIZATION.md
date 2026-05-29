# Project localization — `.polymath/project.yaml`

**Schema:** [`shared/schemas/project.schema.json`](../shared/schemas/project.schema.json).
**Loader:** [`plugins/polymath-core/hooks/scripts/load-project-context.py`](../plugins/polymath-core/hooks/scripts/load-project-context.py).
**Skill:** [`polymath-core:project-context`](../plugins/polymath-core/skills/project-context/SKILL.md).
**Examples:** [`.polymath/examples/`](../.polymath/examples/) — dotnet, python, typescript, java, go.

## Why this exists

Without project localization, Polymath skills ship generic guidance.
The `code-review` skill produces the same checklist for a .NET 8
service and a Go service. The `verify-change` skill defaults to a
language it had no way to know about.

`.polymath/project.yaml` at the root of your repo tells the catalog:

- **Stack** — languages, testing frameworks, build tool, runtime,
  database, package manager.
- **Conventions** — commit style, branch strategy, code-review
  checklist path, language-specific style files.
- **External skills** — pointer to other catalogs (e.g.
  `github.com/dotnet/skills`) the project recommends installing.
- **Skill overrides** — per-skill additional context, additional
  review axes, and test commands.
- **Prompts** — pointers to project-owned PR / postmortem / PRD / ADR
  templates skills should prefer over their built-in versions.
- **Setup** — context sources, required local tools, environment
  variable names, and first steps for a new contributor or coding
  agent. Secret values never belong here.
- **Polymath activation** — recommended Polymath plugins, useful
  workflows, and compatible agent surfaces for this repo.
- **MCP servers** — capability → MCP server overrides.
- **Capabilities** — pointer to `.polymath/capabilities.yaml`
  (separate file, separate schema; see
  [`docs/CAPABILITIES.md`](CAPABILITIES.md)).

The polymath-core SessionStart hook loads this file, validates it, and
writes a resolved snapshot to
`${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json`. Skills read
that snapshot and adapt.

## Quick start

1. Run `/polymath-core:init-project` in the target repo, or pick the
   closest example from [`.polymath/examples/`](../.polymath/examples/).
2. If using an example, copy it to `.polymath/project.yaml` at the root
   of your repo.
3. Edit values for your project — `project.name`, stack details,
   conventions paths.
4. Start a new Claude Code session; the SessionStart hook emits a
   one-line summary like:

```text
Polymath: project context loaded. Languages: dotnet 8 (aspnet-core) · Tests: xunit + nsubstitute + fluentassertions · Runtime: kubernetes · External skills: github.com/dotnet/skills
```

Skills that consume the context adapt to your stack.

## File shape

Minimal valid file:

```yaml
schemaVersion: 1
project:
  name: my-service
stack:
  languages:
    - lang: python
      version: "3.12"
```

Full file (every section exercised):

```yaml
schemaVersion: 1

project:
  name: refund-service
  description: Payment refund workflow service.

stack:
  languages:
    - lang: dotnet
      version: "8"
      framework: aspnet-core
  testing:
    - framework: xunit
      mocking: nsubstitute
      assertion: fluentassertions
  build:
    primary: dotnet
    secondary: docker
  runtime:
    kind: kubernetes
    namespace: payments
    manifests: deploy/k8s/
  database:
    primary:
      kind: postgres
      version: "16"
  package_manager:
    kind: nuget
    lock_file: packages.lock.json

conventions:
  code_review_checklist: docs/code-review-checklist.md
  commit_style: conventional-commits
  branch_strategy: trunk-based
  api_style_guide: docs/api-style-guide.md
  language_specific:
    dotnet:
      file: docs/dotnet-conventions.md

external_skills:
  - source: github.com/dotnet/skills
    plugins: [dotnet, dotnet-aspnet, dotnet-test, dotnet-data, dotnet-msbuild]
    install: marketplace

capabilities:
  inherit_from: .polymath/capabilities.yaml

setup:
  context_sources:
    - README.md
    - AGENTS.md
    - docs/CONTRIBUTING.md
  required_tools:
    - name: dotnet
      version: "8"
      check: dotnet --version
      required: true
  environment:
    - name: ANTHROPIC_API_KEY
      purpose: Optional live LLM evaluation.
      required: false
      sensitive: true
  first_steps:
    - Restore dependencies.
    - Run the default test command.

polymath:
  recommended_plugins:
    - name: polymath-core
      reason: Loads project context and SessionStart hints.
      required: true
    - name: polymath-engineering
      reason: Reads code, reviews changes, and verifies diffs.
      required: false
  recommended_workflows:
    - activateProject
    - shipFeature
  compatible_agents:
    - claude-code
    - codex

skill_overrides:
  polymath-engineering:code-review:
    additional_context:
      - docs/code-review-checklist.md
      - docs/dotnet-conventions.md
    additional_axes:
      - axis: csproj-modernization
        prompt: |
          Check new .csproj uses SDK-style with ImplicitUsings + Nullable
          enabled and Directory.Packages.props version pinning.
  polymath-engineering:verify-change:
    test_commands:
      - language: dotnet
        cmd: dotnet test --no-build -- --filter TestCategory!=Integration

prompts:
  pr_description_template: docs/pr-template.md
  postmortem_template: docs/postmortem-template.md

mcp_servers:
  vcs: "@azure-devops/mcp-server"
  ci: "@azure-devops/mcp-server"
```

See [the schema](../shared/schemas/project.schema.json) for the full
set of validated fields and constraints.

## Resolution order

The loader looks for `project.yaml` in this order, first hit wins:

1. `./.polymath/project.yaml` (project, repo-root)
2. `${CLAUDE_CONFIG_DIR}/polymath/project.yaml` (user / team default)
3. `~/.polymath/project.yaml` (last-resort user default)

There is no merge between layers.

## Validation

The loader enforces a minimal subset of the JSON schema at session
start:

- `schemaVersion: 1` (required).
- Unknown top-level keys are rejected.
- `stack.languages` must be a non-empty list of objects each
  containing `lang`.
- `conventions.commit_style` ∈ `{conventional-commits, free-form,
  ticket-prefixed}`.
- `conventions.branch_strategy` ∈ `{trunk-based, gitflow, github-flow,
  release-branch}`.
- `external_skills[*]` must declare `source`. `install`, when
  present, must be one of `{marketplace, manual, submodule}`.
- `setup.required_tools[*]` and `setup.environment[*]`, when present,
  must declare `name`.
- `polymath.recommended_plugins[*]`, when present, must declare `name`.

A bad file exits the loader with code 2 and surfaces the violations
on stderr — the existing snapshot is left untouched so the previous
good context still applies. The SessionStart hook continues; other
surfaces (paused workflows, scheduled work) still render.

The full JSON schema is the source of truth for CI; the in-loader
validator has the same shape, trimmed for the runtime check.

## Versioning & refresh

`schemaVersion` is currently `1`, and the loader accepts only `1`. There is no
automatic migration: if a future Polymath release bumps the schema, an old
file keeps working as long as it still validates against the version the loader
accepts. **The supported refresh path is to re-run `/polymath-core:init-project`**
— it re-inspects the repo and rewrites `.polymath/project.yaml` at the current
schema version, preserving your explicit intent where it can. When the schema
version advances, that release's CHANGELOG names what changed and whether a
re-run is required; the loader's exit-2 validation errors tell you which fields
to fix if you would rather edit by hand.

## How skills consume the context

Skills read `${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json`.
The file mirrors the user's `.polymath/project.yaml` with a `_meta`
block added (source path, load time, schema version). Example:

```bash
ctx="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data}/polymath-core/project-context.json"
if [[ -f "$ctx" ]]; then
  primary_lang="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('stack',{}).get('languages',[{}])[0].get('lang',''))" "$ctx")"
fi
```

The highest-leverage skills to adapt:

- **`polymath-engineering:code-review`** — append review axes from
  `skill_overrides["polymath-engineering:code-review"].additional_axes`;
  cite the project's code-review checklist + language-specific style
  file.
- **`polymath-engineering:verify-change`** — pick the test command
  from `skill_overrides["polymath-engineering:verify-change"].test_commands`
  matching the project's primary language.
- **`polymath-release:pr`** — use `prompts.pr_description_template`
  when set instead of the catalog default.
- **`polymath-incident:postmortem-blameless`** — use
  `prompts.postmortem_template` when set.

Skills that don't consume the context still work — they just produce
generic guidance.

## External skill recommendations

The `external_skills` section lets a project tell contributors which
other catalogs to install:

```yaml
external_skills:
  - source: github.com/dotnet/skills
    plugins: [dotnet, dotnet-aspnet, dotnet-test, dotnet-data, dotnet-msbuild]
    install: marketplace
```

The SessionStart hook surfaces this in its summary line so a new
contributor sees them. Installation itself is out of scope for
Polymath — follow the external catalog's own instructions.

The framing is **delegation**: Polymath does not compete with
`dotnet/skills` on .NET depth. The project says "for .NET use
`dotnet/skills`; Polymath provides the SDLC workflow on top of that."

## Project activation

Use `polymath-core:initialize-project` or
`/polymath-flows:run-workflow activateProject` to create the first
project file for an existing repo. The initializer reads local
instructions, docs, CI, package manifests, and deployment files, then
writes:

- `.polymath/project.yaml` with stack, conventions, setup, Polymath
  recommendations, and skill overrides.
- `.polymath/capabilities.yaml` when providers can be inferred with
  confidence.
- `docs/polymath-onboarding.md` with required tools, environment
  variable names, recommended plugin install sets, useful workflows,
  portability notes, and open questions.

The initializer must not store secret values and must not guess unknown
capability providers.

## Capability mapping (sibling file)

Capability resolution lives in `.polymath/capabilities.yaml`
(see [`docs/CAPABILITIES.md`](CAPABILITIES.md)). The two files are
siblings under `.polymath/`. `project.yaml` may declare:

```yaml
capabilities:
  inherit_from: .polymath/capabilities.yaml
```

This is a pointer for tooling; it does not duplicate the capability
data. A project without `capabilities.yaml` simply doesn't get
capability resolution — workflows that need it fail clearly at start
time.

## Per-session, not per-message

The loader runs once per Claude Code session (at SessionStart). If
you edit `.polymath/project.yaml` mid-session, restart Claude Code to
pick up the change.

## What this does **not** do

- Install external skill plugins for you — that's manual.
- Cross-validate against `.polymath/capabilities.yaml`.
- Run the skill overrides automatically — skills read the snapshot
  and apply the overrides themselves.
- Provide a UI for editing — copy an example and edit YAML directly.
