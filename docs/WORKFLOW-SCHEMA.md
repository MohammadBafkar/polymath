# Workflow YAML schema (v0.1 — flows-lite)

Canonical schema: [`shared/schemas/workflow.schema.json`](../shared/schemas/workflow.schema.json).
Scaffolder template: [`tools/scaffolder-templates/Workflow.yaml`](../tools/scaffolder-templates/Workflow.yaml) (used by `tools/new-workflow.sh`).

flows-lite v0.1 is **serial only**. Parallel steps, agent panels, connector events, and `wait-for-event` are out of scope.

## 1. Anatomy

```yaml
schemaVersion: 0.1
name: shipFeature              # camelCase
version: 0.1.0
description: Ship a small feature from PRD to PR draft.
requires:
  plugins: [polymath-core, polymath-product, polymath-engineering, polymath-release]
inputs:
  - name: title
    type: string
    required: true
  - name: scope
    type: enum
    values: [small, medium]
    default: small
guards:
  - id: git-worktree-readable
    type: command
    command: git status --short
steps:
  - id: prd
    invoke: polymath-product:prd
    prompt: Write a PRD for ${inputs.title}.
    artifacts:
      - docs/prds/${workflow.slug}.md
  - id: implement
    invoke: polymath-engineering:feature-dev
    prompt: Implement the smallest safe change satisfying the PRD.
    needs: [prd]
mustPass:
  - id: prd-exists
    type: fileExists
    path: docs/prds/${workflow.slug}.md
```

## 2. Resolution order

A workflow by `name` resolves in this order (highest priority first):

1. Project: `.claude/polymath/workflows/<name>.yaml`
2. User: `${CLAUDE_CONFIG_DIR}/polymath/workflows/<name>.yaml` (fallback `~/.claude/polymath/workflows/`)
3. Marketplace: installed `polymath-flows/workflows/<name>.yaml`

## 3. Inheritance

```yaml
schemaVersion: 0.1
extends: polymath-flows:shipFeature@0.1
override:
  steps:
    - id: review
      invoke: polymath-engineering:code-review
      prompt: Review with extra attention to authentication.
insertAfter:
  implement:
    - id: license-check
      invoke: polymath-release:pr
      prompt: Check whether the PR mentions third-party dependency changes.
mustPass:
  - id: pr-draft-mentions-risk
    type: fileMatches
    path: docs/pr/${workflow.slug}.md
    pattern: "(risk|rollback|test)"
```

Override semantics:

- `override.steps`: replace parent steps with the same `id`.
- `insertAfter.<id>`: insert new steps after the named anchor.
- `mustPass`: appended to parent checks.

## 4. `mustPass` check types

| Type | Required fields | Default severity | Behavior |
| --- | --- | --- | --- |
| `fileExists` | `path` | blocking | Pass if file exists on disk. Weak — a stub file satisfies it. |
| `fileMatches` | `path`, `pattern` (regex) | blocking | Pass if the file exists and matches the pattern. Weak — a regex match does not imply real content. |
| `commandSucceeds` | `command` | blocking | **Strong.** Pass if the shell command exits 0. |
| `stepSummaryMatches` | `step`, `pattern` (regex) | **advisory** | Pass if the named step's summary matches the pattern. Default-advisory because a summary is a freeform string the executor authored; matching it cannot prove the underlying work. |
| `artifactValid` | `path`, `artifact` (PRD / ADR / Postmortem / ThreatModel) | blocking | **Strong.** Pass if frontmatter parses and satisfies the named artifact schema. |
| `artifactSchemaStrict` | `path`, `artifact`, optional `minBodyChars`, `rejectAdditionalProperties` | blocking | **Strong.** Like `artifactValid` plus: requires `minBodyChars` (default 200) of substantive non-heading content, and (by default) rejects frontmatter fields not declared in the schema. Catches hollow stub artifacts. |
| `diffConstraint` | at least one of `filesChanged`, `linesChanged`, `pathAllowlist`, `pathBlocklist`; optional `since` ref | blocking | **Strong.** Bounds the worktree (or ranged-diff) effect of the workflow. `filesChanged.min` proves *something* changed; `.max` and `pathAllowlist` prove the agent did not run away. Untracked files are counted. |
| `command` (in guards) | `command` | blocking | Used in `guards:` only. Pre-step precondition. |

### 4.1 Severity

Every check accepts an optional `severity: advisory | blocking`. Blocking checks (the default for everything except `stepSummaryMatches`) pause the workflow on failure. Advisory checks run, report their failure in the `advisories` array of the run result, but do **not** pause.

A workflow should have at least one strong-deterministic blocking gate — one of `commandSucceeds`, `artifactValid`, `artifactSchemaStrict`, or `diffConstraint`. `polymath-flow validate` emits a warning when this is missing, because a workflow whose only blockers are `fileExists` / `fileMatches` / advisory `stepSummaryMatches` can pass on a hollow run (stub files plus a regex-matching summary).

## 5. Placeholders

- `${inputs.<name>}` — user-supplied input.
- `${workflow.slug}` — auto-derived kebab-case slug from `${inputs.title}`.
- `${workflow.id}` — full workflow run ID (timestamp + slug).

Future: `${steps.<id>.summary}` will be exposed when richer summaries land.

## 6. State

Each run gets a directory under `${CLAUDE_PLUGIN_DATA}/workflows/`:

```text
${CLAUDE_PLUGIN_DATA}/workflows/2026-05-23T14-22-shipFeature-rate-limit/
  ├── state.json
  ├── inputs.json
  ├── trace.jsonl
  ├── step-summaries/<step-id>.md
  └── artifacts/
```

State transitions are owned by `polymath-flows/bin/polymath-flow`. The skills (`run-workflow`, `resume-workflow`, `list-workflows`) call this executable.

## 7. Out of scope (v0.1)

- Parallel steps.
- Agent panels.
- Connector events (`wait-for-event`).
- Shell steps that mutate infrastructure.
- AI-based cross-artifact alignment as a blocking gate.
- Real PR creation through GitHub.

These all land after the serial runner has proven installation, state, resumption, and deterministic checks.
