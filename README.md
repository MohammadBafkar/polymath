# Polymath

> A public, open-source Claude Code marketplace of work-shaped plugins covering the full lifecycle of building software products — from idea to incident, from thinking-craft to platform engineering. Installable a-la-carte.

## Status

**v0.1 — Phase 1 MVP**: five plugins prove the marketplace mechanics with one complete, resumable feature-shipping loop.

- `polymath-core` — Foundation: conventions, glossary, plugin-budget reporter, SessionStart hook.
- `polymath-product` — PRD, acceptance criteria, epic decomposition.
- `polymath-engineering` — TDD feature-dev, code review, change verification, codebase orientation.
- `polymath-release` — Conventional Commits, PR descriptions, CHANGELOG, release notes.
- `polymath-flows` — flows-lite serial workflow runner + `shipFeature` workflow.

## Quick start

```bash
# 1. Add the marketplace from a local checkout
claude plugin marketplace add /path/to/polymath

# 2. Install the MVP set
claude plugin install \
  polymath-core@polymath polymath-product@polymath polymath-engineering@polymath \
  polymath-release@polymath polymath-flows@polymath

# 3. Run the golden demo
claude
> /polymath-flows:run-workflow shipFeature title="Rate-limit /login" scope=small
```

## Repo layout

```text
polymath/
├── .claude-plugin/marketplace.json
├── plugins/                # one directory per plugin
├── shared/
│   ├── templates/          # canonical artifact templates (PRD, ADR, …)
│   ├── schemas/            # workflow.schema.json, etc.
│   └── scripts/            # validate-frontmatter, secret-scan, compute-dora
├── tools/                  # scaffolders, validators, token-budget reporter
├── docs/                   # PLUGIN-AUTHORING, WORKFLOW-SCHEMA, CONTRIBUTING
└── .github/workflows/      # CI: validate, token-budget, lint, link-check, golden-tests
```

See [docs/PLUGIN-AUTHORING.md](docs/PLUGIN-AUTHORING.md) and [docs/WORKFLOW-SCHEMA.md](docs/WORKFLOW-SCHEMA.md).

## Design principles

- Plugins are work-shaped (one role / lifecycle stage / language / target each), not primitive-shaped.
- Per-plugin always-on token budget ≤ 400; MVP total ≤ 1,500 measured.
- Commands for thin aliases; skills when bundling templates/scripts/references.
- Agents only when a forked context or panel critique is justified.
- Workflows are YAML driven by a deterministic executable (`polymath-flows/bin/polymath-flow`); skills present the steps but the script owns state.
- Enforcement = deterministic `mustPass:` checks (`fileExists`, `fileMatches`, `commandSucceeds`, `stepSummaryMatches`). AI cross-checks are advisory.

## License

Apache-2.0. See [LICENSE](LICENSE).

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).
