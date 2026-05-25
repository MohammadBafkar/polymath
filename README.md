# Polymath

> A public, open-source Claude Code marketplace of work-shaped plugins covering the full lifecycle of building software products — from idea to incident, from thinking-craft to platform engineering. Installable a-la-carte.

## The marketplace

**71 plugins** across foundation, mind & craft, product, engineering, languages, quality & safety, platform & operate, infra, people & content, connectors, orchestration, and authoring. **15 workflows** that compose those plugins into proven SDLC scenarios — `shipFeature`, `reviewPR`, `respondToIncident`, `bugTriage`, `perfRegression`, `refactorWithSafety`, `securityFinding`, `bumpDependency`, `migrateLanguageVersion`, `sunsetCapability`, `featureFromIdea`, `experimentToGA`, `weeklyReleaseTrain`, `incidentRetroToActions`, `deprecationToRemoval`.

Install only what you need. Per-plugin always-on listing cost stays under 400 tokens; the canonical CLI-measured total across all plugins is ~6.6 k — for users who install everything. Most teams install 5–10.

## Quick start

```bash
# 1. Add the marketplace from this checkout (or its GitHub URL)
claude plugin marketplace add /path/to/polymath

# 2. Install a starter set
claude plugin install \
  polymath-core@polymath polymath-engineering@polymath \
  polymath-release@polymath polymath-flows@polymath

# 3. Run a workflow
claude
> /polymath-flows:run-workflow shipFeature title="Rate-limit /login" scope=small
```

The full catalog is at [docs/site/index.html](docs/site/index.html) (also published as the marketplace's GitHub Pages site).

## Catalog by tier

- **Foundation** — `polymath-core` (conventions, glossary, plugin-budget, SessionStart hook).
- **Mind & craft** — `polymath-thinking`, `polymath-planning`, `polymath-writing`, `polymath-decisions`, `polymath-learning`.
- **Product & discovery** — `polymath-product`, `polymath-research`, `polymath-design`.
- **Engineering** — `polymath-engineering`, `polymath-frontend`, `polymath-backend`, `polymath-mobile`, `polymath-data`, `polymath-ai`.
- **Languages** — `polymath-lang-python`, `-typescript`, `-dotnet`, `-go`, `-rust`, `-java`, `-swift`, `-kotlin`, `-ruby`, `-php`.
- **Quality & safety** — `polymath-qa`, `polymath-security`, `polymath-performance`.
- **Platform & operate** — `polymath-platform`, `polymath-devops`, `polymath-sre`, `polymath-observability`, `polymath-incident`, `polymath-release`.
- **Infra** — `polymath-infra-kubernetes`, `-docker`, `-postgres`, `-redis`, `-aws`, `-gcp`, `-azure`, `-terraform-stack`.
- **People & content** — `polymath-communication`, `polymath-leadership`, `polymath-content`.
- **Connectors (MCP + hooks; some are CLI-only)** — `polymath-connector-github`, `-github-actions`, `-jira`, `-pagerduty`, `-datadog`, `-snyk`, `-slack`, `-sentry`, `-linear`, `-launchdarkly`, `-statuspage`, `-terraform`, `-figma`, `-notion`, `-asana`, `-aws`, `-gcp`, `-azure`, `-stripe`, `-vercel`, `-cloudflare`, `-elastic`, `-grafana`, `-honeycomb`.
- **Orchestration** — `polymath-flows` (the workflow runner).
- **Authoring** — `polymath-author` (governance + scaffolders + skill review).

## Design principles

- **Work-shaped plugins.** One role / lifecycle stage / language / target per plugin. Not primitive-shaped catch-alls.
- **Token budget discipline.** ≤ 400 tokens always-on per plugin; the CLI's `claude plugin details` is the authoritative measurement, the heuristic in `tools/token-budget.sh` is informational.
- **Commands vs. skills.** Skills bundle templates / scripts / references. Commands are thin aliases (≤ 20 lines).
- **Agents only when justified.** Reserved for forked context or panel critique. No custom agents without a no-agent baseline evidence record and a golden fixture proving the forked context is load-bearing.
- **Workflows are YAML.** Driven by a deterministic executable (`polymath-flows/bin/polymath-flow`) that owns validation, state, and `mustPass` checks. The skill drives the loop; the script owns state.
- **Deterministic enforcement.** `mustPass:` types: `fileExists`, `fileMatches`, `commandSucceeds`, `stepSummaryMatches`, `artifactValid` (validates artifact frontmatter against `shared/schemas/artifacts/<Name>.schema.json`). AI cross-checks are advisory.
- **Proof before promotion.** Marketplace `status` (`stable`, `beta`, `experimental`, `deprecated`) is enforced in conformance. Stable promotion requires strong gates, live fixture evidence, and real external use.
- **Bakeoffs over vibes.** `tools/bakeoff.py` compares baseline Claude Code against Polymath on scored cases before claiming outcome quality.
- **Each plugin owns its templates.** Artifact templates live under `plugins/<plugin>/templates/`. Frontmatter on canonical artifacts (PRD, ADR, Postmortem, ThreatModel) is gated by the matching JSON schema.
- **Connectors share a shape.** `.mcp.json` for the upstream MCP server, `userConfig` for credentials (`sensitive: true`), hooks for event-driven reactions, a `references/<service>-tools.md` doc.
- **No native scheduler.** Recurring work lives in external schedulers (Cloud Routines, GitHub Actions, OS cron) that write to a queue file the `polymath-core` SessionStart hook surfaces.
- **No telemetry.** See [docs/PRIVACY.md](docs/PRIVACY.md).

## Repo layout

```text
polymath/
├── .claude-plugin/marketplace.json
├── plugins/                          # one directory per plugin
│   └── polymath-<name>/
│       ├── .claude-plugin/plugin.json
│       ├── skills/<skill>/SKILL.md
│       ├── templates/                # plugin-owned artifact templates
│       ├── commands/<cmd>.md
│       ├── agents/<role>.md
│       ├── hooks/                    # event-driven hook scripts
│       ├── .mcp.json                 # connector plugins only
│       ├── workflows/*.yaml          # polymath-flows only
│       ├── README.md, CHANGELOG.md
│       └── tests/
├── shared/schemas/                   # workflow + artifact + conformance schemas
├── tools/                            # scaffolders, validators, conformance, catalog generator
├── tests/golden/                     # one fixture per plugin + one per workflow
├── docs/                             # PLUGIN-AUTHORING, WORKFLOW-SCHEMA, CONTRIBUTING, PRIVACY
└── .github/workflows/                # validate, token-budget, lint, link-check, golden-tests, pages, release
```

See [docs/PLUGIN-AUTHORING.md](docs/PLUGIN-AUTHORING.md) and [docs/WORKFLOW-SCHEMA.md](docs/WORKFLOW-SCHEMA.md).

## Gates

Every change runs locally and in CI:

- `tools/validate-all.sh` — `claude plugin validate --strict` per plugin.
- `tools/lint-skills.sh` — description ≤ 200 chars, SKILL.md ≤ 500 lines.
- `tools/token-budget.sh` — per-plugin cap of 400 tokens; total target scales with plugin count.
- `tools/conformance.sh --all` — structural check, including `MANIFEST-3` (maturity tier declared in `marketplace.json`), `CONNECTOR-2` (connector / lang / infra plugins audited in `docs/CONNECTOR-POLICY.md`), and `AGENT-1` (every agent has baseline evidence + golden fixture).
- `tools/build-catalog.py --check` — verifies the GitHub Pages catalog regenerates reproducibly.
- `bin/polymath-flow validate` — every workflow YAML against the schema.
- `python3 -m unittest discover -s plugins/polymath-flows/tests` — executable unit tests.
- `tools/check-agent-evidence.py` — every agent has baseline evidence + a golden fixture.
- `tools/bakeoff.py check` — baseline-vs-Polymath quality cases are parseable and scored out of 10.

The `claude-cli-fixtures` CI job runs `tests/golden/run-fixtures.sh` against the Claude Code CLI on every push to `main`. The job requires `CLAUDE_CODE_OAUTH_TOKEN` (preferred — Claude.ai subscription) or `ANTHROPIC_API_KEY` to be set in repo secrets, and **hard-fails** main-branch pushes when no auth is present. PR jobs without secrets (e.g. fork PRs) emit a warning and skip the live run. Setup instructions are in [LIMITATIONS.md § 4.1](LIMITATIONS.md#41-how-to-provide-the-key).

## Quality

- [`docs/EVIDENCE/bakeoff-runs/2026-05-25/`](docs/EVIDENCE/bakeoff-runs/2026-05-25/SUMMARY.md) — first published bakeoff: **8 of 9** pre-registered cases pass the 9+ threshold (Polymath ≥ 8/10 and Δ ≥ 2 over baseline), 1 tie, 0 losses, aggregate +25 rubric points.
- [`docs/QUALITY-SCORECARD.md`](docs/QUALITY-SCORECARD.md) — the explicit promotion bar to 9+ and the proof loop.
- [`LIMITATIONS.md`](LIMITATIONS.md) — what Polymath doesn't yet prove, where official tools beat it, what would change this file. Read this before the catalog if you care about depth.
- [`docs/CONNECTOR-POLICY.md`](docs/CONNECTOR-POLICY.md) — the per-plugin audit for every `polymath-connector-*`, `polymath-lang-*`, and `polymath-infra-*` plugin. Records (a) whether an official MCP / LSP exists, (b) what Polymath adds, (c) the sunset trigger.

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) and [polymath-author](plugins/polymath-author/) — the meta-plugin that scaffolds new plugins, validates them against every gate, reviews SKILL.md quality, and measures the listing-token cost.

## License

[Apache-2.0](LICENSE).
