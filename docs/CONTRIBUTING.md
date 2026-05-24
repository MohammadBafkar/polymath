# Contributing to Polymath

Thanks for considering a contribution. Polymath is a public, open-source Claude Code marketplace.

## Ground rules

1. **One plugin per concern.** Roles, lifecycle stages, languages, infra targets, and external services each get their own plugin.
2. **Per-plugin always-on listing cost ≤ 400 tokens.** Measured by `tools/token-budget.sh`. CI enforces.
3. **Skill body ≤ 500 lines.** Reference material spills to `references/`.
4. **Description ≤ 200 chars**, trigger phrase first.
5. **Each plugin owns its templates** in `plugins/<plugin>/templates/`. Frontmatter on canonical artifacts (PRD, ADR, Postmortem, ThreatModel, …) is validated against the corresponding JSON schema in `shared/schemas/artifacts/`.
6. **No secrets** in commits. The `polymath-engineering` secret-scan hook is a backstop, not a permission slip.

## Workflow

1. Open an issue describing the gap, the user, and the expected components.
2. Scaffold with `tools/new-plugin.sh <name>` or `tools/new-skill.sh <plugin> <skill>`.
3. Author components. Keep them small. Match the SDLC stage that motivated the issue.
4. Run all local checks:
   - `tools/validate-all.sh`
   - `tools/lint-skills.sh`
   - `tools/token-budget.sh`
   - `tools/conformance.sh --all` (catches structural gaps)
5. Add at least one golden fixture under `tests/golden/<plugin>/<scenario>.md`.
6. Update `.claude-plugin/marketplace.json` if you added or renamed a plugin.
7. Open a PR. CI runs validate / lint / token-budget / link-check / golden-tests.

## Commit and PR conventions

- Conventional Commits (`feat:`, `fix:`, `refactor:`, …). The `polymath-release` plugin enforces this on its own bumps; we ask contributors to follow the same rule.
- PR titles mirror the headline commit.
- PR descriptions follow [`plugins/polymath-release/templates/PR-description.md`](../plugins/polymath-release/templates/PR-description.md).

## Authoring discipline (lifted from `docs/PLUGIN-AUTHORING.md`)

- Skills bundle templates / scripts / references. Commands are flat aliases.
- Agents only when forked context or panel critique is genuinely needed.
- Hooks for deterministic gates (secret-scan, format-on-save, push reminder).
- MCP for tool calls into external services.

## Reviewing

Reviewers check:

1. Does this fit the work-shaped plugin model (no primitive-shaped catch-alls)?
2. Is the always-on cost under budget?
3. Are there at least one golden fixture and one README entry?
4. Does each artifact-producing skill link the right template under its plugin's `templates/` directory?
5. Does the PR include a CHANGELOG update?

## Reporting bugs

Open an issue with:

- Plugin and version.
- Minimal reproduction.
- Expected vs actual behavior.
- Relevant transcript excerpt if possible.

## License

Contributions are licensed under Apache-2.0. By opening a PR you agree your contribution is licensed under those terms.
