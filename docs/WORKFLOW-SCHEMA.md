# Workflow YAML schema

Canonical schema: [`registry/schemas/workflow.schema.json`](../registry/schemas/workflow.schema.json).
Scaffolder template:
[`plugins/polymath-author/templates/Workflow.yaml`](../plugins/polymath-author/templates/Workflow.yaml)
(used by `polymath-author:new-workflow`).

flows-lite is serial. Parallel steps, agent panels, connector
events, and `wait-for-event` are reserved for future schema versions
and unsupported by the runner.

## 1. Anatomy

```yaml
schemaVersion: 0.1
name: shipFeature              # camelCase
version: 0.1.0
description: Ship a small feature from PRD to PR draft.
requires:
  plugins: [polymath-core, polymath-product, polymath-engineering, polymath-release]
  capabilities:
    # Optional. Each capability resolves at start time against
    # .polymath/capabilities.yaml. See docs/CAPABILITIES.md.
    issue_tracker: true
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

A step's `artifacts:` list is a CHECKED contract, not documentation:
`polymath-flow complete` refuses (exit 2, step stays in-flight) while any
declared path is missing — the smallest hollow-run guard, applied at the
moment of the claim rather than only at final `assert`. A step whose
artifacts are genuinely conditional declares `artifactsAdvisory: true`;
missing paths then warn in the completion payload instead of refusing.
Existence is the per-step bar — content quality stays with the strong
`artifactValid` / `artifactSchemaStrict` gates at `assert`.

## 2. Resolution order

A workflow by `name` resolves in this order (highest priority first):

1. Project: `.claude/polymath/workflows/<name>.yaml`
2. User: `${CLAUDE_CONFIG_DIR}/polymath/workflows/<name>.yaml`
   (fallback `~/.claude/polymath/workflows/`)
3. Marketplace: installed `polymath-flows/workflows/<name>.yaml`

## 3. Inheritance — build-time flattening

`extends` is **build-time only**. A partial workflow names a parent and
contributes overrides; `polymath-flow flatten` composes them into a
standalone workflow that the runner executes. The runner **hard-errors**
on any workflow still carrying `extends` / `override` / `insertAfter` at
`validate`, `start`, `next`, or `assert` time — runtime merging would
make a run's behavior depend on a parent file that can change underneath
it.

A partial (e.g. `.claude/polymath/partials/shipFeatureAcme.yaml` —
anywhere outside the runner's workflow resolution directories):

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

Flatten it into the project workflow layer, and keep it fresh with the
drift lint:

```bash
polymath-flow flatten .claude/polymath/partials/shipFeatureAcme.yaml \
  --out .claude/polymath/workflows/shipFeature.yaml
polymath-flow flatten .claude/polymath/partials/shipFeatureAcme.yaml \
  --out .claude/polymath/workflows/shipFeature.yaml --check   # exit 1 when stale
```

Composition semantics:

- `override.steps`: replace parent steps with the same `id` (unknown id
  errors).
- `override.removeSteps`: drop the named steps, applied LAST (so a
  partial may insert after an anchor and then remove the anchor). Guarded
  by the **strong-gate-survival invariant**: flatten errors when a
  surviving step still `needs` a removed one, when a
  `stepSummaryMatches` check names a removed step, when a strong
  blocking gate checks an artifact that only removed steps produced, or
  when removal would leave a parent-with-strong-gate flattened into a
  result with none. `mustPass` itself is append-only — an org variant
  can never silently strip the parent's gates.
- `insertAfter.<id>`: insert new steps after the named anchor (unknown
  anchor or colliding step id errors).
- `steps`: appended after the parent's steps.
- `mustPass` / `guards`: appended to the parent's checks.
- Any other key present on the partial (`name`, `version`, `description`,
  `whenToUse`, `triggers`, `requires`, `inputs`, …) replaces the parent's
  value wholesale; absent keys are inherited. A partial without `name`
  produces a workflow that shadows its parent by name in the project
  layer (§ 2).
- The `@major.minor` pin must prefix-match the parent's semver, or
  flatten refuses.

The flattened output carries a `provenance` block (`extends` ref, the
parent's full version, and a `sha256:` hash over both sources) stamped by
the flattener. `flatten --check` recomputes the composition from the
sources and exits 1 when the on-disk flattened file no longer matches —
wire it wherever the project lints. Hand-authored workflows must not
declare `provenance`.

## 4. `mustPass` check types

| Type | Required fields | Default severity | Behavior |
| --- | --- | --- | --- |
| `fileExists` | `path` | blocking | Pass if file exists on disk. Weak — a stub file satisfies it. |
| `fileMatches` | `path`, `pattern` (regex) | blocking | Pass if the file exists and matches the pattern. Weak — a regex match does not imply real content. |
| `commandSucceeds` | `command` | blocking | **Strong.** Pass if the shell command exits 0. |
| `stepSummaryMatches` | `step`, `pattern` (regex) | **advisory** | Pass if the named step's summary matches the pattern. Default-advisory because a summary is a freeform string the executor authored; matching it cannot prove the underlying work. |
| `artifactValid` | `path`, `artifact` | blocking | **Strong.** Pass if frontmatter parses and satisfies the named artifact schema. |
| `artifactSchemaStrict` | `path`, `artifact`, optional `minBodyChars`, `rejectAdditionalProperties` | blocking | **Strong.** Like `artifactValid` plus: requires `minBodyChars` (default 200) of substantive non-heading content and (by default) rejects frontmatter fields not declared in the schema. Catches hollow stub artifacts. |
| `diffConstraint` | at least one of `filesChanged`, `linesChanged`, `pathAllowlist`, `pathBlocklist`; optional `since` ref | blocking | **Strong.** Bounds the worktree (or ranged-diff) effect of the workflow. `filesChanged.min` proves *something* changed; `.max` and `pathAllowlist` prove the agent did not run away. Untracked files are counted. |
| `appStarts` | optional `lang` (which `smoke.<lang>` recipe; required when several exist) | blocking | **Strong.** Boot-verifies the app from the frozen project snapshot's `smoke.<lang>` recipe (start command, then HTTP path / boot-log pattern / TCP port readiness, within `timeout_seconds`). Resolves **`not-applicable`** — reported in the result's `not_applicable` array, never pausing — when the repo declares no matching recipe or the recipe's `credentials_file` is absent on this machine. Tests passing does not imply the app runs; this gate closes that gap. |
| `connectorAvailable` | `capability`; optional `provider` pin | blocking | Pass iff the capability has a provider configured in `.polymath/capabilities.yaml` (and an adapter plugin resolves). Pass/fail only — use it in `guards:` to stop a connector-dependent workflow before any work. A static presence probe; not the out-of-scope connector *events* (§ 7). |
| `command` (in guards) | `command` | blocking | Pre-step precondition (any check type except `stepSummaryMatches` is legal in `guards:` — no step summaries exist before any step has run; `command` is the common one). |

Recognised artifact names for `artifactValid` / `artifactSchemaStrict`:

`PRD`, `ADR`, `Plan`, `RFC`, `Runbook`, `ArchitectureDoc`,
`DACIDecision`, `TradeoffMatrix`, `Postmortem`, `ThreatModel`,
`PRDescription`. Each is backed by a JSON schema under
[`registry/schemas/artifacts/`](../registry/schemas/artifacts/).

### 4.1 Severity

Every check accepts an optional `severity: advisory | blocking`.
Blocking checks (the default for everything except
`stepSummaryMatches`) pause the workflow on failure. Advisory checks
run, report their failure in the `advisories` array of the run
result, but do **not** pause.

A workflow should have at least one strong-deterministic blocking
gate — one of `commandSucceeds`, `artifactValid`,
`artifactSchemaStrict`, `diffConstraint`, or `appStarts`.
`polymath-flow validate` emits a warning when this is missing, because a
workflow whose only blockers are `fileExists` / `fileMatches` / advisory
`stepSummaryMatches` can pass on a hollow run (stub files plus a
regex-matching summary).

### 4.2 Guards

`guards:` run at `start`, after validation and capability resolution but
**before any run state is created**. A failing blocking guard prints
`{"status": "guard-failed", "failures": [...]}` and exits 2 without
creating a run directory; advisory guard failures are reported on the
start payload (`guard_advisories`) and the run proceeds.
`not-applicable` guard outcomes (e.g. `appStarts` with no smoke recipe)
are reported (`not_applicable`) and never block.

## 5. Placeholders

- `${inputs.<name>}` — user-supplied input.
- `${workflow.slug}` — auto-derived kebab-case slug from `${inputs.title}`.
- `${workflow.id}` — full workflow run ID (timestamp + slug).
- `${capabilities.<cap>.provider}` — provider token resolved from
  `.polymath/capabilities.yaml` (e.g. `datadog`).
- `${capabilities.<cap>.plugin}` — adapter plugin name resolved from
  the same file (e.g. `polymath-observability`).
- `${project.<dotted.path>}` — value from the project-context snapshot
  (`.polymath/project.yaml` as loaded by polymath-core), e.g.
  `${project.stack.languages.0.lang}`. Numeric segments index lists;
  mappings/lists render as compact JSON. The snapshot is frozen into
  the run state at `start`, like the capability map.
- `${project.<dotted.path>:-fallback}` — same, with a fallback used
  when the path misses or no snapshot exists. **Marketplace workflows
  must use this form** — a repo without `.polymath/project.yaml` has no
  snapshot, and the bare form stays in the prompt as a literal.
  `polymath-flow validate` warns on bare `${project.*}`; the bare form
  is for project/org-layer workflows where the config is known to
  exist. The fallback text cannot contain `}`.

The `invoke` field of a step accepts capability placeholders as well,
so a workflow can be provider-agnostic by writing
`${capabilities.observability.plugin}:query-during-incident` instead
of a hard-coded connector plugin name. See
[`docs/CAPABILITIES.md`](CAPABILITIES.md). `${project.*}` expands in
`prompt`, `artifacts`, and mustPass `path`/`command` — not in `invoke`.

`invoke` also accepts the form `agent:<plugin>:<name>` to label a
forked-context agent (`plugins/<plugin>/agents/<name>.md`) instead of a
skill — e.g. `agent:polymath-thinking:architecture-critic` for an
adversarial design-review step. Like every invoke, it is a routing
label, not a programmatic call; `tools/check-workflow-invokes.py`
resolves it against the agent definition and fails on a dangling label.

## 6. State

Each run gets a directory under
`${CLAUDE_PLUGIN_DATA}/polymath-flows/workflows/`:

```text
${CLAUDE_PLUGIN_DATA}/polymath-flows/workflows/2026-05-23T14-22-shipFeature-rate-limit/
  ├── state.json
  ├── inputs.json
  ├── trace.jsonl
  ├── step-summaries/<step-id>.md
  └── artifacts/
```

`state.json` also persists the resolved `capabilities` map and the
`effective_plugins` list when the workflow declares
`requires.capabilities`, so the run is stable against mid-flight
changes to `.polymath/capabilities.yaml`.

State transitions are owned by
`plugins/polymath-flows/bin/polymath-flow`. The skills (`run-workflow`,
`resume-workflow`, `list-workflows`) call this executable.

## 7. Out of scope

- Parallel steps.
- Agent panels.
- Connector events (`wait-for-event`) — *waiting on* a connector is out of
  scope; checking that a connector is *configured* is the supported
  `connectorAvailable` gate (§ 4).
- Shell steps that mutate infrastructure.
- AI-based cross-artifact alignment as a blocking gate.
- Real PR creation through GitHub (the `pr` skill drafts only;
  `polymath-vcs:open-pr` opens the PR through the MCP).
