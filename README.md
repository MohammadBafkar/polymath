# Polymath

> A public, open-source Claude Code marketplace of work-shaped plugins covering the full lifecycle of building software products — from idea to incident, from thinking-craft to platform engineering. Installable a-la-carte.

## The marketplace

**36 plugins** across foundation, mind & craft, product & discovery, engineering, quality & safety, platform & operate, infra, people & content, connectors, orchestration, and authoring. **26 workflows** compose those plugins into SDLC journeys such as `activateProject`, `reviewPR`, `shipFeature`, `respondToIncident`, `designSystem`, `refactorWithSafety`, `securityFinding`, `bumpDependency`, `migrateLanguageVersion`, `experimentToGA`, `weeklyReleaseTrain`, and `deprecationToRemoval`.

Install only what you need. Per-plugin always-on listing cost stays under 400 tokens. Most teams install 5–10.

## Start with a journey, not a plugin

The unit of value is the **workflow** — an end-to-end SDLC arc that composes
plugins for you. Reach for one of these before hand-picking plugins; run with
`/polymath-flows:run-workflow <name>` (or just describe the task and let
`polymath-core:route` propose one):

| Journey | When to run it |
| --- | --- |
| `featureFromIdea` | Discovery (interviews/persona) then ship a feature. |
| `shipFeature` / `prdToShip` | Ship a small feature from PRD to PR draft. |
| `reviewPR` | Multi-critic review of a PR/diff + synthesis. |
| `respondToIncident` | Drive a live incident end-to-end to postmortem. |
| `rootCauseAnalysis` | Drive to a system root cause; write an RCA. |
| `designSystem` | Design a system: arch doc + threat model + ADR. |
| `decideUnderAmbiguity` | Frame a hard decision, govern it, record an ADR. |
| `refactorWithSafety` | Pin behavior in tests, then refactor safely. |
| `securityFinding` | Fix a security finding end-to-end and verify. |
| `bumpDependency` | Upgrade one dependency safely and fix call-sites. |
| `progressiveRollout` | Flag rollout with SLO health gates. |
| `weeklyReleaseTrain` | Cut a release: notes, verify, tag PR. |

Full list (27): `/polymath-flows:list-workflows`, or see [`plugins/polymath-flows/workflows/`](plugins/polymath-flows/workflows/).

## Quick start

```bash
# 1. Add the marketplace from this checkout (or its GitHub URL)
claude plugin marketplace add /path/to/polymath

# 2. Install a starter set
claude plugin install \
  polymath-core@polymath polymath-engineering@polymath \
  polymath-release@polymath polymath-flows@polymath

# 3. Route a prompt or run a workflow
claude
> /polymath-core:route "Review this PR for correctness, security, and missing tests"
> /polymath-flows:run-workflow shipFeature title="Rate-limit /login" scope=small
```

### Install profiles

Picking a handful of plugins out of 36 is the real first hurdle. Install
profiles in [`registry/polymath-profiles.json`](registry/polymath-profiles.json)
are curated role spines — install one, then add more a-la-carte on top. Every
profile implicitly includes the `polymath-core` + `polymath-flows` spine.

| Profile | For | Adds (beyond the core+flows spine) |
| --- | --- | --- |
| `backend` | API/service devs | engineering, backend, qa, security, release, vcs |
| `frontend` | Web/UI devs | engineering, frontend, design, qa, release, vcs |
| `sre` | Reliability / on-call | sre, observability, incident, performance, paging, chat |
| `platform` | Platform / DevOps | platform, devops, cloud, kubernetes, sre, release |
| `pm` | Product managers | product, research, planning, communication, decisions, tracker |
| `staff` | Staff+ / tech leads | thinking, decisions, writing, planning, engineering, communication, leadership |
| `author` | Plugin authors | author, engineering, writing |

```bash
# e.g. the backend spine
claude plugin install \
  polymath-core@polymath polymath-flows@polymath \
  polymath-engineering@polymath polymath-backend@polymath \
  polymath-qa@polymath polymath-security@polymath \
  polymath-release@polymath polymath-vcs@polymath
```

For a new target repository, run `/polymath-core:init-project` or
`/polymath-flows:run-workflow activateProject` first. It creates
`.polymath/project.yaml`, maps known capability providers, and writes
`docs/POLYMATH-ONBOARDING.md` so agents know the stack, conventions,
required tools, environment variables, recommended plugins, and first
steps. See [`docs/POLYMATH-ONBOARDING.md`](docs/POLYMATH-ONBOARDING.md).

The full catalog is published as the marketplace's GitHub Pages site under `docs/site/`.

## Catalog by tier

- **Foundation** — `polymath-core` (route prompts, conventions, glossary, project initialization, project-context loader, plugin-budget, SessionStart hook).
- **Mind & craft** — `polymath-thinking`, `polymath-planning`, `polymath-writing`, `polymath-decisions`, `polymath-learning`.
- **Product & discovery** — `polymath-product`, `polymath-research`, `polymath-design`.
- **Engineering** — `polymath-engineering`, `polymath-frontend`, `polymath-backend`, `polymath-mobile`, `polymath-data`, `polymath-ai`.
- **Quality & safety** — `polymath-qa`, `polymath-security`, `polymath-performance`.
- **Platform & operate** — `polymath-platform`, `polymath-devops`, `polymath-sre`, `polymath-observability`, `polymath-incident`, `polymath-release`.
- **Infra** — `polymath-kubernetes`, `polymath-cloud` (Postgres migration/config craft now lives in `polymath-backend`).
- **People & content** — `polymath-communication` (internal + customer-facing prose), `polymath-leadership`.
- **Connectors (MCP + hooks, by capability)** — `polymath-vcs`, `-tracker` (Jira + Linear), `-observability` (Datadog + Grafana + Honeycomb + Elastic), `-pagerduty`, `-snyk`, `-slack`, `-sentry`, `-statuspage`, `-terraform`.
- **Orchestration** — `polymath-flows`.
- **Authoring** — `polymath-author`.

For language-specific depth (`.NET`, Python, Laravel, …), Polymath defers to external skill catalogs such as [dotnet/skills](https://github.com/dotnet/skills) and [Laravel Boost](https://laravel.com/docs/12.x/boost). `.polymath/project.yaml` declares the external sources the project recommends and `polymath-engineering:verify-change` adapts to the project's language at runtime.

## Design principles

- **Work-shaped plugins.** One role / lifecycle stage / target per plugin. Not primitive-shaped catch-alls.
- **Token budget discipline.** ≤ 400 tokens always-on per plugin; the CLI's `claude plugin details` is the authoritative measurement, the heuristic in `tools/token-budget.sh` is informational.
- **Commands vs. skills.** Skills bundle templates / scripts / references. Commands are thin aliases (≤ 20 lines).
- **Agents only when justified.** Reserved for forked context or panel critique.
- **Workflows are YAML.** Driven by a deterministic executable (`polymath-flows/bin/polymath-flow`) that owns validation, state, and `mustPass` checks. The skill drives the loop; the script owns state.
- **Deterministic enforcement.** `mustPass:` types: `fileExists`, `fileMatches`, `commandSucceeds`, `stepSummaryMatches`, `command`, `artifactValid`, `artifactSchemaStrict`, `diffConstraint`. AI cross-checks are advisory.
- **Capability abstraction.** Workflows declare *what* they need (issue tracker, observability, pager, vulnerability scanner) via `requires.capabilities`. Projects pick the provider once in `.polymath/capabilities.yaml`. See [`docs/CAPABILITIES.md`](docs/CAPABILITIES.md).
- **Project localization.** `.polymath/project.yaml` describes the project's stack, conventions, external skill catalogs, and per-skill overrides. The SessionStart hook loads it and exposes a resolved snapshot to every skill. See [`docs/PROJECT-LOCALIZATION.md`](docs/PROJECT-LOCALIZATION.md).
- **Each plugin owns its templates.** Artifact templates live under `plugins/<plugin>/templates/`. Frontmatter on canonical artifacts (PRD, ADR, Plan, RFC, Runbook, ArchitectureDoc, DACIDecision, TradeoffMatrix, Postmortem, ThreatModel, PRDescription) is gated by the matching JSON schema.
- **Connectors share a shape.** `.mcp.json` for the upstream MCP server, `userConfig` for credentials (`sensitive: true`), hooks for event-driven reactions, a `references/<service>-tools.md` doc.
- **No native scheduler.** Recurring work lives in external schedulers (Cloud Routines, GitHub Actions, OS cron) that write to a queue file the `polymath-core` SessionStart hook surfaces.
- **No telemetry.** See [docs/PRIVACY.md](docs/PRIVACY.md).
- **agentskills.io v1.0 compatible.** Skills are portable across any harness implementing the open standard (Claude Code, Codex, Cursor, Gemini CLI, Goose, JetBrains Junie).

## Repo layout

```text
polymath/
├── .claude-plugin/marketplace.json
├── .polymath/                          # project-context + capabilities examples
├── plugins/                            # one directory per plugin
│   └── polymath-<name>/
│       ├── .claude-plugin/plugin.json
│       ├── skills/<skill>/SKILL.md
│       ├── templates/                  # plugin-owned artifact templates
│       ├── commands/<cmd>.md
│       ├── agents/<role>.md
│       ├── hooks/                      # event-driven hook scripts
│       ├── .mcp.json                   # connector plugins only
│       ├── workflows/*.yaml            # polymath-flows only
│       ├── bin/                        # bundled executables (polymath-flow, scaffolders)
│       ├── README.md, CHANGELOG.md
│       └── tests/
├── registry/schemas/                     # workflow + artifact + capability + project + conformance schemas
├── tools/                              # scaffolders, validators, conformance, catalog, bakeoff, token analyzer
├── tests/
│   ├── golden/                         # fixtures per plugin / workflow
│   ├── bakeoff/                        # per-plugin/scenario bakeoff cases
│   └── skill-triggering/               # naive-prompt triggering tests per skill
├── docs/                               # CAPABILITIES, PROJECT-LOCALIZATION, PLUGIN-AUTHORING, WORKFLOW-SCHEMA, …
└── .github/workflows/                  # validate, token-budget, lint, link-check, golden-tests, evaluation, pages, release
```

See [docs/PLUGIN-AUTHORING.md](docs/PLUGIN-AUTHORING.md) and [docs/WORKFLOW-SCHEMA.md](docs/WORKFLOW-SCHEMA.md).

## Gates

Every change runs locally and in CI:

- `tools/validate-all.sh` — `claude plugin validate --strict` at marketplace root + per plugin; catches version drift between a marketplace entry and its `plugin.json`.
- `tools/lint-skills.sh` — description ≤ 200 chars, SKILL.md ≤ 500 lines.
- `tools/token-budget.sh` — per-plugin cap of 400 tokens; total target scales with plugin count.
- `tools/conformance.sh --all` — structural check, including `MANIFEST-3` (maturity tier in `registry/polymath-catalog.json`), `INTEGRATION-2` (connector / infra plugins audited in `docs/INTEGRATION-POLICY.md`), `SKILL-1`, `TEMPLATE-1`, `WORKFLOW-1`, `FIXTURE-1`. The cross-check via `tools/check-catalog.py` verifies plugin sets and versions agree across `marketplace.json`, every `plugin.json`, and `registry/polymath-catalog.json`.
- `tools/build-catalog.py --check` — verifies the GitHub Pages catalog regenerates reproducibly.
- `plugins/polymath-flows/bin/polymath-flow validate` — every workflow YAML against the schema.
- `python3 -m unittest discover -s plugins/polymath-flows/tests` and `-s plugins/polymath-core/tests` — executable unit tests.
- `tools/bakeoff.py check` — baseline-vs-Polymath quality cases are parseable; optional `--judge` mode scores with an LLM judge.
- `tools/skill-triggering.py check` — every skill-triggering test's frontmatter is valid.

The `claude-cli-fixtures` job runs `tests/golden/run-fixtures.sh` against the Claude Code CLI on every push to `main`. The job requires `CLAUDE_CODE_OAUTH_TOKEN` (preferred — Claude.ai subscription) or `ANTHROPIC_API_KEY` set in repo secrets, and **hard-fails** main-branch pushes when no auth is present. PR jobs without secrets (e.g. fork PRs) emit a warning and skip the live run.

## Quality

- [`docs/QUALITY-SCORECARD.md`](docs/QUALITY-SCORECARD.md) — the gates, what gets measured, where the artifacts land, and the proof loop.
- [`docs/INTEGRATION-POLICY.md`](docs/INTEGRATION-POLICY.md) — per-plugin audit for every integration plugin (one shipping a `.mcp.json` / `bindings/`) and infra plugin. Records (a) whether an official MCP / LSP exists, (b) what Polymath adds, (c) the sunset trigger.
- [`docs/POLYMATH-ONBOARDING.md`](docs/POLYMATH-ONBOARDING.md) — first-run setup, project activation, env vars, plugin sets, workflows, and portability notes.

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) and [polymath-author](plugins/polymath-author/) — the meta-plugin that scaffolds new plugins, validates them against every gate, reviews `SKILL.md` quality, and measures the listing-token cost.

## Use outside Claude Code

Polymath skills are written to the [agentskills.io v1.0](https://agentskills.io) standard. Export the portable skills bundle and drop it into Codex CLI, Cursor, GitHub Copilot, VS Code, Gemini CLI, Goose, JetBrains Junie, and other listed clients:

```bash
python3 tools/export-agents-skills.py --clean
# → dist/agents-skills/<plugin>-<skill>/SKILL.md + manifest.json
```

See [docs/PORTABILITY.md](docs/PORTABILITY.md) for the drop-location per harness and the honest list of surfaces that do **not** port (commands, hooks, MCP config, workflows, agents).

## License

[MIT](LICENSE).
