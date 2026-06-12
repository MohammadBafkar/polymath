# Contributing to Polymath

Thanks for considering a contribution. Polymath is a public,
open-source Claude Code marketplace.

## Ground rules

1. **One plugin per concern.** Roles, lifecycle stages, target platforms, and external services each get their own plugin.
2. **Budgets and limits** (always-on token cost, skill body length, description shape) — the canonical numbers live in [`PLUGIN-AUTHORING.md` §8](PLUGIN-AUTHORING.md#8-token-budget-discipline) and §4. CI enforces them; don't memorize them from here.
3. **Each plugin owns its templates** in `plugins/<plugin>/templates/`. Frontmatter on canonical artifacts (PRD, ADR, Plan, RFC, Runbook, ArchitectureDoc, DACIDecision, TradeoffMatrix, Postmortem, ThreatModel, PRDescription) is validated against the corresponding JSON schema in `registry/schemas/artifacts/`.
4. **No secrets** in commits. The `polymath-engineering` secret-scan hook is a backstop, not a permission slip.

## Workflow

1. Open an issue describing the gap, the user, and the expected components.
2. Scaffold via `polymath-author:new-plugin <name>` or
   `polymath-author:new-skill <plugin> <skill>` (the bundled scripts at
   `plugins/polymath-author/bin/` walk up to find the caller's marketplace root).
3. Author components. Keep them small. Match the SDLC stage that motivated the issue.
4. Run the local check sequence in
   [`PLUGIN-AUTHORING.md` §11](PLUGIN-AUTHORING.md#11-submitting-a-plugin)
   (the canonical list; `tools/conformance.sh --all` is the umbrella gate).
5. Add at least one golden fixture under `tests/golden/<plugin>/<scenario>.md`.
6. Update `.claude-plugin/marketplace.json` if you added or renamed a plugin.
7. Open a PR. CI runs validate / lint / token-budget / link-check / golden-tests / evaluation.

## Commit and PR conventions

- Conventional Commits (`feat:`, `fix:`, `refactor:`, …). The `polymath-release:commit` skill enforces this on its own bumps; we ask contributors to follow the same rule.
- PR titles mirror the headline commit.
- PR descriptions follow [`plugins/polymath-release/templates/PR-description.md`](../plugins/polymath-release/templates/PR-description.md).

## Authoring discipline

See [`docs/PLUGIN-AUTHORING.md`](PLUGIN-AUTHORING.md). Highlights:

- Skills bundle templates / scripts / references. Commands are flat aliases.
- Agents only when forked context or panel critique is genuinely needed.
- Hooks for deterministic gates (secret-scan, format-on-save, push reminder).
- MCP for tool calls into external services.

## Reviewing

Reviewers check:

1. Does this fit the work-shaped plugin model (no primitive-shaped catch-alls)?
2. Is the always-on cost under budget?
3. Are there at least one golden fixture and one README entry?
4. Does each artifact-producing skill link the right template under its plugin's `templates/` directory, and is the template's frontmatter backed by a schema?
5. Does the PR include a CHANGELOG update?
6. For new connectors / infra plugins: is the `polymath_value` row in [`docs/INTEGRATION-POLICY.md`](INTEGRATION-POLICY.md) populated?

## Reporting bugs

Open an issue with:

- Plugin and version.
- Minimal reproduction.
- Expected vs actual behavior.
- Relevant transcript excerpt if possible.

## License

Contributions are licensed under MIT. By opening a PR you agree your contribution is licensed under those terms.
