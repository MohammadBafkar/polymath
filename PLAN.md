# Polymath — Plan

> A public, open-source Claude Code marketplace of work-shaped plugins covering the full lifecycle of building software products.

---

## 1. Mission

Curated, role-shaped extensions for Claude Code that real teams can install a-la-carte. Each plugin owns one role, one lifecycle stage, one language, one infra target, or one external service. The unit of trust, versioning, and token budget is the plugin.

---

## 2. Status snapshot

**71 plugins**, **12 workflows**, **all gates green**.

Tier coverage:

- Foundation, mind & craft, product, engineering, languages, quality, operate, people, orchestration, authoring — complete.
- Connectors — github, github-actions, jira, pagerduty, datadog, snyk, slack, sentry, linear, launchdarkly, statuspage, terraform, figma, notion, asana, aws, gcp, azure, stripe, vercel, cloudflare, elastic, grafana, honeycomb.
- Languages — python, typescript, dotnet, go, rust, java, swift, kotlin, ruby, php.
- Infra — docker, postgres, redis, kubernetes, aws, gcp, azure, terraform-stack.

Workflows: `shipFeature`, `reviewPR`, `respondToIncident`, `bugTriage`, `perfRegression`, `refactorWithSafety`, `securityFinding`, `bumpDependency`, `migrateLanguageVersion`, `sunsetCapability`, `featureFromIdea`, `experimentToGA`.

Local gate measurements: 6,634 canonical listing tokens across 71 plugins (avg 93 / max < 400 cap). All `bin/polymath-flow` unit tests pass. `tools/conformance.sh --all` green. `tools/build-catalog.py --check` clean.

---

## 3. Design principles (load-bearing)

- **Plugins are work-shaped.** One role / lifecycle stage / language / target / service per plugin. Not primitive-shaped.
- **Per-plugin always-on cost ≤ 400 tokens** measured by `claude plugin details`. CLI is authoritative.
- **Commands are thin aliases (≤ 20 lines); skills bundle templates/scripts/references.** When both exist, the command points at the skill.
- **Agents are reserved.** Forked context or panel critique only; no custom agents without a golden fixture proving they outperform a skill.
- **Workflows are YAML driven by a deterministic executable.** `polymath-flows/bin/polymath-flow` owns validation, state, resumption, and `mustPass`. Skills drive the loop but never own state.
- **Enforcement is deterministic `mustPass:` checks.** Types: `fileExists`, `fileMatches`, `commandSucceeds`, `stepSummaryMatches`, `artifactValid`. AI cross-checks are advisory, never blocking.
- **Each plugin owns its templates** under `plugins/<plugin>/templates/`. Frontmatter on canonical artifacts (PRD, ADR, Postmortem, ThreatModel) is gated by JSON schemas in `shared/schemas/artifacts/`.
- **Connectors share a shape.** Either `.mcp.json` + `userConfig` (sensitive credentials) + optional event-driven hooks + `references/<service>-tools.md`, OR `polymath-cli-only` keyword for connectors that wrap a local CLI (terraform, aws, gcp, azure).
- **Three-layer workflow resolution.** project → user → marketplace.
- **No native scheduler.** Recurring work writes to `${CLAUDE_PLUGIN_DATA}/polymath-core/queue.json`; the SessionStart hook surfaces due items.
- **No telemetry.** See [docs/PRIVACY.md](docs/PRIVACY.md).
- **Claude Code only.** No Codex / Copilot / Cursor adapters until real demand surfaces.

---

## 4. Marketplace shape

### Catalog tiers

```text
Foundation    — polymath-core
Mind & craft  — polymath-thinking, polymath-planning, polymath-writing,
                polymath-decisions, polymath-learning
Product       — polymath-product, polymath-research, polymath-design
Engineering   — polymath-engineering, polymath-frontend, polymath-backend,
                polymath-mobile, polymath-data, polymath-ai
Languages     — polymath-lang-{python, typescript, dotnet, go, rust, java,
                swift, kotlin, ruby, php}
Quality       — polymath-qa, polymath-security, polymath-performance
Operate       — polymath-platform, polymath-devops, polymath-sre,
                polymath-observability, polymath-incident, polymath-release
Infra         — polymath-infra-{kubernetes, docker, postgres, redis,
                aws, gcp, azure, terraform-stack}
People        — polymath-communication, polymath-leadership, polymath-content
Connectors    — polymath-connector-{github, github-actions, jira, pagerduty,
                datadog, snyk, slack, sentry, linear, launchdarkly, statuspage,
                terraform, figma, notion, asana, aws, gcp, azure, stripe,
                vercel, cloudflare, elastic, grafana, honeycomb}
Orchestration — polymath-flows
Authoring     — polymath-author
```

### Workflows

```text
shipFeature            PRD → acceptance → implement → review → verify → changelog → PR draft
reviewPR               orient → 4 parallel critics (correctness, coverage, security, challenge) → synthesize
respondToIncident      page-context → triage → datadog signals → postmortem → file Jira bugs
bugTriage              5-whys → read-code → review-diff → work-breakdown
perfRegression         datadog signals → review-diff → fix → verify
refactorWithSafety     orient → coverage-gap → pin behavior with tests → refactor → verify → review
securityFinding        OWASP review → STRIDE model → implement → review → verify
bumpDependency         snyk triage → orient → smallest bump → review → verify
migrateLanguageVersion plan → PIN → FIX → verify per batch → STRICT → review
sunsetCapability       notice → deprecate-in-code → (remove at stage=remove) → verify → release-notes
featureFromIdea        interview-guide → persona → PRD → acceptance → implement → review → verify → PR
experimentToGA         plan (run-experiment, pre-registered) → rollout-plan (launchdarkly)
                       → launch-checklist → results-analysis → GA decision
```

### Repo layout

```text
polymath/
├── .claude-plugin/marketplace.json
├── plugins/<plugin>/
│   ├── .claude-plugin/plugin.json
│   ├── skills/<skill>/SKILL.md
│   ├── templates/                # plugin-owned artifact templates
│   ├── commands/<cmd>.md
│   ├── hooks/
│   ├── .mcp.json                 # connector plugins (unless polymath-cli-only)
│   ├── workflows/*.yaml          # polymath-flows only
│   ├── tests/, README.md, CHANGELOG.md
├── shared/schemas/               # workflow + artifact + conformance schemas
├── tools/                        # scaffolders, validators, conformance, catalog
├── tests/golden/                 # one fixture per plugin + one per workflow
├── docs/                         # PLUGIN-AUTHORING, WORKFLOW-SCHEMA, CONTRIBUTING, PRIVACY
└── .github/workflows/            # validate, token-budget, lint, link-check, golden-tests, pages, release
```

---

## 5. Orchestration (`flows-lite`)

`polymath-flows` provides:

1. **Skills** (`run-workflow`, `resume-workflow`, `list-workflows`) — drive the loop and perform Claude work for each step.
2. **Executable** (`bin/polymath-flow`) — validates YAML, owns state, evaluates `mustPass`. Python 3 stdlib-only with an embedded minimal YAML subset parser.

Workflows are serial. `topology: fanout` is accepted (and `reviewPR` declares it on its critic steps) but the executor still runs serially — fanout is a declaration of parallel intent for downstream tooling.

State layout: `${CLAUDE_PLUGIN_DATA}/polymath-flows/workflows/<run_id>/` with `state.json`, `inputs.json`, `trace.jsonl`, `budget.json`, `step-summaries/`.

See [docs/WORKFLOW-SCHEMA.md](docs/WORKFLOW-SCHEMA.md).

---

## 6. Verification gates

Local + CI:

- `tools/validate-all.sh` — `claude plugin validate --strict`.
- `tools/lint-skills.sh` — description ≤ 200 chars, SKILL.md ≤ 500 lines.
- `tools/token-budget.sh` — 400-tok per-plugin cap; total target scales as `max(1500, 250 × plugin_count)`.
- `tools/conformance.sh --all` — 12-criterion structural check (manifest, docs, skill discipline, templates with schema-required frontmatter, workflows, connector shape, fixtures, secrets).
- `tools/build-catalog.py --check` — catalog reproducibility.
- `bin/polymath-flow validate` — every workflow YAML.
- `python3 -m unittest discover -s plugins/polymath-flows/tests` — executable tests.

CI: `validate.yml`, `token-budget.yml`, `lint.yml`, `link-check.yml`, `golden-tests.yml` (executable-unit + executable-e2e + fixtures-parse jobs), `pages.yml`, `release.yml`.

Deferred: full multi-step `claude -p` runs of every workflow end-to-end. The `claude-cli-fixtures` job is wired and skips until `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` is in repo secrets.

---

## 7. Remaining work

### Operational

- Wire `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` into repo secrets so `claude-cli-fixtures` CI runs end-to-end fixtures.
- Submit proven plugins to the community marketplace once a few have demonstrably low-surprise behavior in real use.

### Future plugin candidates

(Add as concrete demand surfaces; do not pre-build.)

- Connectors: Microsoft Teams, Discord, BigQuery, Snowflake, Redshift, OpenTelemetry Collector, Sentry source-map upload, Vault.
- Languages: C++, Elixir, Scala, Clojure, Zig.
- Infra: Kafka, MongoDB, Elasticsearch (cluster ops, not connector), nginx config audit.
- Workflows: `weeklyReleaseTrain`, `incidentRetroToActions`, `deprecationToRemoval` (multi-quarter).

### Long-tail polish

- Live golden-fixture pass rate ≥ 90% (once secrets in place).
- README screenshots / asciinema for the top workflows.
- Cross-plugin compatibility matrix (which connectors pair with which workflows).

---

## 8. Locked-in decisions

These are stable; revisit only when a clear failure mode appears.

- Monorepo, Apache-2.0, public OSS from day one.
- Templates live in each plugin (no `shared/templates/`). JSON Schemas in `shared/schemas/artifacts/` validate frontmatter.
- Workflows are YAML; state owned by `bin/polymath-flow`; state stored under `${CLAUDE_PLUGIN_DATA}/polymath-flows/workflows/<id>/`; project overrides in `.claude/polymath/workflows/`.
- Connectors ship MCP + hooks + skills OR the `polymath-cli-only` keyword for CLI-wrapping connectors; credentials via `userConfig.sensitive: true`.
- Per-plugin token budget ≤ 400 (CLI-measured). Total target scales with plugin count.
- No native scheduler. External schedulers write to `${CLAUDE_PLUGIN_DATA}/polymath-core/queue.json`.
- No telemetry. Future opt-in requires `POLYMATH_TELEMETRY=1` + documented payload + local-disable + CI gate.
- Auto-update off by default. Per-plugin semver tags via `claude plugin tag --push`.
