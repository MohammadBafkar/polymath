# Polymath — Plan

> A public, open-source Claude Code marketplace of work-shaped plugins covering the full lifecycle of building software products. This document tracks design, status, and what's left.

---

## 1. Mission

Curated, role-shaped extensions for Claude Code that real teams can install a-la-carte. Each plugin owns one role, one lifecycle stage, one language, one infra target, or one external service. The unit of trust, versioning, and token budget is the plugin.

---

## 2. Status snapshot

**42 plugins**, **11 workflows**, **all gates green**.

Done:

- Marketplace plumbing (Phase 0).
- MVP loop — core / product / engineering / release / flows + `shipFeature` (Phase 1).
- Quality lane — qa / security / thinking / planning / writing + `reviewPR` (Phase 1.5).
- Stack specialize — frontend / backend / 3 langs / data / ai (Phase 2).
- Operate — platform / devops / k8s / sre / observability / incident (Phase 3).
- Connectors wave 1+2 — github / gh-actions / jira / pagerduty / datadog / snyk + `respondToIncident` (Phase 4).
- Connectors wave 3a — slack / sentry / linear.
- Catalog hardening — author plugin + Pages + release CI + conformance + privacy (Phase 5).
- Tier-1 craft completion — decisions, research, design, communication, leadership, learning, performance, content, mobile.
- Workflow library — bugTriage, perfRegression, refactorWithSafety, securityFinding, bumpDependency, migrateLanguageVersion, sunsetCapability, featureFromIdea.

Pending:

- **Connector wave 3b** — figma, notion, asana, aws, gcp, azure, stripe, vercel, cloudflare, elastic, grafana, honeycomb, launchdarkly, statuspage, terraform.
- **Language wave 2** — go, rust, java, swift, kotlin, ruby, php.
- **Infra waves** — aws, gcp, azure, terraform-stack, docker, postgres, redis.
- **One more workflow** — `experimentToGA` (blocked on a `run-experiment` skill in polymath-data).
- **Live golden-fixture CI** (operational) — requires `CLAUDE_CODE_OAUTH_TOKEN` (or `ANTHROPIC_API_KEY`) in repo secrets.
- **Community-marketplace submission** (operational) — once proven plugins surface.

Local gate measurements: 8,061 canonical listing tokens across 42 plugins (avg 191 / max 345 / cap 400). 22/22 `bin/polymath-flow` unit tests pass. `tools/conformance.sh --all` green.

---

## 3. Design principles (load-bearing)

- **Plugins are work-shaped.** One role / lifecycle stage / language / target / service per plugin. Not primitive-shaped (no "all hooks here" or "all skills there").
- **Per-plugin always-on cost ≤ 400 tokens** measured by `claude plugin details`. The CLI is the authority; the heuristic in `tools/token-budget.sh` is informational.
- **Commands are thin aliases (≤ 20 lines); skills bundle templates/scripts/references.** When both exist for the same name, the command points at the skill.
- **Agents are reserved.** Only for forked context or panel critique. No custom agents without a golden fixture proving they outperform a skill. Subagent constraints (no nested subagents, no per-agent hooks/MCPs, synchronous execution) are design inputs.
- **Workflows are YAML driven by a deterministic executable.** `polymath-flows/bin/polymath-flow` owns validation, state, resumption, and `mustPass` checks. The skill drives the loop but never owns state.
- **Enforcement is deterministic `mustPass:` checks.** Types: `fileExists`, `fileMatches`, `commandSucceeds`, `stepSummaryMatches`, `artifactValid`. AI cross-checks are advisory, never blocking.
- **Each plugin owns its templates** under `plugins/<plugin>/templates/`. Frontmatter on canonical artifacts (PRD, ADR, Postmortem, ThreatModel) is gated by JSON schemas in `shared/schemas/artifacts/`.
- **Connectors share a shape.** `.mcp.json` (upstream MCP server) + `userConfig` (`sensitive: true` credentials) + hooks for event-driven reactions + `references/<service>-tools.md`.
- **Three-layer workflow resolution.** project (`.claude/polymath/workflows/`) → user (`$CLAUDE_CONFIG_DIR/polymath/workflows/`) → marketplace (`plugins/polymath-flows/workflows/`).
- **No native scheduler.** Recurring work writes to `${CLAUDE_PLUGIN_DATA}/polymath-core/queue.json`; the `polymath-core` SessionStart hook surfaces due items.
- **No telemetry.** See [docs/PRIVACY.md](docs/PRIVACY.md).
- **Claude Code only.** No Codex / Copilot / Cursor adapters until real demand surfaces.

---

## 4. Marketplace shape

### Catalog tiers

```text
Foundation   — polymath-core
Mind & craft — polymath-thinking, polymath-planning, polymath-writing,
               polymath-decisions, polymath-learning
Product      — polymath-product, polymath-research, polymath-design
Engineering  — polymath-engineering, polymath-frontend, polymath-backend,
               polymath-mobile, polymath-data, polymath-ai
Languages    — polymath-lang-python, polymath-lang-typescript, polymath-lang-dotnet
Quality      — polymath-qa, polymath-security, polymath-performance
Operate      — polymath-platform, polymath-devops, polymath-infra-kubernetes,
               polymath-sre, polymath-observability, polymath-incident,
               polymath-release
People       — polymath-communication, polymath-leadership, polymath-content
Connectors   — polymath-connector-{github, github-actions, jira,
               pagerduty, datadog, snyk, slack, sentry, linear}
Orchestration — polymath-flows
Authoring    — polymath-author
```

### Workflows

```text
shipFeature           PRD → acceptance → implement → review → verify → changelog → PR draft
reviewPR              orient → 4 parallel critics (correctness, coverage, security, challenge) → synthesize
respondToIncident     page-context → triage → datadog signals → postmortem → file Jira bugs
bugTriage             5-whys → read-code → review-diff → work-breakdown
perfRegression        datadog signals → review-diff → fix → verify
refactorWithSafety    orient → coverage-gap → pin behavior with tests → refactor → verify → review
securityFinding       OWASP review → STRIDE model → implement → review → verify
bumpDependency        snyk triage → orient → smallest bump → review → verify
migrateLanguageVersion plan → PIN → FIX → verify per batch → STRICT → review
sunsetCapability      notice → deprecate-in-code → (remove at stage=remove) → verify → release-notes
featureFromIdea       interview-guide → persona → PRD → acceptance → implement → review → verify → PR
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
│   ├── .mcp.json                 # connector plugins only
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

Claude Code's runtime has no built-in DAG executor, state machine, or resumable job runner. `polymath-flows` provides:

1. **Skills** (`run-workflow`, `resume-workflow`, `list-workflows`) — drive the loop and perform Claude work for each step.
2. **Executable** (`bin/polymath-flow`) — validates YAML, owns state, evaluates `mustPass`. Python 3 stdlib-only with an embedded minimal YAML subset parser.

Workflows are serial. `topology: fanout` is accepted (and `reviewPR` declares it on its critic steps) but executor still runs serially in v0.1.5 — fanout is a declaration of parallel intent for downstream tooling.

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

CI: `validate.yml`, `token-budget.yml`, `lint.yml`, `link-check.yml`, `golden-tests.yml` (executable-unit + executable-e2e + fixtures-parse jobs), `pages.yml` (GitHub Pages catalog deploy), `release.yml` (manual per-plugin version tagger).

Deferred: full multi-step `claude -p` runs of every workflow end-to-end. Token-expensive; the `claude-cli-fixtures` job is wired and skips until `CLAUDE_CODE_OAUTH_TOKEN` (subscription) or `ANTHROPIC_API_KEY` is in repo secrets.

---

## 7. Remaining work (prioritized)

### Priority 1 — Connector wave 3 (continued)

- **polymath-connector-slack / -sentry / -linear** — `[done]`.
- **polymath-connector-launchdarkly / -statuspage / -terraform** — already designed in the original tier-7 table; build next.
- Future: figma, notion, asana, aws, gcp, azure, stripe, vercel, cloudflare, elastic, grafana, honeycomb.

### Priority 2 — Language wave 2

Each follows the Phase 2b shape (3 skills + 3 thin command aliases).

- **polymath-lang-go** — `write-gotest`, `lint-with-golangci-lint`, `propose-error-wrapping`.
- **polymath-lang-rust** — `write-cargo-test`, `lint-with-clippy`, `propose-error-types`.
- **polymath-lang-java** — `write-junit-test`, `lint-with-spotbugs`, `propose-records`.
- Future: swift, kotlin, ruby, php.

### Priority 3 — Infra waves

Cross-cloud and cross-runtime.

- **polymath-infra-docker** — `multi-stage-dockerfile-review`, `compose-design`, `image-vuln-triage` (pairs with snyk).
- **polymath-infra-postgres** — `index-strategy`, `query-plan-review`, `migration-online` (deeper than `polymath-backend:migration-plan`).
- **polymath-infra-redis** — `key-design`, `eviction-tuning`, `cluster-failure-modes`.
- Future: aws, gcp, azure, terraform-stack.

### Priority 4 — `experimentToGA` workflow

Blocked on a `run-experiment` skill in `polymath-data`. Add the skill first, then the workflow:

```text
research-question → metrics-tree (define success) → run-experiment → measure-adoption → release-narrative
```

### Priority 5 — Operational

- Wire `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` into repo secrets so `claude-cli-fixtures` CI runs.
- Submit proven plugins to the community marketplace once a few have demonstrably low-surprise behavior in real use.

---

## 8. Locked-in decisions

These are stable; revisit only when a clear failure mode appears.

- Monorepo, Apache-2.0, public OSS from day one.
- Templates live in each plugin (no `shared/templates/`). JSON Schemas in `shared/schemas/artifacts/` validate frontmatter.
- Workflows are YAML; state owned by `bin/polymath-flow`; state stored under `${CLAUDE_PLUGIN_DATA}/polymath-flows/workflows/<id>/`; project overrides in `.claude/polymath/workflows/`.
- Connectors ship MCP + hooks + skills together; credentials via `userConfig.sensitive: true`.
- Per-plugin token budget ≤ 400 (CLI-measured). Total target scales with plugin count.
- No native scheduler. External schedulers write to `${CLAUDE_PLUGIN_DATA}/polymath-core/queue.json`.
- No telemetry. Future opt-in requires `POLYMATH_TELEMETRY=1` + documented payload + local-disable + CI gate.
- Auto-update off by default. Per-plugin semver tags via `claude plugin tag --push`.
