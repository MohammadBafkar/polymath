# Polymath onboarding

Two audiences read this file:

- **Installing Polymath into your own repo?** Read [Install](#install) →
  [Activate your repo](#activate-your-repo). Activation generates a
  `docs/polymath-onboarding.md` tailored to *your* project — the
  [Maintaining this marketplace](#maintaining-this-marketplace) section at the
  bottom is for contributors to Polymath itself, not for you.
- **Contributing to this marketplace?** Read the whole file.

## Install

```bash
claude plugin marketplace add /path/to/polymath
```

`polymath-core` is **required** — the SessionStart hook and project-context
loader live there. `polymath-flows` is **required only if you want workflows**.
Everything else is opt-in. Pick the persona closest to your need:

### Persona — code review + shipping

```bash
claude plugin install \
  polymath-core@polymath \
  polymath-engineering@polymath \
  polymath-release@polymath \
  polymath-flows@polymath
```

- `polymath-core` — required foundation (project context, conventions, `doctor`).
- `polymath-engineering` — code review, reading unfamiliar code, verifying changes.
- `polymath-release` — commit messages, PR descriptions, changelog, release notes.
- `polymath-flows` — runs the `reviewPR` and `shipFeature` workflows.

### Persona — full SDLC

```bash
claude plugin install \
  polymath-core@polymath \
  polymath-author@polymath \
  polymath-flows@polymath \
  polymath-thinking@polymath \
  polymath-planning@polymath \
  polymath-decisions@polymath \
  polymath-engineering@polymath \
  polymath-release@polymath
```

Adds `polymath-thinking` / `polymath-planning` / `polymath-decisions` (the
reasoning, breakdown, and decision skills the design/RCA/planning workflows
compose) and `polymath-author` (scaffolders for new plugins/skills/workflows).

### Persona — thinking & planning only

```bash
claude plugin install \
  polymath-core@polymath \
  polymath-thinking@polymath \
  polymath-planning@polymath \
  polymath-decisions@polymath \
  polymath-flows@polymath
```

The lightest set that still runs `deliberationLoop`, `decideUnderAmbiguity`,
`rootCauseAnalysis`, and `fuzzyGoalToPlan`.

## Activate your repo

From the target repository:

```text
/polymath-core:doctor        # optional preflight — confirms your tools are ready
/polymath-core:init-project  # works with only polymath-core installed
```

or, if you installed `polymath-flows` and want validation gates:

```text
/polymath-flows:run-workflow activateProject
```

> Use `/polymath-core:init-project` if you installed only `polymath-core`. Use
> the `activateProject` workflow only if `polymath-flows` is installed — it adds
> `mustPass` gates but depends on the flows runner.

Activation reads README files, `AGENTS.md`, `CLAUDE.md`, docs, CI, package
manifests, and deployment files, then writes:

- `.polymath/project.yaml` — stack, conventions, setup, recommended plugins, skill overrides.
- `.polymath/capabilities.yaml` — provider mappings (GitHub, Jira, Datadog, …) when confidently inferred.
- `docs/polymath-onboarding.md` — *your* project's first steps, tools, env vars, workflows, and open questions.

If you skip activation, a fresh session in an un-initialized repo prints one
suppressible line pointing you here.

## Required local tools

| Tool | Need | Check |
| --- | --- | --- |
| `bash` | required | `bash --version` |
| `python3` | required | `python3 --version` |
| `git` | recommended | `git --version` |
| `claude` | recommended | `claude --version` |
| PyYAML | optional | `python3 -c 'import yaml'` |
| `jq` | optional | `jq --version` |

`/polymath-core:doctor` runs these checks and reports PASS/WARN/FAIL with fix
hints. `python3` powers the hooks, the project-context loader, and the tooling;
the loader falls back to a minimal parser when PyYAML is absent. `jq` is **not**
required by Polymath — it is handy only for hand-inspecting JSON snapshots. The
`claude` CLI is needed for `claude plugin validate --strict` and live golden
fixtures.

## Environment variables

Never store secret values in `.polymath/project.yaml` — only names and purposes.

| Variable | Required | Purpose |
| --- | --- | --- |
| `CLAUDE_CODE_OAUTH_TOKEN` | optional | Preferred auth for live Claude CLI golden fixtures in CI. |
| `ANTHROPIC_API_KEY` | optional | Fallback auth for live Claude CLI fixtures. |
| `GITHUB_TOKEN` | optional | Release, PR, and Pages automation when publishing the marketplace. |

## Useful workflows

| Workflow | Use |
| --- | --- |
| `activateProject` | Generate project context, capability mapping, and onboarding notes. |
| `deliberationLoop` | Observe, frame, compare options, critique, and write a revised plan. |
| `decideUnderAmbiguity` | Frame the context, ledger the unknowns, compare, govern, and record a decision. |
| `rootCauseAnalysis` | Drill to a system root cause, anticipate fix failure, challenge the cause, synthesize. |
| `fuzzyGoalToPlan` | Disambiguate a vague goal into a story map, breakdown, estimate, and plan. |
| `designSystem` | Orient, frame, deliberate, trade off, document, threat-model, and challenge a design. |
| `shipFeature` | PRD → acceptance criteria → implementation → PR draft. |
| `reviewPR` | Multi-axis review: correctness, coverage, security, and challenge passes. |

## Capability mapping

Workflows declare what they need; projects choose providers once:

```yaml
schemaVersion: 1
capabilities:
  vcs:
    provider: github
  ci:
    provider: github_actions
  issue_tracker:
    provider: github_issues
```

Configure only providers the project actually uses. Unknown providers should be
captured as open questions, not guessed.

## Agent compatibility

Skills are portable through the agentskills.io format. Commands, hooks,
workflows, and MCP connector config are Claude Code surfaces today.

| Surface | Portable to other agents | Notes |
| --- | --- | --- |
| Skills | yes | Export with `python3 tools/export-agents-skills.py --clean`. |
| Templates and references | mostly | Travel with skills when bundled or copied. |
| Commands | no | Claude Code slash-command surface. |
| Hooks | no | Claude Code hook lifecycle. |
| Workflows | no | The YAML is readable elsewhere, but only the bundled `polymath-flows` runner executes it. |
| MCP config | partial | Depends on target agent MCP support. |

> On a non-Claude agent, `init-project` (a command), `activateProject` (a
> workflow), and automatic project-context loading (a hook) do **not** run.
> Export the skills with `tools/export-agents-skills.py` and create
> `.polymath/project.yaml` by hand from the schema.

See [PORTABILITY.md](PORTABILITY.md) for current drop locations and limitations.

---

## Maintaining this marketplace

*This section is for contributors to Polymath itself. A downstream project's
generated `docs/polymath-onboarding.md` does not include it.*

Run these before opening a PR (CI enforces all of them):

```bash
tools/validate-all.sh
tools/lint-skills.sh
tools/token-budget.sh
tools/conformance.sh --all
tools/bakeoff.py check
tools/skill-triggering.py check
python3 -m unittest discover -s plugins/polymath-core/tests
python3 -m unittest discover -s plugins/polymath-flows/tests
```
